# Espacements

Référence extraite de `../utilities.md`.

---

## Échelle des valeurs

L'échelle n'est pas une liste courte, c'est une règle. Relevé dans
`dist/dsfr.min.css` du paquet 1.15.3, identique pour les quatorze préfixes
(`fr-m`, `fr-mt`, `fr-mb`, `fr-ml`, `fr-mr`, `fr-mx`, `fr-my` et leurs
équivalents `fr-p*`) :

- unité `v` : 0,25 rem par cran, de `1v` à `32v` (`fr-m-32v` vaut 8 rem)
- unité `w` : 0,5 rem par cran, de `1w` à `16w` (`fr-m-8w` vaut 4 rem) —
  l'échelle `w` s'arrête à 16 : `fr-mb-30w` n'existe pas
- demi-crans : `0-5v` (0,125 rem) et `1-5v` (0,375 rem)
- `0` : aucun espacement ; `auto` : marges automatiques (marges seulement)
- marges négatives, préfixe `n` : `n1v` à `n8v`, `n1w` à `n4w`, plus `n0-5v`
  et `n1-5v` (aucun padding négatif)
- variantes par point de rupture : `fr-m{direction}-{sm,md,lg,xl}-{valeur}`
  (par exemple `fr-mb-md-4v`)

`fr-mb-4v` et `fr-mt-11w` sont donc valides, contrairement à ce que
suggérerait une liste figée.

Limite du skill : `generate_atom.py spacing` borne `size` à 0-32 quelle que
soit l'unité. Une valeur `w` supérieure à 16 sort une classe inexistante avec
un code de retour nul (`fr-mb-30w`) : vérifier la borne de l'unité `w` à la
main.

## Marges (margin)
### Toutes directions
- `fr-m-*` : Marge sur tous les côtés

### Horizontales
- `fr-mx-*` : Marges gauche et droite
- `fr-ml-*` : Marge gauche uniquement
- `fr-mr-*` : Marge droite uniquement

### Verticales
- `fr-my-*` : Marges haut et bas
- `fr-mt-*` : Marge haut uniquement
- `fr-mb-*` : Marge bas uniquement

## Paddings (padding)
### Toutes directions
- `fr-p-*` : Padding sur tous les côtés
  - Mêmes valeurs que les marges, sans `auto` ni valeurs négatives

### Horizontales
- `fr-px-*` : Paddings gauche et droite
- `fr-pl-*` : Padding gauche uniquement
- `fr-pr-*` : Padding droite uniquement

### Verticales
- `fr-py-*` : Paddings haut et bas
- `fr-pt-*` : Padding haut uniquement
- `fr-pb-*` : Padding bas uniquement

## Repères de conversion (extrait)

Extrait de l'échelle, pas la liste complète : voir la règle de composition
ci-dessus.

- `*-0` : 0
- `*-0-5v` : 0.125rem
- `*-1v` : 0.25rem
- `*-1w` : 0.5rem
- `*-2w` : 1rem
- `*-3w` : 1.5rem
- `*-4w` : 2rem
- `*-5w` : 2.5rem
- `*-6w` : 3rem
- `*-8w` : 4rem
- `*-16w` : 8rem (dernier cran `w`)
- `*-32v` : 8rem (dernier cran `v`)
