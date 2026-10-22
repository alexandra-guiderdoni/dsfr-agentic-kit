# 008 — Aligner la documentation et vérifier le parcours complet

**Résultat reçu :** la documentation, les prompts et les exemples décrivent le
nouveau contrat standalone, puis un contrôle final prouve que le kit et la
recette séparée restent cohérents.

**Dépendances reçues :** 001, 002, 003, 004, 005, 006 et 007.

**Statut :** reçu le 22 octobre 2026 ; limites et preuves dans
[le reçu de migration](../documentation/RECEPTION-ET-BASCULE.md).

- [x] Les exemples ne pointent jamais `PROJECT_ROOT` vers le kit.
- [x] Les statuts `BLOQUE_INFRA`, `NO-GO` et les modes d’archives sont alignés.
- [x] La règle de séparation kit, recette métier et couche hôte est documentée.
- [x] Les affirmations de version Python sont datées et prouvées ou marquées
  comme non exercées.
- [x] Le contrôle complet termine au vert sur un scénario nominal.
- [x] Un scénario bloqué ne produit aucun faux livrable d’audit.

**Preuve attendue :** contrôle complet, rapport de statut et revue des exemples
depuis un projet consommateur séparé.
