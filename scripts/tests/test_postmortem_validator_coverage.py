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
from probe_matrix import criterion_sources, load_validator
from validator_results import validator_result


class ValidatorResultTests(unittest.TestCase):
    def test_transport_or_missing_document_is_not_a_success(self):
        for payload in (
            None,
            [],
            {},
            {"messages": None},
            {"messages": ["invalid"]},
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
        for payload in ("not JSON", {}):
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


if __name__ == "__main__":
    unittest.main()
