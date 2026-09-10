#!/usr/bin/env bash
set -euo pipefail

# Vérifie que les skills produit restent utilisables quel que soit leur dossier
# d'installation. Une commande interne doit partir de SKILL_DIR, jamais d'un
# chemin figé .claude/skills/<skill>/<sous-chemin>.

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WORKSPACE="${1:-$(cd "$SCRIPT_DIR/../.." && pwd)}"
MANIFEST="$WORKSPACE/config/agentic-design-packages.yaml"
[[ -f "$MANIFEST" ]] || { printf '[FAIL] manifeste absent : %s\n' "$MANIFEST" >&2; exit 1; }

# shellcheck source=../lib/python-with-pyyaml.sh
. "$WORKSPACE/scripts/lib/python-with-pyyaml.sh"

skills=()
while IFS= read -r skill; do
  [[ -n "$skill" ]] && skills+=("$skill")
done < <(MANIFEST="$MANIFEST" python_with_pyyaml - <<'PY'
import os
from pathlib import Path

import yaml

manifest = yaml.safe_load(Path(os.environ["MANIFEST"]).read_text(encoding="utf-8")) or {}

# Deux formes coexistent : product.skills dans l’export public,
# packages.<paquet>.includes.skills dans le workspace source et le miroir.
skills = list(manifest.get("product", {}).get("skills", []))
if not skills:
    prefixe = "skills/"
    vus = set()
    for paquet in (manifest.get("packages") or {}).values():
        for entree in ((paquet or {}).get("includes") or {}).get("skills", []):
            texte = entree if isinstance(entree, str) else str(entree)
            if prefixe not in texte:
                continue
            # Le segment qui suit skills/ nomme le skill ; ce qui vient apres
            # designe un fichier interne et ne doit pas devenir un nom.
            nom = texte.split(prefixe, 1)[1].split("/", 1)[0]
            if nom and nom not in vus:
                vus.add(nom)
                skills.append(nom)

for skill in skills:
    print(skill)
PY
)

if (( ${#skills[@]} == 0 )); then
  printf '[FAIL] aucun skill déclaré dans le manifeste\n' >&2
  exit 1
fi

motif='\.claude/skills/[a-z0-9-]+/[A-Za-z0-9_.-]'
violations=0
controlled=0
for skill in "${skills[@]}"; do
  target="$WORKSPACE/.claude/skills/$skill"
  if [[ ! -d "$target" ]]; then
    printf '[FAIL] skill déclaré absent : .claude/skills/%s\n' "$skill" >&2
    violations=$((violations + 1))
    continue
  fi
  controlled=$((controlled + 1))
  while IFS= read -r file; do
    rel="${file#"$WORKSPACE"/}"
    case "$rel" in
      */examples/*/preuve.md|*/examples/*/page.json|*/examples/*/page.html|*/evals/*-trace.md|*/evals/official-coverage-inventory.md)
        continue ;;
    esac
    if grep -EqI "$motif" "$file" 2>/dev/null; then
      grep -EnI "$motif" "$file" | cut -c1-160 | sed "s#^#[FAIL] $rel:#" >&2
      violations=$((violations + 1))
    fi
    # Tous les fichiers sont scannes, sans liste d-extensions : une extension
    # non prevue creait un angle mort silencieux. grep -I ecarte les binaires,
    # comme le fait deja le controle de frontiere.
  done < <(find "$target" -type f \
    -not -path '*/__pycache__/*' -not -path '*/node_modules/*' | sort)
done

# Le contrôle de chemin ne suffit pas : un exemple peut rester portable tout
# en révélant une mission, un poste ou une arborescence privée. Les marqueurs
# sont assemblés pour que ce script ne se signale pas lui-même.
marker_acti="actim""age"
marker_spec="spec""inov"
marker_spen="spen""inov"
marker_afa="bo-afa""2025"
marker_projects="projets-""actifs"
marker_open="open""src"
marker_git="git-hors-""workflow"
marker_zsh=".z""shrc"
marker_packs="dsfr-agentic-""packs"
marker_douane="moa.""douane"
forbidden="$marker_acti|$marker_spec|$marker_spen|$marker_afa|$marker_projects|$marker_open|$marker_git|$marker_zsh|$marker_packs|$marker_douane"

portable_files=()
while IFS= read -r -d '' file; do
  [[ -f "$file" ]] && portable_files+=("$file")
done < <(
  git -C "$WORKSPACE" ls-files -z -- \
    README.md DEMARRAGE-AGENT.md CHANGELOG.md documentation design-systems .claude/skills scripts \
    | while IFS= read -r -d '' rel; do printf '%s\0' "$WORKSPACE/$rel"; done
)

for file in "${portable_files[@]}"; do
  rel="${file#"$WORKSPACE/"}"
  if grep -EqI "$forbidden" "$file" 2>/dev/null; then
    grep -EnI "$forbidden" "$file" | cut -c1-200 | sed "s#^#[FAIL] $rel:#" >&2
    violations=$((violations + 1))
  fi
done

if (( violations > 0 )); then
  printf '[FAIL] %d violation(s) de portabilité des chemins de skills\n' "$violations" >&2
  exit 1
fi

printf "[OK] chemins des skills indépendants du dossier d'installation (%d skills contrôlés)\n" "$controlled"
