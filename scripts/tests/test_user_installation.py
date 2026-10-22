"""Réception locale de l’installation, des conflits et du retour arrière."""

import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


class InstallationTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.base = Path(self.temp.name)
        self.source = self.base / "source"
        self.home = self.base / "home"
        self.prefix = self.home / ".local/share/dsfr-agentic-kit"
        self.cache = self.home / ".cache/dsfr-agentic-kit"
        (self.source / "scripts").mkdir(parents=True)
        (self.source / "config").mkdir()
        for name in ("use-dsfr-kit.py", "verify-kit-lock.py", "install-user.py"):
            shutil.copy2(ROOT / "scripts" / name, self.source / "scripts" / name)
        for name in ("dsfr-components", "agentic-design-harness"):
            path = self.source / ".claude/skills" / name / "SKILL.md"
            path.parent.mkdir(parents=True)
            path.write_text(f"---\nname: {name}\ndescription: Fixture\n---\n")
        (self.source / "config/distribution-profiles.json").write_text(
            json.dumps(
                {
                    "profiles": {
                        "complete": {"excluded_skills": []},
                        "light": {"excluded_skills": ["agentic-design-harness"]},
                    }
                }
            )
        )
        (self.source / "scripts/hello.py").write_text("print('A')\n")
        self.command("git", "init", "-q", str(self.source))
        self.pin()

    def command(self, *args):
        result = subprocess.run(
            list(map(str, args)), capture_output=True, text=True, check=False
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        return result.stdout.strip()

    def pin(self):
        self.command("git", "-C", self.source, "add", ".")
        self.command(
            "git",
            "-C",
            self.source,
            "-c",
            "user.name=fixture",
            "-c",
            "user.email=fixture@localhost",
            "commit",
            "-qm",
            "fixture",
        )
        self.commit = self.command("git", "-C", self.source, "rev-parse", "HEAD")

    def cli(self, action="install", *args):
        command = [
            sys.executable,
            "-B",
            str(ROOT / "scripts/install-user.py"),
            action,
            "--home",
            str(self.home),
        ]
        if action == "install":
            command += ["--repository", str(self.source), "--commit", self.commit]
        return subprocess.run(
            [*command, *args], capture_output=True, text=True, check=False
        )

    def execute(self, *args):
        return self.command(
            sys.executable,
            "-B",
            self.prefix / "current/scripts/use-dsfr-kit.py",
            "--cache-root",
            self.cache,
            "--exec",
            "scripts/hello.py",
            "--",
            *args,
        )

    def test_adoption_is_explicit_and_rollback_restores_original_directory(self):
        original = self.home / ".codex/skills/dsfr-components"
        original.mkdir(parents=True)
        (original / "SKILL.md").write_text("ancienne enveloppe")
        self.assertNotEqual(self.cli().returncode, 0)
        self.assertFalse((self.prefix / "current").exists())
        self.assertEqual((original / "SKILL.md").read_text(), "ancienne enveloppe")
        result = self.cli("install", "--adopt-existing")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertTrue(original.is_symlink())
        self.assertEqual(self.execute(), "A")
        result = self.cli("rollback")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertFalse(original.is_symlink())
        self.assertEqual((original / "SKILL.md").read_text(), "ancienne enveloppe")

    def test_update_and_rollback_preserve_version_and_human_qualification(self):
        self.assertEqual(self.cli().returncode, 0)
        previous = (self.prefix / "current").resolve()
        product_a = (previous / ".dsfr-kit").resolve()
        qualification = self.base / "qualification.json"
        qualification.write_text('{"decision":"humaine"}')
        before = qualification.read_bytes()
        (self.source / "scripts/hello.py").write_text("print('B')\n")
        self.pin()
        self.assertEqual(self.cli().returncode, 0)
        self.assertEqual(self.execute(), "B")
        self.assertEqual((product_a / "scripts/hello.py").read_text(), "print('A')\n")
        self.assertEqual(self.cli("rollback").returncode, 0)
        self.assertEqual(self.execute(), "A")
        self.assertEqual(qualification.read_bytes(), before)

    def test_light_upgrade_hides_owned_core_and_rollback_restores_it(self):
        self.assertEqual(self.cli().returncode, 0)
        core = self.home / ".agents/skills/agentic-design-harness"
        self.assertTrue(core.is_symlink())
        result = self.cli("install", "--profile", "light")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertFalse(core.is_symlink())
        self.assertEqual(self.cli("rollback").returncode, 0)
        self.assertTrue(core.is_symlink())

    def test_cache_tampering_is_refused_before_entry_execution(self):
        self.assertEqual(self.cli().returncode, 0)
        entry = self.prefix / "current/.dsfr-kit/scripts/hello.py"
        entry.chmod(0o644)
        entry.write_text("print('COMPROMIS')\n")
        result = subprocess.run(
            [
                sys.executable,
                "-B",
                str(self.prefix / "current/scripts/use-dsfr-kit.py"),
                "--exec",
                "scripts/hello.py",
            ],
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertNotEqual(result.returncode, 0)
        self.assertNotIn("COMPROMIS", result.stdout)

    def test_rollback_refuses_to_overwrite_later_user_edits(self):
        self.assertEqual(self.cli().returncode, 0)
        entry = self.home / ".claude/skills/dsfr-components"
        entry.unlink()
        entry.mkdir()
        (entry / "keep").write_text("travail utilisateur")
        self.assertNotEqual(self.cli("rollback").returncode, 0)
        self.assertEqual((entry / "keep").read_text(), "travail utilisateur")

    def test_update_keeps_workspace_binding_and_other_skills_from_another_cwd(self):
        workspace = self.base / "workflow avec espaces"
        workspace.mkdir()
        other = self.home / ".agents/skills/other/SKILL.md"
        other.parent.mkdir(parents=True)
        other.write_text("à conserver")
        result = self.cli("install", "--bind-workspace", str(workspace))
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(self.cli().returncode, 0)
        self.assertTrue((workspace / ".dsfr-kit").is_symlink())
        result = subprocess.run(
            [str(self.home / ".local/bin/dsfr-kit"), "--exec", "scripts/hello.py"],
            cwd=workspace,
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout.strip(), "A")
        self.assertEqual(other.read_text(), "à conserver")


if __name__ == "__main__":
    unittest.main()
