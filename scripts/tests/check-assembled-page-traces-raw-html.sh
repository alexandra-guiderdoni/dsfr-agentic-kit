#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WORKSPACE="$(cd "$SCRIPT_DIR/../.." && pwd)"
GENERATOR="$WORKSPACE/.claude/skills/dsfr-components/scripts/generate_assembled_page.py"

tmp_dir="$(mktemp -d "${TMPDIR:-/tmp}/assembled-raw-html-trace.XXXXXX")"
cleanup() {
  rm -rf "$tmp_dir"
}
trap cleanup EXIT

cat > "$tmp_dir/raw.json" <<'JSON'
{
  "title": "Test HTML brut tracé",
  "sections": [
    {"block": "content", "title": "Intro", "body_text": "Texte."},
    {"block": "content", "title": "Brut", "body": "<p>HTML relu par un humain.</p>", "allow_raw_html": true}
  ]
}
JSON

if ! python3 "$GENERATOR" --config-file "$tmp_dir/raw.json" --output "$tmp_dir/raw.html" \
  >"$tmp_dir/stdout" 2>"$tmp_dir/stderr"; then
  printf '[FAIL] allow_raw_html config was rejected (opt-in must keep working)\n' >&2
  sed -n '1,20p' "$tmp_dir/stderr" >&2
  exit 1
fi

if ! grep -qi "allow_raw_html" "$tmp_dir/raw.html"; then
  printf '[FAIL] generated HTML carries no allow_raw_html marker before raw content\n' >&2
  exit 1
fi

if ! grep -qi "allow_raw_html" "$tmp_dir/stderr"; then
  printf '[FAIL] generator emitted no allow_raw_html warning on stderr\n' >&2
  exit 1
fi

cat > "$tmp_dir/clean.json" <<'JSON'
{
  "title": "Test sans HTML brut",
  "sections": [
    {"block": "content", "title": "Intro", "body_text": "Texte."}
  ]
}
JSON

if ! python3 "$GENERATOR" --config-file "$tmp_dir/clean.json" --output "$tmp_dir/clean.html" \
  >"$tmp_dir/stdout-clean" 2>"$tmp_dir/stderr-clean"; then
  printf '[FAIL] clean config was rejected\n' >&2
  sed -n '1,20p' "$tmp_dir/stderr-clean" >&2
  exit 1
fi

if grep -qi "allow_raw_html" "$tmp_dir/clean.html"; then
  printf '[FAIL] clean HTML must not carry the allow_raw_html marker\n' >&2
  exit 1
fi

printf '[OK] raw html opt-in is traced, clean pages stay clean\n'
