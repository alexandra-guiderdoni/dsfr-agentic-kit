# Validation locale reproductible

Objectif : fournir des traces observables pour les mots conducteurs du skill
sans stocker de hash ou d'archive N=5 dans `SKILL.md`.

## Portée

Cette validation couvre les scripts, les références Markdown et les contrats
HTML générés localement. Elle ne prouve pas le déclenchement runtime du modèle :
ce point reste limité au proxy décrit dans `model-trigger-smoke.md`.

Le contrôle Playwright est optionnel : il exige un module `playwright`
résoluble depuis `node_modules`, `PLAYWRIGHT_PACKAGE_DIR` ou le cache
`~/.npm/_npx`, ainsi qu'un paquet `@gouvfr/dsfr` extrait localement. S'il
manque un prérequis, le script doit sortir `SKIPPED` avec raison explicite et
code `2`, jamais un `PASS`.

Les contrôles navigateur remplacent les liens CDN DSFR par les fichiers locaux
du cache `DSFR_OFFICIAL_CACHE_DIR` ou `DSFR_OFFICIAL_PACKAGE_DIR`. Pour un check
de paquet, la variable `DSFR_INTERACTIVE_SKIP_ON_RUNTIME_LOAD=1` autorise un
`SKIPPED` si le runtime DSFR ne se charge pas avant le timeout ; cela prouve que
le test est branché, pas que le navigateur a validé le rendu.

Le contrôle d'accents appelle `scripts/check-accents.sh` depuis la racine du
workspace hôte. C'est une preuve interne workspace, pas une
dépendance portable du skill pour Sandjab ou une publication hors workspace.

## Commandes minimales à rejouer

Ces commandes ne scorent pas le skill. Elles vérifient seulement que les sorties
locales gardent les invariants attendus.

`SKILL_DIR` désigne le dossier du skill (`.claude/skills/dsfr-components` chez
le mainteneur, ailleurs selon l'hôte). Le bloc suivant doit s'arrêter au premier échec (les fichiers générés vont
dans un dossier temporaire supprimé en sortie ; `SKILL_DIR` est protégé par des
guillemets, un chemin avec espace reste valide). Les seuls échecs acceptés sans
NO-GO local sont les contrôles Playwright qui sortent `SKIPPED` avec code `2`.

```bash
set -euo pipefail
SKILL_DIR="${SKILL_DIR:-.claude/skills/dsfr-components}"  # adapter à l'emplacement d'installation
WORK="$(mktemp -d)"
trap 'rm -rf "$WORK"' EXIT
python3 --version
python3 -B - "$SKILL_DIR"/scripts/*.py <<'PY'
import ast, sys
for path in sys.argv[1:]:
    ast.parse(open(path, encoding="utf-8").read(), path)
print("syntaxe PASS")
PY
python3 -B "$SKILL_DIR/scripts/generate_page.py" --type form --title "Validation locale" >"$WORK/form.html"
python3 -B "$SKILL_DIR/scripts/generate_component.py" accordion >"$WORK/accordion.html"
python3 -B "$SKILL_DIR/scripts/generate_field.py" date-unique >"$WORK/field.html"
python3 -B "$SKILL_DIR/scripts/generate_atom.py" grid --config '{"gutters":true,"cols":[{"content":"A","md":6},{"content":"B","md":6}]}' >"$WORK/atom.html"
python3 -B "$SKILL_DIR/scripts/generate_layout.py" card-grid --config '{"cards":[{"title":"Démarche","desc":"En ligne","href":"/d"}],"md":4}' >"$WORK/layout.html"
# rg : 0 = trouvé (invariant violé), 1 = rien (attendu), 2 = erreur de lecture (échec)
rc=0; rg -n 'href="#"' "$WORK"/form.html "$WORK"/accordion.html "$WORK"/field.html "$WORK"/atom.html "$WORK"/layout.html || rc=$?; test "$rc" -eq 1
rc=0; rg -U -n '<(input|select|textarea)[^>]*(\s|\n)(required|aria-required=|pattern=|aria-invalid=)' "$WORK"/form.html "$WORK"/accordion.html "$WORK"/field.html "$WORK"/atom.html "$WORK"/layout.html || rc=$?; test "$rc" -eq 1
python3 -B "$SKILL_DIR/scripts/check_generated_outputs.py"
python3 -B "$SKILL_DIR/scripts/check_golden_outputs.py"
python3 -B - "$WORK"/form.html "$WORK"/accordion.html "$WORK"/field.html "$WORK"/atom.html "$WORK"/layout.html <<'PY'
from collections import Counter
from html.parser import HTMLParser
from pathlib import Path
import sys

class Targets(HTMLParser):
    """Cibles ARIA, `for` des labels et ancres locales résolus ; ids uniques."""
    def __init__(self):
        super().__init__()
        self.ids = Counter()
        self.refs = []

    def handle_starttag(self, tag, attrs):
        data = dict(attrs)
        if data.get("id"):
            self.ids[data["id"]] += 1
        for attr in ("aria-controls", "aria-labelledby", "aria-describedby", "for"):
            for target in (data.get(attr) or "").split():
                self.refs.append((attr, target))
        href = data.get("href") or ""
        if href.startswith("#") and len(href) > 1:
            self.refs.append(("href", href[1:]))

for filename in sys.argv[1:]:
    parser = Targets()
    parser.feed(Path(filename).read_text(encoding="utf-8"))
    parser.close()
    duplicates = sorted(i for i, n in parser.ids.items() if n > 1)
    if duplicates:
        raise SystemExit(f"{filename}: ids dupliqués: {duplicates}")
    known = set(parser.ids) | {"top", "contenu", "footer", "navigation"}
    missing = [(attr, target) for attr, target in parser.refs if target not in known]
    if missing:
        raise SystemExit(f"{filename}: cibles absentes: {missing}")
print("aria_targets PASS")
PY
artifacts=$(find "$SKILL_DIR" \( -name '.DS_Store' -o -name '__pycache__' \) -print)
test -z "$artifacts" || { printf '%s\n' "$artifacts"; exit 1; }
rg -n 'pos-page-form|pos-component-accordion|pos-audit-local|pos-js-accordion-proof|near-miss-rgaa|near-miss-react|near-miss-service-public-no-dsfr|near-miss-publication' "$SKILL_DIR/evals/model-trigger-smoke.md"
rg -n 'React|Vue|Angular' "$SKILL_DIR/SKILL.md"
rg -n 'audit RGAA complet|publication|certification' "$SKILL_DIR/SKILL.md"
rg -n 'Besoin DSFR explicite|service public' "$SKILL_DIR/SKILL.md"
node "$SKILL_DIR/scripts/check_deferred_validation_playwright.js" "$WORK/form.html" || test "$?" -eq 2
DSFR_INTERACTIVE_SKIP_ON_RUNTIME_LOAD=1 node "$SKILL_DIR/scripts/check_interactive_components_playwright.js" || test "$?" -eq 2
DSFR_INTERACTIVE_SKIP_ON_RUNTIME_LOAD=1 node "$SKILL_DIR/scripts/check_header_navigation_playwright.js" || test "$?" -eq 2
DSFR_INTERACTIVE_SKIP_ON_RUNTIME_LOAD=1 node "$SKILL_DIR/scripts/check_generated_pages_playwright.js" || test "$?" -eq 2
```

Comparaison officielle cacheable à lancer avant publication ou recalage du
catalogue local :

```bash
python3 -B "$SKILL_DIR/scripts/check_generated_outputs.py" --official-version 1.15.2
python3 -B "$SKILL_DIR/scripts/inventory_official_coverage.py" --official-version 1.15.2 --output "$SKILL_DIR/evals/official-coverage-inventory.md"
```

Le cache officiel est rempli par `npm pack`, qui n'exécute pas le hook
`preinstall` ajouté en 1.15. Vérifié le 2026-08-29 dans un dossier jetable :
`npm pack @gouvfr/dsfr@1.15.2 --ignore-scripts=false --loglevel=verbose` sort en
code 0, produit `gouvfr-dsfr-1.15.2.tgz` (22,8 Mo) sans aucune ligne de cycle
de vie (`preinstall`, `prepare`), alors que le `package.json` du paquet déclare
`"preinstall": "node scripts/preinstall.js"` ; `--ignore-scripts=false` neutralise
le `ignore-scripts=true` du `~/.npmrc` du poste. Une installation classique du
paquet exige en revanche l'acceptation des CGU (`.dsfr.yml` ou
`DSFR_ACCEPT_LICENSE=1`, voir `design-systems/dsfr/references/sources.md`).

`evals/archive/couverture-officielle-1-14-4-historique.md` conserve
l'instantané historique de la couverture en 1.14.4. Ses chiffres ne décrivent
pas la référence courante : utiliser `evals/official-coverage-inventory.md`,
qui est régénéré par la commande ci-dessus.

Résolution de Playwright : les scripts cherchent le module dans
`PLAYWRIGHT_PACKAGE_DIR`, puis par `require` standard, puis dans le cache
`~/.npm/_npx` (le plus récent) ; les navigateurs viennent de
`~/Library/Caches/ms-playwright`. Sur ce poste, le cache npx suffit : les
quatre scripts s'exécutent sans installation (vérifié le 2026-08-28,
Playwright 1.61.1). `check_deferred_validation_playwright.js` exige un fichier
HTML en argument et soumet le formulaire de `<main>`, pas celui de la
recherche du header.

Le contrôle Playwright peut sortir `SKIPPED` avec code `2`. Dans ce cas, la
validation différée reste vérifiée statiquement, mais le comportement navigateur
et les composants JS interactifs restent `non vérifiés`.

## Sources lues

| Besoin | Source ciblée | Observation |
| --- | --- | --- |
| ordre prénom puis nom | `references/patterns/nom-prenom.md` | le pattern demande prénom avant nom |
| valeurs `autocomplete` | `references/patterns/autocomplete.md` | `given-name`, `family-name`, `email` applicables au formulaire |
| validation différée | `references/patterns/validation-differee.md` | `required`, `aria-required`, `pattern` et `aria-invalid` ne doivent pas fuir au repos |
| composants formulaire | `references/components/forms-services.md` puis sous-fichier utile | les fragments de formulaire renvoient au pattern différé pour tout champ requis ou contraint |
| familles de composants | `references/components.md`, index de famille, puis sous-fichier ciblé | l'index route vers 5 familles et leurs sous-références |
| contrat de méthode | `references/method-contract.md` | le contrat WGS complet est chargé seulement pour publication, scoring, refactor ou investigation |
| déclencheur resserré | `SKILL.md#déclencheurs` et `evals/model-trigger-smoke.md` | `.gouv`, service public ou administratif seul ne suffit plus ; le besoin DSFR doit être explicite |
| pré-vol observable | `SKILL.md#génération` | chaque point de pré-vol a un signal observable |
| mots conducteurs | `evals/leading-words-trace.md` | chaque mot est relié à un fichier, une commande ou un verdict borné |
| génération formulaire | `scripts/generate_page.py` | `--type form` produit les attributs attendus sans contrainte native au repos |
| blocs fonctionnels | `scripts/generate_field.py` et pages officielles `blocs-fonctionnels` 1.15.2 | 5 blocs (civilité, nom-prenom, email, date-unique, societe) sourcés page par page ; aucun attribut de contrainte au repos ; conflit d'ordre nom/prénom tranché en faveur de prénom-puis-nom (convention skill), `order` configurable |
| variantes riches structurelles | `scripts/generate_component.py` (header, navigation, footer) et templates ejs 1.15.2 | header tools/languages, navigation mega-menu + align-right, footer partenaires + bottom ; opt-in, défaut préservé ; classes vérifiées dans `dsfr.min.css` |
| harnais golden | `scripts/check_golden_outputs.py` et `evals/golden/*.html` | capture les sorties natives header/navigation/footer (minimal + riches) ; diff vide = non-régression ; `--update` pour changement délibéré |
| atomes et gabarits | `scripts/generate_atom.py` et `scripts/generate_layout.py` | 11 atomes + 5 gabarits ; smoke grid + card-grid dans le bloc minimal (compilation, génération, scans href/contraintes, cibles ARIA) |
| interactif JS header/navigation | `scripts/check_header_navigation_playwright.js` | vrais fragments (header search/menu/translate, navigation menu/mega-menu) en navigateur ; viewport mobile (navbar) + desktop (tools/nav) ; assertions aria-expanded + classes d'ouverture |

## Journal observé

Exécution locale du 8 juillet 2026 après les correctifs header/search et les
correctifs markup `toggle`, `notice`, `tooltip`, `follow`.

| Trace | Commande | Sortie observée |
| --- | --- | --- |
| accents Markdown | `find $SKILL_DIR -name '*.md' -print0 \| xargs -0 -n1 bash scripts/check-accents.sh` | exit 0 |
| compilation scripts | `export PYTHONPYCACHEPREFIX=/tmp/dsfr-components-pycache` puis `python3 -m py_compile $SKILL_DIR/scripts/generate_page.py $SKILL_DIR/scripts/generate_component.py $SKILL_DIR/scripts/generate_field.py $SKILL_DIR/scripts/generate_atom.py $SKILL_DIR/scripts/generate_layout.py` | exit 0 sans `__pycache__` dans le skill |
| page HTML | smoke pages générées pour les 12 types (`check_generated_outputs.py`, `iter_pages`) | `PASS generated outputs: pages=12 components=136` |
| composants HTML | smoke `alert` et `accordion` (`check_generated_outputs.py`, `iter_native_component_defaults`) | inclus dans `PASS generated outputs` |
| blocs fonctionnels | `generate_field.py date-unique`, `civilite` et `societe` exercés par `check_generated_outputs.py` (`iter_fields`, `FIELD_NEGATIVE_ARGS`) | inclus dans `PASS generated outputs` : ARIA `aria-describedby`/`aria-labelledby` résolus, aucune contrainte au repos, entrées vides ou inconnues refusées |
| variantes riches + golden | `generate_component.py` header (tools/languages, search, menu), navigation (mega-menu), footer (partenaires) + `check_golden_outputs.py` | `PASS golden: 21 cas inchangés + invariants OK` ; aucune régénération de baseline |
| composants à risque | `check_generated_outputs.py --official-version 1.15.2` + cas natifs adversariaux `toggle`, `notice`, `tooltip`, `follow` | `PASS generated outputs: pages=12 components=136` ; messages group et ARIA des toggles, `fr-notice__desc`/`fr-notice__link`, tooltip sans `aria-hidden` statique, abonnement en bouton et `fr-btn--twitter-x` vérifiés statiquement |
| inventaire officiel | `inventory_official_coverage.py --official-version 1.15.2` | 1090 variables CSS, 1517 classes utilitaires dont 221 hors icônes/artwork, 1044 classes `fr-icon-*`, 154 classes legacy `fr-fi-*`, 102 pictogrammes SVG et 46/46 composants officiels couverts localement |
| atomes et gabarits | smoke `generate_atom.py grid` et `generate_layout.py card-grid` dans le bloc minimal | `PASS` : aucun href="#", aucune contrainte au repos, cibles ARIA résolues |
| interactif header/navigation | `node scripts/check_header_navigation_playwright.js` (vrais fragments, viewport mobile+desktop) | `PASS` : modales search/menu ouvrent (`fr-modal--opened`) puis ferment, translate/menu/mega `aria-expanded` false→true, collapses `fr-collapse--expanded`, 0 erreur console |
| P3 pictogram + analytics | `generate_atom.py pictogram` + `references/analytics.md` | atom pictogram pointer-only (11 atomes, classes `fr-artwork*` vérifiées) ; référence analytics (9 attributs `data-fr-analytics-*` sourcés du paquet) ; `check_generated_outputs.py` PASS local et `--official-version 1.15.2`, `check_golden_outputs.py` PASS 21 cas |
| page account + icon-list | `generate_page.py --type account` + `list_icons.py` | page création de compte (FranceConnect + form prénom-puis-nom/email/new-password, validation différée, 0 contrainte au repos) ; `check` pages 11→12 ; icon-list runtime (1044 icônes, 18 catégories, `--filter`/`--validate` exit 0/1) |
| footer et liens externes | contrôle `target_blank_without_noopener` de `check_generated_outputs.py` sur toutes les sorties | inclus dans `PASS generated outputs` |
| cibles ARIA statiques | scan `aria-controls`, `aria-labelledby`, `aria-describedby`, `for` et ancres locales des sorties minimales, ids uniques | `aria_targets PASS` |
| validation différée | génération `--type form` puis scan des balises `input`, `select` et `textarea` | aucune contrainte `required`, `aria-required`, `pattern` ou `aria-invalid` au repos |
| contrats structurels composants | `python3 $SKILL_DIR/scripts/check_generated_outputs.py` | `PASS generated outputs: pages=12 components=136` ; racines DSFR, header, footer, formulaire, accordéon, onglets, modale et composants à risque contrôlés statiquement |
| CI paquet | `.github/workflows/agentic-design-pack.yml` | checks source DSFR/RGAA, génération des paquets et checks des paquets générés branchés sur `push`, `pull_request` et `workflow_dispatch` |
| garde composants formulaire | scan récursif `references/components/forms-services/**/*.md` sur les balises `input`, `select` et `textarea` avec `required`, `aria-required`, `pattern` ou `aria-invalid` | aucune sortie |
| validation Playwright | `node scripts/check_deferred_validation_playwright.js <formulaire.html>` | `PASS`, `invalidBeforeCount=0`, contraintes visibles après `submit`, nettoyage après `reset` si présent |
| composants interactifs Playwright | `node scripts/check_interactive_components_playwright.js` | `PASS` ou `SKIPPED` explicite ; accordéon, onglets, modale et paramètres d'affichage vérifiés avec assets DSFR locaux si Chromium et cache DSFR sont disponibles |
| pages générées Playwright | `node scripts/check_generated_pages_playwright.js` | `PASS` ou `SKIPPED` explicite ; les 12 pages produites par `generate_page.py` sont ouvertes avec assets DSFR locaux si Chromium et cache DSFR sont disponibles |
| split références longues | index courts + sous-fichiers dédiés | anciens fichiers de référence sous 300 lignes ; sous-fichiers nouveaux sous 200 lignes |
| extraction contrat méthode | `rg -n "INVESTIGATION-WORK|METHOD-COMPLETE|TALK-FIDELITY" references/method-contract.md` | blocs retrouvés hors `SKILL.md`, pointeur présent dans `CONTEXT-POINTERS` |
| pré-vol et fallback | `rg -n "Signal observable|page officielle du composant concerné|contraste, focus" SKILL.md` | critères observables et limites explicites retrouvés |
| proxy déclenchement modèle | `rg` sur les prompts de `evals/model-trigger-smoke.md`, puis scans séparés front-end, audit/publication et service public dans `SKILL.md` | prompts positifs, audit ponctuel et near-miss retrouvés ; proxy non runtime seulement |
| trace mots conducteurs | `evals/leading-words-trace.md` | `aligné DSFR avec limites`, `référence ciblée` et `preuve observable` associés à des preuves |
| artefacts locaux | `artifacts=$(find $SKILL_DIR \( -name '.DS_Store' -o -name '__pycache__' \) -print); test -z "$artifacts"` | échoue si un artefact interdit existe |

## Verdict local

GO local pour générer ou vérifier ponctuellement du HTML statique aligné DSFR
avec limites. NO-GO pour publication, certification DSFR, conformité DSFR
globale ou conformité RGAA sans audit dédié. Si Playwright est indisponible, le
rendu navigateur et les composants JS interactifs restent `non vérifiés`.
