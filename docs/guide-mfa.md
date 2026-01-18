# Guide: Gestion de l'Authentification Multi-Facteurs (MFA) pour Azure CLI

**Version:** 1.0
**Date:** 2026-01-18
**Audience:** Techniciens Modern Workplace
**Objectif:** Permettre la connexion Azure CLI depuis le conteneur Docker malgré les politiques MFA actives

---

## Table des Matières

1. [Comprendre le Problème MFA](#comprendre-le-problème-mfa)
2. [Solutions Recommandées](#solutions-recommandées)
3. [Solution 1: Emplacements Nommés (Recommandé)](#solution-1-emplacements-nommés)
4. [Solution 2: Exclusion Temporaire MFA](#solution-2-exclusion-temporaire-mfa)
5. [Solution 3: Service Principal (Avancé)](#solution-3-service-principal-avancé)
6. [Troubleshooting](#troubleshooting)
7. [Rappels de Sécurité](#rappels-de-sécurité)
8. [Ressources Microsoft](#ressources-microsoft)

---

## Comprendre le Problème MFA

### Qu'est-ce que le MFA ?

L'**Authentification Multi-Facteurs (MFA)** est une sécurité qui demande une double vérification lors de la connexion :
1. Votre mot de passe (ce que vous savez)
2. Un code de votre téléphone (ce que vous avez)

### Pourquoi MFA bloque Azure CLI ?

Quand vous exécutez `az login` dans le conteneur Docker, Azure CLI ouvre un navigateur pour la connexion. **Problème :** dans certains environnements (RDP, VDI, conteneurs), le navigateur peut :
- Ne pas s'ouvrir correctement
- Ne pas communiquer avec Azure CLI
- Être bloqué par des politiques réseau

Même avec `az login --use-device-code`, le MFA peut bloquer si :
- Votre IP n'est pas reconnue
- Votre emplacement géographique est différent
- Une politique d'accès conditionnel est trop stricte

### Symptômes Courants

```bash
$ az login
# Résultat: Le navigateur s'ouvre mais rien ne se passe
# OU
# Résultat: "MFA is required but cannot be completed"
# OU
# Résultat: "Conditional Access policy blocked"
```

---

## Solutions Recommandées

| Solution | Complexité | Sécurité | Recommandé pour |
|----------|------------|----------|-----------------|
| **Emplacements Nommés** | Moyenne | ✅ Élevée | Déploiements réguliers depuis même IP |
| **Exclusion Temporaire MFA** | Facile | ⚠️ Moyenne | Déploiements ponctuels |
| **Service Principal** | Élevée | ✅ Élevée | Automatisation CI/CD |

**Notre recommandation :** Commencez par les **Emplacements Nommés** si vous déployez régulièrement depuis le même site/IP.

---

## Solution 1: Emplacements Nommés

### Vue d'Ensemble

Les **Emplacements Nommés** (Named Locations) permettent de définir des adresses IP ou plages IP comme "fiables". Une fois configurés, les connexions depuis ces IPs peuvent être exemptées de MFA.

### Prérequis

- Rôle **Administrateur de sécurité** ou **Administrateur d'accès conditionnel** dans Entra ID
- Connaître votre adresse IP publique (trouvez-la sur [https://whatismyipaddress.com/](https://whatismyipaddress.com/))

### Étape 1: Créer un Emplacement Nommé

1. **Connectez-vous au portail Azure**
   [https://portal.azure.com](https://portal.azure.com)

2. **Accédez à Entra ID (anciennement Azure AD)**
   Portail Azure > **Microsoft Entra ID**

3. **Naviguez vers Emplacements Nommés**
   Microsoft Entra ID > **Sécurité** > **Accès conditionnel** > **Emplacements nommés**

4. **Créez un nouvel emplacement**
   Cliquez sur **+ Nouvel emplacement**

5. **Configurez l'emplacement**
   - **Nom :** `Bureau Technicien - [Votre Nom]` (exemple: "Bureau Technicien - Eric")
   - **Type :** Sélectionnez **Plages IP**
   - **Marquer comme emplacement approuvé :** ☑️ Cochez cette case
   - **Plages IPv4 :** Ajoutez votre IP publique (exemple: `203.0.113.45/32`)
     - `/32` signifie une seule IP exacte
     - Utilisez `/24` pour une plage (exemple: `203.0.113.0/24` = toutes les IPs de 203.0.113.0 à 203.0.113.255)

6. **Enregistrez**
   Cliquez sur **Créer**

### Étape 2: Créer une Politique d'Accès Conditionnel

Une fois l'emplacement nommé créé, vous devez créer une **politique d'accès conditionnel** qui exempte cet emplacement du MFA.

1. **Naviguez vers Politiques d'Accès Conditionnel**
   Microsoft Entra ID > **Sécurité** > **Accès conditionnel** > **Politiques**

2. **Créez une nouvelle politique**
   Cliquez sur **+ Nouvelle politique**

3. **Configurez la politique**

   **Nom :**
   `Exemption MFA - Emplacements Fiables - Azure CLI`

   **Affectations - Utilisateurs :**
   - Sélectionnez **Utilisateurs et groupes spécifiques**
   - Ajoutez votre compte de déploiement OU un groupe de techniciens
   - ⚠️ **Important :** Ne sélectionnez PAS "Tous les utilisateurs"

   **Affectations - Applications cloud :**
   - Sélectionnez **Toutes les applications cloud** OU
   - Spécifique : **Azure Management** (pour Azure CLI uniquement)

   **Conditions - Emplacements :**
   - Configurez : **Oui**
   - Inclure : **Tous les emplacements**
   - Exclure : ☑️ **Tous les emplacements approuvés** (votre emplacement nommé créé à l'Étape 1)

   **Contrôles d'accès - Accorder :**
   - Sélectionnez **Accorder l'accès**
   - ☑️ **Exiger l'authentification multifacteur** (désactivez cette option si vous êtes dans un emplacement approuvé)

   **Alternative recommandée :**
   - Conditions - Emplacements : Inclure **Tous les emplacements**
   - Exclure : Sélectionnez votre emplacement nommé `Bureau Technicien - [Votre Nom]`
   - Contrôles : Exiger MFA uniquement si HORS de l'emplacement approuvé

4. **Activez la politique**
   - **Activer la politique :** Sélectionnez **Activé**
   - Cliquez sur **Créer**

### Étape 3: Tester la Connexion

1. **Vérifiez votre IP publique**
   ```bash
   curl ifconfig.me
   # OU
   curl https://api.ipify.org
   ```

2. **Testez Azure CLI**
   ```bash
   az login
   # Si device code nécessaire :
   az login --use-device-code
   ```

3. **Vérifiez la connexion**
   ```bash
   az account show
   ```

✅ **Succès :** Vous devriez pouvoir vous connecter sans MFA depuis votre IP fiable.

---

## Solution 2: Exclusion Temporaire MFA

### ⚠️ Avertissement de Sécurité

Cette solution **désactive temporairement le MFA** pour votre compte. Utilisez-la uniquement si :
- Vous déployez ponctuellement (une seule fois)
- Vous n'avez pas accès aux emplacements nommés
- Vous êtes conscient du risque de sécurité

**🛡️ IMPORTANT :** Réactivez le MFA immédiatement après le déploiement.

### Prérequis

- Rôle **Administrateur d'authentification** ou **Administrateur global** dans Entra ID
- Durée d'exclusion prévue (recommandé : maximum 24 heures)

### Étape 1: Créer une Politique d'Exclusion Temporaire

1. **Accédez aux Politiques d'Accès Conditionnel**
   Microsoft Entra ID > **Sécurité** > **Accès conditionnel** > **Politiques**

2. **Créez une nouvelle politique**
   Cliquez sur **+ Nouvelle politique**

3. **Configurez la politique temporaire**

   **Nom :**
   `TEMPORAIRE - Exclusion MFA - Déploiement [Votre Nom] - [Date]`
   Exemple : `TEMPORAIRE - Exclusion MFA - Déploiement Eric - 2026-01-18`

   **Affectations - Utilisateurs :**
   - Sélectionnez **Utilisateurs et groupes spécifiques**
   - Ajoutez UNIQUEMENT votre compte de déploiement

   **Affectations - Applications cloud :**
   - Sélectionnez **Azure Management** (pour limiter à Azure CLI uniquement)

   **Conditions - Applications clientes :**
   - Configurez : **Oui**
   - ☑️ **Navigateur** et ☑️ **Applications mobiles et clients de bureau**

   **Contrôles d'accès - Accorder :**
   - Sélectionnez **Accorder l'accès**
   - ☑️ **Exiger l'authentification multifacteur** : **DÉCOCHEZ** cette option

   **Session :**
   - **Fréquence de connexion :** Configurez à **1 heure** ou **4 heures**
   - Cela force une nouvelle connexion après expiration

4. **Activez la politique**
   - **Activer la politique :** Sélectionnez **Activé**
   - Cliquez sur **Créer**

### Étape 2: Testez et Déployez

```bash
# Déconnectez-vous d'Azure CLI
az logout

# Reconnectez-vous (sans MFA)
az login --use-device-code

# Vérifiez la connexion
az account show

# Effectuez votre déploiement
opencode
# Puis suivez les instructions de déploiement
```

### Étape 3: ⚠️ SUPPRIMER L'EXCLUSION IMMÉDIATEMENT APRÈS

**🛡️ CRITIQUE :** Une fois le déploiement terminé, supprimez cette politique :

1. **Retournez aux Politiques d'Accès Conditionnel**
   Microsoft Entra ID > **Sécurité** > **Accès conditionnel** > **Politiques**

2. **Trouvez votre politique temporaire**
   `TEMPORAIRE - Exclusion MFA - Déploiement [Votre Nom] - [Date]`

3. **Supprimez la politique**
   Sélectionnez la politique > **Supprimer**

4. **Vérifiez que MFA est réactivé**
   ```bash
   az logout
   az login
   # Devrait maintenant demander MFA
   ```

---

## Solution 3: Service Principal (Avancé)

### Vue d'Ensemble

Un **Service Principal** est un compte de service (non humain) qui peut se connecter à Azure sans MFA. C'est la solution idéale pour l'automatisation.

### Prérequis

- Rôle **Propriétaire** ou **Administrateur d'application** dans Entra ID
- Compréhension des rôles et permissions Azure

### Étape 1: Créer le Service Principal

```bash
# Créer un Service Principal avec rôle Contributor
az ad sp create-for-rbac --name "SP-TradBot-Deploy" \
  --role Contributor \
  --scopes /subscriptions/<SUBSCRIPTION_ID>

# Résultat (NOTEZ CES VALEURS) :
# {
#   "appId": "12345678-1234-1234-1234-123456789abc",
#   "displayName": "SP-TradBot-Deploy",
#   "password": "XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX",
#   "tenant": "87654321-4321-4321-4321-cba987654321"
# }
```

⚠️ **Sécurité :** Ne partagez JAMAIS ces credentials. Stockez-les de manière sécurisée (Azure Key Vault, gestionnaire de mots de passe).

### Étape 2: Se Connecter avec le Service Principal

```bash
# Connexion avec Service Principal
az login --service-principal \
  --username <appId> \
  --password <password> \
  --tenant <tenant>

# Vérifiez la connexion
az account show
```

### Étape 3: Utiliser dans OpenCode

Configurez les variables d'environnement dans le conteneur :

```bash
# Dans .env ou variables d'environnement
export AZURE_CLIENT_ID=<appId>
export AZURE_CLIENT_SECRET=<password>
export AZURE_TENANT_ID=<tenant>

# Azure CLI détectera automatiquement ces variables
az login --service-principal \
  --username $AZURE_CLIENT_ID \
  --password $AZURE_CLIENT_SECRET \
  --tenant $AZURE_TENANT_ID
```

### Avantages et Inconvénients

**✅ Avantages :**
- Pas de MFA requis
- Idéal pour automatisation
- Permissions contrôlées par rôles RBAC

**❌ Inconvénients :**
- Gestion des secrets plus complexe
- Nécessite permissions élevées pour créer
- Risque de sécurité si credentials compromis

---

## Troubleshooting

### Problème 1: "Conditional Access policy blocked"

**Symptôme :**
```
ERROR: Conditional Access policy blocked. Please contact your administrator.
```

**Causes possibles :**
- Votre IP n'est pas dans un emplacement nommé fiable
- Une politique MFA stricte s'applique
- Votre compte n'a pas les permissions nécessaires

**Solutions :**
1. Vérifiez votre IP publique : `curl ifconfig.me`
2. Contactez votre admin pour vérifier les politiques d'accès conditionnel
3. Demandez une exclusion temporaire (Solution 2)
4. Utilisez un Service Principal (Solution 3)

---

### Problème 2: "Device code flow is disabled"

**Symptôme :**
```
ERROR: Device code flow is disabled for your tenant
```

**Causes possibles :**
- Le tenant a désactivé le device code flow
- Politique de sécurité trop restrictive

**Solutions :**
1. Contactez votre administrateur Entra ID
2. Demandez l'activation du device code flow
3. Utilisez un Service Principal (Solution 3)

---

### Problème 3: MFA demandé malgré l'emplacement nommé

**Symptôme :**
Vous avez créé un emplacement nommé mais MFA est toujours demandé.

**Causes possibles :**
- L'emplacement nommé n'est pas marqué comme "approuvé"
- La politique d'accès conditionnel n'exclut pas les emplacements approuvés
- Votre IP a changé (IP dynamique)
- Délai de propagation (jusqu'à 1 heure)

**Solutions :**
1. Vérifiez que l'emplacement est **marqué comme approuvé** (☑️)
2. Vérifiez la politique d'accès conditionnel :
   - Conditions > Emplacements > Exclure : **Tous les emplacements approuvés**
3. Attendez 15-30 minutes pour propagation
4. Vérifiez votre IP actuelle : `curl ifconfig.me`
5. Si IP dynamique, utilisez une plage `/24` au lieu de `/32`

---

### Problème 4: "Browser did not open or communicate back"

**Symptôme :**
```
The browser failed to open or communicate back.
```

**Causes possibles :**
- Environnement sans interface graphique (conteneur, serveur)
- Navigateur bloqué par pare-feu
- Redirection localhost bloquée

**Solutions :**
1. Utilisez le device code flow :
   ```bash
   az login --use-device-code
   ```
2. Copiez le code affiché
3. Ouvrez [https://microsoft.com/devicelogin](https://microsoft.com/devicelogin) sur votre machine Windows
4. Entrez le code
5. Complétez l'authentification MFA sur votre machine

---

### Problème 5: "You must use multi-factor authentication to access this resource"

**Symptôme :**
```
ERROR: You must use multi-factor authentication to access this resource.
```

**Causes possibles :**
- Politique MFA stricte s'applique
- Pas d'exclusion configurée pour votre IP/compte

**Solutions :**
1. Créez un emplacement nommé (Solution 1)
2. Demandez une exclusion temporaire (Solution 2)
3. Utilisez un Service Principal (Solution 3)
4. Si urgent : contactez votre admin pour exclusion manuelle

---

## Rappels de Sécurité

### ⚠️ Exclusions Temporaires MFA

Si vous utilisez la **Solution 2 (Exclusion Temporaire)** :

1. ✅ **Supprimez la politique immédiatement après le déploiement**
2. ✅ **Limitez l'exclusion à votre compte uniquement** (pas "Tous les utilisateurs")
3. ✅ **Limitez aux applications Azure Management** (pas toutes les apps)
4. ✅ **Documentez la raison** dans le nom de la politique
5. ✅ **Informez votre responsable sécurité** si politique de l'entreprise

### 🛡️ Bonnes Pratiques

- **Privilégiez les Emplacements Nommés** (Solution 1) pour la sécurité
- **Ne partagez jamais vos credentials de Service Principal**
- **Utilisez Azure Key Vault** pour stocker les secrets de Service Principal
- **Activez les logs d'audit** pour tracer les connexions
- **Révisez régulièrement** les politiques d'accès conditionnel

### 📋 Checklist Post-Déploiement

Après chaque déploiement, vérifiez :

- [ ] Politique d'exclusion MFA temporaire supprimée (si utilisée)
- [ ] MFA réactivé sur votre compte (testez avec `az logout && az login`)
- [ ] Pas de credentials Azure CLI stockés en clair dans le conteneur
- [ ] Service Principal (si utilisé) a les permissions minimales nécessaires
- [ ] Logs d'audit Azure consultés pour vérifier connexions

---

## Ressources Microsoft

### Documentation Officielle

- **Emplacements Nommés (Named Locations) :**
  [https://learn.microsoft.com/fr-fr/entra/identity/conditional-access/location-condition](https://learn.microsoft.com/fr-fr/entra/identity/conditional-access/location-condition)

- **Accès Conditionnel (Conditional Access) :**
  [https://learn.microsoft.com/fr-fr/entra/identity/conditional-access/overview](https://learn.microsoft.com/fr-fr/entra/identity/conditional-access/overview)

- **Azure CLI - Connexion (az login) :**
  [https://learn.microsoft.com/fr-fr/cli/azure/authenticate-azure-cli](https://learn.microsoft.com/fr-fr/cli/azure/authenticate-azure-cli)

- **Service Principals - Authentification :**
  [https://learn.microsoft.com/fr-fr/cli/azure/authenticate-azure-cli-service-principal](https://learn.microsoft.com/fr-fr/cli/azure/authenticate-azure-cli-service-principal)

- **MFA - Méthodes d'authentification :**
  [https://learn.microsoft.com/fr-fr/entra/identity/authentication/concept-authentication-methods](https://learn.microsoft.com/fr-fr/entra/identity/authentication/concept-authentication-methods)

### Tutoriels Vidéo (Microsoft Learn)

- **Configurer l'Accès Conditionnel :**
  [https://learn.microsoft.com/fr-fr/training/modules/secure-aad-users-with-mfa/](https://learn.microsoft.com/fr-fr/training/modules/secure-aad-users-with-mfa/)

- **Gérer les Emplacements Nommés :**
  [https://learn.microsoft.com/fr-fr/training/modules/plan-implement-conditional-access/](https://learn.microsoft.com/fr-fr/training/modules/plan-implement-conditional-access/)

### Support Microsoft

Si vous rencontrez des problèmes persistants :

1. **Support Azure :**
   Portail Azure > **Aide + support** > **Nouvelle demande de support**

2. **Forums Microsoft Q&A :**
   [https://learn.microsoft.com/fr-fr/answers/topics/azure-active-directory.html](https://learn.microsoft.com/fr-fr/answers/topics/azure-active-directory.html)

3. **Community Microsoft Tech :**
   [https://techcommunity.microsoft.com/](https://techcommunity.microsoft.com/)

---

## Résumé des Solutions

| Situation | Solution Recommandée | Temps Setup | Sécurité |
|-----------|---------------------|-------------|----------|
| **Déploiements réguliers depuis même IP** | Emplacements Nommés (Solution 1) | 15 min | ✅ Élevée |
| **Déploiement ponctuel urgent** | Exclusion Temporaire (Solution 2) | 5 min | ⚠️ Moyenne |
| **Automatisation CI/CD** | Service Principal (Solution 3) | 30 min | ✅ Élevée |
| **IP dynamique (ISP change IP)** | Service Principal (Solution 3) | 30 min | ✅ Élevée |
| **Pas accès admin Entra ID** | Demande à l'admin | Variable | Selon admin |

---

## Questions Fréquentes (FAQ)

### Q1: Puis-je utiliser mon compte Microsoft 365 pour Azure CLI ?

**R:** Oui, si votre compte M365 a des permissions sur l'Azure subscription du client. Cependant, le MFA M365 s'appliquera également à Azure CLI.

### Q2: Le MFA est-il obligatoire pour Azure ?

**R:** Microsoft recommande fortement le MFA, et de nombreuses entreprises l'imposent via des politiques d'accès conditionnel. Vous ne pouvez pas désactiver le MFA globalement sans permissions d'administrateur global.

### Q3: Combien de temps faut-il pour qu'un emplacement nommé soit actif ?

**R:** Généralement 5-15 minutes, mais peut prendre jusqu'à 1 heure dans certains cas. Attendez au moins 15 minutes avant de tester.

### Q4: Mon IP change souvent, que faire ?

**R:** Si votre FAI change votre IP fréquemment, utilisez plutôt un **Service Principal** (Solution 3) ou demandez à votre admin IT une connexion VPN avec IP fixe.

### Q5: Est-ce que `--use-device-code` évite le MFA ?

**R:** Non, `--use-device-code` change uniquement la méthode de connexion (navigateur externe). Le MFA sera toujours demandé si une politique l'exige.

---

## Contact et Support

Pour toute question sur ce guide ou le déploiement du Bot Traducteur :

- **Documentation complète :** `http://localhost:5545/procedure` (quand conteneur démarré)
- **Repo GitHub :** [Votre repo deploy-trad-bot-container]
- **Support Équipe :** Contactez votre responsable Modern Workplace

---

**Guide créé par :** Équipe Aux Petits Oignons
**Dernière mise à jour :** 2026-01-18
**Version :** 1.0
**Licence :** Usage interne entreprise

---

🎉 **Bon déploiement !** Si vous suivez ce guide, vous devriez pouvoir vous connecter à Azure CLI même avec MFA activé.
