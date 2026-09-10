# Distribution du skill

Ce skill embarque un corpus officiel DSFR de référence et peut créer des pictogrammes originaux proches du style DSFR. La diffusion doit préserver une distinction stricte entre copie officielle et création non officielle.

## Statuts de sortie

- `dsfr-replica` : copie byte-à-byte depuis `pictos-svg/dsfr-officiels/`. Le fichier source existe dans le manifeste embarqué.
- `dsfr-artwork` : copie depuis une source officielle locale vérifiée, par exemple un dossier `dist/artwork/pictograms`.
- `exact-copy-minor-recolored` : copie officielle dont le calque `minor` prend une couleur à indice `-main` de la palette DSFR (`--minor-color`), personnalisation prévue par la documentation DSFR ; le manifeste passe `official` à `false`, garde `official_reference` à `true`, et trace le nom de la couleur, sa valeur et son contraste. Un PNG produit par `--export-png` est un export tracé du SVG, jamais un substitut silencieux.
- `original-dsfr-like` : création originale au gabarit `80x80`, inspirée par la grammaire DSFR, toujours `official: false`.
- `generated-legacy` : ancien mode filaire `256x256`, utile pour des assets génériques, jamais pour imiter un pictogramme officiel.

Ne jamais présenter `original-dsfr-like` ou `generated-legacy` comme un pictogramme officiel DSFR.

## Usage du corpus embarqué

Le corpus `pictos-svg/dsfr-officiels/` sert à reproduire des pictogrammes existants et à comparer les créations. Il ne doit pas être modifié, renommé ou complété sans procédure dédiée de mise à jour du corpus. Les champs `title`, `description`, `major`, `minor` et `decorative` de son manifeste sont des annotations propres au skill, issues d’une revue visuelle assistée validée par revue humaine le 28 août 2026, et non d’une source DSFR ; ils ne sont pas des Ressources officielles.

Une distribution peut omettre les fichiers `.svg` de `pictos-svg/dsfr-officiels/` et ne livrer que `manifest.json`, `INDEX.md` et `SOURCE.md`. Le manifeste (annotations propres au skill, `sha256` et `dsfr_version`) suffit alors à reproduire chaque pictogramme ; chaque copie trace sa provenance dans le manifeste de sortie (`resolved_from` : `embedded` ou `official-cache`) et depuis le paquet officiel en cache (`DSFR_OFFICIAL_CACHE_DIR`, voir SKILL.md) avec la même garantie octet pour octet ; sans paquet en cache, le script répond `NOT VERIFIED: source officielle absente` et n’écrit rien. Les scripts de mesure du profil et la planche du corpus embarqué restent réservés au workspace qui porte les SVG.

Avant une publication institutionnelle, vérifier la source officielle courante du DSFR ou une distribution locale contrôlée. Le snapshot embarqué facilite le travail, mais ne remplace pas une vérification de version quand la conformité officielle est l’enjeu.

Version de référence du corpus : `@gouvfr/dsfr@1.15.2`, vérifiée le 28 août 2026 ; le lot initial `1.14.4` lui est identique octet pour octet. La procédure de vérification d’une nouvelle version est décrite dans `pictos-svg/dsfr-officiels/SOURCE.md` ; la version de référence ne change qu’après cette vérification explicite.

Pour obtenir une source officielle locale sans exécuter de script d’installation, utiliser `npm pack @gouvfr/dsfr@<version> --ignore-scripts` puis extraire l’archive. Depuis `1.15.0`, `npm install @gouvfr/dsfr` exécute `scripts/preinstall.js`, qui interrompt l’installation (`process.exit(1)`) tant que les modalités d’utilisation en vigueur n’ont pas été acceptées, par un fichier `.dsfr.yml` portant `accept-license: <version des modalités>` à la racine du projet ou par la variable `DSFR_ACCEPT_LICENSE=1`. Un poste dont `~/.npmrc` porte `ignore-scripts=true` ne voit pas ce contrôle. Les releases GitHub ne fournissent plus le code compilé depuis `1.15.0`.

## Limites DSFR et licence

Les pictogrammes officiels restent soumis aux conditions du DSFR et de leur distribution d’origine. Ce skill ne confère aucun droit supplémentaire, ne crée pas de label officiel et ne permet pas de produire des logos, emblèmes, Marianne, sceaux ou marques institutionnelles.

État vérifié dans le dépôt amont `GouvernementFR/dsfr` à `v1.15.2` (28 août 2026) :

- le code est publié sous licence Etalab 2.0 (Licence Ouverte 2.0) depuis `1.15.1` (`LICENSE.md`, `package.json`, `publiccode.yml`), alors que `1.14.4` déclarait la licence MIT ;
- l’usage est encadré par les modalités d’utilisation `1.0.1` du 20 juillet 2026 (`doc/legal/cgu.md`, champ `cguVersion`), qui remplacent les anciennes CGU ;
- les modalités réservent les Ressources à la conception de sites exploités en `.gouv.fr` ou d’applications mobiles de l’État (§ 7 et § 14), interdisent de modifier les Fondamentaux, dont les iconographies de la Marque de l’État (§ 14 et § 20), imposent de conserver les mentions de propriété intellectuelle sur toute copie (§ 19) et proscrivent tout usage créant une confusion avec un service public (§ 18) ;
- l’acceptation est matérialisée à l’installation par le script `preinstall` décrit plus haut.

Conséquences pour ce skill, interprétation raisonnable des textes cités et non avis juridique : les copies `dsfr-replica` et `dsfr-artwork` sont des reproductions à l’identique et doivent rester attribuées au DSFR ; les créations `original-dsfr-like`, `dsfr-grammar-transplant` et `generated-legacy` ne sont pas des Ressources DSFR, ne doivent jamais être présentées comme telles, et leur diffusion reste soumise au périmètre institutionnel et à l’interdiction de confusion. En cas de doute sur un usage hors `.gouv.fr`, s’en remettre aux modalités elles-mêmes.

Les créations `original-dsfr-like` doivent être accompagnées d’un manifeste indiquant `official: false`, les références inspectées et la preuve de validation structurelle.

## Copies du manifeste d’interface

`agents/openai.yaml` existe en trois exemplaires sans synchronisation automatique : la source dans ce skill, le jumeau versionné `.agents/skills/generer-pictos-svg-dsfr/agents/openai.yaml` et la copie runtime `~/.codex/skills/generer-pictos-svg-dsfr/agents/openai.yaml`, hors dépôt. Après toute modification de la source, recopier les deux autres à l’identique ; le test `test_openai_manifest_contract_and_twin_parity` compare le jumeau versionné et, s’il est présent, la copie Codex, et échoue à la moindre divergence. Le manifeste ne porte que le bloc `interface` : un bloc `policy` n’est appliqué par aucun runtime, et le déclenchement contextuel du skill est celui de la description du `SKILL.md`.

## Revue humaine avant publication

Avant publication large :

1. Générer une planche comparative avec `scripts/build_svg_preview.py --references`.
2. Contrôler chaque création à `80 px`, `40 px` et `24 px`.
3. Comparer la densité, les calques, la composition et le rôle du rouge avec les références officielles.
4. Vérifier le manifeste et le statut `official: false`.
5. Obtenir un verdict humain explicite : `accepté`, `à reprendre` ou `refusé`.

Utiliser `references/cas-validation-visuelle.md` pour les cas de test et la grille de notation.

## Validation d’intégration PPT

Ne pas supposer qu’un moteur de présentation accepte les SVG. Avant de déclarer un livrable PowerPoint validé :

1. Insérer le SVG dans le moteur réellement utilisé.
2. Ouvrir le fichier généré et vérifier le rendu.
3. Contrôler l’export ou l’aperçu si le document est destiné à être partagé.
4. Conserver le SVG source dans les assets nommés.
5. Signaler `NOT VERIFIED: insertion SVG non supportée` si l’insertion n’a pas été testée.

Ne jamais remplacer silencieusement un SVG par un PNG ou un autre format. Un format de secours n’est acceptable que si la demande l’autorise explicitement.
