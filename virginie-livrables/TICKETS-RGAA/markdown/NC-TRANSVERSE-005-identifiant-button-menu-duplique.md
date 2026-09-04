# NC-TRANSVERSE-005 — Identifiant button-menu dupliqué dans l’en-tête

**Statut** : Préqualification — NC confirmée dans les rapports sources  
**Référentiel** : RGAA 4.1.2  
**Sévérité** : Majeur  
**Justification de sévérité** : Les scripts ou relations qui ciblent `button-menu` peuvent résoudre le mauvais bouton et produire un comportement imprévisible.  
**Date** : 2026-09-04  
**Composant / gabarit** : En-tête  
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

### id=button-menu présent 2 fois

```html
<button data-fr-opened="false" aria-controls="modal-menu" title="Menu" type="button" id="button-menu" class="fr-btn--menu fr-btn" data-fr-js-modal-button="true">Menu</button>

<button aria-controls="modal-menu" title="Fermer" type="button" id="button-menu" class=" fr-btn--close fr-btn" data-fr-js-modal-button="true">Fermer</button>
```

## Inventaire des constats sources

| Page | Identifiant source | Critère / test | Sélecteur | Observation | Provenance | Preuve principale |
|---|---|---|---|---|---|---|
| P01 | `P01-RGAA-8-2-ID-UNIQUE-001-002` | 8.2 / 8.2.1 | `div.fr-container > div.fr-header__body-row > div.fr-header__brand.fr-enlarge-link:nth-of-type(1) > div.fr-header__brand-top:nth-of-type(1) > div.fr-header__navbar:nth-of-type(3) > button.fr-btn--menu.fr-btn:nth-of-type(2), body.path-frontpage.eu-cookie-compliance-popup-open > div.dialog-off-canvas-main-canvas:nth-of-type(3) > header.fr-header > div.fr-header__menu.fr-modal:nth-of-type(2) > div.fr-container > button.fr-btn--close.fr-btn` | id=button-menu présent 2 fois | RENDERED_DOM | `rgaa/preuves/P01/attempt-009/raw-dom.json` |
| P02 | `P02-RGAA-8-2-ID-UNIQUE-001-002` | 8.2 / 8.2.1 | `div.fr-container > div.fr-header__body-row > div.fr-header__brand.fr-enlarge-link:nth-of-type(1) > div.fr-header__brand-top:nth-of-type(1) > div.fr-header__navbar:nth-of-type(3) > button.fr-btn--menu.fr-btn:nth-of-type(2), body.path-plan-du-site.eu-cookie-compliance-popup-open > div.dialog-off-canvas-main-canvas:nth-of-type(3) > header.fr-header > div.fr-header__menu.fr-modal:nth-of-type(2) > div.fr-container > button.fr-btn--close.fr-btn` | id=button-menu présent 2 fois | RENDERED_DOM | `rgaa/preuves/P02/attempt-002/raw-dom.json` |
| P03 | `P03-RGAA-8-2-ID-UNIQUE-001-002` | 8.2 / 8.2.1 | `div.fr-container > div.fr-header__body-row > div.fr-header__brand.fr-enlarge-link:nth-of-type(1) > div.fr-header__brand-top:nth-of-type(1) > div.fr-header__navbar:nth-of-type(3) > button.fr-btn--menu.fr-btn:nth-of-type(2), body.path-node.node--type-page > div.dialog-off-canvas-main-canvas:nth-of-type(3) > header.fr-header > div.fr-header__menu.fr-modal:nth-of-type(2) > div.fr-container > button.fr-btn--close.fr-btn` | id=button-menu présent 2 fois | RENDERED_DOM | `rgaa/preuves/P03/attempt-001/raw-dom.json` |
| P04 | `P04-RGAA-8-2-ID-UNIQUE-001-002` | 8.2 / 8.2.1 | `div.fr-container > div.fr-header__body-row > div.fr-header__brand.fr-enlarge-link:nth-of-type(1) > div.fr-header__brand-top:nth-of-type(1) > div.fr-header__navbar:nth-of-type(3) > button.fr-btn--menu.fr-btn:nth-of-type(2), body.path-node.node--type-page > div.dialog-off-canvas-main-canvas:nth-of-type(3) > header.fr-header > div.fr-header__menu.fr-modal:nth-of-type(2) > div.fr-container > button.fr-btn--close.fr-btn` | id=button-menu présent 2 fois | RENDERED_DOM | `rgaa/preuves/P04/attempt-001/raw-dom.json` |
| P05 | `P05-RGAA-8-2-ID-UNIQUE-001-002` | 8.2 / 8.2.1 | `div.fr-container > div.fr-header__body-row > div.fr-header__brand.fr-enlarge-link:nth-of-type(1) > div.fr-header__brand-top:nth-of-type(1) > div.fr-header__navbar:nth-of-type(3) > button.fr-btn--menu.fr-btn:nth-of-type(2), body.path-node.node--type-page > div.dialog-off-canvas-main-canvas:nth-of-type(3) > header.fr-header > div.fr-header__menu.fr-modal:nth-of-type(2) > div.fr-container > button.fr-btn--close.fr-btn` | id=button-menu présent 2 fois | RENDERED_DOM | `rgaa/preuves/P05/attempt-002/raw-dom.json` |
| P06 | `P06-RGAA-8-2-ID-UNIQUE-001-004` | 8.2 / 8.2.1 | `div.fr-container > div.fr-header__body-row > div.fr-header__brand.fr-enlarge-link:nth-of-type(1) > div.fr-header__brand-top:nth-of-type(1) > div.fr-header__navbar:nth-of-type(3) > button.fr-btn--menu.fr-btn:nth-of-type(2), body.path-formulaire-infos-douane-service.eu-cookie-compliance-popup-open > div.dialog-off-canvas-main-canvas:nth-of-type(3) > header.fr-header > div.fr-header__menu.fr-modal:nth-of-type(2) > div.fr-container > button.fr-btn--close.fr-btn` | id=button-menu présent 2 fois | RENDERED_DOM | `rgaa/preuves/P06/attempt-004/raw-dom.json` |
| P07 | `P07-RGAA-8-2-ID-UNIQUE-001-002` | 8.2 / 8.2.1 | `div.fr-container > div.fr-header__body-row > div.fr-header__brand.fr-enlarge-link:nth-of-type(1) > div.fr-header__brand-top:nth-of-type(1) > div.fr-header__navbar:nth-of-type(3) > button.fr-btn--menu.fr-btn:nth-of-type(2), div.thematique:nth-of-type(2) > header.banner.bandeau > header.fr-header > div.fr-header__menu.fr-modal:nth-of-type(2) > div.fr-container > button.fr-btn--close.fr-btn` | id=button-menu présent 2 fois | RENDERED_DOM | `rgaa/preuves/P07/attempt-002/raw-dom.json` |
| P08 | `P08-RGAA-8-2-ID-UNIQUE-001-002` | 8.2 / 8.2.1 | `div.fr-container > div.fr-header__body-row > div.fr-header__brand.fr-enlarge-link:nth-of-type(1) > div.fr-header__brand-top:nth-of-type(1) > div.fr-header__navbar:nth-of-type(3) > button.fr-btn--menu.fr-btn:nth-of-type(2), div.thematique:nth-of-type(2) > header.banner.bandeau > header.fr-header > div.fr-header__menu.fr-modal:nth-of-type(2) > div.fr-container > button.fr-btn--close.fr-btn` | id=button-menu présent 2 fois | RENDERED_DOM | `rgaa/preuves/P08/attempt-001/raw-dom.json` |
| P09 | `P09-RGAA-8-2-ID-UNIQUE-001-003` | 8.2 / 8.2.1 | `div.fr-container > div.fr-header__body-row > div.fr-header__brand.fr-enlarge-link:nth-of-type(1) > div.fr-header__brand-top:nth-of-type(1) > div.fr-header__navbar:nth-of-type(3) > button.fr-btn--menu.fr-btn:nth-of-type(2), body.path-node.node--type-actualite > div.dialog-off-canvas-main-canvas:nth-of-type(3) > header.fr-header > div.fr-header__menu.fr-modal:nth-of-type(2) > div.fr-container > button.fr-btn--close.fr-btn` | id=button-menu présent 2 fois | RENDERED_DOM | `rgaa/preuves/P09/attempt-001/raw-dom.json` |

---

## Analyse du défaut

Sur les neuf pages, le bouton d’ouverture et le bouton de fermeture du menu partagent l’identifiant `button-menu`. Un identifiant doit désigner un seul élément dans le document. Cette cause relève du template d’en-tête et possède un correctif distinct des autres duplications.

## Impact utilisateur

Les scripts ou relations qui ciblent `button-menu` peuvent résoudre le mauvais bouton et produire un comportement imprévisible.

---

## Recommandations

### Solution 1 — Donner un identifiant distinct à chaque bouton (recommandée)

Conserver `aria-controls="modal-menu"` mais utiliser deux identifiants uniques, ou retirer les `id` s’ils ne sont référencés nulle part.

```html
<button id="button-menu-open" aria-controls="modal-menu">Menu</button>
<button id="button-menu-close" aria-controls="modal-menu">Fermer</button>
```

## Comparaison avec le composant DSFR

**Composant concerné** : En-tête

| Point contrôlé | DSFR / comportement attendu | Site audité |
|---|---|---|
| Boutons du menu | Identifiants uniques par contrôle | button-menu présent deux fois |
| Cible contrôlée | aria-controls peut viser la même modale | modal-menu partagé, ce qui est attendu |
| Cause attribuée | Instances distinctes | Template d’en-tête intégré |

Le constat est attribué à l’intégration observée. La présence de classes `fr-*` ne suffit pas à attribuer le défaut au DSFR natif.

---

## Vérification après correction

- [ ] Vérifier l’unicité de `button-menu` sur les neuf pages.
- [ ] Rejouer l’ouverture et la fermeture du menu sur desktop et mobile.
- [ ] Contrôler que les scripts ciblent toujours les bons boutons.

La correction ne doit être considérée comme clôturée qu’après production d’une nouvelle preuve et recontrôle humain.

## Références

- [RGAA 4.1.2 — test 8.2.1](https://accessibilite.numerique.gouv.fr/methode/criteres-et-tests/#8.2.1)
- [DSFR 1.15.2 — composant header](https://github.com/GouvernementFR/dsfr/tree/v1.15.2/src/dsfr/component/header)
- Source factuelle : rapports HTML RGAA livrés pour les pages indiquées et constats `NC_CONFIRMEE` correspondants.
