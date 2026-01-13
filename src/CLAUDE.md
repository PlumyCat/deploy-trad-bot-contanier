# Instructions de Deploiement - Bot Traducteur

---

## ⚠️ REGLES CRITIQUES - A LIRE EN PREMIER ⚠️

### NE JAMAIS creer de ressources en double !

**AVANT de creer une ressource Azure, TOUJOURS verifier si elle existe deja :**

```bash
# Lister les Translator existants dans la souscription
az cognitiveservices account list --query "[?kind=='TextTranslation'].{Nom:name, SKU:sku.name, RG:resourceGroup}" -o table

# Lister les Storage Accounts
az storage account list --query "[].{Nom:name, RG:resourceGroup}" -o table

# Lister les Function Apps
az functionapp list --query "[].{Nom:name, RG:resourceGroup}" -o table
```

### Azure Translator : TOUJOURS utiliser F0 (gratuit) !

- **F0** = Gratuit (2M caracteres/mois)
- **S1** = Payant (~35$/mois) ❌ NE PAS UTILISER SAUF DEMANDE EXPLICITE

**Si un Translator F0 existe deja** → Reutiliser ses credentials, NE PAS en creer un nouveau !

```bash
# Recuperer les credentials d'un Translator existant
TRANSLATOR_NAME="nom-du-translator-existant"
RESOURCE_GROUP="son-resource-group"

TRANSLATOR_KEY=$(az cognitiveservices account keys list \
  --name $TRANSLATOR_NAME \
  --resource-group $RESOURCE_GROUP \
  --query key1 -o tsv)

TRANSLATOR_ENDPOINT=$(az cognitiveservices account show \
  --name $TRANSLATOR_NAME \
  --resource-group $RESOURCE_GROUP \
  --query properties.endpoint -o tsv)

echo "TRANSLATOR_KEY: $TRANSLATOR_KEY"
echo "TRANSLATOR_ENDPOINT: $TRANSLATOR_ENDPOINT"
```

---

## Workflow de Deploiement Complet

Le deploiement se fait en **3 phases** avec **2 comptes Azure differents** :

### Phase 0 : Creation App Entra ID (OneDrive)
**Compte requis** : Admin Global du tenant CLIENT

### Phase 1 : Deploiement Azure Backend
**Compte requis** : Compte delegue avec acces a la souscription Azure

### Phase 2 : Power Platform
**Compte requis** : Admin du tenant CLIENT

---

## PHASE 0 : App Entra ID pour OneDrive

### Pourquoi ?
Les fichiers traduits sont sauvegardes dans le OneDrive des utilisateurs.
Cela necessite une App Registration Entra ID avec des permissions Microsoft Graph.

### Etape 0.1 : Verifier la connexion Azure

La connexion Azure a ete faite au demarrage du container (via Windows avec navigateur).
Verifier que le bon compte est connecte :

```bash
az account show --query "{Compte:user.name, Tenant:tenantId}" -o table
```

**Si le mauvais compte est connecte**, quitter le container (`exit`) et relancer `start.bat` pour changer de tenant.

**IMPORTANT** : Pour cette phase, le technicien doit etre connecte avec un compte **Admin Global du tenant client** (pas le compte delegue Azure).

### Etape 0.2 : Recuperer le Tenant ID
```bash
TENANT_ID=$(az account show --query tenantId -o tsv)
echo "Tenant ID: $TENANT_ID"
```

### Etape 0.3 : Creer l'App Registration
```bash
CLIENT_NAME="nom-du-client"
APP_NAME="TradBot-OneDrive-$CLIENT_NAME"

CLIENT_ID=$(az ad app create \
  --display-name "$APP_NAME" \
  --sign-in-audience AzureADMyOrg \
  --query appId -o tsv)

echo "Client ID: $CLIENT_ID"
```

### Etape 0.4 : Creer le Service Principal
```bash
az ad sp create --id $CLIENT_ID
```

### Etape 0.5 : Ajouter les permissions Microsoft Graph
```bash
# User.Read.All (Application permission)
az ad app permission add \
  --id $CLIENT_ID \
  --api 00000003-0000-0000-c000-000000000000 \
  --api-permissions df021288-bdef-4463-88db-98f22de89214=Role

# Files.ReadWrite.All (Application permission)
az ad app permission add \
  --id $CLIENT_ID \
  --api 00000003-0000-0000-c000-000000000000 \
  --api-permissions 01d4889c-1287-42c6-ac1f-5d1e02578ef6=Role
```

### Etape 0.6 : Accorder le consentement administrateur
```bash
# Attendre quelques secondes que les permissions se propagent
sleep 5

az ad app permission admin-consent --id $CLIENT_ID
```

### Etape 0.6b : VERIFICATION MANUELLE DU CONSENTEMENT

**IMPORTANT** : La commande `admin-consent` peut parfois echouer silencieusement.

Demander au technicien de verifier manuellement :

1. Aller sur **https://entra.microsoft.com**
2. Menu **Applications** > **Inscriptions d'applications**
3. Cliquer sur l'application **TradBot-OneDrive-{client}**
4. Aller dans **Permissions API**
5. Verifier que les permissions ont un **check vert** (consentement accorde)
6. Si pas de check vert : cliquer sur **Accorder le consentement administrateur pour {tenant}**

Une fois le consentement valide, continuer.

### Etape 0.7 : Creer un secret client
```bash
CLIENT_SECRET=$(az ad app credential reset \
  --id $CLIENT_ID \
  --append \
  --display-name "TradBot-Secret" \
  --years 2 \
  --query password -o tsv)

echo "Client Secret: $CLIENT_SECRET"
```

### Etape 0.8 : Sauvegarder les credentials
**IMPORTANT** : Noter ces valeurs pour la Phase 1 !
- CLIENT_ID: $CLIENT_ID
- SECRET_ID: $CLIENT_SECRET (variable nommee SECRET_ID dans l'app)
- TENANT_ID: $TENANT_ID

---

## PHASE 1 : Deploiement Azure Backend

### Etape 1.1 : Reconnexion avec compte delegue

Le technicien doit maintenant se connecter avec le **compte delegue** qui a acces a la souscription Azure.

```bash
# Verifier le compte actuel
az account show --query "{Compte:user.name, Tenant:tenantId}" -o table
```

**Si besoin de changer de compte** : quitter le container (`exit`) et relancer `start.bat` pour se reconnecter avec le compte delegue.

### Etape 1.2 : Verifier les ressources existantes

**⚠️ OBLIGATOIRE avant toute creation :**

```bash
# Selectionner la souscription
az account list --query "[].{Nom:name, ID:id, Defaut:isDefault}" -o table
az account set --subscription "ID-de-la-souscription"

# Verifier les Translator existants (NE PAS CREER SI F0 EXISTE !)
az cognitiveservices account list --query "[?kind=='TextTranslation'].{Nom:name, SKU:sku.name, RG:resourceGroup}" -o table
```

**Si un Translator F0 existe** → utiliser celui-la, passer a l'etape 1.4

### Etape 1.3 : Creer les ressources Azure (seulement si necessaire)

**Translator** (seulement si aucun F0 n'existe) :
```bash
az cognitiveservices account create \
  --name "translator-$CLIENT_NAME" \
  --resource-group $RESOURCE_GROUP \
  --kind TextTranslation \
  --sku F0 \
  --location francecentral \
  --yes
```

> ⚠️ **TOUJOURS utiliser `--sku F0`** (gratuit). Ne JAMAIS utiliser S1 sauf demande explicite du client.

### Etape 1.4 : Recuperer les credentials du Translator

```bash
# Adapter TRANSLATOR_NAME au nom reel (existant ou nouvellement cree)
TRANSLATOR_KEY=$(az cognitiveservices account keys list \
  --name $TRANSLATOR_NAME \
  --resource-group $RESOURCE_GROUP \
  --query key1 -o tsv)

TRANSLATOR_ENDPOINT=$(az cognitiveservices account show \
  --name $TRANSLATOR_NAME \
  --resource-group $RESOURCE_GROUP \
  --query properties.endpoint -o tsv)
```

### Etape 1.5 : Configurer les variables d'environnement
Lors de la configuration de la Function App, inclure les variables OneDrive :

```bash
az functionapp config appsettings set \
  --name $FUNCTION_APP_NAME \
  --resource-group $RESOURCE_GROUP \
  --settings \
    "AZURE_ACCOUNT_NAME=$STORAGE_NAME" \
    "AZURE_ACCOUNT_KEY=$STORAGE_KEY" \
    "TRANSLATOR_KEY=$TRANSLATOR_KEY" \
    "TRANSLATOR_ENDPOINT=$TRANSLATOR_ENDPOINT" \
    "TRANSLATOR_REGION=$REGION" \
    "INPUT_CONTAINER=doc-to-trad" \
    "OUTPUT_CONTAINER=doc-trad" \
    "CLIENT_ID=$CLIENT_ID" \
    "SECRET_ID=$CLIENT_SECRET" \
    "TENANT_ID=$TENANT_ID" \
    "ONEDRIVE_UPLOAD_ENABLED=true" \
    "ONEDRIVE_FOLDER=Translated Documents"
```

---

## Variables d'environnement requises

### Azure Storage
- `AZURE_ACCOUNT_NAME` : Nom du Storage Account
- `AZURE_ACCOUNT_KEY` : Cle d'acces Storage Account

### Azure Translator
- `TRANSLATOR_KEY` : Cle API Translator
- `TRANSLATOR_ENDPOINT` : Endpoint Translator
- `TRANSLATOR_REGION` : Region (ex: francecentral)

### Containers Blob
- `INPUT_CONTAINER` : doc-to-trad (defaut)
- `OUTPUT_CONTAINER` : doc-trad (defaut)

### Microsoft Graph (OneDrive) - OBLIGATOIRE
- `CLIENT_ID` : ID de l'App Registration Entra
- `SECRET_ID` : Secret de l'App Registration
- `TENANT_ID` : ID du tenant client
- `ONEDRIVE_UPLOAD_ENABLED` : **true** (obligatoire pour sauvegarder les traductions)
- `ONEDRIVE_FOLDER` : Nom du dossier OneDrive (defaut: "Translated Documents")

---

## Permissions API requises pour l'App Entra

| Permission | Type | ID | Description |
|------------|------|-------|-------------|
| User.Read.All | Application | df021288-bdef-4463-88db-98f22de89214 | Lire les infos utilisateurs |
| Files.ReadWrite.All | Application | 01d4889c-1287-42c6-ac1f-5d1e02578ef6 | Lire/ecrire fichiers OneDrive |

---

## Rappel : Ordre des operations

1. **Lancer start.bat** avec Tenant ID client + compte **Admin Global client** -> Creer App Entra -> Noter CLIENT_ID, SECRET_ID, TENANT_ID
2. **exit + relancer start.bat** avec compte **delegue** -> Deployer ressources Azure -> Configurer Function App avec TOUTES les variables
3. **exit + relancer start.bat** avec compte **Admin client** -> Importer solution Power Platform

> **Note** : La connexion Azure se fait sur Windows (avec navigateur), puis les credentials sont partages avec le container automatiquement.
