# Retour d’installation du harnais — 11 septembre 2026

## Objet

Cette fiche consigne le retour d’une réinstallation et d’un rejeu du harnais
avec Claude. Elle distingue les corrections du kit, leur propagation vers le
kit et les écarts qui appartiennent au projet consommateur ou à la méthode
opératoire.

## Frictions à traiter

| ID | Observation | Propriété | État constaté | Traitement attendu |
| --- | --- | --- | --- | --- |
| F-01 | `resume` ne rejouait pas automatiquement les phases dérivées après le rejeu d’une phase amont. | Harnais d’audit RGAA/DSFR | Corrigé dans le kit ; test de régression présent pour `protocols → report → validate`. | Conserver le correctif et le test dans le kit. Vérifier un rejeu réel. |
| F-02 | Le prérequis détectait Playwright Node, mais pas l’import Python dans l’interpréteur utilisé par les collecteurs. | Harnais d’audit | Corrigé : le prévol vérifie l’import dans l’interpréteur choisi par `find_python_for_ay11` et bloque les phases `browser`, `rgaa` et `dsfr` concernées ; le test de simulation masque désormais réellement Playwright, quel que soit son site d’installation. Le retest P06 importe aussi Playwright après la garde de frontière. | Conserver le correctif et vérifier l’interpréteur réellement utilisé. |
| F-03 | Aucun bloc de configuration ne permettait de gouverner `headless`, proxy, arguments, `executable_path` ou `channel` du navigateur. | Harnais d’audit | Corrigé : `browser.launch` est validé par schéma, appliqué aux trois contrôles Playwright et tracé sous forme expurgée. | Conserver le correctif et vérifier le filtrage du runtime. |
| F-04 | Le prompt historique demandait `errors: []` dans `MANIFESTE-DSFR-COMPOSANTS.json`, alors que cette donnée était aujourd’hui dans la sortie JSON et `RECU-GENERATION.json`. | Recette Virginie / livrable du kit | Décision prise et implémentée : le manifeste absorbe désormais `errors`, ce qui le rend exploitable seul en post-mortem ; le gabarit de rejeu vérifie cette clé. Le prompt Douane n’est pas réintroduit. | Correction propre au générateur Virginie du kit. |
| F-05 | `--no-index` évitait l’écriture de l’index, mais les fiches HTML conservaient le lien `../INDEX-LIVRABLES.html`. | Générateur Virginie du kit | Corrigé : le lien parent est conditionnel et absent lorsque `--no-index` est actif ; un test de non-régression le couvre. | Correction propre au générateur Virginie du kit. |
| F-06 | Le catalogue DSFR peut changer d’empreinte sans changement de version ni de nombre de règles ; les pages déjà auditées deviennent alors non reconductibles. | Harnais d’audit RGAA/DSFR | Corrigé : `validate` échoue si l’empreinte est obsolète ou mélangée, avec indication du rejeu nécessaire ; une empreinte absente reste un avertissement d’audit incomplet. | Conserver le contrôle et distinguer rejeu frais et synthèse d’archives. |

## Éléments hors backlog technique

- L’absence de `rsync` est un avertissement attendu pour une dépendance
  optionnelle ; elle ne constitue pas une friction du harnais d’audit.
- Le lancement de la campagne avant les deux contrôles du kit est un écart de
  méthode opératoire. Il doit être consigné dans le compte rendu de campagne ou
  le runbook du projet consommateur, pas transformé en défaut du harnais.
- La lecture initiale de `component: null` était une mauvaise clé de lecture.
  Le champ contractuel est `name` ; aucun correctif n’est requis.
- La fiche d’installation cloud périmée et le prompt Douane relèvent de
  documents locaux ou historiques. Ils ne doivent pas être réintroduits dans
  la distribution générique.
