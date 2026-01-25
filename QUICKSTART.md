# Quick Start - Aux petits Oignons

Installation rapide en 3 étapes

## 1. Build de l'image Docker (2-3 min)

```batch
rebuild-fast.bat
```

Attendez que le build soit terminé. Vous verrez :
```
========================================
  BUILD REUSSI - FORK CUSTOM
========================================
```

## 2. Premier démarrage (6-8 min)

```batch
start.bat
```

**Au premier démarrage uniquement** :
- Le container va installer les dépendances Bun (~6 min)
- Un fichier `.build_done` sera créé
- Les démarrages suivants seront instantanés

## 3. Utilisation

Après le premier démarrage :
- Documentation web : http://localhost:5545/procedure
- Fenêtre OpenCode s'ouvre automatiquement
- 3 modèles Azure disponibles

---

## Dépannage

### Erreur "No services to build"

**Cause** : Image Docker pas encore créée

**Solution** : Lancez `rebuild-fast.bat` d'abord

### Container "unhealthy"

**Cause** : Image Docker manquante ou corrompue

**Solution** :
```batch
rebuild-fast.bat
start.bat
```

### OpenCode demande credentials Anthropic

**Cause** : Fichier `.env` manquant

**Solution** : Le fichier `conf_opencode/.env` doit exister avec les clés Azure pré-configurées
