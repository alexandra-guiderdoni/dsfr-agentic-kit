"""Contrat kit.lock : commits réels, caches natifs et refus avant génération."""

import importlib.util
import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CLI = ROOT / "scripts/verify-kit-lock.py"
SPEC = importlib.util.spec_from_file_location("kit_lock", CLI)
kit_lock = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(kit_lock)


class LockTest(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.base = Path(self.temp.name)
        self.project = self.base / "project"
        self.project.mkdir()
        self.source = self.base / "source"
        self.source.mkdir()
        self.command("git", "init", "-q", cwd=self.source)
        (self.source / "engine.py").write_text("print('A')\n")
        self.commit_a = self.commit("A")
        self.lock = kit_lock.create(self.source, self.commit_a, "fixture-local", None)
        self.cache = self.base / "cache-A"
        shutil.copytree(self.source, self.cache, ignore=shutil.ignore_patterns(".git"))
        self.lock_file = self.project / "kit.lock"
        self.lock_file.write_text(json.dumps(self.lock))

    def command(self, *args, **kwargs):
        return (
            subprocess.check_output(args, stderr=subprocess.PIPE, **kwargs)
            .decode()
            .strip()
        )

    def commit(self, message):
        self.command("git", "add", "-A", cwd=self.source)
        self.command(
            "git",
            "-c",
            "user.name=fixture",
            "-c",
            "user.email=fixture@localhost",
            "commit",
            "-qm",
            message,
            cwd=self.source,
        )
        return self.command("git", "rev-parse", "HEAD", cwd=self.source)

    def verify(self):
        kit_lock.verify(self.lock, self.cache, self.project)

    def test_native_cache_and_host_metadata(self):
        (self.cache / ".in_use").mkdir()
        (self.cache / ".in_use/host").write_text("metadata")
        (self.cache / ".orphaned_at").write_text("metadata")
        self.verify()

    def test_tampered_missing_extra_and_mode(self):
        engine = self.cache / "engine.py"
        engine.write_text("print('tampered')\n")
        with self.assertRaisesRegex(ValueError, "divergente"):
            self.verify()
        engine.unlink()
        with self.assertRaisesRegex(ValueError, "manquant"):
            self.verify()
        engine.write_text("print('A')\n")
        engine.chmod(0o755)
        with self.assertRaisesRegex(ValueError, "divergente"):
            self.verify()
        engine.chmod(0o644)
        (self.cache / "unexpected.py").write_text("print('extra')")
        with self.assertRaisesRegex(ValueError, "divergente"):
            self.verify()

    def test_symlink_and_overlapping_roots(self):
        (self.cache / "engine.py").unlink()
        (self.cache / "engine.py").symlink_to(self.source / "engine.py")
        with self.assertRaisesRegex(ValueError, "régulier"):
            self.verify()
        with self.assertRaisesRegex(ValueError, "disjoints"):
            kit_lock.verify(self.lock, self.source, self.source)

    def test_commit_pin_and_tag(self):
        with self.assertRaisesRegex(ValueError, "commit complet"):
            kit_lock.create(self.source, "main", "fixture-local", None)
        self.command("git", "tag", "version-A", cwd=self.source)
        tagged = kit_lock.create(
            self.source, self.commit_a, "fixture-local", "version-A"
        )
        self.assertEqual(tagged["tag"], "version-A")
        (self.source / "engine.py").write_text("print('B')\n")
        commit_b = self.commit("B")
        self.assertNotEqual(commit_b, self.commit_a)
        with self.assertRaisesRegex(ValueError, "tag"):
            kit_lock.create(self.source, commit_b, "fixture-local", "version-A")
        with self.assertRaisesRegex(ValueError, "commit du cache"):
            kit_lock.verify(self.lock, self.source, self.project)
        # A reste utilisable après publication locale de B dans la source.
        self.verify()
        self.assertEqual(
            self.command(sys.executable, str(self.cache / "engine.py")), "A"
        )

    def test_cli_and_corrupt_lock(self):
        command = [
            sys.executable,
            str(CLI),
            "verify",
            "--lock",
            str(self.lock_file),
            "--kit-root",
            str(self.cache),
            "--project-root",
            str(self.project),
        ]
        self.assertIn("[OK]", self.command(*command))
        self.lock["fingerprint"] = "0" * 64
        self.lock_file.write_text(json.dumps(self.lock))
        refused = subprocess.run(command, capture_output=True, text=True, check=False)
        self.assertEqual(refused.returncode, 1)
        self.assertIn("empreinte", refused.stderr)

    def test_objects_ignore_dirty_tree_and_keep_export_ignored_files(self):
        (self.source / ".gitattributes").write_text("engine.py export-ignore\n")
        commit = self.commit("attributes")
        (self.source / "engine.py").write_text("print('uncommitted')\n")
        lock = kit_lock.create(self.source, commit, "fixture-local", None)
        self.assertEqual(lock["files"]["engine.py"], self.lock["files"]["engine.py"])

    def test_committed_symlink_refused(self):
        (self.source / "link.py").symlink_to("engine.py")
        commit = self.commit("link")
        with self.assertRaisesRegex(ValueError, "liens"):
            kit_lock.create(self.source, commit, "fixture-local", None)


if __name__ == "__main__":
    unittest.main()
