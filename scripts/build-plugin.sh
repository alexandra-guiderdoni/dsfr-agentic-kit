#!/usr/bin/env bash
# Construit un plugin Claude Code à partir de la source canonique du kit.
#
# Le plugin est dérivé de .claude/skills : il n'existe pas de copie maintenue
# dans le dépôt. Après une mise à jour du kit, il suffit de reconstruire le
# paquet et de changer sa version pour déclencher la mise à jour côté hôte.
#
# Le plugin porte les skills et leurs références. Il ne porte pas les scripts
# de contrôle, le profil DSFR ni le paquet officiel DSFR : ces éléments
# supposent un dépôt cloné et restent nécessaires pour une vérification complète.
#
#   bash scripts/build-plugin.sh
#   bash scripts/build-plugin.sh --version 0.2.0
#   bash scripts/build-plugin.sh --out /tmp/dsfr-agentic-kit.plugin

set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SOURCE_SKILLS="$ROOT/.claude/skills"
MANIFEST="$ROOT/config/agentic-design-packages.yaml"
VERSION=""
OUTPUT=""

usage() {
  sed -n '2,16p' "$0"
}

fail() {
  printf '[FAIL] %s\n' "$*" >&2
  exit 1
}

ok() {
  printf '[OK] %s\n' "$*"
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --version)
      [[ $# -ge 2 && -n "$2" ]] || fail "--version attend une valeur"
      VERSION="$2"
      shift 2
      ;;
    --out)
      [[ $# -ge 2 && -n "$2" ]] || fail "--out attend une valeur"
      OUTPUT="$2"
      shift 2
      ;;
    --help|-h)
      usage
      exit 0
      ;;
    *)
      fail "argument inconnu : $1"
      ;;
  esac
done

command -v zip >/dev/null 2>&1 || fail "zip absent : requis pour construire l’archive"
[[ -d "$SOURCE_SKILLS" ]] || fail "source des skills absente : $SOURCE_SKILLS"
[[ -f "$MANIFEST" ]] || fail "manifeste absent : $MANIFEST"

if [[ -z "$VERSION" ]]; then
  VERSION="$(git -C "$ROOT" describe --tags --abbrev=0 2>/dev/null | sed 's/^v//' || true)"
  VERSION="${VERSION:-$(sed -n 's/^version: *"\{0,1\}\([^"[:space:]]*\).*/\1/p' "$MANIFEST" | head -1)}"
  VERSION="${VERSION:-0.1.0}"
fi
[[ "$VERSION" =~ ^[0-9]+\.[0-9]+\.[0-9]+([.-][0-9A-Za-z.-]+)?$ ]] \
  || fail "version invalide : $VERSION"

if [[ -z "$OUTPUT" ]]; then
  OUTPUT="$ROOT/../dsfr-agentic-kit-$VERSION.plugin"
fi
mkdir -p "$(dirname "$OUTPUT")"
OUTPUT="$(cd "$(dirname "$OUTPUT")" && pwd)/$(basename "$OUTPUT")"
case "$OUTPUT" in
  "$ROOT"/*) fail "la sortie du plugin doit rester hors du dépôt : $OUTPUT" ;;
esac

# Provenance exacte du contenu embarqué. Un arbre sale reste constructible,
# mais il est signalé dans le README du plugin pour éviter une fausse release.
COMMIT="$(git -C "$ROOT" rev-parse HEAD 2>/dev/null || printf 'inconnu')"
if [[ -n "$(git -C "$ROOT" status --porcelain 2>/dev/null)" ]]; then
  TREE_STATE="non propre"
else
  TREE_STATE="propre"
fi
BUILD="$(mktemp -d "${TMPDIR:-/tmp}/dsfr-agentic-kit-plugin.XXXXXX")"
trap 'rm -rf "$BUILD"' EXIT INT TERM
PLUGIN="$BUILD/plugin"
mkdir -p "$PLUGIN/.claude-plugin"
cp -R "$SOURCE_SKILLS" "$PLUGIN/skills"
find "$PLUGIN/skills" -name '__pycache__' -type d -exec rm -rf {} + 2>/dev/null || true
find "$PLUGIN/skills" -name '.DS_Store' -type f -delete 2>/dev/null || true

cat > "$PLUGIN/.claude-plugin/plugin.json" <<JSON
{
  "name": "dsfr-agentic-kit",
  "version": "$VERSION",
  "description": "Skills DSFR et RGAA/WCAG pour concevoir, vérifier et corriger des interfaces publiques françaises sans confondre génération plausible et conformité prouvée.",
  "author": {
    "name": "Équipe DSFR Agentic"
  },
  "homepage": "https://github.com/alexandra-guiderdoni/dsfr-agentic-kit",
  "repository": "https://github.com/alexandra-guiderdoni/dsfr-agentic-kit",
  "license": "Licence Ouverte 2.0 / Open Licence 2.0 (Etalab)",
  "keywords": [
    "dsfr",
    "rgaa",
    "wcag",
    "accessibilité",
    "design-system",
    "service-public"
  ]
}
JSON

python3 - "$PLUGIN/.claude-plugin/plugin.json" <<'PY'
import json
import sys
from pathlib import Path

json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
PY

# Ce contrôle rejette les divergences et les liens relatifs cassés avant la
# création de l’archive. Tous les renvois doivent rester dans le plugin copié.
# Le manifeste est lu avec le même adaptateur que les contrôles du kit.
# shellcheck disable=SC1091
# shellcheck source=lib/python-with-pyyaml.sh
. "$ROOT/scripts/lib/python-with-pyyaml.sh"
python_with_pyyaml - "$MANIFEST" "$PLUGIN/skills" "$PLUGIN" <<'PY'
import re
import sys
from pathlib import Path

import yaml

manifest = yaml.safe_load(Path(sys.argv[1]).read_text(encoding="utf-8")) or {}
plugin_skills = Path(sys.argv[2])
plugin_root = Path(sys.argv[3]).resolve()
declared = set((manifest.get("product") or {}).get("skills") or [])
actual = {path.name for path in plugin_skills.iterdir() if path.is_dir()}
errors = []

if declared != actual:
    errors.append(
        "parité manifeste/plugin rompue : "
        f"déclarés={sorted(declared)} livrés={sorted(actual)}"
    )

for skill in sorted(actual):
    if not (plugin_skills / skill / "SKILL.md").is_file():
        errors.append(f"SKILL.md manquant : {skill}")

relative_link = re.compile(r"\]\(\s*(?:<([^>]+)>|([^\s)]+))")
personal_path = re.compile(r"(?:/Users/|/home/|[A-Za-z]:\\\\Users\\\\)")
for path in plugin_root.rglob("*"):
    if not path.is_file() or path.is_symlink():
        if path.is_symlink():
            errors.append(f"lien symbolique interdit : {path.relative_to(plugin_root)}")
        continue
    try:
        content = path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        continue
    if personal_path.search(content):
        errors.append(f"chemin personnel détecté : {path.relative_to(plugin_root)}")
    for match in relative_link.finditer(content):
        target = (match.group(1) or match.group(2) or "").split("#", 1)[0]
        if not target.startswith("../"):
            continue
        resolved = (path.parent / target).resolve()
        try:
            resolved.relative_to(plugin_root)
        except ValueError:
            errors.append(f"lien hors plugin : {path.relative_to(plugin_root)} -> {target}")
            continue
        if not resolved.exists():
            errors.append(f"lien relatif cassé : {path.relative_to(plugin_root)} -> {target}")

if errors:
    for error in errors:
        print(f"[FAIL] {error}", file=sys.stderr)
    raise SystemExit(1)
print(f"[OK] parité et références du plugin : {len(actual)} skills")
PY

SKILL_COUNT="$(find "$PLUGIN/skills" -mindepth 1 -maxdepth 1 -type d | wc -l | tr -d ' ')"
DATE="$(date -u +%Y-%m-%dT%H:%M:%SZ)"
README_DATE="$DATE" \
README_COMMIT="$COMMIT" \
README_TREE_STATE="$TREE_STATE" \
README_VERSION="$VERSION" \
README_SKILL_COUNT="$SKILL_COUNT" \
README_PATH="$PLUGIN/README.md" \
python3 - <<'PY'
import os
from pathlib import Path

text = """# DSFR Agentic Kit — plugin

Plugin dérivé le __DATE__ depuis le commit `__COMMIT__` (arbre __TREE_STATE__),
version `__VERSION__`.

## Contenu

Les __SKILL_COUNT__ skills de `.claude/skills` sont disponibles sous le préfixe
`dsfr-agentic-kit:`. Les références partagées sont embarquées dans le même
répertoire afin que les renvois relatifs restent internes au plugin.

## Limites

Le plugin ne porte ni les contrôles `scripts/*.sh`, ni le profil
`design-systems/dsfr`, ni le paquet officiel `@gouvfr/dsfr`. Pour une
vérification complète, conserver le dépôt cloné et utiliser le plugin comme
point d’accès natif aux skills.

Un skill chargé ne constitue pas une preuve de conformité DSFR ou RGAA.

## Mise à jour

Après un `git pull --ff-only` vérifié du kit, reconstruire l’archive avec une
nouvelle version, puis la réinstaller. La version est un signal de cache : elle
doit changer avec chaque publication de l’archive.
"""

for key in ("DATE", "COMMIT", "TREE_STATE", "VERSION", "SKILL_COUNT"):
    text = text.replace(f"__{key}__", os.environ[f"README_{key}"])

Path(os.environ["README_PATH"]).write_text(text, encoding="utf-8")
PY

ARCHIVE="$BUILD/dsfr-agentic-kit.plugin"
(cd "$PLUGIN" && zip -qr "$ARCHIVE" . -x '*.DS_Store')

python3 - "$ARCHIVE" "$SKILL_COUNT" <<'PY'
import json
import sys
import zipfile

archive = sys.argv[1]
expected_skills = int(sys.argv[2])
with zipfile.ZipFile(archive) as package:
    names = set(package.namelist())
    if ".claude-plugin/plugin.json" not in names:
        raise SystemExit("[FAIL] plugin.json absent de l’archive")
    if any(".." in name.split("/") for name in names):
        raise SystemExit("[FAIL] chemin parent présent dans l’archive")
    manifest = json.loads(package.read(".claude-plugin/plugin.json"))
    skills = {
        name.split("/")[1]
        for name in names
        if name.startswith("skills/") and name.count("/") == 2 and name.endswith("/SKILL.md")
    }
    if len(skills) != expected_skills:
        raise SystemExit(
            f"[FAIL] skills dans l’archive : attendu={expected_skills} observé={len(skills)}"
        )
    print(f"[OK] archive plugin valide : {manifest['name']} {manifest['version']}, {len(skills)} skills")
PY

if [[ -e "$OUTPUT" ]]; then
  printf "[WARN] remplacement de l’archive existante : %s\n" "$OUTPUT"
fi
mv -f "$ARCHIVE" "$OUTPUT"
ok "plugin écrit : $OUTPUT"
printf '     provenance : commit %s, arbre %s\n' "$COMMIT" "$TREE_STATE"
