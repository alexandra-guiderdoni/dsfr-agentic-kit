# Catalogue des pictos SVG

## Sources DSFR

Source officielle à privilégier quand une conformité DSFR est demandée : le dépôt `GouvernementFR/dsfr-artwork` ou une distribution locale vérifiée contenant les pictogrammes.

Sources à vérifier au moment de l’usage :

- documentation officielle DSFR « Pictogramme » : `https://www.systeme-de-design.gouv.fr/version-courante/fr/fondamentaux/pictogramme` ;
- dépôt officiel : `https://github.com/GouvernementFR/dsfr-artwork` ;
- paquet public DSFR `@gouvfr/dsfr`, qui expose `dist/artwork/pictograms` ; le récupérer avec `npm pack @gouvfr/dsfr@<version> --ignore-scripts` puis l’extraire, car `npm install` exécute depuis `1.15.0` un script `preinstall` qui exige l’acceptation des modalités d’utilisation (voir `DISTRIBUTION.md`) ;
- clone du dépôt amont `GouvernementFR/dsfr`, dossier `src/dsfr/core/asset/artwork/pictograms`, identique au `dist` publié pour `1.14.4` et `1.15.2` ;
- distribution locale contrôlée contenant `dist/artwork/pictograms`. Depuis `1.15.0`, les releases GitHub ne fournissent plus le code compilé (note publiée `v1.15.0`) ; une archive de release n’est donc plus une source de pictogrammes.

Conséquence opérationnelle : ne jamais promettre une copie officielle sans dossier local vérifié ou sans reproduction depuis le corpus embarqué. Utiliser `--source dsfr-artwork --dsfr-artwork-root <chemin>` seulement si le dossier contient des fichiers `famille/nom.svg`. Utiliser `--source dsfr-replica` si le nom existe dans `pictos-svg/dsfr-officiels/manifest.json`. Ne pas supposer qu’un paquet NPM `@gouvfr/dsfr-artwork` est disponible : vérifier le dépôt, l’archive ou le dossier local au moment de l’usage.

Le skill embarque un snapshot officiel sous `pictos-svg/dsfr-officiels/`. Les conditions d’usage DSFR restent applicables. Les créations originales doivent rester marquées `official: false`.

## Noms DSFR connus

La liste complète embarquée dans le script correspond au snapshot récupéré depuis `@gouvfr/dsfr@1.14.4`, vérifié identique dans `@gouvfr/dsfr@1.15.2` le 28 août 2026 (`pictos-svg/dsfr-officiels/SOURCE.md`) : utiliser `python3 scripts/generate_pictos_svg.py --list-dsfr-names` pour l’afficher.

Pour la revue unitaire du corpus récupéré, utiliser `pictos-svg/dsfr-officiels/INDEX.md`. Le script accepte aussi un futur nom `famille/nom` si le fichier correspondant existe dans la source DSFR fournie.

La liste ci-dessous reste un aperçu pratique des familles fréquentes.

## Reproduction embarquée

Le corpus `pictos-svg/dsfr-officiels/` contient 102 pictogrammes officiels issus de `@gouvfr/dsfr@1.14.4`, inchangés dans `1.15.2`. Pour reproduire un pictogramme existant, utiliser :

```bash
python3 scripts/generate_pictos_svg.py \
  --source dsfr-replica \
  --icons buildings/house \
  --output-dir assets/pictos
```

Ce mode doit être préféré à une imitation manuelle. Le manifeste de sortie indique `source: dsfr-replica` et `reproduction: exact-copy-from-embedded-official-corpus`.

## Guide de style

Le guide `references/guide-style-pictogrammes-dsfr.md` est la source principale pour créer de nouveaux pictogrammes proches du DSFR quand aucun pictogramme officiel n’existe.

Le profil `references/dsfr-style-profile.md` et sa version machine `references/dsfr-style-profile.json` complètent le guide avec les statistiques extraites du corpus.

Règles issues du corpus, détaillées dans le guide :

- utiliser un gabarit `0 0 80 80` ;
- conserver les calques `artwork-decorative`, `artwork-minor`, `artwork-major` ;
- utiliser trois `<use>` pour appliquer les calques ;
- placer les couleurs dans les classes `fr-artwork-*` ;
- réserver `artwork-major` au sujet principal et `artwork-minor` aux accents de sens ;
- garder les éléments décoratifs rares et secondaires.

### buildings

- `buildings/city-hall`
- `buildings/factory`
- `buildings/house`
- `buildings/nuclear-plant`
- `buildings/school`

### digital

- `digital/application`
- `digital/avatar`
- `digital/calendar`
- `digital/coding`
- `digital/data-visualization`
- `digital/internet`
- `digital/mail-send`
- `digital/search`

### document

- `document/contract`
- `document/document`
- `document/document-add`
- `document/document-download`
- `document/document-signature`
- `document/driving-licence`
- `document/national-identity-card`
- `document/passport`
- `document/tax-stamp`
- `document/vehicle-registration`

### environment

- `environment/environment`
- `environment/food`
- `environment/grocery`
- `environment/human-cooperation`
- `environment/leaf`
- `environment/moon`
- `environment/mountain`
- `environment/sun`
- `environment/tree`

### health, institutions, leisure, map, system

- `health/health`
- `health/hospital`
- `health/vaccine`
- `health/virus`
- `institutions/firefighter`
- `institutions/gendarmerie`
- `institutions/justice`
- `institutions/money`
- `institutions/police`
- `leisure/book`
- `leisure/community`
- `leisure/culture`
- `leisure/digital-art`
- `leisure/paint`
- `map/airport`
- `map/location-france`
- `map/luggage`
- `map/map`
- `system/connection-lost`
- `system/error`
- `system/information`
- `system/notification`
- `system/padlock`
- `system/success`
- `system/system`
- `system/technical-error`
- `system/warning`

## Gabarit officiel DSFR

Pour un pictogramme officiel ou conforme DSFR :

- `viewBox="0 0 80 80"` ;
- `width="80px" height="80px"` pour une création nouvelle ;
- `width="80" height="80"` accepté seulement pour une copie officielle existante ;
- grille de conception carrée `80 x 80` sur base `2 px`, espacements et détails alignés autant que possible sur des multiples de `4` ou `8` ; repère de dessin, pas un critère d’audit, les coordonnées officielles étant majoritairement décimales ;
- occupation du carré comparable aux références : repères mesurés dans `references/dsfr-style-profile.md` ;
- lisibilité contrôlée à `40 x 40 px`, et à `24 px` pour les usages de slides ou légendes ;
- trois calques avec les id `artwork-decorative`, `artwork-minor`, `artwork-major` ;
- pas de `fill` ni `stroke` sur les chemins des symboles ;
- intégration via trois `<use>` ;
- classe `fr-artwork` et `aria-hidden="true"` dans un contexte web DSFR ;
- couleur majeure non personnalisable, couleur mineure personnalisable avec un indice `main` de la palette DSFR (`--minor-color`, 24 couleurs relevées dans `src/module/color/variable/_options.scss` de `1.15.2`), couleur décorative optionnelle ;
- équilibre visuel major / minor / decorative proche de `60 / 30 / 10`.

## Mode legacy généré

Les pictogrammes générés par le mode `generated` (`--source generated`, jamais par défaut) sont des symboles filaires autonomes en `256x256`, utilisables comme assets PowerPoint génériques. Ils ne remplacent pas `dsfr-artwork` et ne doivent pas être utilisés pour une demande `original-dsfr-like`.

Règles :

- utiliser un `viewBox` carré `0 0 256 256` ;
- garder un trait homogène, par défaut 9 px ;
- utiliser `#000091` pour le preset DSFR et `#001070` pour le preset `slides-ia` ;
- réserver le rouge à l’alerte, au contrôle ou à une validation critique ;
- éviter les dégradés, ombres, motifs, CSS externe, texte visible et images embarquées ;
- privilégier une silhouette lisible à 24 px plutôt qu’un dessin détaillé.

Ces pictos générés ne sont pas les pictogrammes officiels DSFR. Ils sont des assets SVG originaux, compatibles avec une présentation DSFR, mais visuellement distincts du corpus officiel.

## Catalogue intégré

| Nom | Usage recommandé |
|-----|------------------|
| `accessibility` | Accessibilité, service ouvert, inclusion |
| `ai` | IA, modèle, automatisation contrôlée |
| `api` | API, intégration, échange de services |
| `calendar` | Jalons, échéance, planification |
| `chain` | Chaîne, dépendance, liaison |
| `check` | Validation, conformité, passage de gate |
| `code` | Développement, script, dépôt |
| `cost` | Coût, budget, euro |
| `data` | Données, base, capitalisation |
| `document` | Source, dossier, livrable écrit |
| `house` | Lieu, accueil, habitat |
| `lock` | Protection, accès, secret |
| `pencil` | Édition, annotation, écriture |
| `production` | Mise en production, exploitation |
| `rocket` | Lancement, POC, passage à l’échelle |
| `server` | Hébergement, infrastructure, runtime |
| `shield` | Sécurité, souveraineté, maîtrise |
| `supervision` | Monitoring, mesure, pilotage |
| `support` | Assistance, exploitation, maintien |
| `test` | Tests, recette, assurance qualité |
| `user` | Agent, utilisateur, équipe |
| `warning` | Risque, alerte, point bloquant |

## Choix de pictos pour slides DSFR

- Carte de processus : choisir des pictos de même niveau de détail.
- Alerte : utiliser `warning`, `shield` ou `lock` avec accent rouge.
- Étape de validation : utiliser `check` ou `test`.
- Chaîne IA applicative : combiner `document`, `ai`, `code`, `test`, `production`.
- Production maîtrisée : combiner `shield`, `server`, `supervision`, `support`.

## Insertion PPT

Avant de déclarer un deck validé, vérifier le support SVG du moteur de rendu. Si le moteur ne supporte pas les SVG, signaler la limite. Produire un PNG de secours seulement si la demande l’autorise explicitement, avec `--export-png <taille>` qui trace le rendu dans le manifeste, en conservant le SVG comme source. Afficher les pictogrammes à `40 px` au moins dans un deck (`32 px` en limite basse) ; sur fond sombre, un SVG autonome garde ses couleurs figées, prévoir un fond clair ou une variante déclarée.
