# Source des pictogrammes officiels DSFR

Version de référence vérifiée : `@gouvfr/dsfr@1.15.3` (tag amont `v1.15.3`, SHA `bfd32c25d94e`, 9 septembre 2026 ; précédente `1.15.2`, `ae35a0c8cdc6`, 12 août 2026, vérifiée le 28 août 2026). Vérification 1.15.3 réalisée le 11 septembre 2026 avec le skill `dsfr-changelog`.

Lot initial récupéré le 13 juin 2026 depuis le paquet npm `@gouvfr/dsfr@1.14.4`, dossier `dist/artwork/pictograms`. Le lot n’a pas été modifié depuis : les 102 SVG de `1.14.4` et de `1.15.2` sont identiques octet pour octet.

## Preuves de la vérification 1.15.2

- `git -C <clone> diff --name-status -M v1.14.4 v1.15.2 -- src/dsfr/core/asset/artwork/pictograms` : diff vide, 102 SVG à chaque borne.
- SHA256 des 102 entrées de `manifest.json` égaux aux fichiers `src/dsfr/core/asset/artwork/pictograms/<famille>/<nom>.svg` du dépôt amont, à `v1.14.4` comme à `v1.15.2`.
- SHA256 des 102 entrées de `manifest.json` égaux aux fichiers `dist/artwork/pictograms` du paquet obtenu par `npm pack @gouvfr/dsfr@1.15.2 --ignore-scripts` ; aucun SVG supplémentaire dans le paquet.
- Analyse d’intervalle `v1.14.4` → `v1.15.2` : les deux items qui citent les pictogrammes (#1384, documentation ; #1422, JavaScript `artwork.js` et `inject-svg.js`) ne touchent aucun fichier SVG.

Rapport complet en neuf rubriques : `design-systems/dsfr/verification-corpus-pictogrammes-1-14-4-vers-1-15-2.md` dans le workspace source, hors du skill.

## Commande de récupération initiale

```bash
python3 scripts/generate_pictos_svg.py \
  --source dsfr-artwork \
  --dsfr-artwork-root /tmp/dsfr-npm-house/package \
  --icons all \
  --output-dir pictos-svg/dsfr-officiels
```

## Procédure de vérification d’une nouvelle version

La version de référence ne change qu’après cette vérification explicite ; observer une version amont plus récente n’autorise pas à la modifier automatiquement.

1. Préparer le clone amont et les bornes selon le skill `dsfr-changelog` : `git fetch --tags`, `rev-parse` des deux tags, `merge-base --is-ancestor`.
2. Mesurer le diff des pictogrammes : `git -C <clone> diff --name-status -M <version-a> <version-b> -- src/dsfr/core/asset/artwork/pictograms`.
3. Récupérer le paquet publié sans exécuter ses scripts : `npm pack @gouvfr/dsfr@<version-b> --ignore-scripts`, puis comparer les SHA256 de `dist/artwork/pictograms` à `manifest.json` et repérer les SVG absents du manifeste.
4. Si le diff est vide et que les SHA256 coïncident : mettre à jour cette fiche, `INDEX.md`, `references/catalogue-pictos.md`, puis régénérer le profil avec `scripts/analyze_dsfr_corpus.py`.
5. Sinon : reconstruire le lot avec `--source dsfr-artwork --dsfr-artwork-root <paquet>/package --icons all --output-dir pictos-svg/dsfr-officiels`, mettre à jour `DSFR_NAMES` dans `scripts/generate_pictos_svg.py`, le catalogue, l’index et le profil, puis lancer `tests/`.

## Annotations sémantiques

Depuis le 28 août 2026, chaque entrée de `manifest.json` porte `title`, `description`, `major` (sujet bleu), `minor` (ce que porte le rouge) et `decorative`. Ces champs sont propres au skill : ils ne viennent pas du DSFR et ne sont pas des Ressources officielles. Méthode : planches HTML par famille rendues en PNG avec `agent-browser`, lues visuellement, puis rédigées ; le bloc `annotation` du manifeste porte le statut de validation : revue visuelle assistée, contre-lecture à 240 px, puis validation humaine d’Alex le 28 août 2026 sur la planche avec légendes. Ils servent à choisir des références proches (étape 2 du skill) et à calibrer les micro-spécifications de `references/dsfr-prompt-profile.json`.

Lors d’une régénération du lot avec `--source dsfr-artwork` sur ce dossier, le script fusionne les annotations existantes par nom et conserve le bloc `annotation` ; un pictogramme nouveau arrive sans annotation, à compléter. `INDEX.md` reprend titre, sujet et accent ; le régénérer depuis le manifeste après toute relecture.

## Contrôles structurels

Le manifeste `manifest.json` référence les fichiers de façon portable ; le champ `official` est un booléen JSON (`true` pour les 102 copies exactes). Les SVG sont copiés sans modification de forme depuis la source DSFR et validés sur les points suivants :

- `viewBox="0 0 80 80"` ;
- `width` et `height` en `80px` ou `80` selon le fichier officiel ;
- calques `artwork-decorative`, `artwork-minor`, `artwork-major` ;
- couleurs `#ECECFF`, `#E1000F`, `#000091` dans les classes `fr-artwork-*` ;
- trois `<use>` ; l’exception officielle `system/system` réutilise `artwork-major` comme le fichier source ;
- absence de `fill` ou `stroke` directement sur les chemins des symboles.

Observations du snapshot : 94 fichiers utilisent `80px`, 8 utilisent `80`, et 4 fichiers ont `fill="none"` sur la racine.

## Conditions d’utilisation

Les conditions d’utilisation du DSFR restent applicables. Depuis `1.15.1`, le code est publié sous licence Etalab 2.0 et son usage est encadré par les modalités d’utilisation `1.0.1` du 20 juillet 2026 ; voir `DISTRIBUTION.md`. Ce lot sert de référence d’analyse et de comparaison pour améliorer le générateur de pictogrammes du skill.

## Preuves de la vérification 1.15.3

Vérification réalisée le 11 septembre 2026, paquet `@gouvfr/dsfr@1.15.3` (tag amont `v1.15.3`, SHA `bfd32c25d94e`, 9 septembre 2026) :

- `diff -rq` entre `gouvfr-dsfr-1.15.2/package/dist/artwork/pictograms` et `gouvfr-dsfr-1.15.3/package/dist/artwork/pictograms` : vide, 102 SVG à chaque borne ;
- `git -C <clone> diff --name-status v1.15.2 v1.15.3 -- src/dsfr/core/asset/artwork/pictograms` : vide ;
- `manifest.json` : `dsfr_version` porté à `1.15.3`, SHA256 des 102 entrées inchangés.
