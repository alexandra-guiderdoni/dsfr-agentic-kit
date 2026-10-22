# Consommer une version immuable du kit

Le projet conserve `kit.lock` ; le code du kit reste dans un cache extérieur
au projet. Un cache natif de plugin peut servir directement : aucun second
clone permanent, copie dans le projet ou sous-module n’est nécessaire.

## Identité et confiance

Le verrou JSON version 1 contient `repository`, un `commit` Git complet de
40 caractères, `algorithm: sha256-files-v1`, `fingerprint` et `files`.
`tag` est facultatif et informatif : il ne remplace jamais le commit.
`files` associe chaque chemin Git à son SHA-256 et au booléen `executable`.
L’empreinte globale est le SHA-256 de cet inventaire sérialisé en JSON UTF-8,
clés triées, séparateurs `,` et `:`, avec `ensure_ascii=True`.

Le verrou vient d’un commit obtenu depuis le dépôt de confiance, puis est
relu avec les changements du projet. Modifier à la fois le verrou et le code
n’est pas détectable comme une attaque par ce seul mécanisme. Ce contrat
prouve une intégrité, pas une signature ni une conformité DSFR ou RGAA.

La commande `create` lit les objets du commit, jamais les changements locaux.
Elle refuse les liens et sous-modules. Le tag fourni doit résoudre ce commit.
La commande `verify` compare tous les fichiers, leurs octets et leur caractère
exécutable ; elle refuse fichiers manquants, supplémentaires et liens.
Dans un checkout Git, `HEAD` doit aussi correspondre. Dans un cache sans Git,
l’attribution au commit repose sur le verrou de confiance et l’égalité des
octets ; le nom du dossier ou le manifeste du plugin ne suffit pas.

Seules les métadonnées racines `.git`, `.in_use` et `.orphaned_at`, appartenant
à l’hôte, sont exclues. Aucun fichier produit ne peut porter ces noms à la
racine. Les caches Python, dépendances, réglages et sorties restent ailleurs.

La CLI du vérificateur reste stricte, y compris sur un clone. Le runner de
campagne possède une tolérance réservée aux clones Git locaux : les fichiers
non versionnés et ignorés par Git sont exclus, mais chaque fichier du verrou
et `HEAD` restent contrôlés. Cela préserve `.env.local` et les livrables du
clone. Cette tolérance ne s’applique jamais à un cache sans Git ; elle ne
constitue pas une garantie sur l’environnement local du développeur.

## Préparer et vérifier

`SOURCE_GIT` désigne un checkout de confiance utilisé pour établir le verrou.
`KIT_ROOT` désigne l’installation réellement exécutée ; `PROJECT_ROOT` le
projet existant, disjoint du cache. Python 3.10+ et Git sont nécessaires pour
créer le verrou ; Python suffit pour vérifier un cache dépourvu de `.git`.

```bash
COMMIT="$(git -C "$SOURCE_GIT" rev-parse HEAD)"
python3 "$SOURCE_GIT/scripts/verify-kit-lock.py" create \
  --source "$SOURCE_GIT" --commit "$COMMIT" \
  --repository git@github.com:alexandra-guiderdoni/dsfr-agentic-kit.git \
  > "$PROJECT_ROOT/kit.lock"
python3 "$SOURCE_GIT/scripts/verify-kit-lock.py" verify \
  --lock "$PROJECT_ROOT/kit.lock" --kit-root "$KIT_ROOT" \
  --project-root "$PROJECT_ROOT"
```

Le vérificateur est lancé depuis une version de confiance, avant tout code
du cache à contrôler. Il ne télécharge rien, ne répare rien et ne réécrit pas
le verrou. Un refus interdit le lancement de la campagne. La garde interne
chargée ensuite par le runner sert à détecter les divergences ; elle ne peut
pas authentifier son propre code contre une altération hostile.

La recette isolée de #9 utilisait `ref: main` avec un champ `sha` contenant le
commit complet. Le catalogue publié suit actuellement `main` sans `sha` :
une mise à jour native peut recevoir un autre commit. Une branche seule
n’est pas un pin ; vérifier les octets réellement installés et conserver A
avant cette mise à jour reste nécessaire.

## Mise à jour et reprise

Une campagne démarrée avec A garde son verrou A et un cache A conservé pour
toute sa durée. L’installation de B laisse intacts son verrou, ses qualifications
et ses références figées. La rétention de l’hôte ne constitue pas une garantie :
le consommateur doit conserver A hors de la purge automatique ou refuser la
reprise lorsqu’il n’est plus disponible. Aucun repli silencieux vers B.

Avant chaque exécution ou reprise, vérifier le cache réellement invoqué.
Un passage explicite à B se prépare dans une nouvelle campagne, après étude
des changements ; conserver A et les décisions humaines originales.
Une compatibilité A → B doit être prouvée séparément, surtout si le moteur,
les règles ou la version DSFR changent.

`resume` peut relancer les phases partielles ou ignorées et invalider l’aval.
Un code 0 ne prouve pas l’absence de recalcul : relever les phases et fichiers
effectivement modifiés. Le rejeu ciblé de `report` recalcule le rapport.

## Portée livrée

`scripts/verify-kit-lock.py` et son test sont l’outil du contrat #6. Les nouvelles
campagnes conservent leur verrou et le vérifient avant leurs écritures. La
préparation d’un cache sans Git exige un commit explicite et une source de
confiance ; [le parcours de distribution](DISTRIBUTION-ET-PROFILS.md) décrit
les commandes et les profils complet et léger. Une campagne historique sans
verrou refuse toute adoption silencieuse. L’archive de skills seule n’est pas
le checkout complet couvert par ce verrou.

Vérification reproductible : `bash scripts/tests/check-kit-lock.sh`. Elle
exerce création, cache sans Git, altération, mauvais commit, liens, fichiers
supplémentaires, frontière projet/cache, conservation et exécution de A après B.
