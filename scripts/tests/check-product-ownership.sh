#!/usr/bin/env bash
set -euo pipefail
WORKSPACE="${1:-$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)}"
python3 - "$WORKSPACE" <<'PY'
import json
import sys
from pathlib import Path

root = Path(sys.argv[1])
authority = json.loads((root / "config/product-authority.json").read_text(encoding="utf-8"))
assert authority["schema_version"] == 1
assert authority["product"] == "dsfr-agentic-kit"
assert authority["accept_workspace_export"] is False
assert authority["canonical_repository"] == "alexandra-guiderdoni/dsfr-agentic-kit"
assert not authority["recipe_paths_pending_extraction"]
for rel in authority["product_roots"]:
    assert (root / rel).is_dir(), rel
for name in ("generate-virginie-rgaa-tickets.py", "generate-p06-form-annex.py", "retest-p06-form-safe.py"):
    assert not (root / "scripts" / name).exists(), name
for entry in (root / "scripts/virginie_dsfr").glob("*.py"):
    assert "portail Douane" not in entry.read_text(encoding="utf-8"), entry.name
print("[OK] propriétaire produit et séparation des recettes")
PY
bash "$WORKSPACE/scripts/check-upstream-zone-edit.sh" "$WORKSPACE"
