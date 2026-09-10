#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WORKSPACE="${1:-$(cd "$SCRIPT_DIR/../.." && pwd)}"
failures=0
fail() { printf '[FAIL] %s\n' "$*" >&2; failures=$((failures + 1)); }
ok() { printf '[OK] %s\n' "$*"; }

while IFS= read -r -d '' file; do
  count="$(grep -c '^```' "$file" || true)"
  if (( count % 2 != 0 )); then
    fail "blocs Markdown non fermés : ${file#"$WORKSPACE/"} ($count clôtures)"
  fi
done < <(find "$WORKSPACE/.claude/skills" -name SKILL.md -type f -print0 | sort -z)

if (( failures == 0 )); then
  ok "blocs Markdown fermés dans les SKILL.md"
fi

# Convention de frontmatter compatible avec la lecture directe et le plugin :
# les clés expérimentales de l'ancien adaptateur ne doivent pas modifier le
# routage d'un hôte qui ne les comprend pas.
frontmatter_errors=0
while IFS= read -r -d '' file; do
  head_block="$(sed -n '1,24p' "$file")"
  grep -q '^name:' <<<"$head_block" || {
    fail "frontmatter sans name : ${file#"$WORKSPACE/"}"
    frontmatter_errors=$((frontmatter_errors + 1))
  }
  grep -q '^description:' <<<"$head_block" || {
    fail "frontmatter sans description : ${file#"$WORKSPACE/"}"
    frontmatter_errors=$((frontmatter_errors + 1))
  }
  if grep -nE '^(whenToUse|user-invocable|background|version):' <<<"$head_block" >/dev/null; then
    fail "clé de frontmatter non portable : ${file#"$WORKSPACE/"}"
    frontmatter_errors=$((frontmatter_errors + 1))
  fi
  if grep -nE '^allowed-tools:.*(mcp__|Bash\(agent-browser:)' <<<"$head_block" >/dev/null; then
    fail "outil hôte spécifique dans allowed-tools : ${file#"$WORKSPACE/"}"
    frontmatter_errors=$((frontmatter_errors + 1))
  fi
done < <(find "$WORKSPACE/.claude/skills" -name SKILL.md -type f -print0 | sort -z)
if (( frontmatter_errors == 0 )); then
  ok "frontmatter des skills conforme à la convention portable"
fi

stale_file="$(mktemp "${TMPDIR:-/tmp}/dsfr-agentic-stale.XXXXXX")"
trap 'rm -f "$stale_file"' EXIT
if rg -n -E '/audit-a11y\b|/screen-reader-test\b|\ba11y-ci\b' \
  "$WORKSPACE/.claude/skills" --glob 'SKILL.md' --glob '*.md' \
  --glob '!a11y-shared-references/axe-core-scan-patterns.md' >"$stale_file" 2>/dev/null; then
  sed 's#^#[FAIL] renvoi obsolète : #' "$stale_file" >&2
  failures=$((failures + 1))
fi

for file in \
  "$WORKSPACE/.claude/skills/ticket-rgaa/SKILL.md" \
  "$WORKSPACE/.claude/skills/pre-audit-rgaa-dsfr/SKILL.md"; do
  if grep -nE '—|–' "$file" >/dev/null 2>&1; then
    fail "tiret non portable dans un gabarit : ${file#"$WORKSPACE/"}"
  fi
done

if (( failures > 0 )); then
  printf '[FAIL] conventions du harnais : %d échec(s)\n' "$failures" >&2
  exit 1
fi
printf '[OK] conventions du harnais\n'
