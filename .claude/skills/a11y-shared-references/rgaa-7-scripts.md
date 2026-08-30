# RGAA 4.1.2 - Thématique 7 - Scripts

**Statut** : référence partagée opérationnelle. **Source locale obligatoire** : `references/rgaa/normalized/rgaa-4.1.2.json` et `references/rgaa/checklists/rgaa-4.1.2-checklists.json`. **Limite** : ce fichier organise les preuves et les reprises possibles ; il ne produit pas un verdict RGAA final sans exécution et validation humaine lorsque le test l’exige.

Couverture locale : 5 critères et 11 tests RGAA. Décision opérationnelle : Combiner règles ARIA, arbre d’accessibilité et scénarios clavier ; ne conclure la compatibilité AT qu’après validation assistée.

Priorité d’intégration : P1 - scénarios interactifs et live regions.

## Sources locales et skills

| Code | Source locale | Usage attendu |
|---|---|---|
| `PAR` | `pre-audit-rgaa-dsfr` | Orchestration de préaudit, tri NC/RECO/NOTE, preuves DOM, DSFR et validation humaine. |
| `ARD` | `audit-rgaa-dsfr` | Périmètre RGAA complet, statuts C/NC/NA/NT et livrables réglementaires. |
| `AAW` | `audit-accessibilite-web` | Scan axe/WCAG, mapping RGAA et signaux techniques non suffisants seuls. |
| `SHR` | `a11y-shared-references` | Contrats communs de preuve, patterns axe et sondes de nom accessible. |
| `TCW` | `tests-conformite-wcag` | Runner Playwright pour reflow, zoom, espacement, focus, orientation, temps et autocomplete. |
| `SRT` | `screen-reader-testing` | Validation lecteur d’écran, arbre d’accessibilité, annonces et restitution réelle. |
| `DSFRC` | `dsfr-components` | Prévention DSFR, modèles de composants et source anti-faux-positif. |

## Sources externes, licences et réemploi

| Code | Source externe | Type | Licence / contrainte | Usage retenu |
|---|---|---|---|---|
| `RGAA` | RGAA officiel | Référentiel normatif | Source publique DINUM | Source des critères/tests ; ne pas extrapoler hors RGAA 4.1.2. |
| `AXE` | axe-core | Moteur automatique | MPL-2.0 | Réutiliser en dépendance ou mapper les résultats ; ne pas copier du code sans notice MPL. |
| `ACT` | ACT Rules W3C | Assertions atomiques | W3C Document License | Réutiliser assertions et fixtures avec citation ; ne vaut pas verdict RGAA complet. |
| `HTMLCS` | HTML_CodeSniffer | Moteur WCAG historique | BSD-3-Clause | Réutiliser heuristiques ciblées, pas empiler un moteur complet en V1. |
| `IBM` | IBMa/equal-access | Moteur et règles | Apache-2.0 | Comparer aux probes internes et reprendre les règles utiles avec attribution. |
| `ARIA` | WAI-ARIA APG | Patterns de widgets | W3C Software and Document License | Réutiliser scénarios clavier/ARIA ; ne pas confondre pattern APG et conformité RGAA. |
| `INT` | Intopia exercise | Corpus pédagogique | MIT | Réutiliser exercices/fixtures comme inspiration ou corpus avec attribution. |
| `AIW` | Accessibility Insights Web | Workflow d’assessment | MIT | Benchmark UX et séparation FastPass/assessment ; pas dépendance nécessaire. |

## Critères couverts

| Critère | Intitulé RGAA local | Tests tracés |
|---|---|---|
| `7.1` | Chaque script est-il, si nécessaire, compatible avec les technologies d’assistance ? | `7.1.1`, `7.1.2`, `7.1.3` |
| `7.2` | Pour chaque script ayant une alternative, cette alternative est-elle pertinente ? | `7.2.1`, `7.2.2` |
| `7.3` | Chaque script est-il contrôlable par le clavier et par tout dispositif de pointage (hors cas particuliers) ? | `7.3.1`, `7.3.2` |
| `7.4` | Pour chaque script qui initie un changement de contexte, l’utilisateur est-il averti ou en a-t-il le contrôle ? | `7.4.1` |
| `7.5` | Dans chaque page web, les messages de statut sont-ils correctement restitués par les technologies d’assistance ? | `7.5.1`, `7.5.2`, `7.5.3` |

## Table opérationnelle par test

Abréviations de statut : `automatisable` = condition technique directement testable ; `préqualification` = signal fort mais verdict incomplet ; `revue humaine requise` = preuve exploitable à arbitrer ; `manuel` = parcours, contenu ou expertise indispensable.

| Test | Critère | Intention du test | Cible DOM ou artefact | Preuve observable attendue | Sources locales utiles | Sources externes utiles | Reprise possible | Statut | Limite connue | Question de validation humaine |
|---|---|---|---|---|---|---|---|---|---|---|
| `7.1.1` | `7.1` | Chaque script qui génère ou contrôle un composant d’interface vérifie-t-il, si nécessaire, une de ces conditions ? | `composant d'interface généré ou contrôlé par JavaScript`, `menu, menubar, menuitem ou bouton d'ouverture de menu`, `bouton d'accordéon ou bouton de transcription`, `bandeau, panneau ou modale de consentement cookies` (+2) | `script_component_count`, `component_nodes`, `component_type`, `js_controlled_component_candidate`, `native_interactive_element`, `custom_interactive_element` (+41) | PAR, ARD, AAW, SHR, TCW, SRT, DSFRC | RGAA, AXE, ACT, HTMLCS, IBM, ARIA, INT, AIW | checklist, UX, inspiration, scénario Playwright | manuel | Aucun verdict fiable sans contenu, parcours ou expertise métier réelle. | Confirmer que le composant est bien généré ou contrôlé par JavaScript et relève de 7.1. |
| `7.1.2` | `7.1` | Chaque script qui génère ou contrôle un composant d’interface respecte-t-il une de ces conditions ? | `composant d'interface généré ou contrôlé par JavaScript`, `menu, menubar, menuitem ou bouton d'ouverture de menu`, `bouton d'accordéon ou bouton de transcription`, `bandeau, panneau ou modale de consentement cookies` (+4) | `script_component_count`, `component_nodes`, `component_type`, `js_controlled_component_candidate`, `native_interactive_element`, `custom_interactive_element` (+43) | PAR, ARD, AAW, SHR, TCW, SRT, DSFRC | RGAA, AXE, ACT, HTMLCS, IBM, ARIA, INT, AIW | checklist, UX, inspiration, scénario Playwright | manuel | Aucun verdict fiable sans contenu, parcours ou expertise métier réelle. | Confirmer que le composant est bien généré ou contrôlé par JavaScript et relève de 7.1. |
| `7.1.3` | `7.1` | Chaque script qui génère ou contrôle un composant d’interface vérifie-t-il ces conditions (hors cas particuliers) ? | `composant d'interface généré ou contrôlé par JavaScript`, `menu, menubar, menuitem ou bouton d'ouverture de menu`, `bouton d'accordéon ou bouton de transcription`, `bandeau, panneau ou modale de consentement cookies` (+4) | `script_component_count`, `component_nodes`, `component_type`, `js_controlled_component_candidate`, `native_interactive_element`, `custom_interactive_element` (+45) | PAR, ARD, AAW, SHR, TCW, SRT, DSFRC | RGAA, AXE, ACT, HTMLCS, IBM, ARIA, INT, AIW | checklist, UX, inspiration, scénario Playwright | manuel | Aucun verdict fiable sans contenu, parcours ou expertise métier réelle. | Confirmer que le composant est bien généré ou contrôlé par JavaScript et relève de 7.1. |
| `7.2.1` | `7.2` | Chaque script débutant par la balise `<script>` et ayant une alternative vérifie-t-il une de ces conditions ? | `script débutant par une balise script et ayant une alternative` | `test_id`, `source_rgaa_locale`, `target_count`, `target_nodes`, `scope`, `inspectability` (+8) | PAR, ARD, AAW, SHR, TCW, SRT, DSFRC | RGAA, AXE, ACT, HTMLCS, IBM, ARIA, INT, AIW | checklist, UX, inspiration, scénario Playwright | manuel | Aucun verdict fiable sans contenu, parcours ou expertise métier réelle. | Exercer le composant scripté et son alternative candidate. |
| `7.2.2` | `7.2` | Chaque élément non textuel mis à jour par un script (dans la page, ou dans un cadre) et ayant une alternative véri… | `élément non textuel mis à jour par script et ayant une alternative` | `test_id`, `source_rgaa_locale`, `target_count`, `target_nodes`, `scope`, `inspectability` (+8) | PAR, ARD, AAW, SHR, TCW, SRT, DSFRC | RGAA, AXE, ACT, HTMLCS, IBM, ARIA, INT, AIW | checklist, UX, inspiration, scénario Playwright | manuel | Aucun verdict fiable sans contenu, parcours ou expertise métier réelle. | Exercer le composant scripté et son alternative candidate. |
| `7.3.1` | `7.3` | Chaque élément possédant un gestionnaire d’événement contrôlé par un script vérifie-t-il une de ces conditions (ho… | `élément possédant un gestionnaire d'événement contrôlé par un script`, `élément avec gestionnaire inline onclick, onmousedown, onmouseup, onkeydown, onkeyup, onm…`, `élément avec listener JavaScript détectable par instrumentation navigateur`, `élément avec role="button", role="link", role="menuitem", role="tab", role="switch", role…` (+1) | `script_event_handler_count`, `event_handler_nodes`, `dom_selector`, `html_excerpt`, `event_types_detected`, `inline_event_handler_candidate` (+58) | PAR, ARD, AAW, SHR, TCW, SRT, DSFRC | RGAA, AXE, ACT, HTMLCS, IBM, ARIA, INT, AIW | sélecteur, heuristique, checklist, scénario Playwright | préqualification | Signal exploitable, verdict RGAA incomplet sans contexte et revue humaine. | Confirmer que l'élément possède bien un gestionnaire d'événement contrôlé par un script et relève de 7.3. |
| `7.3.2` | `7.3` | Un script ne doit pas supprimer le focus d’un élément qui le reçoit. Cette règle est-elle respectée (hors cas part… | `élément possédant un gestionnaire d'événement contrôlé par un script`, `élément avec gestionnaire inline onclick, onmousedown, onmouseup, onkeydown, onkeyup, onm…`, `élément avec listener JavaScript détectable par instrumentation navigateur`, `élément avec role="button", role="link", role="menuitem", role="tab", role="switch", role…` (+5) | `script_event_handler_count`, `event_handler_nodes`, `dom_selector`, `html_excerpt`, `event_types_detected`, `inline_event_handler_candidate` (+57) | PAR, ARD, AAW, SHR, TCW, SRT, DSFRC | RGAA, AXE, ACT, HTMLCS, IBM, ARIA, INT, AIW | sélecteur, heuristique, checklist, scénario Playwright | préqualification | Signal exploitable, verdict RGAA incomplet sans contexte et revue humaine. | Confirmer que l'élément possède bien un gestionnaire d'événement contrôlé par un script et relève de 7.3. |
| `7.4.1` | `7.4` | Chaque script qui initie un changement de contexte vérifie-t-il une de ces conditions ? | `scripts initiant un changement de contexte` | `test_id`, `source_rgaa_locale`, `target_count`, `target_nodes`, `scope`, `inspectability` (+9) | PAR, ARD, AAW, SHR, TCW, SRT, DSFRC | RGAA, AXE, ACT, HTMLCS, IBM, ARIA, INT, AIW | checklist, heuristique, revue, scénario Playwright | revue humaine requise | Interaction, temporalité ou restitution AT à confirmer sur page réelle. | Déclencher l'interaction réelle avant de statuer. |
| `7.5.1` | `7.5` | Chaque message de statut qui informe de la réussite, du résultat d’une action ou bien de l’état d’une application… | `messages de statut de réussite, résultat d'action ou état d'application` | `test_id`, `source_rgaa_locale`, `target_count`, `target_nodes`, `scope`, `inspectability` (+11) | PAR, ARD, AAW, SHR, TCW, SRT, DSFRC | RGAA, AXE, ACT, HTMLCS, IBM, ARIA, INT, AIW | sélecteur, heuristique, checklist, scénario Playwright | préqualification | Signal exploitable, verdict RGAA incomplet sans contexte et revue humaine. | Déclencher les états : succès, erreur, progression ou changement de résultat. |
| `7.5.2` | `7.5` | Chaque message de statut qui présente une suggestion, ou avertit de l’existence d’une erreur utilise-t-il l’attrib… | `messages de statut présentant une suggestion ou avertissant d'une erreur` | `test_id`, `source_rgaa_locale`, `target_count`, `target_nodes`, `scope`, `inspectability` (+11) | PAR, ARD, AAW, SHR, TCW, SRT, DSFRC | RGAA, AXE, ACT, HTMLCS, IBM, ARIA, INT, AIW | sélecteur, heuristique, checklist, scénario Playwright | préqualification | Signal exploitable, verdict RGAA incomplet sans contexte et revue humaine. | Déclencher les états : succès, erreur, progression ou changement de résultat. |
| `7.5.3` | `7.5` | Chaque message de statut qui indique la progression d’un processus utilise-t-il l’un des attributs WAI-ARIA… | `messages de statut indiquant la progression d'un processus` | `test_id`, `source_rgaa_locale`, `target_count`, `target_nodes`, `scope`, `inspectability` (+14) | PAR, ARD, AAW, SHR, TCW, SRT, DSFRC | RGAA, AXE, ACT, HTMLCS, IBM, ARIA, INT, AIW | sélecteur, heuristique, checklist, scénario Playwright | préqualification | Signal exploitable, verdict RGAA incomplet sans contexte et revue humaine. | Déclencher les états : succès, erreur, progression ou changement de résultat. |

## Garde-fous de réemploi

- Les codes de sources externes renvoient au tableau de licences ci-dessus ; toute copie de fixture ou de helper `AR` doit rester isolée avec notice MPL-2.0.
- Les sources `CARN`, `COP`, `TEM` ou `TPG` ne doivent pas être copiées dans les modules propres sans isolation ou validation juridique ; reprendre seulement les comportements observables et les idées de preuve.
- Les lignes `préqualification` et `revue humaine requise` doivent toujours conserver la preuve brute, la limite et la question humaine dans le résultat du skill consommateur.
- `pre-audit-rgaa-dsfr` peut consommer cette référence pour orienter les preuves, mais `audit-rgaa-dsfr` reste nécessaire pour un audit complet et un taux de conformité.
