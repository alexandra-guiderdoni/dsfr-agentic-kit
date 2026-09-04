# A-REQUALIFIER-RGAA-004 — Libellés French Customs à requalifier comme noms propres

**Statut** : À requalifier avant transmission comme non-conformité  
**Référentiel** : RGAA 4.1.2  
**Sévérité** : Majeur  
**Justification de sévérité** : Sans langue déclarée, une synthèse vocale française peut appliquer une prononciation inadaptée ; l’applicabilité RGAA reste à arbitrer.  
**Date** : 2026-09-04  
**Composant / gabarit** : Navigation et liens éditoriaux  
**Portée** : Transverse — P02, P03, P04, P05, P06, P07  
**Pages affectées** : P02, P03, P04, P05, P06, P07  
**Constats sources regroupés** : 21

> Ces conclusions proviennent d’une préqualification instrumentée. Elles ne constituent ni un taux RGAA officiel ni une validation après correction.

> **Alerte méthodologique :** Le test 8.7.1 exclut notamment les noms propres. Il faut décider éditorialement si « French Customs » est un nom de service ou de rubrique à traiter comme nom propre avant de maintenir ces constats en NC.

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

## Références RGAA

- **Critère 8.7** — Dans chaque page web, chaque changement de langue est-il indiqué dans le code source (hors cas particuliers) ?
- **Test 8.7.1** — Dans chaque page web, chaque texte écrit dans une langue différente de la langue par défaut vérifie-t-il une de ces conditions (hors cas particuliers) ? L’indication de langue est donnée sur l’élément contenant le texte (attribut `lang` et/ou `xml:lang`) ; L’indication de langue est donnée sur un des éléments parents (attribut `lang` et/ou `xml:lang`)

---

## Code source constaté

### Intitulé anglais sans lang=en : French Customs for business

```html
<a href="/professionnels/french-customs-business" class="fr-nav__link">
							French Customs for business
						</a>
```

### Intitulé anglais sans lang=en : French Customs presentation

```html
<a href="/professionnels/french-customs-business/french-customs-presentation" class="fr-nav__link">
										French Customs presentation
									</a>
```

## Inventaire des constats sources

| Page | Identifiant source | Critère / test | Sélecteur | Observation | Provenance | Preuve principale |
|---|---|---|---|---|---|---|
| P02 | `P02-RGAA-8-7-LANGUAGE-CHANGE-001-006` | 8.7 / 8.7.1 | `div.fr-collapse.fr-mega-menu > div.fr-container.fr-container--fluid > div.fr-grid-row.fr-grid-row-lg--gutters:nth-of-type(1) > div.fr-col-12.fr-col-lg-3:nth-of-type(13) > h5.fr-mega-menu__category > a.fr-nav__link` | Intitulé anglais sans lang=en : French Customs for business | RENDERED_DOM | `rgaa/preuves/P02/attempt-002/raw-dom.json` |
| P02 | `P02-RGAA-8-7-LANGUAGE-CHANGE-001-007` | 8.7 / 8.7.1 | `div.fr-container.fr-container--fluid > div.fr-grid-row.fr-grid-row-lg--gutters:nth-of-type(1) > div.fr-col-12.fr-col-lg-3:nth-of-type(13) > ul.fr-mega-menu__list > li:nth-of-type(1) > a.fr-nav__link` | Intitulé anglais sans lang=en : French Customs presentation | RENDERED_DOM | `rgaa/preuves/P02/attempt-002/raw-dom.json` |
| P02 | `P02-RGAA-8-7-LANGUAGE-CHANGE-001-008` | 8.7 / 8.7.1 | `div.fr-container.fr-container--fluid > div.fr-grid-row.fr-grid-row-lg--gutters:nth-of-type(1) > div.fr-col-12.fr-col-lg-3:nth-of-type(13) > ul.fr-mega-menu__list > li:nth-of-type(2) > a.fr-nav__link` | Intitulé anglais sans lang=en : French Customs for business | RENDERED_DOM | `rgaa/preuves/P02/attempt-002/raw-dom.json` |
| P02 | `P02-RGAA-8-7-LANGUAGE-CHANGE-001-010` | 8.7 / 8.7.1 | `li.fr-mb-8v:nth-of-type(2) > section.globallisteThematique > div.fr-grid-row.fr-grid-row--gutters > div.fr-col-lg-4.fr-col-md-4:nth-of-type(12) > h3 > a.fr-link.fr-h3` | Intitulé anglais sans lang=en : French Customs for business | RENDERED_DOM | `rgaa/preuves/P02/attempt-002/raw-dom.json` |
| P02 | `P02-RGAA-8-7-LANGUAGE-CHANGE-001-011` | 8.7 / 8.7.1 | `div.fr-grid-row.fr-grid-row--gutters > div.fr-col-lg-4.fr-col-md-4:nth-of-type(12) > section.listeThematique > ul > li.listeDocument.listeDocumentEnavant:nth-of-type(1) > a.fr-link` | Intitulé anglais sans lang=en : French Customs presentation | RENDERED_DOM | `rgaa/preuves/P02/attempt-002/raw-dom.json` |
| P02 | `P02-RGAA-8-7-LANGUAGE-CHANGE-001-012` | 8.7 / 8.7.1 | `div.fr-grid-row.fr-grid-row--gutters > div.fr-col-lg-4.fr-col-md-4:nth-of-type(12) > section.listeThematique > ul > li.listeDocument.listeDocumentEnavant:nth-of-type(2) > a.fr-link` | Intitulé anglais sans lang=en : French Customs for business | RENDERED_DOM | `rgaa/preuves/P02/attempt-002/raw-dom.json` |
| P03 | `P03-RGAA-8-7-LANGUAGE-CHANGE-001-006` | 8.7 / 8.7.1 | `div.fr-collapse.fr-mega-menu > div.fr-container.fr-container--fluid > div.fr-grid-row.fr-grid-row-lg--gutters:nth-of-type(1) > div.fr-col-12.fr-col-lg-3:nth-of-type(13) > h5.fr-mega-menu__category > a.fr-nav__link` | Intitulé anglais sans lang=en : French Customs for business | RENDERED_DOM | `rgaa/preuves/P03/attempt-001/raw-dom.json` |
| P03 | `P03-RGAA-8-7-LANGUAGE-CHANGE-001-007` | 8.7 / 8.7.1 | `div.fr-container.fr-container--fluid > div.fr-grid-row.fr-grid-row-lg--gutters:nth-of-type(1) > div.fr-col-12.fr-col-lg-3:nth-of-type(13) > ul.fr-mega-menu__list > li:nth-of-type(1) > a.fr-nav__link` | Intitulé anglais sans lang=en : French Customs presentation | RENDERED_DOM | `rgaa/preuves/P03/attempt-001/raw-dom.json` |
| P03 | `P03-RGAA-8-7-LANGUAGE-CHANGE-001-008` | 8.7 / 8.7.1 | `div.fr-container.fr-container--fluid > div.fr-grid-row.fr-grid-row-lg--gutters:nth-of-type(1) > div.fr-col-12.fr-col-lg-3:nth-of-type(13) > ul.fr-mega-menu__list > li:nth-of-type(2) > a.fr-nav__link` | Intitulé anglais sans lang=en : French Customs for business | RENDERED_DOM | `rgaa/preuves/P03/attempt-001/raw-dom.json` |
| P04 | `P04-RGAA-8-7-LANGUAGE-CHANGE-001-006` | 8.7 / 8.7.1 | `div.fr-collapse.fr-mega-menu > div.fr-container.fr-container--fluid > div.fr-grid-row.fr-grid-row-lg--gutters:nth-of-type(1) > div.fr-col-12.fr-col-lg-3:nth-of-type(13) > h5.fr-mega-menu__category > a.fr-nav__link` | Intitulé anglais sans lang=en : French Customs for business | RENDERED_DOM | `rgaa/preuves/P04/attempt-001/raw-dom.json` |
| P04 | `P04-RGAA-8-7-LANGUAGE-CHANGE-001-007` | 8.7 / 8.7.1 | `div.fr-container.fr-container--fluid > div.fr-grid-row.fr-grid-row-lg--gutters:nth-of-type(1) > div.fr-col-12.fr-col-lg-3:nth-of-type(13) > ul.fr-mega-menu__list > li:nth-of-type(1) > a.fr-nav__link` | Intitulé anglais sans lang=en : French Customs presentation | RENDERED_DOM | `rgaa/preuves/P04/attempt-001/raw-dom.json` |
| P04 | `P04-RGAA-8-7-LANGUAGE-CHANGE-001-008` | 8.7 / 8.7.1 | `div.fr-container.fr-container--fluid > div.fr-grid-row.fr-grid-row-lg--gutters:nth-of-type(1) > div.fr-col-12.fr-col-lg-3:nth-of-type(13) > ul.fr-mega-menu__list > li:nth-of-type(2) > a.fr-nav__link` | Intitulé anglais sans lang=en : French Customs for business | RENDERED_DOM | `rgaa/preuves/P04/attempt-001/raw-dom.json` |
| P05 | `P05-RGAA-8-7-LANGUAGE-CHANGE-001-007` | 8.7 / 8.7.1 | `div.fr-collapse.fr-mega-menu > div.fr-container.fr-container--fluid > div.fr-grid-row.fr-grid-row-lg--gutters:nth-of-type(1) > div.fr-col-12.fr-col-lg-3:nth-of-type(13) > h5.fr-mega-menu__category > a.fr-nav__link` | Intitulé anglais sans lang=en : French Customs for business | RENDERED_DOM | `rgaa/preuves/P05/attempt-002/raw-dom.json` |
| P05 | `P05-RGAA-8-7-LANGUAGE-CHANGE-001-008` | 8.7 / 8.7.1 | `div.fr-container.fr-container--fluid > div.fr-grid-row.fr-grid-row-lg--gutters:nth-of-type(1) > div.fr-col-12.fr-col-lg-3:nth-of-type(13) > ul.fr-mega-menu__list > li:nth-of-type(1) > a.fr-nav__link` | Intitulé anglais sans lang=en : French Customs presentation | RENDERED_DOM | `rgaa/preuves/P05/attempt-002/raw-dom.json` |
| P05 | `P05-RGAA-8-7-LANGUAGE-CHANGE-001-009` | 8.7 / 8.7.1 | `div.fr-container.fr-container--fluid > div.fr-grid-row.fr-grid-row-lg--gutters:nth-of-type(1) > div.fr-col-12.fr-col-lg-3:nth-of-type(13) > ul.fr-mega-menu__list > li:nth-of-type(2) > a.fr-nav__link` | Intitulé anglais sans lang=en : French Customs for business | RENDERED_DOM | `rgaa/preuves/P05/attempt-002/raw-dom.json` |
| P06 | `P06-RGAA-8-7-LANGUAGE-CHANGE-001-009` | 8.7 / 8.7.1 | `div.fr-collapse.fr-mega-menu > div.fr-container.fr-container--fluid > div.fr-grid-row.fr-grid-row-lg--gutters:nth-of-type(1) > div.fr-col-12.fr-col-lg-3:nth-of-type(13) > h5.fr-mega-menu__category > a.fr-nav__link` | Intitulé anglais sans lang=en : French Customs for business | RENDERED_DOM | `rgaa/preuves/P06/attempt-004/raw-dom.json` |
| P06 | `P06-RGAA-8-7-LANGUAGE-CHANGE-001-010` | 8.7 / 8.7.1 | `div.fr-container.fr-container--fluid > div.fr-grid-row.fr-grid-row-lg--gutters:nth-of-type(1) > div.fr-col-12.fr-col-lg-3:nth-of-type(13) > ul.fr-mega-menu__list > li:nth-of-type(1) > a.fr-nav__link` | Intitulé anglais sans lang=en : French Customs presentation | RENDERED_DOM | `rgaa/preuves/P06/attempt-004/raw-dom.json` |
| P06 | `P06-RGAA-8-7-LANGUAGE-CHANGE-001-011` | 8.7 / 8.7.1 | `div.fr-container.fr-container--fluid > div.fr-grid-row.fr-grid-row-lg--gutters:nth-of-type(1) > div.fr-col-12.fr-col-lg-3:nth-of-type(13) > ul.fr-mega-menu__list > li:nth-of-type(2) > a.fr-nav__link` | Intitulé anglais sans lang=en : French Customs for business | RENDERED_DOM | `rgaa/preuves/P06/attempt-004/raw-dom.json` |
| P07 | `P07-RGAA-8-7-LANGUAGE-CHANGE-001-007` | 8.7 / 8.7.1 | `div.fr-collapse.fr-mega-menu > div.fr-container.fr-container--fluid > div.fr-grid-row.fr-grid-row-lg--gutters:nth-of-type(1) > div.fr-col-12.fr-col-lg-3:nth-of-type(13) > h5.fr-mega-menu__category > a.fr-nav__link` | Intitulé anglais sans lang=en : French Customs for business | RENDERED_DOM | `rgaa/preuves/P07/attempt-002/raw-dom.json` |
| P07 | `P07-RGAA-8-7-LANGUAGE-CHANGE-001-008` | 8.7 / 8.7.1 | `div.fr-container.fr-container--fluid > div.fr-grid-row.fr-grid-row-lg--gutters:nth-of-type(1) > div.fr-col-12.fr-col-lg-3:nth-of-type(13) > ul.fr-mega-menu__list > li:nth-of-type(1) > a.fr-nav__link` | Intitulé anglais sans lang=en : French Customs presentation | RENDERED_DOM | `rgaa/preuves/P07/attempt-002/raw-dom.json` |
| P07 | `P07-RGAA-8-7-LANGUAGE-CHANGE-001-009` | 8.7 / 8.7.1 | `div.fr-container.fr-container--fluid > div.fr-grid-row.fr-grid-row-lg--gutters:nth-of-type(1) > div.fr-col-12.fr-col-lg-3:nth-of-type(13) > ul.fr-mega-menu__list > li:nth-of-type(2) > a.fr-nav__link` | Intitulé anglais sans lang=en : French Customs for business | RENDERED_DOM | `rgaa/preuves/P07/attempt-002/raw-dom.json` |

---

## Analyse du défaut

Les rapports sources classent « French Customs for business » et « French Customs presentation » comme passages anglais sans langue déclarée. Ces chaînes sont répétées dans la navigation de P02 à P07. Leur statut RGAA dépend toutefois de l’exception relative aux noms propres.

## Impact utilisateur

Sans langue déclarée, une synthèse vocale française peut appliquer une prononciation inadaptée ; l’applicabilité RGAA reste à arbitrer.

---

## Recommandations

### Solution 1 — Déclarer la langue si ces libellés sont des passages anglais

Si l’exception de nom propre n’est pas retenue, ajouter `lang="en"` sur toutes les occurrences.

```html
<a href="/professionnels/french-customs-business"
   class="fr-nav__link" lang="en">
  French Customs for business
</a>
```

### Solution 2 — Tracer l’exception de nom propre

Si « French Customs » est le nom propre officiel de la rubrique, documenter l’exception et reclasser les constats concernés.

```html
<!-- Décision éditoriale documentée : nom propre officiel -->
<a href="/professionnels/french-customs-business" class="fr-nav__link">
  French Customs for business
</a>
```

## Comparaison avec le composant DSFR

**Composant concerné** : Navigation et liens éditoriaux

| Point contrôlé | DSFR / comportement attendu | Site audité |
|---|---|---|
| Langue | À déclarer pour un passage étranger | Aucun lang=en |
| Exception | Nom propre exclu du test 8.7.1 | Qualification non documentée |
| Cause attribuée | Contenu paramétrable | Décision éditoriale Drupal |

Le constat est attribué à l’intégration observée. La présence de classes `fr-*` ne suffit pas à attribuer le défaut au DSFR natif.

---

## Vérification après correction

- [ ] Faire arbitrer le statut de nom propre par l’auditeur et l’équipe éditoriale.
- [ ] Si l’exception est écartée, vérifier `lang="en"` sur chaque occurrence.
- [ ] Si l’exception est retenue, consigner la justification et reclasser les constats sources.

La correction ne doit être considérée comme clôturée qu’après production d’une nouvelle preuve et recontrôle humain.

## Références

- [RGAA 4.1.2 — test 8.7.1](https://accessibilite.numerique.gouv.fr/methode/criteres-et-tests/#8.7.1)
- [DSFR 1.15.2 — composant navigation](https://github.com/GouvernementFR/dsfr/tree/v1.15.2/src/dsfr/component/navigation)
- Source factuelle : rapports HTML RGAA livrés pour les pages indiquées et constats `NC_CONFIRMEE` correspondants.
