#!/usr/bin/env python3
"""Inventory the official @gouvfr/dsfr package surface used for coverage claims."""

from __future__ import annotations

import argparse
import contextlib
import json
import os
import re
import sys
from collections import Counter
from pathlib import Path

sys.dont_write_bytecode = True
import dsfr_component_registry as registry  # noqa: E402


SKILL_DIR = Path(__file__).resolve().parents[1]
LIBRARY_PATH = SKILL_DIR / "assets" / "dsfr_complete_library.json"
# L'échappement CSS `\@` fait partie du nom des classes à point de rupture
# (`fr-fieldset__element--inline@md`…) : sans lui, la classe est tronquée au
# `@` et repliée sur un préfixe déjà compté, ce qui sous-compte la surface.
CSS_CLASS_RE = re.compile(r"\.((?:fr|ri)-(?:[A-Za-z0-9_-]|\\@)+)")
CSS_VAR_DEF_RE = re.compile(r"(--[\w-]+)\s*:")
# Plancher de taille : une feuille officielle tronquée ne doit pas produire un
# inventaire silencieusement réduit.
MIN_CSS_BYTES = 10_000


def read_css(path: Path) -> str:
    """Lecture stricte d'une feuille officielle.

    `errors="ignore"` supprimait les octets invalides d'un fichier corrompu —
    donc des classes — sans rien signaler, et un fichier absent devenait une
    chaîne vide, donc un inventaire de zéros.
    """
    try:
        text = path.read_text(encoding="utf-8")
    except FileNotFoundError:
        raise SystemExit(f"feuille officielle absente : {path} (paquet incomplet ou chemin erroné)") from None
    except UnicodeDecodeError:
        raise SystemExit(f"feuille officielle illisible : {path} (encodage invalide, fichier corrompu)") from None
    except OSError as exc:
        raise SystemExit(f"feuille officielle illisible : {path} ({exc.strerror})") from None
    size = len(text.encode("utf-8"))
    if size < MIN_CSS_BYTES:
        raise SystemExit(f"feuille officielle tronquée : {path} ({size} octets, minimum attendu {MIN_CSS_BYTES})")
    return text


def classes(css: str) -> set[str]:
    return {name.replace("\\", "") for name in CSS_CLASS_RE.findall(css)}


def variables(css: str) -> set[str]:
    return set(CSS_VAR_DEF_RE.findall(css))


def names(root: Path) -> list[str]:
    return sorted(path.name for path in root.iterdir() if path.is_dir()) if root.is_dir() else []


def svg_stats(root: Path) -> tuple[int, int]:
    # Sortie anticipée : l'écriture conditionnelle en fin d'expression ne
    # protégeait que le second membre du tuple.
    if not root.is_dir():
        return 0, 0
    return len(names(root)), len(list(root.rglob("*.svg")))


def families(items: set[str], strip: str = "") -> dict[str, int]:
    counts: Counter[str] = Counter()
    for item in items:
        value = item.removeprefix(strip).lstrip("-")
        counts[value.split("-", 1)[0]] += 1
    return dict(sorted(counts.items(), key=lambda kv: (-kv[1], kv[0])))


def top(items: dict[str, int], limit: int = 12) -> str:
    return ", ".join(f"{name} ({count})" for name, count in list(items.items())[:limit])


def load_json(path: Path) -> dict:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        raise SystemExit(f"fichier absent : {path} (paquet officiel incomplet ou chemin erroné)") from None
    except OSError as exc:
        raise SystemExit(f"fichier illisible : {path} ({exc.strerror})") from None
    except json.JSONDecodeError as exc:
        raise SystemExit(f"JSON invalide : {path} ({exc})") from None
    if not isinstance(data, dict):
        raise SystemExit(f"objet JSON attendu : {path}")
    return data


def portable_path(path: Path) -> str:
    """Chemin sans nom de machine : le dossier personnel devient `~` pour que
    l'inventaire versionné reste partageable (règle du miroir, 17 août)."""
    resolved = Path(path).expanduser().resolve()
    home = Path.home().resolve()
    if resolved.is_relative_to(home):
        return "~/" + resolved.relative_to(home).as_posix()
    return str(resolved)


def build_inventory(package_path: Path) -> dict:
    dist = package_path / "dist"
    dsfr_css = dist / "dsfr.min.css"
    utility_css = dist / "utility" / "utility.min.css"
    package_json = load_json(package_path / "package.json")
    if not str(package_json.get("version", "")).strip():
        raise SystemExit(f"version absente de {package_path / 'package.json'} : paquet officiel non identifiable")
    for required in (dsfr_css, utility_css, dist / "component"):
        if not required.exists():
            raise SystemExit(f"paquet officiel incomplet : {required} absent (dist tronqué ou chemin erroné)")
    library = load_json(LIBRARY_PATH)

    # Une seule lecture par feuille : `variables()` et `classes()` relisaient
    # chacune `dsfr.min.css` en entier (environ 0,7 Mo par passage).
    dsfr_text = read_css(dsfr_css)
    utility_text = read_css(utility_css)
    css_vars = variables(dsfr_text)
    dsfr_classes = classes(dsfr_text)
    utility_classes = classes(utility_text)
    icon_classes = {item for item in utility_classes if item.startswith("fr-icon-")}
    legacy_icon_classes = {item for item in utility_classes if item.startswith("fr-fi-")}
    artwork_classes = {item for item in utility_classes if item.startswith("fr-artwork")}
    other_utilities = utility_classes - icon_classes - legacy_icon_classes - artwork_classes

    official_components = names(dist / "component")
    local_components = set(library.get("components", {}))
    normalized_local = {
        registry.official_name(component) for component in local_components
    }
    official_set = set(official_components)
    icon_categories, icon_svg_files = svg_stats(dist / "icons")
    pictogram_categories, pictogram_svg_files = svg_stats(dist / "artwork" / "pictograms")

    return {
        "package": package_json.get("name", "@gouvfr/dsfr"),
        "version": package_json.get("version"),
        "package_path": portable_path(package_path),
        "official": {
            "css_variables_dsfr_min": len(css_vars),
            "css_variable_families": families(css_vars, "--"),
            "classes_dsfr_min": len(dsfr_classes),
            "utility_classes_total": len(utility_classes),
            "utility_classes_non_icon_non_artwork": len(other_utilities),
            "utility_class_families": families(other_utilities, "fr-"),
            "icon_classes": len(icon_classes),
            "legacy_icon_classes": len(legacy_icon_classes),
            "icon_categories": icon_categories,
            "icon_svg_files": icon_svg_files,
            "artwork_classes": len(artwork_classes),
            "pictogram_categories": pictogram_categories,
            "pictogram_svg_files": pictogram_svg_files,
            "components": len(official_components),
            "component_names": official_components,
        },
        "local": {
            "library_components_raw": len(local_components),
            "library_variants": library.get("total_variants"),
            "official_components_covered": len(official_set & normalized_local),
            "official_components_missing": sorted(official_set - normalized_local),
            "local_extra_components": sorted(
                normalized_local - official_set - registry.LOCAL_HELPER_COMPONENTS
            ),
            "helper_components": sorted(local_components & registry.LOCAL_HELPER_COMPONENTS),
        },
    }


def render_markdown(data: dict) -> str:
    official = data["official"]
    local = data["local"]
    status = (
        f"{local['official_components_covered']}/{official['components']} officiels couverts"
        if not local["official_components_missing"] and not local["local_extra_components"]
        else f"{local['official_components_covered']}/{official['components']} couverts, écarts à traiter"
    )
    lines = [
        f"# Inventaire officiel DSFR {data['version']}",
        "",
        "Inventaire généré depuis le paquet npm extrait localement. Il mesure la",
        "surface officielle disponible ; il ne prouve pas une conformité RGAA ni",
        "un droit de publication.",
        "",
        "## Source",
        "",
        f"- Paquet : `{data['package']}@{data['version']}`",
        f"- Chemin : `{data['package_path']}`",
        "- Commande :",
        "",
        "```bash",
        "SKILL_DIR=.claude/skills/dsfr-components  # adapter à l'emplacement d'installation",
        f"python3 \"$SKILL_DIR/scripts/inventory_official_coverage.py\" --official-version {data['version']} --output \"$SKILL_DIR/evals/official-coverage-inventory.md\"",
        "```",
        "",
        "## Synthèse",
        "",
        "| Surface | Total officiel | Couverture locale | Statut |",
        "| --- | --- | --- | --- |",
        f"| Variables CSS `dsfr.min.css` | {official['css_variables_dsfr_min']} | références `tokens.md` / `tokens-advanced.md` | inventaire officiel, pas catalogue embarqué |",
        f"| Classes `dsfr.min.css` | {official['classes_dsfr_min']} | validation des classes générées | preuve de présence, pas audit visuel |",
        f"| Classes utilitaires `utility.min.css` | {official['utility_classes_total']} | `utilities.md` + sous-références | charger la famille utile |",
        f"| Utilitaires hors icônes/artwork | {official['utility_classes_non_icon_non_artwork']} | `generate_atom.py` + références | couverture partielle bornée |",
        f"| Icônes `fr-icon-*` | {official['icon_classes']} classes, {official['icon_categories']} familles, {official['icon_svg_files']} SVG | `list_icons.py` | validation runtime possible |",
        f"| Icônes legacy `fr-fi-*` | {official['legacy_icon_classes']} classes | références icônes | dépréciées, ne pas introduire |",
        f"| Pictogrammes | {official['pictogram_svg_files']} SVG, {official['pictogram_categories']} familles | `generate_atom.py pictogram` | pointer-only |",
        f"| Composants `dist/component` | {official['components']} | {status} | claim borné aux composants officiels |",
        f"| Variantes locales | n/a | {local['library_variants']} variantes JSON | bibliothèque locale, pas surface officielle exhaustive |",
        "",
        "## Familles principales",
        "",
        f"- Variables CSS : {top(official['css_variable_families'])}.",
        f"- Utilitaires hors icônes/artwork : {top(official['utility_class_families'])}.",
        "",
        "## Composants officiels",
        "",
        ", ".join(official["component_names"]),
        "",
        "## Écarts",
        "",
    ]
    missing = local["official_components_missing"]
    extras = local["local_extra_components"]
    helpers = local["helper_components"]
    lines.append("- Composants officiels absents localement : " + (", ".join(missing) if missing else "aucun") + ".")
    lines.append("- Composants locaux non officiels : " + (", ".join(extras) if extras else "aucun hors helpers déclarés") + ".")
    if helpers:
        lines.append("- Helpers locaux hors catalogue officiel : " + ", ".join(helpers) + ".")
    lines += [
        "",
        "## Usage agentique",
        "",
        "- Pour valider un token précis, vérifier le paquet ou la référence ciblée.",
        "- Pour valider une classe, charger la famille utilitaire ou le composant.",
        "- Pour revendiquer `100 %`, citer cet inventaire et la commande rejouée.",
        "- Pour RGAA, publication ou marque État, router vers `verification.md`.",
    ]
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description="Inventorie la surface officielle DSFR.")
    parser.add_argument("--official-package", type=Path, help="chemin du paquet extrait")
    parser.add_argument(
        "--official-version",
        default=os.environ.get("DSFR_OFFICIAL_VERSION", "1.15.2"),
        help="version npm",
    )
    parser.add_argument("--official-cache-dir", type=Path, default=None,
                        help="cache du paquet officiel (défaut : celui de check_generated_outputs.py)")
    parser.add_argument("--format", choices=["markdown", "json"], default="markdown")
    parser.add_argument("--output", type=Path, help="fichier de sortie optionnel (régénéré : l'inventaire versionné est écrasé volontairement)")
    args = parser.parse_args()
    env_package = os.environ.get("DSFR_OFFICIAL_PACKAGE_DIR")
    if args.official_package:
        package_path = Path(args.official_package).expanduser()
        if not package_path.is_dir():
            raise SystemExit(f"--official-package : dossier introuvable : {package_path}")
    elif env_package:
        package_path = Path(env_package).expanduser()
        if not package_path.is_dir():
            raise SystemExit(f"DSFR_OFFICIAL_PACKAGE_DIR : dossier introuvable : {package_path}")
    else:
        # Import tardif : au niveau module, la garde d'intégrité de
        # check_generated_outputs.py refusait de démarrer l'inventaire dès
        # qu'un script du skill manquait, y compris ceux qu'il n'utilise pas.
        # Ici, il est chargé seulement quand le cache doit être résolu.
        import check_generated_outputs as checks  # noqa: PLC0415
        cache_dir = args.official_cache_dir or checks.DEFAULT_OFFICIAL_CACHE_DIR
        # Messages d'état de la résolution renvoyés sur stderr : stdout reste
        # réservé au document ou au JSON produit.
        with contextlib.redirect_stdout(sys.stderr):
            package_path = checks.resolve_official_package(args.official_version, cache_dir)
    if package_path is None:
        raise SystemExit(
            "official package unavailable: pass --official-package or allow the download "
            "(unset DSFR_OFFICIAL_CACHE_OFFLINE)"
        )
    data = build_inventory(package_path)
    output = json.dumps(data, ensure_ascii=False, indent=2, sort_keys=True)
    if args.format == "markdown":
        output = render_markdown(data)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(output + "\n", encoding="utf-8")
    else:
        print(output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
