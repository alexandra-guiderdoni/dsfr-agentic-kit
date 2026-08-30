#!/usr/bin/env python3
"""Validate assembled page JSON Schema and example configs.

The check uses the real `jsonschema` implementation when available. If the
package is not installed and `uv` is available, the script re-executes itself
with an ephemeral `jsonschema` dependency.
"""

from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path


SKILL_ROOT = Path(__file__).resolve().parents[1]
# Racine de travail : le workspace hôte quand le skill est installé sous
# <racine>/.claude/skills/, sinon le dossier du skill lui-même.
WORKSPACE = SKILL_ROOT.parents[2] if len(SKILL_ROOT.parents) > 2 else SKILL_ROOT
SKILL_DIR = Path(__file__).resolve().parents[1]
DEFAULT_SCHEMA = SKILL_DIR / "schemas" / "generate_assembled_page.schema.json"
DEFAULT_EXAMPLES_DIR = SKILL_DIR / "examples" / "assembled"
DEFAULT_FIXTURE_EXAMPLES_DIR = SKILL_DIR / "examples" / "assembled-fixtures"
DEFAULT_INVALID_EXAMPLES_DIR = SKILL_DIR / "examples" / "assembled-invalid"
BUILDER_SCRIPT = SKILL_DIR / "scripts" / "generate_assembled_page.py"


def ensure_jsonschema():
    try:
        from jsonschema.validators import validator_for
    except ImportError:
        if os.environ.get("DSFR_JSONSCHEMA_UV_ACTIVE") == "1":
            print(
                "[FAIL] jsonschema unavailable after uv re-exec. "
                "Install jsonschema>=4.22,<5 or check uv configuration.",
                file=sys.stderr,
            )
            raise SystemExit(2)

        uv = shutil.which("uv")
        if uv:
            env = os.environ.copy()
            env["DSFR_JSONSCHEMA_UV_ACTIVE"] = "1"
            cmd = [
                uv,
                "run",
                "--quiet",
                "--with",
                "jsonschema>=4.22,<5",
                "python",
                str(Path(__file__).resolve()),
                *sys.argv[1:],
            ]
            if not env.get("UV_CACHE_DIR"):
                cache_owner = os.getuid() if hasattr(os, "getuid") else "user"
                uv_cache_dir = Path(tempfile.gettempdir()) / (
                    f"dsfr-agentic-packs-uv-cache-{cache_owner}"
                )
                uv_cache_dir.mkdir(parents=True, exist_ok=True, mode=0o700)
                if hasattr(os, "getuid") and uv_cache_dir.stat().st_uid != os.getuid():
                    print(f"[FAIL] uv cache {uv_cache_dir} owned by another user: set UV_CACHE_DIR", file=sys.stderr)
                    raise SystemExit(2)
                env["UV_CACHE_DIR"] = str(uv_cache_dir)
            try:
                result = subprocess.run(cmd, cwd=WORKSPACE, env=env, timeout=600)
            except subprocess.TimeoutExpired:
                print("[FAIL] uv re-exec timed out after 600 s", file=sys.stderr)
                raise SystemExit(2)
            raise SystemExit(result.returncode)

        print(
            "[FAIL] jsonschema unavailable and uv not found. "
            "Install jsonschema>=4.22,<5 or run with uv.",
            file=sys.stderr,
        )
        raise SystemExit(2)
    return validator_for


def rel(path: Path) -> str:
    try:
        return str(path.relative_to(WORKSPACE))
    except ValueError:
        return str(path)


def load_json(path: Path):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        print(f"[FAIL] missing file: {rel(path)}", file=sys.stderr)
        raise SystemExit(1)
    except OSError as e:
        print(f"[FAIL] unreadable file {rel(path)}: {e.strerror}", file=sys.stderr)
        raise SystemExit(1)
    except json.JSONDecodeError as e:
        print(f"[FAIL] invalid JSON in {rel(path)}: {e}", file=sys.stderr)
        raise SystemExit(1)


def iter_example_configs(examples_dir: Path) -> list[Path]:
    if not examples_dir.is_dir():
        print(f"[FAIL] examples dir missing: {rel(examples_dir)}", file=sys.stderr)
        raise SystemExit(1)
    configs = sorted(examples_dir.glob("*/page.json"))
    if not configs:
        print(f"[FAIL] no assembled page examples found in {rel(examples_dir)}", file=sys.stderr)
        raise SystemExit(1)
    return configs


def iter_fixture_configs(examples_dir: Path) -> list[Path]:
    if not examples_dir.is_dir():
        print(f"[FAIL] fixture examples dir missing: {rel(examples_dir)}", file=sys.stderr)
        raise SystemExit(1)
    configs = sorted(examples_dir.glob("*/page.json"))
    if not configs:
        print(f"[FAIL] no fixture examples found in {rel(examples_dir)} (regression cases missing)", file=sys.stderr)
        raise SystemExit(1)
    return configs


def iter_invalid_example_configs(examples_dir: Path) -> list[Path]:
    if not examples_dir.is_dir():
        print(f"[FAIL] invalid examples dir missing: {rel(examples_dir)}", file=sys.stderr)
        raise SystemExit(1)
    configs = sorted(examples_dir.glob("*/page.json"))
    if not configs:
        print(f"[FAIL] no invalid examples found in {rel(examples_dir)} (rejection cases missing)", file=sys.stderr)
        raise SystemExit(1)
    return configs


def format_jsonschema_error(path: Path, error) -> str:
    location = "/".join(str(part) for part in error.path) or "<root>"
    return f"{rel(path)}:{location}: {error.message}"


def run_builder_check(config_path: Path) -> None:
    env = os.environ.copy()
    env.setdefault("PYTHONDONTWRITEBYTECODE", "1")
    result = subprocess.run(
        [
            sys.executable,
            str(BUILDER_SCRIPT),
            "--config-file",
            str(config_path),
            "--check",
        ],
        cwd=WORKSPACE,
        env=env,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    if result.returncode != 0:
        output = (result.stdout + result.stderr).strip()
        print(f"[FAIL] builder --check failed for {rel(config_path)}", file=sys.stderr)
        if output:
            print(output, file=sys.stderr)
        raise SystemExit(1)
    # Les avertissements du builder (ex. allow_raw_html) restent visibles.
    for line in result.stderr.splitlines():
        if line.startswith("Avertissement"):
            print(f"{rel(config_path)} : {line}", file=sys.stderr)
    print(f"PASS builder {rel(config_path)}")


def run_builder_rejection_check(config_path: Path) -> None:
    env = os.environ.copy()
    env.setdefault("PYTHONDONTWRITEBYTECODE", "1")
    result = subprocess.run(
        [
            sys.executable,
            str(BUILDER_SCRIPT),
            "--config-file",
            str(config_path),
            "--check",
        ],
        cwd=WORKSPACE,
        env=env,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    output = (result.stdout + result.stderr).strip()
    if result.returncode == 0:
        print(f"[FAIL] builder accepted invalid config {rel(config_path)}", file=sys.stderr)
        if output:
            print(output, file=sys.stderr)
        raise SystemExit(1)
    # Tout rejet doit porter un message d'erreur nommé (schéma ou garde-fou HTML).
    if not ("Erreur" in output or "Error" in output):
        print(f"[FAIL] builder rejection lacks guidance for {rel(config_path)}", file=sys.stderr)
        if output:
            print(output, file=sys.stderr)
        raise SystemExit(1)
    print(f"PASS builder-rejects {rel(config_path)}")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate generate_assembled_page JSON Schema and examples"
    )
    parser.add_argument("--schema", type=Path, default=DEFAULT_SCHEMA)
    parser.add_argument("--examples-dir", type=Path, default=DEFAULT_EXAMPLES_DIR)
    parser.add_argument("--fixture-examples-dir", type=Path, default=DEFAULT_FIXTURE_EXAMPLES_DIR)
    parser.add_argument("--invalid-examples-dir", type=Path, default=DEFAULT_INVALID_EXAMPLES_DIR)
    parser.add_argument(
        "--schema-only",
        action="store_true",
        help="validate schema and examples without running generate_assembled_page.py --check",
    )
    args = parser.parse_args()
    # Chemins absolus : le builder est lancé avec cwd=WORKSPACE, un chemin relatif
    # à un autre répertoire courant ne s'y résoudrait pas.
    for name in ("schema", "examples_dir", "fixture_examples_dir", "invalid_examples_dir"):
        setattr(args, name, getattr(args, name).resolve())

    validator_for = ensure_jsonschema()
    schema = load_json(args.schema)
    Validator = validator_for(schema)
    try:
        Validator.check_schema(schema)
    except Exception as e:
        print(f"[FAIL] invalid JSON Schema {rel(args.schema)}: {e}", file=sys.stderr)
        return 1
    print(f"PASS schema {rel(args.schema)}")

    validator = Validator(schema)
    configs = iter_example_configs(args.examples_dir)
    fixture_configs = iter_fixture_configs(args.fixture_examples_dir)
    failures: list[str] = []
    for config_path in [*configs, *fixture_configs]:
        config = load_json(config_path)
        errors = sorted(validator.iter_errors(config), key=lambda item: list(item.path))
        if errors:
            failures.extend(format_jsonschema_error(config_path, error) for error in errors)
            continue
        print(f"PASS schema-example {rel(config_path)}")
        if not args.schema_only:
            run_builder_check(config_path)

    invalid_configs = iter_invalid_example_configs(args.invalid_examples_dir)
    if not args.schema_only:
        for config_path in invalid_configs:
            run_builder_rejection_check(config_path)

    if failures:
        print(f"FAIL assembled page schema: {len(failures)} issue(s)", file=sys.stderr)
        for failure in failures:
            print(failure, file=sys.stderr)
        return 1

    builder_note = " (builder --check et rejets non exécutés : --schema-only)" if args.schema_only else ""
    print(
        "PASS assembled page schema: "
        f"examples={len(configs)} fixtures={len(fixture_configs)} invalid_examples={len(invalid_configs)}{builder_note}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
