#!/usr/bin/env bash
set -euo pipefail
export PYTHONDONTWRITEBYTECODE=1
WORKSPACE="${1:-$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)}"
python3 -B "$WORKSPACE/scripts/tests/test_kit_lock.py"
