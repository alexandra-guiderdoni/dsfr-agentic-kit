#!/usr/bin/env bash
set -euo pipefail

# Registre canonique des composants DSFR (issue #8 du miroir) : lance les tests
# unitaires `test_dsfr_component_registry.py` avec `python3 -B`, sans écrire de
# `__pycache__` dans le paquet, et échoue si un test échoue.

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WORKSPACE="${1:-$(cd "$SCRIPT_DIR/../.." && pwd)}"
tests="$WORKSPACE/scripts/tests/test_dsfr_component_registry.py"
[[ -f "$tests" ]] || { printf '[FAIL] tests du registre absents : %s\n' "$tests" >&2; exit 1; }

if AGENTIC_DESIGN_WORKSPACE="$WORKSPACE" PYTHONDONTWRITEBYTECODE=1 python3 -B "$tests" 2>&1 | tail -4; then
  printf '[OK] registre canonique des composants DSFR : alias, noms officiels et consommateurs\n'
else
  printf '[FAIL] registre canonique des composants DSFR\n' >&2
  exit 1
fi
