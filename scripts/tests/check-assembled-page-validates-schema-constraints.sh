#!/usr/bin/env bash
set -euo pipefail

# Deux couches rejettent une config invalide : le schéma JSON d'abord
# (indexe les sections à 0, « sections/1 »), le garde du builder ensuite
# (« section 1 »). Les motifs acceptent les deux formes.

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WORKSPACE="$(cd "$SCRIPT_DIR/../.." && pwd)"
GENERATOR="$WORKSPACE/.claude/skills/dsfr-components/scripts/generate_assembled_page.py"

tmp_dir="$(mktemp -d "${TMPDIR:-/tmp}/assembled-schema-constraints.XXXXXX")"
cleanup() {
  rm -rf "$tmp_dir"
}
trap cleanup EXIT

expect_reject() {
  local config="$1"
  local pattern="$2"
  local label="$3"
  set +e
  python3 "$GENERATOR" --config-file "$config" --check \
    >"$tmp_dir/stdout" 2>"$tmp_dir/stderr"
  local rc=$?
  set -e
  if [[ "$rc" -ne 1 ]]; then
    printf '[FAIL] %s : expected exit code 1, got %s\n' "$label" "$rc" >&2
    sed -n '1,20p' "$tmp_dir/stdout" >&2
    sed -n '1,20p' "$tmp_dir/stderr" >&2
    exit 1
  fi
  if ! grep -qiE "$pattern" "$tmp_dir/stderr"; then
    printf '[FAIL] %s : error message does not mention %s\n' "$label" "$pattern" >&2
    sed -n '1,20p' "$tmp_dir/stderr" >&2
    exit 1
  fi
}

cat > "$tmp_dir/bad-align.json" <<'JSON'
{
  "title": "Align hors enum",
  "sections": [
    {"block": "content", "title": "Intro", "body_text": "Texte."},
    {"block": "buttons", "align": "danger", "items": [{"label": "Bouton"}]}
  ]
}
JSON
expect_reject "$tmp_dir/bad-align.json" "align" "buttons align hors enum"
expect_reject "$tmp_dir/bad-align.json" "section 1|sections/1" "erreur align cite la section fautive"

cat > "$tmp_dir/bad-heading.json" <<'JSON'
{
  "title": "Heading level invalide",
  "sections": [
    {"block": "content", "title": "Intro", "body_text": "Texte.", "heading_level": "abc"}
  ]
}
JSON
expect_reject "$tmp_dir/bad-heading.json" "heading_level" "heading_level non entier rejeté"

cat > "$tmp_dir/bad-ratio.json" <<'JSON'
{
  "title": "Ratio hors pattern",
  "sections": [
    {"block": "content", "title": "Intro", "body_text": "Texte."},
    {"block": "image", "src": "visuel.png", "alt": "", "ratio": "bad"}
  ]
}
JSON
expect_reject "$tmp_dir/bad-ratio.json" "ratio" "image ratio hors pattern"

cat > "$tmp_dir/duplicate-explicit-ids.json" <<'JSON'
{
  "title": "IDs explicites dupliqués",
  "sections": [
    {"block": "content", "title": "Intro", "body_text": "Texte."},
    {"block": "form", "title": "Form A", "fields": [{"type": "input", "label": "Email", "id": "email"}]},
    {"block": "form", "title": "Form B", "fields": [{"type": "input", "label": "Email", "id": "email"}]}
  ]
}
JSON
expect_reject "$tmp_dir/duplicate-explicit-ids.json" "dupliqu" "ids explicites dupliqués inter-formulaires"

cat > "$tmp_dir/valid.json" <<'JSON'
{
  "title": "Valeurs valides",
  "sections": [
    {"block": "content", "title": "Intro", "body_text": "Texte."},
    {"block": "buttons", "align": "center", "items": [{"label": "Bouton"}]},
    {"block": "image", "src": "visuel.png", "alt": "", "ratio": "16x9"},
    {"block": "form", "title": "Form A", "fields": [{"type": "input", "label": "Email"}]},
    {"block": "form", "title": "Form B", "fields": [{"type": "input", "label": "Email"}]}
  ]
}
JSON
if ! python3 "$GENERATOR" --config-file "$tmp_dir/valid.json" --check \
  >"$tmp_dir/stdout-ok" 2>"$tmp_dir/stderr-ok"; then
  printf '[FAIL] valid config was rejected\n' >&2
  sed -n '1,20p' "$tmp_dir/stderr-ok" >&2
  exit 1
fi

printf '[OK] schema constraints enforced at generation\n'
