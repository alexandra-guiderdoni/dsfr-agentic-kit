# Design tokens DSFR 1.15.3

Les tokens sont des **variables CSS** (`--…`) exposées au `:root` par
`dist/dsfr.min.css`. Ils se **consomment en CSS** (`color: var(--…)`), on ne
les émet pas en HTML : ce fichier est une **référence**, pas un générateur.
Frontière token/utilitaire/composant : voir `references/strate-artefact.md`.

Source de vérité : `:root` de `dist/dsfr.min.css` du paquet
`@gouvfr/dsfr@1.15.3`, consulté le 2026-08-28. La liste exhaustive vit dans le
paquet ; ce document en donne la **structure** et des exemples vérifiés.
Breakpoints, transitions et variables internes : voir
`references/tokens-advanced.md`.

## Couleurs sémantiques (recommandées)

Usage sémantique par rôle (fond / texte / bordure / artwork), chacune
déclinée par couleur Marianne. Préfixes vérifiés au `:root` :

- `--background-{alt,default,contrast,flat,raised,lifted,overlap,disabled,open,action-high,action-low,active}-{couleur}`
- `--text-{default,inverted,label,mention,title,action-high,active}-{couleur}`
- `--border-{default,plain,contrast,action-high,action-low,active,disabled,open}-{couleur}`
- `--artwork-{decorative,minor,major,motif,background}-{couleur}`

Exemple :

```css
.bandeau {
  background-color: var(--background-alt-blue-france); /* #f5f5fe clair, #1b1b35 sombre */
  color: var(--text-action-high-blue-france);          /* #000091 clair, #8585f6 sombre */
  border: 1px solid var(--border-default-grey);
}
```

Ne pas associer `--background-alt-blue-france` à `--text-inverted-blue-france` :
les deux valent `#f5f5fe` en thème clair (contraste 1:1). Les rôles `inverted`
sont faits pour un fond `action-high` ou `flat` de la même couleur.

Les rôles `action-high`, `active`, `hover` existent pour les états
interactifs (cf. déclinaisons `--text-action-high-*`, `--*-active`,
`--*-hover`).

## Couleurs brutes (échelles)

Variables de teintes brutes, sans rôle sémantique :

- Bleu France : `--blue-france-975-sun-113` (#f5f5fe en thème clair, #000091 en
  thème sombre : le premier nombre est la teinte claire, `sun-113` la teinte
  sombre), déclinaisons `-hover`/`-active`. Le bleu Marianne foncé en thème
  clair est `--blue-france-sun-113-625` (#000091 clair, #8585f6 sombre).
- Gris : `--grey-{N-M}` (ex. `--grey-925-125`, `--grey-200-850`,
  `--grey-1000-50`). Les déclinaisons `-hover`/`-active` n'existent que pour
  certaines échelles (`--grey-200-850-hover` oui, `--grey-925-125-hover` non) :
  vérifier au cas par cas dans `dist/dsfr.min.css`.
- Couleurs nommées, toujours avec leur échelle :
  `--red-marianne-425-625`, `--blue-cumulus-950-100`,
  `--green-emeraude-975-75`, etc. (palette Marianne complète, cf.
  `references/strate-artefact.md`).

Aucune teinte brute n'existe sous sa forme courte : `--grey`, `--blue-france`,
`--red-marianne`, `--blue-cumulus` et `--green-emeraude` ne sont déclarées
nulle part dans `dist/dsfr.min.css`. Écrire `var(--blue-france)` ne résout
rien, sans erreur ni avertissement : la couleur retombe sur l'héritage.

Préférez les **sémantiques** au brut : elles gèrent les thèmes clair/sombre.

## Espacement et typo

- `--title-spacing` : espacement associé aux titres.
- Échelle d'espacement : les utilitaires `fr-m-*` / `fr-p-*` (atom `spacing`)
  sont la forme HTML ; les variables brutes correspondantes vivent au `:root`
  (consulter le paquet pour la liste exhaustive `--*-spacing` / valeurs de pas).
- Typo : tailles `fr-text--{xs,sm,md,lg,xl,lead,…}` (atom `text`) ; les
  variables `--text-*` de taille/graisse sont au `:root`.

## Ombres (élévation)

Tokens d'élévation attestés au `:root` (valeurs thème clair vérifiées dans
`dist/dsfr.main.css`) :

- `--shadow-color: rgba(0, 0, 18, 0.16)` : couleur d'ombre de base
  (`rgba(0, 0, 18, 0.32)` en thème sombre).
- `--raised-shadow: 0 1px 3px var(--shadow-color)` : cartes, tuiles
  (élévation standard).
- `--overlap-shadow: 0 2px 6px var(--shadow-color)` : menus, modales
  (recouvrement).
- `--lifted-shadow: 0 3px 9px var(--shadow-color)` : éléments survolés
  (élévation forte).

Aucun token `--shadow` autonome : consommer l'un des quatre ci-dessus.

## Arrondis

**Aucun token `--radius-*`** n'est exposé au `:root`. Les arrondis sont codés
en dur par composant (`border-radius: 0.25rem`, `0.75rem`, `50%`, `0`…). Ne
pas écrire `var(--radius-*)` — la variable n'existe pas. **Pas** d'utilitaire
`fr-radius-*` non plus (cf. `references/strate-artefact.md`).

## Limites

- Aucune variable n'est inventée : seules les catégories attestées au `:root`
  sont listées. Pour une variable précise, vérifier dans `dist/dsfr.min.css`.
- Les tokens ne produisent rien en HTML statique : ce fichier est une
  référence de consommation.
- Version figée : 1.15.3.
