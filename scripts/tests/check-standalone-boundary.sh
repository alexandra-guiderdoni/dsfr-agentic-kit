#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WORKSPACE="${1:-$(cd "$SCRIPT_DIR/../.." && pwd)}"
MANIFEST="$WORKSPACE/config/agentic-design-packages.yaml"
CHECK="$WORKSPACE/scripts/check-agentic-design-pack.sh"

failures=0
ok() { printf '[OK] %s\n' "$*"; }
fail() { printf '[FAIL] %s\n' "$*" >&2; failures=$((failures + 1)); }

nested_git="$(find "$WORKSPACE" -name .git -print -prune | grep -vxF "$WORKSPACE/.git" || true)"
if [[ -n "$nested_git" ]]; then
  printf '%s\n' "$nested_git" >&2
  fail "dépôt Git imbriqué dans le kit"
else
  ok "aucun dépôt Git imbriqué"
fi

for rel in \
  ".lor""iq" \
  ".agents" \
  ".verdent" \
  ".codegraph" \
  "AGENTS.md" \
  "CLAUDE.md" \
  "GEMINI.md" \
  "CONTRIBUTING.md" \
  "dist"; do
  if [[ -e "$WORKSPACE/$rel" ]]; then
    fail "surface interne livrée : $rel"
  fi
done

for prefix in "syn""c-" "pack""age-" "check-mirror-" "codex-harness-"; do
  while IFS= read -r path; do
    [[ -z "$path" ]] && continue
    fail "script de fabrication livré : ${path#"$WORKSPACE/"}"
  done < <(find "$WORKSPACE/scripts" -type f -name "$prefix*" -print 2>/dev/null)
done

marker_one="lor""iq"
marker_two="her""mes"
marker_three="PUB""-07"
marker_four='scripts/(syn'"c"'|pack'"age"')-'
marker_pattern="$marker_one|$marker_two|$marker_three|$marker_four|/Users/[[:alnum:]_.-]+/|/home/[[:alnum:]_.-]+/"
marker_hits="$(
  while IFS= read -r -d '' file; do
    grep -nEIH "$marker_pattern" "$file" 2>/dev/null | sed "s#^#$file:#" || true
  done < <(find "$WORKSPACE" -path "$WORKSPACE/.git" -prune -o -type f -print0)
)"
if [[ -n "$marker_hits" ]]; then
  printf '%s\n' "$marker_hits" | head -20 >&2
  fail "marqueur interne ou chemin personnel détecté"
else
  ok "aucun marqueur interne ni chemin personnel"
fi

symlinks="$(find "$WORKSPACE" -path "$WORKSPACE/.git" -prune -o -type l -print)"
if [[ -n "$symlinks" ]]; then
  printf '%s\n' "$symlinks" >&2
  fail "liens symboliques interdits dans l'export autonome"
else
  ok "aucun lien symbolique"
fi

runtime_residue="$(find "$WORKSPACE" -path "$WORKSPACE/.git" -prune -o \( -type d -name '__pycache__' -o -type f -name '*.pyc' \) -print)"
if [[ -n "$runtime_residue" ]]; then
  printf '%s\n' "$runtime_residue" >&2
  fail "résidu d'exécution Python livré"
else
  ok "aucun résidu d'exécution Python"
fi

if [[ ! -f "$MANIFEST" ]]; then
  fail "manifeste consommateur absent"
elif [[ ! -f "$CHECK" ]]; then
  fail "check standalone absent"
else
  # shellcheck source=../lib/python-with-pyyaml.sh
  . "$WORKSPACE/scripts/lib/python-with-pyyaml.sh"
  if WORKSPACE="$WORKSPACE" MANIFEST="$MANIFEST" python_with_pyyaml - <<'PY'
import os
import sys
from pathlib import Path

import yaml

workspace = Path(os.environ["WORKSPACE"])
manifest = yaml.safe_load(Path(os.environ["MANIFEST"]).read_text(encoding="utf-8")) or {}
expected = manifest.get("product", {}).get("skills", [])
actual = sorted(path.name for path in (workspace / ".claude/skills").iterdir() if path.is_dir())

if len(expected) != 14:
    print(f"[FAIL] manifeste : 14 skills attendus, {len(expected)} déclarés", file=sys.stderr)
    raise SystemExit(1)
if len(expected) != len(set(expected)):
    print("[FAIL] manifeste : skills dupliqués", file=sys.stderr)
    raise SystemExit(1)
if sorted(expected) != actual:
    print(f"[FAIL] parité skills : attendu={sorted(expected)} réel={actual}", file=sys.stderr)
    raise SystemExit(1)
print("[OK] parité exacte des 14 skills produit")
PY
  then
    ok "inventaire consommateur piloté par le manifeste"
  else
    fail "inventaire consommateur invalide"
  fi
fi

if (( failures > 0 )); then
  printf '[FAIL] frontière standalone : %d échec(s)\n' "$failures" >&2
  exit 1
fi
printf '[OK] frontière standalone\n'
