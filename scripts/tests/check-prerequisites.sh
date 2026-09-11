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

# 3. Le paquet Node seul ne valide pas Playwright Python : deux diagnostics
#    indépendants doivent apparaître, exit 0. Le lanceur Python temporaire
#    masque uniquement les modules de site pour la sonde Playwright ; les
#    prérequis Python généraux restent ceux de l’environnement courant.
mkdir -p "$tmp/home" "$tmp/vide" "$tmp/playwright-node"
printf '{}\n' > "$tmp/playwright-node/package.json"
python_reel="$(command -v python3)"
mkdir -p "$tmp/python-bin"
python3_probe_log="$tmp/python3-probe.log"
printf '%s\n' \
  '#!/bin/sh' \
  "printf '%s\\n' \"\$*\" >> \"$python3_probe_log\"" \
  "case \"\${2:-}\" in" \
  "  *playwright*) exec env -u PYTHONPATH \"$python_reel\" -S \"\$@\" ;;" \
  'esac' \
  "exec \"$python_reel\" \"\$@\"" \
  > "$tmp/python-bin/python3"
chmod +x "$tmp/python-bin/python3"
# Le diagnostic est informatif : même en signalant Playwright absent, il ne doit
# jamais lancer la commande d'installation suggérée dans son message.
python_install_log="$tmp/python-install.log"
printf '%s\n' \
  '#!/bin/sh' \
  "printf '%s\\n' \"\$*\" >> \"$python_install_log\"" \
  'exit 77' \
  > "$tmp/python-bin/python"
chmod +x "$tmp/python-bin/python"
set +e
sortie="$(cd "$tmp/vide" && PATH="$tmp/python-bin:$PATH" HOME="$tmp/home" PYTHONNOUSERSITE=1 PLAYWRIGHT_PACKAGE_DIR="$tmp/playwright-node" NODE_PATH='' bash "$DIAG" 2>&1)"; rc=$?
set -e
if [[ "$rc" -eq 0 ]] \
  && grep -qi '^\[OPTIONNEL\] playwright python absent' <<<"$sortie" \
  && grep -qi '^\[OPTIONNEL\] playwright node présent' <<<"$sortie" \
  && ! grep -Fq -- '-m playwright install chromium' "$python3_probe_log" 2>/dev/null \
  && ! grep -Fq -- '-m playwright install chromium' "$python_install_log" 2>/dev/null; then
  ok "Playwright Node seul : Playwright Python signalé absent sans installation implicite, exit 0"
else
  printf '%s\n' "$sortie" | grep -i playwright >&2 || true
  if [[ -s "$python_install_log" ]]; then
    printf "[FAIL] commande d’installation exécutée par le diagnostic : %s\n" "$(cat "$python_install_log")" >&2
  fi
  if grep -Fq -- '-m playwright install chromium' "$python3_probe_log" 2>/dev/null; then
    printf "[FAIL] commande d’installation exécutée avec python3 par le diagnostic\n" >&2
  fi
  ko "Playwright Python/Node indépendants (exit $rc)"
fi

# 4. L'interpréteur explicitement sélectionné par la campagne est celui de la sonde.
mkdir -p "$tmp/interpreter"
printf '%s\n' \
  '#!/bin/sh' \
  "if [ \"\${1:-}\" = \"-c\" ]; then printf '%s\\n' '/selected/playwright/__init__.py'; else exec \"$python_reel\" \"\$@\"; fi" \
  > "$tmp/interpreter/python"
chmod +x "$tmp/interpreter/python"
set +e
sortie="$(DSFR_AUDIT_PYTHON="$tmp/interpreter/python" bash "$DIAG" 2>&1)"; rc=$?
set -e
if [[ "$rc" -eq 0 ]] \
  && grep -Fq "[OPTIONNEL] Playwright Python présent avec $tmp/interpreter/python" <<<"$sortie"; then
  ok "interpréteur Python sélectionné utilisé par la sonde"
else
  printf '%s\n' "$sortie" | grep -i playwright >&2 || true
  ko "interpréteur Python sélectionné ignoré (exit $rc)"
fi

if (( echecs > 0 )); then
  printf '[FAIL] diagnostic des prérequis : %d échec(s)\n' "$echecs" >&2
  exit 1
fi
printf '[OK] diagnostic des prérequis : classes, actions et codes de sortie conformes\n'
