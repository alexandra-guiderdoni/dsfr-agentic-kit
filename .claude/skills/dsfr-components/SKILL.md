---
name: dsfr-components
version: 2.8.0
description: "Utiliser quand la demande explicite vise une page HTML statique DSFR, un fragment ou composant DSFR à insérer, ou une vérification DSFR ponctuelle d'un HTML local ; exclut applications front-end et audits RGAA complets."
allowed-tools: ["Bash", "Read", "Write", "Glob", "Edit", "WebFetch"]
context: fork
background: false
argument-hint: "[page: standard|landing|form|dashboard|error|login|account|search|confirmation|list|detail|sitemap --title titre --output fichier.html --dark --brand-mode neutral|republique] | [component nom --variant variante|--config JSON --output fragment.html] | [field civilite|nom-prenom|email|date-unique|societe --config JSON --output fragment.html] | [audit-dsfr html-ou-composant]"
---

# Composants DSFR

Générer du HTML statique aligné avec le Design System de l'État français, avec
les scripts et références du skill. Le livrable doit rester accessible, en
français et proche des conventions DSFR, sans revendiquer une conformité sans
preuve dédiée.

## Déclencheurs

- Demande explicite de page HTML statique DSFR.
- Demande explicite de fragment ou composant DSFR à insérer dans un `<main>`.
- Vérification ponctuelle DSFR d'un HTML généré ou d'un composant local.
- Besoin DSFR explicite dans la demande courante ; un contexte service public,
  `.gouv` ou administratif ne suffit pas seul.

## Smoke prompts de déclenchement

La fiche complète vit dans `evals/model-trigger-smoke.md`. Cette table reste le
pointeur chargé en contexte.

| Prompt sans nommer le skill | Attendu |
| --- | --- |
| « Crée une page HTML statique DSFR pour une demande de rendez-vous administratif. » | Utiliser ce skill, charger le profil DSFR partagé, générer une page `form`. |
| « J'ai besoin d'un composant accordéon DSFR à intégrer dans une page service public. » | Utiliser ce skill, lire seulement la section accordéons, produire un fragment. |
| « Vérifie si ce HTML généré respecte les composants DSFR utilisés. » | Utiliser la branche audit DSFR ponctuel, appliquer `references/prompt-conformite-dsfr.md`, produire un statut borné. |
| « Audite la conformité RGAA complète de ce site existant. » | Ne pas générer de page ; router vers `audit-rgaa-dsfr` ou `audit-accessibilite-web`. |
| « Crée une page HTML pour un service public de prise de rendez-vous. » | Ne pas déclencher ce skill sans demande DSFR explicite ; demander si DSFR est requis. |

## Quand NE PAS utiliser

- Ne pas utiliser pour une application React, Vue ou Angular.
- Ne pas utiliser pour modifier le DSFR lui-même.
- Ne pas utiliser seul pour un audit RGAA complet, une publication ou une
  certification.
- Ne jamais écraser un fichier de sortie existant ; choisir un autre chemin ou
  demander une suppression explicite hors script.
- Ne jamais inventer un composant DSFR si un équivalent officiel existe.
- Ne jamais masquer qu'un fallback manuel a été utilisé.
- Ne jamais revendiquer `conforme DSFR`, `conforme RGAA` ou `prêt pour
  publication` sans preuve dédiée.

## Types et arguments

| Argument | Défaut | Effet |
| --- | --- | --- |
| `type` | `standard` | type de page pour `generate_page.py` |
| `component` | aucun | composant isolé pour `generate_component.py` |
| `field` | aucun | bloc fonctionnel isolé (civilité, nom-prenom, email, date-unique, societe) pour `generate_field.py` |
| `--title` | titre générique | `<title>` et `<h1>` (`generate_page.py`) |
| `--output` | stdout si absent | chemin de sortie optionnel, jamais écrasé |
| `--dark` | désactivé | ajoute le thème sombre DSFR (`generate_page.py`) |
| `--brand-mode` | `neutral` | génère sans bloc marque ; `republique` seulement si le droit d'usage est établi (`generate_page.py` ; pour un composant : `--config '{"brand_mode":"republique"}'`) |
| `--no-header` | inclus | exclut l'en-tête (`generate_page.py`) |
| `--no-footer` | inclus | exclut le pied de page (`generate_page.py`) |
| `--assets` | CDN jsdelivr | préfixe d'URL des assets DSFR (CSS/JS/favicons) ; offline ou souveraineté (m-13) (`generate_page.py`) |

Types de page : `standard`, `landing`, `form`, `dashboard`, `error`, `login`,
`account`, `search`, `confirmation`, `list`, `detail`, `sitemap`.

Les composants isolés ne passent pas par `--type component` dans
`generate_page.py` ; utiliser `generate_component.py <component>`.
Pour `header` et `footer`, la variante par défaut est `neutral`. Les variantes
qui contiennent le bloc marque doivent être demandées explicitement et seulement
si le droit d'usage est établi.

Si l'ambiguïté change la branche, la sortie, le risque d'écrasement ou la
frontière audit ponctuel / audit complet, poser une question courte. Sinon,
choisir prudemment la branche la plus étroite et nommer l'hypothèse.

## BRANCH-MAP

| Branche | Déclencheur utilisateur ou modèle | Étapes nécessaires | Critère de fin |
| --- | --- | --- | --- |
| page complète | demande de page HTML statique DSFR, ou contexte service public avec besoin DSFR explicite | 1. pré-vol ; 2. lire profil DSFR partagé si présent ; 3. choisir le type ; 4. générer avec `generate_page.py` ; 5. personnaliser ; 6. vérifier | DONE-CRITERION: fichier ou stdout HTML sans `href="#"`, `<title>` et `<h1>` cohérents avec `--title`, header/main/footer présents, cibles ARIA présentes, limites nommées |
| composant isolé | demande d'un composant ou fragment DSFR à insérer | 1. identifier le composant ; 2. lire profil DSFR partagé si présent ; 3. lire la famille ciblée ; 4. générer avec `generate_component.py` ; 5. signaler la source d'insertion ; 6. vérifier liens et ARIA | DONE-CRITERION: fragment produit sur stdout ou `--output`, composant existant nommé, aucune cible ARIA absente, aucun conteneur vide, aucune conformité revendiquée sans audit |
| routage audit DSFR ponctuel | demande de vérification DSFR d'un HTML généré ou d'un composant DSFR | 1. vérifier que le HTML ou le fichier à contrôler est disponible ; 2. si audit RGAA complet, site multi-page, publication, certification ou conformité globale, arrêter et router vers `audit-rgaa-dsfr` ou `audit-accessibilite-web` ; 3. sinon appliquer `references/prompt-conformite-dsfr.md` ; 4. citer les sources lues ; 5. classer les écarts | DONE-CRITERION: HTML ou fichier contrôlé identifié, écarts DSFR classés, statut borné aux sources lues, inconnus marqués, ou routage explicite vers le skill d'audit adapté |

Une demande de comparaison de versions, de changelog ou de préparation de migration sort du périmètre de ce skill : router vers `dsfr-changelog`. Ne pas modifier la version cible depuis les seules références de composants.

Un pictogramme se pose ici en pointeur seulement (`generate_atom.py pictogram`, trois `<use href>` vers un asset servi depuis la même origine). L’asset SVG lui-même, copie exacte d’un officiel, recoloration `--minor-color` ou création `original-dsfr-like` déclarée `official: false`, relève du skill `generer-pictos-svg-dsfr` livré avec ce pack : ne jamais dessiner, recopier inline ni inventer un SVG de pictogramme depuis ce skill.

Les références par branche (commune / conditionnelle / externe) sont
centralisées dans `CONTEXT-POINTERS` ci-dessous, indexées par référence.

### CONTEXT-POINTERS

| Branche | Référence ciblée | Quand charger | Action concrète | Preuve attendue |
| --- | --- | --- | --- | --- |
| profil DSFR partagé | `design-systems/dsfr/DESIGN.md` et `design-systems/dsfr/tokens.yaml` | avant page ou composant si ces fichiers existent dans le workspace | reprendre les contraintes locales DSFR, tokens, revendications autorisées et limites de publication | fichiers cités ou absence explicitée |
| page complète | `assets/template-base.html` | seulement si `generate_page.py` est indisponible ou inadapté | partir du template, remplacer titre, contenu, navigation et footer | fallback signalé et limite nommée |
| page formulaire | `references/patterns.md`, puis `references/patterns/validation-differee.md`, `references/patterns/nom-prenom.md` et `references/patterns/autocomplete.md` | dès que `--type form` ou un formulaire administratif est choisi | appliquer l'ordre prénom puis nom, `given-name`, `family-name`, `email`, les labels associés, et différer `required` / `pattern` jusqu'au premier `submit` | smoke HTML montrant ordre, attributs et absence de contrainte native au repos |
| page thème sombre | `references/theming.md` | seulement avec `--dark` ou demande de thème | appliquer les attributs et contrôles de thème documentés | HTML avec thème sombre inspecté |
| mise en page | `references/utilities.md`, puis sous-référence exacte dans `references/utilities/` | si la demande touche grille, espacements, couleurs ou responsive | choisir les classes `fr-col-*`, espacements et utilitaires utiles | classes citées ou visibles dans le HTML |
| mesure d'audience | `references/analytics.md` | si la demande porte sur la mesure d'audience DSFR (attributs `data-fr-analytics-*`, intégration script) | documenter l'intégration et les attributs à poser ; ne pas générer la configuration | attributs et source paquet cités |
| frontière strate | `references/strate-artefact.md` | si la demande touche un token/utilitaire/composant ambigu ou un utilitaire possiblement absent (display, flex, position, radius, shadow) | distinguer token (CSS var) / utilitaire (classe) / composant ; n'inventer aucune classe absente du paquet 1.15.2 | strate décidée ou absence documentée |
| design tokens | `references/tokens.md` | si la demande porte sur les variables CSS DSFR (couleurs Marianne sémantiques/brutes, espacement, ombres, arrondis) | consommer `var(--…)` en CSS ; ne pas émettre de token en HTML | catégories sourcées du `:root` |
| couverture officielle | `evals/official-coverage-inventory.md` | si la demande exige 100 %, exhaustivité, taux ou périmètre chiffré | lire l'inventaire généré, puis rejouer la commande si le claim doit être actualisé | chiffres cités, commande rejouée ou limite nommée |
| composant isolé | `references/components.md`, puis index de famille dans `references/components/*.md`, puis sous-fichier ciblé | après identification du composant demandé | lire l'index, ouvrir la famille utile, puis le sous-fichier du composant | composant nommé et source ciblée citée |
| composant formulaire | `references/components/forms-services.md`, sous-fichier utile et `references/patterns/validation-differee.md` | si un fragment `input`, `textarea`, checkbox, radio, recherche ou formulaire doit être requis ou contraint | garder labels, aides et `autocomplete`, mais ne pas poser `required`, `aria-required`, `pattern` ou `aria-invalid` au repos | fragment sans contrainte native au repos ou arbitrage documenté |
| options avancées des scripts | `references/scripts-options.md` | si une option, variante ou configuration manque dans `Types et arguments` | lire seulement la section du script concerné | option citée et commande cohérente |
| audit DSFR ponctuel | `references/prompt-conformite-dsfr.md` | pour vérifier un HTML ou un composant déjà produit | classer les écarts sur les sources lues ; ne pas produire de statut `conforme` global ; router les audits RGAA complets | statut borné ou routage explicite |
| claims et publication | `design-systems/dsfr/references/verification.md` | si une preuve, une publication ou une revendication DSFR/RGAA est demandée et si le chemin existe | appliquer les niveaux de preuve et abaisser les formulations sans preuve dédiée | claims autorisés, retirés ou limite nommée |
| déclenchement modèle | `evals/model-trigger-smoke.md` | avant publication, investigation d'invocation ou modification du frontmatter / des déclencheurs | jouer les prompts positifs et near-miss si le runtime de sélection est observable ; sinon utiliser le proxy local décrit dans l'eval | PASS runtime si observable ; sinon proxy smoke déclaré avec limite |
| validation locale | `evals/local-validation.md` et `evals/leading-words-trace.md` | avant de publier, scorer ou modifier substantiellement le skill | rejouer les commandes de validation, vérifier les traces et échouer si `.DS_Store` ou `__pycache__` existe | sorties `PASS`, absence d'artefact ou limites nommées |
| contrat de méthode | `references/method-contract.md` | avant publication, scoring, refactor du skill ou investigation WGS | charger le contrat complet, vérifier `INVESTIGATION-WORK`, `COLOCATION`, `LEXICAL-CANDIDATES`, `LEADING-WORDS`, `INCARNATION-PROBE`, `PRUNING`, `TALK-FIDELITY` et `METHOD-COMPLETE` | blocs cités ou limite nommée |
| fallback officiel | `https://www.systeme-de-design.gouv.fr/composants-et-modeles/composants/` | seulement si la référence locale du composant manque | charger uniquement la page du composant concerné, relever URL, section et contrainte utile ; ne pas importer le catalogue entier | URL, section et limite du fallback citées |

## Contrat de méthode

Le contrat complet vit dans `references/method-contract.md`.

Charger cette référence avant publication, scoring, refactor du skill ou
investigation WGS. Ne pas la charger pour une simple génération : les branches,
pointeurs et critères observables ci-dessus suffisent.

Elle contient `INVESTIGATION-WORK`, `COLOCATION`, `LEXICAL-CANDIDATES`,
`LEADING-WORDS`, `INCARNATION-PROBE`, `PRUNING`, `TALK-FIDELITY` et
`METHOD-COMPLETE`.

## Génération

Pré-vol :

| Point | Action | Signal observable |
| --- | --- | --- |
| Python | lancer `python3 --version` | version citée ou fallback annoncé |
| dossier du skill | identifier le dossier qui contient ce `SKILL.md` (`SKILL_DIR`, par exemple `.claude/skills/dsfr-components` ou `~/.codex/skills/dsfr-components`) et vérifier `$SKILL_DIR/scripts/` | chemin cité ou absence nommée |
| sortie | si `--output`, vérifier que le fichier n'existe pas | fichier préservé, autre chemin choisi ou arrêt |
| branche | choisir page, composant ou audit ponctuel | type et script nommés |
| sources | lire seulement les références ciblées utiles | fichiers lus ou absences citées |
| fallback | si script ou référence locale manque, utiliser template ou page officielle ciblée | raison, URL ou template et limite nommés |

Les commandes partent de `SKILL_DIR`, le dossier de ce skill, quel que soit
l'hôte qui l'a installé (`.claude/skills/`, `.codex/skills/`, `.agents/skills/`).

Page complète :

```bash
python3 "$SKILL_DIR/scripts/generate_page.py" --type standard --title "Mon service" --brand-mode neutral --output page.html
```

Composant isolé :

```bash
python3 "$SKILL_DIR/scripts/generate_component.py" alert --config '{"type":"warning","title":"Maintenance","description":"Service indisponible de 2 h à 6 h."}'
```

Les 46 composants officiels DSFR 1.15.2 acceptent une génération native
paramétrable par `--config` ; la CLI en liste 48, les 2 de plus
(`back_to_top`, `button_group`) n'existant qu'en variante de bibliothèque. Sans `--variant`, le générateur natif est utilisé
pour les 46 composants officiels ; `back_to_top` et `button_group` répondent toujours depuis la
bibliothèque et leur `--config` est sans effet (avertissement sur stderr). Avec `--variant`,
c'est la variante figée de la bibliothèque JSON.

Autres générateurs : `generate_atom.py`, `generate_layout.py`,
`generate_field.py`, `generate_assembled_page.py` et `list_icons.py` sont
détaillés dans `references/scripts-options.md`. `generate_assembled_page.py`
compose une page riche depuis un JSON de sections (cf.
`references/assembly.md`) ; son schéma vit dans
`schemas/generate_assembled_page.schema.json` et les exemples complets dans
`examples/assembled/`. Les blocs fonctionnels conservent la validation différée
et les conventions de `references/patterns/`.

Variantes riches des composants structurels : header `tools`/`languages`/
`search`/`navigation`, navigation `categories` (mega-menu) + `align`, footer
`partners`/`bottom_links`/`copyright`. Les exemples et options détaillés vivent
dans `references/scripts-options.md`.

`search` et `navigation` ajoutent `fr-header__brand-top` + `fr-header__navbar`
(boutons `fr-btn--search` / `fr-btn--menu`) et les modales `fr-header__search`
et `fr-header__menu`. Opt-in : sans eux, l'en-tête reste minimal. Le
comportement interactif JS (ouverture des modales, `aria-expanded` dynamique)
n'est pas vérifié sans navigateur.

Note : ce paragraphe décrit le générateur de composant isolé
`generate_component.py header`. Le header des pages complètes
(`generate_page.py`) inclut par défaut la recherche, le menu et les outils ;
le contrat `with_search_neutral` de `check_generated_outputs.py` vérifie la
recherche et le bouton de menu avec sa cible.

Régression golden : `scripts/check_golden_outputs.py` capture les sorties
 natives de header, navigation et footer (variantes minimales + riches), et de
card, alert, form, accordion, tabs et blocs fonctionnels (civilite, nom-prenom,
email, date-unique, societe) (défauts), dans
`evals/golden/*.html` et détecte toute dérive au prochain changement. `--update`
(re)génère le baseline, à n'utiliser que pour un changement délibéré.


Nommage : utiliser les noms DSFR canoniques quand ils existent. Le générateur
accepte `tab` et `skiplink`, tout en gardant les anciens alias locaux `tabs` et
`skiplinks`. Les entrées `back_to_top` et `button_group` sont des helpers
locaux composés avec des classes DSFR, pas des composants autonomes du paquet
officiel.

Erreurs de génération : si `--config` contient un JSON invalide, si le composant
ou la variante demandée n'existe pas, ou si le script retourne un code non nul,
arrêter ; citer l'erreur courte et ne pas inventer de composant de remplacement.

Si Python est absent, partir de `assets/template-base.html` et remplacer
manuellement titre, contenu, navigation et footer. Si une référence locale de
composant manque, utiliser WebFetch seulement sur la page officielle du
composant concerné, citer l'URL et ne pas charger le catalogue entier.

## Contraintes DSFR

- Utiliser `lang="fr"` sur `<html>`.
- Inclure charset, viewport, CSS et JS DSFR.
- Cibler DSFR 1.15.2 (repli figé dans `scripts/generate_page.py`, surchargeable
  par `DSFR_OFFICIAL_VERSION`) ; ne pas
  changer de version sans raison donnée.
- Utiliser `--brand-mode neutral` par défaut ; choisir `--brand-mode
  republique` et le bloc marque République française seulement si le droit
  d'usage est établi pour le service.
- Fournir un footer avec plan du site, accessibilité, mentions légales et
  données personnelles.
- Respecter la hiérarchie des titres sans saut.
- Conserver `role="banner"` sur le header et `role="contentinfo"` sur le footer.
- Associer chaque champ de formulaire à un label.
- Pour un champ requis ou contraint, différer `required`, `aria-required`,
  `pattern` et `aria-invalid` jusqu'au premier `submit`, sauf arbitrage
  documenté.
- Utiliser `rel="noopener"` avec `target="_blank"`.

## Personnalisation

Après génération :

- remplacer les textes génériques par du contenu réel ;
- remplacer tous les `href="#"` ;
- adapter la grille `fr-col-*` au contenu ;
- ajouter seulement les composants nécessaires ;
- vérifier les libellés, états d'erreur et aides de formulaire ;
- éviter le CSS custom qui écrase les classes `fr-*`.

Finir la personnalisation seulement avec un signal observable : commande ou
inspection qui montre les liens remplacés, les libellés présents et les limites
restantes.

## Vérification

Avant livraison :

- consulter `design-systems/dsfr/references/verification.md` si une preuve, une publication ou une revendication DSFR/RGAA est demandée ;
- appliquer `references/prompt-conformite-dsfr.md` au HTML généré avec un statut
  borné, sans écrire `conforme DSFR` ou `conforme RGAA` sans preuve dédiée ;
- corriger les écarts bloquants ou majeurs ;
- vérifier les labels, liens et cibles ARIA par inspection du HTML ;
- vérifier contraste, focus et navigation clavier avec un outil ou une passe
  manuelle nommée ; sinon déclarer explicitement la limite ;
- vérifier l'absence de `href="#"` et de cibles ARIA absentes ;
- rejouer `scripts/check_generated_outputs.py`, qui couvre les contrats
  structurels des pages, des racines de composants et des composants critiques ;
- rejouer `scripts/check_golden_outputs.py` pour les 21 sorties natives (header,
  navigation, footer, card, alert, form, accordion, tabs et les 5 blocs
  fonctionnels ; régression golden contre `evals/golden/*.html`) ;
- vérifier l'absence de `.DS_Store` et `__pycache__` dans le dossier du skill ;
- pour les composants JS, vérifier d'abord les cibles ARIA statiques ; si le
  comportement interactif est revendiqué, attendre l'initialisation DSFR puis
  vérifier `aria-expanded`, les classes d'ouverture, le focus et la console ;
- avant publication, ouvrir les pages générées avec
  `scripts/check_generated_pages_playwright.js` si Playwright et le cache DSFR
  local sont disponibles ;
- séparer dans le compte rendu `vérifié`, `non vérifié` et `hypothèse` ; un
  `SKIPPED` Playwright est une limite nommée, pas un `PASS` navigateur ;
- annoncer les limites si une vérification n'a pas été faite.

## Exemple

```text
Demande : page DSFR de demande de rendez-vous.
Action : generate_page.py --type form --title "Demande de rendez-vous".
Livrable : fichier HTML avec header, formulaire labellisé, bouton et footer.
Vérification : prompt de conformité DSFR puis correction des écarts.
```

## Pièges fréquents

- Lire toute la référence composants au lieu de cibler le sous-fichier utile.
- Laisser des liens `href="#"` dans le livrable.
- Ajouter du CSS custom qui casse le DSFR.
- Oublier les labels et messages d'erreur des formulaires.
- Générer une page visuellement DSFR mais non navigable au clavier.
- Utiliser une version DSFR différente sans raison donnée.

## Checklist

- [ ] Type, titre et chemin de sortie confirmés.
- [ ] Fichier existant préservé ; aucun écrasement implicite.
- [ ] Références lues de façon ciblée.
- [ ] HTML DSFR généré ou fallback manuel signalé.
- [ ] Header, main, footer et liens obligatoires présents.
- [ ] Accessibilité de base vérifiée par inspection du HTML : labels, liens et cibles ARIA (pas seulement supposés).
- [ ] Aucun `href="#"` résiduel.
- [ ] Aucune cible ARIA absente pour les contrôles générés.
- [ ] `scripts/check_generated_outputs.py` rejoué, sortie `PASS` citée (pages, racines de composants, composants critiques).
- [ ] Aucun `.DS_Store` ni `__pycache__` dans le dossier du skill avant score ou publication.
- [ ] Smoke prompts positifs, audit ponctuel et near-miss négatifs couverts si publication ou modification des déclencheurs.
- [ ] Proxy de déclenchement déclaré quand le runtime de sélection n'est pas observable.
- [ ] Vérification DSFR finale appliquée ou limite explicitée.
