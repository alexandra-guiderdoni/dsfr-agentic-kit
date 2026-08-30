# Système de grille

Référence extraite de `../utilities.md`.

---

## Container
- `fr-container` : Container centré avec marges latérales
- `fr-container--fluid` : Container pleine largeur
- `fr-container-sm`, `fr-container-md`, `fr-container-lg`, `fr-container-xl` :
  même container, marges latérales appliquées à partir d'un point de rupture
  différent. Le suffixe n'est pas une largeur maximale.

Largeur maximale commune : 78 rem (1248 px), posée sur `fr-container` et sur
les quatre variantes dans `@media (min-width: 78em)`. Aucune des quatre
n'a de largeur propre.

Point de rupture à partir duquel les marges latérales s'appliquent (relevé
dans `dist/dsfr.css`) :

- `fr-container` : marges dès la plus petite largeur (1 rem), puis 1,5 rem à
  partir de 62 em
- `fr-container-sm` : 36 em (1 rem), puis 1,5 rem à partir de 62 em
- `fr-container-md` : 48 em (1 rem), puis 1,5 rem à partir de 62 em
- `fr-container-lg` : 62 em (1,5 rem)
- `fr-container-xl` : 78 em (1,5 rem)

Chaque variante a son pendant `--fluid` (`fr-container-sm--fluid`, etc.) qui
retire marges et largeur maximale.

## Lignes
- `fr-grid-row` : Ligne de la grille
- `fr-grid-row--gutters` : Ligne avec gouttières entre colonnes
- `fr-grid-row--no-gutters` : Ligne sans gouttières
- `fr-grid-row--center` : Ligne centrée horizontalement
- `fr-grid-row--right` : Ligne alignée à droite
- `fr-grid-row--middle` : Ligne centrée verticalement
- `fr-grid-row--bottom` : Ligne alignée en bas

## Colonnes
- `fr-col` : Colonne flexible
- `fr-col-1` à `fr-col-12` : Colonnes de largeur fixe (1/12 à 12/12)
- `fr-col-sm-*` : Colonnes à partir de 36 em (576 px à racine 16 px)
- `fr-col-md-*` : Colonnes à partir de 48 em (768 px à racine 16 px)
- `fr-col-lg-*` : Colonnes à partir de 62 em (992 px à racine 16 px)
- `fr-col-xl-*` : Colonnes à partir de 78 em (1248 px à racine 16 px)

## Décalages
- `fr-col-offset-*` : Décalage de colonne (1 à 12)
- `fr-col-offset-sm-*` : Décalage pour écrans small
- `fr-col-offset-md-*` : Décalage pour écrans medium
- `fr-col-offset-lg-*` : Décalage pour écrans large
- `fr-col-offset-xl-*` : Décalage pour écrans extra large
- `fr-col-offset-{breakpoint}-{n}--right` : Décalage vers la droite

Limite du skill : `generate_atom.py col` n'expose qu'un paramètre `offset`
global (1 à 11) et n'émet que `fr-col-offset-{n}`. Les décalages par point de
rupture (`fr-col-offset-md-4`, etc.) existent bien dans le paquet mais doivent
être écrits à la main.

## Grille en liste
Depuis DSFR 1.15.0 (#1452, #1467), `fr-grid-row` s'applique aussi à `<ul>` et
`<ol>` : le style neutralise puces et compteurs, les colonnes deviennent des
`<li class="fr-col-*">`. À préférer quand les colonnes forment une liste
sémantique (cartes, tuiles). `generate_atom.py grid` accepte `tag: "ul"` ou
`"ol"`.
```html
<ul class="fr-grid-row fr-grid-row--gutters">
    <li class="fr-col-12 fr-col-md-4">Première carte</li>
    <li class="fr-col-12 fr-col-md-4">Deuxième carte</li>
</ul>
```

`fr-grid-row--center` centre les colonnes par flexbox. Pour ancrer un contenu
sur la grille, utiliser les offsets `fr-col-offset-{breakpoint}-{n}` vérifiés
contre la version DSFR chargée. Avec le DSFR 1.15.2, la forme
`fr-col-lg-offset-*` est une classe morte : vérifier la syntaxe par grep du CSS
réel ou par computed style quand la version DSFR change.
