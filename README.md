# 🧅 Aux Petits Oignons

> *Parce que le déploiement du Bot Traducteur, on vous le prépare aux petits oignons !*

Un environnement de déploiement tout-en-un pour le **Bot Traducteur Copilot Studio**. OpenCode + Azure CLI + documentation intégrée, le tout servi dans un container Docker bien mijoté.

---

## 🚀 Installation

### Prérequis

1. **Docker Desktop** : https://www.docker.com/products/docker-desktop/
2. **Inno Setup** : https://jrsoftware.org/isdl.php

> ⚠️ Redémarrez votre ordinateur après l'installation de Docker.

### Étapes d'installation

```
1. Cloner le repo
2. Clic droit sur exclude-defender.ps1 → Exécuter en tant qu'administrateur
3. Ouvrir installer/setup.iss avec Inno Setup → Compile (Ctrl+F9)
4. Lancer installer/output/AuxPetitsOignons_Setup.exe
```

> **Note** : L'exe n'est pas inclus dans le repo (non signé = bloqué par Defender). Il doit être compilé localement.

---

## 🎯 Utilisation

Après installation, vous trouverez dans le **Menu Démarrer** :

| Raccourci | Description |
|-----------|-------------|
| 🧅 **Aux petits oignons** | Lance OpenCode + Documentation |
| 📄 **Documentation (Web)** | Ouvre le guide de déploiement |
| 📦 **Solution Power Platform** | Accès au fichier .zip à importer |
| 📁 **Rapports Clients** | Dossier des rapports d'intervention |

---

## 📖 C'est quoi dans la marmite ?

```
🧅 Aux Petits Oignons
│
├── 🤖 OpenCode          → Agent IA pour le déploiement
├── ☁️  Azure CLI         → Gestion des ressources Azure
├── ⚡ Azure Func Tools   → Déploiement des Functions
├── 📚 Documentation     → Guide pas-à-pas avec images
└── 🐳 Docker            → Tout ça bien emballé !
```

---

## 🛠️ Pour les développeurs

### Structure du projet

```
├── src/                    # Code Azure Functions du bot traducteur
├── Solution/               # Solution Power Platform (.zip)
├── clients/                # Rapports d'intervention (persistant)
├── conf_opencode/          # Configuration OpenCode
├── icone/                  # L'oignon ! 🧅
├── installer/              # Script Inno Setup
│   ├── setup.iss
│   └── output/             # L'exe généré
├── Dockerfile
├── docker-compose.yml
├── doc_server.py           # Serveur de documentation Flask
└── start.bat               # Point d'entrée
```

### Lancer manuellement (sans installeur)

```bash
# Démarrer le container
docker-compose up -d

# Ouvrir OpenCode
docker exec -it trad-bot-opencode opencode
```

Documentation : http://localhost:5545/procedure

### Publier l'image Docker (pour accélérer l'installation)

Pour éviter le build de 20+ minutes lors de l'installation, publiez l'image sur Docker Hub :

```bash
# Build et tag l'image
docker-compose build
docker tag deploy-trad-bot-contanier-trad-bot:latest becloud/aux-petits-oignons:latest

# Se connecter à Docker Hub
docker login

# Push l'image
docker push becloud/aux-petits-oignons:latest
```

Une fois publiée, l'installeur téléchargera l'image (~2 min) au lieu de la construire (~20 min).

---

## 🧅 Pourquoi "Aux Petits Oignons" ?

Parce qu'un bon déploiement, c'est comme un bon plat :
- Ça demande les **bons ingrédients** (Azure CLI, Functions Tools...)
- Une **recette claire** (la documentation intégrée)
- Et surtout, beaucoup de **soin** dans la préparation !

*Bon déploiement, et n'oubliez pas de pleurer de joie, pas à cause des oignons !* 😄

---

## 📝 Licence

Projet interne Be-Cloud

---

<p align="center">
  <img src="icone/oignon.ico" width="64" alt="Aux Petits Oignons">
  <br>
  <i>Fait avec 💚 et quelques larmes d'oignon</i>
</p>
