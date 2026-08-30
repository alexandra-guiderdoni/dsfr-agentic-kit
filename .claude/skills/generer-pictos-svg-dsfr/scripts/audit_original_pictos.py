#!/usr/bin/env python3
"""Audite les créations originales DSFR-like avant revue visuelle."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import statistics
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

sys.dont_write_bytecode = True  # aucun __pycache__ dans un skill packagé
_SCRIPTS_DIR = str(Path(__file__).resolve().parent)
if _SCRIPTS_DIR not in sys.path:
    sys.path.append(_SCRIPTS_DIR)  # après la bibliothèque standard, jamais devant
from analyze_dsfr_corpus import symbol_geometry  # noqa: E402

EXIT_OK, EXIT_FINDINGS, EXIT_STRICT_WARNINGS, EXIT_RUNTIME = 0, 1, 2, 3


COMMAND_RE = re.compile(r"[AaCcHhLlMmQqSsTtVvZz]")
STYLE_FILL_RE = re.compile(r"\.([a-zA-Z0-9_-]+)\s*\{[^}]*fill:\s*([^;]+);", re.MULTILINE)
LAYERS = ("artwork-decorative", "artwork-minor", "artwork-major")
CLASSES = ("fr-artwork-decorative", "fr-artwork-minor", "fr-artwork-major")
FILLS = {"fr-artwork-decorative": "#ECECFF", "fr-artwork-minor": "#E1000F", "fr-artwork-major": "#000091"}
DEFAULT_PROFILE = Path(__file__).resolve().parents[1] / "references" / "dsfr-style-profile.json"
# Repli si le profil ne porte pas de calibration ; les seuils vivants viennent de profile["audit_calibration"],
# mesurés sur le corpus par analyze_dsfr_corpus.py (percentile 10 des ratios officiel/références de même famille).
FALLBACK_CALIBRATION = {
    "poverty_command_p10": {"artwork-major": 52, "artwork-minor": 18},
    "reference_command_ratio": {"artwork-major": 0.3, "artwork-minor": 0.2},
    "reference_bbox_ratio": {"artwork-major": 0.5, "artwork-minor": 0.1},
    "bbox_pct_range": {"artwork-major": [20, 74], "artwork-minor": [1, 63]},
}


def local_name(tag: str) -> str:
    return tag.rsplit("}", 1)[-1]


class AuditRuntimeError(RuntimeError):
    """Erreur d'exécution de l'audit, distincte d'une erreur d'audit sur le SVG."""


def read_json(path: Path) -> dict[str, object]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise AuditRuntimeError(f"fichier introuvable : {path}") from exc
    except (OSError, json.JSONDecodeError, UnicodeDecodeError) as exc:
        raise AuditRuntimeError(f"JSON illisible : {path} ({exc})") from exc
    if not isinstance(data, dict):
        raise AuditRuntimeError(f"JSON inattendu : {path} doit contenir un objet.")
    return data


def style_fills(root: ET.Element) -> dict[str, str]:
    fills: dict[str, str] = {}
    for element in root.iter():
        if local_name(element.tag) == "style" and element.text:
            for class_name, fill in STYLE_FILL_RE.findall(element.text):
                fills[class_name] = fill.strip().upper()
    return fills


def use_href(element: ET.Element) -> str:
    return element.attrib.get("href") or element.attrib.get("{http://www.w3.org/1999/xlink}href") or ""


def command_count(symbol: ET.Element) -> int:
    return sum(
        len(COMMAND_RE.findall(element.attrib.get("d", "")))
        for element in symbol.iter()
        if local_name(element.tag) == "path"
    )


def parse_reference_names(value: str | None, manifest: dict[str, object] | None) -> list[str]:
    if value:
        return [item.strip() for item in value.split(",") if item.strip()]
    if not manifest:
        return []
    refs = manifest.get("references_inspected", [])
    return [str(item) for item in refs] if isinstance(refs, list) else []


def official_reference_medians(profile: dict[str, object], references: list[str], metric: str) -> dict[str, float]:
    """Médiane par calque d'une métrique des références inspectées : commands ou bbox_pct."""
    icons = profile.get("icons", [])
    by_name = {item.get("name"): item for item in icons if isinstance(item, dict)}
    medians: dict[str, float] = {}
    for layer in LAYERS:
        values: list[float] = []
        for reference in references:
            item = by_name.get(reference)
            if not item:
                continue
            layers = item.get("layers", {})
            layer_data = layers.get(layer) if isinstance(layers, dict) else None
            if not isinstance(layer_data, dict):
                continue
            if metric == "commands":
                if "commands" in layer_data:
                    values.append(float(layer_data["commands"]))
            else:
                geometry = layer_data.get("geometry", {})
                if isinstance(geometry, dict) and metric in geometry:
                    values.append(float(geometry[metric]))
        if values:
            medians[layer] = float(statistics.median(values))
    return medians


def official_command_medians(profile: dict[str, object], references: list[str]) -> dict[str, int]:
    return {layer: int(value) for layer, value in official_reference_medians(profile, references, "commands").items()}


def profile_layer_stat(profile: dict[str, object], layer: str, metric: str, key: str) -> float | None:
    stats = profile.get("layer_stats", {})
    layer_stats = stats.get(layer) if isinstance(stats, dict) else None
    values = layer_stats.get(metric) if isinstance(layer_stats, dict) else None
    if isinstance(values, dict) and key in values:
        return float(values[key])
    return None


def analyze_svg(svg_path: Path) -> tuple[dict[str, int], list[str], dict[str, dict[str, object]]]:
    errors: list[str] = []
    geometry: dict[str, dict[str, object]] = {}
    try:
        content = svg_path.read_text(encoding="utf-8", errors="replace")
    except FileNotFoundError as exc:
        raise AuditRuntimeError(f"SVG introuvable : {svg_path}") from exc
    if "<!DOCTYPE" in content or "<!ENTITY" in content:
        return {}, ["DOCTYPE ou entités XML présents, refusés pour un pictogramme DSFR"], {}
    try:
        root = ET.parse(svg_path).getroot()
    except ET.ParseError as exc:
        return {}, [f"XML invalide : {exc}"], {}

    if local_name(root.tag) != "svg":
        errors.append("racine <svg> absente")
    if root.attrib.get("viewBox") != "0 0 80 80":
        errors.append('viewBox différent de "0 0 80 80"')
    if root.attrib.get("width") not in {"80px", "80"} or root.attrib.get("height") not in {"80px", "80"}:
        errors.append('taille différente de "80px" ou "80"')

    fills = style_fills(root)
    for class_name, expected in FILLS.items():
        if fills.get(class_name) != expected:
            errors.append(f"couleur .{class_name} différente de {expected}")

    symbols = [element for element in root.iter() if local_name(element.tag) == "symbol"]
    symbol_order = [element.attrib.get("id", "") for element in symbols]
    if symbol_order != list(LAYERS):
        errors.append("ordre des symboles non canonique")

    uses = [element for element in root.iter() if local_name(element.tag) == "use"]
    if [use_href(element) for element in uses] != [f"#{layer}" for layer in LAYERS]:
        errors.append("href des <use> non canoniques")
    if [element.attrib.get("class", "") for element in uses] != list(CLASSES):
        errors.append("classes des <use> non canoniques")

    metrics: dict[str, int] = {}
    by_id = {element.attrib.get("id", ""): element for element in symbols}
    for layer in LAYERS:
        symbol = by_id.get(layer)
        if symbol is None:
            errors.append(f"symbole manquant : {layer}")
            continue
        paths = [element for element in symbol.iter() if local_name(element.tag) == "path"]
        if not paths:
            errors.append(f"{layer} ne contient aucun <path>")
        for element in symbol.iter():
            name = local_name(element.tag)
            if name not in {"symbol", "path"}:
                errors.append(f"{layer} contient un élément interdit <{name}>")
            if name == "path" and ({"fill", "stroke"} & set(element.attrib)):
                errors.append(f"{layer} contient un <path> avec fill ou stroke")
        metrics[layer] = command_count(symbol)
        try:
            geometry[layer] = symbol_geometry([element.attrib.get("d", "") for element in paths])
        except ValueError as exc:
            errors.append(f"{layer} : chemin invalide, {exc}")
    return metrics, errors, geometry


def calibration(profile: dict[str, object]) -> dict[str, dict[str, object]]:
    """Seuils lus dans le profil ; une clé absente prend le repli, une clé malformée est une erreur d'exécution (code 3)."""
    raw = profile.get("audit_calibration")
    if not isinstance(raw, dict):
        return FALLBACK_CALIBRATION  # type: ignore[return-value]
    result: dict[str, dict[str, object]] = {}
    for key in FALLBACK_CALIBRATION:
        value = raw.get(key)
        if value is None:
            result[key] = FALLBACK_CALIBRATION[key]  # type: ignore[assignment]
            continue
        if not isinstance(value, dict):
            raise AuditRuntimeError(f"profil : audit_calibration.{key} doit être un objet calque → valeur.")
        for layer, item in value.items():
            if key == "bbox_pct_range":
                ok = isinstance(item, list) and len(item) == 2 and all(isinstance(bound, (int, float)) and not isinstance(bound, bool) for bound in item)
            else:
                ok = isinstance(item, (int, float)) and not isinstance(item, bool)
            if not ok:
                raise AuditRuntimeError(f"profil : audit_calibration.{key}.{layer} malformé ({item!r}).")
        result[key] = value
    return result


def manifest_describes(manifest: object, filename: str) -> bool:
    """Un manifeste voisin ne vaut que s'il décrit le SVG audité (entrée icons[].file ou champ file)."""
    if not isinstance(manifest, dict):
        return False
    if manifest.get("file") == filename:
        return True
    icons = manifest.get("icons")
    return isinstance(icons, list) and any(isinstance(item, dict) and item.get("file") == filename for item in icons)


def audit(args: argparse.Namespace) -> int:
    svg_path = Path(args.svg).expanduser().resolve()
    manifest_path = Path(args.manifest).expanduser().resolve() if args.manifest else None
    ignored_sibling: Path | None = None
    if manifest_path is None and (svg_path.parent / "manifest.json").is_file():
        sibling = svg_path.parent / "manifest.json"
        if manifest_describes(read_json(sibling), svg_path.name):
            manifest_path = sibling
        else:
            ignored_sibling = sibling
    manifest = read_json(manifest_path) if manifest_path else None
    profile = read_json(Path(args.profile).expanduser().resolve())
    references = parse_reference_names(args.references, manifest)
    metrics, errors, geometry = analyze_svg(svg_path)
    warnings: list[str] = []
    cal = calibration(profile)

    if manifest is not None and manifest.get("official") is not False:
        errors.append("le manifeste doit déclarer official: false")
    digest = hashlib.sha256(svg_path.read_bytes()).hexdigest()  # analyze_svg a déjà levé si le fichier manque
    same = [str(item.get("name")) for item in profile.get("icons", []) if isinstance(item, dict) and item.get("sha256") == digest]
    if same:
        errors.append(f"copie exacte du pictogramme officiel {same[0]} déclarée comme création : utiliser --source dsfr-replica")
    if len(references) < 3 or len(references) > 5:
        warnings.append("citer trois à cinq références officielles inspectées")

    icons = profile.get("icons", [])
    official_names = {str(item.get("name")) for item in icons if isinstance(item, dict)}
    unknown_references = [reference for reference in references if reference not in official_names]
    if unknown_references:
        errors.append("référence officielle inconnue : " + ", ".join(unknown_references))

    ref_medians = official_command_medians(profile, references)
    if references and not ref_medians:
        errors.append("aucune référence officielle inspectée n'existe dans le profil")

    ref_bbox_medians = official_reference_medians(profile, references, "bbox_pct")
    for layer in ("artwork-major", "artwork-minor"):
        if layer not in metrics:
            continue
        commands = metrics[layer]
        bbox_pct = float(geometry.get(layer, {}).get("bbox_pct", 0.0))  # type: ignore[arg-type]
        p10 = profile_layer_stat(profile, layer, "commands_per_icon", "p10")
        p10_value = int(p10) if p10 is not None else int(cal["poverty_command_p10"].get(layer, 0))  # type: ignore[union-attr]
        low, high = cal["bbox_pct_range"].get(layer, [0.0, 100.0])  # type: ignore[union-attr]
        ratio_cmd = float(cal["reference_command_ratio"].get(layer, 0.0))  # type: ignore[union-attr]
        ratio_box = float(cal["reference_bbox_ratio"].get(layer, 0.0))  # type: ignore[union-attr]
        # Pauvreté : sous le p10 officiel ET sous la moitié des références inspectées (un officiel sobre n'est pas pauvre).
        if commands < p10_value and (layer not in ref_medians or commands < ref_medians[layer] * 0.5):
            warnings.append(f"{layer} trop pauvre : {commands} commandes, p10 officiel {p10_value}" + (f", médiane des références {ref_medians[layer]:.0f}" if layer in ref_medians else ""))
        if layer in ref_medians and commands < round(ref_medians[layer] * ratio_cmd):
            warnings.append(
                f"{layer} très sous les références inspectées "
                f"({commands} commandes vs médiane {ref_medians[layer]:.0f}, seuil calibré {ratio_cmd:g})"
            )
        if not float(low) <= bbox_pct <= float(high):
            warnings.append(f"{layer} occupe {bbox_pct:.0f} % du carré, hors de la plage observée sur les officiels [{float(low):.0f}, {float(high):.0f}] %")
        if layer in ref_bbox_medians and bbox_pct < ref_bbox_medians[layer] * ratio_box:
            warnings.append(
                f"{layer} occupe {bbox_pct:.0f} % du carré, très sous les références inspectées (médiane {ref_bbox_medians[layer]:.0f} %, seuil calibré {ratio_box:g})"
            )

    print(f"SVG audité : {svg_path}")
    if ignored_sibling is not None:
        print(f"Manifeste voisin ignoré : {ignored_sibling} ne décrit pas {svg_path.name}")
    print(f"Manifeste : {manifest_path}" if manifest_path else "Manifeste : aucun (official: false non vérifiable)")
    print("Commandes par calque : " + ", ".join(f"{layer}={metrics.get(layer, 0)}" for layer in LAYERS))
    print(
        "Occupation du carré par calque : "
        + ", ".join(f"{layer}={float(geometry.get(layer, {}).get('bbox_pct', 0.0)):.0f} %" for layer in LAYERS)  # type: ignore[arg-type]
    )
    if references:
        print("Références : " + ", ".join(references))
    for error in errors:
        print(f"ERREUR : {error}", file=sys.stderr)
    for warning in warnings:
        print(f"AVERTISSEMENT : {warning}")
    if errors:
        return EXIT_FINDINGS
    if warnings and args.strict:
        return EXIT_STRICT_WARNINGS
    return EXIT_OK


def main(argv: list[str] | None = None) -> int:
    try:
        return audit(build_parser().parse_args(argv))
    except (AuditRuntimeError, OSError, ValueError, TypeError) as exc:
        print(f"ERREUR D'EXÉCUTION : {exc}", file=sys.stderr)
        return EXIT_RUNTIME


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Auditer un SVG original DSFR-like.")
    parser.add_argument("--svg", required=True, help="SVG original à auditer.")
    parser.add_argument("--manifest", help="Manifest JSON associé ; à défaut, le manifest.json voisin du SVG est lu s'il existe.")
    parser.add_argument("--references", help="Références officielles famille/nom, séparées par des virgules.")
    parser.add_argument("--profile", default=str(DEFAULT_PROFILE), help="Profil JSON du corpus DSFR officiel.")
    parser.add_argument("--strict", action="store_true", help="Retourner le code 2 sur avertissement ; 1 = erreurs d'audit, 3 = erreur d'exécution.")
    return parser


if __name__ == "__main__":
    raise SystemExit(main())
