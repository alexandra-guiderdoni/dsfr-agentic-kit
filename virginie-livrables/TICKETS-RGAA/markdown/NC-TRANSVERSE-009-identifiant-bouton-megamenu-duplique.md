# NC-TRANSVERSE-009 — Identifiant de fermeture du méga-menu dupliqué

**Statut** : Préqualification — NC confirmée dans les rapports sources  
**Référentiel** : RGAA 4.1.2  
**Sévérité** : Majeur  
**Justification de sévérité** : Une association ou un script fondé sur cet identifiant peut agir sur le mauvais méga-menu.  
**Date** : 2026-09-04  
**Composant / gabarit** : Navigation / méga-menu  
**Portée** : Transverse — P01, P02, P03, P04, P05, P06, P07, P08, P09  
**Pages affectées** : P01, P02, P03, P04, P05, P06, P07, P08, P09  
**Constats sources regroupés** : 9

> Ces conclusions proviennent d’une préqualification instrumentée. Elles ne constituent ni un taux RGAA officiel ni une validation après correction.

---

## Pages et rapports sources

| Page | Nom | URL | Rapport RGAA |
|---|---|---|---|
| P01 | Accueil | https://moa.douane.gouv.fr/ | [P01-RGAA.html](../../RGAA/P01-RGAA.html) |
| P02 | Plan du site | https://moa.douane.gouv.fr/plan-du-site | [P02-RGAA.html](../../RGAA/P02-RGAA.html) |
| P03 | Déclaration d’accessibilité | https://moa.douane.gouv.fr/pied-de-page/declaration-daccessibilite-du-portail-dounegouvfr | [P03-RGAA.html](../../RGAA/P03-RGAA.html) |
| P04 | Mentions légales | https://moa.douane.gouv.fr/mentions-legales | [P04-RGAA.html](../../RGAA/P04-RGAA.html) |
| P05 | Données personnelles | https://moa.douane.gouv.fr/pied-de-page/donnees-personnelles | [P05-RGAA.html](../../RGAA/P05-RGAA.html) |
| P06 | Formulaire Écrivez-nous | https://moa.douane.gouv.fr/formulaire-infos-douane-service | [P06-RGAA.html](../../RGAA/P06-RGAA.html) |
| P07 | Voyages à l’étranger | https://moa.douane.gouv.fr/particuliers/voyages-letranger | [P07-RGAA.html](../../RGAA/P07-RGAA.html) |
| P08 | Commerce international | https://moa.douane.gouv.fr/professionnels/commerce-international | [P08-RGAA.html](../../RGAA/P08-RGAA.html) |
| P09 | Actualité DELTA IE | https://moa.douane.gouv.fr/actualites/point-dactualite-sur-le-deploiement-de-delta-ie-import-et-export-au-5-fevrier-2026 | [P09-RGAA.html](../../RGAA/P09-RGAA.html) |

## Références RGAA

- **Critère 8.2** — Pour chaque page web, le code source généré est-il valide selon le type de document spécifié ?
- **Test 8.2.1** — Pour chaque déclaration de type de document, le code source généré de la page vérifie-t-il ces conditions ? Les balises, attributs et valeurs d’attributs respectent les règles d’écriture ; L’imbrication des balises est conforme ; L’ouverture et la fermeture des balises sont conformes ; Les valeurs d’attribut id sont uniques dans la page ; Les attributs ne sont pas doublés sur un même élément.

---

## Code source constaté

### id=button-2835 présent 2 fois

```html
<button aria-controls="menu-la-douane" title="Fermer" type="button" id="button-2835" class="fr-btn--close fr-btn" data-fr-js-collapse-button="true">Fermer</button>

<button aria-controls="menu-services-aides" title="Fermer" type="button" id="button-2835" class="fr-btn--close fr-btn" data-fr-js-collapse-button="true">Fermer</button>
```

## Inventaire des constats sources

| Page | Identifiant source | Critère / test | Sélecteur | Observation | Provenance | Preuve principale |
|---|---|---|---|---|---|---|
| P01 | `P01-RGAA-8-2-ID-UNIQUE-001-003` | 8.2 / 8.2.1 | `li.fr-nav__item:nth-of-type(3) > div.fr-collapse.fr-mega-menu > div.fr-container.fr-container--fluid > div.fr-grid-row.fr-grid-row-lg--gutters > div.fr-col-12.fr-mb-n3v:nth-of-type(1) > button.fr-btn--close.fr-btn, li.fr-nav__item:nth-of-type(5) > div.fr-collapse.fr-mega-menu > div.fr-container.fr-container--fluid > div.fr-grid-row.fr-grid-row-lg--gutters:nth-of-type(1) > div.fr-col-12.fr-mb-n3v:nth-of-type(1) > button.fr-btn--close.fr-btn` | id=button-2835 présent 2 fois | RENDERED_DOM | `rgaa/preuves/P01/attempt-009/raw-dom.json` |
| P02 | `P02-RGAA-8-2-ID-UNIQUE-001-003` | 8.2 / 8.2.1 | `li.fr-nav__item:nth-of-type(3) > div.fr-collapse.fr-mega-menu > div.fr-container.fr-container--fluid > div.fr-grid-row.fr-grid-row-lg--gutters > div.fr-col-12.fr-mb-n3v:nth-of-type(1) > button.fr-btn--close.fr-btn, li.fr-nav__item:nth-of-type(5) > div.fr-collapse.fr-mega-menu > div.fr-container.fr-container--fluid > div.fr-grid-row.fr-grid-row-lg--gutters:nth-of-type(1) > div.fr-col-12.fr-mb-n3v:nth-of-type(1) > button.fr-btn--close.fr-btn` | id=button-2835 présent 2 fois | RENDERED_DOM | `rgaa/preuves/P02/attempt-002/raw-dom.json` |
| P03 | `P03-RGAA-8-2-ID-UNIQUE-001-003` | 8.2 / 8.2.1 | `li.fr-nav__item:nth-of-type(3) > div.fr-collapse.fr-mega-menu > div.fr-container.fr-container--fluid > div.fr-grid-row.fr-grid-row-lg--gutters > div.fr-col-12.fr-mb-n3v:nth-of-type(1) > button.fr-btn--close.fr-btn, li.fr-nav__item:nth-of-type(5) > div.fr-collapse.fr-mega-menu > div.fr-container.fr-container--fluid > div.fr-grid-row.fr-grid-row-lg--gutters:nth-of-type(1) > div.fr-col-12.fr-mb-n3v:nth-of-type(1) > button.fr-btn--close.fr-btn` | id=button-2835 présent 2 fois | RENDERED_DOM | `rgaa/preuves/P03/attempt-001/raw-dom.json` |
| P04 | `P04-RGAA-8-2-ID-UNIQUE-001-003` | 8.2 / 8.2.1 | `li.fr-nav__item:nth-of-type(3) > div.fr-collapse.fr-mega-menu > div.fr-container.fr-container--fluid > div.fr-grid-row.fr-grid-row-lg--gutters > div.fr-col-12.fr-mb-n3v:nth-of-type(1) > button.fr-btn--close.fr-btn, li.fr-nav__item:nth-of-type(5) > div.fr-collapse.fr-mega-menu > div.fr-container.fr-container--fluid > div.fr-grid-row.fr-grid-row-lg--gutters:nth-of-type(1) > div.fr-col-12.fr-mb-n3v:nth-of-type(1) > button.fr-btn--close.fr-btn` | id=button-2835 présent 2 fois | RENDERED_DOM | `rgaa/preuves/P04/attempt-001/raw-dom.json` |
| P05 | `P05-RGAA-8-2-ID-UNIQUE-001-003` | 8.2 / 8.2.1 | `li.fr-nav__item:nth-of-type(3) > div.fr-collapse.fr-mega-menu > div.fr-container.fr-container--fluid > div.fr-grid-row.fr-grid-row-lg--gutters > div.fr-col-12.fr-mb-n3v:nth-of-type(1) > button.fr-btn--close.fr-btn, li.fr-nav__item:nth-of-type(5) > div.fr-collapse.fr-mega-menu > div.fr-container.fr-container--fluid > div.fr-grid-row.fr-grid-row-lg--gutters:nth-of-type(1) > div.fr-col-12.fr-mb-n3v:nth-of-type(1) > button.fr-btn--close.fr-btn` | id=button-2835 présent 2 fois | RENDERED_DOM | `rgaa/preuves/P05/attempt-002/raw-dom.json` |
| P06 | `P06-RGAA-8-2-ID-UNIQUE-001-005` | 8.2 / 8.2.1 | `li.fr-nav__item:nth-of-type(3) > div.fr-collapse.fr-mega-menu > div.fr-container.fr-container--fluid > div.fr-grid-row.fr-grid-row-lg--gutters > div.fr-col-12.fr-mb-n3v:nth-of-type(1) > button.fr-btn--close.fr-btn, li.fr-nav__item:nth-of-type(5) > div.fr-collapse.fr-mega-menu > div.fr-container.fr-container--fluid > div.fr-grid-row.fr-grid-row-lg--gutters:nth-of-type(1) > div.fr-col-12.fr-mb-n3v:nth-of-type(1) > button.fr-btn--close.fr-btn` | id=button-2835 présent 2 fois | RENDERED_DOM | `rgaa/preuves/P06/attempt-004/raw-dom.json` |
| P07 | `P07-RGAA-8-2-ID-UNIQUE-001-003` | 8.2 / 8.2.1 | `li.fr-nav__item:nth-of-type(3) > div.fr-collapse.fr-mega-menu > div.fr-container.fr-container--fluid > div.fr-grid-row.fr-grid-row-lg--gutters > div.fr-col-12.fr-mb-n3v:nth-of-type(1) > button.fr-btn--close.fr-btn, li.fr-nav__item:nth-of-type(5) > div.fr-collapse.fr-mega-menu > div.fr-container.fr-container--fluid > div.fr-grid-row.fr-grid-row-lg--gutters:nth-of-type(1) > div.fr-col-12.fr-mb-n3v:nth-of-type(1) > button.fr-btn--close.fr-btn` | id=button-2835 présent 2 fois | RENDERED_DOM | `rgaa/preuves/P07/attempt-002/raw-dom.json` |
| P08 | `P08-RGAA-8-2-ID-UNIQUE-001-003` | 8.2 / 8.2.1 | `li.fr-nav__item:nth-of-type(3) > div.fr-collapse.fr-mega-menu > div.fr-container.fr-container--fluid > div.fr-grid-row.fr-grid-row-lg--gutters > div.fr-col-12.fr-mb-n3v:nth-of-type(1) > button.fr-btn--close.fr-btn, li.fr-nav__item:nth-of-type(5) > div.fr-collapse.fr-mega-menu > div.fr-container.fr-container--fluid > div.fr-grid-row.fr-grid-row-lg--gutters:nth-of-type(1) > div.fr-col-12.fr-mb-n3v:nth-of-type(1) > button.fr-btn--close.fr-btn` | id=button-2835 présent 2 fois | RENDERED_DOM | `rgaa/preuves/P08/attempt-001/raw-dom.json` |
| P09 | `P09-RGAA-8-2-ID-UNIQUE-001-004` | 8.2 / 8.2.1 | `li.fr-nav__item:nth-of-type(3) > div.fr-collapse.fr-mega-menu > div.fr-container.fr-container--fluid > div.fr-grid-row.fr-grid-row-lg--gutters > div.fr-col-12.fr-mb-n3v:nth-of-type(1) > button.fr-btn--close.fr-btn, li.fr-nav__item:nth-of-type(5) > div.fr-collapse.fr-mega-menu > div.fr-container.fr-container--fluid > div.fr-grid-row.fr-grid-row-lg--gutters:nth-of-type(1) > div.fr-col-12.fr-mb-n3v:nth-of-type(1) > button.fr-btn--close.fr-btn` | id=button-2835 présent 2 fois | RENDERED_DOM | `rgaa/preuves/P09/attempt-001/raw-dom.json` |

---

## Analyse du défaut

Sur les neuf pages, deux boutons de fermeture appartenant à des méga-menus différents partagent l’identifiant `button-2835`. La correction doit être appliquée dans la boucle qui génère les entrées de navigation, indépendamment du correctif de l’en-tête.

## Impact utilisateur

Une association ou un script fondé sur cet identifiant peut agir sur le mauvais méga-menu.

---

## Recommandations

### Solution 1 — Dériver l’identifiant de la cible contrôlée (recommandée)

Générer un identifiant stable et unique depuis la clé métier de chaque entrée de navigation.

```html
<button id="button-menu-la-douane" aria-controls="menu-la-douane">Fermer</button>
<button id="button-menu-services" aria-controls="menu-services-aides">Fermer</button>
```

## Comparaison avec le composant DSFR

**Composant concerné** : Navigation / méga-menu

| Point contrôlé | DSFR / comportement attendu | Site audité |
|---|---|---|
| Boutons de fermeture | Un identifiant par instance | button-2835 partagé par deux menus |
| Génération | Clé propre à l’entrée | Constante réutilisée |
| Cause attribuée | Template paramétré | Boucle de navigation Drupal |

Le constat est attribué à l’intégration observée. La présence de classes `fr-*` ne suffit pas à attribuer le défaut au DSFR natif.

---

## Vérification après correction

- [ ] Vérifier l’unicité de tous les boutons de fermeture des méga-menus.
- [ ] Ouvrir et fermer chaque entrée de navigation au clavier.
- [ ] Contrôler la cohérence entre chaque bouton et son `aria-controls`.

La correction ne doit être considérée comme clôturée qu’après production d’une nouvelle preuve et recontrôle humain.

## Références

- [RGAA 4.1.2 — test 8.2.1](https://accessibilite.numerique.gouv.fr/methode/criteres-et-tests/#8.2.1)
- [DSFR 1.15.2 — composant navigation](https://github.com/GouvernementFR/dsfr/tree/v1.15.2/src/dsfr/component/navigation)
- Source factuelle : rapports HTML RGAA livrés pour les pages indiquées et constats `NC_CONFIRMEE` correspondants.
