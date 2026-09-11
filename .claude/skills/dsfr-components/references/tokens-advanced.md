# Tokens avancés DSFR 1.15.3

Complément de `references/tokens.md` : ombres, arrondis, transitions et
breakpoints. Source de vérité : `:root` et composants de
`@gouvfr/dsfr@1.15.3/dist/dsfr.main.css`, consulté le 2026-08-28.

Ce fichier est une **référence de consommation** (CSS `var(--…)`), pas un
générateur : on n'émet aucun token en HTML. Aucune variable listée ici n'est
inventée — toute affirmation non attestée au paquet est marquée comme limite.

---

## Ombres (élévation)

Les quatre tokens d'élévation (`--shadow-color`, `--raised-shadow`,
`--overlap-shadow`, `--lifted-shadow`) et leurs valeurs vérifiées vivent dans
`references/tokens.md` afin de garder une source unique. Aucun token
`--shadow` autonome et aucun token `--flat-shadow` n'existent dans le paquet.

---

## Arrondis (border-radius)

**Aucun token `--radius-*`** n'est exposé au `:root`. Les arrondis sont codés
en dur par composant. Relevé exhaustif des 34 règles `border-radius` de
`dist/dsfr.min.css`, sélecteur par sélecteur :

- `.fr-badge` : `0.25rem`
- `.fr-input`, `.fr-select` : `0.25rem 0.25rem 0 0` (deux coins hauts
  seulement)
- `.fr-tag` : `1rem` ; `.fr-tag--sm` et les tags des variantes `--sm`
  (`.fr-card--sm`, `.fr-tile--sm`, `.fr-tags-group--sm`) : `0.75rem`
- `.fr-segmented__elements` et `.fr-segmented input~label` : `0.25rem`
- `.fr-checkbox-group input[type=checkbox]~label:before` : `0.25rem`
  (`~.fr-label:before` : `4px`)
- `.fr-radio-group input[type=radio]~label:before` : `1.5rem` ;
  `.fr-radio-group--sm` : `0.5rem` ; `.fr-radio-rich` : `0`
- `.fr-toggle label:before` : `0.75rem` ; `.fr-toggle label:after` : `50%`
- `.fr-quote__image` : `50%`
- `.fr-range` : pistes `0.375rem` (`0.25rem` en `--sm`), curseurs
  (`::-webkit-slider-thumb`, `::-moz-range-thumb`, `::-ms-thumb`) : `50%`
- `.fr-search-bar .fr-btn` : `0 0.25rem 0 0` ; `.fr-search-bar .fr-input` :
  `0.25rem 0 0`
- `.fr-input-wrap--addon` : `0.25rem 0 0 0` sur le premier enfant,
  `0 0.25rem 0 0` sur le dernier
- `.fr-follow__newsletter .fr-input-wrap .fr-input` : `0.25rem 0.25rem 0 0`,
  puis `0.25rem 0 0 0` ; le `.fr-btn` du même bloc : `0`, puis
  `0 0.25rem 0 0`
- `input`, `select`, `textarea` : `0` (remise à plat de base du navigateur)

Aucune règle `border-radius` ne cible `.fr-btn` en général, ni un sélecteur
contenant `modal`, ni `.fr-card` lui-même. Le DSFR n'a ni composant avatar ni
pictogramme rond : les `50%` relevés appartiennent aux trois sélecteurs
ci-dessus.

**Règle** : le DSFR est sobre sur les arrondis. Ne pas écrire
`var(--radius-*)` (la variable n'existe pas), ni ajouter de `border-radius`
custom sur les composants DSFR.

---

## Transitions et animations

Le DSFR **n'expose pas de token public** de durée ou de courbe
(`--duration`, `--easing` n'existent pas au `:root`). Les transitions sont
codées en dur dans le SCSS de chaque composant.

| Composant | Animation gérée par le JS DSFR |
| --- | --- |
| Accordéon | Ouverture/fermeture du contenu |
| Modale | Apparition avec overlay |
| Navigation | Déroulement des sous-menus |
| Onglets | Transition entre panneaux |
| Toggle | Glissement du curseur |
| Alerte fermable | Disparition |

Le JavaScript DSFR (`dsfr.min.js`) pilote toutes les animations. Ne pas
ajouter de CSS `transition` custom sur les composants DSFR.

---

## Variables internes des composants

Chaque composant utilise des variables internes préfixées (non énumérées
ici). **Ces variables ne sont pas une API publique** : elles ne sont pas
documentées comme stables et peuvent changer entre versions mineures. Ne pas
les surcharger. Pour personnaliser, utiliser les classes utilitaires et les
tokens publics (`references/tokens.md`), pas les variables internes.

---

## Points de rupture (breakpoints)

Le DSFR exprime ses media queries en **`em`** (et non en `px`) afin de
respecter la taille de police de l'utilisateur. Valeurs attestées dans
`dist/dsfr.main.css` :

| Nom | Media query DSFR | Équivalent (root 16px) | Usage |
| --- | --- | --- | --- |
| `sm` | `36em` | 576px | Mobile paysage |
| `md` | `48em` | 768px | Tablette |
| `lg` | `62em` | 992px | Desktop |
| `xl` | `78em` | 1248px | Grand écran |

Le DSFR est mobile-first : les utilitaires `fr-col-*` s'appliquent par défaut,
puis `fr-col-{sm,md,lg,xl}-*` à partir du breakpoint correspondant.

```css
/* Tablette et plus — utiliser em comme le DSFR, pas px.
   Le sélecteur est applicatif : ne jamais redéfinir une classe fr-*. */
@media (min-width: 48em) {
  .mon-bloc { width: 50%; }
}
```

Les breakpoints ne sont **pas** modifiables via CSS. Préférer `em` à `px` dans
le CSS personnel pour rester cohérent avec le comportement accessible du
DSFR (les équivalents px supposent une racine à 16px).

---

## Bonnes pratiques

1. Ne pas surcharger les variables internes du DSFR — utiliser les classes
   utilitaires et les tokens publics.
2. Consommer les tokens de couleur (`--background-*`, `--text-*`) plutôt que
   des valeurs hex.
3. Respecter les breakpoints du DSFR pour la cohérence responsive.
4. Pas de `!important` sur les classes `fr-*`.
5. Pas de CSS custom qui écrase le comportement des composants DSFR.
