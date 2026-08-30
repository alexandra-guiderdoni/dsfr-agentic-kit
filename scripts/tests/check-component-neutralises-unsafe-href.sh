#!/usr/bin/env bash
set -euo pipefail

# generate_component.py émet des fragments : son contrat est de NEUTRALISER un
# href dangereux (repli sur "/"), pas d'échouer comme le builder assemblé.
# Le test lit donc la sortie HTML et vérifie qu'aucun href exécutable n'en sort.
#
# La normalisation reproduit celle du navigateur : tab, LF, CR et caractères de
# contrôle sont retirés AVANT de lire le schéma (spec URL WHATWG). Sans elle,
# "java<TAB>script:" paraît inoffensif alors qu'il s'exécute.

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WORKSPACE="$(cd "$SCRIPT_DIR/../.." && pwd)"
GENERATOR="$WORKSPACE/.claude/skills/dsfr-components/scripts/generate_component.py"

python3 - "$GENERATOR" <<'PYEOF'
import json, re, subprocess, sys

generator = sys.argv[1]

CHARGES = [
    ("javascript nominal",     "javascript:alert(1)"),
    ("casse melangee",         "JaVaScRiPt:alert(1)"),
    ("tab interne au schema",  "java\tscript:alert(1)"),
    ("newline interne",        "java\nscript:alert(1)"),
    ("espaces de tete",        "   javascript:alert(1)"),
    ("data",                   "data:text/html;base64,PHNjcmlwdD4="),
    ("vbscript",               "vbscript:msgbox(1)"),
    ("blob",                   "blob:https://evil.example/x"),
    ("file",                   "file:///etc/passwd"),
    ("about",                  "about:blank"),
    ("protocol-relative",      "//evil.example/x"),
    ("retour chariot interne", "java\rscript:alert(1)"),
    ("null byte de tete",      "\x00javascript:alert(1)"),
    ("tab avant deux-points",  "javascript\t:alert(1)"),
    ("data casse et espace",   " DATA:text/html;base64,PHNjcmlwdD4="),
]

# Un composant par clé de configuration portant un href utilisateur.
CIBLES = [
    ("link",       lambda h: {"label": "X", "href": h}),
    ("card",       lambda h: {"title": "X", "link": h}),
    ("tile",       lambda h: {"title": "X", "href": h}),
    # Deux éléments obligatoires : le breadcrumb rend le DERNIER en
    # aria-current="page" sans href. Avec un seul élément, aucun lien n'est
    # émis et le cas ne prouverait rien.
    ("breadcrumb", lambda h: {"items": [{"label": "N1", "href": h},
                                        {"label": "N2", "href": "/courante"}]}),
    ("download",   lambda h: {"label": "X", "href": h}),
    ("summary",    lambda h: {"items": [{"label": "S1", "href": h}]}),
    ("sidemenu",   lambda h: {"items": [{"label": "M1", "href": h}]}),
    ("tag",        lambda h: {"label": "T", "href": h}),
]

BRUIT = re.compile(r"[\x00-\x20\x7f]")
SCHEMA = re.compile(r"^([a-z][a-z0-9+.\-]*):", re.IGNORECASE)
AUTORISES = {"http", "https", "mailto", "tel"}
HREFS = re.compile(r'href="([^"]*)"')

def hrefs_dangereux(html):
    mauvais = []
    for brut in HREFS.findall(html):
        # html.unescape n'est pas requis : le générateur échappe &, < et >,
        # pas les caractères de contrôle, qui ressortent littéraux.
        net = BRUIT.sub("", brut)
        if net.startswith("//"):
            mauvais.append(brut); continue
        m = SCHEMA.match(net)
        if m and m.group(1).lower() not in AUTORISES:
            mauvais.append(brut)
    return mauvais

echecs = 0

for composant, fabrique in CIBLES:
    for label, charge in CHARGES:
        cfg = json.dumps(fabrique(charge))
        r = subprocess.run([sys.executable, generator, composant, "--config", cfg],
                           capture_output=True, text=True)
        if r.returncode != 0:
            print(f"[FAIL] {composant} / {label} : le générateur a planté "
                  f"(exit {r.returncode})", file=sys.stderr)
            print(r.stderr[:300], file=sys.stderr)
            echecs += 1
            continue
        fuites = hrefs_dangereux(r.stdout)
        if fuites:
            print(f"[FAIL] {composant} / {label} : href exécutable en sortie "
                  f"-> {fuites!r}", file=sys.stderr)
            echecs += 1

# Les href légitimes doivent survivre intacts.
LEGITIMES = ["https://example.gouv.fr/service", "/contact", "page.html",
             "mailto:contact@example.gouv.fr", "tel:+33123456789"]
for composant, fabrique in CIBLES:
    for href in LEGITIMES:
        cfg = json.dumps(fabrique(href))
        r = subprocess.run([sys.executable, generator, composant, "--config", cfg],
                           capture_output=True, text=True)
        if r.returncode != 0 or href not in r.stdout:
            print(f"[FAIL] {composant} : href légitime perdu ou rejeté -> {href}",
                  file=sys.stderr)
            echecs += 1

if echecs:
    sys.exit(1)

print(f"[OK] {len(CIBLES)} composants x {len(CHARGES)} charges neutralisées, "
      f"{len(LEGITIMES)} href légitimes préservés")
PYEOF
