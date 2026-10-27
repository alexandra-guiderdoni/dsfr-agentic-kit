"""Régressions des tickets kit #17 et #16 sur des campagnes jetables."""

import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[2]
SCRIPTS = ROOT / ".claude/skills/audit-rgaa-creator/scripts"
sys.path.insert(0, str(SCRIPTS))
from audit_campaign import write_validator_receipt
from collection_identity import write_binding
from engine_coverage import generate_engine_coverage
from probe_matrix import classify_payload, criterion_sources, load_validator
from validator_results import validator_result


class ValidatorResultTests(unittest.TestCase):
    def test_transport_or_missing_document_is_not_a_success(self):
        for payload in (
            None,
            [],
            {},
            {"messages": None},
            {"messages": ["invalid"]},
            {"messages": [{}]},
            {"messages": [{"type": "garbage"}]},
            {"messages": [{"type": "error"}]},
            {
                "messages": [
                    {"type": "non-document-error", "message": "Forbidden host."}
                ]
            },
        ):
            with self.subTest(payload=payload):
                result = validator_result(payload)
                self.assertFalse(result["executed"])
                self.assertIsNone(result["errors"])

    def test_syntax_error_and_empty_valid_response_are_executed(self):
        self.assertTrue(validator_result({"messages": []})["executed"])
        result = validator_result(
            {"messages": [{"type": "error", "message": "Bad markup"}]}
        )
        self.assertTrue(result["executed"])
        self.assertEqual(1, result["errors"])

    def test_unexecuted_validator_does_not_instrument_the_criterion(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "validateur-w3c").mkdir()
            (root / "validateur-w3c/P01.json").write_text(
                json.dumps({"messages": [{"type": "non-document-error"}]})
            )
            aggregate = {"validator": load_validator(root)}
            result = criterion_sources(aggregate, "8.2")
            self.assertEqual(["P01"], result["validator_unexecuted_pages"])
            self.assertFalse(result["instrumente"])
            self.assertNotIn("validateur", result["sources"])

    def test_legacy_receipt_is_archived_without_rewriting_its_bytes(self):
        with tempfile.TemporaryDirectory() as directory:
            destination = Path(directory)
            old = b'{"messages":[]}\n\n'
            (destination / "P01.json").write_bytes(old)
            receipt = write_validator_receipt(
                destination, "P01", {"messages": [{"type": "non-document-error"}]}
            )
            self.assertEqual(old, (destination / "P01/attempt-001.json").read_bytes())
            self.assertEqual("attempt-002.json", receipt.name)


class ValidatorCampaignTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix="kit-validator-")
        self.root = Path(self.tmp.name) / "campaign"
        initialized = self.cli(
            "init",
            "https://example.test/",
            "--output",
            self.root,
            "--page",
            "https://example.test/::Accueil::homepage",
        )
        self.assertEqual(0, initialized.returncode, initialized.stderr)
        self.config = self.root / "campaign.yaml"
        config = yaml.safe_load(self.config.read_text())
        self.payload = self.root / "fake-validator-response.txt"
        script = self.root / "fake-validator.py"
        script.write_text(
            "from pathlib import Path\nprint(Path(__file__).with_name('fake-validator-response.txt').read_text())\n"
        )
        config["validator"] = {
            "command": f"{sys.executable} {script}",
            "delay_seconds": 0,
        }
        self.config.write_text(yaml.safe_dump(config, allow_unicode=True))
        replanned = self.cli("replan", self.config)
        self.assertEqual(0, replanned.returncode, replanned.stderr)
        capture = self.root / "captures-ay11/P01/attempt-001"
        capture.mkdir(parents=True)
        (capture / "fixture-rendered.html").write_text(
            "<!doctype html><html lang='fr'><title>Test</title><p>Fixture</p></html>"
        )

    def tearDown(self):
        self.tmp.cleanup()

    def cli(self, *args):
        return subprocess.run(
            [sys.executable, str(SCRIPTS / "audit_campaign.py"), *map(str, args)],
            check=False,
            capture_output=True,
            text=True,
            env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"},
            timeout=30,
        )

    def run_validator(self, payload):
        self.payload.write_text(
            payload if isinstance(payload, str) else json.dumps(payload)
        )
        result = self.cli("run", self.config, "--only", "validator")
        state = json.loads((self.root / ".creator/state.json").read_text())
        return result, state

    def test_forbidden_host_is_partial_without_an_html_error(self):
        result, state = self.run_validator(
            {"messages": [{"type": "non-document-error", "message": "Forbidden host."}]}
        )
        self.assertEqual(4, result.returncode, result.stderr)
        self.assertEqual("PARTIEL", state["phases"]["validator"]["status"])
        self.assertFalse(state["pages"]["P01"]["validator"]["executed"])
        self.assertIsNone(state["pages"]["P01"]["validator"]["erreurs"])

    def test_malformed_or_missing_document_is_partial(self):
        for payload in (
            "not JSON",
            {},
            {"messages": [{}]},
            {"messages": [{"type": "garbage"}]},
        ):
            with self.subTest(payload=payload):
                result, state = self.run_validator(payload)
                self.assertEqual(4, result.returncode, result.stderr)
                self.assertEqual("PARTIEL", state["phases"]["validator"]["status"])

    def test_actual_syntax_error_remains_a_collected_result(self):
        result, state = self.run_validator(
            {"messages": [{"type": "error", "message": "Invalid HTML"}]}
        )
        self.assertEqual(0, result.returncode, result.stderr)
        self.assertEqual(1, state["pages"]["P01"]["validator"]["erreurs"])
        self.assertTrue(state["pages"]["P01"]["validator"]["executed"])

    def test_missing_local_binary_is_receipted_as_partial(self):
        config = yaml.safe_load(self.config.read_text())
        config["validator"]["command"] = "/nonexistent/kit-test-validator"
        self.config.write_text(yaml.safe_dump(config, allow_unicode=True))
        self.assertEqual(0, self.cli("replan", self.config).returncode)
        result, state = self.run_validator({"messages": []})
        self.assertEqual(4, result.returncode, result.stderr)
        self.assertFalse(state["pages"]["P01"]["validator"]["executed"])

    def test_successful_retry_preserves_the_initial_failure(self):
        result, first = self.run_validator(
            {"messages": [{"type": "non-document-error"}]}
        )
        self.assertEqual(4, result.returncode)
        archived = self.root / first["pages"]["P01"]["validator"]["receipt"]
        original = archived.read_bytes()
        result, second = self.run_validator({"messages": []})
        self.assertEqual(0, result.returncode, result.stderr)
        self.assertEqual("OK", second["phases"]["validator"]["status"])
        self.assertEqual(original, archived.read_bytes())
        self.assertNotEqual(
            str(archived.relative_to(self.root)),
            second["pages"]["P01"]["validator"]["receipt"],
        )


class EngineCoverageTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix="kit-coverage-")
        self.root = Path(self.tmp.name)
        self.capture = self.root / "captures-ay11/P01/attempt-001"
        self.attempt = self.root / "collectes-ay11/P01/attempt-001"
        self.capture.mkdir(parents=True)
        (self.attempt / "sondes").mkdir(parents=True)
        self.html = self.capture / "fixture-rendered.html"
        self.html.write_text("<button disabled>Action</button>")
        self.browser = self.capture / "fixture-browser-collection.json"
        self.browser.write_text("{}")
        self.axe = self.capture / "fixture-axe-core-collection.json"
        self.axe.write_text(
            json.dumps(
                {
                    "kind": "ay11_tool_evidence_collection",
                    "tool_name": "axe-core",
                    "rules": [{"outcome": "violations", "rgaa_mappings": ["11.1.1"]}],
                }
            )
        )
        self.probe = self.attempt / "sondes/accessible-name-11.1.json"
        self.probe.write_text(
            json.dumps(
                {
                    "collection_status": "partially_collected",
                    "results": [
                        {
                            "severity": "fail",
                            "is_disabled": True,
                            "selector": "button",
                            "rgaa_candidates": ["11.1"],
                        }
                    ],
                    "test_collection": {"11.1.1": "not_collected"},
                }
            )
        )
        (self.attempt / "rgaa-collected-plan.json").write_text(
            json.dumps(
                {
                    "proof_contract": {
                        "tests": [
                            {"test_id": "11.1.1", "collection_status": "not_collected"}
                        ]
                    },
                }
            )
        )
        self.state = {
            "pages": {
                "P01": {
                    "capture_dir": str(self.capture.relative_to(self.root)),
                    "collect_dir": str(self.attempt.relative_to(self.root)),
                }
            }
        }
        (self.root / ".creator").mkdir()
        self.save_state()
        write_binding(
            self.root, self.attempt, "P01", [self.html, self.browser, self.axe]
        )

    def save_state(self):
        (self.root / ".creator/state.json").write_text(json.dumps(self.state))

    def tearDown(self):
        self.tmp.cleanup()

    def test_native_subdirectory_and_axe_count_provenance_only(self):
        result = generate_engine_coverage(self.root)
        self.assertEqual(1, result["summary"]["rgaa_pages_with_axe_core"])
        self.assertEqual(1, result["summary"]["rgaa_tests_with_ay11_probe"])
        self.assertEqual(0, result["summary"]["rgaa_tests_collected_by_ay11"])
        candidate = result["ay11_review_candidates"][0]
        self.assertTrue(candidate["is_disabled"])
        self.assertEqual("A_REVOIR", candidate["decision_status"])
        self.assertEqual(
            1, classify_payload(json.loads(self.probe.read_text()))["signal_count"]
        )

    def test_capture_change_does_not_consume_previous_evidence(self):
        self.state["pages"]["P01"]["capture_dir"] = "captures-ay11/P01/attempt-002"
        self.save_state()
        result = generate_engine_coverage(self.root)
        self.assertEqual(
            "capture_mismatch", result["ay11_collection_provenance"][0]["status"]
        )
        self.assertEqual(0, result["summary"]["rgaa_pages_with_axe_core"])
        self.assertEqual(0, result["summary"]["rgaa_tests_with_ay11_probe"])

    def test_changed_input_or_unselected_collection_is_explicit(self):
        self.html.write_text("changed")
        result = generate_engine_coverage(self.root)
        self.assertEqual(
            "artifact_mismatch", result["ay11_collection_provenance"][0]["status"]
        )
        self.state["pages"]["P01"]["collect_dir"] = "collectes-ay11/P01/attempt-002"
        self.save_state()
        result = generate_engine_coverage(self.root)
        self.assertEqual(
            "collection_not_selected", result["ay11_collection_provenance"][0]["status"]
        )

    def test_legacy_artifacts_remain_visible_without_current_state_credit(self):
        (self.attempt / "source-identity.json").unlink()
        result = generate_engine_coverage(self.root)
        self.assertEqual(
            "identity_unknown", result["ay11_collection_provenance"][0]["status"]
        )
        self.assertEqual(1, len(result["ay11_discovered_probes"]))
        self.assertEqual(1, len(result["ay11_discovered_axe"]))
        self.assertEqual(0, result["summary"]["rgaa_tests_with_ay11_probe"])


if __name__ == "__main__":
    unittest.main()
