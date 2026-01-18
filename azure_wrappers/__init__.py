"""
Azure Wrappers - Modules Python pour automatiser le déploiement Azure

Ce package contient les wrappers Python pour les commandes Azure CLI,
permettant à OpenCode de déployer automatiquement les ressources Azure
nécessaires au Bot Traducteur.

Modules disponibles:
- translator: Déploiement Azure Translator (SKU F0 UNIQUEMENT)
- storage: Déploiement Azure Storage Account ✅
- functions: Déploiement Azure Functions App ✅
- account: Gestion multi-comptes et permissions Azure ✅
- common: Fonctions communes et gestion d'erreurs
"""

__version__ = "1.3.0"
__author__ = "Aux Petits Oignons Team"

from .translator import create_translator, verify_translator
from .storage import (
    create_storage_account,
    create_blob_container,
    verify_storage_account,
    delete_storage_account,
)
from .functions import (
    create_function_app,
    configure_app_settings,
    deploy_functions,
    check_health,
    verify_function_app,
    delete_function_app,
)
from .account import (
    login_azure,
    logout_azure,
    list_accounts,
    get_current_account,
    select_account,
    select_account_interactive,
    check_permissions,
    reconnect_azure,
    ensure_logged_in_with_permissions,
)
from .common import AzureWrapperError, sanitize_credential

__all__ = [
    # Translator
    "create_translator",
    "verify_translator",
    # Storage
    "create_storage_account",
    "create_blob_container",
    "verify_storage_account",
    "delete_storage_account",
    # Functions
    "create_function_app",
    "configure_app_settings",
    "deploy_functions",
    "check_health",
    "verify_function_app",
    "delete_function_app",
    # Account
    "login_azure",
    "logout_azure",
    "list_accounts",
    "get_current_account",
    "select_account",
    "select_account_interactive",
    "check_permissions",
    "reconnect_azure",
    "ensure_logged_in_with_permissions",
    # Common
    "AzureWrapperError",
    "sanitize_credential",
]
