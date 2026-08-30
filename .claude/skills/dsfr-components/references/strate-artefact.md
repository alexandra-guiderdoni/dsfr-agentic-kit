# Table strate × artefact (DSFR 1.15.2)

Lève la frontière floue **token / utilitaire / composant** (retour validation
croisée #5 du PRD-140) pour décider, par besoin, quel générateur émet quoi — et
éviter les doublons (ex. « token couleur » vs « utilitaire background »).

Source de vérité : paquet `@gouvfr/dsfr@1.15.2` (`dist/component`,
`dist/utility/utility.css`, `:root` de `dist/dsfr.min.css`), consulté le
2026-07-07.

## Les trois strates

| Strate | Forme | Source paquet | Générateur du skill | Exemples |
| --- | --- | --- | --- | --- |
| Composant | markup complet (structure + ARIA) | `dist/component/*` | `generate_component.py` | `fr-card`, `fr-header`, `fr-accordion` |
| Atome utilitaire | élément portant une **classe** `fr-*` | `dist/utility/utility.css` + `dist/dsfr.min.css` | `generate_atom.py` | `fr-grid-row`, `fr-mt-4w`, `fr-text--lg`, `fr-background-alt--blue-france` |
| Token | **variable CSS** consommée dans votre CSS (`var(--…)`) | `:root` de `dist/dsfr.min.css` | `references/tokens.md` (référence, pas de générateur) | `--text-default-grey`, `--background-alt-blue-france`, `--blue-france-975-sun-113` |

Règle de frontière :
- un **token** est une valeur consommée en CSS (`color: var(--text-default-grey)`) ;
  on ne l'« émet » pas en HTML → **référence**.
- un **utilitaire** est une classe appliquée à un élément HTML → **atom**.
- un **composant** a sa propre structure sémantique → `generate_component.py`.

## Utilitaires réellement fournis par DSFR 1.15.2

Sourcé depuis `dist/utility/utility.css` + `dist/dsfr.min.css`. Le DSFR n'est
**pas** un framework utilitaire type Tailwind : beaucoup de classes
« attendues » n'existent pas.

| Catégorie | Existe ? | Classes officielles |
| --- | :---: | --- |
| Couleur de fond | oui | `fr-background-{action-high,action-low,alt,contrast,default,flat}--{couleur}` (107 classes) |
| Couleur de texte | oui | `fr-text-{action-high,default,inverted,label,mention,title}--{couleur}` (69 classes) |
| Grille / colonnage | oui | `fr-grid-row`, `fr-grid-row--*`, `fr-col-*` (atom `grid`/`col`) |
| Espacements | oui | `fr-m-*`, `fr-p-*` (atom `spacing`) |
| Taille de texte | oui | `fr-text--{xs,sm,md,lg,xl,lead,…}` (atom `text`/`lead`) |
| Titres / display | oui | `fr-h1`…`fr-h6`, `fr-display--{xs…xl}` (atom `title`) |
| Icônes | oui | `fr-icon-*` (atom `icon`) |
| Pictogrammes | oui (pointer) | `fr-artwork` + `<use>` (atom `pictogram`) |
| **Affichage** (`display`) | **partiel** | `fr-hidden[-sm/-md/-lg/-xl]`, `fr-unhidden[-sm/-md/-lg/-xl]` (10 classes, cf. `references/utilities/display.md`) ; `fr-d-block/flex/none/…` **absents** |
| **Flex** (justify/items/gap) | **non** | `fr-justify-*`, `fr-items-*`, `fr-gap-*` **absents** |
| **Alignement texte** | **non** | `fr-text-left/right/center` **absents** |
| **Position** | **non** | `fr-absolute/relative/position-*` **absents** |
| **Dépassement** (`overflow`) | **non** | `fr-overflow-*` **absent** |
| **Arrondi** (`radius`) | **non** | pas d'utilitaire `fr-radius-*` ; **aucun token `--radius-*`** non plus (arrondis codés en dur par composant) |
| **Ombre** (`shadow`) | **non** | pas d'utilitaire `fr-shadow-*` ; tokens `--raised-shadow` / `--overlap-shadow` / `--lifted-shadow` / `--shadow-color` (cf. `references/tokens.md`) |

Conséquence : l'atom `color` (P1.3) couvre les seuls utilitaires de couleur.
Pour masquer ou révéler un élément, y compris par point de rupture, employer
`fr-hidden*` / `fr-unhidden*` : ce sont des classes officielles, pas du CSS
personnel. Pour le reste de l'affichage, le positionnement ou l'arrondi,
utiliser du CSS personnel
(les arrondis sont codés en dur par composant — **pas de token `--radius-*`**)
ou les composants DSFR qui les intègrent. Pour l'ombre, consommer les tokens
attestés (`var(--raised-shadow)`, `var(--overlap-shadow)`, `var(--lifted-shadow)`).
Ne pas inventer de classes ni de tokens.

## Palette de couleurs Marianne (suffixe `--{couleur}`)

`blue-france`, `grey`, `beige-gris-galet`, `blue-cumulus`,
`blue-ecume`, `brown-cafe-creme`, `brown-caramel`, `brown-opera`,
`green-archipel`, `green-bourgeon`, `green-emeraude`, `green-menthe`,
`green-tilleul-verveine`, `orange-terre-battue`, `pink-macaron`, `pink-tuile`,
`purple-glycine`, `yellow-moutarde`, `yellow-tournesol`, plus les états
`info`, `success`, `warning`, `error`.

`red-marianne` fait exception depuis DSFR 1.15.0 : il n'est plus accepté en
suffixe de `background`, `text` ni `border`, seulement en `artwork`. Il reste
disponible comme variable CSS. Voir `references/utilities/colors.md`.
