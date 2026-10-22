"""Contrats publics des campagnes consommant un kit installé et immuable."""

# PDG-LARGE-FILE-JUSTIFICATION: une fixture Git partagée exerce le cycle installé par les CLI publiques.

import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[2]
CAMPAIGN = ".claude/skills/audit-rgaa-creator/scripts/audit_campaign.py"


def command(*args, cwd=None):
    return subprocess.run(
        [str(arg) for arg in args],
        cwd=cwd,
        capture_output=True,
        text=True,
        env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"},
        check=False,
    )


class InstalledCampaignTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.scratch = tempfile.TemporaryDirectory(prefix="dsfr-distribution-")
        cls.addClassCleanup(cls.scratch.cleanup)
        cls.source = Path(cls.scratch.name) / "source"
        cls.source.mkdir()
        paths = command(
            "git", "ls-files", "--cached", "--others", "--exclude-standard", cwd=ROOT
        )
        assert paths.returncode == 0, paths.stderr
        for name in paths.stdout.splitlines():
            source = ROOT / name
            if source.is_file():
                dest = cls.source / name
                dest.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(source, dest)
        assert command("git", "init", "-q", cwd=cls.source).returncode == 0
        assert command("git", "add", "--all", cwd=cls.source).returncode == 0
        result = command(
            "git",
            "-c",
            "user.name=fixture",
            "-c",
            "user.email=fixture@localhost",
            "commit",
            "-qm",
            "fixture A",
            cwd=cls.source,
        )
        assert result.returncode == 0, result.stderr
        cls.commit_a = command(
            "git", "rev-parse", "HEAD", cwd=cls.source
        ).stdout.strip()
        result = command(
            sys.executable,
            cls.source / "scripts/verify-kit-lock.py",
            "create",
            "--source",
            cls.source,
            "--commit",
            cls.commit_a,
            "--repository",
            "fixture-local",
        )
        assert result.returncode == 0, result.stderr
        cls.lock_a = result.stdout

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(dir=self.scratch.name)
        self.addCleanup(self.temp.cleanup)
        self.base = Path(self.temp.name)
        self.cache = self.base / "cache-A"
        shutil.copytree(self.source, self.cache, ignore=shutil.ignore_patterns(".git"))
        self.project = self.base / "campaign"
        self.seed = self.base / "trusted.lock"
        self.seed.write_text(self.lock_a)

    def cli(self, *args, cache=None):
        return command(sys.executable, (cache or self.cache) / CAMPAIGN, *args)

    def init(self):
        result = self.cli(
            "init",
            "https://example.test/",
            "--output",
            self.project,
            "--kit-lock",
            self.seed,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        return self.project / "campaign.yaml"

    def snapshot(self):
        return {
            p.relative_to(self.project).as_posix(): hashlib.sha256(
                p.read_bytes()
            ).hexdigest()
            for p in self.project.rglob("*")
            if p.is_file()
        }

    def test_installed_init_records_identity_and_report_runs(self):
        config = self.init()
        self.assertEqual(
            json.loads((self.project / "kit.lock").read_text())["commit"], self.commit_a
        )
        result = self.cli("report", config)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertTrue((self.project / "PORTAIL-AUDITS.html").is_file())

    def test_direct_python_protects_child_imports_and_campaign_reuse(self):
        config = self.init()
        before = {p.relative_to(self.cache) for p in self.cache.rglob("*")}
        scripts = (self.cache / CAMPAIGN).parent
        probe = """
import runpy, sys
from pathlib import Path
scripts, log = sys.argv[1:]
sys.path.insert(0, scripts)
runner = runpy.run_path(str(Path(scripts) / 'audit_campaign.py'))
code, out, err = runner['run_command'](
    [sys.executable, '-c', 'import sys; sys.path.insert(0, sys.argv[1]); import navigation, browser_launch', scripts],
    Path(log),
)
assert code == 0, err
"""
        env = dict(os.environ)
        env.pop("PYTHONDONTWRITEBYTECODE", None)
        result = subprocess.run(
            [
                sys.executable,
                "-c",
                probe,
                str(scripts),
                str(self.project / "logs/child.json"),
            ],
            env=env,
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(
            {p.relative_to(self.cache) for p in self.cache.rglob("*")}, before
        )
        result = self.cli("status", config)
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_git_clone_preserves_ignored_data_but_checks_product(self):
        clone = self.base / "clone"
        shutil.copytree(self.source, clone)
        local = clone / ".env.local"
        local.write_text("DSFR_PROJECT_TEST=1\n")
        (clone / "archives").mkdir()
        (clone / "archives/local.txt").write_text("Livrable à préserver.\n")
        result = self.cli(
            "init",
            "https://example.test/",
            "--output",
            self.project,
            cache=clone,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        config = self.project / "campaign.yaml"
        self.assertEqual(self.cli("report", config, cache=clone).returncode, 0)
        self.assertEqual(local.read_text(), "DSFR_PROJECT_TEST=1\n")
        (clone / "README.md").write_text("Produit altéré\n")
        result = self.cli("report", config, cache=clone)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("README.md", result.stderr)

    def test_installed_cache_rejects_git_ignored_extras(self):
        config = self.init()
        (self.cache / ".env.local").write_text("DSFR_PROJECT_TEST=1\n")
        result = self.cli("report", config)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn(".env.local", result.stderr)

    def test_divergence_blocks_every_campaign_command_before_writes(self):
        config = self.init()
        before = self.snapshot()
        with (self.cache / "README.md").open("a") as stream:
            stream.write("\naltération\n")
        for action in [
            "run",
            "resume",
            "report",
            "validate",
            "replan",
            "sample",
            "status",
        ]:
            with self.subTest(action=action):
                result = self.cli(action, config)
                self.assertNotEqual(result.returncode, 0)
                self.assertIn("kit.lock", result.stderr)
                self.assertEqual(self.snapshot(), before)

    def test_cache_without_seed_and_legacy_campaign_refuse_silent_adoption(self):
        result = self.cli("init", "https://example.test/", "--output", self.project)
        self.assertNotEqual(result.returncode, 0)
        self.assertFalse(self.project.exists())
        config = self.init()
        (self.project / "kit.lock").unlink()
        before = self.snapshot()
        result = self.cli("resume", config)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("kit.lock", result.stderr)
        self.assertEqual(self.snapshot(), before)
        self.assertEqual(self.cli("status", config).returncode, 0)

    def test_campaign_symlink_cannot_redirect_writes_into_product(self):
        config = self.init()
        (self.project / ".creator").rename(self.project / "saved-state")
        (self.project / ".creator").symlink_to(
            self.cache / "documentation", target_is_directory=True
        )
        before = self.snapshot()
        product_before = {
            p.relative_to(self.cache).as_posix(): hashlib.sha256(
                p.read_bytes()
            ).hexdigest()
            for p in self.cache.rglob("*")
            if p.is_file()
        }
        result = self.cli("replan", config)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("kit.lock", result.stderr)
        self.assertEqual(self.snapshot(), before)
        self.assertEqual(
            {
                p.relative_to(self.cache).as_posix(): hashlib.sha256(
                    p.read_bytes()
                ).hexdigest()
                for p in self.cache.rglob("*")
                if p.is_file()
            },
            product_before,
        )

    def test_b_refuses_a_and_a_preserves_qualification_after_b(self):
        config = self.init()
        qualification = self.project / "qualification.json"
        data = json.loads(qualification.read_text())
        data["criteria"]["1.1"]["comment"] = "Qualification synthétique à préserver."
        qualification.write_text(json.dumps(data))
        before = self.snapshot()
        source_b = self.base / "source-B"
        shutil.copytree(self.source, source_b)
        with (source_b / "README.md").open("a") as stream:
            stream.write("\nVersion B de la fixture.\n")
        self.assertEqual(command("git", "add", "README.md", cwd=source_b).returncode, 0)
        result = command(
            "git",
            "-c",
            "user.name=fixture",
            "-c",
            "user.email=fixture@localhost",
            "commit",
            "-qm",
            "fixture B",
            cwd=source_b,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        cache_b = self.base / "cache-B"
        shutil.copytree(source_b, cache_b, ignore=shutil.ignore_patterns(".git"))
        result = self.cli("resume", config, cache=cache_b)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("kit.lock", result.stderr)
        self.assertEqual(self.snapshot(), before)
        result = self.cli("report", config)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(
            self.snapshot()["qualification.json"], before["qualification.json"]
        )
        self.assertEqual(self.snapshot()["kit.lock"], before["kit.lock"])

    def test_internal_symlink_and_old_escape_flag_are_rejected(self):
        link = self.base / "linked-kit"
        link.symlink_to(self.cache, target_is_directory=True)
        for output, extra in [
            (self.cache / "campaign", []),
            (link / "campaign", []),
            (self.cache / "campaign", ["--allow-inside-kit"]),
        ]:
            result = self.cli(
                "init",
                "https://example.test/",
                "--output",
                output,
                "--kit-lock",
                self.seed,
                *extra,
            )
            self.assertNotEqual(result.returncode, 0)
            self.assertFalse((self.cache / "campaign").exists())

    def test_prepare_fetches_objects_then_verifies_before_writing(self):
        project = self.base / "project"
        project.mkdir()
        prepare = self.source / "scripts/prepare-kit-lock.py"
        args = [
            sys.executable,
            prepare,
            "--repository",
            self.source,
            "--commit",
            self.commit_a,
            "--kit-root",
            self.cache,
            "--project-root",
            project,
        ]
        result = command(*args)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(
            json.loads((project / "kit.lock").read_text())["commit"], self.commit_a
        )
        (project / "kit.lock").unlink()
        (self.cache / "unexpected").write_text("divergent")
        result = command(*args)
        self.assertNotEqual(result.returncode, 0)
        self.assertFalse((project / "kit.lock").exists())

    def test_marketplace_exposes_18_and_17_from_same_source(self):
        result = command(
            sys.executable, ROOT / "scripts/build-marketplace.py", "--check"
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        catalog = json.loads((ROOT / ".claude-plugin/marketplace.json").read_text())
        full, light = catalog["plugins"]
        self.assertEqual(full["source"], light["source"])
        self.assertEqual(len(light["skills"]), 17)
        self.assertNotIn("./.claude/skills/agentic-design-harness", light["skills"])
        self.assertEqual(full["skills"], ["./.claude/skills"])
        self.assertEqual(len(list((ROOT / ".claude/skills").glob("*/SKILL.md"))), 18)

    def test_pack_check_uses_target_profiles_when_caller_diverges(self):
        caller, target = self.base / "caller", self.base / "target"
        for checkout in (caller, target):
            for relative in (
                "scripts/check-agentic-design-pack.sh",
                "scripts/build-marketplace.py",
                "scripts/lib/python-with-pyyaml.sh",
                "config/agentic-design-packages.yaml",
                "config/distribution-profiles.json",
                ".claude-plugin/marketplace.json",
            ):
                dest = checkout / relative
                dest.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(ROOT / relative, dest)
        # Seuls les contrôles annexes sont remplacés ; le contrôle des profils
        # et le catalogue utilisent les vrais scripts et des checkouts distincts.
        for relative in (
            "scripts/tests/check-standalone-boundary.sh",
            "scripts/check-prerequisites.sh",
            "scripts/check-accents.sh",
            "scripts/check-dsfr-design-system.sh",
            "scripts/tests/fixture.sh",
        ):
            dest = caller / relative
            dest.parent.mkdir(parents=True, exist_ok=True)
            dest.write_text("#!/bin/bash\nexit 0\n")
        (target / "scripts/tests").mkdir()
        shutil.copy2(
            caller / "scripts/tests/fixture.sh", target / "scripts/tests/fixture.sh"
        )
        (target / "README.md").write_text("# Cible de vérification\n")
        path = target / "config/agentic-design-packages.yaml"
        manifest = yaml.safe_load(path.read_text())
        manifest["product"]["required_paths"] = ["README.md"]
        manifest["validation"] = {
            "product_tests": ["scripts/tests/fixture.sh"],
            "markdown": ["README.md"],
        }
        path.write_text(yaml.safe_dump(manifest, allow_unicode=True))
        path = caller / ".claude-plugin/marketplace.json"
        catalog = json.loads(path.read_text())
        catalog["plugins"][1]["skills"] = []
        path.write_text(json.dumps(catalog))
        result = command(
            sys.executable, caller / "scripts/build-marketplace.py", "--check"
        )
        self.assertNotEqual(result.returncode, 0)
        result = command(
            "bash",
            caller / "scripts/check-agentic-design-pack.sh",
            target,
            "--stop-after-product-tests",
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)


if __name__ == "__main__":
    unittest.main()
