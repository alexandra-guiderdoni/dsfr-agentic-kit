#!/usr/bin/env python3
"""Construit l'étalon original-dsfr-like « horloge » : SVG 80x80, trois calques, chemins remplis uniquement.

Grammaire empruntée : anneau ouvert à trait de 2 px et terminaisons rondes de system/success, accent rouge
centré de map/compass, points décoratifs à rayon 1 en périphérie. Aucun chemin officiel n'est copié.
V2 : l'anneau est ouvert en haut à droite, comme les références, pour éviter la régularité d'icône de bibliothèque.
"""

from __future__ import annotations

import math
from pathlib import Path

CX = CY = 40.0


def fmt(value: float) -> str:
    text = f"{value:.2f}".rstrip("0").rstrip(".")
    return "0" if text in ("", "-0", "-") else text


def disc(cx: float, cy: float, r: float) -> str:
    return f"M{fmt(cx - r)} {fmt(cy)}a{fmt(r)} {fmt(r)} 0 1 0 {fmt(2 * r)} 0a{fmt(r)} {fmt(r)} 0 1 0 {fmt(-2 * r)} 0Z"


def ring(cx: float, cy: float, outer: float, inner: float) -> str:
    """Anneau plein : cercle extérieur et cercle intérieur en sens inverse, règle evenodd inutile."""
    outer_path = f"M{fmt(cx - outer)} {fmt(cy)}a{fmt(outer)} {fmt(outer)} 0 1 0 {fmt(2 * outer)} 0a{fmt(outer)} {fmt(outer)} 0 1 0 {fmt(-2 * outer)} 0Z"
    inner_path = f"M{fmt(cx - inner)} {fmt(cy)}a{fmt(inner)} {fmt(inner)} 0 1 1 {fmt(2 * inner)} 0a{fmt(inner)} {fmt(inner)} 0 1 1 {fmt(-2 * inner)} 0Z"
    return outer_path + inner_path


def arc_band(r_mid: float, width: float, start_deg: float, end_deg: float) -> str:
    """Portion d'anneau à bouts ronds : trait de largeur donnée le long d'un arc, angles horaires (0 = midi)."""
    r = width / 2
    outer, inner = r_mid + r, r_mid - r
    sweep = (end_deg - start_deg) % 360
    large = 1 if sweep > 180 else 0
    (ox1, oy1), (ox2, oy2) = polar(start_deg, outer), polar(end_deg, outer)
    (ix1, iy1), (ix2, iy2) = polar(start_deg, inner), polar(end_deg, inner)
    return (
        f"M{fmt(ox1)} {fmt(oy1)}A{fmt(outer)} {fmt(outer)} 0 {large} 1 {fmt(ox2)} {fmt(oy2)}"
        f"A{fmt(r)} {fmt(r)} 0 0 1 {fmt(ix2)} {fmt(iy2)}"
        f"A{fmt(inner)} {fmt(inner)} 0 {large} 0 {fmt(ix1)} {fmt(iy1)}"
        f"A{fmt(r)} {fmt(r)} 0 0 1 {fmt(ox1)} {fmt(oy1)}Z"
    )


def capsule(x1: float, y1: float, x2: float, y2: float, width: float) -> str:
    """Segment à bouts ronds, simulant un trait de largeur donnée par une forme remplie."""
    r = width / 2
    dx, dy = x2 - x1, y2 - y1
    length = math.hypot(dx, dy)
    if length == 0:
        raise ValueError("capsule : les deux extrémités sont confondues, segment de longueur nulle.")
    nx, ny = -dy / length * r, dx / length * r
    return (
        f"M{fmt(x1 + nx)} {fmt(y1 + ny)}L{fmt(x2 + nx)} {fmt(y2 + ny)}"
        f"a{fmt(r)} {fmt(r)} 0 0 1 {fmt(-2 * nx)} {fmt(-2 * ny)}"
        f"L{fmt(x1 - nx)} {fmt(y1 - ny)}a{fmt(r)} {fmt(r)} 0 0 1 {fmt(2 * nx)} {fmt(2 * ny)}Z"
    )


def polar(angle_deg: float, radius: float) -> tuple[float, float]:
    angle = math.radians(angle_deg - 90)
    return CX + radius * math.cos(angle), CY + radius * math.sin(angle)


def build() -> str:
    major = [arc_band(29, 2, 75, 30)]  # anneau ouvert entre 1 h et 2 h 30, comme system/success
    for hour in range(12):
        angle = hour * 30
        if hour % 3 == 0:
            (x1, y1), (x2, y2) = polar(angle, 25), polar(angle, 20)
            major.append(capsule(x1, y1, x2, y2, 2))
        else:
            x, y = polar(angle, 23)
            major.append(disc(x, y, 1))
    minor = [
        capsule(CX, CY, *polar(0, 14), 2),  # aiguille des heures vers midi
        capsule(CX, CY, *polar(90, 20), 2),  # aiguille des minutes vers 3 h
        ring(CX, CY, 3, 1.4),  # axe central évidé
    ]
    decorative = [disc(12, 10, 1), disc(68, 9, 1), disc(10, 70, 1), disc(70, 71, 1)]
    return f"""<svg width="80px" height="80px" viewBox="0 0 80 80" xmlns="http://www.w3.org/2000/svg">
	<style>
		.fr-artwork-decorative {{
			fill: #ECECFF;
		}}
		.fr-artwork-minor {{
			fill: #E1000F;
		}}
		.fr-artwork-major {{
			fill: #000091;
		}}
	</style>
	<symbol id="artwork-decorative">
		<path d="{''.join(decorative)}"/>
	</symbol>
	<symbol id="artwork-minor">
		<path d="{''.join(minor)}"/>
	</symbol>
	<symbol id="artwork-major">
		<path d="{''.join(major)}"/>
	</symbol>
	<use class="fr-artwork-decorative" href="#artwork-decorative"/>
	<use class="fr-artwork-minor" href="#artwork-minor"/>
	<use class="fr-artwork-major" href="#artwork-major"/>
</svg>
"""


if __name__ == "__main__":
    target = Path(__file__).resolve().parent / "horloge.svg"
    target.write_text(build(), encoding="utf-8")
    print(target)
