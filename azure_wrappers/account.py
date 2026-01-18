"""
Azure Account Management - Gestion des comptes et subscriptions Azure

Ce module fournit des wrappers Python pour gérer les comptes Azure CLI,
permettant aux techniciens de se connecter avec différents comptes (délégué,
admin créé) et de gérer plusieurs subscriptions.

Author: Aux Petits Oignons Team
Version: 1.3.0
Story: STORY-009 (Support Multi-comptes Azure dans OpenCode)
"""

import json
import subprocess
from typing import Dict, Any, Optional, List

from .common import (
    run_az_command,
    AzureWrapperError,
)

# ============================================
# Constants
# ============================================

# Rôles Azure avec permissions suffisantes pour déploiement
REQUIRED_ROLES = [
    "Owner",
    "Contributor",
    "Co-Administrator",
]

# Messages en français pour guidance
GUIDANCE_MESSAGES = {
    "login_prompt": """
╔════════════════════════════════════════════════════════════════╗
║  🔐 CONNEXION À AZURE CLI                                       ║
╚════════════════════════════════════════════════════════════════╝

Pour déployer les ressources Azure, vous devez vous connecter avec:
  • Un compte DÉLÉGUÉ avec permissions Contributor/Owner
  • OU un compte ADMIN créé par le client

La connexion utilise le "Device Flow" (code de vérification):
  1. Un code sera affiché dans le terminal
  2. Ouvrez https://microsoft.com/devicelogin dans votre navigateur
  3. Entrez le code affiché
  4. Authentifiez-vous avec vos identifiants Azure

Appuyez sur Entrée pour lancer la connexion...
""",
    "login_device_flow": """
🔑 Connexion en cours avec Device Flow...

➤ Un code va s'afficher ci-dessous
➤ Ouvrez: https://microsoft.com/devicelogin
➤ Entrez le code et authentifiez-vous
""",
    "multiple_accounts": """
╔════════════════════════════════════════════════════════════════╗
║  ⚠️  PLUSIEURS COMPTES DÉTECTÉS                                 ║
╚════════════════════════════════════════════════════════════════╝

Plusieurs subscriptions Azure sont disponibles.
Veuillez sélectionner la subscription à utiliser pour ce déploiement.
""",
    "no_permissions": """
╔════════════════════════════════════════════════════════════════╗
║  ❌ PERMISSIONS INSUFFISANTES                                   ║
╚════════════════════════════════════════════════════════════════╝

Le compte connecté n'a PAS les permissions nécessaires pour déployer
des ressources Azure dans cette subscription.

Permissions requises:
  • Owner (Propriétaire)
  • Contributor (Contributeur)
  • Co-Administrator (Co-administrateur)

Solutions possibles:
  1. Demandez au client de vous accorder un rôle Contributor
  2. Connectez-vous avec un compte ayant les permissions appropriées
  3. Utilisez un compte ADMIN créé spécialement pour ce déploiement

Voulez-vous vous reconnecter avec un autre compte ? (o/n)
""",
    "reconnect_prompt": """
╔════════════════════════════════════════════════════════════════╗
║  🔄 RECONNEXION                                                 ║
╚════════════════════════════════════════════════════════════════╝

Pour vous reconnecter avec un autre compte:
  1. Nous allons d'abord vous déconnecter du compte actuel
  2. Puis vous pourrez vous reconnecter avec vos nouveaux identifiants

Appuyez sur Entrée pour continuer...
""",
}


# ============================================
# Login & Logout
# ============================================


def login_azure(use_device_code: bool = True) -> Dict[str, Any]:
    """
    Guide le technicien pour se connecter à Azure CLI avec device flow.

    Args:
        use_device_code: Utiliser device code flow (défaut: True)
                        Si False, utilise le navigateur classique

    Returns:
        Dict avec:
            - success: True si connexion réussie
            - account_count: Nombre de subscriptions disponibles
            - current_subscription: Subscription actuellement sélectionnée
            - message: Message de guidance en français

    Raises:
        AzureWrapperError: Si connexion échoue
    """
    # Afficher le message de guidance
    print(GUIDANCE_MESSAGES["login_prompt"])
    input()  # Attendre que l'utilisateur appuie sur Entrée

    # Construire la commande de login
    if use_device_code:
        print(GUIDANCE_MESSAGES["login_device_flow"])
        cmd = ["az", "login", "--use-device-code"]
    else:
        cmd = ["az", "login"]

    try:
        # Exécuter la connexion (Azure CLI gère l'interaction utilisateur)
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=True,
        )

        # Récupérer les informations des comptes après connexion
        accounts = list_accounts()

        return {
            "success": True,
            "account_count": len(accounts),
            "current_subscription": get_current_account(),
            "message": f"✅ Connexion réussie! {len(accounts)} subscription(s) disponible(s)",
        }

    except subprocess.CalledProcessError as e:
        error_msg = e.stderr if e.stderr else str(e)
        raise AzureWrapperError(f"Échec de connexion Azure CLI: {error_msg}")


def logout_azure() -> bool:
    """
    Déconnecte le compte Azure CLI actuel.

    Returns:
        True si déconnexion réussie

    Raises:
        AzureWrapperError: Si déconnexion échoue
    """
    cmd = ["az", "logout"]

    try:
        run_az_command(cmd)
        return True

    except subprocess.CalledProcessError as e:
        error_msg = e.stderr if e.stderr else str(e)
        raise AzureWrapperError(f"Échec de déconnexion: {error_msg}")


# ============================================
# Account Listing & Selection
# ============================================


def list_accounts() -> List[Dict[str, Any]]:
    """
    Liste toutes les subscriptions Azure disponibles pour le compte connecté.

    Returns:
        Liste de dict avec pour chaque subscription:
            - id: ID de la subscription
            - name: Nom de la subscription
            - is_default: True si c'est la subscription par défaut
            - state: État (Enabled, Disabled, etc.)
            - tenant_id: ID du tenant Azure AD

    Raises:
        AzureWrapperError: Si listage échoue ou aucun compte connecté
    """
    cmd = ["az", "account", "list", "--output", "json"]

    try:
        result = run_az_command(cmd)
        accounts = json.loads(result["stdout"])

        # Formater les informations
        formatted_accounts = []
        for account in accounts:
            formatted_accounts.append({
                "id": account.get("id", ""),
                "name": account.get("name", ""),
                "is_default": account.get("isDefault", False),
                "state": account.get("state", ""),
                "tenant_id": account.get("tenantId", ""),
            })

        return formatted_accounts

    except subprocess.CalledProcessError as e:
        error_msg = e.stderr if e.stderr else str(e)

        if "az login" in error_msg or "not logged in" in error_msg.lower():
            raise AzureWrapperError(
                "Aucun compte connecté. Utilisez login_azure() pour vous connecter."
            )
        else:
            raise AzureWrapperError(f"Échec du listage des comptes: {error_msg}")


def get_current_account() -> Dict[str, Any]:
    """
    Récupère les informations du compte/subscription actuellement sélectionné.

    Returns:
        Dict avec:
            - id: ID de la subscription
            - name: Nom de la subscription
            - tenant_id: ID du tenant
            - state: État de la subscription
            - user: Informations sur l'utilisateur connecté

    Raises:
        AzureWrapperError: Si récupération échoue
    """
    cmd = ["az", "account", "show", "--output", "json"]

    try:
        result = run_az_command(cmd)
        account = json.loads(result["stdout"])

        return {
            "id": account.get("id", ""),
            "name": account.get("name", ""),
            "tenant_id": account.get("tenantId", ""),
            "state": account.get("state", ""),
            "user": account.get("user", {}),
        }

    except subprocess.CalledProcessError as e:
        error_msg = e.stderr if e.stderr else str(e)
        raise AzureWrapperError(f"Échec de récupération du compte actuel: {error_msg}")


def select_account(subscription_id: str) -> Dict[str, Any]:
    """
    Sélectionne une subscription Azure spécifique comme active.

    Args:
        subscription_id: ID de la subscription à sélectionner

    Returns:
        Dict avec les informations de la subscription sélectionnée

    Raises:
        AzureWrapperError: Si sélection échoue
    """
    if not subscription_id:
        raise AzureWrapperError("ID de subscription requis")

    cmd = [
        "az", "account", "set",
        "--subscription", subscription_id,
    ]

    try:
        run_az_command(cmd)

        # Récupérer et retourner les infos de la subscription sélectionnée
        return get_current_account()

    except subprocess.CalledProcessError as e:
        error_msg = e.stderr if e.stderr else str(e)

        if "not found" in error_msg.lower():
            raise AzureWrapperError(f"Subscription '{subscription_id}' introuvable")
        else:
            raise AzureWrapperError(f"Échec de sélection de la subscription: {error_msg}")


def select_account_interactive() -> Dict[str, Any]:
    """
    Permet à l'utilisateur de sélectionner interactivement une subscription
    si plusieurs sont disponibles.

    Returns:
        Dict avec les informations de la subscription sélectionnée

    Raises:
        AzureWrapperError: Si sélection échoue
    """
    # Lister les comptes disponibles
    accounts = list_accounts()

    if len(accounts) == 0:
        raise AzureWrapperError("Aucune subscription disponible")

    if len(accounts) == 1:
        # Une seule subscription, la sélectionner automatiquement
        return select_account(accounts[0]["id"])

    # Plusieurs subscriptions: afficher le menu
    print(GUIDANCE_MESSAGES["multiple_accounts"])
    print("\nSubscriptions disponibles:\n")

    for i, account in enumerate(accounts, 1):
        default_marker = " [ACTUELLE]" if account["is_default"] else ""
        print(f"  {i}. {account['name']}")
        print(f"     ID: {account['id']}{default_marker}")
        print(f"     État: {account['state']}")
        print()

    # Demander à l'utilisateur de choisir
    while True:
        try:
            choice = input(f"Sélectionnez une subscription (1-{len(accounts)}): ")
            index = int(choice) - 1

            if 0 <= index < len(accounts):
                selected = accounts[index]
                return select_account(selected["id"])
            else:
                print(f"❌ Choix invalide. Entrez un nombre entre 1 et {len(accounts)}")
        except ValueError:
            print("❌ Entrée invalide. Entrez un nombre")
        except KeyboardInterrupt:
            raise AzureWrapperError("Sélection annulée par l'utilisateur")


# ============================================
# Permissions Verification
# ============================================


def check_permissions(subscription_id: Optional[str] = None) -> Dict[str, Any]:
    """
    Vérifie que l'utilisateur a les permissions nécessaires pour déployer
    des ressources Azure (Contributor, Owner, ou Co-Administrator).

    Args:
        subscription_id: ID de la subscription à vérifier (défaut: subscription actuelle)

    Returns:
        Dict avec:
            - has_permissions: True si permissions suffisantes
            - roles: Liste des rôles attribués
            - required_roles: Liste des rôles requis
            - message: Message explicatif en français

    Raises:
        AzureWrapperError: Si vérification échoue
    """
    # Utiliser la subscription actuelle si non spécifiée
    if not subscription_id:
        current = get_current_account()
        subscription_id = current["id"]

    cmd = [
        "az", "role", "assignment", "list",
        "--assignee", "@me",  # Utilisateur actuel
        "--scope", f"/subscriptions/{subscription_id}",
        "--output", "json",
    ]

    try:
        result = run_az_command(cmd)
        assignments = json.loads(result["stdout"])

        # Extraire les rôles
        user_roles = [assignment.get("roleDefinitionName", "") for assignment in assignments]

        # Vérifier si l'utilisateur a un rôle requis
        has_permissions = any(role in REQUIRED_ROLES for role in user_roles)

        if has_permissions:
            message = f"✅ Permissions suffisantes: {', '.join(user_roles)}"
        else:
            message = (
                f"❌ Permissions insuffisantes\n"
                f"Rôles actuels: {', '.join(user_roles) if user_roles else 'Aucun'}\n"
                f"Rôles requis: {', '.join(REQUIRED_ROLES)}"
            )

        return {
            "has_permissions": has_permissions,
            "roles": user_roles,
            "required_roles": REQUIRED_ROLES,
            "message": message,
        }

    except subprocess.CalledProcessError as e:
        error_msg = e.stderr if e.stderr else str(e)
        raise AzureWrapperError(f"Échec de vérification des permissions: {error_msg}")


def prompt_insufficient_permissions() -> bool:
    """
    Affiche un message si les permissions sont insuffisantes et demande
    si l'utilisateur veut se reconnecter.

    Returns:
        True si l'utilisateur veut se reconnecter, False sinon
    """
    print(GUIDANCE_MESSAGES["no_permissions"])

    while True:
        choice = input().strip().lower()
        if choice in ["o", "oui", "y", "yes"]:
            return True
        elif choice in ["n", "non", "no"]:
            return False
        else:
            print("Répondez par 'o' (oui) ou 'n' (non): ", end="")


def reconnect_azure() -> Dict[str, Any]:
    """
    Guide l'utilisateur pour se déconnecter puis se reconnecter avec
    un autre compte.

    Returns:
        Dict avec les informations de connexion (comme login_azure())

    Raises:
        AzureWrapperError: Si reconnexion échoue
    """
    print(GUIDANCE_MESSAGES["reconnect_prompt"])
    input()  # Attendre confirmation

    # Déconnexion
    print("\n🔓 Déconnexion en cours...")
    logout_azure()
    print("✅ Déconnexion réussie\n")

    # Reconnexion
    return login_azure()


# ============================================
# Complete Workflow
# ============================================


def ensure_logged_in_with_permissions() -> Dict[str, Any]:
    """
    Fonction complète qui s'assure que l'utilisateur est connecté avec
    les permissions appropriées.

    Ce workflow:
    1. Vérifie si un compte est connecté, sinon guide pour login
    2. Liste les subscriptions disponibles
    3. Permet de sélectionner si plusieurs subscriptions
    4. Vérifie les permissions
    5. Propose de se reconnecter si permissions insuffisantes

    Returns:
        Dict avec:
            - account: Informations du compte sélectionné
            - permissions: Résultat de la vérification des permissions
            - ready: True si tout est prêt pour déploiement

    Raises:
        AzureWrapperError: Si workflow échoue
    """
    # Step 1: Vérifier si connecté
    try:
        current = get_current_account()
        print(f"\n✅ Déjà connecté: {current['name']}\n")
    except AzureWrapperError:
        # Pas connecté, guider pour login
        login_result = login_azure()
        print(f"\n{login_result['message']}\n")

    # Step 2: Sélectionner la subscription si plusieurs
    accounts = list_accounts()
    if len(accounts) > 1:
        account = select_account_interactive()
        print(f"\n✅ Subscription sélectionnée: {account['name']}\n")
    else:
        account = get_current_account()

    # Step 3: Vérifier les permissions
    permissions = check_permissions(account["id"])
    print(f"\n{permissions['message']}\n")

    if not permissions["has_permissions"]:
        # Permissions insuffisantes, proposer reconnexion
        if prompt_insufficient_permissions():
            # Reconnexion demandée
            login_result = reconnect_azure()
            # Revérifier les permissions
            account = get_current_account()
            permissions = check_permissions(account["id"])
            print(f"\n{permissions['message']}\n")

            if not permissions["has_permissions"]:
                raise AzureWrapperError(
                    "Les permissions sont toujours insuffisantes après reconnexion"
                )
        else:
            raise AzureWrapperError("Déploiement annulé: permissions insuffisantes")

    return {
        "account": account,
        "permissions": permissions,
        "ready": True,
    }
