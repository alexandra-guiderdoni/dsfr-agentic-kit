#!/usr/bin/env python3
"""Exécuter un commit DSFR vérifié depuis une installation ou un projet épinglé."""

# PDG-LARGE-FILE-JUSTIFICATION: chargeur de confiance repris sans moteur parallèle ;
# la récupération et la vérification précèdent ensemble toute exécution du produit.

import argparse
import errno
import hashlib
import importlib.util
import json
import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path

sys.dont_write_bytecode = True
os.environ["PYTHONDONTWRITEBYTECODE"] = "1"


def git(root: Path, *args: str) -> bytes:
    return subprocess.check_output(
        ["git", "-C", str(root), *args], stderr=subprocess.PIPE
    )


def bind(workspace: Path, cache_root: Path, entry: str | None) -> Path:
    config = json.loads((workspace / "config/dsfr-consumer.json").read_text())
    commit = config["commit"]
    if config.get("schema_version") != 1 or not re.fullmatch(r"[0-9a-f]{40}", commit):
        raise ValueError("configuration version 1 et commit complet obligatoires")
    if config.get("profile") not in {"complete", "light"}:
        raise ValueError("profil DSFR inconnu")
    lock_path = workspace / config["lock"]
    if not lock_path.resolve().is_relative_to(workspace):
        raise ValueError("verrou du consommateur hors workspace")
    lock = json.loads(lock_path.read_text())
    if lock["commit"] != commit or lock["repository"] != config["repository"]:
        raise ValueError("configuration et verrou divergent")
    if entry and (
        entry not in lock["files"] or Path(entry).suffix not in {".py", ".sh"}
    ):
        raise ValueError(
            "entrée absente du produit ou non exécutable par cet adaptateur"
        )
    if (
        cache_root == workspace
        or cache_root.is_relative_to(workspace)
        or workspace.is_relative_to(cache_root)
    ):
        raise ValueError("cache et workspace doivent être disjoints")
    binding = workspace / ".dsfr-kit"
    if binding.exists() and not binding.is_symlink():
        raise ValueError(".dsfr-kit existant non symbolique : remplacement interdit")
    cache = cache_root / "commits" / commit
    trusted = cache_root / "verification" / (commit + ".py")
    if any(
        path.is_symlink() for path in (cache, cache.parent, trusted, trusted.parent)
    ):
        raise ValueError("cache ou vérificateur symbolique interdit")
    expected = lock["files"]["scripts/verify-kit-lock.py"]["sha256"]
    if (
        trusted.exists()
        and hashlib.sha256(trusted.read_bytes()).hexdigest() != expected
    ):
        raise ValueError(
            "vérificateur de confiance divergent ; aucune réparation automatique"
        )
    if not cache.exists() or not trusted.exists():
        cache_root.mkdir(parents=True, exist_ok=True)
        with tempfile.TemporaryDirectory(
            prefix="dsfr-fetch-", dir=cache_root
        ) as temporary:
            source = Path(temporary) / "objects"
            subprocess.run(
                ["git", "init", "--bare", "-q", str(source)],
                check=True,
                capture_output=True,
            )
            git(source, "fetch", "--depth=1", "--", config["repository"], commit)
            if (
                git(source, "rev-parse", commit + "^{commit}").decode().strip()
                != commit
            ):
                raise ValueError("commit non résolu")
            code = git(source, "show", commit + ":scripts/verify-kit-lock.py")
            if hashlib.sha256(code).hexdigest() != expected:
                raise ValueError("vérificateur Git différent du verrou de confiance")
            trusted.parent.mkdir(parents=True, exist_ok=True)
            candidate = Path(temporary) / "verifier.py"
            candidate.write_bytes(code)
            try:
                os.link(candidate, trusted)
            except FileExistsError:
                pass  # Un autre appel a publié le même vérificateur complet.
            if hashlib.sha256(trusted.read_bytes()).hexdigest() != expected:
                raise ValueError("vérificateur concurrent différent du verrou")
            spec = importlib.util.spec_from_file_location("dsfr_trusted_lock", trusted)
            check = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(check)
            check.validate(lock)
            if (
                check.create(source, commit, config["repository"], lock.get("tag"))
                != lock
            ):
                raise ValueError("objets Git différents du verrou de confiance")
            if not cache.exists():
                staging = Path(temporary) / "product"
                staging.mkdir()
                # Lire tous les objets : git archive peut omettre export-ignore.
                for relative, identity in lock["files"].items():
                    target = staging / relative
                    target.parent.mkdir(parents=True, exist_ok=True)
                    target.write_bytes(git(source, "show", commit + ":" + relative))
                    target.chmod(0o755 if identity["executable"] else 0o644)
                check.verify(lock, staging, workspace)
                cache.parent.mkdir(parents=True, exist_ok=True)
                try:
                    staging.rename(cache)
                except OSError as error:
                    if error.errno not in {errno.EEXIST, errno.ENOTEMPTY}:
                        raise
                    if not cache.is_dir() or cache.is_symlink():
                        raise
                    # Le gagnant sera contrôlé par le vérificateur externe.
    result = subprocess.run(
        [
            sys.executable,
            "-B",
            str(trusted),
            "verify",
            "--lock",
            str(lock_path),
            "--kit-root",
            str(cache),
            "--project-root",
            str(workspace),
        ],
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode:
        raise ValueError(result.stderr.strip() or "cache DSFR divergent")
    # Éviter aussi le bytecode des imports directs hors de cet adaptateur.
    for relative, identity in lock["files"].items():
        target = cache / relative
        mode = 0o555 if identity["executable"] else 0o444
        if target.stat().st_mode & 0o777 != mode:
            target.chmod(mode)
    for directory in [
        p for p in cache.rglob("*") if not p.is_symlink() and p.is_dir()
    ] + [cache]:
        if directory.stat().st_mode & 0o777 != 0o555:
            directory.chmod(0o555)
    if not binding.is_symlink() or binding.resolve() != cache:
        staged = workspace / (".dsfr-kit.next-" + str(os.getpid()))
        staged.symlink_to(cache, target_is_directory=True)
        staged.replace(binding)
    os.environ.setdefault("DSFR_KIT_LOCK", str(lock_path))
    os.environ["DSFR_KIT_ROOT"] = str(cache)
    return cache


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--workspace", type=Path, default=Path(__file__).resolve().parents[1]
    )
    parser.add_argument(
        "--cache-root",
        type=Path,
        default=None,
    )
    parser.add_argument("--exec", dest="entry")
    parser.add_argument("args", nargs=argparse.REMAINDER)
    args = parser.parse_args()
    try:
        workspace = args.workspace.resolve()
        config = json.loads((workspace / "config/dsfr-consumer.json").read_text())
        cache_root = args.cache_root or Path(
            os.environ.get(
                "DSFR_KIT_CACHE",
                config.get("cache_root", str(Path.home() / ".cache/dsfr-agentic-kit")),
            )
        )
        cache = bind(workspace, cache_root.expanduser().resolve(), args.entry)
        if args.entry:
            forwarded = args.args[1:] if args.args[:1] == ["--"] else args.args
            command = (
                [sys.executable, "-B"] if args.entry.endswith(".py") else ["/bin/bash"]
            )
            os.execv(command[0], [*command, str(cache / args.entry), *forwarded])
        print(f"[OK] consommateur DSFR vérifié : {cache.name}")
        return 0
    except (
        ValueError,
        OSError,
        KeyError,
        TypeError,
        subprocess.CalledProcessError,
    ) as error:
        detail = (
            "récupération Git refusée"
            if isinstance(error, subprocess.CalledProcessError)
            else str(error)
        )
        print(f"[FAIL] consommateur DSFR : {detail}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
