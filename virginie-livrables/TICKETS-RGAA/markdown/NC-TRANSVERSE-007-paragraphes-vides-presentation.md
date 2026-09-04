# NC-TRANSVERSE-007 — Paragraphes vides utilisés pour l’espacement

**Statut** : Préqualification — NC confirmée dans les rapports sources  
**Référentiel** : RGAA 4.1.2  
**Sévérité** : Majeur  
**Justification de sévérité** : La structure exposée peut contenir des paragraphes sans contenu et la présentation dépend d’un balisage sémantique détourné.  
**Date** : 2026-09-04  
**Composant / gabarit** : Bandeau de consentement  
**Portée** : Transverse — P01, P02, P03, P04, P05, P06  
**Pages affectées** : P01, P02, P03, P04, P05, P06  
**Constats sources regroupés** : 12

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

## Références RGAA

- **Critère 8.9** — Dans chaque page web, les balises ne doivent pas être utilisées uniquement à des fins de présentation. Cette règle est-elle respectée ?
- **Test 8.9.1** — Dans chaque page web les balises (à l’exception de `<div>`, `<span>` et `<table>`) ne doivent pas être utilisées uniquement à des fins de présentation. Cette règle est-elle respectée ?

---

## Code source constaté

### Paragraphe vide observé

```html
<p class="fr-text--sm"></p>
```

### Paragraphe vide observé

```html
<p></p>
```

## Inventaire des constats sources

| Page | Identifiant source | Critère / test | Sélecteur | Observation | Provenance | Preuve principale |
|---|---|---|---|---|---|---|
| P01 | `P01-RGAA-8-9-EMPTY-PRESENTATION-001-006` | 8.9 / 8.9.1 | `html.js > body.path-frontpage.eu-cookie-compliance-popup-open > div.sliding-popup-bottom:nth-of-type(1) > div.fr-consent-banner > div.fr-consent-banner__content > p.fr-text--sm:nth-of-type(1)` | Paragraphe vide avec marge 0px 0px 16px | MEASUREMENTS | `rgaa/preuves/P01/attempt-009/raw-dom.json` |
| P01 | `P01-RGAA-8-9-EMPTY-PRESENTATION-001-007` | 8.9 / 8.9.1 | `html.js > body.path-frontpage.eu-cookie-compliance-popup-open > div.sliding-popup-bottom:nth-of-type(1) > div.fr-consent-banner > div.fr-consent-banner__content > p:nth-of-type(3)` | Paragraphe vide avec marge 0px 0px 16px | MEASUREMENTS | `rgaa/preuves/P01/attempt-009/raw-dom.json` |
| P02 | `P02-RGAA-8-9-EMPTY-PRESENTATION-001-015` | 8.9 / 8.9.1 | `html.js > body.path-plan-du-site.eu-cookie-compliance-popup-open > div.sliding-popup-bottom:nth-of-type(1) > div.fr-consent-banner > div.fr-consent-banner__content > p.fr-text--sm:nth-of-type(1)` | Paragraphe vide avec marge 0px 0px 16px | MEASUREMENTS | `rgaa/preuves/P02/attempt-002/raw-dom.json` |
| P02 | `P02-RGAA-8-9-EMPTY-PRESENTATION-001-016` | 8.9 / 8.9.1 | `html.js > body.path-plan-du-site.eu-cookie-compliance-popup-open > div.sliding-popup-bottom:nth-of-type(1) > div.fr-consent-banner > div.fr-consent-banner__content > p:nth-of-type(3)` | Paragraphe vide avec marge 0px 0px 16px | MEASUREMENTS | `rgaa/preuves/P02/attempt-002/raw-dom.json` |
| P03 | `P03-RGAA-8-9-EMPTY-PRESENTATION-001-010` | 8.9 / 8.9.1 | `html.js > body.path-node.node--type-page > div.sliding-popup-bottom:nth-of-type(1) > div.fr-consent-banner > div.fr-consent-banner__content > p.fr-text--sm:nth-of-type(1)` | Paragraphe vide avec marge 0px 0px 16px | MEASUREMENTS | `rgaa/preuves/P03/attempt-001/raw-dom.json` |
| P03 | `P03-RGAA-8-9-EMPTY-PRESENTATION-001-011` | 8.9 / 8.9.1 | `html.js > body.path-node.node--type-page > div.sliding-popup-bottom:nth-of-type(1) > div.fr-consent-banner > div.fr-consent-banner__content > p:nth-of-type(3)` | Paragraphe vide avec marge 0px 0px 16px | MEASUREMENTS | `rgaa/preuves/P03/attempt-001/raw-dom.json` |
| P04 | `P04-RGAA-8-9-EMPTY-PRESENTATION-001-010` | 8.9 / 8.9.1 | `html.js > body.path-node.node--type-page > div.sliding-popup-bottom:nth-of-type(1) > div.fr-consent-banner > div.fr-consent-banner__content > p.fr-text--sm:nth-of-type(1)` | Paragraphe vide avec marge 0px 0px 16px | MEASUREMENTS | `rgaa/preuves/P04/attempt-001/raw-dom.json` |
| P04 | `P04-RGAA-8-9-EMPTY-PRESENTATION-001-011` | 8.9 / 8.9.1 | `html.js > body.path-node.node--type-page > div.sliding-popup-bottom:nth-of-type(1) > div.fr-consent-banner > div.fr-consent-banner__content > p:nth-of-type(3)` | Paragraphe vide avec marge 0px 0px 16px | MEASUREMENTS | `rgaa/preuves/P04/attempt-001/raw-dom.json` |
| P05 | `P05-RGAA-8-9-EMPTY-PRESENTATION-001-011` | 8.9 / 8.9.1 | `html.js.tablesaw-enhanced > body.path-node.node--type-page > div.sliding-popup-bottom:nth-of-type(1) > div.fr-consent-banner > div.fr-consent-banner__content > p.fr-text--sm:nth-of-type(1)` | Paragraphe vide avec marge 0px 0px 16px | MEASUREMENTS | `rgaa/preuves/P05/attempt-002/raw-dom.json` |
| P05 | `P05-RGAA-8-9-EMPTY-PRESENTATION-001-012` | 8.9 / 8.9.1 | `html.js.tablesaw-enhanced > body.path-node.node--type-page > div.sliding-popup-bottom:nth-of-type(1) > div.fr-consent-banner > div.fr-consent-banner__content > p:nth-of-type(3)` | Paragraphe vide avec marge 0px 0px 16px | MEASUREMENTS | `rgaa/preuves/P05/attempt-002/raw-dom.json` |
| P06 | `P06-RGAA-8-9-EMPTY-PRESENTATION-001-015` | 8.9 / 8.9.1 | `html.js > body.path-formulaire-infos-douane-service.eu-cookie-compliance-popup-open > div.sliding-popup-bottom:nth-of-type(1) > div.fr-consent-banner > div.fr-consent-banner__content > p.fr-text--sm:nth-of-type(1)` | Paragraphe vide avec marge 0px 0px 16px | MEASUREMENTS | `rgaa/preuves/P06/attempt-004/raw-dom.json` |
| P06 | `P06-RGAA-8-9-EMPTY-PRESENTATION-001-016` | 8.9 / 8.9.1 | `html.js > body.path-formulaire-infos-douane-service.eu-cookie-compliance-popup-open > div.sliding-popup-bottom:nth-of-type(1) > div.fr-consent-banner > div.fr-consent-banner__content > p:nth-of-type(3)` | Paragraphe vide avec marge 0px 0px 16px | MEASUREMENTS | `rgaa/preuves/P06/attempt-004/raw-dom.json` |

---

## Analyse du défaut

Le bandeau de consentement contient deux paragraphes vides qui produisent une marge de 16 pixels. Une balise `p` représente un paragraphe de contenu ; elle ne doit pas être créée uniquement pour obtenir un espacement. Le défaut est répété par le même template sur P01 à P06.

## Impact utilisateur

La structure exposée peut contenir des paragraphes sans contenu et la présentation dépend d’un balisage sémantique détourné.

---

## Recommandations

### Solution 1 — Supprimer les paragraphes vides et utiliser le CSS (recommandée)

Conserver uniquement le paragraphe utile et appliquer la marge au conteneur ou à ce paragraphe avec une classe DSFR/CSS.

```html
<div class="fr-consent-banner__content fr-mb-2w">
  <p>Ce site utilise des cookies afin de vous proposer…</p>
</div>
```

## Comparaison avec le composant DSFR

**Composant concerné** : Bandeau de consentement

| Point contrôlé | DSFR / comportement attendu | Site audité |
|---|---|---|
| Paragraphes | Contenu textuel réel | Deux éléments p vides |
| Espacement | Classes utilitaires ou CSS | Marge portée par des paragraphes vides |
| Cause attribuée | Structure du composant | Template de consentement intégré |

Le constat est attribué à l’intégration observée. La présence de classes `fr-*` ne suffit pas à attribuer le défaut au DSFR natif.

---

## Vérification après correction

- [ ] Inspecter le DOM rendu du bandeau sur P01 à P06.
- [ ] Vérifier qu’aucun paragraphe vide ne sert à créer une marge.
- [ ] Désactiver les styles et contrôler que la structure conserve son sens.

La correction ne doit être considérée comme clôturée qu’après production d’une nouvelle preuve et recontrôle humain.

## Références

- [RGAA 4.1.2 — test 8.9.1](https://accessibilite.numerique.gouv.fr/methode/criteres-et-tests/#8.9.1)
- [DSFR 1.15.2 — composant consent](https://github.com/GouvernementFR/dsfr/tree/v1.15.2/src/dsfr/component/consent)
- Source factuelle : rapports HTML RGAA livrés pour les pages indiquées et constats `NC_CONFIRMEE` correspondants.
