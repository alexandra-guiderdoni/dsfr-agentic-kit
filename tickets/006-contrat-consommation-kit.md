# 006 — Documenter le contrat de consommation versionnée du kit

**Résultat :** le kit expose un contrat générique permettant à un projet
consommateur de le récupérer dans un cache, de se positionner sur un commit
figé et de vérifier son empreinte sans copier le kit ni l’intégrer comme
sous-module.

**Bloqué par :** Aucun — peut commencer immédiatement.

**Statut :** implémenté, relu et vérifié ; intégration automatique dans #11.

- [x] Le contrat décrit un commit obligatoire et un tag facultatif.
- [x] Le contrat définit les informations minimales de `kit.lock`.
- [x] Le contrat décrit la vérification du commit et de l’empreinte.
- [x] Le contrat prévoit un cache de travail séparé du dépôt consommateur.
- [x] Aucun exemple ne copie le kit dans le projet consommateur.
- [x] Les exemples restent indépendants de toute couche hôte et de tout
  hostname Douane.

**Preuve attendue :** exemple de consommation reproductible sur un commit connu,
avec échec explicite en cas d’empreinte divergente.

Livraison : [contrat](../documentation/CONSOMMATION-VERSIONNEE.md),
`scripts/verify-kit-lock.py` et `bash scripts/tests/check-kit-lock.sh`.
L’intégration automatique à chaque campagne reste dans #11.
