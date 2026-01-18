# Création de l'installeur "Aux petits oignons"

## Prérequis

1. **Inno Setup 6.x** - Télécharger et installer depuis : https://jrsoftware.org/isdl.php
2. **Windows 10/11** - Système d'exploitation cible pour la compilation et l'installation

## Fichiers nécessaires

```
installer/
├── setup.iss      # Script Inno Setup
├── oignon.ico     # Icône de l'application (à ajouter)
└── output/        # Dossier de sortie (créé automatiquement)
```

## Icône

Placer l'icône au format `.ico` dans ce dossier avec le nom `oignon.ico`.

Conversion PNG → ICO : https://convertio.co/png-ico/

Tailles recommandées dans le .ico : 16x16, 32x32, 48x48, 256x256

## Générer l'installeur

### Option 1 : Interface graphique
1. Ouvrir Inno Setup Compiler
2. File → Open → `setup.iss`
3. Build → Compile (Ctrl+F9)
4. L'installeur sera créé dans `installer/output/AuxPetitsOignons_Setup.exe`

### Option 2 : Ligne de commande
```cmd
"C:\Program Files (x86)\Inno Setup 6\ISCC.exe" setup.iss
```

## Ce que fait l'installeur

1. ✅ Vérifie si Docker Desktop est installé
2. ✅ Si non → propose d'ouvrir la page de téléchargement
3. ✅ Copie tous les fichiers du projet
4. ✅ Build l'image Docker automatiquement
5. ✅ Crée les raccourcis (Menu Démarrer + Bureau)
6. ✅ Propose de lancer l'application

## Raccourcis créés

- **Aux petits oignons** → Lance `start.bat` (OpenCode + Doc)
- **Configuration** → Configure les clés API (Azure Foundry, Tavily)
- **Documentation (Web)** → Ouvre http://localhost:5545/procedure
- **Solution Power Platform** → Accès direct au dossier Solution
- **Rapports Clients** → Accès direct aux rapports
- **Désinstaller** → Désinstallation propre

## Sécurité - Defender ASR

⚠️ **IMPORTANT** : L'installeur n'est PAS signé avec un certificat (coût non justifié pour 2-3 utilisateurs).

### Exclusions Windows Defender

La désinstallation supprime automatiquement les exclusions Defender créées lors de l'installation.

Si vous rencontrez des problèmes, les exclusions ASR doivent être configurées **après** l'installation via STORY-002 (Script PowerShell dédié).

### Taille et Performance

- **Taille .exe** : < 50MB (sans images Docker)
- **Temps installation** : < 2 minutes (dépend de la vitesse du disque)
- **Espace disque requis** : ~500MB (installation + données)

## Validation Pre-Build

Avant de compiler sur Windows, valider que tous les fichiers sont présents :

```bash
# Sur Linux/Mac
bash installer/validate.sh

# Sur Windows (PowerShell)
.\installer\validate.ps1
```

## Désinstallation

La désinstallation :
1. ✅ Supprime les fichiers de l'application
2. ✅ Supprime les exclusions Defender automatiquement
3. ❓ Demande si les données utilisateur doivent être supprimées (clients/, Solution/)

## Troubleshooting

### Docker n'est pas détecté

Vérifier que Docker Desktop est installé ET démarré avant de lancer l'installeur.

### L'exe est bloqué par Windows Defender

Utiliser le script PowerShell de STORY-002 pour créer les exclusions ASR nécessaires.

### Compilation échoue sur Inno Setup

1. Vérifier que tous les fichiers source existent (voir `validate.sh`)
2. Vérifier la version d'Inno Setup (6.x requis)
3. Vérifier les chemins relatifs dans `setup.iss`
