# 001 — Intégrer le générateur à la validation canonique

**À construire :** le contrôle principal du kit exécute également la suite de
tests du générateur DSFR et expose son résultat dans le bilan final.

**Bloqué par :** Aucun — peut commencer immédiatement.

**Statut :** terminé

- [x] La validation canonique lance les tests produit du générateur.
- [x] Un échec du générateur fait échouer la validation globale.
- [x] Le nombre de tests exécutés est reporté sans double comptage.
- [x] Le contrôle reste vert sur l’état de référence `f200af9`.
- [x] Un scénario négatif prouve qu’un test du générateur en échec est visible.

**Preuve attendue :** sortie du contrôle canonique et test automatisé du chemin
d’échec (`check-validation-produit-en-echec.sh`).
