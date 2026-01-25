# 🚀 Quick Start - Option 4 : Fork Aux-petits-Oignons

**Installation rapide en 5 minutes**

---

## ⚡ Installation Express

### 1️⃣ Configurer les clés Azure (2 min)

```bash
# Copier le template
copy conf_opencode\.env.example conf_opencode\.env

# Éditer avec Notepad
notepad conf_opencode\.env
```

**Remplir AU MINIMUM 1 endpoint** :

```env
# Option A : Azure OpenAI (recommandé)
AZURE_OPENAI_ENDPOINT=https://votre-endpoint.openai.azure.com
AZURE_OPENAI_API_KEY=votre_cle_api

# OU Option B : Azure AI Foundry
AZURE_AI_FOUNDRY_ENDPOINT=https://votre-endpoint.cognitiveservices.azure.com
AZURE_API_KEY=votre_cle_api
```

**⚠️ Commenter Anthropic si non utilisé** :
```env
# ANTHROPIC_BASE_URL=...
# ANTHROPIC_API_KEY=...
```

---

### 2️⃣ Builder l'image (2-3 min)

```bash
# Lancer le menu
rebuild-fast.bat

# Choisir 4
4

# Appuyer sur Entrée
```

**OU directement** :
```bash
docker build -f Dockerfile.custom-opencode -t deploy-trad-bot-contanier-trad-bot-opencode:latest .
```

---

### 3️⃣ Démarrer le container (1 min)

```bash
# Via docker-compose
docker-compose up -d

# OU via script PowerShell
.\start-custom.ps1
```

---

### 4️⃣ Attendre l'installation du fork (5-6 min) ☕

**Première fois uniquement** - Le container installe automatiquement :
- 1818 packages Bun
- Configuration entreprise
- Wrapper OpenCode

```
==========================================
  Premier démarrage - Compilation du fork
  Aux Petits Oignons (OpenCode custom)
==========================================

Installation des dépendances Bun...
...
✓ Fork Aux Petits Oignons prêt
==========================================
```

**Démarrages suivants** : ⚡ **Instantané** !

---

### 5️⃣ Tester OpenCode (30 sec)

```bash
# Accéder au container
docker exec -it trad-bot-opencode bash

# Lancer OpenCode
opencode
```

**Message attendu** :
```
========================================
  🧅 Aux Petits Oignons - Be-Cloud
========================================

  Modeles IA disponibles (Azure):
    - GPT-4.1 Mini    (defaut)
    - GPT-5 Mini
    - Model Routeur

  opencode      Nouvelle conversation
========================================
```

---

## ✅ Vérification Rapide

```powershell
# Script de test automatique
.\test-opencode.ps1
```

**Résultat attendu** :
```
✅ OpenCode version: local
✅ Azure OpenAI Endpoint configuré
✅ Azure AI Foundry Endpoint configuré
✅ Fork opérationnel
```

---

## 🎯 Commandes Essentielles

```bash
# Accéder au container
docker exec -it trad-bot-opencode bash

# Lancer OpenCode
opencode

# Reprendre conversation
opencode -c

# Changer de modèle
/settings

# Quitter OpenCode
exit (ou Ctrl+C)

# Voir les logs
docker logs trad-bot-opencode

# Redémarrer container
docker restart trad-bot-opencode
```

---

## ❌ Problèmes Fréquents

### OpenCode demande clé Anthropic

**Solution** : Commenter les lignes dans `conf_opencode/.env`
```env
# ANTHROPIC_BASE_URL=...
# ANTHROPIC_API_KEY=...
```

Puis redémarrer :
```bash
docker restart trad-bot-opencode
```

---

### Warning "baseline-browser-mapping"

**Solution** : Ignorable - automatiquement supprimé au démarrage.

---

### Container ne démarre pas

**Solution** : Vérifier les volumes
```bash
mkdir "%USERPROFILE%\AuxPetitsOignons\clients"
mkdir "%USERPROFILE%\AuxPetitsOignons\Solution"
```

---

## 📚 Documentation Complète

Pour plus de détails :

👉 **[README-OPTION4.md](./README-OPTION4.md)** - Documentation complète

Sections :
- Configuration détaillée des 3 endpoints
- Troubleshooting approfondi
- Comparaison avec autres options
- Mise à jour du fork
- Architecture du système

---

## ⏱️ Temps Total

| Étape | Temps |
|-------|-------|
| Configuration .env | 2 min |
| Build Docker | 2-3 min |
| Démarrage container | 1 min |
| Installation fork (1ère fois) | 5-6 min |
| Test OpenCode | 30 sec |
| **TOTAL** | **~11 minutes** |

**Démarrages suivants** : ⚡ **Instantané** (~10 secondes)

---

## 🎉 C'est tout !

Vous avez maintenant un environnement OpenCode sécurisé avec :
- ✅ 4 modèles Azure verrouillés
- ✅ Configuration entreprise non modifiable
- ✅ Custom loaders pour routage Azure
- ✅ Branding Be-Cloud
- ✅ Sécurité renforcée (pas de fuite données)

**Bon coding ! 🧅**

_Propulsé par Be-Cloud_
