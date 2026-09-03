# Retour d’expérience - audits RGAA et DSFR P01 à P09

## Sources analysées

- Métadonnées de session DSH : 93 tours, 3 264 étapes, environ 1,08 M tokens générés et 8,5 M ms d’outils.
- Livrables et journaux des campagnes P08 et P09.
- Validation RGAA, DSFR et rapports générés durant la session.

Le stockage DSH accessible expose les métriques de session et l’objectif actif, mais pas le transcript complet. Les constats ci-dessous s’appuient aussi sur les artefacts réellement produits et les incidents observés.

## Incidents confirmés

1. Une campagne P09 initialisée sans identifiant explicite a démarré en P01, puis a dû être modifiée manuellement.
2. Des wrappers P08 réemployés pour P09 ont produit des métadonnées et une capture de rapport P08 dans une campagne P09.
3. Une qualification RGAA sans sélecteur pouvait s’appliquer silencieusement à plusieurs instances partageant règle et test.
4. Le manifeste a inclus des fichiers `__pycache__`, puis la suppression de ces fichiers a rendu la validation incohérente.
5. La qualification DSFR manuelle a échoué lorsque des propriétés non admises par son schéma ont été ajoutées.
6. Les signaux lexicaux de changement de langue, les documents indisponibles et plusieurs interactions nécessitent des décisions humaines explicites plutôt qu’une conclusion automatique.

## Améliorations appliquées

- `init --page` accepte maintenant la forme stable `PXX::URL::Nom::type`, tout en conservant la forme historique `URL::Nom::type`.
- Le manifeste ignore désormais `__pycache__` et les fichiers `.pyc`.
- Une qualification RGAA qui correspond à plusieurs instances échoue explicitement et demande un sélecteur ou un identifiant de signal.
- Trois tests de non-régression couvrent l’identifiant de page explicite, l’ambiguïté de qualification et les caches transitoires.

## Prochaines priorités

### P0 - Contrat de qualification par instance

Ajouter `signal_id` et `instance` aux schémas RGAA et DSFR. Le moteur doit vérifier page, règle, test, sélecteur et instance avant d’appliquer une qualification. Les preuves devraient déclarer leur rôle : `assertion`, `state`, `inventory` ou `manual`.

### P0 - Protocoles génériques pilotés par la campagne

Remplacer les wrappers de campagne par une extension déclarative à laquelle le runner transmet le contexte canonique de page : identifiant, nom, URL, type et répertoire de preuves. Valider que chaque JSON d’extension restitue ces mêmes métadonnées.

### P1 - Capture et finalisation natives des rapports

Ajouter une phase `report_capture` qui lit `rapport-dsfr/BUILD.json`, capture le portail et chaque détail RGAA/DSFR, puis contrôle titre, URL, builder, ancres, filtres et interactions clavier. Finaliser ensuite dans cet ordre : rapports, captures, nettoyage des transitoires, manifeste, validation, archive.

### P1 - Schéma DSFR plus explicite

Documenter les propriétés autorisées de `dsfr-findings.json`. Ajouter `instance` et, si `kind` ou `severity` sont autorisés, les comparer aux données canoniques au lieu de les laisser définir un verdict.

### P2 - Rapports multi-pages

Remplacer les hypothèses de fichier unique dans le portail par des mappings par identifiant de page. Chaque PXX doit lier sa propre matrice de 258 tests et sa couverture DSFR.

### P2 - Couverture AY11 traçable

Transformer chaque signal AY11 non relié en ligne `A_RETESTER` avec test, preuve et protocole, plutôt qu’en avertissement global isolé.

## Principes conservés

- Aucun taux RGAA officiel sans qualification humaine complète.
- Aucun claim global de conformité DSFR.
- Les migrations DSFR restent distinctes des écarts d’intégration.
- Les documents, médias, restitution par technologie d’assistance et décisions éditoriales restent visibles comme limites tant qu’ils ne sont pas testés.
