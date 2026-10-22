# 007 — Extraire la recette Douane du kit générique

**Résultat :** les trois scripts de campagne et leur retour d’expérience sont
retirés du kit générique et publiés dans le dépôt privé
`dsfr-agentic-recipes`.

**Dépendance :** le dépôt privé `alexandra-guiderdoni/dsfr-agentic-recipes`
a été créé par l’utilisateur, publié et reçu. Les archives et preuves brutes
restent dans leur stockage actuel.

**Statut :** séparation publiée et reçue ; verrou des recettes publié après le
kit. Réception synthétique dans #8 et le reçu de migration.

- [x] La liste des artefacts Douane à déplacer est établie.
- [x] Les recettes migrées consomment le kit par `kit.lock`.
- [x] Les URLs Douane ne sont plus nécessaires aux contrôles génériques du kit.
- [x] Les archives et preuves brutes ne sont pas ajoutées au dépôt public du
  kit.
- [x] Un contrôle prouve que le kit générique fonctionne sans la recette Douane.

**Preuve attendue :** inventaire avant/après, contrôle standalone et rejeu d’une
recette depuis le dépôt privé consommateur.

Livraison : [inventaire et limites](../documentation/SEPARATION-RECETTES.md).
Les quatre fichiers reçus sont conservés à l’identique hors du kit. Le lanceur
local vérifie `kit.lock` avant l’appel aux moteurs du kit. Un rejeu synthétique
local ne remplace pas la réception fonctionnelle du produit dans #8.
Les trois versions d’exécution adaptent les racines du collecteur, avec tests
de régression et conservation séparée des originaux.

Rejeu depuis le clone privé : trois tests ciblés réussis, première revue en
code 2 puis rendu synthétique en code 0, sept pages HTML et revue inchangée.
Un cache divergent est refusé en code 1 avant toute sortie. Le reçu de
publication consigne le rejeu sur le nouveau verrou et les commits distants.
Ces preuves synthétiques ne valent pas un audit frais du portail réel.
