# Azure Wrappers - Automation pour Déploiement Azure

**Version:** 1.1.0
**Projet:** Aux Petits Oignons - Bot Traducteur
**BMAD Stories:** STORY-006 (Storage), STORY-007 (Translator F0)

---

## 📋 Vue d'ensemble

Ce package Python fournit des wrappers pour automatiser le déploiement de ressources Azure nécessaires au **Bot Traducteur** (Power Platform + Azure Functions).

**Modules disponibles:**
- ✅ **translator** - Déploiement Azure Translator avec **SKU F0 UNIQUEMENT**
- ✅ **storage** - Déploiement Azure Storage Account avec SKU Standard_LRS
- 🔜 **functions** - Déploiement Azure Functions (STORY-008)
- ✅ **common** - Utilitaires partagés (erreurs, validation, sanitisation)

---

## ⚠️ AVERTISSEMENT CRITIQUE - SKU F0 OBLIGATOIRE

**Ce package déploie EXCLUSIVEMENT Azure Translator avec le SKU F0 (GRATUIT).**

### Pourquoi SKU F0 est hardcodé ?

| SKU | Coût mensuel | Caractères inclus | Usage recommandé |
|-----|--------------|-------------------|------------------|
| **F0** | **0 EUR** | **2M caractères/mois** | **✅ USAGE PROFESSIONNEL SUFFISANT** |
| S0 | 35 USD | 2M caractères/mois | ❌ COÛT NON BUDGÉTÉ |
| S1+ | >100 USD | 40M+ caractères/mois | ❌ COÛT NON BUDGÉTÉ |

**Décision architecturale:**
- Le SKU F0 est **hardcodé** dans le code (constante `TRANSLATOR_SKU_F0 = "F0"`)
- **AUCUN paramètre** ne permet de changer le SKU
- Si un client nécessite >2M caractères/mois, cela doit être une **décision explicite documentée**

**Protection:**
```python
# ❌ NE PAS MODIFIER - SKU F0 OBLIGATOIRE ❌
TRANSLATOR_SKU_F0 = "F0"
```

---

## 📦 Installation

### Prérequis

1. **Python 3.8+** installé
2. **Azure CLI** installé et configuré
   ```bash
   # Vérifier Azure CLI
   az --version

   # Se connecter à Azure
   az login
   ```

### Installation du package

```bash
# Depuis le répertoire racine du projet
pip install -e azure_wrappers/
```

---

## 🚀 Utilisation

### 1. Déployer un service Azure Translator (SKU F0)

```python
from azure_wrappers import create_translator, verify_translator

# Créer un service Translator
result = create_translator(
    name="translator-acme-20260118",
    resource_group="rg-bot-traducteur-acme",
    region="francecentral",  # Défaut: francecentral
    tags={"client": "Acme Corp", "project": "Bot Traducteur"}
)

# Résultat
print(result)
# {
#     "name": "translator-acme-20260118",
#     "id": "/subscriptions/.../resourceGroups/rg-bot-traducteur-acme/...",
#     "endpoint": "https://api.cognitive.microsofttranslator.com/",
#     "key": "a1b2c3d4e5f6...",  # Clé complète (SENSIBLE)
#     "key_display": "****************ABCD",  # Clé masquée pour affichage
#     "region": "francecentral",
#     "sku": "F0"  # ✅ TOUJOURS F0
# }

# Afficher les informations (avec clé masquée)
print(f"Endpoint: {result['endpoint']}")
print(f"Clé API: {result['key_display']}")
print(f"SKU: {result['sku']}")
```

### 2. Vérifier qu'un service Translator existe

```python
from azure_wrappers import verify_translator

# Vérifier un service existant
status = verify_translator(
    name="translator-acme-20260118",
    resource_group="rg-bot-traducteur-acme"
)

# Résultat
print(status)
# {
#     "exists": True,
#     "state": "Succeeded",
#     "sku": "F0",
#     "sku_is_f0": True,  # ✅ Validation que SKU est bien F0
#     "endpoint": "https://api.cognitive.microsofttranslator.com/"
# }

# Vérifier le SKU
if not status["sku_is_f0"]:
    print(f"⚠️ ATTENTION: Le SKU '{status['sku']}' n'est PAS F0 (gratuit) !")
```

### 3. Gestion des erreurs

```python
from azure_wrappers import create_translator, AzureWrapperError

try:
    result = create_translator(
        name="translator-test",
        resource_group="rg-test"
    )
except AzureWrapperError as e:
    print(f"Erreur lors du déploiement: {e}")
```

**Erreurs gérées:**
- ❌ **Pas connecté à Azure CLI** → "Vous devez être connecté à Azure CLI"
- ❌ **Nom invalide** → "Le nom de Translator doit contenir au moins 3 caractères"
- ❌ **Ressource existe déjà** → "Le service Translator 'X' existe déjà"
- ❌ **Quota dépassé** → "Quota Azure dépassé pour les services Cognitive Services"
- ❌ **Resource Group inexistant** → "Le Resource Group 'X' n'existe pas"

---

## 💾 Module Storage - Déploiement Azure Storage Account

### 1. Créer un Storage Account avec génération automatique de nom

```python
from azure_wrappers import create_storage_account

# Créer un Storage Account avec nom automatique
result = create_storage_account(
    resource_group="rg-bot-traducteur-acme",
    region="francecentral",  # Défaut: francecentral
    tags={"client": "Acme Corp", "project": "Bot Traducteur"}
)

# Résultat
print(result)
# {
#     "name": "tradbot3f2a260118",  # Nom unique généré automatiquement
#     "id": "/subscriptions/.../resourceGroups/rg-bot-traducteur-acme/...",
#     "endpoints": {
#         "blob": "https://tradbot3f2a260118.blob.core.windows.net/",
#         "file": "https://tradbot3f2a260118.file.core.windows.net/",
#         "queue": "https://tradbot3f2a260118.queue.core.windows.net/",
#         "table": "https://tradbot3f2a260118.table.core.windows.net/"
#     },
#     "access_keys": {
#         "key1": "ZXhhbXBsZWtleTE...",  # Clé complète (SENSIBLE)
#         "key2": "ZXhhbXBsZWtleTI...",
#         "key1_display": "****************xyz1",  # Clé masquée
#         "key2_display": "****************xyz2"
#     },
#     "region": "francecentral",
#     "sku": "Standard_LRS",  # Locally Redundant Storage (économique)
#     "kind": "StorageV2",
#     "container_created": True,
#     "container_name": "translations"
# }

# Afficher les informations (avec clés masquées)
print(f"Storage Account: {result['name']}")
print(f"Blob Endpoint: {result['endpoints']['blob']}")
print(f"Access Key: {result['access_keys']['key1_display']}")
print(f"Container: {result['container_name']}")
```

### 2. Créer un Storage Account avec nom personnalisé

```python
from azure_wrappers import create_storage_account

# Créer avec un nom spécifique
result = create_storage_account(
    resource_group="rg-bot-traducteur-acme",
    name="acmebottrad20260118",  # Nom personnalisé (3-24 chars, minuscules+chiffres)
    region="francecentral",
    create_container=True,  # Créer le container "translations" automatiquement
    container_name="documents",  # Nom personnalisé du container
    tags={"environment": "production"}
)

print(f"✅ Storage Account créé: {result['name']}")
print(f"✅ Container créé: {result['container_name']}")
```

### 3. Créer uniquement un blob container dans un Storage existant

```python
from azure_wrappers import create_blob_container

# Créer un nouveau container
success = create_blob_container(
    account_name="acmebottrad20260118",
    container_name="backups",
    account_key="ZXhhbXBsZWtleTE..."  # Clé d'accès du Storage Account
)

if success:
    print("✅ Container 'backups' créé avec succès")
```

### 4. Vérifier qu'un Storage Account existe

```python
from azure_wrappers import verify_storage_account

# Vérifier un Storage existant
status = verify_storage_account(
    name="acmebottrad20260118",
    resource_group="rg-bot-traducteur-acme"
)

# Résultat
print(status)
# {
#     "exists": True,
#     "provisioning_state": "Succeeded",
#     "sku": "Standard_LRS",
#     "kind": "StorageV2",
#     "region": "francecentral",
#     "endpoints": {
#         "blob": "https://acmebottrad20260118.blob.core.windows.net/"
#     }
# }

# Vérifier l'état
if status["provisioning_state"] == "Succeeded":
    print("✅ Storage Account actif et opérationnel")
```

### 5. Supprimer un Storage Account

```python
from azure_wrappers import delete_storage_account

# Supprimer (demande confirmation)
success = delete_storage_account(
    name="acmebottrad20260118",
    resource_group="rg-bot-traducteur-acme",
    confirm=True  # Confirmation explicite requise
)

if success:
    print("✅ Storage Account supprimé")
```

### 6. Gestion des erreurs Storage

```python
from azure_wrappers import create_storage_account, AzureWrapperError

try:
    result = create_storage_account(
        resource_group="rg-test",
        name="invalid name with spaces"  # ❌ Nom invalide
    )
except AzureWrapperError as e:
    print(f"Erreur: {e}")
```

**Erreurs gérées:**
- ❌ **Nom invalide** → "Le nom doit contenir uniquement des lettres minuscules et des chiffres (3-24 caractères)"
- ❌ **Nom déjà pris** → "Le nom 'X' n'est pas disponible (déjà utilisé)"
- ❌ **Resource Group inexistant** → "Le Resource Group 'X' n'existe pas"
- ❌ **Quota dépassé** → "Quota Azure dépassé pour les Storage Accounts"
- ❌ **Région invalide** → "La région 'X' n'existe pas"

### 7. Options de SKU pour Storage Account

Le module utilise **Standard_LRS** par défaut (recommandé pour la plupart des cas):

| SKU | Redondance | Coût | Usage recommandé |
|-----|------------|------|------------------|
| **Standard_LRS** (défaut) | Locale | € | ✅ Usage général, économique |
| Standard_GRS | Géo-redondant | €€ | Haute disponibilité |
| Standard_ZRS | Zone-redondant | €€ | Applications critiques |
| Premium_LRS | Locale (SSD) | €€€ | Performance élevée |

```python
# Utiliser un SKU différent
result = create_storage_account(
    resource_group="rg-test",
    sku="Standard_GRS"  # Redondance géographique
)
```

---

### 4. Sanitisation des credentials

```python
from azure_wrappers import sanitize_credential

# Masquer une clé API
key = "sk-1234567890abcdefghijklmnop"
masked = sanitize_credential(key, visible_chars=4)
print(masked)
# Output: ****************mnop
```

---

## 🧪 Tests

### Exécuter les tests unitaires

```bash
# Installer les dépendances de test
pip install -r azure_wrappers/tests/requirements.txt

# Lancer tous les tests
python3 -m pytest azure_wrappers/tests/ -v

# Lancer les tests avec couverture
python3 -m pytest azure_wrappers/tests/ --cov=azure_wrappers --cov-report=html
```

### Tests critiques (SKU F0)

Le fichier `azure_wrappers/tests/test_translator.py` contient **26 tests** dont **5 tests critiques** validant que:
- ✅ La constante `TRANSLATOR_SKU_F0` existe et vaut `"F0"`
- ✅ La fonction `create_translator()` n'a **AUCUN paramètre `sku`**
- ✅ La commande Azure CLI utilise **uniquement SKU F0**
- ✅ Aucun SKU payant (S0, S1, S2, S3, S4) n'est utilisé
- ✅ La fonction `verify_translator()` détecte correctement le SKU

**Classe de tests critique:**
```python
class TestTranslatorSKUF0:
    """⚠️ TESTS CRITIQUES: Validation que seul le SKU F0 est utilisé"""

    def test_sku_f0_constant_value(self):
        assert TRANSLATOR_SKU_F0 == "F0"

    def test_create_translator_no_sku_parameter(self):
        assert 'sku' not in inspect.signature(create_translator).parameters

    def test_create_translator_uses_f0_sku(self):
        # Vérifie que la commande Azure CLI contient "--sku F0"

    def test_create_translator_never_uses_s0(self):
        # Vérifie qu'aucun SKU payant n'est utilisé
```

---

## 🏗️ Architecture

### Structure du package

```
azure_wrappers/
├── __init__.py           # Exports publics
├── common.py             # Utilitaires partagés
├── translator.py         # Module Translator (SKU F0)
├── storage.py            # Module Storage Account (Standard_LRS)
├── README.md             # Cette documentation
└── tests/
    ├── __init__.py
    ├── test_translator.py  # Tests du module Translator (26 tests)
    ├── test_storage.py     # Tests du module Storage (32 tests)
    └── requirements.txt    # Dépendances de test
```

### Fonctions du module `common`

| Fonction | Description |
|----------|-------------|
| `AzureWrapperError` | Exception personnalisée pour erreurs Azure |
| `sanitize_credential()` | Masque les credentials (API keys, secrets) |
| `run_az_command()` | Exécute une commande Azure CLI de manière sécurisée |
| `validate_resource_name()` | Valide les noms de ressources Azure |
| `validate_azure_region()` | Valide les régions Azure |
| `parse_az_json_output()` | Parse la sortie JSON d'Azure CLI |
| `check_az_logged_in()` | Vérifie si connecté à Azure CLI |
| `get_current_subscription()` | Récupère la subscription Azure active |

### Fonctions du module `translator`

| Fonction | Description |
|----------|-------------|
| `create_translator()` | Crée un service Azure Translator **avec SKU F0** |
| `verify_translator()` | Vérifie qu'un service existe et est actif |
| `delete_translator()` | Supprime un service Translator |

### Fonctions du module `storage`

| Fonction | Description |
|----------|-------------|
| `create_storage_account()` | Crée un Azure Storage Account avec génération automatique de nom unique |
| `create_blob_container()` | Crée un blob container dans un Storage Account existant |
| `verify_storage_account()` | Vérifie qu'un Storage Account existe et est actif |
| `delete_storage_account()` | Supprime un Storage Account (avec confirmation) |

**Caractéristiques Storage:**
- **Génération automatique de nom unique** respectant les contraintes Azure (3-24 chars, lowercase+chiffres)
- **SKU Standard_LRS par défaut** (Locally Redundant Storage, économique)
- **Container "translations" créé automatiquement** pour stocker les documents traduits
- **Récupération des access keys** (avec affichage masqué pour sécurité)
- **Validation de disponibilité du nom** avant création

---

## 📚 Exemples Complets

### Exemple 1: Script de déploiement complet

```python
#!/usr/bin/env python3
"""
Script de déploiement Azure Translator pour client
Usage: python deploy_translator.py <client-name>
"""

import sys
from datetime import datetime
from azure_wrappers import create_translator, verify_translator, AzureWrapperError

def deploy_translator_for_client(client_name: str):
    """Déploie Azure Translator pour un client"""

    # Générer un nom unique
    date_suffix = datetime.now().strftime("%Y%m%d")
    translator_name = f"translator-{client_name}-{date_suffix}"
    resource_group = f"rg-bot-traducteur-{client_name}"

    print(f"🚀 Déploiement Azure Translator pour {client_name}")
    print(f"   Nom: {translator_name}")
    print(f"   Resource Group: {resource_group}")
    print()

    try:
        # Créer le service Translator
        result = create_translator(
            name=translator_name,
            resource_group=resource_group,
            region="francecentral",
            tags={
                "client": client_name,
                "project": "Bot Traducteur",
                "environment": "production"
            }
        )

        print("✅ Déploiement réussi !")
        print()
        print("📋 Informations du service:")
        print(f"   Endpoint: {result['endpoint']}")
        print(f"   Clé API: {result['key_display']}")
        print(f"   SKU: {result['sku']}")
        print(f"   Région: {result['region']}")
        print()

        # Vérifier le service
        print("🔍 Vérification du service...")
        status = verify_translator(translator_name, resource_group)

        if status["sku_is_f0"]:
            print("✅ SKU F0 (gratuit) confirmé")
        else:
            print(f"⚠️ ATTENTION: SKU détecté '{status['sku']}' n'est PAS F0 !")

        if status["state"] == "Succeeded":
            print("✅ Service actif et opérationnel")
        else:
            print(f"⚠️ État du service: {status['state']}")

        # Sauvegarder les informations (à implémenter)
        save_to_config(client_name, result)

        return result

    except AzureWrapperError as e:
        print(f"❌ Erreur: {e}")
        sys.exit(1)

def save_to_config(client_name: str, config: dict):
    """Sauvegarde la configuration dans un fichier"""
    # TODO: Implémenter la sauvegarde sécurisée
    pass

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python deploy_translator.py <client-name>")
        sys.exit(1)

    client_name = sys.argv[1]
    deploy_translator_for_client(client_name)
```

### Exemple 2: Validation d'un déploiement existant

```python
#!/usr/bin/env python3
"""Valide qu'un service Translator existant utilise bien SKU F0"""

from azure_wrappers import verify_translator

def validate_translator_sku(name: str, resource_group: str):
    """Valide qu'un Translator utilise SKU F0"""

    status = verify_translator(name, resource_group)

    if not status["exists"]:
        print(f"❌ Service '{name}' introuvable")
        return False

    if not status["sku_is_f0"]:
        print(f"❌ ÉCHEC: SKU détecté '{status['sku']}' n'est PAS F0 (gratuit) !")
        print(f"⚠️ Coût mensuel potentiel: >35 USD/mois")
        return False

    print(f"✅ Validation réussie: '{name}' utilise bien SKU F0 (gratuit)")
    return True

# Exemple
validate_translator_sku("translator-acme-20260118", "rg-bot-traducteur-acme")
```

---

## 🔒 Sécurité

### Bonnes pratiques

1. **NE JAMAIS logger les clés API complètes**
   ```python
   # ❌ MAUVAIS
   print(f"Clé API: {result['key']}")

   # ✅ BON
   print(f"Clé API: {result['key_display']}")
   ```

2. **Utiliser `sanitize_credential()` pour afficher des secrets**
   ```python
   from azure_wrappers import sanitize_credential

   api_key = "secret-1234567890"
   print(f"Clé: {sanitize_credential(api_key)}")  # Output: ****************7890
   ```

3. **Stocker les credentials de manière sécurisée**
   - Utiliser Azure Key Vault
   - Utiliser des variables d'environnement
   - NE PAS committer les credentials dans Git

---

## 🛠️ Développement

### Ajouter un nouveau module

Pour ajouter un nouveau wrapper Azure (ex: Storage, Functions):

1. Créer un nouveau fichier `azure_wrappers/storage.py`
2. Implémenter les fonctions principales (`create_storage`, `verify_storage`, etc.)
3. Utiliser les utilitaires de `common.py`
4. Créer les tests dans `tests/test_storage.py`
5. Exporter les fonctions dans `__init__.py`

**Template de base:**
```python
"""
Azure Storage Wrapper - Déploiement Azure Storage Account
"""

from typing import Dict, Any
from .common import (
    run_az_command,
    validate_resource_name,
    AzureWrapperError,
    check_az_logged_in,
)

def create_storage(
    name: str,
    resource_group: str,
    region: str = "francecentral",
) -> Dict[str, Any]:
    """Crée un Azure Storage Account"""

    if not check_az_logged_in():
        raise AzureWrapperError("Vous devez être connecté à Azure CLI")

    validate_resource_name(name, "Storage Account")

    # Implémenter la logique...
```

### Guidelines de code

- ✅ Utiliser les type hints
- ✅ Documenter toutes les fonctions publiques
- ✅ Valider tous les paramètres d'entrée
- ✅ Gérer les erreurs avec `AzureWrapperError`
- ✅ Tester avec pytest (couverture ≥80%)
- ✅ Masquer les credentials dans les logs

---

## 📖 Références

### Documentation Azure

- [Azure CLI Documentation](https://learn.microsoft.com/cli/azure/)
- [Azure Translator Documentation](https://learn.microsoft.com/azure/cognitive-services/translator/)
- [Azure Translator Pricing](https://azure.microsoft.com/pricing/details/cognitive-services/translator/)

### Documentation Projet

- **Sprint Plan:** `docs/sprint-plan-aux-petits-oignons-2026-01-18.md`
- **STORY-007:** "Wrapper Python Azure CLI - Déploiement Translator F0"
- **Critères d'acceptation:** 8 critères dont "Tests unitaires vérifiant que seul F0 est utilisé"

---

## 📝 Changelog

### Version 1.1.0 (2026-01-18)

**STORY-006 Completed: Wrapper Python Azure CLI - Déploiement Storage Account**

- ✅ Implémentation `create_storage_account()` avec génération automatique de nom unique
- ✅ Implémentation `create_blob_container()` pour créer des containers blob
- ✅ Implémentation `verify_storage_account()` avec vérification de l'état
- ✅ Implémentation `delete_storage_account()` avec confirmation obligatoire
- ✅ Génération automatique de noms respectant les contraintes Azure (3-24 chars, lowercase+digits)
- ✅ Validation de disponibilité du nom avant création (check-name)
- ✅ SKU Standard_LRS par défaut (Locally Redundant Storage, économique)
- ✅ Container "translations" créé automatiquement pour les documents traduits
- ✅ Récupération et affichage sécurisé des access keys (masquage)
- ✅ 32 tests unitaires (tous passing, couverture complète)
- ✅ Documentation complète avec exemples d'utilisation

**Acceptance Criteria:**
- [x] Module `storage.py` créé avec fonctions de déploiement
- [x] Fonction `create_storage_account()` implémentée
- [x] Génération automatique de nom unique respectant contraintes Azure
- [x] SKU Standard_LRS configuré par défaut (type StorageV2)
- [x] Container "translations" créé automatiquement
- [x] Access keys récupérées et retournées
- [x] Gestion complète des erreurs (nom invalide, quota, etc.)
- [x] Logs sanitisés (access keys masquées dans les affichages)

---

### Version 1.0.0 (2026-01-18)

**STORY-007 Completed:**
- ✅ Implémentation `create_translator()` avec SKU F0 hardcodé
- ✅ Implémentation `verify_translator()` avec validation SKU
- ✅ Implémentation `delete_translator()` avec confirmation
- ✅ Module `common.py` avec 8 fonctions utilitaires
- ✅ 26 tests unitaires (tous passing)
- ✅ Documentation complète (README.md)
- ✅ Protection contre utilisation de SKU payants (S0+)

**Acceptance Criteria:**
- [x] Fonction `create_translator()` implémentée
- [x] SKU F0 **hardcodé** dans le code (pas de paramètre variable)
- [x] Impossible de sélectionner S0 ou autre SKU
- [x] Région francecentral par défaut
- [x] Endpoint et clé récupérés et affichés
- [x] Vérification que le service est actif
- [x] Tests unitaires vérifiant que seul F0 est utilisé
- [x] Documentation claire: "SKU F0 OBLIGATOIRE - NE PAS MODIFIER"

---

## 👥 Support

Pour toute question ou problème:
- **Projet:** Aux Petits Oignons
- **Epic:** EPIC-002 (Azure Deployment Automation)
- **Story:** STORY-007 (Wrapper Python Azure CLI - Déploiement Translator F0)
- **Priorité:** Must Have (CRITIQUE)

---

## ⚖️ Licence

Propriétaire: Aux Petits Oignons Team
Usage interne uniquement
