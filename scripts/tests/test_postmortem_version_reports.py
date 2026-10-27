"""Contre-tests des versions CLI et des référentiels annoncés par BUILD.json."""

import importlib.util
import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import yaml

ROOT = Path(__file__).resolve().parents[2]
SCRIPTS = ROOT / ".claude/skills/audit-rgaa-creator/scripts"
sys.path.insert(0, str(SCRIPTS))
from audit_campaign import detect_ay11_version, preflight

spec = importlib.util.spec_from_file_location(
    "report_capture",
    ROOT / ".claude/skills/audit-report-dsfr/scripts/capture_audit_reports.py",
)
capture = importlib.util.module_from_spec(spec)
spec.loader.exec_module(capture)


class VersionTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.cli = self.root / "ay11"

    def tearDown(self):
        self.tmp.cleanup()

    def fake_cli(self, output, code):
        self.cli.write_text(
            f"#!{sys.executable}\nimport sys\nprint({output!r})\nsys.exit({code})\n"
        )
        self.cli.chmod(0o700)

    def test_help_failure_or_success_does_not_become_a_version(self):
        for text, code in (
            ("usage: ay11 106", 2),
            ("0.1.0", 2),
            ("usage: ay11 0.1.0", 0),
            ("0.1.0\nwarning", 0),
        ):
            with self.subTest(text=text, code=code):
                self.fake_cli(text, code)
                self.assertEqual("", detect_ay11_version(self.cli))

    def test_identifiable_successful_version_is_accepted(self):
        for text in ("0.1.0", "ay11 version 0.1.0", "ay11 v0.1.0"):
            self.fake_cli(text, 0)
            self.assertEqual("0.1.0", detect_ay11_version(self.cli))

    def check_preflight(self, minimum, absent=False):
        config = {
            "campaign": {"target": "https://example.test/"},
            "sample": [{"id": "P01", "url": "https://example.test/"}],
            "tooling": {"skills_roots": []},
            "tooling_options": {"ay11_version": minimum},
            "phases": {
                "ay11": True,
                "browser_checks": False,
                "rgaa_checks": False,
                "dsfr_checks": False,
                "validator": False,
            },
        }
        state = {"phases": {}, "pages": {}}
        with (
            patch(
                "audit_campaign.find_ay11",
                return_value=(None if absent else self.cli, []),
            ),
            patch("audit_campaign.campaign_schema_errors", return_value=[]),
            patch("audit_campaign.probe_network_url", return_value={"kind": "SITE"}),
        ):
            result = preflight(config, self.root, state, dry_run=False)
        return result, state["phases"]["preflight"]

    def test_required_minimum_refuses_unknown_or_insufficient_version(self):
        for text, code in (("usage: ay11", 2), ("0.1.0", 0)):
            self.fake_cli(text, code)
            valid, state = self.check_preflight("0.2.0")
            self.assertFalse(valid)
            self.assertTrue(state["errors"])

    def test_unknown_without_minimum_is_explicit_and_not_a_product_error(self):
        self.fake_cli("usage: ay11", 2)
        valid, state = self.check_preflight("")
        self.assertTrue(valid)
        self.assertIsNone(state["ay11_version"])
        self.assertEqual("unknown", state["ay11_version_status"])
        self.assertTrue(any("inconnue" in message for message in state["warnings"]))

    def test_missing_executable_is_fatal_only_when_required(self):
        self.assertFalse(self.check_preflight("0.2.0", absent=True)[0])
        self.assertTrue(self.check_preflight("", absent=True)[0])


class ReportDiscoveryTests(unittest.TestCase):
    def fixture(self, root, modes):
        (root / "rapport-dsfr").mkdir()
        (root / "campaign.yaml").write_text(
            yaml.safe_dump(
                {
                    "sample": [{"id": "P01"}],
                    "phases": {
                        f"{name}_checks": name in modes for name in ("rgaa", "dsfr")
                    },
                }
            )
        )
        paths = [
            "PORTAIL-AUDITS.html",
            *[f"{name}/pages-html/P01.html" for name in modes],
        ]
        for rel in paths:
            path = root / rel
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text("<!doctype html><title>Fixture</title>")
        build = {
            "active_referentials": modes,
            "outputs": [{"path": path} for path in paths],
        }
        (root / "rapport-dsfr/BUILD.json").write_text(json.dumps(build))

    def test_rgaa_dsfr_and_mixed_only_request_active_reports(self):
        for modes in (["rgaa"], ["dsfr"], ["rgaa", "dsfr"]):
            with tempfile.TemporaryDirectory() as directory:
                root = Path(directory)
                self.fixture(root, modes)
                _, reports = capture.discover(root)
                self.assertEqual(
                    ["portal", *[f"{name}-P01" for name in modes]],
                    [item["key"] for item in reports],
                )

    def test_announced_missing_output_still_fails(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.fixture(root, ["rgaa"])
            (root / "rgaa/pages-html/P01.html").unlink()
            with self.assertRaisesRegex(ValueError, "absente"):
                capture.discover(root)

    def test_build_from_a_different_configuration_is_not_consumed(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.fixture(root, ["rgaa"])
            config = yaml.safe_load((root / "campaign.yaml").read_text())
            config["phases"]["dsfr_checks"] = True
            (root / "campaign.yaml").write_text(yaml.safe_dump(config))
            with self.assertRaisesRegex(ValueError, "incompatibles"):
                capture.discover(root)


if __name__ == "__main__":
    unittest.main()
