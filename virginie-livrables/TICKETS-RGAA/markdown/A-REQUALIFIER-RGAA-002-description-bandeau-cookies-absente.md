# A-REQUALIFIER-RGAA-002 — Description du bandeau de cookies non reliée

**Statut** : À requalifier avant transmission comme non-conformité  
**Référentiel** : RGAA 4.1.2  
**Sévérité** : Majeur  
**Justification de sévérité** : Le lecteur d’écran ne restitue pas la description attendue du bandeau. La personne peut manquer l’explication utile avant de choisir ses préférences de cookies.  
**Date** : 2026-09-04  
**Composant / gabarit** : Bandeau de consentement  
**Portée** : Transverse — P01, P02, P03, P04, P05, P06, P07  
**Pages affectées** : P01, P02, P03, P04, P05, P06, P07  
**Constats sources regroupés** : 7

> Ces conclusions proviennent d’une préqualification instrumentée. Elles ne constituent ni un taux RGAA officiel ni une validation après correction.

> **Alerte méthodologique :** Un aria-describedby orphelin ne suffit pas, à lui seul, à établir l’échec de 7.1.1 si le nom, le rôle, les états et les informations nécessaires restent accessibles. P08 et P09 classent d’ailleurs ce même signal A_RETESTER. Une vérification fonctionnelle est requise.

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

## Références RGAA

- **Critère 7.1** — Chaque script est-il, si nécessaire, compatible avec les technologies d’assistance ?
- **Test 7.1.1** — Chaque script qui génère ou contrôle un composant d’interface vérifie-t-il, si nécessaire, une de ces conditions ? Le nom, le rôle, la valeur, le paramétrage et les changements d’états sont accessibles aux technologies d’assistance via une API d’accessibilité ; Un composant d’interface accessible permettant d’accéder aux mêmes fonctionnalités est présent dans la page ; Une alternative accessible permet d’accéder aux mêmes fonctionnalités.

---

## Code source constaté

### Référence absente : popup-text

```html
<div id="sliding-popup" role="alertdialog" aria-describedby="popup-text" aria-label="Cookie compliance banner" class="sliding-popup-bottom" style="height: auto; width: 100%; bottom: 0px;">
```

## Inventaire des constats sources

| Page | Identifiant source | Critère / test | Sélecteur | Observation | Provenance | Preuve principale |
|---|---|---|---|---|---|---|
| P01 | `P01-RGAA-7-1-ARIA-REFERENCE-002-001` | 7.1 / 7.1.1 | `#sliding-popup` | aria-describedby référence #popup-text absent | RENDERED_DOM | `rgaa/preuves/P01/attempt-009/raw-dom.json` |
| P02 | `P02-RGAA-7-1-ARIA-REFERENCE-002-001` | 7.1 / 7.1.1 | `#sliding-popup` | aria-describedby référence #popup-text absent | RENDERED_DOM | `rgaa/preuves/P02/attempt-002/raw-dom.json` |
| P03 | `P03-RGAA-7-1-ARIA-REFERENCE-002-001` | 7.1 / 7.1.1 | `#sliding-popup` | aria-describedby référence #popup-text absent | RENDERED_DOM | `rgaa/preuves/P03/attempt-001/raw-dom.json` |
| P04 | `P04-RGAA-7-1-ARIA-REFERENCE-002-001` | 7.1 / 7.1.1 | `#sliding-popup` | aria-describedby référence #popup-text absent | RENDERED_DOM | `rgaa/preuves/P04/attempt-001/raw-dom.json` |
| P05 | `P05-RGAA-7-1-ARIA-REFERENCE-002-001` | 7.1 / 7.1.1 | `#sliding-popup` | aria-describedby référence #popup-text absent | RENDERED_DOM | `rgaa/preuves/P05/attempt-002/raw-dom.json` |
| P06 | `P06-RGAA-7-1-ARIA-REFERENCE-002-002` | 7.1 / 7.1.1 | `#sliding-popup` | aria-describedby référence #popup-text absent | RENDERED_DOM | `rgaa/preuves/P06/attempt-004/raw-dom.json` |
| P07 | `P07-RGAA-7-1-ARIA-REFERENCE-002-001` | 7.1 / 7.1.1 | `#sliding-popup` | aria-describedby référence #popup-text absent | RENDERED_DOM | `rgaa/preuves/P07/attempt-002/raw-dom.json` |

---

## Analyse du défaut

Le bandeau de consentement cite `popup-text` dans `aria-describedby` sur P01 à P07, mais cette cible est absente. La relation ne transmet une description que si l’identifiant référencé existe dans le même document. Le défaut relève du template de consentement commun.

## Impact utilisateur

Le lecteur d’écran ne restitue pas la description attendue du bandeau. La personne peut manquer l’explication utile avant de choisir ses préférences de cookies.

---

## Recommandations

### Solution 1 — Créer une description utile et la relier (recommandée)

Ajouter un texte utile avec l’identifiant exact `popup-text`, puis conserver `aria-describedby`.

```html
<div id="sliding-popup" role="alertdialog"
     aria-describedby="popup-text" aria-label="Gestion des cookies">
  <p id="popup-text">Ce site utilise des cookies…</p>
  <!-- actions -->
</div>
```

### Solution 2 — Supprimer une référence obsolète

Si le bandeau est autonome sans description dédiée, retirer l’attribut. Ne pas créer un élément vide.

```html
<div id="sliding-popup" role="alertdialog"
     aria-label="Gestion des cookies">
  <!-- contenu complet et autonome -->
</div>
```

## Comparaison avec le composant DSFR

**Composant concerné** : Bandeau de consentement

| Point contrôlé | DSFR / comportement attendu | Site audité |
|---|---|---|
| Relation de description | Chaque IDREF cible un élément existant | popup-text absent |
| Texte d’aide | Présent et relié lorsqu’il est nécessaire | Description non restituable |
| Cause attribuée | Contrat ARIA valide | Template de consentement intégré |

Le constat est attribué à l’intégration observée. La présence de classes `fr-*` ne suffit pas à attribuer le défaut au DSFR natif.

---

## Vérification après correction

- [ ] Contrôler que `popup-text` existe et reste unique si `aria-describedby` est conservé.
- [ ] Inspecter la description calculée du bandeau.
- [ ] Vérifier la restitution avec un lecteur d’écran réel.

La correction ne doit être considérée comme clôturée qu’après production d’une nouvelle preuve et recontrôle humain.

## Références

- [RGAA 4.1.2 — test 7.1.1](https://accessibilite.numerique.gouv.fr/methode/criteres-et-tests/#7.1.1)
- [DSFR 1.15.2 — composant consent](https://github.com/GouvernementFR/dsfr/tree/v1.15.2/src/dsfr/component/consent)
- Source factuelle : rapports HTML RGAA livrés pour les pages indiquées et constats `NC_CONFIRMEE` correspondants.
