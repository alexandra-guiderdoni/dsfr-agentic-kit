# Page assemblée (generate_assembled_page.py)

Génère une page DSFR complète (head, header, skiplinks, main, footer) depuis une
description JSON de sections. Réutilise les fonctions de génération de
`generate_component.py` et la structure de page de `generate_page.py` : aucune
sortie n'est écrite à la main, et les garde-fous locaux vérifient la structure
produite. Cela ne remplace ni une relecture DSFR ciblée, ni un audit RGAA.

Usage :

```bash
python3 scripts/generate_assembled_page.py --config-file page.json --output page.html
python3 scripts/generate_assembled_page.py --config-file page.json --check
```

Schéma JSON publié : `schemas/generate_assembled_page.schema.json`.
Validation dédiée :

```bash
python3 scripts/check_assembled_page_schema.py
```

Les deux scripts (le builder comme la validation dédiée) valident la
configuration contre le schéma : ils utilisent `jsonschema>=4.22,<5` si le
paquet est installé, sinon se ré-exécutent sous `uv --with jsonschema`. Sans
`jsonschema` ni `uv`, le builder s'arrête avec une erreur nommée : le schéma
est une dépendance de fonctionnement, pas seulement de contrôle.

Les `columns` imbriquées sont limitées à 8 niveaux (la validation du schéma
croît avec la profondeur).

Exemples complets : `examples/assembled/`, au format
`brief.md -> page.json -> page.html -> preuve.md`. Le check global
`scripts/check_generated_outputs.py` valide aussi les `page.json` contre le
schéma et vérifie que chaque `page.html` versionné correspond à son `page.json`.

## Format d'entrée

Un objet JSON :

| Clé | Description |
| --- | --- |
| `title` | Titre de la page (`<title>` et sous-titre de service). |
| `description` | Balise `<meta name="description">` optionnelle. |
| `main_title` | Titre principal affiché si le builder doit ajouter automatiquement un `<h1>` ; défaut : `title`. |
| `auto_h1` | `true` par défaut. Ajoute un `<h1>` en début de `<main>` si aucune section `content` ne déclare `heading_level: 1`. Mettre `false` seulement si le `<h1>` est fourni autrement et vérifié. |
| `brand_mode` | `neutral` (défaut) ou `republique` (bloc marque Marianne, si droit d'usage). |
| `dark` | `true` pour le thème sombre. |
| `assets_prefix` | Préfixe d'URL des assets DSFR au lieu du CDN (offline). Exemple : `assets/dsfr` produit `assets/dsfr/dsfr.min.css` et `assets/dsfr/dsfr.module.min.js`. |
| `header` | En-tête riche optionnel, passé à `generate_header`. |
| `footer` | Pied de page optionnel, passé à `generate_footer`. |
| `sections` | Liste des sections (ordonnée) du `<main>`. |

Chaque section est un objet avec :

| Clé | Description |
| --- | --- |
| `block` | Type de section (voir ci-dessous). Obligatoire. |
| `id` | Identifiant stable sur le conteneur de section, utile pour navigation et sommaire. Si le block a déjà son propre `id`, utiliser `section_id`. |
| `section_id` | Identifiant explicite du conteneur de section, prioritaire sur `id` ; conservé tel quel s'il est un identifiant HTML valide (`^[A-Za-z][A-Za-z0-9_-]*$`), sinon normalisé. Exige `container: true` (l'ancre est posée sur le conteneur). |
| `heading` | Titre `<h2>` de section (optionnel). |
| `container` | `true` (défaut, sauf `notice`) pour envelopper dans `fr-container`. |
| `spacing` | Classes d'espacement DSFR du conteneur (défaut `fr-py-6w`) ; seules les classes `fr-*` sans caractère spécial sont acceptées. |
| autres | Props spécifiques au block. |

## Deux interfaces, deux contrats

Le builder assemblé et `generate_component.py` ne parlent pas la même langue,
et ne réagissent pas pareil à une entrée dangereuse. Un agent qui passe de
l'un à l'autre sans le savoir produit soit une erreur, soit un lien muet.

| | Builder assemblé (`page.json`) | `generate_component.py --config` |
|---|---|---|
| Alerte | `type`, `text` | `alert_type`, `description` |
| Carte / tuile | `desc` | `description` (carte), `desc` (tuile) |
| href ou src dangereux | **échoue** (exit 1, motif) : liste blanche du schéma, puis pré-validation de toutes les URL de la configuration avant le rendu | **neutralise** en `/`, sans message |

Le builder traduit vers les noms du générateur (`generate_assembled_page.py`,
`block_alert`, `block_cards`). Les clés de ce tableau sont celles du builder :
c'est lui que documente ce fichier. Pour un appel direct au générateur, lire
la signature de la fonction dans `generate_component.py`.

Conséquence sur la vérification : un `href="/"` dans une sortie de
`generate_component.py` peut être une neutralisation silencieuse. Vérifier
l'entrée, pas seulement la sortie.

## Blocks supportés

Les props principales de chaque block (toutes optionnelles sauf indication) ;

| Block | Props principales |
| --- | --- |
| `audit_report` | bloc structuré de rendu d’audit : `report_type`, `claim`, `sample_pages`, `metrics`, `links`, `root_causes`, `findings`, `filters` ; `sample_pages` place l’échantillon en tête avec URL et liens de détail ; tous les extraits de code sont échappés, aucun HTML brut accepté |
| `notice` | `title`, `description`, `variant` (info/warning/success/error), `link {label, href}`, `closable` |
| `callout` | `title`, `text`, `color` (ex. green-emeraude), `icon` |
| `alert` | `type` (info/success/warning/error), `title`, `text`, `closable` |
| `highlight` | `text`, `size` (sm/lead) |
| `cards` | `columns` (défaut 3, de 1 à 12 ; les largeurs sont réparties sur les 12 unités de la grille), `items [{title, desc, href, image}]` |
| `tiles` | `columns` (défaut 3), `items [{title, desc, href, orientation, image}]` |
| `accordion` | `items [{title, content}]`, avec `content` chaîne échappée ou contenu riche structuré ; `heading_level` (2 à 6, défaut 3) pour les titres de section |
| `tabs` | `tabs [{label, content, selected}]`, avec `content` chaîne échappée ou contenu riche structuré |
| `form` | `action`, `title`, `fields [...]` (voir « Champs du form »), `submit_label`, `reset_label`, `deferred`, `form_id` ou `id` |
| `stepper` | `current`, `total`, `title`, `next` |
| `badges` | `items [{label, variant, sm}]` |
| `tags` | `items [{label, href, sm}]` |
| `quote` | `text`, `author`, `source`, `cite`, `image` |
| `content` | `title`, `lead`, `body_text`, `body_structured`, `as_article`, `heading_level` (1 à 6, défaut 2) ; `body` (HTML brut) exige `allow_raw_html: true` |
| `summary` | `title`, `items [{label, href, children}]` |
| `buttons` | CTA : `items [{label, href?, variant, icon, size}]`, `align` (inline-md / right / center) |
| `breadcrumb` | Fil d'Ariane : `items [{label, href}]` |
| `columns` | Layout : `columns [{span?, blocks [...]}]` ; les sous-blocks ne sont pas des sections (`id`, `section_id`, `heading`, `container`, `spacing` refusés ; `id_prefix` accepté) |
| `image` | `src` (requis, chemin ou URL http/https), `alt` (requis ; une chaîne vide déclare une image décorative, `decorative: true` en est la forme explicite facultative), `caption`, `ratio` (ex. 16x9, images matricielles seulement) |
| `transcription` | `label`, `content` |
| `download` | `label`, `href`, `detail`, `items` |
| `share` | `title`, `items [{platform, label, href}]` |
| `follow` | `newsletter_title`, `newsletter_desc`, `newsletter_url` (lien d'abonnement ; sans lui, bouton officiel), `socials [{platform, label}]` (liste vide = aucun réseau) |
| `consent` | `site_name` |

Les props sont passées aux fonctions de `generate_component.py` ; un paramètre
invalide renvoie une erreur (exit 1). Les couleurs d'accent et les variantes
suivent la palette Marianne officielle (cf. `references/components.md`).

## Assets locaux et Marianne

Par défaut, les pages générées pointent vers le CDN DSFR 1.15.3. Pour une page
locale ou partageable sans CDN DSFR, fournir `assets_prefix`, par exemple
`"assets_prefix": "assets/dsfr"`, puis servir le paquet DSFR extrait au même
emplacement que la page. Ce mode charge aussi les polices locales du paquet
DSFR. Il ne prouve pas à lui seul le droit d'usage du bloc marque Marianne :
`brand_mode: "republique"` reste réservé aux cas où ce droit est établi.

## Images et SVG

Le block `image` applique `fr-responsive-img`. Le champ `ratio` contraint
l'affichage et doit rester réservé aux images matricielles dont le cadrage est
maîtrisé. Le builder refuse `ratio` quand `src` pointe vers un fichier `.svg`,
car un schéma SVG doit conserver sa géométrie naturelle et ne pas être rogné par
un ratio de présentation.

## Contenu riche structuré

Les blocs `accordion` et `tabs` échappent toujours les chaînes simples. Pour
insérer des listes et des liens sans HTML brut, passer un objet `content`
structuré :

```json
{
  "paragraphs": ["Texte introductif."],
  "list": ["Point clé", {"label": "Source", "href": "/source"}],
  "links": [{"label": "Documentation", "href": "/doc", "target": "_blank"}]
}
```

Variante plus fine :

```json
{
  "blocks": [
    {"type": "paragraph", "text": "Texte échappé."},
    {"type": "list", "items": ["A", "B"]},
    {"type": "links", "items": [{"label": "Source", "href": "/source"}]}
  ]
}
```

Les labels et textes sont échappés. Les liens `target="_blank"` reçoivent
`rel="noopener"`.

Le bloc `content` accepte aussi `body_structured` avec le même format. Si
`body_structured` est présent, il remplace `body` et évite d'insérer du HTML
brut pour les contenus éditoriaux simples ou moyens. Pour un paragraphe simple
sans HTML brut, utiliser `body_text` : le texte est échappé et rendu dans un
paragraphe.

`body` reste disponible pour du HTML éditorial maîtrisé, à condition de
déclarer `allow_raw_html: true` sur la section : sans cette clé, le builder
refuse la configuration et propose `body_text` ou `body_structured`. Le HTML
brut est inséré sans vérification (un avertissement est émis sur stderr) : ne
pas y passer de contenu utilisateur, de sortie LLM non relue ou de source non
fiable.

La page porte un seul `h1` : si aucune section n'en déclare (`content`,
`callout` ou `alert` avec `heading_level: 1`, ou un `heading` de niveau 1 dans
`body_structured`), le builder l'ajoute depuis `title` (désactivable par
`auto_h1: false`) ; un second `h1` est refusé.

## Champs du block `form`

La liste `fields` accepte des objets avec un `type` :

| Type | Description / props |
| --- | --- |
| `field` | Bloc fonctionnel officiel (`generate_field`) : `name` parmi `civilite`, `nom-prenom`, `email`, `date-unique`, `societe` ; `config` = kwargs du bloc (ex. `{"legend": "..."}`) ; sans `config.id`, un identifiant unique est dérivé du formulaire, deux blocs de même nom peuvent donc coexister. |
| `input` | Champ simple : `label`, `input_type` (text/email/tel/number/date…), `required`, `id`, `name` (défaut : identifiant technique), `hint`, `error`. |
| `select` | Liste déroulante : `label`, `options [{value, label}]`, `id`, `hint`, `name`. |
| `textarea` | Zone de texte : `label`, `id`, `rows`, `hint`, `name`. |
| `checkbox` | Case à cocher : `label`, `required`, `id`, `name`. |
| `radio` | Groupe de radios : `legend`, `items [{label, value}]`, `inline`, `name`, `id`. |

Avec `deferred: true` et des champs `input`/`checkbox` portant `required: true`,
la validation différée du skill est ajoutée (contraintes posées au premier
`submit`, aucune au repos). Les blocs fonctionnels et `select`/`radio` ne sont
pas marqués automatiquement (validation spécifique à gérer en personnalisation).

## Layout : block `columns`

Le block `columns` organise des sous-sections en colonnes (grille DSFR). Chaque
colonne est un objet `{span?, blocks: [...]}` (ou une liste de blocks). `span`
est la largeur sur 12 (défaut : équiréparti). Les sous-blocks utilisent les
mêmes blocks que les sections.

Le builder refuse maintenant les valeurs de grille impossibles : `columns` et
`span` doivent être des entiers entre 1 et 12.

```json
{"block": "columns", "columns": [
  {"span": 4, "blocks": [{"block": "callout", "title": "À gauche", "text": "..."}]},
  {"span": 8, "blocks": [{"block": "badges", "items": [{"label": "A"}, {"label": "B"}]}]}
]}
```

## Header riche (option)

Par défaut, le header est `neutral` (ou `republique` si `brand_mode`). Pour un
header riche (liens d'outils, recherche, navigation), ajouter une clé `header`
au config ; ses props sont passées à `gc.generate_header` :

```json
{
  "title": "Mon service",
  "header": {
    "brand_mode": "republique",
    "service_title": "Mon service",
    "tools": [{"label": "Se connecter", "href": "/connexion"}],
    "search": {"label": "Rechercher"},
    "navigation": [{"label": "Accueil", "href": "/", "active": true}, {"label": "Démarches", "href": "/demarches"}]
  },
  "sections": [...]
}
```

## Vérification sèche

`--check` génère la page en mémoire, sans écrire de fichier, puis vérifie les
garde-fous rapides du builder :

- IDs dupliqués ;
- liens `href="#"` ;
- ancres locales sans cible (`href="#section"` sans `id="section"`) ;
- références ARIA sans cible (`aria-controls`, `aria-labelledby`, `aria-describedby`) ;
- présence d'au moins un `<h1>` dans `<main>` hors modale ;
- gestionnaires d'événement inline.

La génération normale applique les mêmes contrôles avant écriture. Les liens
d'évitement automatiques sont ajustés au HTML final : si un header personnalisé
n'expose pas de navigation, le lien d'évitement `Menu` n'est pas émis.

## Footer riche (option)

Par défaut, le footer vient de `generate_page.py`. Pour personnaliser le nom de
service, la description, les liens de contenu ou les liens bas de page sans
post-traiter le HTML, ajouter une clé `footer` :

```json
{
  "footer": {
    "brand_mode": "neutral",
    "service_name": "Mon service",
    "content_desc": "Prototype local à vérifier avant publication.",
    "content_links": [
      {"label": "Documentation", "href": "/documentation"}
    ],
    "bottom_links": [
      {"label": "Plan du site", "href": "/plan-du-site"},
      {"label": "Accessibilité : à vérifier", "href": "/accessibilite"}
    ]
  }
}
```

Si `content_links` est absent, les liens institutionnels par défaut du
générateur de footer sont conservés. Si `content_links` vaut `[]`, aucun lien de
contenu n'est émis.

## Exemple

```json
{
  "title": "Rendez-vous public - Prise de rendez-vous en ligne",
  "description": "Prototype de prise de rendez-vous en ligne.",
  "brand_mode": "republique",
  "sections": [
    {"block": "content", "id": "intro", "title": "Rendez-vous public", "heading_level": 1, "lead": "Prise de rendez-vous en ligne", "body_structured": {"paragraphs": ["Choisissez votre créneau."]}},
    {"block": "notice", "title": "Nouveau service", "description": "RDV 100% en ligne.", "variant": "info"},
    {"block": "callout", "title": "Finis les files d'attente.", "text": "Choisissez votre créneau.", "color": "green-emeraude"},
    {"block": "badges", "items": [{"label": "En ligne", "variant": "success"}, {"label": "Gratuit", "variant": "info"}]},
    {"block": "tags", "items": [{"label": "Passeport", "href": "/passeport"}, {"label": "Carte d'identité", "href": "/cni"}]},
    {"block": "stepper", "current": 2, "total": 4, "title": "Choisissez votre créneau", "next": "Confirmer"},
    {"block": "cards", "heading": "Démarches demandées", "columns": 3, "items": [
      {"title": "Passeport", "desc": "Demande ou renouvellement.", "href": "/passeport"},
      {"title": "Carte d'identité", "desc": "Renouvellement.", "href": "/cni"},
      {"title": "Permis", "desc": "Échange ou perte.", "href": "/permis"}
    ]},
    {"block": "tiles", "columns": 3, "items": [
      {"title": "Mes rendez-vous", "desc": "Gérez vos RDV.", "href": "/rdv"},
      {"title": "Annuler", "desc": "Annulez un créneau.", "href": "/annuler"},
      {"title": "Aide", "desc": "Une question ?", "href": "/aide"}
    ]},
    {"block": "accordion", "heading": "Questions fréquentes", "items": [
      {"title": "Quels documents ?", "content": {"paragraphs": ["La liste vous est envoyée par e-mail."], "links": [{"label": "Voir la liste", "href": "/documents"}]}},
      {"title": "Puis-je annuler ?", "content": "Oui, à tout moment, sans frais."}
    ]},
    {"block": "highlight", "text": "Délai moyen : 9 jours, en baisse de 30 %."},
    {"block": "alert", "type": "success", "title": "Confirmation", "text": "Demande envoyée."},
    {"block": "quote", "text": "Service rapide et clair.", "author": "Camille D., Lyon", "source": "Avis vérifié"}
  ]
}
```

## Limites

- Le `<main>` est assemblé à partir des blocks ; pour un contenu très spécifique
  (markup non couvert par un block), compléter en personnalisation ou étendre la
  liste des blocks.
- Le header et le footer sont configurables, mais les liens, mentions légales,
  données personnelles, cookies et claims de publication restent à vérifier
  avant mise en ligne.
- Les invariants (pas de `href="#"`, cibles ARIA résolues, pas de contrainte au
  repos) sont garantis par les fonctions réutilisées ; vérifier tout de même
  après personnalisation avec `references/prompt-conformite-dsfr.md`.
- Le `<h1>` peut être ajouté automatiquement, mais le titre final doit rester
  relu : il ne prouve pas la qualité éditoriale ni l'ordre complet des titres.
- Si `auto_h1` vaut `false`, le builder exige tout de même un `<h1>` hors
  modale dans `<main>`.
