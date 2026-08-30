# RGAA 4.1.2 - Thématique 6 - Liens

**Statut** : référence partagée opérationnelle. **Source locale obligatoire** : `references/rgaa/normalized/rgaa-4.1.2.json` et `references/rgaa/checklists/rgaa-4.1.2-checklists.json`. **Limite** : ce fichier organise les preuves et les reprises possibles ; il ne produit pas un verdict RGAA final sans exécution et validation humaine lorsque le test l’exige.

Couverture locale : 2 critères et 6 tests RGAA. Décision opérationnelle : Calculer nom accessible, source du nom, texte visible et destination ; évaluer l’explicitation en contexte humainement.

Priorité d’intégration : P1 - extension de `accessible-name-probe` vers liens et zones.

## Sources locales et skills

| Code | Source locale | Usage attendu |
|---|---|---|
| `PAR` | `pre-audit-rgaa-dsfr` | Orchestration de préaudit, tri NC/RECO/NOTE, preuves DOM, DSFR et validation humaine. |
| `ARD` | `audit-rgaa-dsfr` | Périmètre RGAA complet, statuts C/NC/NA/NT et livrables réglementaires. |
| `AAW` | `audit-accessibilite-web` | Scan axe/WCAG, mapping RGAA et signaux techniques non suffisants seuls. |
| `SHR` | `a11y-shared-references` | Contrats communs de preuve, patterns axe et sondes de nom accessible. |
| `ALT` | `alt-text` | Jugement sur rôle, alternative, image-lien, CAPTCHA, image texte ou image complexe. |
| `OPQ` | `opquast` | Appui qualité web et priorisation ; non normatif RGAA. |

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
| `TPG` | ThePacielloGroup bookmarklets | Favelets | Licence non déclarée | Inspiration UX uniquement ; aucune copie directe. |

## Critères couverts

| Critère | Intitulé RGAA local | Tests tracés |
|---|---|---|
| `6.1` | Chaque lien est-il explicite (hors cas particuliers) ? | `6.1.1`, `6.1.2`, `6.1.3`, `6.1.4`, `6.1.5` |
| `6.2` | Dans chaque page web, chaque lien a-t-il un intitulé ? | `6.2.1` |

## Table opérationnelle par test

Abréviations de statut : `automatisable` = condition technique directement testable ; `préqualification` = signal fort mais verdict incomplet ; `revue humaine requise` = preuve exploitable à arbitrer ; `manuel` = parcours, contenu ou expertise indispensable.

| Test | Critère | Intention du test | Cible DOM ou artefact | Preuve observable attendue | Sources locales utiles | Sources externes utiles | Reprise possible | Statut | Limite connue | Question de validation humaine |
|---|---|---|---|---|---|---|---|---|---|---|
| `6.1.1` | `6.1` | Chaque lien texte vérifie-t-il une de ces conditions (hors cas particuliers) ? | `a[href] sans enfant de type image`, `[role="link"] sans enfant de type image et dont la navigation est prise en charge par scr…`, `lien texte au sens du glossaire RGAA` | `link_count`, `link_nodes`, `link_type`, `visible_text`, `accessible_name`, `accessible_name_source` (+24) | PAR, ARD, AAW, SHR, ALT, OPQ | RGAA, AXE, ACT, AR, RC, HTMLCS, IBM, TPG | checklist, UX, inspiration, fixture MPL isolée, probe nom accessible | manuel | Aucun verdict fiable sans contenu, parcours ou expertise métier réelle. | Confirmer si l'intitulé du lien seul permet de comprendre la fonction et la destination. |
| `6.1.2` | `6.1` | Chaque lien image vérifie-t-il une de ces conditions (hors cas particuliers) ? | `a[href] contenant uniquement un ou plusieurs enfants de type image`, `[role="link"] contenant uniquement un ou plusieurs enfants de type image`, `area[href]`, `lien image au sens du glossaire RGAA` | `link_count`, `link_nodes`, `link_type`, `visible_text`, `accessible_name`, `accessible_name_source` (+25) | PAR, ARD, AAW, SHR, ALT, OPQ | RGAA, AXE, ACT, AR, RC, HTMLCS, IBM, TPG | checklist, UX, inspiration, fixture MPL isolée, probe nom accessible | manuel | Aucun verdict fiable sans contenu, parcours ou expertise métier réelle. | Confirmer si l'intitulé du lien seul permet de comprendre la fonction et la destination. |
| `6.1.3` | `6.1` | Chaque lien composite vérifie-t-il une de ces conditions (hors cas particuliers) ? | `a[href] contenant à la fois du texte et au moins un enfant de type image`, `[role="link"] contenant à la fois du texte et au moins un enfant de type image`, `lien composite au sens du glossaire RGAA` | `link_count`, `link_nodes`, `link_type`, `visible_text`, `accessible_name`, `accessible_name_source` (+25) | PAR, ARD, AAW, SHR, ALT, OPQ | RGAA, AXE, ACT, AR, RC, HTMLCS, IBM, TPG | checklist, UX, inspiration, fixture MPL isolée, probe nom accessible | manuel | Aucun verdict fiable sans contenu, parcours ou expertise métier réelle. | Confirmer si l'intitulé du lien seul permet de comprendre la fonction et la destination. |
| `6.1.4` | `6.1` | Chaque lien SVG vérifie-t-il une de ces conditions (hors cas particuliers) ? | `svg a[href]`, `svg a[xlink:href]`, `lien SVG au sens du glossaire RGAA` | `link_count`, `link_nodes`, `link_type`, `visible_text`, `accessible_name`, `accessible_name_source` (+27) | PAR, ARD, AAW, SHR, ALT, OPQ | RGAA, AXE, ACT, AR, RC, HTMLCS, IBM, TPG | checklist, UX, inspiration, fixture MPL isolée, probe nom accessible | manuel | Aucun verdict fiable sans contenu, parcours ou expertise métier réelle. | Confirmer si l'intitulé du lien seul permet de comprendre la fonction et la destination. |
| `6.1.5` | `6.1` | Pour chaque lien ayant un intitulé visible, le nom accessible du lien contient-il au moins l’intitulé visible (hor… | `lien non SVG ayant un intitulé visible et un nom accessible fourni ou complété par title,…`, `lien SVG ayant un intitulé visible et un nom accessible fourni par aria-labelledby, aria-…` | `link_count`, `link_nodes`, `link_type`, `visible_text`, `accessible_name`, `accessible_name_source` (+28) | PAR, ARD, AAW, SHR, ALT, OPQ | RGAA, AXE, ACT, AR, RC, HTMLCS, IBM, TPG | checklist, UX, inspiration, fixture MPL isolée, probe nom accessible | manuel | Aucun verdict fiable sans contenu, parcours ou expertise métier réelle. | Confirmer les cas particuliers où la ponctuation ou les majuscules peuvent être ignorées. |
| `6.2.1` | `6.2` | Dans chaque page web, chaque lien a-t-il un intitulé entre `<a>` et `</a>` ? | `a[href]`, `[role="link"] dont l'action de navigation est prise en charge par script`, `svg a[xlink:href]`, `svg a[href] comme compatibilité à signaler avec le support SVG moderne` (+1) | `link_count`, `link_nodes`, `link_selector`, `html_anchor_href_candidate`, `aria_role_link_candidate`, `scripted_navigation_candidate` (+27) | PAR, ARD, AAW, SHR, ALT, OPQ | RGAA, AXE, ACT, AR, RC, HTMLCS, IBM, TPG | sélecteur, heuristique, checklist, fixture MPL isolée, probe nom accessible | préqualification | Signal exploitable, verdict RGAA incomplet sans contexte et revue humaine. | Vérifier que l'inventaire n'a pas compté comme liens les ancres sans href ou sans rôle="link". |

## Garde-fous de réemploi

- Les codes de sources externes renvoient au tableau de licences ci-dessus ; toute copie de fixture ou de helper `AR` doit rester isolée avec notice MPL-2.0.
- Les sources `CARN`, `COP`, `TEM` ou `TPG` ne doivent pas être copiées dans les modules propres sans isolation ou validation juridique ; reprendre seulement les comportements observables et les idées de preuve.
- Les lignes `préqualification` et `revue humaine requise` doivent toujours conserver la preuve brute, la limite et la question humaine dans le résultat du skill consommateur.
- `pre-audit-rgaa-dsfr` peut consommer cette référence pour orienter les preuves, mais `audit-rgaa-dsfr` reste nécessaire pour un audit complet et un taux de conformité.
