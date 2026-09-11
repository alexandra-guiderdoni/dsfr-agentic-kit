#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WORKSPACE="$(cd "$SCRIPT_DIR/.." && pwd)"
EXAMPLE="vibe-coding-harnais-agentique"
OUT_DIR=""
PORT=8137
QUIET=0

usage() {
  cat <<'EOF'
Usage:
  bash scripts/demo-dsfr-vitrine.sh [--out-dir PATH] [--port PORT] [--quiet]

Generates a complete local DSFR showcase directory:
  index.html
  schema-harnais.svg
  assets/dsfr/

The DSFR asset cache must exist at:
  ${DSFR_OFFICIAL_CACHE_DIR:-$HOME/.cache/dsfr-official-cache}/gouvfr-dsfr-${DSFR_OFFICIAL_VERSION:-1.15.3}/package/dist

Run the DSFR package check first if the cache is missing.
EOF
}

fail() {
  printf '[FAIL] %s\n' "$*" >&2
  exit 1
}

ok() {
  if [[ "$QUIET" -eq 0 ]]; then
    printf '[OK] %s\n' "$*"
  fi
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
    --port)
      require_value "$1" "${2-}"
      PORT="${2:-}"
      shift 2
      ;;
    --port=*)
      PORT="${1#*=}"
      require_value "--port" "$PORT"
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

case "$PORT" in
  ''|*[!0-9]*)
    fail "--port must be a number"
    ;;
esac

if ! command -v rsync >/dev/null 2>&1; then
  fail "rsync is required"
fi

EXAMPLE_DIR="$WORKSPACE/.claude/skills/dsfr-components/examples/assembled/$EXAMPLE"
CONFIG="$EXAMPLE_DIR/page.json"
SCHEMA="$EXAMPLE_DIR/schema-harnais.svg"
PROOF="$EXAMPLE_DIR/preuve.md"
BUILDER="$WORKSPACE/.claude/skills/dsfr-components/scripts/generate_assembled_page.py"

[[ -f "$CONFIG" ]] || fail "missing page config: $CONFIG"
[[ -f "$SCHEMA" ]] || fail "missing SVG schema: $SCHEMA"
[[ -f "$PROOF" ]] || fail "missing proof note: $PROOF"
[[ -f "$BUILDER" ]] || fail "missing builder: $BUILDER"
command -v python3 >/dev/null 2>&1 || fail "python3 introuvable dans le PATH"

DSFR_CACHE_ROOT="${DSFR_OFFICIAL_CACHE_DIR:-$HOME/.cache/dsfr-official-cache}"
DSFR_VERSION="${DSFR_OFFICIAL_VERSION:-1.15.3}"
DSFR_DIST="$DSFR_CACHE_ROOT/gouvfr-dsfr-$DSFR_VERSION/package/dist"
if [[ ! -d "$DSFR_DIST" ]]; then
  fail "DSFR asset cache missing: $DSFR_DIST. Run: bash scripts/check-agentic-design-pack.sh"
fi

if [[ -z "$OUT_DIR" ]]; then
  TMP_BASE="${TMPDIR:-/tmp}"
  TMP_BASE="${TMP_BASE%/}"
  OUT_DIR="$(mktemp -d "$TMP_BASE/agentic-design-vitrine.XXXXXX")"
  # Répertoire temporaire : nettoyé à la sortie, y compris sur erreur.
  trap 'rm -rf "$OUT_DIR"' EXIT INT TERM
else
  mkdir -p "$OUT_DIR"
  if find "$OUT_DIR" -mindepth 1 -print -quit | grep -q .; then
    fail "out directory must be empty: $OUT_DIR"
  fi
fi

HTML="$OUT_DIR/index.html"
ASSETS="$OUT_DIR/assets/dsfr"

cp "$SCHEMA" "$OUT_DIR/schema-harnais.svg"
mkdir -p "$ASSETS"
rsync -a "$DSFR_DIST/" "$ASSETS/"
python3 "$BUILDER" --config-file "$CONFIG" --check >/dev/null
python3 "$BUILDER" --config-file "$CONFIG" --output "$HTML" >/dev/null

[[ -f "$HTML" ]] || fail "HTML not generated: $HTML"
[[ -f "$OUT_DIR/schema-harnais.svg" ]] || fail "SVG not copied"
[[ -f "$ASSETS/dsfr.min.css" ]] || fail "DSFR CSS not copied"
[[ -f "$ASSETS/dsfr.module.min.js" ]] || fail "DSFR module JS not copied"

if grep -q 'cdn.jsdelivr' "$HTML"; then
  fail "unexpected CDN reference in generated HTML"
fi
if ! grep -q 'assets/dsfr/dsfr.min.css' "$HTML"; then
  fail "generated HTML does not reference local DSFR CSS"
fi
if ! grep -q 'schema-harnais.svg' "$HTML"; then
  fail "generated HTML does not reference schema-harnais.svg"
fi
if grep -q 'fr-ratio-' "$HTML"; then
  fail "SVG image must not be wrapped in a DSFR ratio class"
fi

ok "vitrine DSFR générée"
printf 'dir=%s\n' "$OUT_DIR"
printf 'html=%s\n' "$HTML"
printf 'proof=%s\n' "$PROOF"
printf 'server=cd %q && python3 -m http.server %s --bind 127.0.0.1\n' "$OUT_DIR" "$PORT"
printf 'url=http://127.0.0.1:%s/index.html\n' "$PORT"
