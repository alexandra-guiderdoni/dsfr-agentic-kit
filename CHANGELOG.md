# Journal des versions

## Prototype standalone

- réunion des capacités DSFR et RGAA/WCAG dans un seul kit consommateur ;
- ajout d’un accueil autonome pour l’humain et pour l’agent ;
- manifeste réduit aux capacités livrées ;
- contrôle standalone sans dépendance à une usine de fabrication ;
- conservation des preuves et évaluations réellement exercées ;
- ajout du mode `audit-rgaa-creator` : campagnes RGAA multi-pages, intégration
  AY11/Playwright, reprise par phase, preuves par tentative, matrice 106,
  rapports, tickets et validation déterministe ;
- extension du creator avec une phase DSFR optionnelle sur le même échantillon :
  inventaire des composants, écarts observables, captures mobile/desktop,
  matrice et rapport DSFR séparés ;
- ajout du skill `audit-dsfr-complet` et de l’audit DSFR v2 par règle et par
  instance : statuts explicites, DOM rendu observé, structure attendue,
  qualification humaine séparée, distinction intégration/migration et rapport
  HTML filtrable ;
- ajout du skill `audit-rgaa-complet` et d’une phase RGAA v2 : signaux par test
  et instance, code observé/attendu, qualification humaine canonique dans
  `rgaa-findings.json`, causes racines et file de revue dérivée des 258 tests
  AY11 ;
- ajout de `audit-report-dsfr` et du bloc structuré `audit_report` au builder
  assemblé DSFR : portail commun RGAA/DSFR, rapports complets et vues par page,
  extraits échappés, configurations conservées et provenance `BUILD.json`.

Ce prototype local n’est pas une release publiée.
