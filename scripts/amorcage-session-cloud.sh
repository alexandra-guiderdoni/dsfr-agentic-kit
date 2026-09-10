#!/usr/bin/env bash
# Reconstitue dsfr-agentic-kit dans un conteneur Cowork éphémère.
#
# Le fichier doit être conservé dans un Projet Cowork ou dans un autre espace
# persistant. Le clone, le cache et le venv sont des sorties reconstructibles.
# Le script ne prouve la conformité DSFR ou RGAA d’aucune page.
#
#   bash scripts/amorcage-session-cloud.sh
#   bash scripts/amorcage-session-cloud.sh --no-check
#   bash scripts/amorcage-session-cloud.sh --update

set -euo pipefail

REPOSITORY="${DSFR_KIT_REPO:-git@github.com:alexandra-guiderdoni/dsfr-agentic-kit.git}"
WORKSPACE="${DSFR_KIT_WORKSPACE:-$HOME/workspace}"
KIT_PATH="${DSFR_KIT_PATH:-$WORKSPACE/dsfr-agentic-kit}"
VENV_PATH="${DSFR_KIT_VENV:-$HOME/.venv-dsfr}"
RUN_CHECKS=1
UPDATE=0
VITRINE_DIR=""

usage() {
  sed -n '2,11p' "$0"
}

fail() {
  printf '[FAIL] %s\n' "$*" >&2
  exit 1
}

info() {
  printf '[INFO] %s\n' "$*"
}

version_ge() {
  awk -v value="$1" -v minimum="$2" 'BEGIN {
    split(value, a, "."); split(minimum, b, ".");
    exit !((a[1] + 0 > b[1] + 0) || (a[1] + 0 == b[1] + 0 && a[2] + 0 >= b[2] + 0))
  }'
}

canonical_repository() {
  local value="$1"
  case "$value" in
    git@github.com:*) value="${value#git@github.com:}" ;;
    ssh://git@github.com/*) value="${value#ssh://git@github.com/}" ;;
    https://github.com/*|http://github.com/*) value="${value#*github.com/}" ;;
  esac
  printf '%s\n' "$value" | sed 's#/$##; s#\.git$##'
}

cleanup() {
  if [[ -n "$VITRINE_DIR" && -d "$VITRINE_DIR" ]]; then
    rm -rf "$VITRINE_DIR"
  fi
}
trap cleanup EXIT INT TERM

while [[ $# -gt 0 ]]; do
  case "$1" in
    --no-check) RUN_CHECKS=0; shift ;;
    --update) UPDATE=1; shift ;;
    --help|-h) usage; exit 0 ;;
    *) fail "argument inconnu : $1" ;;
  esac
done

command -v git >/dev/null 2>&1 || fail "git absent : requis pour cloner le kit"
mkdir -p "$WORKSPACE"
WORKSPACE="$(cd "$WORKSPACE" && pwd)"
if [[ "$KIT_PATH" != /* ]]; then
  KIT_PATH="$WORKSPACE/$KIT_PATH"
fi

if [[ -d "$KIT_PATH/.git" || -f "$KIT_PATH/.git" ]]; then
  info "kit déjà présent : $KIT_PATH"
  ORIGIN="$(git -C "$KIT_PATH" remote get-url origin 2>/dev/null || true)"
  [[ -n "$ORIGIN" ]] || fail "dépôt existant sans remote origin : $KIT_PATH"
  if [[ "$(canonical_repository "$ORIGIN")" != "$(canonical_repository "$REPOSITORY")" ]]; then
    fail "remote origin inattendu : $ORIGIN (attendu : $REPOSITORY)"
  fi
  if [[ "$UPDATE" -eq 1 ]]; then
    if [[ -n "$(git -C "$KIT_PATH" status --porcelain)" ]]; then
      fail "mise à jour refusée : le kit contient des modifications locales"
    fi
    BEFORE="$(git -C "$KIT_PATH" rev-parse HEAD)"
    git -C "$KIT_PATH" pull --ff-only
    AFTER="$(git -C "$KIT_PATH" rev-parse HEAD)"
    if [[ "$BEFORE" == "$AFTER" ]]; then
      info "kit déjà à jour : ${AFTER:0:12}"
    else
      info "mise à jour ${BEFORE:0:12} -> ${AFTER:0:12}"
      git -C "$KIT_PATH" log --oneline "$BEFORE..$AFTER"
      info "relire CHANGELOG.md et config/agentic-design-packages.yaml"
    fi
  fi
elif [[ -e "$KIT_PATH" ]]; then
  fail "le chemin cible existe mais n’est pas un dépôt Git : $KIT_PATH"
else
  git clone "$REPOSITORY" "$KIT_PATH"
fi

MANIFEST="$KIT_PATH/config/agentic-design-packages.yaml"
[[ -f "$MANIFEST" ]] || fail "manifeste absent après installation : $MANIFEST"

PYTHON_MINIMUM="$(sed -n 's/^  python_minimum: *"\{0,1\}\([^"[:space:]]*\).*/\1/p' "$MANIFEST" | head -1)"
[[ -n "$PYTHON_MINIMUM" ]] || fail "python_minimum absent du manifeste"

system_python_ok=0
if command -v python3 >/dev/null 2>&1; then
  SYSTEM_VERSION="$(python3 -c 'import sys; print("%d.%d" % sys.version_info[:2])' 2>/dev/null || true)"
  if [[ -n "$SYSTEM_VERSION" ]] && version_ge "$SYSTEM_VERSION" "$PYTHON_MINIMUM"; then
    system_python_ok=1
  fi
fi

if [[ "$system_python_ok" -eq 1 ]] && python3 -c 'import yaml, jsonschema' >/dev/null 2>&1; then
  info "Python système utilisable : $SYSTEM_VERSION"
else
  command -v uv >/dev/null 2>&1 || fail "Python $PYTHON_MINIMUM avec PyYAML et jsonschema requis ; uv absent"
  if [[ -e "$VENV_PATH" && ! -x "$VENV_PATH/bin/python" ]]; then
    fail "venv existant inutilisable : $VENV_PATH"
  fi
  PYTHON_SPEC="python3"
  if [[ "$system_python_ok" -eq 0 ]]; then
    uv python install "$PYTHON_MINIMUM"
    PYTHON_SPEC="$PYTHON_MINIMUM"
  fi
  if [[ ! -x "$VENV_PATH/bin/python" ]]; then
    uv venv --python "$PYTHON_SPEC" "$VENV_PATH"
  fi
  VIRTUAL_ENV="$VENV_PATH" uv pip install --quiet PyYAML jsonschema
  export PATH="$VENV_PATH/bin:$PATH"
  info "venv utilisable : $(python3 -V)"
fi

DSFR_VERSION="$(python3 - "$MANIFEST" <<'PY'
import sys
from pathlib import Path

import yaml

manifest = yaml.safe_load(Path(sys.argv[1]).read_text(encoding="utf-8")) or {}
runtime = manifest.get("runtime") or {}
print(runtime.get("dsfr_version", ""))
PY
)"
[[ -n "$DSFR_VERSION" ]] || fail "dsfr_version absent du manifeste"

if ! command -v rsync >/dev/null 2>&1; then
  if command -v apt-get >/dev/null 2>&1; then
    apt-get install -y rsync >/dev/null 2>&1 \
      || { apt-get update -qq >/dev/null 2>&1 && apt-get install -y rsync >/dev/null 2>&1; }
  elif command -v brew >/dev/null 2>&1; then
    brew install rsync >/dev/null
  else
    fail "rsync absent et aucun gestionnaire de paquets compatible détecté"
  fi
fi
command -v rsync >/dev/null 2>&1 || fail "installation de rsync échouée"

CACHE_ROOT="${DSFR_OFFICIAL_CACHE_DIR:-$HOME/.cache/dsfr-official-cache}"
CACHE="$CACHE_ROOT/gouvfr-dsfr-$DSFR_VERSION"
if [[ -d "$CACHE/package/dist" ]]; then
  info "cache DSFR déjà présent : $DSFR_VERSION"
else
  [[ "${DSFR_OFFICIAL_CACHE_OFFLINE:-0}" != 1 ]] \
    || fail "cache DSFR absent en mode hors ligne : $CACHE"
  command -v npm >/dev/null 2>&1 || fail "npm absent : requis pour le cache DSFR officiel"
  mkdir -p "$CACHE"
  ARCHIVE="$(cd "$CACHE" && npm pack --silent "@gouvfr/dsfr@$DSFR_VERSION")"
  tar xzf "$CACHE/$ARCHIVE" -C "$CACHE"
  [[ -d "$CACHE/package/dist" ]] || fail "cache DSFR incomplet : $CACHE"
  info "cache DSFR installé : $DSFR_VERSION"
fi

if [[ "$RUN_CHECKS" -eq 1 ]]; then
  cd "$KIT_PATH"
  bash scripts/check-prerequisites.sh
  bash scripts/check-agentic-design-pack.sh
  bash scripts/demo-dsfr-assembled-page.sh --quiet >/dev/null
  VITRINE_DIR="$(mktemp -d "${TMPDIR:-/tmp}/dsfr-agentic-vitrine.XXXXXX")"
  bash scripts/demo-dsfr-vitrine.sh --quiet --out-dir "$VITRINE_DIR" >/dev/null
  info "contrôles et démonstrations : OK"
else
  info "installation terminée sans contrôles (--no-check)"
fi

if [[ -n "$(git -C "$KIT_PATH" status --porcelain)" ]]; then
  fail "le kit a été modifié par ses propres contrôles"
fi
info "kit prêt : $KIT_PATH"
info "DSFR en cache : $DSFR_VERSION"
