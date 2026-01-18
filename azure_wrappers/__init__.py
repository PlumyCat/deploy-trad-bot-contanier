"""
Azure Wrappers - Modules Python pour automatiser le déploiement Azure

Ce package contient les wrappers Python pour les commandes Azure CLI,
permettant à OpenCode de déployer automatiquement les ressources Azure
nécessaires au Bot Traducteur.

Modules disponibles:
- translator: Déploiement Azure Translator (SKU F0 UNIQUEMENT)
- storage: Déploiement Azure Storage Account (à venir dans STORY-006)
- functions: Déploiement Azure Functions (à venir dans STORY-008)
- common: Fonctions communes et gestion d'erreurs
"""

__version__ = "1.0.0"
__author__ = "Aux Petits Oignons Team"

from .translator import create_translator, verify_translator
from .common import AzureWrapperError, sanitize_credential

__all__ = [
    "create_translator",
    "verify_translator",
    "AzureWrapperError",
    "sanitize_credential",
]
