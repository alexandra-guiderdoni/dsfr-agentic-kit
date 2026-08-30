# Sonde unitaire des noms accessibles

**Statut** : référence partagée minimale. **Dépôt source** : `https://github.com/bobdodd/carnforth`. **Source inspectée** : `chrome_plugin/js/content.js`, commit `206dc9641455e5d21f0db1c559e99660967209cc`.

Cette référence définit un catalogue de tests unitaires. Chaque `unit_id` correspond à une seule assertion observable ; la sonde doit produire un résultat séparé par élément DOM testé. Elle ne produit pas un verdict RGAA final.

## Sortie et périmètre

Champs minimaux : `tool`, `unit_id`, `target`, `rgaa_candidates`, `evidence_type`, `severity`, `selector`, `raw_dom`, `accessible_name`, `is_visible`, `inspection_limits`, `decision`. `fail` visible = preuve candidate forte ; `warn` = préqualification ; `pass` = absence de signal local ; `fail` masqué devient `warn` avec `is_visible:false`. Chaque `unit_id` doit avoir une fixture positive et négative.

Familles Carnforth couvertes : `img`, `svg[role=img]`, `[role=img]`, champs, radios, selects, `input[type=image]`, `fieldset`, `[role=group]`, formulaires, boutons, liens, `area[href]`, landmarks, dialogues, widgets ARIA, `progress`, `meter`, `iframe`, médias contrôlés et éléments focusables par `tabindex`. Les fonctions UI de surbrillance et de débogage sont hors verdict RGAA, mais justifient `selector` et `raw_dom`.

## Calcul du nom accessible

| ID | Cible | Assertion unitaire | RGAA candidats |
|---|---|---|---|
| NAME-01 | `fieldset` | Le premier `legend` non vide fournit le nom. | 11.5, 11.6 |
| NAME-02 | `aria-labelledby` | Les textes des IDs existants sont concaténés dans l'ordre. | 7.1, 11.1, 12.6 |
| NAME-03 | `aria-labelledby` | Un ID absent produit `aria_labelledby_broken`. | 7.1, 11.1, 12.6 |
| NAME-04 | `aria-label` | Une valeur vide produit `aria_label_empty`. | 7.1, 11.1, 12.6 |
| NAME-05 | `aria-label` | Une valeur blanche produit `aria_label_empty`. | 7.1, 11.1, 12.6 |
| NAME-06 | `aria-label` | Une valeur ponctuation seule produit `name_punctuation_only`. | 7.1, 11.2 |
| NAME-07 | `label[for]` | Un label explicite fournit le nom des contrôles associés. | 11.1, 11.2 |
| NAME-08 | `label` enveloppant | Un label enveloppant fournit un nom mais marque `_labelType=wrapped`. | 11.1, 11.2 |
| NAME-09 | `alt` | `alt` fournit le nom des `img` et `area`. | 1.1, 1.6 |
| NAME-10 | `value` | `value` fournit le nom des boutons `input`. | 11.9 |
| NAME-11 | `iframe[title]` | `title` fournit le nom d'un cadre. | 2.1 |
| NAME-12 | `[title]` | `title` seul produit `title_only_name`. | 7.1, 11.1, 12.6 |
| NAME-13 | `a img[alt]` | Le `alt` de l'image interne fournit le nom du lien. | 6.2, 1.1 |
| NAME-14 | texte visible | Le texte fournit le nom des rôles textuels prévus. | 6.2, 7.1, 11.9 |

## Heuristiques communes

| ID | Cible | Assertion unitaire | RGAA candidats |
|---|---|---|---|
| CORE-01 | élément masqué | Un échec visible est dégradé en avertissement si l'élément est masqué. | limite |
| CORE-02 | texte | Un nom de fichier est détecté. | 1.3, 6.1, 11.2 |
| CORE-03 | texte | Une URL est détectée. | 6.1, 11.2, 12.6 |
| CORE-04 | texte | Une chaîne ponctuation seule est détectée. | 1.3, 6.2, 11.2 |
| CORE-05 | texte | Un libellé générique de champ ou d'image est détecté. | 1.3, 11.2 |
| CORE-06 | texte | Un texte générique de bouton est détecté. | 11.9 |
| CORE-07 | texte | Un texte générique de lien est détecté. | 6.1 |
| CORE-08 | contenu | Un contenu uniquement `aria-hidden=true` est détecté. | 7.1 |

## Tests par famille

| ID | Cible | Assertion unitaire | RGAA candidats |
|---|---|---|---|
| IMG-01 | `img` décorative | Image décorative avec nom accessible. | 1.2 |
| IMG-02 | `img` informative | Nom absent. | 1.1 |
| IMG-03 | `img` informative | `alt` blanc. | 1.1 |
| IMG-04 | `img` informative | `alt` ponctuation seule. | 1.1, 1.3 |
| IMG-05 | `img` informative | `alt` nom de fichier. | 1.3 |
| IMG-06 | `img` informative | `alt` contenant du HTML. | 1.3 |
| IMG-07 | `img` informative | `alt` redondant avec "image". | 1.3 |
| IMG-08 | `img` informative | `alt` générique. | 1.3 |
| MAPIMG-01 | `img[usemap]` | Nom absent. | 1.1, 1.6 |
| MAPIMG-02 | `img[usemap]` | Nom vide. | 1.1, 1.6 |
| MAPIMG-03 | `img[usemap]` | Nom de fichier. | 1.3, 1.6 |
| MAPIMG-04 | `img[usemap]` | Nom ponctuation seule. | 1.3, 1.6 |
| MAPIMG-05 | `img[usemap]` | Nom très court. | 1.3, 1.6 |
| MAPIMG-06 | `img[usemap]` | Nom générique. | 1.3, 1.6 |
| SVG-01 | `svg[role=img]` décoratif | SVG décoratif avec nom accessible. | 1.2 |
| SVG-02 | `svg[role=img]` | Nom absent. | 1.1 |
| SVG-03 | `svg[role=img]` | Nom blanc. | 1.1 |
| SVG-04 | `svg[role=img]` | Nom ponctuation seule. | 1.1, 1.3 |
| SVG-05 | `svg[role=img]` | Nom contenant du HTML. | 1.3 |
| SVG-06 | `svg[role=img]` | Nom de fichier. | 1.3 |
| SVG-07 | `svg[role=img]` | Nom générique. | 1.3 |
| SVG-08 | `svg[role=img]` | `<title>` vide avec autre source de nom. | 1.3 |
| RIMG-01 | `[role=img]` non SVG | Nom absent. | 1.1, 7.1 |
| RIMG-02 | `[role=img]` non SVG | Nom blanc. | 1.1, 7.1 |
| RIMG-03 | `[role=img]` non SVG | Nom ponctuation seule. | 1.1, 1.3 |
| RIMG-04 | `[role=img]` non SVG | Nom contenant du HTML. | 1.3 |
| RIMG-05 | `[role=img]` non SVG | Nom de fichier. | 1.3 |
| RIMG-06 | `[role=img]` non SVG | Nom URL. | 1.3 |
| RIMG-07 | `[role=img]` non SVG | Nom redondant avec "image". | 1.3 |
| RIMG-08 | `[role=img]` non SVG | Nom générique. | 1.3 |
| CTRL-01 | champ | Nom absent. | 11.1 |
| CTRL-02 | `input[placeholder]` | Placeholder seul sans nom. | 11.1 |
| CTRL-03 | champ | Nom blanc. | 11.1 |
| CTRL-04 | champ | Nom ponctuation seule. | 11.1, 11.2 |
| CTRL-05 | champ | Nom générique. | 11.2 |
| CTRL-06 | champ | Nom de fichier. | 11.2 |
| CTRL-07 | champ | Nom URL. | 11.2 |
| CTRL-08 | champ | Nom issu du `title` seul. | 11.1 |
| CTRL-09 | champ | Label implicite enveloppant. | 11.1 |
| RADIO-01 | `input[type=radio]` | Radio hors `fieldset` et hors `[role=radiogroup]`. | 11.5, 11.6 |
| SELECT-01 | `select` | Première option vide. | 11.10 |
| SELECT-02 | `option` | Option composée uniquement de blancs. | 11.10 |
| IMAGEINPUT-01 | `input[type=image]` | `alt` absent. | 1.1, 11.9 |
| IMAGEINPUT-02 | `input[type=image]` | `alt` vide. | 1.1, 11.9 |
| IMAGEINPUT-03 | `input[type=image]` | `alt` blanc. | 1.1, 11.9 |
| IMAGEINPUT-04 | `input[type=image]` | `alt` ponctuation seule. | 1.1, 11.9 |
| IMAGEINPUT-05 | `input[type=image]` | `alt` nom de fichier. | 1.3, 11.9 |
| IMAGEINPUT-06 | `input[type=image]` | `alt` générique. | 1.3, 11.9 |
| FIELDSET-01 | `fieldset`, `[role=group]` | `legend` présent mais pas premier enfant. | 11.5, 11.6 |
| FIELDSET-02 | `fieldset`, `[role=group]` | `aria-labelledby` cassé. | 11.5, 11.6 |
| FIELDSET-03 | `fieldset`, `[role=group]` | `aria-labelledby` pointe vers un élément vide. | 11.5, 11.6 |
| FIELDSET-04 | `fieldset`, `[role=group]` | `legend` valide et ARIA redondant. | 11.6 |
| FIELDSET-05 | `fieldset`, `[role=group]` | `aria-label` vide. | 11.5, 11.6 |
| FIELDSET-06 | `fieldset`, `[role=group]` | `aria-label` ponctuation seule. | 11.5, 11.6 |
| FIELDSET-07 | `fieldset`, `[role=group]` | `legend` vide. | 11.5, 11.6 |
| FIELDSET-08 | `fieldset`, `[role=group]` | Nom absent. | 11.5, 11.6 |
| FIELDSET-09 | `fieldset`, `[role=group]` | Nom blanc. | 11.5, 11.6 |
| FIELDSET-10 | `fieldset`, `[role=group]` | Nom ponctuation seule. | 11.5, 11.6 |
| FIELDSET-11 | `fieldset`, `[role=group]` | Nom de fichier. | 11.6 |
| FIELDSET-12 | `fieldset`, `[role=group]` | Nom URL. | 11.6 |
| FIELDSET-13 | `fieldset`, `[role=group]` | Nom issu du `title` seul. | 11.6 |
| FORM-01 | `form`, `[role=form]` | `aria-labelledby` cassé. | 12.6 |
| FORM-02 | `form`, `[role=form]` | `aria-labelledby` pointe vers un élément vide. | 12.6 |
| FORM-03 | `form`, `[role=form]` | `aria-label` vide. | 12.6 |
| FORM-04 | `form`, `[role=form]` | `aria-label` ponctuation seule. | 12.6 |
| FORM-05 | `form`, `[role=form]` | Nom absent. | 12.6 |
| FORM-06 | `form`, `[role=form]` | Nom blanc. | 12.6 |
| FORM-07 | `form`, `[role=form]` | Nom ponctuation seule. | 12.6 |
| FORM-08 | `form`, `[role=form]` | Nom de fichier. | 12.6 |
| FORM-09 | `form`, `[role=form]` | Nom URL. | 12.6 |
| FORM-10 | `form`, `[role=form]` | Nom issu du `title` seul. | 12.6 |
| BUTTON-01 | bouton | `aria-labelledby` cassé. | 11.9, 7.1 |
| BUTTON-02 | bouton `input` | Attribut `value` absent. | 11.9 |
| BUTTON-03 | bouton | `aria-label` vide. | 11.9 |
| BUTTON-04 | bouton | `aria-label` ponctuation seule. | 11.9 |
| BUTTON-05 | bouton | Aucun texte et aucun nom ARIA. | 11.9 |
| BUTTON-06 | bouton | Nom absent. | 11.9 |
| BUTTON-07 | bouton | Nom blanc. | 11.9 |
| BUTTON-08 | bouton | Icône seule sans libellé descriptif. | 11.9 |
| BUTTON-09 | bouton | Texte générique. | 11.9 |
| LINK-01 | lien | `aria-labelledby` cassé. | 6.2, 7.1 |
| LINK-02 | lien avec image | Image interne sans `alt` exploitable. | 6.2, 1.1 |
| LINK-03 | lien | Nom absent. | 6.2 |
| LINK-04 | lien | Nom blanc. | 6.2 |
| LINK-05 | lien | Nom ponctuation seule. | 6.2 |
| LINK-06 | lien | Icône seule sans nom descriptif. | 6.2 |
| LINK-07 | lien | Texte générique. | 6.1 |
| LINK-08 | lien | URL comme texte de lien. | 6.1 |
| AREA-01 | `area[href]` | `aria-labelledby` cassé. | 1.6, 6.2 |
| AREA-02 | `area[href]` | Nom absent. | 1.6, 6.2 |
| AREA-03 | `area[href]` | Nom blanc. | 1.6, 6.2 |
| AREA-04 | `area[href]` | Nom ponctuation seule. | 1.6, 6.2 |
| AREA-05 | `area[href]` | Nom de fichier. | 1.6, 6.2 |
| AREA-06 | `area[href]` | Nom générique. | 1.6, 6.1 |
| AREA-07 | `area[href]` | Texte de lien générique. | 1.6, 6.1 |
| AREA-08 | `area[href]` | Nom issu du `title` seul. | 1.6, 6.2 |
| LANDMARK-01 | landmark unique `banner/main/contentinfo` | Nom absent accepté comme absence de signal. | 12.6 |
| LANDMARK-02 | `nav` unique | Nom absent. | 12.6 |
| LANDMARK-03 | `region` | Nom absent. | 12.6 |
| LANDMARK-04 | landmark répété | Nom absent. | 12.6 |
| LANDMARK-05 | landmark | Nom blanc. | 12.6 |
| LANDMARK-06 | landmark de formulaire | Nom ponctuation seule. | 12.6 |
| LANDMARK-07 | landmark de formulaire | Nom de fichier. | 12.6 |
| LANDMARK-08 | landmark de formulaire | Nom URL. | 12.6 |
| LANDMARK-09 | landmark | Nom issu du `title` seul. | 12.6 |
| DIALOG-01 | `[role=dialog]` | `aria-labelledby` cassé. | 7.1 |
| DIALOG-02 | `[role=dialog]` | Nom absent. | 7.1 |
| DIALOG-03 | `[role=dialog]` | Nom blanc. | 7.1 |
| DIALOG-04 | `[role=dialog]` | Nom ponctuation seule. | 7.1 |
| DIALOG-05 | `[role=dialog]` | `aria-label` identique à un titre visible. | 7.1 |
| WIDGET-01 | widget ARIA | `aria-labelledby` cassé. | 7.1 |
| WIDGET-02 | widget ARIA | Nom absent. | 7.1 |
| WIDGET-03 | widget ARIA | Nom blanc. | 7.1 |
| WIDGET-04 | widget ARIA | Nom ponctuation seule. | 7.1 |
| WIDGET-05 | `[role=tab]` | Contenu uniquement `aria-hidden=true` sans texte accessible. | 7.1 |
| WIDGET-06 | `[role=tabpanel]` | Référence vers élément sans nom. | 7.1 |
| WIDGET-07 | `[role=tabpanel]` | Référence vers élément au nom vide. | 7.1 |
| WIDGET-08 | `[role=tabpanel]` | Référence vers élément seulement `aria-hidden`. | 7.1 |
| PROGRESS-01 | `progress`, `[role=progressbar]` | `aria-labelledby` cassé. | 11.1, 7.1 |
| PROGRESS-02 | `progress`, `[role=progressbar]` | Nom absent. | 11.1, 7.1 |
| PROGRESS-03 | `progress`, `[role=progressbar]` | Nom blanc. | 11.1, 7.1 |
| PROGRESS-04 | `progress`, `[role=progressbar]` | Nom ponctuation seule. | 11.1, 7.1 |
| PROGRESS-05 | `progress`, `[role=progressbar]` | Nom générique. | 11.2, 7.1 |
| PROGRESS-06 | `progress`, `[role=progressbar]` | Nom issu du `title` seul. | 11.1, 7.1 |
| PROGRESS-07 | `progress`, `[role=progressbar]` | Label enveloppant. | 11.1, 7.1 |
| PROGRESS-08 | `progress`, `[role=progressbar]` | Collecte `value`, `max` et pourcentage. | preuve |
| METER-01 | `meter`, `[role=meter]` | `aria-labelledby` cassé. | 11.1, 7.1 |
| METER-02 | `meter`, `[role=meter]` | Nom absent. | 11.1, 7.1 |
| METER-03 | `meter`, `[role=meter]` | Nom blanc. | 11.1, 7.1 |
| METER-04 | `meter`, `[role=meter]` | Nom ponctuation seule. | 11.1, 7.1 |
| METER-05 | `meter`, `[role=meter]` | Nom générique. | 11.2, 7.1 |
| METER-06 | `meter`, `[role=meter]` | Nom issu du `title` seul. | 11.1, 7.1 |
| METER-07 | `meter`, `[role=meter]` | Label enveloppant. | 11.1, 7.1 |
| METER-08 | `meter`, `[role=meter]` | Collecte `value`, `min`, `max` et pourcentage. | preuve |
| IFRAME-01 | `iframe` | `aria-labelledby` cassé. | 2.1 |
| IFRAME-02 | `iframe` | Nom absent. | 2.1 |
| IFRAME-03 | `iframe` | Nom blanc. | 2.1 |
| IFRAME-04 | `iframe` | Nom ponctuation seule. | 2.1 |
| IFRAME-05 | `iframe` | `title` très court. | 2.2 |
| MEDIA-01 | `audio[controls]` | Nom absent. | 4.x |
| MEDIA-02 | `video[controls]` | Nom absent. | 4.x |
| MEDIA-03 | `[role=video]` | Nom absent. | 4.x |
| MEDIA-04 | média contrôlé | Nom blanc. | 4.x |
| TABINDEX-01 | `[tabindex]` | Élément natif interactif ignoré. | limite |
| TABINDEX-02 | `[tabindex]` | Conteneur textuel déjà nommé ignoré. | limite |
| TABINDEX-03 | `[tabindex]` | `aria-labelledby` cassé. | 7.1, 12.8 |
| TABINDEX-04 | `[tabindex]` | Nom absent. | 7.1, 12.8 |
| TABINDEX-05 | `[tabindex]` | Nom blanc. | 7.1, 12.8 |

## Garde-fous

Ne pas conclure à la pertinence RGAA depuis ces seules heuristiques, remplacer l'arbre d'accessibilité, axe-core, Playwright ou un test lecteur d'écran réel, ni promouvoir un verdict sans matrice AY11, `test_id`, limites d'inspection et validation humaine quand le sens du nom est en jeu.
