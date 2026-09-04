# NC-P06-001 — Attributs size utilisés pour dimensionner les champs

**Statut** : Préqualification — NC confirmée dans les rapports sources  
**Référentiel** : RGAA 4.1.2  
**Sévérité** : Majeur  
**Justification de sévérité** : La présentation dépend du code HTML au lieu des styles. Elle devient plus difficile à adapter aux différents écrans, zooms et préférences d’affichage.  
**Date** : 2026-09-04  
**Composant / gabarit** : Champ de saisie / téléversement  
**Portée** : Locale — P06  
**Pages affectées** : P06  
**Constats sources regroupés** : 7

> Ces conclusions proviennent d’une préqualification instrumentée. Elles ne constituent ni un taux RGAA officiel ni une validation après correction.

---

## Pages et rapports sources

| Page | Nom | URL | Rapport RGAA |
|---|---|---|---|
| P06 | Formulaire Écrivez-nous | https://moa.douane.gouv.fr/formulaire-infos-douane-service | [P06-RGAA.html](../../RGAA/P06-RGAA.html) |

## Références RGAA

- **Critère 10.1** — Dans le site web, des feuilles de styles sont-elles utilisées pour contrôler la présentation de l’information ?
- **Test 10.1.2** — Dans chaque page web, les attributs servant à la présentation de l’information ne doivent pas être présents dans le code source généré des pages. Cette règle est-elle respectée ?

---

## Code source constaté

### Attributs de présentation sur <input> : size='40'

```html
<input class="fr-input form-text" style="display: none" data-drupal-selector="edit-societe" type="text" id="edit-societe" name="Societe" value="" size="40" maxlength="128">
```

### Attributs de présentation sur <input> : size='60'

```html
<input class="fr-input form-email required" autocomplete="email" data-drupal-selector="edit-adressemail" type="email" id="edit-adressemail" name="AdresseMail" value="" size="60" maxlength="128" required="required">
```

### Attributs de présentation sur <input> : size='22'

```html
<input accept=".jpg,.jpeg,.png,.pdf" data-drupal-selector="edit-document-upload" multiple="multiple" class="fr-upload js-form-file form-file fr-mt-3v" type="file" id="edit-document-upload" name="files[Document][]" size="22" aria-describedby="edit-document--description" data-once="fileValidate auto-file-upload">
```

## Inventaire des constats sources

| Page | Identifiant source | Critère / test | Sélecteur | Observation | Provenance | Preuve principale |
|---|---|---|---|---|---|---|
| P06 | `P06-RGAA-10-1-PRESENTATIONAL-ATTRIBUTE-002-017` | 10.1 / 10.1.2 | `#edit-societe` | Attributs de présentation sur <input> : size='40' | RENDERED_DOM | `rgaa/preuves/P06/attempt-004/raw-dom.json` |
| P06 | `P06-RGAA-10-1-PRESENTATIONAL-ATTRIBUTE-002-018` | 10.1 / 10.1.2 | `#edit-nom` | Attributs de présentation sur <input> : size='40' | RENDERED_DOM | `rgaa/preuves/P06/attempt-004/raw-dom.json` |
| P06 | `P06-RGAA-10-1-PRESENTATIONAL-ATTRIBUTE-002-019` | 10.1 / 10.1.2 | `#edit-prenom` | Attributs de présentation sur <input> : size='40' | RENDERED_DOM | `rgaa/preuves/P06/attempt-004/raw-dom.json` |
| P06 | `P06-RGAA-10-1-PRESENTATIONAL-ATTRIBUTE-002-020` | 10.1 / 10.1.2 | `#edit-pays` | Attributs de présentation sur <input> : size='40' | RENDERED_DOM | `rgaa/preuves/P06/attempt-004/raw-dom.json` |
| P06 | `P06-RGAA-10-1-PRESENTATIONAL-ATTRIBUTE-002-021` | 10.1 / 10.1.2 | `#edit-codepostal` | Attributs de présentation sur <input> : size='40' | RENDERED_DOM | `rgaa/preuves/P06/attempt-004/raw-dom.json` |
| P06 | `P06-RGAA-10-1-PRESENTATIONAL-ATTRIBUTE-002-022` | 10.1 / 10.1.2 | `#edit-adressemail` | Attributs de présentation sur <input> : size='60' | RENDERED_DOM | `rgaa/preuves/P06/attempt-004/raw-dom.json` |
| P06 | `P06-RGAA-10-1-PRESENTATIONAL-ATTRIBUTE-002-023` | 10.1 / 10.1.2 | `#edit-document-upload` | Attributs de présentation sur <input> : size='22' | RENDERED_DOM | `rgaa/preuves/P06/attempt-004/raw-dom.json` |

---

## Analyse du défaut

Sept champs du formulaire P06 utilisent l’attribut HTML `size` avec les valeurs 22, 40 ou 60. Pour le test 10.1.2, `size` est un attribut de présentation interdit, sauf sur l’élément `select`. La largeur des champs doit être pilotée par les feuilles de styles.

## Impact utilisateur

La présentation dépend du code HTML au lieu des styles. Elle devient plus difficile à adapter aux différents écrans, zooms et préférences d’affichage.

---

## Recommandations

### Solution 1 — Retirer size et dimensionner avec les styles (recommandée)

Supprimer les sept attributs `size` du template Drupal et utiliser les classes de grille ou une règle CSS adaptée au contexte.

```html
<label class="fr-label" for="edit-nom">Nom</label>
<input class="fr-input" autocomplete="family-name"
       id="edit-nom" name="Nom" type="text" maxlength="128">
```

## Comparaison avec le composant DSFR

**Composant concerné** : Champ de saisie / téléversement

| Point contrôlé | DSFR / comportement attendu | Site audité |
|---|---|---|
| Largeur | Contrôlée par classes et CSS | Attributs size sur sept champs |
| Code HTML | Sémantique et contraintes de saisie | Présentation mêlée au balisage |
| Cause attribuée | Composants stylés | Génération du formulaire Drupal |

Le constat est attribué à l’intégration observée. La présence de classes `fr-*` ne suffit pas à attribuer le défaut au DSFR natif.

---

## Vérification après correction

- [ ] Contrôler l’absence de `size` sur les sept champs inventoriés.
- [ ] Tester la mise en page à 320 px, à 200 % de zoom et avec l’agrandissement des textes.
- [ ] Vérifier que les contraintes métier comme `maxlength` restent inchangées.

La correction ne doit être considérée comme clôturée qu’après production d’une nouvelle preuve et recontrôle humain.

## Références

- [RGAA 4.1.2 — test 10.1.2](https://accessibilite.numerique.gouv.fr/methode/criteres-et-tests/#10.1.2)
- [DSFR 1.15.2 — composant input](https://github.com/GouvernementFR/dsfr/tree/v1.15.2/src/dsfr/component/input)
- [DSFR 1.15.2 — composant upload](https://github.com/GouvernementFR/dsfr/tree/v1.15.2/src/dsfr/component/upload)
- Source factuelle : rapports HTML RGAA livrés pour les pages indiquées et constats `NC_CONFIRMEE` correspondants.
