"""Résolution sûre des chemins d’écriture des pipelines Virginie.

Le clone du kit porte le code et les références ; le projet de travail porte
les archives, les livrables et les verrous d’exécution. Toute destination
d’écriture est résolue avant le premier effet de bord et doit rester sous la
racine du projet, qui doit elle-même être distincte du clone du kit.
"""

from __future__ import annotations

import os
from pathlib import Path

KIT_ROOT = Path(__file__).resolve().parents[2]
PROJECT_ROOT_ENV = "DSFR_PROJECT_ROOT"


def is_within(path: Path, root: Path) -> bool:
    """Indique si *path* est *root* ou un de ses descendants."""
    return path == root or root in path.parents


def require_project_root(
    value: Path | str | None = None, *, kit_root: Path = KIT_ROOT
) -> Path:
    """Retourne une racine de projet existante et distincte du kit."""
    raw_value = value if value is not None else os.environ.get(PROJECT_ROOT_ENV)
    if not raw_value:
        raise SystemExit(
            "Projet de travail obligatoire : fournir --project-root ou définir "
            f"{PROJECT_ROOT_ENV}. Les livrables ne sont jamais écrits dans le kit."
        )

    project_root = Path(raw_value).expanduser().resolve(strict=False)
    if not project_root.is_dir():
        raise SystemExit(
            f"Projet de travail inexistant ou non accessible : {project_root}"
        )

    resolved_kit = kit_root.expanduser().resolve(strict=False)
    if is_within(project_root, resolved_kit):
        raise SystemExit(
            "Projet de travail interdit : sa résolution se trouve dans le clone "
            f"du kit ({resolved_kit})."
        )
    return project_root


def safe_write_path(
    path: Path | str,
    *,
    project_root: Path,
    kit_root: Path = KIT_ROOT,
    label: str,
) -> Path:
    """Résout une destination et refuse le kit ou la sortie du projet."""
    resolved = Path(path).expanduser().resolve(strict=False)
    resolved_project = project_root.expanduser().resolve(strict=False)
    resolved_kit = kit_root.expanduser().resolve(strict=False)

    if is_within(resolved, resolved_kit):
        raise SystemExit(
            f"Destination d’écriture interdite pour {label} : {resolved} "
            f"résout dans le clone du kit ({resolved_kit})."
        )
    if not is_within(resolved, resolved_project):
        raise SystemExit(
            f"Destination d’écriture interdite pour {label} : {resolved} "
            f"doit rester sous le projet ({resolved_project})."
        )
    return resolved


def safe_pipeline_lock(project_root: Path, *, kit_root: Path = KIT_ROOT) -> Path:
    """Retourne le verrou partagé placé dans le projet de travail."""
    return safe_write_path(
        project_root / ".dsfr-kit-pipeline.lock",
        project_root=project_root,
        kit_root=kit_root,
        label="verrou partagé",
    )
