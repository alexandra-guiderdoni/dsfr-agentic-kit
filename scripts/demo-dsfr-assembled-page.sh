#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WORKSPACE="$(cd "$SCRIPT_DIR/.." && pwd)"
EXAMPLE="prise-en-main-agent"
OUTPUT=""
OUT_DIR=""
QUIET=0

usage() {
  cat <<'EOF'
Usage:
  bash scripts/demo-dsfr-assembled-page.sh [--example NAME] [--out-dir PATH] [--quiet]
  bash scripts/demo-dsfr-assembled-page.sh [--example NAME] --output PATH [--quiet]

Options:
  --quiet: sortie minimale (chemins seulement, sans narration)

Defaults:
  --example: prise-en-main-agent
  --out-dir: a new temporary directory under $TMPDIR or /tmp

The demo reads:
  .claude/skills/dsfr-components/examples/assembled/<example>/brief.md
  .claude/skills/dsfr-components/examples/assembled/<example>/page.json
  .claude/skills/dsfr-components/examples/assembled/<example>/preuve.md

It writes one generated HTML file outside the repository by default.
EOF
}

fail() {
  printf '[FAIL] %s\n' "$*" >&2
  exit 1
}

require_value() {
  local option="$1"
  local value="${2-}"
  if [[ -z "$value" ]]; then
    fail "$option requires a value"
  fi
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --example)
      require_value "$1" "${2-}"
      EXAMPLE="${2:-}"
      shift 2
      ;;
    --example=*)
      EXAMPLE="${1#*=}"
      require_value "--example" "$EXAMPLE"
      shift
      ;;
    --out-dir)
      require_value "$1" "${2-}"
      OUT_DIR="${2:-}"
      shift 2
      ;;
    --out-dir=*)
      OUT_DIR="${1#*=}"
      require_value "--out-dir" "$OUT_DIR"
      shift
      ;;
    --output)
      require_value "$1" "${2-}"
      OUTPUT="${2:-}"
      shift 2
      ;;
    --output=*)
      OUTPUT="${1#*=}"
      require_value "--output" "$OUTPUT"
      shift
      ;;
    --quiet)
      QUIET=1
      shift
      ;;
    --help|-h)
      usage
      exit 0
      ;;
    *)
      fail "unexpected argument: $1"
      ;;
  esac
done

if [[ -n "$OUTPUT" && -n "$OUT_DIR" ]]; then
  fail "--output and --out-dir are mutually exclusive"
fi

EXAMPLE_DIR="$WORKSPACE/.claude/skills/dsfr-components/examples/assembled/$EXAMPLE"
BRIEF="$EXAMPLE_DIR/brief.md"
CONFIG="$EXAMPLE_DIR/page.json"
PROOF="$EXAMPLE_DIR/preuve.md"
SCHEMA_CHECK="$WORKSPACE/.claude/skills/dsfr-components/scripts/check_assembled_page_schema.py"
BUILDER="$WORKSPACE/.claude/skills/dsfr-components/scripts/generate_assembled_page.py"

[[ -f "$BRIEF" ]] || fail "missing brief: $BRIEF"
[[ -f "$CONFIG" ]] || fail "missing page config: $CONFIG"
[[ -f "$PROOF" ]] || fail "missing proof note: $PROOF"
[[ -f "$SCHEMA_CHECK" ]] || fail "missing schema check: $SCHEMA_CHECK"
[[ -f "$BUILDER" ]] || fail "missing builder: $BUILDER"
command -v python3 >/dev/null 2>&1 || fail "python3 introuvable dans le PATH"

if [[ -z "$OUTPUT" ]]; then
  if [[ -z "$OUT_DIR" ]]; then
    TMP_BASE="${TMPDIR:-/tmp}"
    TMP_BASE="${TMP_BASE%/}"
    OUT_DIR="$(mktemp -d "$TMP_BASE/agentic-design-dsfr-demo.XXXXXX")"
    # Répertoire temporaire : nettoyé à la sortie, y compris sur erreur.
    trap 'rm -rf "$OUT_DIR"' EXIT INT TERM
  else
    mkdir -p "$OUT_DIR"
  fi
  OUTPUT="$OUT_DIR/$EXAMPLE.html"
else
  output_dir="$(dirname "$OUTPUT")"
  [[ -d "$output_dir" ]] || fail "output directory does not exist: $output_dir"
fi

if [[ -e "$OUTPUT" ]]; then
  fail "output already exists: $OUTPUT"
fi

run_step() {
  local label="$1"
  shift
  if [[ "$QUIET" -eq 1 ]]; then
    local log_file
    log_file="$(mktemp "${TMPDIR:-/tmp}/agentic-design-dsfr-demo-log.XXXXXX")"
    if "$@" >"$log_file" 2>&1; then
      rm -f "$log_file"
      printf '[OK] %s\n' "$label"
    else
      cat "$log_file" >&2
      rm -f "$log_file"
      fail "$label"
    fi
  else
    printf '[RUN] %s\n' "$label"
    "$@"
    printf '[OK] %s\n' "$label"
  fi
}

inspect_html() {
  python3 - "$OUTPUT" <<'PY'
from html.parser import HTMLParser
from pathlib import Path
import sys

path = Path(sys.argv[1])
html = path.read_text(encoding="utf-8")

class Facts(HTMLParser):
    def __init__(self):
        super().__init__()
        self.ids = set()
        self.fragment_hrefs = []
        self.main_seen = False
        self.footer_seen = False
        self.h1_count = 0
        self.main_depth = 0

    def handle_starttag(self, tag, attrs):
        data = dict(attrs)
        if data.get("id"):
            self.ids.add(data["id"])
        href = data.get("href")
        if href and href.startswith("#"):
            self.fragment_hrefs.append(href[1:])
        if tag == "main":
            self.main_seen = True
            self.main_depth += 1
        if tag == "footer":
            self.footer_seen = True
        if tag == "h1" and self.main_depth > 0:
            self.h1_count += 1

    def handle_endtag(self, tag):
        if tag == "main":
            self.main_depth = max(0, self.main_depth - 1)

facts = Facts()
facts.feed(html)
errors = []
if 'href="#"' in html:
    errors.append('href="#" présent')
missing = sorted(ref for ref in facts.fragment_hrefs if ref and ref not in facts.ids)
if missing:
    errors.append("ancres sans cible: " + ", ".join(missing[:10]))
if not facts.main_seen:
    errors.append("main absent")
if not facts.footer_seen:
    errors.append("footer absent")
if facts.h1_count != 1:
    errors.append(f"h1 dans main attendu une fois, observé {facts.h1_count}")
if errors:
    raise SystemExit("; ".join(errors))
print(f"OK : page HTML inspectée ({path}, {len(html)} caractères)")
PY
}

if [[ "$QUIET" -eq 0 ]]; then
  printf '[INFO] workspace: %s\n' "$WORKSPACE"
  printf '[INFO] brief: %s\n' "$BRIEF"
  printf '[INFO] config: %s\n' "$CONFIG"
  printf '[INFO] proof: %s\n' "$PROOF"
fi

run_step "JSON Schema examples" python3 "$SCHEMA_CHECK" --schema-only
run_step "builder check" python3 "$BUILDER" --config-file "$CONFIG" --check
run_step "HTML generation" python3 "$BUILDER" --config-file "$CONFIG" --output "$OUTPUT"
run_step "HTML inspection" inspect_html

printf '[OK] demo DSFR assemblée\n'
printf 'brief=%s\n' "$BRIEF"
printf 'config=%s\n' "$CONFIG"
printf 'output=%s\n' "$OUTPUT"
printf 'proof=%s\n' "$PROOF"
