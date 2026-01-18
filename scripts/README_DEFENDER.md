# Exclusions Windows Defender ASR - Aux Petits Oignons

**Date:** 2026-01-18
**Story:** STORY-002 - Script PowerShell Exclusions Defender ASR
**Status:** ✅ Ready for Windows execution
**Story Points:** 3

---

## Vue d'Ensemble

Ces scripts PowerShell permettent de créer et supprimer les exclusions Windows Defender ASR (Attack Surface Reduction) nécessaires pour exécuter l'installeur non-signé "Aux Petits Oignons" et ses composants Docker.

### Pourquoi ces exclusions ?

⚠️ **IMPORTANT** : L'installeur `.exe` n'est **PAS signé** avec un certificat de code (coût non justifié pour 2-3 utilisateurs).

Sans exclusions, Windows Defender ASR peut bloquer:
- L'exécution de l'installeur `.exe`
- Les scripts `.bat` de lancement
- Les processus Docker
- Les fichiers non-signés dans l'installation

---

## Scripts Disponibles

### 1. Add-DefenderExclusions.ps1

**Usage:** Créer les exclusions Defender ASR

**Fichier:** `scripts/Add-DefenderExclusions.ps1`

**Fonctionnalités:**
- ✅ Vérifie les droits administrateur
- ✅ Vérifie que Defender est actif
- ✅ Crée exclusions ciblées (pas globales)
- ✅ Confirme succès de chaque exclusion
- ✅ Messages clairs en français
- ✅ Mode interactif avec confirmation
- ✅ Mode silencieux (-Quiet) pour automatisation

### 2. Remove-DefenderExclusions.ps1

**Usage:** Supprimer les exclusions (désinstallation/rollback)

**Fichier:** `scripts/Remove-DefenderExclusions.ps1`

**Fonctionnalités:**
- ✅ Vérifie les droits administrateur
- ✅ Supprime toutes les exclusions créées
- ✅ Messages clairs en français
- ✅ Mode interactif avec confirmation
- ✅ Mode silencieux (-Quiet) pour automatisation

---

## Exclusions Créées

### Exclusions de Chemins

| Chemin | Description |
|--------|-------------|
| `C:\Program Files\AuxPetitsOignons` | Installation principale |
| `%USERPROFILE%\AuxPetitsOignons` | Dossier de données utilisateur |
| `%LOCALAPPDATA%\Programs\AuxPetitsOignons` | Fichiers locaux |
| `%USERPROFILE%\AppData\AuxPetitsOignons` | Données applicatives |
| `%USERPROFILE%\.opencode` | Configuration OpenCode |

### Exclusions de Processus

| Processus | Description |
|-----------|-------------|
| `docker.exe` | Docker CLI |
| `dockerd.exe` | Docker Daemon |
| `com.docker.backend.exe` | Docker Backend |

**Note:** Les exclusions sont **ciblées** et **non globales** pour minimiser les risques de sécurité.

---

## Utilisation

### Prérequis

- ✅ Windows 10 ou Windows 11
- ✅ Windows Defender activé
- ✅ Droits administrateur
- ✅ PowerShell 5.1 ou supérieur

### Méthode 1 : Mode Interactif (Recommandé)

**Pour créer les exclusions :**

1. **Ouvrir PowerShell en tant qu'administrateur**
   - Rechercher "PowerShell" dans le menu Démarrer
   - Clic droit → "Exécuter en tant qu'administrateur"

2. **Naviguer vers le dossier scripts**
   ```powershell
   cd "C:\chemin\vers\deploy-trad-bot-contanier\scripts"
   ```

3. **Exécuter le script**
   ```powershell
   .\Add-DefenderExclusions.ps1
   ```

4. **Suivre les instructions à l'écran**
   - Vérification des droits admin
   - Vérification Defender actif
   - Liste des chemins et processus à exclure
   - Confirmation requise (O/N)
   - Résumé des exclusions créées

**Exemple de sortie :**
```
========================================
Exclusions Defender ASR - Aux Petits Oignons
========================================

ℹ Vérification des droits administrateur...
✓ Droits administrateur confirmés
ℹ Vérification Windows Defender...
✓ Windows Defender est actif

ℹ Chemins à exclure:
  Installation:    C:\Program Files\AuxPetitsOignons
  Données:         C:\Users\Eric\AuxPetitsOignons
  OpenCode:        C:\Users\Eric\.opencode
  LocalAppData:    C:\Users\Eric\AppData\Local\Programs\AuxPetitsOignons
  AppData:         C:\Users\Eric\AppData\AuxPetitsOignons

ℹ Processus à exclure:
  - docker.exe
  - dockerd.exe
  - com.docker.backend.exe

⚠ ATTENTION: Ces exclusions permettront l'exécution de fichiers non-signés.
⚠ Assurez-vous de faire confiance à la source 'Aux Petits Oignons'.

Voulez-vous créer ces exclusions? (O/N): O

========================================
Création des Exclusions
========================================

ℹ Ajout des exclusions de chemins...
✓ Installation principale : Exclusion ajoutée
✓ Dossier de données : Exclusion ajoutée
✓ LocalAppData : Exclusion ajoutée
✓ AppData : Exclusion ajoutée
✓ Configuration OpenCode : Exclusion ajoutée

ℹ Ajout des exclusions de processus...
✓ Docker CLI : Exclusion ajoutée
✓ Docker Daemon : Exclusion ajoutée
✓ Docker Backend : Exclusion ajoutée

========================================
Résumé
========================================

Exclusions de chemins:   5/5 créées
Exclusions de processus: 3/3 créées
Total:                   8/8 créées

✓ Toutes les exclusions ont été créées avec succès!

ℹ Vous pouvez maintenant installer 'Aux Petits Oignons' sans blocage Defender.
```

**Pour supprimer les exclusions :**

```powershell
.\Remove-DefenderExclusions.ps1
```

### Méthode 2 : Mode Silencieux (Automatisation)

**Créer sans confirmation :**
```powershell
.\Add-DefenderExclusions.ps1 -Quiet
```

**Supprimer sans confirmation :**
```powershell
.\Remove-DefenderExclusions.ps1 -Quiet
```

### Méthode 3 : Chemins Personnalisés

**Installation dans un dossier personnalisé :**
```powershell
.\Add-DefenderExclusions.ps1 -InstallPath "D:\MesApplications\AuxPetitsOignons" -DataPath "D:\Donnees\AuxPetitsOignons"
```

---

## Workflow Recommandé

### Installation Initiale

1. **Télécharger/Cloner le projet**
   ```bash
   git clone <repo-url>
   cd deploy-trad-bot-contanier
   ```

2. **Créer les exclusions Defender**
   ```powershell
   cd scripts
   .\Add-DefenderExclusions.ps1
   ```

3. **Compiler l'installeur Inno Setup** (STORY-001)
   ```cmd
   cd ..\installer
   "C:\Program Files (x86)\Inno Setup 6\ISCC.exe" setup.iss
   ```

4. **Installer "Aux Petits Oignons"**
   ```cmd
   .\output\AuxPetitsOignons_Setup.exe
   ```

### Désinstallation

L'installeur Inno Setup supprime automatiquement les exclusions lors de la désinstallation (section `[UninstallRun]` dans `setup.iss`).

**Si besoin de suppression manuelle :**
```powershell
cd scripts
.\Remove-DefenderExclusions.ps1
```

---

## Sécurité

### Risques

⚠️ **Les exclusions Defender désactivent la protection pour les chemins spécifiés.**

**Risques potentiels :**
- Fichiers malveillants pourraient s'exécuter dans les dossiers exclus
- Processus Docker exclus ne seront plus scannés

**Atténuation :**
- ✅ Exclusions **ciblées** (pas globales)
- ✅ Chemins spécifiques à l'application
- ✅ Source fiable (Be-Cloud / interne)
- ✅ Utilisation limitée à 2-3 techniciens

### Recommandations

1. **Vérifier la source** : N'exécuter ces scripts que si vous faites confiance à la source "Aux Petits Oignons"
2. **Audit régulier** : Vérifier périodiquement les exclusions actives
3. **Supprimer si non utilisé** : Si l'application n'est plus utilisée, supprimer les exclusions
4. **Alternative Intune** : Pour un déploiement à plus grande échelle, demander au SI une règle Intune centralisée

### Vérifier les Exclusions Actives

**PowerShell (Admin) :**
```powershell
# Lister toutes les exclusions de chemins
(Get-MpPreference).ExclusionPath

# Lister toutes les exclusions de processus
(Get-MpPreference).ExclusionProcess
```

---

## Troubleshooting

### Erreur : "Ce script nécessite des droits administrateur"

**Solution :**
1. Fermer PowerShell
2. Rechercher "PowerShell" dans le menu Démarrer
3. Clic droit → "Exécuter en tant qu'administrateur"
4. Réessayer

### Erreur : "Impossible de charger le fichier... car l'exécution de scripts est désactivée"

**Solution :**
```powershell
# Temporairement autoriser l'exécution (Admin required)
Set-ExecutionPolicy -ExecutionPolicy Bypass -Scope Process

# Puis exécuter le script
.\Add-DefenderExclusions.ps1
```

**Alternative :**
```powershell
# Exécuter directement avec bypass
powershell -ExecutionPolicy Bypass -File .\Add-DefenderExclusions.ps1
```

### Avertissement : "Windows Defender ne semble pas actif"

**Signification :** Defender est désactivé ou non détecté.

**Actions possibles :**
- Si Defender est vraiment désactivé → Les exclusions ne sont pas nécessaires
- Si erreur de détection → Continuer quand même (choisir "O" à la confirmation)

### Erreur : "Échec - Access denied"

**Causes possibles :**
1. Pas de droits administrateur
2. GPO (Group Policy) bloque les modifications Defender
3. Antivirus tiers contrôle les exclusions

**Solutions :**
1. Vérifier droits admin
2. Contacter l'administrateur système si GPO active
3. Désactiver temporairement antivirus tiers

### Les exclusions ne s'appliquent pas

**Vérification :**
```powershell
# Lister les exclusions créées
(Get-MpPreference).ExclusionPath
(Get-MpPreference).ExclusionProcess
```

**Si vides après exécution :**
- GPO peut override les exclusions locales
- Demander au SI une règle Intune centralisée

---

## Codes de Sortie

Les scripts utilisent des codes de sortie standards :

| Code | Signification |
|------|---------------|
| 0 | Succès |
| 1 | Erreur critique (ex: pas de droits admin) |
| 2 | Succès partiel (certaines exclusions échouées) |
| 99 | Erreur inattendue |

**Usage dans scripts batch :**
```batch
powershell -ExecutionPolicy Bypass -File Add-DefenderExclusions.ps1
if %ERRORLEVEL% EQU 0 (
    echo Exclusions créées avec succès
) else (
    echo Erreur lors de la création des exclusions
)
```

---

## Tests de Validation

### Tests Fonctionnels

| Test | Commande | Résultat attendu |
|------|----------|------------------|
| Vérif droits admin | Script sans admin | Erreur + message clair |
| Création exclusions | `Add-DefenderExclusions.ps1` | 8/8 créées |
| Vérif exclusions | `(Get-MpPreference).ExclusionPath` | 5 chemins listés |
| Confirmation interactive | Répondre "N" | Annulation propre |
| Mode silencieux | `-Quiet` | Pas de confirmation |
| Suppression | `Remove-DefenderExclusions.ps1` | 8/8 supprimées |
| Chemins personnalisés | `-InstallPath D:\Test` | Chemins custom exclus |

### Tests Défensifs

| Scénario | Résultat attendu |
|----------|------------------|
| Defender désactivé | Avertissement + option continuer |
| Exclusion déjà existante | "Déjà exclu" (pas d'erreur) |
| Chemin invalide | Exclusion créée quand même |
| Erreur GPO | Message d'erreur clair |

---

## Critères d'Acceptation - Validation

### ✅ AC-1 : Script PowerShell créé avec exclusions ciblées

- Fichier `Add-DefenderExclusions.ps1` créé (294 lignes)
- Exclusions ciblées : 5 chemins spécifiques + 3 processus Docker
- Pas d'exclusions globales (ex: pas de `C:\*`)

### ✅ AC-2 : Script vérifie les droits administrateur

- Fonction `Test-Administrator` (ligne 76-80)
- Vérification au démarrage (ligne 152-163)
- Message d'erreur clair si non-admin

### ✅ AC-3 : Exclusion pour chemin spécifique de l'exe

- Chemin installation : `C:\Program Files\AuxPetitsOignons`
- Chemins données : `%USERPROFILE%\AuxPetitsOignons`, etc.
- Pas d'exclusion de dossiers système

### ✅ AC-4 : Script confirme succès

- Messages `✓ ... : Exclusion ajoutée` pour chaque exclusion
- Résumé final : `8/8 créées`
- Code de sortie 0 si succès total

### ✅ AC-5 : Documentation claire

- README_DEFENDER.md complet (500+ lignes)
- Commentaires dans les scripts
- Exemples d'usage
- Troubleshooting détaillé

### ⚠️ AC-6 : Script testé sur Windows 10/11

- **Linux** : Impossible de tester (PowerShell Windows uniquement)
- **Windows** : À tester par les techniciens
- **Validation** : Scripts suivent les best practices PowerShell

---

## Alternatives (Futur)

### Option 1 : Règle Intune Centralisée

**Avantages :**
- Gestion centralisée par le SI
- Pas besoin d'exécuter scripts manuellement
- Déploiement sur tous les postes techniciens

**Processus :**
1. Demander au SI de créer une règle Intune
2. Cibler les 2-3 techniciens Modern Workplace
3. Ajouter les exclusions définies ci-dessus
4. Déployer via Intune

### Option 2 : Signature de Code

**Avantages :**
- Pas besoin d'exclusions
- Windows reconnaît l'éditeur
- Plus sécurisé

**Inconvénients :**
- Coût : ~300-500€/an pour certificat
- Non justifié pour 2-3 utilisateurs
- Process de signature à chaque build

---

## Prochaines Étapes

**Sprint 1 - Stories suivantes :**

1. **STORY-003** : Configuration et Build du Container Docker (8 points)
2. **STORY-004** : Script de Démarrage Automatique (start.bat) (3 points)

**Pour tester sur Windows :**

```powershell
# 1. Navigation
cd deploy-trad-bot-contanier\scripts

# 2. Création exclusions
.\Add-DefenderExclusions.ps1

# 3. Vérification
(Get-MpPreference).ExclusionPath
(Get-MpPreference).ExclusionProcess

# 4. Test installation
cd ..\installer\output
.\AuxPetitsOignons_Setup.exe

# 5. Nettoyage (si besoin)
cd ..\..\scripts
.\Remove-DefenderExclusions.ps1
```

---

**Documentation créée par :** Eric (Be-Cloud)
**BMAD Method v6 - Phase 4 (Implementation)**
**Story Points:** 3 points
**Temps estimé:** 4-8 heures
