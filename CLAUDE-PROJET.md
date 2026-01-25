# Bot Traducteur - Projet Azure Functions

Vous êtes dans le projet **Bot Traducteur** (trad-bot-src).

## Votre mission

Aider au développement et déploiement des Azure Functions pour la traduction de documents.

## Architecture

- **Langage** : Python 3.11
- **Framework** : Azure Functions (HTTP triggers)
- **Services** : Azure Translator, Azure Storage, Microsoft Graph (OneDrive)

## Structure du projet

```
/app/src/
├── start_translation/    - Démarre un job de traduction
├── check_status/         - Vérifie le statut
├── get_result/           - Récupère les résultats
├── health/              - Health check
├── languages/           - Liste des langues
├── formats/             - Formats supportés
├── shared/              - Code partagé
│   ├── config.py        - Variables d'environnement
│   ├── services/        - Services Azure
│   └── utils/           - Utilitaires
└── requirements.txt     - Dépendances Python
```

## Commandes utiles

```bash
# Installer dépendances
pip install -r requirements.txt

# Lancer localement
func start

# Déployer
func azure functionapp publish <NOM_FUNCTION_APP>
```

## Ce que vous NE devez PAS faire

- ❌ Modifier le code d'OpenCode (/opt/aux-petits-oignons)
- ❌ Lire AGENTS.md (c'est pour développer OpenCode, pas pour ce projet)
- ❌ Travailler sur le fork Aux-petits-Oignons

## Ce que vous DEVEZ faire

- ✅ Travailler dans /app/src (projet trad-bot-src)
- ✅ Lire CLAUDE.md s'il existe dans /app/src
- ✅ Aider au développement des Azure Functions
- ✅ Respecter l'architecture existante

## Documentation complète

Lisez `/app/src/CLAUDE.md` pour les instructions détaillées du projet.
