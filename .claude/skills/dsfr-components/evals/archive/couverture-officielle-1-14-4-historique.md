# Couverture officielle DSFR 1.14.4 — gap exhaustif et plan

> Instantané conservé tel quel. Le pack cible 1.15.2 depuis le 2026-08-28 ; ce
> document atteste l'état 1.14.4 et n'a pas été rejoué. La borne vaut aussi
> pour les chiffres du skill lui-même (nombre d'atomes, de gabarits, de cas
> golden, de types de page) : ils datent de la session décrite et ont augmenté
> depuis. Le périmètre qu'il sert à établir, 46 composants officiels sur 46, a
> été revérifié contre 1.15.2 le 2026-08-28 : le catalogue officiel compte 46
> composants dans les deux versions, sans ajout ni retrait. Pour tout chiffre à
> jour, lire `official-coverage-inventory.md` et `local-validation.md`, jamais
> ce document.

> Dernière vérification exécutée le 2026-08-22 :
> `check_generated_outputs.py --official-version 1.14.4` → PASS pages=12
> components=136. La preuve est cette commande, rejouable ; aucun identifiant
> de commit n'est cité, l'historique du dépôt amont du pack n'étant pas
> résoluble depuis les dépôts où ce skill est publié.

Date de consultation des sources officielles : 2026-07-07.

## Méthode

- Liste autoritaire des composants officiels : énumération des dossiers
  `dist/component/*` du paquet `@gouvfr/dsfr@1.14.4`, via l'API jsDelivr
  (`data.jsdelivr.com/v1/packages/npm/@gouvfr/dsfr@1.14.4?structure=flat`).
- Croisement avec la propre machinerie du skill :
  `python3 scripts/check_generated_outputs.py --official-version 1.14.4`.
- Comparaison markup pour la sonde de fidélité : page officielle « Code de
  l'Interrupteur » (récupérée via synthèse de recherche web, à confirmer par
  fetch direct lors de l'implémentation).

## Verdict global

Couverture déjà exhaustive des composants officiels. Preuve :
`check_generated_outputs.py --official-version 1.14.4` retourne
`PASS (exit 0)`, soit zéro `missing_local_component` et zéro
`unknown_official_component` (hors helpers locaux exemptés `button_group` et
`back_to_top`).

## Faits vs jugements

### Fait 1 — Couverture exhaustive (vérifié)

Les 46 dossiers `dist/component/*` officiels sont tous présents dans la
bibliothèque locale (48 entrées), après normalisation des alias
`skiplinks → skiplink` et `tabs → tab`.

### Fait 2 — Les deux composants cités comme « manquants » ne sont pas des composants officiels (vérifié)

Ni `plan-du-site`/`sitemap`, ni `toggle-group` n'existent comme dossier
`dist/component/*` dans `@gouvfr/dsfr@1.14.4`.

### Fait 3 — Le bug `--list` « 4 natifs au lieu de 7 » ne se reproduit pas (vérifié)

`generate_component.py --list` affiche bien les 7 natifs. Le décompte « 4 »
ne reproduit pas sur le code courant.

### Jugement 1 — Réinterprétation charitable de « toggle-group »

« toggle-group » correspond vraisemblablement au **groupement
d'interrupteurs** officiel, conteneur `fr-toggle__list`, lui-même une variante
réelle du composant `toggle`. L'entrée `toggle` de la bibliothèque ne couvre
que `basic`, `with_hint`, `bordered` : la variante groupée est absente. C'est
un ajout ciblé dans le catalogue, à prouver contre les exemples officiels.

### Jugement 2 — Réinterprétation charitable de « sitemap/plan-du-site »

« plan-du-site » n'est ni un composant ni un modèle DSFR. C'est un type de
page (footer obligatoire), donc un candidat pour `generate_page.py`
(`PAGE_TYPES`), pas pour `generate_component.py`.

### Jugement 3 — Fragilité latente `--list` (vrai défaut de maintenance)

`list_components` durcit une liste `native` séparée du dict
`NATIVE_COMPONENTS`. Elles peuvent diverger à la prochaine nativisation.
Correction : dériver la liste affichée depuis `NATIVE_COMPONENTS`.

### Jugement 4 — Dérive de fidélité du markup `toggle` (plausible, à confirmer par fetch direct)

Sonde contre la page officielle : le markup `toggle` local omet les attributs
d'état `data-fr-checked-label` / `data-fr-unchecked-label` et place le hint
dans le label (`<span class="fr-hint-text">`), alors que l'officiel lie
l'input au hint via `aria-describedby` vers un `<p class="fr-hint-text">`
extérieur. À confirmer par fetch direct de la page de code avant correction.

## Gap exhaustif (officiel vs local)

> Avertissement : la colonne « Natif `--config` » ci-dessous décrit l'état
> *avant* les incréments B1 à B4 décrits plus bas dans ce même document. Les
> « non » qu'elle porte ne valent plus : la section Avancement conclut
> « 46/46 composants officiels nativement paramétrables ». Ne pas lire ce
> tableau isolément.

| Composant officiel (`dist/component`) | Présent localement | Natif `--config` | Note |
| --- | :---: | :---: | --- |
| accordion | oui | oui | — |
| alert | oui | oui | — |
| badge | oui | non | candidat nativisation |
| breadcrumb | oui | oui | — |
| button | oui | oui | — |
| callout | oui | non | candidat nativisation |
| card | oui | oui | — |
| checkbox | oui | non | candidat nativisation |
| connect | oui | non | — |
| consent | oui | non | — |
| content | oui | non | — |
| display | oui | non | — |
| download | oui | non | — |
| follow | oui | non | — |
| footer | oui | non | — |
| form | oui | non | — |
| header | oui | non | — |
| highlight | oui | non | candidat nativisation |
| input | oui | oui | — |
| link | oui | non | candidat nativisation |
| logo | oui | non | — |
| modal | oui | oui | — |
| navigation | oui | non | — |
| notice | oui | non | candidat nativisation |
| pagination | oui | non | candidat nativisation |
| password | oui | non | — |
| quote | oui | non | candidat nativisation |
| radio | oui | non | candidat nativisation |
| range | oui | non | candidat nativisation |
| search | oui | non | candidat nativisation |
| segmented | oui | non | candidat nativisation |
| select | oui | non | candidat nativisation |
| share | oui | non | — |
| sidemenu | oui | non | — |
| skiplink | oui (clé `skiplinks`) | non | alias |
| stepper | oui | non | candidat nativisation |
| summary | oui | non | — |
| tab | oui (clé `tabs`) | non | alias |
| table | oui | non | — |
| tag | oui | non | candidat nativisation |
| tile | oui | non | candidat nativisation |
| toggle | oui | non | variante groupée manquante + dérive markup |
| tooltip | oui | non | candidat nativisation |
| transcription | oui | non | — |
| translate | oui | non | — |
| upload | oui | non | candidat nativisation |

Helpers locaux (hors catalogue officiel, exemptés) : `back_to_top`,
`button_group`.

Composants cités absents du catalogue officiel : `plan-du-site`/`sitemap`
(type de page), `toggle-group` (variante de `toggle`, pas un composant).

## Plan priorisé (pivote la mission initiale)

La mission visait « ajouter les composants manquants + étendre la génération
native ». Le gap réel recentre sur trois axes, tous alignés avec l'objectif
explicite de fidélité et de nativisation.

### Axe A — Markup officiel 1.14.4

A1. Fetch direct de la page officielle « Code de l'Interrupteur », confirmer
    la dérive `toggle`, corriger le markup (attributs d'état + hint
    `aria-describedby`), ajouter la variante groupée `fr-toggle__list`.
    Réversible, test `check_generated_outputs.py` après.
A2. Audit fidélité ciblé sur les entrées à risque visuel repérées : `notice`
    (emoji d'avertissement dans le titre, contrevient à la règle anti-emoji), `follow`
    (classes `fr-btn--twitter`/`fr-btn--linkedin` à vérifier contre 1.14.4),
    `tooltip` (structure non standard). Un par un, fetch officiel, correction.

### Axe B — Nativisation paramétrable (objectif explicite de la mission)

Étendre `NATIVE_COMPONENTS` composant par composant, réversible, test après
chacun. Priorisation par ratio valeur/effort :

Priorité 1 (simple, forte valeur, usage courant) :
- `badge`, `tag`, `callout`, `highlight`, `notice`, `link`.

Priorité 2 (champs de formulaire, cohérent avec la branche formulaire) :
- `select`, `checkbox`, `radio`, `toggle`, `search`, `range`, `upload`.

Priorité 3 (navigation/structure) :
- `stepper`, `pagination`, `tile`, `quote`, `tooltip`, `segmented`.

Chaque nativisation : fonction Python paramétrable + entrée dans
`NATIVE_COMPONENTS` + test `--config` réel inspecté au niveau des classes
`fr-*` et d'ARIA + `check_generated_outputs.py` PASS.

### Axe C — Correction du défaut de maintenance `--list`

C1. `list_components` dérive la liste native de `NATIVE_COMPONENTS` au lieu
    de la durcir, évitant toute divergence à la prochaine nativisation.

### Bornes préservées

- Les 7 natifs actuels (button, alert, accordion, card, modal, input,
  breadcrumb) et le contrat `SKILL.md` (frontmatter, `context: fork`,
  `allowed-tools`, `argument-hint`) intacts.
- 1.14.4 figé.
- `check_generated_outputs.py` reste PASS après chaque modification.
- Aucun composant inventé hors catalogue officiel.
- Français, kebab-case, pas d'emoji, capitalisation française des titres.

## Avancement (session 2026-07-07)

Direction choisie : pivot accepté + `sitemap` comme type de page. Ordre :
markup toggle d'abord.

- A1 réévalué le 8 juillet 2026, corrigé mais fidélité de markup non
  revérifiée par comparaison directe : le fetch direct de la page officielle
  « Code de l'Interrupteur » exigé par l'axe A1 n'a pas été exécuté, et le
  contrôle cité en preuve (`check_generated_outputs.py`) ne compare aucune
  structure produite à un exemple officiel — il vérifie la présence des
  dossiers `dist/component`, les échelles de couleur utilitaires et
  l'appartenance des classes émises au CSS officiel. Markup `toggle` corrigé
  dans le natif et la
  bibliothèque JSON avec `fr-messages-group`, `aria-live="polite"` et
  `aria-describedby` résolu ; variante groupée enveloppée dans
  `fieldset.fr-fieldset`, `legend.fr-fieldset__legend`,
  `fr-fieldset__element` et `fr-toggle__list`. Preuve :
  `check_generated_outputs.py --official-version 1.14.4` → `PASS generated
  outputs: pages=12 components=136`.
- Type de page `sitemap` fait et vérifié : `generate_page.py` + `PAGE_TYPES` +
  `SKILL.md`. `check` pages 10 → 11.
- B1 fait et vérifié : nativisation de badge, tag, callout, highlight, notice,
  link. 13 natifs au total.
- C fait et vérifié : `list_components` dérive de `NATIVE_COMPONENTS` ;
  `--list` affiche 13 natifs au lieu de 7 ; comptes dynamiques dans la
  docstring et la description argparse.
- B2 fait et vérifié : nativisation de select, checkbox, radio, toggle,
  search, range, upload. Bug `esc(0)` corrigé (`min="0"` du range). 20 natifs.
- B3 fait et vérifié : nativisation de stepper, pagination, tile, quote,
  tooltip, segmented. 26 natifs au total (sur 48 entrées bibliothèque).
- A2 réévalué le 8 juillet 2026 : `notice` accepte `description`/`desc` et
  `link` (`fr-notice__desc`, `fr-notice__link`) ; `tooltip` émet le bouton
  avant le `<span role="tooltip">`, avec `type="button"` et sans
  `aria-hidden` statique ; `follow` émet l'abonnement en
  `<button type="button">` et utilise `fr-btn--twitter-x` avec le libellé
  « X (anciennement Twitter) ». Preuve : mêmes checks que A1, plus génération
  ciblée des quatre composants inspectée.
- B4 fait et vérifié : nativisation des 20 restants (logo, connect, download,
  content, summary, share, translate, transcription, password, table, tabs,
  skiplinks, sidemenu, navigation, header, footer, form, follow, consent,
  display). **46/46 composants officiels nativement paramétrables.** Normalisation
  des alias `tab`/`skiplink` (singulier canonique) dans le dispatch natif.
- Reste : couche « atomes / molécules / gabarits + grille / colonnage /
  espacements » (refonte structurelle du modèle de génération, architecture à
  valider).
- Atomes et gabarits faits et vérifiés : `generate_atom.py` (9 atomes à cette étape, 11 aujourd'hui) et
  `generate_layout.py` (5 gabarits). Toutes les classes `fr-*` vérifiées
  officielles 1.14.4.
- P1 du PRD-140 fait et vérifié : `generate_field.py` génère les 5 blocs
  fonctionnels officiels (civilité, nom-prenom, email, date-unique, societe),
  sourcés page par page depuis `blocs-fonctionnels` 1.14.4. Validation différée
  respectée (zéro contrainte au repos), cibles ARIA résolues, classes
  officielles 1.14.4 (dont `fr-fieldset__element--year/number/inline-grow`,
  `fr-mt-n1v`, `fr-messages-group`). Conflit d'ordre nom/prénom tranché en
  faveur de prénom-puis-nom (convention skill), `order` configurable.
  `SKILL.md` v2.4.0, `evals/local-validation.md`
  mis à jour. `check_generated_outputs.py` PASS local + officiel.
- P2 du PRD-140 fait et vérifié (incrément outillage + 3 composants) :
  - Harnais golden `check_golden_outputs.py` + `evals/golden/*.html` (9 cas)
    protégeant les sorties natives header/navigation/footer, inexistantes dans
    le check précédent (qui n'exerçait que les variantes JSON). Baseline des
    sorties minimales inchangé après chaque variante (preuve de non-régression).
  - Header : variantes `tools` (liens d'accès rapide) et `languages`
    (fr-translate), sourcées de `header-tools.ejs` / `translate.ejs`.
  - Navigation : variante `categories` (mega-menu `fr-collapse fr-mega-menu` +
    catégories `fr-col-lg-3`) et `align: right`, sourcées de
    `navigation-mega-menu.ejs`.
  - Footer : variantes `partners` (logos) et `bottom_links`/`copyright`,
    sourcées de `footer-partners.ejs` / `footer-bottom.ejs`.
  - Reporté (changement structurel large, incrément dédié) : barre de recherche
    et menu modale du header (navbar + brand-top + modales).
  - Header riche fait et vérifié (incrément dédié) : variantes opt-in `search`
    (fr-header__navbar bouton fr-btn--search + fr-header__search fr-modal +
    fr-search-bar) et `navigation` (fr-btn--menu + fr-header__menu fr-modal
    contenant la navigation), avec brand-top + navbar émis seulement quand
    search ou navigation est fourni. Sourcé des templates ejs 1.14.4 et du
    header de `generate_page.py` (référence locale validée). Étape 0 : confirmé
    que `generate_page.py` a son propre header -> pages non impactées.
    `SKILL.md` v2.6.0. Cas golden `header-with-search` / `header-with-menu`
    ajoutés (baseline header-default/republique inchangé).
  - `SKILL.md` v2.5.0, `evals/local-validation.md` mis à jour.
    `check_generated_outputs.py` PASS local + `--official-version 1.14.4` ;
    `check_golden_outputs.py` PASS 11 cas ; classes des variantes vérifiées
    dans `dsfr.min.css`.
- Vérification JS interactive faite et vérifiée : nouveau
  `check_header_navigation_playwright.js` joue les vrais fragments (header
  search/menu/translate, navigation menu/mega-menu) en navigateur Chromium,
  avec viewport mobile (navbar) + desktop (tools/nav). `PASS` : modales
  search/menu ouvrent (`fr-modal--opened`) puis ferment au Fermer,
  translate/menu/mega `aria-expanded` false→true, collapses
  `fr-collapse--expanded`, 0 erreur console. Le statut « non vérifié » sur le
  comportement interactif est levé pour ces éléments (la barre de recherche et
  le menu modale étaient les seuls non couverts par le check interactif
  existant).
- P3 fait et vérifié :
  - Atom `pictogram` (pointer-only) dans `generate_atom.py` (10 atomes à cette étape, 11 aujourd'hui) :
    wrapper `<svg class="fr-artwork">` + 3 calques `<use>` pointant vers
    l'asset officiel ; jamais de SVG art inline (rôle du skill séparé
    `generer-pictos-svg-dsfr`). Classes `fr-artwork*` vérifiées dans
    `dsfr.min.css`.
  - `references/analytics.md` : intégration (ordre des scripts + dépendances),
    objet de configuration, et 9 attributs `data-fr-analytics-*`
    (click, dblclick, action, change, download, external, internal, rating,
    page-total) sourcés du paquet (`dist/analytics/README.md`,
    `example/config.ejs`, `example/attribute/index.ejs`). API JS pointée vers
    `api.js` du paquet (non énumérée par cœur).
  - `SKILL.md` v2.7.0 (atome pictogram + CONTEXT-POINTERS mesure d'audience).
    `check_generated_outputs.py` PASS local + `--official-version 1.14.4` ;
    `check_golden_outputs.py` PASS 11 cas. PRD-140 : P1.1 (blocs fonctionnels),
    P1.3 (utilitaires couleur — scope réduit : 7 catégories absentes du paquet),
    P1.4 (tokens + table strate×artefact), P2.5 (variantes riches + header
    search/menu), P3.7 (pictogrammes), P3.8 (analytics) sont livrés.
    **Restent** : P1.2 (page `account`), P2.6 (`icon-list`).
- P1.2 + P2.6 faits et vérifiés (clôture du PRD-140) : page `account`
  (FranceConnect + form prénom-puis-nom/email/new-password, validation
  différée ; `check` pages 11→12) + `scripts/list_icons.py` (énumère/valide au
  runtime les 1042 icônes `fr-icon-*`, 18 catégories, sans embarquement en
  contexte). **PRD-140 : couverture complète 8/8 axes.**
