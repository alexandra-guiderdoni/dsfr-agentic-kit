# NC-P06-006 — Textes anglais du formulaire sans langue déclarée

**Statut** : Préqualification — NC confirmée dans les rapports sources  
**Référentiel** : RGAA 4.1.2  
**Sévérité** : Majeur  
**Justification de sévérité** : Les instructions peuvent être mal prononcées et moins bien comprises par une personne utilisant une synthèse vocale française.  
**Date** : 2026-09-04  
**Composant / gabarit** : Formulaire  
**Portée** : Locale — P06  
**Pages affectées** : P06  
**Constats sources regroupés** : 2

> Ces conclusions proviennent d’une préqualification instrumentée. Elles ne constituent ni un taux RGAA officiel ni une validation après correction.

---

## Pages et rapports sources

| Page | Nom | URL | Rapport RGAA |
|---|---|---|---|
| P06 | Formulaire Écrivez-nous | https://moa.douane.gouv.fr/formulaire-infos-douane-service | [P06-RGAA.html](../../RGAA/P06-RGAA.html) |

## Références RGAA

- **Critère 8.7** — Dans chaque page web, chaque changement de langue est-il indiqué dans le code source (hors cas particuliers) ?
- **Test 8.7.1** — Dans chaque page web, chaque texte écrit dans une langue différente de la langue par défaut vérifie-t-il une de ces conditions (hors cas particuliers) ? L’indication de langue est donnée sur l’élément contenant le texte (attribut `lang` et/ou `xml:lang`) ; L’indication de langue est donnée sur un des éléments parents (attribut `lang` et/ou `xml:lang`)

---

## Code source constaté

### Intitulé anglais sans lang=en : Maximum 2000 characters

```html
<span class="fr-hint-text">Maximum 2000 characters</span>
```

### Intitulé anglais sans lang=en : Conditions and submission

```html
<legend class="fr-sr-only" id="fieldset-ids-bottom-legend">
		Conditions and submission
	</legend>
```

## Inventaire des constats sources

| Page | Identifiant source | Critère / test | Sélecteur | Observation | Provenance | Preuve principale |
|---|---|---|---|---|---|---|
| P06 | `P06-RGAA-8-7-LANGUAGE-CHANGE-001-013` | 8.7 / 8.7.1 | `form.ids-eloquant-form > fieldset.fr-fieldset:nth-of-type(1) > div.fr-fieldset__element:nth-of-type(9) > div.fr-input-group > label.fr-label.js-form-required > span.fr-hint-text` | Intitulé anglais sans lang=en : Maximum 2000 characters | RENDERED_DOM | `rgaa/preuves/P06/attempt-004/raw-dom.json` |
| P06 | `P06-RGAA-8-7-LANGUAGE-CHANGE-001-014` | 8.7 / 8.7.1 | `#fieldset-ids-bottom-legend` | Intitulé anglais sans lang=en : Conditions and submission | RENDERED_DOM | `rgaa/preuves/P06/attempt-004/raw-dom.json` |

---

## Analyse du défaut

Deux textes du formulaire P06 restent en anglais : l’aide « Maximum 2000 characters » et la légende masquée « Conditions and submission ». Aucun attribut `lang="en"` ne s’applique. Ces textes relèvent du template du formulaire, distinct des libellés de navigation.

## Impact utilisateur

Les instructions peuvent être mal prononcées et moins bien comprises par une personne utilisant une synthèse vocale française.

---

## Recommandations

### Solution 1 — Traduire les deux textes d’interface (recommandée)

Employer des formulations françaises cohérentes avec le reste du formulaire.

```html
<span class="fr-hint-text">Maximum 2 000 caractères</span>
<legend class="fr-sr-only">Conditions et envoi</legend>
```

### Solution 2 — Déclarer la langue si l’anglais est conservé

Ajouter `lang="en"` directement sur chaque élément concerné.

```html
<span class="fr-hint-text" lang="en">Maximum 2000 characters</span>
<legend class="fr-sr-only" lang="en">Conditions and submission</legend>
```

## Comparaison avec le composant DSFR

**Composant concerné** : Formulaire

| Point contrôlé | DSFR / comportement attendu | Site audité |
|---|---|---|
| Aides et légendes | Français ou langue déclarée | Deux textes anglais sans lang=en |
| Cause attribuée | Libellés paramétrables | Traduction du template du formulaire |

Le constat est attribué à l’intégration observée. La présence de classes `fr-*` ne suffit pas à attribuer le défaut au DSFR natif.

---

## Vérification après correction

- [ ] Contrôler les deux formulations dans le DOM rendu de P06.
- [ ] Vérifier qu’elles sont traduites ou explicitement déclarées en anglais.
- [ ] Écouter l’aide et la légende avec un lecteur d’écran configuré en français.

La correction ne doit être considérée comme clôturée qu’après production d’une nouvelle preuve et recontrôle humain.

## Références

- [RGAA 4.1.2 — test 8.7.1](https://accessibilite.numerique.gouv.fr/methode/criteres-et-tests/#8.7.1)
- [DSFR 1.15.2 — composant input](https://github.com/GouvernementFR/dsfr/tree/v1.15.2/src/dsfr/component/input)
- Source factuelle : rapports HTML RGAA livrés pour les pages indiquées et constats `NC_CONFIRMEE` correspondants.
