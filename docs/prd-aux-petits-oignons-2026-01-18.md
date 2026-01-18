# Product Requirements Document: Aux Petits Oignons

**Date:** 2026-01-18
**Author:** Eric
**Version:** 1.0
**Project Type:** Deployment Automation Tool
**Project Level:** 2 (Medium - 5-15 stories)
**Status:** Draft

---

## Document Overview

This Product Requirements Document (PRD) defines the functional and non-functional requirements for Aux Petits Oignons. It serves as the source of truth for what will be built and provides traceability from requirements through implementation.

**Related Documents:**
- Product Brief: `docs/product-brief-aux-petits-oignons-2026-01-18.md`

---

## Executive Summary

Aux Petits Oignons est une application de déploiement automatisé qui permet aux techniciens non-familiers avec Azure de déployer des bots Copilot Studio avec leurs services Azure associés, sans erreur. Elle utilise un container Docker avec OpenCode (connecté à Azure Foundry) pour guider les techniciens à travers le déploiement Azure complexe, tout en affichant une documentation pour la partie Power Platform qu'ils maîtrisent déjà. L'objectif est de déléguer des déploiements testés à 100% tout en garantissant la qualité "aux petits oignons", avec une extension prévue vers d'autres bots si le succès est au rendez-vous.

---

## Product Goals

### Business Objectives

1. **Standardiser les déploiements** : Garantir que chaque déploiement du Bot Traducteur suit exactement la même procédure avec les mêmes configurations
2. **Satisfaction des techniciens** : Fournir un outil qui leur évite d'apprendre Azure en profondeur et leur permet de rester dans leur zone de confort
3. **Tranquillité d'installation sur Azure** : Éliminer le stress lié aux erreurs potentielles (mauvais SKU, mauvaise config) et garantir la qualité

### Success Metrics

- **100% des déploiements standardisés** : Même méthode, mêmes SKU (F0 pour Translator), même architecture
- **Feedback positif des 2 techniciens** : Satisfaction utilisateur, préférence pour l'outil vs formation Azure
- **Zéro incident lié à une mauvaise configuration Azure** : Pas d'erreur de SKU, pas de mauvais service, pas de problème de facturation

---

## Functional Requirements

Functional Requirements (FRs) define **what** the system does - specific features and behaviors.

Each requirement includes:
- **ID**: Unique identifier (FR-001, FR-002, etc.)
- **Priority**: Must Have / Should Have / Could Have (MoSCoW)
- **Description**: What the system should do
- **Acceptance Criteria**: How to verify it's complete

---

### Zone 1: Installation & Setup

### FR-001: Installation via exécutable Windows

**Priority:** Must Have

**Description:**
Le système doit fournir un installeur exécutable (.exe) qui installe l'environnement complet (Docker, OpenCode, documentation) sur Windows.

**Acceptance Criteria:**
- [ ] L'exe s'exécute sur Windows 10/11
- [ ] L'installation ne nécessite pas d'intervention manuelle pour Docker
- [ ] L'exe crée l'arborescence nécessaire et configure les composants
- [ ] Message de succès clair à la fin de l'installation

**Dependencies:** Aucune

---

### FR-002: Gestion automatique exclusions Defender ASR

**Priority:** Must Have

**Description:**
Le système doit fournir un script PowerShell pour créer les exclusions Defender ASR nécessaires au fonctionnement de l'exe non-signé.

**Acceptance Criteria:**
- [ ] Script PowerShell exécutable en mode administrateur
- [ ] Exclusions ciblées uniquement sur l'application (pas d'exclusions globales)
- [ ] Documentation claire pour le technicien sur comment exécuter le script
- [ ] Vérification que l'exclusion a été créée avec succès

**Dependencies:** FR-001

---

### FR-003: Lancement automatique du container Docker

**Priority:** Must Have

**Description:**
Le système doit lancer automatiquement le container Docker pré-configuré au démarrage de l'application (via start.bat).

**Acceptance Criteria:**
- [ ] Container démarre sans intervention manuelle
- [ ] Vérification que Docker Desktop est installé et démarré
- [ ] Message d'erreur clair si Docker n'est pas disponible
- [ ] Container prêt à l'emploi en < 2 minutes

**Dependencies:** FR-001

---

### FR-004: Container Docker pré-configuré

**Priority:** Must Have

**Description:**
Le container Docker doit inclure OpenCode (connecté Azure Foundry), Azure CLI, et serveur Flask pré-configurés.

**Acceptance Criteria:**
- [ ] Container basé sur Ubuntu 24.04
- [ ] OpenCode configuré avec API key Azure Foundry
- [ ] Azure CLI version récente installée
- [ ] Flask installé et prêt à servir la documentation
- [ ] Toutes les dépendances Python installées

**Dependencies:** FR-003

---

### FR-005: Ouverture automatique terminal + navigateur

**Priority:** Must Have

**Description:**
Au démarrage du container, le système doit automatiquement ouvrir un terminal avec OpenCode et un navigateur sur localhost:5545.

**Acceptance Criteria:**
- [ ] Terminal s'ouvre avec session OpenCode active
- [ ] Navigateur s'ouvre sur http://localhost:5545
- [ ] Les deux se lancent sans intervention du technicien
- [ ] Feedback visuel que tout est prêt

**Dependencies:** FR-004

---

### Zone 2: Déploiement Azure Automatisé

### FR-006: Déploiement Azure Storage Account

**Priority:** Must Have

**Description:**
OpenCode doit guider le technicien pour créer un Azure Storage Account avec les bonnes configurations.

**Acceptance Criteria:**
- [ ] Storage Account créé avec nom unique
- [ ] Type de stockage approprié (Standard LRS ou similaire)
- [ ] Container blob créé pour les fichiers de traduction
- [ ] Clés d'accès fournies au technicien (sans stockage)
- [ ] Vérification que le Storage Account est opérationnel

**Dependencies:** FR-013

---

### FR-007: Déploiement Azure Translator (SKU F0)

**Priority:** Must Have

**Description:**
OpenCode doit créer une ressource Azure Translator avec SKU F0 (gratuit) exclusivement, sans possibilité d'erreur.

**Acceptance Criteria:**
- [ ] Translator créé avec SKU F0 (gratuit jusqu'à 2,5M caractères)
- [ ] Aucune possibilité de sélectionner S0 ou autre SKU payant
- [ ] Endpoint et clé fournis au technicien
- [ ] Région correctement configurée
- [ ] Vérification que le service est actif

**Dependencies:** FR-013

---

### FR-008: Déploiement Azure Functions (backend Python)

**Priority:** Must Have

**Description:**
OpenCode doit déployer l'application Azure Functions (backend Python) avec toutes les fonctions nécessaires au Bot Traducteur.

**Acceptance Criteria:**
- [ ] Function App créée avec runtime Python
- [ ] Toutes les fonctions déployées (start_translation, check_status, get_result, health, languages, formats)
- [ ] Variables d'environnement configurées correctement
- [ ] URL de la Function App fournie au technicien
- [ ] Test de santé réussi (endpoint /api/health)

**Dependencies:** FR-006, FR-007, FR-013

---

### FR-009: Support multi-comptes Azure

**Priority:** Must Have

**Description:**
Le système doit permettre au technicien de se connecter avec un compte délégué OU un compte admin créé chez le client.

**Acceptance Criteria:**
- [ ] Azure CLI peut gérer plusieurs comptes simultanément
- [ ] Processus de connexion guidé par OpenCode
- [ ] Vérification des permissions nécessaires avant déploiement
- [ ] Message clair si permissions insuffisantes
- [ ] Possibilité de changer de compte en cas d'erreur

**Dependencies:** FR-004

---

### FR-010: Gestion des cas MFA

**Priority:** Should Have

**Description:**
Le système doit fournir de la documentation/guidance pour gérer les blocages MFA (création d'emplacements nommés).

**Acceptance Criteria:**
- [ ] Documentation claire sur la création d'emplacements nommés (named locations)
- [ ] Guide pour suspendre/réactiver MFA temporairement
- [ ] OpenCode peut guider le technicien sur cette procédure
- [ ] Liens vers documentation Microsoft si nécessaire

**Dependencies:** FR-013

---

### Zone 3: Documentation & Guidance

### FR-011: Serveur de documentation Flask

**Priority:** Must Have

**Description:**
Le système doit servir la documentation Power Platform via Flask sur localhost:5545.

**Acceptance Criteria:**
- [ ] Serveur Flask démarre automatiquement avec le container
- [ ] Documentation accessible sur http://localhost:5545/procedure
- [ ] Documentation formatée et lisible (HTML/Markdown)
- [ ] Navigation claire dans la documentation
- [ ] Temps de chargement < 2 secondes

**Dependencies:** FR-004

---

### FR-012: Clone automatique repo trad-bot-src

**Priority:** Must Have

**Description:**
Le container doit cloner automatiquement le repo trad-bot-src pour accéder aux instructions spécifiques au Bot Traducteur.

**Acceptance Criteria:**
- [ ] Repo cloné au démarrage du container (ou disponible localement)
- [ ] Emplacement accessible par OpenCode
- [ ] Vérification que le clone a réussi
- [ ] Gestion d'erreur si repo inaccessible
- [ ] Documentation synchronisée avec la dernière version

**Dependencies:** FR-004

---

### FR-013: Guidance conversationnelle OpenCode

**Priority:** Must Have

**Description:**
OpenCode doit guider le technicien via conversation naturelle pour toutes les étapes du déploiement Azure.

**Acceptance Criteria:**
- [ ] OpenCode explique chaque étape clairement en français
- [ ] Instructions adaptées au niveau de compétence (non-expert Azure)
- [ ] Détection et explication des erreurs potentielles
- [ ] Pas de stockage de credentials
- [ ] Confirmation avant chaque action critique
- [ ] Feedback positif quand une étape réussit

**Dependencies:** FR-004

---

### Zone 4: Reporting

### FR-014: Génération rapport d'intervention

**Priority:** Must Have

**Description:**
À la fin du déploiement, le système doit générer un rapport d'intervention simple pour le ticketing.

**Acceptance Criteria:**
- [ ] Rapport contient: nom client, groupe de ressources, services déployés, URLs/endpoints, date/heure
- [ ] Format facile à copier-coller dans un ticket
- [ ] Pas d'informations sensibles (credentials) dans le rapport
- [ ] Rapport sauvegardé localement avec timestamp
- [ ] Possibilité de regénérer le rapport si besoin

**Dependencies:** FR-006, FR-007, FR-008

---

## Non-Functional Requirements

Non-Functional Requirements (NFRs) define **how** the system performs - quality attributes and constraints.

---

### NFR-001: Performance - Temps de démarrage

**Priority:** Should Have

**Description:**
Le container Docker doit démarrer et être opérationnel en moins de 2 minutes sur une machine standard (8GB RAM, SSD).

**Acceptance Criteria:**
- [ ] Container démarre en < 2 minutes (de `docker-compose up` à OpenCode prêt)
- [ ] Flask serveur accessible en < 30 secondes après démarrage container
- [ ] Terminal OpenCode opérationnel en < 1 minute

**Rationale:**
Expérience utilisateur fluide pour les techniciens, pas d'attente frustrante au démarrage.

---

### NFR-002: Performance - Temps de déploiement Azure

**Priority:** Should Have

**Description:**
Le déploiement complet des services Azure (Storage + Translator + Functions) doit s'effectuer en moins de 15 minutes (hors téléchargements réseau).

**Acceptance Criteria:**
- [ ] Déploiement complet en < 15 minutes dans 90% des cas
- [ ] Feedback de progression fourni à chaque étape
- [ ] Pas de timeout Azure CLI pour les opérations standards

**Rationale:**
Permettre aux techniciens de compléter un déploiement client dans un créneau horaire raisonnable.

---

### NFR-003: Security - Aucun stockage de credentials

**Priority:** Must Have

**Description:**
Le système ne doit JAMAIS stocker de credentials (clés Azure, tokens, mots de passe) de manière persistante, ni en mémoire au-delà de l'usage immédiat, ni sur disque.

**Acceptance Criteria:**
- [ ] Aucun fichier .env ou config contenant des credentials
- [ ] Credentials fournis au technicien via terminal uniquement
- [ ] Pas de logs contenant des informations sensibles
- [ ] Vérification par scan de sécurité qu'aucun credential n'est persisté

**Rationale:**
Sécurité critique - éviter toute exposition de credentials clients. Conformité avec les bonnes pratiques de sécurité.

---

### NFR-004: Security - Exclusions Defender ciblées

**Priority:** Must Have

**Description:**
Les exclusions Defender ASR doivent être strictement ciblées sur l'exécutable de l'application uniquement, pas d'exclusions globales.

**Acceptance Criteria:**
- [ ] Script PowerShell crée exclusion uniquement pour le chemin spécifique de l'exe
- [ ] Aucune exclusion de dossiers système (C:\, Program Files, etc.)
- [ ] Documentation justifiant pourquoi l'exclusion est nécessaire

**Rationale:**
Minimiser la surface d'attaque - ne pas compromettre la sécurité globale du poste pour le déploiement.

---

### NFR-005: Reliability - Gestion d'erreurs Azure CLI

**Priority:** Must Have

**Description:**
Le système doit détecter et gérer gracieusement les erreurs Azure CLI (permissions insuffisantes, timeouts, services indisponibles).

**Acceptance Criteria:**
- [ ] Toute erreur Azure CLI est capturée et interprétée
- [ ] Message d'erreur compréhensible fourni au technicien (pas de stack trace brute)
- [ ] Suggestion d'action corrective pour les erreurs communes
- [ ] Possibilité de retry pour les erreurs temporaires (timeout, réseau)

**Rationale:**
Les techniciens ne sont pas experts Azure - ils ont besoin de guidance claire en cas d'erreur, pas de messages techniques incompréhensibles.

---

### NFR-006: Usability - Interface conversationnelle simple

**Priority:** Must Have

**Description:**
OpenCode doit communiquer dans un langage simple, adapté à des non-experts Azure, sans jargon technique excessif.

**Acceptance Criteria:**
- [ ] Instructions en français clair et compréhensible
- [ ] Pas de termes techniques Azure sans explication
- [ ] Confirmation à chaque étape critique
- [ ] Feedback positif quand une étape réussit

**Rationale:**
Les techniciens Modern Workplace ne sont pas des experts Azure - le langage doit être accessible et rassurant.

---

### NFR-007: Maintainability - Mises à jour Azure CLI

**Priority:** Should Have

**Description:**
Le container doit permettre des mises à jour régulières d'Azure CLI pour suivre les évolutions de l'API Azure.

**Acceptance Criteria:**
- [ ] Processus documenté pour mettre à jour Azure CLI dans le container
- [ ] Versionning du container (tags Docker) pour rollback si nécessaire
- [ ] Tests de compatibilité après mise à jour Azure CLI

**Rationale:**
Azure CLI publie des MAJ fréquentes - nécessité de maintenir la compatibilité sans casser les déploiements existants.

---

### NFR-008: Compatibility - Environnement Windows

**Priority:** Must Have

**Description:**
L'application doit fonctionner sur Windows 10 (version 21H2+) et Windows 11 avec Docker Desktop installé.

**Acceptance Criteria:**
- [ ] Compatible Windows 10 version 21H2 et supérieur
- [ ] Compatible Windows 11 toutes versions
- [ ] Nécessite Docker Desktop 4.x ou supérieur
- [ ] Vérification des prérequis au démarrage (Docker installé et démarré)

**Rationale:**
Environnement standard des techniciens Modern Workplace - pas de support Mac/Linux pour limiter la complexité.

---

### NFR-009: Compatibility - Navigateurs modernes

**Priority:** Must Have

**Description:**
La documentation Flask doit être accessible et bien rendue sur les navigateurs modernes (Chrome, Edge, Firefox).

**Acceptance Criteria:**
- [ ] Compatible Chrome/Edge version courante -2
- [ ] Compatible Firefox version courante -2
- [ ] Rendu HTML/Markdown correct sans artefacts
- [ ] Pas de JavaScript complexe requis

**Rationale:**
Les techniciens utilisent des navigateurs standard d'entreprise - garantir compatibilité maximale.

---

### NFR-010: Usability - Messages d'erreur clairs

**Priority:** Must Have

**Description:**
Tous les messages d'erreur doivent être compréhensibles par un non-expert et suggérer une action corrective.

**Acceptance Criteria:**
- [ ] Format: "Problème: [description simple]. Solution: [action à faire]"
- [ ] Pas de stack traces techniques visibles par défaut
- [ ] Lien vers documentation si applicable
- [ ] Numéro d'erreur pour référence si support nécessaire

**Rationale:**
Autonomie des techniciens - ils doivent pouvoir résoudre les problèmes courants sans contacter Eric.

---

## Epics

Epics are logical groupings of related functionality that will be broken down into user stories during sprint planning (Phase 4).

Each epic maps to multiple functional requirements and will generate 2-10 stories.

---

### EPIC-001: Installation et Configuration Initiale

**Description:**
Permettre au technicien d'installer l'environnement complet "Aux Petits Oignons" sur son poste Windows avec un minimum d'intervention manuelle. Cet épic couvre l'exe, les exclusions Defender, le container Docker, et l'ouverture automatique de l'interface.

**Functional Requirements:**
- FR-001: Installation via exécutable Windows
- FR-002: Gestion automatique exclusions Defender ASR
- FR-003: Lancement automatique du container Docker
- FR-004: Container Docker pré-configuré
- FR-005: Ouverture automatique terminal + navigateur

**Story Count Estimate:** 4-6 stories

**Priority:** Must Have

**Business Value:**
Base fondamentale du projet - sans installation facile, les techniciens ne pourront pas utiliser l'outil. Première impression critique pour l'adoption.

**Success Criteria:**
- Installation complète en < 10 minutes
- Aucune intervention manuelle sauf exécution du script Defender
- Container démarre automatiquement au lancement

---

### EPIC-002: Déploiement Azure Automatisé

**Description:**
Guider le technicien à travers le déploiement complet des services Azure (Storage, Translator F0, Functions) via OpenCode, avec gestion des cas complexes (multi-comptes, MFA). Cet épic garantit que les déploiements sont standardisés et sans erreur de configuration.

**Functional Requirements:**
- FR-006: Déploiement Azure Storage Account
- FR-007: Déploiement Azure Translator (SKU F0)
- FR-008: Déploiement Azure Functions (backend Python)
- FR-009: Support multi-comptes Azure
- FR-010: Gestion des cas MFA

**Story Count Estimate:** 5-7 stories

**Priority:** Must Have

**Business Value:**
Cœur du projet - automatisation Azure qui élimine les erreurs coûteuses (mauvais SKU) et permet la délégation. Valeur business maximale.

**Success Criteria:**
- 100% des déploiements utilisent SKU F0 pour Translator
- Zéro erreur de configuration Azure
- Techniciens autonomes même avec MFA/multi-comptes

---

### EPIC-003: Documentation et Interface Utilisateur

**Description:**
Fournir une documentation Power Platform accessible via Flask et une guidance conversationnelle via OpenCode qui permet aux techniciens de comprendre chaque étape et de rester autonomes. Cet épic garantit que les techniciens ont toutes les informations nécessaires pour réussir.

**Functional Requirements:**
- FR-011: Serveur de documentation Flask
- FR-012: Clone automatique repo trad-bot-src
- FR-013: Guidance conversationnelle OpenCode

**Story Count Estimate:** 3-4 stories

**Priority:** Must Have

**Business Value:**
Différenciateur clé vs une simple procédure écrite - l'assistance IA et la documentation intégrée rendent les techniciens autonomes et confiants.

**Success Criteria:**
- Documentation accessible instantanément (localhost:5545)
- OpenCode répond clairement aux questions des techniciens
- Zéro appel à Eric pour questions documentation

---

### EPIC-004: Reporting et Traçabilité

**Description:**
Générer automatiquement un rapport d'intervention formaté pour le ticketing, permettant la traçabilité des déploiements et facilitant le support post-déploiement. Cet épic garantit que chaque déploiement est documenté pour audit et support.

**Functional Requirements:**
- FR-014: Génération rapport d'intervention

**Story Count Estimate:** 2-3 stories

**Priority:** Must Have

**Business Value:**
Traçabilité essentielle pour les déploiements clients - permet audit, support, et facturation. Complète le cycle de déploiement.

**Success Criteria:**
- Rapport généré automatiquement à chaque déploiement
- Format facile à copier-coller dans ticket
- Contient toutes les informations nécessaires (ressources, URLs, date)

---

## User Stories (High-Level)

User stories follow the format: "As a [user type], I want [goal] so that [benefit]."

These are preliminary stories. Detailed stories will be created in Phase 4 (Implementation).

---

Detailed user stories will be created during sprint planning (Phase 4).

---

## User Personas

### Persona 1: Technicien Modern Workplace (Primaire)

**Nom:** Jean (représentatif des 2 techniciens)

**Rôle:** Technicien Modern Workplace / Consultant Power Platform

**Compétences:**
- Expert Power Platform (Copilot Studio, Power Apps, Power Automate)
- Autonome sur le déploiement Power Platform
- Non-familier avec Azure (Infrastructure as a Service)
- Capable de gérer les connexions Entra ID et règles MFA

**Contexte:** Travaille chez des clients avec des comptes délégués ou crée des comptes admin temporaires

**Attitude:** Motivé pour Power Platform, réticent à apprendre Azure en profondeur (pas son cœur de métier)

**Besoins:**
- Déployer Azure sans expertise Azure
- Éviter les erreurs coûteuses
- Documentation claire pour Power Platform
- Rester autonome après le déploiement Azure

**Frustrations:**
- Formations Azure trop complexes et hors périmètre
- Risque de faire des erreurs de configuration (SKU, services)
- Dépendance sur Eric pour chaque déploiement

---

### Persona 2: Eric (Mainteneur/Support)

**Rôle:** Développeur/Architecte, créateur de la solution

**Compétences:**
- Expert Azure et Claude Code
- Connaissance approfondie des bots Copilot Studio
- Déploiements testés à 100%

**Besoins:**
- Déléguer les déploiements aux techniciens
- Maintenir la qualité "aux petits oignons"
- Se libérer du temps pour d'autres projets
- Support exceptionnel uniquement

**Frustrations actuelles:**
- Goulot d'étranglement - seul capable de faire les déploiements
- Impossible de transférer expertise via formations traditionnelles
- Risque de non-scalabilité

---

### Persona 3: Client final (Secondaire)

**Rôle:** Organisation cliente utilisant le Bot Traducteur

**Besoins:**
- Déploiement fiable et sans erreur
- Coûts Azure prévisibles (SKU F0 gratuit)
- Service opérationnel rapidement

**Attentes:**
- Transparence sur les services déployés
- Pas de surprise sur la facturation Azure
- Support disponible si problème

---

## User Flows

### Flow 1: Installation initiale de l'outil

**Acteur:** Technicien Modern Workplace

**Prérequis:** Docker Desktop installé sur le poste Windows

**Étapes:**
1. Technicien télécharge l'exe "Aux Petits Oignons"
2. Exécute le script PowerShell pour exclusions Defender ASR (mode administrateur)
3. Lance l'exe → Container Docker démarre automatiquement
4. Terminal OpenCode s'ouvre automatiquement
5. Navigateur s'ouvre automatiquement sur http://localhost:5545
6. Technicien voit la documentation et OpenCode prêt
7. Technicien prêt à déployer

**Résultat:** Environnement opérationnel en < 10 minutes

---

### Flow 2: Déploiement complet Bot Traducteur chez un client

**Acteur:** Technicien Modern Workplace

**Prérequis:** Outil installé, accès Azure client (compte délégué ou admin créé)

**Étapes:**

**Phase Azure (guidée par OpenCode):**
1. Technicien lance OpenCode et dit "nouveau déploiement Bot Traducteur"
2. OpenCode demande connexion Azure → Technicien se connecte (compte délégué ou admin)
3. OpenCode vérifie les permissions → OK ou message d'erreur clair
4. OpenCode guide création Azure Storage Account:
   - Nom unique généré
   - Type Standard LRS
   - Container blob créé
   - Clés fournies au technicien (copier-coller)
5. OpenCode guide création Azure Translator:
   - **SKU F0 imposé** (pas d'erreur possible)
   - Région sélectionnée
   - Endpoint et clé fournis au technicien
6. OpenCode guide déploiement Azure Functions:
   - Runtime Python configuré
   - Toutes les fonctions déployées
   - Variables d'environnement configurées (Storage, Translator)
   - URL Function App fournie au technicien
   - Test santé effectué
7. OpenCode génère rapport d'intervention:
   - Groupe de ressources
   - Services déployés (Storage, Translator F0, Functions)
   - URLs/endpoints
   - Date/heure
8. Technicien copie rapport dans ticket client

**Phase Power Platform (autonome avec doc):**
9. Technicien consulte documentation sur http://localhost:5545/procedure
10. Technicien suit les étapes Power Platform (import solution, configuration connexions, etc.)
11. Déploiement complet terminé

**Résultat:** Bot Traducteur opérationnel, déploiement tracé, technicien autonome

---

### Flow 3: Gestion cas MFA bloquant (Edge Case)

**Acteur:** Technicien Modern Workplace

**Problème:** MFA bloque l'authentification Azure CLI

**Étapes:**
1. Technicien tente connexion Azure CLI → MFA bloque
2. OpenCode détecte l'échec et explique le problème MFA
3. OpenCode guide le technicien:
   - Créer un emplacement nommé (named location) avec son IP
   - Créer règle d'exclusion MFA pour cet emplacement
   - Réessayer la connexion
4. Connexion Azure CLI réussie
5. Déploiement continue normalement
6. (Rappel: supprimer l'exclusion MFA après déploiement)

**Résultat:** Technicien autonome même en cas de blocage MFA

---

## Dependencies

### Internal Dependencies

- **Azure Foundry avec modèle IA configuré** : OpenCode nécessite accès à un modèle IA via Azure Foundry (payé par la société)
- **Compte OpenCode configuré** : API key configurée dans le container
- **Repo `trad-bot-src` accessible** : Contient les instructions spécifiques et code source du Bot Traducteur

### External Dependencies

- **Docker Desktop installé** : Prérequis sur le poste du technicien (version 4.x+)
- **Azure subscription avec permissions appropriées** : Le technicien doit avoir accès (compte délégué ou admin créé)
- **Connexion internet stable** : Pour Docker, Azure CLI, OpenCode, et clone de repo
- **Windows 10/11** : OS supporté uniquement

---

## Assumptions

- Les techniciens ont des **droits administrateur sur leurs postes** (pour installer l'exe et exécuter script PowerShell)
- Les techniciens ont accès à **Azure avec permissions nécessaires** (via compte délégué ou compte admin créé)
- Les clients ont des **environnements Azure et Power Platform configurés**
- **Connexion internet stable** disponible pour Docker, Azure CLI, et OpenCode
- Les techniciens savent **gérer les connexions Azure/Entra ID** (multi-comptes)
- Les techniciens savent **créer et supprimer des règles d'exclusion MFA** (emplacements nommés avec IP)
- Les techniciens ont les **permissions pour modifier les politiques de sécurité Entra ID** (gestion MFA temporaire)

---

## Out of Scope

Les éléments suivants sont **explicitement exclus** de cette version:

- ✗ **Déploiement d'autres bots** (prévu pour versions futures si succès du Bot Traducteur)
- ✗ **Interface graphique (GUI)** pour la configuration (OpenCode conversationnel suffit)
- ✗ **Signature de certificat** pour l'exécutable (coût non justifié pour 2-3 utilisateurs)
- ✗ **Support multi-OS** (Mac/Linux) - Windows uniquement pour limiter complexité
- ✗ **Automatisation complète Power Platform** (les techniciens sont déjà autonomes avec documentation)
- ✗ **Stockage de credentials** (volontairement exclu pour sécurité)
- ✗ **Interface web pour le déploiement** (terminal OpenCode suffit)
- ✗ **Support multi-langues** (français uniquement)
- ✗ **Télémétrie et analytics** (pas de tracking utilisateur)

---

## Open Questions

Les questions suivantes nécessitent des décisions architecturales ou d'implémentation:

### Q1: Processus de mise à jour du container quand Azure CLI change

**Statut:** Non pris en compte actuellement

**Impact:** Haute - Azure CLI publie des MAJ fréquentes, risque d'obsolescence

**Options à considérer:**
- Processus manuel documenté pour rebuild du container
- Script automatique de mise à jour Azure CLI dans container existant
- Versionning du container avec tags Docker pour rollback
- Notification automatique quand nouvelle version Azure CLI disponible

**Décision requise pour:** Phase 3 (Architecture)

---

### Q2: Gestion des erreurs si Docker Desktop n'est pas démarré

**Statut:** Non pris en compte actuellement

**Impact:** Moyenne - Bloque le démarrage de l'application

**Options à considérer:**
- Vérification au lancement de l'exe + message d'erreur clair
- Tentative automatique de démarrage Docker Desktop
- Script de pré-vérification des prérequis
- Fallback mode (mode dégradé sans container?)

**Décision requise pour:** Phase 3 (Architecture)

---

### Q3: Fallback si Azure Foundry est indisponible

**Statut:** Non pris en compte actuellement

**Impact:** Haute - OpenCode devient inutilisable

**Options à considérer:**
- Mode dégradé avec instructions textuelles prédéfinies
- Fallback vers API Anthropic directe (si compte disponible)
- Message d'erreur clair + procédure manuelle de secours
- Cache des instructions les plus communes

**Décision requise pour:** Phase 3 (Architecture)

---

## Approval & Sign-off

### Stakeholders

- **Eric (Développeur/Architecte)** - High influence. Créateur et mainteneur de la solution
- **Les 2 techniciens Modern Workplace** - Medium influence. Utilisateurs principaux
- **Les clients finaux** - Low influence. Bénéficient des déploiements fiables
- **Service Informatique (SI)** - Medium influence. Potentiel support pour règles Intune centralisées

### Approval Status

- [ ] Product Owner (Eric)
- [ ] Engineering Lead
- [ ] Techniciens utilisateurs (feedback après premier déploiement autonome)

---

## Revision History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2026-01-18 | Eric | Initial PRD - 14 FRs, 10 NFRs, 4 Epics |

---

## Next Steps

### Phase 3: Architecture

Run `/architecture` to create system architecture based on these requirements.

The architecture will address:
- All functional requirements (14 FRs)
- All non-functional requirements (10 NFRs)
- Technical stack decisions (Docker, OpenCode, Azure CLI, Flask, Python)
- Data models and APIs
- System components and interactions
- Answers to open questions (Q1, Q2, Q3)

### Phase 4: Sprint Planning

After architecture is complete, run `/sprint-planning` to:
- Break epics into detailed user stories (14-20 stories estimated)
- Estimate story complexity (story points)
- Plan sprint iterations
- Begin implementation

---

**This document was created using BMAD Method v6 - Phase 2 (Planning)**

*To continue: Run `/workflow-status` to see your progress and next recommended workflow.*

---

## Appendix A: Requirements Traceability Matrix

| Epic ID | Epic Name | Functional Requirements | Story Count (Est.) | Priority |
|---------|-----------|-------------------------|-------------------|----------|
| EPIC-001 | Installation et Configuration Initiale | FR-001, FR-002, FR-003, FR-004, FR-005 | 4-6 stories | Must Have |
| EPIC-002 | Déploiement Azure Automatisé | FR-006, FR-007, FR-008, FR-009, FR-010 | 5-7 stories | Must Have |
| EPIC-003 | Documentation et Interface Utilisateur | FR-011, FR-012, FR-013 | 3-4 stories | Must Have |
| EPIC-004 | Reporting et Traçabilité | FR-014 | 2-3 stories | Must Have |

**Total: 4 Epics | 14 FRs | 14-20 Stories (estimated)**

---

## Appendix B: Prioritization Details

### Functional Requirements Breakdown

**Must Have:** 13 FRs
- FR-001: Installation via exécutable Windows
- FR-002: Gestion automatique exclusions Defender ASR
- FR-003: Lancement automatique du container Docker
- FR-004: Container Docker pré-configuré
- FR-005: Ouverture automatique terminal + navigateur
- FR-006: Déploiement Azure Storage Account
- FR-007: Déploiement Azure Translator (SKU F0)
- FR-008: Déploiement Azure Functions (backend Python)
- FR-009: Support multi-comptes Azure
- FR-011: Serveur de documentation Flask
- FR-012: Clone automatique repo trad-bot-src
- FR-013: Guidance conversationnelle OpenCode
- FR-014: Génération rapport d'intervention

**Should Have:** 1 FR
- FR-010: Gestion des cas MFA

**Could Have:** 0 FRs

---

### Non-Functional Requirements Breakdown

**Must Have:** 7 NFRs
- NFR-003: Security - Aucun stockage de credentials
- NFR-004: Security - Exclusions Defender ciblées
- NFR-005: Reliability - Gestion d'erreurs Azure CLI
- NFR-006: Usability - Interface conversationnelle simple
- NFR-008: Compatibility - Environnement Windows
- NFR-009: Compatibility - Navigateurs modernes
- NFR-010: Usability - Messages d'erreur clairs

**Should Have:** 3 NFRs
- NFR-001: Performance - Temps de démarrage
- NFR-002: Performance - Temps de déploiement Azure
- NFR-007: Maintainability - Mises à jour Azure CLI

**Could Have:** 0 NFRs

---

### Priority Distribution

| Priority | FRs | NFRs | Total |
|----------|-----|------|-------|
| Must Have | 13 | 7 | 20 |
| Should Have | 1 | 3 | 4 |
| Could Have | 0 | 0 | 0 |
| **Total** | **14** | **10** | **24** |

**Analysis:**
- 83% des requirements sont "Must Have" - projet bien cadré avec priorisation claire
- Tous les epics sont "Must Have" - scope MVP bien défini
- "Should Have" représente 17% - optimisations de performance et cas edge (MFA, maintenance)
- Aucun "Could Have" - scope strictement limité pour garantir livraison

---

**Validation Checklist:**

✓ Tous les Must-Have FRs couvrent les fonctionnalités critiques
✓ Chaque FR a des critères d'acceptation testables
✓ NFRs couvrent Performance, Security, Reliability, Usability, Maintainability, Compatibility
✓ NFRs sont mesurables (temps < 2min, 100% standardisé, etc.)
✓ Epics regroupent logiquement les FRs
✓ Tous les FRs sont assignés à des epics
✓ Priorités réalistes (pas tout "Must Have" sans raison)
✓ Requirements tracent aux business objectives (standardisation, satisfaction, tranquillité)
✓ Out of scope clairement défini
✓ Open questions identifiées pour l'architecture
