# 📦 Guide Docker Hub - Image Publique

Ce guide explique comment publier l'image Docker sur Docker Hub pour accélérer l'installation.

---

## 🎯 Pourquoi publier sur Docker Hub ?

### Sans image publiée (actuellement)
```
Installation .exe
↓
Lancer start.bat
↓
Build Docker: 20 min ⏳
↓
Installation Bun: 6 min ⏳
↓
Total: 26 minutes
```

### Avec image publiée
```
Installation .exe
↓
Lancer start-production.bat
↓
Pull Docker Hub: 2-3 min ⚡
↓
Installation Bun: 6 min ⏳
↓
Total: 8-9 minutes
```

**Gain: 18 minutes par installation !**

---

## 📋 Prérequis

### 1. Créer un compte Docker Hub (gratuit)

1. Visitez: https://hub.docker.com/signup
2. Créez un compte:
   - **Docker ID**: `becloud` (ou autre nom)
   - **Email**: votre email
   - **Mot de passe**: choisir un mot de passe fort
3. Confirmez votre email
4. Notez votre **Docker ID** (ex: `becloud`)

### 2. Créer un repository public

1. Connexion: https://hub.docker.com
2. Cliquer **"Create Repository"**
3. Configuration:
   - **Name**: `aux-petits-oignons`
   - **Description**: "Bot Traducteur avec OpenCode - Fork Aux-petits-Oignons"
   - **Visibility**: **Public** ✅ (gratuit, aucune authentification requise)
4. Cliquer **"Create"**

**Résultat**: Repository `becloud/aux-petits-oignons` créé

---

## 🚀 Publication de l'image (vous, une seule fois)

### Étape 1: Modifier le Docker ID

Éditez `publish-docker-image.bat` et changez:

```batch
set DOCKER_ID=becloud
```

Remplacez `becloud` par votre Docker ID.

### Étape 2: Publier l'image

```batch
publish-docker-image.bat
```

Le script va:
1. Se connecter à Docker Hub (entrez vos identifiants)
2. Builder l'image localement (~20 min)
3. Tagger l'image avec votre Docker ID
4. Publier sur Docker Hub (~5-10 min)

**Total: ~30 minutes** (à faire une seule fois)

### Étape 3: Vérifier sur Docker Hub

Visitez: `https://hub.docker.com/r/VOTRE_DOCKER_ID/aux-petits-oignons`

Vous devriez voir:
- Tag `latest`
- Taille ~2 GB
- Statut "Public"

---

## ⚙️ Configuration pour les utilisateurs finaux

### Modifier l'installeur pour utiliser l'image publiée

1. Éditez `docker-compose.prod.yml` et changez:
   ```yaml
   image: becloud/aux-petits-oignons:latest
   ```
   Remplacez `becloud` par votre Docker ID.

2. Éditez `start-production.bat` et changez:
   ```batch
   set "DOCKER_IMAGE=becloud/aux-petits-oignons:latest"
   ```

3. Dans l'installeur, remplacez `start.bat` par `start-production.bat`

---

## 📂 Structure finale du projet

```
F:\deploy-trad-bot-contanier\
├── docker-compose.yml          # DEV: Build local
├── docker-compose.prod.yml     # PROD: Image Docker Hub
├── start.bat                   # DEV: Build si nécessaire
├── start-production.bat        # PROD: Pull depuis Docker Hub
├── publish-docker-image.bat    # Vous: Publier sur Docker Hub
└── rebuild-fast.bat            # DEV: Rebuild manuel
```

---

## 🔄 Workflow complet

### Pour vous (développeur)

**Développement:**
```batch
start.bat              # Build local + test
```

**Nouvelle version à publier:**
```batch
publish-docker-image.bat    # Build + Push vers Docker Hub
```

### Pour les utilisateurs finaux

**Installation .exe inclut:**
- `docker-compose.prod.yml`
- `start-production.bat`
- `conf_opencode/.env` (pré-configuré)

**Après installation, lancer:**
```
Menu Démarrer > Aux petits oignons
```

**Séquence:**
1. Pull image depuis Docker Hub (~2-3 min)
2. Démarrer container
3. Installation Bun (~6 min au premier lancement)
4. OpenCode s'ouvre

**Total: 8-9 minutes**

---

## 🔒 Image Publique vs Privée

### Image Publique (actuelle, GRATUIT)

✅ **Avantages:**
- Gratuit illimité
- Aucune authentification pour pull
- Les utilisateurs téléchargent directement
- Simple à mettre en place

❌ **Inconvénients:**
- Tout le monde peut télécharger l'image
- Visible sur Docker Hub

### Image Privée (optionnel, PAYANT)

✅ **Avantages:**
- Contrôle d'accès (authentification requise)
- Invisible sur Docker Hub
- Sécurité renforcée

❌ **Inconvénients:**
- **$7/mois** pour Docker Hub Pro (1 repo privé gratuit)
- Les utilisateurs doivent se connecter avec `docker login`
- Plus complexe pour l'installation

**Recommandation**: Image **publique** car:
- Le code source est déjà public sur GitHub
- Pas de secrets dans l'image Docker
- Installation plus simple pour les utilisateurs

---

## 📊 Comparaison finale

| Critère | Build local | Image Docker Hub |
|---------|-------------|------------------|
| **Temps installation** | 26 min | 8 min |
| **Connexion Internet** | Requise | Requise |
| **Taille téléchargement** | ~500 MB (packages) | ~2 GB (image) |
| **Premier lancement** | Build 20 min | Pull 2-3 min |
| **Mises à jour** | Rebuild 20 min | Pull 2-3 min |
| **Coût** | Gratuit | Gratuit (public) |

---

## 🔄 Mettre à jour l'image

Quand vous faites des modifications au code:

```batch
# 1. Tester localement
start.bat

# 2. Si OK, republier sur Docker Hub
publish-docker-image.bat

# 3. Les utilisateurs récupèrent la nouvelle version
docker pull becloud/aux-petits-oignons:latest
```

**Versionning recommandé:**
```batch
docker tag auxpetitsoignons-trad-bot:latest becloud/aux-petits-oignons:v1.4
docker push becloud/aux-petits-oignons:v1.4
```

---

## ❓ FAQ

**Q: L'image contient-elle les clés API Azure?**
R: Non, les clés sont dans `conf_opencode/.env` qui est monté comme volume (pas dans l'image).

**Q: Dois-je republier à chaque modification?**
R: Seulement pour les modifications du Dockerfile ou des dépendances système. Les modifications de `conf_opencode/` ou `scripts/` sont des volumes.

**Q: Combien de temps l'upload prend-il?**
R: ~5-10 minutes pour ~2 GB (selon votre connexion).

**Q: Les utilisateurs paient-ils quelque chose?**
R: Non, le téléchargement d'images publiques est gratuit et illimité.

---

## 🎉 Résultat final pour l'utilisateur

```
1. Double-clic sur AuxPetitsOignons_Setup.exe
2. Cliquer "Suivant" plusieurs fois
3. Cocher "Lancer Aux petits oignons"
4. Attendre 8-9 minutes
5. OpenCode s'ouvre avec les 3 modèles Azure
```

**Installation complètement automatisée !**
