# System Architecture: Aux Petits Oignons

**Date:** 2026-01-18
**Author:** Eric (System Architect)
**Version:** 1.0
**Project Type:** Deployment Automation Tool
**Project Level:** 2 (Medium - 5-15 stories)
**Status:** Approved

---

## Document Overview

This architecture document defines the system design for "Aux Petits Oignons" - a deployment automation tool for Bot Traducteur (Translator Bot) with Azure services. It addresses all functional and non-functional requirements from the PRD and provides implementation guidance for development teams.

**Related Documents:**
- Product Brief: `docs/product-brief-aux-petits-oignons-2026-01-18.md`
- Product Requirements Document: `docs/prd-aux-petits-oignons-2026-01-18.md`

---

## Executive Summary

Aux Petits Oignons utilise une architecture en couches basée sur un container Docker pour fournir un environnement d'automatisation de déploiement Azure isolé, reproductible et guidé par IA. L'architecture privilégie la simplicité, la fiabilité et la facilité de maintenance pour un projet Level 2, tout en garantissant la sécurité (aucun stockage de credentials) et la standardisation (SKU F0 imposé pour Azure Translator).

**Architecture clé:**
- **Pattern:** Layered Architecture avec container-based deployment
- **Composants:** 6 composants principaux
- **Stack:** Windows exe + Docker + OpenCode (Azure Foundry) + Azure CLI + Flask + PowerShell
- **Déploiement:** Local (poste technicien) → Azure (services client)

---

## Architectural Drivers

Les NFRs suivantes ont un impact significatif sur l'architecture et dictent les décisions de conception:

### Driver 1: NFR-003 - Security (Aucun stockage de credentials)

**Impact:** **CRITIQUE**

**Exigence:** Le système ne doit JAMAIS stocker de credentials de manière persistante.

**Décisions architecturales:**
- Container éphémère sans volumes persistants pour credentials
- OpenCode fournit credentials via terminal (affichage uniquement)
- Aucun fichier .env ou configuration stockant des clés
- Logs filtrés pour exclure toute information sensible
- Session Azure CLI dans le container uniquement (pas de cache permanent)

**Validation:** Scan de sécurité du container + code review

---

### Driver 2: NFR-007 - Maintainability (Mises à jour Azure CLI)

**Impact:** **HAUT**

**Exigence:** Azure CLI nécessite des mises à jour fréquentes pour suivre les évolutions API Azure.

**Décisions architecturales:**
- Container Docker versionné avec tags (v1.0, v1.1, etc.)
- Dockerfile avec version Azure CLI explicite
- Processus de rebuild du container documenté
- Rollback possible vers version précédente si breaking changes
- Script de test post-mise à jour

**Validation:** Tests de compatibilité après chaque mise à jour Azure CLI

---

### Driver 3: NFR-001 & NFR-002 - Performance (Temps de démarrage et déploiement)

**Impact:** **MOYEN**

**Exigence:**
- Container opérationnel en < 2 minutes
- Déploiement Azure complet en < 15 minutes

**Décisions architecturales:**
- Image Docker optimisée (layers cachés, dépendances pré-installées)
- Azure CLI pré-authentifié dans le container (session temporaire)
- Flask en mode production (pas de reload automatique)
- Parallélisation des déploiements Azure quand possible

**Validation:** Tests de performance avec métriques temps réel

---

### Driver 4: NFR-005 - Reliability (Gestion d'erreurs Azure CLI)

**Impact:** **HAUT**

**Exigence:** Détecter et gérer gracieusement les erreurs Azure CLI avec messages compréhensibles.

**Décisions architecturales:**
- Wrapper Python autour d'Azure CLI pour capture d'erreurs
- Mapping des codes d'erreur Azure vers messages français clairs
- Retry automatique pour erreurs temporaires (timeout, réseau)
- Logging détaillé pour debugging (sans credentials)

**Validation:** Tests d'erreurs avec scénarios simulés (permissions insuffisantes, MFA, etc.)

---

### Driver 5: NFR-006 - Usability (Interface conversationnelle simple)

**Impact:** **MOYEN**

**Exigence:** OpenCode doit communiquer en langage simple adapté à des non-experts Azure.

**Décisions architecturales:**
- Prompts OpenCode en français avec explications contextuelles
- Glossaire Azure intégré (terme technique → explication)
- Confirmations explicites avant actions critiques
- Feedback positif à chaque étape réussie

**Validation:** Tests utilisateurs avec les 2 techniciens Modern Workplace

---

## High-Level Architecture

### Architectural Pattern

**Pattern choisi:** **Layered Architecture avec Container-Based Deployment**

**Rationale:**
- **Simplicité:** Adapté pour projet Level 2 (5-15 stories)
- **Isolation:** Container Docker garantit environnement reproductible
- **Portabilité:** Facile à distribuer (exe + container)
- **Séparation des préoccupations:** Layers clairs (Installer → Container → Services → Azure)

**Trade-offs:**
- ✓ **Gain:** Simplicité de déploiement, isolation environnement, reproductibilité
- ✗ **Perte:** Nécessite Docker Desktop (dépendance), moins flexible qu'une architecture microservices
- **Justification:** Pour 2-3 utilisateurs, simplicité > flexibilité

---

### High-Level Components

```
┌─────────────────────────────────────────────────────────────┐
│                    Poste Technicien (Windows)               │
│  ┌───────────────────────────────────────────────────────┐  │
│  │  1. Windows Installer (.exe)                          │  │
│  │     - Inno Setup package                              │  │
│  │     - Crée arborescence                               │  │
│  │     - Lance start.bat                                 │  │
│  └──────────────────┬────────────────────────────────────┘  │
│                     │                                        │
│  ┌──────────────────▼────────────────────────────────────┐  │
│  │  2. PowerShell Security Manager                       │  │
│  │     - Script ASR exclusions                           │  │
│  │     - Mode administrateur                             │  │
│  └───────────────────────────────────────────────────────┘  │
│                                                               │
│  ┌───────────────────────────────────────────────────────┐  │
│  │  Docker Desktop                                        │  │
│  │  ┌─────────────────────────────────────────────────┐  │  │
│  │  │  3. Docker Container (Ubuntu 24.04)             │  │  │
│  │  │  ┌─────────────────────────────────────────┐    │  │  │
│  │  │  │ 4. OpenCode Service (AI Assistant)      │    │  │  │
│  │  │  │    - Azure Foundry connection           │    │  │  │
│  │  │  │    - Conversation engine                │    │  │  │
│  │  │  │    - Deployment orchestration           │    │  │  │
│  │  │  └─────────────────────────────────────────┘    │  │  │
│  │  │  ┌─────────────────────────────────────────┐    │  │  │
│  │  │  │ 5. Flask Documentation Server           │    │  │  │
│  │  │  │    - Serve Power Platform docs          │    │  │  │
│  │  │  │    - Port 5545                          │    │  │  │
│  │  │  └─────────────────────────────────────────┘    │  │  │
│  │  │  ┌─────────────────────────────────────────┐    │  │  │
│  │  │  │ 6. Azure CLI Automation Layer           │    │  │  │
│  │  │  │    - Python wrapper                     │    │  │  │
│  │  │  │    - Error handling                     │    │  │  │
│  │  │  │    - Deployment scripts                 │    │  │  │
│  │  │  └─────────────────────────────────────────┘    │  │  │
│  │  │  ┌─────────────────────────────────────────┐    │  │  │
│  │  │  │ Repository Manager                      │    │  │  │
│  │  │  │    - Clone trad-bot-src                 │    │  │  │
│  │  │  └─────────────────────────────────────────┘    │  │  │
│  │  └─────────────────────────────────────────────────┘  │  │
│  └───────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                           │
                           │ HTTPS (Azure CLI)
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│                   Azure (Client Tenant)                     │
│  ┌────────────┐  ┌────────────┐  ┌────────────┐            │
│  │  Storage   │  │ Translator │  │ Functions  │            │
│  │  Account   │  │   (F0)     │  │  (Python)  │            │
│  └────────────┘  └────────────┘  └────────────┘            │
└─────────────────────────────────────────────────────────────┘
```

---

### Data Flow

**Flow 1: Installation**
```
User → Windows Installer (.exe)
  → Crée structure fichiers
  → Affiche instructions PowerShell ASR
User → Exécute script PowerShell (admin)
  → Exclusions Defender créées
User → Lance start.bat
  → Docker container démarre
  → OpenCode ready
  → Flask serveur ready
  → Browser opens localhost:5545
```

**Flow 2: Déploiement Azure**
```
User → OpenCode: "Nouveau déploiement Bot Traducteur"
  → OpenCode: Demande connexion Azure
  → User: Se connecte (az login --tenant <tenant-id>)
  → OpenCode: Vérifie permissions
  → OpenCode: Crée Storage Account
    → Azure CLI wrapper → Azure API
    → Retour: Account name + keys
  → OpenCode: Affiche credentials (sans stockage)
  → OpenCode: Crée Translator (SKU F0 imposé)
    → Azure CLI wrapper → Azure API
    → Retour: Endpoint + key
  → OpenCode: Affiche credentials
  → OpenCode: Déploie Functions
    → Azure CLI wrapper → Azure API
    → Configure variables env
    → Retour: Function URL
  → OpenCode: Génère rapport intervention
  → OpenCode: Affiche rapport
User → Copie rapport dans ticket
```

**Flow 3: Documentation Power Platform**
```
User → Browser: http://localhost:5545/procedure
  → Flask: Sert documentation
  → Browser: Affiche HTML/Markdown
User → Suit procédure Power Platform
  → Autonome (hors scope automation)
```

---

## Technology Stack

### 1. Windows Installer

**Choice:** Inno Setup

**Rationale:**
- **Gratuit et open-source:** Pas de coût de licence
- **Mature et stable:** Utilisé depuis 20+ ans, très fiable
- **Scriptable:** Langage Pascal pour logique complexe
- **Génère exe signable:** (futur si budget certificat)
- **Léger:** Installeur < 100MB

**Alternatives considérées:**
- WiX Toolset: Trop complexe pour nos besoins
- NSIS: Moins moderne qu'Inno Setup
- InstallShield: Payant, trop lourd

**Trade-offs:**
- ✓ Gain: Simplicité, gratuité, stabilité
- ✗ Perte: Moins de fonctionnalités que solutions payantes
- **Justification:** Pour 2-3 utilisateurs, Inno Setup largement suffisant

---

### 2. Container Platform

**Choice:** Docker Desktop for Windows

**Rationale:**
- **Standard industrie:** Techniciens peuvent avoir déjà Docker installé
- **Cross-platform:** Facilite développement (Eric sur n'importe quel OS)
- **Isolation:** Garantit environnement reproductible
- **Ecosystem:** Large bibliothèque d'images, documentation riche

**Base Image:** Ubuntu 24.04 LTS

**Rationale:**
- **LTS:** Support long-terme, stabilité
- **Familiarité:** Eric connaît Ubuntu
- **Compatibilité:** Azure CLI officiellement supporté
- **Léger:** Plus léger que d'autres distributions

**Alternatives considérées:**
- Podman: Moins mature sur Windows
- VM (VirtualBox): Trop lourd, moins portable
- WSL2 direct: Nécessite configuration manuelle, moins isolé

**Trade-offs:**
- ✓ Gain: Isolation, reproductibilité, portabilité
- ✗ Perte: Nécessite Docker Desktop installé (2-3 GB)
- **Justification:** Isolation et reproductibilité valent la dépendance

---

### 3. AI Assistant

**Choice:** OpenCode connecté à Azure Foundry

**Rationale:**
- **Pas de compte Anthropic requis:** Modèle payé par la société via Azure
- **Intégration Azure:** Déjà dans l'écosystème Azure
- **Conversation naturelle:** Meilleur UX que scripts CLI
- **Guidage contextuel:** Peut adapter explications selon erreurs

**Model:** Claude (via Azure Foundry)

**Alternatives considérées:**
- Claude Code direct: Nécessite compte Anthropic individuel
- Scripts CLI purs: Moins intuitif, pas de guidage adaptatif
- ChatGPT: Nécessite compte externe

**Trade-offs:**
- ✓ Gain: UX conversationnel, guidage adaptatif, pas de compte individuel
- ✗ Perte: Dépendance sur Azure Foundry (voir open question Q3)
- **Justification:** UX conversationnel vaut la dépendance

---

### 4. Azure Automation

**Choice:** Azure CLI (version 2.x latest)

**Rationale:**
- **Officiel Microsoft:** Support complet de toutes les APIs Azure
- **Cross-platform:** Fonctionne dans container Linux
- **Scriptable:** Facile à wrapper en Python
- **Active development:** Mises à jour fréquentes

**Python Wrapper:** Custom (voir Component 6)

**Alternatives considérées:**
- Azure SDK for Python: Plus verbose, courbe d'apprentissage
- Terraform: Overkill pour déploiements simples
- PowerShell Az module: Nécessiterait Windows container

**Trade-offs:**
- ✓ Gain: Officiel, complet, bien documenté
- ✗ Perte: Mises à jour fréquentes nécessitent maintenance
- **Justification:** Support officiel + scriptabilité > maintenance

---

### 5. Documentation Server

**Choice:** Flask (Python)

**Rationale:**
- **Léger:** Microframework, pas de overhead
- **Simple:** Serve HTML/Markdown en quelques lignes
- **Même stack:** Déjà Python dans container
- **Aucune DB requise:** Documentation statique

**Template Engine:** Jinja2 (intégré Flask)

**Alternatives considérées:**
- FastAPI: Trop moderne/complexe pour simple doc server
- HTTP server Python natif: Moins de fonctionnalités
- Nginx: Overkill, nécessite configuration complexe

**Trade-offs:**
- ✓ Gain: Simplicité, même langage que wrapper Azure CLI
- ✗ Perte: Moins performant que Nginx (non pertinent pour 1 user)
- **Justification:** Simplicité > performance (1 utilisateur à la fois)

---

### 6. Scripting & Automation

**Choice:** PowerShell (Windows host) + Bash (container) + Python (container)

**Rationale:**
- **PowerShell:** Nécessaire pour exclusions Defender ASR sur Windows
- **Bash:** Scripts d'orchestration dans container Linux
- **Python:** Wrapper Azure CLI, Flask, logique métier

**Python Version:** 3.11

**Rationale:**
- Moderne mais stable (pas bleeding edge 3.12)
- Support long-terme
- Compatibilité Azure CLI

**Alternatives considérées:**
- Tout en Bash: Moins lisible pour logique complexe
- Node.js: Moins familier pour Eric
- Go: Compilation nécessaire, overkill

**Trade-offs:**
- ✓ Gain: Chaque langage pour son usage optimal
- ✗ Perte: 3 langages à maintenir
- **Justification:** Chaque langage nécessaire pour sa couche

---

### 7. Source Control & Repository

**Choice:** Git + GitHub

**Rationale:**
- **Standard industrie:** Eric connaît Git
- **Repo trad-bot-src:** Déjà sur GitHub
- **Clone facile:** `git clone` dans container

**Repository Structure:**
```
deploy-trad-bot-container/  (ce repo - infrastructure)
  ├── installer/            (Inno Setup scripts)
  ├── container/            (Dockerfile, scripts)
  ├── docs/                 (Product Brief, PRD, Architecture)
  └── README.md

trad-bot-src/               (repo séparé - code bot)
  ├── src/                  (Azure Functions Python)
  ├── docs/                 (Power Platform docs)
  └── README.md
```

---

## System Components

### Component 1: Windows Installer Package

**Purpose:** Distribuer et installer l'environnement Aux Petits Oignons sur le poste du technicien.

**Technology:** Inno Setup 6.x

**Responsibilities:**
- Créer arborescence fichiers (C:\AuxPetitsOignons\)
- Copier start.bat, docker-compose.yml, scripts PowerShell
- Afficher instructions pour script PowerShell ASR
- Créer raccourci bureau
- Optionnel: Vérifier prérequis (Docker Desktop installé)

**Interfaces:**
- Input: User execute .exe
- Output: Fichiers installés + message succès

**Dependencies:**
- Windows 10/11 (NFR-008)
- Droits utilisateur normaux (pas admin pour installation)

**FRs Addressed:** FR-001

**Architecture Files:**
```
installer/
  ├── setup.iss           (Inno Setup script)
  ├── files/
  │   ├── start.bat
  │   ├── docker-compose.yml
  │   ├── scripts/
  │   │   └── add-asr-exclusion.ps1
  │   └── README.txt
  └── output/
      └── AuxPetitsOignons_Setup.exe
```

**Build Process:**
1. Compile Inno Setup script: `iscc setup.iss`
2. Génère exe dans `installer/output/`
3. Distribuer exe aux techniciens

---

### Component 2: PowerShell Security Manager

**Purpose:** Créer exclusions Defender ASR pour permettre exécution de l'exe non-signé.

**Technology:** PowerShell 5.1+

**Responsibilities:**
- Ajouter exclusion ASR ciblée sur chemin exe
- Vérifier succès de l'exclusion
- Fournir feedback clair au technicien

**Interfaces:**
- Input: Exécution manuelle par technicien (mode admin)
- Output: Exclusion créée + message confirmation

**Dependencies:**
- Windows Defender activé
- Droits administrateur

**FRs Addressed:** FR-002

**Script Structure:**
```powershell
# add-asr-exclusion.ps1

# Vérifier droits admin
if (-NOT ([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole] "Administrator"))
{
    Write-Error "Ce script nécessite des droits administrateur."
    exit 1
}

# Ajouter exclusion ASR ciblée
$exePath = "C:\AuxPetitsOignons\AuxPetitsOignons.exe"
Add-MpPreference -AttackSurfaceReductionOnlyExclusions $exePath

# Vérifier
$exclusions = Get-MpPreference | Select-Object -ExpandProperty AttackSurfaceReductionOnlyExclusions
if ($exclusions -contains $exePath) {
    Write-Host "✓ Exclusion ASR ajoutée avec succès pour: $exePath" -ForegroundColor Green
} else {
    Write-Error "✗ Échec de l'ajout de l'exclusion ASR"
    exit 1
}
```

**NFRs Addressed:** NFR-004 (exclusions ciblées)

---

### Component 3: Docker Container

**Purpose:** Fournir environnement isolé et reproductible pour OpenCode, Flask, et Azure CLI.

**Technology:** Docker (Ubuntu 24.04 base image)

**Responsibilities:**
- Héberger OpenCode, Flask, Azure CLI
- Isoler environnement des dépendances système
- Garantir reproductibilité
- Démarrage automatique via start.bat

**Interfaces:**
- Input: docker-compose up via start.bat
- Output: Container running avec OpenCode ready + Flask ready

**Dependencies:**
- Docker Desktop installé et démarré

**FRs Addressed:** FR-003, FR-004, FR-005

**Dockerfile Structure:**
```dockerfile
FROM ubuntu:24.04

# Metadata
LABEL maintainer="eric@company.com"
LABEL version="1.0"

# Install base dependencies
RUN apt-get update && apt-get install -y \
    python3.11 \
    python3-pip \
    git \
    curl \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Install Azure CLI
RUN curl -sL https://aka.ms/InstallAzureCLIDeb | bash

# Install OpenCode
RUN pip3 install opencode

# Install Flask
RUN pip3 install flask markdown

# Copy application files
COPY app/ /app/
WORKDIR /app

# Configure OpenCode with Azure Foundry
ENV OPENCODE_API_KEY=${AZURE_FOUNDRY_KEY}
ENV OPENCODE_ENDPOINT=${AZURE_FOUNDRY_ENDPOINT}

# Expose Flask port
EXPOSE 5545

# Startup script
CMD ["/app/start.sh"]
```

**docker-compose.yml:**
```yaml
version: '3.8'

services:
  trad-bot-opencode:
    build: ./container
    container_name: trad-bot-opencode
    ports:
      - "5545:5545"
    environment:
      - AZURE_FOUNDRY_KEY=${AZURE_FOUNDRY_KEY}
      - AZURE_FOUNDRY_ENDPOINT=${AZURE_FOUNDRY_ENDPOINT}
    volumes:
      - ./data:/app/data  # Pour rapport intervention uniquement
    stdin_open: true
    tty: true
```

**start.sh (Container entrypoint):**
```bash
#!/bin/bash

# Start Flask documentation server (background)
python3 /app/flask_server.py &

# Clone trad-bot-src repo
cd /app
git clone https://github.com/company/trad-bot-src.git || echo "Repo already cloned"

# Open browser on host (via script)
# Note: Exécuté par start.bat sur host, pas dans container

# Start OpenCode interactive session
opencode
```

**NFRs Addressed:**
- NFR-001 (démarrage < 2 min via optimisation image)
- NFR-008 (environnement Windows avec Docker Desktop)

---

### Component 4: OpenCode Service (AI Assistant)

**Purpose:** Guider le technicien via conversation pour déployer services Azure.

**Technology:** OpenCode connecté à Azure Foundry (Claude model)

**Responsibilities:**
- Conversation en français avec technicien
- Orchestrer déploiement Azure (via Component 6)
- Fournir explications contextuelles
- Afficher credentials sans les stocker
- Générer rapport intervention

**Interfaces:**
- Input: Terminal interactif (technicien tape commandes)
- Output: Messages conversationnels + appels Azure CLI

**Dependencies:**
- Azure Foundry accessible (internet)
- Component 6 (Azure CLI wrapper)

**FRs Addressed:** FR-013

**Configuration:**
```python
# opencode_config.py

import os

OPENCODE_CONFIG = {
    "api_key": os.getenv("AZURE_FOUNDRY_KEY"),
    "endpoint": os.getenv("AZURE_FOUNDRY_ENDPOINT"),
    "model": "claude-3-5-sonnet",  # Via Azure Foundry
    "language": "fr",
    "system_prompt": """
Tu es un assistant de déploiement Azure spécialisé dans le Bot Traducteur.
Ton rôle est de guider un technicien Modern Workplace (expert Power Platform,
non-expert Azure) à travers le déploiement des services Azure nécessaires.

Règles critiques:
1. Communique TOUJOURS en français clair
2. Explique les termes techniques Azure
3. Confirme avant toute action critique
4. Pour Azure Translator, utilise TOUJOURS le SKU F0 (gratuit)
5. NE STOCKE JAMAIS les credentials - affiche-les seulement
6. Fournis feedback positif à chaque étape réussie

Services à déployer:
- Azure Storage Account (Standard LRS)
- Azure Translator (SKU F0 obligatoire)
- Azure Functions (runtime Python 3.11)
"""
}
```

**Conversation Flow Example:**
```
OpenCode: Bonjour! Je vais vous guider pour déployer le Bot Traducteur chez votre client.
          Commençons par vous connecter à Azure. Tapez: az login --tenant <tenant-id>

User: az login --tenant <tenant-id>
[Browser opens for authentication]

OpenCode: Parfait! Vous êtes connecté. Maintenant, créons le groupe de ressources.
          Dans quelle région souhaitez-vous déployer? (Recommandé: francecentral)

User: francecentral

OpenCode: Excellent choix. Je vais créer le groupe de ressources "rg-bot-traducteur-[client]".
          [Exécute: az group create...]
          ✓ Groupe de ressources créé!

          Passons au Storage Account...
```

**NFRs Addressed:**
- NFR-006 (interface conversationnelle simple)
- NFR-010 (messages d'erreur clairs)

---

### Component 5: Flask Documentation Server

**Purpose:** Servir la documentation Power Platform sur localhost:5545.

**Technology:** Flask 3.x + Markdown rendering

**Responsibilities:**
- Charger documentation depuis trad-bot-src/docs/
- Convertir Markdown → HTML
- Servir sur port 5545
- Fournir navigation simple

**Interfaces:**
- Input: HTTP GET http://localhost:5545/procedure
- Output: HTML documentation

**Dependencies:**
- Component 3 (container)
- Repo trad-bot-src cloné

**FRs Addressed:** FR-011

**Flask App Structure:**
```python
# flask_server.py

from flask import Flask, render_template_string
import markdown
import os

app = Flask(__name__)

# Load documentation
DOCS_PATH = "/app/trad-bot-src/docs/GUIDE_POWER_PLATFORM_COMPLET.md"

@app.route("/")
@app.route("/procedure")
def procedure():
    """Serve Power Platform deployment procedure."""
    if not os.path.exists(DOCS_PATH):
        return "<h1>Erreur: Documentation non trouvée</h1>", 404

    with open(DOCS_PATH, 'r', encoding='utf-8') as f:
        md_content = f.read()

    html_content = markdown.markdown(
        md_content,
        extensions=['tables', 'fenced_code', 'toc']
    )

    template = """
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <title>Procédure Power Platform - Bot Traducteur</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                max-width: 900px;
                margin: 40px auto;
                padding: 20px;
                line-height: 1.6;
            }
            code {
                background: #f4f4f4;
                padding: 2px 6px;
                border-radius: 3px;
            }
            pre {
                background: #f4f4f4;
                padding: 15px;
                border-radius: 5px;
                overflow-x: auto;
            }
            h1, h2, h3 {
                color: #0078d4;
            }
        </style>
    </head>
    <body>
        {{ content | safe }}
    </body>
    </html>
    """

    return render_template_string(template, content=html_content)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5545, debug=False)
```

**NFRs Addressed:**
- NFR-001 (Flask ready < 30s)
- NFR-009 (compatible Chrome/Edge/Firefox)

---

### Component 6: Azure CLI Automation Layer

**Purpose:** Wrapper Python autour d'Azure CLI pour déploiements automatisés avec gestion d'erreurs.

**Technology:** Python 3.11 + subprocess + Azure CLI

**Responsibilities:**
- Exécuter commandes Azure CLI
- Capturer et interpréter erreurs
- Retry automatique pour erreurs temporaires
- Fournir credentials sans les stocker
- Générer rapport intervention

**Interfaces:**
- Input: Appels depuis OpenCode (ex: deploy_storage_account())
- Output: Résultats structurés (JSON) ou erreurs claires

**Dependencies:**
- Azure CLI installé dans container
- User authentifié (az login --tenant <tenant-id>)

**FRs Addressed:** FR-006, FR-007, FR-008, FR-009, FR-014

**Python Wrapper Structure:**
```python
# azure_deployer.py

import subprocess
import json
import time
from typing import Dict, Optional, Tuple

class AzureDeploymentError(Exception):
    """Custom exception pour erreurs Azure."""
    pass

class AzureDeployer:
    """Wrapper autour d'Azure CLI pour déploiements Bot Traducteur."""

    def __init__(self):
        self.deployment_report = {
            "timestamp": None,
            "resource_group": None,
            "resources": []
        }

    def _run_az_command(
        self,
        command: str,
        retry_count: int = 3,
        retry_delay: int = 5
    ) -> Tuple[bool, str]:
        """
        Exécute une commande Azure CLI avec retry.

        Returns:
            (success: bool, output: str)
        """
        for attempt in range(retry_count):
            try:
                result = subprocess.run(
                    command,
                    shell=True,
                    capture_output=True,
                    text=True,
                    timeout=300  # 5 min max
                )

                if result.returncode == 0:
                    return (True, result.stdout)
                else:
                    # Interpréter erreur
                    error_msg = self._interpret_error(result.stderr)

                    # Retry si erreur temporaire
                    if self._is_temporary_error(result.stderr) and attempt < retry_count - 1:
                        time.sleep(retry_delay)
                        continue
                    else:
                        return (False, error_msg)

            except subprocess.TimeoutExpired:
                if attempt < retry_count - 1:
                    time.sleep(retry_delay)
                    continue
                else:
                    return (False, "Timeout: La commande Azure CLI a pris trop de temps (>5 min)")
            except Exception as e:
                return (False, f"Erreur inattendue: {str(e)}")

        return (False, "Échec après plusieurs tentatives")

    def _interpret_error(self, stderr: str) -> str:
        """
        Convertit erreurs Azure CLI en messages français clairs.
        """
        # Mapping erreurs communes
        error_mappings = {
            "AuthorizationFailed": "Problème: Permissions insuffisantes.\nSolution: Vérifiez que votre compte a les droits 'Contributor' sur la subscription.",
            "ResourceGroupNotFound": "Problème: Groupe de ressources introuvable.\nSolution: Créez d'abord le groupe de ressources.",
            "SubscriptionNotFound": "Problème: Subscription Azure introuvable.\nSolution: Vérifiez que vous êtes connecté au bon tenant Azure.",
            "InvalidAuthenticationToken": "Problème: Token d'authentification invalide ou expiré.\nSolution: Reconnectez-vous avec 'az login --tenant <tenant-id>'.",
            "LocationNotAvailableForResourceType": "Problème: La région choisie ne supporte pas ce service.\nSolution: Essayez une autre région (ex: francecentral, westeurope).",
        }

        for error_key, user_message in error_mappings.items():
            if error_key in stderr:
                return user_message

        # Erreur non mappée - retourner message brut mais formaté
        return f"Erreur Azure CLI:\n{stderr}\n\nContactez Eric si vous ne comprenez pas cette erreur."

    def _is_temporary_error(self, stderr: str) -> bool:
        """Détecte si une erreur est temporaire (retry possible)."""
        temporary_errors = [
            "Timeout",
            "ConnectionError",
            "ServiceUnavailable",
            "TooManyRequests"
        ]
        return any(err in stderr for err in temporary_errors)

    def create_resource_group(
        self,
        name: str,
        location: str = "francecentral"
    ) -> Dict:
        """
        Crée un groupe de ressources Azure.

        Args:
            name: Nom du resource group (ex: rg-bot-traducteur-client1)
            location: Région Azure

        Returns:
            Dict avec infos du resource group

        Raises:
            AzureDeploymentError si échec
        """
        command = f"az group create --name {name} --location {location} --output json"
        success, output = self._run_az_command(command)

        if not success:
            raise AzureDeploymentError(output)

        rg_info = json.loads(output)
        self.deployment_report["resource_group"] = name
        return rg_info

    def create_storage_account(
        self,
        resource_group: str,
        name: str,
        location: str = "francecentral"
    ) -> Dict:
        """
        Crée un Azure Storage Account.

        Returns:
            Dict avec name, keys, connection_string
        """
        # Créer storage account
        create_cmd = f"""
        az storage account create \
          --name {name} \
          --resource-group {resource_group} \
          --location {location} \
          --sku Standard_LRS \
          --kind StorageV2 \
          --output json
        """

        success, output = self._run_az_command(create_cmd)
        if not success:
            raise AzureDeploymentError(output)

        # Récupérer les clés
        keys_cmd = f"az storage account keys list --account-name {name} --resource-group {resource_group} --output json"
        success, keys_output = self._run_az_command(keys_cmd)
        if not success:
            raise AzureDeploymentError(keys_output)

        keys = json.loads(keys_output)
        primary_key = keys[0]["value"]

        # Créer container blob
        container_cmd = f"""
        az storage container create \
          --name translations \
          --account-name {name} \
          --account-key {primary_key} \
          --output json
        """
        self._run_az_command(container_cmd)

        result = {
            "name": name,
            "key": primary_key,
            "connection_string": f"DefaultEndpointsProtocol=https;AccountName={name};AccountKey={primary_key};EndpointSuffix=core.windows.net"
        }

        self.deployment_report["resources"].append({
            "type": "Storage Account",
            "name": name
        })

        return result

    def create_translator(
        self,
        resource_group: str,
        name: str,
        location: str = "francecentral"
    ) -> Dict:
        """
        Crée Azure Translator avec SKU F0 (OBLIGATOIRE).

        Returns:
            Dict avec endpoint, key, region
        """
        # SKU F0 forcé - aucune possibilité de sélectionner S0
        create_cmd = f"""
        az cognitiveservices account create \
          --name {name} \
          --resource-group {resource_group} \
          --kind TextTranslation \
          --sku F0 \
          --location {location} \
          --yes \
          --output json
        """

        success, output = self._run_az_command(create_cmd)
        if not success:
            raise AzureDeploymentError(output)

        # Récupérer clés
        keys_cmd = f"az cognitiveservices account keys list --name {name} --resource-group {resource_group} --output json"
        success, keys_output = self._run_az_command(keys_cmd)
        if not success:
            raise AzureDeploymentError(keys_output)

        keys = json.loads(keys_output)

        result = {
            "endpoint": f"https://api.cognitive.microsofttranslator.com/",
            "key": keys["key1"],
            "region": location
        }

        self.deployment_report["resources"].append({
            "type": "Translator (SKU F0)",
            "name": name
        })

        return result

    def deploy_function_app(
        self,
        resource_group: str,
        name: str,
        storage_connection_string: str,
        translator_key: str,
        translator_endpoint: str,
        translator_region: str,
        location: str = "francecentral"
    ) -> Dict:
        """
        Déploie Azure Functions pour le Bot Traducteur.

        Returns:
            Dict avec function_url
        """
        # Créer App Service Plan
        plan_cmd = f"""
        az functionapp plan create \
          --name {name}-plan \
          --resource-group {resource_group} \
          --location {location} \
          --sku Y1 \
          --is-linux \
          --output json
        """
        self._run_az_command(plan_cmd)

        # Créer Function App
        create_cmd = f"""
        az functionapp create \
          --name {name} \
          --resource-group {resource_group} \
          --plan {name}-plan \
          --runtime python \
          --runtime-version 3.11 \
          --storage-account {storage_connection_string.split(';')[1].split('=')[1]} \
          --functions-version 4 \
          --output json
        """
        success, output = self._run_az_command(create_cmd)
        if not success:
            raise AzureDeploymentError(output)

        # Configurer App Settings
        settings_cmd = f"""
        az functionapp config appsettings set \
          --name {name} \
          --resource-group {resource_group} \
          --settings \
            AZURE_ACCOUNT_NAME={storage_connection_string.split(';')[1].split('=')[1]} \
            TRANSLATOR_KEY={translator_key} \
            TRANSLATOR_ENDPOINT={translator_endpoint} \
            TRANSLATOR_REGION={translator_region} \
          --output json
        """
        self._run_az_command(settings_cmd)

        # Déployer code depuis trad-bot-src
        deploy_cmd = f"cd /app/trad-bot-src/src && func azure functionapp publish {name}"
        success, deploy_output = self._run_az_command(deploy_cmd)
        if not success:
            raise AzureDeploymentError(deploy_output)

        result = {
            "function_url": f"https://{name}.azurewebsites.net"
        }

        self.deployment_report["resources"].append({
            "type": "Function App (Python 3.11)",
            "name": name,
            "url": result["function_url"]
        })

        return result

    def generate_intervention_report(self) -> str:
        """
        Génère un rapport d'intervention formaté pour ticketing.
        """
        import datetime

        report = f"""
╔══════════════════════════════════════════════════════════════╗
║        RAPPORT D'INTERVENTION - BOT TRADUCTEUR              ║
╚══════════════════════════════════════════════════════════════╝

Date: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Groupe de ressources: {self.deployment_report['resource_group']}

Services déployés:
"""

        for resource in self.deployment_report["resources"]:
            report += f"\n  ✓ {resource['type']}: {resource['name']}"
            if 'url' in resource:
                report += f"\n    URL: {resource['url']}"

        report += f"""

Prochaines étapes:
  1. Configurer les connexions dans Power Platform
  2. Importer la solution Copilot Studio
  3. Tester le bot

Déployé avec: Aux Petits Oignons v1.0
"""

        return report
```

**NFRs Addressed:**
- NFR-002 (déploiement < 15min via optimisations)
- NFR-003 (aucun stockage credentials - affichage seulement)
- NFR-005 (gestion erreurs avec messages clairs)

---

## Data Architecture

### Data Model

**Entities:**

Le système "Aux Petits Oignons" ne gère **aucune donnée persistante** en base de données. Toutes les données sont éphémères (session container) ou générées temporairement (rapport intervention).

**Données transitoires:**

1. **Session Azure CLI**
   - Type: Credentials temporaires
   - Stockage: Mémoire container uniquement
   - Durée de vie: Session container
   - Sécurité: NFR-003 - jamais persisté sur disque

2. **Credentials affichés**
   - Type: Clés Azure (Storage, Translator, Functions)
   - Stockage: Affichage terminal uniquement
   - Durée de vie: Affichage puis oubli
   - Sécurité: NFR-003 - technicien les copie manuellement

3. **Rapport d'intervention**
   - Type: Texte formaté
   - Stockage: Fichier temporaire dans volume Docker (/app/data/)
   - Durée de vie: Session container
   - Contenu: Groupe de ressources, liste services déployés, URLs (PAS de credentials)

**Data Flow Diagram:**

```
[Technicien]
    ↓ az login --tenant <tenant-id>
[Azure CLI in Container]
    ↓ Token temporaire (mémoire)
[Azure API]
    ↓ Credentials (Storage key, Translator key, etc.)
[Azure CLI Wrapper]
    ↓ Affichage terminal
[Technicien] → Copie manuellement dans Power Platform
    ↓
[Rapport généré] → Fichier temporaire
    ↓ Technicien copie dans ticket
[Fin de session] → Container arrêté → Toutes données effacées
```

**No Database Required:** Aucune base de données n'est nécessaire pour ce projet.

---

## API Design

### API Architecture

**Pattern:** Aucune API REST exposée par "Aux Petits Oignons" lui-même.

**Rationale:**
- Application locale (1 utilisateur à la fois sur son poste)
- Interface = Terminal OpenCode + Browser (Flask docs)
- Pas d'API multi-utilisateurs nécessaire

**APIs consommées:**

1. **Azure APIs (via Azure CLI)**
   - Resource Management API
   - Storage API
   - Cognitive Services API (Translator)
   - Functions API

2. **Azure Foundry API (OpenCode)**
   - API Claude via Azure endpoint
   - Authentification: API key

---

## NFR Coverage (Systematic)

### NFR-001: Performance - Temps de démarrage

**Requirement:** Container démarré et opérationnel en < 2 minutes

**Architecture Solution:**
- **Image Docker optimisée:**
  - Layers cachés (dépendances pré-installées)
  - Pas de compilation à la volée
  - Image taille < 1GB
- **Flask en mode production:** Pas de reload automatique
- **Démarrage parallèle:** Flask & OpenCode démarrent ensemble (start.sh)

**Implementation Notes:**
```dockerfile
# Optimisations Dockerfile
RUN apt-get update && apt-get install -y ... && rm -rf /var/lib/apt/lists/*  # Nettoyer cache
RUN pip3 install --no-cache-dir flask opencode  # Pas de cache pip
```

**Validation:**
- Mesurer temps: `time docker-compose up` jusqu'à "OpenCode ready"
- Target: < 120 secondes
- Test sur machine standard: 8GB RAM, SSD

---

### NFR-002: Performance - Temps de déploiement Azure

**Requirement:** Déploiement complet (Storage + Translator + Functions) en < 15 minutes

**Architecture Solution:**
- **Parallélisation quand possible:**
  - Storage Account et Translator peuvent être créés en parallèle (pas de dépendance)
- **Azure CLI optimisé:**
  - Mode `--no-wait` pour opérations longues non-bloquantes
  - Polling status au lieu d'attente synchrone
- **Région proche:** Recommandation `francecentral` (latence faible depuis France)

**Implementation Notes:**
```python
# Parallélisation avec threading
import concurrent.futures

def deploy_in_parallel():
    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
        storage_future = executor.submit(create_storage_account, ...)
        translator_future = executor.submit(create_translator, ...)

        storage_result = storage_future.result()
        translator_result = translator_future.result()
```

**Validation:**
- Chronomètre déploiement complet
- Target: 90% des déploiements < 15 min
- Mesure séparée: Storage (~3 min), Translator (~2 min), Functions (~8 min)

---

### NFR-003: Security - Aucun stockage de credentials

**Requirement:** JAMAIS stocker credentials de manière persistante

**Architecture Solution:**
- **Container éphémère:** Aucun volume Docker pour credentials
- **Session Azure CLI temporaire:** Token dans mémoire container uniquement
- **Affichage terminal:** Credentials affichés une fois puis oubliés
- **Logs filtrés:** Aucune clé dans les logs

**Implementation Notes:**
```python
# Filtre logs
import re

def sanitize_log(log_message: str) -> str:
    """Supprime credentials des logs."""
    # Patterns à supprimer
    patterns = [
        r'AccountKey=[^;]+',  # Storage account key
        r'"key[0-9]*":\s*"[^"]+"',  # JSON keys
        r'Ocp-Apim-Subscription-Key:\s*\S+',  # Translator key
    ]

    sanitized = log_message
    for pattern in patterns:
        sanitized = re.sub(pattern, '[REDACTED]', sanitized)

    return sanitized
```

**Validation:**
- **Scan de sécurité:**
  - Aucun fichier .env, .credentials, config.json
  - Aucun volume Docker persistant
- **Code review:** Vérifier aucun `with open(..., 'w')` pour credentials
- **Test:** Arrêter container → redémarrer → vérifier aucun credential présent

**Trade-off:** Technicien doit copier manuellement credentials → mais sécurité > convénience

---

### NFR-004: Security - Exclusions Defender ciblées

**Requirement:** Exclusions ASR strictement ciblées sur l'exe, pas d'exclusions globales

**Architecture Solution:**
- **Script PowerShell avec chemin absolu:**
  ```powershell
  $exePath = "C:\AuxPetitsOignons\AuxPetitsOignons.exe"
  Add-MpPreference -AttackSurfaceReductionOnlyExclusions $exePath
  ```
- **Pas d'exclusion de dossiers:** Uniquement fichier exe
- **Documentation justificatif:** README explique pourquoi nécessaire (pas de certificat)

**Implementation Notes:**
- Vérification dans script que chemin existe avant ajout exclusion
- Feedback clair au technicien sur ce qui a été exclu

**Validation:**
- Vérifier `Get-MpPreference | Select AttackSurfaceReductionOnlyExclusions`
- Confirmer: 1 seule entrée = chemin exe
- Pas d'exclusion C:\, Program Files, etc.

---

### NFR-005: Reliability - Gestion d'erreurs Azure CLI

**Requirement:** Détection et gestion gracieuse des erreurs Azure CLI

**Architecture Solution:**
- **Wrapper Python** (Component 6) avec:
  - Capture subprocess stderr
  - Mapping erreurs → messages français clairs
  - Retry automatique pour erreurs temporaires
  - Suggestions d'actions correctives

**Implementation Notes:**
Voir Component 6 (`_interpret_error()` et `_is_temporary_error()`)

**Validation:**
- **Tests d'erreurs simulés:**
  - Permissions insuffisantes → Message clair + solution
  - Timeout réseau → Retry automatique
  - Subscription introuvable → Message + vérification compte
- **Aucun stack trace Python visible** au technicien

---

### NFR-006: Usability - Interface conversationnelle simple

**Requirement:** OpenCode communique en français simple, sans jargon excessif

**Architecture Solution:**
- **System prompt OpenCode** en français avec:
  - Explications contextuelles des termes Azure
  - Confirmations avant actions critiques
  - Feedback positif à chaque succès
- **Glossaire intégré:**
  ```python
  GLOSSARY = {
      "Resource Group": "Groupe de ressources - un conteneur logique pour vos services Azure",
      "SKU": "Niveau de tarification du service (F0 = gratuit, S0 = payant)",
      "Storage Account": "Espace de stockage cloud pour vos fichiers",
  }
  ```

**Implementation Notes:**
Voir Component 4 (opencode_config.py - system_prompt)

**Validation:**
- **Tests utilisateurs:** Les 2 techniciens comprennent-ils les messages?
- **Feedback:** Aucune question "c'est quoi [terme]?"
- **Satisfaction:** Techniciens préfèrent OpenCode vs doc écrite

---

### NFR-007: Maintainability - Mises à jour Azure CLI

**Requirement:** Processus de mise à jour Azure CLI régulier

**Architecture Solution:**
- **Dockerfile avec version explicite:**
  ```dockerfile
  ARG AZURE_CLI_VERSION=2.56.0
  RUN curl -sL https://aka.ms/InstallAzureCLIDeb | bash
  ```
- **Tags Docker versionnés:** `trad-bot-opencode:v1.0`, `v1.1`, etc.
- **Script de test post-update:**
  ```bash
  #!/bin/bash
  # test-azure-cli.sh
  az --version
  az group list --output table  # Test command
  ```
- **Processus documenté:**
  1. Mettre à jour Dockerfile
  2. Rebuild image: `docker build -t trad-bot-opencode:v1.1 .`
  3. Tester: `./test-azure-cli.sh`
  4. Si OK → Tag latest: `docker tag trad-bot-opencode:v1.1 trad-bot-opencode:latest`
  5. Si KO → Rollback: `docker tag trad-bot-opencode:v1.0 trad-bot-opencode:latest`

**Implementation Notes:**
- Créer `docs/maintenance/azure-cli-update.md` avec procédure complète

**Validation:**
- Simuler mise à jour Azure CLI 2.56 → 2.57
- Vérifier aucune breaking change
- Tester déploiement complet avec nouvelle version

**Answer to Open Question Q1:** Processus défini ci-dessus

---

### NFR-008: Compatibility - Environnement Windows

**Requirement:** Fonctionnel sur Windows 10 (21H2+) et Windows 11

**Architecture Solution:**
- **Prérequis vérifiés:**
  - start.bat vérifie version Windows
  - Vérifie Docker Desktop installé
  - Message clair si manquant
- **Compatibilité testée:**
  - Windows 10 21H2
  - Windows 11 22H2

**Implementation Notes:**
```batch
@echo off
REM start.bat

REM Vérifier Windows version
ver | findstr /i "10.0.19" >nul
if %errorlevel%==0 (
    echo Windows 10 detecte
) else (
    ver | findstr /i "10.0.22" >nul
    if %errorlevel%==0 (
        echo Windows 11 detecte
    ) else (
        echo ERREUR: Windows 10 (21H2+) ou Windows 11 requis
        pause
        exit /b 1
    )
)

REM Vérifier Docker Desktop
docker --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERREUR: Docker Desktop n'est pas installe ou pas demarre
    echo Veuillez installer Docker Desktop: https://www.docker.com/products/docker-desktop
    pause
    exit /b 1
)

REM Démarrer container
docker-compose up -d

REM Ouvrir browser
start http://localhost:5545

REM Ouvrir terminal OpenCode
docker exec -it trad-bot-opencode opencode
```

**Validation:**
- Tester sur VM Windows 10 21H2
- Tester sur VM Windows 11
- Vérifier messages d'erreur si prérequis manquants

**Answer to Open Question Q2:** Vérification dans start.bat avec message clair

---

### NFR-009: Compatibility - Navigateurs modernes

**Requirement:** Documentation Flask accessible sur Chrome, Edge, Firefox

**Architecture Solution:**
- **HTML/CSS standard:** Pas de fonctionnalités bleeding-edge
- **Pas de JavaScript complexe:** HTML statique + CSS simple
- **Rendu testé:** Chrome 120+, Edge 120+, Firefox 120+

**Implementation Notes:**
Voir Component 5 (flask_server.py - template HTML simple)

**Validation:**
- Ouvrir localhost:5545 sur Chrome, Edge, Firefox
- Vérifier rendu identique
- Vérifier navigation fonctionnelle

---

### NFR-010: Usability - Messages d'erreur clairs

**Requirement:** Messages d'erreur compréhensibles + action corrective

**Architecture Solution:**
- **Format standardisé:**
  ```
  Problème: [Description simple]
  Solution: [Action concrète à faire]
  ```
- **Pas de stack traces** visibles (loggés pour debug Eric uniquement)
- **Numéro d'erreur** pour référence si support nécessaire

**Implementation Notes:**
Voir Component 6 (`_interpret_error()`)

**Validation:**
- Simuler erreurs communes (permissions, MFA, timeout)
- Vérifier messages clairs + actions correctives
- Techniciens peuvent résoudre sans contacter Eric

---

## Security Architecture

### Authentication

**Azure CLI Authentication:**
- **Method:** `az login --tenant <tenant-id>` (OAuth 2.0 device flow ou browser)
- **Token lifetime:** Géré par Azure CLI (typiquement 1h, refresh automatique)
- **Multi-factor authentication:** Supporté (voir Open Question Q3 - gestion MFA)

**No application-level auth:** Application locale, pas d'authentification propre nécessaire.

---

### Authorization

**Azure RBAC:**
- **Technicien doit avoir:** Rôle "Contributor" ou "Owner" sur la subscription Azure client
- **Vérification:** Azure CLI retourne erreur si permissions insuffisantes
- **Message clair:** Wrapper Python interprète erreur (NFR-005)

**No application-level authz:** Toutes opérations via identité Azure du technicien.

---

### Data Encryption

**At Rest:**
- **Aucune donnée persistée** dans "Aux Petits Oignons" (NFR-003)
- Azure services (Storage, Translator, Functions) utilisent encryption at rest par défaut (Azure-managed keys)

**In Transit:**
- **HTTPS uniquement:** Toutes communications Azure via HTTPS (TLS 1.2+)
- **Azure CLI:** Utilise HTTPS pour toutes les API calls
- **OpenCode ↔ Azure Foundry:** HTTPS

**Key Management:**
- **Aucune gestion de clés** dans "Aux Petits Oignons" (credentials affichés seulement)
- **Azure Foundry API key:** Stockée dans variable d'environnement container (non-persistante)

---

### Security Best Practices

**Input Validation:**
- **Noms de ressources:** Validation Regex (caractères alphanumériques + hyphens)
- **Commandes Azure CLI:** Wrapper Python sanitize inputs (pas d'injection de commandes)

**SQL Injection:** N/A (aucune base de données)

**XSS Prevention:**
- Flask avec Jinja2 auto-escape activé par défaut
- Documentation Markdown → HTML safe (bibliothèque markdown escape)

**CSRF Protection:** N/A (aucune API REST exposée)

**Rate Limiting:** N/A (application locale)

**Security Headers:** N/A (Flask local, pas exposé sur internet)

---

## Scalability & Performance

### Scaling Strategy

**Not Applicable:** Application locale, 1 utilisateur à la fois sur son poste.

**Extensibilité future (si autres bots):**
- **Architecture modulaire:** Repo séparé par bot (trad-bot-src, autre-bot-src)
- **Container générique:** Même container, clone repo différent selon bot
- **Aucun changement infrastructure:** Scaling = distribuer exe à plus de techniciens

---

### Performance Optimization

**Container:**
- **Image optimisée:** Layers cachés, pas de fichiers inutiles
- **Taille image:** Target < 1GB

**Azure CLI:**
- **Parallélisation:** Storage + Translator en parallèle (NFR-002)
- **Mode asynchrone:** `--no-wait` pour opérations longues

**Flask:**
- **Mode production:** `debug=False`, pas de reload
- **Documentation pré-compilée:** Markdown → HTML au démarrage (pas à chaque requête)

---

### Caching Strategy

**Minimal caching:**
- **Documentation Flask:** Fichiers Markdown lus une fois au démarrage Flask
- **Aucun cache Azure CLI:** Chaque déploiement est unique (client différent)

---

### Load Balancing

**Not Applicable:** Application locale, aucun load balancing nécessaire.

---

## Reliability & Availability

### High Availability

**Not Applicable:** Application locale.

**Fiabilité:**
- **Docker container:** Isolation garantit pas d'interférence avec système host
- **Retry logic:** Erreurs temporaires Azure CLI retentées automatiquement (NFR-005)

---

### Disaster Recovery

**Not Applicable:** Aucune donnée à récupérer (éphémère).

**Recovery scenario:**
- Si container crashe → `docker-compose up` relance
- Si exe corrompu → Réinstaller depuis exe original

---

### Backup Strategy

**Not Applicable:** Aucune donnée à sauvegarder.

**Code source:**
- Versionné sur Git (repos deploy-trad-bot-container + trad-bot-src)

---

### Monitoring & Alerting

**Local monitoring:**
- **Docker logs:** `docker logs trad-bot-opencode`
- **Azure CLI output:** Capturé par wrapper Python, loggé dans container

**No centralized monitoring:** Application locale, pas de Datadog/CloudWatch nécessaire.

**Alerting:**
- **Erreurs critiques:** Affichées au technicien via OpenCode
- **Support Eric:** Technicien contacte si bloqué (logs Docker disponibles)

---

### Fallback Strategy (Open Question Q3)

**Problem:** Que faire si Azure Foundry indisponible?

**Architecture Solution:**

**Option A: Mode dégradé avec instructions statiques** (Recommandé)
- Détecter indisponibilité Azure Foundry au démarrage
- Afficher message: "OpenCode indisponible, mode manuel activé"
- Servir fichier `instructions-manuelles.md` avec commandes Azure CLI exactes à exécuter
- Exemple:
  ```bash
  # Instructions manuelles - Bot Traducteur

  1. Créer Resource Group:
     az group create --name rg-bot-traducteur-[client] --location francecentral

  2. Créer Storage Account:
     az storage account create --name stbottraducteur[client] ...

  [etc.]
  ```

**Option B: Fallback vers API Anthropic directe**
- Nécessite compte Anthropic (non souhaité - voir Product Brief)
- Rejeté

**Implementation:**
```python
# container/app/start.sh

#!/bin/bash

# Test Azure Foundry connectivity
python3 -c "
import requests
import os
import sys

try:
    endpoint = os.getenv('AZURE_FOUNDRY_ENDPOINT')
    api_key = os.getenv('AZURE_FOUNDRY_KEY')

    response = requests.get(
        f'{endpoint}/health',
        headers={'Authorization': f'Bearer {api_key}'},
        timeout=10
    )

    if response.status_code != 200:
        sys.exit(1)
except:
    sys.exit(1)
"

if [ $? -ne 0 ]; then
    echo "╔════════════════════════════════════════════════════════╗"
    echo "║  ATTENTION: OpenCode indisponible                      ║"
    echo "║  Mode manuel activé - suivez les instructions ci-dessous ║"
    echo "╚════════════════════════════════════════════════════════╝"
    cat /app/instructions-manuelles.md
    exec bash  # Shell interactif pour commandes manuelles
else
    # Start Flask + OpenCode normalement
    python3 /app/flask_server.py &
    opencode
fi
```

**Validation:**
- Simuler indisponibilité (bloquer endpoint Azure Foundry)
- Vérifier fallback vers instructions manuelles
- Technicien peut toujours déployer (moins guidé mais possible)

**Answer to Open Question Q3:** Mode dégradé avec instructions statiques

---

## Development & Deployment

### Code Organization

**Repository Structure:**

```
deploy-trad-bot-container/
├── installer/
│   ├── setup.iss              # Inno Setup script
│   ├── files/
│   │   ├── start.bat
│   │   ├── docker-compose.yml
│   │   └── scripts/
│   │       └── add-asr-exclusion.ps1
│   └── output/
│       └── AuxPetitsOignons_Setup.exe
│
├── container/
│   ├── Dockerfile
│   ├── app/
│   │   ├── start.sh
│   │   ├── flask_server.py
│   │   ├── azure_deployer.py
│   │   ├── opencode_config.py
│   │   └── instructions-manuelles.md
│   └── requirements.txt
│
├── docs/
│   ├── product-brief-aux-petits-oignons-2026-01-18.md
│   ├── prd-aux-petits-oignons-2026-01-18.md
│   ├── architecture-aux-petits-oignons-2026-01-18.md
│   └── maintenance/
│       └── azure-cli-update.md
│
├── README.md
└── .gitignore
```

**Naming Conventions:**
- Files: snake_case (azure_deployer.py)
- Classes: PascalCase (AzureDeployer)
- Functions: snake_case (create_storage_account)
- Constants: UPPER_SNAKE_CASE (AZURE_FOUNDRY_KEY)

---

### Testing Strategy

**Unit Testing:**
- **Python code:** pytest
- **Coverage target:** 80%+ pour azure_deployer.py
- **Mock Azure CLI:** Utiliser `unittest.mock` pour subprocess

**Example:**
```python
# tests/test_azure_deployer.py

import pytest
from unittest.mock import patch, MagicMock
from container.app.azure_deployer import AzureDeployer

def test_create_storage_account_success():
    deployer = AzureDeployer()

    with patch.object(deployer, '_run_az_command') as mock_run:
        mock_run.return_value = (True, '{"name": "test-storage"}')

        result = deployer.create_storage_account(
            resource_group="rg-test",
            name="test-storage"
        )

        assert result["name"] == "test-storage"
        assert deployer.deployment_report["resources"][0]["type"] == "Storage Account"

def test_create_translator_enforces_f0_sku():
    deployer = AzureDeployer()

    # Vérifier que la commande contient --sku F0
    with patch('subprocess.run') as mock_run:
        mock_run.return_value = MagicMock(returncode=0, stdout='{}')

        deployer.create_translator(
            resource_group="rg-test",
            name="translator-test"
        )

        # Vérifier commande Azure CLI
        call_args = mock_run.call_args[0][0]
        assert '--sku F0' in call_args
        assert '--sku S0' not in call_args
```

**Integration Testing:**
- **Docker build:** Vérifier image build sans erreurs
- **Container startup:** Vérifier Flask + OpenCode démarrent < 2 min
- **End-to-end:** Déploiement complet sur subscription Azure de test

**E2E Testing:**
- **Scénario complet:**
  1. Installer exe
  2. Exécuter script PowerShell
  3. Lancer start.bat
  4. Déployer services Azure (subscription test)
  5. Vérifier rapport intervention généré
- **Validation:** Services réellement créés sur Azure

**Performance Testing:**
- **Load test:** N/A (1 utilisateur)
- **Timing tests:** Mesurer temps démarrage + déploiement (NFR-001, NFR-002)

---

### CI/CD Pipeline

**GitHub Actions Pipeline:**

```yaml
# .github/workflows/ci.yml

name: CI/CD - Aux Petits Oignons

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'

      - name: Install dependencies
        run: |
          pip install -r container/requirements.txt
          pip install pytest pytest-cov

      - name: Run unit tests
        run: |
          pytest tests/ --cov=container/app --cov-report=term

      - name: Check coverage
        run: |
          pytest tests/ --cov=container/app --cov-report=term --cov-fail-under=80

  build-docker:
    runs-on: ubuntu-latest
    needs: test
    steps:
      - uses: actions/checkout@v3

      - name: Build Docker image
        run: |
          docker build -t trad-bot-opencode:test ./container

      - name: Test container startup
        run: |
          docker run -d --name test-container trad-bot-opencode:test
          sleep 30  # Attendre démarrage
          docker exec test-container ps aux | grep flask  # Vérifier Flask running
          docker stop test-container

  build-installer:
    runs-on: windows-latest
    needs: build-docker
    if: github.ref == 'refs/heads/main'
    steps:
      - uses: actions/checkout@v3

      - name: Install Inno Setup
        run: choco install innosetup

      - name: Compile installer
        run: |
          iscc installer/setup.iss

      - name: Upload installer artifact
        uses: actions/upload-artifact@v3
        with:
          name: AuxPetitsOignons_Setup
          path: installer/output/AuxPetitsOignons_Setup.exe
```

**Deployment Strategy:**
- **Manual deployment:** Eric distribue exe aux 2 techniciens
- **Versioning:** Tags Git (v1.0, v1.1) → Image Docker tags correspondants

---

### Environments

**Development:**
- **Eric's machine:** Développement local
- **Git branch:** `develop`
- **Container:** `trad-bot-opencode:dev`

**Testing:**
- **Azure subscription test:** Déploiements de test
- **Git branch:** `main`
- **Container:** `trad-bot-opencode:test`

**Production:**
- **Postes techniciens:** 2 machines
- **Git tag:** `v1.0`, `v1.1`, etc.
- **Container:** `trad-bot-opencode:latest` (ou `trad-bot-opencode:v1.0`)

**Environment Parity:**
- **Même container:** Dev/Test/Prod utilisent même Dockerfile
- **Différences:** API keys Azure Foundry (dev vs prod)

**Configuration Management:**
- **Variables d'environnement:** `.env` pour dev, docker-compose.yml pour prod
- **Secrets:** API keys jamais commitées (gitignore .env)

---

## Requirements Traceability

### FR Traceability

| FR ID | FR Name | Components | Implementation Notes |
|-------|---------|------------|---------------------|
| FR-001 | Installation via exécutable Windows | Component 1 (Installer) | Inno Setup, crée arborescence, lance start.bat |
| FR-002 | Gestion exclusions Defender ASR | Component 2 (PowerShell) | Script add-asr-exclusion.ps1, mode admin |
| FR-003 | Lancement automatique container | Component 3 (Docker) | start.bat → docker-compose up |
| FR-004 | Container pré-configuré | Component 3 (Docker) | Dockerfile avec OpenCode, Azure CLI, Flask |
| FR-005 | Ouverture automatique terminal + navigateur | Component 3 + start.bat | start.bat ouvre browser + exec docker opencode |
| FR-006 | Déploiement Azure Storage | Component 6 (Azure Deployer) | azure_deployer.create_storage_account() |
| FR-007 | Déploiement Translator F0 | Component 6 (Azure Deployer) | SKU F0 imposé dans create_translator() |
| FR-008 | Déploiement Functions | Component 6 (Azure Deployer) | deploy_function_app(), runtime Python 3.11 |
| FR-009 | Support multi-comptes | Component 6 + Azure CLI | az login --tenant <tenant-id> avec device flow, gère multi-comptes |
| FR-010 | Gestion cas MFA | Component 4 (OpenCode) + Doc | OpenCode guide création emplacements nommés |
| FR-011 | Serveur documentation Flask | Component 5 (Flask) | flask_server.py, serve Markdown → HTML |
| FR-012 | Clone repo trad-bot-src | Component 3 (start.sh) | git clone dans container au démarrage |
| FR-013 | Guidance conversationnelle | Component 4 (OpenCode) | System prompt français, explications claires |
| FR-014 | Génération rapport | Component 6 (Azure Deployer) | generate_intervention_report() |

**Coverage:** 14/14 FRs (100%)

---

### NFR Traceability

| NFR ID | NFR Name | Solution | Validation |
|--------|----------|----------|------------|
| NFR-001 | Temps démarrage < 2min | Image Docker optimisée, démarrage parallèle | Timer: docker-compose up → ready |
| NFR-002 | Déploiement < 15min | Parallélisation Storage + Translator | Chronomètre déploiement complet |
| NFR-003 | Aucun stockage credentials | Container éphémère, affichage terminal only | Scan sécurité + code review |
| NFR-004 | Exclusions Defender ciblées | Script PowerShell avec chemin absolu exe | Vérifier Get-MpPreference |
| NFR-005 | Gestion erreurs Azure CLI | Wrapper Python avec mapping erreurs → français | Tests erreurs simulées |
| NFR-006 | Interface conversationnelle simple | System prompt OpenCode + glossaire | Tests utilisateurs (2 techniciens) |
| NFR-007 | Mises à jour Azure CLI | Dockerfile versionné, tags Docker, rollback | Simuler update CLI 2.56→2.57 |
| NFR-008 | Environnement Windows | start.bat vérifie version + Docker Desktop | Tests VM Win10/Win11 |
| NFR-009 | Navigateurs modernes | HTML/CSS standard, pas de JS complexe | Tester Chrome/Edge/Firefox |
| NFR-010 | Messages erreur clairs | Format "Problème/Solution", pas de stack traces | Simuler erreurs, vérifier messages |

**Coverage:** 10/10 NFRs (100%)

---

## Architectural Trade-offs

### Decision 1: Container Docker vs Application native Windows

**Decision:** Utiliser Docker container

**Trade-offs:**
- ✓ **Gain:**
  - Isolation environnement (reproductibilité garantie)
  - Portabilité (Eric peut développer sur n'importe quel OS)
  - Pas d'interférence avec système host
  - Facilite maintenance (rebuild image vs réinstaller dépendances)
- ✗ **Perte:**
  - Nécessite Docker Desktop installé (~2-3 GB)
  - Temps de démarrage container (~1-2 min vs app native ~10s)
  - Overhead mémoire container (~500 MB vs app native ~100 MB)

**Rationale:** Pour un outil de déploiement, isolation et reproductibilité sont critiques. Le temps de démarrage acceptable (< 2min) et les techniciens ont des machines performantes (8GB+ RAM).

---

### Decision 2: OpenCode (Azure Foundry) vs Scripts CLI purs

**Decision:** Utiliser OpenCode pour guidance conversationnelle

**Trade-offs:**
- ✓ **Gain:**
  - UX conversationnel vs suivre doc écrite
  - Guidage adaptatif selon erreurs
  - Explications contextuelles en français
  - Réduction charge cognitive techniciens
- ✗ **Perte:**
  - Dépendance sur Azure Foundry (voir fallback Open Question Q3)
  - Coût API Claude (payé par société)
  - Latence réseau pour chaque réponse OpenCode

**Rationale:** Les techniciens ne sont pas experts Azure - guidage conversationnel réduit drastiquement erreurs et améliore satisfaction (Business Objective #2).

---

### Decision 3: Inno Setup vs WiX Toolset pour installer

**Decision:** Utiliser Inno Setup

**Trade-offs:**
- ✓ **Gain:**
  - Simplicité (script Pascal vs XML verbeux)
  - Gratuit et open-source
  - Mature et stable
  - Communauté large, documentation riche
- ✗ **Perte:**
  - Moins de fonctionnalités avancées que WiX
  - Moins "enterprise-grade"

**Rationale:** Pour 2-3 utilisateurs, simplicité > fonctionnalités avancées. Inno Setup largement suffisant.

---

### Decision 4: SKU F0 imposé (pas de choix utilisateur)

**Decision:** Hardcoder SKU F0 pour Azure Translator

**Trade-offs:**
- ✓ **Gain:**
  - Zéro risque d'erreur coûteuse (S0 = 35$/mois)
  - Standardisation garantie (Business Objective #1)
  - Confiance clients (pas de surprise facturation)
- ✗ **Perte:**
  - Aucune flexibilité si besoin > 2,5M caractères/mois
  - Doit modifier code pour changer SKU

**Rationale:** Product Brief identifie risque SKU comme critique. Pour Bot Traducteur, F0 suffit largement (2,5M caractères). Si futur bot nécessite S0, nouveau déploiement avec code modifié.

---

### Decision 5: Aucune base de données

**Decision:** Pas de DB, données éphémères uniquement

**Trade-offs:**
- ✓ **Gain:**
  - Simplicité architecture (pas de DB à gérer)
  - Sécurité (NFR-003 - aucun stockage credentials)
  - Aucun backup/restore nécessaire
- ✗ **Perte:**
  - Pas d'historique déploiements
  - Rapport intervention non persisté (technicien doit copier)
  - Pas de métriques/analytics

**Rationale:** Aucun besoin identifié pour données persistantes. Rapports copiés dans tickets clients (traçabilité externe).

---

## Next Steps

**Phase 4: Sprint Planning** → Run `/sprint-planning`

Avec cette architecture complète, l'équipe de développement a tout le nécessaire:

✓ **14 Functional Requirements** → Mappés à 6 composants
✓ **10 Non-Functional Requirements** → Solutions architecturales définies
✓ **4 Epics** → Prêts pour découpe en stories (14-20 estimées)
✓ **Technology Stack** → Justifié et documenté
✓ **3 Open Questions** → Résolues (Q1: Processus update CLI, Q2: Vérification Docker, Q3: Fallback mode dégradé)

**Sprint Planning va:**
- Créer 14-20 user stories détaillées depuis les 4 epics
- Estimer complexité (story points)
- Prioriser stories
- Planifier 2-3 sprints
- Commencer implémentation

---

## Appendix A: Deployment Checklist

**Pre-deployment (Eric):**
- [ ] Compiler Inno Setup: `iscc installer/setup.iss`
- [ ] Tester exe sur VM Windows test
- [ ] Vérifier Docker image build: `docker build -t trad-bot-opencode:latest ./container`
- [ ] Tester déploiement complet sur subscription Azure test
- [ ] Distribuer exe aux 2 techniciens

**Deployment (Technicien):**
- [ ] Vérifier Docker Desktop installé et démarré
- [ ] Exécuter AuxPetitsOignons_Setup.exe
- [ ] Exécuter script PowerShell ASR (mode admin): `.\add-asr-exclusion.ps1`
- [ ] Lancer start.bat
- [ ] Vérifier browser ouvre localhost:5545
- [ ] Vérifier OpenCode ready dans terminal
- [ ] Suivre guidance OpenCode pour déploiement Azure
- [ ] Copier rapport intervention dans ticket client
- [ ] Suivre documentation Power Platform (localhost:5545)

**Post-deployment (Technicien):**
- [ ] Vérifier services Azure créés (portal.azure.com)
- [ ] Tester Function App: GET /api/health
- [ ] Configurer connexions Power Platform
- [ ] Tester bot end-to-end

---

## Appendix B: Troubleshooting Guide

### Issue 1: Docker Desktop not started

**Symptom:** `docker: command not found` ou `Cannot connect to Docker daemon`

**Solution:**
1. Lancer Docker Desktop manuellement
2. Attendre 1-2 minutes que Docker démarre
3. Relancer start.bat

---

### Issue 2: Azure Foundry indisponible

**Symptom:** OpenCode ne démarre pas, message "OpenCode indisponible"

**Solution:**
- Mode dégradé activé automatiquement
- Suivre instructions manuelles affichées
- Exécuter commandes Azure CLI une par une

---

### Issue 3: Permissions Azure insuffisantes

**Symptom:** Erreur "AuthorizationFailed"

**Solution:**
1. Vérifier rôle dans Azure Portal
2. Demander au client Admin de donner rôle "Contributor"
3. Relancer déploiement

---

### Issue 4: MFA bloque az login

**Symptom:** `az login --tenant <tenant-id>` échoue avec erreur MFA

**Solution:**
1. OpenCode guide création emplacement nommé
2. Ajouter IP technicien dans emplacement nommé
3. Créer règle exclusion MFA pour cet emplacement
4. Réessayer `az login --tenant <tenant-id>`
5. **Important:** Supprimer règle MFA après déploiement

---

**This architecture was created using BMAD Method v6 - Phase 3 (Solutioning)**

*To continue: Run `/workflow-status` to see progress and next workflow.*
