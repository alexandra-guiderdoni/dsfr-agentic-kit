"""État ciblé : options natives et refus des observations non préparées."""

# PDG-LARGE-FILE-JUSTIFICATION: ce module réunit le contrat d'état et ses
# contre-preuves via le CLI natif, Chromium et les journaux du même parcours.

import asyncio
import importlib.util
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / ".claude/skills/audit-rgaa-creator/scripts"))
from audit_campaign import run_command
from observation_state import (
    native_capture_options,
    native_state_observation,
    reject_unprepared_reports,
    require_page_state,
)


def page_info():
    return {
        "id": "P01",
        "url": "https://example.test/",
        "state": {
            "id": "confirmation",
            "journey": "journey.json",
            "expect": "Fixture",
            "expect_selector": "#state",
        },
    }


class StateContractTests(unittest.TestCase):
    def test_invariant_arguments_are_masked_in_command_logs(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "command.json"
            argv = [
                "ay11",
                "--expect",
                "synthetic-sensitive-value",
                "--expect-selector",
                "#synthetic-secret",
            ]
            run_command(argv, path, dry_run=True, private_invariant=True)
            self.assertNotIn("synthetic-sensitive-value", path.read_text())
            self.assertNotIn("#synthetic-secret", path.read_text())
            self.assertEqual("synthetic-sensitive-value", argv[2])

    def test_profile_and_temporal_are_separate_requests(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "journey.json").write_text("{}")
            config = {"campaign": {"profile": "rgaa-50"}, "browser": {}}
            options = native_capture_options(config, page_info(), root)
            self.assertEqual(["--profile", "rgaa-50"], options[:2])
            self.assertNotIn("--temporal-probes", options)
            self.assertIn("--expect-selector", options)
            config["browser"]["temporal_probes"] = True
            self.assertIn(
                "--temporal-probes", native_capture_options(config, page_info(), root)
            )

    def test_journey_outside_campaign_is_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            info = page_info()
            info["state"]["journey"] = "../outside.json"
            with self.assertRaisesRegex(ValueError, "hors"):
                native_capture_options({}, info, Path(directory))

    def test_cli_success_is_not_enough_for_a_targeted_state(self):
        for manifest in (
            {},
            [],
            {"journey_trace": "invalid"},
            {
                "journey_trace": {
                    "expectation_verified": True,
                    "expectation_mode": "text_present",
                }
            },
        ):
            self.assertFalse(
                native_state_observation(page_info(), manifest)["invariant_verified"]
            )
        trace = {
            "expectation_verified": True,
            "expectation_mode": "target_state_observed",
            "expectation_target": {"match_count": 1, "visible": True},
        }
        self.assertTrue(
            native_state_observation(page_info(), {"journey_trace": trace})[
                "invariant_verified"
            ]
        )

    def test_unprepared_engines_cannot_feed_comparative_reports(self):
        config = {"sample": [page_info()], "phases": {"rgaa_checks": True}}
        with self.assertRaisesRegex(ValueError, "refusés"):
            reject_unprepared_reports(config)
        reject_unprepared_reports(
            {"sample": [{"id": "P01"}], "phases": {"rgaa_checks": True}}
        )


@unittest.skipUnless(
    importlib.util.find_spec("playwright"),
    "Playwright Python requis pour la preuve navigateur",
)
class StateBrowserTests(unittest.TestCase):
    def test_closed_dialog_is_not_credited_by_any_secondary_engine(self):
        from playwright.async_api import async_playwright

        async def run(root):
            async with async_playwright() as pw:
                browser = await pw.chromium.launch(headless=True)
                for engine in ("browser", "rgaa", "dsfr"):
                    context = await browser.new_context()
                    page = await context.new_page()
                    await page.set_content(
                        '<title>Fixture</title><dialog><h2 id="state">Fixture</h2></dialog>'
                    )
                    with self.assertRaisesRegex(ValueError, "non pris en charge"):
                        await require_page_state(
                            page, page_info(), root, engine, "desktop"
                        )
                    receipt = json.loads(
                        next(
                            (root / "observations" / engine / "P01").glob("*.json")
                        ).read_text()
                    )
                    self.assertEqual("unsupported_preparation", receipt["status"])
                    self.assertFalse(receipt["invariant_verified"])
                    self.assertFalse(receipt["target_visible"])
                    self.assertEqual(engine, receipt["engine"])
                await browser.close()

        with tempfile.TemporaryDirectory() as directory:
            asyncio.run(run(Path(directory)))


@unittest.skipUnless(
    importlib.util.find_spec("ay11"), "Runtime AY11 requis pour la capture native"
)
class NativeCaptureTests(unittest.TestCase):
    def test_native_capture_reaches_the_requested_dialog(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            html = root / "fixture.html"
            html.write_text(
                '<!doctype html><html lang="fr"><title>Fixture</title><button id="open" onclick="document.querySelector(\'dialog\').showModal()">Ouvrir</button><dialog><h2 id="state">Fixture</h2><button>Fermer</button></dialog></html>'
            )
            (root / "journey.json").write_text(
                json.dumps(
                    {
                        "schema_version": 1,
                        "read_only_effect_confirmed": True,
                        "actions": [{"type": "click", "selector": "#open"}],
                    }
                )
            )
            options = native_capture_options(
                {"campaign": {"profile": "rgaa-25"}}, page_info(), root
            )
            result = subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "ay11",
                    "preaudit",
                    "capture-browser",
                    html.as_uri(),
                    "--output-dir",
                    str(root / "capture"),
                    "--wait-ms",
                    "0",
                    "--json",
                    *options,
                ],
                capture_output=True,
                text=True,
                check=False,
                timeout=120,
                env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"},
            )
            self.assertEqual(0, result.returncode, result.stderr)
            manifest = json.loads(result.stdout)
            self.assertTrue(
                native_state_observation(page_info(), manifest)["invariant_verified"]
            )


if __name__ == "__main__":
    unittest.main()
