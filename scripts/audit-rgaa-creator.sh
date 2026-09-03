#!/usr/bin/env bash
set -euo pipefail
export PYTHONDONTWRITEBYTECODE=1
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
if [ -f "$SCRIPT_DIR/../.env.local" ]; then
  # shellcheck disable=SC1091
  set -a
  . "$SCRIPT_DIR/../.env.local"
  set +a
fi
# shellcheck source=lib/python-with-pyyaml.sh
. "$SCRIPT_DIR/lib/python-with-pyyaml.sh"
python_with_pyyaml "$SCRIPT_DIR/../.claude/skills/audit-rgaa-creator/scripts/audit_campaign.py" "$@"
