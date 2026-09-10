---
name: fix-accessibilite
description: "Utiliser après un audit accessibilité quand l'utilisateur demande de corriger des violations WCAG dans le code source. Ne pas utiliser pour auditer seul, lancer une boucle scan-fix ou tester au lecteur d'écran."
allowed-tools: Read, Glob, Grep, Bash, Edit, Write, WebFetch
argument-hint: "[fichier-rapport] [--scope all|color|aria|keyboard] [--auto-apply]"
context: conversation
---

# Remédiation d'accessibilité web

Corrige les violations WCAG détectées par `audit-accessibilite-web` en modifiant le code source fourni. Mode suggestif par défaut : les corrections à haute confiance sont appliquées, les autres sont proposées pour validation.

## Declencheurs

- "/fix-a11y", "corrige l'accessibilite", "applique les corrections WCAG"
- "remediation accessibilite", "fixe les violations"
- Toute demande de correction post-audit d'accessibilite

## Hors perimetre

- Audit d'accessibilité (utiliser `audit-accessibilite-web`)
- Tests avec lecteur d'écran (utiliser `screen-reader-testing`)
- Creation de tests automatises d'accessibilite
- Accessibilite native mobile (iOS/Android)

## Arguments

Les arguments sont passes via `$ARGUMENTS` :

```text
/fix-a11y rapport-audit.md
/fix-a11y rapport-audit.md --scope color
/fix-a11y rapport-audit.md --auto-apply
"corrige les violations de contraste dans rapport-audit.md"
"applique toutes les corrections y compris les Low"
```

| Argument | Description | Defaut |
|----------|-------------|--------|
| `fichier-rapport` | Rapport généré par `audit-accessibilite-web` | obligatoire |
| `--scope` (ou "seulement les couleurs", "uniquement ARIA") | Filtrer par type : all, color, aria, keyboard, semantic | all |
| `--auto-apply` (ou "applique tout") | Appliquer aussi les corrections Low (sans confirmation) | off |

Si le fichier rapport est manquant, afficher une ERREUR avec le format d'utilisation et arreter.

## Classification des corrections

Lire [violation-classification](../a11y-shared-references/violation-classification.md) pour les définitions High/Low, la priorité par sévérité et les règles détaillées. En résumé : High = corrections mécaniques (contraste, alt, lang, labels), Low = corrections nécessitant jugement (ARIA, clavier, sémantique). En cas d'ambiguïté, classifier comme Low.

## Workflow

### Prerequis

- Fichier rapport généré par `audit-accessibilite-web` ou fourni manuellement dans un format compatible (tableau avec critère WCAG, sévérité, élément, fichier)
- Fichier `resources/implementation-playbook.md` (optionnel, enrichit les patterns de base avec la formule de contraste detaillee et des exemples supplementaires). Si absent, les patterns de fallback ci-dessous sont autonomes et suffisants. Structure attendue :
  ```
  fix-accessibilite/
  ├── SKILL.md
  └── resources/
      └── implementation-playbook.md
  ```

**Patterns de fallback** (si playbook absent) : voir [correction-patterns](../a11y-shared-references/correction-patterns.md) section "Patterns de correction (fallback)".

### Phase 1 : chargement du rapport

- Verifier l'existence du fichier rapport et du playbook de remediation
- Parser `$ARGUMENTS` : le premier argument positionnel (`$0`) est le fichier rapport, les flags `--scope` et `--auto-apply` sont optionnels
- Lire le fichier rapport et extraire les violations avec critere WCAG, severite, element concerne et fichier source
- Filtrer par `--scope` si specifie
- Si plus de 50 violations, proposer un traitement par lots ou par `--scope`

### Phase 2 : classification

- Attribuer un niveau de confiance (High/Low) a chaque violation selon le tableau ci-dessus
- Trier par severite decroissante (critique > serieux > modere > mineur)
- Presenter le plan de remediation a l'utilisateur

### Phase 3 : remediation

Pour chaque violation, dans l'ordre de severite :

1. Localiser le fichier source et le snippet concerne (Glob + Grep)
2. Expliquer la violation et le critere WCAG
3. Si **High** : appliquer la correction via Edit, documenter le changement
4. Si **Low** : consigner la correction proposee dans le rapport FIX-REPORT.md avec avertissement "non-verifie en runtime" (l'utilisateur peut relancer avec `--auto-apply` pour appliquer les Low)
5. Pour les violations de contraste : utiliser la formule de luminance relative (consulter [implementation-playbook](resources/implementation-playbook.md) (si disponible)). Si playbook absent, utiliser le fallback contraste defini dans les Prerequis

### Phase 4 : verification

Lire [correction-patterns](../a11y-shared-references/correction-patterns.md) sections "Vérification structurelle via @accesslint/mcp" et "Vérification runtime via Chrome DevTools" pour les procédures détaillées.

Si ni @accesslint/mcp ni chrome-devtools ne sont disponibles, passer directement a la Phase 5 en indiquant dans le rapport que la verification n'a pas ete effectuee.

### Phase 5 : resume et rapport de suivi

Generer le fichier `FIX-REPORT.md` dans le repertoire courant avec :

- **Corrections appliquees (High)** : critere, fichier, ligne, avant/apres
- **Suggestions en attente (Low)** : critere, fichier, suggestion, risque
- **Decisions humaines requises** : critere, probleme, options proposees

Consulter [implementation-playbook](resources/implementation-playbook.md) (si disponible) pour le template complet du rapport et les patterns de correction.

## Contraintes

- TOUJOURS expliquer chaque correction avant de l'appliquer
- TOUJOURS avertir que les corrections Low ne sont pas verifiees en runtime
- TOUJOURS proposer un rollback si la correction echoue
- Les corrections Low sont consignees dans le rapport sans attendre de validation. L'utilisateur peut relancer avec `--auto-apply` pour les appliquer
- JAMAIS modifier le rapport d'audit original (creer un fichier de suivi separe)
- Si le rapport contient plus de 50 violations, proposer un traitement par lots ou par `--scope` pour eviter l'explosion du contexte

## Gestion des erreurs

| Scenario | Comportement |
|----------|-------------|
| Rapport introuvable | Demander le chemin correct |
| Fichier source introuvable | Signaler, passer a la violation suivante |
| Conflit de correction | Expliquer le conflit, demander decision |
| Contraste impossible a atteindre | Proposer alternatives (changer background ou accepter teinte differente) |
| Format de rapport non reconnu | Signaler le format attendu (tableau critere/severite/element/fichier), proposer un parsing best-effort ou abandonner |

## Exemples d'utilisation

### Exemple 1 : remediation complete

```text
Utilisateur : /fix-a11y rapport-wcag.md

Assistant :
> Phase 1 : 12 violations extraites du rapport
> Phase 2 : 8 High, 4 Low
>
> Phase 3 : Remediation
> [High] [1.1.1] img sans alt dans Hero.tsx:25 -> alt="Banner principal" applique
> [High] [1.4.3] .nav-link 2.8:1 -> #595959 (4.6:1) dans Nav.tsx:42 applique
> [High] [3.1.1] html sans lang dans index.html:1 -> lang="fr" applique
> ... 5 autres corrections High appliquees
>
> [Low] [2.1.1] Dropdown non accessible au clavier dans Menu.tsx:68
>   Correction proposée : ajouter onKeyDown avec ArrowUp/ArrowDown
>   Risque : non vérifié en runtime. Appliquer ? (o/n)
>
> Phase 5 : FIX-REPORT.md genere
> 8/8 High appliquees, 1/4 Low validees, 3 Low en attente
```

### Exemple 2 : scope contraste uniquement

```text
Utilisateur : /fix-a11y rapport-wcag.md --scope color

Assistant :
> 4 violations contraste (High) -> 4/4 appliquees
> [1.4.3] .nav-link 2.8:1 -> #595959 (4.6:1) dans Nav.tsx:42
> [1.4.3] .subtitle 3.1:1 -> #4A4A4A (4.8:1) dans Hero.tsx:18
> [1.4.3] .footer-text 3.5:1 -> #525252 (4.5:1) dans Footer.tsx:31
> [1.4.11] .btn-outline border 2.2:1 -> #666666 (3.1:1) dans Button.tsx:12
```

### Exemple 3 : mode auto-apply avec corrections Low

```text
Utilisateur : /fix-a11y rapport-wcag.md --auto-apply

Assistant :
> Phase 1 : 15 violations extraites
> Phase 2 : 10 High, 5 Low (--auto-apply : toutes seront appliquees)
>
> Phase 3 : Remediation
> [High] 10/10 appliquees
> [Low] [4.1.2] rôle="combobox" ajouté sur Select.tsx:34 (auto-apply)
> [Low] [2.4.3] tabindex corrige sur Modal.tsx:12 (auto-apply)
> ... 3 autres Low appliquees
>
> Phase 4 : Verification @accesslint
> Régression détectée : [4.1.2] aria-expanded manquant sur Select.tsx:34
> -> Rollback applique sur Select.tsx:34, signale dans le rapport
>
> Phase 5 : FIX-REPORT.md généré
> 10 High appliquees, 4/5 Low appliquees, 1 Low rollback (regression)
```

## Pièges fréquents

- NE PAS modifier le rapport d'audit original.
- NE PAS appliquer une correction Low comme si elle était vérifiée en runtime.
- JAMAIS déclarer la correction terminée sans rapport de suivi.
- Hors périmètre : lancer un nouvel audit complet au lieu de traiter le rapport fourni.

## Checklist finale

- [ ] Rapport d'audit charge et violations extraites
- [ ] Chaque violation classifiee (High/Low)
- [ ] Plan de remediation presente a l'utilisateur
- [ ] Corrections High appliquees avec explication prealable
- [ ] Corrections Low proposees avec avertissement runtime
- [ ] Verification optionnelle executee (si chrome-devtools disponible)
- [ ] Rapport de suivi FIX-REPORT.md genere avec les 3 sections
- [ ] Corrections Low consignees dans le rapport (appliquees uniquement si --auto-apply)
- [ ] Erreurs de fichier source ou conflits traites et signales
- [ ] Rapport d'audit original non modifie
