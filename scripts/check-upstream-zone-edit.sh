#!/usr/bin/env bash
set -euo pipefail

# Avertit quand un commit modifie un fichier qui provient du workspace source.
#
# Ce depot peut etre un miroir ou un export : plusieurs de ses zones sont
# recopiees depuis le workspace source a chaque synchronisation. Une correction
# faite ici y survit jusqu-a la prochaine recopie, puis disparait ou doit etre
# reportee a la main. Le geste correct est de corriger a la source.
#
# Le controle avertit sans bloquer. Exporter UPSTREAM_ZONE_GUARD=block pour
# refuser le commit, UPSTREAM_ZONE_GUARD=off pour le desactiver.

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WORKSPACE="${1:-$(cd "$SCRIPT_DIR/.." && pwd)}"
MODE="${UPSTREAM_ZONE_GUARD:-warn}"

[[ "$MODE" == "off" ]] && exit 0

# Le workspace source n-est pas un miroir : il n-a rien en amont.
# Source et miroir portent le meme manifeste, le contenu ne les distingue donc
# pas. Ce qui les separe est la cible de synchronisation : elle existe comme
# dossier dans la source, jamais dans le miroir qu-elle designe.
MANIFEST="$WORKSPACE/config/agentic-design-packages.yaml"
if [[ -f "$MANIFEST" ]]; then
  cible="$(sed -n '/^standalone_mirror:/,/^[a-z]/p' "$MANIFEST" \
    | grep -m1 '^  default_target:' | sed 's/.*: *//' | tr -d '"' || true)"
  if [[ -n "$cible" && -d "$WORKSPACE/$cible" ]]; then
    exit 0
  fi
fi

# Prefixes recopies depuis la source. Volontairement stables et larges : le
# but est de signaler un geste, pas de trancher un cas limite.
zones=(
  ".claude/skills/"
  "design-systems/"
  "scripts/"
  "config/"
  "templates/"
  "documentation/guides/"
  "DEMARRAGE-AGENT.md"
)

# Chemins que ce depot possede en propre : jamais recopies, donc modifiables ici.
owned=()
if [[ -f "$MANIFEST" ]]; then
  while IFS= read -r line; do
    [[ -n "$line" ]] && owned+=("$line")
  done < <(sed -n '/^  mirror_owned_paths:/,/^  [a-z_]*:/p' "$MANIFEST" \
    | grep -oE '"[^"]+"' | tr -d '"' || true)
fi

staged="$(git -C "$WORKSPACE" diff --cached --name-only --diff-filter=ACMR || true)"
[[ -n "$staged" ]] || exit 0

concernes=""
while IFS= read -r file; do
  [[ -n "$file" ]] || continue
  garde=""
  for o in "${owned[@]:-}"; do
    [[ -n "$o" ]] || continue
    case "$file" in "$o"|"$o"/*) garde="oui"; break ;; esac
  done
  [[ -n "$garde" ]] && continue
  for z in "${zones[@]}"; do
    case "$file" in "$z"*) concernes+="$file"$'\n'; break ;; esac
  done
done <<< "$staged"

[[ -n "$concernes" ]] || exit 0

nb="$(printf '%s' "$concernes" | grep -c . || true)"
{
  printf '\n'
  printf '  %s fichier(s) de ce commit proviennent du workspace source.\n' "$nb"
  printf '\n'
  printf '%s' "$concernes" | head -12 | sed 's/^/    /'
  [[ "$nb" -gt 12 ]] && printf '    ... et %s autre(s)\n' "$((nb - 12))"
  printf '\n'
  printf '  Ces zones sont recopiees a chaque synchronisation. Une correction\n'
  printf '  faite ici sera ecrasee, ou devra etre reportee a la main.\n'
  printf '\n'
  printf '  Corriger de preference dans le workspace source, puis resynchroniser.\n'
  printf '  Si la correction doit rester ici, la declarer en mirror_owned_paths.\n'
  printf '\n'
  printf '  UPSTREAM_ZONE_GUARD=off pour ignorer, =block pour refuser le commit.\n'
  printf '\n'
} >&2

if [[ "$MODE" == "block" ]]; then
  printf '[FAIL] commit refuse : modification en zone synchronisee\n' >&2
  exit 1
fi
printf '[WARN] commit accepte, mais la derive devra etre reportee\n' >&2
exit 0
