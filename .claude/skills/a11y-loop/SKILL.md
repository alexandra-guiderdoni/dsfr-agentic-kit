---
name: a11y-loop
description: "Utiliser quand une page web doit être corrigée en boucle scan-fix-verify WCAG avec Chrome DevTools, axe-core ou accesslint. Ne pas utiliser pour un audit seul, un correctif ponctuel ou une validation lecteur d'écran."
allowed-tools: Read, Write, Edit, Glob, Grep, Bash, mcp__chrome-devtools__navigate_page, mcp__chrome-devtools__take_snapshot, mcp__chrome-devtools__take_screenshot, mcp__chrome-devtools__evaluate_script, mcp__accesslint__audit_url, mcp__accesslint__audit_html, mcp__accesslint__diff_html
argument-hint: "[url] [--source dir] [--max-iterations 5] [--level AA|AAA] [--aggressive]"
context: conversation
---

# Boucle a11y

## Vue d'ensemble

`a11y-loop` orchestre une boucle courte : scanner une page, corriger le code
source, recharger, re-scanner, puis arrêter dès que le signal se dégrade ou
converge. Le skill vise les corrections WCAG mécaniques et prouvables ; il ne
remplace pas une revue RGAA humaine ni un test lecteur d'écran.

Le principe central : modifier le code source, jamais le DOM en direct, et
comparer chaque itération au scan précédent.

## Quand l'utiliser

| Situation | Décision |
|---|---|
| Page locale avec violations axe-core connues | Utiliser `a11y-loop` |
| Besoin de boucle scan-fix-verify jusqu'à convergence | Utiliser `a11y-loop` |
| Audit seul sans correction | Utiliser `audit-accessibilite-web` |
| Correctif ciblé depuis un rapport déjà produit | Utiliser `fix-accessibilite` |
| Validation finale lecteur d'écran ou parcours clavier expert | Utiliser `screen-reader-testing` |

## Arguments

| Argument | Défaut | Rôle |
|---|---|---|
| `url` | obligatoire | Page à auditer et recharger |
| `--source` | répertoire courant | Racine des fichiers modifiables |
| `--max-iterations` | `5` | Plafond strict de boucle |
| `--level` | `AA` | Niveau WCAG `AA` ou `AAA` |
| `--aggressive` | off | Autorise les corrections basse confiance |

Sans `url`, arrêter avec l'usage attendu. Ne jamais modifier un fichier hors
`--source`.

## Références à charger

Charger seulement les références nécessaires à l'étape courante :

- Scan axe-core et fallbacks : [../a11y-shared-references/axe-core-scan-patterns.md](../a11y-shared-references/axe-core-scan-patterns.md)
- Classification High/Low : [../a11y-shared-references/violation-classification.md](../a11y-shared-references/violation-classification.md)
- Localisation et corrections : [../a11y-shared-references/correction-patterns.md](../a11y-shared-references/correction-patterns.md)
- Playbook historique : [resources/implementation-playbook.md](resources/implementation-playbook.md)
- Règles locales : [references/classification-rules.md](references/classification-rules.md)

Les chemins sont relatifs au dossier du skill actif, donc valables côté
`.claude` et côté `.agents`.

## Pré-vol

1. Parser `url`, `--source`, `--max-iterations`, `--level` et `--aggressive`.
2. Ouvrir `url` avec Chrome DevTools ; arrêter si la page est inaccessible.
3. Vérifier que `--source` contient des fichiers HTML, CSS, JS, JSX, TSX, Vue
   ou Svelte.
4. Détecter le mode de rechargement : hot reload, build statique ou fichiers
   statiques.
5. Si le dossier est un dépôt Git, noter `git rev-parse HEAD` pour rollback.
6. Afficher les paramètres retenus avant le scan initial.

## Scan

Lire la référence de scan, puis utiliser la meilleure surface disponible :

1. `mcp__accesslint__audit_url` si disponible et adapté au besoin.
2. Chrome DevTools avec injection axe-core.
3. Fallback CLI `npx @axe-core/cli` si CSP ou injection impossible.

Stocker pour chaque itération :

- total des violations ;
- violations par impact ;
- paires stables `(id axe-core, sélecteur cible)` ;
- fragments utiles à la localisation source ;
- historique compact des deltas.

Si le scan initial retourne zéro violation, produire le rapport conforme et
arrêter.

## Classification

Classer chaque violation avant correction :

| Classe | Traitement |
|---|---|
| High | Correction mécanique autorisée |
| Low | Correction proposée seulement, sauf `--aggressive` ou itération >= 4 |
| Skipped | Cas non localisable, risqué ou hors périmètre |

Les corrections High typiques couvrent `image-alt`, `label`,
`color-contrast`, `html-has-lang`, `document-title`, `link-name`,
`button-name`, `frame-title` et `meta-viewport`.

Les corrections Low typiques couvrent ARIA complexe, clavier, ordre de focus,
hiérarchie de titres, landmarks, régions et `tabindex`.

## Correction

Pour chaque violation retenue :

1. extraire l'ID, le sélecteur, le snippet et la recommandation ;
2. localiser le fichier source par recherche ciblée ;
3. lire le fichier avant édition ;
4. modifier le code source avec la correction minimale ;
5. journaliser fichier, ligne, règle, confiance, avant et après.

NE PAS corriger dans le DOM via `evaluate_script`. NE PAS inventer un libellé
accessible métier sans indice dans la page ou le code. En cas de doute, noter la
limite et laisser la violation en manuel.

## Rechargement et comparaison

Après chaque série de corrections :

1. lancer le build si nécessaire ;
2. recharger la page ;
3. refaire le scan avec la même stratégie ou une stratégie documentée ;
4. comparer les paires `(id, sélecteur)`, pas seulement les IDs ;
5. utiliser `mcp__accesslint__diff_html` si disponible pour détecter les
   régressions structurelles.

Arrêts obligatoires :

| Signal | Action |
|---|---|
| Nouvelles violations ou diff HTML régressif | Arrêt immédiat, proposer rollback |
| Aucune baisse du total | Arrêt, suggérer `--aggressive` si pertinent |
| Zéro violation | Rapport `CONFORME` |
| `--max-iterations` atteint | Rapport `MAX ITERATIONS` |
| Build ou navigation échoue | Arrêt avec erreur et rollback possible |

## Rapport

Toujours produire `A11Y-LOOP-REPORT.md`, même en cas d'arrêt prématuré.

Le rapport doit contenir :

- URL, source, niveau WCAG, date, statut et nombre d'itérations ;
- tableau d'évolution des violations ;
- corrections appliquées avec fichier, règle, confiance, avant et après ;
- violations restantes et recommandations ;
- limites de scan et fallbacks utilisés ;
- prochaine étape selon le statut.

Statuts autorisés : `CONFORME`, `ARRÊT — régression`,
`ARRÊT — pas de progrès`, `MAX ITERATIONS`, `ERREUR`.

## Exemple

```text
/a11y-loop http://localhost:3000 --source ./src --max-iterations 3

Paramètres :
- URL : http://localhost:3000
- Source : ./src
- Niveau : AA
- Mode agressif : non

Scan initial : 12 violations
Itération 1 : 12 -> 4, aucune nouvelle violation
Itération 2 : 4 -> 2, aucune nouvelle violation
Itération 3 : 2 -> 2, arrêt sans progrès

Rapport généré : A11Y-LOOP-REPORT.md
Statut : ARRÊT — pas de progrès
```

## Pièges fréquents

| Piège | Correction |
|---|---|
| Corriger le DOM au lieu du code source | Modifier uniquement les fichiers sous `--source` |
| Comparer seulement les IDs axe-core | Comparer `(id, sélecteur)` pour détecter les nouvelles cibles |
| Continuer malgré une régression | Arrêter immédiatement et proposer rollback |
| Appliquer des Low trop tôt | Attendre `--aggressive` ou l'itération 4 |
| Charger toutes les références au départ | Charger la référence utile à l'étape courante |
| Oublier le rapport en cas d'erreur | Générer un rapport ou un reçu d'arrêt exploitable |

## Checklist finale

- [ ] Arguments parsés et paramètres affichés.
- [ ] URL ouverte et source vérifiée.
- [ ] Scan initial exécuté avec stratégie documentée.
- [ ] Violations classées High, Low ou Skipped.
- [ ] Corrections appliquées uniquement dans le code source.
- [ ] Rechargement et re-scan réalisés après chaque série.
- [ ] Comparaison par `(id, sélecteur)` effectuée.
- [ ] Arrêt déclenché en cas de régression ou absence de progrès.
- [ ] `--max-iterations` respecté.
- [ ] `A11Y-LOOP-REPORT.md` généré ou erreur bloquante explicitée.
- [ ] Résumé final donné à l'utilisateur avec limites non vérifiées.
