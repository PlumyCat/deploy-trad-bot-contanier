"""
Azure Wrappers - Modules Python pour automatiser le déploiement Azure

Ce package contient les wrappers Python pour les commandes Azure CLI,
permettant à OpenCode de déployer automatiquement les ressources Azure
nécessaires au Bot Traducteur.

Modules disponibles:
- translator: Déploiement Azure Translator (SKU F0 UNIQUEMENT)
- storage: Déploiement Azure Storage Account ✅
- functions: Déploiement Azure Functions (à venir dans STORY-008)
- common: Fonctions communes et gestion d'erreurs
"""

__version__ = "1.1.0"
__author__ = "Aux Petits Oignons Team"

from .translator import create_translator, verify_translator
from .storage import (
    create_storage_account,
    create_blob_container,
    verify_storage_account,
    delete_storage_account,
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
    # Common
    "AzureWrapperError",
    "sanitize_credential",
]
