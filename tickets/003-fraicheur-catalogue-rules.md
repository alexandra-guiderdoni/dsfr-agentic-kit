# 003 — Calculer la fraîcheur avec le catalogue réellement utilisé

**À construire :** lorsque l’utilisateur fournit `--rules`, le générateur
calcule la fraîcheur avec ce fichier et inscrit son empreinte dans le manifeste.

**Bloqué par :** Aucun — peut commencer immédiatement.

**Statut :** ready-for-agent

- [ ] `--rules` est transmis à toutes les étapes de collecte concernées.
- [ ] L’empreinte et le nombre de règles utilisés sont inscrits dans le
  manifeste.
- [ ] Un catalogue temporaire cohérent avec les archives est reconnu comme à
  jour.
- [ ] Le catalogue par défaut conserve le comportement actuel.
- [ ] Un signal explicite indique l’utilisation d’un catalogue non canonique.

**Preuve attendue :** tests avec catalogue temporaire, catalogue par défaut et
empreinte absente ou divergente.
