#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WORKSPACE="${1:-$(cd "$SCRIPT_DIR/../.." && pwd)}"
# Un slash final ferait echouer la comparaison exacte avec "$WORKSPACE/.git" :
# le depot lui-meme serait signale comme imbrique et son elagage desactive.
WORKSPACE="${WORKSPACE%/}"
[[ -n "$WORKSPACE" ]] || WORKSPACE="/"
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
# Périmètre du contrôle : ce que le dépôt livre réellement.
# Dans un dépôt Git, seuls les fichiers suivis sont contrôlés — un fichier
# ignoré (.env.local, archives/, __pycache__) n'est jamais publié et n'a donc
# pas à faire échouer la frontière. Hors dépôt Git (export autonome déjà
# détaché), tout l'arbre est contrôlé : il n'y a plus d'index pour arbitrer.
delivered_files() {
  if git -C "$WORKSPACE" rev-parse --is-inside-work-tree >/dev/null 2>&1; then
    git -C "$WORKSPACE" ls-files -z | while IFS= read -r -d '' rel; do
      printf '%s\0' "$WORKSPACE/$rel"
    done
  else
    find "$WORKSPACE" -path "$WORKSPACE/.git" -prune -o -type f -print0
  fi
}

# « head -20 <<< » et non « printf | head -20 » : au-delà du tampon de tube
# (~64 Kio), head se ferme avant la fin de l'écriture, printf reçoit SIGPIPE
# et, sous « set -o pipefail », le script meurt en 141 sans exécuter les
# contrôles suivants ni afficher son verdict.
extrait() { head -20 <<<"$1" >&2; }

# grep -H préfixe déjà chaque ligne du chemin : un sed supplémentaire le
# dupliquait, et un « # » dans un chemin y faisait disparaître toutes les
# correspondances sans le moindre message.
marker_hits="$(
  while IFS= read -r -d '' file; do
    [[ -f "$file" ]] || continue
    grep -nEIH "$marker_pattern" "$file" 2>/dev/null || true
  done < <(delivered_files)
)"
if [[ -n "$marker_hits" ]]; then
  extrait "$marker_hits"
  fail "marqueur interne ou chemin personnel détecté"
else
  ok "aucun marqueur interne ni chemin personnel"
fi

symlinks="$(
  while IFS= read -r -d '' file; do
    [[ -L "$file" ]] && printf '%s\n' "$file"
  done < <(delivered_files)
  true
)"
if [[ -n "$symlinks" ]]; then
  extrait "$symlinks"
  fail "liens symboliques interdits dans l'export autonome"
else
  ok "aucun lien symbolique"
fi

runtime_residue="$(
  while IFS= read -r -d '' file; do
    if [[ "$file" == */__pycache__/* || "$file" == *.pyc ]]; then
      printf '%s\n' "$file"
    fi
  done < <(delivered_files)
  true
)"
if [[ -n "$runtime_residue" ]]; then
  extrait "$runtime_residue"
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

if not expected:
    print("[FAIL] manifeste : aucun skill déclaré", file=sys.stderr)
    raise SystemExit(1)
if len(expected) != len(set(expected)):
    print("[FAIL] manifeste : skills dupliqués", file=sys.stderr)
    raise SystemExit(1)
if sorted(expected) != actual:
    print(f"[FAIL] parité skills : attendu={sorted(expected)} réel={actual}", file=sys.stderr)
    raise SystemExit(1)
print(f"[OK] parité exacte des {len(expected)} skills produit")
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
