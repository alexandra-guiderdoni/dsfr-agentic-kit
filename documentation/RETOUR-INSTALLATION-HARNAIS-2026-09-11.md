# Retour d’installation du harnais — 11 septembre 2026

## Objet

Cette fiche consigne le retour d’une réinstallation et d’un rejeu du harnais
avec Claude. Elle distingue les corrections du kit, leur propagation vers le
miroir `dsfr-agentic-packs` et les écarts qui appartiennent au projet
consommateur ou à la méthode opératoire.

Le kit est la source de vérité. `dsfr-agentic-packs` est un miroir autonome :
une correction durable des zones synchronisées se fait ici, puis est propagée
et vérifiée dans le miroir.

## Frictions à traiter

| ID | Observation | Propriété | État constaté | Traitement attendu |
| --- | --- | --- | --- | --- |
| F-01 | `resume` ne rejouait pas automatiquement les phases dérivées après le rejeu d’une phase amont. | Harnais d’audit RGAA/DSFR | Corrigé dans le kit ; test de régression présent pour `protocols → report → validate`. | Conserver le correctif et le test dans le kit, puis propager au pack. Vérifier un rejeu réel après synchronisation. |
| F-02 | Le prérequis détectait Playwright Node, mais pas l’import Python dans l’interpréteur utilisé par les collecteurs. | Harnais d’audit | Corrigé : le prévol vérifie l’import dans l’interpréteur choisi par `find_python_for_ay11` et bloque les phases `browser`, `rgaa` et `dsfr` concernées ; le test de simulation masque désormais réellement Playwright, quel que soit son site d’installation. Le retest P06 importe aussi Playwright après la garde de frontière. | Propager au pack et vérifier la parité. |
| F-03 | Aucun bloc de configuration ne permettait de gouverner `headless`, proxy, arguments, `executable_path` ou `channel` du navigateur. | Harnais d’audit | Corrigé : `browser.launch` est validé par schéma, appliqué aux trois contrôles Playwright et tracé sous forme expurgée. | Propager au pack et vérifier la parité. |
| F-04 | Le prompt historique demandait `errors: []` dans `MANIFESTE-DSFR-COMPOSANTS.json`, alors que cette donnée était aujourd’hui dans la sortie JSON et `RECU-GENERATION.json`. | Recette Virginie / livrable du kit | Décision prise et implémentée : le manifeste absorbe désormais `errors`, ce qui le rend exploitable seul en post-mortem ; le gabarit de rejeu vérifie cette clé. Le prompt Douane n’est pas réintroduit. | Kit uniquement : le générateur Virginie n’est pas distribué dans le pack. |
| F-05 | `--no-index` évitait l’écriture de l’index, mais les fiches HTML conservaient le lien `../INDEX-LIVRABLES.html`. | Générateur Virginie du kit | Corrigé : le lien parent est conditionnel et absent lorsque `--no-index` est actif ; un test de non-régression le couvre. | Kit uniquement : aucune propagation au pack, qui ne distribue pas ce générateur. |
| F-06 | Le catalogue DSFR peut changer d’empreinte sans changement de version ni de nombre de règles ; les pages déjà auditées deviennent alors non reconductibles. | Harnais d’audit RGAA/DSFR | Corrigé : `validate` échoue si l’empreinte est obsolète ou mélangée, avec indication du rejeu nécessaire ; une empreinte absente reste un avertissement d’audit incomplet. | Propager au pack et vérifier la parité. |

## Éléments hors backlog technique

- L’absence de `rsync` est un avertissement attendu pour une dépendance
  optionnelle ; elle ne constitue pas une friction du harnais d’audit.
- Le lancement de la campagne avant les deux contrôles du kit est un écart de
  méthode opératoire. Il doit être consigné dans le compte rendu de campagne ou
  le runbook du projet consommateur, pas transformé en défaut du pack.
- La lecture initiale de `component: null` était une mauvaise clé de lecture.
  Le champ contractuel est `name` ; aucun correctif n’est requis.
- La fiche d’installation cloud périmée et le prompt Douane relèvent de
  documents locaux ou historiques. Ils ne doivent pas être réintroduits dans
  la distribution générique.

## Règle de propagation

Pour F-01 à F-03 et F-06 :

1. modifier et tester `dsfr-agentic-kit` ;
2. contrôler le pack `dsfr-agentic-packs` avec ses variantes de creator ;
3. contrôler la parité fonctionnelle sans écraser ses extensions propres.

F-04 et F-05 restent des corrections du kit autonome uniquement : leur
générateur n’est pas présent dans `dsfr-agentic-packs`.

Le pack reçoit donc une propagation seulement pour F-01 à F-03, avec une
preuve de ses checks dédiés.
