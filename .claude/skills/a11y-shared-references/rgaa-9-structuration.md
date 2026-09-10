# RGAA 4.1.2 - Thématique 9 - Structuration de l’information

**Statut** : référence partagée opérationnelle. **Source locale obligatoire** : `references/rgaa/normalized/rgaa-4.1.2.json` et `references/rgaa/checklists/rgaa-4.1.2-checklists.json`. **Limite** : ce fichier organise les preuves et les reprises possibles ; il ne produit pas un verdict RGAA final sans exécution et validation humaine lorsque le test l’exige.

Couverture locale : 4 critères et 9 tests RGAA. Décision opérationnelle : Produire plan de titres, listes et citations candidates ; arbitrer l’appropriation sémantique par revue humaine.

Priorité d’intégration : P1 - plan de document et listes candidates.

## Sources locales et skills

| Code | Source locale | Usage attendu |
|---|---|---|
| `PAR` | `pre-audit-rgaa-dsfr` | Orchestration de préaudit, tri NC/RECO/NOTE, preuves DOM, DSFR et validation humaine. |
| `ARD` | `audit-rgaa-creator` | Campagne RGAA multi-pages, orchestration et validation humaine, sans taux automatique. |
| `AHTML` | `accessible-html` | Production HTML accessible : doctype, langue, titre, structure, skip link, tableaux. |
| `APDF` | `accessible-pdf` | Production PDF/PDF-UA et points documentaires RGAA 13.3/13.4. |
| `ADOCX` | `accessible-docx` | Production DOCX structuré et version documentaire accessible possible. |
| `APPTX` | `accessible-pptx` | Production PPTX : ordre de lecture, langue, alternatives, tableaux et contrastes. |
| `OPQ` | `opquast` | Appui qualité web et priorisation ; non normatif RGAA. |
| `DSFRC` | `dsfr-components` | Prévention DSFR, modèles de composants et source anti-faux-positif. |

## Sources externes, licences et réemploi

| Code | Source externe | Type | Licence / contrainte | Usage retenu |
|---|---|---|---|---|
| `RGAA` | RGAA officiel | Référentiel normatif | Source publique DINUM | Source des critères/tests ; ne pas extrapoler hors RGAA 4.1.2. |
| `AXE` | axe-core | Moteur automatique | MPL-2.0 | Réutiliser en dépendance ou mapper les résultats ; ne pas copier du code sans notice MPL. |
| `HTMLCS` | HTML_CodeSniffer | Moteur WCAG historique | BSD-3-Clause | Réutiliser heuristiques ciblées, pas empiler un moteur complet en V1. |
| `IBM` | IBMa/equal-access | Moteur et règles | Apache-2.0 | Comparer aux probes internes et reprendre les règles utiles avec attribution. |
| `AR` | assistant-rgaa | Extension/fixtures RGAA | MPL-2.0 | Copie possible seulement avec notice et isolation MPL ; préférer contrats et fixtures isolées. |
| `RC` | rgaa-checker | Extension RGAA | Apache-2.0 | Réutiliser idées de sélecteurs, statuts et UX ; vérifier la couverture réelle. |
| `COP` | Copsaé outils audits accessibilité | Inventaire/grilles | GPL-3.0 | Méthodologie seulement ou isolation GPL explicite ; pas d’import dans modules propres. |

## Critères couverts

| Critère | Intitulé RGAA local | Tests tracés |
|---|---|---|
| `9.1` | Dans chaque page web, l’information est-elle structurée par l’utilisation appropriée de titres ? | `9.1.1`, `9.1.2`, `9.1.3` |
| `9.2` | Dans chaque page web, la structure du document est-elle cohérente (hors cas particuliers) ? | `9.2.1` |
| `9.3` | Dans chaque page web, chaque liste est-elle correctement structurée ? | `9.3.1`, `9.3.2`, `9.3.3` |
| `9.4` | Dans chaque page web, chaque citation est-elle correctement indiquée ? | `9.4.1`, `9.4.2` |

## Table opérationnelle par test

Abréviations de statut : `automatisable` = condition technique directement testable ; `préqualification` = signal fort mais verdict incomplet ; `revue humaine requise` = preuve exploitable à arbitrer ; `manuel` = parcours, contenu ou expertise indispensable.

| Test | Critère | Intention du test | Cible DOM ou artefact | Preuve observable attendue | Sources locales utiles | Sources externes utiles | Reprise possible | Statut | Limite connue | Question de validation humaine |
|---|---|---|---|---|---|---|---|---|---|---|
| `9.1.1` | `9.1` | Dans chaque page web, la hiérarchie entre les titres (balise `<hx>` ou balise possédant un attribut WAI-ARIA… | `éléments h1, h2, h3, h4, h5 et h6 dans l'ordre du DOM`, `éléments possédant role="heading" avec un attribut aria-level`, `titres visuellement cachés mais présents dans le DOM ou l'arbre d'accessibilité`, `document HTML principal et états dynamiques ouverts pendant l'audit` | `heading_count`, `native_heading_count`, `aria_heading_count`, `h1_count`, `heading_nodes`, `heading_dom_order` (+43) | PAR, ARD, AHTML, APDF, ADOCX, APPTX, OPQ, DSFRC | RGAA, AXE, HTMLCS, IBM, AR, RC, COP | checklist, UX, inspiration, fixture MPL isolée | manuel | Aucun verdict fiable sans contenu, parcours ou expertise métier réelle. | Ne pas mélanger avec 8.5 : la balise title de head n'est pas un titre de contenu. |
| `9.1.2` | `9.1` | Dans chaque page web, le contenu de chaque titre (balise `<hx>` ou balise possédant un attribut WAI-ARIA… | `éléments h1, h2, h3, h4, h5 et h6 dans l'ordre du DOM`, `éléments possédant role="heading" avec un attribut aria-level`, `titres visuellement cachés mais présents dans le DOM ou l'arbre d'accessibilité`, `document HTML principal et états dynamiques ouverts pendant l'audit` | `heading_count`, `native_heading_count`, `aria_heading_count`, `h1_count`, `heading_nodes`, `heading_dom_order` (+44) | PAR, ARD, AHTML, APDF, ADOCX, APPTX, OPQ, DSFRC | RGAA, AXE, HTMLCS, IBM, AR, RC, COP | checklist, UX, inspiration, fixture MPL isolée | manuel | Aucun verdict fiable sans contenu, parcours ou expertise métier réelle. | Ne pas mélanger avec 8.5 : la balise title de head n'est pas un titre de contenu. |
| `9.1.3` | `9.1` | Dans chaque page web, chaque passage de texte constituant un titre est-il structuré à l’aide d’une balise `<hx>` o… | `éléments h1, h2, h3, h4, h5 et h6 dans l'ordre du DOM`, `éléments possédant role="heading" avec un attribut aria-level`, `titres visuellement cachés mais présents dans le DOM ou l'arbre d'accessibilité`, `document HTML principal et états dynamiques ouverts pendant l'audit` (+1) | `heading_count`, `native_heading_count`, `aria_heading_count`, `h1_count`, `heading_nodes`, `heading_dom_order` (+44) | PAR, ARD, AHTML, APDF, ADOCX, APPTX, OPQ, DSFRC | RGAA, AXE, HTMLCS, IBM, AR, RC, COP | checklist, UX, inspiration, fixture MPL isolée | manuel | Aucun verdict fiable sans contenu, parcours ou expertise métier réelle. | Ne pas mélanger avec 8.5 : la balise title de head n'est pas un titre de contenu. |
| `9.2.1` | `9.2` | Dans chaque page web, la structure du document vérifie-t-elle ces conditions (hors cas particuliers) ? | `structure du document : header, nav, main, footer et usage de main visible unique` | `test_id`, `source_rgaa_locale`, `target_count`, `target_nodes`, `scope`, `inspectability` (+13) | PAR, ARD, AHTML, APDF, ADOCX, APPTX, OPQ, DSFRC | RGAA, AXE, HTMLCS, IBM, AR, RC, COP | checklist, UX, inspiration, fixture MPL isolée | manuel | Aucun verdict fiable sans contenu, parcours ou expertise métier réelle. | Comparer la structure programmée au rendu et au contenu. |
| `9.3.1` | `9.3` | Dans chaque page web, les informations regroupées visuellement sous forme de liste non ordonnée vérifient-elles un… | `informations regroupées visuellement sous forme de liste non ordonnée` | `test_id`, `source_rgaa_locale`, `target_count`, `target_nodes`, `scope`, `inspectability` (+11) | PAR, ARD, AHTML, APDF, ADOCX, APPTX, OPQ, DSFRC | RGAA, AXE, HTMLCS, IBM, AR, RC, COP | sélecteur, heuristique, checklist, fixture MPL isolée | préqualification | Signal exploitable, verdict RGAA incomplet sans contexte et revue humaine. | Identifier les listes visuelles simulées par retours ligne ou ponctuation. |
| `9.3.2` | `9.3` | Dans chaque page web, les informations regroupées visuellement sous forme de liste ordonnée vérifient-elles une de… | `informations regroupées visuellement sous forme de liste ordonnée` | `test_id`, `source_rgaa_locale`, `target_count`, `target_nodes`, `scope`, `inspectability` (+11) | PAR, ARD, AHTML, APDF, ADOCX, APPTX, OPQ, DSFRC | RGAA, AXE, HTMLCS, IBM, AR, RC, COP | sélecteur, heuristique, checklist, fixture MPL isolée | préqualification | Signal exploitable, verdict RGAA incomplet sans contexte et revue humaine. | Identifier les listes visuelles simulées par retours ligne ou ponctuation. |
| `9.3.3` | `9.3` | Dans chaque page web, les informations regroupées sous forme de liste de description utilisent-elles les balises… | `informations regroupées sous forme de liste de description` | `test_id`, `source_rgaa_locale`, `target_count`, `target_nodes`, `scope`, `inspectability` (+11) | PAR, ARD, AHTML, APDF, ADOCX, APPTX, OPQ, DSFRC | RGAA, AXE, HTMLCS, IBM, AR, RC, COP | sélecteur, heuristique, checklist, fixture MPL isolée | préqualification | Signal exploitable, verdict RGAA incomplet sans contexte et revue humaine. | Identifier les listes visuelles simulées par retours ligne ou ponctuation. |
| `9.4.1` | `9.4` | Dans chaque page web, chaque citation courte utilise-t-elle une balise `<q>` ? | `citations courtes dans le contenu de la page` | `test_id`, `source_rgaa_locale`, `target_count`, `target_nodes`, `scope`, `inspectability` (+9) | PAR, ARD, AHTML, APDF, ADOCX, APPTX, OPQ, DSFRC | RGAA, AXE, HTMLCS, IBM, AR, RC, COP | checklist, UX, inspiration, fixture MPL isolée | manuel | Aucun verdict fiable sans contenu, parcours ou expertise métier réelle. | Confirmer qu'il s'agit d'une citation et non d'un simple slogan ou exemple. |
| `9.4.2` | `9.4` | Dans chaque page web, chaque bloc de citation utilise-t-il une balise `<blockquote>` ? | `blocs de citation dans le contenu de la page` | `test_id`, `source_rgaa_locale`, `target_count`, `target_nodes`, `scope`, `inspectability` (+9) | PAR, ARD, AHTML, APDF, ADOCX, APPTX, OPQ, DSFRC | RGAA, AXE, HTMLCS, IBM, AR, RC, COP | checklist, UX, inspiration, fixture MPL isolée | manuel | Aucun verdict fiable sans contenu, parcours ou expertise métier réelle. | Confirmer qu'il s'agit d'une citation et non d'un simple slogan ou exemple. |

## Garde-fous de réemploi

- Les codes de sources externes renvoient au tableau de licences ci-dessus ; toute copie de fixture ou de helper `AR` doit rester isolée avec notice MPL-2.0.
- Les sources `CARN`, `COP`, `TEM` ou `TPG` ne doivent pas être copiées dans les modules propres sans isolation ou validation juridique ; reprendre seulement les comportements observables et les idées de preuve.
- Les lignes `préqualification` et `revue humaine requise` doivent toujours conserver la preuve brute, la limite et la question humaine dans le résultat du skill consommateur.
- `pre-audit-rgaa-dsfr` peut consommer cette référence pour orienter les preuves, mais `audit-rgaa-creator` reste la voie pour un audit complet et une qualification humaine.
