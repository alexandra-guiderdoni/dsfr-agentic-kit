"""Sorties des traces hors du produit, sans appeler de modèle."""

import argparse
import importlib.util
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


if __name__ == "__main__":
    unittest.main()
