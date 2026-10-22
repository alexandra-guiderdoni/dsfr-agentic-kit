"""Réutiliser le contrat kit.lock avant toute écriture d’une campagne."""

import importlib.util
import json
import subprocess
import tempfile
from pathlib import Path


def verifier(root: Path):
    spec = importlib.util.spec_from_file_location(
        "dsfr_kit_lock", root / "scripts/verify-kit-lock.py"
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def outside(root: Path, project: Path) -> None:
    root, project = root.resolve(), project.resolve()
    if root == project or root in project.parents or project in root.parents:
        raise ValueError("cache du kit et campagne doivent être disjoints")


def initial_lock(root: Path, project: Path, seed: str | None) -> dict:
    outside(root, project)
    check = verifier(root)
    if seed:
        lock = json.loads(Path(seed).expanduser().read_text(encoding="utf-8"))
    elif (root / ".git").exists():
        commit = check.git(root, "rev-parse", "HEAD").decode().strip()
        authority = json.loads((root / "config/product-authority.json").read_text())
        repository = "git@github.com:" + authority["canonical_repository"] + ".git"
        lock = check.create(root, commit, repository, None)
    else:
        raise ValueError(
            "cache sans identité : fournir --kit-lock issu de confiance ; "
            "scripts/prepare-kit-lock.py prépare ce verrou sur un commit explicite"
        )
    # Le dossier de campagne n’existe pas encore. Vérifier les octets sans
    # y créer une sortie, puis écrire son verrou seulement après ce contrôle.
    with tempfile.TemporaryDirectory(prefix="dsfr-identity-") as temporary:
        check.verify(lock, root, Path(temporary))
    return lock


def verify_campaign(root: Path, project: Path, *, required: bool = True) -> None:
    outside(root, project)
    project = project.resolve()
    for entry in project.rglob("*"):
        if entry.is_symlink():
            try:
                target = entry.resolve()
            except RuntimeError as error:
                raise ValueError("lien de campagne non résoluble") from error
            if target != project and project not in target.parents:
                raise ValueError(
                    "lien de campagne hors de sa racine : "
                    + entry.relative_to(project).as_posix()
                )
    lock_path = project / "kit.lock"
    if not lock_path.is_file():
        if not required:
            return
        raise ValueError(
            "kit.lock absent : campagne historique non adoptée automatiquement ; "
            "identifier et vérifier son kit d’origine avant toute reprise"
        )
    lock = json.loads(lock_path.read_text(encoding="utf-8"))
    verifier(root).verify(lock, root, project)


IDENTITY_ERRORS = (ValueError, OSError, subprocess.CalledProcessError)
