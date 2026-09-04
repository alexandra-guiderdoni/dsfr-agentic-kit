# NC-P06-002 — Champ entreprise optionnel annoncé comme obligatoire

**Statut** : Préqualification — NC confirmée dans les rapports sources  
**Référentiel** : RGAA 4.1.2  
**Sévérité** : Majeur  
**Justification de sévérité** : La personne peut croire à tort qu’elle doit fournir le nom de son entreprise, ce qui augmente la charge de saisie et peut conduire à communiquer une donnée non requise.  
**Date** : 2026-09-04  
**Composant / gabarit** : Champ de saisie  
**Portée** : Locale — P06  
**Pages affectées** : P06  
**Constats sources regroupés** : 1

> Ces conclusions proviennent d’une préqualification instrumentée. Elles ne constituent ni un taux RGAA officiel ni une validation après correction.

> **Alerte méthodologique :** La note technique du critère 11.10 autorise l’instruction globale « tous les champs sont obligatoires sauf… » uniquement si chaque champ facultatif porte une mention visible dans son libellé ou sa légende, et si les autres champs conservent required ou aria-required=true.

---

## Pages et rapports sources

| Page | Nom | URL | Rapport RGAA |
|---|---|---|---|
| P06 | Formulaire Écrivez-nous | https://moa.douane.gouv.fr/formulaire-infos-douane-service | [P06-RGAA.html](../../RGAA/P06-RGAA.html) |

## Références RGAA

- **Critère 11.10** — Dans chaque formulaire, le contrôle de saisie est-il utilisé de manière pertinente (hors cas particuliers) ?
- **Test 11.10.1** — Les indications du caractère obligatoire de la saisie des champs vérifient-elles une de ces conditions (hors cas particuliers) ? Une indication de champ obligatoire est visible et permet d’identifier nommément le champ concerné préalablement à la validation du formulaire ; Le champ obligatoire dispose de l’attribut `aria-required="true"` ou `required` préalablement à la validation du formulaire.

---

## Code source constaté

### P06 — champ Société et état interactif mesuré

```html
<input class="fr-input form-text" style="display: none" data-drupal-selector="edit-societe" type="text" id="edit-societe" name="Societe" value="" size="40" maxlength="128">
<!-- État interactif mesuré après sélection « Un professionnel » :
     instruction globale : « Sauf mention contraire, tous les champs sont obligatoires. » ;
     visible=true ; required=false ; aria-required absent ;
     valeur vide acceptée ; aucune mention « optionnel ». -->
```

## Inventaire des constats sources

| Page | Identifiant source | Critère / test | Sélecteur | Observation | Provenance | Preuve principale |
|---|---|---|---|---|---|---|
| P06 | `RGAA-P06-Q-013` | 11.10 / 11.10.1 | `#edit-societe` | L’instruction annonce que tous les champs sont obligatoires sauf mention contraire. Dans la variante Un professionnel, Société est visible, accepte une valeur vide et ne porte aucune mention optionnel. | MEASUREMENTS | `preuves-p06-complet/P06-CHAMP-SOCIETE-OPTIONNEL.json` |

---

## Analyse du défaut

L’instruction générale annonce que tous les champs sont obligatoires sauf mention contraire. Dans la variante « Un professionnel », le champ « Nom de l’entreprise » est visible, accepte une valeur vide et ne porte aucune mention « optionnel ». L’information donnée avant la saisie est donc contradictoire avec la validation réelle du formulaire.

## Impact utilisateur

La personne peut croire à tort qu’elle doit fournir le nom de son entreprise, ce qui augmente la charge de saisie et peut conduire à communiquer une donnée non requise.

---

## Recommandations

### Solution 1 — Indiquer explicitement que le champ est optionnel (recommandée)

Conserver le comportement métier actuel et ajouter une mention visible dans l’étiquette du champ.

```html
<label class="fr-label" for="edit-societe">
  Nom de l’entreprise
  <span class="fr-hint-text">Optionnel</span>
</label>
<input class="fr-input" id="edit-societe" name="Societe" type="text">
```

### Solution 2 — Rendre le champ réellement obligatoire après décision métier

Si la donnée est indispensable, ajouter l’indication visible et l’attribut `required`. Ne pas appliquer cette option sans validation métier.

```html
<label class="fr-label" for="edit-societe">
  Nom de l’entreprise <span aria-hidden="true">*</span>
</label>
<input class="fr-input" id="edit-societe" name="Societe"
       type="text" required>
```

## Comparaison avec le composant DSFR

**Composant concerné** : Champ de saisie

| Point contrôlé | DSFR / comportement attendu | Site audité |
|---|---|---|
| Information avant saisie | Caractère obligatoire ou optionnel cohérent | Instruction globale inexacte |
| Validation native | Cohérente avec l’indication visible | Le champ accepte une valeur vide |
| Cause attribuée | Libellé paramétrable | Règle métier / template du formulaire |

Le constat est attribué à l’intégration observée. La présence de classes `fr-*` ne suffit pas à attribuer le défaut au DSFR natif.

---

## Vérification après correction

- [ ] Sélectionner la variante « Un professionnel ».
- [ ] Vérifier que le caractère optionnel ou obligatoire est visible avant la saisie.
- [ ] Soumettre le formulaire sans valeur après validation métier et contrôler la cohérence du comportement.

La correction ne doit être considérée comme clôturée qu’après production d’une nouvelle preuve et recontrôle humain.

## Références

- [RGAA 4.1.2 — test 11.10.1](https://accessibilite.numerique.gouv.fr/methode/criteres-et-tests/#11.10.1)
- [DSFR 1.15.2 — composant input](https://github.com/GouvernementFR/dsfr/tree/v1.15.2/src/dsfr/component/input)
- Source factuelle : rapports HTML RGAA livrés pour les pages indiquées et constats `NC_CONFIRMEE` correspondants.
