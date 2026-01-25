# Guide de Test - Fork Aux-petits-Oignons

## ✅ Modifications effectuées

1. **`.env` modifié** :
   - ❌ Lignes Anthropic commentées (en secours uniquement)
   - ✅ Azure OpenAI actif (GPT-4.1-mini + GPT-5-mini)
   - ✅ Azure AI Foundry actif (Model-Router)
   - ✅ Tavily Search actif

2. **`enterprise-config.json` modifié** :
   - Claude Sonnet : `"enabled": false`
   - GPT-4.1 Mini : `"enabled": true, "default": true` ⭐
   - GPT-5 Mini : `"enabled": true`
   - Model-Router : `"enabled": true`

## 🚀 Comment tester OpenCode

### Étape 1 : Accéder au container

```powershell
docker exec -it trad-bot-opencode bash
```

### Étape 2 : Lancer OpenCode

```bash
opencode
```

**Comportement attendu** :
- ✅ OpenCode démarre directement
- ✅ GPT-4.1-mini est sélectionné par défaut
- ❌ Plus de demande de clé Anthropic

### Étape 3 : Tester les 3 modèles actifs

Dans OpenCode, tapez `/settings` pour changer de modèle :

1. **GPT-4.1 Mini** (par défaut)
   - Endpoint : `AZURE_OPENAI_ENDPOINT`
   - Clé configurée : ✅

2. **GPT-5 Mini**
   - Endpoint : `AZURE_OPENAI_ENDPOINT` (même que GPT-4.1)
   - Clé configurée : ✅

3. **Model-Router**
   - Endpoint : `AZURE_AI_FOUNDRY_ENDPOINT`
   - Clé configurée : ✅

## 🔧 Si l'avertissement `baseline-browser-mapping` apparaît

C'est un simple warning (pas une erreur) :

```
[baseline-browser-mapping] The data in this module is over two months old...
```

**Solution** : Ignorez-le pour l'instant. C'est juste une dépendance de développement Bun qui n'affecte pas le fonctionnement.

Pour le supprimer définitivement (optionnel) :
```bash
# Dans le container
cd /opt/aux-petits-oignons
bun update baseline-browser-mapping
```

## ✅ Test rapide

```bash
# 1. Connexion au container
docker exec -it trad-bot-opencode bash

# 2. Lancer OpenCode
opencode

# 3. Taper une question simple
"Bonjour, quel est ton nom ?"

# 4. Vérifier la réponse
# Devrait répondre avec GPT-4.1-mini sans erreur
```

## 📝 Modèles disponibles maintenant

| Modèle | Status | Endpoint | Clé |
|--------|--------|----------|-----|
| GPT-4.1 Mini | ✅ Actif (défaut) | AZURE_OPENAI_ENDPOINT | ✅ |
| GPT-5 Mini | ✅ Actif | AZURE_OPENAI_ENDPOINT | ✅ |
| Model-Router | ✅ Actif | AZURE_AI_FOUNDRY_ENDPOINT | ✅ |
| Claude Sonnet | ⏸️ Désactivé (secours) | - | ❌ |

## 🔄 Pour réactiver Claude Sonnet plus tard

1. Éditer `conf_opencode/.env` :
   ```env
   ANTHROPIC_BASE_URL=https://votre-endpoint-claude.services.ai.azure.com/anthropic
   ANTHROPIC_API_KEY=votre_vraie_cle
   ```

2. Modifier le fork pour réactiver :
   ```bash
   docker cp trad-bot-opencode:/root/.config/opencode/enterprise-config.json ./
   # Éditer : "enabled": true pour claude-sonnet
   docker cp ./enterprise-config.json trad-bot-opencode:/root/.config/opencode/
   docker restart trad-bot-opencode
   ```

## 🎯 Résumé

- ✅ Fork fonctionnel avec 3 modèles Azure actifs
- ✅ Plus de demande Anthropic au démarrage
- ✅ GPT-4.1-mini par défaut
- ⚠️ Warning `baseline-browser-mapping` ignorable
