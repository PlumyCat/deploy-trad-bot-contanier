# Projet deploy-trad-bot-container

## Description
Ce projet est un système de déploiement automatisé pour un **Bot Traducteur** basé sur Copilot Studio et Azure Functions. Il utilise OpenCode dans un container Docker pour orchestrer les déploiements chez les clients.

## Architecture

### Container Docker (Ubuntu 24.04)
- **OpenCode**: Agent IA pour le déploiement automatisé
- **Python 3.12**: Environnement d'exécution principal
- **Documentation Server**: Flask sur port 8080

### Composants Azure déployés pour chaque client
1. **Resource Group**: `rg-translation-{client}`
2. **Storage Account**: `sttrad{client}` avec containers `doc-to-trad` et `doc-trad`
3. **Azure Translator**: Service de traduction (F0 gratuit ou S1 payant)
4. **Function App**: Azure Functions Python 3.12

### Composants Power Platform
- **Solution Copilot Studio**: `BotCopilotTraducteur_1_0_0_4.zip`
- **Topics de conversation**: Démarrage, statut, validation, liste des déploiements

## Structure des fichiers clés

```
/
├── Dockerfile              # Image Docker Ubuntu + OpenCode
├── docker-compose.yml      # Configuration du container
├── requirements.txt        # Dépendances Python Azure
├── conf_opencode/
│   ├── .env               # Clé API OpenCode (ANTHROPIC_API_KEY)
│   └── opencode.json      # Configuration OpenCode
├── clients/               # Données clients (volume monté)
└── src/
    ├── deploy_client.py   # Script principal de déploiement
    ├── setup_vm.sh        # Installation des prérequis système
    ├── host.json          # Config Azure Functions
    ├── requirements.txt   # Dépendances des Functions
    ├── Solution/          # Solution Power Apps à importer
    └── copilot-deployment-bot/  # Backend du bot de déploiement
```

## Outils requis (à installer dans le container)
- **Azure CLI (az)**: Gestion des ressources Azure
- **Azure Functions Core Tools (func)**: Déploiement des Functions
- **Power Platform CLI (pac)**: Déploiement des solutions Copilot

## Workflow de déploiement
1. Vérification des prérequis (`check_prerequisites`)
2. Connexion Azure (`az login`)
3. Collecte des informations client
4. Création des ressources Azure
5. Configuration et déploiement du code
6. Test de l'endpoint /health
7. (Optionnel) Déploiement de la solution Power Platform
