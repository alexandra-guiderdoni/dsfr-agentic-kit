# A-REQUALIFIER-RGAA-003 — Aide du champ de téléversement non reliée

**Statut** : À requalifier avant transmission comme non-conformité  
**Référentiel** : RGAA 4.1.2  
**Sévérité** : Majeur  
**Justification de sévérité** : Les formats, limites ou consignes attendus ne sont pas associés au champ pour une personne utilisant un lecteur d’écran.  
**Date** : 2026-09-04  
**Composant / gabarit** : Champ de téléversement  
**Portée** : Locale — P06  
**Pages affectées** : P06  
**Constats sources regroupés** : 1

> Ces conclusions proviennent d’une préqualification instrumentée. Elles ne constituent ni un taux RGAA officiel ni une validation après correction.

> **Alerte méthodologique :** La relation orpheline est un défaut technique observable, mais le test 7.1.1 exige de démontrer que l’information est nécessaire au composant. Requalifier après contrôle du texte d’aide visible et, si nécessaire, du test 11.10.5 relatif aux indications de format.

---

## Pages et rapports sources

| Page | Nom | URL | Rapport RGAA |
|---|---|---|---|
| P06 | Formulaire Écrivez-nous | https://moa.douane.gouv.fr/formulaire-infos-douane-service | [P06-RGAA.html](../../RGAA/P06-RGAA.html) |

## Références RGAA

- **Critère 7.1** — Chaque script est-il, si nécessaire, compatible avec les technologies d’assistance ?
- **Test 7.1.1** — Chaque script qui génère ou contrôle un composant d’interface vérifie-t-il, si nécessaire, une de ces conditions ? Le nom, le rôle, la valeur, le paramétrage et les changements d’états sont accessibles aux technologies d’assistance via une API d’accessibilité ; Un composant d’interface accessible permettant d’accéder aux mêmes fonctionnalités est présent dans la page ; Une alternative accessible permet d’accéder aux mêmes fonctionnalités.

---

## Code source constaté

### Référence absente : edit-document--description

```html
<input accept=".jpg,.jpeg,.png,.pdf" data-drupal-selector="edit-document-upload" multiple="multiple" class="fr-upload js-form-file form-file fr-mt-3v" type="file" id="edit-document-upload" name="files[Document][]" size="22" aria-describedby="edit-document--description" data-once="fileValidate auto-file-upload">
```

## Inventaire des constats sources

| Page | Identifiant source | Critère / test | Sélecteur | Observation | Provenance | Preuve principale |
|---|---|---|---|---|---|---|
| P06 | `P06-RGAA-7-1-ARIA-REFERENCE-002-003` | 7.1 / 7.1.1 | `#edit-document-upload` | aria-describedby référence #edit-document--description absent | RENDERED_DOM | `rgaa/preuves/P06/attempt-004/raw-dom.json` |

---

## Analyse du défaut

Sur P06, le champ de téléversement cite `edit-document--description` dans `aria-describedby`, mais aucun élément ne porte cet identifiant. Cette cause est propre au composant de téléversement et nécessite un correctif distinct du bandeau de cookies.

## Impact utilisateur

Les formats, limites ou consignes attendus ne sont pas associés au champ pour une personne utilisant un lecteur d’écran.

---

## Recommandations

### Solution 1 — Créer le texte d’aide référencé (recommandée)

Ajouter un texte d’aide utile avec l’identifiant exact généré par le champ.

```html
<label class="fr-label" for="edit-document-upload">Document</label>
<input id="edit-document-upload" type="file"
       aria-describedby="edit-document--description">
<p id="edit-document--description" class="fr-hint-text">
  Formats acceptés : JPG, PNG ou PDF.
</p>
```

### Solution 2 — Référencer le texte d’aide déjà présent

Si une aide existe sous un autre identifiant, corriger la valeur de `aria-describedby` au lieu de dupliquer le texte.

```html
<input id="edit-document-upload" type="file"
       aria-describedby="document-formats-aide">
<p id="document-formats-aide" class="fr-hint-text">Formats acceptés…</p>
```

## Comparaison avec le composant DSFR

**Composant concerné** : Champ de téléversement

| Point contrôlé | DSFR / comportement attendu | Site audité |
|---|---|---|
| Relation de description | IDREF vers une aide existante | edit-document--description absent |
| Consignes | Reliées au champ | Aide non restituable |
| Cause attribuée | Composant paramétrable | Génération du champ Drupal |

Le constat est attribué à l’intégration observée. La présence de classes `fr-*` ne suffit pas à attribuer le défaut au DSFR natif.

---

## Vérification après correction

- [ ] Contrôler que chaque identifiant cité par le champ existe et reste unique.
- [ ] Inspecter la description accessible calculée pour `#edit-document-upload`.
- [ ] Tester le champ avec un lecteur d’écran et vérifier que l’aide est annoncée une seule fois.

La correction ne doit être considérée comme clôturée qu’après production d’une nouvelle preuve et recontrôle humain.

## Références

- [RGAA 4.1.2 — test 7.1.1](https://accessibilite.numerique.gouv.fr/methode/criteres-et-tests/#7.1.1)
- [DSFR 1.15.2 — composant upload](https://github.com/GouvernementFR/dsfr/tree/v1.15.2/src/dsfr/component/upload)
- Source factuelle : rapports HTML RGAA livrés pour les pages indiquées et constats `NC_CONFIRMEE` correspondants.
