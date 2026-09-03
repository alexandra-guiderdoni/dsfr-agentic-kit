#!/usr/bin/env bash
set -euo pipefail
export PYTHONDONTWRITEBYTECODE=1
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=lib/python-with-pyyaml.sh
. "$SCRIPT_DIR/lib/python-with-pyyaml.sh"
python_with_pyyaml "$SCRIPT_DIR/../.claude/skills/audit-rgaa-creator/scripts/audit_campaign.py" "$@"
