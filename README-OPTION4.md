# 🧅 Option 4 : Fork Aux-petits-Oignons

**Version sécurisée avec restrictions entreprise**

---

## 📋 Table des Matières

1. [Qu'est-ce que l'Option 4 ?](#quest-ce-que-loption-4-)
2. [Différences avec les autres options](#différences-avec-les-autres-options)
3. [Configuration requise](#configuration-requise)
4. [Installation](#installation)
5. [Premier démarrage](#premier-démarrage)
6. [Utilisation](#utilisation)
7. [Troubleshooting](#troubleshooting)
8. [Mise à jour](#mise-à-jour)

---

## Qu'est-ce que l'Option 4 ?

L'**Option 4** construit un container Docker avec le **fork personnalisé "Aux-petits-Oignons"** d'OpenCode. Ce fork apporte :

### 🔒 **Sécurité Entreprise**

- **4 modèles IA Azure verrouillés** (pas de modèles gratuits externes)
- **Configuration entreprise non modifiable** (`locked: true`)
- **Custom loaders** pour routage Azure automatique
- **Provider adapters** pour chaque endpoint Azure

### 🎯 **Modèles Disponibles**

| Modèle | Provider | Endpoint | Par défaut |
|--------|----------|----------|------------|
| **GPT-4.1 Mini** | Azure OpenAI | `AZURE_OPENAI_ENDPOINT` | ✅ Oui |
| **GPT-5 Mini** | Azure OpenAI | `AZURE_OPENAI_ENDPOINT` | Non |
| **Model-Router** | Azure AI Foundry | `AZURE_AI_FOUNDRY_ENDPOINT` | Non |
| **Claude Sonnet** | Anthropic (Azure) | `ANTHROPIC_BASE_URL` | Non (optionnel) |

### 🎨 **Personnalisation Be-Cloud**

- Message de bienvenue personnalisé
- Branding "Aux petits Oignons"
- Documentation intégrée pour déploiement Bot Traducteur

---

## Différences avec les autres options

| Caractéristique | Option 1-3 | Option 4 (Fork) |
|----------------|-----------|-----------------|
| OpenCode | Standard | Fork custom sécurisé |
| Modèles IA | Tous (Anthropic, OpenAI, etc.) | 4 modèles Azure uniquement |
| Configuration | Modifiable | Verrouillée entreprise |
| Code source | Binaire standard | TypeScript custom avec loaders |
| Sécurité | Standard | Renforcée (pas de fuite données) |
| Installation | ~2-3 min | ~8-9 min (première fois) |
| Taille image | ~2.0 GB | ~2.0 GB |
| Démarrage suivant | Instantané | Instantané |

---

## Configuration requise

### ✅ Prérequis

1. **Docker Desktop** installé et démarré
2. **Git** installé
3. **Espace disque** : 3 GB minimum
4. **RAM** : 4 GB minimum

### 🔑 Clés API Azure

Pour utiliser le fork, vous devez avoir **au minimum 1 endpoint Azure configuré** :

#### Configuration Minimale (1 endpoint)

**Option A : Azure OpenAI** (recommandé)
```env
AZURE_OPENAI_ENDPOINT=https://votre-endpoint.openai.azure.com
AZURE_OPENAI_API_KEY=votre_cle_api_openai
```

**OU Option B : Azure AI Foundry**
```env
AZURE_AI_FOUNDRY_ENDPOINT=https://votre-endpoint.cognitiveservices.azure.com
AZURE_API_KEY=votre_cle_api_foundry
```

#### Configuration Complète (3 endpoints)

```env
# Endpoint 1 : Azure OpenAI (GPT-4.1-mini + GPT-5-mini)
AZURE_OPENAI_ENDPOINT=https://votre-endpoint.openai.azure.com
AZURE_OPENAI_API_KEY=votre_cle_api_openai

# Endpoint 2 : Azure AI Foundry (Model-Router)
AZURE_AI_FOUNDRY_ENDPOINT=https://votre-endpoint.cognitiveservices.azure.com
AZURE_API_KEY=votre_cle_api_foundry

# Endpoint 3 : Anthropic via Azure (Claude Sonnet) - OPTIONNEL
ANTHROPIC_BASE_URL=https://votre-endpoint-claude.services.ai.azure.com/anthropic
ANTHROPIC_API_KEY=votre_cle_api_claude
```

### 📁 Fichier de configuration

Créez ou éditez `conf_opencode/.env` avec vos clés :

```bash
# Copier le template
cp conf_opencode/.env.example conf_opencode/.env

# Éditer avec vos vraies clés
notepad conf_opencode/.env
```

**⚠️ Important** : Si vous ne configurez pas Anthropic, commentez les lignes :
```env
# ANTHROPIC_BASE_URL=...
# ANTHROPIC_API_KEY=...
```

---

## Installation

### Étape 1 : Cloner le repository

```bash
git clone https://github.com/PlumyCat/deploy-trad-bot-contanier.git
cd deploy-trad-bot-contanier
```

### Étape 2 : Configurer les clés API

```bash
# Copier le template
cp conf_opencode/.env.example conf_opencode/.env

# Éditer avec vos clés Azure
notepad conf_opencode/.env
```

### Étape 3 : Lancer le build

```bash
# Lancer le menu de build
rebuild-fast.bat

# Choisir l'option 4
# Appuyer sur 4 puis Entrée
```

**OU directement** :

```bash
docker build -f Dockerfile.custom-opencode -t deploy-trad-bot-contanier-trad-bot-opencode:latest .
```

### ⏱️ Temps de build

- **Build Docker** : 2-3 minutes
- Images de base téléchargées
- Clone du fork Aux-petits-Oignons
- Installation outils (Azure CLI, Bun, etc.)

---

## Premier démarrage

### Étape 1 : Démarrer le container

```bash
# Via docker-compose (recommandé)
docker-compose up -d

# OU via script PowerShell
.\start-custom.ps1

# OU manuellement
docker run -d --name trad-bot-opencode -p 5545:8080 \
  -v "%USERPROFILE%/AuxPetitsOignons/clients:/app/src/clients" \
  -v "%USERPROFILE%/AuxPetitsOignons/Solution:/app/src/Solution" \
  -v "./conf_opencode:/app/conf_opencode_mount" \
  -it deploy-trad-bot-contanier-trad-bot-opencode:latest \
  bash -c "python /app/doc_server.py & exec bash"
```

### Étape 2 : Installation du fork (première fois)

**⏱️ Temps : ~5-6 minutes**

Le container va automatiquement :
1. Installer les dépendances Bun (1818 packages) - ~5 min
2. Mettre à jour baseline-browser-mapping (supprime warning)
3. Créer le wrapper OpenCode
4. Copier la configuration entreprise

**Progression** :
```
==========================================
  Premier démarrage - Compilation du fork
  Aux Petits Oignons (OpenCode custom)
==========================================

Installation des dépendances Bun...
bun install v1.3.6 (d530ed99)
Resolving dependencies
Resolved, downloaded and extracted [360]
...
1818 packages installed [337.30s]
✓ Dépendances installées

Mise à jour baseline-browser-mapping...
Configuration du fork OpenCode...
✓ Fork OpenCode configuré

==========================================
  ✓ Fork Aux Petits Oignons prêt
==========================================
```

### Étape 3 : Vérifier l'installation

```bash
# Accéder au shell du container
docker exec -it trad-bot-opencode bash

# Tester OpenCode
opencode --version
# Output attendu : local

# Lancer OpenCode
opencode
```

### ✅ Démarrages suivants

Après la première installation, les démarrages suivants sont **instantanés** ! Le marqueur `.build_done` indique que le fork est déjà installé.

---

## Utilisation

### Accéder au container

```bash
docker exec -it trad-bot-opencode bash
```

### Lancer OpenCode

```bash
# Nouvelle conversation
opencode

# Reprendre la conversation précédente
opencode -c
```

### Message de bienvenue

Vous verrez ce message au démarrage :

```
========================================
  🧅 Aux Petits Oignons - Be-Cloud
========================================

  Modeles IA disponibles (Azure):
    - GPT-4.1 Mini    (defaut)
    - GPT-5 Mini
    - Model Routeur
    - Claude Sonnet   (si disponible)

  opencode      Nouvelle conversation
  opencode -c   REPRENDRE conversation

  az-update     Mettre a jour Azure CLI

========================================
```

### Changer de modèle

Dans OpenCode, tapez :
```
/settings
```

Puis sélectionnez le modèle souhaité.

### Variables d'environnement chargées automatiquement

Le wrapper OpenCode charge automatiquement votre `.env` :
```bash
# Ces variables sont déjà exportées
echo $AZURE_OPENAI_ENDPOINT
echo $AZURE_AI_FOUNDRY_ENDPOINT
```

---

## Troubleshooting

### ❌ Problème : Warning "baseline-browser-mapping"

**Symptôme** :
```
[baseline-browser-mapping] The data in this module is over two months old...
```

**Solution** : Ce warning est ignorable (juste un avertissement de version). Il est automatiquement supprimé au premier démarrage avec `bun update baseline-browser-mapping`.

Si le warning persiste :
```bash
# Dans le container
cd /opt/aux-petits-oignons
bun update baseline-browser-mapping
```

---

### ❌ Problème : OpenCode demande une clé Anthropic

**Symptôme** :
OpenCode demande `ANTHROPIC_API_KEY` même si vous avez sélectionné GPT-4.1-mini.

**Cause** : Les lignes Anthropic ne sont pas commentées dans `.env`

**Solution** :
```bash
# Éditer conf_opencode/.env
notepad conf_opencode/.env

# Commenter les lignes Anthropic
# ANTHROPIC_BASE_URL=...
# ANTHROPIC_API_KEY=...

# Redémarrer le container
docker restart trad-bot-opencode
```

---

### ❌ Problème : "bun install" échoue

**Symptôme** :
```
error: Cannot find module '@opentui/solid/scripts/solid-plugin'
```

**Cause** : Problème de dépendances Bun workspace

**Solution** : Utiliser l'approche actuelle (runtime install) ou passer à l'Option B (cached).

---

### ❌ Problème : "opencode: command not found"

**Symptôme** :
```bash
opencode
bash: opencode: command not found
```

**Cause** : Le fork n'est pas encore installé

**Solution** :
1. Vérifier si `.build_done` existe :
   ```bash
   ls -la /opt/aux-petits-oignons/.build_done
   ```

2. Si absent, redémarrer le container :
   ```bash
   docker restart trad-bot-opencode
   ```

3. Attendre 5-6 minutes que `bun install` se termine

4. Vérifier les logs :
   ```bash
   docker logs trad-bot-opencode
   ```

---

### ❌ Problème : Container ne démarre pas

**Symptôme** :
```bash
docker ps
# Container absent
```

**Solution** :
1. Vérifier les logs :
   ```bash
   docker logs trad-bot-opencode
   ```

2. Vérifier que les volumes existent :
   ```bash
   mkdir -p "%USERPROFILE%/AuxPetitsOignons/clients"
   mkdir -p "%USERPROFILE%/AuxPetitsOignons/Solution"
   ```

3. Relancer :
   ```bash
   docker-compose up -d
   ```

---

### ❌ Problème : Erreur "invalid API key"

**Symptôme** :
OpenCode démarre mais répond avec "Invalid API key"

**Cause** : Clé API incorrecte ou endpoint mal configuré

**Solution** :
1. Vérifier le fichier `.env` :
   ```bash
   docker exec trad-bot-opencode cat /root/.config/opencode/.env
   ```

2. Tester l'endpoint :
   ```bash
   curl -H "api-key: VOTRE_CLE" https://votre-endpoint.openai.azure.com/openai/deployments?api-version=2024-02-01
   ```

3. Si erreur, vérifier dans Azure Portal :
   - Clé API copiée correctement
   - Endpoint URL exact (avec `/`)
   - Déploiement du modèle actif

---

## Mise à jour

### Mettre à jour le fork Aux-petits-Oignons

Si le fork GitHub est mis à jour :

```bash
# 1. Arrêter le container
docker stop trad-bot-opencode
docker rm trad-bot-opencode

# 2. Rebuild l'image (récupère la dernière version du fork)
docker build -f Dockerfile.custom-opencode -t deploy-trad-bot-contanier-trad-bot-opencode:latest .

# 3. Redémarrer
docker-compose up -d
```

### Mettre à jour Azure CLI dans le container

```bash
# Depuis le container
az-update

# OU
az upgrade --yes
```

---

## 📊 Résumé des Temps

| Opération | Temps |
|-----------|-------|
| Build Docker (première fois) | 2-3 min |
| Premier démarrage (bun install) | 5-6 min |
| **Total première installation** | **~8-9 min** |
| Démarrages suivants | ⚡ Instantané |
| Rebuild image (mise à jour fork) | 2-3 min |

---

## 🔧 Fichiers de Configuration

### Structure des fichiers

```
deploy-trad-bot-contanier/
├── Dockerfile.custom-opencode     # Dockerfile pour Option 4
├── entrypoint.sh                  # Script de démarrage
├── conf_opencode/
│   ├── .env                       # VOS clés API (à créer)
│   ├── .env.example               # Template de config
│   └── CLAUDE.md                  # Welcome page personnalisée
├── rebuild-fast.bat               # Menu de build
├── start-custom.ps1               # Script de démarrage container
├── test-opencode.ps1              # Script de vérification
├── test-opencode-guide.md         # Guide de test détaillé
└── README-OPTION4.md              # Cette documentation
```

### enterprise-config.json (dans le container)

Fichier de configuration verrouillée du fork :

```json
{
  "projectName": "Aux petits Oignons",
  "aiModels": [
    {
      "id": "gpt-4.1-mini",
      "default": true,
      "enabled": true,
      "provider": "azure"
    },
    {
      "id": "gpt-5-mini",
      "enabled": true,
      "provider": "azure"
    },
    {
      "id": "model-routeur",
      "enabled": true,
      "provider": "azure"
    },
    {
      "id": "claude-sonnet",
      "enabled": false,
      "provider": "anthropic"
    }
  ],
  "locked": true
}
```

**⚠️ Ce fichier ne peut pas être modifié** (sécurité entreprise).

---

## 📚 Ressources

### Documentation

- **Guide de test** : `test-opencode-guide.md`
- **Documentation Power Platform** : http://localhost:5545/procedure (dans le container)
- **GitHub Fork** : https://github.com/PlumyCat/Aux-petits-Oignons
- **GitHub Projet** : https://github.com/PlumyCat/deploy-trad-bot-contanier

### Scripts utiles

```bash
# Vérification rapide
.\test-opencode.ps1

# Mesure temps d'installation
.\measure-install-time.ps1

# Démarrage container
.\start-custom.ps1

# Build avec menu
.\rebuild-fast.bat
```

### Commandes Docker utiles

```bash
# Voir les logs du container
docker logs trad-bot-opencode

# Suivre les logs en temps réel
docker logs -f trad-bot-opencode

# Accéder au shell
docker exec -it trad-bot-opencode bash

# Redémarrer le container
docker restart trad-bot-opencode

# Arrêter et supprimer
docker stop trad-bot-opencode
docker rm trad-bot-opencode

# Voir les images Docker
docker images | grep trad-bot

# Nettoyer les images inutilisées
docker image prune -a
```

---

## ✅ Checklist Post-Installation

Après l'installation, vérifiez que :

- [ ] Container démarré : `docker ps | grep trad-bot`
- [ ] Fork installé : `docker exec trad-bot-opencode test -f /opt/aux-petits-oignons/.build_done`
- [ ] OpenCode fonctionne : `docker exec trad-bot-opencode opencode --version`
- [ ] Pas de warning baseline : Lancer `opencode` et vérifier
- [ ] Clés API configurées : Tester une question dans OpenCode
- [ ] Modèles accessibles : Tester GPT-4.1-mini (défaut)
- [ ] Documentation accessible : http://localhost:5545/procedure

---

## 🆘 Support

En cas de problème :

1. **Vérifier les logs** : `docker logs trad-bot-opencode`
2. **Consulter le guide de test** : `test-opencode-guide.md`
3. **Tester manuellement** : `.\test-opencode.ps1`
4. **Mesurer les temps** : `.\measure-install-time.ps1`
5. **Issues GitHub** : https://github.com/PlumyCat/deploy-trad-bot-contanier/issues

---

**🎉 Félicitations ! Vous avez installé le fork Aux-petits-Oignons avec succès !**

_Propulsé par Be-Cloud 🧅_
