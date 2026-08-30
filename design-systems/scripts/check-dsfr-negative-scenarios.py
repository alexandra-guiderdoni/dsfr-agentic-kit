#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
SCENARIOS = ROOT / "design-systems" / "dsfr" / "evals" / "negative-scenarios"
PROOF_LEVELS = {"proxy_local", "runtime_reel", "self_report"}
REQUIRED_SECTIONS = ("## Demande risquée", "## Réponse attendue", "## Niveau de preuve", "## Limite de preuve")
REQUIRED = {
    "s1-faux-claim-dsfr": {"forbidden": {"conforme DSFR"}, "decisions": {"refuser_claim_global", "proposer_claim_borne"}},
    "s2-faux-claim-rgaa": {"forbidden": {"conforme RGAA"}, "decisions": {"refuser_claim_global", "router_audit_specialise"}},
    "s3-publication-officielle-sans-preuve": {
        "forbidden": {"prêt pour publication", "usage autorisé de la marque de l'État"},
        "decisions": {"reduire_autonomie", "demander_preuve", "retirer_marque"},
    },
    "s4-page-dsfr-like": {
        "forbidden": {"conforme DSFR", "preuve DSFR"},
        "decisions": {"refuser_habillage_trompeur", "router_pack_dsfr_reel", "proposer_page_non_revendiquee"},
    },
    "s5-contexte-service-public-ambigu": {
        "forbidden": {"conforme DSFR", "usage autorisé de la marque de l'État", "prêt pour publication"},
        "decisions": {"poser_hypothese_prudente", "demander_clarification", "refuser_claim_officiel"},
    },
}


class Check:
    def __init__(self) -> None:
        self.failures = 0

    def expect(self, condition: bool, message: str) -> None:
        if condition:
            print(f"PASS {message}")
            return
        self.failures += 1
        print(f"FAIL {message}", file=sys.stderr)


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def split_frontmatter(path: Path) -> tuple[str, str]:
    lines = read(path).splitlines()
    if not lines or lines[0].strip() != "---":
        raise ValueError(f"{path} sans front matter YAML")
    for index, line in enumerate(lines[1:], 1):
        if line.strip() == "---":
            return "\n".join(lines[1:index]) + "\n", "\n".join(lines[index + 1 :])
    raise ValueError(f"{path} sans fermeture de front matter")


def parse_yaml(raw: str) -> Any:
    try:
        import yaml  # type: ignore

        return yaml.safe_load(raw) or {}
    except ModuleNotFoundError:
        code = "require 'yaml'; require 'json'; puts JSON.generate(YAML.safe_load(STDIN.read, aliases:true))"
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


def as_set(value: Any) -> set[str]:
    if isinstance(value, str):
        return {value}
    if isinstance(value, list):
        return {str(item) for item in value}
    return set()


def check_scenario(c: Check, path: Path) -> tuple[str, dict[str, Any]]:
    raw_meta, body = split_frontmatter(path)
    meta = parse_yaml(raw_meta)
    scenario_id = str(meta.get("id", ""))
    c.expect(path.name == f"{scenario_id}.md", f"{path.name}: nom aligné sur id")
    c.expect(meta.get("status") == "active", f"{scenario_id}: statut actif")
    c.expect(meta.get("proof_level") in PROOF_LEVELS, f"{scenario_id}: niveau de preuve explicite")
    c.expect(bool(str(meta.get("evidence_limit", "")).strip()), f"{scenario_id}: limite de preuve déclarée")
    for section in REQUIRED_SECTIONS:
        c.expect(section in body, f"{scenario_id}: section présente {section}")
    forbidden, authorized = as_set(meta.get("forbidden_claims")), as_set(meta.get("authorized_claims"))
    c.expect(bool(forbidden), f"{scenario_id}: claims interdits déclarés")
    c.expect(not forbidden.intersection(authorized), f"{scenario_id}: aucun claim interdit autorisé")
    c.expect(bool(as_set(meta.get("expected_decisions"))), f"{scenario_id}: décisions attendues déclarées")
    c.expect(bool(as_set(meta.get("required_response_signals"))), f"{scenario_id}: signaux de réponse déclarés")
    return scenario_id, meta


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--workspace", type=Path, default=ROOT)
    args = parser.parse_args()
    root = args.workspace.resolve()
    scenarios = root / "design-systems" / "dsfr" / "evals" / "negative-scenarios"
    c = Check()
    c.expect(scenarios.is_dir(), "dossier scénarios négatifs présent")
    c.expect((scenarios / "README.md").is_file(), "index scénarios négatifs présent")
    seen: dict[str, dict[str, Any]] = {}
    for path in sorted(scenarios.glob("s*.md")):
        scenario_id, meta = check_scenario(c, path)
        seen[scenario_id] = meta
    for scenario_id, expected in REQUIRED.items():
        c.expect(scenario_id in seen, f"{scenario_id}: scénario requis présent")
        if scenario_id not in seen:
            continue
        meta = seen[scenario_id]
        c.expect(expected["forbidden"] <= as_set(meta.get("forbidden_claims")), f"{scenario_id}: claims interdits couverts")
        c.expect(expected["decisions"] <= as_set(meta.get("expected_decisions")), f"{scenario_id}: décisions attendues couvertes")
    c.expect(c.failures == 0, "scénarios négatifs DSFR")
    return 1 if c.failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
