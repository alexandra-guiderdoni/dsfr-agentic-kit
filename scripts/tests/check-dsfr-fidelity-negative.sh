#!/usr/bin/env bash
set -euo pipefail

# Test négatif du contrôle de fidélité DSFR (PUB-06 du miroir) : un token et
# une classe inventés, injectés dans une copie du profil, doivent faire échouer
# check-dsfr-fidelity.py en nommant les fautifs. Sans cache officiel, le test
# saute explicitement : il ne prouve rien, il ne passe pas en silence.

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WORKSPACE="$(cd "$SCRIPT_DIR/../.." && pwd)"

version="$(sed -n 's/^package_version_ref: *"\{0,1\}\([0-9.]*\)"\{0,1\}.*/\1/p' "$WORKSPACE/design-systems/dsfr/tokens.yaml" | head -1)"
cache="${DSFR_OFFICIAL_CACHE_DIR:-$HOME/.cache/dsfr-official-cache}"
if [[ -z "$version" || ! -d "$cache/gouvfr-dsfr-$version/package/dist" ]]; then
  printf '[SKIP] cache officiel %s absent (%s) : test négatif de fidélité non exercé\n' "${version:-?}" "$cache"
  exit 0
fi

tmp="$(mktemp -d "${TMPDIR:-/tmp}/fidelity-negative.XXXXXX")"
cleanup() { rm -rf "$tmp"; }
trap cleanup EXIT INT TERM

# Copie du seul périmètre lu par le contrôle : design-systems/ (scripts + profil).
mkdir -p "$tmp/design-systems"
cp -R "$WORKSPACE/design-systems/scripts" "$WORKSPACE/design-systems/dsfr" "$tmp/design-systems/"
printf '\ninventaire_test_negatif: "$inventaire-test-999"\n' >> "$tmp/design-systems/dsfr/tokens.yaml"
exemple="$(ls "$tmp/design-systems/dsfr/examples/"*.html | head -1)"
printf '<div class="fr-inventee-999"></div>\n' >> "$exemple"

set +e
sortie="$(cd "$tmp" && python3 design-systems/scripts/check-dsfr-fidelity.py --version "$version" 2>&1)"
rc=$?
set -e

echecs=0
if [[ "$rc" -eq 1 ]]; then
  printf '[OK] token et classe inventés : le contrôle échoue (exit 1)\n'
else
  printf '[FAIL] exit %s attendu 1\n' "$rc" >&2; echecs=$((echecs + 1))
fi
if grep -q 'FAIL token absent du CSS .*: \$inventaire-test-999' <<<"$sortie"; then
  printf '[OK] le token fautif est nommé\n'
else
  printf '[FAIL] token fautif non nommé\n' >&2; echecs=$((echecs + 1))
fi
if grep -q 'FAIL classe absente du CSS .*: fr-inventee-999' <<<"$sortie"; then
  printf '[OK] la classe fautive est nommée\n'
else
  printf '[FAIL] classe fautive non nommée\n' >&2; echecs=$((echecs + 1))
fi
if grep -q "$version" <<<"$sortie"; then
  printf '[OK] la version contrôlée (%s) est nommée\n' "$version"
else
  printf '[FAIL] version contrôlée non nommée\n' >&2; echecs=$((echecs + 1))
fi

if (( echecs > 0 )); then
  printf '%s\n' "$sortie" | tail -6 >&2
  printf '[FAIL] test négatif de fidélité DSFR : %d échec(s)\n' "$echecs" >&2
  exit 1
fi
printf '[OK] test négatif de fidélité DSFR : un token ou une classe inventés font échouer le contrôle avec leur nom\n'
