#!/usr/bin/env python3
"""Cartographie explicite des couvertures et trous des moteurs RGAA et DSFR."""
from __future__ import annotations

import collections
import json
import re
from pathlib import Path
from typing import Any

SKILLS_ROOT = Path(__file__).resolve().parents[2]
RGAA_RULES = SKILLS_ROOT / "audit-rgaa-complet/rules/rgaa-rules.json"


def _read(path: Path, fallback: Any) -> Any:
    if not path.is_file():
        return fallback
    return json.loads(path.read_text(encoding="utf-8"))


def _positive_candidate_codes(test: dict[str, Any]) -> list[str]:
    ignored = {
        "test_id", "source_rgaa_locale", "target_count", "target_nodes", "scope",
        "inspectability", "inspection_limits", "human_review_question",
        "human_validation_result", "rendered_text_sample", "source_text_sample",
    }
    positives: list[str] = []
    for item in test.get("observed_evidence", []):
        code, value = str(item.get("code", "")), item.get("value")
        if code in ignored or not code:
            continue
        if isinstance(value, dict) and value.get("status", "") in {"not_collected", "not_collected_static_html"}:
            continue
        if value not in (None, False, "", [], {}):
            positives.append(code)
    return sorted(set(positives))


def generate_engine_coverage(root: Path) -> dict[str, Any]:
    rules = _read(RGAA_RULES, {"rules": []}).get("rules", [])
    rules_by_test: dict[str, list[str]] = collections.defaultdict(list)
    for rule in rules:
        rules_by_test[str(rule["test"])].append(str(rule["rule_id"]))

    decision_paths = sorted((root / "rgaa").glob("P*-DECISIONS-258.json"))
    decision_path = decision_paths[0] if decision_paths else root / "rgaa/DECISIONS-258.json"
    decision_document = _read(decision_path, {"page": {}, "decisions": []})
    page_id = str(decision_document.get("page", {}).get("id") or "P01")
    decisions = decision_document.get("decisions", [])
    decisions_by_test = {str(item.get("test")): item for item in decisions if re.fullmatch(r"\d+\.\d+\.\d+", str(item.get("test", "")))}

    plans = sorted((root / "collectes-ay11").glob("P*/attempt-*/rgaa-collected-plan.json"))
    ay11_tests: dict[str, dict[str, Any]] = {}
    for plan_path in plans:
        plan = _read(plan_path, {})
        for test in plan.get("proof_contract", {}).get("tests", []):
            ay11_tests[str(test.get("test_id"))] = test

    probe_criteria: dict[str, list[str]] = collections.defaultdict(list)
    for probe_path in sorted((root / "collectes-ay11").glob("P*/attempt-*/*.json")):
        if probe_path.name == "rgaa-collected-plan.json":
            continue
        probe = _read(probe_path, {})
        criterion_id = str(probe.get("criterion_id", ""))
        if criterion_id:
            probe_criteria[criterion_id].append(str(probe_path.relative_to(root)))

    official_tests = sorted(
        set(decisions_by_test) or set(ay11_tests),
        key=lambda value: tuple(int(part) for part in value.split(".")),
    )
    rows: list[dict[str, Any]] = []
    for test_id in official_tests:
        decision = decisions_by_test.get(test_id, {})
        criterion = ".".join(test_id.split(".")[:2])
        executable_rules = sorted(rules_by_test.get(test_id, []))
        candidate_codes = _positive_candidate_codes(ay11_tests.get(test_id, {}))
        coverage_mode = str(decision.get("coverage_mode", "NON_DECLARE"))
        probes = sorted(probe_criteria.get(criterion, []))
        ay11_collected = ay11_tests.get(test_id, {}).get("collection_status") == "collected"
        flags: list[str] = []
        if not executable_rules:
            flags.append("SANS_REGLE_EXECUTABLE")
        if candidate_codes and not executable_rules and coverage_mode not in {"COLLECTEUR_AY11_QUALIFIE", "COLLECTEUR_AY11_PARTIEL", "SONDE_AY11_PARTIELLE"}:
            flags.append("SIGNAUX_AY11_NON_BRANCHES")
        if decision.get("status") in {"C_CONFIRMEE", "NC_CONFIRMEE", "NA_CONFIRMEE"} and coverage_mode == "NON_DECLARE":
            flags.append("DECISION_CONFIRMEE_SANS_COUVERTURE_DECLAREE")
        if decision.get("status") == "A_RETESTER":
            flags.append("PROTOCOLE_COMPLEMENTAIRE_REQUIS")
        rows.append({
            "test": test_id,
            "criterion": criterion,
            "decision_status": decision.get("status", "NON_DOCUMENTE"),
            "coverage_mode": coverage_mode,
            "coverage_complete": bool(decision.get("coverage_complete", False)),
            "executable_rules": executable_rules,
            "ay11_collection_status": ay11_tests.get(test_id, {}).get("collection_status", "ABSENT"),
            "ay11_collected": ay11_collected,
            "ay11_probes": probes,
            "positive_candidate_codes": candidate_codes,
            "flags": flags,
        })

    dsfr_page = _read(root / f"dsfr/pages/{page_id}.json", {"inventory": []})
    dsfr_dimension_path = root / f"dsfr/{page_id}-COUVERTURE-DIMENSIONNELLE.json"
    dsfr_dimensions = _read(dsfr_dimension_path, {"summary": {}, "families": [], "classes": []})
    dimensions_by_family = {str(item.get("component")): item for item in dsfr_dimensions.get("families", [])}
    dsfr_rows = []
    for item in dsfr_page.get("inventory", []):
        executed = sorted(item.get("rules_executed", []))
        dsfr_flags = []
        if not executed:
            dsfr_flags.append("COMPOSANT_DETECTE_SANS_REGLE")
        if len(executed) == 1:
            dsfr_flags.append("COUVERTURE_UNIDIMENSIONNELLE_A_REVOIR")
        dimension_row = dimensions_by_family.get(str(item.get("name")), {})
        incomplete_dimensions = list(dimension_row.get("incomplete_dimensions", []))
        if incomplete_dimensions:
            dsfr_flags.append("DIMENSIONS_COMPLEMENTAIRES_REQUISES")
        dsfr_rows.append({
            "component": item.get("name"), "instances": item.get("count", 0),
            "rules_executed": executed, "status": item.get("status"),
            "incomplete_dimensions": incomplete_dimensions,
            "coverage_complete": bool(dimension_row.get("coverage_complete", False)),
            "flags": dsfr_flags,
        })

    summary = {
        "official_rgaa_tests": len(official_tests),
        "rgaa_catalog_rules": len(rules),
        "rgaa_tests_with_executable_rule": sum(bool(row["executable_rules"]) for row in rows),
        "rgaa_tests_without_executable_rule": sum("SANS_REGLE_EXECUTABLE" in row["flags"] for row in rows),
        "rgaa_tests_collected_by_ay11": sum(row["ay11_collected"] for row in rows),
        "rgaa_tests_with_ay11_probe": sum(bool(row["ay11_probes"]) for row in rows),
        "rgaa_tests_with_declared_coverage": sum(row["coverage_mode"] != "NON_DECLARE" for row in rows),
        "ay11_positive_tests_unlinked_to_decision": sum("SIGNAUX_AY11_NON_BRANCHES" in row["flags"] for row in rows),
        "confirmed_decisions_without_declared_coverage": sum("DECISION_CONFIRMEE_SANS_COUVERTURE_DECLAREE" in row["flags"] for row in rows),
        "rgaa_tests_requiring_additional_protocol": sum("PROTOCOLE_COMPLEMENTAIRE_REQUIS" in row["flags"] for row in rows),
        "dsfr_catalog_rules": int(dsfr_dimensions.get("summary", {}).get("catalog_rules", 0)),
        "observed_dsfr_class_tokens": int(dsfr_dimensions.get("summary", {}).get("observed_fr_classes", 0)),
        "dsfr_class_tokens_targeted_by_rule": int(dsfr_dimensions.get("summary", {}).get("classes_targeted_by_rule", 0)),
        "dsfr_class_tokens_inventory_only": int(dsfr_dimensions.get("summary", {}).get("classes_inventory_only", 0)),
        "detected_dsfr_component_families": len(dsfr_rows),
        "dsfr_families_with_complete_multidimensional_coverage": sum(row["coverage_complete"] for row in dsfr_rows),
        "dsfr_families_without_rule": sum("COMPOSANT_DETECTE_SANS_REGLE" in row["flags"] for row in dsfr_rows),
        "dsfr_families_with_one_rule_only": sum("COUVERTURE_UNIDIMENSIONNELLE_A_REVOIR" in row["flags"] for row in dsfr_rows),
    }
    ay11_retest_decisions = [{"id": f"AY11-UNLINKED-{row['test'].replace('.', '-')}", "test": row["test"], "criterion": row["criterion"], "status": "A_RETESTER", "reason": "Signaux AY11 collectés sans règle exécutable reliée à une décision.", "candidate_codes": row["positive_candidate_codes"], "evidence": [path for path in row["ay11_probes"]]} for row in rows if "SIGNAUX_AY11_NON_BRANCHES" in row["flags"]]
    result = {
        "schema_version": 2,
        "claim": "Cette cartographie mesure les branchements du moteur, pas la conformité RGAA ou DSFR.",
        "summary": summary,
        "ay11_retest_decisions": ay11_retest_decisions,
        "rgaa_tests": rows,
        "dsfr_components": dsfr_rows,
        "dsfr_class_coverage": dsfr_dimensions.get("classes", []),
        "dsfr_dimension_coverage_source": str(dsfr_dimension_path.relative_to(root)) if dsfr_dimension_path.is_file() else "ABSENTE",
        "limits": [
            "Un test sans règle exécutable peut relever d’un protocole humain, mais il doit rester explicitement visible.",
            "Une règle DSFR unique ne couvre pas nécessairement structure, états, clavier, responsive et contenu.",
            "Les preuves AY11 collectées doivent être branchées dans la qualification et le rapport pour ne pas devenir des signaux orphelins.",
        ],
    }
    (root / "COUVERTURE-MOTEURS.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    md = [
        "# Couverture des moteurs RGAA et DSFR", "",
        result["claim"], "", "## Synthèse", "",
        "| Indicateur | Valeur |", "|---|---:|",
    ]
    labels = {
        "official_rgaa_tests": "Tests RGAA officiels inventoriés",
        "rgaa_catalog_rules": "Règles RGAA exécutables",
        "rgaa_tests_with_executable_rule": "Tests RGAA avec au moins une règle exécutable",
        "rgaa_tests_without_executable_rule": "Tests RGAA sans règle exécutable",
        "rgaa_tests_collected_by_ay11": "Tests avec collecte AY11 test-spécifique",
        "rgaa_tests_with_ay11_probe": "Tests rattachés à une sonde AY11",
        "rgaa_tests_with_declared_coverage": "Tests avec mode de couverture déclaré",
        "ay11_positive_tests_unlinked_to_decision": "Tests avec signaux AY11 non reliés à la décision",
        "confirmed_decisions_without_declared_coverage": "Décisions confirmées sans couverture déclarée",
        "rgaa_tests_requiring_additional_protocol": "Tests à retester",
        "dsfr_catalog_rules": "Règles du catalogue DSFR",
        "observed_dsfr_class_tokens": "Classes fr-* observées",
        "dsfr_class_tokens_targeted_by_rule": "Classes fr-* citées par une règle",
        "dsfr_class_tokens_inventory_only": "Classes fr-* seulement inventoriées",
        "detected_dsfr_component_families": "Familles DSFR détectées",
        "dsfr_families_with_complete_multidimensional_coverage": "Familles DSFR à couverture multidimensionnelle complète",
        "dsfr_families_without_rule": "Familles DSFR sans règle",
        "dsfr_families_with_one_rule_only": "Familles DSFR avec une seule règle",
    }
    md.extend(f"| {labels[key]} | {value} |" for key, value in summary.items())
    md += ["", "## Trous RGAA prioritaires", "", "| Test | Décision | Mode de couverture | Règles | Signaux AY11 | Drapeaux |", "|---|---|---|---|---|---|"]
    for row in rows:
        if row["flags"]:
            md.append(f"| {row['test']} | {row['decision_status']} | {row['coverage_mode']} | {', '.join(row['executable_rules']) or 'aucune'} | {', '.join(row['positive_candidate_codes']) or 'aucun'} | {', '.join(row['flags'])} |")
    md += ["", "## Décisions A_RETESTER issues d’AY11", "", "| Identifiant | Critère | Test | Signaux | Preuves |", "|---|---|---|---|---|"]
    for item in ay11_retest_decisions:
        md.append(f"| `{item['id']}` | {item['criterion']} | {item['test']} | {', '.join(item['candidate_codes']) or 'aucun'} | {', '.join(item['evidence']) or 'collecte AY11'} |")
    md += ["", "## Couverture DSFR par famille détectée", "", "| Composant | Instances | Règles | Statut | Dimensions partielles | Drapeaux |", "|---|---:|---|---|---|---|"]
    for row in dsfr_rows:
        md.append(f"| {row['component']} | {row['instances']} | {', '.join(row['rules_executed']) or 'aucune'} | {row['status']} | {', '.join(row['incomplete_dimensions']) or 'aucune'} | {', '.join(row['flags']) or 'aucun'} |")
    md += ["", "## Limites", ""] + [f"- {item}" for item in result["limits"]]
    (root / "COUVERTURE-MOTEURS.md").write_text("\n".join(md) + "\n", encoding="utf-8")
    return result


if __name__ == "__main__":
    import sys
    if len(sys.argv) != 2:
        raise SystemExit("Usage: engine_coverage.py CAMPAIGN_ROOT")
    value = generate_engine_coverage(Path(sys.argv[1]).resolve())
    print(json.dumps(value["summary"], ensure_ascii=False))
