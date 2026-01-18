"""
Azure Translator Wrapper - Déploiement Azure Translator avec SKU F0

⚠️ CRITIQUE: Ce module déploie Azure Translator avec SKU F0 (GRATUIT) UNIQUEMENT

SKU F0 vs SKU Payants:
- F0 (Free): 0 EUR/mois, 2M caractères/mois - SUFFISANT pour usage professionnel
- S0 (Standard): 35 USD/mois minimum - COÛT NON BUDGÉTÉ

❌ NE JAMAIS MODIFIER LE SKU F0 HARDCODÉ DANS CE CODE ❌

Si un client a besoin de plus de 2M caractères/mois, cela doit être
une décision explicite documentée APRÈS validation du besoin réel.
"""

import time
from typing import Dict, Any, Optional
from .common import (
    run_az_command,
    parse_az_json_output,
    validate_resource_name,
    validate_azure_region,
    sanitize_credential,
    AzureWrapperError,
    check_az_logged_in,
)


# ============================================================================
# ⚠️ CONSTANTE CRITIQUE - NE PAS MODIFIER ⚠️
# ============================================================================
# Le SKU F0 est HARDCODÉ pour éviter toute erreur coûteuse.
# Modifier cette valeur pourrait entraîner des coûts non budgétés pour le client.
# F0 = Gratuit (2M caractères/mois)
# S0/S1/S2/S3/S4 = Payant (à partir de 35 USD/mois)
# ============================================================================
TRANSLATOR_SKU_F0 = "F0"  # ❌ NE PAS MODIFIER - SKU F0 OBLIGATOIRE ❌
# ============================================================================


def _purge_soft_deleted_translators() -> int:
    """
    Purge tous les services Translator soft-deleted pour libérer le quota F0.
    
    Azure ne permet qu'un seul service Translator F0 par subscription.
    Les services supprimés restent en soft-deleted et comptent contre le quota.
    Cette fonction les purge définitivement.
    
    Returns:
        Nombre de services purgés
        
    Raises:
        AzureWrapperError: Si le listage ou le purge échoue
    """
    try:
        # Lister les services soft-deleted
        list_cmd = ["az", "cognitiveservices", "account", "list-deleted", "--output", "json"]
        result = run_az_command(list_cmd)
        
        import json
        soft_deleted = json.loads(result["stdout"])
        
        # Filtrer uniquement les TextTranslation
        translator_deleted = [
            svc for svc in soft_deleted 
            if svc.get("kind") == "TextTranslation"
        ]
        
        if not translator_deleted:
            return 0
        
        print(f"⚠️  Détecté {len(translator_deleted)} service(s) Translator soft-deleted bloquant le quota F0")
        print("🧹 Purge automatique en cours...")
        
        purged_count = 0
        for svc in translator_deleted:
            name = svc.get("name")
            location = svc.get("location")

            # Extraire le resource group de l'id
            # Format: /subscriptions/.../resourceGroups/RG_NAME/deletedAccounts/...
            svc_id = svc.get("id", "")
            resource_group = ""
            if "/resourceGroups/" in svc_id:
                parts = svc_id.split("/resourceGroups/")[1].split("/")
                resource_group = parts[0] if parts else ""

            if not name or not location or not resource_group:
                continue
            
            try:
                purge_cmd = [
                    "az", "cognitiveservices", "account", "purge",
                    "--name", name,
                    "--resource-group", resource_group,
                    "--location", location
                ]
                run_az_command(purge_cmd, timeout=30)
                print(f"   ✅ Purgé: {name} ({location})")
                purged_count += 1
            except Exception as e:
                print(f"   ⚠️  Échec du purge de {name}: {e}")
                continue
        
        print(f"✅ {purged_count} service(s) purgé(s) - Quota F0 libéré")
        print()
        return purged_count
        
    except Exception as e:
        # Ne pas bloquer la création si le purge échoue
        print(f"⚠️  Avertissement: Impossible de purger les services soft-deleted: {e}")
        return 0


def create_translator(
    name: str,
    resource_group: str,
    region: str = "francecentral",
    tags: Optional[Dict[str, str]] = None,
) -> Dict[str, Any]:
    """
    Crée un service Azure Translator avec SKU F0 (GRATUIT)

    ⚠️ IMPORTANT: Le SKU F0 est HARDCODÉ dans cette fonction.
    Il n'y a AUCUN paramètre pour modifier le SKU.
    Ceci est intentionnel pour éviter les coûts non budgétés.

    Args:
        name: Nom du service Translator (ex: "translator-acme-20260118")
        resource_group: Nom du Resource Group existant
        region: Région Azure (défaut: "francecentral")
        tags: Tags optionnels pour la ressource (ex: {"client": "Acme Corp"})

    Returns:
        Dict contenant:
            - name: Nom du service créé
            - id: ID complet de la ressource Azure
            - endpoint: URL de l'endpoint Translator
            - key: Clé d'API (masquée dans les logs)
            - key_display: Clé partiellement masquée pour affichage
            - region: Région où le service est déployé
            - sku: SKU utilisé (toujours F0)

    Raises:
        AzureWrapperError: Si la création échoue

    Example:
        >>> result = create_translator(
        ...     name="translator-acme-20260118",
        ...     resource_group="rg-bot-traducteur-acme",
        ...     region="francecentral",
        ...     tags={"client": "Acme Corp", "project": "Bot Traducteur"}
        ... )
        >>> print(result["endpoint"])
        https://api.cognitive.microsofttranslator.com/
        >>> print(result["key_display"])
        ****************ABCD
    """

    # Vérification de connexion Azure CLI
    if not check_az_logged_in():
        raise AzureWrapperError(
            "Vous devez être connecté à Azure CLI. Exécutez: az login --tenant <tenant-id>"
        )

    # Validation des paramètres
    validate_resource_name(name, "Translator")
    validate_resource_name(resource_group, "Resource Group")
    validate_azure_region(region)

    print(f"🔧 Création d'Azure Translator...")
    print(f"   Nom: {name}")
    print(f"   Groupe de ressources: {resource_group}")
    print(f"   Région: {region}")
    print(f"   ⚠️  SKU: {TRANSLATOR_SKU_F0} (GRATUIT - 2M caractères/mois)")
    print()

    # Construction de la commande Azure CLI
    command = [
        "az", "cognitiveservices", "account", "create",
        "--name", name,
        "--resource-group", resource_group,
        "--kind", "TextTranslation",
        "--sku", TRANSLATOR_SKU_F0,  # ❌ SKU F0 HARDCODÉ - NE PAS MODIFIER ❌
        "--location", region,
        "--yes",  # Accepter automatiquement les conditions
    ]

    # Ajouter les tags si fournis
    if tags:
        tags_str = " ".join([f"{k}={v}" for k, v in tags.items()])
        command.extend(["--tags", tags_str])

    # Exécution de la commande (avec retry automatique si quota F0 bloqué)
    retry_attempted = False
    while True:
        try:
            print("⏳ Création du service Translator en cours... (environ 1 minute)")
            result = run_az_command(command, timeout=180)  # 3 minutes max

            print("✅ Service Translator créé avec succès !")
            print()
            break  # Succès, sortir de la boucle

        except AzureWrapperError as e:
            # Gestion d'erreurs spécifiques
            error_msg = str(e)

            if "ResourceExists" in error_msg or "AlreadyExists" in error_msg:
                raise AzureWrapperError(
                    f"Le service Translator '{name}' existe déjà dans le Resource Group '{resource_group}'. "
                    "Utilisez un nom différent ou supprimez le service existant."
                ) from e

            elif "CanNotCreateMultipleFreeAccounts" in error_msg:
                # Quota F0 bloqué par services soft-deleted
                if retry_attempted:
                    # Déjà essayé une fois, ne pas boucler
                    raise AzureWrapperError(
                        "Impossible de créer le service Translator F0 malgré le purge des services soft-deleted. "
                        "Vérifiez qu'il n'existe pas déjà un service Translator F0 actif dans votre subscription."
                    ) from e

                # Première tentative de résolution automatique
                print()
                print("⚠️  ERREUR: Quota F0 atteint (1 seul service Translator F0 autorisé par subscription)")
                _purge_soft_deleted_translators()

                # Toujours réessayer une fois, même si le purge a échoué
                # (le service peut avoir été purgé manuellement ou il y a un délai de propagation)
                print("🔄 Nouvelle tentative de création...")
                print()
                retry_attempted = True
                continue  # Réessayer la boucle

            elif "QuotaExceeded" in error_msg or "quota" in error_msg.lower():
                raise AzureWrapperError(
                    f"Quota Azure dépassé pour les services Cognitive Services. "
                    "Vérifiez les limites de votre subscription ou contactez le support Azure."
                ) from e

            elif "InvalidResourceGroup" in error_msg:
                raise AzureWrapperError(
                    f"Le Resource Group '{resource_group}' n'existe pas. "
                    "Créez-le d'abord avec: az group create --name {resource_group} --location {region}"
                ) from e

            else:
                # Erreur générique
                raise

    # Récupération de l'endpoint
    print("📋 Récupération de l'endpoint...")
    endpoint = _get_translator_endpoint(name, resource_group)

    # Récupération de la clé (masquée)
    print("🔑 Récupération de la clé d'API...")
    key = _get_translator_key(name, resource_group)
    key_display = sanitize_credential(key, visible_chars=4)

    # Récupération de l'ID de ressource
    resource_id = _get_translator_resource_id(name, resource_group)

    print("✅ Configuration complète !")
    print()
    print("📋 Informations du service Translator:")
    print(f"   Nom: {name}")
    print(f"   Endpoint: {endpoint}")
    print(f"   Région: {region}")
    print(f"   Clé API: {key_display} (masquée pour sécurité)")
    print(f"   SKU: {TRANSLATOR_SKU_F0} (Gratuit)")
    print()

    return {
        "name": name,
        "id": resource_id,
        "endpoint": endpoint,
        "key": key,  # Clé complète (à ne jamais logger)
        "key_display": key_display,  # Clé masquée pour affichage
        "region": region,
        "sku": TRANSLATOR_SKU_F0,  # Toujours F0
    }


def _get_translator_endpoint(name: str, resource_group: str) -> str:
    """
    Récupère l'endpoint du service Translator

    Args:
        name: Nom du service Translator
        resource_group: Nom du Resource Group

    Returns:
        URL de l'endpoint (ex: "https://api.cognitive.microsofttranslator.com/")

    Raises:
        AzureWrapperError: Si impossible de récupérer l'endpoint
    """
    command = [
        "az", "cognitiveservices", "account", "show",
        "--name", name,
        "--resource-group", resource_group,
        "--query", "properties.endpoint",
        "--output", "tsv",
    ]

    result = run_az_command(command)
    endpoint = result["stdout"].strip()

    if not endpoint:
        raise AzureWrapperError(
            f"Impossible de récupérer l'endpoint pour le Translator '{name}'"
        )

    return endpoint


def _get_translator_key(name: str, resource_group: str) -> str:
    """
    Récupère la clé d'API du service Translator

    Args:
        name: Nom du service Translator
        resource_group: Nom du Resource Group

    Returns:
        Clé d'API (non masquée)

    Raises:
        AzureWrapperError: Si impossible de récupérer la clé
    """
    command = [
        "az", "cognitiveservices", "account", "keys", "list",
        "--name", name,
        "--resource-group", resource_group,
        "--query", "key1",
        "--output", "tsv",
    ]

    result = run_az_command(command)
    key = result["stdout"].strip()

    if not key:
        raise AzureWrapperError(
            f"Impossible de récupérer la clé d'API pour le Translator '{name}'"
        )

    return key


def _get_translator_resource_id(name: str, resource_group: str) -> str:
    """
    Récupère l'ID complet de la ressource Translator

    Args:
        name: Nom du service Translator
        resource_group: Nom du Resource Group

    Returns:
        ID de ressource Azure (format: /subscriptions/.../resourceGroups/...)

    Raises:
        AzureWrapperError: Si impossible de récupérer l'ID
    """
    command = [
        "az", "cognitiveservices", "account", "show",
        "--name", name,
        "--resource-group", resource_group,
        "--query", "id",
        "--output", "tsv",
    ]

    result = run_az_command(command)
    resource_id = result["stdout"].strip()

    if not resource_id:
        raise AzureWrapperError(
            f"Impossible de récupérer l'ID de ressource pour le Translator '{name}'"
        )

    return resource_id


def verify_translator(name: str, resource_group: str) -> Dict[str, Any]:
    """
    Vérifie qu'un service Translator existe et est actif

    Cette fonction est utile pour :
    - Vérifier qu'un déploiement précédent a réussi
    - Confirmer que le service est dans l'état "Succeeded"
    - Valider que le SKU F0 est bien utilisé

    Args:
        name: Nom du service Translator
        resource_group: Nom du Resource Group

    Returns:
        Dict contenant:
            - exists: True si le service existe
            - state: État du service ("Succeeded", "Creating", etc.)
            - sku: SKU utilisé (doit être F0)
            - sku_is_f0: True si SKU est bien F0
            - endpoint: URL de l'endpoint

    Raises:
        AzureWrapperError: Si la vérification échoue

    Example:
        >>> result = verify_translator("translator-acme-20260118", "rg-bot-traducteur-acme")
        >>> if result["sku_is_f0"]:
        ...     print("✅ SKU F0 confirmé")
        >>> if result["state"] == "Succeeded":
        ...     print("✅ Service actif")
    """

    print(f"🔍 Vérification du service Translator '{name}'...")

    command = [
        "az", "cognitiveservices", "account", "show",
        "--name", name,
        "--resource-group", resource_group,
    ]

    try:
        result = run_az_command(command, check=False)

        if not result["success"]:
            return {
                "exists": False,
                "state": "NotFound",
                "sku": None,
                "sku_is_f0": False,
                "endpoint": None,
            }

        # Parser la sortie JSON
        translator_info = parse_az_json_output(result["stdout"])

        state = translator_info.get("properties", {}).get("provisioningState", "Unknown")
        sku = translator_info.get("sku", {}).get("name", "Unknown")
        endpoint = translator_info.get("properties", {}).get("endpoint", "")

        sku_is_f0 = sku == TRANSLATOR_SKU_F0

        print(f"   État: {state}")
        print(f"   SKU: {sku}")
        print(f"   Endpoint: {endpoint}")

        if not sku_is_f0:
            print(f"   ⚠️  ATTENTION: Le SKU '{sku}' n'est PAS F0 (gratuit) !")
        else:
            print(f"   ✅ SKU F0 confirmé (gratuit)")

        if state != "Succeeded":
            print(f"   ⚠️  Le service n'est pas encore prêt (état: {state})")
        else:
            print(f"   ✅ Service actif et opérationnel")

        print()

        return {
            "exists": True,
            "state": state,
            "sku": sku,
            "sku_is_f0": sku_is_f0,
            "endpoint": endpoint,
        }

    except AzureWrapperError as e:
        raise AzureWrapperError(
            f"Erreur lors de la vérification du Translator '{name}': {str(e)}"
        ) from e


def delete_translator(name: str, resource_group: str, yes: bool = False) -> bool:
    """
    Supprime un service Azure Translator

    ⚠️ ATTENTION: Cette opération est IRRÉVERSIBLE

    Args:
        name: Nom du service Translator
        resource_group: Nom du Resource Group
        yes: Confirmer la suppression sans demander (défaut: False)

    Returns:
        True si la suppression a réussi

    Raises:
        AzureWrapperError: Si la suppression échoue

    Example:
        >>> delete_translator("translator-test-20260118", "rg-test", yes=True)
        True
    """

    if not yes:
        print(f"⚠️  Vous êtes sur le point de SUPPRIMER le service Translator '{name}'")
        print(f"   Resource Group: {resource_group}")
        print()
        response = input("   Confirmer la suppression ? (oui/non): ").strip().lower()

        if response not in ["oui", "yes", "y"]:
            print("❌ Suppression annulée")
            return False

    print(f"🗑️  Suppression du service Translator '{name}'...")

    command = [
        "az", "cognitiveservices", "account", "delete",
        "--name", name,
        "--resource-group", resource_group,
        "--yes",
    ]

    try:
        run_az_command(command, timeout=120)
        print(f"✅ Service Translator '{name}' supprimé avec succès")
        return True

    except AzureWrapperError as e:
        raise AzureWrapperError(
            f"Erreur lors de la suppression du Translator '{name}': {str(e)}"
        ) from e
