# 004 — Distinguer un blocage d’infrastructure d’un échec d’audit

**Résultat :** une campagne interrompue par un proxy, un tunnel refusé ou
une impossibilité d’accès produit `BLOQUE_INFRA`, sans constat ni verdict RGAA
ou DSFR.

**Bloqué par :** Aucun — peut commencer immédiatement.

**Statut :** implémenté ; cas ciblés vérifiés, réception complète suivie dans #8.

- [x] Le prévol contrôle chaque origine requise une seule fois.
- [x] Une preuve proxy explicite produit `BLOQUE_INFRA`.
- [x] Un simple HTTP 403 émis par le site reste un résultat HTTP du site.
- [x] Les services facultatifs sont distingués des origines requises.
- [x] Les phases dépendantes de la page ne s’exécutent pas après un blocage
  d’infrastructure.
- [x] La sortie machine, le rapport humain et le code de sortie sont distincts
  d’un `NO-GO` ordinaire.
- [x] La défense côté navigateur refuse une réponse proxy ou une erreur de
  tunnel sans produire de constat.

**Preuve attendue :** tests locaux avec page 200, page 403 du site, refus proxy,
échec DNS et port fermé.

Preuves : tests de navigation et de sonde dans `test_audit_rgaa_creator.py`,
plus `test_proxy_block_probes_origin_once_and_stops_before_audit` sur cache
installé. Trois pages d’une même origine ne produisent qu’une sonde ; un vrai
serveur local de refus proxy produit le code 5, sans phase navigateur ou rapport
ni altération de la qualification. Le port local sans écoute est exercé ; le
DNS est injecté et les erreurs de navigation simulées, sans revendication de
mesure réseau distante. Les services facultatifs non sondés sont marqués
`NON_EXERCE_AU_PREVOL`, jamais comme joignables.
