#!/usr/bin/env bash
set -euo pipefail

# Vérifie le skill de génération de pictogrammes, sa route et la cohérence de
# son corpus. Les SVG officiels ne sont pas redistribués dans le kit.

WORKSPACE="${1:-$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)}"
DESIGN="$WORKSPACE/design-systems/dsfr/DESIGN.md"
TOKENS="$WORKSPACE/design-systems/dsfr/tokens.yaml"
COMPONENT_SKILL="$WORKSPACE/.claude/skills/dsfr-components/SKILL.md"
PICTOGRAMS_DOC="$WORKSPACE/.claude/skills/dsfr-components/references/pictograms.md"
SKILL="$WORKSPACE/.claude/skills/generer-pictos-svg-dsfr"

fail() {
  printf '[FAIL] %s\n' "$1" >&2
  exit 1
}

for rel in \
  SKILL.md \
  DISTRIBUTION.md \
  agents/openai.yaml \
  scripts/generate_pictos_svg.py \
  scripts/build_svg_preview.py \
  scripts/audit_original_pictos.py \
  references/catalogue-pictos.md \
  tests/test_generate_pictos_svg.py \
  pictos-svg/etalon/manifest.json \
  pictos-svg/dsfr-officiels/manifest.json \
  pictos-svg/dsfr-officiels/INDEX.md \
  pictos-svg/dsfr-officiels/SOURCE.md; do
  test -f "$SKILL/$rel" || fail "élément du skill pictos absent : $rel"
done

official_svg_count="$(find "$SKILL/pictos-svg/dsfr-officiels" -type f -name '*.svg' | wc -l | tr -d ' ')"
[[ "$official_svg_count" == "0" ]] \
  || fail "$official_svg_count SVG officiel(s) redistribué(s)"

grep -Fq 'generer-pictos-svg-dsfr' "$DESIGN" \
  || fail "routage generer-pictos-svg-dsfr absent de DESIGN.md"
grep -Fq 'generer-pictos-svg-dsfr' "$COMPONENT_SKILL" \
  || fail "frontière pictos absente de dsfr-components/SKILL.md"
grep -Fq 'generer-pictos-svg-dsfr' "$PICTOGRAMS_DOC" \
  || fail "copie outillée absente de references/pictograms.md"

corpus_version="$(python3 -c "import json,sys; print(json.load(open(sys.argv[1]))['dsfr_version'])" "$SKILL/pictos-svg/dsfr-officiels/manifest.json")"
kit_version="$(sed -n 's/^package_version_ref: *"\{0,1\}\([0-9.]*\)"\{0,1\}.*/\1/p' "$TOKENS" | head -1)"
[[ -n "$corpus_version" && "$corpus_version" == "$kit_version" ]] \
  || fail "version du corpus pictos ($corpus_version) différente de package_version_ref ($kit_version)"

if [[ "${AGENTIC_DESIGN_PACK_SKIP_SELF_TESTS:-0}" != "1" ]]; then
  tests_log="$(mktemp "${TMPDIR:-/tmp}/check-dsfr-pictos-skill.XXXXXX")"
  trap 'rm -f "$tests_log"' EXIT
  (cd "$SKILL" && PYTHONDONTWRITEBYTECODE=1 python3 -B -m unittest tests.test_generate_pictos_svg >/dev/null 2>"$tests_log") \
    || { tail -20 "$tests_log" >&2; fail "suite du skill pictos en échec"; }
  pycache="$(find "$SKILL" -type d -name '__pycache__' | wc -l | tr -d ' ')"
  [[ "$pycache" == "0" ]] || fail "$pycache __pycache__ laissé(s) dans le skill pictos"
fi

printf '[OK] contrat standalone generer-pictos-svg-dsfr\n'
