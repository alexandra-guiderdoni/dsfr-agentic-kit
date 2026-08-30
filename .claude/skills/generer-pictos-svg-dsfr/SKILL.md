---
name: generer-pictos-svg-dsfr
description: "Produit des pictogrammes SVG autonomes structurés selon le modèle DSFR : reproduction exacte depuis un corpus officiel embarqué, copie depuis dsfr-artwork local, ou création originale DSFR-like non officielle quand le pictogramme est absent. Utiliser quand l’utilisateur demande des pictos SVG pour slides, documents, web, cartes, étapes, callouts ou schémas institutionnels. Ne pas utiliser pour générer des slides complètes, créer des logos/emblèmes officiels, ou rasteriser silencieusement en PNG."
argument-hint: "[famille/nom officiel ou concept original] [--source dsfr-replica|dsfr-artwork|generated] [--minor-color nom-main] [--export-png taille]"
allowed-tools: Read, Glob, Grep, Bash, Write, Edit
---

# Générer pictos SVG DSFR

Créer ou récupérer des pictogrammes SVG autonomes pour des supports DSFR, en distinguant strictement les références officielles des créations originales.

## Contrat

Mission : produire des fichiers `.svg` réutilisables, avec provenance claire, structure validée et manifeste exploitable.

Objectif verrouillé : toujours prouver la source avant de générer ; ne jamais redessiner un officiel existant ; ne jamais faire passer une création originale pour un pictogramme officiel DSFR, donc jamais sans `official: false`.

Priorité de source :

- `dsfr-replica` : si le nom existe dans `pictos-svg/dsfr-officiels/manifest.json`, copier le SVG embarqué byte-à-byte.
- `dsfr-artwork` : si une source officielle locale `dist/artwork/pictograms` est fournie, copier et valider le SVG source.
- `original-dsfr-like` : si le pictogramme est absent du corpus, créer un SVG original au gabarit DSFR `80x80`, marqué non officiel.
- `dsfr-grammar-transplant` : variante non officielle construite depuis un archétype DSFR inspecté, avec delta sémantique documenté, jamais présentée comme officielle.
- `generated-legacy` : ancien mode filaire `256x256`, seulement pour des assets DSFR-inspired quand l’utilisateur n’exige pas le style pictogramme DSFR officiel.
- PNG référence d’abord, mode de conception haute fidélité : pour une série originale ambitieuse ou quand le rendu SVG direct reste trop loin du DSFR, générer d’abord une planche PNG de direction artistique, sélectionner les candidats, puis reconstruire chaque pictogramme en SVG natif DSFR `80x80`. Le PNG sert de référence visuelle, pas de livrable SVG final.

Pièges et prévention. La prévention tient en une règle : utiliser le script pour les copies (`dsfr-replica`, `dsfr-artwork`) ; pour une création originale, lire `references/guide-style-pictogrammes-dsfr.md` et `references/dsfr-prompt-profile.json`, citer trois à cinq SVG officiels proches, puis valider XML, structure `80x80`, calques, couleurs, `<use>` et manifeste. Les pièges typiques :

- s’arrêter à un premier SVG conforme alors que la preview montre une icône générique trop éloignée du DSFR ;
- utiliser le mode legacy `256x256` pour une demande DSFR-like, ou produire une icône filaire générique avec `stroke-width` au lieu de chemins DSFR ;
- prétendre qu’un SVG original est officiel, ou masquer qu’une création haute fidélité reprend la grammaire ou des chemins d’un archétype officiel ;
- livrer un autotrace, un SVG conteneur avec PNG embarqué, ou une planche PNG qui n’est qu’un brouillon vectoriel sans vraie alternative visuelle ;
- mal doser le rouge : deux accents concurrents, par exemple une loupe rouge et un lien rouge, ou un `minor` sous-dosé par prudence alors que les références officielles l’affichent ;
- livrer un PNG ou un SVG dépendant d’une ressource externe ;
- prendre une classe CSS `fr-icon-*` pour un SVG autonome, ou présenter la distillation déterministe du skill comme un entraînement de modèle ;
- modifier une copie officielle pour y ajouter `title` ou `desc` : porter titres et descriptions dans le manifeste ou le contexte d’insertion ;
- produire un logo officiel, une Marianne, un drapeau, un sceau ou une marque institutionnelle.

Preuve attendue : commande ou fichier produit, manifeste, statut de source, références inspectées, parse XML, et tests ou contrôle automatisé quand le skill est modifié.

Arrêts et replis, codes à reprendre tels quels :

- `NOT VERIFIED: source officielle absente` : officiel exigé, nom absent du corpus et aucune source locale vérifiable ; ne pas générer de substitut.
- `NOT VERIFIED: rendu visuel non relu` : création livrée sans contrôle de la planche à `80`, `40` et `24 px`.
- `NOT VERIFIED: insertion SVG non supportée` : moteur PPT non testé ; jamais de PNG à la place sans demande explicite.
- `NOT VERIFIED: export PNG indisponible` : `--export-png` sans moteur de rendu sur le poste.
- Avertissement de l’audit : justification par une référence officielle précise, ou reprise du SVG.
- V2 visuellement faible ou refusée : bifurcation `prompt-image`, puis reconstruction en SVG natif `80x80`.

Portabilité : ne pas écrire de chemin personnel dans les exemples. Exécuter les commandes depuis le dossier du skill, ou remplacer `scripts/generate_pictos_svg.py` par le chemin réel après installation.

## Procédure

### 1. Prouver la source

Lire d’abord `pictos-svg/dsfr-officiels/manifest.json`.

Si le nom demandé existe, utiliser `--source dsfr-replica`. Ne pas redessiner.

Si les SVG officiels ne sont pas embarqués (distribution qui ne redistribue pas les Ressources DSFR, par exemple le pack `agentic-design-dsfr-pack`), le mode `dsfr-replica` les résout depuis le paquet officiel en cache : `DSFR_OFFICIAL_CACHE_DIR` (défaut `~/.cache/dsfr-official-cache`), dossier `gouvfr-dsfr-<version>/package/dist/artwork/pictograms`, version lue dans `pictos-svg/dsfr-officiels/manifest.json` (`dsfr_version`), avec contrôle du `sha256` de chaque fichier contre le manifeste. Sans cache, le script répond `NOT VERIFIED: source officielle absente` avec la commande `npm pack @gouvfr/dsfr@<version> --ignore-scripts` et n’écrit rien.

Si la demande exige un officiel et que le nom est absent du corpus embarqué, chercher une source locale DSFR contenant `dist/artwork/pictograms`. Si aucune source vérifiable n’est disponible, répondre `NOT VERIFIED: source officielle absente` et ne pas générer de substitut.

Si le pictogramme est absent du corpus officiel et que l’utilisateur accepte une création, ouvrir `references/guide-style-pictogrammes-dsfr.md`, `references/dsfr-prompt-profile.json`, puis `references/dsfr-style-profile.md` ou `.json`.

### 2. Choisir les références

Pour un officiel DSFR, utiliser les noms `famille/nom`, par exemple `digital/application`, `document/document`, `system/warning`.

Pour un pictogramme absent, sélectionner trois à cinq références en lisant `title`, `major` et `minor` de chaque entrée de `pictos-svg/dsfr-officiels/manifest.json`, sans deviner depuis le nom de fichier :

- deux références de la même famille sémantique ;
- une référence de géométrie proche ;
- une référence pour le rôle du rouge `artwork-minor` si l’action ou le statut est important ;
- une référence de décor seulement si utile.

Noter pour chaque référence : sujet `major`, rôle `minor`, décor, densité, position dans le carré `80x80`, écart assumé.

### 3. Produire les SVG officiels

Reproduction depuis le corpus embarqué :

```bash
python3 scripts/generate_pictos_svg.py \
  --source dsfr-replica \
  --icons buildings/house \
  --output-dir assets/pictos
```

Inventaire complet depuis le corpus embarqué :

```bash
python3 scripts/generate_pictos_svg.py \
  --source dsfr-replica \
  --icons all \
  --output-dir assets/pictos
```

Copie depuis une source officielle locale :

```bash
python3 scripts/generate_pictos_svg.py \
  --source dsfr-artwork \
  --dsfr-artwork-root "$DSFR_ARTWORK_ROOT" \
  --icons digital/application,document/document,system/warning \
  --output-dir assets/pictos
```

Le script valide `viewBox="0 0 80 80"`, taille `80px` ou `80`, trois symboles dans l’ordre canonique, couleurs `fr-artwork-*`, trois `<use>`, absence de `fill`/`stroke` sur les chemins, de primitives non DSFR, de `DOCTYPE` et d’entités XML. Toutes les sources sont validées avant la première copie, les options le sont avant toute écriture, et un `manifest.json` existant est fusionné dans tous les modes, `generated` compris : entrées non régénérées et annotations humaines conservées, origine portée par chaque entrée, en-tête `source: mixed` et `official: false` si un dossier mélange copies officielles et créations, fichier illisible refusé plutôt qu’écrasé. Deux options tracées dans le manifeste, pour les copies officielles seulement : `--minor-color <nom>` recolore le calque `minor` avec une couleur à indice `-main` de la palette DSFR (ex. `green-emeraude-main-632`, valeur du thème clair ; personnalisation autorisée par la documentation « Pictogramme » ; contraste sur blanc contrôlé, avertissement sous `3:1`), statut `exact-copy-minor-recolored` ; `--export-png <taille>` produit en plus un PNG plein cadre rendu par `qlmanage`, ou répond `NOT VERIFIED: export PNG indisponible`.

### 4. Créer un original DSFR-like

Utiliser cette voie seulement si l’absence officielle est prouvée. Un exemple complet et audité sert d’étalon : `pictos-svg/etalon/` (SVG, générateur reproductible, manifeste avec micro-spécification et score, planche face aux références).

Contraintes bloquantes :

- racine `width="80px" height="80px" viewBox="0 0 80 80"` ;
- composition équilibrée dans la grille `80 x 80`, avec repères et espacements sur base `2 px` ;
- détails et espacements alignés autant que possible sur des multiples de `4` ou `8` ;
- silhouette principale assez riche pour être reconnaissable sans le rouge ni le décor ;
- trois symboles `artwork-decorative`, `artwork-minor`, `artwork-major` ;
- trois `<use>` canoniques `decorative`, `minor`, `major` ;
- couleurs uniquement dans les classes `fr-artwork-*` ;
- dominance visuelle proche des proportions DSFR : major environ `60 %`, minor environ `30 %`, decorative environ `10 %` ;
- emprunt de grammaire explicitement nommé : chaque création doit reprendre une logique de composition d’une référence officielle inspectée, sans copier ses formes ;
- accent rouge spécifique au concept : le `minor` peut combiner plusieurs sous-formes coordonnées si elles portent le même signal sémantique ; il ne doit pas être un badge, une coche ou un point focal réutilisé par défaut dans toute une série ;
- symboles composés uniquement de `<path>` ;
- aucun `stroke`, `stroke-width`, primitive filaire, couleur directe, filtre, masque ou ressource externe ;
- statut `official: false` dans le manifeste.

Rejeter la création si le dessin est trop pauvre par rapport aux références : un `major` ou `minor` très sous les seuils des références proches ressemble à une icône générique, pas à un artwork DSFR. Rejeter aussi si le pictogramme n’est pas lisible à `80 px`, `40 px` et `24 px`, si le rouge devient le sujet principal, si le résultat ressemble à une icône de bibliothèque convertie en chemins, ou si plusieurs créations d’une même série partagent le même squelette géométrique ou le même motif rouge.

Signature visuelle attendue : un sujet bleu dominant, composé de formes remplies qui simulent des traits de 2 px par la géométrie ; un signal rouge `minor` visible qui précise l’action, le statut ou le détail actif, éventuellement par plusieurs formes coordonnées ; un décor périphérique discret ; une occupation du carré proche des références inspectées, sans petit objet isolé au centre sauf justification par une référence officielle sobre.

Pipeline de prompt DSFR-like, inspiré de `prompt-image` mais spécialisé SVG :

1. Fidélité sémantique : comprendre le pictogramme demandé, prouver son absence officielle et lever toute ambiguïté qui changerait le sujet.
2. Traduction pictographique : convertir le concept en sujet `major`, accent `minor`, décor `decorative`, composition `80x80`, stratégie de chemins et densité cible.
3. Conformité DSFR : vérifier le résultat contre `references/dsfr-prompt-profile.json`, le guide de style, les références officielles inspectées, la palette, les calques, le path-only et les interdits.
4. Faisabilité SVG : vérifier que la forme peut être codée en `<path>` remplis, lisible à `80 px`, `40 px` et `24 px`, sans `stroke` ni primitives.

Avant d’écrire le SVG, produire un Prompt1 interne avec ces dix clés : `concept`, `official_status`, `official_references`, `major_subject`, `minor_accent`, `decorative_role`, `composition_80x80`, `path_strategy`, `density_targets`, `validation`. Enrichir ensuite seulement les calques, la composition et la densité. Le prompt final interne doit commencer par le `prompt_core` de `references/dsfr-prompt-profile.json`, puis décrire le sujet spécifique.

Garde-fou de rendu V2 : avant de coder une série de pictogrammes, rédiger une micro-spécification par fichier avec `borrowed_grammar`, `concept_metaphor`, `unique_minor_accent` et `series_difference`. Une série est refusée si elle ressemble à une déclinaison du même pictogramme, si elle repose sur une puce électronique, une base de données ou un document générique pour des concepts différents, ou si le rouge sert de décoration interchangeable.

Bifurcation `prompt-image` (skill optionnel : s’il est absent de l’installation, reformuler la direction visuelle à la main selon les mêmes contraintes) : si la V2 reste visuellement décevante, si l’utilisateur n’aime pas le pictogramme, ou si la preview révèle une mauvaise métaphore, revenir à `prompt-image` pour produire un prompt de direction visuelle DSFR contraint. Ce prompt doit améliorer la composition, le sujet, le rôle du rouge et la lisibilité, puis le résultat doit être reconstruit en SVG natif `80x80` path-only. Ne jamais livrer le raster, le prompt image ou une vectorisation automatique comme pictogramme final.

Méthodes avancées : pour `archetype-first`, `dsfr-grammar-transplant`, PNG référence d’abord et `production_score`, appliquer `references/guide-style-pictogrammes-dsfr.md` et `references/dsfr-prompt-profile.json`. Documenter `primary_archetype`, `preserved_grammar`, `semantic_delta`, `path_edit_budget`, `visual_delta_check`, `png_reference_role`, `selected_png_candidate`, `visual_features_to_preserve`, `raster_features_to_discard` et `native_svg_reconstruction`. Les invariants restent : `official: false`, SVG final natif `80x80`, aucune vectorisation automatique, aucun PNG embarqué comme livrable final et un seul accent rouge utile.

Statuts de manifeste : utiliser `review-needed` par défaut pour toute création originale. Utiliser `production-candidate` seulement si `production_score >= 8/10`, aucun critère à `0`, preview relue à `80`, `40` et `24 px`, et revue humaine explicite. Ne pas inventer de statut hybride.

### 5. Utiliser le mode legacy avec prudence

Le mode `generated` du script, à demander explicitement par `--source generated` (le défaut est `dsfr-replica`), produit des SVG filaires `256x256` avec accessibilité intégrée et un manifeste `official: false`. Il sert à des assets DSFR-inspired historiques, pas à créer un pictogramme proche des officiels DSFR.

```bash
python3 scripts/generate_pictos_svg.py \
  --source generated \
  --icons document,ai,shield \
  --output-dir pictos-svg/generated \
  --preset dsfr \
  --background none
```

Marquer ces fichiers comme `generated-legacy` ou `DSFR-inspired`, jamais comme officiels ni `original-dsfr-like`.

### 6. Maintenir le corpus

Régénérer le profil après modification du corpus officiel :

```bash
python3 scripts/analyze_dsfr_corpus.py \
  --json-output references/dsfr-style-profile.json \
  --md-output references/dsfr-style-profile.md
```

Le profil est un artefact de mesure. La norme d’exécution reste `references/guide-style-pictogrammes-dsfr.md`.

Vérifier la version de référence avant toute régénération : comparer depuis le dépôt amont avec le skill `dsfr-changelog` (`git diff --name-status -M <a> <b> -- src/dsfr/core/asset/artwork/pictograms`), puis confronter les SHA256 de `manifest.json` au `dist/artwork/pictograms` du paquet obtenu par `npm pack @gouvfr/dsfr@<b> --ignore-scripts`. Procédure détaillée, preuves et version vérifiée : `pictos-svg/dsfr-officiels/SOURCE.md`. La version de référence ne change qu’après cette vérification explicite.

Après toute modification du skill, lancer depuis son dossier `python3 -B -m unittest tests.test_generate_pictos_svg` ; `-B` évite `tests/__pycache__`, artefact interdit dans un skill packagé.

Le profil `references/dsfr-prompt-profile.json` est un artefact de cadrage du prompt. Il verrouille le `prompt_core`, la signature visuelle, les interdits et les checkpoints de qualité pour les créations `original-dsfr-like`. Ne pas le remplacer par un profil image généraliste.

### 7. Prévisualiser les créations originales

Pour les créations `original-dsfr-like`, générer une planche HTML de contrôle à `80`, `40` et `24 px` depuis le dossier qui contient les créations. Le corpus `dsfr-officiels` est exclu par défaut ; sans création dans le dossier, le script répond `Aucun SVG trouvé`, et `--include-official` l’ajoute, par exemple pour une planche du corpus officiel seul.

```bash
python3 scripts/build_svg_preview.py \
  --svg-root pictos-svg/<dossier-de-creations> \
  --references health/health,health/doctor,system/success \
  --output outputs/pictos-preview.html
```

Ouvrir la planche, comparer aux références citées et signaler `NOT VERIFIED: rendu visuel non relu` si aucun contrôle visuel n’a été fait. Pour des cas de revue prêts à l’emploi et une grille de notation, lire `references/cas-validation-visuelle.md`.

Boucle qualité obligatoire pour `original-dsfr-like` :

1. Produire une V1 conforme.
2. Générer la preview `80`, `40` et `24 px`.
3. Rédiger une critique courte : proximité DSFR, richesse du `major`, dosage du `minor`, lisibilité à `24 px`.
4. Produire une V2 si la V1 ressemble à une icône générique, si le rouge domine, si le rouge est trop discret par rapport aux références, si la silhouette est trop pauvre, ou si le rendu s’éloigne des références.
5. Si la V2 ne plaît pas ou reste visuellement faible, utiliser `prompt-image` comme outil de reformulation de direction visuelle, puis reconstruire une V3 en SVG natif.
6. Livrer la meilleure version ou marquer `review-needed` avec la limite nommée.

Avant revue humaine, lancer aussi l’audit de structure, de complexité et d’occupation du carré, dont les seuils calibrés sur le corpus sont lus dans `references/dsfr-style-profile.json` (codes de sortie : `0` conforme, `1` erreurs, `2` avertissements en `--strict`, `3` erreur d’exécution) :

```bash
python3 scripts/audit_original_pictos.py \
  --svg pictos-svg/coeur/heart.svg \
  --manifest pictos-svg/coeur/manifest.json \
  --references health/health,health/doctor,system/success \
  --strict
```

Un avertissement de l’audit ne suffit pas à refuser automatiquement un pictogramme, mais il impose une justification visuelle explicite ou une reprise du SVG.

### 8. Transmettre à un pipeline documentaire ou PPT

Transmettre les chemins SVG comme assets nommés. Ne pas supposer qu’un moteur PPT accepte directement les SVG : vérifier l’insertion réelle ou annoncer `NOT VERIFIED: insertion SVG non supportée`. Taille d’affichage conseillée pour slides et documents : `40 px` au minimum, `32 px` en limite basse ; à `24 px`, un trait de `2 px` sur `80` ne fait plus que `0,6 px` et les officiels eux-mêmes perdent leurs détails.

Ne jamais remplacer silencieusement un SVG demandé par un PNG.

Avant diffusion ou publication, appliquer `DISTRIBUTION.md` : statut non officiel des créations, limites DSFR/licence, usage du corpus et revue humaine.

## Embarquement dans une page DSFR

Les SVG produits (officiels ou `original-dsfr-like`) portent les symboles `id="artwork-decorative"`, `id="artwork-major"`, `id="artwork-minor"`. Pour les insérer dans une page ou un composant DSFR (tuile, callout, carte), les référencer via le wrapper `fr-artwork` plutôt que de recopier le SVG inline :

```html
<svg class="fr-artwork" aria-hidden="true" viewBox="0 0 80 80" width="80" height="80">
    <use class="fr-artwork-decorative" href="{chemin-vers-le-svg}.svg#artwork-decorative"></use>
    <use class="fr-artwork-minor" href="{chemin-vers-le-svg}.svg#artwork-minor"></use>
    <use class="fr-artwork-major" href="{chemin-vers-le-svg}.svg#artwork-major"></use>
</svg>
```

Servir le SVG depuis la même origine que la page : un `<use href>` externe inter-origines n’est pas résolu par les navigateurs, quelle que soit la version DSFR. Depuis `1.15.0`, le mode legacy d’`artwork.js` (IE11 ou appel explicite de `replace()`) assainit le SVG et refuse une URL d’une autre origine ; les classes `fr-artwork-*` sont inchangées dans le CSS distribué `1.15.2`.

Thème sombre : dans ce wrapper, les couleurs viennent des classes `fr-artwork-*` du CSS DSFR et suivent le thème clair ou sombre de la page. Un SVG servi seul (balise `<img>`, PowerPoint, document) garde ses couleurs figées dans son `<style>` : le prévoir sur fond clair, ou livrer une variante explicitement déclarée pour fond sombre.

Pour produire ce wrapper automatiquement, utiliser le skill `dsfr-components` : `generate_atom.py pictogram --config '{"src":"…/pictogramme.svg"}'`. Répartition : ce skill produit l'asset SVG (le dessin), `dsfr-components` l'embarque en HTML (pointer-only, jamais le dessin inline).

## Exemples

### Reproduire un pictogramme officiel existant

Demande utilisateur : `génère une maison officielle DSFR`.

Commande :

```bash
python3 scripts/generate_pictos_svg.py \
  --source dsfr-replica \
  --icons buildings/house \
  --output-dir pictos-svg/maison
```

Résultat attendu : `pictos-svg/maison/buildings-house.svg`, byte-à-byte identique à `pictos-svg/dsfr-officiels/buildings-house.svg`, avec manifeste `source: dsfr-replica`.

### Créer un pictogramme absent du corpus

Demande utilisateur : `génère un cœur`.

Workflow attendu :

```bash
python3 scripts/build_svg_preview.py \
  --svg-root pictos-svg/coeur \
  --references health/health,health/doctor,system/success \
  --output pictos-svg/coeur/preview.html
```

Résultat attendu : `pictos-svg/coeur/heart.svg`, manifeste `official: false`, références officielles inspectées dans `references_inspected`, validation structurelle DSFR et contrôle visuel à `80`, `40` et `24 px`.

## Checklist de livraison

Avant de conclure, vérifier :

- [ ] Chaque fichier attendu existe en `.svg` et sa source est `dsfr-artwork`, `dsfr-replica`, `original-dsfr-like`, `dsfr-grammar-transplant` ou `generated-legacy`.
- [ ] Les SVG `dsfr-replica` sont byte-à-byte identiques au corpus embarqué, sauf recoloration `minor` déclarée par `--minor-color` dans le manifeste.
- [ ] Les SVG officiels copiés ou reproduits contiennent `viewBox="0 0 80 80"`, trois symboles et trois `<use>` validés.
- [ ] Les créations originales suivent `references/guide-style-pictogrammes-dsfr.md`, et le `prompt_core` et les interdits de `references/dsfr-prompt-profile.json` ont cadré la micro-spécification.
- [ ] Chaque création originale nomme un emprunt de grammaire, une métaphore de concept et un accent rouge unique.
- [ ] Le `minor` rouge est assez présent par rapport aux références ; plusieurs formes rouges sont acceptées si elles servent un même signal sémantique.
- [ ] Si le mode PNG référence d’abord a été utilisé, le PNG est cité comme référence de direction artistique, le livrable final reste un SVG natif reconstruit, et aucun SVG de production ne dépend d’un PNG embarqué, d’un autotrace ou d’un artefact raster.
- [ ] Pour un rendu haute fidélité, chaque création originale nomme un `primary_archetype`, le `semantic_delta` et le `visual_delta_check`.
- [ ] Les créations visant la production ont un score `production_score` avec `dsfr_native_feel`, `semantic_delta_integration`, `red_accent_sobriety`, `small_size_legibility` et `standalone_usability`.
- [ ] Les créations originales ont suivi la boucle V1 -> preview -> critique -> V2, ou la V1 est explicitement justifiée comme suffisante.
- [ ] Si la preview ou le retour utilisateur invalide la direction visuelle, `prompt-image` a été utilisé comme étape de reformulation avant reconstruction SVG.
- [ ] Le manifeste des créations originales porte `official: false` et `review-needed` par défaut ; `production-candidate` n’apparaît qu’après score suffisant et revue humaine explicite.
- [ ] Les créations originales citent trois à cinq références officielles inspectées.
- [ ] L’audit `audit_original_pictos.py --strict` passe, ou chaque avertissement est justifié par une référence officielle inspectée.
- [ ] Les créations originales ont été prévisualisées à `80`, `40` et `24 px` avec `build_svg_preview.py --references famille/nom,...`, ou la limite `NOT VERIFIED` est annoncée.
- [ ] Pour une diffusion large, `DISTRIBUTION.md` et `references/cas-validation-visuelle.md` ont été appliqués.
- [ ] Le `manifest.json` liste les fichiers, titres ou descriptions disponibles, source et statut.
- [ ] La commande de génération ou la vérification réalisée est citée.
- [ ] Avant packaging ou diffusion, aucun `.DS_Store`, `__pycache__` ni `*.pyc` n’est présent dans le dossier du skill.
