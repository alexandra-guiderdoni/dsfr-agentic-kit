# 006 — Documenter le contrat de consommation versionnée du kit

**À construire :** le kit expose un contrat générique permettant à un projet
consommateur de le récupérer dans un cache, de se positionner sur un commit
figé et de vérifier son empreinte sans copier le kit ni l’intégrer comme
sous-module.

**Bloqué par :** Aucun — peut commencer immédiatement.

**Statut :** ready-for-agent

- [ ] Le contrat décrit un commit obligatoire et un tag facultatif.
- [ ] Le contrat définit les informations minimales de `kit.lock`.
- [ ] Le contrat décrit la vérification du commit et de l’empreinte.
- [ ] Le contrat prévoit un cache de travail séparé du dépôt consommateur.
- [ ] Aucun exemple ne copie le kit dans le projet consommateur.
- [ ] Les exemples restent indépendants de toute couche hôte et de tout
  hostname Douane.

**Preuve attendue :** exemple de consommation reproductible sur un commit connu,
avec échec explicite en cas d’empreinte divergente.
