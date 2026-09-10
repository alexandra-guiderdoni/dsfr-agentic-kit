#!/usr/bin/env bash
set -euo pipefail
export PYTHONDONTWRITEBYTECODE=1

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
STOP_AFTER_PRODUCT_TESTS=0
WORKSPACE_ARG=""

usage() {
  printf 'Usage : %s [WORKSPACE] [--stop-after-product-tests]\n' "${BASH_SOURCE[0]}"
}

for arg in "$@"; do
  case "$arg" in
    --stop-after-product-tests)
      STOP_AFTER_PRODUCT_TESTS=1
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      if [[ -n "$WORKSPACE_ARG" ]]; then
        printf '[FAIL] argument inattendu : %s\n' "$arg" >&2
        usage >&2
        exit 2
      fi
      WORKSPACE_ARG="$arg"
      ;;
  esac
done

WORKSPACE="${WORKSPACE_ARG:-$(cd "$SCRIPT_DIR/.." && pwd)}"
WORKSPACE="$(cd "$WORKSPACE" && pwd)"
MANIFEST="$WORKSPACE/config/agentic-design-packages.yaml"

# shellcheck source=lib/python-with-pyyaml.sh
. "$SCRIPT_DIR/lib/python-with-pyyaml.sh"

failures=0
ok() { printf '[OK] %s\n' "$*"; }
warn() { printf '[WARN] %s\n' "$*"; }
fail() { printf '[FAIL] %s\n' "$*" >&2; failures=$((failures + 1)); }

# Les suites Python peuvent laisser des caches transitoires malgré le garde
# d’environnement. Ils ne font pas partie du kit livré et doivent être retirés
# avant les contrôles qui vérifient précisément leur absence.
clean_runtime_artifacts() {
  local root
  for root in "$WORKSPACE/.claude" "$WORKSPACE/design-systems" "$WORKSPACE/scripts"; do
    [[ -d "$root" ]] || continue
    find "$root" -type d -name '__pycache__' -prune -exec rm -rf -- {} + 2>/dev/null || true
    find "$root" -type f -name '*.pyc' -delete 2>/dev/null || true
  done
}

run_check() {
  local label="$1"
  shift
  printf '[RUN] %s\n' "$label"
  if "$@"; then
    ok "$label"
  else
    fail "$label"
  fi
}

[[ -d "$WORKSPACE" ]] || { printf '[FAIL] répertoire absent : %s\n' "$WORKSPACE" >&2; exit 1; }
[[ -f "$MANIFEST" ]] || { printf '[FAIL] manifeste absent : %s\n' "$MANIFEST" >&2; exit 1; }
clean_runtime_artifacts

run_check "frontière standalone" bash "$SCRIPT_DIR/tests/check-standalone-boundary.sh" "$WORKSPACE"
run_check "prérequis" bash "$SCRIPT_DIR/check-prerequisites.sh" --quiet

inventory=""
if inventory="$(WORKSPACE="$WORKSPACE" MANIFEST="$MANIFEST" python_with_pyyaml - <<'PY'
import os
import sys
from pathlib import Path

import yaml

workspace = Path(os.environ["WORKSPACE"])
manifest_path = Path(os.environ["MANIFEST"])
manifest = yaml.safe_load(manifest_path.read_text(encoding="utf-8")) or {}
errors = []

if manifest.get("schema_version") != 1:
    errors.append("schema_version doit valoir 1")
if manifest.get("name") != "dsfr-agentic-kit":
    errors.append("name doit valoir dsfr-agentic-kit")

product = manifest.get("product") or {}
validation = manifest.get("validation") or {}
skills = product.get("skills") or []
required = product.get("required_paths") or []
tests = validation.get("product_tests") or []
markdown = validation.get("markdown") or []

for label, values in (
    ("product.skills", skills),
    ("product.required_paths", required),
    ("validation.product_tests", tests),
    ("validation.markdown", markdown),
):
    if not isinstance(values, list) or not values:
        errors.append(f"{label} doit être une liste non vide")
        continue
    if len(values) != len(set(values)):
        errors.append(f"{label} contient des doublons")

for rel in [*required, *tests, *markdown]:
    if not (workspace / rel).is_file():
        errors.append(f"fichier déclaré absent : {rel}")

if errors:
    for error in errors:
        print(f"[FAIL] manifeste : {error}", file=sys.stderr)
    raise SystemExit(1)

for rel in tests:
    print(f"TEST\t{rel}")
for rel in markdown:
    print(f"MARKDOWN\t{rel}")
PY
)"; then
  ok "manifeste consommateur"
else
  fail "manifeste consommateur"
fi

marketplace_manifest="$WORKSPACE/.claude-plugin/marketplace.json"
if [[ -f "$marketplace_manifest" ]]; then
  run_check "catalogue marketplace" python3 - "$marketplace_manifest" <<'PY'
import json
import sys
from pathlib import Path

data = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
assert data.get("name") == "dsfr-agentic"
assert isinstance(data.get("owner", {}).get("name"), str)
plugins = data.get("plugins")
assert isinstance(plugins, list) and len(plugins) == 1
plugin = plugins[0]
assert plugin.get("name") == "dsfr-agentic-kit"
source = plugin.get("source", {})
assert source.get("source") == "github"
assert source.get("repo") == "alexandra-guiderdoni/dsfr-agentic-kit"
assert source.get("ref") == "main"
assert plugin.get("strict") is False
assert plugin.get("skills") == ["./.claude/skills"]
PY
fi

tests=()
markdown=()
while IFS=$'\t' read -r kind rel; do
  [[ -n "$kind" && -n "$rel" ]] || continue
  case "$kind" in
    TEST) tests+=("$rel") ;;
    MARKDOWN) markdown+=("$rel") ;;
  esac
done <<<"$inventory"

shell_failures=0
while IFS= read -r -d '' file; do
  if ! bash -n "$file"; then
    shell_failures=$((shell_failures + 1))
  fi
done < <(find "$WORKSPACE" -type f -name '*.sh' -print0)
if (( shell_failures == 0 )); then
  ok "syntaxe Bash"
else
  fail "syntaxe Bash : $shell_failures fichier(s) invalide(s)"
fi

python_interpreters=()
for candidate in python3.10 python3.11 python3; do
  if command -v "$candidate" >/dev/null 2>&1; then
    python_interpreters+=("$candidate")
  fi
done

python_syntax_failed=0
if ((${#python_interpreters[@]} == 0)); then
  python_syntax_failed=1
  printf '[FAIL] syntaxe Python : aucun interpréteur disponible\n' >&2
fi
for interpreter in "${python_interpreters[@]}"; do
  if ! WORKSPACE="$WORKSPACE" "$interpreter" - <<'PY'
import os
import sys
from pathlib import Path

workspace = Path(os.environ["WORKSPACE"])
errors = []
for relative_root in (".claude", "design-systems", "scripts"):
    root = workspace / relative_root
    if not root.is_dir():
        continue
    for path in root.rglob("*.py"):
        if "__pycache__" in path.parts:
            continue
        try:
            compile(path.read_text(encoding="utf-8"), str(path), "exec")
        except Exception as exc:
            errors.append(f"{path.relative_to(workspace)}: {exc}")
for error in errors:
    print(f"[FAIL] syntaxe Python : {error}", file=sys.stderr)
raise SystemExit(1 if errors else 0)
PY
  then
    python_syntax_failed=1
  fi
done
if (( python_syntax_failed == 0 )); then
  ok "syntaxe Python (${python_interpreters[*]})"
else
  fail "syntaxe Python"
fi

accent_output=""
for rel in ${markdown[@]+"${markdown[@]}"}; do
  output="$(bash "$SCRIPT_DIR/check-accents.sh" "$WORKSPACE/$rel")"
  if [[ -n "$output" ]]; then
    accent_output+="$output"$'\n'
  fi
done
if [[ -n "$accent_output" ]]; then
  printf '%s' "$accent_output" >&2
  fail "accents des documents consommateurs"
elif (( ${#markdown[@]} == 0 )); then
  fail "accents : aucun document déclaré par le manifeste"
else
  ok "accents des documents consommateurs"
fi

run_check "profil DSFR" env AGENTIC_DESIGN_PACK_SKIP_SELF_TESTS=1 \
  bash "$SCRIPT_DIR/check-dsfr-design-system.sh" "$WORKSPACE"

for rel in ${tests[@]+"${tests[@]}"}; do
  run_check "test produit : $rel" bash "$WORKSPACE/$rel" "$WORKSPACE"
done

clean_runtime_artifacts

if (( STOP_AFTER_PRODUCT_TESTS )); then
  if (( failures > 0 )); then
    printf '[FAIL] tests produit : %d échec(s)\n' "$failures" >&2
    exit 1
  fi
  printf '[OK] tests produit\n'
  exit 0
fi

dsfr_version="$(sed -n 's/^package_version_ref: *"\{0,1\}\([0-9.]*\)"\{0,1\}.*/\1/p' "$WORKSPACE/design-systems/dsfr/tokens.yaml" | head -1)"
cache_root="${DSFR_OFFICIAL_CACHE_DIR:-$HOME/.cache/dsfr-official-cache}"
official_package="$cache_root/gouvfr-dsfr-$dsfr_version/package"
css_dir="$official_package/dist"

if [[ -n "$dsfr_version" && -d "$css_dir" ]]; then
  run_check "fidélité au paquet DSFR $dsfr_version" python3 \
    "$WORKSPACE/design-systems/scripts/check-dsfr-fidelity.py" \
    --version "$dsfr_version" --css-dir "$css_dir"
else
  warn "fidélité officielle non exercée : cache DSFR $dsfr_version absent ($css_dir)"
fi

if [[ -n "$dsfr_version" ]]; then
  run_check "sorties générées" env DSFR_OFFICIAL_CACHE_OFFLINE=1 PYTHONDONTWRITEBYTECODE=1 \
    python3 "$WORKSPACE/.claude/skills/dsfr-components/scripts/check_generated_outputs.py" \
    --official-version "$dsfr_version" --official-cache-dir "$cache_root"
else
  fail "version DSFR absente de tokens.yaml"
fi

run_check "démo de page assemblée" bash "$SCRIPT_DIR/demo-dsfr-assembled-page.sh" --quiet

if (( failures > 0 )); then
  printf '[FAIL] DSFR Agentic Kit standalone : %d échec(s)\n' "$failures" >&2
  exit 1
fi

printf '[OK] DSFR Agentic Kit standalone\n'
