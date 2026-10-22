#!/usr/bin/env bash
set -euo pipefail
export PYTHONDONTWRITEBYTECODE=1
WORKSPACE="${1:-$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)}"
# shellcheck source=../lib/python-with-pyyaml.sh
. "$WORKSPACE/scripts/lib/python-with-pyyaml.sh"
python_with_pyyaml "$WORKSPACE/scripts/tests/test_campaign_distribution.py"
python_with_pyyaml "$WORKSPACE/scripts/tests/test_runtime_trace_output.py"
