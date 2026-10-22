# 005 — Rendre explicite la qualification en deux temps

**Résultat :** le générateur documente et trace séparément la création de
la revue à qualifier et le rendu effectué après validation de cette revue.

**Bloqué par :** Aucun — peut commencer immédiatement.

**Statut :** livré, reçu et vérifié ; preuves dans le reçu de #8.

- [x] Le premier passage sans fiche crée la fiche et ne rend aucun livrable.
- [x] `--allow-pending` ne contourne pas la création initiale de la fiche.
- [x] Le second passage rend les éléments autorisés et marque les groupes non
  arbitrés comme non vérifiés.
- [x] L’état du passage et l’empreinte de la fiche sont traçables.
- [x] Une fiche préexistante reste inchangée octet pour octet pendant le rendu.
- [x] La documentation décrit clairement les deux passages et leurs codes de
  sortie compatibles.

**Preuve attendue :** rejeu complet première exécution puis seconde exécution,
avec vérification de la fiche et de l’état produit.

Preuves : `bash scripts/tests/check-virginie-dsfr-composants.sh` ; tests
du reçu en deux passages et du premier passage sans groupe à arbitrer.
Le [mode opératoire](../documentation/MODE-OPERATOIRE.md) décrit les phases
et codes de sortie ; le reçu contient le SHA-256 de la fiche préservée.
