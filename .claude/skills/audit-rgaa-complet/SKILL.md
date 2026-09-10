---
name: audit-rgaa-complet
description: Auditer l’accessibilité RGAA 4.1.2 par règle, test et instance, avec preuves du DOM rendu, qualification humaine séparée, file de revue des 258 tests et rapport filtrable.
allowed-tools: Read, Glob, Grep, Bash, Write, Edit, WebFetch
---

# Audit RGAA complet

Transformer une collecte instrumentée en audit qualifiable sans présenter un
scanner comme un audit réglementaire. Le skill travaille par test et par
instance ; `audit-rgaa-creator` assure l’orchestration multi-pages.

## Orchestration

La phase `rgaa`, placée après `browser`, réutilise exactement l’échantillon et
les preuves fraîches de la campagne :

```bash
bash <kit>/scripts/audit-rgaa-creator.sh run <audit>/campaign.yaml \
  --only browser,rgaa,report,validate
```

Le référentiel officiel embarqué et versionné se trouve dans
`references/rgaa-4.1.2.json` (106 critères et 258 tests). Le catalogue
exécutable `rules/rgaa-rules.json` est contrôlé contre ce référentiel. AY11 est
un collecteur optionnel : son absence ne supprime ni le référentiel ni le plan
de preuve.

Livrables :

- `rgaa/pages/Pxx.json` ;
- `rgaa/CONSTATS-INSTANCES.json` ;
- `rgaa/MATRICE-TESTS-258.md` ;
- `rgaa/REVUE-MANUELLE-258.md` ;
- `rgaa/AUDIT-PAR-PAGE.html` et `rgaa/pages-html/Pxx.html`, rendus par le builder DSFR via `audit-report-dsfr` ;
- `rgaa/RAPPORT-CONSOLIDE.md` ;
- `rgaa-findings.json` pour la qualification humaine ;
- pour une revue exhaustive d’une page, `rgaa/Pxx-DECISIONS-258.json` et sa
  vue Markdown conservent une décision et des preuves pour chacun des 258
  tests, sans transformer les tests `A_RETESTER` en résultats favorables.

## Deux niveaux de statut

### Signal instrumenté

- `PASS_CANDIDATE` : règle passée dans le seul état exercé ;
- `FAIL_CANDIDATE` : assertion en échec avec preuve ;
- `A_CONFIRMER` : signal insuffisant ;
- `NON_APPLICABLE_CANDIDAT` : aucune cible observée, applicabilité à revoir ;
- `CONTROLE_EN_ECHEC` : problème technique.

### Qualification humaine

- `C_CONFIRMEE` ;
- `NC_CONFIRMEE` ;
- `NA_CONFIRMEE` ;
- `A_RETESTER` ;
- `NON_TESTE`.

Un signal automatique ne devient jamais seul `NC_CONFIRMEE`. Une absence de
cible ne devient jamais seule `NA_CONFIRMEE`.

## Preuve minimale d’une instance

Chaque signal d’échec cite :

- identifiant de règle, critère et test RGAA ;
- page, URL, état et viewport ;
- sélecteur reproductible et numéro d’instance ;
- DOM rendu ou mesure observée avec son origine ;
- résultat attendu ;
- assertion en échec ;
- impact utilisateur ;
- source RGAA 4.1.2 ;
- recommandation et procédure de contre-test ;
- fichiers de preuve locaux.

Le DOM rendu ne doit pas être présenté comme le fichier source du dépôt.

## File de revue des 258 tests

Le référentiel embarqué est la source de vérité. AY11 peut enrichir la collecte
quand il est installé, mais ne remplace pas le référentiel. Pour chaque test,
conserver :

- cible et preuves attendues ;
- points de revue humaine ;
- limites automatiques ;
- pages proposées ;
- état `A_REVOIR`, `DECISION_PARTIELLE` ou `DECIDE` ;
- priorité selon les signaux et les parcours critiques.

La présence des 258 lignes ne prouve pas leur exécution. Un audit réglementaire
complet exige une décision et une preuve pour chaque test applicable.

## États à exercer

- initial, consentement accepté et refusé ;
- menus, recherche, accordéons, onglets et modales ouverts ;
- formulaire vide, erreur et aide ;
- desktop, mobile, zoom, reflow et espacement du texte ;
- navigation clavier ;
- lecteur d’écran réel lorsque requis ;
- documents et médias lorsqu’ils sont présents.

## Garde-fous

- Aucun taux RGAA officiel tant que les décisions humaines ne sont pas terminées.
- `PASS_CANDIDATE` ne signifie pas conformité.
- Un arbre Chromium n’est pas NVDA, JAWS, VoiceOver ou TalkBack.
- La pertinence éditoriale des alternatives, liens, titres et instructions reste humaine.
- La détection lexicale d’un changement de langue produit seulement un signal
  `A_CONFIRMER` avant revue humaine du passage et de son contexte.
- Les PDF, médias, parcours authentifiés et états non exercés restent visibles dans la file de revue.
- Les causes répétées sont regroupées sans masquer leurs instances.

## Définition de fin

- les 106 critères et 258 tests sont présents ;
- chaque signal échoué contient code observé et attendu ;
- chaque qualification confirmée possède une preuve locale ;
- les tests restants sont listés avec protocole ;
- le rapport commence par la liste des pages de l’échantillon ; chaque vue Pxx
  commence par la page auditée et son URL ;
- le rapport filtre pages, critères, statuts, sévérités et causes racines ;
- `VALIDATION.json` ne contient aucune erreur ;
- les limites humaines et techniques restent visibles.
