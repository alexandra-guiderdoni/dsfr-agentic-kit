#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WORKSPACE="$(cd "$SCRIPT_DIR/../.." && pwd)"
CHECK_SCRIPT="$WORKSPACE/scripts/check-dsfr-design-router.py"
BASE_DSFR="$WORKSPACE/design-systems/dsfr"

tmp_dir="$(mktemp -d "${TMPDIR:-/tmp}/dsfr-router-routes.XXXXXX")"
cleanup() {
  rm -rf "$tmp_dir"
}
trap cleanup EXIT

copy_case() {
  local name="$1"
  local case_dir="$tmp_dir/$name"
  mkdir -p "$case_dir/design-systems"
  cp -R "$BASE_DSFR" "$case_dir/design-systems/dsfr"
  printf '%s\n' "$case_dir"
}

insert_route() {
  local design="$1"
  local line="$2"
  awk -v insert="$line" '
    { print }
    $0 == "  load_when_needed:" { print insert }
  ' "$design" > "$design.tmp"
  mv "$design.tmp" "$design"
}

replace_route_block() {
  local design="$1"
  local replacement="$2"
  awk -v replacement="$replacement" '
    $0 == "  load_when_needed:" {
      print replacement
      in_block = 1
      next
    }
    in_block && $0 ~ /^    / { next }
    { in_block = 0; print }
  ' "$design" > "$design.tmp"
  mv "$design.tmp" "$design"
}

assert_nominal() {
  local case_dir
  case_dir="$(copy_case nominal)"
  set +e
  python3 "$CHECK_SCRIPT" --workspace "$case_dir" > "$case_dir/stdout" 2> "$case_dir/stderr"
  local rc=$?
  set -e
  if [[ "$rc" -ne 0 ]]; then
    printf '[FAIL] nominal routeur DSFR expected rc 0, got %s\n' "$rc" >&2
    sed -n '1,120p' "$case_dir/stdout" >&2
    sed -n '1,80p' "$case_dir/stderr" >&2
    exit 1
  fi
}

assert_invalid() {
  local name="$1"
  local expected="$2"
  local case_dir="$tmp_dir/$name"

  set +e
  python3 "$CHECK_SCRIPT" --workspace "$case_dir" > "$case_dir/stdout" 2> "$case_dir/stderr"
  local rc=$?
  set -e

  if [[ "$rc" -eq 0 ]]; then
    printf '[FAIL] %s expected failure, got rc 0\n' "$name" >&2
    sed -n '1,120p' "$case_dir/stdout" >&2
    sed -n '1,80p' "$case_dir/stderr" >&2
    exit 1
  fi

  if grep -q 'Traceback' "$case_dir/stdout" "$case_dir/stderr"; then
    printf '[FAIL] %s leaked Python traceback\n' "$name" >&2
    sed -n '1,120p' "$case_dir/stdout" >&2
    sed -n '1,80p' "$case_dir/stderr" >&2
    exit 1
  fi

  if ! grep -Fq "$expected" "$case_dir/stdout"; then
    printf '[FAIL] %s missing expected message: %s\n' "$name" "$expected" >&2
    sed -n '1,120p' "$case_dir/stdout" >&2
    sed -n '1,80p' "$case_dir/stderr" >&2
    exit 1
  fi
}

insert_case() {
  local name="$1"
  local route_line="$2"
  local expected="$3"
  local case_dir
  case_dir="$(copy_case "$name")"
  insert_route "$case_dir/design-systems/dsfr/DESIGN.md" "$route_line"
  assert_invalid "$name" "$expected"
}

replace_case() {
  local name="$1"
  local replacement="$2"
  local expected="$3"
  local case_dir
  case_dir="$(copy_case "$name")"
  replace_route_block "$case_dir/design-systems/dsfr/DESIGN.md" "$replacement"
  assert_invalid "$name" "$expected"
}

assert_nominal
replace_case "not_object" '  load_when_needed: "references/page-shell.md"' "load_when_needed doit être un objet"
insert_case "nonstring_key" '    1: "references/one.md"' "load_when_needed clé non string"
insert_case "empty_key" '    "": "references/empty.md"' "load_when_needed clé vide"
insert_case "invalid_key" '    bad-key: "references/page-shell.md"' "load_when_needed clé invalide"
insert_case "nonstring_value" '    bad_number: 42' "route bad_number: valeur non string"
insert_case "empty_value" '    empty_value: ""' "route empty_value: valeur vide"
insert_case "absolute" '    absolute: "/tmp/secret.md"' "route absolute: chemin absolu interdit"
insert_case "escape" '    escape: "../secret.md"' "route escape: chemin parent interdit"
insert_case "backslash" "    backslash: 'references/..\\\\secret.md'" "route backslash: backslash interdit"
insert_case "outside" '    outside: "tokens.yaml"' "route outside: chemin hors references/*.md"

printf '[OK] DSFR load_when_needed route validation\n'
