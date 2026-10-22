"""Réception du consommateur DSFR avec Git local, sans données réelles."""

import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
BOOTSTRAP = ROOT / "scripts/use-dsfr-kit.py"
VERIFIER = ROOT / "scripts/verify-kit-lock.py"


def run(*args, cwd=None):
    return subprocess.run(
        [str(a) for a in args],
        cwd=cwd,
        text=True,
        capture_output=True,
        check=False,
        env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"},
    )


class ConsumerTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.base = Path(self.temp.name)
        self.source, self.workspace, self.cache = (
            self.base / x for x in ("source", "workspace", "cache")
        )
        for path in (self.source / "scripts", self.workspace / "config"):
            path.mkdir(parents=True)
        shutil.copy2(VERIFIER, self.source / "scripts/verify-kit-lock.py")
        (self.source / "scripts/hello.py").write_text(
            "import sys, library; print('A', sys.dont_write_bytecode, *sys.argv[1:])\n"
        )
        (self.source / "scripts/library.py").write_text("VALUE = 'fixture'\n")
        self.assertEqual(run("git", "init", "-q", cwd=self.source).returncode, 0)
        self.pin()

    def pin(self):
        self.assertEqual(run("git", "add", "--all", cwd=self.source).returncode, 0)
        result = run(
            "git",
            "-c",
            "user.name=fixture",
            "-c",
            "user.email=fixture@localhost",
            "commit",
            "-qm",
            "fixture",
            cwd=self.source,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        commit = run("git", "rev-parse", "HEAD", cwd=self.source).stdout.strip()
        result = run(
            sys.executable,
            "-B",
            VERIFIER,
            "create",
            "--source",
            self.source,
            "--commit",
            commit,
            "--repository",
            self.source,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        (self.workspace / "config/dsfr-kit.lock").write_text(result.stdout)
        (self.workspace / "config/dsfr-consumer.json").write_text(
            json.dumps(
                {
                    "schema_version": 1,
                    "repository": str(self.source),
                    "commit": commit,
                    "profile": "complete",
                    "lock": "config/dsfr-kit.lock",
                }
            )
        )
        return commit

    def cli(self, *args):
        return run(
            sys.executable,
            "-B",
            BOOTSTRAP,
            "--workspace",
            self.workspace,
            "--cache-root",
            self.cache,
            *args,
        )

    def test_install_execute_and_reject_divergence_before_execution(self):
        result = self.cli("--exec", "scripts/hello.py", "--", "argument")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout.strip(), "A True argument")
        kit = (self.workspace / ".dsfr-kit").resolve()
        self.assertFalse((kit / ".git").exists())
        (kit / "scripts/verify-kit-lock.py").chmod(0o644)
        (kit / "scripts/verify-kit-lock.py").write_text("raise SystemExit(0)\n")
        result = self.cli("--exec", "scripts/hello.py")
        self.assertNotEqual(result.returncode, 0)
        self.assertNotIn("A True", result.stdout)
        self.assertEqual((self.workspace / ".dsfr-kit").resolve(), kit)

    def test_non_symlink_binding_is_preserved(self):
        binding = self.workspace / ".dsfr-kit"
        binding.mkdir()
        (binding / "keep").write_text("préserver")
        result = self.cli()
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual((binding / "keep").read_text(), "préserver")

    def test_direct_import_cannot_add_bytecode_to_cache(self):
        self.assertEqual(self.cli().returncode, 0)
        kit = (self.workspace / ".dsfr-kit").resolve()
        env = dict(os.environ)
        env.pop("PYTHONDONTWRITEBYTECODE", None)
        result = subprocess.run(
            [sys.executable, str(kit / "scripts/hello.py")],
            env=env,
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertFalse(list(kit.rglob("__pycache__")))
        self.assertEqual(self.cli().returncode, 0)

    def test_b_preserves_a_and_project_qualification(self):
        self.assertEqual(self.cli().returncode, 0)
        a = (self.workspace / ".dsfr-kit").resolve()
        original = (a / "scripts/hello.py").read_bytes()
        qualification = self.workspace / "qualification.json"
        qualification.write_text('{"decision":"humaine"}')
        before = qualification.read_bytes()
        (self.source / "scripts/hello.py").write_text("print('B')\n")
        self.pin()
        result = self.cli("--exec", "scripts/hello.py")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout.strip(), "B")
        self.assertNotEqual((self.workspace / ".dsfr-kit").resolve(), a)
        self.assertEqual((a / "scripts/hello.py").read_bytes(), original)
        self.assertEqual(qualification.read_bytes(), before)

    def test_branch_name_cannot_replace_pin(self):
        path = self.workspace / "config/dsfr-consumer.json"
        config = json.loads(path.read_text())
        config["commit"] = "main"
        path.write_text(json.dumps(config))
        self.assertNotEqual(self.cli().returncode, 0)
        self.assertFalse((self.workspace / ".dsfr-kit").exists())

    def test_concurrent_preparations_share_the_verified_winner(self):
        with ThreadPoolExecutor(max_workers=8) as pool:
            results = list(pool.map(lambda _: self.cli(), range(8)))
        self.assertEqual(
            [r.returncode for r in results],
            [0] * 8,
            "\n".join(r.stderr for r in results),
        )
        self.assertEqual(self.cli().returncode, 0)

    def test_host_metadata_symlink_does_not_change_external_permissions(self):
        self.assertEqual(self.cli().returncode, 0)
        kit = (self.workspace / ".dsfr-kit").resolve()
        outside = self.base / "external"
        outside.mkdir(mode=0o755)
        before = outside.stat().st_mode & 0o777
        kit.chmod(0o755)
        (kit / ".in_use").symlink_to(outside, target_is_directory=True)
        self.assertEqual(self.cli().returncode, 0)
        self.assertEqual(outside.stat().st_mode & 0o777, before)


if __name__ == "__main__":
    unittest.main()
