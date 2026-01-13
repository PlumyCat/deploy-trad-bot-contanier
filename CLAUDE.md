# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

"Aux Petits Oignons" is a Docker-based deployment environment for a **Bot Traducteur** (Translator Bot) that combines Copilot Studio with Azure Functions. It packages OpenCode (AI agent), Azure CLI, and documentation into a container for deploying translation services to client tenants.

## Common Commands

### Docker Operations
```bash
# Build and start container
docker-compose up -d

# Access container shell (then run 'opencode' inside)
docker exec -it trad-bot-opencode bash

# View documentation
# Open http://localhost:5545/procedure in browser
```

### Azure Functions (run inside container, from /app/src)
```bash
# Install dependencies
pip install -r requirements.txt

# Run functions locally
func start

# Deploy to Azure
func azure functionapp publish <FUNCTION_APP_NAME>
```

### Installer (Windows, requires Inno Setup)
```bash
# Compile installer from installer/setup.iss
# Output: installer/output/AuxPetitsOignons_Setup.exe
```

## Architecture

### Two-Layer System

1. **Deployment Container** (root level): Ubuntu 24.04 Docker container with OpenCode, Azure CLI, and Flask documentation server. Entry point is `start.bat` (Windows) which starts the container and opens docs at port 5545.

2. **Azure Functions Backend** (`src/`): Python HTTP functions deployed to client Azure subscriptions that handle document translation.

### Azure Functions Endpoints

| Function | Route | Purpose |
|----------|-------|---------|
| `start_translation` | POST /api/start_translation | Initiates Azure Translator batch job |
| `check_status` | GET /api/check_status?translation_id=X | Polls translation status |
| `get_result` | GET/POST /api/get_result | Returns SAS URL + optional OneDrive upload |
| `health` | GET /api/health | Health check endpoint |
| `languages` | GET /api/languages | Lists supported languages |
| `formats` | GET /api/formats | Lists supported file formats |

### Shared Services (`src/shared/`)

- `config.py` - Centralized environment variable configuration
- `services/translation_service.py` - Azure Translator Batch API client
- `services/blob_service.py` - Azure Storage operations with SAS generation
- `services/graph_service.py` - Microsoft Graph API for OneDrive uploads
- `utils/response_helper.py` - Standardized HTTP response formatting

### Deployment Workflow (3 Phases)

1. **Phase 0** (Client Admin Global): Create Entra ID App Registration for OneDrive access
2. **Phase 1** (Delegated Account): Deploy Azure resources (Storage, Translator, Function App)
3. **Phase 2** (Client Admin): Import Power Platform solution (`Solution/BotCopilotTraducteur_1_0_0_4.zip`)

## Environment Variables (for Function App)

**Required:**
- `AZURE_ACCOUNT_NAME`, `AZURE_ACCOUNT_KEY` - Storage Account
- `TRANSLATOR_KEY`, `TRANSLATOR_ENDPOINT`, `TRANSLATOR_REGION` - Azure Translator

**OneDrive Integration:**
- `CLIENT_ID`, `SECRET_ID`, `TENANT_ID` - Entra ID App credentials
- `ONEDRIVE_UPLOAD_ENABLED` - Set to "true" to enable
- `ONEDRIVE_FOLDER` - Target folder name in user's OneDrive

## Key Files

- `src/CLAUDE.md` - Detailed deployment instructions with Azure CLI commands
- `src/GUIDE_POWER_PLATFORM_COMPLET.md` - Step-by-step Power Platform guide (served by Flask)
- `conf_opencode/.env` - OpenCode API key configuration (create from `.env.example`)
