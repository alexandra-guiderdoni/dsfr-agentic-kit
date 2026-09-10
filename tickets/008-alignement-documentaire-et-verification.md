# 008 — Aligner la documentation et vérifier le parcours complet

**À construire :** la documentation, les prompts et les exemples décrivent le
nouveau contrat standalone, puis un contrôle final prouve que le kit et la
recette séparée restent cohérents.

**Bloqué par :** 001, 002, 003, 004, 005, 006 et 007.

**Statut :** bloqué

- [ ] Les exemples ne pointent jamais `PROJECT_ROOT` vers le kit.
- [ ] Les statuts `BLOQUE_INFRA`, `NO-GO` et les modes d’archives sont alignés.
- [ ] La règle de séparation kit, recette Douane et Loriq est documentée.
- [ ] Les affirmations de version Python sont datées et prouvées ou marquées
  comme non exercées.
- [ ] Le contrôle complet termine au vert sur un scénario nominal.
- [ ] Un scénario bloqué ne produit aucun faux livrable d’audit.

**Preuve attendue :** contrôle complet, rapport de statut et revue des exemples
depuis un projet consommateur séparé.
