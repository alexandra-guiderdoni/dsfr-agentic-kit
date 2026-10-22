"""Le validateur reçoit le contrat actuel et refuse un contrat incomplet."""

import contextlib
import importlib.util
import io
import unittest
from pathlib import Path
from unittest.mock import patch

SOURCE = (
    Path(__file__).resolve().parents[2] / "design-systems/scripts/check-dsfr-profile.py"
)


class ProfileContractTests(unittest.TestCase):
    def setUp(self):
        spec = importlib.util.spec_from_file_location("profile_fixture", SOURCE)
        self.module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(self.module)

    def run_profile(self, removed=None):
        read = self.module.rd

        def fixture(path):
            text = read(path)
            if path == self.module.DESIGN and removed:
                return text.replace(f'    - "{removed}"\n', "")
            return text

        with (
            patch.object(self.module, "rd", side_effect=fixture),
            patch("sys.argv", [str(SOURCE)]),
            contextlib.redirect_stdout(io.StringIO()),
            contextlib.redirect_stderr(io.StringIO()),
        ):
            return self.module.main()

    def test_current_canonical_profile_is_accepted(self):
        self.assertEqual(self.run_profile(), 0)

    def test_both_evidence_bounded_claims_are_required(self):
        for claim in (
            "aucun écart observé sur les règles DSFR exécutées",
            "écarts DSFR observés à qualifier",
        ):
            with self.subTest(claim=claim):
                self.assertEqual(self.run_profile(removed=claim), 1)


if __name__ == "__main__":
    unittest.main()
