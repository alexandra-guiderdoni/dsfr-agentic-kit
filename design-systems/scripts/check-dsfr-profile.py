#!/usr/bin/env python3
# PDG-LARGE-FILE-JUSTIFICATION: validateur contractuel autonome gardé dans un seul exécutable ; plafond local strict à 220 lignes.
from __future__ import annotations
import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import Any
ROOT = Path(__file__).resolve().parents[2]
DSFR = ROOT / "design-systems" / "dsfr"
DESIGN = DSFR / "DESIGN.md"
TOKENS = DSFR / "tokens.yaml"
REFS = DSFR / "references"
SMOKE = DSFR / "evals" / "profile-skill-smoke.md"
SKILL = ROOT / ".claude" / "skills" / "dsfr-components" / "SKILL.md"
CHANGELOG_SKILL = ROOT / ".claude" / "skills" / "dsfr-changelog" / "SKILL.md"

LABELS = {"officiel_lu", "local_lu", "inféré", "à_vérifier", "hors_périmètre"}
GROUPS = {"colors", "typography", "spacing", "rounded", "components"}
BRANCHES = {"page complète", "composant isolé", "routage audit DSFR ponctuel"}
EVIDENCE_FAMILIES = {"colors", "typography", "spacing", "layout", "components", "claims"}
CLAIMS = {"aligné DSFR avec limites", "prototype DSFR à vérifier avant publication", "structure inspirée des fondamentaux DSFR", "composants DSFR utilisés selon les sources lues"}
FORBIDDEN = {"conforme DSFR", "conforme RGAA", "prêt pour publication", "usage autorisé de la marque de l'État"}
REQ_REFS = {"references/index.md", "references/agent-recipes.md", "references/foundations.md", "references/page-shell.md", "references/components-routing.md", "references/forms-models.md", "references/figma-handoff.md", "references/verification.md", "references/sources.md"}
SMOKE_IDS = {"pos-profile-page", "pos-page-form", "pos-rdv-page", "pos-component-accordion", "pos-form-field", "pos-publication-guard", "pos-version-migration", "near-miss-service-public-no-dsfr", "near-miss-rgaa-complete", "near-miss-google-strict", "near-miss-token-catalog", "near-miss-dsfr-like-landing"}

class Check:
    def __init__(self) -> None:
        self.ok: list[str] = []
        self.bad: list[str] = []
        self.skip: list[str] = []

    def expect(self, cond: bool, msg: str) -> None:
        (self.ok if cond else self.bad).append(("PASS " if cond else "FAIL ") + msg)

    def skipped(self, msg: str) -> None:
        self.skip.append("SKIP " + msg)

    def finish(self) -> int:
        for line in self.ok + self.skip:
            print(line)
        for line in self.bad:
            print(line, file=sys.stderr)
        if self.bad:
            return 1
        print("PASS contrat profil DSFR")
        return 0

def rd(path: Path) -> str:
    return path.read_text(encoding="utf-8")

def fm(path: Path) -> tuple[str, str]:
    lines = rd(path).splitlines()
    if not lines or lines[0].strip() != "---":
        raise ValueError(f"{path} sans front matter YAML")
    for index, line in enumerate(lines[1:], 1):
        if line.strip() == "---":
            return "\n".join(lines[1:index]) + "\n", "\n".join(lines[index + 1 :])
    raise ValueError(f"{path} sans fermeture de front matter")

def yml(raw: str) -> Any:
    try:
        import yaml  # type: ignore

        return yaml.safe_load(raw)
    except ModuleNotFoundError:
        code = "require 'yaml'; require 'json'; require 'date'; puts JSON.generate(YAML.safe_load(STDIN.read, permitted_classes:[Date], aliases:true))"
        try:
            run = subprocess.run(["ruby", "-e", code], input=raw, text=True, capture_output=True)
        except FileNotFoundError:
            raise RuntimeError(
                "PyYAML absent et ruby indisponible : installer PyYAML "
                "(ou lancer via scripts/lib/python-with-pyyaml.sh, qui utilise uv)"
            )
        if run.returncode:
            raise RuntimeError(
                "fallback ruby en échec (PyYAML absent) : " + run.stderr.strip()
            )
        return json.loads(run.stdout)

def walk(node: Any, path: tuple[str, ...] = ()) -> list[tuple[tuple[str, ...], Any]]:
    out: list[tuple[tuple[str, ...], Any]] = []
    if isinstance(node, dict):
        for key, value in node.items():
            child = path + (str(key),)
            out.append((child, value))
            out.extend(walk(value, child))
    elif isinstance(node, list):
        for index, value in enumerate(node):
            out.extend(walk(value, path + (str(index),)))
    return out

def flat(value: Any) -> list[str]:
    if isinstance(value, str):
        return [value]
    if isinstance(value, list):
        return [item for sub in value for item in flat(sub)]
    if isinstance(value, dict):
        return [item for sub in value.values() for item in flat(sub)]
    return []

def evidence_path(item: str) -> Path:
    raw = item.split("#", 1)[0]
    if raw.startswith((".claude/", "design-systems/")):
        return ROOT / raw
    return DSFR / raw

def branch_map(raw: str) -> set[str]:
    found: set[str] = set()
    active = False
    for line in raw.splitlines():
        if line.strip() == "## BRANCH-MAP":
            active = True
            continue
        if active and line.startswith(("## ", "### ")):
            break
        if active and line.startswith("|"):
            first = line.strip().strip("|").split("|")[0].strip()
            if first not in {"Branche", "---"} and set(first) != {"-"}:
                found.add(first)
    return found

def check_tokens(c: Check, tokens: Any) -> None:
    projection = tokens.get("design_md_projection", {})
    meta = tokens.get("components", {}).get("decision_tokens_meta", {})
    c.expect(projection.get("google_format") == "inspired_not_compliant", "tokens inspired_not_compliant")
    c.expect(set(projection.get("google_groups", {})) >= GROUPS, "groupes Google utiles couverts")
    c.expect(meta.get("exhaustive") is False and meta.get("normative_source") is False, "decision_tokens non exhaustif et non normatif")
    c.expect(bool(tokens.get("missing_is_not_absent")), "missing_is_not_absent présent")

    evidence = flat(tokens.get("evidence_by_family", {}))
    for path, value in walk(tokens):
        key = path[-1]
        if key == "evidence":
            evidence.extend(flat(value))
        if key in {"provenance", "source_status", "class_provenance"}:
            c.expect(value in LABELS, f"label valide: {'.'.join(path)}")
    c.expect(EVIDENCE_FAMILIES <= set(tokens.get("evidence_by_family", {})), "evidence_by_family complet")
    c.expect(bool(evidence), "pointeurs evidence présents")
    for item in sorted(set(evidence)):
        c.expect(evidence_path(item).exists(), f"evidence existe: {item}")
    for name, role in tokens.get("typography_roles", {}).items():
        strong = role.get("class_provenance") in {"officiel_lu", "local_lu"} or role.get("provenance") in {"officiel_lu", "local_lu"}
        if strong:
            c.expect(bool(role.get("evidence")), f"typography_roles.{name} porte une evidence")
    for name, token in tokens.get("components", {}).get("decision_tokens", {}).items():
        strong = token.get("provenance") in {"officiel_lu", "local_lu"} or token.get("source_status") in {"officiel_lu", "local_lu"}
        if strong:
            c.expect(bool(token.get("evidence")), f"decision_tokens.{name} porte une evidence")

def check_runtime(c: Check, path: Path | None) -> None:
    if path is None:
        c.skipped("runtime sélection de skill non observable sans --runtime-trace")
        return
    c.expect(path.exists(), f"trace runtime existe: {path}")
    if not path.exists():
        return
    raw = rd(path)
    for needle in ["dsfr-components", "DESIGN.md", "tokens.yaml"]:
        c.expect(needle in raw, f"trace runtime mentionne {needle}")
    signals = SMOKE_IDS | {"Crée une page HTML statique DSFR", "accordéon DSFR", "champ date DSFR", "publication officielle"}
    c.expect(any(signal in raw for signal in signals), "trace runtime contient un cas smoke")

def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--runtime-trace", type=Path)
    args = parser.parse_args()
    c = Check()
    required_paths = [DESIGN, TOKENS, SMOKE, SKILL, CHANGELOG_SKILL]
    manquants = [path for path in required_paths if not path.exists()]
    for path in required_paths:
        c.expect(path.exists(), f"{path.relative_to(ROOT)} existe")
    if manquants:
        return c.finish()
    design_yaml, design_body = fm(DESIGN)
    design, tokens, skill = yml(design_yaml), yml(rd(TOKENS)), rd(SKILL)
    changelog_skill = rd(CHANGELOG_SKILL)
    relation = design.get("design_md_relation", {})
    c.expect(relation.get("google_format") == "inspired_not_compliant", "DESIGN inspired_not_compliant")
    c.expect(relation.get("token_source") == "tokens.yaml" and relation.get("detail_source") == "references/", "DESIGN pointe vers tokens et references")
    c.expect(relation.get("primary_consumer") == ".claude/skills/dsfr-components", "DESIGN cible dsfr-components")
    c.expect(relation.get("migration_consumer") == ".claude/skills/dsfr-changelog", "DESIGN cible dsfr-changelog pour les migrations")
    c.expect(bool(design.get("package_version_ref")) and design.get("package_version_ref") == tokens.get("package_version_ref"), "package_version_ref identique entre DESIGN et tokens")
    listed = set(map(str, design.get("progressive_disclosure", {}).get("load_when_needed", {}).values()))
    c.expect(REQ_REFS <= listed, "références requises listées dans DESIGN")
    for ref in sorted(REQ_REFS):
        c.expect((DSFR / ref).exists(), f"{ref} existe")
    c.expect(CLAIMS <= set(design.get("claim_language", {}).get("allowed", [])), "claims autorisés complets")
    c.expect(FORBIDDEN <= set(design.get("claim_language", {}).get("forbidden_without_proof", [])), "claims interdits complets")
    c.expect("references/index.md" in design_body and "references/agent-recipes.md" in design_body, "DESIGN référence index et recettes")
    c.expect("dsfr-changelog" in design_body, "DESIGN route les comparaisons de versions")
    c.expect(len(rd(DESIGN).splitlines()) <= 320, "DESIGN reste court")
    check_tokens(c, tokens)
    smoke, recipes = rd(SMOKE), rd(REFS / "agent-recipes.md")
    for smoke_id in sorted(SMOKE_IDS):
        c.expect(smoke_id in smoke, f"smoke {smoke_id} présent")
    c.expect("design-systems/dsfr/DESIGN.md" in skill and "design-systems/dsfr/tokens.yaml" in skill, "skill pointe vers le profil")
    c.expect("profil DSFR partagé" in skill, "skill nomme le profil partagé")
    c.expect("dsfr-changelog" in skill, "dsfr-components exclut les migrations")
    c.expect("Comparer deux versions DSFR" in changelog_skill, "dsfr-changelog porte le contrat de comparaison")
    c.expect(BRANCHES <= branch_map(skill), "BRANCH-MAP expose les branches attendues")
    c.expect(all(f"`{branch}`" in recipes for branch in BRANCHES), "recettes citent les branches attendues")
    for path in [REFS / "index.md", REFS / "agent-recipes.md", SMOKE]:
        c.expect(len(rd(path).splitlines()) <= 200, f"{path.relative_to(ROOT)} sous 200 lignes")
    c.expect(len(rd(Path(__file__).resolve()).splitlines()) <= 220, "check-dsfr-profile.py sous 220 lignes")
    check_runtime(c, args.runtime_trace)
    return c.finish()

if __name__ == "__main__":
    raise SystemExit(main())
