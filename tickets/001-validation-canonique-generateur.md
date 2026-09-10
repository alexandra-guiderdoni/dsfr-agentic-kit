# 001 — Intégrer le générateur à la validation canonique

**À construire :** le contrôle principal du kit exécute également la suite de
tests du générateur DSFR et expose son résultat dans le bilan final.

**Bloqué par :** Aucun — peut commencer immédiatement.

**Statut :** ready-for-agent

- [ ] La validation canonique lance les tests produit du générateur.
- [ ] Un échec du générateur fait échouer la validation globale.
- [ ] Le nombre de tests exécutés est reporté sans double comptage.
- [ ] Le contrôle reste vert sur l’état de référence `f200af9`.
- [ ] Un scénario négatif prouve qu’un test du générateur en échec est visible.

**Preuve attendue :** sortie du contrôle canonique et test automatisé du chemin
d’échec.
