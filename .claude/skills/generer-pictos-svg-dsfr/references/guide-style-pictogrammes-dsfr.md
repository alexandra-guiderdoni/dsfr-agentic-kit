# Guide de style des pictogrammes DSFR

Ce guide distille le corpus officiel embarqué dans `pictos-svg/dsfr-officiels/`. Il sert à reproduire les pictogrammes existants sans approximation et à créer des pictogrammes originaux visuellement indiscernables au premier regard dans une planche DSFR, tout en les déclarant comme non officiels.

Le skill embarque 102 références officielles dans `pictos-svg/dsfr-officiels/` ; la distillation normative vient uniquement de ces références. Les repères chiffrés, complexité et occupation du carré, sont mesurés par `scripts/analyze_dsfr_corpus.py` et publiés dans `references/dsfr-style-profile.md` ; ce guide n’en recopie aucun pour ne pas dériver du corpus.

## Priorité absolue

Si le pictogramme existe dans `pictos-svg/dsfr-officiels/manifest.json`, utiliser `--source dsfr-replica`. Ne pas le redessiner.

Si la demande exige un pictogramme officiel et qu’aucune source vérifiable ne le contient, arrêter avec `NOT VERIFIED`. Ne pas générer un substitut.

Si le pictogramme est absent du corpus, créer un `original-dsfr-like` seulement après avoir cité trois à cinq références officielles inspectées et appliqué le profil de prompt `references/dsfr-prompt-profile.json`.

## Statuts de sortie

- `dsfr-artwork` : copie depuis une source officielle locale vérifiée.
- `dsfr-replica` : copie byte-à-byte depuis le corpus officiel embarqué.
- `original-dsfr-like` : création originale au gabarit DSFR, `official: false`.
- `dsfr-grammar-transplant` : variante non officielle issue d’un archétype DSFR inspecté, avec `primary_archetype`, `semantic_delta` et `official: false`.
- `generated-legacy` : ancien mode filaire `256x256`, DSFR-inspired, non indiscernable du corpus officiel.

Ne jamais présenter `original-dsfr-like`, `dsfr-grammar-transplant` ou `generated-legacy` comme officiel.

## Structure obligatoire

Toute création `original-dsfr-like` doit utiliser cette structure :

```xml
<svg width="80px" height="80px" viewBox="0 0 80 80" xmlns="http://www.w3.org/2000/svg">
  <style>
    .fr-artwork-decorative { fill: #ECECFF; }
    .fr-artwork-minor { fill: #E1000F; }
    .fr-artwork-major { fill: #000091; }
  </style>
  <symbol id="artwork-decorative">...</symbol>
  <symbol id="artwork-minor">...</symbol>
  <symbol id="artwork-major">...</symbol>
  <use class="fr-artwork-decorative" href="#artwork-decorative"/>
  <use class="fr-artwork-minor" href="#artwork-minor"/>
  <use class="fr-artwork-major" href="#artwork-major"/>
</svg>
```

Observations du corpus officiel :

- 102 fichiers analysés.
- `viewBox="0 0 80 80"` dans tous les fichiers.
- 94 fichiers déclarent `width="80px" height="80px"`.
- 8 fichiers déclarent `width="80" height="80"`.
- 4 fichiers ajoutent `fill="none"` sur la racine.
- Les trois symboles sont toujours dans l’ordre `artwork-decorative`, `artwork-minor`, `artwork-major`.
- `system-system.svg` réutilise deux fois `fr-artwork-major` dans les `<use>` ; ne pas reprendre cette exception pour une création nouvelle.

Règle de création : utiliser `80px`, sans `fill` racine, avec trois `<use>` canoniques.

## Grille et lisibilité

Repères issus de la documentation DSFR :

- le symbole est construit par défaut sur un carré `80 x 80` ;
- la construction repose sur une base de `2 px` ;
- les espacements et détails doivent rester autant que possible sur des multiples de `4` ou `8` ;
- le pictogramme doit rester lisible à `40 x 40 px` dans un contexte web ;
- pour les slides et documents, contrôler aussi le rendu à `24 px`, car c’est une taille fréquente d’annotation ou de légende.

Ces repères décrivent une grille de conception, pas une propriété vérifiable des chemins officiels : mesuré sur le corpus, seules quatre coordonnées sur dix des `d` sont entières, trois sur quatre pour le décor. Ne pas en faire un critère d’audit ; contrôler la composition par l’occupation du carré et la lisibilité.

Règle de création : équilibrer les masses dans le carré `80 x 80`, garder de l’aération, éviter les détails isolés sous `2 px`, puis vérifier visuellement à 80 px, 40 px et 24 px.

## Calques

- `artwork-major` porte le sujet principal, sa silhouette et ses détails structurants. Le sujet doit rester lisible si les deux autres calques disparaissent.
- `artwork-minor` porte un seul accent de sens : statut, action, repère, détail actif, fenêtre, sceau, alerte, trajet, coche ou point focal. Cet accent peut être composé de plusieurs sous-formes rouges si elles servent le même signal, par exemple un pavillon et des détails de coque sur un même sujet maritime.
- `artwork-decorative` apporte de la respiration : points périphériques, petites particules, repères discrets. Il ne porte jamais le sens.

Test mental : retirer le minor, le domaine reste lisible ; remettre le minor, l’intention précise apparaît.

## Signature visuelle DSFR

Un pictogramme DSFR n’est pas une icône filaire générique en bleu et rouge. La fidélité vient de la grammaire de formes :

- le `major` dessine la silhouette complète du sujet, avec une densité comparable aux références inspectées ;
- les traits apparents sont des formes remplies, souvent proches de `2 px`, avec terminaisons arrondies construites dans le `d` ;
- les évidements internes sont larges et lisibles, jamais des détails décoratifs microscopiques ;
- l’objet occupe le carré avec une présence comparable aux références, généralement entre `6 px` et `72 px` sur au moins un axe ; l’occupation mesurée par la boîte englobante du `major` et du `minor` est publiée dans `references/dsfr-style-profile.md` et l’audit la compare aux références inspectées ;
- les points décoratifs restent en périphérie et ne compensent jamais un sujet trop pauvre ;
- le rouge est un accent de sens visible, pas la couleur principale d’un objet entier sauf référence officielle très proche ;
- la composition évite le petit pictogramme isolé au centre quand les références de la famille utilisent une scène, un support, une main, un document, une base ou un second repère.
- chaque création cite l’emprunt de grammaire repris depuis une référence officielle : occupation du carré, support, rythme des évidements, rôle du rouge ou type de scène ;
- dans une série, chaque pictogramme doit avoir une silhouette et un accent rouge propres au concept, pas une variation du même pictogramme avec un détail différent.
- si l’archétype porte déjà un accent rouge fort, le delta sémantique doit rester dans le `major` bleu ou dans la composition ; deux signaux rouges concurrents rendent le pictogramme confus à petite taille. Plusieurs formes rouges coordonnées restent acceptables quand elles expriment le même signal.

Signaux de reprise immédiate :

- objet réduit à une icône Lucide/Feather/Material simplifiée ;
- contours très réguliers, symétriques et sans détails de contexte ;
- `minor` plus visible que le sujet principal ;
- rouge utilisé comme remplissage majoritaire ;
- rouge trop discret par rapport aux références officielles inspectées ;
- diagonale fine seule dans le carré sans support DSFR ;
- puce électronique, base de données ou document générique utilisé comme sujet par défaut pour plusieurs concepts abstraits ;
- même coche, badge, pastille, ligne ou motif rouge réutilisé dans plusieurs pictogrammes d’une série ;
- deux accents rouges qui expliquent deux choses différentes dans le même pictogramme ;
- `major` ou `minor` très sous les commandes des références inspectées.

## Couleurs et chemins

Les trois couleurs doivent vivre uniquement dans les classes `fr-artwork-*` :

- décoratif : `#ECECFF`
- mineur : `#E1000F`
- majeur : `#000091`

Proportion de référence : major / minor / decorative autour de `60 / 30 / 10`. Ce repère sert à équilibrer le dessin, pas à calculer des surfaces exactes. Une création qui passe techniquement l’audit mais dont le `minor` disparaît à `40 px` ou semble absent à côté des références doit être reprise.

Dans les symboles officiels, les formes visibles sont des `<path>`. Les attributs observés sur les chemins sont `d`, `fill-rule` et `clip-rule`.

Règles bloquantes :

- ne pas utiliser `stroke-width` pour simuler un pictogramme filaire ;
- ne pas utiliser `<line>`, `<rect>`, `<circle>`, `<polyline>` ou `<g fill="none" stroke="...">` dans les symboles ;
- ne pas mettre `fill`, `stroke`, dégradé, filtre, masque ou opacité directement sur les chemins ;
- ne pas ajouter de calque, couleur, texte, chiffre décoratif, logo, Marianne, drapeau, sceau ou marque.

Le rendu peut paraître filaire et aéré, mais l’implémentation doit être en formes remplies, fusionnées en chemins.

## Complexité minimale

Le style officiel utilise peu de chemins, mais des chemins riches. Un picto trop simple devient une icône générique déguisée.

Repères officiels par calque : lire la section « Complexité par calque » de `references/dsfr-style-profile.md`, régénérée à chaque mise à jour du corpus ; l’audit lit les p10 dans `references/dsfr-style-profile.json`. Le style officiel utilise le plus souvent un chemin par calque, riche en sous-chemins.

Règle de création :

- viser un chemin par calque, avec plusieurs sous-chemins dans le même `d` ;
- garder le `major` au-dessus du p10 officiel du profil et proche des références choisies, sauf concept très sobre ;
- garder le `minor` visible et sémantique, au-dessus du p10 officiel du profil, sauf point ou accent minimal justifié ;
- comparer `major` et `minor` à la médiane des références inspectées, pas seulement au p10 global ;
- comparer l’occupation du carré du `major` et du `minor` à la plage officielle p10-p90 et aux références inspectées ;
- rejeter une création dont `major` et `minor` sont très sous les références inspectées sans justification.

Les seuils relatifs de l’audit sont calibrés sur le corpus et lus dans `references/dsfr-style-profile.json` (`audit_calibration`) : pour chaque officiel comparé à trois références de sa famille, le minimum observé des ratios officiel/références fixe le seuil, si bien qu’aucun officiel n’est « très sous ses références » par construction (un percentile 10 en signalait 29 sur 102, mesure du 29 août 2026) ; la plage d’occupation est la plage observée ; seule la pauvreté absolue (p10 des commandes, et sous la moitié des références) peut signaler un officiel très sobre, au plus une dizaine, à justifier par une référence précise. L’audit refuse aussi une copie exacte d’un officiel déclarée comme création.

Commande de garde-fou :

```bash
python3 scripts/audit_original_pictos.py \
  --svg pictos-svg/<dossier>/<picto>.svg \
  --manifest pictos-svg/<dossier>/manifest.json \
  --references famille/nom,famille/nom,famille/nom \
  --strict
```

L’audit détecte la structure non canonique, le statut `official` absent ou incorrect, une copie exacte d’un officiel, les références insuffisantes, les calques trop pauvres et une occupation du carré hors de la plage observée. Codes de sortie : `0` conforme, `1` erreurs d’audit, `2` avertissements en `--strict`, `3` erreur d’exécution (fichier, JSON ou profil de calibration illisible). Le code `2` est aussi celui d’argparse pour une ligne de commande invalide : dans ce cas la sortie d’erreur commence par `usage:`, jamais par `AVERTISSEMENT`. Il ne remplace pas la revue visuelle : un avertissement accepté doit être expliqué par une référence officielle précise.

Sans `--manifest`, l’audit lit le `manifest.json` voisin du SVG s’il existe ; sans aucun manifeste, `official: false` reste non vérifiable et la sortie le signale.

## Décor

Les points décoratifs officiels sont presque toujours des disques de rayon environ 1, encodés en `<path>`, placés en périphérie.

Règle de création :

- utiliser 3 à 5 points décoratifs si le concept le supporte ;
- garder des coordonnées simples et entières quand c’est possible ;
- ne jamais placer le décor au centre comme sujet ;
- ne pas créer de fond plein, disque, ombre, motif dense, texture ou scène d’arrière-plan.

## Métaphores par famille

- `accessibility` : personne, oreille, œil, fauteuil ; le rouge signale absence, limitation ou focus fonctionnel.
- `buildings` : façade, maison, école, usine, infrastructure ; le rouge différencie une fonction ou un détail architectural.
- `digital` : écran, calendrier, enveloppe, avatar, graphe, loupe ; le rouge marque état actif, notification, validation ou point focal.
- `document` : feuille, carte, passeport, permis, tampon, signature ; le rouge porte statut, sceau, ligne active ou action.
- `environment` : feuille, arbre, soleil, lune, montagne, mains ; le rouge reste organique : pousse, fruit, rayon, trace humaine.
- `health` : stéthoscope, hôpital, microscope, vaccin, virus ; le rouge signale l’élément médical critique.
- `institutions` : objet-symbole de fonction publique, sans emblème officiel ; le rouge distingue le rôle.
- `leisure` : livre, casque, palette, manette, vidéo, micro ; le rouge porte interaction ou expressivité.
- `map` : carte, repère, bagage, avion, boussole, France ; le rouge désigne destination, trajet ou point géographique.
- `system` : statut, sécurité, notification, langue, configuration ; le rouge peut être le message central.

Choisir un seul sujet dominant. Si deux objets sont nécessaires, l’un est support principal et l’autre badge secondaire.

## Méthode de référence

Avant toute création absente du corpus, citer trois à cinq SVG officiels inspectés :

- deux références de la même famille sémantique ;
- une référence avec une géométrie proche ;
- une référence pour le rôle du `minor` rouge si l’action ou le statut est important ;
- une référence de décor seulement si la composition pose une vraie question.

Pour chaque référence, noter : sujet `major`, rôle `minor`, type de décor, densité, position dans le carré `80x80`, et écart assumé. Les champs `title`, `major` et `minor` de `pictos-svg/dsfr-officiels/manifest.json` donnent le sujet et le rôle du rouge de chaque officiel ; la densité et l’occupation sont dans `references/dsfr-style-profile.json` ; trois micro-spécifications rétro-ingénierées d’officiels servent de calibrage dans `references/dsfr-prompt-profile.json` (`worked_examples`).

Reprendre la grammaire du corpus, pas des morceaux de formes.

Avant de dessiner, écrire une micro-spécification en quatre lignes :

- sujet bleu principal et détails qui restent lisibles sans rouge ;
- accent rouge unique et raison sémantique ; plusieurs formes rouges sont possibles si elles renforcent le même signal ;
- décor périphérique choisi ou absence justifiée ;
- références dont on reprend la grammaire : densité, occupation, rôle du rouge, niveau de détail.

Pour une série, ajouter quatre champs de contrôle avant chaque SVG :

- `borrowed_grammar` : référence officielle et règle visuelle reprise sans copier les chemins ;
- `concept_metaphor` : objet ou scène concrète qui incarne le concept abstrait ;
- `unique_minor_accent` : forme rouge propre à ce pictogramme et justification ; lister les sous-formes rouges coordonnées si le signal en combine plusieurs ;
- `series_difference` : différence de silhouette, support ou scène avec les autres pictogrammes de la série.

## Méthode v3 : archétype d’abord

Quand l’objectif est une haute fidélité visuelle au DSFR, ne pas partir d’une page blanche. Choisir un `primary_archetype` parmi les SVG officiels inspectés, puis créer une variante par delta minimal.

Champs obligatoires pour une création V3 :

- `primary_archetype` : référence officielle qui fixe l’occupation du carré et le rythme global ;
- `preserved_grammar` : éléments conservés de l’archétype, par exemple support, masses, évidements, décor, niveau de détail ou rôle du rouge ;
- `semantic_delta` : modification minimale qui porte le nouveau concept ;
- `path_edit_budget` : limite volontaire des zones modifiées, généralement un ou deux détails sémantiques ;
- `visual_delta_check` : phrase de contrôle vérifiant que le résultat reste d’abord lisible comme une variante naturelle du DSFR.

Règle : conserver l’ADN visuel avant d’ajouter le sens. Le bon résultat doit sembler proche d’une référence officielle voisine, pas d’un pictogramme reconstruit avec des formes compatibles.

Si une partie significative des chemins officiels est conservée, le manifeste doit utiliser `reproduction: "dsfr-grammar-transplant"` et expliquer le caractère dérivatif. Ce mode est acceptable pour une haute fidélité visuelle, mais il ne doit jamais servir à dupliquer un pictogramme officiel sous un autre nom sans delta sémantique lisible.

Signaux de reprise V3 :

- le dessin ne peut pas citer un archétype principal ;
- le delta sémantique change toute la silhouette ;
- plusieurs formes simples remplacent les chemins organiques de l’archétype ;
- les points, coins arrondis et traits de `2 px` sont réguliers mais sans rythme officiel ;
- le pictogramme semble techniquement conforme mais visuellement extérieur au corpus DSFR.

## Mode PNG référence d’abord

Quand une série originale doit atteindre un rendu plus professionnel que le dessin SVG direct, utiliser le PNG comme maquette de direction artistique, pas comme livrable vectoriel.

Séquence obligatoire :

1. Produire une planche PNG de pictogrammes isolés sur fond blanc, sans texte, sans logo, sans emblème, avec la palette DSFR et une composition proche du corpus.
2. Sélectionner seulement les candidats qui ont déjà une silhouette DSFR crédible : sujet bleu fort, accent rouge sobre, évidements larges, détails lisibles.
3. Pour chaque candidat, choisir un `primary_archetype` officiel et écrire ce qui vient du PNG : `png_reference_role`, `selected_png_candidate`, `visual_features_to_preserve`, `raster_features_to_discard`, `native_svg_reconstruction`.
4. Reconstruire un SVG natif `80x80` avec les trois symboles DSFR, uniquement des `<path>` remplis, sans primitive et sans ressource externe.
5. Comparer le SVG reconstruit au PNG, à l’archétype officiel et aux tailles `80 px`, `40 px`, `24 px`.

Une planche PNG n’est pas concluante si elle répète la même solution sous quatre formes ou si elle ressemble déjà à un SVG brouillon. Pour les concepts abstraits, inclure au moins une proposition sobre très proche d’un officiel, une proposition plus expressive, une proposition avec autre support et une proposition sans second objet. Choisir par lisibilité à `24 px` et proximité DSFR avant la richesse explicative.

Quand le candidat retenu vient d’un archétype qui utilise déjà le rouge, le delta sémantique ne doit pas ajouter de second signal rouge concurrent. Exemple de règle générale : si la loupe rouge signifie déjà la recherche, la similarité ou la sémantique doivent être portées par le réseau bleu, le support ou la composition. En revanche, plusieurs sous-formes rouges restent acceptables si elles appartiennent au même accent sémantique.

Le PNG peut être conservé comme preuve visuelle, et un SVG conteneur avec PNG embarqué peut servir de planche de revue si le fichier est explicitement nommé `png-reference` ou `png-embarque`. Ce conteneur n’est pas un pictogramme DSFR natif.

Interdits :

- ne pas livrer une vectorisation automatique du PNG comme production ;
- ne pas utiliser d’autotrace comme substitut à la reconstruction DSFR ;
- ne pas conserver flou, ombre, texture, anti-crénelage visible ou artefact de raster ;
- ne pas copier les imperfections du PNG si elles contredisent le gabarit `80 x 80`, les calques ou le path-only ;
- ne pas déclarer `production-candidate` sans SVG natif reconstruit et score visuel.

Cette méthode sert à améliorer l’intuition visuelle et la sélection des formes. La production reste la même : un SVG autonome, path-only, déclaré non officiel.

## Grille de maturité production

La validation XML et l’audit de densité ne suffisent pas pour un usage production. Après la planche comparative et le contrôle à `80 px`, `40 px` et `24 px`, noter chaque création sur cinq critères `0 / 1 / 2`.

| Critère | 0 | 1 | 2 |
|---------|---|---|---|
| `dsfr_native_feel` | extérieur au corpus | proche mais dérivatif ou raide | semble naturellement DSFR |
| `semantic_delta_integration` | ajout collé | delta lisible mais encore visible | delta intégré dans la grammaire |
| `red_accent_sobriety` | rouge dominant ou décoratif | rouge utile mais trop présent | rouge sémantique et discret |
| `small_size_legibility` | confus à 24 px | lisible surtout à 40 px | lisible à 24 px |
| `standalone_usability` | nécessite une explication | utilisable avec libellé | compréhensible en contexte réel |

Statuts recommandés :

- `prototype` : moins de `6/10`, ou un critère à `0` ;
- `review-needed` : `6/10` ou `7/10`, sans critère à `0` ;
- `production-candidate` : au moins `8/10`, sans critère à `0`.

Ne pas déclarer un SVG exploitable en production si le score visuel est absent. Un score élevé reste une aide de décision : il doit être confirmé par une revue humaine avant diffusion large.

## Pipeline de prompt DSFR-like

La méthode reprend la logique de raffinement du skill `prompt-image`, mais elle la contraint au SVG DSFR. Elle ne doit pas importer de notions de caméra, lumière, matière, rendu photo ou générateur image.

Le profil de prompt `references/dsfr-prompt-profile.json` verrouille le `prompt_core`, la signature visuelle, les interdits et les checkpoints. Le `prompt_core` doit ouvrir le prompt final interne pour que le style DSFR domine avant le sujet spécifique.

Avant tout SVG original, appliquer quatre passes :

1. Fidélité sémantique : reformuler le concept demandé, prouver l’absence dans le corpus officiel et isoler le domaine utile.
2. Traduction pictographique : convertir le concept en `major_subject`, `minor_accent`, `decorative_role`, composition `80x80`, stratégie de chemins et densité.
3. Conformité DSFR : comparer aux références officielles inspectées, au profil de prompt, aux calques, à la palette, aux proportions et aux interdits.
4. Faisabilité SVG : vérifier que la forme peut être réalisée uniquement en `<path>` remplis et rester lisible à `80 px`, `40 px` et `24 px`.

Prompt1 interne obligatoire :

```text
concept:
official_status:
official_references:
major_subject:
minor_accent:
decorative_role:
composition_80x80:
path_strategy:
density_targets:
validation:
```

Prompt2 peut enrichir seulement la composition, la hiérarchie des calques, les évidements, les sous-chemins et les repères de densité. Il ne peut pas ajouter un autre style visuel, une bibliothèque d’icônes, un effet de rendu, un décor porteur de sens ou un rouge dominant.

Prompt3 interne commence par le `prompt_core`, puis ajoute la micro-spécification du pictogramme, les références officielles inspectées, l’emprunt de grammaire, la métaphore concrète, l’accent rouge unique, les contraintes bloquantes et la preuve attendue. Si le Prompt3 contredit le profil de prompt, le guide ou les références, reprendre avant d’écrire le SVG.

Pour la V3, Prompt3 ajoute aussi `primary_archetype`, `preserved_grammar`, `semantic_delta`, `path_edit_budget` et `visual_delta_check`. Le prompt doit interdire l’assemblage libre de briques géométriques quand un archétype DSFR peut porter le concept.

Si une V2 conforme ne plaît pas à la revue humaine ou reste trop faible visuellement, utiliser `prompt-image` comme étape de reformulation de direction artistique. Cette bifurcation sert à mieux décrire la silhouette, la composition, le rôle du rouge et la lisibilité ; elle ne change pas le livrable final, qui reste un SVG natif DSFR `80x80`, sans autotrace ni PNG embarqué.

## Prompt interne de création

```text
Créer un pictogramme SVG original `original-dsfr-like`.

Sources obligatoires : `pictos-svg/dsfr-officiels/manifest.json`, `references/guide-style-pictogrammes-dsfr.md`, `references/dsfr-prompt-profile.json`, `references/dsfr-style-profile.md`, puis 3 à 5 SVG officiels proches.

Avant le SVG : produire un Prompt1 interne en dix clés, puis une micro-spécification avec sujet `major`, accent `minor`, décor, références reprises et écarts assumés. Le Prompt3 interne commence par le `prompt_core` du profil DSFR. Le `major` doit rester lisible seul.

Pour une série : vérifier `borrowed_grammar`, `concept_metaphor`, `unique_minor_accent` et `series_difference` pour chaque SVG. Ne pas réutiliser la même puce électronique, base de données, feuille de document, coche ou badge rouge comme solution par défaut. Doser le rouge contre les références inspectées : assez visible pour exister dans la planche, jamais dominant au point de remplacer le sujet bleu.

Pour la haute fidélité V3 : choisir un `primary_archetype` officiel, conserver `preserved_grammar`, limiter le `semantic_delta` via `path_edit_budget`, puis contrôler `visual_delta_check` à 80 px, 40 px et 24 px.

Contraintes : `width="80px"`, `height="80px"`, `viewBox="0 0 80 80"`, grille de conception `80 x 80` sur base `2 px`, espacements en multiples de `4` ou `8`, proportions visuelles indicatives `60 / 30 / 10`, occupation du carré comparable aux références du profil, trois classes `fr-artwork-*` avec les couleurs DSFR, trois symboles `artwork-decorative`, `artwork-minor`, `artwork-major`, puis trois `use` canoniques.

Interdits : ne pas utiliser `stroke-width`, primitives SVG, couleur directe sur les chemins, calque supplémentaire, logo, emblème ou texte. Ne pas redessiner un pictogramme officiel existant. Ne pas présenter la création comme officielle.

Interdits visuels : ne pas produire une icône de bibliothèque simplement recolorée ; ne pas mettre tout l’objet en rouge ; ne pas compenser un sujet pauvre par des points décoratifs ; ne pas livrer une diagonale ou une silhouette isolée si les références utilisent un support, une base ou une scène.

Preuve attendue : XML valide, structure DSFR validée, statut `official: false`, références inspectées nommées, rôle de chaque calque justifié, complexité comparée aux références, audit `audit_original_pictos.py`, prévisualisation à 80 px, 40 px et 24 px, puis revue visuelle.
```

## Checklist de validation

- Le nom demandé n’existe pas dans `dsfr-officiels`, ou `dsfr-replica` a été utilisé.
- Le SVG a une racine `80px` / `80px` / `0 0 80 80`.
- Les trois symboles sont présents, dans l’ordre attendu.
- Les trois `<use>` sont présents, dans l’ordre canonique.
- Les couleurs sont uniquement dans les classes `fr-artwork-*`.
- Les symboles contiennent uniquement des `<path>`.
- Les chemins des symboles ne portent pas de `fill` ou `stroke`.
- Le sujet principal est dans `artwork-major`.
- L’accent rouge est utile et dans `artwork-minor`.
- Le rouge est visible à côté des références officielles ; il n’est pas sous-dosé par excès de prudence.
- Le rouge ne domine pas le sujet, sauf justification par une référence officielle très proche.
- Le décor est discret, périphérique et dans `artwork-decorative`.
- Au moins trois références officielles proches ont été inspectées.
- Le manifeste indique `official: false` pour toute création.
- L’audit `audit_original_pictos.py --strict` passe, ou les avertissements sont justifiés.
- Le rendu reste lisible à 80 px, 40 px et 24 px.
