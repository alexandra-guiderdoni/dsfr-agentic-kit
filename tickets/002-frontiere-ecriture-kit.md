# 002 — Garantir qu’une campagne n’écrit jamais dans le kit

**À construire :** les pipelines qui produisent des livrables exigent un
projet de travail distinct et refusent toute destination qui résout dans le
clone du kit, y compris par lien symbolique ou chemin explicite.

**Bloqué par :** 001 — Intégrer le générateur à la validation canonique.

**Statut :** ready-for-agent

- [ ] L’absence de racine de projet produit une erreur d’usage claire.
- [ ] Les sorties et verrous par défaut sont créés sous le projet de travail.
- [ ] Une destination explicite dans le kit est refusée sans écriture.
- [ ] Un chemin passant par un lien symbolique vers le kit est refusé.
- [ ] Les quatre pipelines concernés partagent la même garde de frontière.
- [ ] L’état Git, y compris les fichiers ignorés, reste inchangé après un run.

**Preuve attendue :** tests nominaux et négatifs exécutés sur un projet
temporaire, avec comparaison de l’état du kit avant et après.
