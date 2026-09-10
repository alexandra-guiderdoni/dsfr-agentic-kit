#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WORKSPACE="${1:-$(cd "$SCRIPT_DIR/../.." && pwd)}"
TMP_ROOT="$(mktemp -d "${TMPDIR:-/tmp}/dsfr-agentic-kit-boundary.XXXXXX")"
PROJECT="$TMP_ROOT/projet"

cleanup() {
  rm -rf -- "$TMP_ROOT"
}
trap cleanup EXIT INT TERM

fail() {
  printf '[FAIL] %s\n' "$*" >&2
  exit 1
}

mkdir -p "$PROJECT"

status_before="$(git -C "$WORKSPACE" status --porcelain --ignored)"

assert_rejected() {
  local label="$1"
  shift
  local output status
  set +e
  output="$(PYTHONDONTWRITEBYTECODE=1 "$@" 2>&1)"
  status=$?
  set -e
  (( status != 0 )) || fail "$label : la destination interdite est acceptée"
  grep -Eq 'Projet de travail|Destination|clone du kit' <<<"$output" \
    || fail "$label : le motif de frontière n’est pas explicite"
}

assert_rejected "racine absente — générateur DSFR" \
  python3 "$WORKSPACE/scripts/generate-virginie-dsfr-composants.py"
assert_rejected "racine absente — tickets RGAA" \
  python3 "$WORKSPACE/scripts/generate-virginie-rgaa-tickets.py"
assert_rejected "racine absente — annexe P06" \
  python3 "$WORKSPACE/scripts/generate-p06-form-annex.py"
assert_rejected "racine absente — retest P06" \
  python3 "$WORKSPACE/scripts/retest-p06-form-safe.py"

assert_rejected "racine égale au kit — générateur DSFR" \
  python3 "$WORKSPACE/scripts/generate-virginie-dsfr-composants.py" \
  --project-root "$WORKSPACE"
assert_rejected "racine égale au kit — tickets RGAA" \
  python3 "$WORKSPACE/scripts/generate-virginie-rgaa-tickets.py" \
  --project-root "$WORKSPACE"
assert_rejected "racine égale au kit — annexe P06" \
  python3 "$WORKSPACE/scripts/generate-p06-form-annex.py" \
  --project-root "$WORKSPACE"
assert_rejected "racine égale au kit — retest P06" \
  python3 "$WORKSPACE/scripts/retest-p06-form-safe.py" \
  --project-root "$WORKSPACE"

assert_rejected "sortie explicite dans le kit — générateur DSFR" \
  python3 "$WORKSPACE/scripts/generate-virginie-dsfr-composants.py" \
  --project-root "$PROJECT" --output "$WORKSPACE/virginie-livrables/test-output"
assert_rejected "sortie explicite dans le kit — annexe P06" \
  python3 "$WORKSPACE/scripts/generate-p06-form-annex.py" \
  --project-root "$PROJECT" --output "$WORKSPACE/virginie-livrables/test-output"
assert_rejected "sortie explicite dans le kit — retest P06" \
  python3 "$WORKSPACE/scripts/retest-p06-form-safe.py" \
  --project-root "$PROJECT" --output "$WORKSPACE/virginie-livrables/test-output"

ln -s "$WORKSPACE/virginie-livrables" "$PROJECT/lien-vers-kit"
assert_rejected "lien symbolique — générateur DSFR" \
  python3 "$WORKSPACE/scripts/generate-virginie-dsfr-composants.py" \
  --project-root "$PROJECT" --output "$PROJECT/lien-vers-kit"
assert_rejected "lien symbolique — annexe P06" \
  python3 "$WORKSPACE/scripts/generate-p06-form-annex.py" \
  --project-root "$PROJECT" --output "$PROJECT/lien-vers-kit"
assert_rejected "lien symbolique — retest P06" \
  python3 "$WORKSPACE/scripts/retest-p06-form-safe.py" \
  --project-root "$PROJECT" --output "$PROJECT/lien-vers-kit"
assert_rejected "lien symbolique — tickets RGAA" \
  python3 "$WORKSPACE/scripts/generate-virginie-rgaa-tickets.py" \
  --project-root "$PROJECT/lien-vers-kit"

# Le chemin nominal doit créer le verrou et les premières sorties sous le
# projet. La fixture reprend le format couvert par les tests du générateur ;
# l’arrêt en code 2 est attendu, car la fiche de revue est créée au premier
# passage.
NOMINAL_ROOT="$TMP_ROOT/nominal"
NOMINAL_PROJECT="$NOMINAL_ROOT/projet"
NOMINAL_ARCHIVES="$NOMINAL_PROJECT/archives"
mkdir -p "$NOMINAL_ARCHIVES" "$NOMINAL_ROOT/cache"
PYTHONDONTWRITEBYTECODE=1 WORKSPACE="$WORKSPACE" ARCHIVES="$NOMINAL_ARCHIVES" python3 - <<'PY'
import os
import sys
from pathlib import Path

workspace = Path(os.environ["WORKSPACE"])
sys.path.insert(0, str(workspace / "scripts"))
sys.path.insert(0, str(workspace / "scripts/tests"))
from test_virginie_dsfr_composants import build_fixture

build_fixture(Path(os.environ["ARCHIVES"]))
PY

set +e
nominal_output="$({
  PYTHONDONTWRITEBYTECODE=1 python3 \
    "$WORKSPACE/scripts/generate-virginie-dsfr-composants.py" \
    --project-root "$NOMINAL_PROJECT" \
    --archives "$NOMINAL_ARCHIVES" \
    --pattern 'audit-test-p{n:02d}-2026-09-02' \
    --pages 1-2 \
    --cache-dir "$NOMINAL_ROOT/cache"
} 2>&1)"
nominal_status=$?
set -e
(( nominal_status == 2 )) \
  || fail "chemin nominal : le premier passage doit créer la revue (code 2)"
grep -Fq "REVUE" <<<"$nominal_output" \
  || fail "chemin nominal : la création de la revue n’est pas annoncée"
[[ -f "$NOMINAL_PROJECT/.dsfr-kit-pipeline.lock" ]] \
  || fail "chemin nominal : verrou absent du projet"
[[ -f "$NOMINAL_PROJECT/virginie-livrables/DSFR-COMPOSANTS-TRAVAIL/REVUE-A-QUALIFIER.md" ]] \
  || fail "chemin nominal : livrable absent du projet"

status_after="$(git -C "$WORKSPACE" status --porcelain --ignored)"
[[ "$status_before" == "$status_after" ]] \
  || fail "le contrôle de frontière a modifié l’état du kit"

printf '[OK] frontière projet/kit vérifiée sur les quatre pipelines\n'
