# Création de l'installeur "Aux petits oignons"

## Prérequis

1. **Inno Setup** - Télécharger et installer depuis : https://jrsoftware.org/isdl.php

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
- **Documentation (Web)** → Ouvre http://localhost:5545/procedure
- **Désinstaller** → Désinstallation propre
