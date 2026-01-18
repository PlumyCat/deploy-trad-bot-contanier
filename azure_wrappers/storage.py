"""
Azure Storage Wrapper - Déploiement Azure Storage Account

Ce module fournit des fonctions pour automatiser le déploiement
d'Azure Storage Accounts pour le Bot Traducteur.

Configuration recommandée:
- SKU: Standard_LRS (Locally Redundant Storage - économique)
- Kind: StorageV2 (usage général recommandé)
- Container: "translations" pour documents traduits
"""

import time
import random
import string
from datetime import datetime
from typing import Dict, Any, Optional, List
from .common import (
    run_az_command,
    parse_az_json_output,
    validate_azure_region,
    sanitize_credential,
    AzureWrapperError,
    check_az_logged_in,
)


# Configuration SKU par défaut (Standard LRS - économique)
STORAGE_SKU_DEFAULT = "Standard_LRS"  # Locally Redundant Storage
STORAGE_KIND_DEFAULT = "StorageV2"    # Recommandé pour usage général


def _generate_unique_storage_name(prefix: str = "tradbot") -> str:
    """
    Génère un nom unique pour un Azure Storage Account

    Azure Storage naming rules:
    - 3-24 caractères
    - Minuscules et chiffres UNIQUEMENT (pas de tirets, pas de majuscules)
    - Doit être globalement unique (DNS)

    Args:
        prefix: Préfixe pour le nom (défaut: "tradbot")

    Returns:
        Nom unique au format: {prefix}{random}{timestamp}
        Exemple: "tradbot3a7f20260118"

    Example:
        >>> name = _generate_unique_storage_name("tradbot")
        >>> print(name)
        tradbot3a7f20260118
    """
    # Générer un suffixe aléatoire (4 caractères hexadécimaux)
    random_suffix = ''.join(random.choices(string.hexdigits.lower()[:16], k=4))

    # Timestamp court (YYMMDD format)
    timestamp = datetime.now().strftime("%y%m%d")

    # Construire le nom (max 24 chars)
    name = f"{prefix}{random_suffix}{timestamp}"

    # Vérifier la longueur (max 24 caractères)
    if len(name) > 24:
        # Tronquer le préfixe si nécessaire
        max_prefix_length = 24 - len(random_suffix) - len(timestamp)
        name = f"{prefix[:max_prefix_length]}{random_suffix}{timestamp}"

    # Vérifier les contraintes Azure (minuscules + chiffres uniquement)
    if not name.islower() or not name.isalnum():
        raise AzureWrapperError(
            f"Nom généré '{name}' invalide (doit être minuscules + chiffres uniquement)"
        )

    return name


def _check_name_availability(name: str) -> bool:
    """
    Vérifie si un nom de Storage Account est disponible

    Args:
        name: Nom du Storage Account à vérifier

    Returns:
        True si disponible, False sinon

    Raises:
        AzureWrapperError: Si la vérification échoue
    """
    command = [
        "az", "storage", "account", "check-name",
        "--name", name,
    ]

    try:
        result = run_az_command(command)
        availability_info = parse_az_json_output(result["stdout"])

        return availability_info.get("nameAvailable", False)

    except AzureWrapperError:
        # En cas d'erreur, considérer comme indisponible par sécurité
        return False


def create_storage_account(
    resource_group: str,
    region: str = "francecentral",
    name: Optional[str] = None,
    sku: str = STORAGE_SKU_DEFAULT,
    kind: str = STORAGE_KIND_DEFAULT,
    tags: Optional[Dict[str, str]] = None,
    create_container: bool = True,
    container_name: str = "translations",
) -> Dict[str, Any]:
    """
    Crée un Azure Storage Account avec configuration optimale

    Cette fonction:
    1. Génère un nom unique (ou valide le nom fourni)
    2. Vérifie que le nom est disponible
    3. Crée le Storage Account avec SKU Standard_LRS
    4. Récupère les clés d'accès
    5. Crée le container blob "translations" (optionnel)

    Args:
        resource_group: Nom du Resource Group existant
        region: Région Azure (défaut: "francecentral")
        name: Nom optionnel du Storage Account (si None, généré automatiquement)
        sku: SKU du Storage (défaut: "Standard_LRS" - économique)
        kind: Type de Storage (défaut: "StorageV2" - usage général)
        tags: Tags optionnels pour la ressource
        create_container: Créer automatiquement le container blob (défaut: True)
        container_name: Nom du container blob (défaut: "translations")

    Returns:
        Dict contenant:
            - name: Nom du Storage Account créé
            - id: ID complet de la ressource Azure
            - primary_endpoints: URLs des endpoints (blob, table, queue, file)
            - access_keys: Dict avec key1 et key2 (NON MASQUÉES)
            - access_keys_display: Dict avec clés masquées pour affichage
            - region: Région où le Storage est déployé
            - sku: SKU utilisé
            - kind: Type de Storage
            - container_created: True si container créé
            - container_name: Nom du container (si créé)

    Raises:
        AzureWrapperError: Si la création échoue

    Example:
        >>> result = create_storage_account(
        ...     resource_group="rg-bot-traducteur-acme",
        ...     region="francecentral",
        ...     tags={"client": "Acme Corp"}
        ... )
        >>> print(result["name"])
        tradbot3a7f20260118
        >>> print(result["access_keys_display"]["key1"])
        ****************ABCD
    """

    # Vérification de connexion Azure CLI
    if not check_az_logged_in():
        raise AzureWrapperError(
            "Vous devez être connecté à Azure CLI. Exécutez: az login --tenant <tenant-id>"
        )

    # Validation des paramètres
    validate_azure_region(region)

    # Générer ou valider le nom
    if name is None:
        # Générer un nom unique
        for attempt in range(5):  # 5 tentatives max
            name = _generate_unique_storage_name("tradbot")
            if _check_name_availability(name):
                break
        else:
            raise AzureWrapperError(
                "Impossible de générer un nom unique disponible après 5 tentatives"
            )

        print(f"✅ Nom unique généré: {name}")
    else:
        # Valider le nom fourni
        if len(name) < 3 or len(name) > 24:
            raise AzureWrapperError(
                f"Le nom de Storage Account doit contenir 3-24 caractères (fourni: {len(name)} caractères)"
            )

        if not name.islower() or not name.isalnum():
            raise AzureWrapperError(
                f"Le nom de Storage Account '{name}' doit contenir uniquement des minuscules et des chiffres"
            )

        # Vérifier disponibilité
        if not _check_name_availability(name):
            raise AzureWrapperError(
                f"Le nom de Storage Account '{name}' n'est pas disponible (déjà pris)"
            )

    print(f"🔧 Création d'Azure Storage Account...")
    print(f"   Nom: {name}")
    print(f"   Groupe de ressources: {resource_group}")
    print(f"   Région: {region}")
    print(f"   SKU: {sku} (Locally Redundant Storage)")
    print(f"   Kind: {kind}")
    print()

    # Construction de la commande Azure CLI
    command = [
        "az", "storage", "account", "create",
        "--name", name,
        "--resource-group", resource_group,
        "--location", region,
        "--sku", sku,
        "--kind", kind,
        "--allow-blob-public-access", "false",  # Sécurité: pas d'accès public
        "--min-tls-version", "TLS1_2",  # Sécurité: TLS 1.2 minimum
    ]

    # Ajouter les tags si fournis
    if tags:
        tags_str = " ".join([f"{k}={v}" for k, v in tags.items()])
        command.extend(["--tags", tags_str])

    # Exécution de la commande
    try:
        print("⏳ Création du Storage Account en cours... (environ 30-60 secondes)")
        result = run_az_command(command, timeout=180)  # 3 minutes max

        print("✅ Storage Account créé avec succès !")
        print()

    except AzureWrapperError as e:
        # Gestion d'erreurs spécifiques
        error_msg = str(e)

        if "AccountNameInvalid" in error_msg or "InvalidAccountName" in error_msg:
            raise AzureWrapperError(
                f"Le nom de Storage Account '{name}' est invalide. "
                "Il doit contenir 3-24 caractères, minuscules et chiffres uniquement."
            ) from e

        elif "StorageAccountAlreadyTaken" in error_msg or "AlreadyExists" in error_msg:
            raise AzureWrapperError(
                f"Le nom de Storage Account '{name}' est déjà pris globalement. "
                "Réessayez avec un nom différent ou laissez la génération automatique."
            ) from e

        elif "QuotaExceeded" in error_msg or "quota" in error_msg.lower():
            raise AzureWrapperError(
                f"Quota Azure dépassé pour les Storage Accounts. "
                "Vérifiez les limites de votre subscription ou contactez le support Azure."
            ) from e

        elif "InvalidResourceGroup" in error_msg or "ResourceGroupNotFound" in error_msg:
            raise AzureWrapperError(
                f"Le Resource Group '{resource_group}' n'existe pas. "
                f"Créez-le d'abord avec: az group create --name {resource_group} --location {region}"
            ) from e

        else:
            # Erreur générique
            raise

    # Récupération des endpoints
    print("📋 Récupération des endpoints...")
    endpoints = _get_storage_endpoints(name, resource_group)

    # Récupération des clés d'accès
    print("🔑 Récupération des clés d'accès...")
    access_keys = _get_storage_keys(name, resource_group)

    # Masquer les clés pour affichage
    access_keys_display = {
        "key1": sanitize_credential(access_keys["key1"], visible_chars=4),
        "key2": sanitize_credential(access_keys["key2"], visible_chars=4),
    }

    # Récupération de l'ID de ressource
    resource_id = _get_storage_resource_id(name, resource_group)

    # Créer le container blob si demandé
    container_created = False
    if create_container:
        print(f"📦 Création du container blob '{container_name}'...")
        container_created = create_blob_container(
            account_name=name,
            container_name=container_name,
            account_key=access_keys["key1"]
        )

    print("✅ Configuration complète !")
    print()
    print("📋 Informations du Storage Account:")
    print(f"   Nom: {name}")
    print(f"   Blob Endpoint: {endpoints['blob']}")
    print(f"   Région: {region}")
    print(f"   Clé 1: {access_keys_display['key1']} (masquée pour sécurité)")
    print(f"   Clé 2: {access_keys_display['key2']} (masquée pour sécurité)")
    print(f"   SKU: {sku}")
    if container_created:
        print(f"   Container: {container_name} ✅")
    print()

    return {
        "name": name,
        "id": resource_id,
        "primary_endpoints": endpoints,
        "access_keys": access_keys,  # ⚠️ Clés complètes (SENSIBLE)
        "access_keys_display": access_keys_display,  # Clés masquées
        "region": region,
        "sku": sku,
        "kind": kind,
        "container_created": container_created,
        "container_name": container_name if container_created else None,
    }


def _get_storage_endpoints(name: str, resource_group: str) -> Dict[str, str]:
    """
    Récupère les endpoints du Storage Account

    Args:
        name: Nom du Storage Account
        resource_group: Nom du Resource Group

    Returns:
        Dict avec les endpoints (blob, table, queue, file)

    Raises:
        AzureWrapperError: Si impossible de récupérer les endpoints
    """
    command = [
        "az", "storage", "account", "show",
        "--name", name,
        "--resource-group", resource_group,
        "--query", "primaryEndpoints",
    ]

    result = run_az_command(command)
    endpoints = parse_az_json_output(result["stdout"])

    if not endpoints:
        raise AzureWrapperError(
            f"Impossible de récupérer les endpoints pour le Storage Account '{name}'"
        )

    return endpoints


def _get_storage_keys(name: str, resource_group: str) -> Dict[str, str]:
    """
    Récupère les clés d'accès du Storage Account

    Args:
        name: Nom du Storage Account
        resource_group: Nom du Resource Group

    Returns:
        Dict avec key1 et key2 (NON MASQUÉES)

    Raises:
        AzureWrapperError: Si impossible de récupérer les clés
    """
    command = [
        "az", "storage", "account", "keys", "list",
        "--account-name", name,
        "--resource-group", resource_group,
    ]

    result = run_az_command(command)
    keys_list = parse_az_json_output(result["stdout"])

    if not keys_list or len(keys_list) < 2:
        raise AzureWrapperError(
            f"Impossible de récupérer les clés d'accès pour le Storage Account '{name}'"
        )

    return {
        "key1": keys_list[0]["value"],
        "key2": keys_list[1]["value"],
    }


def _get_storage_resource_id(name: str, resource_group: str) -> str:
    """
    Récupère l'ID complet de la ressource Storage Account

    Args:
        name: Nom du Storage Account
        resource_group: Nom du Resource Group

    Returns:
        ID de ressource Azure

    Raises:
        AzureWrapperError: Si impossible de récupérer l'ID
    """
    command = [
        "az", "storage", "account", "show",
        "--name", name,
        "--resource-group", resource_group,
        "--query", "id",
        "--output", "tsv",
    ]

    result = run_az_command(command)
    resource_id = result["stdout"].strip()

    if not resource_id:
        raise AzureWrapperError(
            f"Impossible de récupérer l'ID de ressource pour le Storage Account '{name}'"
        )

    return resource_id


def create_blob_container(
    account_name: str,
    container_name: str,
    account_key: str,
) -> bool:
    """
    Crée un container blob dans le Storage Account

    Args:
        account_name: Nom du Storage Account
        container_name: Nom du container à créer
        account_key: Clé d'accès du Storage Account

    Returns:
        True si créé avec succès

    Raises:
        AzureWrapperError: Si la création échoue

    Example:
        >>> created = create_blob_container(
        ...     account_name="tradbot3a7f20260118",
        ...     container_name="translations",
        ...     account_key="your-access-key"
        ... )
        >>> print(created)
        True
    """
    command = [
        "az", "storage", "container", "create",
        "--name", container_name,
        "--account-name", account_name,
        "--account-key", account_key,
        "--public-access", "off",  # Sécurité: pas d'accès public
    ]

    try:
        result = run_az_command(command, timeout=60)
        container_info = parse_az_json_output(result["stdout"])

        # Vérifier que la création a réussi
        if container_info.get("created", False):
            print(f"   ✅ Container '{container_name}' créé")
            return True
        else:
            # Container existe déjà
            print(f"   ℹ️  Container '{container_name}' existe déjà")
            return True

    except AzureWrapperError as e:
        if "ContainerAlreadyExists" in str(e):
            print(f"   ℹ️  Container '{container_name}' existe déjà")
            return True
        raise


def verify_storage_account(name: str, resource_group: str) -> Dict[str, Any]:
    """
    Vérifie qu'un Storage Account existe et est actif

    Args:
        name: Nom du Storage Account
        resource_group: Nom du Resource Group

    Returns:
        Dict contenant:
            - exists: True si le Storage Account existe
            - provisioning_state: État du provisioning
            - sku: SKU utilisé
            - kind: Type de Storage
            - primary_location: Région primaire

    Raises:
        AzureWrapperError: Si la vérification échoue

    Example:
        >>> result = verify_storage_account("tradbot3a7f20260118", "rg-test")
        >>> if result["provisioning_state"] == "Succeeded":
        ...     print("✅ Storage Account actif")
    """
    print(f"🔍 Vérification du Storage Account '{name}'...")

    command = [
        "az", "storage", "account", "show",
        "--name", name,
        "--resource-group", resource_group,
    ]

    try:
        result = run_az_command(command, check=False)

        if not result["success"]:
            return {
                "exists": False,
                "provisioning_state": "NotFound",
                "sku": None,
                "kind": None,
                "primary_location": None,
            }

        # Parser la sortie JSON
        storage_info = parse_az_json_output(result["stdout"])

        provisioning_state = storage_info.get("provisioningState", "Unknown")
        sku = storage_info.get("sku", {}).get("name", "Unknown")
        kind = storage_info.get("kind", "Unknown")
        primary_location = storage_info.get("primaryLocation", "Unknown")

        print(f"   État: {provisioning_state}")
        print(f"   SKU: {sku}")
        print(f"   Kind: {kind}")
        print(f"   Région: {primary_location}")

        if provisioning_state != "Succeeded":
            print(f"   ⚠️  Le Storage Account n'est pas encore prêt (état: {provisioning_state})")
        else:
            print(f"   ✅ Storage Account actif et opérationnel")

        print()

        return {
            "exists": True,
            "provisioning_state": provisioning_state,
            "sku": sku,
            "kind": kind,
            "primary_location": primary_location,
        }

    except AzureWrapperError as e:
        raise AzureWrapperError(
            f"Erreur lors de la vérification du Storage Account '{name}': {str(e)}"
        ) from e


def delete_storage_account(name: str, resource_group: str, yes: bool = False) -> bool:
    """
    Supprime un Azure Storage Account

    ⚠️ ATTENTION: Cette opération est IRRÉVERSIBLE et supprime TOUTES les données

    Args:
        name: Nom du Storage Account
        resource_group: Nom du Resource Group
        yes: Confirmer la suppression sans demander (défaut: False)

    Returns:
        True si la suppression a réussi

    Raises:
        AzureWrapperError: Si la suppression échoue

    Example:
        >>> delete_storage_account("tradbot-test", "rg-test", yes=True)
        True
    """
    if not yes:
        print(f"⚠️  Vous êtes sur le point de SUPPRIMER le Storage Account '{name}'")
        print(f"   Resource Group: {resource_group}")
        print(f"   ⚠️  TOUTES LES DONNÉES SERONT PERDUES")
        print()
        response = input("   Confirmer la suppression ? (oui/non): ").strip().lower()

        if response not in ["oui", "yes", "y"]:
            print("❌ Suppression annulée")
            return False

    print(f"🗑️  Suppression du Storage Account '{name}'...")

    command = [
        "az", "storage", "account", "delete",
        "--name", name,
        "--resource-group", resource_group,
        "--yes",
    ]

    try:
        run_az_command(command, timeout=120)
        print(f"✅ Storage Account '{name}' supprimé avec succès")
        return True

    except AzureWrapperError as e:
        raise AzureWrapperError(
            f"Erreur lors de la suppression du Storage Account '{name}': {str(e)}"
        ) from e
