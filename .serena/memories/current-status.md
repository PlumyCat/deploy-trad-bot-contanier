# État actuel du projet

**Dernière mise à jour**: 2026-01-09

## Nettoyage effectué ✅

### Structure finale de src/
```
src/
├── check_status/       # Azure Function
├── formats/            # Azure Function
├── get_result/         # Azure Function
├── health/             # Azure Function
├── languages/          # Azure Function
├── start_translation/  # Azure Function
├── shared/             # Code partagé
├── Solution/           # BotCopilotTraducteur_1_0_0_4.zip
├── images/             # Screenshots pour la doc
├── clients/            # Rapports d'intervention
├── host.json
├── requirements.txt
├── .funcignore
├── .gitignore
├── README.md
└── GUIDE_POWER_PLATFORM_COMPLET.md
```

### Fichiers supprimés
- `copilot-deployment-bot/` (projet séparé non utilisé)
- `.git/`, `.vscode/`, `tests/`, `docs/`
- Scripts: `setup_vm.sh`, `deploy_client.py`, `deploy_power_platform.py`, `deploy.sh`
- Docs obsolètes: CORRECTIONS_FINALES.md, DEMARRAGE_*.md, etc.

## Configuration Docker

### docker-compose.yml
- Lance `opencode` directement au démarrage
- Serveur de doc en background sur port 8080 (exposé 5545)
- Working directory: `/app/src`

### Commandes
```bash
# Lancer le container (opencode s'ouvre automatiquement)
docker-compose up -d
docker attach trad-bot-opencode

# Documentation
http://localhost:5545/procedure
```

## Outils disponibles dans le container
- ✅ Azure CLI (`az`)
- ✅ Azure Functions Core Tools (`func`)
- ✅ OpenCode
- ✅ Python 3.12 + packages Azure
