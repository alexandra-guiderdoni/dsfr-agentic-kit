"""Écriture des sorties, insertion dans l'index général, empreintes et contrôles.

L'index général est régénéré par generate-virginie-rgaa-tickets.py : la carte
est insérée entre deux marqueurs et restaurée à chaque exécution, sans toucher
à ce script.
"""

from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path

from . import render_html, render_markdown
from .verdict import Report, build_manifest

INDEX_START = "<!-- dsfr-composants:debut -->"
INDEX_END = "<!-- dsfr-composants:fin -->"
FORBIDDEN_FRAGMENTS = ("/Users/", "/private/tmp/", "/home/")


def clean_generated(folder: Path, suffix: str) -> list[Path]:
    removed = []
    if folder.is_dir():
        for path in sorted(folder.glob(f"*{suffix}")):
            path.unlink()
            removed.append(path)
    return removed


def write_outputs(report: Report, output: Path) -> list[Path]:
    written: list[Path] = []
    (output / "composants").mkdir(parents=True, exist_ok=True)
    (output / "markdown").mkdir(parents=True, exist_ok=True)
    clean_generated(output / "composants", ".html")
    clean_generated(output / "markdown", ".md")

    def write(path: Path, text: str) -> None:
        path.write_text(text, encoding="utf-8")
        written.append(path)

    write(output / "INDEX-DSFR-COMPOSANTS.html", render_html.render_index(report))
    write(output / "SYNTHESE-DSFR-COMPOSANTS.md", render_markdown.render_synthese(report))
    write(output / "MANIFESTE-DSFR-COMPOSANTS.json", json.dumps(build_manifest(report), ensure_ascii=False, indent=2) + "\n")
    for name in report.components:
        write(output / "composants" / f"{name}.html", render_html.render_fiche(report, name))
        write(output / "markdown" / f"{name}.md", render_markdown.render_fiche(report, name))
    return written


def insert_index_card(index_path: Path, card: str) -> str:
    """Insère ou remplace la carte entre marqueurs. Retourne : inserted, replaced, missing, no_anchor."""
    if not index_path.is_file():
        return "missing"
    text = index_path.read_text(encoding="utf-8")
    block = f"{INDEX_START}{card}{INDEX_END}"
    if INDEX_START in text and INDEX_END in text:
        pattern = re.compile(re.escape(INDEX_START) + ".*?" + re.escape(INDEX_END), re.DOTALL)
        index_path.write_text(pattern.sub(lambda _: block, text, count=1), encoding="utf-8")
        return "replaced"
    anchor = text.find("</section>")
    if anchor < 0:
        return "no_anchor"
    index_path.write_text(text[:anchor] + "    " + block + "\n  " + text[anchor:], encoding="utf-8")
    return "inserted"


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def write_checksums(output: Path, files: list[Path]) -> Path:
    lines = [f"{sha256_file(path)}  {path.relative_to(output).as_posix()}" for path in sorted(files)]
    target = output / "SHA256SUMS"
    target.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return target


def verify_outputs(files: list[Path], known_classes: set[str] | None) -> list[str]:
    errors: list[str] = []
    for path in files:
        text = path.read_text(encoding="utf-8")
        for fragment in FORBIDDEN_FRAGMENTS:
            if fragment in text:
                errors.append(f"{path.name} : chemin local « {fragment} » présent")
        if path.suffix == ".html":
            if 'lang="fr"' not in text or 'id="contenu"' not in text:
                errors.append(f"{path.name} : structure HTML incomplète (lang ou main)")
            if known_classes is not None:
                unknown = [c for c in render_html.dsfr_classes(text) if c not in known_classes]
                if unknown:
                    errors.append(f"{path.name} : classes absentes de DSFR cible : {', '.join(unknown)}")
    return errors
