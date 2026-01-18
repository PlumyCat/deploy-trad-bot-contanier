# Tests End-to-End (E2E) - Aux Petits Oignons

**STORY-INF-001**: Tests E2E du Workflow Complet

Ce document explique comment exécuter les tests End-to-End qui valident l'intégration complète du système de déploiement du Bot Traducteur.

---

## Table des Matières

1. [Vue d'Ensemble](#vue-densemble)
2. [Prérequis](#prérequis)
3. [Configuration](#configuration)
4. [Exécution des Tests](#exécution-des-tests)
5. [Workflow Testé](#workflow-testé)
6. [Cleanup et Ressources](#cleanup-et-ressources)
7. [Interprétation des Résultats](#interprétation-des-résultats)
8. [Troubleshooting](#troubleshooting)
9. [CI/CD](#cicd)

---

## Vue d'Ensemble

Les tests E2E valident le workflow complet de bout en bout :

```
Connexion Azure CLI
    ↓
Déploiement Storage Account
    ↓
Déploiement Translator (SKU F0 CRITIQUE)
    ↓
Déploiement Functions App
    ↓
Génération Rapport
    ↓
Cleanup Automatique
```

**⚠️ IMPORTANT:** Ces tests utilisent une **vraie subscription Azure** et créent de vraies ressources (qui sont automatiquement supprimées après les tests).

---

## Prérequis

### 1. Environnement Python

```bash
# Python 3.8 ou supérieur requis
python --version

# Installer les dépendances
pip install -r requirements.txt

# Installer pytest et dépendances de test
pip install pytest pytest-order pytest-timeout
```

### 2. Azure CLI

```bash
# Vérifier installation Azure CLI
az --version

# Doit afficher version 2.x.x ou supérieure
```

### 3. Connexion Azure

**CRITIQUE:** Vous devez être connecté à Azure CLI **avant** d'exécuter les tests.

```bash
# Se connecter à Azure avec compte délégué (TOUJOURS spécifier tenant-id)
az login --tenant <tenant-id>

# OU si device code nécessaire
az login --tenant <tenant-id> --use-device-code

# Vérifier la connexion
az account show

# Lister les subscriptions disponibles
az account list --output table

# Sélectionner la subscription de TEST
az account set --subscription "<SUBSCRIPTION_ID_TEST>"
```

### 4. Permissions Requises

Votre compte Azure doit avoir au minimum le rôle **Contributor** sur la subscription de test :

- `Microsoft.Resources/deployments/write`
- `Microsoft.Storage/*`
- `Microsoft.CognitiveServices/*`
- `Microsoft.Web/*`

**Vérification :**

```bash
# Lister les rôles
az role assignment list --assignee <YOUR_EMAIL> --output table
```

---

## Configuration

### Variables d'Environnement (Optionnel)

Par défaut, les tests utilisent :
- **Préfixe:** `test-`
- **Région:** `francecentral`
- **Resource Group:** `test-tradbot-e2e-rg`

Vous pouvez personnaliser en modifiant le fichier `tests/test_e2e_workflow.py` :

```python
# Configuration des Tests E2E (lignes 46-57)
TEST_PREFIX = "test"  # Préfixe pour identification
TEST_REGION = "francecentral"  # Région Azure
TEST_RESOURCE_GROUP = f"{TEST_PREFIX}-tradbot-e2e-rg"  # Nom du RG
AZURE_OPERATION_TIMEOUT = 300  # Timeout (5 minutes)
```

---

## Exécution des Tests

### Exécution Complète

```bash
# Exécuter tous les tests E2E
pytest tests/test_e2e_workflow.py -v -s

# Avec marqueurs
pytest tests/test_e2e_workflow.py -v -s -m e2e
```

**Options :**
- `-v` : Mode verbose (affiche plus de détails)
- `-s` : Affiche les `print()` dans les tests (recommandé pour E2E)
- `-m e2e` : Exécute uniquement les tests marqués `e2e`

**Durée estimée :** 10-15 minutes (dépend de la vitesse d'Azure)

### Exécution d'un Test Spécifique

```bash
# Test 1 : Connexion Azure
pytest tests/test_e2e_workflow.py::TestE2EWorkflow::test_01_connection_and_permissions -v -s

# Test 3 : Vérification SKU F0 Translator (CRITIQUE)
pytest tests/test_e2e_workflow.py::TestE2EWorkflow::test_03_deploy_translator_sku_f0 -v -s
```

### Exécution en Mode Dry-Run (Vérification Sans Exécution)

```bash
# Collecter les tests sans les exécuter
pytest tests/test_e2e_workflow.py --collect-only
```

### Exécution Avec Rapport HTML

```bash
# Installer pytest-html
pip install pytest-html

# Exécuter avec rapport HTML
pytest tests/test_e2e_workflow.py -v -s --html=tests/report_e2e.html --self-contained-html
```

---

## Workflow Testé

### Test 1: Connexion Azure et Permissions

**Ce qui est testé :**
- Connexion Azure CLI active
- Subscription accessible
- Permissions suffisantes (Contributor)

**Sortie attendue :**
```
✅ Connecté à Azure: Visual Studio Enterprise Subscription
   Subscription ID: 12345678-1234-1234-1234-123456789abc
   Tenant ID: 87654321-4321-4321-4321-cba987654321
✅ Permissions OK
✅ Test 1 réussi: Connexion Azure validée
```

---

### Test 2: Déploiement Storage Account

**Ce qui est testé :**
- Création du Storage Account avec préfixe "test-"
- Création d'un blob container "documents"
- Vérification des endpoints et clés

**Ressources créées :**
- Storage Account: `test-tradbot-xxxxx` (xxxxx = suffixe unique)
- Blob Container: `documents`

**Sortie attendue :**
```
✅ Storage Account créé: test-tradbot-abc123
✅ Blob container créé: documents
✅ Storage Account vérifié et fonctionnel
✅ Test 2 réussi: Storage Account déployé et vérifié
```

---

### Test 3: Déploiement Translator (SKU F0 CRITIQUE)

**Ce qui est testé :**
- Création du Translator avec SKU F0
- **🔴 VÉRIFICATION CRITIQUE:** SKU F0 confirmé (pas S0/S1/S2)
- Récupération des clés et endpoint

**Ressources créées :**
- Translator: `test-tradbot-translator-xxxxx`

**Sortie attendue :**
```
✅ Translator créé: test-tradbot-translator-abc123

🔴 VÉRIFICATION CRITIQUE: SKU Translator
   SKU détecté: F0
   ✅ SKU F0 confirmé (gratuit)

✅ Translator vérifié et fonctionnel
✅ Test 3 réussi: Translator déployé avec SKU F0 confirmé
```

**⚠️ IMPORTANT:** Si ce test échoue avec un SKU différent de F0, c'est un **échec critique**. Le déploiement utiliserait un SKU payant (35$/mois minimum).

---

### Test 4: Déploiement Functions App

**Ce qui est testé :**
- Création du Functions App lié au Storage Account
- Configuration des app settings
- Vérification du health check

**Ressources créées :**
- Function App: `test-tradbot-functions-xxxxx`
- App Service Plan: Consumption Plan (Y1)

**Sortie attendue :**
```
✅ Function App créé: test-tradbot-functions-abc123
✅ Function App vérifié et fonctionnel
   URL: https://test-tradbot-functions-abc123.azurewebsites.net
✅ Test 4 réussi: Function App déployé et vérifié
```

---

### Test 5: Génération Rapport

**Ce qui est testé :**
- Génération du rapport avec toutes les ressources créées
- Présence des informations clés (Storage, Translator SKU F0, Functions)
- Format du rapport
- Sauvegarde du rapport dans `tests/outputs/`

**Fichiers créés :**
- Rapport: `tests/outputs/rapport_TEST-E2E-Client_YYYY-MM-DD_HH-MM-SS.txt`

**Sortie attendue :**
```
✅ Rapport généré avec toutes les informations
✅ Rapport sauvegardé: tests/outputs/rapport_TEST-E2E-Client_2026-01-18_14-30-45.txt
✅ Test 5 réussi: Rapport généré et sauvegardé
```

---

### Test 6: Vérification Finale

**Ce qui est testé :**
- Toutes les ressources ont été créées
- Le groupe de ressources existe
- Nombre de ressources ≥ 3

**Sortie attendue :**
```
✅ Groupe de ressources existe: test-tradbot-e2e-rg
✅ Ressources créées: 4
   - Microsoft.Storage/storageAccounts: test-tradbot-abc123
   - Microsoft.CognitiveServices/accounts: test-tradbot-translator-abc123
   - Microsoft.Web/serverFarms: test-tradbot-functions-plan-abc123
   - Microsoft.Web/sites: test-tradbot-functions-abc123

✅ TOUS LES TESTS E2E RÉUSSIS!

📊 Résumé du workflow E2E:
   ✅ Connexion Azure validée
   ✅ Storage Account déployé: test-tradbot-abc123
   ✅ Translator déployé avec SKU F0: test-tradbot-translator-abc123
   ✅ Function App déployé: test-tradbot-functions-abc123
   ✅ Rapport généré: tests/outputs/rapport_...txt
   ✅ 4 ressources créées

🧹 Cleanup:
   Le groupe de ressources 'test-tradbot-e2e-rg' sera supprimé automatiquement
   par la fixture après tous les tests.
```

---

## Cleanup et Ressources

### Cleanup Automatique

Les tests E2E nettoient **automatiquement** toutes les ressources créées :

1. **Pendant les tests :** Les ressources sont créées avec le préfixe `test-`
2. **Après tous les tests :** La fixture `test_resource_group` supprime le groupe de ressources entier (et toutes les ressources qu'il contient)

**Commande de suppression (exécutée automatiquement) :**

```bash
az group delete --name test-tradbot-e2e-rg --yes --no-wait
```

**`--no-wait`** signifie que la suppression se fait en arrière-plan (asynchrone). Les ressources seront complètement supprimées dans les 5-10 minutes suivant la fin des tests.

### Vérification du Cleanup

```bash
# Lister les groupes de ressources
az group list --output table

# Vérifier qu'aucun groupe "test-*" n'existe
az group list --query "[?starts_with(name, 'test-')]" --output table

# Si un groupe test reste :
az group delete --name test-tradbot-e2e-rg --yes
```

### Cleanup Manuel (Si Nécessaire)

Si les tests sont interrompus (Ctrl+C, crash, etc.) avant la fin, le cleanup automatique peut ne pas s'exécuter.

**Nettoyage manuel :**

```bash
# Supprimer le groupe de ressources de test
az group delete --name test-tradbot-e2e-rg --yes

# Vérifier suppression
az group show --name test-tradbot-e2e-rg
# Devrait retourner une erreur "ResourceGroupNotFound"
```

---

## Interprétation des Résultats

### Succès Complet

```
============================= test session starts ==============================
collected 6 items

tests/test_e2e_workflow.py::TestE2EWorkflow::test_01_connection_and_permissions PASSED
tests/test_e2e_workflow.py::TestE2EWorkflow::test_02_deploy_storage_account PASSED
tests/test_e2e_workflow.py::TestE2EWorkflow::test_03_deploy_translator_sku_f0 PASSED
tests/test_e2e_workflow.py::TestE2EWorkflow::test_04_deploy_function_app PASSED
tests/test_e2e_workflow.py::TestE2EWorkflow::test_05_generate_report PASSED
tests/test_e2e_workflow.py::TestE2EWorkflow::test_06_cleanup_verification PASSED

============================== 6 passed in 647.32s (0:10:47) ===============================
```

**Interprétation :** ✅ Tous les tests réussis. Le workflow complet fonctionne end-to-end.

---

### Échec Test 1 (Connexion/Permissions)

```
FAILED tests/test_e2e_workflow.py::TestE2EWorkflow::test_01_connection_and_permissions
❌ Erreur: Pas connecté à Azure CLI.
Exécutez 'az login --tenant <tenant-id>' avant de lancer les tests E2E.
```

**Cause :** Pas connecté à Azure CLI

**Solution :**
```bash
az login --tenant <tenant-id>
pytest tests/test_e2e_workflow.py -v -s
```

---

### Échec Test 3 (SKU Translator)

```
FAILED tests/test_e2e_workflow.py::TestE2EWorkflow::test_03_deploy_translator_sku_f0
❌ ÉCHEC CRITIQUE: SKU Translator incorrect!
   Attendu: F0 (gratuit)
   Obtenu: S0
   ⚠️  RISQUE: Coût client si SKU payant (S0 = 35$/mois minimum)
```

**Cause :** Le code de création Translator n'utilise pas SKU F0

**Impact :** 🔴 **CRITIQUE** - Coût client

**Solution :**
1. Vérifier `azure_wrappers/translator.py` ligne avec `--sku`
2. S'assurer que `--sku F0` est hardcodé (pas de paramètre)
3. Corriger le code
4. Relancer les tests

---

### Échec Timeout

```
FAILED tests/test_e2e_workflow.py::TestE2EWorkflow::test_02_deploy_storage_account
❌ Timeout lors de la création du Storage Account
```

**Cause :** Azure prend trop de temps (>5 minutes)

**Solutions :**
- Vérifier la connexion Internet
- Vérifier l'état d'Azure (status.azure.com)
- Augmenter le timeout dans `test_e2e_workflow.py` :
  ```python
  AZURE_OPERATION_TIMEOUT = 600  # 10 minutes au lieu de 5
  ```

---

## Troubleshooting

### Problème: "ResourceGroupNotFound" pendant cleanup

**Symptôme :**
```
⚠️  Avertissement: Échec suppression groupe (peut-être déjà supprimé)
```

**Cause :** Le groupe de ressources a déjà été supprimé (normal en cas de re-run)

**Impact :** Aucun (c'est juste un avertissement)

---

### Problème: "QuotaExceeded"

**Symptôme :**
```
ERROR: QuotaExceeded: Subscription has exceeded quota for Storage Accounts
```

**Cause :** Trop de ressources dans la subscription

**Solutions :**
1. Nettoyer les anciennes ressources de test :
   ```bash
   az group list --query "[?starts_with(name, 'test-')]" --output table
   az group delete --name <OLD_TEST_RG> --yes
   ```
2. Utiliser une autre subscription de test
3. Demander une augmentation de quota

---

### Problème: "NameAlreadyExists"

**Symptôme :**
```
ERROR: The storage account name 'test-tradbot-abc123' is already taken
```

**Cause :** Un ancien Storage Account avec ce nom existe encore (globalement dans Azure)

**Solutions :**
1. Attendre que l'ancien soit complètement supprimé (peut prendre 5-10 minutes)
2. Relancer les tests (un nouveau nom unique sera généré)

---

### Problème: Tests s'arrêtent après Test 2

**Symptôme :** Les tests 3, 4, 5, 6 ne s'exécutent pas

**Cause :** Test 2 a échoué, pytest arrête la suite (comportement normal)

**Solution :**
1. Corriger l'erreur du Test 2
2. Relancer les tests depuis le début

---

## CI/CD

### GitHub Actions (Exemple)

Créez `.github/workflows/e2e-tests.yml` :

```yaml
name: E2E Tests

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]
  workflow_dispatch:  # Permet déclenchement manuel

jobs:
  e2e-tests:
    runs-on: ubuntu-latest
    timeout-minutes: 30

    steps:
      - uses: actions/checkout@v3

      - name: Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'

      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -r requirements.txt
          pip install pytest pytest-order pytest-timeout

      - name: Azure Login
        uses: azure/login@v1
        with:
          creds: ${{ secrets.AZURE_CREDENTIALS }}

      - name: Run E2E Tests
        run: |
          pytest tests/test_e2e_workflow.py -v -s --html=report_e2e.html --self-contained-html

      - name: Upload Test Report
        if: always()
        uses: actions/upload-artifact@v3
        with:
          name: e2e-test-report
          path: report_e2e.html

      - name: Cleanup (Failsafe)
        if: always()
        run: |
          az group delete --name test-tradbot-e2e-rg --yes --no-wait || true
```

**Configuration des Secrets :**

Dans GitHub > Settings > Secrets > Actions, ajoutez :
- `AZURE_CREDENTIALS` : Service Principal credentials JSON

---

### Azure DevOps (Exemple)

Créez `azure-pipelines.yml` :

```yaml
trigger:
  branches:
    include:
      - main
      - develop

pool:
  vmImage: 'ubuntu-latest'

steps:
  - task: UsePythonVersion@0
    inputs:
      versionSpec: '3.11'

  - script: |
      python -m pip install --upgrade pip
      pip install -r requirements.txt
      pip install pytest pytest-order pytest-timeout
    displayName: 'Install dependencies'

  - task: AzureCLI@2
    inputs:
      azureSubscription: 'Azure-Test-Subscription'
      scriptType: 'bash'
      scriptLocation: 'inlineScript'
      inlineScript: |
        pytest tests/test_e2e_workflow.py -v -s
    displayName: 'Run E2E Tests'

  - task: PublishTestResults@2
    condition: always()
    inputs:
      testResultsFiles: '**/test-results.xml'
      testRunTitle: 'E2E Tests'
```

---

## Métriques et Reporting

### Métriques Collectées

Les tests E2E collectent automatiquement :
- ✅ Temps d'exécution de chaque phase
- ✅ Noms des ressources créées
- ✅ SKU Translator vérifié (F0)
- ✅ Nombre total de ressources déployées

### Rapport Généré

Le rapport d'intervention généré contient :
- Informations client
- Liste des ressources déployées
- URLs et endpoints
- Configuration clés
- SKU Translator (F0 confirmé)

**Emplacement :** `tests/outputs/rapport_TEST-E2E-Client_<timestamp>.txt`

---

## Fréquence d'Exécution Recommandée

| Événement | Fréquence | Justification |
|-----------|-----------|---------------|
| Avant commit (code critique) | Optionnel | Vérification avant push |
| Pull Request | Automatique | Validation intégration |
| Merge vers main | Automatique | Validation finale |
| Release | Obligatoire | Garantie qualité production |
| Hebdomadaire | Recommandé | Détection régression |

---

## Contacts et Support

Pour toute question sur les tests E2E :

- **Documentation complète :** `docs/sprint-plan-aux-petits-oignons-2026-01-18.md`
- **Story JIRA :** STORY-INF-001
- **Support :** Équipe Aux Petits Oignons

---

**Guide créé par :** Équipe Aux Petits Oignons
**Dernière mise à jour :** 2026-01-18
**Version :** 1.0
**Story :** STORY-INF-001

---

🎉 **Bon testing !** Ces tests E2E garantissent que le système fonctionne correctement de bout en bout avant chaque déploiement client.
