# NC-TRANSVERSE-008 — Valeur type=link invalide sur un lien

**Statut** : Préqualification — NC confirmée dans les rapports sources  
**Référentiel** : RGAA 4.1.2  
**Sévérité** : Majeur  
**Justification de sévérité** : Le code source généré n’est pas valide. Cette erreur réduit la robustesse d’interprétation et peut perturber des outils qui exploitent le type déclaré de la ressource.  
**Date** : 2026-09-04  
**Composant / gabarit** : Navigation  
**Portée** : Transverse — P05, P06, P07, P08, P09  
**Pages affectées** : P05, P06, P07, P08, P09  
**Constats sources regroupés** : 5

> Ces conclusions proviennent d’une préqualification instrumentée. Elles ne constituent ni un taux RGAA officiel ni une validation après correction.

---

## Pages et rapports sources

| Page | Nom | URL | Rapport RGAA |
|---|---|---|---|
| P05 | Données personnelles | https://moa.douane.gouv.fr/pied-de-page/donnees-personnelles | [P05-RGAA.html](../../RGAA/P05-RGAA.html) |
| P06 | Formulaire Écrivez-nous | https://moa.douane.gouv.fr/formulaire-infos-douane-service | [P06-RGAA.html](../../RGAA/P06-RGAA.html) |
| P07 | Voyages à l’étranger | https://moa.douane.gouv.fr/particuliers/voyages-letranger | [P07-RGAA.html](../../RGAA/P07-RGAA.html) |
| P08 | Commerce international | https://moa.douane.gouv.fr/professionnels/commerce-international | [P08-RGAA.html](../../RGAA/P08-RGAA.html) |
| P09 | Actualité DELTA IE | https://moa.douane.gouv.fr/actualites/point-dactualite-sur-le-deploiement-de-delta-ie-import-et-export-au-5-fevrier-2026 | [P09-RGAA.html](../../RGAA/P09-RGAA.html) |

## Références RGAA

- **Critère 8.2** — Pour chaque page web, le code source généré est-il valide selon le type de document spécifié ?
- **Test 8.2.1** — Pour chaque déclaration de type de document, le code source généré de la page vérifie-t-il ces conditions ? Les balises, attributs et valeurs d’attributs respectent les règles d’écriture ; L’imbrication des balises est conforme ; L’ouverture et la fermeture des balises sont conformes ; Les valeurs d’attribut id sont uniques dans la page ; Les attributs ne sont pas doublés sur un même élément.

---

## Code source constaté

### Lien de navigation observé

```html
<a id="menu-nous-rejoindre" type="link" href="/devenir-douanier" class="fr-nav__link">Nous rejoindre</a>
```

## Inventaire des constats sources

| Page | Identifiant source | Critère / test | Sélecteur | Observation | Provenance | Preuve principale |
|---|---|---|---|---|---|---|
| P05 | `P05-RGAA-8-2-ANCHOR-TYPE-002-005` | 8.2 / 8.2.1 | `#menu-nous-rejoindre` | type='link' n’est pas un type MIME valide sur a | RENDERED_DOM | `rgaa/preuves/P05/attempt-002/raw-dom.json` |
| P06 | `P06-RGAA-8-2-ANCHOR-TYPE-002-007` | 8.2 / 8.2.1 | `#menu-nous-rejoindre` | type='link' n’est pas un type MIME valide sur a | RENDERED_DOM | `rgaa/preuves/P06/attempt-004/raw-dom.json` |
| P07 | `P07-RGAA-8-2-ANCHOR-TYPE-002-005` | 8.2 / 8.2.1 | `#menu-nous-rejoindre` | type='link' n’est pas un type MIME valide sur a | RENDERED_DOM | `rgaa/preuves/P07/attempt-002/raw-dom.json` |
| P08 | `P08-RGAA-8-2-ANCHOR-TYPE-002-005` | 8.2 / 8.2.1 | `#menu-nous-rejoindre` | type='link' n’est pas un type MIME valide sur a | RENDERED_DOM | `rgaa/preuves/P08/attempt-001/raw-dom.json` |
| P09 | `P09-RGAA-8-2-ANCHOR-TYPE-002-006` | 8.2 / 8.2.1 | `#menu-nous-rejoindre` | type='link' n’est pas un type MIME valide sur a | RENDERED_DOM | `rgaa/preuves/P09/attempt-001/raw-dom.json` |

---

## Analyse du défaut

Le lien « Nous rejoindre » porte `type="link"` sur P05 à P09. Pour un élément `a`, l’attribut `type` décrit le type MIME de la ressource cible ; la valeur `link` n’est pas un type MIME. L’attribut est inutile pour donner le rôle de lien, déjà fourni par la balise et son `href`.

## Impact utilisateur

Le code source généré n’est pas valide. Cette erreur réduit la robustesse d’interprétation et peut perturber des outils qui exploitent le type déclaré de la ressource.

---

## Recommandations

### Solution 1 — Supprimer l’attribut type (recommandée)

La ressource étant une page HTML ordinaire, supprimer l’attribut ajouté par le template de navigation.

```html
<a id="menu-nous-rejoindre"
   href="/devenir-douanier"
   class="fr-nav__link">
  Nous rejoindre
</a>
```

### Solution 2 — Déclarer un type MIME réel uniquement si nécessaire

Si la cible possède un type utile et connu, employer une valeur MIME valide telle que `application/pdf`.

```html
<a href="/document.pdf" type="application/pdf">Télécharger le document</a>
```

## Comparaison avec le composant DSFR

**Composant concerné** : Navigation

| Point contrôlé | DSFR / comportement attendu | Site audité |
|---|---|---|
| Rôle du lien | Fourni par a[href] | Attribut type=link ajouté |
| Attribut type | Absent ou type MIME valide | Valeur non MIME |
| Cause attribuée | Lien HTML standard | Template de navigation intégré |

Le constat est attribué à l’intégration observée. La présence de classes `fr-*` ne suffit pas à attribuer le défaut au DSFR natif.

---

## Vérification après correction

- [ ] Rechercher `a[type]` dans le DOM rendu de P05 à P09.
- [ ] Supprimer `type="link"` et valider le code HTML généré.
- [ ] Vérifier que le lien « Nous rejoindre » conserve son fonctionnement.

La correction ne doit être considérée comme clôturée qu’après production d’une nouvelle preuve et recontrôle humain.

## Références

- [RGAA 4.1.2 — test 8.2.1](https://accessibilite.numerique.gouv.fr/methode/criteres-et-tests/#8.2.1)
- [DSFR 1.15.2 — composant navigation](https://github.com/GouvernementFR/dsfr/tree/v1.15.2/src/dsfr/component/navigation)
- Source factuelle : rapports HTML RGAA livrés pour les pages indiquées et constats `NC_CONFIRMEE` correspondants.
