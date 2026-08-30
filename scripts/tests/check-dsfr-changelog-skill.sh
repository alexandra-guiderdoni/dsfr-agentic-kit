#!/usr/bin/env bash
set -euo pipefail

WORKSPACE="${1:-$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)}"
DESIGN="$WORKSPACE/design-systems/dsfr/DESIGN.md"
COMPONENT_SKILL="$WORKSPACE/.claude/skills/dsfr-components/SKILL.md"
CHANGELOG_SKILL="$WORKSPACE/.claude/skills/dsfr-changelog"

fail() {
  printf '[FAIL] %s\n' "$1" >&2
  exit 1
}

for rel in SKILL.md agents/openai.yaml scripts/dsfr-collect.py scripts/test-collect.sh; do
  test -f "$CHANGELOG_SKILL/$rel" || fail "élément dsfr-changelog absent : $rel"
done

grep -Fq 'dsfr-changelog' "$DESIGN" \
  || fail "routage dsfr-changelog absent de DESIGN.md"
grep -Fq 'dsfr-changelog' "$COMPONENT_SKILL" \
  || fail "frontière dsfr-changelog absente de dsfr-components"

printf '[OK] contrat standalone dsfr-changelog\n'
