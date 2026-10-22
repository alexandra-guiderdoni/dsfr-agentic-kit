# 003 — Calculer la fraîcheur avec le catalogue réellement utilisé

**Résultat :** lorsque l’utilisateur fournit `--rules`, le générateur
calcule la fraîcheur avec ce fichier et inscrit son empreinte dans le manifeste.

**Bloqué par :** Aucun — peut commencer immédiatement.

**Statut :** livré, reçu et vérifié ; preuves dans le reçu de #8.

- [x] `--rules` est transmis à toutes les étapes de collecte concernées.
- [x] L’empreinte et le nombre de règles utilisés sont inscrits dans le
  manifeste.
- [x] Un catalogue temporaire cohérent avec les archives est reconnu comme à
  jour.
- [x] Le catalogue par défaut conserve le comportement actuel.
- [x] Un signal explicite indique l’utilisation d’un catalogue non canonique.

**Preuve attendue :** tests avec catalogue temporaire, catalogue par défaut et
empreinte absente ou divergente.

Preuves : `bash scripts/tests/check-virginie-dsfr-composants.sh` ; tests
`test_selected_catalog_matches_its_archive_fingerprint`,
`test_custom_catalog_and_two_pass_receipts_preserve_review` et cas historiques
de catalogue absent ou obsolète. Le [reçu](../documentation/RECEPTION-ET-BASCULE.md)
distingue les vérifications ciblées de la réception.
