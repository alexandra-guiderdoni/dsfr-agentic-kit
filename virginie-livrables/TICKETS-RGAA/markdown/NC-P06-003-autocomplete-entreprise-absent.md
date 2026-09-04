# NC-P06-003 — Finalité du champ entreprise non déclarée

**Statut** : Préqualification — NC confirmée dans les rapports sources  
**Référentiel** : RGAA 4.1.2  
**Sévérité** : Majeur  
**Justification de sévérité** : Les outils de remplissage automatique et les adaptations personnalisées ne peuvent pas reconnaître le nom de l’organisation attendu dans ce champ.  
**Date** : 2026-09-04  
**Composant / gabarit** : Champ de saisie  
**Portée** : Locale — P06  
**Pages affectées** : P06  
**Constats sources regroupés** : 1

> Ces conclusions proviennent d’une préqualification instrumentée. Elles ne constituent ni un taux RGAA officiel ni une validation après correction.

---

## Pages et rapports sources

| Page | Nom | URL | Rapport RGAA |
|---|---|---|---|
| P06 | Formulaire Écrivez-nous | https://moa.douane.gouv.fr/formulaire-infos-douane-service | [P06-RGAA.html](../../RGAA/P06-RGAA.html) |

## Références RGAA

- **Critère 11.13** — La finalité d’un champ de saisie peut-elle être déduite pour faciliter le remplissage automatique des champs avec les données de l’utilisateur ?
- **Test 11.13.1** — Chaque champ de formulaire dont l’objet se rapporte à une information concernant l’utilisateur vérifie-t-il ces conditions ? Le champ de formulaire possède un attribut `autocomplete `; L’attribut `autocomplete` est pourvu d’une valeur présente dans la liste des valeurs possibles pour l’attribut `autocomplete` associés à un champ de formulaire ; La valeur indiquée pour l’attribut `autocomplete` est pertinente au regard du type d’information attendu.

---

## Code source constaté

### P06 — champ Société observé dans la collecte initiale

```html
<input class="fr-input form-text" style="display: none" data-drupal-selector="edit-societe" type="text" id="edit-societe" name="Societe" value="" size="40" maxlength="128">
```

## Inventaire des constats sources

| Page | Identifiant source | Critère / test | Sélecteur | Observation | Provenance | Preuve principale |
|---|---|---|---|---|---|---|
| P06 | `RGAA-P06-Q-012` | 11.13 / 11.13.1 | `#edit-societe` | Dans la variante Un professionnel, le champ Nom de l’entreprise devient visible avec son label, mais ne possède pas autocomplete=organization. | MEASUREMENTS | `preuves-p06-complet/P06-COLLECTE-COMPLETE.json` |

---

## Analyse du défaut

Dans la variante « Un professionnel », le champ « Nom de l’entreprise » collecte une information sur l’utilisateur mais ne possède aucun attribut `autocomplete`. La valeur standard `organization` permet aux aides à la saisie d’identifier cette finalité.

## Impact utilisateur

Les outils de remplissage automatique et les adaptations personnalisées ne peuvent pas reconnaître le nom de l’organisation attendu dans ce champ.

---

## Recommandations

### Solution 1 — Ajouter autocomplete=organization (recommandée)

Déclarer la finalité avec la valeur normalisée correspondant au nom d’une entreprise ou organisation.

```html
<label class="fr-label" for="edit-societe">Nom de l’entreprise</label>
<input class="fr-input" id="edit-societe" name="Societe"
       type="text" autocomplete="organization">
```

## Comparaison avec le composant DSFR

**Composant concerné** : Champ de saisie

| Point contrôlé | DSFR / comportement attendu | Site audité |
|---|---|---|
| Finalité | Attribut autocomplete pertinent | Attribut absent |
| Valeur attendue | organization | Aucune |
| Cause attribuée | Attribut HTML supporté | Configuration du champ Drupal |

Le constat est attribué à l’intégration observée. La présence de classes `fr-*` ne suffit pas à attribuer le défaut au DSFR natif.

---

## Vérification après correction

- [ ] Afficher la variante « Un professionnel » et inspecter `#edit-societe`.
- [ ] Vérifier la présence exacte de `autocomplete="organization"`.
- [ ] Tester avec un gestionnaire de saisie automatique compatible.

La correction ne doit être considérée comme clôturée qu’après production d’une nouvelle preuve et recontrôle humain.

## Références

- [RGAA 4.1.2 — test 11.13.1](https://accessibilite.numerique.gouv.fr/methode/criteres-et-tests/#11.13.1)
- [DSFR 1.15.2 — composant input](https://github.com/GouvernementFR/dsfr/tree/v1.15.2/src/dsfr/component/input)
- [HTML — valeurs autocomplete](https://html.spec.whatwg.org/multipage/form-control-infrastructure.html#autofill)
- Source factuelle : rapports HTML RGAA livrés pour les pages indiquées et constats `NC_CONFIRMEE` correspondants.
