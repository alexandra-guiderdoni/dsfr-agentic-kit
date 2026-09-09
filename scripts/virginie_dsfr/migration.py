"""Séparation intégration / migration à partir des paquets officiels DSFR.

Un écart compte dans le verdict d'intégration seulement si les classes que la
règle attend existent dans la version DSFR observée. Sinon il relève de la
migration vers la version cible. Preuve : dist/dsfr.min.css de chaque paquet.
"""

from __future__ import annotations

import re
from pathlib import Path

CLASS_IN_TEXT_RE = re.compile(r"\bfr-[a-z0-9]+(?:-[a-z0-9]+)*(?:__[a-z0-9]+(?:-[a-z0-9]+)*)?(?:--[a-z0-9]+(?:-[a-z0-9]+)*)?\b")
CLASS_IN_CSS_RE = re.compile(r"\.(fr-[a-zA-Z0-9_-]+)")
CLASS_ATTR_RE = re.compile(r'class="([^"]*)"')
ID_LIKE_RE = re.compile(r'(?:id|aria-controls|aria-labelledby|aria-describedby|for|href)="#?([^"]*)"')

EXAMPLE_FOLDERS = {
    "consent_manager": "consent", "consent_service": "consent", "button_group": "button", "tag_group": "tag",
    "mega_menu": "header", "message_group": "input", "fieldset": "form", "enlarge_link": "card",
    "skiplink": "skiplink", "navigation": "navigation", "display": "display", "follow": "follow",
}


def package_dir(cache_dir: Path, version: str) -> Path:
    return cache_dir / f"gouvfr-dsfr-{version}" / "package"


CSS_FILES = ("dist/dsfr.min.css", "dist/utility/icons/icons.min.css", "dist/utility/utility.min.css")


def css_classes(cache_dir: Path, version: str) -> set[str] | None:
    """Classes définies par le paquet : cœur obligatoire, icônes et utilitaires si présents."""
    package = package_dir(cache_dir, version)
    core = package / CSS_FILES[0]
    if not core.is_file():
        return None
    classes: set[str] = set()
    for relative in CSS_FILES:
        path = package / relative
        if path.is_file():
            classes.update(CLASS_IN_CSS_RE.findall(path.read_text(encoding="utf-8", errors="replace")))
    return classes


def example_classes(cache_dir: Path, version: str, component: str) -> set[str] | None:
    folder = EXAMPLE_FOLDERS.get(component, component)
    path = package_dir(cache_dir, version) / "example" / "component" / folder / "index.html"
    if not path.is_file():
        return None
    text = path.read_text(encoding="utf-8", errors="replace")
    return {token for attr in CLASS_ATTR_RE.findall(text) for token in attr.split() if token.startswith("fr-")}


class CssIndex:
    """Classes DSFR réellement définies par la version observée et la version cible."""

    def __init__(self, cache_dir: Path, observed: str, target: str) -> None:
        self.cache_dir = Path(cache_dir)
        self.observed = observed
        self.target = target
        self.observed_classes = css_classes(self.cache_dir, observed)
        self.target_classes = css_classes(self.cache_dir, target)

    @property
    def available(self) -> bool:
        return self.observed_classes is not None and self.target_classes is not None

    def classify(self, expected_html: str, failed_conditions: list[str]) -> tuple[str, list[str]]:
        """Retourne (intégration|migration, classes attendues absentes de la version observée)."""
        if self.observed_classes is None:
            return "integration", []
        id_like = {token for attr in ID_LIKE_RE.findall(expected_html) for token in attr.split()}
        expected = {token for attr in CLASS_ATTR_RE.findall(expected_html) for token in attr.split() if token.startswith("fr-")}
        expected |= set(CLASS_IN_TEXT_RE.findall(" ".join(failed_conditions))) - id_like
        missing = sorted(c for c in expected if c not in self.observed_classes)
        in_target = [c for c in missing if self.target_classes and c in self.target_classes]
        return ("migration" if in_target else "integration"), missing

    def example_diff(self, component: str) -> dict[str, list[str]] | None:
        before = example_classes(self.cache_dir, self.observed, component)
        after = example_classes(self.cache_dir, self.target, component)
        if before is None or after is None:
            return None
        return {"added": sorted(after - before), "removed": sorted(before - after)}
