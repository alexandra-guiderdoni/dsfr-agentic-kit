# Options des scripts

Référence des options des scripts de génération DSFR 1.15.3 du skill. Pour les
paramètres détaillés de chaque composant, voir `references/components.md`, puis
l'index de famille et le sous-fichier ciblé. La sortie de `--list` donne le
catalogue générable.

---

## Version DSFR ciblée

La variable d'environnement `DSFR_OFFICIAL_VERSION` fixe la version employée par
toute la chaîne. Ne rien poser laisse le comportement inchangé.

Les générateurs `generate_page.py` et `generate_layout.py` l'emploient pour les
URL du CDN écrites dans le HTML produit, `list_icons.py` pour le paquet
interrogé et `playwright_dsfr_helpers.js` pour les vérifications en navigateur ;
tous quatre retombent sur `1.15.3`, la version figée du skill, quand elle est
absente.

`check_generated_outputs.py` s'en sert autrement : elle lui fournit sa version
de contrôle par défaut, sans repli. Sans variable ni option de version, ce
script ne compare rien au paquet officiel et se limite à ses contrôles
structurels.

```bash
DSFR_OFFICIAL_VERSION=1.15.3 python3 "$SKILL_DIR/scripts/generate_page.py" --type standard --title Test
```

Son intérêt est de garder générateurs et contrôle sur la même version. Les
piloter séparément permet de produire des pages dans une version et de les
valider contre une autre, sans que rien ne le signale.

Pour `check_generated_outputs.py`, le plus explicite l'emporte : un
`--official-package <chemin>` prime sur tout, sinon `--official-version <x.y.z>`,
sinon la variable. Ce que porte la ligne de commande gagne donc toujours sur
l'environnement.

Changer de version rend les sorties figées obsolètes : les exemples
`examples/assembled/*/page.html` portent la version en dur et
`check_generated_outputs.py` les signale alors en `builder_example_drift`. Les
régénérer depuis leur `page.json` fait partie de la bascule.

---

Les commandes de ce document partent de la racine du dépôt, `SKILL_DIR`
désignant le dossier du skill (`.claude/skills/dsfr-components` chez le
mainteneur, ailleurs selon l'hôte).

## generate_page.py — pages complètes

| Option | Description |
|--------|-------------|
| `--type` | Type de page : standard, landing, form, dashboard, error, login, account, search, confirmation, list, detail, sitemap (12) |
| `--title` | Titre de la page (`<title>` et `<h1>`) |
| `--content` | Contenu HTML personnalisé à insérer |
| `--dark` | Mode sombre (`data-fr-scheme="dark"`) |
| `--brand-mode` | neutral (défaut) ou republique (bloc marque, si droit d'usage établi) |
| `--no-header` | Sans en-tête |
| `--no-footer` | Sans pied de page |
| `--output` | Fichier de sortie (sinon stdout) ; refuse d'écraser un fichier existant |
| `--assets` | Préfixe d'URL des assets DSFR (CSS/JS/favicons) au lieu du CDN jsdelivr ; offline/souveraineté (servir le paquet extrait ; son obtention par `npm install` exige depuis 1.15 l'acceptation des CGU, voir `design-systems/dsfr/references/sources.md`) |

`account` (création de compte) et `sitemap` (plan du site) sont les types les
plus récents. Les formulaires (`form`, `account`, `login`) appliquent la
validation différée (aucune contrainte native au repos).

## generate_assembled_page.py — page riche assemblée

Compose une page DSFR complète (header, main, footer) depuis un JSON décrivant
des sections (callout, cards, tiles, accordion, form, alert, etc.). Réutilise
les fonctions de génération partagées : structure produite par le skill,
garde-fous locaux à rejouer, aucune conformité globale revendiquée. Voir
`references/assembly.md` pour la liste des blocks (24) et un exemple complet.
Le schéma JSON vit dans `schemas/generate_assembled_page.schema.json`; les
exemples complets vivent dans `examples/assembled/`. Le check dédié
`check_assembled_page_schema.py` valide le schéma et les exemples avec
`jsonschema>=4.22,<5` si disponible, ou via `uv --with jsonschema`.

| Argument | Description |
|----------|-------------|
| `--config-file` | Fichier JSON décrivant la page (title, brand_mode, dark, assets_prefix, sections) |
| `--output` | Fichier de sortie ; refuse d'écraser un fichier existant |
| `--check` | Génère en mémoire et vérifie les garde-fous rapides sans écrire de fichier |

Exemple :

```bash
python3 "$SKILL_DIR/scripts/generate_assembled_page.py" --config-file page.json --output page.html
python3 "$SKILL_DIR/scripts/generate_assembled_page.py" --config-file page.json --check
```

Dépendance : le builder valide toujours la configuration contre le schéma et
exige `jsonschema>=4.22,<5`, ou `uv` (qui le ré-exécute avec la dépendance
éphémère) ; sans l'un ni l'autre il échoue en code 1 avec « jsonschema
indisponible et uv introuvable : installer jsonschema>=4.22,<5 ».

## generate_component.py — composants isolés

Deux modes :

- **Mode natif** (46 composants paramétrables) : tous les composants officiels
  DSFR 1.15.3, via `--config` JSON. Lister avec `--list`.
- **Mode bibliothèque** (variantes figées) : variantes de
  `assets/dsfr_complete_library.json`, via `--variant`. Arbitrage : les
  variantes `with_error` (`input`, `select`, `upload`) démontrent un état
  d'erreur après soumission et portent `aria-invalid="true"` à dessein ;
  elles sont exemptées du contrat « aucune contrainte au repos » par
  `allow_error_state` dans `check_generated_outputs.py`.

| Argument | Description |
|----------|-------------|
| `component` | Nom du composant (ou `list` pour lister) |
| `--variant` | Variante figée (mode bibliothèque) |
| `--config` | Configuration JSON (mode natif) |
| `--output` | Fichier de sortie ; refuse d'écraser un fichier existant |
| `--list` | Lister les composants disponibles |

Exemples :

```bash
python3 "$SKILL_DIR/scripts/generate_component.py" button --config '{"label":"Valider","variant":"primary"}'
python3 "$SKILL_DIR/scripts/generate_component.py" header --config '{"service_title":"Mon service","tools":[{"label":"Se connecter","href":"/c"}]}'
python3 "$SKILL_DIR/scripts/generate_component.py" tag --variant clickable   # mode bibliothèque
python3 "$SKILL_DIR/scripts/generate_component.py" --list
```

Variantes riches (natif, opt-in) : header `tools`/`languages`/`search`/
`navigation`, navigation `categories` (mega-menu) + `align`, footer `partners`/
`bottom_links`/`copyright`. Sans ces params, la sortie reste minimale.

`search` accepte `true`, `{}` ou `{"label": "…", "action": "/recherche"}` ; la
barre est générée dans un `<form method="get">` avec un bouton
`type="submit"` (DSFR 1.15.0, #1432). `range` accepte `hint`, `size: "sm"`,
`step`, `value`, `disabled` ; `translate` accepte `current`, `languages`
(`code`, `label`, `href`) et `id`.

## generate_atom.py — atomes (primitives sous-composant)

11 atomes : `title`, `text`, `lead`, `bold`, `icon`, `container`, `grid`,
`col`, `spacing`, `pictogram`, `color`.

Le paramètre `content` est inséré brut (HTML, non échappé) par tous les atomes
qui l'acceptent (`container`, `grid`, `col`, `spacing`, `color`) : ne pas y
passer de contenu non fiable. `col` accepte `offset` (1 à 11) et les décalages
par point de rupture `offset_sm`, `offset_md`, `offset_lg`, `offset_xl`
(`fr-col-offset-{bp}-N`). `spacing` borne `size` selon l'unité du paquet
1.15.3 : 0 à 32 pour `v`, 0 à 16 pour `w` ; hors plage, erreur courte en code 1.
`pictogram` filtre `src` par la liste blanche d'URL du skill (un schéma
`javascript:` est neutralisé en `/`).

| Argument | Description |
|----------|-------------|
| `atom` | Nom de l'atome (ou `list`) |
| `--config` | Configuration JSON |
| `--output` | Fichier de sortie ; refuse d'écraser un fichier existant |
| `--list` | Lister les atomes |

Exemples :

```bash
python3 "$SKILL_DIR/scripts/generate_atom.py" grid --config '{"gutters":true,"cols":[{"content":"A","md":6}]}'
python3 "$SKILL_DIR/scripts/generate_atom.py" container --config '{"size":"lg","fluid":true}'
python3 "$SKILL_DIR/scripts/generate_atom.py" color --config '{"kind":"background","variant":"alt","color":"blue-france"}'
python3 "$SKILL_DIR/scripts/generate_atom.py" pictogram --config '{"src":"/dsfr/artwork/pictograms/buildings/house.svg"}'
```

Note : `container` émet `fr-container[-{sm|md|lg|xl}][--fluid]` (séparateur
simple). `color` en mode texte, échelles relevées dans `utility.min.css`
1.15.3 (table `UTILITY_COLOR_SCALES` de `generate_atom.py`) : `action-high`
(défaut) et `label` acceptent la palette Marianne ; `inverted` accepte la
palette Marianne, `grey` et les états ; `default` n'accepte que
`{error, grey, info, success, warning}` ; `mention` n'accepte que `grey` ;
`title` n'accepte que `blue-france` et `grey`. Pictogrammes en
pointer-only (l'art SVG relève du skill `generer-pictos-svg-dsfr`).

## generate_layout.py — gabarits (agencement structurel)

5 gabarits : `skeleton` (page HTML complète avec assets DSFR), `sidebar`,
`columns`, `card-grid`, `tile-grid`.

| Argument | Description |
|----------|-------------|
| `layout` | Nom du gabarit (ou `list`) |
| `--config` | Configuration JSON |
| `--output` | Fichier de sortie ; refuse d'écraser un fichier existant |
| `--list` | Lister les gabarits |

## generate_field.py — blocs fonctionnels (champs pré-construits officiels)

5 blocs : `civilite`, `nom-prenom`, `email`, `date-unique`, `societe`. Sourcés
des pages officielles `blocs-fonctionnels` (consultées le 2026-07-07, branche
1.14) puis confrontés le 2026-08-28 aux exemples rendus
`example/layout/pattern/*` du paquet 1.15.3 : structure (légendes,
`aria-labelledby`, groupes de messages), aides, `autocomplete` et `aria-live`
alignés ; validation différée (aucune contrainte native au repos). Seules
différences : l'ordre prénom puis nom par défaut (voir ci-dessous) et la taille
standard des radios de civilité.

| Argument | Description |
|----------|-------------|
| `field` | Nom du bloc (ou `list`) ; sans nom, l'aide sort sur stderr en code 2 |
| `--config` | Configuration JSON ; une clé inconnue est refusée par son nom (code 1) |
| `--output` | Fichier de sortie ; refuse d'écraser un fichier existant ; refusé avec `list` (code 2) |
| `--list` | Lister les blocs |

Note de source sur `nom-prenom` : défaut `order: "prenom-nom"` (convention
skill) ; l'ordre officiel 1.15.3 (nom d'abord) est disponible via
`--config '{"order":"nom-prenom"}'`.

## list_icons.py — icônes RI (énumération/validation au runtime)

Lit `dist/utility` au runtime (jamais d'embarquement en contexte). Résout le
paquet via `DSFR_OFFICIAL_PACKAGE_DIR` puis `DSFR_OFFICIAL_CACHE_DIR`.

| Option | Description |
|--------|-------------|
| (aucune) | Compte + catégories (défaut) |
| `--filter` | Icônes contenant le terme |
| `--validate NOM` | Exit 0 si `NOM` (ou `fr-icon-NOM`) est une icône officielle du paquet lu, 1 sinon, 2 si l'argument est vide ou de la forme Remix `ri-*` (non exposée par le paquet). |
| `--count` | Compte et catégories (comportement par défaut ; ignoré avec `--validate`, `--all` ou `--filter`) |
| `--all` | Liste complète (1044 classes en 1.15.3) |

La version affichée est celle du paquet réellement lu (`package.json`), pas la
cible `DSFR_OFFICIAL_VERSION`. `DSFR_OFFICIAL_PACKAGE_DIR` accepte `~` et
doit pointer vers un paquet extrait valide, sinon sortie 2.

## Scripts de vérification

| Script | Rôle |
|--------|------|
| `check_generated_outputs.py` | Contrats structurels (pages, racines composants, composants critiques) + invariants (ARIA, `href="#"`, contraintes au repos, IDs uniques, gestionnaires inline, markup équilibré) + page assemblée du builder ; `--official-version 1.15.3` valide toutes les classes émises (pages + bibliothèque + natifs + atomes + gabarits + builder) contre le paquet. Options : `--official-package <dossier>` (paquet extrait), `--official-version x.y.z` (cache `npm pack`), `--official-cache-dir <dossier>` (défaut `DSFR_OFFICIAL_CACHE_DIR` ou `~/.cache/dsfr-official-cache`), `--pages-only` et `--forms-only` (contrôles partiels : les sorties natives, atomes, gabarits et builder sont alors sautées) |
| `check_assembled_page_schema.py` | Validation JSON Schema du builder assemblé : schéma, `examples/assembled/*/page.json`, puis `generate_assembled_page.py --check` par exemple |
| `inventory_official_coverage.py` | Inventaire chiffré du paquet officiel : variables CSS, classes utilitaires, icônes, pictogrammes, composants et couverture locale. Options : `--official-package <dossier>` (ou `DSFR_OFFICIAL_PACKAGE_DIR`), `--official-version x.y.z` (cache `npm pack`), `--official-cache-dir`, `--format markdown\|json`, `--output <fichier>` (régénère le fichier : c'est le seul script qui écrase, l'inventaire versionné étant sa sortie) |
| `check_pictograms_doc.sh` | Chaque pictogramme (`famille/nom.svg`) et icône (`fr-icon-*`) cité par `references/pictograms.md` et `references/icons.md` existe dans le paquet officiel du cache ; SKIP explicite en code 2 sans paquet |
| `check_golden_outputs.py` | Régression golden byte-exacte de 21 sorties natives (header ×5, navigation ×3, footer ×3, card, alert, form, accordion, tabs, et les 5 blocs fonctionnels), baseline `evals/golden/*.html` ; `--update` régénère après validation de tous les cas |
| `check_header_navigation_playwright.js` | Comportement interactif JS (modales header, mega-menu, translate) en navigateur |
| `check_interactive_components_playwright.js` | Comportement interactif (accordion, onglets, modale, affichage) en navigateur |
| `check_generated_pages_playwright.js` | Ouverture des 12 pages générées avec les assets DSFR locaux, console propre, aucune contrainte au repos |
| `check_deferred_validation_playwright.js <page.html>` | Validation différée d'un formulaire généré : aucun état invalide avant soumission, erreurs exposées après, nettoyage au reset ; cible le formulaire de `<main>` |

`check_generated_outputs.py --official-version` est le garde-fou binaire de
fidélité : 0 classe `fr-*`/`ri-*` non officielle après chaque changement, dans
les sorties générées (pages, composants, natifs, atomes, gabarits, pages
assemblées) comme dans les blocs HTML des fiches `references/**/*.md`
(`reference_unknown_class`).
