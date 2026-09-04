# NC-TRANSVERSE-011 — Lien English content sans langue déclarée

**Statut** : Préqualification — NC confirmée dans les rapports sources  
**Référentiel** : RGAA 4.1.2  
**Sévérité** : Majeur  
**Justification de sévérité** : Une synthèse vocale française peut rendre cette destination moins compréhensible.  
**Date** : 2026-09-04  
**Composant / gabarit** : Navigation et liens éditoriaux  
**Portée** : Transverse — P02, P03, P04, P05, P06, P07, P08  
**Pages affectées** : P02, P03, P04, P05, P06, P07, P08  
**Constats sources regroupés** : 9

> Ces conclusions proviennent d’une préqualification instrumentée. Elles ne constituent ni un taux RGAA officiel ni une validation après correction.

---

## Pages et rapports sources

| Page | Nom | URL | Rapport RGAA |
|---|---|---|---|
| P02 | Plan du site | https://moa.douane.gouv.fr/plan-du-site | [P02-RGAA.html](../../RGAA/P02-RGAA.html) |
| P03 | Déclaration d’accessibilité | https://moa.douane.gouv.fr/pied-de-page/declaration-daccessibilite-du-portail-dounegouvfr | [P03-RGAA.html](../../RGAA/P03-RGAA.html) |
| P04 | Mentions légales | https://moa.douane.gouv.fr/mentions-legales | [P04-RGAA.html](../../RGAA/P04-RGAA.html) |
| P05 | Données personnelles | https://moa.douane.gouv.fr/pied-de-page/donnees-personnelles | [P05-RGAA.html](../../RGAA/P05-RGAA.html) |
| P06 | Formulaire Écrivez-nous | https://moa.douane.gouv.fr/formulaire-infos-douane-service | [P06-RGAA.html](../../RGAA/P06-RGAA.html) |
| P07 | Voyages à l’étranger | https://moa.douane.gouv.fr/particuliers/voyages-letranger | [P07-RGAA.html](../../RGAA/P07-RGAA.html) |
| P08 | Commerce international | https://moa.douane.gouv.fr/professionnels/commerce-international | [P08-RGAA.html](../../RGAA/P08-RGAA.html) |

## Références RGAA

- **Critère 8.7** — Dans chaque page web, chaque changement de langue est-il indiqué dans le code source (hors cas particuliers) ?
- **Test 8.7.1** — Dans chaque page web, chaque texte écrit dans une langue différente de la langue par défaut vérifie-t-il une de ces conditions (hors cas particuliers) ? L’indication de langue est donnée sur l’élément contenant le texte (attribut `lang` et/ou `xml:lang`) ; L’indication de langue est donnée sur un des éléments parents (attribut `lang` et/ou `xml:lang`)

---

## Code source constaté

### Intitulé anglais sans lang=en : English content

```html
<a href="/english-content" class="fr-nav__link" data-drupal-link-system-path="node/3812">English content</a>
```

## Inventaire des constats sources

| Page | Identifiant source | Critère / test | Sélecteur | Observation | Provenance | Preuve principale |
|---|---|---|---|---|---|---|
| P02 | `P02-RGAA-8-7-LANGUAGE-CHANGE-001-009` | 8.7 / 8.7.1 | `div.fr-grid-row.fr-grid-row-lg--gutters > div.fr-col-12.fr-col-lg-3:nth-of-type(5) > div.menu_link_content.menu-link-contentla-douane > ul.fr-mega-menu__list > li:nth-of-type(6) > a.fr-nav__link` | Intitulé anglais sans lang=en : English content | RENDERED_DOM | `rgaa/preuves/P02/attempt-002/raw-dom.json` |
| P02 | `P02-RGAA-8-7-LANGUAGE-CHANGE-001-013` | 8.7 / 8.7.1 | `div.fr-grid-row.fr-grid-row--gutters > div.fr-col-lg-4.fr-col-md-4:nth-of-type(4) > div.lexique-item > ul.sitemap-submenu > li:nth-of-type(6) > a.fr-link` | Intitulé anglais sans lang=en : English content | RENDERED_DOM | `rgaa/preuves/P02/attempt-002/raw-dom.json` |
| P02 | `P02-RGAA-8-7-LANGUAGE-CHANGE-001-014` | 8.7 / 8.7.1 | `div.fr-grid-row.fr-grid-row--gutters > div.fr-col-lg-4.fr-col-md-4:nth-of-type(10) > div.lexique-item > ul.sitemap-submenu > li:nth-of-type(6) > a.fr-link` | Intitulé anglais sans lang=en : English content | RENDERED_DOM | `rgaa/preuves/P02/attempt-002/raw-dom.json` |
| P03 | `P03-RGAA-8-7-LANGUAGE-CHANGE-001-009` | 8.7 / 8.7.1 | `div.fr-grid-row.fr-grid-row-lg--gutters > div.fr-col-12.fr-col-lg-3:nth-of-type(5) > div.menu_link_content.menu-link-contentla-douane > ul.fr-mega-menu__list > li:nth-of-type(6) > a.fr-nav__link` | Intitulé anglais sans lang=en : English content | RENDERED_DOM | `rgaa/preuves/P03/attempt-001/raw-dom.json` |
| P04 | `P04-RGAA-8-7-LANGUAGE-CHANGE-001-009` | 8.7 / 8.7.1 | `div.fr-grid-row.fr-grid-row-lg--gutters > div.fr-col-12.fr-col-lg-3:nth-of-type(5) > div.menu_link_content.menu-link-contentla-douane > ul.fr-mega-menu__list > li:nth-of-type(6) > a.fr-nav__link` | Intitulé anglais sans lang=en : English content | RENDERED_DOM | `rgaa/preuves/P04/attempt-001/raw-dom.json` |
| P05 | `P05-RGAA-8-7-LANGUAGE-CHANGE-001-010` | 8.7 / 8.7.1 | `div.fr-grid-row.fr-grid-row-lg--gutters > div.fr-col-12.fr-col-lg-3:nth-of-type(5) > div.menu_link_content.menu-link-contentla-douane > ul.fr-mega-menu__list > li:nth-of-type(6) > a.fr-nav__link` | Intitulé anglais sans lang=en : English content | RENDERED_DOM | `rgaa/preuves/P05/attempt-002/raw-dom.json` |
| P06 | `P06-RGAA-8-7-LANGUAGE-CHANGE-001-012` | 8.7 / 8.7.1 | `div.fr-grid-row.fr-grid-row-lg--gutters > div.fr-col-12.fr-col-lg-3:nth-of-type(5) > div.menu_link_content.menu-link-contentla-douane > ul.fr-mega-menu__list > li:nth-of-type(6) > a.fr-nav__link` | Intitulé anglais sans lang=en : English content | RENDERED_DOM | `rgaa/preuves/P06/attempt-004/raw-dom.json` |
| P07 | `P07-RGAA-8-7-LANGUAGE-CHANGE-001-010` | 8.7 / 8.7.1 | `div.fr-grid-row.fr-grid-row-lg--gutters > div.fr-col-12.fr-col-lg-3:nth-of-type(5) > div.menu_link_content.menu-link-contentla-douane > ul.fr-mega-menu__list > li:nth-of-type(6) > a.fr-nav__link` | Intitulé anglais sans lang=en : English content | RENDERED_DOM | `rgaa/preuves/P07/attempt-002/raw-dom.json` |
| P08 | `P08-RGAA-8-7-LANGUAGE-CHANGE-001-010` | 8.7 / 8.7.1 | `div.fr-grid-row.fr-grid-row-lg--gutters > div.fr-col-12.fr-col-lg-3:nth-of-type(5) > div.menu_link_content.menu-link-contentla-douane > ul.fr-mega-menu__list > li:nth-of-type(6) > a.fr-nav__link` | Intitulé anglais sans lang=en : English content | RENDERED_DOM | `rgaa/preuves/P08/attempt-001/raw-dom.json` |

---

## Analyse du défaut

Le lien « English content » est intégré dans des pages françaises sans attribut `lang="en"`. Il apparaît dans plusieurs emplacements rendus de P02 à P08. Il s’agit d’un passage anglais explicite et non d’un nom propre.

## Impact utilisateur

Une synthèse vocale française peut rendre cette destination moins compréhensible.

---

## Recommandations

### Solution 1 — Déclarer la langue du lien anglais (recommandée)

Ajouter `lang="en"` sur toutes les occurrences rendues du lien.

```html
<a href="/english-content" class="fr-nav__link" lang="en">
  English content
</a>
```

### Solution 2 — Fournir un intitulé français

Lorsque le contexte éditorial le permet, traduire l’intitulé du lien.

```html
<a href="/english-content" class="fr-nav__link">
  Contenus en anglais
</a>
```

## Comparaison avec le composant DSFR

**Composant concerné** : Navigation et liens éditoriaux

| Point contrôlé | DSFR / comportement attendu | Site audité |
|---|---|---|
| Passage anglais | Langue déclarée au plus près | Aucun lang=en |
| Occurrences | Configuration cohérente dans tous les menus | Libellé répété sans langue |
| Cause attribuée | Contenu paramétrable | Configuration éditoriale Drupal |

Le constat est attribué à l’intégration observée. La présence de classes `fr-*` ne suffit pas à attribuer le défaut au DSFR natif.

---

## Vérification après correction

- [ ] Rechercher « English content » dans P02 à P08.
- [ ] Vérifier chaque occurrence, y compris les variantes de navigation masquées puis ouvertes.
- [ ] Écouter le lien avec un lecteur d’écran configuré en français.

La correction ne doit être considérée comme clôturée qu’après production d’une nouvelle preuve et recontrôle humain.

## Références

- [RGAA 4.1.2 — test 8.7.1](https://accessibilite.numerique.gouv.fr/methode/criteres-et-tests/#8.7.1)
- [DSFR 1.15.2 — composant navigation](https://github.com/GouvernementFR/dsfr/tree/v1.15.2/src/dsfr/component/navigation)
- Source factuelle : rapports HTML RGAA livrés pour les pages indiquées et constats `NC_CONFIRMEE` correspondants.
