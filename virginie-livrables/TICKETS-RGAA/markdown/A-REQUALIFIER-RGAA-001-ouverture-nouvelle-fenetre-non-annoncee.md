# A-REQUALIFIER-RGAA-001 — Ouvertures de liens dans une nouvelle fenêtre à requalifier

**Statut** : À requalifier avant transmission comme non-conformité  
**Référentiel** : RGAA 4.1.2  
**Sévérité** : Majeur  
**Justification de sévérité** : Une nouvelle fenêtre non annoncée peut surprendre certaines personnes. Cet impact justifie une amélioration, mais ne suffit pas à établir l’échec du test 13.2.1 décrit dans la méthode officielle.  
**Date** : 2026-09-04  
**Composant / gabarit** : Liens externes / suivi sur les réseaux sociaux  
**Portée** : Transverse — P02, P03, P04, P05, P06  
**Pages affectées** : P02, P03, P04, P05, P06  
**Constats sources regroupés** : 5

> Ces conclusions proviennent d’une préqualification instrumentée. Elles ne constituent ni un taux RGAA officiel ni une validation après correction.

> **Alerte méthodologique :** Ne pas transmettre ce fichier comme non-conformité RGAA 13.2.1 sans arbitrage d’un auditeur. La méthode officielle locale consultée valide le test lorsqu’aucune fenêtre ne s’ouvre au chargement.

---

## Pages et rapports sources

| Page | Nom | URL | Rapport RGAA |
|---|---|---|---|
| P02 | Plan du site | https://moa.douane.gouv.fr/plan-du-site | [P02-RGAA.html](../../RGAA/P02-RGAA.html) |
| P03 | Déclaration d’accessibilité | https://moa.douane.gouv.fr/pied-de-page/declaration-daccessibilite-du-portail-dounegouvfr | [P03-RGAA.html](../../RGAA/P03-RGAA.html) |
| P04 | Mentions légales | https://moa.douane.gouv.fr/mentions-legales | [P04-RGAA.html](../../RGAA/P04-RGAA.html) |
| P05 | Données personnelles | https://moa.douane.gouv.fr/pied-de-page/donnees-personnelles | [P05-RGAA.html](../../RGAA/P05-RGAA.html) |
| P06 | Formulaire Écrivez-nous | https://moa.douane.gouv.fr/formulaire-infos-douane-service | [P06-RGAA.html](../../RGAA/P06-RGAA.html) |

## Références RGAA

- **Critère 13.2** — Dans chaque page web, l’ouverture d’une nouvelle fenêtre ne doit pas être déclenchée sans action de l’utilisateur. Cette règle est-elle respectée ?
- **Test 13.2.1** — Dans chaque page web, l’ouverture d’une nouvelle fenêtre ne doit pas être déclenchée sans action de l’utilisateur. Cette règle est-elle respectée ?

---

## Code source constaté

### P02 — exemple de lien mesuré

```html
<a title="Suivez-nous sur Facebook" id="rs-facebook" href="https://www.facebook.com/douanefrancaise/" target="_blank" rel="noopener external" class="fr-btn--facebook fr-btn">Facebook</a>
```

## Inventaire des constats sources

| Page | Identifiant source | Critère / test | Sélecteur | Observation | Provenance | Preuve principale |
|---|---|---|---|---|---|---|
| P02 | `RGAA-P02-Q-007` | 13.2 / 13.2.1 | `Mesure documentée` | Six liens vers les réseaux sociaux utilisent target=_blank sans annoncer la nouvelle fenêtre dans leur nom accessible. Cinq autres liens target=_blank l’annoncent correctement dans title. | MEASUREMENTS | `dsfr/preuves/P02/attempt-004/evidence.json` |
| P03 | `RGAA-P03-Q-007` | 13.2 / 13.2.1 | `Mesure documentée` | Onze liens target=_blank, dont six liens sociaux et cinq liens de contenu, ouvrent une nouvelle fenêtre sans l’annoncer dans leur nom accessible. Les huit autres occurrences l’annoncent correctement. | MEASUREMENTS | `dsfr/preuves/P03/attempt-004/evidence.json` |
| P04 | `RGAA-P04-Q-007` | 13.2 / 13.2.1 | `Mesure documentée` | Douze liens target=_blank, dont six liens sociaux et six liens de contenu, ouvrent une nouvelle fenêtre sans l’annoncer dans leur nom accessible. Les six autres occurrences l’annoncent correctement. | MEASUREMENTS | `dsfr/preuves/P04/attempt-002/evidence.json` |
| P05 | `RGAA-P05-Q-007` | 13.2 / 13.2.1 | `Mesure documentée` | Quinze liens target=_blank, dont six liens sociaux et neuf liens de contenu, ouvrent une nouvelle fenêtre sans l’annoncer dans leur nom accessible. Les six autres occurrences l’annoncent correctement. | MEASUREMENTS | `dsfr/preuves/P05/attempt-002/evidence.json` |
| P06 | `RGAA-P06-Q-011` | 13.2 / 13.2.1 | `Mesure documentée` | Huit liens target=_blank, dont six liens sociaux et deux liens d’information sur le coronavirus, ouvrent une nouvelle fenêtre sans l’annoncer. Les six liens institutionnels restants l’annoncent correctement. | MEASUREMENTS | `dsfr/preuves/P06/attempt-008/evidence.json` |

---

## Analyse du défaut

Les rapports sources classent sous le test 13.2.1 des liens `target="_blank"` dont le nom accessible n’annonce pas la nouvelle fenêtre. Cette recommandation est utile, mais le test RGAA 13.2.1 vérifie l’absence d’ouverture automatique au chargement, sans action de l’utilisateur. L’activation d’un lien constitue une action. Si aucune fenêtre ne s’ouvre automatiquement, le mapping en non-conformité 13.2.1 doit être retiré ou remplacé par une recommandation.

## Impact utilisateur

Une nouvelle fenêtre non annoncée peut surprendre certaines personnes. Cet impact justifie une amélioration, mais ne suffit pas à établir l’échec du test 13.2.1 décrit dans la méthode officielle.

---

## Recommandations

### Solution 1 — Éviter l’ouverture forcée (recommandée)

Supprimer `target="_blank"` lorsque l’ouverture dans un nouvel onglet n’est pas indispensable.

```html
<a href="https://www.facebook.com/douanefrancaise/"
   rel="external" class="fr-btn--facebook fr-btn">
  Facebook
</a>
```

### Solution 2 — Annoncer le changement de contexte si target=_blank est conservé

Ajouter une mention perceptible dans le nom du lien et conserver `rel="noopener"`.

```html
<a href="https://www.facebook.com/douanefrancaise/"
   target="_blank" rel="noopener external"
   class="fr-btn--facebook fr-btn">
  Facebook <span class="fr-sr-only">— nouvelle fenêtre</span>
</a>
```

## Comparaison avec le composant DSFR

**Composant concerné** : Liens externes / suivi sur les réseaux sociaux

| Point contrôlé | DSFR / comportement attendu | Site audité |
|---|---|---|
| Ouverture | Même fenêtre par défaut | target=_blank |
| Information | Changement de contexte explicite s’il est imposé | Mention absente selon la mesure |
| Qualification RGAA | 13.2.1 vise l’ouverture automatique | Mapping source à revalider |

Le constat est attribué à l’intégration observée. La présence de classes `fr-*` ne suffit pas à attribuer le défaut au DSFR natif.

---

## Vérification après correction

- [ ] Recharger chaque page sans action et vérifier qu’aucune nouvelle fenêtre ne s’ouvre.
- [ ] Si aucune ouverture automatique n’existe, reclasser ces constats en recommandation hors NC 13.2.1.
- [ ] Si `target=_blank` est maintenu, vérifier que le changement de contexte est annoncé de façon cohérente.

La correction ne doit être considérée comme clôturée qu’après production d’une nouvelle preuve et recontrôle humain.

## Références

- [RGAA 4.1.2 — test 13.2.1](https://accessibilite.numerique.gouv.fr/methode/criteres-et-tests/#13.2.1)
- [DSFR 1.15.2 — composant follow](https://github.com/GouvernementFR/dsfr/tree/v1.15.2/src/dsfr/component/follow)
- Source factuelle : rapports HTML RGAA livrés pour les pages indiquées et constats `NC_CONFIRMEE` correspondants.
