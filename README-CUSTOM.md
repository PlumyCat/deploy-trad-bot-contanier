# Version Custom : Fork Aux-petits-Oignons

Ce document explique la différence entre la version **standard** et la version **custom** du container.

## 🆚 Comparaison des versions

| Fonctionnalité | Version Standard | Version Custom (Fork) |
|---|---|---|
| OpenCode | `opencode-ai` (npm) | Fork Aux-petits-Oignons |
| Modèles IA | Tous les modèles disponibles | **4 modèles Azure uniquement** |
| Configuration | Libre | **Verrouillée entreprise** |
| Welcome Page | Standard OpenCode | **"Aux petits Oignons" personnalisée** |
| Build Time | 9-10 min | 12-15 min |
| Taille Image | ~3.5 GB | ~3.8 GB |

## 🎯 Pourquoi la version Custom ?

### Sécurité & Contrôle des coûts
- ✅ **Pas de modèles gratuits** qui pourraient fuiter des données clients
- ✅ **Seulement 4 modèles Azure approuvés** de votre souscription dev (140$/mois)
- ✅ **Configuration verrouillée** - impossible de modifier les modèles sans rebuild

### Modèles disponibles (Azure uniquement)

1. **GPT-4.1 Mini** (défaut)
   - Provider: Azure OpenAI
   - Variable: `AZURE_OPENAI_ENDPOINT` + `AZURE_OPENAI_API_KEY`

2. **GPT-5 Mini**
   - Provider: Azure OpenAI
   - Variable: `AZURE_OPENAI_ENDPOINT` + `AZURE_OPENAI_API_KEY`

3. **Model Routeur**
   - Provider: Azure AI Foundry
   - Variable: `AZURE_AI_FOUNDRY_ENDPOINT` + `AZURE_API_KEY`

4. **Claude Sonnet** (optionnel, si dispo France)
   - Provider: Azure AI Foundry (Anthropic)
   - Variable: `ANTHROPIC_BASE_URL` + `ANTHROPIC_API_KEY`

## 🚀 Build de la version Custom

### 1. Choisir la version Custom lors du rebuild

```batch
rebuild-fast.bat
```

Puis choisissez **Option 4 : Fork Aux-petits-Oignons**

### 2. Configuration des credentials

Le fork nécessite **plus de variables** que la version standard :

```bash
# Copiez le template spécifique au fork
copy conf_opencode\.env.example.custom conf_opencode\.env

# Ou utilisez configure.bat qui demandera toutes les variables
configure.bat
```

### 3. Variables d'environnement requises

**Minimum requis (GPT-4.1 Mini + GPT-5 Mini uniquement) :**
```env
AZURE_OPENAI_ENDPOINT=https://votre-ressource.openai.azure.com
AZURE_OPENAI_API_KEY=votre_cle_api
```

**Pour activer Claude Sonnet (optionnel) :**
```env
ANTHROPIC_BASE_URL=https://proj-becloud-ia-us.services.ai.azure.com/anthropic
ANTHROPIC_API_KEY=votre_cle_api_anthropic
```

**Pour activer Model Routeur (optionnel) :**
```env
AZURE_AI_FOUNDRY_ENDPOINT=https://votre-endpoint.cognitiveservices.azure.com
AZURE_API_KEY=votre_cle_api_generique
```

## 📦 Différences techniques

### Architecture du Fork

Le fork **Aux-petits-Oignons** est basé sur :
- **Monorepo Bun** (au lieu de package npm simple)
- **Configuration entreprise** dans `config/enterprise-config.json`
- **Welcome page personnalisée** intégrée
- **Restrictions de modèles** au niveau du code source

### Fichiers spécifiques

```
/opt/aux-petits-oignons/              # Fork complet
├── config/
│   └── enterprise-config.json        # Config verrouillée
├── packages/
│   └── opencode/                     # Package OpenCode modifié
└── .env                              # Variables d'environnement
```

## 🔄 Passer de Standard à Custom

1. Arrêter le container actuel :
   ```batch
   docker-compose down
   ```

2. Rebuild avec Option 4 :
   ```batch
   rebuild-fast.bat
   ```

3. Mettre à jour `.env` avec les nouvelles variables

4. Redémarrer :
   ```batch
   start.bat
   ```

## ⚠️ Limitations

### Version Custom
- ❌ Pas de modèles gratuits (Anthropic direct, OpenAI direct, etc.)
- ❌ Configuration verrouillée (changement = rebuild)
- ⏱️ Build plus long (12-15 min vs 9-10 min)

### Avantages
- ✅ Sécurité maximale (pas de fuite possible vers modèles externes)
- ✅ Contrôle des coûts (souscription dev 140$/mois)
- ✅ Welcome page entreprise
- ✅ Conformité garantie

## 🆘 Troubleshooting

**Erreur "Model not found"**
→ Vérifiez que les variables d'environnement Azure sont bien configurées dans `.env`

**Build échoue sur "bun: not found"**
→ Normal, le Dockerfile installe Bun automatiquement. Si ça échoue, relancez le build.

**OpenCode démarre mais pas de modèles disponibles**
→ Vérifiez `/root/.config/opencode/enterprise-config.json` dans le container

## 🔗 Liens

- Repo du fork : https://github.com/PlumyCat/Aux-petits-Oignons
- OpenCode officiel : https://github.com/anomalyco/opencode
- Branch custom : `feature/opencode-custom`
