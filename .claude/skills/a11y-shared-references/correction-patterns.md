# Patterns de correction et verification

Reference partagee pour les skills appliquant des corrections WCAG.
Consulte par : a11y-loop, fix-accessibilite.

## Localisation du fichier source

Pour chaque violation, extraire le selecteur CSS et le snippet HTML du noeud affecte (`node.target`, `node.html`).

Chercher dans le repertoire source via `Grep` :
1. D'abord : snippet HTML exact (texte, classes, IDs)
2. Si non trouve : par ID (`id="..."`) ou classe specifique
3. Si non trouve : par balise + attributs partiels

### Gestion des frameworks

- **JSX/TSX** : `className` au lieu de `class`, syntaxe `{}` pour attributs
- **Vue SFC** : chercher dans `<template>`, `:class` pour bindings
- **Svelte** : syntaxe `class:nom` pour classes conditionnelles

Si fichier introuvable apres 3 tentatives : logger dans `skipped` et passer a la violation suivante.

## Patterns de correction (fallback)

Si le playbook (`resources/implementation-playbook.md`) est absent, utiliser ces patterns :

- **Contraste** : ajuster la luminosite HSL du foreground par pas de 1% jusqu'au ratio 4.5:1 (AA) ou 7:1 (AAA)
- **Alt manquant** : `<img alt="[description du contenu]" />` ou `<img alt="" />` si decoratif
- **Label manquant** : `<label for="[id]">[texte]</label>` avant le champ

## Application de la correction

Pour chaque fichier localise :
1. Lire le fichier via `Read`
2. Appliquer la correction via `Edit` en utilisant le pattern correspondant
3. Logger la correction : `{ file, line, rule_id, wcag, before, after, confidence }`

## Verification structurelle via @accesslint/mcp (prioritaire)

Apres chaque correction, utiliser `mcp__accesslint__diff_html` pour comparer le HTML avant/apres :
1. Passer le HTML original comme reference (`audit_html` avec un `name` unique)
2. Passer le HTML corrige a `diff_html` pour verifier qu'aucune nouvelle violation n'apparait
3. Si regression detectee : rollback de la correction via `Edit` et signaler a l'utilisateur

## Verification runtime via Chrome DevTools (complementaire)

Si mcp__chrome-devtools disponible (tester avec un appel `navigate_page` sur l'URL cible) :
1. Naviguer vers la page corrigee via `navigate_page`
2. Prendre un snapshot de l'arbre d'accessibilite via `take_snapshot`
3. Executer un script de verification contraste via `evaluate_script`
4. Comparer les resultats avec les violations corrigees
5. Si regression detectee (violation WCAG nouvelle ou ratio degrade) : rollback et signaler

Si aucun outil de verification disponible, passer directement au rapport en indiquant que la verification n'a pas ete effectuee.
