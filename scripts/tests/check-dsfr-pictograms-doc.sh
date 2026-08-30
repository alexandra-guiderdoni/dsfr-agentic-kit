#!/usr/bin/env bash
set -euo pipefail

# Délègue au script distribué avec le skill (source unique) ; la version cible
# vient de design-systems/dsfr/tokens.yaml comme pour les autres contrôles du
# pack. Un paquet absent du cache est un SKIP explicite (code 2 du script du
# skill), rendu ici en code 0 pour rester non bloquant hors ligne, comme avant.

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WORKSPACE="$(cd "$SCRIPT_DIR/../.." && pwd)"
VERSION="$(sed -n 's/^package_version_ref: *"\{0,1\}\([0-9.]*\)"\{0,1\}.*/\1/p' "$WORKSPACE/design-systems/dsfr/tokens.yaml" | head -1)"

set +e
DSFR_OFFICIAL_VERSION="$VERSION" bash "$WORKSPACE/.claude/skills/dsfr-components/scripts/check_pictograms_doc.sh"
rc=$?
set -e
if [[ "$rc" -eq 2 ]]; then
  exit 0
fi
exit "$rc"
