# NC-TRANSVERSE-001 — Recherche visible et focalisable sous aria-hidden

**Statut** : Préqualification — NC confirmée dans les rapports sources  
**Référentiel** : RGAA 4.1.2  
**Sévérité** : Bloquant  
**Justification de sévérité** : La navigation clavier et la restitution vocale sont désynchronisées. Le champ et le bouton peuvent être impossibles à identifier ou à utiliser avec une technologie d’assistance.  
**Date** : 2026-09-04  
**Composant / gabarit** : En-tête / barre de recherche  
**Portée** : Transverse — P01, P02, P03, P04, P05, P06, P07, P08, P09  
**Pages affectées** : P01, P02, P03, P04, P05, P06, P07, P08, P09  
**Constats sources regroupés** : 34

> Ces conclusions proviennent d’une préqualification instrumentée. Elles ne constituent ni un taux RGAA officiel ni une validation après correction.

> **Alerte méthodologique :** Le rattachement au test 10.8.1 est direct. Le rattachement secondaire au test 7.1.1 doit rester appuyé par la preuve d’arbre d’accessibilité montrant la perte de restitution du composant.

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

- **Critère 7.1** — Chaque script est-il, si nécessaire, compatible avec les technologies d’assistance ?
- **Critère 10.8** — Pour chaque page web, les contenus cachés ont-ils vocation à être ignorés par les technologies d’assistance ?
- **Test 7.1.1** — Chaque script qui génère ou contrôle un composant d’interface vérifie-t-il, si nécessaire, une de ces conditions ? Le nom, le rôle, la valeur, le paramétrage et les changements d’états sont accessibles aux technologies d’assistance via une API d’accessibilité ; Un composant d’interface accessible permettant d’accéder aux mêmes fonctionnalités est présent dans la page ; Une alternative accessible permet d’accéder aux mêmes fonctionnalités.
- **Test 10.8.1** — Dans chaque page web, chaque contenu caché vérifie-t-il une de ces conditions ? Le contenu caché a vocation à être ignoré par les technologies d’assistance ; Le contenu caché n’a pas vocation à être ignoré par les technologies d’assistance et est rendu restituable par les technologies d’assistance suite à une action de l’utilisateur réalisable au clavier ou par tout dispositif de pointage sur un élément précédent le contenu caché ou suite à un repositionnement du focus dessus.

---

## Code source constaté

### P01 — formulaire de recherche et état observé

```html
<form action="/recherche" method="get" class="fr-search-bar" id="search" role="search" aria-hidden="true">
								<label class="fr-label" for="search-input">
									Rechercher
								</label>
								<input class="fr-input" name="query" aria-describedby="search-input-messages" placeholder="Rechercher" id="search-input" type="search" style="">
								<div class="fr-messages-group" id="search-input-messages" aria-live="polite"></div>
								<button title="Rechercher" type="submit" id="search-btn" class="fr-btn">Rechercher</button>
							</form>
```

## Inventaire des constats sources

| Page | Identifiant source | Critère / test | Sélecteur | Observation | Provenance | Preuve principale |
|---|---|---|---|---|---|---|
| P01 | `P01-RGAA-10-8-HIDDEN-FOCUS-001-010` | 10.8 / 10.8.1 | `#search-input` | Focus atteint à la tabulation 10 sous aria-hidden=true | KEYBOARD_TRACE | `rgaa/preuves/P01/attempt-009/raw-dom.json` |
| P01 | `P01-RGAA-10-8-HIDDEN-FOCUS-001-012` | 10.8 / 10.8.1 | `#search-btn` | Focus atteint à la tabulation 11 sous aria-hidden=true | KEYBOARD_TRACE | `rgaa/preuves/P01/attempt-009/raw-dom.json` |
| P01 | `P01-RGAA-7-1-SCRIPT-ARIA-HIDDEN-003-009` | 7.1 / 7.1.1 | `#search-input` | Contrôle scripté focalisé à la tabulation 10 sous aria-hidden=true | KEYBOARD_TRACE | `rgaa/preuves/P01/attempt-009/raw-dom.json` |
| P01 | `P01-RGAA-7-1-SCRIPT-ARIA-HIDDEN-003-011` | 7.1 / 7.1.1 | `#search-btn` | Contrôle scripté focalisé à la tabulation 11 sous aria-hidden=true | KEYBOARD_TRACE | `rgaa/preuves/P01/attempt-009/raw-dom.json` |
| P02 | `P02-RGAA-10-8-HIDDEN-FOCUS-001-018` | 10.8 / 10.8.1 | `#search-input` | Focus atteint à la tabulation 10 sous aria-hidden=true | KEYBOARD_TRACE | `rgaa/preuves/P02/attempt-002/raw-dom.json` |
| P02 | `P02-RGAA-10-8-HIDDEN-FOCUS-001-020` | 10.8 / 10.8.1 | `#search-btn` | Focus atteint à la tabulation 11 sous aria-hidden=true | KEYBOARD_TRACE | `rgaa/preuves/P02/attempt-002/raw-dom.json` |
| P02 | `P02-RGAA-7-1-SCRIPT-ARIA-HIDDEN-003-017` | 7.1 / 7.1.1 | `#search-input` | Contrôle scripté focalisé à la tabulation 10 sous aria-hidden=true | KEYBOARD_TRACE | `rgaa/preuves/P02/attempt-002/raw-dom.json` |
| P02 | `P02-RGAA-7-1-SCRIPT-ARIA-HIDDEN-003-019` | 7.1 / 7.1.1 | `#search-btn` | Contrôle scripté focalisé à la tabulation 11 sous aria-hidden=true | KEYBOARD_TRACE | `rgaa/preuves/P02/attempt-002/raw-dom.json` |
| P03 | `P03-RGAA-10-8-HIDDEN-FOCUS-001-013` | 10.8 / 10.8.1 | `#search-input` | Focus atteint à la tabulation 10 sous aria-hidden=true | KEYBOARD_TRACE | `rgaa/preuves/P03/attempt-001/raw-dom.json` |
| P03 | `P03-RGAA-10-8-HIDDEN-FOCUS-001-015` | 10.8 / 10.8.1 | `#search-btn` | Focus atteint à la tabulation 11 sous aria-hidden=true | KEYBOARD_TRACE | `rgaa/preuves/P03/attempt-001/raw-dom.json` |
| P03 | `P03-RGAA-7-1-SCRIPT-ARIA-HIDDEN-003-012` | 7.1 / 7.1.1 | `#search-input` | Contrôle scripté focalisé à la tabulation 10 sous aria-hidden=true | KEYBOARD_TRACE | `rgaa/preuves/P03/attempt-001/raw-dom.json` |
| P03 | `P03-RGAA-7-1-SCRIPT-ARIA-HIDDEN-003-014` | 7.1 / 7.1.1 | `#search-btn` | Contrôle scripté focalisé à la tabulation 11 sous aria-hidden=true | KEYBOARD_TRACE | `rgaa/preuves/P03/attempt-001/raw-dom.json` |
| P04 | `P04-RGAA-10-8-HIDDEN-FOCUS-001-013` | 10.8 / 10.8.1 | `#search-input` | Focus atteint à la tabulation 10 sous aria-hidden=true | KEYBOARD_TRACE | `rgaa/preuves/P04/attempt-001/raw-dom.json` |
| P04 | `P04-RGAA-10-8-HIDDEN-FOCUS-001-015` | 10.8 / 10.8.1 | `#search-btn` | Focus atteint à la tabulation 11 sous aria-hidden=true | KEYBOARD_TRACE | `rgaa/preuves/P04/attempt-001/raw-dom.json` |
| P04 | `P04-RGAA-7-1-SCRIPT-ARIA-HIDDEN-003-012` | 7.1 / 7.1.1 | `#search-input` | Contrôle scripté focalisé à la tabulation 10 sous aria-hidden=true | KEYBOARD_TRACE | `rgaa/preuves/P04/attempt-001/raw-dom.json` |
| P04 | `P04-RGAA-7-1-SCRIPT-ARIA-HIDDEN-003-014` | 7.1 / 7.1.1 | `#search-btn` | Contrôle scripté focalisé à la tabulation 11 sous aria-hidden=true | KEYBOARD_TRACE | `rgaa/preuves/P04/attempt-001/raw-dom.json` |
| P05 | `P05-RGAA-10-8-HIDDEN-FOCUS-001-014` | 10.8 / 10.8.1 | `#search-input` | Focus atteint à la tabulation 10 sous aria-hidden=true | KEYBOARD_TRACE | `rgaa/preuves/P05/attempt-002/raw-dom.json` |
| P05 | `P05-RGAA-10-8-HIDDEN-FOCUS-001-016` | 10.8 / 10.8.1 | `#search-btn` | Focus atteint à la tabulation 11 sous aria-hidden=true | KEYBOARD_TRACE | `rgaa/preuves/P05/attempt-002/raw-dom.json` |
| P05 | `P05-RGAA-7-1-SCRIPT-ARIA-HIDDEN-003-013` | 7.1 / 7.1.1 | `#search-input` | Contrôle scripté focalisé à la tabulation 10 sous aria-hidden=true | KEYBOARD_TRACE | `rgaa/preuves/P05/attempt-002/raw-dom.json` |
| P05 | `P05-RGAA-7-1-SCRIPT-ARIA-HIDDEN-003-015` | 7.1 / 7.1.1 | `#search-btn` | Contrôle scripté focalisé à la tabulation 11 sous aria-hidden=true | KEYBOARD_TRACE | `rgaa/preuves/P05/attempt-002/raw-dom.json` |
| P06 | `P06-RGAA-10-8-HIDDEN-FOCUS-001-025` | 10.8 / 10.8.1 | `#search-input` | Focus atteint à la tabulation 10 sous aria-hidden=true | KEYBOARD_TRACE | `rgaa/preuves/P06/attempt-004/raw-dom.json` |
| P06 | `P06-RGAA-10-8-HIDDEN-FOCUS-001-027` | 10.8 / 10.8.1 | `#search-btn` | Focus atteint à la tabulation 11 sous aria-hidden=true | KEYBOARD_TRACE | `rgaa/preuves/P06/attempt-004/raw-dom.json` |
| P06 | `P06-RGAA-7-1-SCRIPT-ARIA-HIDDEN-003-024` | 7.1 / 7.1.1 | `#search-input` | Contrôle scripté focalisé à la tabulation 10 sous aria-hidden=true | KEYBOARD_TRACE | `rgaa/preuves/P06/attempt-004/raw-dom.json` |
| P06 | `P06-RGAA-7-1-SCRIPT-ARIA-HIDDEN-003-026` | 7.1 / 7.1.1 | `#search-btn` | Contrôle scripté focalisé à la tabulation 11 sous aria-hidden=true | KEYBOARD_TRACE | `rgaa/preuves/P06/attempt-004/raw-dom.json` |
| P07 | `P07-RGAA-10-8-HIDDEN-FOCUS-001-012` | 10.8 / 10.8.1 | `#search-input` | Focus atteint à la tabulation 10 sous aria-hidden=true | KEYBOARD_TRACE | `rgaa/preuves/P07/attempt-002/raw-dom.json` |
| P07 | `P07-RGAA-10-8-HIDDEN-FOCUS-001-014` | 10.8 / 10.8.1 | `#search-btn` | Focus atteint à la tabulation 11 sous aria-hidden=true | KEYBOARD_TRACE | `rgaa/preuves/P07/attempt-002/raw-dom.json` |
| P07 | `P07-RGAA-7-1-SCRIPT-ARIA-HIDDEN-003-011` | 7.1 / 7.1.1 | `#search-input` | Contrôle scripté focalisé à la tabulation 10 sous aria-hidden=true | KEYBOARD_TRACE | `rgaa/preuves/P07/attempt-002/raw-dom.json` |
| P07 | `P07-RGAA-7-1-SCRIPT-ARIA-HIDDEN-003-013` | 7.1 / 7.1.1 | `#search-btn` | Contrôle scripté focalisé à la tabulation 11 sous aria-hidden=true | KEYBOARD_TRACE | `rgaa/preuves/P07/attempt-002/raw-dom.json` |
| P08 | `P08-RGAA-10-8-HIDDEN-FOCUS-001-012` | 10.8 / 10.8.1 | `#search-input` | Focus atteint à la tabulation 10 sous aria-hidden=true | KEYBOARD_TRACE | `rgaa/preuves/P08/attempt-001/raw-dom.json` |
| P08 | `P08-RGAA-10-8-HIDDEN-FOCUS-001-014` | 10.8 / 10.8.1 | `#search-btn` | Focus atteint à la tabulation 11 sous aria-hidden=true | KEYBOARD_TRACE | `rgaa/preuves/P08/attempt-001/raw-dom.json` |
| P08 | `P08-RGAA-7-1-SCRIPT-ARIA-HIDDEN-003-011` | 7.1 / 7.1.1 | `#search-input` | Contrôle scripté focalisé à la tabulation 10 sous aria-hidden=true | KEYBOARD_TRACE | `rgaa/preuves/P08/attempt-001/raw-dom.json` |
| P08 | `P08-RGAA-7-1-SCRIPT-ARIA-HIDDEN-003-013` | 7.1 / 7.1.1 | `#search-btn` | Contrôle scripté focalisé à la tabulation 11 sous aria-hidden=true | KEYBOARD_TRACE | `rgaa/preuves/P08/attempt-001/raw-dom.json` |
| P09 | `RGAA-P09-Q-007` | 10.8 / 10.8.1 | `#search-input, #search-btn` | Le champ et le bouton de recherche sont atteints à la tabulation sous #search[aria-hidden=true]. | MEASUREMENTS | `rgaa/preuves/P09/attempt-001/evidence.json` |
| P09 | `RGAA-P09-Q-003` | 7.1 / 7.1.1 | `#search` | La recherche visible conserve aria-hidden=true et ses contrôles restent atteignables au clavier. | MEASUREMENTS | `rgaa/preuves/P09/attempt-001/evidence.json` |

---

## Analyse du défaut

Le formulaire de recherche conserve `aria-hidden="true"` alors que son champ et son bouton sont visibles et atteints par la tabulation. L’attribut retire le sous-arbre de l’arbre d’accessibilité sans le retirer du parcours clavier. La personne au clavier peut donc placer le focus sur des contrôles qu’un lecteur d’écran ne restitue pas. Une même cause racine met en échec les tests 7.1.1 et 10.8.1. Le défaut provient du gabarit d’en-tête commun aux neuf pages.

## Impact utilisateur

La navigation clavier et la restitution vocale sont désynchronisées. Le champ et le bouton peuvent être impossibles à identifier ou à utiliser avec une technologie d’assistance.

---

## Recommandations

### Solution 1 — Synchroniser l’état masqué et l’état ouvert (recommandée)

Lorsque la recherche est fermée, retirer tout le panneau du rendu et du parcours clavier avec `hidden` ou le mécanisme natif du composant DSFR. Retirer cet état avant de déplacer le focus dans la recherche. Ne pas maintenir `aria-hidden="true"` sur un formulaire visible.

```html
<!-- État ouvert : le formulaire est exposé et utilisable -->
<div id="header-search" class="fr-header__search fr-modal">
  <form action="/recherche" method="get" class="fr-search-bar"
        id="search" role="search">
    <label class="fr-label" for="search-input">Rechercher</label>
    <input class="fr-input" id="search-input" name="query" type="search">
    <button class="fr-btn" id="search-btn" type="submit">Rechercher</button>
  </form>
</div>
```

### Solution 2 — Reprendre le cycle d’ouverture du composant DSFR

Aligner le template Drupal et son JavaScript sur le composant d’en-tête DSFR : le panneau fermé ne doit pas exposer de contrôles focalisables et le panneau ouvert ne doit pas rester masqué aux technologies d’assistance.

```html
<!-- État fermé : aucun descendant ne reçoit le focus -->
<div id="header-search" class="fr-header__search fr-modal" hidden>
  <!-- formulaire de recherche -->
</div>
```

## Comparaison avec le composant DSFR

**Composant concerné** : En-tête / barre de recherche

| Point contrôlé | DSFR / comportement attendu | Site audité |
|---|---|---|
| État ouvert | Contenu exposé dans l’arbre d’accessibilité | Formulaire encore aria-hidden |
| Parcours clavier | Contrôles atteignables uniquement à l’ouverture | Champ et bouton atteignables sous aria-hidden |
| Cause attribuée | Comportement géré par le composant | Intégration / synchronisation d’état |

Le constat est attribué à l’intégration observée. La présence de classes `fr-*` ne suffit pas à attribuer le défaut au DSFR natif.

---

## Vérification après correction

- [ ] Tester les états fermé puis ouvert au clavier sur chaque gabarit.
- [ ] Vérifier qu’aucun descendant d’un élément `aria-hidden="true"` ne reçoit le focus.
- [ ] À l’ouverture, contrôler le rôle, le nom et la présence des contrôles dans l’arbre d’accessibilité.
- [ ] Compléter par NVDA + Firefox ou VoiceOver + Safari avant clôture.

La correction ne doit être considérée comme clôturée qu’après production d’une nouvelle preuve et recontrôle humain.

## Références

- [RGAA 4.1.2 — test 7.1.1](https://accessibilite.numerique.gouv.fr/methode/criteres-et-tests/#7.1.1)
- [RGAA 4.1.2 — test 10.8.1](https://accessibilite.numerique.gouv.fr/methode/criteres-et-tests/#10.8.1)
- [DSFR 1.15.2 — composant search](https://github.com/GouvernementFR/dsfr/tree/v1.15.2/src/dsfr/component/search)
- [DSFR 1.15.2 — composant header](https://github.com/GouvernementFR/dsfr/tree/v1.15.2/src/dsfr/component/header)
- Source factuelle : rapports HTML RGAA livrés pour les pages indiquées et constats `NC_CONFIRMEE` correspondants.
