#!/usr/bin/env python3
"""Construit le catalogue RGAA embarqué à partir de la source officielle.

Le runner n'exécute pas ce script pendant un audit. Il sert aux mainteneurs à
reconstruire le fichier versionné après publication d'une nouvelle source.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path
from typing import Any


SOURCE_URL = "https://accessibilite.numerique.gouv.fr/methode/criteres-et-tests/"
SOURCE_REPOSITORY = "https://github.com/DISIC/accessibilite.numerique.gouv.fr"


def read(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def build(source: Path) -> dict[str, Any]:
    criteria_source = read(source / "criteres.json")
    methodologies = read(source / "methodologies.json")
    manifest = read(source / "manifest.json")
    themes: list[dict[str, Any]] = []
    criteria: list[dict[str, Any]] = []
    tests: list[dict[str, Any]] = []
    for topic in criteria_source["topics"]:
        theme_slug = re.sub(r"[^a-z0-9]+", "-", topic["topic"].lower().encode("ascii", "ignore").decode()).strip("-")
        theme_id = f"theme-{int(topic['number']):02d}-{theme_slug}"
        theme_criteria: list[str] = []
        for item in topic["criteria"]:
            criterion = item["criterium"]
            criterion_id = f"{topic['number']}.{criterion['number']}"
            test_ids = [f"{criterion_id}.{number}" for number in criterion.get("tests", {})]
            theme_criteria.append(criterion_id)
            criteria.append({
                "criterion_id": criterion_id,
                "number": criterion["number"],
                "theme_id": theme_id,
                "title": criterion.get("title", ""),
                "references": criterion.get("references", []),
                "particular_cases": criterion.get("particularCases", []),
                "technical_note": criterion.get("technicalNote", []),
                "test_ids": test_ids,
                "source_url": f"{SOURCE_URL}#{criterion_id}",
            })
            for number, content in criterion.get("tests", {}).items():
                test_id = f"{criterion_id}.{number}"
                title = content[0] if content else ""
                tests.append({
                    "test_id": test_id,
                    "criterion_id": criterion_id,
                    "number": int(number),
                    "title": title,
                    "methodology": methodologies.get(test_id, ""),
                    "source_url": f"{SOURCE_URL}#{test_id}",
                    "human_validation_required": True,
                })
        themes.append({
            "theme_id": theme_id,
            "number": topic["number"],
            "name": topic["topic"],
            "criterion_ids": theme_criteria,
        })
    source_files = {}
    for name in ("criteres.json", "methodologies.json", "manifest.json"):
        source_files[name] = hashlib.sha256((source / name).read_bytes()).hexdigest()
    return {
        "schema_version": 1,
        "referential_id": "rgaa-4.1.2",
        "version": "4.1.2",
        "source": {
            "url": SOURCE_URL,
            "repository": SOURCE_REPOSITORY,
            "commit": manifest.get("source_commit", ""),
            "license": "Licence Ouverte 2.0",
            "files_sha256": source_files,
        },
        "counts": {
            "themes": len(themes),
            "criteria": len(criteria),
            "tests": len(tests),
        },
        "themes": themes,
        "criteria": criteria,
        "tests": tests,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Construit le référentiel RGAA embarqué")
    parser.add_argument("source", type=Path, help="Dossier officiel 4.1.2")
    parser.add_argument("output", type=Path, help="Catalogue JSON à écrire")
    args = parser.parse_args()
    value = build(args.source.expanduser().resolve())
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Référentiel écrit : {args.output} ({value['counts']['criteria']} critères, {value['counts']['tests']} tests)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
