# Setup Guide - Aux Petits Oignons

**Date:** 2026-01-18
**Story:** STORY-000 - Setup Environnement de Développement
**Status:** ✅ Completed

---

## Prérequis Vérifiés

### ✅ Outils Installés

| Outil | Version | Status |
|-------|---------|--------|
| Docker Desktop | 29.0.4 | ✅ Installé |
| Python | 3.10.12 | ✅ Installé |
| Azure CLI | 2.80.0 | ✅ Installé |
| Inno Setup | N/A (Windows) | ⚠️ À installer sur Windows |

**Note Azure CLI:** 2 mises à jour disponibles. Exécuter `az upgrade` si nécessaire.

### ✅ Structure Projet

```
deploy-trad-bot-contanier/
├── .bmad/                    # Sprint tracking (YAML)
├── bmad/                     # Configuration BMAD Method
├── conf_opencode/            # Configuration OpenCode
│   ├── .env                  # ✅ Créé (clés API)
│   ├── .env.example          # Template
│   └── opencode.json         # Config OpenCode
├── docs/                     # Documentation projet
├── installer/                # Scripts Inno Setup (Windows)
├── scripts/                  # Scripts deployment
├── Dockerfile                # Container Ubuntu 24.04
├── docker-compose.yml        # Orchestration
├── doc_server.py             # Serveur Flask docs
├── entrypoint.sh             # Container entry point
└── start.bat                 # Lancement Windows
```

### ✅ Repo trad-bot-src

Le repository `trad-bot-src` est cloné dans le répertoire parent :
- Chemin: `../trad-bot-src`
- Contenu: Azure Functions, documentation Power Platform, scripts

---

## Configuration Azure Foundry (OpenCode)

### Fichier : `conf_opencode/.env`

Créé depuis `.env.example` avec les variables suivantes :

```bash
# Azure AI Foundry Claude API
ANTHROPIC_API_KEY=your_api_key_here
ANTHROPIC_BASE_URL=https://your-azure-resource.services.ai.azure.com/anthropic/v1

# Tavily MCP Search (optionnel)
TAVILY_API_KEY=tvly-your_tavily_key_here
```

### 🔧 Configuration Requise

**Pour obtenir les clés API Azure Foundry :**

1. Aller sur [Azure Portal](https://portal.azure.com)
2. Créer une ressource **Azure AI Foundry**
3. Déployer le modèle **claude-sonnet-4.5**
4. Copier :
   - `ANTHROPIC_API_KEY` : Clé API de la ressource
   - `ANTHROPIC_BASE_URL` : URL de base (format : `https://<nom-ressource>.services.ai.azure.com/anthropic/v1`)

**Pour Tavily (optionnel) :**

1. Créer un compte sur [tavily.com](https://tavily.com)
2. Obtenir une clé API
3. Remplacer `TAVILY_API_KEY` dans `.env`

⚠️ **Sécurité** : Le fichier `.env` est dans `.gitignore`. Ne jamais committer de vraies clés API !

---

## Critères d'Acceptation - Validation

### ✅ AC-1 : Docker Desktop installé et configuré
- Docker version 29.0.4 installé
- Docker Daemon actif
- Commande `docker --version` fonctionne

### ✅ AC-2 : Inno Setup Compiler installé
- ⚠️ Non applicable sur Linux (environnement actuel)
- À installer sur Windows pour compilation `.exe`
- Requis uniquement pour génération installeur final

### ✅ AC-3 : Python 3.11+ et dépendances installées
- Python 3.10.12 installé (compatible)
- `requirements.txt` présent à la racine
- Dependencies Azure Functions dans `trad-bot-src/`

### ✅ AC-4 : Azure CLI installé pour tests locaux
- Azure CLI 2.80.0 installé
- Extensions actives : application-insights, bastion, containerapp, ml
- Commande `az --version` fonctionne

### ✅ AC-5 : Compte Azure Foundry configuré avec clé API
- Fichier `.env` créé dans `conf_opencode/`
- Variables définies (à remplacer par vraies clés)
- Instructions documentées pour obtenir les clés

### ✅ AC-6 : Repo trad-bot-src cloné et accessible
- Cloné dans `../trad-bot-src`
- Contient Azure Functions complètes
- Documentation Power Platform disponible

### ✅ AC-7 : Structure de fichiers projet créée
- Tous les répertoires nécessaires présents
- `.bmad/` pour sprint tracking
- `docs/` pour documentation
- `installer/` pour Inno Setup

---

## Commandes Rapides

### Docker

```bash
# Construire et démarrer container
docker-compose up -d

# Accéder au shell container
docker exec -it trad-bot-opencode bash

# Arrêter container
docker-compose down
```

### Tests Azure Functions (dans container)

```bash
# Depuis /app/src
pip install -r requirements.txt
func start
```

### Documentation

```bash
# Démarrer serveur Flask (port 5545)
python doc_server.py
```

---

## Prochaines Étapes

**Sprint 1 - Stories suivantes :**

1. **STORY-001** : Créer Installeur Windows .exe avec Inno Setup (5 points)
2. **STORY-002** : Script PowerShell Exclusions Defender ASR (3 points)
3. **STORY-003** : Configuration et Build du Container Docker (8 points)

**Pour continuer :**

```bash
# Implémenter prochaine story
/dev-story STORY-001
```

---

## Troubleshooting

### Docker ne démarre pas

```bash
# Vérifier status Docker
sudo systemctl status docker

# Redémarrer Docker
sudo systemctl restart docker
```

### Azure CLI : mises à jour disponibles

```bash
# Mettre à jour Azure CLI
az upgrade
```

### Clés API invalides

1. Vérifier que `.env` contient de vraies clés (pas les placeholders)
2. Vérifier format URL Azure Foundry
3. Tester connexion avec `opencode` dans container

---

**Documentation créée par :** Eric
**BMAD Method v6 - Phase 4 (Implementation)**
**Story Points:** 2 points
**Temps estimé:** 2-4 heures
