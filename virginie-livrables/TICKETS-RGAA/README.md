# Tickets RGAA — Échantillon Douane P01 à P09

- **Date de génération :** 2026-09-04
- **Référentiel :** RGAA 4.1.2
- **Occurrences RGAA sources :** 161 (145 `NC_CONFIRMEE`, 11 `A_RETESTER`, 4 `NON_TESTE`, 1 `C_CONFIRMEE`)
- **Constats `NC_CONFIRMEE` transformés :** 145
- **Causes racines livrées :** 19
- **Tickets NC :** 15
- **Fiches à requalifier :** 4

## Contenu

- `INDEX-TICKETS-RGAA.html` : accès principal aux fiches ;
- `html/` : fiches client autonomes et imprimables ;
- `markdown/` : sources structurées, enrichies à partir du canevas `ticket-rgaa` ;
- `MANIFESTE-TICKETS-RGAA.json` : correspondance exhaustive entre constats et tickets ;
- `VALIDATION-TICKETS-RGAA.json` : résultat des contrôles déterministes ;
- `SHA256SUMS` : empreintes des fichiers du répertoire livrable ;
- `../P06-FORMULAIRES/` : matrice probatoire des 34 tests, retest sûr et tickets candidats 11.10.2 / 7.5.2.

## Principe de regroupement

Une fiche est produite par cause racine. Les défauts systémiques listent toutes les pages affectées au lieu de dupliquer une fiche complète pour chaque page. Les constats 7.1.1 et 10.8.1 relatifs à la recherche sont regroupés, de même que les constats 12.7.1 et 12.7.2 relatifs au lien vers `#content`.

Les occurrences `A_RETESTER`, `NON_TESTE` et `C_CONFIRMEE` restent dans les rapports sources et ne sont pas transformées en tickets NC.

Les chemins de preuve mentionnés dans les inventaires assurent la traçabilité vers les archives de travail ; ces archives volumineuses ne sont pas dupliquées dans ce répertoire. Chaque fiche embarque néanmoins l’extrait de code nécessaire à sa compréhension.

## Limite

Ces fiches dérivent d’une préqualification instrumentée. Elles ne constituent pas un taux RGAA officiel. Toute correction revendiquée doit être recontrôlée avant clôture.

Les rapports RGAA/DSFR sont conservés byte-identiques à leurs sources. Leurs liens relatifs vers les preuves et portails d’archive ne sont pas embarqués ; la validation des liens porte uniquement sur les fichiers générés du paquet.
