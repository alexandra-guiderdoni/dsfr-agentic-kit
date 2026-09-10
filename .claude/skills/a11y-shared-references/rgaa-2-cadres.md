# RGAA 4.1.2 - Thématique 2 - Cadres

**Statut** : référence partagée opérationnelle. **Référentiel embarqué** : `../audit-rgaa-complet/references/rgaa-4.1.2.json`. **Limite** : ce fichier organise les preuves et les reprises possibles ; il ne produit pas un verdict RGAA final sans exécution et validation humaine lorsque le test l’exige.

Couverture locale : 2 critères et 2 tests RGAA. Décision opérationnelle : Automatiser la présence de `title` sur les cadres ; traiter la pertinence du titre comme revue humaine appuyée par `src`, contexte et capture.

Priorité d’intégration : P0 - très rentable pour préaudit et anti-faux-positif iframe.

## Sources locales et skills

| Code | Source locale | Usage attendu |
|---|---|---|
| `PAR` | `pre-audit-rgaa-dsfr` | Orchestration de préaudit, tri NC/RECO/NOTE, preuves DOM, DSFR et validation humaine. |
| `ARD` | `audit-rgaa-creator` | Campagne RGAA multi-pages, orchestration et validation humaine, sans taux automatique. |
| `SHR` | `a11y-shared-references` | Contrats communs de preuve, patterns axe et sondes de nom accessible. |
| `SRT` | `screen-reader-testing` | Validation lecteur d’écran, arbre d’accessibilité, annonces et restitution réelle. |
| `DSFRC` | `dsfr-components` | Prévention DSFR, modèles de composants et source anti-faux-positif. |

## Sources externes, licences et réemploi

| Code | Source externe | Type | Licence / contrainte | Usage retenu |
|---|---|---|---|---|
| `RGAA` | RGAA officiel | Référentiel normatif | Source publique DINUM | Source des critères/tests ; ne pas extrapoler hors RGAA 4.1.2. |
| `AXE` | axe-core | Moteur automatique | MPL-2.0 | Réutiliser en dépendance ou mapper les résultats ; ne pas copier du code sans notice MPL. |
| `ACT` | ACT Rules W3C | Assertions atomiques | W3C Document License | Réutiliser assertions et fixtures avec citation ; ne vaut pas verdict RGAA complet. |
| `AR` | assistant-rgaa | Extension/fixtures RGAA | MPL-2.0 | Copie possible seulement avec notice et isolation MPL ; préférer contrats et fixtures isolées. |
| `RC` | rgaa-checker | Extension RGAA | Apache-2.0 | Réutiliser idées de sélecteurs, statuts et UX ; vérifier la couverture réelle. |
| `HTMLCS` | HTML_CodeSniffer | Moteur WCAG historique | BSD-3-Clause | Réutiliser heuristiques ciblées, pas empiler un moteur complet en V1. |
| `IBM` | IBMa/equal-access | Moteur et règles | Apache-2.0 | Comparer aux probes internes et reprendre les règles utiles avec attribution. |
| `DSFR` | GouvernementFR/dsfr | Design system | MIT + exceptions fontes/marque | Vérifier template et doc accessibilité ; respecter les conditions de marque et de fonte. |

## Critères couverts

| Critère | Intitulé RGAA local | Tests tracés |
|---|---|---|
| `2.1` | Chaque cadre a-t-il un titre de cadre ? | `2.1.1` |
| `2.2` | Pour chaque cadre ayant un titre de cadre, ce titre de cadre est-il pertinent ? | `2.2.1` |

## Table opérationnelle par test

Abréviations de statut : `automatisable` = condition technique directement testable ; `préqualification` = signal fort mais verdict incomplet ; `revue humaine requise` = preuve exploitable à arbitrer ; `manuel` = parcours, contenu ou expertise indispensable.

| Test | Critère | Intention du test | Cible DOM ou artefact | Preuve observable attendue | Sources locales utiles | Sources externes utiles | Reprise possible | Statut | Limite connue | Question de validation humaine |
|---|---|---|---|---|---|---|---|---|---|---|
| `2.1.1` | `2.1` | Chaque cadre (balise `<iframe>` ou `<frame>`) a-t-il un attribut `title` ? | `iframe, frame ou contenu embarqué assimilable à un cadre` | `test_id`, `source_rgaa_locale`, `target_count`, `target_nodes`, `scope`, `inspectability` (+9) | PAR, ARD, SHR, SRT, DSFRC | RGAA, AXE, ACT, AR, RC, HTMLCS, IBM, DSFR | code, sélecteur, fixture, fixture MPL isolée, probe nom accessible | automatisable | Prouve une condition technique, pas les cas particuliers ni la pertinence. | Confirmer que la cible est bien un cadre au sens RGAA. |
| `2.2.1` | `2.2` | Pour chaque cadre (balise `<iframe>` ou `<frame>`) ayant un attribut `title`, le contenu de cet attribut est-il pe… | `cadres ayant un titre de cadre` | `test_id`, `source_rgaa_locale`, `target_count`, `target_nodes`, `scope`, `inspectability` (+9) | PAR, ARD, SHR, SRT, DSFRC | RGAA, AXE, ACT, AR, RC, HTMLCS, IBM, DSFR | checklist, heuristique, revue, fixture MPL isolée, probe nom accessible | revue humaine requise | La preuve brute doit être arbitrée humainement avant décision. | Comparer le titre au contenu réel du cadre, y compris si le contenu est tiers. |

## Garde-fous de réemploi

- Les codes de sources externes renvoient au tableau de licences ci-dessus ; toute copie de fixture ou de helper `AR` doit rester isolée avec notice MPL-2.0.
- Les sources `CARN`, `COP`, `TEM` ou `TPG` ne doivent pas être copiées dans les modules propres sans isolation ou validation juridique ; reprendre seulement les comportements observables et les idées de preuve.
- Les lignes `préqualification` et `revue humaine requise` doivent toujours conserver la preuve brute, la limite et la question humaine dans le résultat du skill consommateur.
- `pre-audit-rgaa-dsfr` peut consommer cette référence pour orienter les preuves, mais `audit-rgaa-creator` reste la voie pour un audit complet et une qualification humaine.
