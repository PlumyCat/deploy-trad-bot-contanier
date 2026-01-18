"""
Tests End-to-End (E2E) du Workflow Complet
STORY-INF-001: Tests E2E du Workflow Complet

Ce script teste l'intégration complète du système:
1. Connexion Azure CLI
2. Déploiement Storage Account
3. Déploiement Translator (SKU F0 CRITICAL)
4. Déploiement Functions App
5. Génération du rapport
6. Cleanup automatique des ressources

⚠️ IMPORTANT: Ce test utilise une VRAIE subscription Azure
- Assure-toi d'être connecté avec `az login --tenant <tenant-id>` avant d'exécuter
- Les ressources créées seront nettoyées automatiquement
- Toutes les ressources ont le préfixe "test-" pour identification

Exécution:
    pytest tests/test_e2e_workflow.py -v -s

Exécution avec marqueur:
    pytest tests/test_e2e_workflow.py -v -s -m e2e
"""

import pytest
import subprocess
import time
import json
import sys
import random
from pathlib import Path

# Ajouter le dossier parent au path pour importer azure_wrappers
sys.path.insert(0, str(Path(__file__).parent.parent))

from azure_wrappers import (
    # Account
    get_current_account,
    check_permissions,
    # Storage
    create_storage_account,
    create_blob_container,
    verify_storage_account,
    delete_storage_account,
    # Translator
    create_translator,
    verify_translator,
    # Functions
    create_function_app,
    verify_function_app,
    delete_function_app,
    # Report
    generate_report,
    save_report,
)
from azure_wrappers.common import AzureWrapperError


# ============================================================================
# Configuration des Tests E2E
# ============================================================================

# Préfixe pour toutes les ressources de test (facilite identification et cleanup)
TEST_PREFIX = "test"

# Région par défaut pour les tests
TEST_REGION = "francecentral"

# Nom du groupe de ressources de test (sera créé et supprimé)
TEST_RESOURCE_GROUP = f"{TEST_PREFIX}-tradbot-e2e-rg"

# Timeout pour les opérations Azure (en secondes)
AZURE_OPERATION_TIMEOUT = 300  # 5 minutes

# Marquer tous les tests de ce fichier comme "e2e" et "slow"
pytestmark = [pytest.mark.e2e, pytest.mark.slow]


# ============================================================================
# Fixtures
# ============================================================================

@pytest.fixture(scope="module")
def azure_connection():
    """
    Fixture: Vérifie la connexion Azure CLI et les permissions

    Scope: module (exécuté une seule fois pour tous les tests)

    Yields:
        dict: Informations sur le compte Azure connecté
    """
    print("\n" + "=" * 80)
    print("PRÉPARATION E2E: Vérification connexion Azure CLI")
    print("=" * 80)

    # Vérifier connexion Azure
    try:
        account = get_current_account()
        print(f"✅ Connecté à Azure: {account['name']}")
        print(f"   Subscription ID: {account['id']}")
        print(f"   Tenant ID: {account['tenant_id']}")
    except AzureWrapperError as e:
        pytest.fail(
            f"❌ Erreur: Pas connecté à Azure CLI.\n"
            f"Exécutez 'az login --tenant <tenant-id>' avant de lancer les tests E2E.\n"
            f"Détails: {e}"
        )

    # Vérifier permissions (optionnel - peut échouer avec comptes délégués)
    print("\nVérification des permissions...")
    try:
        permissions_result = check_permissions(subscription_id=account["id"])

        if not permissions_result["has_permissions"]:
            pytest.fail(
                f"❌ Permissions insuffisantes.\n"
                f"{permissions_result['message']}\n"
                f"Rôles trouvés: {', '.join(permissions_result['roles'])}\n"
                f"Rôles requis: {', '.join(permissions_result['required_roles'])}"
            )

        print(f"✅ Permissions OK - Rôles: {', '.join(permissions_result['roles'])}")
    except AzureWrapperError as e:
        # Comptes délégués peuvent ne pas avoir accès au Graph pour check_permissions
        print(f"⚠️  Vérification des permissions ignorée (compte délégué): {str(e)[:100]}...")
        print("   Les tests vont continuer - les erreurs de permissions apparaîtront lors des déploiements.")

    yield account

    # Pas de cleanup ici, chaque test gère son propre cleanup


@pytest.fixture(scope="module")
def test_resource_group(azure_connection):
    """
    Fixture: Crée un groupe de ressources de test

    Scope: module (partagé entre tous les tests)

    Yields:
        str: Nom du groupe de ressources créé

    Cleanup:
        Supprime le groupe de ressources après tous les tests
    """
    print("\n" + "=" * 80)
    print("SETUP E2E: Création du groupe de ressources de test")
    print("=" * 80)

    subscription_id = azure_connection["id"]

    # Créer le groupe de ressources
    cmd = [
        "az", "group", "create",
        "--name", TEST_RESOURCE_GROUP,
        "--location", TEST_REGION,
        "--subscription", subscription_id,
    ]

    print(f"Création du groupe: {TEST_RESOURCE_GROUP} dans {TEST_REGION}...")

    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=True,
            timeout=AZURE_OPERATION_TIMEOUT
        )
        print("✅ Groupe de ressources créé")
    except subprocess.CalledProcessError as e:
        pytest.fail(
            f"❌ Échec création groupe de ressources:\n"
            f"Commande: {' '.join(cmd)}\n"
            f"Stderr: {e.stderr}"
        )
    except subprocess.TimeoutExpired:
        pytest.fail(f"❌ Timeout lors de la création du groupe de ressources")

    yield TEST_RESOURCE_GROUP

    # Cleanup: Supprimer le groupe de ressources après tous les tests
    print("\n" + "=" * 80)
    print("CLEANUP E2E: Suppression du groupe de ressources de test")
    print("=" * 80)

    cmd_delete = [
        "az", "group", "delete",
        "--name", TEST_RESOURCE_GROUP,
        "--yes",  # Pas de confirmation
        "--no-wait",  # Ne pas attendre la fin (asynchrone)
        "--subscription", subscription_id,
    ]

    print(f"Suppression du groupe: {TEST_RESOURCE_GROUP}...")

    try:
        subprocess.run(
            cmd_delete,
            capture_output=True,
            text=True,
            check=True,
            timeout=30  # Timeout court car --no-wait
        )
        print("✅ Suppression lancée (asynchrone)")
        print("   Les ressources seront supprimées en arrière-plan")
    except subprocess.CalledProcessError as e:
        print(f"⚠️  Avertissement: Échec suppression groupe (peut-être déjà supprimé)")
        print(f"   Stderr: {e.stderr}")


# ============================================================================
# Tests E2E
# ============================================================================

class TestE2EWorkflow:
    """
    Tests End-to-End du workflow complet de déploiement

    Ces tests valident l'intégration de bout en bout:
    - Connexion Azure
    - Déploiement des ressources (Storage, Translator, Functions)
    - Vérification SKU F0 pour Translator (CRITIQUE)
    - Génération du rapport
    - Cleanup

    Les tests sont exécutés dans l'ordre grâce aux numéros de test.
    """

    @pytest.mark.order(1)
    def test_01_connection_and_permissions(self, azure_connection):
        """
        Test 1: Connexion Azure CLI et vérification des permissions

        Vérifie:
        - Connexion Azure CLI active
        - Subscription accessible
        - Permissions suffisantes (Contributor ou supérieur)
        """
        print("\n" + "-" * 80)
        print("TEST E2E 1/6: Connexion Azure et Permissions")
        print("-" * 80)

        # La fixture azure_connection a déjà vérifié la connexion
        assert azure_connection is not None
        assert "id" in azure_connection
        assert "name" in azure_connection

        print(f"✅ Test 1 réussi: Connexion Azure validée")
        print(f"   Subscription: {azure_connection['name']}")

    @pytest.mark.order(2)
    def test_02_deploy_storage_account(self, azure_connection, test_resource_group):
        """
        Test 2: Déploiement d'un Storage Account

        Vérifie:
        - Création du Storage Account avec préfixe "test"
        - Création d'un container blob
        - Vérification des endpoints
        - Récupération des clés
        """
        print("\n" + "-" * 80)
        print("TEST E2E 2/6: Déploiement Storage Account")
        print("-" * 80)

        subscription_id = azure_connection["id"]

        # Créer Storage Account
        print(f"Création Storage Account dans {test_resource_group}...")
        storage_result = create_storage_account(
            resource_group=test_resource_group,
            region=TEST_REGION,
            name=None,  # Génération automatique du nom
        )

        assert "name" in storage_result
        assert "access_keys" in storage_result
        assert storage_result["container_created"] is True

        storage_name = storage_result["name"]
        storage_key = storage_result["access_keys"]["key1"]
        print(f"✅ Storage Account créé: {storage_name}")
        print(f"✅ Container blob créé: {storage_result['container_name']}")

        print(f"✅ Test 2 réussi: Storage Account déployé avec container")

        # Stocker pour tests suivants
        self.storage_name = storage_name
        self.storage_key = storage_key

    @pytest.mark.order(3)
    def test_03_deploy_translator_sku_f0(self, azure_connection, test_resource_group):
        """
        Test 3: Déploiement Azure Translator avec SKU F0 (CRITIQUE)

        Vérifie:
        - Création du Translator avec SKU F0 (gratuit)
        - ⚠️  CRITIQUE: Vérification que SKU F0 est BIEN utilisé (pas S0/S1/S2)
        - Récupération des clés et endpoint
        """
        print("\n" + "-" * 80)
        print("TEST E2E 3/6: Déploiement Translator (SKU F0 CRITIQUE)")
        print("-" * 80)

        subscription_id = azure_connection["id"]

        # Créer Translator avec nom unique
        translator_name = f"test-trans-{random.randint(1000, 9999)}"
        print(f"Création Translator avec SKU F0 dans {test_resource_group}...")
        print(f"   Nom: {translator_name}")

        translator_result = create_translator(
            name=translator_name,
            resource_group=test_resource_group,
            region=TEST_REGION,
        )

        assert "name" in translator_result
        assert "key" in translator_result
        assert translator_result["sku"] == "F0"

        translator_key = translator_result["key"]
        print(f"✅ Translator créé: {translator_name}")
        print(f"✅ SKU F0 confirmé (gratuit - 2M caractères/mois)")

        # 🔴 VÉRIFICATION CRITIQUE: SKU F0 (déjà confirmé par create_translator)
        # Vérifier Translator (double-check SKU F0)
        print("\nVérification Translator...")
        verify_result = verify_translator(
            name=translator_name,
            resource_group=test_resource_group,
        )

        assert verify_result["exists"] is True
        assert verify_result["sku_is_f0"] is True, (
            f"❌ Double-check ÉCHEC: SKU devrait être F0, obtenu {verify_result['sku']}"
        )
        print(f"✅ Translator vérifié: SKU F0 double-confirmé")

        print(f"✅ Test 3 réussi: Translator déployé avec SKU F0 confirmé")

        # Stocker pour tests suivants
        self.translator_name = translator_name
        self.translator_key = translator_key
        self.translator_endpoint = verify_result["endpoint"]

    @pytest.mark.order(4)
    def test_04_deploy_function_app(self, azure_connection, test_resource_group):
        """
        Test 4: Déploiement Azure Functions App

        Vérifie:
        - Création du Functions App
        - Configuration des app settings
        - Vérification health check
        """
        print("\n" + "-" * 80)
        print("TEST E2E 4/6: Déploiement Functions App")
        print("-" * 80)

        subscription_id = azure_connection["id"]

        # S'assurer que storage_name et translator_key existent
        assert hasattr(self, "storage_name"), "Test 2 doit être exécuté avant Test 4"
        assert hasattr(self, "translator_key"), "Test 3 doit être exécuté avant Test 4"

        # Créer Function App avec nom unique
        function_app_name = f"test-func-{random.randint(1000, 9999)}"
        print(f"Création Function App dans {test_resource_group}...")
        print(f"   Nom: {function_app_name}")

        function_result = create_function_app(
            name=function_app_name,
            resource_group=test_resource_group,
            storage_account=self.storage_name,
            region=TEST_REGION,
        )

        assert "name" in function_result
        assert "default_hostname" in function_result

        print(f"✅ Function App créé: {function_app_name}")
        print(f"   URL: https://{function_result['default_hostname']}")

        # Vérifier Function App
        print("Vérification Function App...")
        verify_result = verify_function_app(
            name=function_app_name,
            resource_group=test_resource_group,
        )

        assert verify_result["exists"] is True
        assert verify_result["state"] == "Running"
        print(f"✅ Function App vérifié: état {verify_result['state']}")

        print(f"✅ Test 4 réussi: Function App déployé et vérifié")

        # Stocker pour tests suivants
        self.function_app_name = function_app_name
        self.function_app_url = f"https://{verify_result['default_hostname']}"

    @pytest.mark.order(5)
    def test_05_generate_report(self, azure_connection, test_resource_group):
        """
        Test 5: Génération du rapport d'intervention

        Vérifie:
        - Génération du rapport avec toutes les ressources créées
        - Présence des informations clés (Storage, Translator SKU F0, Functions)
        - Format du rapport
        - Sauvegarde du rapport
        """
        print("\n" + "-" * 80)
        print("TEST E2E 5/6: Génération Rapport d'Intervention")
        print("-" * 80)

        # S'assurer que toutes les ressources existent
        assert hasattr(self, "storage_name"), "Test 2 doit être exécuté avant Test 5"
        assert hasattr(self, "translator_name"), "Test 3 doit être exécuté avant Test 5"
        assert hasattr(self, "function_app_name"), "Test 4 doit être exécuté avant Test 5"

        subscription_id = azure_connection["id"]

        # Préparer les données pour le rapport
        deployment_data = {
            "client_name": "TEST-E2E-Client",
            "subscription_id": subscription_id,
            "resource_group": test_resource_group,
            "region": TEST_REGION,
            "storage_account": self.storage_name,
            "translator_name": self.translator_name,
            "translator_sku": "F0",  # IMPORTANT: SKU F0 vérifié dans test 3
            "function_app_name": self.function_app_name,
            "function_app_url": self.function_app_url,
        }

        # Générer le rapport
        print("Génération du rapport...")
        report = generate_report(deployment_data)

        assert report is not None
        assert isinstance(report, str)
        assert len(report) > 0

        # Vérifications du contenu du rapport
        print("Vérification du contenu du rapport...")
        assert "TEST-E2E-Client" in report
        assert self.storage_name in report
        assert self.translator_name in report
        assert "F0" in report  # SKU F0 doit apparaître dans le rapport
        assert self.function_app_name in report
        assert test_resource_group in report

        print("✅ Rapport généré avec toutes les informations")

        # Sauvegarder le rapport
        print("Sauvegarde du rapport...")
        report_path = save_report(
            report_content=report,
            client_name="TEST-E2E-Client",
            output_dir="tests/outputs"
        )

        assert report_path is not None
        assert Path(report_path).exists()

        print(f"✅ Rapport sauvegardé: {report_path}")

        print(f"✅ Test 5 réussi: Rapport généré et sauvegardé")

        # Stocker pour vérification finale
        self.report_path = report_path
        self.report_content = report

    @pytest.mark.order(6)
    def test_06_cleanup_verification(self, azure_connection, test_resource_group):
        """
        Test 6: Vérification du cleanup (sera fait par la fixture)

        Vérifie:
        - Toutes les ressources ont été créées correctement
        - Le groupe de ressources existe
        - Les ressources seront nettoyées par la fixture test_resource_group
        """
        print("\n" + "-" * 80)
        print("TEST E2E 6/6: Vérification Finale")
        print("-" * 80)

        subscription_id = azure_connection["id"]

        # Vérifier que le groupe de ressources existe toujours
        cmd_show_rg = [
            "az", "group", "show",
            "--name", test_resource_group,
            "--subscription", subscription_id,
            "--output", "json",
        ]

        try:
            result = subprocess.run(
                cmd_show_rg,
                capture_output=True,
                text=True,
                check=True,
                timeout=30
            )
            rg_details = json.loads(result.stdout)
            assert rg_details["name"] == test_resource_group
            print(f"✅ Groupe de ressources existe: {test_resource_group}")
        except subprocess.CalledProcessError as e:
            pytest.fail(f"❌ Groupe de ressources introuvable: {e.stderr}")

        # Lister les ressources dans le groupe
        cmd_list_resources = [
            "az", "resource", "list",
            "--resource-group", test_resource_group,
            "--subscription", subscription_id,
            "--output", "json",
        ]

        try:
            result = subprocess.run(
                cmd_list_resources,
                capture_output=True,
                text=True,
                check=True,
                timeout=30
            )
            resources = json.loads(result.stdout)
            resource_count = len(resources)

            print(f"✅ Ressources créées: {resource_count}")
            for resource in resources:
                print(f"   - {resource['type']}: {resource['name']}")

            # On s'attend à au moins 3 ressources (Storage, Translator, Function App)
            assert resource_count >= 3, (
                f"❌ Pas assez de ressources créées. Attendu: ≥3, Obtenu: {resource_count}"
            )

        except subprocess.CalledProcessError as e:
            pytest.fail(f"❌ Échec listage des ressources: {e.stderr}")

        print("\n" + "=" * 80)
        print("✅ TOUS LES TESTS E2E RÉUSSIS!")
        print("=" * 80)
        print("\n📊 Résumé du workflow E2E:")
        print(f"   ✅ Connexion Azure validée")
        print(f"   ✅ Storage Account déployé: {self.storage_name}")
        print(f"   ✅ Translator déployé avec SKU F0: {self.translator_name}")
        print(f"   ✅ Function App déployé: {self.function_app_name}")
        print(f"   ✅ Rapport généré: {self.report_path}")
        print(f"   ✅ {resource_count} ressources créées")
        print("\n🧹 Cleanup:")
        print(f"   Le groupe de ressources '{test_resource_group}' sera supprimé automatiquement")
        print(f"   par la fixture après tous les tests.")
        print("=" * 80)


# ============================================================================
# Tests Additionnels (Optionnels)
# ============================================================================

@pytest.mark.skip(reason="Test optionnel - décommentez pour exécuter")
class TestE2EErrorHandling:
    """
    Tests optionnels pour la gestion des erreurs

    Ces tests vérifient que le système gère correctement les erreurs:
    - Ressource déjà existante
    - Permissions insuffisantes
    - Région non supportée
    """

    def test_duplicate_resource_handling(self, azure_connection, test_resource_group):
        """Test: Gestion de ressource déjà existante"""
        # TODO: Implémenter si nécessaire
        pass

    def test_insufficient_permissions_handling(self, azure_connection):
        """Test: Gestion permissions insuffisantes"""
        # TODO: Implémenter si nécessaire
        pass
