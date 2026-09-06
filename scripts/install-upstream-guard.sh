#!/usr/bin/env bash
set -euo pipefail

# Installe le garde de zone synchronisee comme hook pre-commit du depot courant.
#
# A lancer une fois par clone de miroir ou d-export. Sans effet dans le
# workspace source, ou le garde se desactive de lui-meme.

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO="${1:-$(cd "$SCRIPT_DIR/.." && pwd)}"
GUARD="scripts/check-upstream-zone-edit.sh"

[[ -d "$REPO/.git" ]] || { printf '[FAIL] pas un depot Git : %s\n' "$REPO" >&2; exit 1; }
[[ -f "$REPO/$GUARD" ]] || { printf '[FAIL] garde absent : %s/%s\n' "$REPO" "$GUARD" >&2; exit 1; }

hook="$REPO/.git/hooks/pre-commit"
if [[ -f "$hook" ]] && ! grep -q 'check-upstream-zone-edit' "$hook"; then
  printf '[FAIL] un hook pre-commit existe deja : %s\n' "$hook" >&2
  printf '[FAIL] y ajouter a la main : bash "$(git rev-parse --show-toplevel)"/%s\n' "$GUARD" >&2
  exit 1
fi

cat > "$hook" <<'HOOK'
#!/usr/bin/env bash
# Garde de zone synchronisee. Voir scripts/check-upstream-zone-edit.sh
set -euo pipefail
racine="$(git rev-parse --show-toplevel)"
garde="$racine/scripts/check-upstream-zone-edit.sh"
[[ -f "$garde" ]] || exit 0
bash "$garde" "$racine"
HOOK
chmod +x "$hook"
printf '[OK] garde installe : %s\n' "$hook"
