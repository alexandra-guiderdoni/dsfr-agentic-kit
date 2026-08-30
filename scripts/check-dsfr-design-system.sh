#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WORKSPACE="${1:-$(cd "$SCRIPT_DIR/.." && pwd)}"
WORKSPACE="$(cd "$WORKSPACE" && pwd)"
DSFR_DIR="$WORKSPACE/design-systems/dsfr"
. "$SCRIPT_DIR/lib/python-with-pyyaml.sh"

failures=0

fail() {
  failures=$((failures + 1))
  printf '[FAIL] %s\n' "$*"
}

ok() {
  printf '[OK] %s\n' "$*"
}

warn() {
  printf '[WARN] %s\n' "$*"
}

require_file() {
  local path="$1"
  if [[ -f "$path" ]]; then
    ok "fichier présent: ${path#$WORKSPACE/}"
  else
    fail "fichier absent: ${path#$WORKSPACE/}"
  fi
}

line_limit() {
  local path="$1"
  local max="$2"
  local lines
  lines="$(wc -l < "$path" | tr -d ' ')"
  if (( lines <= max )); then
    ok "${path#$WORKSPACE/}: ${lines}/${max} lignes"
  else
    fail "${path#$WORKSPACE/}: ${lines}/${max} lignes"
  fi
}

require_file "$DSFR_DIR/DESIGN.md"
require_file "$DSFR_DIR/tokens.yaml"
require_file "$DSFR_DIR/references/foundations.md"
require_file "$DSFR_DIR/references/page-shell.md"
require_file "$DSFR_DIR/references/components-routing.md"
require_file "$DSFR_DIR/references/forms-models.md"
require_file "$DSFR_DIR/references/figma-handoff.md"
require_file "$DSFR_DIR/references/verification.md"
require_file "$DSFR_DIR/references/sources.md"

if WORKSPACE="$WORKSPACE" python_with_pyyaml "$SCRIPT_DIR/check-dsfr-design-router.py" --workspace "$WORKSPACE"; then
  ok "routeur DSFR"
else
  fail "routeur DSFR"
fi

router_routes_regression="$WORKSPACE/scripts/tests/check-dsfr-design-router-load-when-needed.sh"
if [[ -f "$router_routes_regression" && "${AGENTIC_DESIGN_PACK_SKIP_SELF_TESTS:-0}" != "1" ]]; then
  if bash "$router_routes_regression"; then
    ok "régression routes load_when_needed DSFR"
  else
    fail "régression routes load_when_needed DSFR"
  fi
fi

if WORKSPACE="$WORKSPACE" python_with_pyyaml "$WORKSPACE/design-systems/scripts/check-dsfr-negative-scenarios.py" --workspace "$WORKSPACE"; then
  ok "scénarios DSFR négatifs"
else
  fail "scénarios DSFR négatifs"
fi

line_limit "$DSFR_DIR/DESIGN.md" 320
line_limit "$DSFR_DIR/tokens.yaml" 320
for ref in "$DSFR_DIR"/references/*.md; do
  max_ref_lines=120
  if [[ "$(basename "$ref")" == "verification.md" ]]; then
    max_ref_lines=130
  fi
  line_limit "$ref" "$max_ref_lines"
done

WORKSPACE="$WORKSPACE" python_with_pyyaml - <<'PY'
import os
import sys
from pathlib import Path

import yaml

workspace = Path(os.environ["WORKSPACE"])
root = workspace / "design-systems/dsfr"
failures = 0


def ok(message):
    print(f"[OK] {message}")


def fail(message):
    global failures
    failures += 1
    print(f"[FAIL] {message}")


def load_frontmatter(path):
    text = path.read_text()
    if not text.startswith("---\n"):
        fail(f"frontmatter absent: {path.relative_to(workspace)}")
        return {}
    try:
        return yaml.safe_load(text.split("---\n", 2)[1]) or {}
    except Exception as exc:
        fail(f"frontmatter invalide: {path.relative_to(workspace)} ({exc})")
        return {}


design = load_frontmatter(root / "DESIGN.md")
tokens = yaml.safe_load((root / "tokens.yaml").read_text()) or {}
for path in sorted((root / "references").glob("*.md")):
    load_frontmatter(path)

progressive = design.get("progressive_disclosure", {})
missing = []
for rel in progressive.get("always_load", []):
    path = root / rel
    if not path.exists():
        missing.append(str(path.relative_to(workspace)))
for rel in progressive.get("load_when_needed", {}).values():
    path = root / rel
    if not path.exists():
        missing.append(str(path.relative_to(workspace)))
if missing:
    fail("chemins progressive disclosure absents: " + ", ".join(missing))
else:
    ok("chemins progressive disclosure valides")

required_token_paths = [
    ("status",),
    ("source_checked_at",),
    ("official_reference_check",),
    ("local_scope",),
    ("refresh_when",),
    ("provenance_by_family",),
    ("anti_misuse",),
    ("missing_is_not_absent",),
    ("color_policy",),
    ("colors", "backgrounds"),
    ("colors", "text"),
    ("colors", "borders"),
    ("typography", "primary"),
    ("spacing", "common_tokens"),
    ("layout", "breakpoints"),
    ("components", "required_page_regions"),
]
for parts in required_token_paths:
    cur = tokens
    for part in parts:
        if not isinstance(cur, dict) or part not in cur:
            fail("tokens.yaml clé absente: " + ".".join(parts))
            break
        cur = cur[part]
    else:
        ok("tokens.yaml clé présente: " + ".".join(parts))

for token in ["1v", "2v", "4v", "6v", "8v", "12v", "16v"]:
    if token not in tokens.get("spacing", {}).get("common_tokens", {}):
        fail(f"spacing token absent: {token}")

for bp in ["sm", "md", "lg", "xl"]:
    if bp not in tokens.get("layout", {}).get("breakpoints", {}):
        fail(f"breakpoint absent: {bp}")

if tokens.get("status") != "local-decision-token-subset":
    fail("tokens.yaml status doit rester local-decision-token-subset")

official_check = tokens.get("official_reference_check") or ""
package_version_ref = str(tokens.get("package_version_ref") or "")
if not package_version_ref:
    fail("tokens.yaml package_version_ref manquant")
for needle in [f"@gouvfr/dsfr@{package_version_ref}", "exhaustivité officielle non revendiquée"]:
    if needle not in official_check:
        fail(f"tokens.yaml official_reference_check incomplet: {needle}")

expected_refresh = {"nouvelle_version_dsfr", "publication", "token_absent", "mode_sombre", "portage_framework"}
missing_refresh = sorted(expected_refresh - set(tokens.get("refresh_when") or []))
if missing_refresh:
    fail("tokens.yaml refresh_when incomplet: " + ", ".join(missing_refresh))

expected_provenance = {
    "colors": "officiel_lu",
    "layout": "officiel_lu",
    "patterns": "inféré",
    "shapes_elevation": "à_vérifier",
}
for key, value in expected_provenance.items():
    if tokens.get("provenance_by_family", {}).get(key) != value:
        fail(f"tokens.yaml provenance_by_family.{key} doit être {value}")

anti_misuse = " ".join(tokens.get("anti_misuse") or [])
for needle in ["colors.*", "couleurs hex", "package DSFR", "Marianne", "blue-france", "usage DSFR autorisé"]:
    if needle not in anti_misuse:
        fail(f"tokens.yaml anti_misuse incomplet: {needle}")

missing_rule = tokens.get("missing_is_not_absent") or ""
for needle in ["references/foundations.md", "documentation officielle", "package projet", "tokens.yaml seul"]:
    if needle not in missing_rule:
        fail(f"tokens.yaml missing_is_not_absent incomplet: {needle}")

if failures:
    sys.exit(1)
PY

accent_output=""
md_count=0
while IFS= read -r md_file; do
  md_count=$((md_count + 1))
  output="$(bash "$SCRIPT_DIR/check-accents.sh" "$md_file")"
  if [[ -n "$output" ]]; then
    accent_output+="$output"$'\n'
  fi
done < <(find "$DSFR_DIR" -name '*.md' -type f | sort)

# Zéro fichier inspecté = le contrôle n'a rien prouvé, pas un succès.
if [[ "$md_count" -eq 0 ]]; then
  fail "accents Markdown : aucun fichier .md trouvé sous $DSFR_DIR"
elif [[ -n "$accent_output" ]]; then
  printf '%s' "$accent_output"
  fail "accents Markdown à corriger"
else
  ok "accents Markdown"
fi

if [[ "${AGENTIC_DESIGN_RUN_EXTERNAL_LINT:-0}" == "1" ]]; then
  if npx --yes @google/design.md lint "$DSFR_DIR/DESIGN.md"; then
    ok "lint design.md externe"
  else
    fail "lint design.md externe"
  fi
else
  warn "lint design.md externe non exécuté : activer avec AGENTIC_DESIGN_RUN_EXTERNAL_LINT=1"
fi

git_root="$(git -C "$WORKSPACE" rev-parse --show-toplevel 2>/dev/null || true)"
if [[ "$git_root" == "$WORKSPACE" ]]; then
  if git -C "$WORKSPACE" diff --check -- design-systems/dsfr; then
    ok "git diff --check"
  else
    fail "git diff --check"
  fi
else
  warn "git diff --check non exécuté : le kit n'est pas la racine d'un dépôt Git"
fi

if [[ "$git_root" == "$WORKSPACE" ]]; then
  tracked_ds_store="$(git -C "$WORKSPACE" ls-files -- '*/.DS_Store' 2>/dev/null || true)"
  if [[ -n "$tracked_ds_store" ]]; then
    printf '%s\n' "$tracked_ds_store"
    fail ".DS_Store suivi par Git"
  else
    ok "aucun .DS_Store suivi par Git"
  fi
else
  warn "contrôle des fichiers suivis non exécuté sans dépôt Git propre au kit"
fi

local_ds_store="$(find "$DSFR_DIR" -name '.DS_Store' -type f -print || true)"
if [[ -n "$local_ds_store" ]]; then
  warn ".DS_Store local présent, ignoré par le contrôle Git: ${local_ds_store#$WORKSPACE/}"
fi

if (( failures > 0 )); then
  printf '[FAIL] %d erreur(s)\n' "$failures"
  exit 1
fi

printf '[OK] DSFR design system progressive disclosure\n'
