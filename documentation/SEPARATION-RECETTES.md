# Séparer le produit des recettes métier

Livraison de #7 : le produit ne contient plus les trois scripts de campagne
ci-dessous. Leurs octets reçus sont conservés dans un dossier externe, avec
un inventaire SHA-256. Les versions exécutables sont publiées dans le dépôt
privé de recettes ; les preuves brutes restent dans leur stockage actuel.

| Artefact reçu | Destination | Motif |
| --- | --- | --- |
| `scripts/generate-virginie-rgaa-tickets.py` | Recettes privées | Constats et décisions de l’échantillon, titres métier, archives et versions historiques |
| `scripts/generate-p06-form-annex.py` | Recettes privées | Annexe probatoire propre à la page formulaire de la campagne |
| `scripts/retest-p06-form-safe.py` | Recettes privées | Attentes des neuf pages et protocole de retest de cette campagne |
| Retour d’expérience des audits P01–P09 | Documentation des recettes | Contexte et décisions de la campagne |
| `scripts/generate-virginie-dsfr-composants.py`, `scripts/virginie_dsfr` | Kit | Collecte, qualification, migration, rendus et frontières génériques ; noms conservés pour compatibilité |
| Archives, livrables, captures et qualifications existants | Stockage actuel du projet | Aucune nouvelle copie publique ; historique et décisions humaines préservés |
| Rapport historique de contre-revue et traces de runtime | Historique du kit | Preuves reçues inchangées, distinctes d’une recette active |

Les rendus génériques ne portent plus le nom du portail métier et ne déclarent
plus qu’un état a été exercé sur une page particulière. Les contrôles du kit
utilisent des données synthétiques ; aucun accès au portail n’est requis.

Le consommateur possède un `kit.lock` et vérifie son cache avant tout
appel. Il importe les modules génériques du kit, sans les recopier. Un cache
divergent interdit le lancement. Le verrou initial désigne le commit reçu,
jusqu’à la publication d’une version contenant la séparation.

Les versions d’exécution des trois recettes distinguent la racine du produit
et celle des recettes pour l’identité et la vérification du collecteur extrait.
Les originaux et leurs empreintes restent conservés séparément. Trois tests
sans réseau reproduisent le défaut initial puis vérifient cette adaptation ;
ils ne constituent pas un audit réel de la campagne.

Le dépôt privé `alexandra-guiderdoni/dsfr-agentic-recipes` est publié et son
contenu distant a été reçu puis exercé sur des données synthétiques. La
publication coordonnée suit l’ordre gardes du workflow, kit, puis nouveau
`kit.lock` des recettes et rejeu sur cette version. Le reçu de publication
consigne les commits et résultats. Le test synthétique ne prouve ni accès au
site réel, ni audit frais. Le transfert des données brutes et le choix de leur
stockage sécurisé restent hors de cette livraison.
