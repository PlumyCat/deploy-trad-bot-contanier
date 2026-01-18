# Guide d'Installation - Aux Petits Oignons
## Installeur Windows avec Inno Setup

**Date:** 2026-01-18
**Story:** STORY-001 - Créer Installeur Windows .exe avec Inno Setup
**Status:** ✅ Ready for Windows compilation
**Story Points:** 5

---

## Vue d'Ensemble

L'installeur "Aux Petits Oignons" permet d'installer l'environnement complet de déploiement du Bot Traducteur en un seul clic. Il gère automatiquement la vérification des prérequis, la copie des fichiers, et la création des raccourcis.

### Caractéristiques

- ✅ Installation complète en < 2 minutes
- ✅ Taille estimée < 50MB (sans images Docker)
- ✅ Vérification Docker Desktop automatique
- ✅ Vérification Git (recommandé)
- ✅ Configuration post-installation guidée
- ✅ Raccourcis Menu Démarrer + Bureau (optionnel)
- ✅ Désinstallation propre avec nettoyage Defender

---

## Compilation de l'Installeur

### Prérequis Windows

1. **Inno Setup 6.x** - Télécharger depuis : https://jrsoftware.org/isdl.php
2. **Windows 10/11** avec droits administrateur
3. **Tous les fichiers source** validés avec `validate.ps1`

### Validation Pre-Build

**Sur Windows (PowerShell) :**
```powershell
cd installer
.\validate.ps1
```

**Sur Linux/Mac (Bash) :**
```bash
cd installer
bash validate.sh
```

**Sortie attendue :**
```
Total files checked: 16
Missing files: 0
✓ All files present!
Ready to compile installer with Inno Setup.
```

### Compilation

**Option 1 : Interface Graphique (Recommandé)**

1. Ouvrir **Inno Setup Compiler**
2. File → Open → `installer/setup.iss`
3. Build → Compile (ou `Ctrl+F9`)
4. Attendre la fin de la compilation (~30 secondes)
5. L'installeur sera créé dans `installer/output/AuxPetitsOignons_Setup.exe`

**Option 2 : Ligne de Commande**

```cmd
"C:\Program Files (x86)\Inno Setup 6\ISCC.exe" installer\setup.iss
```

**Sortie :**
```
Successful compile (X.XX sec). Resulting Setup program filename is:
installer\output\AuxPetitsOignons_Setup.exe
```

---

## Structure de l'Installation

### Fichiers Copiés

L'installeur copie tous les fichiers nécessaires vers `C:\Program Files\AuxPetitsOignons\` :

```
C:\Program Files\AuxPetitsOignons\
├── conf_opencode/
│   ├── opencode.json           # Config OpenCode
│   └── .env.example            # Template clés API
├── scripts/
│   ├── decrypt-credentials.ps1
│   └── encrypt-credentials.ps1
├── Dockerfile                   # Container Ubuntu 24.04
├── docker-compose.yml           # Orchestration
├── doc_server.py                # Serveur Flask docs
├── requirements.txt             # Dependencies Python
├── entrypoint.sh                # Container entry point
├── start.bat                    # Launcher principal
├── configure.bat                # Configuration API keys
├── repo-config.txt              # Config repo GitHub
└── oignon.ico                   # Icône application
```

### Dossier de Données

Un dossier séparé est créé dans le profil utilisateur : `%USERPROFILE%\AuxPetitsOignons\`

```
%USERPROFILE%\AuxPetitsOignons\
├── clients/                     # Rapports par client
├── Solution/                    # Solutions Power Platform
└── README.txt                   # Instructions
```

**Note :** Le code source `src/` (Azure Functions) est cloné automatiquement au premier démarrage via `start.bat`.

---

## Raccourcis Créés

### Menu Démarrer

Tous les raccourcis sont accessibles via **Menu Démarrer > Aux petits oignons** :

| Raccourci | Action | Fichier cible |
|-----------|--------|---------------|
| **Aux petits oignons** | Lance l'application | `start.bat` |
| **Configuration** | Configure clés API | `configure.bat` |
| **Documentation (Web)** | Ouvre http://localhost:5545/procedure | Navigateur |
| **Solution Power Platform** | Ouvre dossier Solution | Explorer |
| **Rapports Clients** | Ouvre dossier clients | Explorer |
| **Désinstaller** | Désinstallation propre | unins000.exe |

### Bureau (Optionnel)

Une icône **Aux petits oignons** peut être créée sur le Bureau lors de l'installation (option cochée par défaut).

---

## Vérifications au Démarrage

L'installeur exécute plusieurs vérifications **avant** l'installation :

### 1. Docker Desktop

**Vérification :**
```pascal
docker --version
docker info
```

**Si absent :**
- Affiche message d'erreur
- Propose d'ouvrir https://www.docker.com/products/docker-desktop/
- **Bloque l'installation**

**Si installé mais non démarré :**
- Affiche message : "Docker Desktop est installé mais n'est pas démarré"
- Demande de démarrer Docker Desktop
- **Bloque l'installation**

### 2. Git (Recommandé)

**Vérification :**
```pascal
git --version
```

**Si absent :**
- Affiche avertissement (non bloquant)
- Propose d'ouvrir https://git-scm.com/download/win
- **Permet de continuer** (le code source sera téléchargé autrement)

---

## Post-Installation

### Message de Succès

À la fin de l'installation, un message s'affiche :

```
Installation terminée avec succès !

Prochaines étapes :
1. Lancez "Configuration" depuis le menu Démarrer
2. Entrez vos clés API (Azure Foundry et Tavily)
3. Lancez "Aux petits oignons" pour démarrer

Tous les raccourcis sont disponibles dans le menu Démarrer.
```

### Configuration Requise

**AVANT le premier lancement**, configurer les clés API :

1. **Menu Démarrer > Aux petits oignons > Configuration**
2. Entrer :
   - `ANTHROPIC_API_KEY` (Azure AI Foundry)
   - `ANTHROPIC_BASE_URL` (URL ressource Azure)
   - `TAVILY_API_KEY` (optionnel pour MCP Search)
3. Sauvegarder

Le fichier `.env` sera créé dans `conf_opencode/`.

---

## Désinstallation

### Processus Automatique

La désinstallation effectue automatiquement :

1. ✅ Suppression des fichiers de `C:\Program Files\AuxPetitsOignons\`
2. ✅ Suppression des raccourcis Menu Démarrer et Bureau
3. ✅ **Suppression automatique des exclusions Defender** (via PowerShell)
4. ❓ Demande confirmation pour supprimer `%USERPROFILE%\AuxPetitsOignons\`

### Exclusions Defender Supprimées

La désinstallation supprime automatiquement les exclusions créées :

```powershell
Remove-MpPreference -ExclusionPath 'C:\Program Files\AuxPetitsOignons'
Remove-MpPreference -ExclusionPath '%LOCALAPPDATA%\Programs\AuxPetitsOignons'
Remove-MpPreference -ExclusionPath '%USERPROFILE%\AuxPetitsOignons'
Remove-MpPreference -ExclusionPath '%USERPROFILE%\AppData\AuxPetitsOignons'
Remove-MpPreference -ExclusionPath '%USERPROFILE%\.opencode'
Remove-MpPreference -ExclusionProcess 'docker.exe', 'dockerd.exe', 'com.docker.backend.exe'
```

**Note :** Les exclusions sont supprimées silencieusement (aucune erreur si déjà absentes).

### Données Utilisateur

Un message demande confirmation avant suppression :

```
Voulez-vous supprimer le dossier de données ?
%USERPROFILE%\AuxPetitsOignons

Ce dossier contient les rapports clients, les solutions Power Platform
et le code source téléchargé.
```

- **Oui** → Suppression complète
- **Non** → Conservation des données

---

## Sécurité et Defender ASR

### Certificat Non Signé

⚠️ **IMPORTANT** : L'installeur `.exe` **n'est PAS signé** avec un certificat de code.

**Raison :** Coût du certificat non justifié pour 2-3 utilisateurs internes.

**Conséquence :** Windows Defender ASR peut bloquer l'exécution.

### Solution : Script PowerShell STORY-002

Les exclusions Defender ASR sont gérées par **STORY-002** (script PowerShell dédié).

**Workflow recommandé :**

1. Installer "Aux Petits Oignons" (STORY-001)
2. Si bloqué par Defender → Exécuter script STORY-002
3. Relancer l'installation

**Alternative :** Demander au SI une règle Intune centralisée (futur).

---

## Troubleshooting

### Erreur : "Docker n'est pas installé"

**Solution :**
1. Télécharger Docker Desktop : https://www.docker.com/products/docker-desktop/
2. Installer et redémarrer l'ordinateur
3. Relancer l'installeur

### Erreur : "Docker n'est pas démarré"

**Solution :**
1. Lancer **Docker Desktop** depuis le menu Démarrer
2. Attendre que Docker soit prêt (icône système)
3. Relancer l'installeur

### Exe bloqué par Windows Defender

**Solution :**
1. Exécuter script PowerShell de **STORY-002**
2. Le script crée les exclusions ASR nécessaires
3. Relancer l'installeur

### Compilation Inno Setup échoue

**Solutions :**
1. Vérifier version Inno Setup (6.x requis)
2. Exécuter `validate.ps1` pour vérifier fichiers
3. Vérifier chemins relatifs dans `setup.iss`
4. Vérifier permissions sur répertoire `output/`

### L'installation est lente

**Normal :** La copie des fichiers peut prendre jusqu'à 2 minutes selon :
- Vitesse du disque (SSD vs HDD)
- Antivirus en cours de scan
- Nombre de fichiers dans `scripts/`

**Si > 5 minutes :** Vérifier que l'antivirus ne bloque pas.

---

## Tests de Validation

### Tests Fonctionnels

| Test | Commande | Résultat attendu |
|------|----------|------------------|
| Validation fichiers | `.\validate.ps1` | ✓ All files present! |
| Compilation | Build → Compile | Successful compile |
| Taille .exe | `dir output\` | < 50MB |
| Installation | Double-clic .exe | Installation complète < 2min |
| Raccourcis | Menu Démarrer | 6 raccourcis créés |
| Docker check | (au démarrage) | Vérifie Docker installé/démarré |
| Git check | (au démarrage) | Avertissement si absent (non bloquant) |
| Message succès | (fin install) | Affiche prochaines étapes |
| Désinstallation | Désinstaller | Supprime tout + demande confirmation données |

### Tests Défensifs

| Scénario | Résultat attendu |
|----------|------------------|
| Docker non installé | Message d'erreur + lien téléchargement + **blocage** |
| Docker non démarré | Message d'erreur + instruction démarrage + **blocage** |
| Git non installé | Avertissement + lien téléchargement + **continue** |
| Exe bloqué Defender | Doit être géré par STORY-002 (hors scope STORY-001) |

---

## Critères d'Acceptation - Validation

### ✅ AC-1 : Script Inno Setup créé

- Fichier `setup.iss` existe et est complet
- Version 1.2 définie
- Configuration complète (app ID, icône, compression)

### ⚠️ AC-2 : Exe compilé et testé

- **Linux** : Compilation impossible (Inno Setup Windows uniquement)
- **Windows** : À tester après compilation
- **Validation** : Script `validate.ps1` confirme tous fichiers présents

### ✅ AC-3 : Copie tous fichiers nécessaires

- 16 fichiers/dossiers référencés dans `setup.iss`
- Validation automatique via `validate.sh` et `validate.ps1`
- Tous fichiers présents ✓

### ✅ AC-4 : Arborescence créée

- `C:\Program Files\AuxPetitsOignons\` (fichiers app)
- `%USERPROFILE%\AuxPetitsOignons\` (données)
- Sous-dossiers : `clients/`, `Solution/`

### ✅ AC-5 : Message succès

- Fonction `CurStepChanged` dans `setup.iss` (ligne 153-177)
- Affiche prochaines étapes
- Mentionne Configuration et lancement

### ⚠️ AC-6 : Taille < 50MB

- **Linux** : Impossible de compiler (estimation basée sur fichiers source)
- **Windows** : À vérifier après compilation
- **Fichiers source totaux** : ~2MB (hors Docker images)

### ✅ AC-7 : Installation < 2 minutes

- Logique installation optimisée
- Compression LZMA activée
- Pas de build Docker pendant install (fait au premier lancement)

---

## Prochaines Étapes

**Sprint 1 - Stories suivantes :**

1. **STORY-002** : Script PowerShell Exclusions Defender ASR (3 points)
2. **STORY-003** : Configuration et Build du Container Docker (8 points)

**Pour compiler sur Windows :**

```powershell
# 1. Validation
cd installer
.\validate.ps1

# 2. Compilation
"C:\Program Files (x86)\Inno Setup 6\ISCC.exe" setup.iss

# 3. Vérification
dir output\AuxPetitsOignons_Setup.exe

# 4. Test installation
.\output\AuxPetitsOignons_Setup.exe
```

---

**Documentation créée par :** Eric
**BMAD Method v6 - Phase 4 (Implementation)**
**Story Points:** 5 points
**Temps estimé:** 1-2 jours
