# 🏗️ Guide des Options de Build

**Menu de build rapide : rebuild-fast.bat**

Ce guide explique les **4 options de build** disponibles pour construire votre container Docker.

---

## 📋 Vue d'ensemble

```
========================================
   MENU DE BUILD DOCKER
========================================

Choisissez votre option de build:

1. BuildKit Cache Mounts (Recommandé)
2. Ultra-Fast (Binaire direct)
3. Microsoft Base Image
4. Fork Aux-petits-Oignons (Sécurité Entreprise)
5. Quitter

Votre choix (1/2/3/4/5) :
```

---

## Option 1 : BuildKit Cache Mounts ⚡ **(Recommandé)**

### 📌 Description

Build optimisé avec **cache persistant BuildKit** pour les packages système.

### ✅ Avantages

- ⚡ **Rapide** : Cache APT/pip persistant entre builds
- 🔄 **Rebuild rapide** : Packages déjà téléchargés réutilisés
- 📦 **Taille optimale** : ~2.0 GB
- 🐳 **Standard Docker** : Fonctionne partout

### 📊 Performance

| Opération | Temps |
|-----------|-------|
| Premier build | 8-10 min |
| Rebuild (avec cache) | 2-3 min |
| Taille image | 2.0 GB |

### 🎯 Quand l'utiliser ?

- **Usage général** (recommandé)
- Développement avec rebuilds fréquents
- Serveur CI/CD

### 📁 Fichier

`Dockerfile.optimized`

---

## Option 2 : Ultra-Fast (Binaire direct) 🚀

### 📌 Description

Build avec **téléchargement direct** du binaire Azure Functions Core Tools (pas d'installation APT).

### ✅ Avantages

- 🚀 **Le plus rapide** : Télécharge le binaire directement
- ⚡ **Build éclair** : Skip l'installation .NET SDK
- 📦 **Léger** : ~1.8 GB

### ⚠️ Inconvénients

- ❌ **Moins stable** : Dépend de la disponibilité du binaire
- ❌ **Pas de .NET SDK** : Limité aux fonctions Python

### 📊 Performance

| Opération | Temps |
|-----------|-------|
| Premier build | 5-7 min |
| Rebuild | 1-2 min |
| Taille image | 1.8 GB |

### 🎯 Quand l'utiliser ?

- Prototypage rapide
- CI/CD avec contrainte de temps
- Tests temporaires

### 📁 Fichier

`Dockerfile.ultra-fast`

---

## Option 3 : Microsoft Base Image 🏢

### 📌 Description

Build basé sur l'**image officielle Microsoft** `mcr.microsoft.com/azure-cli`.

### ✅ Avantages

- ✅ **Azure CLI préinstallé** : Gain de temps
- ✅ **Image officielle** : Supportée par Microsoft
- ✅ **Toujours à jour** : Dernière version Azure CLI

### ⚠️ Inconvénients

- ❌ **Alpine Linux** : Incompatibilités possibles
- ❌ **Entrypoint complexe** : Modification nécessaire
- ❌ **Plus gros** : ~2.5 GB

### 📊 Performance

| Opération | Temps |
|-----------|-------|
| Premier build | 10-12 min |
| Rebuild | 3-4 min |
| Taille image | 2.5 GB |

### 🎯 Quand l'utiliser ?

- Environnement 100% Microsoft
- Besoin de l'image officielle
- Déploiement Azure managed

### 📁 Fichier

`Dockerfile.from-mcr`

---

## Option 4 : Fork Aux-petits-Oignons 🔒 **(Sécurité Entreprise)**

### 📌 Description

Build avec le **fork personnalisé OpenCode** incluant des restrictions de sécurité entreprise.

### ✅ Avantages

- 🔒 **Sécurité renforcée** : 4 modèles Azure verrouillés
- 🎨 **Branding Be-Cloud** : Message de bienvenue personnalisé
- ⚙️ **Config entreprise** : Paramètres non modifiables
- 🔌 **Custom loaders** : Routage Azure automatique
- 🚫 **Pas de fuite données** : Aucun modèle gratuit externe

### 🎯 Modèles IA disponibles

| Modèle | Provider | Défaut |
|--------|----------|--------|
| GPT-4.1 Mini | Azure OpenAI | ✅ |
| GPT-5 Mini | Azure OpenAI | |
| Model-Router | Azure AI Foundry | |
| Claude Sonnet | Anthropic (Azure) | (optionnel) |

### 📊 Performance

| Opération | Temps |
|-----------|-------|
| Build Docker | 2-3 min |
| Premier démarrage (bun install) | 5-6 min |
| **Total première installation** | **~8-9 min** |
| Démarrages suivants | ⚡ Instantané |
| Taille image | 2.0 GB |

### 🔑 Configuration requise

**Minimum 1 endpoint Azure** :
- Azure OpenAI (GPT-4.1/GPT-5)
- OU Azure AI Foundry (Model-Router)
- OU Anthropic via Azure (Claude Sonnet)

Fichier : `conf_opencode/.env`

### 🎯 Quand l'utiliser ?

- **Déploiement client** (données sensibles)
- Environnement de production
- Besoin de contrôle strict des modèles IA
- Conformité RGPD/sécurité

### 📁 Fichiers

- `Dockerfile.custom-opencode`
- `entrypoint.sh` (avec install runtime)
- `README-OPTION4.md` (documentation complète) 📖

### 📚 Documentation détaillée

👉 **[Lire la documentation complète de l'Option 4](./README-OPTION4.md)**

---

## 📊 Tableau Comparatif

| Critère | Option 1 | Option 2 | Option 3 | Option 4 |
|---------|----------|----------|----------|----------|
| **Nom** | BuildKit Cache | Ultra-Fast | MCR Base | Fork Custom |
| **Build temps** | 2-3 min | 1-2 min | 3-4 min | 2-3 min + 5-6 min runtime |
| **Taille** | 2.0 GB | 1.8 GB | 2.5 GB | 2.0 GB |
| **OpenCode** | Standard | Standard | Standard | Fork sécurisé |
| **Modèles IA** | Tous | Tous | Tous | 4 Azure uniquement |
| **Sécurité** | Standard | Standard | Standard | Entreprise ✅ |
| **Stabilité** | ✅ Haute | ⚠️ Moyenne | ✅ Haute | ✅ Haute |
| **Recommandé pour** | Usage général | Prototypage | Env. Microsoft | Production client |

---

## 🚀 Utilisation du Menu

### Lancer le menu

```bash
rebuild-fast.bat
```

### Sélectionner une option

```
Votre choix (1/2/3/4/5) : 4
```

### Build automatique

Le script va :
1. Builder l'image Docker avec le Dockerfile correspondant
2. Afficher la progression
3. Confirmer le succès
4. Afficher les informations de l'image

---

## 🎯 Recommandations par Cas d'Usage

### 🏠 Utilisation personnelle / Développement

**Option 1 - BuildKit Cache** ✅
- Build rapide
- Stable et fiable
- Tous les outils disponibles

### 🚀 Prototypage / Tests rapides

**Option 2 - Ultra-Fast** ✅
- Le plus rapide
- Léger
- Parfait pour tests temporaires

### 🏢 Environnement Microsoft / Azure

**Option 3 - MCR Base** ✅
- Image officielle Microsoft
- Azure CLI préinstallé
- Support garanti

### 🔒 Production Client / Données Sensibles

**Option 4 - Fork Aux-petits-Oignons** ✅✅✅
- Sécurité renforcée
- Configuration verrouillée
- Contrôle strict des modèles IA
- Pas de fuite de données

---

## 📁 Structure des Fichiers

```
deploy-trad-bot-contanier/
├── rebuild-fast.bat              # Menu de build principal
├── Dockerfile                    # Dockerfile standard
├── Dockerfile.optimized          # Option 1
├── Dockerfile.ultra-fast         # Option 2
├── Dockerfile.from-mcr           # Option 3
├── Dockerfile.custom-opencode    # Option 4
├── entrypoint.sh                 # Entrypoint pour Option 4
├── README-BUILD-OPTIONS.md       # Cette documentation
└── README-OPTION4.md             # Documentation détaillée Option 4
```

---

## 🆘 Troubleshooting

### Build échoue avec "cache mount"

**Symptôme** : Erreur avec `--mount=type=cache`

**Cause** : BuildKit pas activé

**Solution** :
```bash
# Activer BuildKit
set DOCKER_BUILDKIT=1

# OU éditer Docker Desktop > Settings > Docker Engine
{
  "features": {
    "buildkit": true
  }
}
```

### Option 4 - Container ne démarre pas

Consultez **[README-OPTION4.md - Section Troubleshooting](./README-OPTION4.md#troubleshooting)**

### Build très long

**Solutions** :
1. Vérifier connexion Internet
2. Utiliser Option 2 (Ultra-Fast)
3. Vérifier cache Docker : `docker system df`
4. Nettoyer : `docker system prune -a`

---

## 🔄 Mise à Jour

### Mettre à jour les Dockerfiles

```bash
git pull origin main
```

### Rebuild l'image

```bash
rebuild-fast.bat
# Choisir votre option
```

---

## 📚 Documentation Complémentaire

- **Option 4 détaillée** : [README-OPTION4.md](./README-OPTION4.md)
- **Guide de test Option 4** : [test-opencode-guide.md](./test-opencode-guide.md)
- **Documentation Power Platform** : http://localhost:5545/procedure (dans le container)

---

## ✅ Checklist de Build

Avant de builder :

- [ ] Docker Desktop démarré
- [ ] Espace disque suffisant (3 GB minimum)
- [ ] Connexion Internet active
- [ ] Pour Option 4 : `.env` configuré avec clés Azure
- [ ] BuildKit activé (pour Option 1)

---

**🎉 Bon build !**

_Propulsé par Be-Cloud 🧅_
