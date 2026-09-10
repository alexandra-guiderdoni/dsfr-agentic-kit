#!/usr/bin/env python3
"""Reproduit, copie ou génère des pictogrammes SVG pour supports DSFR."""

# PDG-LARGE-FILE-JUSTIFICATION: ce script reste dense pour garder le skill
# autonome : il porte une seule responsabilité, générer déterministiquement un
# catalogue ciblé de pictogrammes SVG sans dépendance externe ni assets cachés.

from __future__ import annotations

import argparse
import difflib
import functools
import hashlib
import json
import math
import os
import re
import shutil
import subprocess
import tempfile
import sys
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from pathlib import Path
from xml.sax.saxutils import escape


PRESETS = {
    "dsfr": {"color": "#000091", "accent": "#E1000F", "background": "#F6F6F6"},
    "slides-ia": {"color": "#001070", "accent": "#E44850", "background": "#F2F3F7"},
}

HEX_COLOR = re.compile(r"^#[0-9A-Fa-f]{6}$")
STYLE_FILL_RE = re.compile(r"\.([a-zA-Z0-9_-]+)\s*\{[^}]*fill:\s*([^;]+);", re.MULTILINE)
DSFR_NAME = re.compile(r"^[a-z0-9-]+/[a-z0-9-]+$")
DSFR_LAYER_IDS = ("artwork-decorative", "artwork-minor", "artwork-major")
DSFR_LAYER_CLASSES = ("fr-artwork-decorative", "fr-artwork-minor", "fr-artwork-major")
DSFR_LAYER_FILLS = {
    "fr-artwork-decorative": "#ECECFF",
    "fr-artwork-minor": "#E1000F",
    "fr-artwork-major": "#000091",
}
DSFR_CANONICAL_USE_HREFS = tuple(f"#{layer}" for layer in DSFR_LAYER_IDS)
DSFR_KNOWN_USE_EXCEPTIONS = {
    (("#artwork-major", "#artwork-minor", "#artwork-major"), ("fr-artwork-major", "fr-artwork-minor", "fr-artwork-major"))
}
DSFR_NAMES = (
    "accessibility/accessibility",
    "accessibility/ear-off",
    "accessibility/eye-off",
    "accessibility/mental-disabilities",
    "accessibility/wheelchair",
    "buildings/base",
    "buildings/city-hall",
    "buildings/companie",
    "buildings/factory",
    "buildings/house",
    "buildings/nuclear-plant",
    "buildings/school",
    "digital/application",
    "digital/avatar",
    "digital/calendar",
    "digital/coding",
    "digital/data-visualization",
    "digital/ecosystem",
    "digital/in-progress",
    "digital/innovation",
    "digital/internet",
    "digital/mail-send",
    "digital/search",
    "digital/self-training",
    "digital/smartphone",
    "document/archive",
    "document/binders",
    "document/conclusion",
    "document/contract",
    "document/document",
    "document/document-add",
    "document/document-download",
    "document/document-search",
    "document/document-signature",
    "document/driving-licence",
    "document/driving-license-new",
    "document/international-driving-license",
    "document/international-driving-license-new",
    "document/national-identity-card",
    "document/national-identity-card-passport",
    "document/passport",
    "document/presse-card",
    "document/sign-document",
    "document/tax-stamp",
    "document/vehicle-registration",
    "environment/environment",
    "environment/food",
    "environment/grocery",
    "environment/human-cooperation",
    "environment/leaf",
    "environment/moon",
    "environment/mountain",
    "environment/sun",
    "environment/tree",
    "health/doctor",
    "health/health",
    "health/hospital",
    "health/medical-research",
    "health/vaccine",
    "health/virus",
    "institutions/army-tank",
    "institutions/astronaut",
    "institutions/firefighter",
    "institutions/gendarmerie",
    "institutions/justice",
    "institutions/money",
    "institutions/navy-anchor",
    "institutions/navy-bachi",
    "institutions/police",
    "leisure/art",
    "leisure/audio",
    "leisure/book",
    "leisure/catalog",
    "leisure/community",
    "leisure/culture",
    "leisure/digital-art",
    "leisure/paint",
    "leisure/pictures",
    "leisure/podcast",
    "leisure/video",
    "leisure/video-games",
    "map/airport",
    "map/backpack",
    "map/compass",
    "map/location-france",
    "map/location-overseas-france",
    "map/luggage",
    "map/map",
    "map/map-pin",
    "map/travel-back",
    "system/connection-lost",
    "system/error",
    "system/flow-list",
    "system/flow-settings",
    "system/information",
    "system/language",
    "system/notification",
    "system/padlock",
    "system/success",
    "system/system",
    "system/technical-error",
    "system/warning",
)
DEFAULT_REPLICA_ROOT = Path(__file__).resolve().parents[1] / "pictos-svg" / "dsfr-officiels"
DEFAULT_OFFICIAL_CACHE_ROOT = Path.home() / ".cache" / "dsfr-official-cache"


DSFR_VERSION_RE = re.compile(r"^\d+\.\d+\.\d+$")


def declared_dsfr_version(manifest: dict[str, object]) -> str | None:
    """Version DSFR déclarée par un manifeste (X.Y.Z), ou None si absente ou malformée : jamais une valeur
    inutilisable dans un chemin de cache ou une commande npm."""
    version = manifest.get("dsfr_version")
    return version if isinstance(version, str) and DSFR_VERSION_RE.match(version) else None


def official_cache_root() -> Path:
    """Cache local du paquet officiel @gouvfr/dsfr, partagé avec les contrôles du pack (DSFR_OFFICIAL_CACHE_DIR)."""
    return Path(os.environ.get("DSFR_OFFICIAL_CACHE_DIR") or DEFAULT_OFFICIAL_CACHE_ROOT).expanduser()


def official_cache_pictograms_dir(version: str) -> Path:
    return official_cache_root() / f"gouvfr-dsfr-{version}" / "package" / "dist" / "artwork" / "pictograms"


def resolve_official_svg(replica_root: Path, item: dict[str, object], version: str | None, *, required: bool = True) -> Path | None:
    """Chemin du SVG officiel d'une entrée du manifeste : copie embarquée, sinon paquet officiel en cache
    (contrôlé par sha256), sinon NOT VERIFIED. Une distribution qui ne redistribue pas les SVG officiels
    reste ainsi utilisable dès que le paquet @gouvfr/dsfr de la version déclarée est en cache."""
    embedded = replica_root / str(item["file"])
    if embedded.exists():
        return embedded
    source = str(item.get("source") or f"{item['name']}.svg")
    expected = str(item.get("sha256") or "").strip().lower()
    if version and "/" not in version and ".." not in source and not source.startswith("/"):
        candidate = official_cache_pictograms_dir(version) / source
        if candidate.is_file():
            if not expected:
                raise ValueError(
                    f"NOT VERIFIED: source officielle absente : {embedded.name} n'est pas embarqué et son entrée de manifeste ne déclare "
                    f"pas de sha256 ; la reproduction depuis le cache officiel ({candidate}) ne serait pas contrôlable."
                )
            digest = file_sha256(candidate)
            if digest != expected:
                raise ValueError(
                    f"{candidate} ne correspond pas au manifeste embarqué (sha256 {digest[:12]}…, attendu {expected[:12]}…) : "
                    f"paquet officiel {version} altéré ou version différente."
                )
            return candidate
    if not required:
        return None
    if version:
        hint = (
            f"obtenir le paquet officiel avec : npm pack @gouvfr/dsfr@{version} --ignore-scripts, puis extraire l'archive sous "
            f"{official_cache_root() / f'gouvfr-dsfr-{version}'} (dossier package/)"
        )
    else:
        declared = item.get("dsfr_version_declared")
        hint = (f"le manifeste déclare une dsfr_version malformée ({declared!r}, attendu X.Y.Z)" if declared
                else "le manifeste ne déclare pas de dsfr_version") + " : impossible de résoudre le paquet officiel en cache"
    raise ValueError(
        f"NOT VERIFIED: source officielle absente : {embedded.name} n'est ni embarqué ({embedded}) ni dans le cache officiel "
        f"({official_cache_root()}) ; {hint}."
    )


@dataclass(frozen=True)
class IconSpec:
    title: str
    desc: str
    tags: tuple[str, ...]
    builder: str


def path(d: str) -> str:
    return f'<path d="{d}"/>'


def line(x1: int, y1: int, x2: int, y2: int) -> str:
    return f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}"/>'


def rect(x: int, y: int, width: int, height: int, rx: int = 0) -> str:
    return f'<rect x="{x}" y="{y}" width="{width}" height="{height}" rx="{rx}"/>'


def circle(cx: int, cy: int, r: int) -> str:
    return f'<circle cx="{cx}" cy="{cy}" r="{r}"/>'


def polyline(points: str) -> str:
    return f'<polyline points="{points}"/>'


def filled_circle(cx: int, cy: int, r: int, fill: str) -> str:
    return f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="{fill}" stroke="none"/>'


def stroke_group(elements: list[str], stroke: str, stroke_width: int) -> str:
    body = "\n    ".join(elements)
    return (
        f'<g fill="none" stroke="{stroke}" stroke-width="{stroke_width}" '
        f'stroke-linecap="round" stroke-linejoin="round">\n    {body}\n  </g>'
    )


def build_document(color: str, accent: str, stroke_width: int) -> list[str]:
    main = [
        path("M72 36H154L194 76V220H72Z"),
        path("M154 36V78H194"),
        line(96, 116, 168, 116),
        line(96, 146, 168, 146),
        line(96, 176, 142, 176),
    ]
    return [stroke_group(main, color, stroke_width), stroke_group([line(96, 202, 128, 202)], accent, stroke_width)]


def build_pencil(color: str, accent: str, stroke_width: int) -> list[str]:
    main = [
        path("M66 190L170 86L204 120L100 224L60 230Z"),
        line(150, 106, 184, 140),
        line(84, 188, 102, 206),
        path("M170 86L184 72C192 64 204 64 212 72C220 80 220 92 212 100L204 120"),
    ]
    tip = [
        path("M60 230L72 198L92 218Z"),
    ]
    return [stroke_group(main, color, stroke_width), stroke_group(tip, accent, stroke_width)]


def build_house(color: str, accent: str, stroke_width: int) -> list[str]:
    main = [
        path("M42 124L128 54L214 124"),
        path("M68 120V216H188V120"),
        path("M162 82V58H192V106"),
        path("M112 216V170C112 156 118 148 128 148C138 148 144 156 144 170V216"),
        rect(82, 136, 28, 30, 0),
        rect(146, 136, 28, 30, 0),
    ]
    accent_parts = [
        line(92, 216, 164, 216),
        filled_circle(140, 184, 5, accent),
    ]
    return [stroke_group(main, color, stroke_width), stroke_group(accent_parts[:1], accent, stroke_width), accent_parts[1]]


def build_ai(color: str, accent: str, stroke_width: int) -> list[str]:
    pins = [
        line(92, 44, 92, 68),
        line(128, 44, 128, 68),
        line(164, 44, 164, 68),
        line(92, 188, 92, 212),
        line(128, 188, 128, 212),
        line(164, 188, 164, 212),
        line(44, 92, 68, 92),
        line(44, 128, 68, 128),
        line(44, 164, 68, 164),
        line(188, 92, 212, 92),
        line(188, 128, 212, 128),
        line(188, 164, 212, 164),
    ]
    main = [rect(68, 68, 120, 120, 10), circle(128, 128, 28), line(104, 128, 152, 128), line(128, 104, 128, 152)]
    return [stroke_group(pins + main, color, stroke_width), filled_circle(128, 128, 8, accent)]


def build_user(color: str, accent: str, stroke_width: int) -> list[str]:
    main = [
        circle(128, 82, 34),
        path("M66 206C76 158 96 134 128 134C160 134 180 158 190 206"),
        line(92, 206, 164, 206),
    ]
    return [stroke_group(main, color, stroke_width), stroke_group([line(96, 126, 160, 126)], accent, stroke_width)]


def build_shield(color: str, accent: str, stroke_width: int) -> list[str]:
    main = [path("M128 32L198 58V112C198 160 168 198 128 222C88 198 58 160 58 112V58Z")]
    check = [polyline("92,126 118,152 166,96")]
    return [stroke_group(main, color, stroke_width), stroke_group(check, accent, stroke_width)]


def build_code(color: str, accent: str, stroke_width: int) -> list[str]:
    main = [
        polyline("94,82 48,128 94,174"),
        polyline("162,82 208,128 162,174"),
        line(140, 66, 116, 190),
    ]
    return [stroke_group(main, color, stroke_width), stroke_group([line(80, 208, 176, 208)], accent, stroke_width)]


def build_calendar(color: str, accent: str, stroke_width: int) -> list[str]:
    main = [
        rect(54, 58, 148, 154, 0),
        line(54, 94, 202, 94),
        line(88, 38, 88, 72),
        line(168, 38, 168, 72),
        line(84, 126, 104, 126),
        line(124, 126, 144, 126),
        line(164, 126, 184, 126),
        line(84, 162, 104, 162),
        line(124, 162, 144, 162),
    ]
    return [stroke_group(main, color, stroke_width), stroke_group([polyline("164,164 174,174 192,148")], accent, stroke_width)]


def build_cost(color: str, accent: str, stroke_width: int) -> list[str]:
    main = [
        circle(128, 128, 78),
        path("M154 82C142 74 112 76 102 102C88 138 110 178 154 172"),
        line(84, 118, 144, 118),
        line(84, 142, 138, 142),
    ]
    return [stroke_group(main, color, stroke_width), stroke_group([line(72, 204, 184, 204)], accent, stroke_width)]


def build_chain(color: str, accent: str, stroke_width: int) -> list[str]:
    main = [
        path("M98 94L82 110C62 130 62 162 82 182C102 202 134 202 154 182L170 166"),
        path("M86 154L102 138"),
        path("M158 162L174 146C194 126 194 94 174 74C154 54 122 54 102 74L86 90"),
        path("M170 102L154 118"),
    ]
    return [stroke_group(main, color, stroke_width), filled_circle(128, 128, 7, accent)]


def build_server(color: str, accent: str, stroke_width: int) -> list[str]:
    main = [
        rect(54, 54, 148, 44, 0),
        rect(54, 106, 148, 44, 0),
        rect(54, 158, 148, 44, 0),
        line(80, 76, 116, 76),
        line(80, 128, 116, 128),
        line(80, 180, 116, 180),
    ]
    dots = [filled_circle(172, 76, 6, accent), filled_circle(172, 128, 6, accent), filled_circle(172, 180, 6, accent)]
    return [stroke_group(main, color, stroke_width)] + dots


def build_rocket(color: str, accent: str, stroke_width: int) -> list[str]:
    main = [
        path("M124 174C98 166 82 150 74 124C102 114 124 88 140 48C178 64 194 80 208 116C168 132 142 154 124 174Z"),
        circle(154, 100, 16),
        path("M82 144L50 176L92 166"),
        path("M132 194L100 226L110 184"),
    ]
    flame = [path("M74 174C56 182 48 198 46 216C64 212 80 204 88 186")]
    return [stroke_group(main, color, stroke_width), stroke_group(flame, accent, stroke_width)]


def build_supervision(color: str, accent: str, stroke_width: int) -> list[str]:
    main = [
        rect(46, 58, 164, 112, 0),
        line(100, 206, 156, 206),
        line(128, 170, 128, 206),
        polyline("72,138 102,112 128,126 160,88 190,102"),
    ]
    return [stroke_group(main, color, stroke_width), filled_circle(160, 88, 7, accent)]


def build_support(color: str, accent: str, stroke_width: int) -> list[str]:
    main = [
        path("M62 136V118C62 80 92 50 128 50C164 50 194 80 194 118V136"),
        rect(48, 126, 28, 50, 6),
        rect(180, 126, 28, 50, 6),
        path("M194 174C188 202 166 216 132 216"),
    ]
    return [stroke_group(main, color, stroke_width), filled_circle(128, 216, 7, accent)]


def build_data(color: str, accent: str, stroke_width: int) -> list[str]:
    main = [
        path("M64 70C64 52 192 52 192 70V186C192 204 64 204 64 186Z"),
        path("M64 70C64 88 192 88 192 70"),
        path("M64 110C64 128 192 128 192 110"),
        path("M64 150C64 168 192 168 192 150"),
    ]
    return [stroke_group(main, color, stroke_width), stroke_group([line(92, 206, 164, 206)], accent, stroke_width)]


def build_lock(color: str, accent: str, stroke_width: int) -> list[str]:
    main = [
        rect(60, 108, 136, 100, 0),
        path("M88 108V82C88 56 106 38 128 38C150 38 168 56 168 82V108"),
        line(128, 148, 128, 174),
    ]
    return [stroke_group(main, color, stroke_width), filled_circle(128, 144, 8, accent)]


def build_check(color: str, accent: str, stroke_width: int) -> list[str]:
    main = [circle(128, 128, 82)]
    check = [polyline("82,130 116,164 178,92")]
    return [stroke_group(main, color, stroke_width), stroke_group(check, accent, stroke_width)]


def build_warning(color: str, accent: str, stroke_width: int) -> list[str]:
    main = [path("M128 42L220 206H36Z")]
    mark = [line(128, 96, 128, 146)]
    return [stroke_group(main, color, stroke_width), stroke_group(mark, accent, stroke_width), filled_circle(128, 176, 7, accent)]


def build_api(color: str, accent: str, stroke_width: int) -> list[str]:
    main = [
        circle(74, 128, 26),
        circle(182, 76, 26),
        circle(182, 180, 26),
        line(98, 116, 158, 88),
        line(98, 140, 158, 168),
    ]
    return [stroke_group(main, color, stroke_width), filled_circle(74, 128, 7, accent)]


def build_test(color: str, accent: str, stroke_width: int) -> list[str]:
    main = [
        rect(68, 48, 120, 164, 0),
        rect(96, 34, 64, 30, 0),
        line(94, 108, 162, 108),
        line(94, 144, 162, 144),
    ]
    return [stroke_group(main, color, stroke_width), stroke_group([polyline("94,176 116,196 162,154")], accent, stroke_width)]


def build_production(color: str, accent: str, stroke_width: int) -> list[str]:
    main = [
        rect(48, 132, 160, 72, 0),
        path("M48 132L86 100L116 132L154 92L208 132"),
        line(78, 204, 78, 170),
        line(112, 204, 112, 170),
        line(146, 204, 146, 170),
        line(180, 204, 180, 170),
    ]
    return [stroke_group(main, color, stroke_width), filled_circle(180, 72, 8, accent)]


def build_accessibility(color: str, accent: str, stroke_width: int) -> list[str]:
    main = [
        circle(128, 42, 14),
        line(128, 64, 128, 142),
        line(76, 88, 180, 88),
        line(128, 142, 94, 208),
        line(128, 142, 162, 208),
        circle(128, 128, 94),
    ]
    return [stroke_group(main, color, stroke_width), filled_circle(128, 42, 5, accent)]


BUILDERS = {
    "accessibility": build_accessibility,
    "ai": build_ai,
    "api": build_api,
    "calendar": build_calendar,
    "chain": build_chain,
    "check": build_check,
    "code": build_code,
    "cost": build_cost,
    "data": build_data,
    "document": build_document,
    "house": build_house,
    "lock": build_lock,
    "pencil": build_pencil,
    "production": build_production,
    "rocket": build_rocket,
    "server": build_server,
    "shield": build_shield,
    "supervision": build_supervision,
    "support": build_support,
    "test": build_test,
    "user": build_user,
    "warning": build_warning,
}

CATALOG = {
    "accessibility": IconSpec("Accessibilité", "Personne stylisée dans un cercle, pour inclusion ou accessibilité.", ("a11y", "service"), "accessibility"),
    "ai": IconSpec("IA", "Puce électronique avec noyau central, pour IA ou automatisation contrôlée.", ("ia", "modèle"), "ai"),
    "api": IconSpec("API", "Trois nœuds connectés, pour API ou intégration de services.", ("service", "intégration"), "api"),
    "calendar": IconSpec("Calendrier", "Calendrier avec coche, pour jalon ou échéance.", ("temps", "planning"), "calendar"),
    "chain": IconSpec("Chaîne", "Deux maillons reliés, pour dépendance ou continuité.", ("lien", "flux"), "chain"),
    "check": IconSpec("Validation", "Coche dans un cercle, pour gate ou conformité.", ("statut", "conformité"), "check"),
    "code": IconSpec("Code", "Chevrons de code et barre oblique, pour développement.", ("dev", "script"), "code"),
    "cost": IconSpec("Coût", "Symbole euro dans un cercle, pour budget ou coût.", ("budget", "finance"), "cost"),
    "data": IconSpec("Données", "Base de données cylindrique, pour données ou capitalisation.", ("data", "base"), "data"),
    "document": IconSpec("Document", "Page avec angle plié et lignes, pour source ou livrable.", ("fichier", "source"), "document"),
    "house": IconSpec("Maison", "Maison filaire avec porte et fenêtres, pour lieu, accueil ou habitat.", ("lieu", "accueil"), "house"),
    "lock": IconSpec("Verrou", "Cadenas, pour protection ou accès maîtrisé.", ("sécurité", "accès"), "lock"),
    "pencil": IconSpec("Crayon", "Crayon filaire, pour édition, annotation ou écriture.", ("édition", "annotation"), "pencil"),
    "production": IconSpec("Production", "Bâtiment de production stylisé, pour exploitation.", ("prod", "exploitation"), "production"),
    "rocket": IconSpec("Lancement", "Fusée filaire, pour POC ou passage à l’échelle.", ("poc", "déploiement"), "rocket"),
    "server": IconSpec("Serveur", "Pile de serveurs, pour infrastructure ou runtime.", ("infra", "hébergement"), "server"),
    "shield": IconSpec("Bouclier", "Bouclier avec coche, pour sécurité ou maîtrise.", ("sécurité", "souveraineté"), "shield"),
    "supervision": IconSpec("Supervision", "Écran avec courbe, pour monitoring ou pilotage.", ("mesure", "pilotage"), "supervision"),
    "support": IconSpec("Support", "Casque d’assistance, pour support ou maintien.", ("assistance", "run"), "support"),
    "test": IconSpec("Tests", "Presse-papiers avec coche, pour recette ou QA.", ("qualité", "recette"), "test"),
    "user": IconSpec("Utilisateur", "Profil utilisateur, pour agent ou équipe.", ("personne", "équipe"), "user"),
    "warning": IconSpec("Alerte", "Triangle d’avertissement, pour risque ou blocage.", ("risque", "alerte"), "warning"),
}


def slugify(value: str) -> str:
    slug = re.sub(r"[^a-zA-Z0-9_-]+", "-", value.lower()).strip("-")
    return slug or "picto"


def validate_color(value: str, label: str) -> str:
    if not HEX_COLOR.match(value):
        raise ValueError(f"{label} doit être une couleur hexadécimale #RRGGBB : {value}")
    return value.upper()


def render_svg(
    name: str,
    title: str,
    desc: str,
    color: str,
    accent: str,
    background: str,
    background_color: str,
    size: int,
    stroke_width: int,
) -> str:
    spec = CATALOG[name]
    builder = BUILDERS[spec.builder]
    parts = builder(color, accent, stroke_width)
    title_id = f"title-{slugify(name)}"
    desc_id = f"desc-{slugify(name)}"

    if background == "none":
        background_svg = ""
    elif background == "tile":
        background_svg = f'  <rect x="10" y="10" width="236" height="236" rx="0" fill="{background_color}"/>'
    elif background == "disk":
        background_svg = f'  <circle cx="128" cy="128" r="118" fill="{background_color}" stroke="none"/>'
    else:
        raise ValueError(f"Fond inconnu : {background}")

    body = "\n  ".join(parts)
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}" '
        f'viewBox="0 0 256 256" role="img" aria-labelledby="{title_id} {desc_id}">\n'
        f'  <title id="{title_id}">{escape(title)}</title>\n'
        f'  <desc id="{desc_id}">{escape(desc)}</desc>\n'
        f'{background_svg + chr(10) if background_svg else ""}'
        f'  {body}\n'
        f'</svg>\n'
    )


def parse_icon_names(value: str) -> list[str]:
    if value == "all":
        return sorted(CATALOG)
    names = [item.strip() for item in value.split(",") if item.strip()]
    if not names:
        raise ValueError("Aucun picto demandé.")
    unknown = [name for name in names if name not in CATALOG]
    if unknown:
        suggestions = []
        for name in unknown:
            close = difflib.get_close_matches(name, CATALOG.keys(), n=3)
            suffix = f" Suggestions : {', '.join(close)}." if close else ""
            suggestions.append(f"{name}.{suffix}")
        raise ValueError("Picto inconnu : " + " ".join(suggestions))
    return names


def local_name(tag: str) -> str:
    return tag.rsplit("}", 1)[-1]


def style_fills(root: ET.Element) -> dict[str, str]:
    fills: dict[str, str] = {}
    for element in root.iter():
        if local_name(element.tag) == "style" and element.text:
            for class_name, fill in STYLE_FILL_RE.findall(element.text):
                fills[class_name] = fill.strip().upper()
    return fills


def use_href(element: ET.Element) -> str | None:
    return element.attrib.get("href") or element.attrib.get("{http://www.w3.org/1999/xlink}href")


def file_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def normalize_dsfr_name(value: str) -> str:
    name = value.strip().removesuffix(".svg").strip("/")
    if not DSFR_NAME.match(name):
        raise ValueError(
            "Nom DSFR invalide : "
            f"{value}. Utiliser le format famille/nom, sans espace ni remontée de chemin."
        )
    return name


@functools.lru_cache(maxsize=None)
def discover_dsfr_names(pictograms_dir: Path) -> list[str]:
    names = []
    for svg_path in sorted(pictograms_dir.rglob("*.svg")):
        relative = svg_path.relative_to(pictograms_dir).with_suffix("").as_posix()
        if DSFR_NAME.match(relative):
            names.append(relative)
    return names


def parse_dsfr_names(value: str, pictograms_dir: Path) -> list[str]:
    if value == "all":
        names = discover_dsfr_names(pictograms_dir)
        if not names:
            raise ValueError(f"Aucun pictogramme DSFR trouvé dans {pictograms_dir} : attendu des fichiers famille/nom.svg.")
        return names
    names = list(dict.fromkeys(normalize_dsfr_name(item) for item in value.split(",") if item.strip()))
    if not names:
        raise ValueError("Aucun pictogramme DSFR demandé.")
    return names


def parse_replica_names(value: str, available_names: list[str]) -> list[str]:
    if value == "all":
        if not available_names:
            raise ValueError("Aucun pictogramme dans le corpus de reproduction : manifest.json ne déclare aucune icône.")
        return sorted(available_names)
    names = list(dict.fromkeys(normalize_dsfr_name(item) for item in value.split(",") if item.strip()))
    if not names:
        raise ValueError("Aucun pictogramme DSFR demandé.")
    unknown = [name for name in names if name not in available_names]
    if unknown:
        suggestions = []
        for name in unknown:
            close = difflib.get_close_matches(name, available_names, n=3)
            suffix = f" Suggestions : {', '.join(close)}." if close else ""
            suggestions.append(f"{name}.{suffix}")
        raise ValueError("Picto DSFR absent du corpus embarqué : " + " ".join(suggestions))
    return names


def resolve_pictograms_dir(root: str | None) -> Path:
    if not root:
        raise ValueError("--dsfr-artwork-root est requis avec --source dsfr-artwork.")
    base = Path(root).expanduser().resolve()
    candidates = [
        base / "dist" / "artwork" / "pictograms",
        base / "artwork" / "pictograms",
        base / "pictograms",
        base / "node_modules" / "@gouvfr" / "dsfr-artwork" / "dist" / "artwork" / "pictograms",
        base / "node_modules" / "@gouvfr" / "dsfr" / "dist" / "artwork" / "pictograms",
        base,
    ]
    for candidate in candidates:
        if candidate.is_dir() and discover_dsfr_names(candidate):
            return candidate
    raise ValueError(
        "Dossier de pictogrammes DSFR introuvable. Fournir le chemin vers "
        "dist/artwork/pictograms ou un dossier qui contient des sous-dossiers de SVG."
    )


# Couleurs à indice -main de la palette DSFR, valeur du thème clair, relevées dans
# @gouvfr/dsfr v1.15.2 src/module/color/variable/_options.scss. La documentation
# « Pictogramme » du DSFR autorise la personnalisation du calque minor avec l'indice -main.
DSFR_MAIN_PALETTE = {
    "grey-main-525": "#7B7B7B",
    "blue-france-main-525": "#6A6AF4",
    "red-marianne-main-472": "#E1000F",
    "info-main-525": "#0078F3",
    "success-main-525": "#1F8D49",
    "warning-main-525": "#D64D00",
    "error-main-525": "#F60700",
    "green-tilleul-verveine-main-707": "#B7A73F",
    "green-bourgeon-main-640": "#68A532",
    "green-emeraude-main-632": "#00A95F",
    "green-menthe-main-548": "#009081",
    "green-archipel-main-557": "#009099",
    "blue-ecume-main-400": "#465F9D",
    "blue-cumulus-main-526": "#417DC4",
    "purple-glycine-main-494": "#A558A0",
    "pink-macaron-main-689": "#E18B76",
    "pink-tuile-main-556": "#CE614A",
    "yellow-tournesol-main-731": "#C8AA39",
    "yellow-moutarde-main-679": "#C3992A",
    "orange-terre-battue-main-645": "#E4794A",
    "brown-cafe-creme-main-782": "#D1B781",
    "brown-caramel-main-648": "#C08C65",
    "brown-opera-main-680": "#BD987A",
    "beige-gris-galet-main-702": "#AEA397",
}
DSFR_MAIN_PALETTE_SOURCE = "@gouvfr/dsfr src/module/color/variable/_options.scss, valeur du thème clair"
MIN_GRAPHIC_CONTRAST = 3.0  # WCAG 1.4.11, composants graphiques
MINOR_FILL_RE = re.compile(r"(\.fr-artwork-minor\s*\{[^}]*?fill:\s*)#[0-9a-fA-F]{6}(\s*;)")


def relative_luminance(hex_color: str) -> float:
    channels = [int(hex_color.lstrip("#")[index:index + 2], 16) / 255 for index in (0, 2, 4)]
    linear = [value / 12.92 if value <= 0.03928 else ((value + 0.055) / 1.055) ** 2.4 for value in channels]
    return 0.2126 * linear[0] + 0.7152 * linear[1] + 0.0722 * linear[2]


def contrast_on_white(hex_color: str) -> float:
    return round(1.05 / (relative_luminance(hex_color) + 0.05), 2)


PREFIX_RE = re.compile(r"^[A-Za-z0-9._-]*$")
EXPORT_PNG_MIN, EXPORT_PNG_MAX = 16, 4096


def validate_prefix(prefix: str) -> str:
    if not PREFIX_RE.match(prefix) or ".." in prefix or prefix.startswith("."):
        raise ValueError(f"--prefix {prefix!r} invalide : lettres, chiffres, point, tiret et souligné seulement, sans séparateur de chemin ni point initial (fichier caché).")
    return prefix


def validate_export_png_size(size: int | None) -> int | None:
    if size is None:
        return None
    if size < EXPORT_PNG_MIN or size > EXPORT_PNG_MAX:
        raise ValueError(f"--export-png doit être compris entre {EXPORT_PNG_MIN} et {EXPORT_PNG_MAX} pixels (reçu {size}).")
    return size


def resolve_minor_color(value: str | None) -> tuple[str, str] | None:
    """Retourne (nom de palette, hex) ou lève ValueError si la couleur n'est pas une -main DSFR."""
    if not value:
        return None
    name = value.strip().lower()
    if name not in DSFR_MAIN_PALETTE:
        raise ValueError(
            f"--minor-color {value!r} n'est pas une couleur à indice -main de la palette DSFR. "
            "Valeurs acceptées : " + ", ".join(sorted(DSFR_MAIN_PALETTE)) + "."
        )
    return name, DSFR_MAIN_PALETTE[name]


def recolor_minor_content(content: str, hex_color: str, label: str) -> str:
    """Remplace uniquement la couleur de .fr-artwork-minor dans le <style> ; les chemins restent intacts.

    La validation de style impose #E1000F en amont, donc la règle existe toujours au format #RRGGBB ici.
    """
    updated, count = MINOR_FILL_RE.subn(lambda match: f"{match.group(1)}{hex_color}{match.group(2)}", content, count=1)
    if count != 1:
        raise ValueError(f"{label} : règle .fr-artwork-minor introuvable dans le <style>.")
    return updated


def resolve_png_renderer_timeout() -> float:
    """Délai du moteur PNG lu dans la variable portable dédiée."""
    variable = "PICTOS_PNG_RENDERER_TIMEOUT"
    raw = os.environ.get(variable)
    if raw is None:
        # Compatibilité avec les scripts de test et les postes ayant déjà
        # configuré le nom historique, sans le documenter comme interface
        # principale.
        variable = "PICTOS_QLMANAGE_TIMEOUT"
        raw = os.environ.get(variable, "60")
    try:
        timeout = float(raw)
    except ValueError as exc:
        raise ValueError(f"{variable}={raw!r} n'est pas un nombre de secondes.") from exc
    if not math.isfinite(timeout) or not timeout > 0:
        raise ValueError(f"{variable}={raw!r} doit être un nombre fini strictement positif.")
    return timeout


def export_png(svg_path: Path, size: int) -> tuple[Path | None, str]:
    """Rend un PNG avec le premier moteur disponible sur le poste."""
    renderer = next(
        (name for name in ("qlmanage", "rsvg-convert", "inkscape") if shutil.which(name)),
        None,
    )
    if renderer is None:
        return None, "NOT VERIFIED: export PNG indisponible, qlmanage, rsvg-convert et inkscape absents"
    timeout = resolve_png_renderer_timeout()
    target = svg_path.with_name(f"{svg_path.stem}-{size}.png")
    with tempfile.TemporaryDirectory() as tmp:
        scaled = Path(tmp) / svg_path.name
        content = svg_path.read_text(encoding="utf-8")
        content = re.sub(r'width="80(px)?"', f'width="{size}"', content, count=1)
        content = re.sub(r'height="80(px)?"', f'height="{size}"', content, count=1)
        scaled.write_text(content, encoding="utf-8")
        if renderer == "qlmanage":
            command = ["qlmanage", "-t", "-s", str(size), "-o", tmp, str(scaled)]
            produced = Path(tmp) / f"{svg_path.name}.png"
        elif renderer == "rsvg-convert":
            command = ["rsvg-convert", "-w", str(size), "-h", str(size), "-o", str(target), str(scaled)]
            produced = target
        else:
            command = ["inkscape", str(scaled), "--export-filename", str(target), "--export-width", str(size), "--export-height", str(size)]
            produced = target
        try:
            result = subprocess.run(command, capture_output=True, text=True, timeout=timeout)
        except subprocess.TimeoutExpired:
            return None, f"NOT VERIFIED: export PNG interrompu, délai de {timeout:g} s dépassé par {renderer}"
        if result.returncode != 0 or not produced.exists():
            detail = (result.stderr or result.stdout or "").strip().replace("\n", " ")[:200]
            return None, f"NOT VERIFIED: export PNG échoué avec {renderer} (code {result.returncode}) : {detail or 'aucun fichier produit'}"
        if produced != target:
            shutil.copyfile(produced, target)
    return target, renderer


def write_json_atomic(path: Path, data: object) -> None:
    """Écrit un JSON par fichier temporaire puis renommage : jamais de manifeste tronqué en cas d'échec."""
    tmp = path.with_name(f".{path.name}.tmp-{os.getpid()}")
    try:
        tmp.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        os.replace(tmp, path)
    finally:
        if tmp.exists():
            tmp.unlink()


def rewrite_manifest(output_dir: Path, updater) -> None:
    manifest_path = output_dir / "manifest.json"
    if not manifest_path.exists():
        raise ValueError(f"{manifest_path} a disparu avant le post-traitement : recoloration ou export non traçables.")
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    updater(manifest)
    write_json_atomic(manifest_path, manifest)


def valid_raster_entries(listed: object) -> list[dict[str, object]]:
    """Entrées raster_exports exploitables : un dict portant un nom de fichier non vide ; le reste est ignoré."""
    if not isinstance(listed, list):
        return []
    return [entry for entry in listed if isinstance(entry, dict) and isinstance(entry.get("file"), str) and entry["file"]]


def existing_raster_exports(svg_path: Path, listed: list[dict[str, object]]) -> list[dict[str, object]]:
    """Exports PNG déjà présents sur disque pour ce SVG, fusionnés avec ceux déjà tracés."""
    known = {str(entry["file"]): entry for entry in valid_raster_entries(listed)}
    for png in sorted(svg_path.parent.glob(f"{svg_path.stem}-*.png")):
        size_text = png.stem.rsplit("-", 1)[-1]
        if png.name not in known and size_text.isdigit():
            known[png.name] = {"file": png.name, "size": int(size_text), "renderer": "inconnu (fichier préexistant)", "source": svg_path.name}
    return list(known.values())


def postprocess_dsfr_outputs(args: argparse.Namespace, generated: list[dict[str, object]]) -> None:
    """Applique --minor-color et --export-png aux copies officielles, en le traçant dans le manifeste.

    Ordre : recoloration, réécriture du manifeste, puis export PNG ; un échec d'export laisse un
    manifeste exact sur l'état recoloré et remonte un diagnostic.
    """
    minor = resolve_minor_color(getattr(args, "minor_color", None))
    png_size = validate_export_png_size(getattr(args, "export_png", None))
    if not minor and not png_size:
        return
    output_dir = Path(args.output_dir).expanduser().resolve()
    traced = not getattr(args, "no_manifest", False)
    if not traced:
        print("AVERTISSEMENT : --no-manifest, recoloration et export non tracés dans un manifeste.")
    by_file: dict[str, dict[str, object]] = {}

    def flush() -> None:
        if not traced:
            return

        def update(manifest: dict[str, object]) -> None:
            if minor:
                manifest["minor_color_source"] = DSFR_MAIN_PALETTE_SOURCE
            for icon in manifest.get("icons", []):  # type: ignore[union-attr]
                if isinstance(icon, dict) and icon.get("file") in by_file:
                    icon.update(by_file[str(icon["file"])])

        rewrite_manifest(output_dir, update)

    if minor:
        name, hex_color = minor
        contrast = contrast_on_white(hex_color)
        if contrast < MIN_GRAPHIC_CONTRAST:
            print(f"AVERTISSEMENT : contraste {contrast}:1 de {name} sur blanc, sous {MIN_GRAPHIC_CONTRAST}:1 (WCAG 1.4.11)")
        recolored: list[tuple[Path, str]] = []
        with tempfile.TemporaryDirectory() as tmp:
            for item in generated:
                svg_path = Path(item["file"])
                content = recolor_minor_content(svg_path.read_text(encoding="utf-8"), hex_color, str(svg_path))
                probe = Path(tmp) / svg_path.name
                probe.write_text(content, encoding="utf-8")
                validate_dsfr_artwork_svg(probe, expected_fills={**DSFR_LAYER_FILLS, "fr-artwork-minor": hex_color})
                recolored.append((svg_path, content))
        for item, (svg_path, content) in zip(generated, recolored):
            svg_path.write_text(content, encoding="utf-8")
            item["sha256"] = file_sha256(svg_path)
            by_file[svg_path.name] = {"minor_color": name, "minor_color_hex": hex_color, "minor_contrast_on_white": contrast, "reproduction": "exact-copy-minor-recolored", "official": False, "official_reference": True, "sha256": item["sha256"]}
        flush()
    if png_size:
        failures: list[str] = []
        traced_exports: dict[str, list[dict[str, object]]] = {}
        manifest_path = output_dir / "manifest.json"
        if traced and manifest_path.exists():
            for icon in json.loads(manifest_path.read_text(encoding="utf-8")).get("icons", []):
                if isinstance(icon, dict) and isinstance(icon.get("file"), str) and isinstance(icon.get("raster_exports"), list):
                    traced_exports[icon["file"]] = valid_raster_entries(icon["raster_exports"])
        for item in generated:
            svg_path = Path(item["file"])
            target, renderer = export_png(svg_path, png_size)
            entry = by_file.setdefault(svg_path.name, {})
            listed = existing_raster_exports(svg_path, list(entry.get("raster_exports") or traced_exports.get(svg_path.name, [])))  # type: ignore[arg-type]
            if target is None:
                failures.append(f"{svg_path.name} : {renderer}")
                entry["raster_exports"] = listed
                continue
            listed = [e for e in listed if e.get("file") != target.name]
            listed.append({"file": target.name, "size": png_size, "renderer": renderer, "source": svg_path.name})
            entry["raster_exports"] = listed
            print(target)
        flush()
        if failures:
            for failure in failures:
                print(failure)
            raise ValueError("Export PNG incomplet : " + " ; ".join(failures))


def validate_dsfr_artwork_svg(svg_path: Path, expected_fills: dict[str, str] | None = None) -> None:
    content = svg_path.read_text(encoding="utf-8", errors="replace")
    if "<!DOCTYPE" in content or "<!ENTITY" in content:
        raise ValueError(f"{svg_path} contient un DOCTYPE ou des entités XML, refusés pour un pictogramme DSFR.")
    try:
        root = ET.parse(svg_path).getroot()
    except ET.ParseError as exc:
        raise ValueError(f"{svg_path} n'est pas un SVG XML valide : {exc}") from exc

    if local_name(root.tag) != "svg":
        raise ValueError(f"{svg_path} ne contient pas de racine <svg>.")
    if root.attrib.get("viewBox") != "0 0 80 80":
        raise ValueError(f"{svg_path} ne déclare pas viewBox=\"0 0 80 80\".")
    if root.attrib.get("width") not in {"80px", "80"}:
        raise ValueError(f"{svg_path} ne déclare pas width=\"80px\" ou width=\"80\".")
    if root.attrib.get("height") not in {"80px", "80"}:
        raise ValueError(f"{svg_path} ne déclare pas height=\"80px\" ou height=\"80\".")

    fills = style_fills(root)
    for class_name, expected_fill in (expected_fills or DSFR_LAYER_FILLS).items():
        if fills.get(class_name) != expected_fill:
            raise ValueError(
                f"{svg_path} ne déclare pas la couleur attendue {expected_fill} "
                f"pour .{class_name}."
            )

    symbols = {
        element.attrib.get("id"): element
        for element in root.iter()
        if local_name(element.tag) == "symbol" and element.attrib.get("id")
    }
    missing = [layer for layer in DSFR_LAYER_IDS if layer not in symbols]
    if missing:
        raise ValueError(f"{svg_path} ne contient pas les calques DSFR attendus : {', '.join(missing)}")
    symbol_order = tuple(element.attrib.get("id") for element in root.iter() if local_name(element.tag) == "symbol" and element.attrib.get("id") in DSFR_LAYER_IDS)
    if symbol_order != tuple(DSFR_LAYER_IDS):
        raise ValueError(f"{svg_path} : ordre des symboles non canonique ({', '.join(symbol_order)}), attendu {', '.join(DSFR_LAYER_IDS)}.")

    uses = [element for element in root.iter() if local_name(element.tag) == "use"]
    use_hrefs = tuple(use_href(element) or "" for element in uses)
    use_classes = tuple(element.attrib.get("class", "") for element in uses)
    use_pattern = (use_hrefs, use_classes)
    if len(uses) != 3:
        raise ValueError(f"{svg_path} ne contient pas exactement trois <use>.")
    if use_pattern != (DSFR_CANONICAL_USE_HREFS, DSFR_LAYER_CLASSES) and use_pattern not in DSFR_KNOWN_USE_EXCEPTIONS:
        raise ValueError(f"{svg_path} ne respecte pas l'ordre ou les classes des <use> DSFR.")

    for layer in DSFR_LAYER_IDS:
        paths = [element for element in symbols[layer].iter() if local_name(element.tag) == "path"]
        if not paths:
            raise ValueError(f"{svg_path} : le calque {layer} ne contient aucun <path>.")
        for element in symbols[layer].iter():
            element_name = local_name(element.tag)
            if element_name not in {"symbol", "path"}:
                raise ValueError(f"{svg_path} : le calque {layer} contient un élément interdit <{element_name}>.")
        for path_element in paths:
            if "d" not in path_element.attrib:
                raise ValueError(f"{svg_path} : le calque {layer} contient un <path> sans attribut d.")
            forbidden = sorted({"fill", "stroke"} & set(path_element.attrib))
            if forbidden:
                raise ValueError(
                    f"{svg_path} : le calque {layer} contient un <path> avec attribut interdit "
                    f"{', '.join(forbidden)}."
                )


ANNOTATION_KEYS = ("title", "description", "major", "minor", "decorative")


DSFR_MANIFEST_SOURCES = ("dsfr-artwork", "dsfr-replica")
MERGEABLE_MANIFEST_SOURCES = DSFR_MANIFEST_SOURCES + ("generated", "mixed")


def load_existing_manifest(output_dir: Path, no_manifest: bool) -> dict[str, object] | None:
    """Lit strictement un manifest.json existant : illisible → erreur ; source étrangère → avertissement et None."""
    manifest_path = output_dir / "manifest.json"
    if no_manifest or not manifest_path.exists():
        return None
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, UnicodeDecodeError) as exc:
        raise ValueError(f"{manifest_path} existant illisible ({exc}) : le réparer ou le déplacer avant de régénérer, sinon ses annotations seraient perdues.") from exc
    if not isinstance(manifest, dict) or not isinstance(manifest.get("icons"), list):
        raise ValueError(f"{manifest_path} existant n'a pas la forme attendue (objet avec une liste icons) : le déplacer avant de régénérer.")
    if manifest.get("source") is not None and manifest.get("source") not in MERGEABLE_MANIFEST_SOURCES:
        print(f"AVERTISSEMENT : manifest.json existant de source {manifest.get('source')!r} ignoré, non fusionné.")
        return None
    return manifest


def merge_manifest(output_dir: Path, existing: dict[str, object] | None, header: dict[str, object], new_icons: list[dict[str, object]]) -> None:
    """Écrit manifest.json en conservant les entrées existantes non régénérées et les annotations humaines.

    La clé de fusion est le nom de fichier. Chaque entrée porte son origine (dsfr-artwork, dsfr-replica,
    generated) ; si le dossier mélange plusieurs origines, l'en-tête devient source: mixed et official: false
    plutôt que d'attribuer à toutes les entrées la provenance du dernier run.
    """
    merged: dict[str, dict[str, object]] = {}
    inherited_origin = existing.get("source") if existing and existing.get("source") in DSFR_MANIFEST_SOURCES + ("generated",) else None
    if existing:
        for item in existing.get("icons", []):  # type: ignore[union-attr]
            if not isinstance(item, dict) or "name" not in item or "file" not in item:
                continue
            origin = item.get("origin") or inherited_origin
            if origin != "generated":
                try:
                    normalize_dsfr_name(str(item["name"]))
                except ValueError:
                    print(f"AVERTISSEMENT : entrée {item.get('name')!r} du manifeste existant ignorée (nom non DSFR).")
                    continue
            if (output_dir / str(item["file"])).exists():
                kept = dict(item)
                if origin and "origin" not in kept:
                    kept["origin"] = origin
                merged[str(item["file"])] = kept
    for icon in new_icons:
        filename = str(icon["file"])
        previous = merged.get(filename, {})
        human = {key: previous[key] for key in ANNOTATION_KEYS if previous.get(key)}
        merged[filename] = {**icon, **human}
        if isinstance(previous.get("raster_exports"), list) and "raster_exports" not in icon:
            merged[filename]["raster_exports"] = previous["raster_exports"]
    origins = sorted({str(item.get("origin")) for item in merged.values() if item.get("origin")})
    manifest: dict[str, object]
    if len(origins) > 1:
        manifest = {"source": "mixed", "sources": origins, "official": False, "reproduction": "mixed"}
    else:
        manifest = dict(header)
    if existing and isinstance(existing.get("annotation"), dict):
        manifest["annotation"] = existing["annotation"]
    manifest["icons"] = [merged[filename] for filename in sorted(merged)]
    write_json_atomic(output_dir / "manifest.json", manifest)


def load_replica_catalog(root: str | None) -> tuple[Path, dict[str, dict[str, str]], str | None]:
    """Catalogue du corpus de reproduction : noms, fichiers, provenance et sha256, sans résoudre les SVG.
    La résolution (embarqué ou cache officiel) et la validation ont lieu pour les icônes demandées,
    avant la première copie (resolve_replica_sources)."""
    replica_root = Path(root).expanduser().resolve() if root else DEFAULT_REPLICA_ROOT.resolve()
    manifest_path = replica_root / "manifest.json"
    if not manifest_path.exists():
        raise ValueError(
            "Corpus de reproduction DSFR introuvable. Fournir --replica-root ou installer "
            "pictos-svg/dsfr-officiels avec son manifest.json."
        )
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ValueError(f"Manifest de reproduction DSFR invalide : {manifest_path} : {exc}") from exc

    icons = manifest.get("icons")
    if not isinstance(icons, list):
        raise ValueError(f"{manifest_path} ne contient pas de liste icons.")

    catalog: dict[str, dict[str, str]] = {}
    for item in icons:
        if not isinstance(item, dict) or "name" not in item or "file" not in item:
            raise ValueError(f"{manifest_path} contient une entrée icons invalide.")
        name = normalize_dsfr_name(str(item["name"]))
        file_name = str(item["file"])
        if "/" in file_name or file_name.startswith(".") or not file_name.endswith(".svg"):
            raise ValueError(f"{manifest_path} contient un nom de fichier invalide : {file_name}")
        catalog[name] = {"file": file_name, "source": str(item.get("source", f"{name}.svg")), "sha256": str(item.get("sha256") or "")}
        catalog[name].update({key: str(item[key]) for key in ANNOTATION_KEYS if item.get(key)})

    return replica_root, catalog, declared_dsfr_version(manifest)


def resolve_replica_sources(replica_root: Path, catalog: dict[str, dict[str, str]], names: list[str], version: str | None, raw_version: object = None) -> dict[str, Path]:
    """Passe 1 du mode replica : résoudre et valider chaque source demandée avant la première copie."""
    sources: dict[str, Path] = {}
    for name in names:
        path = resolve_official_svg(replica_root, {**catalog[name], "name": name, "dsfr_version_declared": raw_version}, version)
        assert path is not None
        validate_dsfr_artwork_svg(path)
        sources[name] = path
    return sources


def plan_targets(output_dir: Path, prefix: str, pairs: list[tuple[str, str]]) -> dict[str, Path]:
    """Cibles de copie, avec refus des collisions de noms aplatis."""
    targets: dict[str, Path] = {}
    seen: dict[Path, str] = {}
    for name, file_name in pairs:
        target = output_dir / f"{prefix}{file_name}"
        if target in seen:
            raise ValueError(f"Collision de fichiers de sortie : {seen[target]} et {name} produiraient tous deux {target.name}.")
        seen[target] = name
        targets[name] = target
    return targets


def write_dsfr_artwork_icons(args: argparse.Namespace) -> list[dict[str, object]]:
    pictograms_dir = resolve_pictograms_dir(args.dsfr_artwork_root)
    output_dir = Path(args.output_dir).expanduser().resolve()
    prefix = validate_prefix(args.prefix)
    existing = load_existing_manifest(output_dir, args.no_manifest)
    names = parse_dsfr_names(args.icons, pictograms_dir)
    available_names = discover_dsfr_names(pictograms_dir)

    # Passe 1 : tout valider avant d'écrire quoi que ce soit.
    sources: dict[str, Path] = {}
    for name in names:
        source = pictograms_dir / f"{name}.svg"
        if not source.exists():
            close = difflib.get_close_matches(name, available_names or DSFR_NAMES, n=3)
            suffix = f" Suggestions : {', '.join(close)}." if close else ""
            raise ValueError(f"Fichier DSFR absent : {source}.{suffix}")
        validate_dsfr_artwork_svg(source)
        sources[name] = source
    targets = plan_targets(output_dir, prefix, [(name, f"{name.replace('/', '-')}.svg") for name in names])

    # Passe 2 : copier.
    output_dir.mkdir(parents=True, exist_ok=True)
    generated: list[dict[str, object]] = []
    for name in names:
        source, target = sources[name], targets[name]
        shutil.copyfile(source, target)
        generated.append({"name": name, "file": str(target), "source": str(source), "origin": "dsfr-artwork",
                "official": True, "sha256": file_sha256(target)})

    if not args.no_manifest:
        manifest_icons: list[dict[str, object]] = []
        for item in generated:
            source = Path(item["source"])
            try:
                source_ref = source.relative_to(pictograms_dir).as_posix()
            except ValueError as exc:
                raise ValueError(f"{source} n'est pas sous la racine {pictograms_dir} : provenance non traçable.") from exc
            manifest_icons.append({**item, "file": Path(item["file"]).name, "source": source_ref})
        header: dict[str, object] = {"source": "dsfr-artwork", "source_root": str(pictograms_dir.resolve()), "expected_layers": list(DSFR_LAYER_IDS)}
        merge_manifest(output_dir, existing, header, manifest_icons)

    return generated


def write_dsfr_replica_icons(args: argparse.Namespace) -> list[dict[str, object]]:
    replica_root, catalog, dsfr_version = load_replica_catalog(args.replica_root)
    output_dir = Path(args.output_dir).expanduser().resolve()
    prefix = validate_prefix(args.prefix)
    existing = load_existing_manifest(output_dir, args.no_manifest)
    names = parse_replica_names(args.icons, sorted(catalog))
    targets = plan_targets(output_dir, prefix, [(name, catalog[name]["file"]) for name in names])
    raw_version = json.loads((replica_root / "manifest.json").read_text(encoding="utf-8")).get("dsfr_version")
    sources = resolve_replica_sources(replica_root, catalog, names, dsfr_version, raw_version)  # passe 1 : tout valider avant d'écrire

    output_dir.mkdir(parents=True, exist_ok=True)
    generated: list[dict[str, object]] = []
    for name in names:
        item = catalog[name]
        source, target = sources[name], targets[name]
        shutil.copyfile(source, target)
        validate_dsfr_artwork_svg(target)
        generated.append(
            {
                "name": name,
                "file": str(target),
                "source": item["source"],
                "replica_file": item["file"],
                "resolved_from": "embedded" if source == replica_root / item["file"] else "official-cache",
                "origin": "dsfr-replica",
                "official": True,
                "official_reference": True,
                "reproduction": "exact-copy",
                "sha256": file_sha256(target),
                **{key: item[key] for key in ANNOTATION_KEYS if item.get(key)},
            }
        )

    if not args.no_manifest:
        manifest_icons = [{**item, "file": Path(item["file"]).name} for item in generated]
        header: dict[str, object] = {"source": "dsfr-replica", "source_root": str(replica_root.resolve()), "expected_layers": list(DSFR_LAYER_IDS), "reproduction": "exact-copy-from-embedded-official-corpus"}
        merge_manifest(output_dir, existing, header, manifest_icons)

    return generated


def write_icons(args: argparse.Namespace) -> list[dict[str, object]]:
    preset = PRESETS[args.preset]
    color = validate_color(args.color or preset["color"], "--color")
    accent = validate_color(args.accent or preset["accent"], "--accent")
    background_color = validate_color(args.background_color or preset["background"], "--background-color")
    output_dir = Path(args.output_dir).expanduser().resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
    existing = load_existing_manifest(output_dir, args.no_manifest)

    generated: list[dict[str, object]] = []
    for name in parse_icon_names(args.icons):
        spec = CATALOG[name]
        filename = f"{args.prefix}{name}.svg"
        svg_path = output_dir / filename
        svg = render_svg(
            name=name,
            title=spec.title,
            desc=spec.desc,
            color=color,
            accent=accent,
            background=args.background,
            background_color=background_color,
            size=args.size,
            stroke_width=args.stroke_width,
        )
        svg_path.write_text(svg, encoding="utf-8")
        generated.append({"name": name, "file": str(svg_path), "title": spec.title, "desc": spec.desc, "sha256": file_sha256(svg_path)})

    if not args.no_manifest:
        settings = {"preset": args.preset, "color": color, "accent": accent, "background": args.background, "size": args.size, "stroke_width": args.stroke_width}
        manifest_icons: list[dict[str, object]] = [
            {**item, "file": Path(item["file"]).name, "origin": "generated", "official": False, "reproduction": "generated-legacy", **settings}
            for item in generated
        ]
        header: dict[str, object] = {"source": "generated", "official": False, "reproduction": "generated-legacy", **settings}
        merge_manifest(output_dir, existing, header, manifest_icons)

    return generated


def list_catalog() -> None:
    for name in sorted(CATALOG):
        spec = CATALOG[name]
        print(f"{name}\t{spec.title}\t{', '.join(spec.tags)}")


def list_dsfr_names() -> None:
    for name in DSFR_NAMES:
        print(name)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Reproduire, copier ou générer des pictogrammes SVG pour supports DSFR.")
    parser.add_argument("--source", choices=["dsfr-replica", "dsfr-artwork", "generated"], default="dsfr-replica", help="Origine des pictogrammes : dsfr-replica (défaut, corpus officiel embarqué, 80x80), dsfr-artwork (source officielle locale), generated (mode legacy filaire 256x256, jamais officiel).")
    parser.add_argument("--icons", default="all", help="Liste séparée par des virgules, ou 'all'.")
    parser.add_argument("--output-dir", help="Dossier de sortie, obligatoire pour générer (aucun défaut : le dossier du skill ne doit pas recevoir de copies).")
    parser.add_argument("--dsfr-artwork-root", help="Dossier dsfr-artwork ou dist/artwork/pictograms.")
    parser.add_argument("--replica-root", help="Dossier du corpus officiel embarqué pour --source dsfr-replica.")
    parser.add_argument("--preset", choices=sorted(PRESETS), default="dsfr", help="Palette visuelle.")
    parser.add_argument("--color", help="Couleur principale #RRGGBB.")
    parser.add_argument("--accent", help="Couleur d’accent #RRGGBB.")
    parser.add_argument("--background", choices=["none", "tile", "disk"], default="none", help="Fond du SVG.")
    parser.add_argument("--background-color", help="Couleur de fond #RRGGBB.")
    parser.add_argument("--stroke-width", type=int, default=9, help="Épaisseur du trait dans le viewBox 256.")
    parser.add_argument("--size", type=int, default=256, help="Attributs width et height du SVG.")
    parser.add_argument("--prefix", default="", help="Préfixe ajouté aux noms de fichiers.")
    parser.add_argument("--minor-color", help="Couleur du calque minor parmi les -main de la palette DSFR (ex. green-emeraude-main-632) ; copies officielles seulement, tracé dans le manifeste.")
    parser.add_argument("--export-png", type=int, help="Exporter aussi un PNG plein cadre de cette taille ; utilise qlmanage, rsvg-convert ou inkscape selon disponibilité.")
    parser.add_argument("--no-manifest", action="store_true", help="Ne pas écrire manifest.json.")
    parser.add_argument("--list", action="store_true", help="Lister les pictos disponibles.")
    parser.add_argument("--list-dsfr-names", action="store_true", help="Lister les noms DSFR connus.")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.list:
        list_catalog()
        return 0
    if args.list_dsfr_names:
        list_dsfr_names()
        return 0

    if args.stroke_width < 2 or args.stroke_width > 18:
        parser.error("--stroke-width doit être compris entre 2 et 18.")
    if args.size < 32 or args.size > 2048:
        parser.error("--size doit être compris entre 32 et 2048.")

    if not args.output_dir:
        parser.error("--output-dir est requis pour générer des fichiers.")
    if args.source in DSFR_MANIFEST_SOURCES:
        defaults = parser.parse_args(["--output-dir", args.output_dir])
        for option in ("--preset", "--color", "--accent", "--background", "--background-color", "--stroke-width", "--size"):
            attr = option.lstrip("-").replace("-", "_")
            if getattr(args, attr) != getattr(defaults, attr):
                parser.error(f"{option} ne s'applique qu'à --source generated : les copies officielles gardent leur rendu DSFR.")

    try:
        validate_prefix(args.prefix)
        resolve_minor_color(args.minor_color)
        validate_export_png_size(args.export_png)
        if args.export_png is not None:
            resolve_png_renderer_timeout()
        if args.source == "dsfr-artwork":
            generated = write_dsfr_artwork_icons(args)
        elif args.source == "dsfr-replica":
            generated = write_dsfr_replica_icons(args)
        else:
            if args.minor_color or args.export_png is not None:
                raise ValueError("--minor-color et --export-png s'appliquent aux copies officielles (dsfr-replica, dsfr-artwork).")
            generated = write_icons(args)
    except ValueError as exc:
        parser.error(str(exc))
    except OSError as exc:
        parser.error(f"Erreur système : {exc}")

    if args.source in DSFR_MANIFEST_SOURCES:
        try:
            postprocess_dsfr_outputs(args, generated)
        except (ValueError, OSError) as exc:
            # Les SVG sont déjà écrits : les lister reste dû à l'appelant ; l'échec de post-traitement n'est pas une erreur d'usage.
            for item in generated:
                print(item["file"])
            print(f"ERREUR : {exc}", file=sys.stderr)
            return 1

    for item in generated:
        print(item["file"])
    return 0


if __name__ == "__main__":
    sys.exit(main())
