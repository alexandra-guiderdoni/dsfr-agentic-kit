#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WORKSPACE="${1:-$(cd "$SCRIPT_DIR/../.." && pwd)}"
# shellcheck source=../lib/python-with-pyyaml.sh
. "$WORKSPACE/scripts/lib/python-with-pyyaml.sh"
TMP_ROOT="$(mktemp -d "${TMPDIR:-/tmp}/dsfr-agentic-kit-validation.XXXXXX")"
TMP_WORKSPACE="$TMP_ROOT/kit"

cleanup() {
  rm -rf -- "$TMP_ROOT"
}
trap cleanup EXIT INT TERM

fail() {
  printf '[FAIL] %s\n' "$*" >&2
  exit 1
}

cp -a "$WORKSPACE/." "$TMP_WORKSPACE"
rm -rf -- "$TMP_WORKSPACE/.git"
cp "$SCRIPT_DIR/fixtures/test-produit-en-echec.sh" \
  "$TMP_WORKSPACE/scripts/tests/test-produit-en-echec.sh"

manifest="$TMP_WORKSPACE/config/agentic-design-packages.yaml"
MANIFEST="$manifest" python_with_pyyaml - <<'PY'
import os
from pathlib import Path

import yaml

manifest = yaml.safe_load(Path(os.environ["MANIFEST"]).read_text(encoding="utf-8"))
tests = manifest.get("validation", {}).get("product_tests", [])
expected = "scripts/tests/check-virginie-dsfr-composants.sh"
if expected not in tests:
    raise SystemExit("contrôle du générateur absent de validation.product_tests")
PY

MANIFEST="$manifest" python3 - <<'PY'
import os
from pathlib import Path

path = Path(os.environ["MANIFEST"])
text = path.read_text(encoding="utf-8")
marker = "  markdown:\n"
if marker not in text:
    raise SystemExit("section validation.markdown absente du manifeste")
text = text.replace(
    marker,
    "    - scripts/tests/test-produit-en-echec.sh\n" + marker,
    1,
)
path.write_text(text, encoding="utf-8")
PY

set +e
output="$(bash "$TMP_WORKSPACE/scripts/check-agentic-design-pack.sh" "$TMP_WORKSPACE" --stop-after-product-tests 2>&1)"
status=$?
set -e

(( status != 0 )) || fail "le contrôle canonique accepte un test produit en échec"
grep -Fq '[FAIL] test produit : scripts/tests/test-produit-en-echec.sh' <<<"$output" \
  || fail "l’échec du test produit n’est pas visible dans le bilan"
grep -Fq '[ÉCHEC-SENTINELLE]' <<<"$output" \
  || fail "la sortie du test produit en échec n’est pas relayée"

printf '[OK] échec d’un test produit visible dans la validation canonique\n'
