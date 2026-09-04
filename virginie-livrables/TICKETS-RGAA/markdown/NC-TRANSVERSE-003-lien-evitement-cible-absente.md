# NC-TRANSVERSE-003 — Lien d’évitement vers une cible absente

**Statut** : Préqualification — NC confirmée dans les rapports sources  
**Référentiel** : RGAA 4.1.2  
**Sévérité** : Bloquant  
**Justification de sévérité** : Les personnes naviguant au clavier ne peuvent pas éviter l’en-tête et doivent parcourir tous ses contrôles avant d’atteindre le contenu principal.  
**Date** : 2026-09-04  
**Composant / gabarit** : Liens d’évitement  
**Portée** : Transverse — P07, P08  
**Pages affectées** : P07, P08  
**Constats sources regroupés** : 3

> Ces conclusions proviennent d’une préqualification instrumentée. Elles ne constituent ni un taux RGAA officiel ni une validation après correction.

---

## Pages et rapports sources

| Page | Nom | URL | Rapport RGAA |
|---|---|---|---|
| P07 | Voyages à l’étranger | https://moa.douane.gouv.fr/particuliers/voyages-letranger | [P07-RGAA.html](../../RGAA/P07-RGAA.html) |
| P08 | Commerce international | https://moa.douane.gouv.fr/professionnels/commerce-international | [P08-RGAA.html](../../RGAA/P08-RGAA.html) |

## Références RGAA

- **Critère 12.7** — Dans chaque page web, un lien d’évitement ou d’accès rapide à la zone de contenu principal est-il présent (hors cas particuliers) ?
- **Test 12.7.1** — Dans chaque page web, un lien permet-il d’éviter la zone de contenu principal ou d’y accéder (hors cas particuliers) ?
- **Test 12.7.2** — Dans chaque ensemble de pages, le lien d’évitement ou d’accès rapide à la zone de contenu principal vérifie-t-il ces conditions (hors cas particuliers) ? Le lien est situé à la même place dans la présentation ; Le lien se présente toujours dans le même ordre relatif dans le code source ; Le lien est visible ou, à défaut, visible à la prise de focus ; Le lien est fonctionnel.

---

## Code source constaté

### P07/P08 — lien sans cible correspondante

```html
<a class="fr-link" href="#content">Contenu</a>
```

## Inventaire des constats sources

| Page | Identifiant source | Critère / test | Sélecteur | Observation | Provenance | Preuve principale |
|---|---|---|---|---|---|---|
| P07 | `P07-RGAA-12-7-SKIPLINK-001-015` | 12.7 / 12.7.1 | `body.eu-cookie-compliance-popup-open.eu-cookie-compliance-status-null > div.fr-skiplinks:nth-of-type(2) > nav.fr-container > ul.fr-skiplinks__list > li:nth-of-type(1) > a.fr-link` | #content ne cible aucun élément | RENDERED_DOM | `rgaa/preuves/P07/attempt-002/raw-dom.json` |
| P08 | `P08-RGAA-12-7-SKIPLINK-001-015` | 12.7 / 12.7.1 | `body.eu-cookie-compliance-popup-open.eu-cookie-compliance-status-null > div.fr-skiplinks:nth-of-type(2) > nav.fr-container > ul.fr-skiplinks__list > li:nth-of-type(1) > a.fr-link` | #content ne cible aucun élément | RENDERED_DOM | `rgaa/preuves/P08/attempt-001/raw-dom.json` |
| P08 | `RGAA-P08-Q-008` | 12.7 / 12.7.2 | `Mesure documentée` | Le lien d’accès rapide au contenu n’est pas fonctionnel puisque sa destination #content est absente. | MEASUREMENTS | `rgaa/preuves/P08/attempt-001/evidence.json` |

---

## Analyse du défaut

Sur P07 et P08, le premier lien d’accès rapide pointe vers `#content`, alors qu’aucun élément ne porte cet identifiant. L’activation ne rejoint donc pas la zone de contenu principal. Sur P08, la revue du test 12.7.2 confirme aussi que le mécanisme répété n’est pas fonctionnel. Les deux tests relèvent de la même cause racine et sont réunis dans un seul ticket.

## Impact utilisateur

Les personnes naviguant au clavier ne peuvent pas éviter l’en-tête et doivent parcourir tous ses contrôles avant d’atteindre le contenu principal.

---

## Recommandations

### Solution 1 — Créer la cible sur la zone principale (recommandée)

Conserver la destination `#content` et appliquer cet identifiant à l’unique élément `main` visible. Si le navigateur ne déplace pas le focus de façon fiable, prévoir un repositionnement contrôlé et testé.

```html
<div class="fr-skiplinks">
  <nav class="fr-container" aria-label="Accès rapide">
    <ul class="fr-skiplinks__list">
      <li><a class="fr-link" href="#content">Contenu</a></li>
    </ul>
  </nav>
</div>

<main id="content">
  <!-- contenu principal -->
</main>
```

### Solution 2 — Corriger la destination existante

Si le contenu principal possède déjà un autre identifiant stable, modifier le `href` du lien pour viser exactement cette cible.

```html
<a class="fr-link" href="#contenu-principal">Contenu</a>
<main id="contenu-principal">…</main>
```

## Comparaison avec le composant DSFR

**Composant concerné** : Liens d’évitement

| Point contrôlé | DSFR / comportement attendu | Site audité |
|---|---|---|
| Lien | Destination correspondant à une cible réelle | href=#content sans cible |
| Fonctionnement | Accès direct au contenu principal | Activation sans déplacement utile |
| Cause attribuée | Composant DSFR paramétrable | Intégration / identifiant de cible |

Le constat est attribué à l’intégration observée. La présence de classes `fr-*` ne suffit pas à attribuer le défaut au DSFR natif.

---

## Vérification après correction

- [ ] Depuis le haut de P07 et P08, afficher le lien avec Tab puis l’activer avec Entrée.
- [ ] Vérifier que l’URL reçoit l’ancre attendue et que la lecture reprend au contenu principal.
- [ ] Contrôler sa position, son ordre et sa visibilité au focus sur les deux pages.

La correction ne doit être considérée comme clôturée qu’après production d’une nouvelle preuve et recontrôle humain.

## Références

- [RGAA 4.1.2 — test 12.7.1](https://accessibilite.numerique.gouv.fr/methode/criteres-et-tests/#12.7.1)
- [RGAA 4.1.2 — test 12.7.2](https://accessibilite.numerique.gouv.fr/methode/criteres-et-tests/#12.7.2)
- [DSFR 1.15.2 — composant skiplink](https://github.com/GouvernementFR/dsfr/tree/v1.15.2/src/dsfr/component/skiplink)
- Source factuelle : rapports HTML RGAA livrés pour les pages indiquées et constats `NC_CONFIRMEE` correspondants.
