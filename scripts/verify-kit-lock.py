"""Créer un verrou depuis un commit Git ou vérifier un cache sans le modifier."""

# PDG-LARGE-FILE-JUSTIFICATION: CLI unique du contrat, création et comparaison partagent l’inventaire.

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import subprocess
import sys
from pathlib import Path, PurePosixPath

ALGORITHM = "sha256-files-v1"
HOST_METADATA = {".git", ".in_use", ".orphaned_at"}
CODEX_MANIFEST = ".codex-plugin/plugin.json"
CODEX_CATALOG = ".agents/plugins/marketplace.json"


def git(root: Path, *args: str) -> bytes:
    return subprocess.check_output(
        ["git", "-C", str(root), *args], stderr=subprocess.PIPE
    )


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def fingerprint(files: dict) -> str:
    return digest(
        json.dumps(
            files, sort_keys=True, separators=(",", ":"), ensure_ascii=True
        ).encode()
    )


def valid_relative(value: str) -> bool:
    entry = PurePosixPath(value)
    return (
        bool(value)
        and entry.as_posix() == value
        and not entry.is_absolute()
        and all(part not in {".", ".."} for part in entry.parts)
        and "\\" not in value
        and not any(ord(char) < 32 for char in value)
    )


def validate(lock: dict) -> None:
    if not isinstance(lock, dict) or lock.get("schema_version") != 1:
        raise ValueError("schema_version doit valoir 1")
    if not isinstance(lock.get("repository"), str) or not lock["repository"].strip():
        raise ValueError("repository obligatoire")
    if not re.fullmatch(r"[0-9a-f]{40}", str(lock.get("commit", ""))):
        raise ValueError("commit Git complet obligatoire")
    if lock.get("algorithm") != ALGORITHM:
        raise ValueError("algorithme inconnu")
    if "tag" in lock and not isinstance(lock["tag"], str):
        raise ValueError("tag facultatif : chaîne attendue")
    files = lock.get("files")
    if not isinstance(files, dict) or not files:
        raise ValueError("inventaire de fichiers obligatoire")
    for rel, entry in files.items():
        if not valid_relative(rel) or PurePosixPath(rel).parts[0] in HOST_METADATA:
            raise ValueError("chemin interdit dans le verrou")
        if not isinstance(entry, dict) or not re.fullmatch(
            r"[0-9a-f]{64}", str(entry.get("sha256", ""))
        ):
            raise ValueError("empreinte de fichier invalide")
        if not isinstance(entry.get("executable"), bool):
            raise ValueError("mode exécutable invalide")  # noqa: TRY004
    if lock.get("fingerprint") != fingerprint(files):
        raise ValueError("empreinte de l’inventaire divergente")


def create(root: Path, commit: str, repository: str, tag: str | None) -> dict:
    if not re.fullmatch(r"[0-9a-f]{40}", commit):
        raise ValueError("fournir un commit complet, jamais une branche")
    if git(root, "rev-parse", commit + "^{commit}").decode().strip() != commit:
        raise ValueError("commit non résolu")
    files = {}
    # Lire les objets, y compris ceux exclus d’un export par .gitattributes.
    for record in git(root, "ls-tree", "-rz", "--full-tree", commit).split(b"\0"):
        if not record:
            continue
        header, name = record.split(b"\t", 1)
        mode, kind, object_id = header.decode().split()
        if kind != "blob" or mode not in {"100644", "100755"}:
            raise ValueError("liens et sous-modules non pris en charge")
        files[name.decode()] = {
            "sha256": digest(git(root, "cat-file", "blob", object_id)),
            "executable": mode == "100755",
        }
    lock = {
        "schema_version": 1,
        "repository": repository,
        "commit": commit,
        "algorithm": ALGORITHM,
        "fingerprint": fingerprint(files),
        "files": files,
    }
    if tag is not None:
        if (
            git(root, "rev-parse", "--verify", "refs/tags/" + tag + "^{commit}")
            .decode()
            .strip()
            != commit
        ):
            raise ValueError("le tag ne désigne pas le commit")
        lock["tag"] = tag
    validate(lock)
    return lock


def codex_host_manifest(lock: dict, root: Path) -> set[str]:
    """Reconnaître seulement le manifeste natif dérivé du catalogue verrouillé."""
    manifest = root / CODEX_MANIFEST
    if CODEX_MANIFEST in lock["files"] or not manifest.exists():
        return set()
    catalog = root / CODEX_CATALOG
    expected = lock["files"].get(CODEX_CATALOG)
    if (
        manifest.is_symlink()
        or not manifest.is_file()
        or manifest.stat().st_mode & 0o111
        or catalog.is_symlink()
        or not catalog.is_file()
        or expected is None
        or digest(catalog.read_bytes()) != expected["sha256"]
    ):
        raise ValueError("métadonnées Codex non vérifiées")
    candidates = []
    for plugin in json.loads(catalog.read_text())["plugins"]:
        candidates.append(
            {
                key: plugin[key]
                for key in ("description", "strict", "skills", "name", "category")
            }
            | {"interface": {"category": plugin["category"]}}
        )
    actual = json.dumps(json.loads(manifest.read_text()), sort_keys=True)
    if actual not in {
        json.dumps(candidate, sort_keys=True) for candidate in candidates
    }:
        raise ValueError("métadonnées Codex divergentes")
    return {CODEX_MANIFEST}


def verify(
    lock: dict, root: Path, project: Path, *, allow_git_ignored: bool = False
) -> None:
    validate(lock)
    root, project = root.resolve(), project.resolve()
    if root == project or root in project.parents or project in root.parents:
        raise ValueError("cache du kit et projet doivent être disjoints")
    if not root.is_dir() or not project.is_dir():
        raise ValueError("kit et projet existants obligatoires")
    ignored = set()
    if (root / ".git").exists():
        if (
            Path(git(root, "rev-parse", "--show-toplevel").decode().strip()).resolve()
            != root
        ):
            raise ValueError("racine Git incorrecte")
        if git(root, "rev-parse", "HEAD").decode().strip() != lock["commit"]:
            raise ValueError("commit du cache divergent")
        if allow_git_ignored:
            ignored = {
                name.decode()
                for name in git(
                    root,
                    "ls-files",
                    "--others",
                    "--ignored",
                    "--exclude-standard",
                    "-z",
                ).split(b"\0")
                if name
            } - set(lock["files"])
    host_files = codex_host_manifest(lock, root)
    actual = set()
    for directory, dirs, names in os.walk(root, followlinks=False):
        base = Path(directory)
        if base == root:
            dirs[:] = [name for name in dirs if name not in HOST_METADATA]
            names = [name for name in names if name not in HOST_METADATA]
        for name in dirs:
            entry = base / name
            if entry.is_symlink() and entry.relative_to(root).as_posix() not in ignored:
                raise ValueError("lien symbolique interdit dans le produit")
        for name in names:
            entry = base / name
            rel = entry.relative_to(root).as_posix()
            if rel in ignored:
                continue
            if entry.is_symlink() or not entry.is_file():
                raise ValueError("fichier produit non régulier")
            if rel in host_files:
                continue
            actual.add(rel)
            expected = lock["files"].get(rel)
            if expected is None or expected != {
                "sha256": digest(entry.read_bytes()),
                "executable": bool(entry.stat().st_mode & 0o111),
            }:
                raise ValueError(f"empreinte divergente : {rel}")
    if actual != set(lock["files"]):
        raise ValueError("inventaire divergent : fichier manquant")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    build = commands.add_parser("create", help="écrit le verrou JSON sur stdout")
    build.add_argument("--source", type=Path, required=True)
    build.add_argument("--commit", required=True)
    build.add_argument("--repository", required=True)
    build.add_argument("--tag")
    check = commands.add_parser("verify", help="lecture seule, aucun téléchargement")
    check.add_argument("--lock", type=Path, required=True)
    check.add_argument("--kit-root", type=Path, required=True)
    check.add_argument("--project-root", type=Path, required=True)
    args = parser.parse_args()
    try:
        if args.command == "create":
            lock = create(args.source.resolve(), args.commit, args.repository, args.tag)
            print(json.dumps(lock, indent=2, sort_keys=True, ensure_ascii=False))
        else:
            lock = json.loads(args.lock.read_text(encoding="utf-8"))
            verify(lock, args.kit_root.resolve(), args.project_root.resolve())
            print(f"[OK] kit vérifié : {lock['commit']} {lock['fingerprint']}")
        return 0
    except (
        ValueError,
        OSError,
        subprocess.CalledProcessError,
    ) as error:
        detail = (
            "commande Git refusée"
            if isinstance(error, subprocess.CalledProcessError)
            else str(error)
        )
        print(f"[FAIL] kit.lock : {detail}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
