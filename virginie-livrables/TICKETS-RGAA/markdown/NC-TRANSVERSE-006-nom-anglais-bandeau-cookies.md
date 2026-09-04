# NC-TRANSVERSE-006 — Nom anglais du bandeau de cookies sans langue déclarée

**Statut** : Préqualification — NC confirmée dans les rapports sources  
**Référentiel** : RGAA 4.1.2  
**Sévérité** : Majeur  
**Justification de sévérité** : Une synthèse vocale française peut prononcer ce nom avec des règles phonétiques inadaptées.  
**Date** : 2026-09-04  
**Composant / gabarit** : Bandeau de consentement  
**Portée** : Transverse — P01, P02, P03, P04, P05, P06, P07, P08  
**Pages affectées** : P01, P02, P03, P04, P05, P06, P07, P08  
**Constats sources regroupés** : 8

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

## Références RGAA

- **Critère 8.7** — Dans chaque page web, chaque changement de langue est-il indiqué dans le code source (hors cas particuliers) ?
- **Test 8.7.1** — Dans chaque page web, chaque texte écrit dans une langue différente de la langue par défaut vérifie-t-il une de ces conditions (hors cas particuliers) ? L’indication de langue est donnée sur l’élément contenant le texte (attribut `lang` et/ou `xml:lang`) ; L’indication de langue est donnée sur un des éléments parents (attribut `lang` et/ou `xml:lang`)

---

## Code source constaté

### Intitulé anglais sans lang=en : Cookie compliance banner

```html
<div id="sliding-popup" role="alertdialog" aria-describedby="popup-text" aria-label="Cookie compliance banner" class="sliding-popup-bottom" style="height: auto; width: 100%; bottom: 0px;">
```

## Inventaire des constats sources

| Page | Identifiant source | Critère / test | Sélecteur | Observation | Provenance | Preuve principale |
|---|---|---|---|---|---|---|
| P01 | `P01-RGAA-8-7-LANGUAGE-CHANGE-001-005` | 8.7 / 8.7.1 | `#sliding-popup` | Intitulé anglais sans lang=en : Cookie compliance banner | RENDERED_DOM | `rgaa/preuves/P01/attempt-009/raw-dom.json` |
| P02 | `P02-RGAA-8-7-LANGUAGE-CHANGE-001-005` | 8.7 / 8.7.1 | `#sliding-popup` | Intitulé anglais sans lang=en : Cookie compliance banner | RENDERED_DOM | `rgaa/preuves/P02/attempt-002/raw-dom.json` |
| P03 | `P03-RGAA-8-7-LANGUAGE-CHANGE-001-005` | 8.7 / 8.7.1 | `#sliding-popup` | Intitulé anglais sans lang=en : Cookie compliance banner | RENDERED_DOM | `rgaa/preuves/P03/attempt-001/raw-dom.json` |
| P04 | `P04-RGAA-8-7-LANGUAGE-CHANGE-001-005` | 8.7 / 8.7.1 | `#sliding-popup` | Intitulé anglais sans lang=en : Cookie compliance banner | RENDERED_DOM | `rgaa/preuves/P04/attempt-001/raw-dom.json` |
| P05 | `P05-RGAA-8-7-LANGUAGE-CHANGE-001-006` | 8.7 / 8.7.1 | `#sliding-popup` | Intitulé anglais sans lang=en : Cookie compliance banner | RENDERED_DOM | `rgaa/preuves/P05/attempt-002/raw-dom.json` |
| P06 | `P06-RGAA-8-7-LANGUAGE-CHANGE-001-008` | 8.7 / 8.7.1 | `#sliding-popup` | Intitulé anglais sans lang=en : Cookie compliance banner | RENDERED_DOM | `rgaa/preuves/P06/attempt-004/raw-dom.json` |
| P07 | `P07-RGAA-8-7-LANGUAGE-CHANGE-001-006` | 8.7 / 8.7.1 | `#sliding-popup` | Intitulé anglais sans lang=en : Cookie compliance banner | RENDERED_DOM | `rgaa/preuves/P07/attempt-002/raw-dom.json` |
| P08 | `P08-RGAA-8-7-LANGUAGE-CHANGE-001-006` | 8.7 / 8.7.1 | `#sliding-popup` | Intitulé anglais sans lang=en : Cookie compliance banner | RENDERED_DOM | `rgaa/preuves/P08/attempt-001/raw-dom.json` |

---

## Analyse du défaut

Le bandeau de cookies porte le nom accessible anglais « Cookie compliance banner » alors que les pages sont déclarées en français. Aucun changement de langue ne s’applique à ce nom. Cette cause relève du template de consentement commun à P01 à P08.

## Impact utilisateur

Une synthèse vocale française peut prononcer ce nom avec des règles phonétiques inadaptées.

---

## Recommandations

### Solution 1 — Traduire le nom du bandeau (recommandée)

Employer un nom accessible français cohérent avec le titre visible du composant.

```html
<div id="sliding-popup" role="alertdialog"
     aria-label="Bandeau de gestion des cookies">…</div>
```

### Solution 2 — Borner la langue au nom anglais si celui-ci est conservé

Faire porter le nom par un texte dédié déclaré en anglais avec `aria-labelledby`. Ne pas appliquer `lang="en"` au dialogue entier, car son contenu reste en français.

```html
<div id="sliding-popup" role="alertdialog"
     aria-labelledby="cookie-banner-name">
  <span id="cookie-banner-name" class="fr-sr-only" lang="en">
    Cookie compliance banner
  </span>
  … contenu du bandeau en français …
</div>
```

## Comparaison avec le composant DSFR

**Composant concerné** : Bandeau de consentement

| Point contrôlé | DSFR / comportement attendu | Site audité |
|---|---|---|
| Langue de page | Français | Français |
| Nom accessible | Français ou langue déclarée | Anglais sans lang=en |
| Cause attribuée | Libellé paramétrable | Traduction du template de consentement |

Le constat est attribué à l’intégration observée. La présence de classes `fr-*` ne suffit pas à attribuer le défaut au DSFR natif.

---

## Vérification après correction

- [ ] Contrôler le nom accessible du bandeau sur P01 à P08.
- [ ] Vérifier qu’il est traduit ou qu’un texte dédié `lang="en"` fournit le nom via `aria-labelledby`.
- [ ] Vérifier que le contenu français du dialogue n’hérite pas de la langue anglaise.
- [ ] Écouter le nom avec un lecteur d’écran configuré en français.

La correction ne doit être considérée comme clôturée qu’après production d’une nouvelle preuve et recontrôle humain.

## Références

- [RGAA 4.1.2 — test 8.7.1](https://accessibilite.numerique.gouv.fr/methode/criteres-et-tests/#8.7.1)
- [DSFR 1.15.2 — composant consent](https://github.com/GouvernementFR/dsfr/tree/v1.15.2/src/dsfr/component/consent)
- Source factuelle : rapports HTML RGAA livrés pour les pages indiquées et constats `NC_CONFIRMEE` correspondants.
