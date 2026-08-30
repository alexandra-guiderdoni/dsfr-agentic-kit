#!/usr/bin/env bash
set -euo pipefail

# Chaque nom de pictogramme et d'icône documenté comme officiel dans les fiches
# du skill doit exister dans le paquet @gouvfr/dsfr. Un nom inventé présenté
# comme officiel est le mode d'échec --bf500 : une documentation qu'un agent
# copie en confiance.
#
# Distribué avec le skill : la racine est celle du skill, la version cible vient
# de DSFR_OFFICIAL_VERSION (défaut : celle de generate_page.py), le paquet du
# cache DSFR_OFFICIAL_CACHE_DIR (défaut ~/.cache/dsfr-official-cache), rempli par
# check_generated_outputs.py --official-version. Sans paquet : SKIP explicite,
# code 2, jamais un PASS.

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILL_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
REFS="$SKILL_DIR/references"
VERSION="${DSFR_OFFICIAL_VERSION:-$(PYTHONDONTWRITEBYTECODE=1 python3 -B -c 'import sys; sys.path.insert(0, sys.argv[1]); import generate_page; print(generate_page.DSFR_VERSION)' "$SCRIPT_DIR")}"
CACHE="${DSFR_OFFICIAL_CACHE_DIR:-$HOME/.cache/dsfr-official-cache}"
CACHE="${CACHE/#\~/$HOME}"
PKG="$CACHE/gouvfr-dsfr-$VERSION/package"

if [[ ! -d "$PKG/dist/artwork/pictograms" ]]; then
  printf '[SKIP] paquet officiel %s absent du cache (%s) : contrôle non exercé\n' "$VERSION" "$PKG" >&2
  exit 2
fi

PKG="$PKG" REFS="$REFS" python3 -B - <<'PYEOF'
import os, re, pathlib, sys
pkg = pathlib.Path(os.environ["PKG"]); refs = pathlib.Path(os.environ["REFS"])
echecs = 0

real_pictos = {f"{p.parent.name}/{p.stem}" for p in (pkg / "dist/artwork/pictograms").glob("*/*.svg")}
doc = (refs / "pictograms.md").read_text(encoding="utf-8")
for name in sorted({m for m in re.findall(r"`([a-z-]+/[a-z0-9-]+)\.svg`", doc)} - real_pictos):
    print(f"[FAIL] pictogramme documenté absent du paquet : {name}", file=sys.stderr); echecs += 1

css = "".join(p.read_text(encoding="utf-8", errors="ignore")
              for p in (pkg / "dist/utility/icons").rglob("*.css"))
doc = (refs / "icons.md").read_text(encoding="utf-8")
names = set()
for m in re.finditer(r"`(fr-icon-[a-z0-9-]+?)-(line|fill)`(?:\s*/\s*`-(line|fill)`)?", doc):
    names.add(f"{m.group(1)}-{m.group(2)}")
    if m.group(3): names.add(f"{m.group(1)}-{m.group(3)}")
for name in sorted(names):
    if not re.search(r"\." + re.escape(name) + r"(?![a-z0-9-])", css):
        print(f"[FAIL] icône documentée absente du paquet : {name}", file=sys.stderr); echecs += 1

if echecs:
    sys.exit(1)
print(f"[OK] {len(real_pictos)} pictogrammes et {len(names)} icônes documentés existent dans le paquet")
PYEOF
