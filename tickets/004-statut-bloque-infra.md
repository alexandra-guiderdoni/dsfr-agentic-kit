# 004 — Distinguer un blocage d’infrastructure d’un échec d’audit

**À construire :** une campagne interrompue par un proxy, un tunnel refusé ou
une impossibilité d’accès produit `BLOQUE_INFRA`, sans constat ni verdict RGAA
ou DSFR.

**Bloqué par :** Aucun — peut commencer immédiatement.

**Statut :** ready-for-agent

- [ ] Le prévol contrôle chaque hôte requis une seule fois.
- [ ] Une preuve proxy explicite produit `BLOQUE_INFRA`.
- [ ] Un simple HTTP 403 émis par le site reste un résultat HTTP du site.
- [ ] Les hôtes secondaires facultatifs sont distingués de l’hôte cible.
- [ ] Les phases dépendantes de la page ne s’exécutent pas après un blocage
  d’infrastructure.
- [ ] La sortie machine, le rapport humain et le code de sortie sont distincts
  d’un `NO-GO` ordinaire.
- [ ] La défense côté navigateur refuse une réponse proxy ou une erreur de
  tunnel sans produire de constat.

**Preuve attendue :** tests locaux avec page 200, page 403 du site, refus proxy,
échec DNS et port fermé.
