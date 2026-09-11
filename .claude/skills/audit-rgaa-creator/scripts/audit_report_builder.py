#!/usr/bin/env python3
"""Adapte les résultats RGAA/DSFR au builder de pages DSFR assemblées."""

from __future__ import annotations

import hashlib
import json
import os
import re
import subprocess
import sys
import urllib.parse
from pathlib import Path
from typing import Any

SKILLS_ROOT = Path(__file__).resolve().parents[2]
BUILDER = SKILLS_ROOT / "dsfr-components/scripts/generate_assembled_page.py"
BUILDER_SCHEMA = (
    SKILLS_ROOT / "dsfr-components/schemas/generate_assembled_page.schema.json"
)
DSFR_RULE_CATALOG = SKILLS_ROOT / "audit-dsfr-complet/rules/dsfr-rules.json"
DSFR_RULE_CATALOG_RELATIVE = "audit-dsfr-complet/rules/dsfr-rules.json"


def _read_required(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise ValueError(f"Entrée canonique absente : {path}") from exc
    except OSError as exc:
        raise ValueError(f"Entrée canonique illisible : {path} ({exc})") from exc
    except json.JSONDecodeError as exc:
        raise ValueError(f"Entrée canonique JSON invalide : {path} ({exc})") from exc


def _plain_hyphens(value: Any, key: str = "") -> Any:
    if isinstance(value, dict):
        return {name: _plain_hyphens(item, name) for name, item in value.items()}
    if isinstance(value, list):
        return [_plain_hyphens(item, key) for item in value]
    if isinstance(value, str) and key not in {"observed_code", "expected_code"}:
        return value.replace("—", "-").replace("–", "-")
    return value


def _write(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(
        json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    temporary.replace(path)


def _digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _dsfr_catalog_status(root: Path, active: bool) -> dict[str, Any]:
    raw = DSFR_RULE_CATALOG.read_bytes()
    catalog = json.loads(raw.decode("utf-8"))
    current = {
        "path": DSFR_RULE_CATALOG_RELATIVE,
        "sha256": hashlib.sha256(raw).hexdigest(),
        "schema_version": catalog.get("schema_version"),
        "target_version": str(catalog.get("target_version", "")),
        "rules_count": len(catalog.get("rules", [])),
    }
    if not active:
        return {
            "status": "NON_APPLICABLE",
            "message": "Le catalogue DSFR n’est pas utilisé par cette campagne.",
            "current": current,
            "observed": [],
            "missing_pages": [],
            "stale_pages": [],
        }
    fingerprints: dict[str, list[str]] = {}
    missing: list[str] = []
    for path in sorted((root / "dsfr/pages").glob("P*.json")):
        data = _read_required(path)
        page_id = str((data.get("page") or {}).get("id") or path.stem)
        fingerprint = (data.get("rule_catalog") or {}).get("sha256")
        if not fingerprint:
            missing.append(page_id)
        else:
            fingerprints.setdefault(str(fingerprint), []).append(page_id)
    stale = sorted(
        page
        for fingerprint, page_ids in fingerprints.items()
        if fingerprint != current["sha256"]
        for page in page_ids
    )
    if not fingerprints or missing:
        status = "EMPREINTE_ABSENTE"
        message = "Le rapport DSFR ne permet pas de prouver le catalogue de règles utilisé ; régénérer les archives avec l’empreinte du catalogue."
    elif stale:
        status = "CATALOGUE_OBSOLETE"
        message = f"Le rapport DSFR a été produit avec une ancienne version du catalogue de règles pour {', '.join(stale)} ; régénérer ces pages."
    elif len(fingerprints) > 1:
        status = "CATALOGUES_MULTIPLES"
        message = "Le rapport DSFR mélange plusieurs empreintes de catalogue ; régénérer toutes les pages avec une version unique."
    else:
        status = "A_JOUR"
        message = "Le rapport DSFR est produit avec l’empreinte courante du catalogue de règles."
    return {
        "status": status,
        "message": message,
        "current": current,
        "observed": sorted(fingerprints),
        "missing_pages": missing,
        "stale_pages": stale,
    }


def _relative_href(campaign_root: Path, output_dir: Path, value: str) -> str:
    raw = str(value).strip()
    decoded = urllib.parse.unquote(raw)
    if (
        not raw
        or raw != decoded
        or "\\" in raw
        or Path(raw).is_absolute()
        or re.match(r"^[A-Za-z]:[\\/]", raw)
    ):
        raise ValueError(f"Chemin de preuve non portable : {value}")
    root = campaign_root.resolve()
    target = (root / raw).resolve()
    if target != root and root not in target.parents:
        raise ValueError(f"Preuve hors campagne : {value}")
    if not target.is_file():
        raise ValueError(f"Preuve absente : {value}")
    return Path(os.path.relpath(target, output_dir.resolve())).as_posix()


def _evidence(
    campaign_root: Path, output_dir: Path, values: list[str]
) -> list[dict[str, str]]:
    return [
        {
            "label": f"Preuve {index}",
            "href": _relative_href(campaign_root, output_dir, value),
        }
        for index, value in enumerate(values, 1)
    ]


def _review_text(item: dict[str, Any]) -> str:
    qualification = item.get("qualification") or {}
    return str(
        qualification.get("comment")
        or item.get("review")
        or "Signal non encore qualifié humainement."
    )


def _rgaa_findings(
    document: dict[str, Any], root: Path, output: Path, with_page_links: bool
) -> list[dict[str, Any]]:
    rows = []
    for item in document.get("findings", []):
        page = str(item.get("page", "GLOBAL"))
        row = {
            "id": str(item.get("id", "")),
            "page": page,
            "page_name": str(item.get("page_name", page)),
            "rule": str(item.get("rule_id", "")),
            "criterion": str(item.get("criterion", "")),
            "test": str(item.get("test", "")),
            "status": str(item.get("qualification_status", "NON_TESTE")),
            "severity": str(item.get("severity", "À qualifier")),
            "title": str(item.get("title", "Constat RGAA")),
            "selector": str(item.get("selector", "-")),
            "observed": str(item.get("observed", "")),
            "observed_code": str(item.get("observed_code", "")),
            "origin": str(item.get("observed_origin", "PREUVE")),
            "expected_code": str(item.get("expected_code", "")),
            "failed_assertions": [
                str(value) for value in item.get("failed_assertions", [])
            ],
            "impact": str(item.get("impact", "Impact à qualifier.")),
            "source": str(item.get("source", "")),
            "source_label": f"RGAA 4.1.2 - test {item.get('test', '-')}",
            "recommendation": str(item.get("recommendation", "")),
            "verification": str(item.get("verification", "")),
            "review": _review_text(item),
            "evidence": _evidence(root, output.parent, item.get("evidence", [])),
        }
        if with_page_links:
            row["page_href"] = f"pages-html/{page}.html"
        rows.append(row)
    return rows


def _dsfr_findings(
    document: dict[str, Any], root: Path, output: Path, with_page_links: bool
) -> list[dict[str, Any]]:
    rows = []
    for item in document.get("differences", []):
        page = str(item.get("page", "GLOBAL"))
        kind = str(item.get("kind", "integration"))
        row = {
            "id": str(item.get("id", "")),
            "page": page,
            "page_name": str(item.get("page_name", page)),
            "rule": str(item.get("rule_id", "")),
            "criterion": kind,
            "test": str(item.get("assessed_against", "")),
            "status": str(item.get("qualification_status", "A_CONFIRMER")),
            "severity": str(item.get("severity", "À qualifier")),
            "title": f"{item.get('title', 'Constat DSFR')} - {kind}",
            "selector": str(item.get("selector", "-")),
            "observed": str(item.get("observed", "")),
            "observed_code": str(item.get("observed_html", "")),
            "origin": str(item.get("observed_html_origin", "PREUVE")),
            "expected_code": str(item.get("expected_html", "")),
            "failed_assertions": [
                str(value) for value in item.get("failed_conditions", [])
            ],
            "impact": f"Signal de {kind} à apprécier dans le périmètre de la règle exécutée.",
            "source_label": str(item.get("source", "Source DSFR locale")),
            "recommendation": str(item.get("recommendation", "")),
            "verification": str(item.get("verification", "")),
            "review": _review_text(item),
            "evidence": _evidence(root, output.parent, item.get("evidence", [])),
        }
        if with_page_links:
            row["page_href"] = f"pages-html/{page}.html"
        rows.append(row)
    return rows


def _causes(values: list[dict[str, Any]], prefix: str = "") -> list[dict[str, Any]]:
    return [
        {
            "rule": str(item.get("rule_id", "")),
            "criterion": str(item.get("criterion", item.get("kind", "-"))),
            "test": str(item.get("test", item.get("component", "-"))),
            "severity": str(item.get("severity") or "À qualifier"),
            "title": f"{prefix}{item.get('title') if item.get('title') not in {None, '', 'None'} else 'Cause'}",
            "count": int(item.get("count", 0)),
            "confirmed": int(item.get("confirmed", 0)),
            "pages": [str(value) for value in item.get("pages", [])],
        }
        for item in values
    ]


def _config(
    title: str,
    description: str,
    report_type: str,
    claim: str,
    metrics: list[dict[str, Any]],
    links: list[dict[str, str]],
    causes: list[dict[str, Any]],
    findings: list[dict[str, Any]],
    pages: list[dict[str, str]] | None = None,
    home_href: str = "PORTAIL-AUDITS.html",
    show_root_causes: bool = True,
    show_empty_findings: bool = True,
    sample_pages: list[dict[str, Any]] | None = None,
    sample_title: str = "Pages de l’échantillon",
    catalog_status: dict[str, Any] | None = None,
) -> dict[str, Any]:
    dsfr_labels = report_type == "DSFR"
    return {
        "title": title,
        "description": description,
        "main_title": title,
        "brand_mode": "neutral",
        "header": {
            "brand_mode": "neutral",
            "service_title": "Rapports d’audit",
            "service_tagline": f"Consultation des preuves {report_type}",
            "home_url": home_href,
        },
        "footer": {
            "brand_mode": "neutral",
            "service_name": "Rapports d’audit",
            "content_desc": "Livrables techniques générés par le harnais ; aucun statut officiel implicite.",
            "content_links": [],
            "bottom_links": [],
        },
        "sections": [
            {
                "block": "audit_report",
                "section_id": "resultats-audit",
                "report_type": report_type,
                "claim": claim,
                "filters": bool(findings),
                "metrics": metrics,
                "links": links,
                "pages": pages or [],
                "sample_pages": sample_pages
                if sample_pages is not None
                else (pages or []),
                "sample_title": sample_title,
                "root_causes": causes,
                "findings": findings,
                "criterion_label": "Nature" if dsfr_labels else "Critère",
                "test_label": "Évaluation" if dsfr_labels else "Test",
                "show_root_causes": show_root_causes,
                "show_empty_findings": show_empty_findings,
                "catalog_status": catalog_status or {},
            }
        ],
    }


def _build(config: dict[str, Any], config_path: Path, output_path: Path) -> None:
    config = _plain_hyphens(config)
    _write(config_path, config)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    check = subprocess.run(
        [sys.executable, str(BUILDER), "--config-file", str(config_path), "--check"],
        text=True,
        capture_output=True,
    )
    if check.returncode:
        raise RuntimeError(
            f"Builder DSFR en échec pour {output_path}: {(check.stderr or check.stdout)[-1500:]}"
        )
    if output_path.exists():
        output_path.unlink()
    result = subprocess.run(
        [
            sys.executable,
            str(BUILDER),
            "--config-file",
            str(config_path),
            "--output",
            str(output_path),
        ],
        text=True,
        capture_output=True,
    )
    if result.returncode:
        raise RuntimeError(
            f"Builder DSFR en échec pour {output_path}: {(result.stderr or result.stdout)[-1500:]}"
        )
    html = output_path.read_text(encoding="utf-8")
    if 'data-audit-builder="dsfr-components"' not in html:
        raise RuntimeError(f"Marqueur du builder absent : {output_path}")


def generate_audit_portal(config: dict[str, Any], root: Path) -> dict[str, Any]:
    """Génère le portail commun, les rapports complets et les vues par page."""
    phases = config.get("phases", {})
    rgaa_active = bool(phases.get("rgaa_checks", False))
    dsfr_active = bool(phases.get("dsfr_checks", False))
    rgaa = (
        _read_required(root / "rgaa/CONSTATS-INSTANCES.json")
        if rgaa_active
        else {"findings": [], "root_causes": []}
    )
    dsfr = (
        _read_required(root / "dsfr/ECARTS-COMPOSANTS.json")
        if dsfr_active
        else {"differences": [], "root_causes": []}
    )
    review = (
        _read_required(root / "rgaa/REVUE-MANUELLE-258.json")
        if rgaa_active
        else {"reviews": []}
    )
    decision_paths = (
        sorted((root / "rgaa").glob("P*-DECISIONS-258.json")) if rgaa_active else []
    )
    page_decisions = {
        str(document.get("page", {}).get("id", path.stem.split("-", 1)[0])): (
            path,
            document,
        )
        for path in decision_paths
        for document in [_read_required(path)]
    }
    dimension_paths = (
        sorted((root / "dsfr").glob("P*-COUVERTURE-DIMENSIONNELLE.json"))
        if dsfr_active
        else []
    )
    page_dimensions = {path.stem.split("-", 1)[0]: path for path in dimension_paths}
    documentary_paths = sorted(root.glob("P*-AUDIT-DECLARATION-ACCESSIBILITE.md"))
    component_review_paths = sorted(root.glob("P*-REVUE-COMPOSANTS-ET-ETATS.md"))
    pages = config.get("sample", [])
    out_config = root / "rapport-dsfr/config"
    outputs: list[Path] = []
    catalog_status = _dsfr_catalog_status(root, dsfr_active)
    out_config.mkdir(parents=True, exist_ok=True)
    for stale in out_config.glob("*.json"):
        stale.unlink()
    for directory in (root / "rgaa/pages-html", root / "dsfr/pages-html"):
        if directory.is_dir():
            for stale in directory.glob("*.html"):
                stale.unlink()
    for active, stale in (
        (rgaa_active, root / "rgaa/AUDIT-PAR-PAGE.html"),
        (dsfr_active, root / "dsfr/AUDIT-PAR-PAGE.html"),
    ):
        if not active and stale.is_file():
            stale.unlink()
    rgaa_findings_count = len(rgaa.get("findings", []))
    rgaa_confirmed = sum(
        item.get("qualification_status") == "NC_CONFIRMEE"
        for item in rgaa.get("findings", [])
    )
    rgaa_confirmed_criteria = len(
        {
            item.get("criterion")
            for item in rgaa.get("findings", [])
            if item.get("qualification_status") == "NC_CONFIRMEE"
        }
    )
    review_pending = (
        sum(
            sum(
                item.get("status") == "A_RETESTER"
                for item in document.get("decisions", [])
            )
            for _, document in page_decisions.values()
        )
        if page_decisions
        else sum(item.get("status") == "A_REVOIR" for item in review.get("reviews", []))
    )
    review_label = (
        "Décisions des 258 tests par page" if page_decisions else "Revue des 258 tests"
    )
    review_root_href = "rgaa/REVUE-MANUELLE-258.md"
    review_rgaa_href = "REVUE-MANUELLE-258.md"
    dsfr_findings_count = len(dsfr.get("differences", []))
    dsfr_confirmed = int(dsfr.get("confirmed_count", 0))
    dsfr_confirmed_rules = len(
        {
            item.get("rule_id")
            for item in dsfr.get("differences", [])
            if item.get("qualification_status") == "ECART_CONFIRME"
        }
    )
    dsfr_candidates = int(dsfr.get("candidate_count", 0))

    portal_output = root / "PORTAIL-AUDITS.html"
    portal_metrics = [{"label": "Pages", "value": len(pages)}]
    portal_links = []
    if rgaa_active:
        portal_metrics += [
            {"label": "Instances RGAA", "value": rgaa_findings_count},
            {
                "label": "Critères RGAA avec NC confirmée",
                "value": rgaa_confirmed_criteria,
            },
        ]
        portal_links += [
            {"label": "Ouvrir le rapport RGAA", "href": "rgaa/AUDIT-PAR-PAGE.html"}
        ]
    if dsfr_active:
        portal_metrics += [
            {"label": "Instances DSFR", "value": dsfr_findings_count},
            {"label": "Règles DSFR avec écart confirmé", "value": dsfr_confirmed_rules},
        ]
        portal_links += [
            {"label": "Ouvrir le rapport DSFR", "href": "dsfr/AUDIT-PAR-PAGE.html"}
        ]
    if rgaa_active:
        portal_metrics += [{"label": "Tests RGAA à revoir", "value": review_pending}]
        portal_links += [{"label": review_label, "href": review_root_href}]
    if (root / "COUVERTURE-MOTEURS.md").is_file():
        portal_links += [
            {
                "label": "Couverture et trous des moteurs",
                "href": "COUVERTURE-MOTEURS.md",
            }
        ]
    for pid, (decision_path, _) in page_decisions.items():
        decision_markdown = decision_path.with_suffix(".md")
        portal_links += [
            {
                "label": f"Décisions des 258 tests {pid}",
                "href": str(decision_markdown.relative_to(root)),
            }
        ]
    for pid, dimension_path in page_dimensions.items():
        if dimension_path.with_suffix(".md").is_file():
            portal_links += [
                {
                    "label": f"Couverture DSFR {pid} par classe et dimension",
                    "href": str(dimension_path.with_suffix(".md").relative_to(root)),
                }
            ]
    for documentary_path in documentary_paths:
        portal_links += [
            {
                "label": "Audit documentaire de la déclaration d’accessibilité",
                "href": str(documentary_path.relative_to(root)),
            }
        ]
    for review_path in component_review_paths:
        portal_links += [
            {
                "label": "Revue des composants et états",
                "href": str(review_path.relative_to(root)),
            }
        ]
    portal_type = (
        "RGAA + DSFR"
        if rgaa_active and dsfr_active
        else ("RGAA" if rgaa_active else "DSFR")
    )
    portal_title = f"Portail de l’audit {portal_type}"
    campaign_name = str(config["campaign"]["name"]).replace("—", "-").replace("–", "-")
    portal_sample = [
        {
            "id": str(page["id"]),
            "name": str(page["name"]),
            "url": str(page["url"]),
            "links": (
                [{"label": "Détail RGAA", "href": f"rgaa/pages-html/{page['id']}.html"}]
                if rgaa_active
                else []
            )
            + (
                [{"label": "Détail DSFR", "href": f"dsfr/pages-html/{page['id']}.html"}]
                if dsfr_active
                else []
            ),
        }
        for page in pages
    ]
    portal_config = _config(
        portal_title,
        f"Résultats de la campagne {campaign_name}",
        portal_type,
        f"Portail de consultation {portal_type}. Conclusions bornées aux preuves et qualifications documentées.",
        portal_metrics,
        portal_links,
        [],
        [],
        show_root_causes=False,
        show_empty_findings=False,
        sample_pages=portal_sample,
        catalog_status=catalog_status,
    )
    if rgaa_active:
        section = _config(
            "",
            "",
            "RGAA",
            "Causes RGAA séparées des observations DSFR.",
            [],
            [],
            _causes(rgaa.get("root_causes", [])),
            [],
            show_empty_findings=False,
            catalog_status=catalog_status,
        )["sections"][0]
        section["section_id"] = "causes-rgaa"
        portal_config["sections"].append(section)
    if dsfr_active:
        section = _config(
            "",
            "",
            "DSFR",
            "Causes DSFR séparées des constats réglementaires RGAA.",
            [],
            [],
            _causes(dsfr.get("root_causes", [])),
            [],
            show_empty_findings=False,
            catalog_status=catalog_status,
        )["sections"][0]
        section["section_id"] = "causes-dsfr"
        portal_config["sections"].append(section)
    _build(portal_config, out_config / "portail.json", portal_output)
    outputs.append(portal_output)

    rgaa_output = root / "rgaa/AUDIT-PAR-PAGE.html"
    rgaa_rows = _rgaa_findings(rgaa, root, rgaa_output, True)
    rgaa_config = _config(
        "Pré-audit RGAA détaillé",
        "Règles et instances RGAA avec preuves observées et attendues.",
        "RGAA",
        str(rgaa.get("claim", "Aucun taux RGAA officiel.")),
        [
            {"label": "Pages", "value": len(pages)},
            {"label": "Instances signalées", "value": rgaa_findings_count},
            {"label": "Instances NC confirmées", "value": rgaa_confirmed},
            {"label": "Critères avec NC confirmée", "value": rgaa_confirmed_criteria},
            {"label": "Tests à revoir", "value": review_pending},
        ],
        [
            {"label": "Portail commun", "href": "../PORTAIL-AUDITS.html"},
            {"label": review_label, "href": review_rgaa_href},
        ],
        _causes(rgaa.get("root_causes", [])),
        rgaa_rows,
        pages=[
            {
                "id": str(page["id"]),
                "name": str(page["name"]),
                "url": str(page["url"]),
                "href": f"pages-html/{page['id']}.html",
            }
            for page in pages
        ],
        home_href="../PORTAIL-AUDITS.html",
        catalog_status=catalog_status,
    )
    if rgaa_active:
        _build(rgaa_config, out_config / "rgaa.json", rgaa_output)
        outputs.append(rgaa_output)

    dsfr_output = root / "dsfr/AUDIT-PAR-PAGE.html"
    dsfr_rows = _dsfr_findings(dsfr, root, dsfr_output, True)
    dsfr_config = _config(
        "Audit DSFR détaillé",
        "Règles et instances DSFR avec séparation intégration et migration.",
        "DSFR",
        str(dsfr.get("claim", "Aucune conformité DSFR globale revendiquée.")),
        [
            {"label": "Pages", "value": len(pages)},
            {"label": "Instances signalées", "value": dsfr_findings_count},
            {"label": "Instances d’écart confirmées", "value": dsfr_confirmed},
            {"label": "Règles avec écart confirmé", "value": dsfr_confirmed_rules},
            {"label": "À qualifier", "value": dsfr_candidates},
        ],
        [
            {"label": "Portail commun", "href": "../PORTAIL-AUDITS.html"},
            {"label": "Matrice DSFR", "href": "MATRICE-RESPECT-DSFR.md"},
        ],
        _causes(dsfr.get("root_causes", [])),
        dsfr_rows,
        pages=[
            {
                "id": str(page["id"]),
                "name": str(page["name"]),
                "url": str(page["url"]),
                "href": f"pages-html/{page['id']}.html",
            }
            for page in pages
        ],
        home_href="../PORTAIL-AUDITS.html",
        catalog_status=catalog_status,
    )
    if dsfr_active:
        _build(dsfr_config, out_config / "dsfr.json", dsfr_output)
        outputs.append(dsfr_output)

    for page in pages:
        pid = str(page["id"])
        name = str(page["name"])
        rgaa_page_output = root / "rgaa/pages-html" / f"{pid}.html"
        rgaa_page_rows = _rgaa_findings(
            {
                "findings": [
                    item for item in rgaa.get("findings", []) if item.get("page") == pid
                ]
            },
            root,
            rgaa_page_output,
            False,
        )
        rgaa_page_causes = [
            item
            for item in _causes(rgaa.get("root_causes", []))
            if pid in item["pages"]
        ]
        rgaa_page_confirmed = [
            item for item in rgaa_page_rows if item["status"] == "NC_CONFIRMEE"
        ]
        rgaa_page_metrics = [
            {"label": "Instances signalées", "value": len(rgaa_page_rows)},
            {"label": "Instances NC confirmées", "value": len(rgaa_page_confirmed)},
            {
                "label": "Critères avec NC confirmée",
                "value": len({item["criterion"] for item in rgaa_page_confirmed}),
            },
            {
                "label": "Instances de signal à retester",
                "value": sum(item["status"] == "A_RETESTER" for item in rgaa_page_rows),
            },
        ]
        rgaa_page_links = [
            {"label": "Rapport RGAA complet", "href": "../AUDIT-PAR-PAGE.html"},
            {"label": "Portail commun", "href": "../../PORTAIL-AUDITS.html"},
        ]
        if pid in page_decisions:
            decision_path, decision_document = page_decisions[pid]
            rgaa_page_metrics.append(
                {
                    "label": "Tests RGAA à retester",
                    "value": sum(
                        item.get("status") == "A_RETESTER"
                        for item in decision_document.get("decisions", [])
                    ),
                }
            )
            rgaa_page_links.append(
                {
                    "label": f"Décisions des 258 tests {pid}",
                    "href": f"../{decision_path.with_suffix('.md').name}",
                }
            )
        rgaa_page_config = _config(
            f"{pid} - {name} - audit RGAA",
            f"Constats RGAA détaillés de {name}.",
            "RGAA",
            str(rgaa.get("claim", "Aucun taux RGAA officiel.")),
            rgaa_page_metrics,
            rgaa_page_links,
            rgaa_page_causes,
            rgaa_page_rows,
            pages=[{"id": pid, "name": name, "url": str(page["url"])}],
            home_href="../../PORTAIL-AUDITS.html",
            sample_title="Page auditée",
            catalog_status=catalog_status,
        )
        if rgaa_active:
            _build(rgaa_page_config, out_config / f"rgaa-{pid}.json", rgaa_page_output)
            outputs.append(rgaa_page_output)

        dsfr_page_output = root / "dsfr/pages-html" / f"{pid}.html"
        dsfr_page_rows = _dsfr_findings(
            {
                "differences": [
                    item
                    for item in dsfr.get("differences", [])
                    if item.get("page") == pid
                ]
            },
            root,
            dsfr_page_output,
            False,
        )
        dsfr_page_causes = [
            item
            for item in _causes(dsfr.get("root_causes", []))
            if pid in item["pages"]
        ]
        dsfr_page_confirmed = [
            item for item in dsfr_page_rows if item["status"] == "ECART_CONFIRME"
        ]
        dsfr_page_metrics = [
            {"label": "Instances signalées", "value": len(dsfr_page_rows)},
            {
                "label": "Instances d’écart confirmées",
                "value": len(dsfr_page_confirmed),
            },
            {
                "label": "Règles avec écart confirmé",
                "value": len({item["rule"] for item in dsfr_page_confirmed}),
            },
            {
                "label": "Instances à qualifier",
                "value": sum(
                    item["status"] == "A_CONFIRMER" for item in dsfr_page_rows
                ),
            },
        ]
        dsfr_page_links = [
            {"label": "Rapport DSFR complet", "href": "../AUDIT-PAR-PAGE.html"},
            {"label": "Portail commun", "href": "../../PORTAIL-AUDITS.html"},
        ]
        if pid in page_dimensions:
            dimension_path = page_dimensions[pid]
            dimension_summary = _read_required(dimension_path).get("summary") or {}
            if "detected_families" in dimension_summary:
                dsfr_page_metrics.append(
                    {
                        "label": "Familles DSFR détectées",
                        "value": dimension_summary["detected_families"],
                    }
                )
            if dimension_path.with_suffix(".md").is_file():
                dsfr_page_links.append(
                    {
                        "label": f"Couverture DSFR {pid}",
                        "href": f"../{dimension_path.with_suffix('.md').name}",
                    }
                )
        dsfr_page_config = _config(
            f"{pid} - {name} - audit DSFR",
            f"Constats DSFR détaillés de {name}.",
            "DSFR",
            str(dsfr.get("claim", "Aucune conformité DSFR globale revendiquée.")),
            dsfr_page_metrics,
            dsfr_page_links,
            dsfr_page_causes,
            dsfr_page_rows,
            pages=[{"id": pid, "name": name, "url": str(page["url"])}],
            home_href="../../PORTAIL-AUDITS.html",
            sample_title="Page auditée",
            catalog_status=catalog_status,
        )
        if dsfr_active:
            _build(dsfr_page_config, out_config / f"dsfr-{pid}.json", dsfr_page_output)
            outputs.append(dsfr_page_output)

    # Le builder est l'unique écrivain HTML public. Les anciens rapports HTML
    # racine ne sont ni modifiés ni réhabilités.
    consolidated = root / "RAPPORT-CONSOLIDE.md"
    if consolidated.is_file():
        value = consolidated.read_text(encoding="utf-8")
        link = f"\n## Portail des audits\n\n- [Ouvrir le portail {portal_type}](PORTAIL-AUDITS.html)\n"
        value = re.sub(
            r"\n## Portail (?:DSFR )?des audits\n\n- \[Ouvrir le portail .*?\]\(PORTAIL-AUDITS\.html\)\n",
            "",
            value,
        )
        consolidated.write_text(value + link, encoding="utf-8")

    input_paths = [root / "campaign.yaml"]
    if rgaa_active:
        input_paths += [
            root / "rgaa/CONSTATS-INSTANCES.json",
            root / "rgaa/REVUE-MANUELLE-258.json",
        ]
        input_paths.extend(path for path, _ in page_decisions.values())
    if dsfr_active:
        input_paths += [root / "dsfr/ECARTS-COMPOSANTS.json"]
    if (root / "COUVERTURE-MOTEURS.json").is_file():
        input_paths.append(root / "COUVERTURE-MOTEURS.json")
    input_paths.extend(page_dimensions.values())
    for documentary_path in documentary_paths:
        input_paths.append(documentary_path)
        documentary_json = documentary_path.with_suffix(".json")
        if documentary_json.is_file():
            input_paths.append(documentary_json)
    input_paths.extend(component_review_paths)
    config_paths = sorted(out_config.glob("*.json"))
    build = {
        "schema_version": 2,
        "builder": str(BUILDER.relative_to(SKILLS_ROOT)),
        "builder_sha256": _digest(BUILDER),
        "builder_schema": str(BUILDER_SCHEMA.relative_to(SKILLS_ROOT)),
        "builder_schema_sha256": _digest(BUILDER_SCHEMA),
        "brand_mode": "neutral",
        "dsfr_assets": "CDN @gouvfr/dsfr 1.15.3 ; contenu lisible sans CSS/JS",
        "dsfr_rule_catalog": catalog_status["current"],
        "dsfr_catalog_status": catalog_status,
        "inputs": [
            {"path": str(path.relative_to(root)), "sha256": _digest(path)}
            for path in input_paths
        ],
        "outputs": [
            {"path": str(path.relative_to(root)), "sha256": _digest(path)}
            for path in outputs
        ],
        "configs": [
            {"path": str(path.relative_to(root)), "sha256": _digest(path)}
            for path in config_paths
        ],
    }
    _write(root / "rapport-dsfr/BUILD.json", build)
    return build


if __name__ == "__main__":
    if len(sys.argv) != 3:
        raise SystemExit("Usage: audit_report_builder.py CAMPAIGN.JSON CAMPAIGN_ROOT")
    generate_audit_portal(
        json.loads(Path(sys.argv[1]).read_text(encoding="utf-8")),
        Path(sys.argv[2]).resolve(),
    )
