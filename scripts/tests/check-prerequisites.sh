#!/usr/bin/env bash
set -euo pipefail

# Le diagnostic des prérequis doit classer chaque capacité en REQUIS, OPTIONNEL
# ou MANQUANT avec une action, échouer seulement sur un requis absent, et se
# contenter d'un avertissement pour un optionnel absent (issue #1 du miroir).

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WORKSPACE="$(cd "$SCRIPT_DIR/../.." && pwd)"
DIAG="$WORKSPACE/scripts/check-prerequisites.sh"

tmp="$(mktemp -d "${TMPDIR:-/tmp}/prerequisites.XXXXXX")"
cleanup() { rm -rf "$tmp"; }
trap cleanup EXIT INT TERM

echecs=0
ok() { printf '[OK] %s\n' "$*"; }
ko() { printf '[FAIL] %s\n' "$*" >&2; echecs=$((echecs + 1)); }

[[ -f "$DIAG" ]] || { printf '[FAIL] diagnostic absent : %s\n' "$DIAG" >&2; exit 1; }

# 1. Environnement courant : requis présents, exit 0, classes affichées.
set +e
sortie="$(bash "$DIAG" 2>&1)"; rc=$?
set -e
if [[ "$rc" -eq 0 ]] && grep -q '^\[REQUIS\] python3 ' <<<"$sortie" && grep -q '^\[REQUIS\] node ' <<<"$sortie" && grep -q '^\[OPTIONNEL\] rsync ' <<<"$sortie" && grep -q '^\[OK\] prérequis' <<<"$sortie"; then
  ok "environnement courant : requis présents, exit 0"
else
  printf '%s\n' "$sortie" | tail -5 >&2
  ko "environnement courant (exit $rc)"
fi

# 2. Un requis inutilisable (node qui échoue) : MANQUANT avec action, exit 1.
mkdir -p "$tmp/bin"
printf '#!/bin/sh\nexit 127\n' > "$tmp/bin/node"; chmod +x "$tmp/bin/node"
set +e
sortie="$(PATH="$tmp/bin:$PATH" bash "$DIAG" 2>&1)"; rc=$?
set -e
if [[ "$rc" -eq 1 ]] && grep -q '^\[MANQUANT\] node ' <<<"$sortie" && grep -qi 'install' <<<"$sortie"; then
  ok "requis inutilisable : MANQUANT avec action, exit 1"
else
  printf '%s\n' "$sortie" | tail -5 >&2
  ko "requis inutilisable (exit $rc)"
fi

# 3. Un optionnel absent (Playwright introuvable) : avertissement, exit 0.
mkdir -p "$tmp/home" "$tmp/vide"
set +e
sortie="$(cd "$tmp/vide" && HOME="$tmp/home" PLAYWRIGHT_PACKAGE_DIR= NODE_PATH= bash "$DIAG" 2>&1)"; rc=$?
set -e
if [[ "$rc" -eq 0 ]] && grep -q '^\[OPTIONNEL\] playwright absent' <<<"$sortie"; then
  ok "optionnel absent : avertissement, exit 0"
else
  printf '%s\n' "$sortie" | grep -i playwright >&2 || true
  ko "optionnel absent (exit $rc)"
fi

if (( echecs > 0 )); then
  printf '[FAIL] diagnostic des prérequis : %d échec(s)\n' "$echecs" >&2
  exit 1
fi
printf '[OK] diagnostic des prérequis : classes, actions et codes de sortie conformes\n'
