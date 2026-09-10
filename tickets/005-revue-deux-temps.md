# 005 — Rendre explicite la qualification en deux temps

**À construire :** le générateur documente et trace séparément la création de
la revue à qualifier et le rendu effectué après validation de cette revue.

**Bloqué par :** Aucun — peut commencer immédiatement.

**Statut :** ready-for-agent

- [ ] Le premier passage sans fiche crée la fiche et ne rend aucun livrable.
- [ ] `--allow-pending` ne contourne pas la création initiale de la fiche.
- [ ] Le second passage rend les éléments autorisés et marque les groupes non
  arbitrés comme non vérifiés.
- [ ] L’état du passage et l’empreinte de la fiche sont traçables.
- [ ] Une fiche préexistante reste inchangée octet pour octet pendant le rendu.
- [ ] La documentation décrit clairement les deux passages et leurs codes de
  sortie compatibles.

**Preuve attendue :** rejeu complet première exécution puis seconde exécution,
avec vérification de la fiche et de l’état produit.
