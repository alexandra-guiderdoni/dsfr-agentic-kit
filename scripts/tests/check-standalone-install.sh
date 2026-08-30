#!/usr/bin/env bash
set -euo pipefail

# Exerce le kit depuis une copie isolée et un projet voisin vierge. Ce test
# vérifie l'installation, la génération et un pré-audit structurel déterministe ;
# il ne revendique ni conformité DSFR ni conformité RGAA.

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WORKSPACE="${1:-$(cd "$SCRIPT_DIR/../.." && pwd)}"
TMP_BASE="${TMPDIR:-/tmp}"
TMP_BASE="${TMP_BASE%/}"
TMP_ROOT="$(mktemp -d "$TMP_BASE/dsfr-agentic-kit-install.XXXXXX")"
KIT_COPY="$TMP_ROOT/dsfr-agentic-kit"
PROJECT="$TMP_ROOT/projet-vierge"

cleanup() {
  if [[ -n "${TMP_ROOT:-}" && -d "$TMP_ROOT" ]]; then
    rm -rf -- "$TMP_ROOT"
  fi
}
trap cleanup EXIT INT TERM

fail() { printf '[FAIL] %s\n' "$*" >&2; exit 1; }
ok() { printf '[OK] %s\n' "$*"; }

fingerprint() {
  ROOT="$1" python3 - <<'PY'
import hashlib
import os
from pathlib import Path

root = Path(os.environ["ROOT"])
digest = hashlib.sha256()
for path in sorted(root.rglob("*"), key=lambda item: item.as_posix()):
    if ".git" in path.relative_to(root).parts:
        continue
    rel = path.relative_to(root).as_posix().encode()
    if path.is_symlink():
        digest.update(b"L\0" + rel + b"\0" + os.readlink(path).encode() + b"\0")
    elif path.is_file():
        digest.update(b"F\0" + rel + b"\0" + hashlib.sha256(path.read_bytes()).digest())
print(digest.hexdigest())
PY
}

[[ -f "$WORKSPACE/config/agentic-design-packages.yaml" ]] || fail "kit source invalide"
command -v python3 >/dev/null 2>&1 || fail "python3 absent"

original_before="$(fingerprint "$WORKSPACE")"
SOURCE_KIT="$WORKSPACE" KIT_COPY="$KIT_COPY" python3 - <<'PY'
import os
import shutil
from pathlib import Path

source = Path(os.environ["SOURCE_KIT"])
destination = Path(os.environ["KIT_COPY"])
shutil.copytree(
    source,
    destination,
    ignore=shutil.ignore_patterns(".git", "__pycache__", "*.pyc"),
)
PY
mkdir -p "$PROJECT"

[[ ! -d "$KIT_COPY/.git" ]] || fail "la copie isolée contient un dépôt Git"
copy_before="$(fingerprint "$KIT_COPY")"

example="$KIT_COPY/.claude/skills/dsfr-components/examples/assembled/prise-en-main-agent"
cp "$example/brief.md" "$PROJECT/brief.md"
cp "$example/page.json" "$PROJECT/page.json"

schema_check="$KIT_COPY/.claude/skills/dsfr-components/scripts/check_assembled_page_schema.py"
builder="$KIT_COPY/.claude/skills/dsfr-components/scripts/generate_assembled_page.py"

(
  cd "$PROJECT"
  PYTHONDONTWRITEBYTECODE=1 python3 "$schema_check" --schema-only >/dev/null
  PYTHONDONTWRITEBYTECODE=1 python3 "$builder" --config-file page.json --check >/dev/null
  PYTHONDONTWRITEBYTECODE=1 python3 "$builder" --config-file page.json --output page.html >/dev/null
)

[[ -s "$PROJECT/page.html" ]] || fail "page HTML non générée dans le projet voisin"
[[ -f "$KIT_COPY/.claude/skills/pre-audit-rgaa-dsfr/SKILL.md" ]] || fail "route de pré-audit absente"
[[ -f "$KIT_COPY/.claude/skills/audit-rgaa-dsfr/SKILL.md" ]] || fail "route d'audit RGAA absente"

PAGE="$PROJECT/page.html" python3 - <<'PY'
import os
from html.parser import HTMLParser
from pathlib import Path


class Structure(HTMLParser):
    def __init__(self):
        super().__init__()
        self.ids = []
        self.html_lang = ""
        self.main = 0
        self.footer = 0
        self.h1 = 0
        self.title = 0
        self.hrefs = []

    def handle_starttag(self, tag, attrs):
        values = dict(attrs)
        if values.get("id"):
            self.ids.append(values["id"])
        if values.get("href"):
            self.hrefs.append(values["href"])
        if tag == "html":
            self.html_lang = values.get("lang", "")
        elif tag == "main":
            self.main += 1
        elif tag == "footer":
            self.footer += 1
        elif tag == "h1":
            self.h1 += 1
        elif tag == "title":
            self.title += 1


page = Path(os.environ["PAGE"])
facts = Structure()
facts.feed(page.read_text(encoding="utf-8"))
errors = []
if not facts.html_lang.startswith("fr"):
    errors.append("langue française absente")
if facts.title != 1:
    errors.append(f"title attendu une fois, observé {facts.title}")
if facts.main != 1:
    errors.append(f"main attendu une fois, observé {facts.main}")
if facts.footer != 1:
    errors.append(f"footer attendu une fois, observé {facts.footer}")
if facts.h1 != 1:
    errors.append(f"h1 attendu une fois, observé {facts.h1}")
if len(facts.ids) != len(set(facts.ids)):
    errors.append("IDs dupliqués")
unsafe = [href for href in facts.hrefs if href.lower().startswith(("javascript:", "data:", "vbscript:"))]
if unsafe:
    errors.append("href dangereux détecté")
if errors:
    raise SystemExit("; ".join(errors))
PY
ok "pré-audit structurel de la page générée"

copy_after="$(fingerprint "$KIT_COPY")"
original_after="$(fingerprint "$WORKSPACE")"
[[ "$copy_before" == "$copy_after" ]] || fail "la génération a modifié la copie du kit"
[[ "$original_before" == "$original_after" ]] || fail "le test a modifié le kit d'origine"

ok "génération depuis un projet voisin vierge"
ok "kit inchangé après utilisation"
printf '[OK] installation standalone isolée\n'
