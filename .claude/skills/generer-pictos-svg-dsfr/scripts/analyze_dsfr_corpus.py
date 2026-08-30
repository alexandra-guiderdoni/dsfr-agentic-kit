#!/usr/bin/env python3
"""Analyse le corpus de pictogrammes DSFR embarqué et produit un profil de style."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import re
import statistics
import tempfile
import sys
import xml.etree.ElementTree as ET
from collections import Counter
from datetime import date
from pathlib import Path


COMMAND_RE = re.compile(r"[AaCcHhLlMmQqSsTtVvZz]")
NUMBER_RE = re.compile(r"[-+]?(?:\d*\.\d+|\d+)")
FILL_RE = re.compile(r"\.([a-zA-Z0-9_-]+)\s*\{[^}]*fill:\s*([^;]+);", re.MULTILINE)
SOURCE_VERSION_RE = re.compile(r"@gouvfr/dsfr@([0-9.]+)")
EXPECTED_LAYERS = ("artwork-decorative", "artwork-minor", "artwork-major")
EXPECTED_CLASSES = ("fr-artwork-decorative", "fr-artwork-minor", "fr-artwork-major")
EXPECTED_FILLS = {
    "fr-artwork-decorative": "#ECECFF",
    "fr-artwork-minor": "#E1000F",
    "fr-artwork-major": "#000091",
}
CANONICAL_USE_HREFS = tuple(f"#{layer}" for layer in EXPECTED_LAYERS)
PATH_TOKEN_RE = re.compile(r"([MmLlHhVvCcSsQqTtAaZz])|([-+]?(?:\d+\.?\d*|\.\d+)(?:[eE][-+]?\d+)?)")
CURVE_SAMPLES = 8
SQUARE_AREA = 80.0 * 80.0


def _arc_points(x1: float, y1: float, rx: float, ry: float, phi_deg: float, large_arc: int, sweep: int, x2: float, y2: float) -> list[tuple[float, float]]:
    """Échantillonne un arc SVG (conversion point final vers centre, notes d'implémentation SVG F.6.5)."""
    if rx == 0 or ry == 0 or (x1 == x2 and y1 == y2):
        return [(x2, y2)]
    phi = math.radians(phi_deg)
    cos_phi, sin_phi = math.cos(phi), math.sin(phi)
    dx, dy = (x1 - x2) / 2, (y1 - y2) / 2
    x1p = cos_phi * dx + sin_phi * dy
    y1p = -sin_phi * dx + cos_phi * dy
    rx, ry = abs(rx), abs(ry)
    lam = (x1p ** 2) / (rx ** 2) + (y1p ** 2) / (ry ** 2)
    if lam > 1:
        rx *= math.sqrt(lam)
        ry *= math.sqrt(lam)
    numerator = rx ** 2 * ry ** 2 - rx ** 2 * y1p ** 2 - ry ** 2 * x1p ** 2
    denominator = rx ** 2 * y1p ** 2 + ry ** 2 * x1p ** 2
    coefficient = math.sqrt(max(0.0, numerator / denominator)) if denominator else 0.0
    if large_arc == sweep:
        coefficient = -coefficient
    cxp = coefficient * rx * y1p / ry
    cyp = -coefficient * ry * x1p / rx
    cx = cos_phi * cxp - sin_phi * cyp + (x1 + x2) / 2
    cy = sin_phi * cxp + cos_phi * cyp + (y1 + y2) / 2

    def angle(ux: float, uy: float, vx: float, vy: float) -> float:
        length = math.hypot(ux, uy) * math.hypot(vx, vy)
        if not length:
            return 0.0
        value = math.acos(max(-1.0, min(1.0, (ux * vx + uy * vy) / length)))
        return -value if ux * vy - uy * vx < 0 else value

    theta1 = angle(1, 0, (x1p - cxp) / rx, (y1p - cyp) / ry)
    delta = angle((x1p - cxp) / rx, (y1p - cyp) / ry, (-x1p - cxp) / rx, (-y1p - cyp) / ry)
    if not sweep and delta > 0:
        delta -= 2 * math.pi
    elif sweep and delta < 0:
        delta += 2 * math.pi
    points = []
    for step in range(1, CURVE_SAMPLES + 1):
        t = theta1 + delta * step / CURVE_SAMPLES
        points.append(
            (
                cos_phi * rx * math.cos(t) - sin_phi * ry * math.sin(t) + cx,
                sin_phi * rx * math.cos(t) + cos_phi * ry * math.sin(t) + cy,
            )
        )
    return points


def _bezier_points(controls: list[tuple[float, float]]) -> list[tuple[float, float]]:
    points = []
    degree = len(controls) - 1
    for step in range(1, CURVE_SAMPLES + 1):
        t = step / CURVE_SAMPLES
        x = y = 0.0
        for index, (px, py) in enumerate(controls):
            weight = math.comb(degree, index) * (1 - t) ** (degree - index) * t ** index
            x += weight * px
            y += weight * py
        points.append((x, y))
    return points


def _tokenize_path(d: str) -> list[str]:
    return [match.group(1) or match.group(2) for match in PATH_TOKEN_RE.finditer(d)]


def path_geometry(d: str) -> dict[str, float | int | list[float]]:
    """Interprète un attribut d (commandes absolues et relatives, courbes et arcs aplatis).

    Retourne la boîte englobante, l'aire approximative (somme des aires absolues des
    sous-chemins aplatis, les évidements comptent donc positivement), le nombre de
    sous-chemins et l'occupation du carré 80x80 en pourcentage.
    """
    tokens = _tokenize_path(d)
    subpaths: list[list[tuple[float, float]]] = []
    current: list[tuple[float, float]] = []
    x = y = 0.0
    start_x = start_y = 0.0
    last_control: tuple[float, float] | None = None
    command = ""
    index = 0

    def take_number() -> float:
        nonlocal index
        if index >= len(tokens) or tokens[index].isalpha():
            raise ValueError(f"attribut d invalide : paramètre manquant après la commande {command!r} (jeton {index}).")
        value = tokens[index]
        index += 1
        try:
            return float(value)
        except ValueError as exc:
            raise ValueError(f"attribut d invalide : {value!r} n'est pas un nombre.") from exc

    def take_flag() -> int:
        nonlocal index
        if index >= len(tokens) or tokens[index].isalpha():
            raise ValueError(f"attribut d invalide : drapeau d'arc manquant (jeton {index}).")
        value = tokens[index]
        if value[0] not in "01":
            raise ValueError(f"attribut d invalide : drapeau d'arc {value!r} hors de 0 ou 1.")
        if len(value) > 1:
            tokens[index] = value[1:]  # drapeau collé au nombre suivant, forme compacte légale (a5 5 0 11.5 2)
            return int(value[0])
        index += 1
        return int(value)

    def move_to(nx: float, ny: float) -> None:
        nonlocal current, x, y, start_x, start_y
        if current:
            subpaths.append(current)
        current = [(nx, ny)]
        x, y = nx, ny
        start_x, start_y = nx, ny

    def extend(points: list[tuple[float, float]]) -> None:
        nonlocal x, y
        current.extend(points)
        x, y = points[-1]

    while index < len(tokens):
        token = tokens[index]
        if token.isalpha():
            command = token
            index += 1
            if command in "Zz":
                if current:
                    subpaths.append(current)
                    current = []
                x, y = start_x, start_y
                current = [(x, y)]
                last_control = None
                continue
        relative = command.islower()
        letter = command.upper()
        ox, oy = (x, y) if relative else (0.0, 0.0)
        if letter == "M":
            move_to(ox + take_number(), oy + take_number())
            command = "l" if relative else "L"
            last_control = None
        elif letter == "L":
            extend([(ox + take_number(), oy + take_number())])
            last_control = None
        elif letter == "H":
            extend([(ox + take_number(), y)])
            last_control = None
        elif letter == "V":
            extend([(x, oy + take_number())])
            last_control = None
        elif letter == "C":
            c1 = (ox + take_number(), oy + take_number())
            c2 = (ox + take_number(), oy + take_number())
            end = (ox + take_number(), oy + take_number())
            extend(_bezier_points([(x, y), c1, c2, end]))
            last_control = c2
        elif letter == "S":
            c1 = (2 * x - last_control[0], 2 * y - last_control[1]) if last_control else (x, y)
            c2 = (ox + take_number(), oy + take_number())
            end = (ox + take_number(), oy + take_number())
            extend(_bezier_points([(x, y), c1, c2, end]))
            last_control = c2
        elif letter == "Q":
            c1 = (ox + take_number(), oy + take_number())
            end = (ox + take_number(), oy + take_number())
            extend(_bezier_points([(x, y), c1, end]))
            last_control = c1
        elif letter == "T":
            c1 = (2 * x - last_control[0], 2 * y - last_control[1]) if last_control else (x, y)
            end = (ox + take_number(), oy + take_number())
            extend(_bezier_points([(x, y), c1, end]))
            last_control = c1
        elif letter == "A":
            rx, ry, rotation = take_number(), take_number(), take_number()
            large_arc, sweep = take_flag(), take_flag()
            end = (ox + take_number(), oy + take_number())
            extend(_arc_points(x, y, rx, ry, rotation, large_arc, sweep, end[0], end[1]))
            last_control = None
        else:
            raise ValueError(f"attribut d invalide : jeton inattendu {token!r} avant toute commande." if not command else f"attribut d invalide : commande {command!r} inconnue.")
    if current and len(current) > 1:
        subpaths.append(current)

    polygons = [points for points in subpaths if len(points) > 1]
    if not polygons:
        return {"bbox": [0.0, 0.0, 0.0, 0.0], "width": 0.0, "height": 0.0, "area": 0.0, "subpaths": 0, "bbox_pct": 0.0, "area_pct": 0.0}
    xs = [px for points in polygons for px, _ in points]
    ys = [py for points in polygons for _, py in points]
    area = 0.0
    for points in polygons:
        shoelace = 0.0
        for (ax, ay), (bx, by) in zip(points, points[1:] + points[:1]):
            shoelace += ax * by - bx * ay
        area += abs(shoelace) / 2
    width, height = max(xs) - min(xs), max(ys) - min(ys)
    return {
        "bbox": [round(min(xs), 2), round(min(ys), 2), round(max(xs), 2), round(max(ys), 2)],
        "width": round(width, 2),
        "height": round(height, 2),
        "area": round(area, 2),
        "subpaths": len(polygons),
        "bbox_pct": round(width * height / SQUARE_AREA * 100, 1),
        "area_pct": round(area / SQUARE_AREA * 100, 1),
    }


ARC_PARAMS = 7


def coordinate_numbers(d: str) -> list[str]:
    """Nombres de l'attribut d qui sont des coordonnées : exclut rayons, rotation et drapeaux des arcs."""
    values: list[str] = []
    command = ""
    position = 0
    tokens = _tokenize_path(d)
    index = 0
    while index < len(tokens):
        token = tokens[index]
        index += 1
        if token.isalpha():
            command, position = token, 0
            continue
        if command in "Aa":
            slot = position % ARC_PARAMS
            if slot in (3, 4):  # drapeaux, éventuellement collés au nombre suivant
                rest = token[1:]
                position += 1
                if rest:
                    tokens.insert(index, rest)
                continue
            if slot < 3:  # rx, ry, rotation
                position += 1
                continue
        values.append(token)
        position += 1
    return values


def symbol_geometry(paths: list[str]) -> dict[str, object]:
    """Géométrie de l'union des chemins d'un calque : boîte englobante, aire, centre, part de coordonnées entières."""
    geometries = [path_geometry(d) for d in paths if d.strip()]
    numbers = [value for d in paths for value in coordinate_numbers(d)]
    integers = sum(1 for value in numbers if float(value) == int(float(value)))
    integer_share = round(integers / len(numbers) * 100, 1) if numbers else 0.0
    boxes = [g["bbox"] for g in geometries if g["subpaths"]]  # type: ignore[index]
    if not boxes:
        return {"bbox": [0.0, 0.0, 0.0, 0.0], "width": 0.0, "height": 0.0, "center": [0.0, 0.0], "area_pct": 0.0, "bbox_pct": 0.0, "subpaths": 0, "integer_share_pct": integer_share}
    xmin = min(box[0] for box in boxes)  # type: ignore[index]
    ymin = min(box[1] for box in boxes)  # type: ignore[index]
    xmax = max(box[2] for box in boxes)  # type: ignore[index]
    ymax = max(box[3] for box in boxes)  # type: ignore[index]
    width, height = xmax - xmin, ymax - ymin
    return {
        "bbox": [xmin, ymin, xmax, ymax],
        "width": round(width, 2),
        "height": round(height, 2),
        "center": [round((xmin + xmax) / 2, 2), round((ymin + ymax) / 2, 2)],
        "area_pct": round(sum(float(g["area"]) for g in geometries) / SQUARE_AREA * 100, 1),  # type: ignore[arg-type]
        "bbox_pct": round(width * height / SQUARE_AREA * 100, 1),
        "subpaths": sum(int(g["subpaths"]) for g in geometries),  # type: ignore[arg-type]
        "integer_share_pct": integer_share,
    }


def local_name(tag: str) -> str:
    return tag.rsplit("}", 1)[-1]


def default_corpus_root() -> Path:
    return Path(__file__).resolve().parents[1] / "pictos-svg" / "dsfr-officiels"


def read_manifest(root: Path) -> list[dict[str, str]]:
    manifest_path = root / "manifest.json"
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError, UnicodeDecodeError) as exc:
        raise ValueError(f"{manifest_path} illisible : {exc}") from exc
    if not isinstance(manifest, dict) or not isinstance(manifest.get("icons"), list):
        raise ValueError(f"{manifest_path} n'a pas la forme attendue : objet avec une liste icons.")
    return manifest["icons"]


def source_version(root: Path) -> str:
    source_path = root / "SOURCE.md"
    if not source_path.exists():
        return "Unknown"
    match = SOURCE_VERSION_RE.search(source_path.read_text(encoding="utf-8"))
    return match.group(1) if match else "Unknown"


def style_fills(root: ET.Element) -> dict[str, str]:
    fills: dict[str, str] = {}
    for element in root.iter():
        if local_name(element.tag) == "style" and element.text:
            for class_name, fill in FILL_RE.findall(element.text):
                fills[class_name] = fill.strip().upper()
    return fills


def child_sequence(root: ET.Element, tag_name: str, attr: str) -> list[str]:
    return [element.attrib.get(attr, "") for element in root.iter() if local_name(element.tag) == tag_name]


def use_href(element: ET.Element) -> str:
    return element.attrib.get("href") or element.attrib.get("{http://www.w3.org/1999/xlink}href") or ""


def sequence_key(values: list[str] | tuple[str, ...]) -> str:
    return " > ".join(values)


def summarize_numbers(values: list[int]) -> dict[str, float | int]:
    if not values:
        return {"min": 0, "p10": 0, "p25": 0, "median": 0, "mean": 0, "p75": 0, "p90": 0, "max": 0}
    sorted_values = sorted(values)

    def percentile(ratio: float) -> int:
        index = int((len(sorted_values) - 1) * ratio + 0.5)  # arrondi demi-supérieur, pas bancaire
        return sorted_values[index]

    return {
        "min": sorted_values[0],
        "p10": percentile(0.10),
        "p25": percentile(0.25),
        "median": statistics.median(sorted_values),
        "mean": round(statistics.mean(sorted_values), 2),
        "p75": percentile(0.75),
        "p90": percentile(0.90),
        "max": sorted_values[-1],
    }


def layer_summary(symbol: ET.Element | None) -> dict[str, object]:
    if symbol is None:
        return {
            "paths": 0,
            "commands": 0,
            "numbers": 0,
            "path_chars": 0,
            "element_tags": {},
            "path_attributes": {},
            "geometry": symbol_geometry([]),
        }

    paths = []
    element_tags = Counter()
    path_attributes = Counter()
    for element in symbol.iter():
        element_name = local_name(element.tag)
        element_tags[element_name] += 1
        if element_name != "path":
            continue
        d = element.attrib.get("d", "")
        paths.append(d)
        path_attributes.update(element.attrib.keys())

    return {
        "paths": len(paths),
        "commands": sum(len(COMMAND_RE.findall(path)) for path in paths),
        "numbers": sum(len(NUMBER_RE.findall(path)) for path in paths),
        "path_chars": sum(len(path) for path in paths),
        "element_tags": dict(sorted(element_tags.items())),
        "path_attributes": dict(sorted(path_attributes.items())),
        "geometry": symbol_geometry(paths),
    }


def analyze_icon(root_dir: Path, item: dict[str, str]) -> dict[str, object]:
    if not isinstance(item, dict) or not item.get("file") or not item.get("name"):
        raise ValueError(f"entrée de manifeste invalide, name et file requis : {item!r}")
    file_name = str(item["file"])
    if "/" in file_name or "\\" in file_name or file_name.startswith(".") or ".." in file_name:
        raise ValueError(f"nom de fichier de manifeste invalide : {file_name!r}")
    svg_path = root_dir / file_name
    content = svg_path.read_text(encoding="utf-8", errors="replace")
    if "<!DOCTYPE" in content or "<!ENTITY" in content:
        raise ValueError(f"{svg_path} contient un DOCTYPE ou des entités XML, refusés.")
    try:
        svg = ET.parse(svg_path).getroot()
    except ET.ParseError as exc:
        raise ValueError(f"{svg_path} n'est pas un SVG XML valide : {exc}") from exc
    symbols = {
        element.attrib.get("id", ""): element
        for element in svg.iter()
        if local_name(element.tag) == "symbol"
    }
    use_elements = [element for element in svg.iter() if local_name(element.tag) == "use"]
    symbol_order = child_sequence(svg, "symbol", "id")
    use_hrefs = [use_href(element) for element in use_elements]
    use_classes = [element.attrib.get("class", "") for element in use_elements]

    return {
        "name": item["name"],
        "file": item["file"],
        "family": item["name"].split("/", 1)[0],
        "title": item.get("title", ""),
        "major": item.get("major", ""),
        "minor": item.get("minor", ""),
        "sha256": hashlib.sha256(svg_path.read_bytes()).hexdigest(),
        "viewBox": svg.attrib.get("viewBox"),
        "width": svg.attrib.get("width"),
        "height": svg.attrib.get("height"),
        "root_fill": svg.attrib.get("fill"),
        "style_fills": style_fills(svg),
        "symbol_order": symbol_order,
        "use_hrefs": use_hrefs,
        "use_classes": use_classes,
        "layers": {layer: layer_summary(require_layer(symbols, layer, svg_path)) for layer in EXPECTED_LAYERS},
    }


def require_layer(symbols: dict[str, ET.Element], layer: str, svg_path: Path) -> ET.Element:
    """Un calque absent est une corruption du corpus : refusée plutôt que comptée à zéro dans la calibration."""
    symbol = symbols.get(layer)
    if symbol is None:
        raise ValueError(f"{svg_path.name} : calque {layer} absent (id des symboles : {', '.join(sorted(symbols)) or 'aucun'}).")
    return symbol


def audit_calibration(icons: list[dict[str, object]]) -> dict[str, object]:
    """Seuils de l'audit mesurés sur le corpus : chaque officiel est comparé à trois références de sa famille.

    Les ratios officiel/médiane des références sont résumés par leur minimum observé : par construction,
    aucun officiel n'est « très sous ses références » (un percentile 10 en signalait 29 sur 102, mesure du
    2026-08-29). La plage d'occupation est la plage observée ; la pauvreté absolue reste au p10 des commandes.
    """
    if not icons:
        return {"method": "minimum observé des ratios officiel/références de même famille", "reference_command_ratio": {}, "reference_bbox_ratio": {}, "bbox_pct_range": {}, "poverty_command_p10": {}}
    by_family: dict[str, list[dict[str, object]]] = {}
    for icon in icons:
        by_family.setdefault(str(icon["family"]), []).append(icon)
    ordered = sorted(icons, key=lambda icon: str(icon["name"]))
    ratios: dict[str, dict[str, list[float]]] = {layer: {"commands": [], "bbox_pct": []} for layer in ("artwork-major", "artwork-minor")}
    for icon in icons:
        peers = [other for other in by_family[str(icon["family"])] if other is not icon][:3]
        if len(peers) < 3:
            peers += [other for other in ordered if other is not icon and other not in peers][: 3 - len(peers)]
        if not peers:
            continue
        for layer in ratios:
            own_cmd = float(icon["layers"][layer]["commands"])  # type: ignore[index]
            own_box = float(icon["layers"][layer]["geometry"]["bbox_pct"])  # type: ignore[index]
            med_cmd = statistics.median(float(p["layers"][layer]["commands"]) for p in peers)  # type: ignore[index]
            med_box = statistics.median(float(p["layers"][layer]["geometry"]["bbox_pct"]) for p in peers)  # type: ignore[index]
            if med_cmd:
                ratios[layer]["commands"].append(own_cmd / med_cmd)
            if med_box:
                ratios[layer]["bbox_pct"].append(own_box / med_box)

    if not any(ratios[layer]["commands"] for layer in ratios):
        print(f"AVERTISSEMENT : {len(icons)} pictogramme(s) seulement, aucune référence disponible : ratios de calibration non calculés.", file=sys.stderr)
        return {
            "method": "minimum observé des ratios officiel/références de même famille ; corpus trop petit, ratios non calculés",
            "reference_command_ratio": {},
            "reference_bbox_ratio": {},
            "bbox_pct_range": {layer: [min(float(i["layers"][layer]["geometry"]["bbox_pct"]) for i in icons), max(float(i["layers"][layer]["geometry"]["bbox_pct"]) for i in icons)] for layer in ratios},  # type: ignore[index]
            "poverty_command_p10": {layer: summarize_numbers([int(i["layers"][layer]["commands"]) for i in icons])["p10"] for layer in ratios},  # type: ignore[index]
        }

    def floor(values: list[float]) -> float:
        return round(min(values), 3) if values else 0.0

    return {
        "method": "minimum observé des ratios officiel/médiane de trois références de même famille ; plage d'occupation observée sur le corpus ; pauvreté au p10 des commandes",
        "reference_command_ratio": {layer: floor(ratios[layer]["commands"]) for layer in ratios},
        "reference_bbox_ratio": {layer: floor(ratios[layer]["bbox_pct"]) for layer in ratios},
        "bbox_pct_range": {layer: [min(float(i["layers"][layer]["geometry"]["bbox_pct"]) for i in icons), max(float(i["layers"][layer]["geometry"]["bbox_pct"]) for i in icons)] for layer in ratios},  # type: ignore[index]
        "poverty_command_p10": {layer: summarize_numbers([int(i["layers"][layer]["commands"]) for i in icons])["p10"] for layer in ratios},  # type: ignore[index]
    }


def build_profile(root_dir: Path) -> dict[str, object]:
    icons = [analyze_icon(root_dir, item) for item in read_manifest(root_dir)]
    families = Counter(str(icon["family"]) for icon in icons)
    observed_sizes = Counter(f"{icon['width']} x {icon['height']}" for icon in icons)
    observed_fills = Counter(fill for icon in icons for fill in icon["style_fills"].values())  # type: ignore[union-attr]
    root_fill_files = [str(icon["file"]) for icon in icons if icon.get("root_fill")]
    symbol_order_counts = Counter(sequence_key(icon["symbol_order"]) for icon in icons)  # type: ignore[arg-type]
    use_pattern_counts = Counter(
        f"hrefs: {sequence_key(icon['use_hrefs'])} | classes: {sequence_key(icon['use_classes'])}"
        for icon in icons
    )
    use_pattern_exceptions = [
        {
            "name": icon["name"],
            "file": icon["file"],
            "use_hrefs": icon["use_hrefs"],
            "use_classes": icon["use_classes"],
        }
        for icon in icons
        if tuple(icon["use_hrefs"]) != CANONICAL_USE_HREFS or tuple(icon["use_classes"]) != EXPECTED_CLASSES
    ]
    path_attribute_counts = Counter()
    symbol_element_counts = Counter()
    layer_stats: dict[str, dict[str, object]] = {}

    for icon in icons:
        for layer in EXPECTED_LAYERS:
            data = icon["layers"][layer]  # type: ignore[index]
            path_attribute_counts.update(data["path_attributes"])  # type: ignore[arg-type]
            symbol_element_counts.update({f"{layer}:{key}": value for key, value in data["element_tags"].items()})  # type: ignore[union-attr]

    for layer in EXPECTED_LAYERS:
        layer_stats[layer] = {
            "paths_per_icon": summarize_numbers([int(icon["layers"][layer]["paths"]) for icon in icons]),  # type: ignore[index]
            "commands_per_icon": summarize_numbers([int(icon["layers"][layer]["commands"]) for icon in icons]),  # type: ignore[index]
            "numbers_per_icon": summarize_numbers([int(icon["layers"][layer]["numbers"]) for icon in icons]),  # type: ignore[index]
            "path_chars_per_icon": summarize_numbers([int(icon["layers"][layer]["path_chars"]) for icon in icons]),  # type: ignore[index]
            "bbox_pct_per_icon": summarize_numbers([round(float(icon["layers"][layer]["geometry"]["bbox_pct"])) for icon in icons]),  # type: ignore[index]
            "area_pct_per_icon": summarize_numbers([round(float(icon["layers"][layer]["geometry"]["area_pct"])) for icon in icons]),  # type: ignore[index]
            "width_per_icon": summarize_numbers([round(float(icon["layers"][layer]["geometry"]["width"])) for icon in icons]),  # type: ignore[index]
            "height_per_icon": summarize_numbers([round(float(icon["layers"][layer]["geometry"]["height"])) for icon in icons]),  # type: ignore[index]
            "center_x_per_icon": summarize_numbers([round(float(icon["layers"][layer]["geometry"]["center"][0])) for icon in icons]),  # type: ignore[index]
            "center_y_per_icon": summarize_numbers([round(float(icon["layers"][layer]["geometry"]["center"][1])) for icon in icons]),  # type: ignore[index]
            "integer_coordinate_share_pct": round(
                statistics.mean([float(icon["layers"][layer]["geometry"]["integer_share_pct"]) for icon in icons] or [0.0]), 1  # type: ignore[index]
            ),
        }

    family_stats: dict[str, dict[str, float | int]] = {}
    for family in sorted(families):
        members = [icon for icon in icons if icon["family"] == family]
        family_stats[family] = {
            "count": len(members),
            "major_commands_median": statistics.median(int(icon["layers"]["artwork-major"]["commands"]) for icon in members),  # type: ignore[index]
            "minor_commands_median": statistics.median(int(icon["layers"]["artwork-minor"]["commands"]) for icon in members),  # type: ignore[index]
            "major_bbox_pct_median": statistics.median(float(icon["layers"]["artwork-major"]["geometry"]["bbox_pct"]) for icon in members),  # type: ignore[index]
            "minor_bbox_pct_median": statistics.median(float(icon["layers"]["artwork-minor"]["geometry"]["bbox_pct"]) for icon in members),  # type: ignore[index]
        }

    corpus_svg_count = len(list(root_dir.glob("*.svg")))
    corpus_sha = hashlib.sha256("\n".join(str(icon["sha256"]) for icon in icons).encode("utf-8")).hexdigest()
    return {
        "source": "pictos-svg/dsfr-officiels",
        "source_package": "@gouvfr/dsfr",
        "source_version": source_version(root_dir),
        "analysis_date": date.today().isoformat(),
        "icon_count": len(icons),
        "corpus_svg_count": corpus_svg_count,
        "corpus_sha256": corpus_sha,
        "audit_calibration": audit_calibration(icons),
        "expected_viewBox": "0 0 80 80",
        "recommended_creation_size": "80px x 80px",
        "observed_sizes": dict(sorted(observed_sizes.items())),
        "root_fill_files": sorted(root_fill_files),
        "expected_layers": list(EXPECTED_LAYERS),
        "expected_use_count": 3,
        "expected_fills": EXPECTED_FILLS,
        "observed_fills": dict(sorted(observed_fills.items())),
        "families": dict(sorted(families.items())),
        "family_stats": family_stats,
        "symbol_order_counts": dict(sorted(symbol_order_counts.items())),
        "use_pattern_counts": dict(sorted(use_pattern_counts.items())),
        "use_pattern_exceptions": use_pattern_exceptions,
        "path_attribute_counts": dict(sorted(path_attribute_counts.items())),
        "symbol_element_counts": dict(sorted(symbol_element_counts.items())),
        "layer_stats": layer_stats,
        "rules": [
            "Utiliser --source dsfr-replica si le nom existe dans le corpus embarqué.",
            "Créer en original-dsfr-like seulement après preuve d'absence officielle.",
            "Utiliser le gabarit 80x80, les trois symboles et les trois use canoniques pour toute création nouvelle.",
            "Utiliser uniquement des path dans les symboles, sans stroke, sans primitive SVG et sans couleur directe sur les chemins.",
            "Viser un chemin riche par calque plutôt qu'une accumulation de primitives.",
            "Comparer la complexité du major et du minor à trois à cinq références officielles proches.",
            "Comparer l'occupation du carré (boîte englobante du major et du minor) aux références inspectées ; l'audit lit les repères dans ce profil.",
            "La grille de 2 px est une grille de conception : les coordonnées officielles ne sont pas majoritairement entières, ne pas en faire un critère d'audit.",
            "Marquer toute création originale comme official=false et ne jamais la présenter comme officielle.",
        ],
        "icons": icons,
    }


def write_markdown(profile: dict[str, object], target: Path) -> None:
    families: dict[str, int] = profile["families"]  # type: ignore[assignment]
    layer_stats: dict[str, object] = profile["layer_stats"]  # type: ignore[assignment]

    def stats_text(stats: dict[str, float | int]) -> str:
        return (
            f"min {stats['min']}, p10 {stats['p10']}, médiane {stats['median']}, "
            f"moyenne {stats['mean']}, p90 {stats['p90']}, max {stats['max']}"
        )

    lines = [
        "# Profil de style des pictogrammes DSFR",
        "",
        f"Corpus analysé : `{profile['source']}`.",
        f"Source : `{profile['source_package']}@{profile['source_version']}`.",
        f"Date d'analyse : {profile['analysis_date']}.",
        f"Nombre de pictogrammes officiels : {profile['icon_count']}.",
        f"Nombre de SVG dans le corpus : {profile['corpus_svg_count']}.",
        f"Empreinte du corpus (SHA256 des empreintes) : `{str(profile['corpus_sha256'])[:16]}…`.",
        "",
        "## Invariants et variantes",
        "",
        f"- Gabarit invariant : `{profile['expected_viewBox']}`.",
        f"- Taille recommandée pour une création : `{profile['recommended_creation_size']}`.",
        f"- Tailles observées : {json.dumps(profile['observed_sizes'], ensure_ascii=False)}.",
        f"- Fichiers avec `fill` racine : {len(profile['root_fill_files'])}.",
        "- Calques : `artwork-decorative`, `artwork-minor`, `artwork-major`.",
        f"- Nombre de `<use>` : {profile['expected_use_count']}.",
        f"- Couleurs attendues : {json.dumps(profile['expected_fills'], ensure_ascii=False)}.",
        "",
        "## Exceptions documentées",
        "",
    ]
    exceptions: list[dict[str, object]] = profile["use_pattern_exceptions"]  # type: ignore[assignment]
    if exceptions:
        for item in exceptions:
            lines.append(f"- `{item['name']}` : hrefs {item['use_hrefs']}, classes {item['use_classes']}.")
    else:
        lines.append("- Aucune exception d'ordre des `<use>`.")
    family_stats: dict[str, dict[str, float | int]] = profile["family_stats"]  # type: ignore[assignment]
    lines.extend(["", "## Familles", ""])
    lines.extend(
        f"- `{family}` : {count} ; médianes major {family_stats[family]['major_commands_median']} commandes, "
        f"{family_stats[family]['major_bbox_pct_median']} % du carré ; minor {family_stats[family]['minor_commands_median']} commandes, "
        f"{family_stats[family]['minor_bbox_pct_median']} % du carré"
        for family, count in sorted(families.items())
    )
    lines.extend(["", "## Complexité par calque", ""])
    for layer, stats in layer_stats.items():
        layer_data: dict[str, object] = stats  # type: ignore[assignment]
        paths: dict[str, float | int] = layer_data["paths_per_icon"]  # type: ignore[assignment]
        commands: dict[str, float | int] = layer_data["commands_per_icon"]  # type: ignore[assignment]
        numbers: dict[str, float | int] = layer_data["numbers_per_icon"]  # type: ignore[assignment]
        chars: dict[str, float | int] = layer_data["path_chars_per_icon"]  # type: ignore[assignment]
        lines.append(f"- `{layer}` :")
        lines.append(f"  - chemins par icône : {stats_text(paths)} ;")
        lines.append(f"  - commandes par icône : {stats_text(commands)} ;")
        lines.append(f"  - nombres par icône : {stats_text(numbers)} ;")
        lines.append(f"  - caractères `d` par icône : {stats_text(chars)}.")
    lines.extend(["", "## Occupation du carré par calque", "", "Boîte englobante des chemins aplatis, en pourcentage du carré `80 x 80` ; l'aire est approximative, les évidements comptent positivement.", ""])
    for layer, stats in layer_stats.items():
        layer_data = stats  # type: ignore[assignment]
        bbox: dict[str, float | int] = layer_data["bbox_pct_per_icon"]  # type: ignore[index]
        area: dict[str, float | int] = layer_data["area_pct_per_icon"]  # type: ignore[index]
        width: dict[str, float | int] = layer_data["width_per_icon"]  # type: ignore[index]
        height: dict[str, float | int] = layer_data["height_per_icon"]  # type: ignore[index]
        cx: dict[str, float | int] = layer_data["center_x_per_icon"]  # type: ignore[index]
        cy: dict[str, float | int] = layer_data["center_y_per_icon"]  # type: ignore[index]
        lines.append(f"- `{layer}` :")
        lines.append(f"  - boîte englobante en % du carré : {stats_text(bbox)} ;")
        lines.append(f"  - aire approximative en % du carré : {stats_text(area)} ;")
        lines.append(f"  - largeur : médiane {width['median']}, p10 {width['p10']}, p90 {width['p90']} ; hauteur : médiane {height['median']}, p10 {height['p10']}, p90 {height['p90']} ;")
        lines.append(f"  - centre médian : ({cx['median']}, {cy['median']}) ;")
        lines.append(f"  - coordonnées entières dans les `d` : {layer_data['integer_coordinate_share_pct']} %.")  # type: ignore[index]
    lines.extend(["", "La base de `2 px` et les multiples de `4` ou `8` sont une grille de conception ; les coordonnées officielles sont majoritairement décimales, cette grille n'est donc pas un critère d'audit."])
    cal: dict[str, object] = profile["audit_calibration"]  # type: ignore[assignment]
    lines.extend(["", "## Calibration de l'audit", "", f"Méthode : {cal['method']}.", ""])
    for layer in ("artwork-major", "artwork-minor"):
        rc = cal["reference_command_ratio"]; rb = cal["reference_bbox_ratio"]; rg = cal["bbox_pct_range"]; pv = cal["poverty_command_p10"]  # type: ignore[index]
        lines.append(f"- `{layer}` : commandes au moins {rc.get(layer, 0)} fois la médiane des références, occupation au moins {rb.get(layer, 0)} fois celle des références, occupation observée entre {rg.get(layer, [0, 0])[0]} % et {rg.get(layer, [0, 0])[1]} % du carré, seuil de pauvreté {pv.get(layer, 0)} commandes (p10).")  # type: ignore[union-attr]
    lines.extend(
        [
            "",
            "## Attributs et éléments",
            "",
            f"- Attributs de `<path>` observés : {json.dumps(profile['path_attribute_counts'], ensure_ascii=False)}.",
            "- Les symboles officiels utilisent des `<path>` ; les primitives `<line>`, `<rect>`, `<circle>` et les groupes stroke ne font pas partie du corpus.",
            "",
            "## Règles de création DSFR-like",
            "",
        ]
    )
    lines.extend(f"- {rule}" for rule in profile["rules"])  # type: ignore[union-attr]
    target.write_text("\n".join(lines) + "\n", encoding="utf-8")


def render_markdown(profile: dict[str, object]) -> str:
    """Rend le Markdown du profil sans rien écrire ; lève si le profil est incomplet."""
    with tempfile.TemporaryDirectory() as tmp:
        buffer = Path(tmp) / "profile.md"
        write_markdown(profile, buffer)
        return buffer.read_text(encoding="utf-8")


def write_outputs(profile: dict[str, object], json_output: Path, md_output: Path) -> None:
    """Écrit le couple JSON + Markdown seulement si les deux rendus réussissent."""
    markdown = render_markdown(profile)
    payload = json.dumps(profile, ensure_ascii=False, indent=2) + "\n"
    json_output.parent.mkdir(parents=True, exist_ok=True)
    md_output.parent.mkdir(parents=True, exist_ok=True)
    json_output.write_text(payload, encoding="utf-8")
    md_output.write_text(markdown, encoding="utf-8")


def build_parser() -> argparse.ArgumentParser:
    references = Path(__file__).resolve().parents[1] / "references"
    parser = argparse.ArgumentParser(description="Analyser le corpus DSFR officiel embarqué.")
    parser.add_argument("--corpus-root", default=str(default_corpus_root()), help="Dossier dsfr-officiels.")
    parser.add_argument("--json-output", default=str(references / "dsfr-style-profile.json"), help="Fichier JSON de sortie (défaut : references/ du skill).")
    parser.add_argument("--md-output", default=str(references / "dsfr-style-profile.md"), help="Fichier Markdown de sortie (défaut : references/ du skill).")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    try:
        root = Path(args.corpus_root).expanduser().resolve()
        profile = build_profile(root)
        json_output = Path(args.json_output).expanduser().resolve()
        md_output = Path(args.md_output).expanduser().resolve()
        write_outputs(profile, json_output, md_output)
    except (ValueError, OSError, KeyError) as exc:
        print(f"Erreur : {exc}", file=sys.stderr)
        return 1
    print(json_output)
    print(md_output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
