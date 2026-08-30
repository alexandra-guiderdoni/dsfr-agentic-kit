#!/usr/bin/env python3
"""Construit une planche HTML de contrôle visuel pour les pictogrammes SVG."""

from __future__ import annotations

import argparse
import difflib
import html
import json
import os
import sys
import urllib.parse
from dataclasses import dataclass
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from generate_pictos_svg import declared_dsfr_version, official_cache_root, resolve_official_svg  # noqa: E402


DEFAULT_SIZES = (80, 40, 24)
MAX_SIZE = 1024
DEFAULT_OFFICIAL_ROOT = Path(__file__).resolve().parents[1] / "pictos-svg" / "dsfr-officiels"


@dataclass(frozen=True)
class ReferenceSvg:
    name: str
    path: Path


def parse_sizes(value: str) -> tuple[int, ...]:
    sizes = []
    for chunk in value.split(","):
        chunk = chunk.strip()
        if not chunk:
            continue
        try:
            size = int(chunk)
        except ValueError as exc:
            raise argparse.ArgumentTypeError(f"Taille non numérique : {chunk!r}.") from exc
        if size <= 0 or size > MAX_SIZE:
            raise argparse.ArgumentTypeError(f"Les tailles doivent être comprises entre 1 et {MAX_SIZE} px.")
        sizes.append(size)
    if not sizes:
        raise argparse.ArgumentTypeError("Fournir au moins une taille.")
    return tuple(sizes)


def discover_svgs(svg_root: Path, include_official: bool) -> list[Path]:
    if not svg_root.exists():
        raise FileNotFoundError(f"Dossier SVG introuvable : {svg_root}")
    if svg_root.is_file():
        if svg_root.suffix.lower() != ".svg":
            raise ValueError(f"Le fichier n'est pas un SVG : {svg_root}")
        if "dsfr-officiels" in svg_root.parts and not include_official:
            raise ValueError(f"{svg_root} appartient au corpus officiel : passer --include-official pour le prévisualiser.")
        return [svg_root]

    svgs = []
    excluded = 0
    for path in sorted(svg_root.rglob("*.svg")):
        if not include_official and "dsfr-officiels" in path.parts:
            excluded += 1
            continue
        svgs.append(path)
    if not svgs:
        if excluded:
            raise ValueError(f"Aucun SVG à prévisualiser dans {svg_root} : {excluded} SVG du corpus officiel y sont exclus par défaut, ajouter --include-official pour les inclure.")
        raise ValueError(f"Aucun SVG trouvé dans {svg_root}.")
    return svgs


def parse_reference_names(value: str | None) -> list[str]:
    if not value:
        return []
    names = []
    for chunk in value.split(","):
        name = chunk.strip()
        if not name:
            continue
        if name.count("/") != 1:
            raise ValueError(f"Référence invalide : {name}. Format attendu : famille/nom.")
        if name not in names:
            names.append(name)
    return names


def official_index(official_root: Path) -> tuple[dict[str, dict[str, object]], str | None]:
    """Index nom → entrée du manifeste officiel (sans résoudre les fichiers) et version DSFR déclarée."""
    manifest_path = official_root / "manifest.json"
    if not manifest_path.exists():
        raise FileNotFoundError(f"Manifeste officiel introuvable : {manifest_path}")
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    if not isinstance(manifest, dict) or not isinstance(manifest.get("icons"), list):
        raise ValueError(f"Manifeste officiel inattendu : {manifest_path} doit contenir un objet avec une liste icons.")
    index = {}
    ignored = 0
    for item in manifest["icons"]:
        name = item.get("name") if isinstance(item, dict) else None
        filename = item.get("file") if isinstance(item, dict) else None
        if not (isinstance(name, str) and isinstance(filename, str)):
            ignored += 1
            continue
        if "/" in filename or "\\" in filename or filename.startswith(".") or ".." in filename:
            raise ValueError(f"Manifeste officiel : nom de fichier invalide {filename!r} pour {name}.")
        index[name] = {**item, "name": name, "file": filename}
    if ignored:
        print(f"AVERTISSEMENT : {ignored} entrée(s) du manifeste officiel {manifest_path} ignorée(s), forme inattendue (name et file requis).")
    return index, declared_dsfr_version(manifest)


def resolve_references(reference_names: list[str], official_root: Path = DEFAULT_OFFICIAL_ROOT) -> list[ReferenceSvg]:
    if not reference_names:
        return []
    index, version = official_index(official_root)
    references = []
    for name in reference_names:
        entry = index.get(name)
        if entry is None:
            suggestions = difflib.get_close_matches(name, sorted(index), n=3)
            suffix = f" Références proches : {', '.join(suggestions)}." if suggestions else ""
            raise ValueError(f"Référence officielle inconnue : {name}.{suffix}")
        path = resolve_official_svg(official_root, entry, version, required=False)
        if path is None:
            hint = (
                f"npm pack @gouvfr/dsfr@{version} --ignore-scripts puis extraction sous le cache" if version
                else "le manifeste officiel ne déclare pas de dsfr_version : impossible de résoudre le paquet en cache"
            )
            raise ValueError(
                f"NOT VERIFIED: source officielle absente : {name} n'est ni embarqué ({official_root / str(entry['file'])}) ni dans le cache officiel "
                f"({official_cache_root()}) ; {hint}."
            )
        references.append(ReferenceSvg(name=name, path=path))
    return references


def relative_href(svg_path: Path, output_path: Path) -> str:
    try:
        relative = os.path.relpath(svg_path, output_path.parent)
    except ValueError as exc:
        raise ValueError(f"Impossible de référencer {svg_path} depuis {output_path.parent} (volumes différents) : placer la planche sur le même volume que les SVG.") from exc
    return urllib.parse.quote(relative.replace(os.sep, "/"), safe="/")


def load_captions(svg_root: Path) -> dict[str, dict[str, str]]:
    """Annotations du manifeste (title, major, minor, description) indexées par chemin relatif au dossier."""
    manifest_dir = svg_root if svg_root.is_dir() else svg_root.parent
    manifest_path = manifest_dir / "manifest.json"
    if not manifest_path.exists():
        print(f"AVERTISSEMENT : --captions demandé mais aucun manifest.json dans {manifest_dir} ; planche sans légende.")
        return {}
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ValueError(f"--captions : manifeste illisible {manifest_path} ({exc}).") from exc
    if not isinstance(manifest, dict) or not isinstance(manifest.get("icons"), list):
        raise ValueError(f"--captions : manifeste inattendu {manifest_path}, objet avec une liste icons attendu.")
    captions: dict[str, dict[str, str]] = {}
    for item in manifest["icons"]:
        if isinstance(item, dict) and item.get("file"):
            key = Path(str(item["file"])).as_posix()
            if key in captions:
                print(f"AVERTISSEMENT : légende en double pour {key} dans {manifest_path}, la dernière est retenue.")
            captions[key] = {k: str(item.get(k) or "") for k in ("title", "major", "minor", "description")}
    return captions


def caption_for(captions: dict[str, dict[str, str]], svg_path: Path, root: Path) -> dict[str, str] | None:
    base = root if root.is_dir() else root.parent
    try:
        key = svg_path.relative_to(base).as_posix()
    except ValueError:
        key = svg_path.name
    if key in captions:
        return captions[key]
    candidates = [candidate for candidate in captions if Path(candidate).name == svg_path.name]
    if len(candidates) == 1:
        return captions[candidates[0]]
    if len(candidates) > 1:
        print(f"AVERTISSEMENT : légende ambiguë pour {key}, {len(candidates)} entrées portent le nom {svg_path.name} ; aucune n'est retenue.")
    return None


def caption_block(caption: dict[str, str] | None) -> str:
    if not caption or not any(caption.values()):
        return ""
    parts = []
    if caption.get("title"):
        parts.append(f"<strong>{html.escape(caption['title'])}</strong>")
    if caption.get("major"):
        parts.append(f"<span class=\"role\">sujet :</span> {html.escape(caption['major'])}")
    if caption.get("minor"):
        parts.append(f"<span class=\"role minor\">accent rouge :</span> {html.escape(caption['minor'])}")
    if caption.get("description"):
        parts.append(html.escape(caption["description"]))
    return '\n  <p class="caption">' + "<br>".join(parts) + "</p>"


def card(svg_path: Path, href: str, sizes: tuple[int, ...], root: Path, caption: dict[str, str] | None = None) -> str:
    title = svg_path.stem
    alt = html.escape((caption or {}).get("title") or title)
    try:
        label = svg_path.relative_to(root if root.is_dir() else root.parent)
    except ValueError:
        label = svg_path.name
    previews = "\n".join(
        f'<div class="preview-size"><img src="{html.escape(href)}" width="{size}" height="{size}" alt="{alt}, {size} px"><span>{size} px</span></div>'
        for size in sizes
    )
    return f"""<article class="card">
  <h2>{html.escape(title)}</h2>
  <p><code>{html.escape(str(label))}</code></p>
  <div class="previews">
    {previews}
  </div>{caption_block(caption)}
</article>"""


def reference_card(reference: ReferenceSvg, output_path: Path, sizes: tuple[int, ...]) -> str:
    href = relative_href(reference.path, output_path)
    previews = "\n".join(
        f'<div class="preview-size"><img src="{html.escape(href)}" width="{size}" height="{size}" alt="{html.escape(reference.name)}, référence officielle, {size} px"><span>{size} px</span></div>'
        for size in sizes
    )
    return f"""<article class="card reference-card">
  <h3>{html.escape(reference.name)}</h3>
  <p><code>{html.escape(reference.path.name)}</code></p>
  <div class="previews">
    {previews}
  </div>
</article>"""


def build_reference_section(references: list[ReferenceSvg], output_path: Path, sizes: tuple[int, ...]) -> str:
    if not references:
        return ""
    cards = "\n".join(reference_card(reference, output_path, sizes) for reference in references)
    return f"""<section class="comparison" aria-labelledby="comparison-title">
    <h2 id="comparison-title">Comparaison avec les références officielles</h2>
    <p class="summary">{len(references)} référence(s) officielle(s) à inspecter aux mêmes tailles.</p>
    <div class="grid">
      {cards}
    </div>
  </section>"""


def build_html(svg_paths: list[Path], output_path: Path, svg_root: Path, sizes: tuple[int, ...], references: list[ReferenceSvg] | None = None, captions: dict[str, dict[str, str]] | None = None) -> str:
    captions = captions or {}
    cards = "\n".join(
        card(path, relative_href(path, output_path), sizes, svg_root, caption_for(captions, path, svg_root))
        for path in svg_paths
    )
    reference_section = build_reference_section(references or [], output_path, sizes)
    return f"""<!doctype html>
<html lang="fr">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Prévisualisation des pictogrammes SVG DSFR</title>
  <style>
    :root {{ --text: #161616; --text-muted: #666; --text-summary: #3a3a3a; --surface: #fff; --border: #ddd; --border-light: #eee; --blue-france: #000091; --red-marianne: #e1000f; }}
    body {{ margin: 24px; font-family: system-ui, sans-serif; color: var(--text); background: var(--surface); }}
    h1 {{ margin: 0 0 16px; font-size: 24px; }}
    h2 {{ margin: 32px 0 12px; font-size: 20px; }}
    .summary {{ margin: 0 0 24px; color: var(--text-summary); }}
    .grid {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(260px, 1fr)); gap: 16px; }}
    .card {{ border: 1px solid var(--border); padding: 16px; border-radius: 4px; }}
    .card h2, .card h3 {{ margin: 0 0 8px; font-size: 16px; }}
    .card p {{ margin: 0 0 16px; font-size: 12px; color: var(--text-muted); word-break: break-word; }}
    .reference-card {{ border-color: var(--blue-france); }}
    .previews {{ display: flex; align-items: flex-end; gap: 18px; min-height: 96px; }}
    .preview-size {{ display: grid; justify-items: center; gap: 8px; font-size: 12px; color: var(--text-muted); }}
    .caption {{ margin: 12px 0 0; font-size: 13px; color: var(--text); }}
    .caption .role {{ font-weight: 600; }}
    .caption .minor {{ color: var(--red-marianne); }}
    img {{ background: var(--surface); outline: 1px solid var(--border-light); }}
  </style>
</head>
<body>
  <header>
    <h1>Prévisualisation des pictogrammes SVG DSFR</h1>
    <p class="summary">{len(svg_paths)} SVG contrôlé{"s" if len(svg_paths) > 1 else ""} aux tailles {", ".join(f"{size} px" for size in sizes)}.</p>
  </header>
  <main>
    <div class="grid">
    {cards}
    </div>
    {reference_section}
  </main>
</body>
</html>
"""


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Créer une planche HTML de prévisualisation SVG.")
    parser.add_argument("--svg-root", default="pictos-svg", help="Dossier ou fichier SVG à prévisualiser.")
    parser.add_argument("--output", default="outputs/pictos-preview.html", help="Fichier HTML de sortie.")
    parser.add_argument("--sizes", type=parse_sizes, default=DEFAULT_SIZES, help="Tailles séparées par des virgules.")
    parser.add_argument("--include-official", action="store_true", help="Inclure le dossier dsfr-officiels.")
    parser.add_argument("--references", help="Références officielles famille/nom à comparer, séparées par des virgules.")
    parser.add_argument("--captions", action="store_true", help="Afficher titre, sujet major et accent minor lus dans le manifest.json du dossier, pour la relecture des annotations.")
    parser.add_argument("--official-root", default=str(DEFAULT_OFFICIAL_ROOT), help="Dossier du corpus officiel utilisé pour --references (défaut : corpus embarqué).")
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    try:
        svg_root = Path(args.svg_root).expanduser().resolve()
        output_path = Path(args.output).expanduser().resolve()
        svg_paths = discover_svgs(svg_root, args.include_official)
        references = resolve_references(parse_reference_names(args.references), Path(args.official_root).expanduser().resolve())
        output_path.parent.mkdir(parents=True, exist_ok=True)
        captions = load_captions(svg_root) if args.captions else {}
        output_path.write_text(build_html(svg_paths, output_path, svg_root, args.sizes, references, captions), encoding="utf-8")
        reference_count = f", {len(references)} référence(s)" if references else ""
        print(f"{output_path} ({len(svg_paths)} SVG{reference_count})")
        return 0
    except (OSError, ValueError) as error:
        print(error, file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
