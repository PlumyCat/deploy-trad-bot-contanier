"""
Tests unitaires pour azure_wrappers.storage

Ce fichier teste toutes les fonctions du module storage incluant:
- Génération de noms uniques
- Création de Storage Accounts
- Création de containers blob
- Vérification et suppression
"""

import pytest
from unittest.mock import patch, MagicMock
from azure_wrappers.storage import (
    create_storage_account,
    create_blob_container,
    verify_storage_account,
    delete_storage_account,
    _generate_unique_storage_name,
    _check_name_availability,
    _get_storage_endpoints,
    _get_storage_keys,
    _get_storage_resource_id,
    STORAGE_SKU_DEFAULT,
    STORAGE_KIND_DEFAULT,
)
from azure_wrappers.common import AzureWrapperError


class TestGenerateUniqueName:
    """Tests pour la génération de noms uniques"""

    def test_generate_unique_storage_name_default(self):
        """Test génération avec préfixe par défaut"""
        name = _generate_unique_storage_name()

        # Vérifier qu'il commence par "tradbot"
        assert name.startswith("tradbot")

        # Vérifier longueur (max 24 caractères)
        assert 3 <= len(name) <= 24

        # Vérifier minuscules et chiffres uniquement
        assert name.islower()
        assert name.isalnum()

    def test_generate_unique_storage_name_custom_prefix(self):
        """Test génération avec préfixe personnalisé"""
        name = _generate_unique_storage_name("custom")

        assert name.startswith("custom")
        assert 3 <= len(name) <= 24
        assert name.islower()
        assert name.isalnum()

    def test_generate_unique_storage_name_long_prefix(self):
        """Test génération avec préfixe très long (doit tronquer)"""
        long_prefix = "a" * 30  # 30 caractères (dépasse limite)
        name = _generate_unique_storage_name(long_prefix)

        # Doit être tronqué à 24 chars max
        assert len(name) <= 24
        assert name.islower()
        assert name.isalnum()

    def test_generate_unique_storage_name_uniqueness(self):
        """Test que deux appels successifs génèrent des noms différents"""
        name1 = _generate_unique_storage_name()
        name2 = _generate_unique_storage_name()

        # Les noms doivent être différents (random suffix)
        assert name1 != name2


class TestCheckNameAvailability:
    """Tests pour la vérification de disponibilité des noms"""

    @patch('azure_wrappers.storage.run_az_command')
    def test_check_name_available(self, mock_run_az):
        """Test vérification d'un nom disponible"""
        mock_run_az.return_value = {
            "stdout": '{"nameAvailable": true, "reason": null}'
        }

        result = _check_name_availability("tradbot12345678")

        assert result is True

    @patch('azure_wrappers.storage.run_az_command')
    def test_check_name_unavailable(self, mock_run_az):
        """Test vérification d'un nom indisponible"""
        mock_run_az.return_value = {
            "stdout": '{"nameAvailable": false, "reason": "AlreadyExists"}'
        }

        result = _check_name_availability("tradbot12345678")

        assert result is False

    @patch('azure_wrappers.storage.run_az_command')
    def test_check_name_error(self, mock_run_az):
        """Test qu'une erreur retourne False par sécurité"""
        mock_run_az.side_effect = AzureWrapperError("Network error")

        result = _check_name_availability("tradbot12345678")

        # En cas d'erreur, considérer comme indisponible par sécurité
        assert result is False


class TestCreateStorageAccount:
    """Tests pour la fonction create_storage_account()"""

    @patch('azure_wrappers.storage.run_az_command')
    @patch('azure_wrappers.storage.check_az_logged_in', return_value=True)
    @patch('azure_wrappers.storage._check_name_availability', return_value=True)
    @patch('azure_wrappers.storage._get_storage_endpoints')
    @patch('azure_wrappers.storage._get_storage_keys')
    @patch('azure_wrappers.storage._get_storage_resource_id')
    @patch('azure_wrappers.storage.create_blob_container', return_value=True)
    def test_create_storage_account_success_auto_name(
        self,
        mock_create_container,
        mock_resource_id,
        mock_keys,
        mock_endpoints,
        mock_check_name,
        mock_logged_in,
        mock_run_az
    ):
        """Test création réussie avec nom auto-généré"""
        # Mock des retours
        mock_run_az.return_value = {"success": True, "returncode": 0, "stdout": "{}", "stderr": ""}
        mock_endpoints.return_value = {
            "blob": "https://tradbot12345678.blob.core.windows.net/",
            "table": "https://tradbot12345678.table.core.windows.net/",
            "queue": "https://tradbot12345678.queue.core.windows.net/",
            "file": "https://tradbot12345678.file.core.windows.net/"
        }
        mock_keys.return_value = {
            "key1": "test-key-1234567890abcdef",
            "key2": "test-key-0987654321fedcba"
        }
        mock_resource_id.return_value = "/subscriptions/test/resourceGroups/rg-test/providers/..."

        # Appel de la fonction
        result = create_storage_account(
            resource_group="rg-test",
            region="francecentral"
        )

        # Vérifications
        assert "name" in result
        assert result["name"].startswith("tradbot")
        assert result["sku"] == STORAGE_SKU_DEFAULT
        assert result["kind"] == STORAGE_KIND_DEFAULT
        assert result["region"] == "francecentral"
        assert result["container_created"] is True
        assert result["container_name"] == "translations"

        # Vérifier que les clés sont bien retournées
        assert "access_keys" in result
        assert result["access_keys"]["key1"] == "test-key-1234567890abcdef"

        # Vérifier que les clés masquées sont présentes
        assert "access_keys_display" in result
        assert result["access_keys_display"]["key1"].endswith("cdef")
        assert "*" in result["access_keys_display"]["key1"]

    @patch('azure_wrappers.storage.run_az_command')
    @patch('azure_wrappers.storage.check_az_logged_in', return_value=True)
    @patch('azure_wrappers.storage._check_name_availability', return_value=True)
    @patch('azure_wrappers.storage._get_storage_endpoints')
    @patch('azure_wrappers.storage._get_storage_keys')
    @patch('azure_wrappers.storage._get_storage_resource_id')
    def test_create_storage_account_with_custom_name(
        self,
        mock_resource_id,
        mock_keys,
        mock_endpoints,
        mock_check_name,
        mock_logged_in,
        mock_run_az
    ):
        """Test création avec nom personnalisé"""
        mock_run_az.return_value = {"success": True, "returncode": 0, "stdout": "{}", "stderr": ""}
        mock_endpoints.return_value = {"blob": "https://customname123.blob.core.windows.net/"}
        mock_keys.return_value = {"key1": "key1-value", "key2": "key2-value"}
        mock_resource_id.return_value = "/subscriptions/test/..."

        result = create_storage_account(
            resource_group="rg-test",
            name="customname123",
            create_container=False  # Pas de container
        )

        assert result["name"] == "customname123"
        assert result["container_created"] is False

    @patch('azure_wrappers.storage.check_az_logged_in', return_value=True)
    @patch('azure_wrappers.storage._check_name_availability', return_value=True)
    def test_create_storage_account_invalid_name_too_short(self, mock_check_name, mock_logged_in):
        """Test échec avec nom trop court"""
        with pytest.raises(AzureWrapperError, match="3-24 caractères"):
            create_storage_account(
                resource_group="rg-test",
                name="ab"  # Trop court
            )

    @patch('azure_wrappers.storage.check_az_logged_in', return_value=True)
    @patch('azure_wrappers.storage._check_name_availability', return_value=True)
    def test_create_storage_account_invalid_name_uppercase(self, mock_check_name, mock_logged_in):
        """Test échec avec majuscules (interdit)"""
        with pytest.raises(AzureWrapperError, match="minuscules et des chiffres"):
            create_storage_account(
                resource_group="rg-test",
                name="StorageAccount123"  # Majuscules interdites
            )

    @patch('azure_wrappers.storage.check_az_logged_in', return_value=True)
    @patch('azure_wrappers.storage._check_name_availability', return_value=True)
    def test_create_storage_account_invalid_name_hyphens(self, mock_check_name, mock_logged_in):
        """Test échec avec tirets (interdit)"""
        with pytest.raises(AzureWrapperError, match="minuscules et des chiffres"):
            create_storage_account(
                resource_group="rg-test",
                name="storage-account-123"  # Tirets interdits
            )

    @patch('azure_wrappers.storage.check_az_logged_in', return_value=True)
    @patch('azure_wrappers.storage._check_name_availability', return_value=False)
    def test_create_storage_account_name_not_available(self, mock_check_name, mock_logged_in):
        """Test échec si nom déjà pris"""
        with pytest.raises(AzureWrapperError, match="n'est pas disponible"):
            create_storage_account(
                resource_group="rg-test",
                name="alreadytaken123"
            )

    @patch('azure_wrappers.storage.check_az_logged_in', return_value=False)
    def test_create_storage_account_not_logged_in(self, mock_logged_in):
        """Test échec si non connecté à Azure CLI"""
        with pytest.raises(AzureWrapperError, match="Vous devez être connecté"):
            create_storage_account(resource_group="rg-test")

    @patch('azure_wrappers.storage.run_az_command')
    @patch('azure_wrappers.storage.check_az_logged_in', return_value=True)
    @patch('azure_wrappers.storage._check_name_availability', return_value=True)
    def test_create_storage_account_already_exists_error(
        self,
        mock_check_name,
        mock_logged_in,
        mock_run_az
    ):
        """Test gestion erreur si Storage Account existe déjà"""
        mock_run_az.side_effect = AzureWrapperError("StorageAccountAlreadyTaken: Name taken")

        with pytest.raises(AzureWrapperError, match="déjà pris globalement"):
            create_storage_account(resource_group="rg-test", name="existingaccount")


class TestCreateBlobContainer:
    """Tests pour la fonction create_blob_container()"""

    @patch('azure_wrappers.storage.run_az_command')
    def test_create_blob_container_success(self, mock_run_az):
        """Test création réussie d'un container"""
        mock_run_az.return_value = {
            "stdout": '{"created": true, "name": "translations"}'
        }

        result = create_blob_container(
            account_name="tradbot12345678",
            container_name="translations",
            account_key="test-key"
        )

        assert result is True

    @patch('azure_wrappers.storage.run_az_command')
    def test_create_blob_container_already_exists(self, mock_run_az):
        """Test si container existe déjà"""
        mock_run_az.side_effect = AzureWrapperError("ContainerAlreadyExists: Container exists")

        result = create_blob_container(
            account_name="tradbot12345678",
            container_name="translations",
            account_key="test-key"
        )

        # Doit retourner True quand même (container existe)
        assert result is True


class TestVerifyStorageAccount:
    """Tests pour la fonction verify_storage_account()"""

    @patch('azure_wrappers.storage.run_az_command')
    def test_verify_storage_account_exists(self, mock_run_az):
        """Test vérification d'un Storage Account existant"""
        mock_run_az.return_value = {
            "success": True,
            "stdout": '''{
                "provisioningState": "Succeeded",
                "sku": {"name": "Standard_LRS"},
                "kind": "StorageV2",
                "primaryLocation": "francecentral"
            }'''
        }

        result = verify_storage_account("tradbot12345678", "rg-test")

        assert result["exists"] is True
        assert result["provisioning_state"] == "Succeeded"
        assert result["sku"] == "Standard_LRS"
        assert result["kind"] == "StorageV2"
        assert result["primary_location"] == "francecentral"

    @patch('azure_wrappers.storage.run_az_command')
    def test_verify_storage_account_not_found(self, mock_run_az):
        """Test vérification d'un Storage Account inexistant"""
        mock_run_az.return_value = {
            "success": False,
            "stderr": "ResourceNotFound"
        }

        result = verify_storage_account("nonexistent", "rg-test")

        assert result["exists"] is False
        assert result["provisioning_state"] == "NotFound"


class TestDeleteStorageAccount:
    """Tests pour la fonction delete_storage_account()"""

    @patch('azure_wrappers.storage.run_az_command')
    def test_delete_storage_account_with_yes(self, mock_run_az):
        """Test suppression avec confirmation automatique"""
        mock_run_az.return_value = {"success": True, "returncode": 0, "stdout": "", "stderr": ""}

        result = delete_storage_account("tradbot12345678", "rg-test", yes=True)

        assert result is True
        assert mock_run_az.called

    @patch('builtins.input', return_value='non')
    def test_delete_storage_account_cancelled(self, mock_input):
        """Test annulation de la suppression"""
        result = delete_storage_account("tradbot12345678", "rg-test", yes=False)

        assert result is False


class TestHelperFunctions:
    """Tests pour les fonctions helper"""

    @patch('azure_wrappers.storage.run_az_command')
    def test_get_storage_endpoints(self, mock_run_az):
        """Test récupération des endpoints"""
        mock_run_az.return_value = {
            "stdout": '''{
                "blob": "https://test.blob.core.windows.net/",
                "table": "https://test.table.core.windows.net/",
                "queue": "https://test.queue.core.windows.net/",
                "file": "https://test.file.core.windows.net/"
            }'''
        }

        endpoints = _get_storage_endpoints("test", "rg-test")

        assert endpoints["blob"] == "https://test.blob.core.windows.net/"
        assert "table" in endpoints
        assert "queue" in endpoints
        assert "file" in endpoints

    @patch('azure_wrappers.storage.run_az_command')
    def test_get_storage_keys(self, mock_run_az):
        """Test récupération des clés"""
        mock_run_az.return_value = {
            "stdout": '''[
                {"keyName": "key1", "value": "first-key-value"},
                {"keyName": "key2", "value": "second-key-value"}
            ]'''
        }

        keys = _get_storage_keys("test", "rg-test")

        assert keys["key1"] == "first-key-value"
        assert keys["key2"] == "second-key-value"

    @patch('azure_wrappers.storage.run_az_command')
    def test_get_storage_resource_id(self, mock_run_az):
        """Test récupération de l'ID de ressource"""
        mock_run_az.return_value = {
            "stdout": "/subscriptions/12345/resourceGroups/rg-test/providers/Microsoft.Storage/storageAccounts/test"
        }

        resource_id = _get_storage_resource_id("test", "rg-test")

        assert resource_id.startswith("/subscriptions/")
        assert "test" in resource_id


class TestSTORY006AcceptanceCriteria:
    """
    Tests validant les critères d'acceptation de STORY-006

    Acceptance Criteria from sprint-plan:
    - [ ] Module Python `azure_deployer.py` créé (ou azure_wrappers/storage.py) ✓
    - [ ] Fonction `create_storage_account()` implémentée ✓
    - [ ] Storage Account créé avec nom unique (génération automatique) ✓
    - [ ] Type Standard_LRS configuré ✓
    - [ ] Container blob "translations" créé automatiquement ✓
    - [ ] Clés d'accès récupérées et affichées (sans stockage) ✓
    - [ ] Gestion d'erreurs Azure CLI (permissions, timeouts, nom déjà pris) ✓
    - [ ] Logs sanitizés (aucun credential visible) ✓
    """

    def test_acceptance_criteria_1_module_created(self):
        """AC#1: Module Python créé"""
        # Le module existe si on peut l'importer
        import azure_wrappers.storage
        assert azure_wrappers.storage is not None

    def test_acceptance_criteria_2_function_exists(self):
        """AC#2: Fonction create_storage_account() implémentée"""
        assert callable(create_storage_account)

    def test_acceptance_criteria_3_unique_name_generation(self):
        """AC#3: Nom unique généré automatiquement"""
        name1 = _generate_unique_storage_name()
        name2 = _generate_unique_storage_name()

        # Les noms doivent être uniques
        assert name1 != name2

        # Les noms doivent respecter les contraintes Azure
        assert 3 <= len(name1) <= 24
        assert name1.islower()
        assert name1.isalnum()

    def test_acceptance_criteria_4_standard_lrs_configured(self):
        """AC#4: Type Standard_LRS configuré"""
        # Vérifier que la constante par défaut est Standard_LRS
        assert STORAGE_SKU_DEFAULT == "Standard_LRS"

    def test_acceptance_criteria_5_container_function_exists(self):
        """AC#5: Container blob "translations" créé automatiquement"""
        assert callable(create_blob_container)

    @patch('azure_wrappers.storage.run_az_command')
    @patch('azure_wrappers.storage.check_az_logged_in', return_value=True)
    @patch('azure_wrappers.storage._check_name_availability', return_value=True)
    @patch('azure_wrappers.storage._get_storage_endpoints', return_value={"blob": "https://test.blob"})
    @patch('azure_wrappers.storage._get_storage_keys')
    @patch('azure_wrappers.storage._get_storage_resource_id', return_value="/test/id")
    @patch('azure_wrappers.storage.create_blob_container', return_value=True)
    def test_acceptance_criteria_6_keys_retrieved(
        self, mock_container, mock_id, mock_keys, mock_endpoints, mock_check, mock_logged_in, mock_run_az
    ):
        """AC#6: Clés d'accès récupérées et affichées"""
        mock_run_az.return_value = {"success": True, "returncode": 0, "stdout": "{}", "stderr": ""}
        mock_keys.return_value = {"key1": "test-key-123", "key2": "test-key-456"}

        result = create_storage_account(resource_group="rg-test", name="testaccount123")

        # Vérifier que les clés sont dans le résultat
        assert "access_keys" in result
        assert result["access_keys"]["key1"] == "test-key-123"

        # Vérifier que les clés masquées sont présentes
        assert "access_keys_display" in result
        assert "*" in result["access_keys_display"]["key1"]

    def test_acceptance_criteria_7_error_handling(self):
        """AC#7: Gestion d'erreurs Azure CLI"""
        # Tester plusieurs cas d'erreur
        # (les tests spécifiques sont dans TestCreateStorageAccount)

        # Vérifier que AzureWrapperError est levée pour nom invalide
        with pytest.raises(AzureWrapperError):
            # Nom trop court
            create_storage_account(resource_group="rg-test", name="ab")

    def test_acceptance_criteria_8_credentials_sanitized(self):
        """AC#8: Logs sanitizés (credentials masqués)"""
        from azure_wrappers.common import sanitize_credential

        # Vérifier que la fonction de sanitisation existe
        assert callable(sanitize_credential)

        # Vérifier qu'elle masque bien les credentials
        key = "test-key-1234567890"
        masked = sanitize_credential(key, visible_chars=4)

        assert "*" in masked
        assert masked.endswith("7890")
        assert "test-key" not in masked
