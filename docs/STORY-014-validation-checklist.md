# STORY-014: Validation Interface Conversationnelle Française

**Story ID:** STORY-014
**Titre:** Interface Conversationnelle Française OpenCode
**Points:** 2
**Statut:** Validation
**Date:** 2026-01-18

## Objectif

Valider que l'interface conversationnelle d'OpenCode en français est claire, compréhensible et accessible pour un technicien Modern Workplace qui n'est pas expert Azure.

## Critères d'Acceptation à Valider

### ✅ AC1: OpenCode répond en français clair et compréhensible

**Implémentation:** conf_opencode/CLAUDE.md lignes 21-33, opencode.json ligne 4

**Test:** Lancer OpenCode et vérifier que toutes les réponses sont en français

**Checklist:**
- [ ] OpenCode démarre et affiche un message de bienvenue en français
- [ ] Les explications techniques sont en français
- [ ] Les confirmations sont en français
- [ ] Les messages d'erreur sont en français
- [ ] Les messages de succès sont en français

---

### ✅ AC2: Pas de termes techniques Azure sans explication

**Implémentation:** conf_opencode/CLAUDE.md lignes 222-227

**Test:** Demander à OpenCode d'expliquer des concepts Azure

**Checklist:**
- [ ] Quand OpenCode mentionne "Storage Account", il explique ce que c'est
- [ ] Quand OpenCode mentionne "SKU F0", il explique que c'est la version gratuite
- [ ] Quand OpenCode mentionne "Resource Group", il donne un exemple concret
- [ ] Les acronymes Azure sont expliqués lors de leur première utilisation
- [ ] Les commandes Azure CLI sont accompagnées d'une explication de leur but

**Exemple de dialogue à tester:**
```
Utilisateur: "Qu'est-ce qu'un Storage Account ?"
OpenCode: [Doit expliquer en français simple avec exemples]
```

---

### ✅ AC3: Confirmation demandée avant chaque action critique

**Implémentation:** conf_opencode/CLAUDE.md lignes 225, exemples 288-679

**Test:** Simuler des opérations de déploiement

**Checklist:**
- [ ] Avant de créer une ressource Azure, OpenCode demande confirmation
- [ ] Avant de modifier une configuration, OpenCode résume l'action
- [ ] Avant de supprimer une ressource, OpenCode demande double confirmation
- [ ] Le résumé de l'action est clair et compréhensible
- [ ] L'utilisateur peut refuser ou modifier l'action proposée

**Exemple de dialogue à tester:**
```
Utilisateur: "Déploie le Storage Account"
OpenCode: "Je vais créer un Storage Account avec ces paramètres:
- Nom: tradbotstorage123
- Région: France Central
- SKU: Standard_LRS (stockage local redondant)

Ça vous convient ? (oui/non)"
```

---

### ✅ AC4: Feedback positif quand une étape réussit

**Implémentation:** conf_opencode/CLAUDE.md lignes 226, 706-713

**Test:** Exécuter une commande qui réussit

**Checklist:**
- [ ] Quand une ressource est créée, OpenCode affiche un message de succès avec emoji ✅
- [ ] Quand une étape est terminée, OpenCode encourage avec "Parfait !" ou "Excellent !"
- [ ] Quand le déploiement progresse, OpenCode indique le nombre d'étapes restantes
- [ ] Les messages de succès sont motivants sans être excessifs
- [ ] OpenCode célèbre les jalons importants (ex: "🎉 Bravo ! Déploiement terminé.")

**Exemples attendus:**
```
✅ Parfait ! Storage Account créé avec succès.
✅ Excellent ! Vous progressez très bien.
🎉 Bravo ! Plus que 2 ressources à déployer.
```

---

### ✅ AC5: Messages d'erreur formatés "Problème: ... Solution: ..."

**Implémentation:** conf_opencode/CLAUDE.md lignes 170-198

**Test:** Provoquer des erreurs courantes

**Checklist:**
- [ ] Quand une erreur se produit, le format "❌ Problème: ... 💡 Solution: ..." est utilisé
- [ ] La description du problème est claire et en français
- [ ] La solution proposée est concrète et actionnable
- [ ] Les erreurs Azure sont traduites en langage compréhensible
- [ ] Les solutions incluent les étapes à suivre

**Exemples à tester:**

1. **Nom de ressource déjà utilisé:**
   ```
   ❌ Problème: Le nom "tradbot-storage" est déjà utilisé par un autre compte Azure.

   💡 Solution: Je vais générer un nouveau nom unique avec un suffixe aléatoire.
   ```

2. **Permission insuffisante:**
   ```
   ❌ Problème: Votre compte n'a pas la permission "Microsoft.Translator/create".

   💡 Solution: Contactez votre administrateur Azure pour obtenir le rôle "Contributor" sur le groupe de ressources.
   ```

3. **Région non disponible:**
   ```
   ❌ Problème: La région "westeurope" n'est pas disponible pour Azure Translator F0.

   💡 Solution: Je vais utiliser la région "francecentral" qui supporte le SKU F0 gratuit.
   ```

---

### 🧪 AC6: Tests utilisateur avec un technicien confirmant compréhensibilité

**Objectif:** Faire tester l'interface par un technicien Modern Workplace réel

**Profil du testeur:**
- Technicien Modern Workplace (M365, Teams, SharePoint)
- PAS expert Azure
- Français langue maternelle ou courant
- Familier avec PowerShell mais pas Azure CLI

**Scénario de test:**

1. **Démarrage du conteneur**
   - Exécuter `start.bat`
   - Observer les messages d'OpenCode
   - Évaluation: Les instructions sont-elles claires ?

2. **Déploiement guidé**
   - Demander: "Je veux déployer le bot traducteur"
   - Suivre les instructions d'OpenCode
   - Évaluation: Les étapes sont-elles compréhensibles sans documentation ?

3. **Gestion d'erreur**
   - Provoquer une erreur (nom déjà utilisé, permission manquante)
   - Observer comment OpenCode gère l'erreur
   - Évaluation: La solution proposée est-elle claire et applicable ?

4. **Questions techniques**
   - Demander: "C'est quoi un Storage Account ?"
   - Demander: "Pourquoi on utilise SKU F0 ?"
   - Évaluation: Les explications sont-elles compréhensibles sans jargon ?

**Grille d'évaluation:**

| Critère | Note (1-5) | Commentaires |
|---------|------------|--------------|
| Clarté du français | __ / 5 | |
| Compréhension des termes techniques | __ / 5 | |
| Confiance dans les confirmations | __ / 5 | |
| Motivation par les feedback positifs | __ / 5 | |
| Utilité des messages d'erreur | __ / 5 | |
| **Score global** | __ / 25 | |

**Seuil de validation:** Score global ≥ 20/25

**Questions ouvertes au testeur:**

1. Avez-vous compris toutes les étapes du déploiement ?
2. Y a-t-il des termes techniques qui vous ont bloqué ?
3. Les messages d'erreur vous ont-ils aidé à résoudre les problèmes ?
4. Vous sentez-vous capable de refaire le déploiement seul ?
5. Suggestions d'amélioration ?

---

## Validation Finale

**Date de validation:** _______________
**Validé par:** _______________
**Testeur utilisateur:** _______________

**Résultat:**
- [ ] Tous les critères AC1-AC5 sont validés techniquement
- [ ] Le test utilisateur AC6 obtient un score ≥ 20/25
- [ ] Aucun bug bloquant identifié
- [ ] La documentation est à jour

**Statut STORY-014:** ✅ COMPLETED

**Signature:** _______________
