# RGAA 4.1.2 - Thématique 8 - Éléments obligatoires

**Statut** : référence partagée opérationnelle. **Référentiel embarqué** : `../audit-rgaa-complet/references/rgaa-4.1.2.json`. **Limite** : ce fichier organise les preuves et les reprises possibles ; il ne produit pas un verdict RGAA final sans exécution et validation humaine lorsque le test l’exige.

Couverture locale : 10 critères et 13 tests RGAA. Décision opérationnelle : Automatiser doctype, langue, titre, validité et `dir` ; garder pertinence de langue, titre et changements de langue en revue humaine.

Priorité d’intégration : P1 - socle de validation statique.

## Sources locales et skills

| Code | Source locale | Usage attendu |
|---|---|---|
| `PAR` | `pre-audit-rgaa-dsfr` | Orchestration de préaudit, tri NC/RECO/NOTE, preuves DOM, DSFR et validation humaine. |
| `ARD` | `audit-rgaa-creator` | Campagne RGAA multi-pages, orchestration et validation humaine, sans taux automatique. |
| `AAW` | `audit-accessibilite-web` | Scan axe/WCAG, mapping RGAA et signaux techniques non suffisants seuls. |
| `AHTML` | `accessible-html` | Production HTML accessible : doctype, langue, titre, structure, skip link, tableaux. |
| `APDF` | `accessible-pdf` | Production PDF/PDF-UA et points documentaires RGAA 13.3/13.4. |
| `ADOCX` | `accessible-docx` | Production DOCX structuré et version documentaire accessible possible. |
| `APPTX` | `accessible-pptx` | Production PPTX : ordre de lecture, langue, alternatives, tableaux et contrastes. |
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

## Critères couverts

| Critère | Intitulé RGAA local | Tests tracés |
|---|---|---|
| `8.1` | Chaque page web est-elle définie par un type de document ? | `8.1.1`, `8.1.2`, `8.1.3` |
| `8.2` | Pour chaque page web, le code source généré est-il valide selon le type de document spécifié ? | `8.2.1` |
| `8.3` | Dans chaque page web, la langue par défaut est-elle présente ? | `8.3.1` |
| `8.4` | Pour chaque page web ayant une langue par défaut, le code de langue est-il pertinent ? | `8.4.1` |
| `8.5` | Chaque page web a-t-elle un titre de page ? | `8.5.1` |
| `8.6` | Pour chaque page web ayant un titre de page, ce titre est-il pertinent ? | `8.6.1` |
| `8.7` | Dans chaque page web, chaque changement de langue est-il indiqué dans le code source (hors cas particuliers) ? | `8.7.1` |
| `8.8` | Dans chaque page web, le code de langue de chaque changement de langue est-il valide et pertinent ? | `8.8.1` |
| `8.9` | Dans chaque page web, les balises ne doivent pas être utilisées uniquement à des fins de présentation. Cette règle est-elle respectée ? | `8.9.1` |
| `8.10` | Dans chaque page web, les changements du sens de lecture sont-ils signalés ? | `8.10.1`, `8.10.2` |

## Table opérationnelle par test

Abréviations de statut : `automatisable` = condition technique directement testable ; `préqualification` = signal fort mais verdict incomplet ; `revue humaine requise` = preuve exploitable à arbitrer ; `manuel` = parcours, contenu ou expertise indispensable.

| Test | Critère | Intention du test | Cible DOM ou artefact | Preuve observable attendue | Sources locales utiles | Sources externes utiles | Reprise possible | Statut | Limite connue | Question de validation humaine |
|---|---|---|---|---|---|---|---|---|---|---|
| `8.1.1` | `8.1` | Pour chaque page web, le type de document (balise `doctype`) est-il présent ? | `déclaration doctype attendue dans le code source de la page` | `test_id`, `source_rgaa_locale`, `target_count`, `target_nodes`, `scope`, `inspectability` (+10) | PAR, ARD, AAW, AHTML, APDF, ADOCX, APPTX, DSFRC, OPQ | RGAA, AXE, ACT, AR, RC, HTMLCS, IBM | code, sélecteur, fixture, fixture MPL isolée | automatisable | Prouve une condition technique, pas les cas particuliers ni la pertinence. | Vérifier le code source généré si le runner inspecte un DOM modifié. |
| `8.1.2` | `8.1` | Pour chaque page web, le type de document (balise `doctype`) est-il valide ? | `déclaration doctype présente et sa validité` | `test_id`, `source_rgaa_locale`, `target_count`, `target_nodes`, `scope`, `inspectability` (+11) | PAR, ARD, AAW, AHTML, APDF, ADOCX, APPTX, DSFRC, OPQ | RGAA, AXE, ACT, AR, RC, HTMLCS, IBM | code, sélecteur, fixture, fixture MPL isolée | automatisable | Prouve une condition technique, pas les cas particuliers ni la pertinence. | Vérifier le code source généré si le runner inspecte un DOM modifié. |
| `8.1.3` | `8.1` | Pour chaque page web possédant une déclaration de type de document, celle-ci est-elle située avant la balise… | `position de la déclaration doctype par rapport à la balise html` | `test_id`, `source_rgaa_locale`, `target_count`, `target_nodes`, `scope`, `inspectability` (+10) | PAR, ARD, AAW, AHTML, APDF, ADOCX, APPTX, DSFRC, OPQ | RGAA, AXE, ACT, AR, RC, HTMLCS, IBM | code, sélecteur, fixture, fixture MPL isolée | automatisable | Prouve une condition technique, pas les cas particuliers ni la pertinence. | Vérifier le code source généré si le runner inspecte un DOM modifié. |
| `8.2.1` | `8.2` | Pour chaque déclaration de type de document, le code source généré de la page vérifie-t-il ces conditions ? | `déclaration de type de document et code source généré` | `test_id`, `source_rgaa_locale`, `target_count`, `target_nodes`, `scope`, `inspectability` (+9) | PAR, ARD, AAW, AHTML, APDF, ADOCX, APPTX, DSFRC, OPQ | RGAA, AXE, ACT, AR, RC, HTMLCS, IBM | code, sélecteur, fixture, fixture MPL isolée | automatisable | Prouve une condition technique, pas les cas particuliers ni la pertinence. | Vérifier les erreurs remontées par le validateur et exclure les avertissements hors périmètre. |
| `8.3.1` | `8.3` | Pour chaque page web, l’indication de langue par défaut vérifie-t-elle une de ces conditions ? | `élément racine html`, `attribut lang sur html pour HTML4 ou HTML5`, `attributs lang et xml:lang sur html pour XHTML 1.0`, `attribut xml:lang sur html pour XHTML 1.1` (+1) | `html_element_present`, `document_markup_flavour`, `html_lang_present`, `html_lang_value`, `html_lang_source`, `html_xml_lang_present` (+14) | PAR, ARD, AAW, AHTML, APDF, ADOCX, APPTX, DSFRC, OPQ | RGAA, AXE, ACT, AR, RC, HTMLCS, IBM | code, sélecteur, fixture, fixture MPL isolée | automatisable | Prouve une condition technique, pas les cas particuliers ni la pertinence. | Ne pas mélanger avec 8.4 : 8.3 vérifie la présence d'une indication de langue, pas la validité du code ni sa pertinence par rapport au contenu réel. |
| `8.4.1` | `8.4` | Pour chaque page web ayant une langue par défaut, le code de langue vérifie-t-il ces conditions ? | `page web HTML inspectable ayant une langue par défaut issue de 8.3`, `valeur de lang sur html lorsque cet attribut porte la langue par défaut`, `valeur de xml:lang sur html lorsque cet attribut porte la langue par défaut`, `code primaire de langue avant tiret, par exemple fr dans fr-FR` (+1) | `default_language_source`, `document_markup_flavour`, `html_lang_value`, `html_xml_lang_value`, `default_language_code_raw`, `default_language_code_normalized` (+37) | PAR, ARD, AAW, AHTML, APDF, ADOCX, APPTX, DSFRC, OPQ | RGAA, AXE, ACT, AR, RC, HTMLCS, IBM | checklist, UX, inspiration, fixture MPL isolée | manuel | Aucun verdict fiable sans contenu, parcours ou expertise métier réelle. | Ne pas refaire 8.3 : 8.4 vérifie le code de langue identifié comme langue par défaut, pas la présence de l'indication. |
| `8.5.1` | `8.5` | Chaque page web a-t-elle un titre de page (balise `<title>`) ? | `élément title enfant de head dans le document HTML principal`, `valeur textuelle de la balise title`, `valeur document.title restituée par le navigateur`, `éventuelles mutations dynamiques du titre après chargement` | `html_document_candidate`, `head_element_present`, `title_element_present`, `title_element_in_head`, `title_count`, `title_nodes` (+27) | PAR, ARD, AAW, AHTML, APDF, ADOCX, APPTX, DSFRC, OPQ | RGAA, AXE, ACT, AR, RC, HTMLCS, IBM | code, sélecteur, fixture, fixture MPL isolée | automatisable | Prouve une condition technique, pas les cas particuliers ni la pertinence. | Ne pas mélanger avec 8.6 : 8.5 vérifie la présence d'un titre de page, pas sa pertinence éditoriale ni son unicité sémantique. |
| `8.6.1` | `8.6` | Pour chaque page web ayant un titre de page (balise `<title>`), le contenu de cette balise est-il pertinent ? | `page web ayant une balise title` | `test_id`, `source_rgaa_locale`, `target_count`, `target_nodes`, `scope`, `inspectability` (+9) | PAR, ARD, AAW, AHTML, APDF, ADOCX, APPTX, DSFRC, OPQ | RGAA, AXE, ACT, AR, RC, HTMLCS, IBM | checklist, UX, inspiration, fixture MPL isolée | manuel | Aucun verdict fiable sans contenu, parcours ou expertise métier réelle. | Comparer le titre à l'objet réel de la page et au titre principal visible. |
| `8.7.1` | `8.7` | Dans chaque page web, chaque texte écrit dans une langue différente de la langue par défaut vérifie-t-il une de ce… | `passages dont la langue diffère de la langue principale` | `test_id`, `source_rgaa_locale`, `target_count`, `target_nodes`, `scope`, `inspectability` (+9) | PAR, ARD, AAW, AHTML, APDF, ADOCX, APPTX, DSFRC, OPQ | RGAA, AXE, ACT, AR, RC, HTMLCS, IBM | sélecteur, heuristique, checklist, fixture MPL isolée | préqualification | Signal exploitable, verdict RGAA incomplet sans contexte et revue humaine. | Identifier les passages réellement dans une autre langue. |
| `8.8.1` | `8.8` | Pour chaque page web, le code de langue de chaque changement de langue vérifie-t-il ces conditions ? | `codes de langue des passages validés comme changements de langue au test 8.7.1` | `test_id`, `source_rgaa_locale`, `target_count`, `target_nodes`, `scope`, `inspectability` (+10) | PAR, ARD, AAW, AHTML, APDF, ADOCX, APPTX, DSFRC, OPQ | RGAA, AXE, ACT, AR, RC, HTMLCS, IBM | sélecteur, heuristique, checklist, fixture MPL isolée | préqualification | Signal exploitable, verdict RGAA incomplet sans contexte et revue humaine. | Ne scanner que les passages qualifiés via 8.7.1, pas tous les `lang` différents de la racine. |
| `8.9.1` | `8.9` | Dans chaque page web les balises (à l’exception de `<div>`, `<span>` et `<table>`) ne doivent pas être utilisées u… | `balises utilisées uniquement à des fins de présentation, hors div, span et table, et simu…` | `test_id`, `source_rgaa_locale`, `target_count`, `target_nodes`, `scope`, `inspectability` (+14) | PAR, ARD, AAW, AHTML, APDF, ADOCX, APPTX, DSFRC, OPQ | RGAA, AXE, ACT, AR, RC, HTMLCS, IBM | sélecteur, heuristique, checklist, fixture MPL isolée | préqualification | Signal exploitable, verdict RGAA incomplet sans contexte et revue humaine. | Examiner le contenu et l'intention structurelle. |
| `8.10.1` | `8.10` | Dans chaque page web, chaque texte dont le sens de lecture est différent du sens de lecture par défaut est contenu… | `texte dont le sens de lecture diffère du sens de lecture par défaut` | `test_id`, `source_rgaa_locale`, `target_count`, `target_nodes`, `scope`, `inspectability` (+8) | PAR, ARD, AAW, AHTML, APDF, ADOCX, APPTX, DSFRC, OPQ | RGAA, AXE, ACT, AR, RC, HTMLCS, IBM | code, sélecteur, fixture, fixture MPL isolée | automatisable | Prouve une condition technique, pas les cas particuliers ni la pertinence. | Identifier les passages réellement concernés par un changement de direction. |
| `8.10.2` | `8.10` | Dans chaque page web, chaque changement du sens de lecture (attribut `dir`) vérifie-t-il ces conditions ? | `changements de sens de lecture matérialisés par attribut dir` | `test_id`, `source_rgaa_locale`, `target_count`, `target_nodes`, `scope`, `inspectability` (+8) | PAR, ARD, AAW, AHTML, APDF, ADOCX, APPTX, DSFRC, OPQ | RGAA, AXE, ACT, AR, RC, HTMLCS, IBM | code, sélecteur, fixture, fixture MPL isolée | automatisable | Prouve une condition technique, pas les cas particuliers ni la pertinence. | Identifier les passages réellement concernés par un changement de direction. |

## Garde-fous de réemploi

- Les codes de sources externes renvoient au tableau de licences ci-dessus ; toute copie de fixture ou de helper `AR` doit rester isolée avec notice MPL-2.0.
- Les sources `CARN`, `COP`, `TEM` ou `TPG` ne doivent pas être copiées dans les modules propres sans isolation ou validation juridique ; reprendre seulement les comportements observables et les idées de preuve.
- Les lignes `préqualification` et `revue humaine requise` doivent toujours conserver la preuve brute, la limite et la question humaine dans le résultat du skill consommateur.
- `pre-audit-rgaa-dsfr` peut consommer cette référence pour orienter les preuves, mais `audit-rgaa-creator` reste la voie pour un audit complet et une qualification humaine.
