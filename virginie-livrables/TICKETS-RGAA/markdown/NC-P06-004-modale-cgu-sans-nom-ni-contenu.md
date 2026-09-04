# NC-P06-004 — Modale CGU sans nom accessible ni contenu utile

**Statut** : Préqualification — NC confirmée dans les rapports sources  
**Référentiel** : RGAA 4.1.2  
**Sévérité** : Bloquant  
**Justification de sévérité** : À l’ouverture, une personne utilisant un lecteur d’écran peut entendre seulement « dialogue » sans identifier les conditions générales ni accéder à leur contenu.  
**Date** : 2026-09-04  
**Composant / gabarit** : Modale CGU  
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

- **Critère 7.1** — Chaque script est-il, si nécessaire, compatible avec les technologies d’assistance ?
- **Test 7.1.1** — Chaque script qui génère ou contrôle un composant d’interface vérifie-t-il, si nécessaire, une de ces conditions ? Le nom, le rôle, la valeur, le paramétrage et les changements d’états sont accessibles aux technologies d’assistance via une API d’accessibilité ; Un composant d’interface accessible permettant d’accéder aux mêmes fonctionnalités est présent dans la page ; Une alternative accessible permet d’accéder aux mêmes fonctionnalités.

---

## Code source constaté

### P06 — dialogue observé

```html
<dialog id="cgu-ids-modal" class="fr-modal" aria-labelledby="cgu-ids-modal-title" role="dialog" data-fr-js-modal="true">
          <div class="fr-container fr-container--fluid fr-container-md">
            <div class="fr-grid-row fr-grid-row--center">
              <div class="fr-col-12">
                <div class="fr-modal__body" data-fr-js-modal-body="true">
                  <div class="fr-modal__header">
                    <button aria-controls="cgu-ids-modal" title="Fermer" type="button" class="fr-btn--close fr-btn" data-fr-js-modal-button="true">Fermer</button>
                  </div>
                  <div class="fr-modal__content"></div>
                </div>
              </div>
            </div>
          </div>
        </dialog>
```

## Inventaire des constats sources

| Page | Identifiant source | Critère / test | Sélecteur | Observation | Provenance | Preuve principale |
|---|---|---|---|---|---|---|
| P06 | `P06-RGAA-7-1-DIALOG-NAME-001-001` | 7.1 / 7.1.1 | `#cgu-ids-modal` | aria-labelledby référence #cgu-ids-modal-title absent | RENDERED_DOM | `rgaa/preuves/P06/attempt-004/raw-dom.json` |

---

## Analyse du défaut

La modale CGU cite `cgu-ids-modal-title` dans `aria-labelledby`, mais aucun élément ne porte cet identifiant dans le DOM rendu. Dans l’état observé, le conteneur de contenu est également vide. Le rôle de dialogue est présent, mais son nom programmatique et l’information attendue ne peuvent pas être restitués.

## Impact utilisateur

À l’ouverture, une personne utilisant un lecteur d’écran peut entendre seulement « dialogue » sans identifier les conditions générales ni accéder à leur contenu.

---

## Recommandations

### Solution 1 — Créer le titre et charger le contenu avant l’ouverture (recommandée)

Ajouter un titre pertinent avec l’identifiant exact référencé par `aria-labelledby`. Charger le contenu utile de la modale avant de l’exposer et d’y déplacer le focus.

```html
<dialog id="cgu-ids-modal" class="fr-modal"
        aria-labelledby="cgu-ids-modal-title">
  <div class="fr-modal__body">
    <div class="fr-modal__content">
      <h2 id="cgu-ids-modal-title" class="fr-modal__title">
        Conditions générales d’utilisation
      </h2>
      <!-- contenu utile des CGU -->
    </div>
  </div>
</dialog>
```

## Comparaison avec le composant DSFR

**Composant concerné** : Modale CGU

| Point contrôlé | DSFR / comportement attendu | Site audité |
|---|---|---|
| Nom accessible | Titre présent et relié par aria-labelledby | Identifiant de titre absent |
| Contenu | Contenu disponible à l’ouverture | Conteneur vide dans l’état observé |
| Cause attribuée | Structure DSFR nommée | Chargement / intégration de la modale CGU |

Le constat est attribué à l’intégration observée. La présence de classes `fr-*` ne suffit pas à attribuer le défaut au DSFR natif.

---

## Vérification après correction

- [ ] Ouvrir la modale CGU au clavier.
- [ ] Contrôler que `aria-labelledby` cible un titre existant et unique.
- [ ] Vérifier que le contenu est présent avant le déplacement du focus.
- [ ] Contrôler le nom calculé puis la restitution avec un lecteur d’écran réel.

La correction ne doit être considérée comme clôturée qu’après production d’une nouvelle preuve et recontrôle humain.

## Références

- [RGAA 4.1.2 — test 7.1.1](https://accessibilite.numerique.gouv.fr/methode/criteres-et-tests/#7.1.1)
- [DSFR 1.15.2 — composant modal](https://github.com/GouvernementFR/dsfr/tree/v1.15.2/src/dsfr/component/modal)
- Source factuelle : rapports HTML RGAA livrés pour les pages indiquées et constats `NC_CONFIRMEE` correspondants.
