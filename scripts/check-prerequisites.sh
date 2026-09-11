#!/usr/bin/env bash
set -euo pipefail

# Diagnostic des prérequis du kit autonome.
# Chaque capacité est classée REQUIS, OPTIONNEL ou MANQUANT avec l'action à faire.
# Le code de sortie vaut 1 seulement si une capacité requise manque ; une
# capacité optionnelle absente produit un avertissement. Rien n'est installé ici.
#
# Usage : bash scripts/check-prerequisites.sh [--quiet]
#   --quiet : n'affiche que les manques et les avertissements.
#   DSFR_AUDIT_PYTHON : interpréteur Python à sonder, comme celui de la campagne.

QUIET=0
[[ "${1:-}" == "--quiet" ]] && QUIET=1
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WORKSPACE="$(cd "$SCRIPT_DIR/.." && pwd)"

manquants=0
avertissements=0
requis_ok() { [[ "$QUIET" -eq 1 ]] || printf '[REQUIS] %s\n' "$*"; }
manquant() { printf '[MANQUANT] %s\n' "$*" >&2; manquants=$((manquants + 1)); }
optionnel_ok() { [[ "$QUIET" -eq 1 ]] || printf '[OPTIONNEL] %s\n' "$*"; }
optionnel_absent() { printf '[OPTIONNEL] %s\n' "$*"; avertissements=$((avertissements + 1)); }

# version_ge "3.12.1" "3.10" : vrai si major.minor >= minimum.
version_ge() {
  awk -v v="$1" -v m="$2" 'BEGIN {
    split(v, a, "."); split(m, b, ".");
    exit !((a[1] + 0 > b[1] + 0) || (a[1] + 0 == b[1] + 0 && a[2] + 0 >= b[2] + 0))
  }'
}

# Python 3.10 minimum (syntaxe des scripts), 3.12 en CI.
python_version=""
if command -v python3 >/dev/null 2>&1; then
  python_version="$(python3 -c 'import sys; print("%d.%d.%d" % sys.version_info[:3])' 2>/dev/null || true)"
fi
if [[ -z "$python_version" ]]; then
  manquant "python3 absent ou inutilisable : installer Python 3.12 (par exemple brew install python@3.12)"
elif ! version_ge "$python_version" "3.10"; then
  manquant "python3 $python_version trop ancien : Python 3.10 minimum, 3.12 en CI (brew install python@3.12)"
elif ! version_ge "$python_version" "3.12"; then
  requis_ok "python3 $python_version (3.12 en CI ; 3.10 minimum accepté)"
else
  requis_ok "python3 $python_version"
fi

has_uv=0
command -v uv >/dev/null 2>&1 && has_uv=1

# PyYAML : lecture du manifeste et des profils ; uv peut le fournir à la volée.
if [[ -n "$python_version" ]] && python3 -c 'import yaml' >/dev/null 2>&1; then
  requis_ok "PyYAML importable"
elif [[ "$has_uv" -eq 1 ]]; then
  requis_ok "PyYAML fourni à la volée par uv"
else
  manquant "PyYAML absent et uv introuvable : python3 -m pip install pyyaml, ou installer uv"
fi

# jsonschema : validation du page.json par le builder ; uv peut le fournir.
if [[ -n "$python_version" ]] && python3 -c 'import jsonschema' >/dev/null 2>&1; then
  requis_ok "jsonschema importable"
elif [[ "$has_uv" -eq 1 ]]; then
  requis_ok "jsonschema fourni à la volée par uv"
else
  manquant "jsonschema absent et uv introuvable : python3 -m pip install \"jsonschema>=4.22,<5\", ou installer uv"
fi

# Node 20 minimum (22 en CI) : démo, lint design.md, téléchargement du paquet officiel, contrôles navigateur.
node_version=""
if command -v node >/dev/null 2>&1; then
  node_version="$(node --version 2>/dev/null | sed 's/^v//' || true)"
fi
if [[ -z "$node_version" ]]; then
  manquant "node absent ou inutilisable : installer Node 22 (brew install node@22)"
elif ! version_ge "$node_version" "20"; then
  manquant "node $node_version trop ancien : Node 20 minimum, 22 en CI (brew install node@22)"
else
  requis_ok "node $node_version"
fi
for outil in npm npx; do
  if command -v "$outil" >/dev/null 2>&1; then
    requis_ok "$outil présent"
  else
    manquant "$outil absent : livré avec Node 22 (brew install node@22)"
  fi
done

# Playwright Python : les collecteurs RGAA/DSFR importent playwright.async_api.
# Le paquet Node seul ne satisfait pas ce prérequis.
playwright_python_path=""
selected_python="${DSFR_AUDIT_PYTHON:-}"
python_from_ay11() {
  local ay11_bin="$1"
  local ay11_dir
  ay11_dir="$(cd -- "$(dirname -- "$ay11_bin")" && pwd -P)" || return 1
  if [[ -x "$ay11_dir/python" ]]; then
    printf '%s\n' "$ay11_dir/python"
  fi
}
if [[ -z "$selected_python" && -n "${AY11_BIN:-}" \
  && -f "$AY11_BIN" && -x "$AY11_BIN" ]]; then
  selected_python="$(python_from_ay11 "$AY11_BIN" || true)"
fi
if [[ -z "$selected_python" && -n "${AY11_ROOT:-}" ]]; then
  for prefix in "$AY11_ROOT/.venv/bin" "$AY11_ROOT/venv/bin"; do
    candidat="$prefix/python"
    if [[ -f "$prefix/ay11" && -x "$prefix/ay11" && -x "$candidat" ]]; then
      selected_python="$candidat"
      break
    fi
  done
fi
if [[ -z "$selected_python" ]] && command -v ay11 >/dev/null 2>&1; then
  selected_python="$(python_from_ay11 "$(command -v ay11)" || true)"
fi
if [[ -z "$selected_python" ]] && command -v python3 >/dev/null 2>&1; then
  selected_python="$(command -v python3)"
fi
if [[ -n "$selected_python" ]] \
  && playwright_python_path="$("$selected_python" -c 'import playwright.async_api; print(playwright.__file__)' 2>/dev/null)"; then
  optionnel_ok "Playwright Python présent avec $selected_python ($playwright_python_path)"
else
  optionnel_absent "Playwright Python absent ou inutilisable avec ${selected_python:-python3} : installer avec cet interpréteur puis lancer `python -m playwright install chromium` ; les contrôles navigateur Python seront sautés"
fi

# Playwright Node : utilisé par les démos et contrôles JavaScript du kit.
playwright_node_dir=""
if [[ -n "${PLAYWRIGHT_PACKAGE_DIR:-}" && -f "${PLAYWRIGHT_PACKAGE_DIR}/package.json" ]]; then
  playwright_node_dir="$PLAYWRIGHT_PACKAGE_DIR"
elif [[ -n "$node_version" ]] && node -e "require.resolve('playwright/package.json')" >/dev/null 2>&1; then
  playwright_node_dir="$(node -e "const p=require('path');console.log(p.dirname(require.resolve('playwright/package.json')))" 2>/dev/null || true)"
else
  for candidat in "$HOME"/.npm/_npx/*/node_modules/playwright; do
    [[ -f "$candidat/package.json" ]] && { playwright_node_dir="$candidat"; break; }
  done
fi
if [[ -n "$playwright_node_dir" ]]; then
  optionnel_ok "Playwright Node présent ($playwright_node_dir)"
else
  optionnel_absent "Playwright Node absent : npx --yes playwright install chromium ; les contrôles navigateur JavaScript seront sautés"
fi

# Cache DSFR officiel : téléchargé par npm pack au premier contrôle, ou SKIP explicite hors ligne.
dsfr_version="$(sed -n 's/^package_version_ref: *"\{0,1\}\([0-9.]*\)"\{0,1\}.*/\1/p' "$WORKSPACE/design-systems/dsfr/tokens.yaml" 2>/dev/null | head -1 || true)"
if [[ -n "$dsfr_version" ]]; then
  cache_dir="${DSFR_OFFICIAL_CACHE_DIR:-$HOME/.cache/dsfr-official-cache}"
  if [[ -d "$cache_dir/gouvfr-dsfr-$dsfr_version/package/dist/component" ]]; then
    optionnel_ok "cache DSFR officiel $dsfr_version présent ($cache_dir)"
  else
    optionnel_absent "cache DSFR officiel $dsfr_version absent : téléchargé par npm pack au premier contrôle (réseau), ou DSFR_OFFICIAL_CACHE_OFFLINE=1 pour un SKIP explicite"
  fi
fi

# rsync : démo vitrine DSFR ; le reste du kit n'en dépend pas.
if command -v rsync >/dev/null 2>&1; then
  optionnel_ok "rsync présent (démo vitrine)"
else
  optionnel_absent "rsync absent : requis par scripts/demo-dsfr-vitrine.sh (brew install rsync ou apt-get install rsync)"
fi

# git : contrôles Git en avertissement sans lui.
if command -v git >/dev/null 2>&1; then
  optionnel_ok "git présent"
else
  optionnel_absent "git absent : les contrôles git diff --check sont signalés comme sautés"
fi

if (( manquants > 0 )); then
  printf '[FAIL] prérequis : %d capacité(s) requise(s) manquante(s), %d avertissement(s)\n' "$manquants" "$avertissements" >&2
  exit 1
fi
printf '[OK] prérequis : capacités requises présentes, %d avertissement(s)\n' "$avertissements"
