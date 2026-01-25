# 📦 Installeur Windows - Aux petits oignons

Guide de compilation de l'installeur Windows `.exe` pour le Bot Traducteur.

---

## 📋 Prérequis

### Inno Setup 6

L'installeur nécessite **Inno Setup 6.3.3 ou supérieur**.

#### Installation Automatique (Recommandé)

```powershell
cd installer
.\install-innosetup.ps1
```

Le script :
- ✅ Vérifie si Inno Setup est déjà installé
- ✅ Télécharge la dernière version depuis jrsoftware.org
- ✅ Lance l'installation interactive
- ✅ Vérifie que l'installation a réussi

#### Installation Manuelle

1. Visitez : https://jrsoftware.org/isdl.php
2. Téléchargez **Inno Setup 6.3.3** ou supérieur
3. Installez avec les options par défaut
4. Vérifiez l'installation :
   ```batch
   "C:\Program Files (x86)\Inno Setup 6\iscc.exe" /?
   ```

---

## 🚀 Compilation

### Méthode 1 : Script Automatique (Recommandé)

```batch
cd installer
compile.bat
```

Le script :
- ✅ Cherche Inno Setup dans les emplacements standards
- ✅ Compile `setup.iss`
- ✅ Génère `output\AuxPetitsOignons_Setup.exe`
- ✅ Affiche la taille du fichier

### Méthode 2 : Compilation Manuelle

```batch
cd installer
"C:\Program Files (x86)\Inno Setup 6\iscc.exe" setup.iss
```

---

## 📂 Structure du Projet

```
installer/
├── README.md                    # Ce fichier
├── setup.iss                    # Script Inno Setup (v1.3)
├── compile.bat                  # Script de compilation automatique
├── install-innosetup.ps1       # Installation automatique d'Inno Setup
└── output/                      # Dossier généré
    └── AuxPetitsOignons_Setup.exe  # Installeur compilé
```

---

## 📝 Fichiers Inclus dans l'Installeur

### Configuration OpenCode
- `conf_opencode/opencode.json` - Configuration fork custom
- `conf_opencode/.env.example` - Template configuration Azure
- `conf_opencode/CLAUDE.md` - Instructions Claude Code

### Scripts
- `scripts/*` - Tous les scripts d'automatisation
- `start.bat` - Démarrage principal
- `configure.bat` - Configuration interactive
- `rebuild-fast.bat` - Menu build Docker

### Dockerfiles (5 options)
- `Dockerfile` - Version standard
- `Dockerfile.optimized` - Version optimisée BuildKit
- `Dockerfile.ultra-fast` - Version ultra-rapide
- `Dockerfile.from-mcr` - Version MCR (Alpine)
- `Dockerfile.custom-opencode` - Fork Aux-petits-Oignons
- `Dockerfile.custom-opencode-cached` - Fork avec cache

### Docker Config
- `docker-compose.yml` - Configuration Docker Compose
- `entrypoint.sh` - Script de démarrage container
- `entrypoint-cached.sh` - Script avec cache
- `doc_server.py` - Serveur documentation Flask
- `requirements.txt` - Dépendances Python
- `repo-config.txt` - Configuration repository

### Scripts PowerShell
- `start-custom.ps1` - Démarrage container fork
- `test-opencode.ps1` - Vérification automatique
- `measure-install-time.ps1` - Mesure temps installation

### Documentation
- `README.md` - Documentation principale
- `README-OPTION4.md` - Guide complet Option 4 (fork)
- `README-BUILD-OPTIONS.md` - Comparaison 4 options
- `QUICKSTART-OPTION4.md` - Quick start 11 minutes
- `test-opencode-guide.md` - Guide tests OpenCode

### Icône
- `icone/oignon.ico` - Icône application

---

## 🎯 Raccourcis Créés

### Menu Démarrer
- **Aux petits oignons** - Lance start.bat
- **Documentation (Web)** - Ouvre http://localhost:5545/procedure
- **Documentation Option 4 (Fork Custom)** - Ouvre README-OPTION4.md
- **Guide Rapide Option 4** - Ouvre QUICKSTART-OPTION4.md
- **Build Docker (Menu)** - Lance rebuild-fast.bat
- **Solution Power Platform** - Ouvre %USERPROFILE%\AuxPetitsOignons\Solution
- **Rapports Clients** - Ouvre %USERPROFILE%\AuxPetitsOignons\clients
- **Configuration** - Lance configure.bat
- **Désinstaller Aux petits oignons** - Désinstallation

### Bureau (optionnel)
- **Aux petits oignons** - Lance start.bat

---

## 🔍 Vérifications Pré-Installation

L'installeur vérifie automatiquement :

### ✅ Docker Desktop
- Vérifie si Docker est installé
- Vérifie si Docker est démarré
- Propose le téléchargement si manquant
- **Bloquant** : Installation impossible sans Docker

### ⚠️ Git (Recommandé)
- Vérifie si Git est installé
- Propose le téléchargement si manquant
- **Non bloquant** : Installation possible sans Git
- Le code source sera téléchargé au premier démarrage

---

## 📦 Sortie de Compilation

### Fichier Généré
```
installer/output/AuxPetitsOignons_Setup.exe
```

### Taille Attendue
Environ **50-100 MB** (selon compression)

### Contenu
- Tous les fichiers listés dans setup.iss
- Scripts de vérification Docker/Git
- Scripts de configuration post-installation
- Icône et raccourcis

---

## 🛠️ Dépannage

### Erreur : "Inno Setup n'est pas installé"

**Solution** :
```powershell
.\install-innosetup.ps1
```

Ou installation manuelle depuis https://jrsoftware.org/isdl.php

---

### Erreur : "setup.iss not found"

**Cause** : Mauvais répertoire de travail

**Solution** :
```batch
cd F:\deploy-trad-bot-contanier\installer
compile.bat
```

---

### Erreur : "Source file not found"

**Cause** : Fichier source manquant dans le répertoire parent

**Solution** : Vérifier que tous les fichiers existent :
```powershell
# Vérifier les Dockerfiles
dir ..\Dockerfile*

# Vérifier les scripts PowerShell
dir ..\*.ps1

# Vérifier la documentation
dir ..\README*.md
```

---

### Warning : "SetupIconFile not found"

**Cause** : Fichier `..\icone\oignon.ico` manquant

**Solution** :
```batch
mkdir ..\icone
# Copier oignon.ico dans ..\icone\
```

---

## ✅ Checklist de Compilation

Avant de compiler, vérifier :

- [ ] Inno Setup 6.3.3+ installé
- [ ] Tous les Dockerfiles présents dans `..`
- [ ] Tous les scripts PowerShell présents dans `..`
- [ ] Toute la documentation présente dans `..`
- [ ] Icône `oignon.ico` dans `..\icone\`
- [ ] `conf_opencode/` configuré avec les fichiers
- [ ] `scripts/` complet
- [ ] Version mise à jour dans `setup.iss` (#define MyAppVersion)

Compiler :
```batch
compile.bat
```

Vérifier :
- [ ] Fichier `output\AuxPetitsOignons_Setup.exe` créé
- [ ] Taille raisonnable (50-100 MB)
- [ ] Pas d'erreurs dans la console

---

## 📄 Modification de la Version

Pour changer le numéro de version :

1. Éditer `setup.iss` :
   ```pascal
   #define MyAppVersion "1.3"  // Changer ici
   ```

2. Recompiler :
   ```batch
   compile.bat
   ```

3. L'installeur affichera la nouvelle version

---

## 🔒 Désinstallation

L'installeur inclut un désinstalleur automatique qui :

1. Supprime les exclusions Windows Defender
2. Supprime les fichiers du programme dans `C:\Program Files\AuxPetitsOignons`
3. Demande si on doit supprimer le dossier de données `%USERPROFILE%\AuxPetitsOignons`
   - **Si OUI** : Supprime clients/, Solution/, et src/
   - **Si NON** : Conserve les données utilisateur

---

## 📊 Versions

### v1.3 (Actuelle)
- ✅ Fork Aux-petits-Oignons (Option 4)
- ✅ 5 Dockerfiles (standard, optimized, ultra-fast, from-mcr, custom-opencode)
- ✅ Scripts PowerShell de test et mesure
- ✅ Documentation complète Option 4
- ✅ Menu build Docker interactif
- ✅ Vérifications Docker/Git automatiques

### v1.2
- Dockerfiles multiples
- Documentation web Flask
- Scripts d'automatisation

### v1.1
- Version initiale
- Container Docker standard

---

## 🎉 Prochaines Étapes

Après compilation :

1. **Tester l'installeur** sur une machine propre
2. **Distribuer** `output\AuxPetitsOignons_Setup.exe`
3. Les utilisateurs devront :
   - Installer Docker Desktop
   - Exécuter l'installeur
   - Lancer "Build Docker (Menu)" pour choisir une option
   - Configurer `.env` avec les clés Azure
   - Démarrer "Aux petits oignons"

---

## 📞 Support

Pour toute question sur la compilation :

- **Documentation Option 4** : `README-OPTION4.md`
- **Quick Start** : `QUICKSTART-OPTION4.md`
- **Comparaison options** : `README-BUILD-OPTIONS.md`

---

**Propulsé par Be-Cloud** 🧅
