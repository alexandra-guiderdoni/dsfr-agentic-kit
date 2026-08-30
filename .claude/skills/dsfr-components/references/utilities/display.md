# Affichage

Référence extraite de `../utilities.md`.

---

## Display CSS

Les classes `fr-display--xs` à `fr-display--xl` listées dans
[typographie](typography.md) sont des styles typographiques, pas des
utilitaires CSS `display`. Le paquet `@gouvfr/dsfr@1.15.2` local ne fournit
pas `fr-display--none`, `fr-display--block`, `fr-display--flex` ou
`fr-display--inline-flex`. Pour le display, utiliser la grille DSFR ou du CSS
projet vérifié.

## Visibilité responsive
Classes cœur DSFR attestées dans le paquet local :

- `fr-hidden` : Toujours masqué
- `fr-hidden-sm` : Masqué sur small et plus
- `fr-hidden-md` : Masqué sur medium et plus
- `fr-hidden-lg` : Masqué sur large et plus
- `fr-hidden-xl` : Masqué sur extra large

## Visibilité par breakpoint
- `fr-unhidden-sm` : Visible sur small et plus
- `fr-unhidden-md` : Visible sur medium et plus
- `fr-unhidden-lg` : Visible sur large et plus
- `fr-unhidden-xl` : Visible sur extra large
