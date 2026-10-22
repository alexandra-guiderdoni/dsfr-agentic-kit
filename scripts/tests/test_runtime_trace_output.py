"""Sorties des traces hors du produit, sans appeler de modèle."""

import argparse
import importlib.util
import json
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

SOURCE = (
    Path(__file__).resolve().parents[2]
    / "design-systems/scripts/check-dsfr-runtime-trace.py"
)


class RuntimeTraceOutputTests(unittest.TestCase):
    def setUp(self):
        spec = importlib.util.spec_from_file_location("runtime_trace_fixture", SOURCE)
        self.module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(self.module)
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.base = Path(self.temp.name).resolve()
        self.kit = self.base / "kit"
        self.kit.mkdir()
        self.module.ROOT = self.kit
        self.module.POSITIVE_OUT = self.kit / "positive.json"
        self.module.NEAR_MISS_OUT = self.kit / "near-miss.json"

    def test_run_uses_external_output_directory(self):
        out = self.base / "project/traces"
        args = argparse.Namespace(output_dir=out, timeout=1)
        with (
            patch.object(self.module, "run_codex") as run,
            patch.object(self.module, "check", return_value=0),
        ):
            self.assertEqual(self.module.run(args), 0)
        self.assertEqual(
            [call.args[2].parent for call in run.call_args_list], [out, out]
        )
        self.assertTrue(out.is_dir())
        self.assertEqual(list(self.kit.iterdir()), [])

    def test_run_refuses_internal_and_redirected_outputs_before_codex(self):
        link = self.base / "redirect"
        link.symlink_to(self.kit, target_is_directory=True)
        for out in (self.kit, self.kit / "traces", link / "traces"):
            with patch.object(self.module, "run_codex") as run:
                with self.assertRaises(ValueError):
                    self.module.run(argparse.Namespace(output_dir=out, timeout=1))
                run.assert_not_called()

    def test_normalize_refuses_internal_output(self):
        source = self.base / "input.jsonl"
        source.write_text("")
        args = argparse.Namespace(
            jsonl=source, case="fixture", output=self.kit / "trace.json"
        )
        with self.assertRaises(ValueError):
            self.module.normalize(args)
        self.assertFalse(args.output.exists())

    def test_run_refuses_file_symlinks_before_any_codex_call(self):
        out = self.base / "project"
        out.mkdir()
        for name in ("positive.json", "near-miss.json"):
            (out / name).symlink_to(self.kit / name)
        with patch.object(self.module, "run_codex") as run:
            with self.assertRaises(ValueError):
                self.module.run(argparse.Namespace(output_dir=out, timeout=1))
            run.assert_not_called()

    def test_codex_uses_consumer_context_instead_of_installed_product(self):
        project = self.base / "consumer"
        project.mkdir()
        out = project / "trace.json"
        result = subprocess.CompletedProcess(
            [], 0, json.dumps({"type": "turn.completed", "usage": {}}), ""
        )
        with patch.object(self.module.subprocess, "run", return_value=result) as call:
            self.module.run_codex("fixture", "fixture", out, 1, cwd=project)
        command = call.call_args.args[0]
        self.assertEqual(command[command.index("-C") + 1], str(project))
        self.assertNotIn(str(self.kit), command)
        self.assertIn(str(project), call.call_args.kwargs["input"])

    def test_default_context_follows_calling_project(self):
        project = self.base / "consumer"
        project.mkdir()
        with (
            patch.object(self.module.Path, "cwd", return_value=project),
            patch.object(self.module, "run_codex") as run,
            patch.object(self.module, "check", return_value=0),
        ):
            self.module.run(
                argparse.Namespace(output_dir=project / "traces", timeout=1)
            )
        self.assertEqual(
            [c.kwargs.get("cwd") for c in run.call_args_list], [project, project]
        )

    def test_context_inside_product_or_redirected_is_refused_before_codex(self):
        redirect = self.base / "redirect"
        redirect.symlink_to(self.kit, target_is_directory=True)
        for context in (self.kit, redirect):
            with patch.object(self.module, "run_codex") as call:
                with self.assertRaises(ValueError):
                    self.module.run(
                        argparse.Namespace(
                            output_dir=self.base / "traces", timeout=1, cwd=context
                        )
                    )
                call.assert_not_called()
            self.assertFalse((self.base / "traces").exists())

    def test_failed_reference_read_cannot_validate_positive_trace(self):
        trace = {
            "case": "pos-page-form",
            "commands": [
                {
                    "command": "cat " + " ".join(self.module.POSITIVE_COMMAND_NEEDLES),
                    "exit_code": 1,
                }
            ],
            "final_messages": ["dsfr-components : page complète form"],
        }
        check = self.module.Check()
        self.module.check_positive(check, trace)
        self.assertTrue(check.bad)


if __name__ == "__main__":
    unittest.main()
