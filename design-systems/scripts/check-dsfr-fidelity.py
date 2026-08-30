#!/usr/bin/env python3
"""Contrôle de fidélité DSFR : tokens et classes du profil contre le CSS officiel.

Compare les tokens de décision de tokens.yaml et les classes fr-* de
tokens.yaml et des exemples HTML au contenu réel de @gouvfr/dsfr, à la
version figée par package_version_ref.

Résolution des CSS officiels (dsfr.min.css et utility/utility.min.css) :
1. --css-dir DOSSIER : copies locales fournies explicitement ;
2. cache officiel du dépôt (DSFR_OFFICIAL_CACHE_DIR, défaut
   ~/.cache/dsfr-official-cache), déjà alimenté par les checks Playwright ;
3. --download : téléchargement depuis cdn.jsdelivr.net (dépendance réseau),
   mis en cache dans le dossier temporaire système.

Ce contrôle prouve l'existence des tokens et classes dans le paquet officiel,
pas la conformité DSFR ou RGAA d'un rendu.
"""
from __future__ import annotations
import argparse
import importlib.util
import os
import re
import sys
import tempfile
import urllib.request
from pathlib import Path

_SPEC = importlib.util.spec_from_file_location("profile_check", Path(__file__).with_name("check-dsfr-profile.py"))
assert _SPEC is not None and _SPEC.loader is not None
_MOD = importlib.util.module_from_spec(_SPEC)
_SPEC.loader.exec_module(_MOD)

ROOT = _MOD.ROOT
DSFR = _MOD.DSFR
TOKENS = _MOD.TOKENS
CSS_SOURCES = {"dsfr.min.css": "dsfr.min.css", "utility.min.css": "utility/utility.min.css"}
CDN = "https://cdn.jsdelivr.net/npm/@gouvfr/dsfr@{version}/dist/{remote}"
# Hooks du markup officiel absents du CSS (cf. example/component/display/index.html du paquet).
CLASS_ALLOWLIST = {"fr-display"}
# Clés de tokens.yaml portant un préfixe ou un motif, pas une classe complète.
PREFIX_KEYS = {"deprecated_icon_prefix", "icon_pattern", "column_prefix"}
TOKEN_RE = re.compile(r"\$([a-z][a-z0-9-]*)")
VAR_RE = re.compile(r"^--[a-z][a-z0-9-]*$")
CLASS_RE = re.compile(r"^fr-[a-z0-9]+(?:-[a-z0-9]+)*(?:--[a-z0-9-]+)?$")
ATTR_RE = re.compile(r'class="([^"]*)"')


def find_css(directory: Path) -> dict[str, Path] | None:
    found: dict[str, Path] = {}
    for name, remote in CSS_SOURCES.items():
        for candidate in (directory / name, directory / remote):
            if candidate.exists():
                found[name] = candidate
                break
        else:
            return None
    return found


def resolve_css(args: argparse.Namespace, version: str) -> dict[str, Path]:
    if args.css_dir:
        found = find_css(args.css_dir)
        if not found:
            sys.exit(f"FAIL CSS incomplet dans {args.css_dir} (attendus : dsfr.min.css et utility.min.css ou utility/utility.min.css)")
        return found
    cache_root = Path(os.environ.get("DSFR_OFFICIAL_CACHE_DIR") or Path.home() / ".cache" / "dsfr-official-cache")
    found = find_css(cache_root / f"gouvfr-dsfr-{version}" / "package" / "dist")
    if found:
        return found
    if args.download:
        cache = Path(tempfile.gettempdir()) / f"dsfr-css-{version}"
        cache.mkdir(parents=True, exist_ok=True)
        for name, remote in CSS_SOURCES.items():
            target = cache / name
            if not target.exists():
                urllib.request.urlretrieve(CDN.format(version=version, remote=remote), target)
        return {name: cache / name for name in CSS_SOURCES}
    sys.exit(
        f"FAIL CSS officiel introuvable : cache {cache_root} sans gouvfr-dsfr-{version} ; "
        "passer --css-dir <dossier> ou --download (réseau cdn.jsdelivr.net)"
    )


def yaml_classes(tokens: object) -> set[str]:
    found: set[str] = set()
    for path, value in _MOD.walk(tokens):
        if not isinstance(value, str) or path[-1] in PREFIX_KEYS:
            continue
        for part in value.split():
            if CLASS_RE.fullmatch(part):
                found.add(part)
    return found


def html_classes() -> set[str]:
    found: set[str] = set()
    for page in sorted((DSFR / "examples").glob("*.html")):
        for attr in ATTR_RE.findall(_MOD.rd(page)):
            for part in attr.split():
                if CLASS_RE.fullmatch(part):
                    found.add(part)
    return found


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--css-dir", type=Path, help="dossier local contenant dsfr.min.css et utility.min.css")
    parser.add_argument("--download", action="store_true", help="télécharger le CSS officiel depuis cdn.jsdelivr.net")
    parser.add_argument("--version", help="version DSFR à contrôler (défaut : package_version_ref de tokens.yaml)")
    args = parser.parse_args()
    tokens_raw = _MOD.rd(TOKENS)
    tokens = _MOD.yml(tokens_raw)
    version = args.version or str(tokens.get("package_version_ref") or "")
    if not version:
        sys.exit("FAIL package_version_ref absent de tokens.yaml et --version non fourni")
    css_paths = resolve_css(args, version)
    css = "".join(_MOD.rd(path) for path in css_paths.values())

    failures: list[str] = []
    var_names = {value for _, value in _MOD.walk(tokens) if isinstance(value, str) and VAR_RE.fullmatch(value)}
    token_names = sorted(set(TOKEN_RE.findall(tokens_raw)) | {name.removeprefix("--") for name in var_names})
    missing_tokens = [name for name in token_names if f"--{name}" not in css]
    for name in missing_tokens:
        failures.append(f"FAIL token absent du CSS {version}: ${name}")
    if not token_names:
        failures.append(
            "FAIL aucun token extrait de tokens.yaml : le contrôle ne prouve rien"
        )
    status = "FAIL" if (missing_tokens or not token_names) else "PASS"
    print(f"{status} tokens de tokens.yaml retrouvés dans le CSS officiel : {len(token_names) - len(missing_tokens)}/{len(token_names)}")

    classes = sorted((yaml_classes(tokens) | html_classes()) - CLASS_ALLOWLIST)
    missing_classes = [name for name in classes if not re.search(rf"\.{re.escape(name)}(?![a-z0-9-])", css)]
    for name in missing_classes:
        failures.append(f"FAIL classe absente du CSS {version}: {name}")
    if not classes:
        failures.append(
            "FAIL aucune classe extraite de tokens.yaml ni des exemples HTML : "
            "le contrôle ne prouve rien"
        )
    status = "FAIL" if (missing_classes or not classes) else "PASS"
    print(f"{status} classes fr-* retrouvées dans le CSS officiel : {len(classes) - len(missing_classes)}/{len(classes)}")
    if CLASS_ALLOWLIST:
        print(f"SKIP hooks de markup officiel non stylés en CSS : {', '.join(sorted(CLASS_ALLOWLIST))}")

    for line in failures:
        print(line, file=sys.stderr)
    if failures:
        return 1
    print(f"PASS fidélité au paquet @gouvfr/dsfr@{version}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
