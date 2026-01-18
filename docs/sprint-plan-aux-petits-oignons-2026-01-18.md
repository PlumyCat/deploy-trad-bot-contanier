# Sprint Plan: Aux Petits Oignons

**Date:** 2026-01-18
**Scrum Master:** Eric
**Project Level:** 2 (Medium - 5-15 stories)
**Total Stories:** 18 stories
**Total Points:** 71 story points
**Planned Sprints:** 3 sprints

---

## Executive Summary

Ce plan de sprint détaille l'implémentation complète de "Aux Petits Oignons", un outil de déploiement automatisé pour le Bot Traducteur. Le projet est divisé en 3 sprints de 2 semaines chacun, couvrant 4 epics principaux : Installation & Configuration, Déploiement Azure Automatisé, Documentation & Interface Utilisateur, et Reporting & Traçabilité.

**Key Metrics:**
- Total Stories: 18
- Total Points: 71 story points
- Sprints: 3 sprints de 2 semaines
- Team Capacity: 30 points par sprint
- Utilisation moyenne: 78%
- Target Completion: 6 semaines (~fin février 2026)

---

## Story Inventory

### Infrastructure

#### STORY-000: Setup Environnement de Développement

**Epic:** Infrastructure
**Priority:** Must Have
**Points:** 2

**User Story:**
En tant que développeur
Je veux configurer l'environnement de développement local
Afin de pouvoir développer et tester "Aux Petits Oignons"

**Acceptance Criteria:**
- [ ] Docker Desktop installé et configuré
- [ ] Inno Setup Compiler installé pour créer les .exe
- [ ] Python 3.11+ installé
- [ ] Azure CLI installé pour tests locaux
- [ ] Compte Azure Foundry configuré avec API key
- [ ] Repo trad-bot-src cloné et accessible
- [ ] Structure de fichiers du projet créée

**Technical Notes:**
- Windows 10/11 requis
- Docker Desktop 4.x+
- Inno Setup 6.x pour compiler l'installeur

**Dependencies:** Aucune

---

### EPIC-001: Installation et Configuration Initiale

#### STORY-001: Créer Installeur Windows .exe avec Inno Setup

**Epic:** EPIC-001
**Priority:** Must Have
**Points:** 5

**User Story:**
En tant que technicien Modern Workplace
Je veux exécuter un installeur .exe simple
Afin d'installer "Aux Petits Oignons" sans configuration manuelle

**Acceptance Criteria:**
- [ ] Script Inno Setup (.iss) créé avec toute la configuration
- [ ] Exe compilé et testé sur Windows 10/11
- [ ] Exe copie tous les fichiers nécessaires (scripts, Dockerfile, docker-compose.yml, documentation)
- [ ] Exe crée l'arborescence de dossiers appropriée
- [ ] Message de succès affiché à la fin de l'installation
- [ ] Exe taille < 50MB (sans images Docker)
- [ ] Installation complète en < 2 minutes

**Technical Notes:**
- Utiliser Inno Setup 6.x
- Inclure start.bat, docker-compose.yml, Dockerfile, scripts PowerShell
- Créer structure: C:\ProgramData\AuxPetitsOignons\ ou similaire
- Pas de signature de certificat (accepté pour 2-3 utilisateurs)

**Dependencies:** STORY-000

---

#### STORY-002: Script PowerShell Exclusions Defender ASR

**Epic:** EPIC-001
**Priority:** Must Have
**Points:** 3

**User Story:**
En tant que technicien Modern Workplace
Je veux exécuter un script PowerShell pour créer les exclusions Defender ASR
Afin que l'exe non-signé puisse s'exécuter sans être bloqué

**Acceptance Criteria:**
- [ ] Script PowerShell créé avec exclusions ciblées (pas d'exclusions globales)
- [ ] Script vérifie les droits administrateur avant exécution
- [ ] Exclusion créée uniquement pour le chemin spécifique de l'exe
- [ ] Script confirme que l'exclusion a été créée avec succès
- [ ] Documentation claire fournie au technicien (README ou commentaires)
- [ ] Script testé sur Windows 10/11 avec Defender activé

**Technical Notes:**
- Utiliser cmdlet `Add-MpPreference` ou `Set-MpPreference`
- Cibler le chemin exact de l'exe installé
- Éviter les exclusions de dossiers système
- Inclure message d'erreur clair si échec

**Dependencies:** STORY-001

---

#### STORY-003: Configuration et Build du Container Docker

**Epic:** EPIC-001
**Priority:** Must Have
**Points:** 8

**User Story:**
En tant que développeur
Je veux créer un container Docker pré-configuré
Afin que les techniciens aient OpenCode, Azure CLI et Flask prêts à l'emploi

**Acceptance Criteria:**
- [ ] Dockerfile créé basé sur Ubuntu 24.04
- [ ] OpenCode installé et configuré avec API key Azure Foundry
- [ ] Azure CLI version récente installée
- [ ] Flask + dépendances Python installées
- [ ] Script de démarrage (/app/start.sh) créé
- [ ] docker-compose.yml configuré avec ports et volumes
- [ ] Container build réussi (< 5 minutes)
- [ ] Container démarre en < 2 minutes
- [ ] Taille du container < 2GB

**Technical Notes:**
- Base image: ubuntu:24.04
- Python 3.11+ requis
- OpenCode via pip: `pip install opencode`
- Azure CLI via script officiel Microsoft
- Flask + markdown pour rendu documentation
- Exposer port 5545 pour Flask
- Variables d'environnement pour Azure Foundry API key

**Dependencies:** STORY-000

---

#### STORY-004: Script de Démarrage Automatique (start.bat)

**Epic:** EPIC-001
**Priority:** Must Have
**Points:** 3

**User Story:**
En tant que technicien Modern Workplace
Je veux lancer "Aux Petits Oignons" avec un simple double-clic
Afin que le container Docker démarre automatiquement

**Acceptance Criteria:**
- [ ] start.bat créé et testé
- [ ] Vérification que Docker Desktop est installé et démarré
- [ ] Message d'erreur clair si Docker n'est pas disponible
- [ ] Lancement de `docker-compose up -d`
- [ ] Attente que container soit prêt (health check)
- [ ] Feedback visuel de progression (messages console)
- [ ] Gestion des erreurs Docker (container déjà démarré, port occupé, etc.)

**Technical Notes:**
- Utiliser `docker ps` pour vérifier que Docker Desktop est actif
- Utiliser `docker-compose up -d --wait` pour attendre que container soit prêt
- Messages en français pour les techniciens
- Inclure timeout (max 5 minutes d'attente)

**Dependencies:** STORY-003

---

#### STORY-005: Ouverture Automatique Terminal et Navigateur

**Epic:** EPIC-001
**Priority:** Must Have
**Points:** 2

**User Story:**
En tant que technicien Modern Workplace
Je veux que le terminal OpenCode et le navigateur s'ouvrent automatiquement
Afin de commencer immédiatement sans chercher les URLs

**Acceptance Criteria:**
- [ ] Terminal Windows s'ouvre automatiquement après démarrage container
- [ ] Terminal exécute `docker exec -it trad-bot-opencode opencode` automatiquement
- [ ] Navigateur par défaut s'ouvre sur http://localhost:5545/procedure
- [ ] Les deux actions se produisent sans intervention utilisateur
- [ ] Délai approprié entre démarrage container et ouverture (attendre que Flask soit prêt)
- [ ] Feedback dans start.bat que tout est prêt

**Technical Notes:**
- Utiliser `start cmd /k "docker exec -it trad-bot-opencode opencode"` pour terminal
- Utiliser `start http://localhost:5545/procedure` pour navigateur
- Ajouter `timeout /t 10` pour attendre que Flask démarre
- Tester health check avant ouverture

**Dependencies:** STORY-004

---

### EPIC-002: Déploiement Azure Automatisé

#### STORY-006: Wrapper Python Azure CLI - Déploiement Storage Account

**Epic:** EPIC-002
**Priority:** Must Have
**Points:** 5

**User Story:**
En tant qu'OpenCode
Je veux utiliser un wrapper Python pour déployer Azure Storage Account
Afin de guider le technicien sans erreur de configuration

**Acceptance Criteria:**
- [ ] Module Python `azure_deployer.py` créé
- [ ] Fonction `create_storage_account()` implémentée
- [ ] Storage Account créé avec nom unique (génération automatique)
- [ ] Type Standard_LRS configuré
- [ ] Container blob "translations" créé automatiquement
- [ ] Clés d'accès récupérées et affichées (sans stockage)
- [ ] Gestion d'erreurs Azure CLI (permissions, timeouts, nom déjà pris)
- [ ] Logs sanitizés (aucun credential visible)

**Technical Notes:**
- Utiliser `az storage account create` via subprocess
- Parser JSON output avec `--output json`
- Générer nom unique : `tradbot{random}{timestamp}`
- Vérifier que le nom est disponible avant création
- Implémenter retry logic pour timeouts réseau

**Dependencies:** STORY-003

---

#### STORY-007: Wrapper Python Azure CLI - Déploiement Translator F0

**Epic:** EPIC-002
**Priority:** Must Have (CRITIQUE)
**Points:** 5

**User Story:**
En tant qu'OpenCode
Je veux déployer Azure Translator avec SKU F0 **exclusivement**
Afin d'éviter toute erreur coûteuse (S0 = 35$/mois)

**Acceptance Criteria:**
- [ ] Fonction `create_translator()` implémentée
- [ ] SKU F0 **hardcodé** dans le code (pas de paramètre variable)
- [ ] Impossible de sélectionner S0 ou autre SKU
- [ ] Région francecentral par défaut (ou sélection guidée)
- [ ] Endpoint et clé récupérés et affichés
- [ ] Vérification que le service est actif
- [ ] Tests unitaires vérifiant que seul F0 est utilisé
- [ ] Documentation claire dans le code: "SKU F0 OBLIGATOIRE - NE PAS MODIFIER"

**Technical Notes:**
- Commande: `az cognitiveservices account create --kind TextTranslation --sku F0`
- **CRITIQUE:** Aucun paramètre pour SKU, valeur F0 en dur dans le code
- Ajouter commentaire expliquant pourquoi (éviter S0 à 35$/mois)
- Test d'intégration vérifiant que F0 est bien déployé

**Dependencies:** STORY-003

---

#### STORY-008: Wrapper Python Azure CLI - Déploiement Azure Functions

**Epic:** EPIC-002
**Priority:** Must Have
**Points:** 8

**User Story:**
En tant qu'OpenCode
Je veux déployer l'application Azure Functions complète
Afin que le backend Python soit opérationnel

**Acceptance Criteria:**
- [ ] Fonction `create_function_app()` implémentée
- [ ] Function App créée avec runtime Python 3.11
- [ ] Toutes les fonctions déployées (start_translation, check_status, get_result, health, languages, formats)
- [ ] Variables d'environnement configurées (AZURE_ACCOUNT_NAME, AZURE_ACCOUNT_KEY, TRANSLATOR_KEY, TRANSLATOR_ENDPOINT, TRANSLATOR_REGION)
- [ ] URL Function App fournie au technicien
- [ ] Health check exécuté (`curl /api/health`)
- [ ] Logs de déploiement capturés et sanitizés

**Technical Notes:**
- Utiliser `az functionapp create --runtime python --runtime-version 3.11`
- Déployer depuis dossier `src/` du repo trad-bot-src
- Utiliser `az functionapp config appsettings set` pour variables environnement
- Vérifier que health endpoint répond 200 OK
- Inclure retry si déploiement échoue

**Dependencies:** STORY-006, STORY-007

---

#### STORY-009: Support Multi-comptes Azure dans OpenCode

**Epic:** EPIC-002
**Priority:** Must Have
**Points:** 3

**User Story:**
En tant que technicien Modern Workplace
Je veux pouvoir me connecter avec un compte délégué OU un compte admin créé
Afin de déployer chez différents clients

**Acceptance Criteria:**
- [ ] OpenCode guide le technicien pour `az login`
- [ ] Processus de connexion device flow supporté
- [ ] OpenCode liste les comptes connectés (`az account list`)
- [ ] OpenCode permet de sélectionner le bon compte si plusieurs
- [ ] Vérification des permissions nécessaires (Contributor ou similaire)
- [ ] Message clair si permissions insuffisantes
- [ ] Possibilité de se reconnecter avec un autre compte

**Technical Notes:**
- Azure CLI gère nativement le multi-compte
- Utiliser `az account set --subscription <id>` pour sélectionner
- Vérifier permissions avec `az role assignment list`
- Guidance OpenCode en français pour device flow

**Dependencies:** STORY-003

---

#### STORY-010: Documentation et Guidance MFA dans OpenCode

**Epic:** EPIC-002
**Priority:** Should Have
**Points:** 2

**User Story:**
En tant que technicien Modern Workplace
Je veux savoir comment gérer les blocages MFA
Afin de pouvoir me connecter à Azure CLI même avec MFA activé

**Acceptance Criteria:**
- [ ] Documentation Markdown créée pour gestion MFA
- [ ] Guide étape par étape pour créer emplacements nommés (named locations)
- [ ] Guide pour créer règle d'exclusion MFA temporaire
- [ ] OpenCode peut afficher cette documentation sur demande
- [ ] Liens vers documentation Microsoft officielle
- [ ] Rappel de supprimer l'exclusion MFA après déploiement

**Technical Notes:**
- Documentation dans `docs/guide-mfa.md`
- OpenCode peut lire et afficher ce fichier
- Inclure screenshots si possible
- Référencer Entra ID > Security > Named Locations

**Dependencies:** STORY-013

---

### EPIC-003: Documentation et Interface Utilisateur

#### STORY-011: Serveur Flask pour Documentation Power Platform

**Epic:** EPIC-003
**Priority:** Must Have
**Points:** 5

**User Story:**
En tant que technicien Modern Workplace
Je veux consulter la documentation Power Platform dans mon navigateur
Afin de suivre les étapes post-déploiement Azure

**Acceptance Criteria:**
- [ ] Application Flask créée (`app.py`)
- [ ] Route `/procedure` servant la documentation Power Platform
- [ ] Documentation formatée en HTML depuis Markdown
- [ ] Navigation claire (table des matières, liens internes)
- [ ] Serveur démarre automatiquement sur port 5545
- [ ] Temps de chargement < 2 secondes
- [ ] Compatible Chrome/Edge/Firefox

**Technical Notes:**
- Flask + extension `markdown` pour rendu
- Documentation source: `GUIDE_POWER_PLATFORM_COMPLET.md`
- Template HTML simple et propre
- Pas de JavaScript complexe requis
- Health check endpoint `/health`

**Dependencies:** STORY-003

---

#### STORY-012: Clone Automatique Repo trad-bot-src au Démarrage

**Epic:** EPIC-003
**Priority:** Must Have
**Points:** 2

**User Story:**
En tant que container Docker
Je veux cloner automatiquement le repo trad-bot-src
Afin d'avoir accès aux instructions et code source du Bot Traducteur

**Acceptance Criteria:**
- [ ] Script de démarrage container clone le repo au premier lancement
- [ ] Repo cloné dans `/app/trad-bot-src/`
- [ ] Vérification que le clone a réussi
- [ ] Gestion d'erreur si repo inaccessible (credentials, réseau)
- [ ] Documentation synchronisée avec la dernière version (git pull)
- [ ] Logs indiquant succès ou échec du clone

**Technical Notes:**
- Utiliser `git clone` dans script start.sh
- Vérifier si dossier existe déjà avant clone
- Utiliser `git pull` pour MAJ si déjà cloné
- Gérer cas où repo est privé (credentials SSH/HTTPS)

**Dependencies:** STORY-003

---

#### STORY-013: Configuration OpenCode avec Prompts Conversationnels

**Epic:** EPIC-003
**Priority:** Must Have
**Points:** 3

**User Story:**
En tant que développeur
Je veux configurer OpenCode avec des prompts conversationnels adaptés
Afin que OpenCode guide efficacement les techniciens non-experts Azure

**Acceptance Criteria:**
- [ ] Configuration OpenCode créée (`.opencode/config.yaml` ou similaire)
- [ ] System prompt défini pour le rôle d'assistant déploiement Azure
- [ ] Instructions claires sur le workflow de déploiement
- [ ] Langue française définie par défaut
- [ ] Ton conversationnel, rassurant, pédagogique
- [ ] Références aux FRs et architecture dans les prompts
- [ ] Tests manuels confirmant que OpenCode répond correctement

**Technical Notes:**
- OpenCode supporte configuration via fichiers YAML
- Définir personnalité : "Assistant déploiement Azure pour techniciens Modern Workplace"
- Inclure contexte : "Les techniciens ne sont pas experts Azure"
- Workflow : Installation → Connexion Azure → Storage → Translator F0 → Functions → Rapport

**Dependencies:** STORY-003

---

#### STORY-014: Interface Conversationnelle Française OpenCode

**Epic:** EPIC-003
**Priority:** Must Have
**Points:** 2

**User Story:**
En tant que technicien Modern Workplace
Je veux converser avec OpenCode en français
Afin de comprendre chaque étape sans jargon technique excessif

**Acceptance Criteria:**
- [ ] OpenCode répond en français clair et compréhensible
- [ ] Pas de termes techniques Azure sans explication
- [ ] Confirmation demandée avant chaque action critique
- [ ] Feedback positif quand une étape réussit
- [ ] Messages d'erreur formatés : "Problème: [description]. Solution: [action]"
- [ ] Tests utilisateur avec un technicien confirmant compréhensibilité

**Technical Notes:**
- Configuration langue dans OpenCode config
- Créer exemples de dialogues types
- Tester avec cas réels (connexion Azure, déploiement, erreurs)
- Guidance sur NFR-006 (Usability - Interface conversationnelle simple)

**Dependencies:** STORY-013

---

### EPIC-004: Reporting et Traçabilité

#### STORY-015: Génération Automatique Rapport d'Intervention

**Epic:** EPIC-004
**Priority:** Must Have
**Points:** 3

**User Story:**
En tant qu'OpenCode
Je veux générer un rapport d'intervention complet après déploiement
Afin de fournir au technicien les informations pour le ticketing

**Acceptance Criteria:**
- [ ] Module Python `report_generator.py` créé
- [ ] Fonction `generate_report()` collecte toutes les infos de déploiement
- [ ] Rapport contient: nom client, groupe de ressources, services déployés, URLs/endpoints, date/heure
- [ ] Aucune information sensible (credentials) dans le rapport
- [ ] Rapport sauvegardé localement avec timestamp : `rapport-{client}-{timestamp}.txt`
- [ ] Rapport affiché dans terminal pour copier-coller
- [ ] Possibilité de regénérer le rapport si besoin

**Technical Notes:**
- Format texte simple (facile copier-coller dans ticket)
- Collecter infos depuis résultats Azure CLI
- Sanitizer pour enlever credentials
- Template: "Déploiement Bot Traducteur - Client: {nom} - Date: {date} - Ressources: ..."

**Dependencies:** STORY-006, STORY-007, STORY-008

---

#### STORY-016: Template de Rapport Formaté pour Ticketing

**Epic:** EPIC-004
**Priority:** Should Have
**Points:** 2

**User Story:**
En tant que technicien Modern Workplace
Je veux un rapport bien formaté et professionnel
Afin de le copier-coller directement dans le système de ticketing client

**Acceptance Criteria:**
- [ ] Template Markdown ou texte créé avec sections claires
- [ ] Sections: En-tête, Services Déployés, URLs/Endpoints, Configuration, Notes
- [ ] Format compatible copier-coller dans tickets
- [ ] Pas de caractères spéciaux qui cassent le formatage
- [ ] Longueur raisonnable (< 50 lignes)
- [ ] Design testé avec système de ticketing réel

**Technical Notes:**
- Template simple en texte brut ou Markdown léger
- Éviter tableaux complexes
- Utiliser listes à puces

**Dependencies:** STORY-015

---

### Infrastructure Testing

#### STORY-INF-001: Tests End-to-End du Workflow Complet

**Epic:** Infrastructure
**Priority:** Should Have
**Points:** 8

**User Story:**
En tant que développeur
Je veux tester le workflow complet de bout en bout
Afin de garantir que tout fonctionne ensemble sans erreur

**Acceptance Criteria:**
- [ ] Script de test E2E créé
- [ ] Test: Installation exe → Démarrage container → Connexion Azure → Déploiement complet
- [ ] Test vérifie que tous les services Azure sont créés
- [ ] Test vérifie que SKU F0 est bien utilisé pour Translator
- [ ] Test vérifie que rapport est généré
- [ ] Test peut être exécuté automatiquement (CI/CD)
- [ ] Cleanup automatique des ressources test après exécution

**Technical Notes:**
- Utiliser subscription Azure de test
- Automatiser avec pytest ou script PowerShell/Bash
- Créer ressources avec préfixe "test-" pour identification
- Nettoyer groupe de ressources après test
- Documenter comment exécuter les tests

**Dependencies:** Toutes les stories précédentes

---

## Sprint Allocation

### Sprint 1 (Semaines 1-2) - 27/30 points (90% utilisation)

**Dates:** 2026-01-20 → 2026-01-31

**Goal:** Établir l'infrastructure de base et l'environnement d'installation complet avec OpenCode configuré

**Stories:**
- STORY-000: Setup Environnement - 2 points
- STORY-001: Installeur Inno Setup - 5 points
- STORY-002: Script PowerShell Defender - 3 points
- STORY-003: Container Docker - 8 points ⚠️ Story complexe
- STORY-004: Script start.bat - 3 points
- STORY-005: Ouverture auto terminal/navigateur - 2 points
- STORY-012: Clone repo automatique - 2 points
- STORY-013: Config OpenCode prompts - 2 points

**Total:** 27 points / 30 capacité (90% utilisation)

**Livrable:** Installation complète fonctionnelle, container Docker opérationnel avec OpenCode configuré, prêt pour développement Azure

**Risques Sprint 1:**
- STORY-003 (8 points) est complexe : Dockerfile avec multiples dépendances
- Exclusions Defender ASR (STORY-002) peuvent nécessiter ajustements
- Première utilisation Inno Setup (STORY-001)

**Mitigation:**
- Tester build Docker incrémentalement
- Documentation claire pour script Defender
- Exemples Inno Setup disponibles

**Critères de Succès Sprint 1:**
- [ ] Exe installeur fonctionne sur Windows 10/11
- [ ] Container Docker démarre en < 2 minutes
- [ ] OpenCode accessible et répondant
- [ ] Documentation Flask accessible sur localhost:5545

---

### Sprint 2 (Semaines 3-4) - 26/30 points (87% utilisation)

**Dates:** 2026-02-03 → 2026-02-14

**Goal:** Implémenter l'automatisation complète du déploiement Azure avec Storage, Translator F0, et Functions

**Stories:**
- STORY-006: Wrapper Python Storage Account - 5 points
- STORY-007: Wrapper Python Translator F0 - 5 points ⚠️ CRITIQUE (SKU F0 hardcodé)
- STORY-008: Wrapper Python Functions - 8 points ⚠️ Story complexe
- STORY-009: Support multi-comptes Azure - 3 points
- STORY-011: Serveur Flask documentation - 5 points

**Total:** 26 points / 30 capacité (87% utilisation)

**Livrable:** Déploiement Azure complet fonctionnel (Storage + Translator F0 + Functions) avec documentation Power Platform accessible

**Risques Sprint 2:**
- STORY-007 CRITIQUE : SKU F0 doit être hardcodé et testé rigoureusement
- STORY-008 complexe : Déploiement Functions avec toutes les variables d'environnement
- Dépendance sur Azure (connexion, permissions)
- First-time Azure CLI automation

**Mitigation:**
- Code review spécifique sur STORY-007 (SKU F0)
- Tests unitaires vérifiant F0 exclusivement
- Tests incrémentaux avec Azure subscription de test
- Documentation claire des erreurs Azure CLI

**Critères de Succès Sprint 2:**
- [ ] Storage Account créé avec container blob
- [ ] Azure Translator créé avec SKU F0 (vérifié par test)
- [ ] Azure Functions déployées, health check OK
- [ ] Variables d'environnement configurées correctement
- [ ] Documentation Power Platform affichée dans navigateur

---

### Sprint 3 (Semaines 5-6) - 17/30 points (57% utilisation)

**Dates:** 2026-02-17 → 2026-02-28

**Goal:** Finaliser la documentation, le reporting, et valider le système complet end-to-end pour premier déploiement autonome

**Stories:**
- STORY-010: Documentation MFA - 2 points (Should Have)
- STORY-014: Interface conversationnelle française - 2 points
- STORY-015: Génération rapport intervention - 3 points
- STORY-016: Template rapport formaté - 2 points
- STORY-INF-001: Tests E2E workflow complet - 8 points ⚠️ Validation finale

**Total:** 17 points / 30 capacité (57% utilisation)

**Livrable:** Système complet validé end-to-end, documentation complète, rapport d'intervention automatique, prêt pour premier déploiement client autonome

**Risques Sprint 3:**
- Tests E2E (STORY-INF-001) peuvent révéler des bugs nécessitant corrections
- Intégration complète jamais testée avant
- STORY-INF-001 complexe, peut prendre plus de 8 points si problèmes découverts

**Buffer Sprint 3:** 13 points disponibles pour:
- Corrections de bugs découverts pendant tests E2E
- Ajustements post-feedback
- Optimisations de performance
- Stories Should Have additionnelles si temps disponible

**Mitigation:**
- Buffer intentionnel (13 points) pour corrections
- Tests incrémentaux pendant Sprints 1-2
- Documentation des erreurs communes
- Support Eric disponible

**Critères de Succès Sprint 3:**
- [ ] Tests E2E réussis (installation → déploiement → rapport)
- [ ] SKU F0 validé par test automatique
- [ ] Rapport d'intervention généré et formaté
- [ ] Documentation MFA accessible
- [ ] Système prêt pour déploiement client

---

## Epic Traceability

| Epic ID | Epic Name | Stories | Total Points | Sprints |
|---------|-----------|---------|--------------|---------|
| Infrastructure | Setup & Testing | STORY-000, STORY-INF-001 | 10 points | Sprint 1, 3 |
| EPIC-001 | Installation et Configuration Initiale | STORY-001, 002, 003, 004, 005 | 21 points | Sprint 1 |
| EPIC-002 | Déploiement Azure Automatisé | STORY-006, 007, 008, 009, 010 | 23 points | Sprint 2, 3 |
| EPIC-003 | Documentation et Interface Utilisateur | STORY-011, 012, 013, 014 | 12 points | Sprint 1, 2, 3 |
| EPIC-004 | Reporting et Traçabilité | STORY-015, 016 | 5 points | Sprint 3 |

---

## Requirements Coverage

### Functional Requirements → Story Mapping

| FR ID | FR Name | Story | Sprint | Epic |
|-------|---------|-------|--------|------|
| FR-001 | Installation via exécutable Windows | STORY-001 | 1 | EPIC-001 |
| FR-002 | Gestion automatique exclusions Defender ASR | STORY-002 | 1 | EPIC-001 |
| FR-003 | Lancement automatique du container Docker | STORY-004 | 1 | EPIC-001 |
| FR-004 | Container Docker pré-configuré | STORY-003 | 1 | EPIC-001 |
| FR-005 | Ouverture automatique terminal + navigateur | STORY-005 | 1 | EPIC-001 |
| FR-006 | Déploiement Azure Storage Account | STORY-006 | 2 | EPIC-002 |
| FR-007 | Déploiement Azure Translator (SKU F0) | STORY-007 | 2 | EPIC-002 |
| FR-008 | Déploiement Azure Functions (backend Python) | STORY-008 | 2 | EPIC-002 |
| FR-009 | Support multi-comptes Azure | STORY-009 | 2 | EPIC-002 |
| FR-010 | Gestion des cas MFA | STORY-010 | 3 | EPIC-002 |
| FR-011 | Serveur de documentation Flask | STORY-011 | 2 | EPIC-003 |
| FR-012 | Clone automatique repo trad-bot-src | STORY-012 | 1 | EPIC-003 |
| FR-013 | Guidance conversationnelle OpenCode | STORY-013, 014 | 1, 3 | EPIC-003 |
| FR-014 | Génération rapport d'intervention | STORY-015, 016 | 3 | EPIC-004 |

**Coverage: 14/14 FRs (100%)**

---

### Non-Functional Requirements → Solution Mapping

| NFR ID | NFR Name | Architecture Solution | Stories |
|--------|----------|----------------------|---------|
| NFR-001 | Performance - Temps de démarrage | Container optimisé, image légère | STORY-003 |
| NFR-002 | Performance - Temps déploiement Azure | Wrappers Python efficaces, Azure CLI | STORY-006, 007, 008 |
| NFR-003 | Security - Aucun stockage credentials | Sanitization logs, display only | STORY-006, 007, 008, 015 |
| NFR-004 | Security - Exclusions Defender ciblées | Script PowerShell ciblé | STORY-002 |
| NFR-005 | Reliability - Gestion erreurs Azure CLI | Error handling dans wrappers | STORY-006, 007, 008 |
| NFR-006 | Usability - Interface conversationnelle simple | OpenCode config français, prompts pédagogiques | STORY-013, 014 |
| NFR-007 | Maintainability - Mises à jour Azure CLI | Dockerfile versionné, process MAJ | STORY-003 |
| NFR-008 | Compatibility - Environnement Windows | Installeur Windows, start.bat | STORY-001, 004 |
| NFR-009 | Compatibility - Navigateurs modernes | Flask HTML simple | STORY-011 |
| NFR-010 | Usability - Messages d'erreur clairs | Error formatting dans tous wrappers | STORY-006, 007, 008, 014 |

**Coverage: 10/10 NFRs (100%)**

---

## Risks and Mitigation

### HIGH Risks

**Risque 1: SKU F0 mal configuré malgré hardcoding**
- **Probabilité:** Low (hardcodé dans code)
- **Impact:** CRITICAL - Coût client (S0 = 35$/mois vs F0 gratuit)
- **Mitigation:**
  - STORY-007: Hardcoder SKU F0 dans le code (pas de paramètre)
  - Tests unitaires vérifiant que seul F0 est utilisé
  - STORY-INF-001: Tests E2E validant déploiement avec F0
  - Code review spécifique sur cette partie critique
  - Documentation explicite: "NE PAS MODIFIER - SKU F0 OBLIGATOIRE"

**Risque 2: Tests E2E révèlent intégration cassée**
- **Probabilité:** Medium
- **Impact:** High - Retarde livraison, nécessite corrections
- **Mitigation:**
  - Sprint 3 avec buffer 13 points pour corrections
  - Tests incrémentaux pendant Sprints 1-2
  - STORY-INF-001 en fin de projet pour validation finale
  - Prévoir Sprint 3 flexible pour ajustements

**Risque 3: Azure Foundry indisponible bloque OpenCode**
- **Probabilité:** Low
- **Impact:** High - OpenCode inutilisable
- **Mitigation:**
  - Mode dégradé documenté (instructions textuelles statiques)
  - Fallback vers documentation Flask uniquement
  - Monitoring Azure Foundry avant déploiements
  - Solution Q3 du PRD: instructions prédéfinies en cache

---

### MEDIUM Risks

**Risque 4: Defender ASR bloque exe malgré exclusions**
- **Probabilité:** Medium
- **Impact:** Medium - Bloque installation
- **Mitigation:**
  - STORY-002: Script PowerShell bien testé
  - Documentation claire pour techniciens
  - Option: Demander règle Intune centralisée au SI
  - Support Eric disponible pour premiers déploiements

**Risque 5: Docker Desktop pas démarré au lancement**
- **Probabilité:** Medium
- **Impact:** Medium - Bloque démarrage application
- **Mitigation:**
  - STORY-004: Vérification Docker dans start.bat
  - Message d'erreur clair avec action corrective
  - Documentation prérequis (Docker Desktop installé et démarré)
  - Solution Q2 du PRD: Vérification au lancement + message clair

**Risque 6: Complexité Dockerfile (multiples dépendances)**
- **Probabilité:** Medium
- **Impact:** Medium - Build lent ou échec
- **Mitigation:**
  - STORY-003: Tests build incrémentaux
  - Utiliser images de base officielles (ubuntu:24.04)
  - Docker layer caching pour accélérer rebuilds
  - Documentation processus build

---

### LOW Risks

**Risque 7: Azure CLI obsolète**
- **Probabilité:** High (MAJ fréquentes Azure)
- **Impact:** Low - Risque à long terme (pas bloquant immédiat)
- **Mitigation:**
  - Versionning container Docker avec tags
  - Process documenté pour MAJ Azure CLI
  - Rollback possible vers version précédente
  - Solution Q1 du PRD: Versionning + process MAJ

**Risque 8: Permissions Azure insuffisantes chez client**
- **Probabilité:** Low
- **Impact:** Low - Bloque déploiement mais détectable rapidement
- **Mitigation:**
  - STORY-009: Vérification permissions avant déploiement
  - Message d'erreur clair si permissions insuffisantes
  - Documentation permissions requises (Contributor minimum)

---

## Dependencies

### External Dependencies

**Infrastructure:**
- Docker Desktop 4.x+ installé sur poste technicien (prérequis)
- Windows 10/11 avec droits administrateur
- Connexion internet stable pour Docker, Azure CLI, OpenCode
- Inno Setup Compiler pour build installeur (développement uniquement)

**Azure:**
- Azure subscription avec permissions Contributor minimum
- Azure Foundry avec modèle IA configuré et accessible
- Compte OpenCode avec API key valide

**Repos et Code Source:**
- Repo trad-bot-src accessible (GitHub, Azure DevOps, etc.)
  - Contient code Azure Functions (src/)
  - Contient documentation Power Platform
- Repo actuel (deploy-trad-bot-contanier) pour développement

**Services Tiers:**
- Azure Translator service disponible avec SKU F0
- Azure Storage disponible
- Azure Functions runtime Python 3.11 supporté

---

### Internal Dependencies (Inter-Stories)

**Sprint 1:**
- STORY-001 → STORY-002 (script Defender dépend de l'exe)
- STORY-000 → STORY-003 (env dev avant build container)
- STORY-003 → STORY-004, 005, 012, 013 (container requis)

**Sprint 2:**
- STORY-003 (Sprint 1) → STORY-006, 007, 008, 009, 011 (toutes dépendent du container)

**Sprint 3:**
- STORY-013 (Sprint 1) → STORY-010, 014 (config OpenCode requise)
- STORY-006, 007, 008 (Sprint 2) → STORY-015 (déploiement requis pour rapport)
- STORY-015 → STORY-016 (rapport avant template)
- ALL stories → STORY-INF-001 (tests E2E nécessitent système complet)

**✓ Toutes les dépendances sont satisfaites dans l'allocation actuelle des sprints.**

---

## Definition of Done

Pour qu'une story soit considérée complète, elle doit satisfaire TOUS les critères suivants:

**Code:**
- [ ] Code implémenté selon acceptance criteria de la story
- [ ] Code committed dans le repo avec message descriptif
- [ ] Pas de code commenté ou de TODOs critiques

**Tests:**
- [ ] Tests unitaires écrits et passant (≥80% coverage pour code critique)
- [ ] Tests d'intégration passant (si applicable)
- [ ] Tests manuels effectués et validés

**Quality:**
- [ ] Code reviewed (self-review minimum, peer review recommandé)
- [ ] Pas de warnings critiques (linting, security scans)
- [ ] Performance acceptable (pas de régression)

**Documentation:**
- [ ] Documentation technique mise à jour (README, comments)
- [ ] Documentation utilisateur mise à jour (si applicable)
- [ ] CLAUDE.md mis à jour si nouvelles conventions

**Deployment:**
- [ ] Code déployé/testé dans environnement local
- [ ] Pas de breaking changes non documentés
- [ ] Rollback possible si nécessaire

**Validation:**
- [ ] Acceptance criteria de la story validés
- [ ] Demo effectuée (si applicable)
- [ ] Product Owner (Eric) approuve la story

**Spécifique "Aux Petits Oignons":**
- [ ] Testé sur Windows 10 ET Windows 11
- [ ] Aucun credential stocké (validé par scan)
- [ ] Messages en français clair
- [ ] Compatible avec Docker Desktop 4.x+

---

## Team Capacity

**Configuration:**
- **Équipe:** 1 développeur senior (Eric)
- **Sprint:** 2 semaines = 10 jours ouvrés
- **Productivité:** 6h/jour (développeur senior)
- **Total heures:** 1 × 10 × 6 = 60 heures par sprint
- **Vélocité:** 1 point = 2 heures (estimation senior)
- **Capacité:** 30 points par sprint

**Hypothèses:**
- Pas de congés planifiés
- Pas de meetings critiques bloquants
- Environnement de développement stable
- Accès Azure disponible pour tests

**Ajustements possibles:**
- Si vélocité réelle diffère : ajuster allocation Sprints 2-3
- Si bugs critiques découverts : utiliser buffer Sprint 3
- Si stories plus rapides : ajouter stories Should Have

---

## Sprint Cadence

**Rythme recommandé:**

**Début de Sprint (Jour 1):**
- Sprint Planning (30-60 min)
- Review sprint goal et stories
- Confirm priorities et dépendances

**Pendant Sprint (Jours 2-9):**
- Daily check-in (5-10 min, optionnel pour équipe de 1)
- Développement continu
- Tests incrémentaux
- Update status stories (via /sprint-status si implémenté)

**Fin de Sprint (Jour 10):**
- Sprint Review (60 min)
  - Demo des stories complétées
  - Validation acceptance criteria
  - Feedback et ajustements
- Sprint Retrospective (30 min)
  - What went well?
  - What didn't go well?
  - What to improve?
- Sprint Planning pour sprint suivant (30-60 min)

**Outils:**
- GitHub Issues ou Azure DevOps pour tracking
- Git pour version control
- Document sprint-status.yaml pour suivi vélocité

---

## Next Steps

**Immediate: Commencer Sprint 1**

**Option 1: Créer les story documents détaillés**
```bash
/create-story STORY-000
/create-story STORY-001
# ... etc pour chaque story Sprint 1
```

**Option 2: Commencer l'implémentation directement**
```bash
/dev-story STORY-000  # Setup environnement
/dev-story STORY-001  # Installeur Inno Setup
# ... etc
```

**Recommandation:** Commencer avec STORY-000 (Setup Environnement) pour établir les bases, puis STORY-003 (Container Docker) qui est critique pour le reste.

**Commandes utiles:**
- `/sprint-status` - Vérifier l'état actuel du sprint
- `/dev-story STORY-XXX` - Implémenter une story spécifique
- `/create-story STORY-XXX` - Créer document détaillé pour une story

---

## Appendix: Story Point Calibration

**Référence pour estimation:**

**1 point (1-2 heures):**
- Update configuration value
- Change text/copy
- Add simple validation
- Fix typo in code

**2 points (2-4 heures):**
- Create basic CRUD endpoint
- Simple component (no complex state)
- Add database index
- Write unit tests for existing code
- **Examples:** STORY-000, 005, 010, 012, 014, 016

**3 points (4-8 heures):**
- Complex component with state
- Business logic function
- Integration test suite
- API endpoint with validation
- **Examples:** STORY-002, 004, 009, 013, 015

**5 points (1-2 days):**
- Feature with frontend + backend
- Database migration with data transformation
- Complex business logic with edge cases
- Full test coverage for feature
- **Examples:** STORY-001, 006, 007, 011

**8 points (2-3 days):**
- Complete user flow (e.g., registration)
- Multiple related components
- Complex state management
- Integration with external service
- **Examples:** STORY-003, 008, STORY-INF-001

**13 points (3-5 days):**
- **TOO BIG - BREAK IT DOWN**
- This is an epic, not a story

---

**This sprint plan was created using BMAD Method v6 - Phase 4 (Implementation Planning)**

*Date de création: 2026-01-18*
*Scrum Master: Eric*
*Prochaine étape: `/dev-story STORY-000` pour commencer Sprint 1*

---

## Project Summary

**"Aux Petits Oignons"** - Outil de déploiement automatisé pour Bot Traducteur

**Objectif:** Permettre aux techniciens Modern Workplace (non-experts Azure) de déployer le Bot Traducteur de manière autonome, standardisée, et sans erreur de configuration (notamment SKU F0 pour Translator).

**Valeur Business:**
- Délégation des déploiements (libère temps d'Eric)
- Qualité garantie (100% standardisé, zéro erreur SKU)
- Satisfaction techniciens (outil vs formation Azure complexe)

**Timeline:** 6 semaines (3 sprints × 2 semaines)
**Livraison:** Fin février 2026
**Premier déploiement autonome:** Sprint 3 complété

✓ Plan validé - Prêt pour implémentation ! 🚀
