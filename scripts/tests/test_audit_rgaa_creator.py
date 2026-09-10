#!/usr/bin/env python3
import hashlib
import asyncio
import http.server
import json
import os
import re
import threading
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import yaml

ROOT = Path(__file__).resolve().parents[2]
CLI = ROOT / ".claude/skills/audit-rgaa-creator/scripts/audit_campaign.py"
sys.path.insert(0, str(CLI.parent))
from audit_campaign import preflight, probe_network_url  # noqa: E402
from navigation import goto_checked  # noqa: E402


class _FakeResponse:
    def __init__(self, status=200, headers=None):
        self.status = status
        self.headers = headers or {}


class _FakePage:
    def __init__(self, response=None, error=None):
        self.response = response
        self.error = error

    async def goto(self, url, wait_until, timeout):
        if self.error:
            raise RuntimeError(self.error)
        return self.response


class _HeadHandler(http.server.BaseHTTPRequestHandler):
    def do_HEAD(self):  # noqa: N802
        if self.path == "/proxy":
            self.send_response(403)
            self.send_header("x-deny-reason", "host_not_allowed")
        elif self.path == "/site":
            self.send_response(403)
            self.send_header("server", "DGDDI-WS")
        else:
            self.send_response(200)
        self.end_headers()

    def log_message(self, format, *args):
        return


class CreatorTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix="audit-rgaa-creator-")
        self.project = Path(self.tmp.name) / "campaign"

    def tearDown(self):
        self.tmp.cleanup()

    def run_cli(self, *args, ok=True):
        result = subprocess.run(
            [sys.executable, str(CLI), *map(str, args)],
            text=True,
            capture_output=True,
            env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"},
        )
        if ok and result.returncode != 0:
            self.fail(
                f"Commande en échec {args}:\nSTDOUT={result.stdout}\nSTDERR={result.stderr}"
            )
        return result

    def init(self, *extra):
        self.run_cli(
            "init",
            "https://example.test/",
            "--output",
            self.project,
            "--page",
            "https://example.test/::Accueil::homepage",
            *extra,
        )
        return self.project / "campaign.yaml"

    def test_init_accepts_explicit_page_identifier(self):
        self.run_cli(
            "init",
            "https://example.test/",
            "--output",
            self.project,
            "--page",
            "P09::https://example.test/news::Actualité::news-article",
        )
        campaign = yaml.safe_load(
            (self.project / "campaign.yaml").read_text(encoding="utf-8")
        )
        self.assertEqual(
            {
                "id": "P09",
                "name": "Actualité",
                "url": "https://example.test/news",
                "type": "news-article",
            },
            campaign["sample"][0],
        )

    def test_generic_report_capture_discovery_uses_build_outputs(self):
        campaign = self.init()
        self.run_cli("report", campaign)
        helper = (
            ROOT / ".claude/skills/audit-report-dsfr/scripts/capture_audit_reports.py"
        )
        result = subprocess.run(
            [sys.executable, str(helper), str(self.project), "--check"],
            text=True,
            capture_output=True,
        )
        self.assertEqual(0, result.returncode, result.stderr)
        self.assertEqual(
            ["portal", "rgaa-P01", "dsfr-P01"], json.loads(result.stdout)["reports"]
        )

    def test_init_report_validate_and_matrix_106(self):
        campaign = self.init()
        self.run_cli("report", campaign)
        result = self.run_cli("validate", campaign)
        self.assertIn("[OK] Validation", result.stdout)
        matrix = (self.project / "MATRICE-RGAA-106.md").read_text(encoding="utf-8")
        self.assertEqual(106, len(re.findall(r"^\| \d+\.\d+ \|", matrix, re.MULTILINE)))
        self.assertFalse((self.project / "AUDIT-PAR-PAGE.html").exists())
        self.assertTrue((self.project / "dsfr/AUDIT-PAR-PAGE.html").is_file())
        self.assertTrue((self.project / "dsfr/INVENTAIRE-COMPOSANTS.json").is_file())
        self.assertTrue((self.project / "PORTAIL-AUDITS.html").is_file())
        self.assertTrue((self.project / "rgaa/pages-html/P01.html").is_file())
        self.assertTrue((self.project / "dsfr/pages-html/P01.html").is_file())
        build = json.loads(
            (self.project / "rapport-dsfr/BUILD.json").read_text(encoding="utf-8")
        )
        self.assertEqual(5, len(build["outputs"]))
        self.assertTrue(
            all(
                json.loads((self.project / rel).read_text(encoding="utf-8"))[
                    "brand_mode"
                ]
                == "neutral"
                for item in build["configs"]
                for rel in [item["path"]]
            )
        )
        portal = (self.project / "PORTAIL-AUDITS.html").read_text(encoding="utf-8")
        self.assertIn('data-audit-builder="dsfr-components"', portal)
        self.assertIn("rgaa/AUDIT-PAR-PAGE.html", portal)
        self.assertIn("dsfr/AUDIT-PAR-PAGE.html", portal)
        self.assertIn('id="causes-rgaa"', portal)
        self.assertIn('id="causes-dsfr"', portal)
        self.assertIn('fr-table__container" tabindex="0"', portal)
        self.assertIn("Pages de l’échantillon", portal)
        self.assertLess(
            portal.index("Pages de l’échantillon"), portal.index("Périmètre du rapport")
        )
        self.assertIn("fr-grid-row fr-grid-row--gutters", portal)
        self.assertIn("fr-ml-md-2w", portal)
        self.assertIn("fr-summary", portal)
        self.assertIn("fr-highlight", portal)
        self.assertIn("Haut de page", portal)
        self.assertNotIn("fr-tile fr-tile--horizontal", portal)
        self.assertNotIn("max-width:100rem", portal)
        self.assertNotIn("Se connecter", portal)
        rgaa_detail = (self.project / "rgaa/pages-html/P01.html").read_text(
            encoding="utf-8"
        )
        dsfr_detail = (self.project / "dsfr/pages-html/P01.html").read_text(
            encoding="utf-8"
        )
        self.assertIn("Page auditée", rgaa_detail)
        self.assertIn("https://example.test/", rgaa_detail)
        self.assertIn("Page auditée", dsfr_detail)
        self.assertIn("https://example.test/", dsfr_detail)
        config = yaml.safe_load(campaign.read_text(encoding="utf-8"))
        self.assertTrue(config["phases"]["dsfr_checks"])
        self.assertTrue(config["phases"]["rgaa_checks"])
        self.assertEqual(
            "aucune conformité DSFR globale revendiquée", config["claims"]["dsfr_claim"]
        )
        self.assertTrue((self.project / "rgaa-findings.json").is_file())
        self.assertTrue((self.project / "dsfr-findings.json").is_file())
        self.assertFalse(self.project.is_relative_to(ROOT))

    def test_rgaa_v2_report_exposes_instance_code_and_filters(self):
        campaign = self.init()
        proof = self.project / "rgaa/preuves/P01/attempt-001"
        proof.mkdir(parents=True)
        (proof / "evidence.json").write_text("{}", encoding="utf-8")
        (proof / "desktop.png").write_bytes(b"png")
        signal = {
            "id": "P01-RGAA-8-2-ID-UNIQUE-001-001",
            "rule_id": "RGAA-8-2-ID-UNIQUE-001",
            "criterion": "8.2",
            "test": "8.2.1",
            "component": "html",
            "instance": 1,
            "signal_status": "FAIL_CANDIDATE",
            "qualification_status": "NON_TESTE",
            "severity": "Majeur",
            "title": "ID dupliqué",
            "selector": "#duplicate",
            "observed": "Deux occurrences",
            "observed_code": "<button id='duplicate'><script>alert(1)</script></button>",
            "observed_origin": "RENDERED_DOM",
            "expected": "ID unique",
            "expected_code": "<button id='unique'>…</button>",
            "failed_assertions": ["Identifiant non unique"],
            "impact": "Relations ambiguës",
            "source": "https://accessibilite.numerique.gouv.fr/methode/criteres-et-tests/#8.2.1",
            "recommendation": "Rendre unique",
            "verification": "Recompter",
            "evidence": [
                "rgaa/preuves/P01/attempt-001/evidence.json",
                "rgaa/preuves/P01/attempt-001/desktop.png",
            ],
        }
        page_dir = self.project / "rgaa/pages"
        page_dir.mkdir(parents=True)
        page = {
            "schema_version": 1,
            "page": {
                "id": "P01",
                "name": "Accueil",
                "url": "https://example.test/",
                "type": "homepage",
            },
            "audited_at": "2026-09-02T00:00:00Z",
            "rules_executed": ["RGAA-8-2-ID-UNIQUE-001"],
            "signals": [signal],
            "passes": [],
            "evidence": {
                "attempt": 1,
                "raw": "rgaa/preuves/P01/attempt-001/evidence.json",
                "screenshot": "rgaa/preuves/P01/attempt-001/desktop.png",
            },
            "limits": ["Préqualification"],
        }
        (page_dir / "P01.json").write_text(
            json.dumps(page, ensure_ascii=False), encoding="utf-8"
        )
        self.run_cli("report", campaign)
        self.run_cli("validate", campaign)
        document = (self.project / "rgaa/AUDIT-PAR-PAGE.html").read_text(
            encoding="utf-8"
        )
        self.assertIn('data-audit-builder="dsfr-components"', document)
        self.assertIn('data-audit-status="NON_TESTE"', document)
        self.assertIn("Preuve observée", document)
        self.assertNotIn("<script>alert(1)", document)
        self.assertIn("&lt;script&gt;alert", document)

    def test_rgaa_review_queue_contains_258_unique_tests(self):
        campaign = self.init()
        catalog = json.loads(
            (
                ROOT / ".claude/skills/audit-rgaa-complet/rules/rgaa-rules.json"
            ).read_text(encoding="utf-8")
        )
        official = list(dict.fromkeys(rule["test"] for rule in catalog["rules"]))
        filler = [f"99.99.{index}" for index in range(1, 259 - len(official))]
        tests = official + filler
        proof_tests = [
            {
                "test_id": test,
                "criterion_id": ".".join(test.split(".")[:2]),
                "reference_contract": {
                    "target": "fixture",
                    "expected_evidence": "preuve",
                    "human_validation": "requise",
                    "limit": "préqualification",
                },
                "human_review_points": ["revoir"],
                "source_rgaa": {"url": f"https://example.test/#{test}"},
            }
            for test in tests
        ]
        (self.project / "plan-preuves-rgaa-106.json").write_text(
            json.dumps({"proof_contract": {"tests": proof_tests}}), encoding="utf-8"
        )
        self.run_cli("report", campaign)
        self.run_cli("validate", campaign)
        review = json.loads(
            (self.project / "rgaa/REVUE-MANUELLE-258.json").read_text(encoding="utf-8")
        )
        self.assertEqual(258, review["tests_count"])
        self.assertEqual(258, len({item["test"] for item in review["reviews"]}))

    def test_rgaa_confirmed_decision_requires_reviewer(self):
        campaign = self.init()
        self.run_cli("report", campaign)
        finding = {
            "id": "Q1",
            "pages": ["P01"],
            "rule_id": "RGAA-8-2-ID-UNIQUE-001",
            "criterion": "8.2",
            "test": "8.2.1",
            "qualification_status": "NC_CONFIRMEE",
            "comment": "Confirmé",
            "evidence": ["rgaa-findings.json"],
        }
        (self.project / "rgaa-findings.json").write_text(
            json.dumps({"schema_version": 1, "findings": [finding]}), encoding="utf-8"
        )
        self.run_cli("report", campaign)
        result = self.run_cli("validate", campaign, ok=False)
        self.assertNotEqual(0, result.returncode)
        self.assertIn("sans revue", result.stderr)

    def test_dsfr_report_uses_same_sample_and_escapes_evidence(self):
        campaign = self.init()
        page_dir = self.project / "dsfr/pages"
        page_dir.mkdir(parents=True, exist_ok=True)
        evidence = {
            "schema_version": 1,
            "page": {
                "id": "P01",
                "name": "Accueil",
                "url": "https://example.test/",
                "type": "homepage",
            },
            "reference_version": "1.15.2",
            "detected_versions": ["1.15.2"],
            "status": "ÉCARTS OBSERVÉS",
            "inventory": [
                {
                    "name": "header",
                    "selector": ".fr-header",
                    "count": 1,
                    "status": "ÉCART",
                    "source": "reference.md",
                }
            ],
            "differences": [
                {
                    "id": "P01-D1",
                    "kind": "component",
                    "component": "header",
                    "status": "ÉCART",
                    "severity": "Majeur",
                    "title": "<script>alert(1)</script>",
                    "expected": "role=banner",
                    "observed": "absent",
                    "source": "reference.md",
                }
            ],
            "sources": ["reference.md"],
            "not_verified": [],
        }
        (page_dir / "P01.json").write_text(
            json.dumps(evidence, ensure_ascii=False), encoding="utf-8"
        )
        self.run_cli("report", campaign)
        self.run_cli("validate", campaign)
        document = (self.project / "dsfr/AUDIT-PAR-PAGE.html").read_text(
            encoding="utf-8"
        )
        self.assertEqual(1, len(re.findall(r"<section id=['\"]P01", document)))
        self.assertNotIn("<script>alert", document)
        self.assertIn("&lt;script&gt;", document)

    def test_dsfr_v2_report_exposes_instance_code_filters_and_version_scope(self):
        campaign = self.init()
        proof = self.project / "dsfr/preuves/P01/attempt-001"
        proof.mkdir(parents=True)
        (proof / "evidence.json").write_text("{}", encoding="utf-8")
        (proof / "desktop.png").write_bytes(b"png")
        (proof / "mobile.png").write_bytes(b"png")
        page_dir = self.project / "dsfr/pages"
        page_dir.mkdir(parents=True)
        difference = {
            "id": "P01-DSFR-CARD-STRUCTURE-001-001",
            "rule_id": "DSFR-CARD-STRUCTURE-001",
            "kind": "migration",
            "component": "card",
            "instance": 1,
            "signal_status": "FAIL_CANDIDATE",
            "status": "ECART_OBSERVE",
            "qualification_status": "A_CONFIRMER",
            "severity": "Majeur",
            "title": "Carte incomplète",
            "expected": "Structure de carte",
            "observed": "Corps absent",
            "selector": ".fr-card",
            "observed_html": "<div class='fr-card'><script>alert(1)</script></div>",
            "observed_html_origin": "RENDERED_DOM",
            "expected_html": "<div class='fr-card'><div class='fr-card__body'></div></div>",
            "failed_conditions": ["fr-card__body absent"],
            "source": "dsfr-components/references/components/content-media/cards.md",
            "reference_target_version": "1.15.2",
            "observed_versions": ["1.13.2"],
            "assessed_against": "MIGRATION_VERS_CIBLE",
            "evidence": [
                "dsfr/preuves/P01/attempt-001/evidence.json",
                "dsfr/preuves/P01/attempt-001/desktop.png",
                "dsfr/preuves/P01/attempt-001/mobile.png",
            ],
            "recommendation": "Restaurer la structure.",
            "verification": "Rejouer la règle.",
        }
        page = {
            "schema_version": 2,
            "page": {
                "id": "P01",
                "name": "Accueil",
                "url": "https://example.test/",
                "type": "homepage",
            },
            "version": {
                "observed": ["1.13.2"],
                "target": "1.15.2",
                "comparison_mode": "MIGRATION_VERS_CIBLE",
                "exact_observed_reference_available": False,
            },
            "reference_version": "1.15.2",
            "detected_versions": ["1.13.2"],
            "status": "SIGNAUX D’ÉCART OBSERVÉS",
            "claim": "Aucune conformité DSFR globale n’est revendiquée.",
            "inventory": [
                {
                    "name": "card",
                    "selector": ".fr-card",
                    "count": 1,
                    "visible": 1,
                    "status": "ECART_OBSERVE",
                    "rules_executed": ["DSFR-CARD-STRUCTURE-001"],
                    "source": "dsfr-components/references/components/content-media/cards.md",
                    "samples": [],
                }
            ],
            "differences": [difference],
            "sources": [],
            "not_verified": [],
            "evidence": {
                "attempt": 1,
                "raw": "dsfr/preuves/P01/attempt-001/evidence.json",
                "desktop_screenshot": "dsfr/preuves/P01/attempt-001/desktop.png",
                "mobile_screenshot": "dsfr/preuves/P01/attempt-001/mobile.png",
            },
        }
        (page_dir / "P01.json").write_text(
            json.dumps(page, ensure_ascii=False), encoding="utf-8"
        )
        self.run_cli("report", campaign)
        self.run_cli("validate", campaign)
        document = (self.project / "dsfr/AUDIT-PAR-PAGE.html").read_text(
            encoding="utf-8"
        )
        self.assertIn('data-audit-builder="dsfr-components"', document)
        self.assertIn('data-audit-status="A_CONFIRMER"', document)
        self.assertIn('aria-pressed="true"', document)
        self.assertIn("data-audit-count", document)
        self.assertIn("Preuve observée", document)
        self.assertIn("Évaluation MIGRATION_VERS_CIBLE", document)
        finding_markup = document[document.index('audit-finding"') :]
        self.assertLess(
            finding_markup.index("fr-card__title"),
            finding_markup.index("fr-card__desc"),
        )
        self.assertIn("Nature migration", document)
        self.assertNotIn("Critère migration", document)
        self.assertIn(
            "Le DOM rendu n’est pas nécessairement le fichier source du dépôt.",
            document,
        )
        self.assertNotIn("<script>alert(1)", document)
        self.assertIn("&lt;script&gt;alert", document)
        consolidated = json.loads(
            (self.project / "dsfr/ECARTS-COMPOSANTS.json").read_text(encoding="utf-8")
        )
        self.assertEqual(2, consolidated["schema_version"])
        self.assertEqual("RENDERED_DOM", consolidated["observed_html_origin"])

    def test_dsfr_catalog_fingerprint_is_recorded_and_stale_report_is_signaled(self):
        campaign = self.init()
        catalog_path = ROOT / ".claude/skills/audit-dsfr-complet/rules/dsfr-rules.json"
        catalog_bytes = catalog_path.read_bytes()
        fingerprint = hashlib.sha256(catalog_bytes).hexdigest()
        page_dir = self.project / "dsfr/pages"
        page_dir.mkdir(parents=True)
        page = {
            "schema_version": 2,
            "page": {
                "id": "P01",
                "name": "Accueil",
                "url": "https://example.test/",
                "type": "homepage",
            },
            "version": {"target": "1.15.2"},
            "reference_version": "1.15.2",
            "detected_versions": ["1.15.2"],
            "inventory": [],
            "differences": [],
            "rule_catalog": {
                "path": "audit-dsfr-complet/rules/dsfr-rules.json",
                "sha256": fingerprint,
                "schema_version": 1,
                "target_version": "1.15.2",
                "rules_count": 53,
            },
        }
        page_path = page_dir / "P01.json"
        page_path.write_text(json.dumps(page, ensure_ascii=False), encoding="utf-8")
        self.run_cli("report", campaign)
        inventory = json.loads(
            (self.project / "dsfr/INVENTAIRE-COMPOSANTS.json").read_text(
                encoding="utf-8"
            )
        )
        build = json.loads(
            (self.project / "rapport-dsfr/BUILD.json").read_text(encoding="utf-8")
        )
        self.assertEqual(fingerprint, page["rule_catalog"]["sha256"])
        self.assertEqual(fingerprint, inventory["rule_catalog"]["sha256"])
        self.assertEqual(fingerprint, build["dsfr_rule_catalog"]["sha256"])
        page["rule_catalog"]["sha256"] = "ancienne-empreinte"
        page_path.write_text(json.dumps(page, ensure_ascii=False), encoding="utf-8")
        self.run_cli("report", campaign)
        status = json.loads(
            (self.project / "dsfr/ECARTS-COMPOSANTS.json").read_text(encoding="utf-8")
        )["catalog_status"]
        self.assertEqual("CATALOGUE_OBSOLETE", status["status"])
        document = (self.project / "dsfr/AUDIT-PAR-PAGE.html").read_text(
            encoding="utf-8"
        )
        self.assertIn("Catalogue de règles à vérifier", document)

    def test_dsfr_rule_catalog_has_unique_instance_rules(self):
        catalog = json.loads(
            (
                ROOT / ".claude/skills/audit-dsfr-complet/rules/dsfr-rules.json"
            ).read_text(encoding="utf-8")
        )
        ids = [rule["rule_id"] for rule in catalog["rules"]]
        self.assertGreaterEqual(len(ids), 52)
        self.assertIn("DSFR-SKIPLINK-STRUCTURE-001", ids)
        self.assertIn("DSFR-CHECKBOX-STRUCTURE-001", ids)
        self.assertIn("DSFR-TRANSLATE-STRUCTURE-001", ids)
        self.assertIn("DSFR-SELECT-STRUCTURE-001", ids)
        self.assertIn("DSFR-UPLOAD-STRUCTURE-001", ids)
        self.assertIn("DSFR-MESSAGES-GROUP-STRUCTURE-001", ids)
        self.assertIn("DSFR-DISPLAY-STRUCTURE-001", ids)
        self.assertIn("DSFR-TAG-SEMANTICS-001", ids)
        self.assertIn("DSFR-BREADCRUMB-STRUCTURE-001", ids)
        self.assertIn("DSFR-SHARE-STRUCTURE-001", ids)
        self.assertEqual(len(ids), len(set(ids)))
        self.assertTrue(
            all(
                rule["expected_html"] and rule["source"] and rule["conditions"]
                for rule in catalog["rules"]
            )
        )
        self.assertTrue(
            all(
                (ROOT / ".claude/skills" / rule["source"]).is_file()
                for rule in catalog["rules"]
            )
        )
        nav_rule = next(
            rule
            for rule in catalog["rules"]
            if rule["rule_id"] == "DSFR-NAV-STRUCTURE-001"
        )
        self.assertEqual(".fr-nav:not(.fr-translate)", nav_rule["selector"])
        fieldset_rule = next(
            rule
            for rule in catalog["rules"]
            if rule["rule_id"] == "DSFR-FIELDSET-STRUCTURE-001"
        )
        self.assertIn(
            ':not([type="submit"])', fieldset_rule["conditions"][2]["selector"]
        )
        share_rule = next(
            rule
            for rule in catalog["rules"]
            if rule["rule_id"] == "DSFR-SHARE-STRUCTURE-001"
        )
        self.assertIn("fr-btns-group", share_rule["expected_html"])
        self.assertNotIn("fr-share__group", share_rule["expected_html"])
        grid_rule = next(
            rule
            for rule in catalog["rules"]
            if rule["rule_id"] == "DSFR-GRID-COLUMNS-001"
        )
        self.assertIn(":not(.fr-grid-row--right)", grid_rule["selector"])
        display_trigger = next(
            rule
            for rule in catalog["rules"]
            if rule["rule_id"] == "DSFR-DISPLAY-TRIGGER-002"
        )
        self.assertEqual("VERSION_INDEPENDENT", display_trigger["version_scope"])
        consent_actions = next(
            rule
            for rule in catalog["rules"]
            if rule["rule_id"] == "DSFR-CONSENT-ACTIONS-STRUCTURE-002"
        )
        self.assertNotIn("fr-modal__footer", consent_actions["expected_html"])
        consent_required = next(
            rule
            for rule in catalog["rules"]
            if rule["rule_id"] == "DSFR-CONSENT-REQUIRED-DISABLED-003"
        )
        self.assertIn(
            ":checked:not([disabled])", consent_required["conditions"][0]["selector"]
        )
        dsfr_collector = (
            ROOT / ".claude/skills/audit-rgaa-creator/scripts/dsfr_checks.py"
        ).read_text(encoding="utf-8")
        self.assertIn("root.tagName==='INPUT'", dsfr_collector)

    def test_rgaa_rule_catalog_has_unique_test_mappings_and_limits(self):
        catalog = json.loads(
            (
                ROOT / ".claude/skills/audit-rgaa-complet/rules/rgaa-rules.json"
            ).read_text(encoding="utf-8")
        )
        ids = [rule["rule_id"] for rule in catalog["rules"]]
        self.assertEqual(27, len(ids))
        self.assertEqual(len(ids), len(set(ids)))
        self.assertTrue(
            all(
                rule["criterion"]
                and rule["test"]
                and rule["expected_code"]
                and rule["limitations"]
                for rule in catalog["rules"]
            )
        )
        self.assertIn("RGAA-10-1-PRESENTATIONAL-ATTRIBUTE-002", ids)
        self.assertIn("RGAA-10-1-PRESENTATIONAL-TAG-001", ids)
        self.assertIn("RGAA-11-6-FIELDSET-LEGEND-002", ids)
        self.assertIn("RGAA-1-2-DECORATIVE-SVG-002", ids)
        self.assertIn("RGAA-8-9-EMPTY-PRESENTATION-001", ids)
        self.assertIn("RGAA-8-2-ANCHOR-TYPE-002", ids)
        self.assertIn("RGAA-11-5-RADIO-GROUP-001", ids)
        self.assertIn("RGAA-8-1-DOCTYPE-VALID-002", ids)
        self.assertIn("RGAA-8-1-DOCTYPE-POSITION-003", ids)
        self.assertIn("RGAA-11-1-LABEL-FOR-002", ids)
        presentation_rule = next(
            rule
            for rule in catalog["rules"]
            if rule["rule_id"] == "RGAA-10-1-PRESENTATIONAL-ATTRIBUTE-002"
        )
        self.assertIn("source enfant direct de picture", presentation_rule["expected"])
        collector = (
            ROOT / ".claude/skills/audit-rgaa-creator/scripts/rgaa_checks.py"
        ).read_text(encoding="utf-8")
        self.assertIn(
            "tagName.toLowerCase()==='source'&&e.parentElement?.tagName.toLowerCase()==='picture'",
            collector,
        )

    def test_old_campaign_without_dsfr_phase_remains_valid(self):
        campaign = self.init()
        self.run_cli("report", campaign)
        self.assertTrue((self.project / "dsfr/AUDIT-PAR-PAGE.html").exists())
        config = yaml.safe_load(campaign.read_text(encoding="utf-8"))
        del config["phases"]["dsfr_checks"]
        campaign.write_text(
            yaml.safe_dump(config, allow_unicode=True, sort_keys=False),
            encoding="utf-8",
        )
        self.run_cli("report", campaign)
        self.run_cli("validate", campaign)
        self.assertFalse((self.project / "dsfr/AUDIT-PAR-PAGE.html").exists())
        portal = (self.project / "PORTAIL-AUDITS.html").read_text(encoding="utf-8")
        self.assertIn("Portail de l’audit RGAA", portal)
        self.assertNotIn("RGAA + DSFR", portal)

    def test_old_campaign_without_rgaa_phase_remains_valid(self):
        campaign = self.init()
        config = yaml.safe_load(campaign.read_text(encoding="utf-8"))
        del config["phases"]["rgaa_checks"]
        campaign.write_text(
            yaml.safe_dump(config, allow_unicode=True, sort_keys=False),
            encoding="utf-8",
        )
        self.run_cli("report", campaign)
        self.run_cli("validate", campaign)
        self.assertFalse((self.project / "rgaa/AUDIT-PAR-PAGE.html").exists())

    def test_builder_uses_only_simple_hyphens_in_editorial_text(self):
        campaign = self.init()
        config = yaml.safe_load(campaign.read_text(encoding="utf-8"))
        config["campaign"]["name"] = "Audit — exemple – campagne"
        campaign.write_text(
            yaml.safe_dump(config, allow_unicode=True, sort_keys=False),
            encoding="utf-8",
        )
        self.run_cli("report", campaign)
        portal = (self.project / "PORTAIL-AUDITS.html").read_text(encoding="utf-8")
        self.assertNotIn("—", portal)
        self.assertNotIn("–", portal)
        self.assertIn("Audit - exemple - campagne", portal)

    def test_builder_rejects_evidence_outside_campaign(self):
        campaign = self.init()
        self.run_cli("report", campaign)
        canonical = json.loads(
            (self.project / "rgaa/CONSTATS-INSTANCES.json").read_text(encoding="utf-8")
        )
        canonical["findings"] = [{"page": "P01", "evidence": ["/etc/passwd"]}]
        (self.project / "rgaa/CONSTATS-INSTANCES.json").write_text(
            json.dumps(canonical), encoding="utf-8"
        )
        config_json = self.project / "campaign.json"
        config_json.write_text(
            json.dumps(yaml.safe_load(campaign.read_text(encoding="utf-8"))),
            encoding="utf-8",
        )
        result = subprocess.run(
            [
                sys.executable,
                str(
                    ROOT
                    / ".claude/skills/audit-rgaa-creator/scripts/audit_report_builder.py"
                ),
                str(config_json),
                str(self.project),
            ],
            text=True,
            capture_output=True,
        )
        self.assertNotEqual(0, result.returncode)
        self.assertIn("non portable", result.stderr)

    def test_validate_rejects_modified_builder_config(self):
        campaign = self.init()
        self.run_cli("report", campaign)
        path = self.project / "rapport-dsfr/config/portail.json"
        data = json.loads(path.read_text(encoding="utf-8"))
        data["title"] = "Altéré"
        path.write_text(json.dumps(data), encoding="utf-8")
        result = self.run_cli("validate", campaign, ok=False)
        self.assertIn("Empreinte de configuration", result.stderr)

    def test_builder_separates_criterion_groups_not_instances(self):
        source = (
            ROOT
            / ".claude/skills/dsfr-components/examples/assembled-fixtures/audit-report/page.json"
        )
        data = json.loads(source.read_text(encoding="utf-8"))
        first = data["sections"][0]["findings"][0]
        second = dict(first, id="F002", criterion="10.8")
        third = dict(first, id="F003")
        data["sections"][0]["findings"] = [first, second, third]
        path = self.project / "criterion-groups.json"
        self.project.mkdir(parents=True)
        path.write_text(json.dumps(data), encoding="utf-8")
        result = subprocess.run(
            [
                sys.executable,
                str(
                    ROOT
                    / ".claude/skills/dsfr-components/scripts/generate_assembled_page.py"
                ),
                "--config-file",
                str(path),
            ],
            text=True,
            capture_output=True,
        )
        self.assertEqual(0, result.returncode)
        self.assertEqual(1, result.stdout.count('<hr class="audit-finding-separator"'))

    def test_builder_avoids_separators_outside_rgaa_and_starts_with_problem(self):
        source = (
            ROOT
            / ".claude/skills/dsfr-components/examples/assembled-fixtures/audit-report/page.json"
        )
        data = json.loads(source.read_text(encoding="utf-8"))
        section = data["sections"][0]
        first = section["findings"][0]
        second = dict(first, id="F002", criterion="Migration")
        section["report_type"] = "DSFR"
        section["findings"] = [first, second]
        path = self.project / "dsfr-no-separators.json"
        self.project.mkdir(parents=True)
        path.write_text(json.dumps(data), encoding="utf-8")
        result = subprocess.run(
            [
                sys.executable,
                str(
                    ROOT
                    / ".claude/skills/dsfr-components/scripts/generate_assembled_page.py"
                ),
                "--config-file",
                str(path),
            ],
            text=True,
            capture_output=True,
        )
        self.assertEqual(0, result.returncode)
        self.assertEqual(0, result.stdout.count('<hr class="audit-finding-separator"'))
        self.assertIn(
            f">{first['title']} - <code>{first['rule']}</code></h3>", result.stdout
        )

    def test_builder_rejects_global_conformity_claim(self):
        source = (
            ROOT
            / ".claude/skills/dsfr-components/examples/assembled-fixtures/audit-report/page.json"
        )
        data = json.loads(source.read_text(encoding="utf-8"))
        data["sections"][0]["claim"] = (
            "Conforme au RGAA : tous les critères applicables sont satisfaits."
        )
        path = self.project / "overclaim.json"
        self.project.mkdir(parents=True)
        path.write_text(json.dumps(data), encoding="utf-8")
        result = subprocess.run(
            [
                sys.executable,
                str(
                    ROOT
                    / ".claude/skills/dsfr-components/scripts/generate_assembled_page.py"
                ),
                "--config-file",
                str(path),
                "--check",
            ],
            text=True,
            capture_output=True,
        )
        self.assertNotEqual(0, result.returncode)
        self.assertIn("claim d’audit interdit", result.stderr)

    def test_builder_rejects_invalid_active_canonical_json(self):
        campaign = self.init()
        self.run_cli("report", campaign)
        (self.project / "rgaa/CONSTATS-INSTANCES.json").write_text(
            "{", encoding="utf-8"
        )
        config_json = self.project / "campaign.json"
        config_json.write_text(
            json.dumps(yaml.safe_load(campaign.read_text(encoding="utf-8"))),
            encoding="utf-8",
        )
        result = subprocess.run(
            [
                sys.executable,
                str(
                    ROOT
                    / ".claude/skills/audit-rgaa-creator/scripts/audit_report_builder.py"
                ),
                str(config_json),
                str(self.project),
            ],
            text=True,
            capture_output=True,
        )
        self.assertNotEqual(0, result.returncode)
        self.assertIn("JSON invalide", result.stderr)

    def test_multi_page_portal_links_each_decision_and_dsfr_coverage(self):
        self.run_cli(
            "init",
            "https://example.test/",
            "--output",
            self.project,
            "--page",
            "P01::https://example.test/::Accueil::homepage",
            "--page",
            "P02::https://example.test/contact::Contact::content",
        )
        campaign = self.project / "campaign.yaml"
        self.run_cli("report", campaign)
        for pid in ("P01", "P02"):
            (self.project / f"rgaa/{pid}-DECISIONS-258.json").write_text(
                json.dumps(
                    {
                        "page": {"id": pid},
                        "decisions": [{"test": "1.1.1", "status": "A_RETESTER"}],
                    }
                ),
                encoding="utf-8",
            )
            (self.project / f"rgaa/{pid}-DECISIONS-258.md").write_text(
                f"# {pid}\n", encoding="utf-8"
            )
            (self.project / f"dsfr/{pid}-COUVERTURE-DIMENSIONNELLE.json").write_text(
                json.dumps({"page": {"id": pid}, "summary": {"detected_families": 3}}),
                encoding="utf-8",
            )
            (self.project / f"dsfr/{pid}-COUVERTURE-DIMENSIONNELLE.md").write_text(
                f"# {pid}\n", encoding="utf-8"
            )
        self.run_cli("report", campaign)
        portal = (self.project / "PORTAIL-AUDITS.html").read_text(encoding="utf-8")
        self.assertIn("rgaa/P01-DECISIONS-258.md", portal)
        self.assertIn("rgaa/P02-DECISIONS-258.md", portal)
        self.assertIn("dsfr/P01-COUVERTURE-DIMENSIONNELLE.md", portal)
        self.assertIn("dsfr/P02-COUVERTURE-DIMENSIONNELLE.md", portal)
        for pid in ("P01", "P02"):
            rgaa = (self.project / f"rgaa/pages-html/{pid}.html").read_text(
                encoding="utf-8"
            )
            dsfr = (self.project / f"dsfr/pages-html/{pid}.html").read_text(
                encoding="utf-8"
            )
            self.assertIn(f"Décisions des 258 tests {pid}", rgaa)
            self.assertIn(f"Couverture DSFR {pid}", dsfr)
            self.assertIn("Familles DSFR détectées", dsfr)

    def test_protocol_receives_and_returns_canonical_page_context(self):
        campaign = self.init()
        script = self.project / "protocol.py"
        script.write_text(
            "import json,pathlib,sys\nc=json.load(open(sys.argv[1]));p=pathlib.Path(c['campaign_root'])/c['protocol']['output'].format(page_id=c['page']['id']);p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps({'page':c['page']}))\n",
            encoding="utf-8",
        )
        config = yaml.safe_load(campaign.read_text(encoding="utf-8"))
        config["protocols"] = [
            {
                "id": "context",
                "script": "protocol.py",
                "output": "preuves-protocoles/{page_id}/result.json",
            }
        ]
        campaign.write_text(yaml.safe_dump(config, sort_keys=False), encoding="utf-8")
        self.run_cli("run", campaign, "--only", "protocols")
        output = json.loads(
            (self.project / "preuves-protocoles/P01/result.json").read_text(
                encoding="utf-8"
            )
        )
        self.assertEqual("P01", output["page"]["id"])

    def test_rgaa_qualification_requires_unambiguous_instance(self):
        campaign = self.init()
        page = self.project / "rgaa/pages/P01.json"
        page.parent.mkdir(parents=True)
        data = {
            "schema_version": 1,
            "page": {
                "id": "P01",
                "name": "Accueil",
                "url": "https://example.test/",
                "type": "homepage",
            },
            "signals": [
                {
                    "id": "S1",
                    "rule_id": "R",
                    "criterion": "7.1",
                    "test": "7.1.1",
                    "selector": "#one",
                    "signal_status": "FAIL_CANDIDATE",
                },
                {
                    "id": "S2",
                    "rule_id": "R",
                    "criterion": "7.1",
                    "test": "7.1.1",
                    "selector": "#two",
                    "signal_status": "FAIL_CANDIDATE",
                },
            ],
            "passes": [],
        }
        page.write_text(json.dumps(data), encoding="utf-8")
        (self.project / "rgaa-findings.json").write_text(
            json.dumps(
                {
                    "schema_version": 1,
                    "findings": [
                        {
                            "id": "Q1",
                            "pages": ["P01"],
                            "rule_id": "R",
                            "criterion": "7.1",
                            "test": "7.1.1",
                            "qualification_status": "NC_CONFIRMEE",
                            "comment": "preuve",
                            "evidence": ["campaign.yaml"],
                            "reviewed_by": "test",
                        }
                    ],
                }
            ),
            encoding="utf-8",
        )
        result = self.run_cli("report", campaign, ok=False)
        self.assertIn("Qualification RGAA Q1 ambiguë", result.stderr)

    def test_rgaa_qualification_signal_id_selects_one_instance(self):
        campaign = self.init()
        page = self.project / "rgaa/pages/P01.json"
        page.parent.mkdir(parents=True)
        data = {
            "schema_version": 1,
            "page": {
                "id": "P01",
                "name": "Accueil",
                "url": "https://example.test/",
                "type": "homepage",
            },
            "signals": [
                {
                    "id": "S1",
                    "rule_id": "R",
                    "criterion": "7.1",
                    "test": "7.1.1",
                    "selector": "#same",
                    "instance": 1,
                    "signal_status": "FAIL_CANDIDATE",
                    "title": "Signal",
                    "source": "https://example.test/rgaa",
                },
                {
                    "id": "S2",
                    "rule_id": "R",
                    "criterion": "7.1",
                    "test": "7.1.1",
                    "selector": "#same",
                    "instance": 2,
                    "signal_status": "FAIL_CANDIDATE",
                    "title": "Signal",
                    "source": "https://example.test/rgaa",
                },
            ],
            "passes": [],
        }
        page.write_text(json.dumps(data), encoding="utf-8")
        q = {
            "id": "Q1",
            "pages": ["P01"],
            "rule_id": "R",
            "criterion": "7.1",
            "test": "7.1.1",
            "signal_id": "S2",
            "instance": 2,
            "state": "open",
            "viewport": {"width": 390, "height": 844},
            "evidence_role": "assertion",
            "qualification_status": "NC_CONFIRMEE",
            "comment": "preuve",
            "evidence": ["campaign.yaml"],
            "reviewed_by": "test",
        }
        (self.project / "rgaa-findings.json").write_text(
            json.dumps({"schema_version": 1, "findings": [q]}), encoding="utf-8"
        )
        self.run_cli("report", campaign)
        signals = json.loads(page.read_text(encoding="utf-8"))["signals"]
        self.assertEqual(
            ["NON_TESTE", "NC_CONFIRMEE"],
            [item["qualification_status"] for item in signals],
        )

    def test_dsfr_qualification_signal_id_selects_one_instance(self):
        campaign = self.init()
        page = self.project / "dsfr/pages/P01.json"
        page.parent.mkdir(parents=True)
        data = {
            "schema_version": 2,
            "page": {
                "id": "P01",
                "name": "Accueil",
                "url": "https://example.test/",
                "type": "homepage",
            },
            "inventory": [],
            "differences": [
                {
                    "id": "D1",
                    "rule_id": "DSFR-TEST-001",
                    "kind": "integration",
                    "component": "test",
                    "title": "Signal",
                    "source": "reference",
                    "selector": "#same",
                    "instance": 1,
                },
                {
                    "id": "D2",
                    "rule_id": "DSFR-TEST-001",
                    "kind": "integration",
                    "component": "test",
                    "title": "Signal",
                    "source": "reference",
                    "selector": "#same",
                    "instance": 2,
                },
            ],
        }
        page.write_text(json.dumps(data), encoding="utf-8")
        q = {
            "id": "Q1",
            "pages": ["P01"],
            "rule_id": "DSFR-TEST-001",
            "signal_id": "D2",
            "instance": 2,
            "state": "open",
            "viewport": {"width": 390, "height": 844},
            "evidence_role": "assertion",
            "qualification_status": "ECART_CONFIRME",
            "comment": "preuve",
            "evidence": ["campaign.yaml"],
            "reviewed_by": "test",
        }
        (self.project / "dsfr-findings.json").write_text(
            json.dumps({"schema_version": 1, "findings": [q]}), encoding="utf-8"
        )
        self.run_cli("report", campaign)
        differences = json.loads(page.read_text(encoding="utf-8"))["differences"]
        self.assertEqual(
            ["A_CONFIRMER", "ECART_CONFIRME"],
            [item["qualification_status"] for item in differences],
        )

    def test_manifest_excludes_archives_and_macos_metadata(self):
        campaign = self.init()
        (self.project / "archive.zip").write_bytes(b"zip")
        (self.project / ".DS_Store").write_bytes(b"meta")
        cache = self.project / "scripts/__pycache__"
        cache.mkdir(parents=True)
        (cache / "transient.pyc").write_bytes(b"cache")
        self.run_cli("report", campaign)
        manifest = json.loads(
            (self.project / "MANIFESTE-ARTEFACTS.json").read_text(encoding="utf-8")
        )
        paths = {item["path"] for item in manifest["artifacts"]}
        self.assertNotIn("archive.zip", paths)
        self.assertNotIn(".DS_Store", paths)
        self.assertNotIn("scripts/__pycache__/transient.pyc", paths)

    def test_init_refuses_non_empty_destination(self):
        self.project.mkdir(parents=True)
        (self.project / "keep.txt").write_text("keep", encoding="utf-8")
        result = self.run_cli(
            "init", "https://example.test/", "--output", self.project, ok=False
        )
        self.assertNotEqual(0, result.returncode)
        self.assertEqual(
            "keep", (self.project / "keep.txt").read_text(encoding="utf-8")
        )

    def test_duplicate_yaml_key_is_rejected(self):
        campaign = self.init()
        text = campaign.read_text(encoding="utf-8")
        campaign.write_text(text + "schema_version: 1\n", encoding="utf-8")
        result = self.run_cli("report", campaign, ok=False)
        self.assertNotEqual(0, result.returncode)
        self.assertIn("dupliquée", result.stderr)

    def test_nc_requires_existing_portable_evidence(self):
        campaign = self.init()
        (self.project / "findings.json").write_text(
            json.dumps(
                {
                    "schema_version": 1,
                    "findings": [
                        {
                            "id": "F001",
                            "pages": ["P01"],
                            "criterion": "8.2",
                            "test": "8.2.1",
                            "status": "NC-A",
                            "title": "IDs",
                            "description": "Doublons",
                            "evidence": ["missing.json"],
                        }
                    ],
                },
                ensure_ascii=False,
            ),
            encoding="utf-8",
        )
        self.run_cli("report", campaign)
        result = self.run_cli("validate", campaign, ok=False)
        self.assertNotEqual(0, result.returncode)
        self.assertIn("preuve absente", result.stderr)

    def test_html_values_are_escaped_and_ticket_generated(self):
        campaign = self.init()
        evidence = self.project / "findings" / "proof.json"
        evidence.write_text("{}", encoding="utf-8")
        finding = {
            "id": "F<script>",
            "pages": ["P01"],
            "criterion": "8.2",
            "test": "8.2.1",
            "status": "NC-A",
            "title": "<script>alert(1)</script>",
            "description": "<img src=x onerror=alert(1)>",
            "evidence": ["findings/proof.json"],
        }
        (self.project / "findings.json").write_text(
            json.dumps({"schema_version": 1, "findings": [finding]}), encoding="utf-8"
        )
        proof = self.project / "rgaa/preuves/P01/attempt-001"
        proof.mkdir(parents=True)
        (proof / "evidence.json").write_text("{}", encoding="utf-8")
        (proof / "desktop.png").write_bytes(b"png")
        page = {
            "schema_version": 1,
            "page": {
                "id": "P01",
                "name": "Accueil",
                "url": "https://example.test/",
                "type": "homepage",
            },
            "audited_at": "2026-09-02T00:00:00Z",
            "rules_executed": ["RGAA-8-2-ID-UNIQUE-001"],
            "signals": [
                {
                    "id": "P01-RGAA-8-2-ID-UNIQUE-001-001",
                    "rule_id": "RGAA-8-2-ID-UNIQUE-001",
                    "criterion": "8.2",
                    "test": "8.2.1",
                    "component": "html",
                    "instance": 1,
                    "signal_status": "FAIL_CANDIDATE",
                    "qualification_status": "NON_TESTE",
                    "severity": "Majeur",
                    "title": "Valeur HTML non fiable",
                    "selector": "#malicious",
                    "observed": "Valeur contrôlée par une source hostile",
                    "observed_code": "<img src=x onerror=alert(1)>",
                    "observed_origin": "RENDERED_DOM",
                    "expected": "Code affiché comme texte dans la preuve",
                    "expected_code": "&lt;img src=x onerror=alert(1)&gt;",
                    "failed_assertions": ["Preuve à qualifier"],
                    "impact": "Injection HTML dans le rapport",
                    "source": "https://accessibilite.numerique.gouv.fr/",
                    "recommendation": "Échapper la valeur avant rendu",
                    "verification": "Relire le HTML produit",
                    "evidence": [
                        "rgaa/preuves/P01/attempt-001/evidence.json",
                        "rgaa/preuves/P01/attempt-001/desktop.png",
                    ],
                }
            ],
            "passes": [],
            "evidence": {
                "attempt": 1,
                "raw": "rgaa/preuves/P01/attempt-001/evidence.json",
                "screenshot": "rgaa/preuves/P01/attempt-001/desktop.png",
            },
            "limits": ["Préqualification"],
        }
        (self.project / "rgaa/pages/P01.json").parent.mkdir(parents=True)
        (self.project / "rgaa/pages/P01.json").write_text(
            json.dumps(page, ensure_ascii=False), encoding="utf-8"
        )
        self.run_cli("report", campaign)
        self.run_cli("validate", campaign)
        document = (self.project / "rgaa/AUDIT-PAR-PAGE.html").read_text(encoding="utf-8")
        self.assertNotIn("<img src=x", document)
        self.assertIn("&lt;img", document)
        self.assertEqual(1, len(list((self.project / "tickets").glob("NC-A-*.md"))))

    def test_navigation_guard_distinguishes_proxy_site_and_unreachable(self):
        response = asyncio.run(
            goto_checked(_FakePage(_FakeResponse()), "https://example.test/", 1000)
        )
        self.assertEqual(200, response.status)

        with self.assertRaisesRegex(RuntimeError, "BLOQUÉ-INFRA"):
            asyncio.run(
                goto_checked(
                    _FakePage(
                        _FakeResponse(
                            403, {"X-Deny-Reason": "host_not_allowed"}
                        )
                    ),
                    "https://example.test/",
                    1000,
                )
            )
        with self.assertRaisesRegex(RuntimeError, "ERREUR_SITE"):
            asyncio.run(
                goto_checked(
                    _FakePage(_FakeResponse(403, {"server": "DGDDI-WS"})),
                    "https://example.test/",
                    1000,
                )
            )
        with self.assertRaisesRegex(RuntimeError, "INJOIGNABLE"):
            asyncio.run(
                goto_checked(
                    _FakePage(error="net::ERR_NAME_NOT_RESOLVED"),
                    "https://example.test/",
                    1000,
                )
            )

    def test_preflight_records_machine_status_for_network_block(self):
        state = {
            "schema_version": 1,
            "campaign_digest": "a" * 64,
            "phases": {},
            "pages": {},
        }
        config = {
            "campaign": {"target": "https://example.test/"},
            "sample": [
                {
                    "id": "P01",
                    "name": "Accueil",
                    "url": "https://example.test/",
                    "type": "homepage",
                }
            ],
            "phases": {"ay11": False},
            "tooling": {"skills_roots": []},
        }
        with patch(
            "audit_campaign.probe_network_url",
            return_value={
                "kind": "BLOQUÉ-INFRA",
                "cause": "x-deny-reason: host_not_allowed",
            },
        ):
            result = preflight(config, self.project, state, dry_run=False)
        self.assertFalse(result)
        self.assertEqual(
            "BLOQUE_INFRA", state["phases"]["preflight"]["status"]
        )
        self.assertEqual(
            "BLOQUÉ-INFRA", state["phases"]["preflight"]["cause"]
        )

    def test_network_probe_distinguishes_proxy_and_site_errors(self):
        server = http.server.ThreadingHTTPServer(("127.0.0.1", 0), _HeadHandler)
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        try:
            base = f"http://127.0.0.1:{server.server_port}"
            self.assertEqual("SITE", probe_network_url(f"{base}/ok")["kind"])
            self.assertEqual(
                "BLOQUÉ-INFRA", probe_network_url(f"{base}/proxy")["kind"]
            )
            site_error = probe_network_url(f"{base}/site")
            self.assertEqual("SITE", site_error["kind"])
            self.assertEqual(403, site_error["http_status"])
        finally:
            server.shutdown()
            server.server_close()
            thread.join(timeout=2)

    def test_unknown_configuration_field_is_rejected(self):
        campaign = self.init()
        config = yaml.safe_load(campaign.read_text(encoding="utf-8"))
        config["commande_shell"] = "rm -rf /"
        campaign.write_text(
            yaml.safe_dump(config, allow_unicode=True, sort_keys=False),
            encoding="utf-8",
        )
        result = self.run_cli("report", campaign, ok=False)
        self.assertNotEqual(0, result.returncode)
        self.assertIn("propriété inconnue", result.stderr)

    def test_replan_uses_next_existing_capture_attempt(self):
        fake_root = Path(self.tmp.name) / "fake-ay11"
        fake_bin = fake_root / ".venv/bin/ay11"
        fake_bin.parent.mkdir(parents=True)
        fake_bin.write_text("#!/bin/sh\nprintf '{}\\n'\n", encoding="utf-8")
        fake_bin.chmod(0o755)
        campaign = self.init("--ay11-root", fake_root)
        (self.project / "captures-ay11/P01/attempt-001").mkdir(parents=True)
        self.run_cli("replan", campaign)
        self.run_cli("run", campaign, "--only", "capture")
        self.assertTrue((self.project / "captures-ay11/P01/attempt-002").is_dir())

    def test_changed_configuration_requires_replan(self):
        campaign = self.init()
        self.run_cli("run", campaign, "--only", "report")
        config = yaml.safe_load(campaign.read_text(encoding="utf-8"))
        config["campaign"]["name"] = "Nouveau nom"
        campaign.write_text(
            yaml.safe_dump(config, allow_unicode=True, sort_keys=False),
            encoding="utf-8",
        )
        result = self.run_cli("resume", campaign, "--only", "report", ok=False)
        self.assertNotEqual(0, result.returncode)
        self.assertIn("replan", result.stderr)
        self.run_cli("replan", campaign)
        self.run_cli("resume", campaign, "--only", "report")
        self.assertTrue(list((self.project / ".creator/history").glob("state-*.json")))

    def test_resume_replays_report_after_upstream_phase_changes(self):
        campaign = self.init()
        protocol = self.project / "protocol.py"
        protocol.write_text(
            "import json, pathlib, sys\n"
            "context = json.loads(pathlib.Path(sys.argv[1]).read_text())\n"
            "output = pathlib.Path(context['campaign_root']) / context['protocol']['output'].format(page_id=context['page']['id'])\n"
            "output.parent.mkdir(parents=True, exist_ok=True)\n"
            "output.write_text(json.dumps({'page': context['page'], 'revision': 1}))\n",
            encoding="utf-8",
        )
        config = yaml.safe_load(campaign.read_text(encoding="utf-8"))
        config["protocols"] = [
            {
                "id": "versioned-proof",
                "script": "protocol.py",
                "output": "preuves-protocoles/{page_id}/result.json",
            }
        ]
        campaign.write_text(
            yaml.safe_dump(config, allow_unicode=True, sort_keys=False),
            encoding="utf-8",
        )
        self.run_cli("run", campaign, "--only", "protocols,report,validate")

        state_path = self.project / ".creator/state.json"
        state = json.loads(state_path.read_text(encoding="utf-8"))
        self.assertEqual("OK", state["phases"]["report"]["status"])
        initial_validate_status = state["phases"]["validate"]["status"]
        self.assertIn(initial_validate_status, {"OK", "PARTIEL"})
        protocol.write_text(
            protocol.read_text(encoding="utf-8").replace("revision': 1", "revision': 2"),
            encoding="utf-8",
        )
        state["phases"]["protocols"]["status"] = "ECHEC"
        state_path.write_text(json.dumps(state), encoding="utf-8")

        result = self.run_cli(
            "resume", campaign, "--only", "protocols,report,validate"
        )
        self.assertIn("phases invalidées", result.stdout)
        self.assertEqual(
            2,
            json.loads(
                (self.project / "preuves-protocoles/P01/result.json").read_text(
                    encoding="utf-8"
                )
            )["revision"],
        )
        state = json.loads(state_path.read_text(encoding="utf-8"))
        self.assertEqual("OK", state["phases"]["report"]["status"])
        self.assertEqual(initial_validate_status, state["phases"]["validate"]["status"])
        self.assertEqual(
            [], json.loads((self.project / "VALIDATION.json").read_text())["errors"]
        )

    def test_human_only_rgaa_finding_is_included_in_report(self):
        campaign = self.init()
        finding = {
            "schema_version": 1,
            "findings": [
                {
                    "id": "RGAA-P01-H-001",
                    "pages": ["P01"],
                    "rule_id": "RGAA-1-8-IMAGE-TEXT-HUMAN-001",
                    "criterion": "1.8",
                    "test": "1.8.1",
                    "qualification_status": "NC_CONFIRMEE",
                    "severity": "Majeur",
                    "comment": "Une image informative contient du texte sans alternative complète.",
                    "evidence": ["campaign.yaml"],
                }
            ],
        }
        (self.project / "rgaa-findings.json").write_text(
            json.dumps(finding), encoding="utf-8"
        )
        documentary = self.project / "P01-AUDIT-DECLARATION-ACCESSIBILITE.md"
        documentary.write_text("# Audit documentaire\n", encoding="utf-8")
        component_review = self.project / "P01-REVUE-COMPOSANTS-ET-ETATS.md"
        component_review.write_text("# Revue des composants\n", encoding="utf-8")
        self.run_cli("report", campaign)
        portal = (self.project / "PORTAIL-AUDITS.html").read_text(encoding="utf-8")
        self.assertIn("P01-AUDIT-DECLARATION-ACCESSIBILITE.md", portal)
        self.assertIn("P01-REVUE-COMPOSANTS-ET-ETATS.md", portal)
        detail = (self.project / "rgaa/pages-html/P01.html").read_text(encoding="utf-8")
        self.assertIn("RGAA-1-8-IMAGE-TEXT-HUMAN-001", detail)
        canonical = json.loads(
            (self.project / "rgaa/CONSTATS-INSTANCES.json").read_text(encoding="utf-8")
        )
        self.assertTrue(
            any(
                item["rule_id"] == "RGAA-1-8-IMAGE-TEXT-HUMAN-001"
                for item in canonical["findings"]
            )
        )
        self.run_cli("report", campaign)
        canonical = json.loads(
            (self.project / "rgaa/CONSTATS-INSTANCES.json").read_text(encoding="utf-8")
        )
        self.assertEqual(
            1,
            sum(
                item["rule_id"] == "RGAA-1-8-IMAGE-TEXT-HUMAN-001"
                for item in canonical["findings"]
            ),
        )

    def test_generic_dsfr_dimensional_coverage_builder(self):
        page_dir = self.project / "dsfr/pages"
        page_dir.mkdir(parents=True)
        proof_dir = self.project / "preuves-p01-complet"
        proof_dir.mkdir(parents=True)
        page = {
            "page": {"id": "P01", "name": "Accueil", "url": "https://example.test/"},
            "inventory": [
                {
                    "name": "share",
                    "count": 1,
                    "status": "AUCUN_ECART_OBSERVE",
                    "rules_executed": ["DSFR-SHARE-STRUCTURE-001"],
                }
            ],
        }
        (page_dir / "P01.json").write_text(json.dumps(page), encoding="utf-8")
        (proof_dir / "P01-COLLECTE-COMPLETE.json").write_text(
            json.dumps(
                {"inventory": {"classes": {"fr-share": 1, "fr-share__title": 1}}}
            ),
            encoding="utf-8",
        )
        script = (
            ROOT
            / ".claude/skills/audit-dsfr-complet/scripts/dsfr_dimensional_coverage.py"
        )
        result = subprocess.run(
            [sys.executable, str(script), str(self.project), "P01"],
            text=True,
            capture_output=True,
        )
        self.assertEqual(0, result.returncode, result.stderr)
        coverage = json.loads(
            (self.project / "dsfr/P01-COUVERTURE-DIMENSIONNELLE.json").read_text(
                encoding="utf-8"
            )
        )
        self.assertEqual(1, coverage["summary"]["detected_families"])
        self.assertGreaterEqual(coverage["summary"]["catalog_rules"], 46)

    def test_page_specific_coverage_paths_are_not_hardcoded_to_p01(self):
        engine = (
            ROOT / ".claude/skills/audit-rgaa-creator/scripts/engine_coverage.py"
        ).read_text(encoding="utf-8")
        report = (
            ROOT / ".claude/skills/audit-rgaa-creator/scripts/audit_report_builder.py"
        ).read_text(encoding="utf-8")
        validator = (
            ROOT / ".claude/skills/audit-rgaa-creator/scripts/audit_campaign.py"
        ).read_text(encoding="utf-8")
        self.assertNotIn('root / "rgaa/P01-DECISIONS-258.json"', engine)
        self.assertNotIn('root / "dsfr/P01-COUVERTURE-DIMENSIONNELLE.json"', engine)
        self.assertNotIn('root / "rgaa/P01-DECISIONS-258.json"', report)
        self.assertNotIn('root / "dsfr/P01-COUVERTURE-DIMENSIONNELLE.json"', report)
        self.assertNotIn("p01_decisions_path", validator)


if __name__ == "__main__":
    unittest.main()
