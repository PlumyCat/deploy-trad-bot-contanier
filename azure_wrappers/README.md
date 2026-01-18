# Azure Wrappers - Automation pour Déploiement Azure

**Version:** 1.0.0
**Projet:** Aux Petits Oignons - Bot Traducteur
**BMAD Story:** STORY-007 (Wrapper Python Azure CLI - Déploiement Translator F0)

---

## 📋 Vue d'ensemble

Ce package Python fournit des wrappers pour automatiser le déploiement de ressources Azure nécessaires au **Bot Traducteur** (Power Platform + Azure Functions).

**Modules disponibles:**
- ✅ **translator** - Déploiement Azure Translator avec **SKU F0 UNIQUEMENT**
- 🔜 **storage** - Déploiement Azure Storage Account (STORY-006)
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
├── README.md             # Cette documentation
└── tests/
    ├── __init__.py
    ├── test_translator.py  # Tests du module Translator
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
