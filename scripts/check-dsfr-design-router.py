#!/usr/bin/env python3
from __future__ import annotations

import os
import re
import shutil
import sys
from pathlib import Path, PurePosixPath

try:
    import yaml
except ModuleNotFoundError:
    if os.environ.get("DSFR_ROUTER_CHECK_WITH_UV") != "1" and shutil.which("uv"):
        os.execvpe(
            "uv",
            ["uv", "run", "--quiet", "--with", "PyYAML", "python", __file__, *sys.argv[1:]],
            dict(os.environ, DSFR_ROUTER_CHECK_WITH_UV="1"),
        )
    print("[FAIL] PyYAML absent: utiliser uv --with PyYAML ou installer PyYAML", file=sys.stderr)
    raise


FORBIDDEN_CLAIMS = {"conforme DSFR", "conforme RGAA", "prêt pour publication", "usage autorisé de la marque de l'État"}
FRONTMATTER_KEYS = {"name", "version", "status", "source_checked_at", "refresh_when", "progressive_disclosure", "claim_language"}
REFRESH_WHEN = {"nouvelle_version_dsfr", "publication", "claim_conforme", "doute_périmètre"}
DESIGN_LINE_LIMIT = 320
CATALOG_TERMS = {
    "accordéon", "alerte", "badge", "bandeau d'information", "bouton", "carte",
    "case à cocher", "champ de saisie", "fil d'ariane", "modale", "onglet",
    "pagination", "sélecteur de langue", "tableau", "tag", "tuile", "upload",
}
ROUTE_KEY_RE = re.compile(r"^[a-z][a-z0-9_]*$")
ROUTE_PATH_RE = re.compile(r"^references/[^/\\]+\.md$")
DEFAULT_WORKSPACE = Path(__file__).resolve().parents[1]
USAGE = "Usage: check-dsfr-design-router.py [--workspace PATH]"


class Check:
    def __init__(self) -> None:
        self.failures = 0

    def ok(self, message: str) -> None:
        print(f"[OK] {message}")

    def fail(self, message: str) -> None:
        self.failures += 1
        print(f"[FAIL] {message}")

    def contains(self, text: str, needles: list[str], label: str) -> None:
        missing = [needle for needle in needles if needle not in text]
        self.fail(f"{label}: éléments absents: {', '.join(missing)}") if missing else self.ok(label)

    def has_set(self, found: set[str], expected: set[str], label: str) -> None:
        missing = sorted(expected - found)
        self.fail(f"{label}: {', '.join(missing)}") if missing else self.ok(label)


def workspace_from_args() -> Path:
    if len(sys.argv) >= 3 and sys.argv[1] == "--workspace":
        if not sys.argv[2]:
            print(USAGE, file=sys.stderr)
            raise SystemExit(2)
        return Path(sys.argv[2]).expanduser().resolve()
    if len(sys.argv) >= 2 and sys.argv[1].startswith("--workspace="):
        value = sys.argv[1].split("=", 1)[1]
        if not value:
            print(USAGE, file=sys.stderr)
            raise SystemExit(2)
        return Path(value).expanduser().resolve()
    if len(sys.argv) >= 2 and sys.argv[1] == "--workspace":
        print(USAGE, file=sys.stderr)
        raise SystemExit(2)
    if len(sys.argv) >= 2 and sys.argv[1] not in {"-h", "--help"}:
        return Path(sys.argv[1]).expanduser().resolve()
    if len(sys.argv) >= 2:
        print(USAGE, file=sys.stderr)
        raise SystemExit(2)
    return DEFAULT_WORKSPACE


def read(path: Path, check: Check) -> str:
    if not path.is_file():
        check.fail(f"fichier absent: {path}")
        return ""
    return path.read_text(encoding="utf-8")


def frontmatter(path: Path, check: Check) -> dict:
    text = read(path, check)
    if not text.startswith("---\n"):
        check.fail(f"frontmatter absent: {path}")
        return {}
    parts = text.split("---\n", 2)
    try:
        data = yaml.safe_load(parts[1]) or {}
    except Exception as exc:
        check.fail(f"frontmatter YAML invalide: {path} ({exc})")
        return {}
    if len(parts) < 3 or not isinstance(data, dict):
        check.fail(f"frontmatter YAML non objet ou incomplet: {path}")
        return {}
    check.ok(f"frontmatter YAML valide: {path.name}")
    return data


def section(text: str, heading: str) -> str:
    match = re.search(rf"^## {re.escape(heading)}\s*$([\s\S]*?)(?=^## |\Z)", text, re.MULTILINE)
    return match.group(1).strip() if match else ""


def check_frontmatter(data: dict, check: Check) -> None:
    check.has_set(set(data), FRONTMATTER_KEYS, "DESIGN.md frontmatter clés minimales")
    check.has_set(set(data.get("refresh_when") or []), REFRESH_WHEN, "refresh_when complet")
    forbidden = set((data.get("claim_language") or {}).get("forbidden_without_proof") or [])
    check.has_set(forbidden, FORBIDDEN_CLAIMS, "claims interdits présents")


def check_quick_decision(design_text: str, check: Check) -> None:
    quick = section(design_text, "Décider vite")
    if not quick:
        check.fail("section Décider vite absente")
        return
    check.ok("section Décider vite présente")
    for label, needles in {
        "prototype": ["Prototype", "continuer avec limites"],
        "publication": ["Publication", "references/page-shell.md", "references/verification.md", "references/sources.md"],
        "claim conforme": ["Claim conforme", "refuser", "abaisser"],
        "hors périmètre": ["Hors périmètre État", "retirer le bloc marque"],
    }.items():
        check.contains(quick, needles, f"Décider vite: {label}")


def validate_load_when_needed(progressive: object, check: Check) -> dict[str, str]:
    if not isinstance(progressive, dict):
        check.fail("progressive_disclosure doit être un objet")
        return {}

    raw_routes = progressive.get("load_when_needed")
    if not isinstance(raw_routes, dict):
        check.fail("load_when_needed doit être un objet")
        return {}

    routes: dict[str, str] = {}
    for raw_key, raw_value in raw_routes.items():
        if not isinstance(raw_key, str):
            check.fail(f"load_when_needed clé non string: {raw_key!r}")
            continue
        key = raw_key.strip()
        if not key:
            check.fail("load_when_needed clé vide")
            continue
        if key != raw_key or not ROUTE_KEY_RE.fullmatch(key):
            check.fail(f"load_when_needed clé invalide: {raw_key!r}")
            continue

        if not isinstance(raw_value, str):
            check.fail(f"route {key}: valeur non string")
            continue
        value = raw_value.strip()
        if not value:
            check.fail(f"route {key}: valeur vide")
            continue
        if value != raw_value:
            check.fail(f"route {key}: chemin invalide: {raw_value!r}")
            continue
        if value.startswith("/"):
            check.fail(f"route {key}: chemin absolu interdit")
            continue
        if "\\" in value:
            check.fail(f"route {key}: backslash interdit")
            continue
        if ".." in PurePosixPath(value).parts:
            check.fail(f"route {key}: chemin parent interdit")
            continue
        if not ROUTE_PATH_RE.fullmatch(value):
            check.fail(f"route {key}: chemin hors references/*.md")
            continue

        routes[key] = value

    if routes:
        check.ok("load_when_needed chemins validés")
    return routes


def check_routes(data: dict, design_text: str, check: Check) -> None:
    progressive = data.get("progressive_disclosure") or {}
    routes = validate_load_when_needed(progressive, check)
    always_load = progressive.get("always_load") if isinstance(progressive, dict) else []
    check.ok("tokens.yaml toujours chargé") if "tokens.yaml" in (always_load or []) else check.fail("tokens.yaml absent de always_load")
    expected = {"page_shell": "references/page-shell.md", "verification": "references/verification.md", "sources": "references/sources.md"}
    for key, value in expected.items():
        actual = routes.get(key)
        check.ok(f"route {key}: {value}") if actual == value else check.fail(f"route {key}: attendu {value}, obtenu {actual!r}")
    check.contains(section(design_text, "Garde de publication"), list(expected.values()), "publication route vers page-shell, verification et sources")


def check_publication_guard(design_text: str, check: Check) -> None:
    publication = section(design_text, "Garde de publication")
    if not publication:
        check.fail("section Garde de publication absente")
        return
    check.ok("section Garde de publication présente")
    for label, needles in {
        "périmètre DSFR": ["périmètre DSFR"],
        "domaine ou agrément": [".gouv.fr", "agrément"],
        "mentions publication": ["données personnelles", "cookies", "licence", "mesure d'audience"],
        "fallback sans marque": ["bloc marque", "structure inspirée des fondamentaux DSFR"],
    }.items():
        check.contains(publication, needles, f"Garde de publication: {label}")


def check_text_rules(texts: dict[str, str], check: Check) -> None:
    for name, text in texts.items():
        check.contains(text, ["liens d'évitement", "toute page complète", "début de page", "Accéder au contenu"], f"{name}: règle liens d'évitement")
    design = texts["DESIGN.md"]
    check.contains(design, ["fragment ou composant isolé", "ne doit pas inventer d'enveloppe de page"], "DESIGN.md: fragment sans enveloppe inventée")
    check.contains(design, ["Marianne", "bloc marque", "République française", "simple style graphique", "hors périmètre autorisé"], "DESIGN.md: anti-pattern marque comme style")


def check_catalog_drift(design_text: str, check: Check) -> None:
    line_count = len(design_text.splitlines())
    if line_count <= DESIGN_LINE_LIMIT:
        check.ok(f"DESIGN.md taille routeur: {line_count}/{DESIGN_LINE_LIMIT} lignes")
    else:
        check.fail(f"DESIGN.md trop long pour un routeur: {line_count}/{DESIGN_LINE_LIMIT} lignes")
    check.fail("DESIGN.md contient une section catalogue") if re.search(r"^## .*catalogue", design_text, re.MULTILINE | re.IGNORECASE) else check.ok("aucune section catalogue dans DESIGN.md")
    terms = sorted(term for term in CATALOG_TERMS if term in design_text.lower())
    check.fail("trop de composants détaillés dans DESIGN.md: " + ", ".join(terms)) if len(terms) > 12 else check.ok(f"pas de dérive catalogue composants ({len(terms)}/12 termes)")


def main() -> int:
    dsfr = workspace_from_args() / "design-systems" / "dsfr"
    check = Check()
    paths = {
        "DESIGN.md": dsfr / "DESIGN.md",
        "page-shell.md": dsfr / "references" / "page-shell.md",
        "verification.md": dsfr / "references" / "verification.md",
    }
    texts = {name: read(path, check) for name, path in paths.items()}
    data = frontmatter(paths["DESIGN.md"], check)
    check_frontmatter(data, check)
    check_quick_decision(texts["DESIGN.md"], check)
    check_routes(data, texts["DESIGN.md"], check)
    check_publication_guard(texts["DESIGN.md"], check)
    check_text_rules(texts, check)
    check_catalog_drift(texts["DESIGN.md"], check)
    print(f"[{'FAIL' if check.failures else 'OK'}] routeur DSFR" + (f": {check.failures} erreur(s)" if check.failures else ""))
    return 1 if check.failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
