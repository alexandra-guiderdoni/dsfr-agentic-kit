# Typographie

Référence extraite de `../utilities.md`.

---

## Polices officielles
- **Marianne** : Police principale (textes, titres, interface). Distribuée avec le DSFR.
- **Spectral** : Police serif pour le contenu éditorial long (articles, rapports). Optionnelle.

**Attention** : ces polices ne sont PAS librement distribuables en dehors du cadre de la charte de l'État. Utiliser uniquement via le CDN DSFR ou le package npm.

## Titres (headings)

Le DSFR déclare des interlignages en rem, pas en ratio, et la bascule
desktop se fait à `@media (min-width: 48em)`. Valeurs relevées dans
`dist/dsfr.min.css` du paquet 1.15.3, sous la forme
`taille / interlignage` :

| Classe | Desktop (≥ 48em) | Mobile |
|--------|------------------|--------|
| `fr-h1` / `<h1>` | 2.5rem / 3rem | 2rem / 2.5rem |
| `fr-h2` / `<h2>` | 2rem / 2.5rem | 1.75rem / 2.25rem |
| `fr-h3` / `<h3>` | 1.75rem / 2.25rem | 1.5rem / 2rem |
| `fr-h4` / `<h4>` | 1.5rem / 2rem | 1.375rem / 1.75rem |
| `fr-h5` / `<h5>` | 1.375rem / 1.75rem | 1.25rem / 1.75rem |
| `fr-h6` / `<h6>` | 1.25rem / 1.75rem | 1.125rem / 1.5rem |

Le ratio n'est donc pas constant : il va de 1,2 (`fr-h1` desktop) à 1,4
(`fr-h5` mobile, `fr-h6` desktop). Deux couples seulement valent 1,25
(`fr-h1` mobile et `fr-h2` desktop) : ne pas reprendre un
`line-height: 1.25` global dans du CSS projet, le rythme vertical
différerait de celui du DSFR.

**Note** : Les classes `fr-h*` permettent d'appliquer le style d'un titre sans changer le niveau sémantique.

## Tailles de texte
- `fr-text--xs` : Très petit (0.75rem / 12px)
- `fr-text--sm` : Petit (0.875rem / 14px)
- `fr-text--md` : Moyen (1rem / 16px) — par défaut
- `fr-text--lg` : Grand (1.125rem / 18px)
- `fr-text--xl` : Très grand (1.25rem / 20px)
- `fr-text--lead` : Texte d'introduction (1.25rem, line-height 2rem,
  ratio 1,6) — déclaration partagée avec `fr-text--xl`

## Display (titres décoratifs)

Deux valeurs par classe, comme pour les titres : bascule à
`@media (min-width: 48em)`, sous la forme `taille / interlignage`.

- `fr-display--xs` : mobile 2.5rem / 3rem, desktop 3rem / 3.5rem
- `fr-display--sm` : mobile 3rem / 3.5rem, desktop 3.5rem / 4rem
- `fr-display--md` : mobile 3.5rem / 4rem, desktop 4rem / 4.5rem
- `fr-display--lg` : mobile 4rem / 4.5rem, desktop 4.5rem / 5rem
- `fr-display--xl` : mobile 4.5rem / 5rem, desktop 5rem / 5.5rem

## Poids de texte
- `fr-text--light` : Léger (300)
- `fr-text--regular` : Normal (400) — par défaut
- `fr-text--bold` : Gras (700)
- `fr-text--heavy` : Très gras (900)

## Alignement, transformation et décoration

Le paquet `@gouvfr/dsfr@1.15.3` local ne fournit pas de classes attestées
`fr-text--left`, `fr-text--center`, `fr-text--uppercase`,
`fr-text--underline` ou équivalentes. Ne pas inventer ces utilitaires :
utiliser la grille DSFR, les composants natifs ou du CSS projet vérifié quand
un alignement, une casse ou une décoration de texte est nécessaire.

## Styles de liste

Aucun utilitaire de liste n'est fourni par le paquet `@gouvfr/dsfr@1.15.3`
(`fr-list--no-marker` n'existe pas ; vérifié dans `dist/dsfr.min.css`). Pour une
liste sans puces, utiliser du CSS projet vérifié (`list-style: none`) ou un
composant DSFR approprié.
