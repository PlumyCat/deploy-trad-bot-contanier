# Product Brief: Aux Petits Oignons

**Date:** 2026-01-18
**Author:** Eric
**Version:** 1.0
**Project Type:** Deployment Automation Tool
**Project Level:** 2 (Medium - 5-15 stories)

---

## Executive Summary

Aux Petits Oignons est une application de déploiement automatisé qui permet aux techniciens non-familiers avec Azure de déployer des bots Copilot Studio avec leurs services Azure associés, sans erreur. Elle utilise un container Docker avec OpenCode (connecté à Azure Foundry) pour guider les techniciens à travers le déploiement Azure complexe, tout en affichant une documentation pour la partie Power Platform qu'ils maîtrisent déjà. L'objectif est de déléguer des déploiements testés à 100% tout en garantissant la qualité "aux petits oignons", avec une extension prévue vers d'autres bots si le succès est au rendez-vous.

---

## Problem Statement

### The Problem

Le déploiement des bots Copilot Studio devient complexe car il inclut l'installation de services Azure (Storage, Translator, Functions). Les techniciens Modern Workplace qui doivent effectuer ces déploiements ne sont pas familiarisés avec Azure - ce n'est pas leur cœur de métier. Les formations réalisées montrent que la complexité Azure les démotive et crée des risques d'erreurs critiques :

- **Choix de SKU incorrects** : Par exemple, sélectionner S0 (35$/mois) au lieu de F0 (gratuit jusqu'à 2,5M caractères) pour Azure Translator peut créer des coûts imprévus chez les clients
- **Configurations incohérentes** : Risque d'utiliser différentes méthodes de déploiement d'une fois à l'autre
- **Erreurs de configuration** : Mauvais type de service, paramètres incorrects
- **Manque de standardisation** : Chaque déploiement peut être fait différemment

### Why Now?

Le créateur du projet doit se concentrer sur d'autres initiatives et a reçu une demande de créer une procédure pour déléguer ces déploiements. Les déploiements sont testés à 100% et fonctionnels, mais impossible de transférer cette expertise via des formations traditionnelles. Une solution automatisée s'impose pour permettre la délégation tout en maintenant la qualité.

### Impact if Unsolved

- **Non-scalable** : Le créateur reste le seul capable de faire les déploiements, créant un goulot d'étranglement
- **Risques financiers** : Erreurs de SKU peuvent créer des coûts imprévus chez les clients (confiance impactée)
- **Blocage de croissance** : Impossible d'étendre le déploiement à d'autres bots sans résoudre ce problème
- **Qualité variable** : Sans standardisation, la qualité des déploiements ne peut être garantie

---

## Target Audience

### Primary Users

**Les 2 techniciens Modern Workplace / Consultants Power Platform**

- **Rôle** : Techniciens spécialisés en Microsoft 365 et Power Platform
- **Compétences** :
  - Experts Power Platform (Copilot Studio, Power Apps, Power Automate)
  - Autonomes sur le déploiement Power Platform
  - Non-familiers avec Azure (Infrastructure as a Service)
  - Capables de gérer les connexions Entra ID et règles MFA
- **Contexte** : Travaillent chez des clients avec des comptes délégués ou créent des comptes admin temporaires
- **Attitude** : Motivés pour Power Platform, réticents à apprendre Azure en profondeur (pas leur cœur de métier)

### Secondary Users

- **Eric (Créateur/Mainteneur)** : Supervision, support exceptionnel, maintenance de l'outil
- **Clients finaux** : Bénéficient de déploiements fiables et standardisés sans intervention visible

### User Needs

Les techniciens ont besoin de :

1. **Déployer Azure sans expertise Azure** - Leur cœur de métier est Power Platform, pas l'infrastructure Azure
2. **Éviter les erreurs coûteuses** - Garantie de sélection des bons SKU (F0 vs S0), bons types de services, bonnes configurations
3. **Documentation claire pour Power Platform** - Partie qu'ils maîtrisent mais qui nécessite des consignes spécifiques au bot
4. **Rester autonomes après le déploiement Azure** - Pas de dépendance continue sur l'expert Azure

---

## Solution Overview

### Proposed Solution

**Aux Petits Oignons** est un outil tout-en-un de déploiement automatisé qui :

1. **S'installe via un exécutable Windows** (`.exe`) avec script PowerShell pour gérer les exclusions Defender ASR
2. **Lance un container Docker pré-configuré** contenant :
   - OpenCode (agent IA) connecté à Azure Foundry (modèle payé par la société)
   - Azure CLI pour les opérations Azure
   - Serveur de documentation Flask
3. **Ouvre automatiquement** :
   - Une page web avec la documentation Power Platform (http://localhost:5545)
   - Un terminal avec OpenCode pré-configuré
4. **Guide le technicien** via conversation avec OpenCode pour :
   - Déployer les services Azure (Storage, Translator F0, Functions)
   - Fournir les informations de connexion (noms, clés, URLs) sans stocker de credentials
   - Cloner le repo `trad-bot-src` pour les instructions spécifiques au Bot Traducteur
5. **Génère un rapport d'intervention** simple pour le ticketing (groupe de ressources créé, services déployés, etc.)

### Key Features

- ✓ **Installation tout-en-un** : Un seul `.exe` installe tout l'environnement nécessaire
- ✓ **Gestion automatique des exclusions Defender** : Script PowerShell pour ASR (Attack Surface Reduction)
- ✓ **Container Docker pré-configuré** : Environnement isolé et reproductible
- ✓ **OpenCode avec Azure Foundry** : Assistant IA conversationnel (pas besoin de compte Anthropic)
- ✓ **Documentation Power Platform intégrée** : Servie via Flask sur navigateur
- ✓ **Déploiement Azure automatisé** : Services créés avec les bons SKU (F0 pour Translator)
- ✓ **Aucun credential stocké** : Sécurité garantie, informations fournies puis oubliées
- ✓ **Rapport d'intervention** : Génération automatique pour le ticketing
- ✓ **Architecture modulaire** : Clone de repo spécifique par bot (extensible à d'autres bots)

### Value Proposition

**Pourquoi c'est mieux qu'une simple procédure documentée ?**

- **Pas d'erreur humaine** : L'outil sélectionne automatiquement les bons SKU et configurations
- **Conversation naturelle** : OpenCode guide via dialogue plutôt qu'un document à suivre
- **Tout intégré** : Pas besoin de chercher des outils, installer Azure CLI, trouver la documentation
- **Standardisation garantie** : Chaque déploiement suit exactement le même processus
- **Traçabilité** : Rapport automatique pour le ticketing
- **Sécurisé** : Aucun credential stocké contrairement à des scripts

---

## Business Objectives

### Goals

1. **Standardiser les déploiements** : Garantir que chaque déploiement du Bot Traducteur suit exactement la même procédure avec les mêmes configurations
2. **Satisfaction des techniciens** : Fournir un outil qui leur évite d'apprendre Azure en profondeur et leur permet de rester dans leur zone de confort
3. **Tranquillité d'installation sur Azure** : Éliminer le stress lié aux erreurs potentielles (mauvais SKU, mauvaise config) et garantir la qualité

### Success Metrics

- **100% des déploiements standardisés** : Même méthode, mêmes SKU (F0 pour Translator), même architecture
- **Feedback positif des 2 techniciens** : Satisfaction utilisateur, préférence pour l'outil vs formation Azure
- **Zéro incident lié à une mauvaise configuration Azure** : Pas d'erreur de SKU, pas de mauvais service, pas de problème de facturation

### Business Value

- **Temps libéré pour le créateur** : Peut se concentrer sur d'autres projets sans être sollicité pour chaque déploiement
- **Qualité garantie des déploiements** : Reproductibilité à 100%, confiance client maintenue
- **Base scalable pour le futur** : Architecture extensible à d'autres bots sans refaire le travail de formation

---

## Scope

### In Scope

- ✓ **Installeur Windows (.exe)** avec gestion des exclusions Defender ASR via PowerShell
- ✓ **Container Docker pré-configuré** avec OpenCode, Azure CLI, et serveur Flask
- ✓ **OpenCode connecté à Azure Foundry** (modèle IA payé par la société)
- ✓ **Déploiement automatisé Azure pour Bot Traducteur** :
  - Azure Storage Account
  - Azure Translator (SKU F0 - gratuit)
  - Azure Functions (backend Python)
- ✓ **Documentation Power Platform** servie via Flask (http://localhost:5545)
- ✓ **Génération de rapport d'intervention** (pour ticketing)
- ✓ **Clone du repo `trad-bot-src`** pour instructions spécifiques au Bot Traducteur
- ✓ **Support multi-comptes** : Compte délégué ou compte admin créé chez le client
- ✓ **Gestion des cas MFA** : Documentation pour création d'emplacements nommés (named locations)

### Out of Scope

- ✗ **Déploiement d'autres bots** (prévu pour versions futures si succès)
- ✗ **Interface graphique (GUI)** pour la configuration (OpenCode conversationnel suffit)
- ✗ **Signature de certificat** pour l'exécutable (coût non justifié pour 2-3 utilisateurs)
- ✗ **Support multi-OS** (Mac/Linux) - Windows uniquement
- ✗ **Automatisation complète Power Platform** (les techs sont déjà autonomes avec documentation)
- ✗ **Stockage de credentials** (volontairement exclu pour sécurité)

### Future Considerations

- **Extension à d'autres bots** : Si le déploiement du Bot Traducteur est un succès, utiliser la même architecture pour d'autres bots (repos séparés)
- **Règle Intune centralisée** : Demander au SI une règle Intune pour gérer les exclusions Defender ASR de manière centralisée
- **Mise à jour automatique Azure CLI** : Mécanisme de maintenance du container pour suivre les MAJ fréquentes
- **Support multi-tenants** : Optimisations pour gérer plusieurs clients simultanément

---

## Key Stakeholders

- **Eric (Développeur/Architecte)** - High influence. Créateur et mainteneur de la solution, expert Azure et Claude Code
- **Les 2 techniciens Modern Workplace** - Medium influence. Utilisateurs principaux, consultants Power Platform chez les clients
- **Les clients finaux** - Low influence. Bénéficient de déploiements fiables et standardisés du Bot Traducteur
- **Service Informatique (SI)** - Medium influence. Potentiel support pour règles Intune centralisées

---

## Constraints and Assumptions

### Constraints

- **Budget** : Utilisation de SKU gratuits quand possible (F0 pour Translator = 2,5M caractères gratuits)
- **Coût IA** : Modèle OpenCode via Azure Foundry payé par la société (pas de compte Anthropic individuel)
- **Technique** : Windows uniquement, pas de support Mac/Linux
- **Sécurité Defender** : Pas de certificat de signature (coût non justifié pour 2-3 users) → Nécessite script PowerShell pour exclusions ASR
- **Environnement client** : Connexions Azure potentiellement bloquées par MFA (nécessite création d'emplacement nommé)
- **Multi-comptes** : Doit gérer compte délégué OU compte admin créé chez le client
- **Maintenance** : Azure CLI publie des MAJ fréquentes → nécessite maintenance du container

### Assumptions

- Les techniciens ont des **droits administrateur sur leurs postes** (pour installer l'exe et exécuter script PowerShell)
- Les techniciens ont accès à **Azure avec permissions nécessaires** (via compte délégué ou compte admin créé)
- Les clients ont des **environnements Azure et Power Platform configurés**
- **Connexion internet stable** disponible pour Docker, Azure CLI, et OpenCode
- Les techniciens savent **gérer les connexions Azure/Entra ID** (multi-comptes)
- Les techniciens savent **créer et supprimer des règles d'exclusion MFA** (emplacements nommés avec IP)
- Les techniciens ont les **permissions pour modifier les politiques de sécurité Entra ID** (gestion MFA temporaire)

---

## Success Criteria

- ✓ **Les 2 techniciens peuvent déployer le Bot Traducteur de manière autonome** sans intervention d'Eric
- ✓ **Zéro incident lié à un mauvais SKU ou une mauvaise configuration Azure** (F0 pour Translator toujours sélectionné)
- ✓ **Tous les déploiements suivent exactement la même procédure standardisée** (reproductibilité 100%)
- ✓ **Les techniciens sont satisfaits et préfèrent cet outil à une formation Azure** (feedback positif)
- ✓ **Eric n'intervient plus dans les déploiements** (sauf support exceptionnel ou maintenance de l'outil)

---

## Timeline and Milestones

### Target Launch

**Finaliser le projet avant le prochain déploiement client** (date exacte à confirmer selon les opportunités clients)

### Key Milestones

- ✓ **Prototype fonctionnel** (Fait) : Container Docker, OpenCode, documentation, déploiement Azure automatisé
- ✓ **Test pilote chez un client** (Fait) : Déploiement réalisé mais Eric a dû intervenir pour terminer
- 🔄 **Finalisation pour autonomie totale** (En cours) : Corrections basées sur le test pilote, documentation complète
- ⏳ **Premier déploiement 100% autonome** (Prochain jalon) : Techniciens déploient sans intervention d'Eric
- ⏳ **Validation et feedback** : Retour des techniciens, ajustements si nécessaire
- ⏳ **Extension à d'autres bots** (Si succès) : Réplication de l'architecture pour autres cas d'usage

---

## Risks and Mitigation

### Risque 1 : ASR/Defender bloque l'exécutable non-signé

- **Probabilité :** Medium
- **Impact :** High (bloque l'installation complète)
- **Mitigation :**
  - Script PowerShell ciblé pour créer exclusion ASR spécifiquement pour l'application
  - Documentation claire pour les techniciens
  - Option : Demander au SI une règle Intune centralisée pour les 2-3 utilisateurs
  - Justification : Certificat de signature code trop coûteux pour ce nombre d'utilisateurs

### Risque 2 : Azure CLI nécessite maintenance fréquente

- **Probabilité :** High
- **Impact :** Medium (commandes obsolètes, nouvelles fonctionnalités manquantes)
- **Mitigation :**
  - Processus de mise à jour régulier du container Docker
  - Versionning du container pour rollback si nécessaire
  - Monitoring des breaking changes Azure CLI via release notes

### Risque 3 : Techniciens bloquent sur la gestion MFA/connexions Azure

- **Probabilité :** Medium
- **Impact :** Medium (déploiement retardé, intervention d'Eric nécessaire)
- **Mitigation :**
  - Documentation détaillée sur la création d'emplacements nommés (named locations)
  - Guide pour suspendre/réactiver MFA avec règle d'exclusion IP
  - Support disponible (Eric) pendant les premiers déploiements
  - Assumption : Les techniciens ont les compétences Entra ID nécessaires

### Risque 4 : Complexité croissante avec plusieurs bots à déployer

- **Probabilité :** Low (c'est l'objectif futur !)
- **Impact :** Medium (maintenance de plusieurs repos, configurations différentes)
- **Mitigation :**
  - Architecture modulaire : un repo par bot (comme `trad-bot-src`)
  - Container générique qui clone le repo spécifique au bot
  - Documentation standardisée pour chaque nouveau bot
  - Le fait que Azure ne soit plus un problème facilite l'extension

### Risque 5 : Échec du test pilote (technicien ne peut pas finaliser seul)

- **Probabilité :** Medium (déjà observé lors du premier test)
- **Impact :** High (remet en question l'autonomie)
- **Mitigation :**
  - Analyser les points de blocage du test pilote
  - Améliorer OpenCode avec des instructions plus détaillées
  - Enrichir la documentation des cas edge (MFA, multi-comptes)
  - Prévoir une phase d'accompagnement sur les 2-3 premiers déploiements

---

## Next Steps

1. **Finaliser les corrections post-test pilote** → Analyser pourquoi Eric a dû intervenir
2. **Créer le PRD (Product Requirements Document)** → `/prd` pour documenter toutes les exigences techniques
3. **Définir l'architecture système** → `/architecture` pour formaliser l'architecture Docker/OpenCode/Azure
4. **Sprint planning** → `/sprint-planning` pour découper le travail en 5-15 stories
5. **Premier déploiement 100% autonome** → Valider que les techniciens peuvent réussir sans intervention

---

**This document was created using BMAD Method v6 - Phase 1 (Analysis)**

*To continue: Run `/workflow-status` to see your progress and next recommended workflow.*
