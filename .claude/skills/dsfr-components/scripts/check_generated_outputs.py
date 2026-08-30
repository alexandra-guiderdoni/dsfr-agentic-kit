#!/usr/bin/env python3
"""Static checks for generated DSFR pages and component variants."""

from __future__ import annotations

import argparse
import importlib.util
import json
import os
import re
import shutil
import subprocess
import sys
import tarfile
import tempfile
from html.parser import HTMLParser
from itertools import chain
from pathlib import Path
from typing import Iterable, NamedTuple


SKILL_DIR = Path(__file__).resolve().parents[1]
# Racine de travail : le workspace hôte quand le skill est installé sous
# <racine>/.claude/skills/, sinon le dossier du skill lui-même.
WORKSPACE = SKILL_DIR.parents[2] if len(SKILL_DIR.parents) > 2 else SKILL_DIR
PAGE_SCRIPT = SKILL_DIR / "scripts" / "generate_page.py"
COMPONENT_SCRIPT = SKILL_DIR / "scripts" / "generate_component.py"
ATOM_SCRIPT = SKILL_DIR / "scripts" / "generate_atom.py"
LAYOUT_SCRIPT = SKILL_DIR / "scripts" / "generate_layout.py"
FIELD_SCRIPT = SKILL_DIR / "scripts" / "generate_field.py"
INVENTORY_SCRIPT = SKILL_DIR / "scripts" / "inventory_official_coverage.py"
ICONS_SCRIPT = SKILL_DIR / "scripts" / "list_icons.py"
BUILDER_SCRIPT = SKILL_DIR / "scripts" / "generate_assembled_page.py"
SCHEMA_CHECK_SCRIPT = SKILL_DIR / "scripts" / "check_assembled_page_schema.py"
BUILDER_SCHEMA = SKILL_DIR / "schemas" / "generate_assembled_page.schema.json"
BUILDER_EXAMPLES_DIR = SKILL_DIR / "examples" / "assembled"

REQUIRED_FILES = (PAGE_SCRIPT, COMPONENT_SCRIPT, ATOM_SCRIPT, LAYOUT_SCRIPT,
                  FIELD_SCRIPT, BUILDER_SCRIPT, SCHEMA_CHECK_SCRIPT, BUILDER_SCHEMA)


def check_required_files() -> None:
    """Échec immédiat et nommé si un script ou schéma attendu manque : sinon le
    validateur plante à la première utilisation, loin de la cause. Appelée par
    main(), pas à l'import : check_golden_outputs.py importe ce module sans
    avoir besoin du builder."""
    for required in REQUIRED_FILES:
        if not required.exists():
            sys.exit(f"FAIL fichier attendu introuvable : {required}")
LIBRARY_PATH = SKILL_DIR / "assets" / "dsfr_complete_library.json"
TEMPLATE_BASE = SKILL_DIR / "assets" / "template-base.html"
LOCAL_ARTIFACT_NAMES = {".DS_Store", "__pycache__"}

# Lue depuis generate_page.py, source unique : une copie locale finissait
# par diverger sans bruit et le validateur couvrait une liste fantôme.
sys.path.insert(0, str(SKILL_DIR / "scripts"))
sys.dont_write_bytecode = True
from generate_page import PAGE_TYPES  # noqa: E402
import generate_field as gf  # noqa: E402

FIELD_NAMES = list(gf.FIELDS)  # source unique : generate_field.FIELDS
import generate_page  # noqa: E402

# Les 11 composants de formulaire de la bibliothèque, pour --forms-only.
FORM_COMPONENTS = {"form", "input", "select", "upload", "checkbox", "radio", "toggle", "range", "password", "search", "segmented"}
import dsfr_component_registry as registry  # noqa: E402
COMPONENT_ROOT_CLASS_CONTRACTS: dict[str, tuple[str, ...]] = {
    "accordion": ("fr-accordion",),
    "alert": ("fr-alert",),
    "back_to_top": ("fr-link",),
    "badge": ("fr-badge",),
    "breadcrumb": ("fr-breadcrumb",),
    "button": ("fr-btn",),
    "button_group": ("fr-btns-group",),
    "callout": ("fr-callout",),
    "card": ("fr-card",),
    "checkbox": ("fr-checkbox-group",),
    "connect": ("fr-connect",),
    "consent": ("fr-consent-banner",),
    "display": ("fr-display",),
    "download": ("fr-download__link", "fr-download"),
    "follow": ("fr-follow",),
    "footer": ("fr-footer",),
    "form": ("fr-fieldset",),
    "header": ("fr-header",),
    "highlight": ("fr-highlight",),
    "input": ("fr-input-group",),
    "link": ("fr-link",),
    "logo": ("fr-logo", "fr-header__operator"),
    "modal": ("fr-modal",),
    "navigation": ("fr-nav",),
    "notice": ("fr-notice",),
    "pagination": ("fr-pagination",),
    "password": ("fr-password",),
    "quote": ("fr-quote",),
    "radio": ("fr-radio-group",),
    "range": ("fr-range-group",),
    "search": ("fr-search-bar",),
    "segmented": ("fr-segmented",),
    "select": ("fr-select-group",),
    "share": ("fr-share",),
    "sidemenu": ("fr-sidemenu",),
    "skiplinks": ("fr-skiplinks",),
    "stepper": ("fr-stepper",),
    "summary": ("fr-summary",),
    "table": ("fr-table",),
    "tabs": ("fr-tabs",),
    "tag": ("fr-tag",),
    "tile": ("fr-tile",),
    "toggle": ("fr-toggle",),
    "tooltip": ("fr-tooltip",),
    "transcription": ("fr-transcription",),
    "translate": ("fr-translate",),
    "upload": ("fr-upload-group",),
}
ARIA_REFERENCE_ATTRS = {"aria-controls", "aria-labelledby", "aria-describedby"}
# Schémas exécutables : refusés dans href et src, après retrait des caractères
# de contrôle que les navigateurs tolèrent avant le deux-points.
UNSAFE_URL_NOISE_RE = re.compile(r"[\x00-\x20\x7f]")
UNSAFE_URL_SCHEMES = ("javascript:", "vbscript:")
STALE_FOOTER_RE = re.compile(r"https://(?:www\.)?service-public\.fr\b|>\s*(?:www\.)?service-public\.fr\s*<")
CLASS_RE = re.compile(r"\b(?:fr|ri)-[A-Za-z0-9_-]+\b")
CSS_CLASS_RE = re.compile(r"\.((?:fr|ri)-[A-Za-z0-9_-]+)")
# Variables CSS consommées dans les sorties générées (var(--…)) et définies au
# :root du paquet. check_official_classes valide aussi ces variables pour éviter
# qu'un token inventé (ex. --bf500) passe inaperçu.
CSS_VAR_USE_RE = re.compile(r"var\(\s*(--[\w-]+)")
OFFICIAL_VAR_DEF_RE = re.compile(r"(--[\w-]+)\s*:")
# Variables CSS légitimement absentes du CSS statique du paquet (par ex. posées
# dynamiquement par le JS DSFR). Documenter chaque entrée ajoutée ici.
LOCAL_CSS_VAR_ALLOWLIST: set[str] = set()
DEFAULT_OFFICIAL_CACHE_DIR = Path(
    os.environ.get("DSFR_OFFICIAL_CACHE_DIR") or "~/.cache/dsfr-official-cache"
).expanduser()


class Issue(NamedTuple):
    code: str
    scope: str
    detail: str


class Element(NamedTuple):
    index: int
    tag: str
    attrs: dict[str, str]
    classes: set[str]
    parent_index: int | None


def check_local_artifacts() -> list[Issue]:
    artifacts = [
        str(path.relative_to(SKILL_DIR))
        for path in sorted(SKILL_DIR.rglob("*"))
        if path.name in LOCAL_ARTIFACT_NAMES
    ]
    if not artifacts:
        return []
    return [
        Issue(
            "local_artifact",
            "skill",
            "forbidden local artifact(s): " + ", ".join(artifacts),
        )
    ]


class MarkupFacts(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.elements: list[Element] = []
        self.stack: list[int] = []
        self.ids: set[str] = set()
        self.id_counts: dict[str, int] = {}
        self.aria_refs: list[tuple[str, str]] = []
        self.classes: set[str] = set()
        self.hrefs: list[str] = []
        self.srcs: list[str] = []
        self.inline_handlers: list[str] = []
        self.form_constraints: list[str] = []
        self.has_skiplinks = False

    VOID_TAGS = {
        "area",
        "base",
        "br",
        "col",
        "embed",
        "hr",
        "img",
        "input",
        "link",
        "meta",
        "param",
        "source",
        "track",
        "wbr",
    }

    def _close_implicitly(self, tag: str) -> None:
        """Fermetures implicites du HTML (li, dt/dd, option, td/th, tr, p) : sans
        elles, un `li` non fermé devient le parent du suivant."""
        while self.stack:
            top = self.elements[self.stack[-1]].tag
            if (tag == "li" and top == "li") or (tag in {"dt", "dd"} and top in {"dt", "dd"}) \
                    or (tag == "option" and top == "option") or (tag in {"td", "th"} and top in {"td", "th"}) \
                    or (tag == "tr" and top in {"td", "th", "tr"}) or (tag in BLOCK_TAGS and top == "p"):
                self.stack.pop()
                continue
            break

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        self._close_implicitly(tag)
        # Attribut répété : la première occurrence compte, comme dans le navigateur.
        data: dict[str, str] = {}
        for name, value in attrs:
            data.setdefault(name, value or "")

        element_id = data.get("id")
        if element_id:
            self.ids.add(element_id)
            self.id_counts[element_id] = self.id_counts.get(element_id, 0) + 1

        classes = data.get("class", "").split()
        class_set = set(classes)
        index = len(self.elements)
        parent_index = self.stack[-1] if self.stack else None
        self.elements.append(Element(index, tag, data, class_set, parent_index))
        if tag not in self.VOID_TAGS:
            self.stack.append(index)
        self.classes.update(classes)
        if "fr-skiplinks" in classes:
            self.has_skiplinks = True

        href = data.get("href")
        if href is not None:
            self.hrefs.append(href)
        src = data.get("src")
        if src is not None:
            self.srcs.append(src)
        for name in data:
            if is_dom_event_handler(name):
                self.inline_handlers.append(f"{tag}@{name}")

        for attr in ARIA_REFERENCE_ATTRS:
            for target in data.get(attr, "").split():
                self.aria_refs.append((attr, target))

        if tag in {"input", "select", "textarea"}:
            present = []
            for attr in ("required", "aria-required", "pattern", "aria-invalid"):
                if attr in data:
                    present.append(attr)
            if present:
                label = element_id or data.get("name") or tag
                self.form_constraints.append(f"{tag}#{label}:{','.join(present)}")

    def handle_endtag(self, tag: str) -> None:
        for offset, index in enumerate(reversed(self.stack)):
            if self.elements[index].tag == tag:
                del self.stack[len(self.stack) - offset - 1 :]
                return

    def handle_startendtag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        self.handle_starttag(tag, attrs)
        if self.stack and self.elements[self.stack[-1]].tag == tag:
            self.stack.pop()


def run_command(args: list[str]) -> str:
    env = os.environ.copy()
    env.setdefault("PYTHONDONTWRITEBYTECODE", "1")
    result = subprocess.run(
        args,
        cwd=WORKSPACE,
        env=env,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    if result.returncode != 0:
        command = " ".join(args)
        raise RuntimeError(f"{command} failed: {result.stderr.strip()}")
    return result.stdout


# Gestionnaires d'événements DOM (attributs on*) : liste blanche, pour ne pas
# confondre un attribut quelconque commençant par « on » avec un gestionnaire.
DOM_EVENT_HANDLERS = frozenset({
    "onabort", "onbeforeunload", "onblur", "oncancel", "oncanplay", "oncanplaythrough", "onchange", "onclick",
    "onclose", "oncontextmenu", "oncopy", "oncuechange", "oncut", "ondblclick", "ondurationchange", "onemptied",
    "onended", "onerror", "onfocus", "onfocusin", "onfocusout", "onformdata", "onhashchange", "oninput", "oninvalid",
    "onload", "onloadeddata", "onloadedmetadata", "onloadstart", "onmessage", "onoffline", "ononline", "onpagehide",
    "onpageshow", "onpaste", "onpause", "onplay", "onplaying", "onpopstate", "onprogress", "onratechange", "onreset",
    "onresize", "onscroll", "onscrollend", "onsearch", "onsecuritypolicyviolation", "onseeked", "onseeking", "onselect",
    "onselectionchange", "onselectstart", "onslotchange", "onstalled", "onstorage", "onsubmit", "onsuspend",
    "ontimeupdate", "ontoggle", "onunload", "onvolumechange", "onwaiting", "onwheel",
})
DOM_EVENT_PREFIXES = ("onmouse", "onkey", "onpointer", "ontouch", "ondrag", "ondrop", "onanimation", "ontransition", "ongotpointer", "onlostpointer")
BLOCK_TAGS = frozenset({
    "address", "article", "aside", "blockquote", "details", "dialog", "div", "dl", "fieldset", "figcaption", "figure",
    "footer", "form", "h1", "h2", "h3", "h4", "h5", "h6", "header", "hr", "main", "nav", "ol", "p", "pre", "section",
    "table", "ul",
})


def is_dom_event_handler(name: str) -> bool:
    lowered = name.lower()
    return lowered in DOM_EVENT_HANDLERS or lowered.startswith(DOM_EVENT_PREFIXES)


def parse_markup(html: str) -> MarkupFacts:
    parser = MarkupFacts()
    parser.feed(html)
    parser.close()
    return parser


def find_elements(
    facts: MarkupFacts,
    tag: str | None = None,
    class_name: str | None = None,
    attr: str | None = None,
    value: str | None = None,
) -> list[Element]:
    if value is not None and attr is None:
        raise ValueError("find_elements : value exige attr")
    matches: list[Element] = []
    for element in facts.elements:
        if tag is not None and element.tag != tag:
            continue
        if class_name is not None and class_name not in element.classes:
            continue
        if attr is not None and attr not in element.attrs:
            continue
        if value is not None and element.attrs.get(attr or "") != value:
            continue
        matches.append(element)
    return matches


def has_element(
    facts: MarkupFacts,
    tag: str | None = None,
    class_name: str | None = None,
    attr: str | None = None,
    value: str | None = None,
) -> bool:
    return bool(find_elements(facts, tag=tag, class_name=class_name, attr=attr, value=value))


def element_by_id(facts: MarkupFacts, element_id: str) -> Element | None:
    for element in facts.elements:
        if element.attrs.get("id") == element_id:
            return element
    return None


def parent_element(facts: MarkupFacts, element: Element) -> Element | None:
    if element.parent_index is None:
        return None
    return facts.elements[element.parent_index]


def has_ancestor_class(facts: MarkupFacts, element: Element, class_name: str) -> bool:
    parent = parent_element(facts, element)
    while parent is not None:
        if class_name in parent.classes:
            return True
        parent = parent_element(facts, parent)
    return False


def has_descendant_class(facts: MarkupFacts, element: Element, class_name: str) -> bool:
    for candidate in facts.elements:
        parent = parent_element(facts, candidate)
        while parent is not None:
            if parent.index == element.index:
                if class_name in candidate.classes:
                    return True
                break
            parent = parent_element(facts, parent)
    return False


def target_has_class(facts: MarkupFacts, target_id: str, class_name: str) -> bool:
    target = element_by_id(facts, target_id)
    return bool(target and class_name in target.classes)


def has_ancestor_tag(facts: MarkupFacts, element: Element, tag: str) -> bool:
    parent = parent_element(facts, element)
    while parent is not None:
        if parent.tag == tag:
            return True
        parent = parent_element(facts, parent)
    return False


def is_descendant(facts: MarkupFacts, candidate: Element, ancestor: Element) -> bool:
    parent = parent_element(facts, candidate)
    while parent is not None:
        if parent.index == ancestor.index:
            return True
        parent = parent_element(facts, parent)
    return False


def check_unsafe_url_schemes(scope: str, facts: MarkupFacts) -> list[Issue]:
    """Refuse tout href/src au schéma exécutable, quelle que soit la sortie."""
    unsafe = []
    for attr, values in (("href", facts.hrefs), ("src", facts.srcs)):
        for value in values:
            normalised = UNSAFE_URL_NOISE_RE.sub("", value).lower()
            if normalised.startswith(UNSAFE_URL_SCHEMES):
                unsafe.append(f"{attr}={value[:40]}")
    if unsafe:
        return [Issue("unsafe_url_scheme", scope, ", ".join(unsafe[:8]))]
    return []


def check_heading_hierarchy(scope: str, facts: MarkupFacts, require_h1_first: bool = True) -> list[Issue]:
    """Titres sans saut de niveau ; pour un document, un seul h1 et en premier (SKILL.md, Contraintes DSFR)."""
    levels = [int(element.tag[1]) for element in facts.elements if element.tag in {"h1", "h2", "h3", "h4", "h5", "h6"}]
    problems: list[str] = []
    if require_h1_first and levels and levels[0] != 1:
        problems.append(f"first heading is h{levels[0]}")
    if require_h1_first and levels.count(1) > 1:
        problems.append(f"{levels.count(1)} h1")
    for previous, current in zip(levels, levels[1:]):
        if current > previous + 1:
            problems.append(f"h{previous} -> h{current}")
    if problems:
        return [Issue("heading_hierarchy", scope, ", ".join(dict.fromkeys(problems)))]
    return []


# Ancres fournies par toute page du skill (generate_page.py, template-base.html) :
# un fragment isolé peut y pointer sans les contenir lui-même.
PAGE_ANCHOR_IDS = frozenset({"top", "contenu", "footer", "navigation"})


def check_anchor_targets(scope: str, facts: MarkupFacts, tolerated: frozenset[str] = frozenset()) -> list[Issue]:
    """Toute ancre interne href=\"#id\" pointe vers un id présent dans la sortie
    (ou, pour un fragment, vers une ancre garantie par les pages du skill)."""
    missing = sorted({
        href for href in facts.hrefs
        if href.startswith("#") and len(href) > 1 and href[1:] not in facts.ids and href[1:] not in tolerated
    })
    if missing:
        return [Issue("missing_anchor_target", scope, ", ".join(missing[:8]))]
    return []


def check_button_types(scope: str, facts: MarkupFacts) -> list[Issue]:
    """Tout <button> porte un type explicite : sans lui, un bouton vaut submit dans un formulaire."""
    missing = [
        "button." + (".".join(sorted(element.classes)) or element.attrs.get("id", "?"))
        for element in facts.elements
        if element.tag == "button" and "type" not in element.attrs
    ]
    if missing:
        return [Issue("button_without_type", scope, ", ".join(missing[:6]))]
    return []


def check_external_links(scope: str, facts: MarkupFacts) -> list[Issue]:
    """target=_blank (quelle que soit la casse) exige rel=noopener et une annonce
    « nouvelle fenêtre » dans le title (SKILL.md, Contraintes DSFR ; exemples
    officiels share/footer 1.15.2)."""
    issues: list[Issue] = []
    blank = [
        element for element in facts.elements
        if element.tag == "a" and element.attrs.get("target", "").strip().lower() == "_blank"
    ]
    bad = [
        element.attrs.get("href", "?")[:40]
        for element in blank
        if "noopener" not in element.attrs.get("rel", "").split()
    ]
    if bad:
        issues.append(Issue("target_blank_without_noopener", scope, ", ".join(bad[:6])))
    silent = [
        element.attrs.get("href", "?")[:40]
        for element in blank
        if "nouvelle fenêtre" not in element.attrs.get("title", "").lower()
    ]
    if silent:
        issues.append(Issue("target_blank_not_announced", scope, ", ".join(silent[:6])))
    return issues


def _ancestor_tags(facts: MarkupFacts, element) -> set[str]:
    tags: set[str] = set()
    parent = element.parent_index
    while parent is not None:
        tags.add(facts.elements[parent].tag)
        parent = facts.elements[parent].parent_index
    return tags


def check_table_header_scope(scope: str, facts: MarkupFacts) -> list[Issue]:
    """Tout <th> porte scope (col dans thead, row ailleurs) : association
    explicite en-tête/cellule pour les technologies d'assistance."""
    bad = []
    for element in facts.elements:
        if element.tag != "th":
            continue
        expected = "col" if "thead" in _ancestor_tags(facts, element) else "row"
        if element.attrs.get("scope") != expected:
            bad.append(f"th[scope={element.attrs.get('scope', 'absent')}] attendu {expected}")
    if bad:
        return [Issue("th_without_scope", scope, ", ".join(bad[:4]))]
    return []


def check_form_control_names(scope: str, facts: MarkupFacts) -> list[Issue]:
    """Tout contrôle soumis porte un name. Exemptés : boutons, interrupteurs
    (fr-toggle) et cases « afficher le mot de passe » (fr-password__checkbox),
    sans name dans les exemples officiels 1.15.2."""
    missing = []
    for element in facts.elements:
        if element.tag not in {"input", "select", "textarea"} or "name" in element.attrs:
            continue
        if element.attrs.get("type", "text") in {"submit", "button", "reset", "image"}:
            continue
        if has_ancestor_class(facts, element, "fr-toggle") or has_ancestor_class(facts, element, "fr-password__checkbox"):
            continue
        missing.append(f"{element.tag}#{element.attrs.get('id', '?')}")
    if missing:
        return [Issue("form_control_without_name", scope, ", ".join(missing[:6]))]
    return []


NATIVE_CONSTRAINT_ATTRS = ("min", "max", "step", "minlength", "maxlength")


def check_native_constraints(scope: str, facts: MarkupFacts) -> list[Issue]:
    """Validation différée : min/max/step/minlength/maxlength déclenchent la
    validation native du navigateur au premier envoi (bulle système non
    restituée) ; hors curseur, ils suivent le même sort que required/pattern."""
    found = []
    for element in facts.elements:
        if element.tag != "input" or element.attrs.get("type") == "range":
            continue
        present = [attr for attr in NATIVE_CONSTRAINT_ATTRS if attr in element.attrs]
        if present:
            found.append(f"input#{element.attrs.get('id', '?')}:{','.join(present)}")
    if found:
        return [Issue("resting_native_constraint", scope, ", ".join(found[:6]))]
    return []


UNESCAPED_AMPERSAND_RE = re.compile(r'="[^"]*&(?!(?:amp|lt|gt|quot|apos|#\d+|#x[0-9a-fA-F]+);)[^"]*"')


def check_unescaped_ampersand(scope: str, html: str) -> list[Issue]:
    """Une esperluette nue dans une valeur d'attribut est une référence de
    caractère non terminée : HTML invalide."""
    hits = UNESCAPED_AMPERSAND_RE.findall(html)
    if hits:
        return [Issue("unescaped_ampersand", scope, f"{len(hits)} valeur(s) d'attribut")]
    return []


def check_select_placeholder_values(scope: str, facts: MarkupFacts) -> list[Issue]:
    """Une option de valeur vide n'est acceptable que comme placeholder
    désactivé (`selected disabled`, 1.15.0 #1424) : sinon un choix est soumis
    avec une valeur vide, indiscernable d'une absence de sélection."""
    bad = [
        option.attrs.get("value", "")
        for option in find_elements(facts, tag="option")
        if option.attrs.get("value", "") == "" and "disabled" not in option.attrs
    ]
    if bad:
        return [Issue("select_option_empty_value", scope, f"{len(bad)} option(s) value=\"\" non désactivée(s)")]
    return []


def check_range_double_names(scope: str, facts: MarkupFacts) -> list[Issue]:
    """Curseur double (exemple officiel range 1.15.2) : chaque input porte un
    id et un aria-label propres (Valeur minimale / Valeur maximale)."""
    problems = []
    for container in find_elements(facts, tag="div", class_name="fr-range--double"):
        inputs = [
            element for element in find_elements(facts, tag="input", attr="type", value="range")
            if has_ancestor_class(facts, element, "fr-range--double")
        ]
        ids = [element.attrs.get("id") for element in inputs]
        labels = [element.attrs.get("aria-label") for element in inputs]
        if len(inputs) < 2 or None in ids or len(set(ids)) != len(ids):
            problems.append("ids distincts requis sur les deux curseurs")
        if None in labels or len(set(labels)) != len(labels):
            problems.append("aria-label distincts requis sur les deux curseurs")
        break
    if problems:
        return [Issue("range_double_names", scope, ", ".join(problems))]
    return []


def check_modal_title_level(scope: str, facts: MarkupFacts) -> list[Issue]:
    """Le titre d'une modale est un h2 (example/component/modal et consent 1.15.2)."""
    bad = sorted({element.tag for element in facts.elements if "fr-modal__title" in element.classes and element.tag != "h2"})
    if bad:
        return [Issue("modal_title_level", scope, "fr-modal__title must be h2, got " + ", ".join(bad))]
    return []


def check_table_structure(scope: str, facts: MarkupFacts) -> list[Issue]:
    """fr-table > fr-table__wrapper > fr-table__container > fr-table__content (1.15.2)."""
    for element in facts.elements:
        if element.tag == "div" and "fr-table" in element.classes and not all(
            has_descendant_class(facts, element, class_name)
            for class_name in ("fr-table__wrapper", "fr-table__container", "fr-table__content")
        ):
            return [Issue("table_structure", scope, "fr-table without wrapper/container/content")]
    return []


def check_search_bar_contract(scope: str, facts: MarkupFacts, require_form: bool) -> list[Issue]:
    """Barre de recherche DSFR 1.15 (#1432) : bouton `type="submit"` et, pour
    une page complète, intégration dans un `<form>` (fonctionnement sans JS)."""
    missing: list[str] = []
    for bar in find_elements(facts, class_name="fr-search-bar"):
        if bar.attrs.get("role") != "search":
            missing.append(".fr-search-bar[role=search]")
        buttons = [
            button for button in find_elements(facts, tag="button", class_name="fr-btn")
            if is_descendant(facts, button, bar)
        ]
        if not buttons or not any(button.attrs.get("type") == "submit" for button in buttons):
            missing.append(".fr-search-bar button.fr-btn[type=submit]")
        if require_form and not has_ancestor_tag(facts, bar, "form"):
            missing.append(".fr-search-bar inside <form>")
    return [Issue("search_bar_contract", scope, ", ".join(sorted(set(missing))))] if missing else []


def check_select_options_contract(scope: str, facts: MarkupFacts) -> list[Issue]:
    """DSFR 1.15.0 (#1424, DSFR-63) : l'option vide d'un sélecteur ne porte
    plus `hidden` ; `selected disabled` suffit."""
    hidden = [option for option in find_elements(facts, tag="option") if "hidden" in option.attrs]
    if not hidden:
        return []
    return [Issue("select_option_hidden", scope, f"{len(hidden)} option[hidden] (retiré par DSFR 1.15.0 #1424)")]


def check_range_contract(scope: str, _variant: str, facts: MarkupFacts) -> list[Issue]:
    """Curseur DSFR 1.15.2 (gabarit range.ejs, #1407) : `fr-range` est un
    conteneur `div` autour de l'input, avec sortie, bornes et messages."""
    missing: list[str] = []
    if not has_element(facts, class_name="fr-range-group"):
        missing.append(".fr-range-group")
    if has_element(facts, tag="input", class_name="fr-range"):
        missing.append("fr-range posée sur l'input au lieu du conteneur div")
    containers = find_elements(facts, tag="div", class_name="fr-range")
    if not containers:
        missing.append("div.fr-range")
    for container in containers:
        for part in ("fr-range__output", "fr-range__min", "fr-range__max"):
            if not has_descendant_class(facts, container, part):
                missing.append(f".fr-range .{part}")
    for output in find_elements(facts, class_name="fr-range__output"):
        if output.attrs.get("aria-hidden") != "true":
            missing.append(".fr-range__output[aria-hidden=true]")
    label_targets = {
        element.attrs["for"] for element in find_elements(facts, tag="label", class_name="fr-label", attr="for")
    }
    inputs = find_elements(facts, tag="input", attr="type", value="range")
    if not inputs:
        missing.append("input[type=range]")
    for element in inputs:
        if not has_ancestor_class(facts, element, "fr-range"):
            missing.append("input[type=range] inside .fr-range")
        if element.attrs.get("id") not in label_targets and "aria-labelledby" not in element.attrs:
            missing.append("input[type=range] sans label for/id")
    if not has_element(facts, class_name="fr-messages-group", attr="aria-live", value="polite"):
        missing.append(".fr-messages-group[aria-live=polite]")
    return [Issue("structure_contract", scope, ", ".join(sorted(set(missing))))] if missing else []


def check_translate_contract(scope: str, _variant: str, facts: MarkupFacts) -> list[Issue]:
    """Sélecteur de langue DSFR 1.15 (#1431) : `div.fr-translate.fr-nav`
    contenant `fr-nav__item`, sans `nav` ni `role="navigation"`."""
    missing: list[str] = []
    roots = find_elements(facts, class_name="fr-translate")
    if not roots:
        missing.append(".fr-translate")
    for root in roots:
        if root.tag == "nav" or root.attrs.get("role") == "navigation":
            missing.append("fr-translate en nav/role=navigation (retiré par DSFR 1.15.0 #1431)")
        if "fr-nav" not in root.classes:
            missing.append(".fr-translate.fr-nav")
        if not has_descendant_class(facts, root, "fr-nav__item"):
            missing.append(".fr-translate .fr-nav__item")
    buttons = find_elements(facts, tag="button", class_name="fr-translate__btn")
    if not buttons:
        missing.append("button.fr-translate__btn")
    for button in buttons:
        for attr in ("aria-controls", "aria-expanded", "title"):
            if attr not in button.attrs:
                missing.append(f"fr-translate__btn[{attr}]")
        if has_descendant_class(facts, button, "fr-translate__language"):
            missing.append("fr-translate__language dans le bouton (réservée aux liens)")
    links = find_elements(facts, tag="a", class_name="fr-translate__language")
    if not links:
        missing.append("a.fr-translate__language")
    for link in links:
        if "fr-nav__link" not in link.classes:
            missing.append("a.fr-translate__language.fr-nav__link")
        for attr in ("hreflang", "lang"):
            if attr not in link.attrs:
                missing.append(f"fr-translate__language[{attr}]")
    return [Issue("structure_contract", scope, ", ".join(sorted(set(missing))))] if missing else []


def check_header_contract(scope: str, variant: str, facts: MarkupFacts) -> list[Issue]:
    missing: list[str] = []
    if not has_element(facts, tag="header", class_name="fr-header", attr="role", value="banner"):
        missing.append("header.fr-header[role=banner]")
    if not has_element(facts, class_name="fr-header__service"):
        missing.append(".fr-header__service")
    if variant.endswith("neutral") and has_element(facts, class_name="fr-logo"):
        missing.append("neutral variant must not contain .fr-logo")
    if variant in {"basic", "with_search", "with_search_republique"} and not has_element(facts, class_name="fr-logo"):
        missing.append("brand variant missing .fr-logo")
    if variant.startswith("with_search"):
        search_buttons = find_elements(facts, tag="button", class_name="fr-btn--search")
        if not search_buttons:
            missing.append("button.fr-btn--search")
        for button in search_buttons:
            target = button.attrs.get("aria-controls", "")
            if not target or not target_has_class(facts, target, "fr-header__search"):
                missing.append("search button aria-controls target")
        search_modals = find_elements(facts, class_name="fr-header__search")
        if not search_modals:
            missing.append(".fr-header__search")
        for modal in search_modals:
            if "fr-modal" not in modal.classes:
                missing.append(".fr-header__search.fr-modal")
            if not has_ancestor_class(facts, modal, "fr-header__tools"):
                missing.append(".fr-header__search inside .fr-header__tools")
            parent = parent_element(facts, modal)
            if parent and parent.tag == "header":
                missing.append(".fr-header__search direct child of header")
            if not has_descendant_class(facts, modal, "fr-container-lg--fluid"):
                missing.append(".fr-header__search .fr-container-lg--fluid")
        if not has_element(facts, class_name="fr-search-bar", attr="role", value="search"):
            missing.append(".fr-search-bar[role=search]")
    if variant.startswith("with_search_") and scope.startswith("page:"):
        # En-tête des pages complètes : le menu mobile et sa cible modale.
        menu_buttons = find_elements(facts, tag="button", class_name="fr-btn--menu")
        if not menu_buttons:
            missing.append("button.fr-btn--menu")
        for button in menu_buttons:
            target = button.attrs.get("aria-controls", "")
            if not target or not target_has_class(facts, target, "fr-header__menu") or not target_has_class(facts, target, "fr-modal"):
                missing.append("menu button aria-controls target .fr-header__menu.fr-modal")
    return [Issue("structure_contract", scope, ", ".join(missing))] if missing else []


def check_footer_contract(scope: str, variant: str, facts: MarkupFacts) -> list[Issue]:
    missing: list[str] = []
    if not has_element(facts, tag="footer", class_name="fr-footer", attr="role", value="contentinfo"):
        missing.append("footer.fr-footer[role=contentinfo]")
    if variant == "neutral" and has_element(facts, class_name="fr-logo"):
        missing.append("neutral variant must not contain .fr-logo")
    if variant == "basic" and not has_element(facts, class_name="fr-logo"):
        missing.append("basic footer missing .fr-logo")
    if variant in {"neutral", "basic"} and not has_element(facts, class_name="fr-footer__content"):
        missing.append(".fr-footer__content")
    if variant == "with_partners":
        if not has_element(facts, class_name="fr-footer__partners"):
            missing.append(".fr-footer__partners")
        if not has_element(facts, class_name="fr-footer__partners-link"):
            missing.append(".fr-footer__partners-link")
    return [Issue("structure_contract", scope, ", ".join(missing))] if missing else []


def check_form_contract(scope: str, facts: MarkupFacts) -> list[Issue]:
    missing: list[str] = []
    if not has_element(facts, tag="form"):
        missing.append("form")
    if not has_element(facts, tag="fieldset", class_name="fr-fieldset"):
        missing.append("fieldset.fr-fieldset")
    if not has_element(facts, tag="legend", class_name="fr-fieldset__legend"):
        missing.append("legend.fr-fieldset__legend")
    if not has_element(facts, tag="button", class_name="fr-btn", attr="type", value="submit"):
        missing.append("button.fr-btn[type=submit]")

    label_targets = {
        element.attrs["for"] for element in find_elements(facts, tag="label", class_name="fr-label", attr="for")
    }
    controls = [
        element for element in facts.elements
        if element.tag in {"input", "select", "textarea"} and element.attrs.get("type") != "hidden"
    ]
    if not controls:
        missing.append("form controls")
    unlabeled = [
        element.attrs.get("id") or element.attrs.get("name") or element.tag
        for element in controls
        if not element.attrs.get("id") or element.attrs.get("id") not in label_targets
    ]
    if unlabeled:
        missing.append("unlabeled controls: " + ", ".join(unlabeled[:6]))
    return [Issue("structure_contract", scope, ", ".join(missing))] if missing else []


def check_accordion_contract(scope: str, facts: MarkupFacts) -> list[Issue]:
    missing: list[str] = []
    if not has_element(facts, tag="section", class_name="fr-accordion"):
        missing.append("section.fr-accordion")
    buttons = find_elements(facts, tag="button", class_name="fr-accordion__btn")
    if not buttons:
        missing.append("button.fr-accordion__btn")
    for button in buttons:
        if "aria-expanded" not in button.attrs:
            missing.append("accordion button aria-expanded")
        target = button.attrs.get("aria-controls", "")
        if not target or not target_has_class(facts, target, "fr-collapse"):
            missing.append("accordion aria-controls target .fr-collapse")
    return [Issue("structure_contract", scope, ", ".join(sorted(set(missing))))] if missing else []


def check_tabs_contract(scope: str, facts: MarkupFacts) -> list[Issue]:
    missing: list[str] = []
    if not has_element(facts, class_name="fr-tabs"):
        missing.append(".fr-tabs")
    if not has_element(facts, class_name="fr-tabs__list", attr="role", value="tablist"):
        missing.append(".fr-tabs__list[role=tablist]")

    tabs = find_elements(facts, tag="button", class_name="fr-tabs__tab")
    if not tabs:
        missing.append("button.fr-tabs__tab")
    for tab in tabs:
        tab_id = tab.attrs.get("id", "")
        if not tab_id:
            missing.append("tab id")
        if tab.attrs.get("role") != "tab":
            missing.append("tab role=tab")
        if "aria-selected" not in tab.attrs:
            missing.append("tab aria-selected")
        panel_id = tab.attrs.get("aria-controls", "")
        panel = element_by_id(facts, panel_id) if panel_id else None
        if not panel or "fr-tabs__panel" not in panel.classes:
            missing.append("tab aria-controls panel")
        elif panel.attrs.get("role") != "tabpanel" or panel.attrs.get("aria-labelledby") != tab_id:
            missing.append("panel role or aria-labelledby")
    if not any(tab.attrs.get("aria-selected") == "true" for tab in tabs):
        missing.append("selected tab")
    if not has_element(facts, class_name="fr-tabs__panel--selected"):
        missing.append(".fr-tabs__panel--selected")
    return [Issue("structure_contract", scope, ", ".join(sorted(set(missing))))] if missing else []


def check_modal_contract(scope: str, variant: str, facts: MarkupFacts) -> list[Issue]:
    missing: list[str] = []
    dialogs = find_elements(facts, tag="dialog", class_name="fr-modal")
    if not dialogs:
        missing.append("dialog.fr-modal")
    for dialog in dialogs:
        modal_id = dialog.attrs.get("id", "")
        if not modal_id:
            missing.append("modal id")
        # Exemples officiels modal/consent 1.15.2 : <dialog> sans role redondant.
        if "role" in dialog.attrs:
            missing.append("modal dialog carries a redundant role")
        title_id = dialog.attrs.get("aria-labelledby", "")
        if not title_id or not target_has_class(facts, title_id, "fr-modal__title"):
            missing.append("modal aria-labelledby title")
        close_buttons = find_elements(facts, tag="button", class_name="fr-btn--close")
        if not any(button.attrs.get("aria-controls") == modal_id for button in close_buttons):
            missing.append("close button aria-controls modal")
    if variant == "basic" and dialogs and not any(
        button.attrs.get("aria-controls") == dialogs[0].attrs.get("id", "")
        for button in find_elements(facts, tag="button", class_name="fr-btn")
    ):
        missing.append("open button aria-controls modal")
    return [Issue("structure_contract", scope, ", ".join(sorted(set(missing))))] if missing else []


def check_toggle_contract(scope: str, facts: MarkupFacts) -> list[Issue]:
    missing: list[str] = []
    inputs = find_elements(facts, tag="input", class_name="fr-toggle__input")
    if not inputs:
        missing.append("input.fr-toggle__input")
    for input_element in inputs:
        input_id = input_element.attrs.get("id", "")
        if not input_id:
            missing.append("toggle input id")
            continue
        labels = find_elements(
            facts,
            tag="label",
            class_name="fr-toggle__label",
            attr="for",
            value=input_id,
        )
        if not labels:
            missing.append(f"label.fr-toggle__label[for={input_id}]")
        describedby = input_element.attrs.get("aria-describedby", "").split()
        message_targets = [
            target for target in describedby
            if target_has_class(facts, target, "fr-messages-group")
        ]
        if not message_targets:
            missing.append(f"{input_id} aria-describedby messages group")
        for target in message_targets:
            target_element = element_by_id(facts, target)
            if target_element and target_element.attrs.get("aria-live") != "polite":
                missing.append(f"{target} aria-live=polite")
        if scope.endswith(".hint_state") and len(describedby) < 2:
            missing.append(f"{input_id} aria-describedby hint + messages")
        if scope.endswith(".hint_state") and labels:
            label = labels[0]
            if "data-fr-checked-label" not in label.attrs:
                missing.append("label data-fr-checked-label")
            if "data-fr-unchecked-label" not in label.attrs:
                missing.append("label data-fr-unchecked-label")

    fieldsets = find_elements(facts, tag="fieldset", class_name="fr-fieldset")
    if scope.endswith(".group"):
        if not fieldsets:
            missing.append("fieldset.fr-fieldset")
        if not has_element(facts, tag="legend", class_name="fr-fieldset__legend"):
            missing.append("legend.fr-fieldset__legend")
        if not has_element(facts, class_name="fr-fieldset__element"):
            missing.append(".fr-fieldset__element")
        if not has_element(facts, tag="ul", class_name="fr-toggle__list"):
            missing.append("ul.fr-toggle__list")
        for fieldset in fieldsets:
            describedby = fieldset.attrs.get("aria-labelledby", "").split()
            if not any(target_has_class(facts, target, "fr-fieldset__legend") for target in describedby):
                missing.append("fieldset aria-labelledby legend")
            if not any(target_has_class(facts, target, "fr-messages-group") for target in describedby):
                missing.append("fieldset aria-labelledby messages group")
    return [Issue("structure_contract", scope, ", ".join(sorted(set(missing))))] if missing else []


def check_notice_contract(scope: str, facts: MarkupFacts) -> list[Issue]:
    missing: list[str] = []
    if (scope.endswith(".basic") or scope.startswith("native-config:notice")) and not has_element(facts, class_name="fr-notice--info"):
        missing.append(".fr-notice--info")
    if scope.endswith(".desc_link") or scope.endswith(".info"):
        if not has_element(facts, class_name="fr-notice__desc"):
            missing.append(".fr-notice__desc")
        if not has_element(facts, tag="a", class_name="fr-notice__link"):
            missing.append("a.fr-notice__link")
    for button in find_elements(facts, tag="button", class_name="fr-btn--close"):
        if button.attrs.get("type") != "button":
            missing.append("button.fr-btn--close[type=button]")
    return [Issue("structure_contract", scope, ", ".join(sorted(set(missing))))] if missing else []


def check_tooltip_contract(scope: str, facts: MarkupFacts) -> list[Issue]:
    if not (scope.startswith("native-config:tooltip") or scope.startswith("component:tooltip")):
        return []
    missing: list[str] = []
    buttons = find_elements(facts, tag="button", class_name="fr-btn--tooltip")
    tooltips = find_elements(facts, tag="span", class_name="fr-tooltip")
    if not buttons:
        missing.append("button.fr-btn--tooltip")
    if not tooltips:
        missing.append("span.fr-tooltip")
    if buttons and buttons[0].attrs.get("type") != "button":
        missing.append("button.fr-btn--tooltip[type=button]")
    if buttons and tooltips:
        target = buttons[0].attrs.get("aria-describedby", "")
        if not target or target != tooltips[0].attrs.get("id"):
            missing.append("button aria-describedby tooltip id")
        if buttons[0].index > tooltips[0].index:
            missing.append("button before tooltip span")
    for tooltip in tooltips:
        if tooltip.attrs.get("role") != "tooltip":
            missing.append("span.fr-tooltip[role=tooltip]")
        if "aria-hidden" in tooltip.attrs:
            missing.append("span.fr-tooltip must not set aria-hidden statically")
    return [Issue("structure_contract", scope, ", ".join(sorted(set(missing))))] if missing else []


def check_follow_contract(scope: str, facts: MarkupFacts) -> list[Issue]:
    missing: list[str] = []
    if not has_element(facts, class_name="fr-follow__newsletter"):
        missing.append(".fr-follow__newsletter")
    if not has_element(facts, class_name="fr-follow__social"):
        missing.append(".fr-follow__social")
    # Bouton officiel (le projet branche son formulaire) ou lien d'abonnement
    # réel (newsletter_url), dans le bloc newsletter.
    newsletter_blocks = find_elements(facts, class_name="fr-follow__newsletter")
    subscribe = [
        element for element in find_elements(facts, class_name="fr-btn")
        if any(is_descendant(facts, element, block) for block in newsletter_blocks)
        and (
            (element.tag == "button" and element.attrs.get("type") == "button")
            or (element.tag == "a" and element.attrs.get("href"))
        )
    ]
    if not subscribe:
        missing.append("newsletter button.fr-btn[type=button] or a.fr-btn[href]")
    if not has_element(facts, tag="a", class_name="fr-btn--twitter-x"):
        missing.append("a.fr-btn--twitter-x")
    if "fr-btn--twitter" in facts.classes:
        missing.append("legacy .fr-btn--twitter")
    return [Issue("structure_contract", scope, ", ".join(sorted(set(missing))))] if missing else []


def check_card_contract(scope: str, _variant: str, facts: MarkupFacts) -> list[Issue]:
    missing: list[str] = []
    if not has_element(facts, class_name="fr-card__body"):
        missing.append(".fr-card__body")
    if not has_element(facts, class_name="fr-card__content"):
        missing.append(".fr-card__content")
    if not any(has_element(facts, tag=f"h{level}", class_name="fr-card__title") for level in range(2, 7)):
        missing.append("hx.fr-card__title")
    cards = find_elements(facts, class_name="fr-card")
    if any("fr-enlarge-link" in card.classes for card in cards):
        links_in_title = [
            a for a in find_elements(facts, tag="a")
            if has_ancestor_class(facts, a, "fr-card__title")
        ]
        if not links_in_title:
            missing.append("fr-enlarge-link card title missing <a>")
    return [Issue("structure_contract", scope, ", ".join(missing))] if missing else []


def check_alert_contract(scope: str, _variant: str, facts: MarkupFacts) -> list[Issue]:
    missing: list[str] = []
    alert_types = ("fr-alert--info", "fr-alert--success", "fr-alert--warning", "fr-alert--error")
    if not any(has_element(facts, class_name=t) for t in alert_types):
        missing.append("fr-alert--{info|success|warning|error}")
    for button in find_elements(facts, tag="button", class_name="fr-btn--close"):
        if not button.attrs.get("title") and not button.attrs.get("aria-label"):
            missing.append("fr-btn--close accessible name (title/aria-label)")
            break
    return [Issue("structure_contract", scope, ", ".join(sorted(set(missing))))] if missing else []


def check_callout_contract(scope: str, _variant: str, facts: MarkupFacts) -> list[Issue]:
    missing: list[str] = []
    if not any(has_element(facts, tag=f"h{level}", class_name="fr-callout__title") for level in range(2, 7)):
        missing.append("hx.fr-callout__title")
    if not has_element(facts, class_name="fr-callout__text"):
        missing.append(".fr-callout__text")
    return [Issue("structure_contract", scope, ", ".join(missing))] if missing else []


def check_tile_contract(scope: str, _variant: str, facts: MarkupFacts) -> list[Issue]:
    missing: list[str] = []
    if not has_element(facts, class_name="fr-tile__body"):
        missing.append(".fr-tile__body")
    if not any(has_element(facts, tag=f"h{level}", class_name="fr-tile__title") for level in range(2, 7)):
        missing.append("hx.fr-tile__title")
    tiles = find_elements(facts, class_name="fr-tile")
    if any("fr-enlarge-link" in tile.classes for tile in tiles):
        links_in_title = [
            a for a in find_elements(facts, tag="a")
            if has_ancestor_class(facts, a, "fr-tile__title")
        ]
        if not links_in_title:
            missing.append("fr-enlarge-link tile title missing <a>")
    return [Issue("structure_contract", scope, ", ".join(missing))] if missing else []


def check_badge_contract(scope: str, _variant: str, facts: MarkupFacts) -> list[Issue]:
    missing: list[str] = []
    if has_element(facts, class_name="fr-badges-group") and not has_element(
        facts, tag="ul", class_name="fr-badges-group"
    ):
        missing.append("ul.fr-badges-group")
    return [Issue("structure_contract", scope, ", ".join(missing))] if missing else []


def check_component_root_contract(component: str, scope: str, facts: MarkupFacts) -> list[Issue]:
    expected = COMPONENT_ROOT_CLASS_CONTRACTS.get(component)
    if not expected:
        return []
    if any(has_element(facts, class_name=class_name) for class_name in expected):
        return []
    return [
        Issue(
            "root_structure_contract",
            scope,
            "missing one of: " + ", ".join(expected),
        )
    ]


def check_component_structure(component: str, variant: str, scope: str, facts: MarkupFacts) -> list[Issue]:
    issues = check_component_root_contract(component, scope, facts)
    if component == "header":
        issues.extend(check_header_contract(scope, variant, facts))
        return issues
    if component == "footer":
        issues.extend(check_footer_contract(scope, variant, facts))
        return issues
    if component == "form":
        issues.extend(check_form_contract(scope, facts))
        return issues
    if component == "accordion":
        issues.extend(check_accordion_contract(scope, facts))
        return issues
    if component == "tabs":
        issues.extend(check_tabs_contract(scope, facts))
        return issues
    if component == "modal":
        issues.extend(check_modal_contract(scope, variant, facts))
        return issues
    if component == "toggle":
        issues.extend(check_toggle_contract(scope, facts))
        return issues
    if component == "notice":
        issues.extend(check_notice_contract(scope, facts))
        return issues
    if component == "tooltip":
        issues.extend(check_tooltip_contract(scope, facts))
        return issues
    if component == "follow":
        issues.extend(check_follow_contract(scope, facts))
        return issues
    if component == "card":
        issues.extend(check_card_contract(scope, variant, facts))
        return issues
    if component == "alert":
        issues.extend(check_alert_contract(scope, variant, facts))
        return issues
    if component == "callout":
        issues.extend(check_callout_contract(scope, variant, facts))
        return issues
    if component == "tile":
        issues.extend(check_tile_contract(scope, variant, facts))
        return issues
    if component == "badge":
        issues.extend(check_badge_contract(scope, variant, facts))
        return issues
    if component == "range":
        issues.extend(check_range_contract(scope, variant, facts))
        return issues
    if component == "translate":
        issues.extend(check_translate_contract(scope, variant, facts))
        return issues
    return issues


def iter_pages() -> Iterable[tuple[str, str]]:
    for page_type in PAGE_TYPES:
        html = run_command(
            [
                sys.executable,
                str(PAGE_SCRIPT),
                "--type",
                page_type,
                "--title",
                f"Validation {page_type}",
            ]
        )
        yield page_type, html


# Options de generate_page.py qui changent la structure : exercées sur la page
# standard pour que la séquence complète de check_pages s'y applique.
PAGE_OPTION_VARIANTS: list[tuple[str, list[str], dict[str, object]]] = [
    ("standard--republique", ["--brand-mode", "republique"], {"header": True, "footer": True, "brand": "republique"}),
    ("standard--no-header", ["--no-header"], {"header": False, "footer": True, "brand": "neutral"}),
    ("standard--no-footer", ["--no-footer"], {"header": True, "footer": False, "brand": "neutral"}),
    ("standard--dark", ["--dark"], {"header": True, "footer": True, "brand": "neutral", "dark": True}),
]


def iter_page_variants() -> Iterable[tuple[str, str, dict[str, object]]]:
    for label, extra, expect in PAGE_OPTION_VARIANTS:
        html = run_command([sys.executable, str(PAGE_SCRIPT), "--type", "standard", "--title", "Validation standard", *extra])
        yield label, html, expect


def check_page_head(scope: str, facts: MarkupFacts) -> list[Issue]:
    """SKILL.md : charset, viewport, CSS et JS DSFR sur toute page produite."""
    missing = []
    if not has_element(facts, tag="meta", attr="charset"):
        missing.append("meta[charset]")
    if not has_element(facts, tag="meta", attr="name", value="viewport"):
        missing.append("meta[name=viewport]")
    if not any("dsfr.min.css" in href for href in facts.hrefs):
        missing.append("link dsfr.min.css")
    if not any("dsfr.module.min.js" in src for src in facts.srcs):
        missing.append("script dsfr.module.min.js")
    if not has_element(facts, tag="html", attr="lang", value="fr"):
        missing.append("html[lang=fr]")
    if missing:
        return [Issue("page_head", scope, ", ".join(missing))]
    return []


def load_component_variants() -> list[tuple[str, str]]:
    try:
        library = json.loads(LIBRARY_PATH.read_text(encoding="utf-8"))
    except FileNotFoundError:
        sys.exit(f"FAIL bibliothèque introuvable : {LIBRARY_PATH}")
    except json.JSONDecodeError as exc:
        sys.exit(f"FAIL bibliothèque JSON illisible {LIBRARY_PATH}: {exc}")
    if not isinstance(library, dict):
        sys.exit(f"FAIL bibliothèque : objet JSON attendu dans {LIBRARY_PATH}")
    components = library.get("components", {})
    if not isinstance(components, dict):
        sys.exit(f"FAIL bibliothèque : 'components' doit être un objet dans {LIBRARY_PATH}")
    variants: list[tuple[str, str]] = []
    for component, data in sorted(components.items()):
        if not isinstance(data, dict) or not isinstance(data.get("html", {}), dict):
            sys.exit(f"FAIL bibliothèque : le composant '{component}' doit être un objet avec un champ 'html' objet ({LIBRARY_PATH})")
        html_variants = data.get("html", {})
        for variant in sorted(html_variants):
            variants.append((component, variant))
    return variants


def iter_components(only_forms: bool = False) -> Iterable[tuple[str, str, str]]:
    for component, variant in load_component_variants():
        if only_forms and component not in FORM_COMPONENTS:
            continue
        html = run_command(
            [
                sys.executable,
                str(COMPONENT_SCRIPT),
                component,
                "--variant",
                variant,
            ]
        )
        yield component, variant, html


# Configs représentatives couvrant les branches émettrices de classes des
# atomes et gabarits (celles que les défauts natifs n'exercent pas : size,
# fluid, couleur texte, structures card/tile). ASCII uniquement (passées en
# argv via subprocess, hors shell).
REPRESENTATIVE_ATOM_CONFIGS: list[tuple[str, str]] = [
    ("container", '{"size":"lg"}'),
    ("container", '{"fluid":true}'),
    ("grid", '{"gutters":true,"cols":[{"content":"A","md":6}]}'),
    ("grid", '{"tag":"ul","cols":[{"content":"A","md":6}]}'),
    ("col", '{"md":6}'),
    ("spacing", '{"size":4}'),
    ("pictogram", '{"src":"/x.svg"}'),
    ("color", '{"kind":"background","variant":"alt","color":"blue-france"}'),
    ("color", '{"kind":"text","variant":"action-high","color":"blue-france"}'),
    ("color", '{"kind":"text","variant":"default","color":"grey"}'),
]
# Cas négatifs des atomes : configurations que le générateur doit refuser.
# Les configurations représentatives n'exercent que blue-france et grey ; une
# couleur retirée d'un rôle par l'amont passerait donc inaperçue alors que la
# classe émise n'aurait plus de style. ASCII uniquement (argv, hors shell).
ATOM_NEGATIVE_CONFIGS: list[tuple[str, str, str, str]] = [
    (
        "atom-negative:color-background-red-marianne",
        "color",
        '{"kind":"background","variant":"alt","color":"red-marianne"}',
        "indisponible",
    ),
    (
        "atom-negative:color-text-red-marianne",
        "color",
        '{"kind":"text","variant":"action-high","color":"red-marianne"}',
        "indisponible",
    ),
    (
        "atom-negative:color-unknown-kind",
        "color",
        '{"kind":"artwork","color":"red-marianne"}',
        "inconnu",
    ),
    (
        "atom-negative:color-background-default-hors-echelle",
        "color",
        '{"kind":"background","variant":"default","color":"blue-france"}',
        "indisponible",
    ),
    (
        "atom-negative:color-text-title-hors-echelle",
        "color",
        '{"kind":"text","variant":"title","color":"green-menthe"}',
        "indisponible",
    ),
    (
        "atom-negative:color-variant-inconnu",
        "color",
        '{"kind":"text","variant":"lead","color":"grey"}',
        "inconnu",
    ),
    (
        "atom-negative:text-tag-injection",
        "text",
        '{"tag":"p><img src=x onerror=alert(1)><p","text":"hello"}',
        "inconnu",
    ),
    ("atom-negative:grid-config-list", "grid", "[1,2]", "objet"),
    ("atom-negative:grid-cols-string", "grid", '{"cols":"abc"}', "cols"),
    ("atom-negative:color-variant-without-color", "color", '{"kind":"text","variant":"nimporte-quoi","color":""}', "variant"),
    ("atom-negative:color-tag-injection", "color", '{"kind":"text","color":"grey","tag":"span onclick=alert(1) x"}', "tag"),
    ("atom-negative:col-span-out-of-range", "col", '{"span":99,"content":"x"}', "span"),
    ("atom-negative:col-offset-md-out-of-range", "col", '{"offset_md":12,"content":"x"}', "offset_md"),
    ("atom-negative:spacing-w-above-16", "spacing", '{"direction":"b","size":30,"unit":"w"}', "size"),
    ("atom-negative:col-md-negative", "col", '{"md":-3,"content":"x"}', "md"),
    ("atom-negative:spacing-kind-unknown", "spacing", '{"kind":"border"}', "kind"),
    ("atom-negative:spacing-size-out-of-range", "spacing", '{"size":999}', "size"),
    ("atom-negative:title-display-unknown", "title", '{"level":3,"display":"nimporte"}', "display"),
    ("atom-negative:text-size-unknown", "text", '{"size":"giant"}', "size"),
    ("atom-negative:icon-name-injection", "icon", '{"name":"x\\" onmouseover=\\"alert(1)"}', "name"),
    ("atom-negative:pictogram-negative-size", "pictogram", '{"size":-10}', "size"),
]
# Cas négatifs et attentes exprimés en arguments complets (options CLI, environnement).
ATOM_NEGATIVE_ARGS: list[tuple[str, list[str], str]] = [
    ("atom-negative:empty-output", ["bold", "--config", '{"text":"x"}', "--output", ""], "--output"),
    ("atom-negative:output-not-a-directory", ["bold", "--config", '{"text":"x"}', "--output", "/dev/null/y"], "Erreur"),
]
ATOM_EXPECTATIONS: list[tuple[str, list[str], dict[str, str], list[str], list[str]]] = [
    ("atom-expect:icon-title-accessible-name", ["icon", "--config", '{"name":"information-line","title":"Information"}'], {}, ['role="img"', 'aria-label="Information"'], []),
    ("atom-expect:grid-col-12-with-breakpoint", ["grid"], {}, ['class="fr-col fr-col-12 fr-col-md-6"'], []),
    ("atom-expect:grid-empty-list-stays-empty", ["grid", "--config", '{"cols":[]}'], {}, ['class="fr-grid-row"'], ["Colonne 1"]),
    ("atom-expect:col-breakpoint-offsets", ["col", "--config", '{"content":"A","md":6,"offset_md":3,"offset_lg":2}'], {}, ['fr-col-offset-md-3', 'fr-col-offset-lg-2'], []),
    ("atom-expect:color-content-raw", ["color", "--config", '{"kind":"text","color":"blue-france","content":"<b>x</b>"}'], {}, ['><b>x</b></span>'], ['&lt;b&gt;']),
    ("atom-expect:spacing-w-16", ["spacing", "--config", '{"direction":"b","size":16,"unit":"w"}'], {}, ['fr-mb-16w'], []),
    ("atom-expect:pictogram-unsafe-src-neutralised", ["pictogram", "--config", '{"src":"javascript:alert(1)"}'], {}, ['href="/#artwork-decorative"'], ['javascript:']),
]
# Cas négatifs des gabarits : brand_mode doit être validé comme dans
# generate_page.py (une faute de frappe ne doit pas apposer la marque de l'État).
LAYOUT_NEGATIVE_CONFIGS: list[tuple[str, str, str, str]] = [
    (
        "layout-negative:brand-mode-inconnu",
        "skeleton",
        '{"title":"T","brand_mode":"neutre"}',
        "brand_mode",
    ),
    ("layout-negative:sidebar-ratio-int", "sidebar", '{"ratio":4}', "ratio"),
    ("layout-negative:sidebar-ratio-sum", "sidebar", '{"ratio":"5-9"}', "ratio"),
    ("layout-negative:skeleton-empty-title", "skeleton", '{"title":""}', "title"),
]
LAYOUT_NEGATIVE_ARGS: list[tuple[str, list[str], str]] = [
    ("layout-negative:empty-output", ["skeleton", "--config", "{}", "--output", ""], "--output"),
]
LAYOUT_EXPECTATIONS: list[tuple[str, list[str], dict[str, str], list[str], list[str]]] = [
    ("layout-expect:card-grid-string-items", ["card-grid", "--config", '{"cards":["Carte A","Carte B"]}'], {}, [">Carte A<"], []),
    ("layout-expect:version-empty-fallback", ["skeleton", "--config", "{}"], {"DSFR_OFFICIAL_VERSION": ""}, ["dsfr@1.15.2/dist"], ["dsfr@/dist"]),
    ("layout-expect:tile-grid-content-container", ["tile-grid", "--config", '{"tiles":[{"title":"A","href":"/a"}]}'], {}, ['<div class="fr-tile__content">'], []),
]
# Cas négatifs des pages : le préfixe --assets est interpolé dans des attributs
# href/src, il doit être validé et échappé.
PAGE_NEGATIVE_ARGS: list[tuple[str, list[str], str]] = [
    (
        "page-negative:assets-attribute-injection",
        ["--type", "standard", "--title", "Injection", "--assets", 'https://x/" onload="alert(1)'],
        "assets",
    ),
    (
        "page-negative:assets-javascript-scheme",
        ["--type", "standard", "--title", "Injection", "--assets", "javascript:alert(1)//"],
        "assets",
    ),
    ("page-negative:empty-title", ["--type", "standard", "--title", ""], "title"),
    ("page-negative:empty-output", ["--type", "standard", "--title", "T", "--output", ""], "--output"),
    ("page-negative:output-not-a-directory", ["--type", "standard", "--title", "T", "--output", "/dev/null/x"], "Erreur"),
    ("page-negative:assets-empty", ["--type", "standard", "--title", "T", "--assets", ""], "assets"),
]
# Options CLI des pages : fragments attendus et interdits dans la sortie.
PAGE_EXPECTATIONS: list[tuple[str, list[str], dict[str, str], list[str], list[str]]] = [
    ("page-expect:no-footer-keeps-skiplinks", ["--type", "standard", "--title", "T", "--no-footer"], {}, ['class="fr-skiplinks"', 'href="#contenu"'], ['href="#footer"']),
    ("page-expect:no-header-drops-menu-skiplink", ["--type", "standard", "--title", "T", "--no-header"], {}, ['href="#contenu"'], ['href="#navigation"']),
    ("page-expect:brand-republique", ["--type", "standard", "--title", "T", "--brand-mode", "republique"], {}, ['class="fr-logo"'], []),
    ("page-expect:brand-neutral", ["--type", "standard", "--title", "T"], {}, [], ['class="fr-logo"']),
    ("page-expect:dark", ["--type", "standard", "--title", "T", "--dark"], {}, ['data-fr-scheme="dark"'], []),
    ("page-expect:sitemap-title", ["--type", "sitemap", "--title", "Mon plan"], {}, ["<h1>Mon plan</h1>"], ["<h1>Plan du site</h1>"]),
    ("page-expect:version-empty-fallback", ["--type", "standard", "--title", "T"], {"DSFR_OFFICIAL_VERSION": ""}, ["dsfr@1.15.2/dist/"], ["dsfr@/dist"]),
    ("page-expect:deferred-script-keeps-server-errors", ["--type", "form", "--title", "T"], {}, ["dropClientConstraints();"], []),
    ("page-expect:landing-tile-content", ["--type", "landing", "--title", "T"], {}, ['<div class="fr-tile__content">'], ['fr-tile--vertical"']),
    ("page-expect:content-code-preserved", ["--type", "standard", "--title", "T", "--content", '<p><code>href="#"</code></p>'], {}, ['<code>href="#"</code>'], []),
    ("page-expect:footer-external-links-announced", ["--type", "standard", "--title", "T"], {}, ['rel="noopener external"', "nouvelle fenêtre"], []),
    ("page-expect:form-required-notice", ["--type", "form", "--title", "T"], {}, ["Sauf mention contraire, tous les champs sont obligatoires."], []),
    ("page-expect:login-required-notice", ["--type", "login", "--title", "T"], {}, ["Sauf mention contraire, tous les champs sont obligatoires."], []),
    ("page-expect:account-required-notice", ["--type", "account", "--title", "T"], {}, ["Sauf mention contraire, tous les champs sont obligatoires."], []),
    ("page-expect:detail-legifrance-announced", ["--type", "detail", "--title", "T"], {}, ['title="Article L.XXX du Code Y - nouvelle fenêtre"'], []),
]
# Blocs fonctionnels : entrées invalides refusées, attributs officiels seulement.
FIELD_NEGATIVE_ARGS: list[tuple[str, list[str], str]] = [
    ("field-negative:civilite-options-string", ["civilite", "--config", '{"options":"ab"}'], "options"),
    ("field-negative:civilite-options-empty", ["civilite", "--config", '{"options":[]}'], "options"),
    ("field-negative:civilite-legend-empty", ["civilite", "--config", '{"legend":""}'], "legend"),
    ("field-negative:email-id-empty", ["email", "--config", '{"id":""}'], "id"),
    ("field-negative:email-label-empty", ["email", "--config", '{"label":""}'], "label"),
    ("field-negative:nom-prenom-order-unknown", ["nom-prenom", "--config", '{"order":"inconnu"}'], "order"),
    ("field-negative:societe-kind-unknown", ["societe", "--config", '{"kind":"siret2"}'], "kind"),
    ("field-negative:config-without-field", ["--config", "{}"], "bloc"),
    ("field-negative:config-list", ["email", "--config", "[]"], "objet"),
    ("field-negative:empty-output", ["email", "--output", ""], "--output"),
]
FIELD_EXPECTATIONS: list[tuple[str, list[str], dict[str, str], list[str], list[str]]] = [
    ("field-expect:date-unique-official-classes", ["date-unique"], {}, ["fr-fieldset__element--inline fr-fieldset__element--number", "fr-fieldset__element--inline-grow fr-fieldset__element--year"], ["fr-fieldset__element--year fr-fieldset__element--number", "fr-fieldset__element--number fr-fieldset__element--inline-grow"]),
]
# Inventaire et icônes : paquet incomplet refusé en message court, sorties propres.
TOOL_NEGATIVE_CASES: list[tuple[str, Path, list[str], dict[str, str], str]] = [
    ("icons-negative:validate-empty", ICONS_SCRIPT, ["--validate", ""], {}, "--validate"),
    ("icons-negative:filter-empty", ICONS_SCRIPT, ["--filter", ""], {}, "--filter"),
    ("icons-negative:validate-remix-name", ICONS_SCRIPT, ["--validate", "ri-account-circle-line"], {}, "ri-"),
    ("icons-negative:package-dir-invalid", ICONS_SCRIPT, [], {"DSFR_OFFICIAL_PACKAGE_DIR": "/nonexistent/paquet"}, "DSFR_OFFICIAL_PACKAGE_DIR"),
]
# Variables d'environnement piégées : refus nommé, jamais interpolées.
ENV_NEGATIVE_CASES: list[tuple[str, Path, list[str], dict[str, str], str]] = [
    ("page-negative:version-injection", PAGE_SCRIPT, ["--type", "standard", "--title", "T"], {"DSFR_OFFICIAL_VERSION": '1.15.2/x"><script>alert(1)</script><link href="'}, "DSFR_OFFICIAL_VERSION"),
    ("layout-negative:version-injection", LAYOUT_SCRIPT, ["skeleton", "--config", "{}"], {"DSFR_OFFICIAL_VERSION": '1.15.2/x"><script>alert(1)</script><link href="'}, "DSFR_OFFICIAL_VERSION"),
]
# Cas négatifs du générateur de composants : entrées utilisateur prévisibles qui
# doivent produire une erreur courte (code 1, sans trace Python).
COMPONENT_NEGATIVE_ARGS: list[tuple[str, list[str], str]] = [
    ("component-negative:config-null", ["button", "--config", "null"], "objet"),
    ("component-negative:tag-unknown-color", ["tag", "--config", '{"label":"T","color":"rouge"}'], "color"),
    ("component-negative:card-unknown-orientation", ["card", "--config", '{"title":"T","orientation":"diagonale"}'], "orientation"),
    ("component-negative:logo-invalid-width", ["logo", "--config", '{"operator_src":"/l.svg","operator_max_width":"3.5rem;color:red"}'], "operator_max_width"),
    ("component-negative:input-error-and-valid", ["input", "--config", '{"label":"N","error":"e","valid":"v"}'], "exclusifs"),
    ("component-negative:content-video-without-title", ["content", "--config", '{"title":"T","video":"https://www.youtube.com/embed/x"}'], "video_title"),
    ("component-negative:content-video-unsafe-src", ["content", "--config", '{"title":"T","video":"javascript:alert(1)","video_title":"V"}'], "http"),
    ("component-negative:stepper-current-above-total", ["stepper", "--config", '{"current":9,"total":3}'], "current"),
    ("component-negative:stepper-total-zero", ["stepper", "--config", '{"current":0,"total":0}'], "total"),
    ("component-negative:range-min-above-max", ["range", "--config", '{"min":100,"max":0,"value":-5}'], "min"),
    ("component-negative:range-non-integer", ["range", "--config", '{"min":"a","max":10}'], "entier"),
    ("component-negative:rich-block-unknown-type", ["content", "--config", '{"title":"T","body_structured":{"blocks":[{"type":"table"}]}}'], "type 'table' inconnu"),
    ("component-negative:config-list", ["accordion", "--config", "[]"], "objet"),
    ("component-negative:config-with-variant", ["button", "--variant", "primary", "--config", '{"label":"X"}'], "--variant"),
    ("component-negative:display-unknown-key", ["display", "--config", '{"cle_inconnue":1}'], "invalide"),
    ("component-negative:logo-operator-without-src", ["logo", "--config", '{"brand":"operator"}'], "operator_src"),
    ("component-negative:pagination-total-zero", ["pagination", "--config", '{"total":0,"current":1}'], "total"),
    ("component-negative:pagination-current-out-of-range", ["pagination", "--config", '{"total":3,"current":9}'], "current"),
    ("component-negative:card-image-javascript", ["card", "--config", '{"title":"T","image":"javascript:alert(1)"}'], "image"),
    ("component-negative:footer-partner-without-src", ["footer", "--config", '{"partners":{"main_partner":{"href":"/p","alt":"P"}}}'], "src"),
    ("component-negative:footer-partner-without-alt", ["footer", "--config", '{"partners":{"main_partner":{"href":"/p","src":"/logo.png"}}}'], "alt"),
    ("component-negative:button-icon-injection", ["button", "--config", '{"label":"X","icon":"fr-icon-x\\" onclick=\\"alert(1)"}'], "icon"),
    ("component-negative:button-icon-position-unknown", ["button", "--config", '{"label":"X","icon":"fr-icon-check-line","icon_position":"top"}'], "icon_position"),
    ("component-negative:tag-icon-injection", ["tag", "--config", '{"label":"X","icon":"fr-icon-x\\" onclick=\\"alert(1)"}'], "icon"),
    ("component-negative:callout-icon-injection", ["callout", "--config", '{"title":"T","text":"t","icon":"fr-icon-x\\" onclick=\\"alert(1)"}'], "icon"),
    ("component-negative:link-icon-injection", ["link", "--config", '{"label":"X","icon":"fr-icon-x\\" onclick=\\"alert(1)"}'], "icon"),
    ("component-negative:table-rows-strings", ["table", "--config", '{"headers":["A","B"],"rows":["Oui","Non"]}'], "rows"),
    ("component-negative:translate-current-unknown", ["translate", "--config", '{"current":"de"}'], "current"),
    ("component-negative:accordion-rich-content-unknown", ["accordion", "--config", '{"items":[{"title":"T","content":{"type":"table","rows":[[1,2]]}}]}'], "content"),
]
# Attentes positives : la sortie (code 0) doit contenir ces fragments.
COMPONENT_EXPECTATIONS: list[tuple[str, list[str], list[str]]] = [
    ("component-expect:input-required-with-hint", ["input", "--config", '{"label":"Nom","required":true,"hint":"Votre nom"}'], ["Champ obligatoire", "Votre nom"]),
    ("component-expect:accordion-id-prefix", ["accordion", "--config", '{"items":[{"title":"T","content":"C"}],"id_prefix":"faq"}'], ['aria-controls="faq-1"']),
    ("component-expect:breadcrumb-string-items", ["breadcrumb", "--config", '{"items":["Accueil","Page"]}'], [">Accueil<"]),
    ("component-expect:summary-string-items", ["summary", "--config", '{"items":["Section A"]}'], ["Section A"]),
    ("component-expect:navigation-item-without-label", ["navigation", "--config", '{"items":[{"href":"/a"}]}'], ["Rubrique 1"]),
    ("component-expect:content-body-text", ["content", "--config", '{"title":"T","body_text":"<b>x</b>"}'], ["&lt;b&gt;x&lt;/b&gt;"]),
    ("component-expect:notice-link-blank", ["notice", "--config", '{"title":"Info","link":{"href":"https://exemple.gouv.fr","label":"En savoir plus","target":"_blank"}}'], ['rel="noopener"']),
    ("component-expect:card-backslash-protocol-relative", ["card", "--config", '{"title":"T","link":"/\\\\evil.example/x"}'], ['href="/"']),
    ("component-expect:breadcrumb-default-items", ["breadcrumb"], ["fr-breadcrumb__link"]),
    ("component-expect:form-distinct-ids", ["form", "--config", "{\"fields\":[{\"label\":\"Nom\"},{\"label\":\"nom\"},{\"label\":\"N'om\"}]}"], ['id="nom"', 'id="nom-2"', 'id="n-om"']),
    ("component-expect:tile-content-container", ["tile"], ['<div class="fr-tile__content">']),
    ("component-expect:header-language-label", ["header", "--config", '{"service_title":"S","languages":[{"code":"FR","label":"Français","href":"/fr","active":true},{"code":"EN","label":"English","href":"/en"}]}'], ['>FR<span class="fr-hidden-lg">&nbsp;- Français</span>', 'id="header-translate-menu"']),
    ("component-expect:header-translate-id", ["header", "--config", '{"languages":[{"code":"FR","label":"Français","href":"/fr"}],"translate_id":"langues"}'], ['aria-controls="langues"']),
    ("component-expect:input-slug-and-spacing", ["input", "--config", '{"label":"Nom / Prénom"}'], ['id="nom---prénom"', 'name="nom---prénom" />']),
    ("component-expect:checkbox-item-id", ["checkbox", "--config", '{"legend":"Choix","items":[{"label":"A","id":"explicite"}]}'], ['id="explicite"', 'for="explicite"']),
    ("component-expect:radio-item-id", ["radio", "--config", '{"legend":"Choix","items":[{"label":"A","id":"radio-a"}]}'], ['id="radio-a"', 'for="radio-a"']),
    ("component-expect:select-label-only-option", ["select", "--config", '{"label":"Nom","options":[{"value":"a"},{"label":"b"}]}'], ['<option value="b">b</option>']),
    ("component-expect:footer-absolute-link-announced", ["footer", "--config", '{"content_links":[{"label":"Mon site","href":"https://mon-site.gouv.fr"}]}'], ['title="Mon site - nouvelle fenêtre"', 'rel="noopener external"']),
    ("component-expect:footer-target-uppercase", ["footer", "--config", '{"content_links":[{"label":"X","href":"https://x.fr","target":"_BLANK"}]}'], ['target="_blank"', 'rel="noopener"', 'title="X - nouvelle fenêtre"']),
    ("component-expect:rich-link-target-uppercase", ["accordion", "--config", '{"items":[{"title":"T","content":{"link":{"label":"L","href":"https://x.fr","target":" _Blank "}}}]}'], ['target="_blank"', 'rel="noopener"', 'title="L - nouvelle fenêtre"']),
    ("component-expect:alert-static-without-role", ["alert", "--config", '{"alert_type":"success"}'], ['<div class="fr-alert fr-alert--success">']),
    ("component-expect:alert-live-error", ["alert", "--config", '{"alert_type":"error","live":true}'], ['role="alert"']),
    ("component-expect:alert-live-info", ["alert", "--config", '{"alert_type":"info","live":true}'], ['role="status"']),
    ("component-expect:range-value-clamped", ["range", "--config", '{"min":0,"max":10,"value":50}'], ['value="10"', '<span class="fr-range__output" aria-hidden="true">10</span>']),
    ("component-expect:share-mailto-same-window", ["share"], ['title="Partager sur Facebook - nouvelle fenêtre"', 'href="mailto:?subject=Partage">']),
    ("component-expect:card-vertical-header-after-body", ["card", "--config", '{"title":"T","image":"/img.png","image_alt":"Vue"}'], ['<div class="fr-card">', '</div>\n    <div class="fr-card__header">', '<img class="fr-responsive-img" src="/img.png" alt="Vue" />']),
    ("component-expect:card-horizontal", ["card", "--config", '{"title":"T","orientation":"horizontal"}'], ['<div class="fr-card fr-card--horizontal">']),
    ("component-expect:download-wrapper", ["download"], ['<div class="fr-download">']),
    ("component-expect:download-group-wrapper", ["download", "--config", '{"items":[{"label":"A","href":"/a.pdf","detail":"PDF"}]}'], ['<li>\n            <div class="fr-download">']),
    ("component-expect:quote-column-image-last", ["quote", "--config", '{"text":"T","author":"A","source":"S","image":"/p.jpg"}'], ['<figure class="fr-quote fr-quote--column">', '</ul>\n        <div class="fr-quote__image"><img class="fr-responsive-img"']),
    ("component-expect:transcription-fullscreen-modal", ["transcription"], ['aria-controls="fr-transcription-modal-transcription-1"', 'id="fr-transcription-modal-transcription-1"', 'data-fr-opened="false"']),
    ("component-expect:password-messages-described", ["password", "--config", '{"new":true}'], ['id="password-input-messages"', 'aria-describedby="password-input-messages"']),
    ("component-expect:stepper-title-then-state", ["stepper", "--config", '{"current":2,"total":4,"title":"Titre","next":"Suite"}'], ['Titre\n        <span class="fr-stepper__state">Étape 2 sur 4</span>', "Étape suivante :"]),
    ("component-expect:footer-official-links", ["footer"], ['href="https://info.gouv.fr"', 'href="https://data.gouv.fr"']),
    ("component-expect:logo-operator-responsive", ["logo", "--config", '{"operator_src":"/logo.svg","operator_alt":"Op"}'], ['<img class="fr-responsive-img" style="max-width:3.5rem;" src="/logo.svg" alt="Op">']),
    ("component-expect:modal-buttons-group", ["modal"], ['<div class="fr-btns-group fr-btns-group--right fr-btns-group--inline-reverse fr-btns-group--inline-lg">', '<dialog id="fr-modal" class="fr-modal" aria-labelledby="fr-modal-title">']),
    ("component-expect:tag-color", ["tag", "--config", '{"label":"T","color":"green-menthe"}'], ['class="fr-tag fr-tag--green-menthe"']),
    ("component-expect:input-error-state", ["input", "--config", '{"label":"Nom","error":"Champ requis"}'], ['fr-input-group--error', 'class="fr-input fr-input--error"', 'aria-describedby="nom-error"']),
    ("component-expect:input-valid-state", ["input", "--config", '{"label":"Nom","valid":"Bien reçu"}'], ['fr-input-group--valid', 'class="fr-input fr-input--valid"', 'class="fr-valid-text"']),
    ("component-expect:alert-close-without-aria-label", ["alert", "--config", '{"closable":true}'], ['<button type="button" class="fr-btn--close fr-btn" title="Masquer le message">']),
    ("component-expect:content-media", ["content", "--config", '{"title":"Légende","image":"/img.png","image_alt":"Vue"}'], ['<figure role="group" class="fr-content-media" aria-label="Légende">', '<figcaption class="fr-content-media__caption">Légende</figcaption>']),
    ("component-expect:content-media-video", ["content", "--config", '{"title":"Présentation","video":"https://www.youtube.com/embed/x","video_title":"Vidéo de présentation - voir transcription"}'], ['<iframe title="Vidéo de présentation - voir transcription" class="fr-responsive-vid" src="https://www.youtube.com/embed/x" allow="accelerometer; autoplay; encrypted-media; gyroscope; picture-in-picture" allowfullscreen></iframe>']),
]
REPRESENTATIVE_LAYOUT_CONFIGS: list[tuple[str, str]] = [
    ("card-grid", '{"cards":[{"title":"A","desc":"B","href":"/a"}],"md":4}'),
    ("tile-grid", '{"tiles":[{"title":"A","href":"/a"}]}'),
    # href à schéma exécutable : doit être neutralisé (esc_href), pas recopié.
    ("card-grid", '{"cards":[{"title":"A","desc":"B","href":"javascript:alert(1)"}]}'),
    ("tile-grid", '{"tiles":[{"title":"A","href":"javascript:alert(1)"}]}'),
    ("skeleton", '{}'),
    ("columns", '{}'),
    ("sidebar", '{}'),
]
REPRESENTATIVE_COMPONENT_CONFIGS: list[tuple[str, str, str]] = [
    (
        "connect",
        "pro",
        '{"brand":"pro"}',
    ),
    (
        "header",
        "with_search_neutral",
        '{"service_title":"Mon service","search":{"label":"Rechercher"}}',
    ),
    (
        "header",
        "with_search_true",
        '{"service_title":"Mon service","search":true}',
    ),
    (
        "header",
        "with_search_empty",
        '{"service_title":"Mon service","search":{}}',
    ),
    (
        "toggle",
        "base",
        '{}',
    ),
    (
        "toggle",
        "hint_state",
        '{"label":"Recevoir la lettre d information","hint":"Texte d aide","state":true}',
    ),
    (
        "toggle",
        "group",
        '{"legend":"Preferences de notification","items":[{"label":"Courriel","id":"notif-email"},{"label":"SMS","id":"notif-sms"}]}',
    ),
    (
        "notice",
        "desc_link",
        '{"title":"Information importante","description":"Texte de description","link":{"label":"Voir le detail","href":"/detail"},"closable":true}',
    ),
    (
        "tooltip",
        "default",
        '{}',
    ),
    (
        "follow",
        "default",
        '{}',
    ),
]


# Composants sans classe racine unique : exception nommée, jamais silencieuse.
ROOT_CONTRACT_EXEMPT = {
    "content": "bloc éditorial générique (div/article sans classe) ; avec `image`, figure.fr-content-media (attente component-expect:content-media)",
}


def native_component_names() -> list[str]:
    """Union du registre natif (generate_component.NATIVE_COMPONENTS) et de la
    bibliothèque JSON : un natif sans variante figée reste exercé."""
    import generate_component as gc  # noqa: PLC0415
    return sorted(set(gc.NATIVE_COMPONENTS) | {component for component, _ in load_component_variants()})


def check_root_contract_coverage() -> list[Issue]:
    """Tout composant a un contrat de classe racine, ou une exemption nommée."""
    missing = [name for name in native_component_names() if name not in COMPONENT_ROOT_CLASS_CONTRACTS and name not in ROOT_CONTRACT_EXEMPT]
    if missing:
        return [Issue("root_contract_missing", "components:registry", ", ".join(missing))]
    return []


def iter_native_component_defaults() -> Iterable[tuple[str, str]]:
    """Sorties natives par défaut (--config implicite) de chaque composant."""
    names = native_component_names()
    for name in names:
        html = run_command([sys.executable, str(COMPONENT_SCRIPT), name])
        yield f"native:{name}", html


def iter_fields() -> Iterable[tuple[str, str]]:
    """Sorties natives des blocs fonctionnels (generate_field.py).

    Non couverts par check_components (variantes JSON) ni par les configs
    représentatives : on les exerce ici pour check_common et la collecte de
    classes officielles.
    """
    for name in FIELD_NAMES:
        html = run_command([sys.executable, str(FIELD_SCRIPT), name])
        yield f"field:{name}", html


def _h1_section(title: str = "Titre") -> dict:
    return {"block": "content", "title": title, "heading_level": 1, "body_text": "Texte."}


def _nested_columns(depth: int) -> dict:
    inner: dict = {"block": "callout", "title": "C", "text": "t", "heading_level": 2}
    for _ in range(depth):
        inner = {"block": "columns", "columns": [[inner]]}
    return inner


BUILDER_CONFIG = {
    "title": "Smoke builder",
    "description": "Description meta du smoke builder.",
    "header": {
        "brand_mode": "republique",
        "service_title": "Smoke",
        "navigation": [{"label": "Accueil", "href": "#intro", "active": True}],
    },
    "footer": {
        "brand_mode": "neutral",
        "service_name": "Smoke",
        "content_desc": "Footer configuré par le builder.",
        "content_links": [
            {"label": "Documentation", "href": "/documentation"},
        ],
        "bottom_links": [
            {"label": "Plan du site", "href": "/plan"},
            {"label": "Accessibilité", "href": "/accessibilite"},
        ],
    },
    "sections": [
        {"block": "content", "id": "intro", "title": "Smoke builder", "heading_level": 1, "body_structured": {
            "paragraphs": ["Intro structurée <b>échappée</b>."],
            "links": [{"label": "Source structurée", "href": "/structured-source"}],
        }},
        {"block": "breadcrumb", "items": [{"label": "A", "href": "/a"}]},
        {"block": "breadcrumb", "items": [{"label": "B", "href": "/b"}]},
        {"block": "accordion", "id_prefix": "faq", "heading_level": 2, "items": [{
            "title": "Q1",
            "content": {
                "paragraphs": ["Intro <script>alert(1)</script>"],
                "list": ["Point clé", {"label": "Source riche", "href": "/rich-source"}],
            },
        }]},
        {"block": "accordion", "id_prefix": "faq-2", "heading_level": 2, "items": [{"title": "Q2", "content": "R2"}]},
        {"block": "tabs", "id_prefix": 'x" onclick="alert(1)', "tabs": [{
            "label": "A",
            "content": {
                "blocks": [
                    {"type": "paragraph", "text": "Onglet riche"},
                    {"type": "links", "items": [{"label": "Documentation", "href": "/doc", "target": "_blank"}]},
                ],
            },
        }]},
        {"block": "transcription", "content": "t"},
        {"block": "callout", "title": "T", "text": "x", "heading_level": 2},
        {"block": "form", "form_id": "smoke-form", "deferred": True, "fields": [
            {"type": "input", "label": "Objet", "required": True, "id": "objet"},
        ]},
    ],
}


BUILDER_AUTO_H1_CONFIG = {
    "title": "Titre automatique",
    "description": "Smoke du h1 automatique.",
    "sections": [
        {"block": "notice", "title": "Information", "description": "Le h1 doit être ajouté avant cette notice."},
        {"block": "content", "title": "Section éditoriale", "body_text": "Texte <strong>échappé</strong>."},
        {"block": "consent", "site_name": "exemple.gouv.fr"},
    ],
}


BUILDER_HEADER_NO_NAV_CONFIG = {
    "title": "Header sans navigation",
    "header": {
        "brand_mode": "neutral",
        "service_title": "Header sans navigation",
    },
    "sections": [
        {"block": "content", "title": "Header sans navigation", "heading_level": 1, "body_text": "Texte."},
    ],
}


BUILDER_LOCAL_ASSETS_CONFIG = {
    "title": "Assets locaux",
    "assets_prefix": "assets/dsfr",
    "sections": [
        {"block": "content", "title": "Assets locaux", "heading_level": 1, "body_text": "Texte."},
    ],
}


BUILDER_SVG_IMAGE_CONFIG = {
    "title": "Image SVG",
    "sections": [
        {"block": "content", "title": "Image SVG", "heading_level": 1, "body_text": "Texte."},
        {"block": "image", "src": "schema.svg", "alt": "Schéma", "caption": "Schéma non contraint par ratio."},
    ],
}


# Deux barrières en série : le schéma JSON d'abord (safeHref, enums, ratio),
# puis le garde HTML aval. Un cas intercepté par le schéma attend son motif,
# pas celui du garde qu'il n'atteint plus. Le garde aval reste exercé par les
# cas que le schéma laisse passer (ARIA, IDs, HTML brut).
BUILDER_NEGATIVE_CONFIGS = [
    ("builder-negative:tags-vbscript-href", {"title": "T", "sections": [{"block": "tags", "items": [{"label": "x", "href": "vbscript:msgbox(1)"}]}]}, "href"),
    ("builder-negative:quote-cite-unsafe-url", {"title": "T", "sections": [{"block": "quote", "text": "T", "author": "A", "cite": "vbscript:msgbox(1)"}]}, "cite"),
    ("builder-negative:image-without-alt", {"title": "T", "sections": [{"block": "image", "src": "/photo.png", "caption": "Une photo"}]}, "image"),
    ("builder-negative:image-decorative-with-alt", {"title": "T", "sections": [{"block": "image", "src": "/photo.png", "alt": "Une photo", "decorative": True}]}, "decorative"),
    ("builder-negative:image-data-src", {"title": "T", "sections": [{"block": "image", "src": "data:image/gif;base64,R0lGODlhAQABAAAAACw=", "alt": "x"}]}, "src"),
    ("builder-negative:stepper-current-above-total", {"title": "T", "sections": [{"block": "stepper", "current": 9, "total": 3, "title": "Etape"}]}, "current"),
    (
        "builder-negative:spacing-injection",
        {
            "title": "Injection attributaire",
            "sections": [
                {
                    "block": "content",
                    "title": "Titre",
                    "heading_level": 1,
                    "spacing": 'fr-py-6w"><script>alert(1)</script><div class="',
                    "body_text": "Texte.",
                },
            ],
        },
        "Erreur de schéma",
    ),
    (
        "builder-negative:missing-aria-target",
        {
            "title": "ARIA manquante",
            "sections": [
                {
                    "block": "content",
                    "title": "Section",
                    "body": '<button aria-controls="missing-target" type="button">Ouvrir</button>',
                    "allow_raw_html": True,
                },
            ],
        },
        "cible ARIA absente",
    ),
    (
        "builder-negative:buttons-icon-injection",
        {
            "title": "Injection de classe",
            "sections": [
                {"block": "content", "title": "Titre", "heading_level": 1, "body_text": "Texte."},
                {
                    "block": "buttons",
                    "items": [{"label": "Bouton", "icon": 'fr-icon-x"><script>alert(1)</script><span class="x'}],
                },
            ],
        },
        "invalide",
    ),
    (
        "builder-negative:buttons-icon-position-inconnue",
        {
            "title": "Position inconnue",
            "sections": [
                {"block": "content", "title": "Titre", "heading_level": 1, "body_text": "Texte."},
                {
                    "block": "buttons",
                    "items": [{"label": "Bouton", "icon": "fr-icon-check-line", "icon_position": "top"}],
                },
            ],
        },
        "icon_position",
    ),
    ("builder-negative:field-id-explicit-collision", {"title": "T", "sections": [_h1_section(), {"block": "form", "form_id": "f", "fields": [
        {"type": "input", "label": "Nom"}, {"type": "input", "label": "Nom"}, {"type": "input", "label": "Autre", "id": "f-nom-2"}]}]}, "dupliqué"),
    ("builder-negative:two-h1", {"title": "T", "sections": [_h1_section("Un"), _h1_section("Deux")]}, "h1"),
    ("builder-negative:columns-subblock-section-keys", {"title": "T", "sections": [_h1_section(), {"block": "columns", "columns": [[{"block": "callout", "title": "C", "text": "t", "section_id": "x"}]]}]}, "columns"),
    ("builder-negative:section-id-without-container", {"title": "T", "sections": [_h1_section(), {"block": "highlight", "text": "t", "section_id": "repere", "container": False}]}, "container"),
    ("builder-negative:image-data-src", {"title": "T", "sections": [_h1_section(), {"block": "image", "src": "data:image/gif;base64,R0lGODlhAQABAAAAACw=", "alt": "x"}]}, "src"),
    ("builder-negative:columns-too-deep", {"title": "T", "sections": [_h1_section(), _nested_columns(12)]}, "profondeur"),
    (
        "builder-negative:svg-ratio",
        {
            "title": "SVG ratio",
            "sections": [
                {"block": "content", "title": "SVG ratio", "heading_level": 1, "body_text": "Texte."},
                {"block": "image", "src": "schema.svg", "alt": "Schéma", "ratio": "16x9"},
            ],
        },
        "Erreur de schéma",
    ),
]

# Attentes du builder : (scope, config, fragments attendus, fragments interdits, comptages exacts).
BUILDER_EXPECTATIONS: list[tuple[str, dict, list[str], list[str], dict[str, int]]] = [
    ("builder-expect:callout-h1-not-doubled", {"title": "T", "sections": [{"block": "callout", "title": "Unique", "heading_level": 1, "text": "x"}]}, [], [], {"<h1": 1}),
    ("builder-expect:repeated-field-blocks-distinct-ids", {"title": "T", "sections": [_h1_section(), {"block": "form", "fields": [{"type": "field", "name": "email"}, {"type": "field", "name": "email"}]}]}, ['id="dsfr-assembled-form-email"', 'id="dsfr-assembled-form-email-2"'], [], {}),
    ("builder-expect:cards-five-columns-sum-twelve", {"title": "T", "sections": [_h1_section(), {"block": "cards", "heading": "Cartes", "columns": 5, "items": [{"title": f"C{i}", "href": "/"} for i in range(5)]}]}, [], [], {"fr-col-md-3\"": 2, "fr-col-md-2\"": 3}),
    ("builder-expect:header-tool-target", {"title": "T", "header": {"tools": [{"label": "Espace externe", "href": "https://exemple.gouv.fr", "target": "_blank"}]}, "sections": [_h1_section()]}, ['target="_blank"', 'rel="noopener"', 'title="Espace externe - nouvelle fenêtre"'], [], {}),
    ("builder-expect:decorative-image-empty-alt", {"title": "T", "sections": [_h1_section(), {"block": "image", "src": "/photo.png", "alt": "", "decorative": True}]}, ['alt=""'], [], {}),
    ("builder-expect:empty-alt-explicit-accepted", {"title": "T", "sections": [_h1_section(), {"block": "image", "src": "/photo.png", "alt": ""}]}, ['alt=""'], [], {}),
    ("builder-expect:radio-duplicates-deduplicated", {"title": "T", "sections": [_h1_section(), {"block": "form", "fields": [
        {"type": "radio", "legend": "Choix", "items": [{"label": "A", "value": "a"}]},
        {"type": "radio", "legend": "Choix", "items": [{"label": "B", "value": "b"}]}]}]}, [], [], {}),
    ("builder-expect:section-id-case-preserved", {"title": "T", "sections": [_h1_section(), {"block": "summary", "items": [{"label": "Ancre", "href": "#Mon_Ancre"}]},
        {"block": "content", "section_id": "Mon_Ancre", "title": "Cible", "body_text": "a"}]}, ['id="Mon_Ancre"'], [], {}),
    ("builder-expect:header-brand-mode-local", {"title": "T", "brand_mode": "neutral", "header": {"brand_mode": "republique", "service_title": "S"}, "footer": {"service_name": "S"},
        "sections": [_h1_section()]}, ['class="fr-logo"'], [], {'class="fr-logo"': 1}),
    ("builder-expect:share-empty-items", {"title": "T", "sections": [_h1_section(), {"block": "share", "items": []}]}, ["fr-share"], ["fr-share__link"], {}),
    ("builder-expect:follow-default-title", {"title": "T", "sections": [_h1_section(), {"block": "follow", "newsletter_url": "/n"}]}, ["Abonnez-vous à notre lettre d&#x27;information"], ['<h2 class="fr-h5"></h2>'], {}),
    ("builder-expect:download-default-detail", {"title": "T", "sections": [_h1_section(), {"block": "download", "label": "Rapport", "href": "/r.pdf"}]}, [], ['<span class="fr-download__detail">\n                    \n'], {}),
    ("builder-expect:orphan-endtag-still-counts-h1", {"title": "T", "auto_h1": False, "sections": [{"block": "content", "title": "Brut", "allow_raw_html": True, "body": "<p>Texte</p></div></div></div>"}, _h1_section("Titre")]}, [], [], {}),
    ("builder-expect:input-name", {"title": "T", "sections": [_h1_section(), {"block": "form", "fields": [{"type": "input", "label": "Courriel", "name": "email"}]}]}, ['name="email"'], [], {}),
    ("builder-expect:notice-id-with-container", {"title": "T", "sections": [_h1_section(), {"block": "notice", "id": "bandeau2", "container": True, "title": "Autre", "description": "Texte"}]}, ['id="bandeau2"'], [], {'id="bandeau2"': 1}),
    ("builder-expect:accordion-explicit-prefix-collision", {"title": "T", "sections": [_h1_section(), {"block": "accordion", "id_prefix": "accordion-2", "heading_level": 2, "items": [{"title": "A", "content": "a"}]},
        {"block": "accordion", "heading_level": 2, "items": [{"title": "B", "content": "b"}]}, {"block": "accordion", "heading_level": 2, "items": [{"title": "C", "content": "c"}]}]}, [], [], {}),
    ("builder-expect:field-id-explicit-then-auto", {"title": "T", "sections": [_h1_section(), {"block": "form", "form_id": "f", "fields": [
        {"type": "input", "label": "Autre", "id": "f-nom-2"}, {"type": "input", "label": "Nom"}, {"type": "input", "label": "Nom"}]}]}, ['id="f-nom-3"'], [], {'id="f-nom-2"': 1}),
    ("builder-expect:accordion-heading-level", {"title": "T", "sections": [_h1_section(), {"block": "accordion", "heading_level": 2, "items": [{"title": "A", "content": "a"}]}]}, ['<h2 class="fr-accordion__title">'], [], {}),
]
# Source unique : la table BLOCK_BUILDERS du builder (comme PAGE_TYPES).
import generate_assembled_page as gap  # noqa: E402
BUILDER_BLOCK_NAMES = set(gap.BLOCK_BUILDERS)


def iter_builder_page() -> Iterable[tuple[str, str]]:
    """Page assemblée de référence (generate_assembled_page.py).

    Exerce le builder (multi-blocks + header riche + form validation différée),
    en particulier les IDs internes répétés (breadcrumb, accordion) pour garantir
    l'unicité des IDs.
    """
    configs = [
        ("builder:smoke", BUILDER_CONFIG),
        ("builder:auto-h1", BUILDER_AUTO_H1_CONFIG),
        ("builder:header-no-nav", BUILDER_HEADER_NO_NAV_CONFIG),
        ("builder:local-assets", BUILDER_LOCAL_ASSETS_CONFIG),
        ("builder:svg-image", BUILDER_SVG_IMAGE_CONFIG),
    ]
    for scope, config in configs:
        with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False, encoding="utf-8") as tf:
            json.dump(config, tf)
            cfg_path = tf.name
        try:
            html = run_command([sys.executable, str(BUILDER_SCRIPT), "--config-file", cfg_path])
        finally:
            os.unlink(cfg_path)
        yield scope, html


def iter_builder_examples() -> Iterable[tuple[str, Path, str]]:
    if not BUILDER_EXAMPLES_DIR.exists():
        return
    for config_path in sorted(BUILDER_EXAMPLES_DIR.glob("*/page.json")):
        scope = f"builder-example:{config_path.parent.name}"
        html = run_command([sys.executable, str(BUILDER_SCRIPT), "--config-file", str(config_path)])
        yield scope, config_path, html


def run_builder_check(config: dict) -> tuple[int, str]:
    env = os.environ.copy()
    env.setdefault("PYTHONDONTWRITEBYTECODE", "1")
    with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False, encoding="utf-8") as tf:
        json.dump(config, tf)
        cfg_path = tf.name
    try:
        result = subprocess.run(
            [sys.executable, str(BUILDER_SCRIPT), "--config-file", cfg_path, "--check"],
            cwd=WORKSPACE,
            env=env,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )
    finally:
        os.unlink(cfg_path)
    return result.returncode, result.stdout + result.stderr


def _collect_schema_block_consts(node) -> set[str]:
    found: set[str] = set()
    if isinstance(node, dict):
        block = node.get("properties", {}).get("block", {})
        if isinstance(block, dict) and isinstance(block.get("const"), str):
            found.add(block["const"])
        for value in node.values():
            found.update(_collect_schema_block_consts(value))
    elif isinstance(node, list):
        for value in node:
            found.update(_collect_schema_block_consts(value))
    return found


def check_builder_schema() -> list[Issue]:
    if not BUILDER_SCHEMA.exists():
        return [Issue("builder_schema_missing", "builder:schema", str(BUILDER_SCHEMA.relative_to(SKILL_DIR)))]
    try:
        schema = json.loads(BUILDER_SCHEMA.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        return [Issue("builder_schema_invalid_json", "builder:schema", str(e))]

    issues: list[Issue] = []
    sections = schema.get("properties", {}).get("sections", {})
    if not ({"oneOf", "anyOf"} & set(sections.get("items", {}))):
        issues.append(Issue("builder_schema_contract", "builder:schema", "sections.items.anyOf missing"))

    schema_blocks = _collect_schema_block_consts(schema.get("$defs", {}))
    missing = sorted(BUILDER_BLOCK_NAMES - schema_blocks)
    extra = sorted(schema_blocks - BUILDER_BLOCK_NAMES)
    if missing:
        issues.append(Issue("builder_schema_contract", "builder:schema", "missing blocks: " + ", ".join(missing)))
    if extra:
        issues.append(Issue("builder_schema_contract", "builder:schema", "unknown blocks: " + ", ".join(extra)))
    return issues


def check_builder_schema_examples() -> list[Issue]:
    if not SCHEMA_CHECK_SCRIPT.exists():
        return [
            Issue(
                "builder_schema_validation_missing",
                "builder:schema",
                str(SCHEMA_CHECK_SCRIPT.relative_to(SKILL_DIR)),
            )
        ]
    env = os.environ.copy()
    env.setdefault("PYTHONDONTWRITEBYTECODE", "1")
    result = subprocess.run(
        [sys.executable, str(SCHEMA_CHECK_SCRIPT)],
        cwd=WORKSPACE,
        env=env,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    if result.returncode == 0:
        return []
    detail = (result.stdout + result.stderr).strip().replace("\n", " ")[:400]
    return [Issue("builder_schema_validation", "builder:schema", detail)]


def check_builder_example_files(scope: str, config_path: Path, html: str) -> list[Issue]:
    example_dir = config_path.parent
    issues: list[Issue] = []
    required = ["brief.md", "page.json", "page.html", "preuve.md"]
    for name in required:
        if not (example_dir / name).is_file():
            issues.append(Issue("builder_example_missing_file", scope, name))

    html_path = example_dir / "page.html"
    if html_path.is_file():
        committed_html = html_path.read_text(encoding="utf-8")
        if committed_html != html:
            issues.append(Issue("builder_example_drift", scope, "page.html differs from generated output"))
    return issues


def iter_representative(script: Path, items: list[tuple[str, str]], prefix: str) -> Iterable[tuple[str, str]]:
    for name, config in items:
        html = run_command([sys.executable, str(script), name, "--config", config])
        yield f"{prefix}:{name}", html


def iter_representative_components() -> Iterable[tuple[str, str, str, str]]:
    for component, variant, config in REPRESENTATIVE_COMPONENT_CONFIGS:
        html = run_command([sys.executable, str(COMPONENT_SCRIPT), component, "--config", config])
        yield component, variant, f"native-config:{component}.{variant}", html


def check_duplicate_ids(scope: str, html: str) -> list[Issue]:
    """Détecte les IDs dupliqués (cassage ARIA silencieux), sur les attributs réels."""
    facts = parse_markup(html)
    dups = sorted(k for k, v in facts.id_counts.items() if v > 1)
    if dups:
        return [Issue("duplicate_id", scope, ", ".join(dups[:10]))]
    return []


def check_no_inline_event_handlers(scope: str, html: str) -> list[Issue]:
    facts = parse_markup(html)
    if facts.inline_handlers:
        return [Issue("inline_event_handler", scope, ", ".join(facts.inline_handlers[:8]))]
    return []


def check_builder_contract(scope: str, html: str) -> list[Issue]:
    missing: list[str] = []
    if scope == "builder:smoke":
        if "<h1>Smoke builder</h1>" not in html:
            missing.append("content.heading_level=1 did not emit h1")
        if '<meta name="description" content="Description meta du smoke builder.">' not in html:
            missing.append("meta description missing")
        if 'id="intro"' not in html:
            missing.append("section id missing")
        if "Footer configuré par le builder." not in html:
            missing.append("footer config missing")
        if "service-public.gouv.fr" in html or "legifrance.gouv.fr" in html or "gouvernement.fr" in html:
            missing.append("footer content_links did not replace default institutional links")
        if '<a class="fr-footer__content-link" href="/documentation">Documentation</a>' not in html:
            missing.append("footer content_links custom link missing")
        if "Intro structurée &lt;b&gt;échappée&lt;/b&gt;." not in html:
            missing.append("body_structured paragraph did not escape HTML")
        if '<a href="/structured-source">Source structurée</a>' not in html:
            missing.append("body_structured link missing")
        if '<a href="/rich-source">Source riche</a>' not in html:
            missing.append("accordion rich link missing")
        if "<li>Point clé</li>" not in html:
            missing.append("accordion rich list missing")
        if "&lt;script&gt;alert(1)&lt;/script&gt;" not in html:
            missing.append("rich paragraph did not escape script tag")
        if '<a href="/doc" title="Documentation - nouvelle fenêtre" target="_blank" rel="noopener">Documentation</a>' not in html:
            missing.append("tabs rich external link missing noopener")
    if scope == "builder:auto-h1":
        if "<h1>Titre automatique</h1>" not in html:
            missing.append("auto_h1 did not emit page h1")
        if '<meta name="description" content="Smoke du h1 automatique.">' not in html:
            missing.append("auto_h1 meta description missing")
        if "Texte &lt;strong&gt;échappé&lt;/strong&gt;." not in html:
            missing.append("body_text did not escape HTML")
    if scope == "builder:header-no-nav":
        if '<a class="fr-link" href="#navigation">Menu</a>' in html:
            missing.append("skiplink to missing navigation was not removed")
        if "<h1>Header sans navigation</h1>" not in html:
            missing.append("header without navigation missing h1")
    if scope == "builder:local-assets":
        if "cdn.jsdelivr.net" in html:
            missing.append("local assets config still emits CDN")
        if 'href="assets/dsfr/dsfr.min.css"' not in html:
            missing.append("local assets css path missing")
        if 'src="assets/dsfr/dsfr.module.min.js"' not in html:
            missing.append("local assets module js path missing")
    if scope == "builder:svg-image":
        if 'src="schema.svg"' not in html:
            missing.append("svg image src missing")
        if "fr-ratio-" in html:
            missing.append("svg image should not emit fr-ratio-*")
    return [Issue("builder_contract", scope, ", ".join(missing))] if missing else []


def run_script_check(script: Path, argv: list[str], extra_env: dict[str, str] | None = None) -> tuple[int, str]:
    env = os.environ.copy()
    env.setdefault("PYTHONDONTWRITEBYTECODE", "1")
    if extra_env:
        env.update(extra_env)
    result = subprocess.run(
        [sys.executable, str(script), *argv],
        cwd=WORKSPACE,
        env=env,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    return result.returncode, result.stdout + result.stderr


def _check_negative_cases(kind: str, cases: Iterable[tuple[str, Path, list[str], str]]) -> list[Issue]:
    issues: list[Issue] = []
    for scope, script, argv, expected_error in cases:
        returncode, output = run_script_check(script, argv)
        if returncode == 0:
            issues.append(Issue(f"{kind}_negative_case_passed", scope, "expected generation failure"))
        elif "Traceback" in output:
            detail = output.strip().replace("\n", " ")[-160:]
            issues.append(Issue(f"{kind}_negative_case_traceback", scope, f"raw Python traceback: {detail!r}"))
        elif expected_error not in output:
            detail = output.strip().replace("\n", " ")[:160]
            issues.append(
                Issue(f"{kind}_negative_case_wrong_error", scope, f"expected {expected_error!r}, got {detail!r}")
            )
    return issues


def check_atom_negative_cases() -> list[Issue]:
    return _check_negative_cases(
        "atom",
        ((scope, ATOM_SCRIPT, [atom, "--config", config], err) for scope, atom, config, err in ATOM_NEGATIVE_CONFIGS),
    )


def check_layout_negative_cases() -> list[Issue]:
    return _check_negative_cases(
        "layout",
        ((scope, LAYOUT_SCRIPT, [layout, "--config", config], err) for scope, layout, config, err in LAYOUT_NEGATIVE_CONFIGS),
    )


def check_component_negative_cases() -> list[Issue]:
    return _check_negative_cases(
        "component",
        ((scope, COMPONENT_SCRIPT, argv, err) for scope, argv, err in COMPONENT_NEGATIVE_ARGS),
    )


def check_component_expectations() -> list[Issue]:
    issues: list[Issue] = []
    for scope, argv, expected in COMPONENT_EXPECTATIONS:
        returncode, output = run_script_check(COMPONENT_SCRIPT, argv)
        if returncode != 0:
            detail = output.strip().replace("\n", " ")[:160]
            issues.append(Issue("component_expectation_failed", scope, f"exit {returncode}: {detail}"))
            continue
        for fragment in expected:
            if fragment not in output:
                issues.append(Issue("component_expectation_missing", scope, fragment))
    return issues


LIBRARY_ENTRY_KEYS = frozenset({"count", "variants", "html"})


def check_library_shape() -> list[Issue]:
    """Chaque entrée de la bibliothèque a exactement {count, variants, html},
    count == len(variants) et les variantes déclarées sont toutes rendues."""
    issues: list[Issue] = []
    try:
        library = json.loads((SKILL_DIR / "assets" / "dsfr_complete_library.json").read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        return [Issue("library_unreadable", "library:shape", str(exc)[:160])]
    for name, entry in library.get("components", {}).items():
        scope = f"library:{name}"
        keys = set(entry) if isinstance(entry, dict) else set()
        if keys != LIBRARY_ENTRY_KEYS:
            issues.append(Issue("library_entry_keys", scope, f"clés {sorted(keys)} attendues {sorted(LIBRARY_ENTRY_KEYS)}"))
            continue
        variants = entry["variants"]
        if entry["count"] != len(variants) or set(variants) != set(entry["html"]) or not variants:
            issues.append(Issue("library_entry_inconsistent", scope, f"count={entry['count']} variants={len(variants)} html={len(entry['html'])}"))
    return issues


def check_library_loading_errors() -> list[Issue]:
    """Bibliothèque JSON corrompue : erreur courte ; absente : mode natif préservé ;
    entrée sans variante : erreur courte ; variante déclarée non rendue : repli."""
    issues: list[Issue] = []
    scripts_dir = str(SKILL_DIR / "scripts")
    with tempfile.TemporaryDirectory() as tmp:
        corrupt = Path(tmp) / "corrompu.json"
        corrupt.write_text('{ "components": ', encoding="utf-8")
        absent = Path(tmp) / "absent.json"
        for scope, entry, expect_exit, expect_text in (
            ("library:empty-entry", '{"count": 0, "variants": [], "html": {}}', 1, "aucune variante"),
            ("library:variant-not-rendered", '{"count": 1, "variants": ["x"], "html": {"basic": "<p>ok</p>"}}', 0, "<p>ok</p>"),
        ):
            code = (
                "import sys, json; sys.dont_write_bytecode = True; "
                f"sys.path.insert(0, {scripts_dir!r}); import generate_component as gc; "
                f"print(gc.generate_from_library({{'components': {{'x': json.loads({entry!r})}}}}, 'x'))"
            )
            result = subprocess.run(
                [sys.executable, "-c", code], cwd=WORKSPACE, text=True,
                stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False,
            )
            output = result.stdout + result.stderr
            if result.returncode != expect_exit or "Traceback" in output or expect_text not in output:
                issues.append(Issue("library_entry_not_guarded", scope, output.strip().replace("\n", " ")[:160]))
        for scope, target, expect_failure in (
            ("library:corrupt", corrupt, True),
            ("library:absent", absent, False),
        ):
            code = (
                "import sys; sys.dont_write_bytecode = True; "
                f"sys.path.insert(0, {scripts_dir!r}); import generate_component as gc; "
                f"gc.LIBRARY_PATH = {str(target)!r}; print(sorted(gc.load_library()))"
            )
            result = subprocess.run(
                [sys.executable, "-c", code], cwd=WORKSPACE, text=True,
                stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False,
            )
            output = result.stdout + result.stderr
            if expect_failure:
                if result.returncode == 0 or "Traceback" in output or "bibliothèque" not in output:
                    issues.append(Issue("library_corrupt_not_reported", scope, output.strip().replace("\n", " ")[:160]))
            elif result.returncode != 0 or "[]" not in result.stdout:
                issues.append(Issue("library_absent_breaks_native_mode", scope, output.strip().replace("\n", " ")[:160]))
    # Composant servi par la bibliothèque : --config est signalé sans effet.
    result = subprocess.run(
        [sys.executable, "-B", str(COMPONENT_SCRIPT), "back_to_top", "--config", '{"label":"Remonter"}'],
        cwd=WORKSPACE, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False,
    )
    if result.returncode != 0 or "sans effet" not in result.stderr or "fr-link" not in result.stdout:
        issues.append(Issue("library_config_not_warned", "library:config-ignored", (result.stderr or result.stdout).strip()[:160]))
    return issues


def check_page_negative_cases() -> list[Issue]:
    return _check_negative_cases(
        "page",
        ((scope, PAGE_SCRIPT, argv, err) for scope, argv, err in PAGE_NEGATIVE_ARGS),
    )


def _check_expectations(kind: str, script: Path, cases) -> list[Issue]:
    issues: list[Issue] = []
    for scope, argv, extra_env, expected, forbidden in cases:
        returncode, output = run_script_check(script, argv, extra_env)
        if returncode != 0:
            detail = output.strip().replace("\n", " ")[:160]
            issues.append(Issue(f"{kind}_expectation_failed", scope, f"exit {returncode}: {detail}"))
            continue
        for fragment in expected:
            if fragment not in output:
                issues.append(Issue(f"{kind}_expectation_missing", scope, fragment))
        for fragment in forbidden:
            if fragment in output:
                issues.append(Issue(f"{kind}_expectation_forbidden", scope, fragment))
    return issues


def check_tool_cases() -> list[Issue]:
    """Blocs fonctionnels, inventaire officiel et icônes : gardes d'entrée et sorties propres."""
    issues: list[Issue] = []
    issues.extend(_check_negative_cases("field", ((scope, FIELD_SCRIPT, argv, err) for scope, argv, err in FIELD_NEGATIVE_ARGS)))
    issues.extend(_check_expectations("field", FIELD_SCRIPT, FIELD_EXPECTATIONS))
    for scope, script, argv, extra_env, expected in TOOL_NEGATIVE_CASES:
        returncode, output = run_script_check(script, argv, extra_env)
        if returncode == 0:
            issues.append(Issue("tool_negative_case_passed", scope, "expected refusal"))
        elif "Traceback" in output or expected not in output:
            issues.append(Issue("tool_negative_case_wrong_error", scope, output.strip().replace("\n", " ")[-160:]))
    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        no_manifest = tmp_path / "sans-package-json" / "dist"; no_manifest.mkdir(parents=True)
        no_dist = tmp_path / "sans-dist"; no_dist.mkdir(); (no_dist / "package.json").write_text('{"name": "@gouvfr/dsfr", "version": "9.9.9"}', encoding="utf-8")
        no_version = tmp_path / "sans-version"; (no_version / "dist" / "component").mkdir(parents=True); (no_version / "package.json").write_text('{"name": "@gouvfr/dsfr"}', encoding="utf-8")
        for scope, package, expected in (
            ("inventory-negative:package-without-manifest", no_manifest.parent, "package.json"),
            ("inventory-negative:package-without-dist", no_dist, "dist"),
            ("inventory-negative:package-without-version", no_version, "version"),
        ):
            returncode, output = run_script_check(INVENTORY_SCRIPT, ["--official-package", str(package)])
            if returncode == 0:
                issues.append(Issue("tool_negative_case_passed", scope, "expected refusal"))
            elif "Traceback" in output or expected not in output:
                issues.append(Issue("tool_negative_case_wrong_error", scope, output.strip().replace("\n", " ")[-160:]))
    official = DEFAULT_OFFICIAL_CACHE_DIR / "gouvfr-dsfr-1.15.2" / "package"
    if official_package_complete(official):
        # Sortie JSON de l'inventaire pure (aucun message parasite sur stdout).
        result = subprocess.run([sys.executable, str(INVENTORY_SCRIPT), "--official-package", str(official), "--format", "json"], cwd=WORKSPACE, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False)
        try:
            json.loads(result.stdout)
        except json.JSONDecodeError:
            issues.append(Issue("tool_expectation_missing", "inventory-expect:json-stdout-pure", result.stdout.strip().replace("\n", " ")[:120]))
        # Tilde développé et version affichée = celle du paquet lu.
        home_relative = "~/" + str(official.relative_to(Path.home())) if str(official).startswith(str(Path.home())) else str(official)
        returncode, output = run_script_check(ICONS_SCRIPT, [], {"DSFR_OFFICIAL_PACKAGE_DIR": home_relative})
        if returncode != 0:
            issues.append(Issue("tool_expectation_failed", "icons-expect:tilde-package-dir", output.strip().replace("\n", " ")[-160:]))
        older = DEFAULT_OFFICIAL_CACHE_DIR / "gouvfr-dsfr-1.14.4" / "package"
        if official_package_complete(older):
            returncode, output = run_script_check(ICONS_SCRIPT, [], {"DSFR_OFFICIAL_PACKAGE_DIR": str(older)})
            if returncode != 0 or "1.14.4" not in output or "1.15.2" in output:
                issues.append(Issue("tool_expectation_missing", "icons-expect:version-of-package-read", output.strip().replace("\n", " ")[:160]))
    return issues


def check_option_cases() -> list[Issue]:
    issues: list[Issue] = []
    for scope, script, argv, extra_env, expected in ENV_NEGATIVE_CASES:
        returncode, output = run_script_check(script, argv, extra_env)
        if returncode == 0:
            issues.append(Issue("env_negative_case_passed", scope, "expected refusal"))
        elif "Traceback" in output or expected not in output:
            issues.append(Issue("env_negative_case_wrong_error", scope, output.strip().replace("\n", " ")[-160:]))
    issues.extend(_check_negative_cases("atom", ((scope, ATOM_SCRIPT, argv, err) for scope, argv, err in ATOM_NEGATIVE_ARGS)))
    issues.extend(_check_negative_cases("layout", ((scope, LAYOUT_SCRIPT, argv, err) for scope, argv, err in LAYOUT_NEGATIVE_ARGS)))
    issues.extend(_check_expectations("atom", ATOM_SCRIPT, ATOM_EXPECTATIONS))
    issues.extend(_check_expectations("layout", LAYOUT_SCRIPT, LAYOUT_EXPECTATIONS))
    issues.extend(_check_expectations("page", PAGE_SCRIPT, PAGE_EXPECTATIONS))
    return issues


def check_layout_skeleton() -> list[Issue]:
    """La charpente porte la structure officielle de l'en-tête et des ancres résolues."""
    issues: list[Issue] = []
    for brand in ("neutral", "republique"):
        scope = f"layout:skeleton.{brand}"
        html = run_command([sys.executable, str(LAYOUT_SCRIPT), "skeleton", "--config", json.dumps({"brand_mode": brand})])
        facts = parse_markup(html)
        issues.extend(check_header_contract(scope, brand, facts))
        issues.extend(check_anchor_targets(scope, facts))
        issues.extend(check_heading_hierarchy(scope, facts, require_h1_first=False))
    return issues


def check_validator_self_guards() -> list[Issue]:
    """Le validateur se contrôle lui-même : gardes qui doivent tenir sur des entrées hostiles."""
    issues: list[Issue] = []
    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        # 1. Archive avec lien symbolique sortant : refusée avant extraction.
        archive_path = tmp_path / "piege.tgz"
        with tarfile.open(archive_path, "w:gz") as archive:
            info = tarfile.TarInfo("package/evil-link"); info.type = tarfile.SYMTYPE; info.linkname = "/etc/passwd"
            archive.addfile(info)
        target = tmp_path / "extract"; target.mkdir()
        try:
            with tarfile.open(archive_path, "r:gz") as archive:
                safe_extract_tar(archive, target)
            issues.append(Issue("self_guard", "validator:tar-symlink", "symlink member extracted without error"))
        except SystemExit:
            pass
        if (target / "package" / "evil-link").is_symlink():
            issues.append(Issue("self_guard", "validator:tar-symlink", "symlink created under the cache"))
        # 2. Version de cache piégée : refusée avant tout accès disque.
        victim = tmp_path / "victime"; victim.mkdir(); (victim / "precieux.txt").write_text("x", encoding="utf-8")
        try:
            resolve_official_package("1.15.2/../../victime", tmp_path / "cache")
            issues.append(Issue("self_guard", "validator:version-traversal", "unsafe version accepted"))
        except SystemExit:
            pass
        if not (victim / "precieux.txt").exists():
            issues.append(Issue("self_guard", "validator:version-traversal", "victim directory was deleted"))
        # 3. Cache tronqué : refusé avec un message, jamais accepté.
        truncated = tmp_path / "cache-tronque" / "gouvfr-dsfr-1.15.2" / "package" / "dist" / "component" / "button"
        truncated.mkdir(parents=True)
        try:
            if resolve_official_package("1.15.2", tmp_path / "cache-tronque") is not None:
                issues.append(Issue("self_guard", "validator:truncated-cache", "truncated cache accepted as official package"))
        except SystemExit:
            pass
        # 4. Catalogue sur un paquet sans dist/component : issue, pas exception.
        try:
            if not check_official_catalog(tmp_path / "absent"):
                issues.append(Issue("self_guard", "validator:catalog-missing-dist", "no issue reported"))
        except Exception as exc:  # noqa: BLE001
            issues.append(Issue("self_guard", "validator:catalog-missing-dist", f"raised {type(exc).__name__}"))
    # 5. Contrat de modale sans dialog mais avec un bouton : issue, pas IndexError.
    try:
        result = check_modal_contract("validator:modal-no-dialog", "basic", parse_markup('<button class="fr-btn" type="button">Ouvrir</button>'))
        if not result:
            issues.append(Issue("self_guard", "validator:modal-no-dialog", "no issue reported"))
    except Exception as exc:  # noqa: BLE001
        issues.append(Issue("self_guard", "validator:modal-no-dialog", f"raised {type(exc).__name__}"))
    # 6. Attribut dupliqué : la première occurrence compte, comme dans le navigateur.
    facts = parse_markup('<div id="present"></div><button type="button" aria-controls="absent" aria-controls="present">x</button>')
    if ("aria-controls", "absent") not in facts.aria_refs:
        issues.append(Issue("self_guard", "validator:duplicate-attribute", "last attribute value wins instead of the first"))
    # 7. Ids dupliqués détectés sur les attributs réels seulement.
    if check_duplicate_ids("validator:ids", '<div data-id="x"></div><!-- id="x" --><p id="x"></p><span id=\'y\'></span><span id="y"></span>') != [Issue("duplicate_id", "validator:ids", "y")]:
        issues.append(Issue("self_guard", "validator:duplicate-ids", "text-based detection differs from the parser"))
    # 8. Bibliothèque avec une entrée non-objet : message court, pas de trace.
    with tempfile.TemporaryDirectory() as tmp:
        bad = Path(tmp) / "lib.json"; bad.write_text('{"components": {"button": "pas un objet"}}', encoding="utf-8")
        code = (f"import sys; sys.dont_write_bytecode = True; sys.path.insert(0, {str(SKILL_DIR / 'scripts')!r}); "
                f"import check_generated_outputs as c; c.LIBRARY_PATH = __import__('pathlib').Path({str(bad)!r}); c.load_component_variants()")
        result = subprocess.run([sys.executable, "-c", code], cwd=WORKSPACE, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False)
        if result.returncode == 0 or "Traceback" in result.stderr:
            issues.append(Issue("self_guard", "validator:library-entry-not-object", (result.stdout + result.stderr).strip().replace("\n", " ")[-160:]))
    return issues


def check_offline_empty_cache_fails() -> list[Issue]:
    """Hors ligne avec un cache vide, la comparaison officielle demandée est sautée
    explicitement (SKIP sur stderr, résumé marqué SKIPPED, exit 0, cache intact)."""
    with tempfile.TemporaryDirectory() as tmp:
        env = dict(os.environ, DSFR_OFFICIAL_CACHE_OFFLINE="1", PYTHONDONTWRITEBYTECODE="1", DSFR_SELF_CHECK_NESTED="1")
        result = subprocess.run(
            [sys.executable, str(Path(__file__).resolve()), "--pages-only", "--official-version", "9.9.9", "--official-cache-dir", tmp],
            cwd=WORKSPACE, env=env, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False,
        )
        cache_touched = any(Path(tmp).iterdir())
    # Contrat consommateur : SKIP explicite, exit 0, cache intact ; jamais un PASS silencieux.
    silent = "SKIP official package" not in result.stderr or "official comparison SKIPPED" not in result.stdout
    if result.returncode != 0 or silent or cache_touched:
        return [Issue("self_guard", "validator:offline-empty-cache", f"offline with empty cache must SKIP explicitly with exit 0 and an untouched cache (exit {result.returncode}, silent={silent}, cache_touched={cache_touched})")]
    return []


TARGET_DSFR_VERSION = generate_page.DSFR_VERSION


def check_template_base() -> tuple[set[str], list[Issue]]:
    """Le template de repli respecte les mêmes invariants qu'une page générée."""
    scope = "template:base"
    html = TEMPLATE_BASE.read_text(encoding="utf-8")
    facts = parse_markup(html)
    issues = check_common(scope, html)
    issues.extend(check_heading_hierarchy(scope, facts))
    issues.extend(check_anchor_targets(scope, facts))
    # Une seule version DSFR dans le gabarit, celle du skill (generate_page.DSFR_VERSION).
    versions = sorted(set(re.findall(r"@gouvfr/dsfr@([0-9][^/\"']*)", html)))
    if versions != [TARGET_DSFR_VERSION]:
        issues.append(Issue("template_version_mismatch", scope, f"versions {versions} attendue {TARGET_DSFR_VERSION}"))
    # use-credentials sur une origine tierce impose une réponse CORS avec identifiants.
    for element in facts.elements:
        if element.tag == "link" and element.attrs.get("crossorigin") == "use-credentials" and element.attrs.get("href", "").startswith(("http://", "https://", "//")):
            issues.append(Issue("template_manifest_credentials", scope, element.attrs.get("href", "")[:80]))
    return set(facts.classes), issues


def check_page_skiplinks_follow_markup() -> list[Issue]:
    """Un en-tête ou un pied de page fourni sans ses ancres n'obtient aucun lien
    d'évitement orphelin (generate_html_page, chemin du builder assemblé)."""
    html = generate_page.generate_html_page(title="T", header_html="", footer_html="")
    orphans = [anchor for anchor in ("#navigation", "#footer") if f'href="{anchor}"' in html]
    if orphans:
        return [Issue("orphan_skiplink", "page:custom-header-footer", ", ".join(orphans))]
    if 'href="#contenu"' not in html:
        return [Issue("missing_skiplink", "page:custom-header-footer", "#contenu")]
    return []


def check_builder_expectations() -> list[Issue]:
    issues: list[Issue] = []
    for scope, config, expected, forbidden, counts in BUILDER_EXPECTATIONS:
        returncode, output = run_builder_check(config)
        if returncode != 0:
            issues.append(Issue("builder_expectation_failed", scope, f"exit {returncode}: {output.strip()[:160]}"))
            continue
        with tempfile.TemporaryDirectory() as tmp:
            config_path = Path(tmp) / "page.json"
            config_path.write_text(json.dumps(config, ensure_ascii=False), encoding="utf-8")
            html = run_command([sys.executable, str(BUILDER_SCRIPT), "--config-file", str(config_path)])
        for fragment in expected:
            if fragment not in html:
                issues.append(Issue("builder_expectation_missing", scope, fragment))
        for fragment in forbidden:
            if fragment in html:
                issues.append(Issue("builder_expectation_forbidden", scope, fragment))
        for fragment, count in counts.items():
            if html.count(fragment) != count:
                issues.append(Issue("builder_expectation_count", scope, f"{fragment} x{html.count(fragment)} (expected {count})"))
        # Le cas de la balise orpheline place sciemment le h1 après une section
        # h2 : c'est la position du h1 qui exerce le parseur, pas la hiérarchie.
        if scope != "builder-expect:orphan-endtag-still-counts-h1":
            issues.extend(check_heading_hierarchy(scope, parse_markup(html)))
    return issues


def check_builder_argument_cases() -> list[Issue]:
    """Arguments du builder et du contrôle de schéma : erreurs courtes, chemins relatifs, cas invalides."""
    issues: list[Issue] = []
    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        config_path = tmp_path / "page.json"
        config_path.write_text(json.dumps({"title": "T", "sections": [_h1_section()]}, ensure_ascii=False), encoding="utf-8")
        issues.extend(_check_negative_cases("builder", [
            ("builder-negative-args:check-with-output", BUILDER_SCRIPT, ["--config-file", str(config_path), "--check", "--output", str(tmp_path / "out.html")], "--check"),
            ("builder-negative-args:empty-output", BUILDER_SCRIPT, ["--config-file", str(config_path), "--output", ""], "--output"),
            ("builder-negative-args:config-is-directory", BUILDER_SCRIPT, ["--config-file", str(BUILDER_EXAMPLES_DIR)], "Erreur"),
            ("builder-negative-args:output-not-a-directory", BUILDER_SCRIPT, ["--config-file", str(config_path), "--output", "/dev/null/x"], "Erreur"),
            ("schemacheck-negative:schema-is-directory", SCHEMA_CHECK_SCRIPT, ["--schema", str(BUILDER_EXAMPLES_DIR), "--schema-only"], "[FAIL]"),
        ]))
        empty_dir = tmp_path / "vide"; empty_dir.mkdir()
        issues.extend(_check_negative_cases("schemacheck", [
            ("schemacheck-negative:fixtures-dir-empty", SCHEMA_CHECK_SCRIPT, ["--fixture-examples-dir", str(empty_dir), "--schema-only"], "fixture"),
        ]))
        invalid_dir = tmp_path / "invalides" / "href-javascript"; invalid_dir.mkdir(parents=True)
        (invalid_dir / "page.json").write_text(json.dumps({"title": "T", "sections": [_h1_section(), {"block": "tags", "items": [{"label": "X", "href": "javascript:alert(1)"}]}]}), encoding="utf-8")
        for scope, argv, cwd, expected, forbidden in (
            ("schemacheck-expect:relative-examples-dir-from-skill", ["--examples-dir", "examples/assembled"], SKILL_DIR, "PASS builder", ""),
            ("schemacheck-expect:invalid-example-other-guidance", ["--invalid-examples-dir", str(tmp_path / "invalides")], WORKSPACE, "PASS builder-rejects", ""),
            ("schemacheck-expect:schema-only-declares-skipped", ["--schema-only"], WORKSPACE, "non exécutés", ""),
        ):
            result = subprocess.run([sys.executable, str(SCHEMA_CHECK_SCRIPT), *argv], cwd=cwd, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False)
            output = result.stdout + result.stderr
            if result.returncode != 0:
                issues.append(Issue("schemacheck_expectation_failed", scope, f"exit {result.returncode}: {output.strip().replace(chr(10), ' ')[-160:]}"))
            elif expected and expected not in output:
                issues.append(Issue("schemacheck_expectation_missing", scope, expected))
            elif forbidden and forbidden in output:
                issues.append(Issue("schemacheck_expectation_forbidden", scope, forbidden))
    return issues


def check_builder_negative_cases() -> list[Issue]:
    issues: list[Issue] = []
    for scope, config, expected_error in BUILDER_NEGATIVE_CONFIGS:
        returncode, output = run_builder_check(config)
        if returncode == 0:
            issues.append(Issue("builder_negative_case_passed", scope, "expected --check failure"))
        elif expected_error not in output:
            detail = output.strip().replace("\n", " ")[:160]
            issues.append(
                Issue("builder_negative_case_wrong_error", scope, f"expected {expected_error!r}, got {detail!r}")
            )
    return issues


# Variante que reproduit la sortie native par défaut de chaque composant : les
# contrats conditionnés au nom de variante s'appliquent ainsi aux natifs.
NATIVE_VARIANT_LABELS = {"header": "neutral", "footer": "neutral"}


def collect_extra_classes() -> tuple[set[str], list[Issue]]:
    """Classes (et invariants communs) des sorties natives + atomes + gabarits.

    Ces sorties ne sont pas couvertes par check_pages/check_components (qui
    n'exercent que les pages et les variantes JSON). On les collecte pour que
    check_official_classes valide aussi leurs classes contre le paquet ciblé.
    """
    classes: set[str] = set()
    issues: list[Issue] = []
    extras = chain(
        iter_native_component_defaults(),
        iter_fields(),
        iter_representative(ATOM_SCRIPT, REPRESENTATIVE_ATOM_CONFIGS, "atom"),
        iter_representative(LAYOUT_SCRIPT, REPRESENTATIVE_LAYOUT_CONFIGS, "layout"),
    )
    for scope, html in extras:
        facts = parse_markup(html)
        classes.update(facts.classes)
        classes.update(CSS_VAR_USE_RE.findall(html))
        issues.extend(check_common(scope, html))
        if scope.startswith("native:"):
            # Les défauts natifs passent aussi par les contrats de structure
            # (range, translate…) : une classe présente ne prouve pas l'élément.
            native_name = scope.split(":", 1)[1]
            issues.extend(check_component_structure(native_name, NATIVE_VARIANT_LABELS.get(native_name, "basic"), scope, facts))
    for component, variant, scope, html in iter_representative_components():
        facts = parse_markup(html)
        classes.update(facts.classes)
        classes.update(CSS_VAR_USE_RE.findall(html))
        issues.extend(check_common(scope, html))
        issues.extend(check_component_structure(component, variant, scope, facts))
    for scope, html in iter_builder_page():
        facts = parse_markup(html)
        classes.update(facts.classes)
        classes.update(CSS_VAR_USE_RE.findall(html))
        issues.extend(check_common(scope, html))
        issues.extend(check_duplicate_ids(scope, html))
        issues.extend(check_no_inline_event_handlers(scope, html))
        issues.extend(check_builder_contract(scope, html))
        issues.extend(check_heading_hierarchy(scope, facts))
        issues.extend(check_anchor_targets(scope, facts))
    for scope, config_path, html in iter_builder_examples():
        facts = parse_markup(html)
        classes.update(facts.classes)
        classes.update(CSS_VAR_USE_RE.findall(html))
        issues.extend(check_common(scope, html))
        issues.extend(check_duplicate_ids(scope, html))
        issues.extend(check_no_inline_event_handlers(scope, html))
        issues.extend(check_builder_example_files(scope, config_path, html))
        issues.extend(check_heading_hierarchy(scope, facts))
    issues.extend(check_builder_schema())
    issues.extend(check_builder_schema_examples())
    issues.extend(check_builder_negative_cases())
    issues.extend(check_builder_expectations())
    issues.extend(check_builder_argument_cases())
    issues.extend(check_atom_negative_cases())
    issues.extend(check_layout_negative_cases())
    issues.extend(check_page_negative_cases())
    issues.extend(check_page_skiplinks_follow_markup())
    issues.extend(check_component_negative_cases())
    issues.extend(check_component_expectations())
    issues.extend(check_library_loading_errors())
    issues.extend(check_library_shape())
    issues.extend(check_option_cases())
    issues.extend(check_tool_cases())
    issues.extend(check_layout_skeleton())
    issues.extend(check_validator_self_guards())
    if os.environ.get("DSFR_SELF_CHECK_NESTED") != "1":
        issues.extend(check_offline_empty_cache_fails())
    template_classes, template_issues = check_template_base()
    classes.update(template_classes)
    issues.extend(template_issues)
    return classes, issues


def check_common(scope: str, html: str, allow_error_state: bool = False) -> list[Issue]:
    facts = parse_markup(html)
    issues: list[Issue] = []

    if "#" in facts.hrefs:
        issues.append(Issue("placeholder_href", scope, 'generated output contains href="#"'))

    missing_refs = [
        f"{attr}={target}" for attr, target in facts.aria_refs if target not in facts.ids
    ]
    if missing_refs:
        issues.append(Issue("missing_aria_target", scope, ", ".join(missing_refs[:8])))

    issues.extend(check_unsafe_url_schemes(scope, facts))
    if facts.inline_handlers:
        issues.append(Issue("inline_event_handler", scope, ", ".join(facts.inline_handlers[:8])))
    if facts.stack:
        issues.append(Issue("unbalanced_markup", scope, "non fermés : " + ", ".join(facts.elements[i].tag for i in facts.stack[:6])))
    dups = sorted(k for k, v in facts.id_counts.items() if v > 1)
    if dups:
        issues.append(Issue("duplicate_id", scope, ", ".join(dups[:10])))
    issues.extend(check_button_types(scope, facts))
    issues.extend(check_external_links(scope, facts))
    issues.extend(check_modal_title_level(scope, facts))
    issues.extend(check_table_structure(scope, facts))
    issues.extend(check_table_header_scope(scope, facts))
    issues.extend(check_form_control_names(scope, facts))
    issues.extend(check_native_constraints(scope, facts))
    issues.extend(check_unescaped_ampersand(scope, html))
    issues.extend(check_select_placeholder_values(scope, facts))
    issues.extend(check_range_double_names(scope, facts))
    # Un sommaire (summary) référence par nature des sections hors du fragment.
    if scope.split(":", 1)[-1].split(".")[0] != "summary":
        issues.extend(check_anchor_targets(scope, facts, tolerated=PAGE_ANCHOR_IDS))

    constraints = []
    for item in facts.form_constraints:
        if allow_error_state and item.endswith(":aria-invalid"):
            continue
        constraints.append(item)
    if constraints:
        issues.append(Issue("resting_form_constraint", scope, ", ".join(constraints[:8])))

    if STALE_FOOTER_RE.search(html):
        issues.append(Issue("stale_footer_link", scope, "service-public.fr still present"))

    issues.extend(check_select_options_contract(scope, facts))
    # Contrat officiel 1.15.2 (search/_part/doc/code/index.md) : la barre de
    # recherche vit dans un <form>, pour fonctionner sans JavaScript.
    issues.extend(check_search_bar_contract(scope, facts, require_form=True))

    return issues


def check_pages() -> tuple[list[Issue], set[str]]:
    issues: list[Issue] = []
    classes: set[str] = set()
    default_expect: dict[str, object] = {"header": True, "footer": True, "brand": "neutral"}
    cases = [(page_type, html, default_expect) for page_type, html in iter_pages()]
    cases.extend(iter_page_variants())
    for page_type, html, expect in cases:
        scope = f"page:{page_type}"
        facts = parse_markup(html)
        classes.update(facts.classes)
        classes.update(CSS_VAR_USE_RE.findall(html))

        if not facts.has_skiplinks:
            issues.append(Issue("missing_skiplinks", scope, "fr-skiplinks not found"))
        if facts.has_skiplinks and "#content" in facts.hrefs:
            issues.append(Issue("wrong_skiplink_target", scope, "uses #content instead of #contenu"))

        issues.extend(check_common(scope, html))
        issues.extend(check_page_head(scope, facts))
        brand = str(expect.get("brand", "neutral"))
        if expect.get("header", True):
            issues.extend(check_header_contract(scope, f"with_search_{brand}", facts))
        elif has_element(facts, tag="header", class_name="fr-header"):
            issues.append(Issue("header_present_with_no_header", scope, "--no-header emitted a header"))
        if expect.get("footer", True):
            issues.extend(check_footer_contract(scope, brand, facts))
        elif has_element(facts, tag="footer", class_name="fr-footer"):
            issues.append(Issue("footer_present_with_no_footer", scope, "--no-footer emitted a footer"))
        expected_scheme = "dark" if expect.get("dark") else "system"
        if not has_element(facts, tag="html", attr="data-fr-scheme", value=expected_scheme):
            issues.append(Issue("page_scheme", scope, f"html[data-fr-scheme={expected_scheme}] attendu"))
        issues.extend(check_heading_hierarchy(scope, facts))
        issues.extend(check_anchor_targets(scope, facts))
        for component, root_class in (("card", "fr-card"), ("tile", "fr-tile"), ("callout", "fr-callout"), ("alert", "fr-alert"), ("tabs", "fr-tabs"), ("accordion", "fr-accordion"), ("form", "fr-fieldset")):
            if has_element(facts, class_name=root_class):
                issues.extend(check_component_structure(component, "page", scope, facts))
    return issues, classes


def check_components(only_forms: bool = False) -> tuple[list[Issue], set[str], int]:
    issues: list[Issue] = []
    classes: set[str] = set()
    count = 0
    for component, variant, html in iter_components(only_forms=only_forms):
        count += 1
        scope = f"component:{component}.{variant}"
        facts = parse_markup(html)
        classes.update(facts.classes)
        classes.update(CSS_VAR_USE_RE.findall(html))

        allow_error_state = variant in {"error", "with_error", "error_state"}
        issues.extend(check_common(scope, html, allow_error_state=allow_error_state))
        issues.extend(check_component_structure(component, variant, scope, facts))

        if component == "skiplinks" and "#content" in facts.hrefs:
            issues.append(Issue("wrong_skiplink_target", scope, "uses #content instead of #contenu"))
    return issues, classes, count


PREFIX_RE = re.compile(r"(?:<%=\s*prefix\s*%>|\$\{prefix\}|\bprefix\})")
PREFIX_CONCAT_RE = re.compile(r"\bprefix\s*\+\s*(['\"])(-?)")


def _normalize_template_prefix(text: str) -> str:
    """Normalise les références au prefix DSFR vers `fr` pour pouvoir extraire
    les classes de markup, y compris les concats JS (prefix + '-password__label')."""
    text = PREFIX_RE.sub("fr", text)
    return PREFIX_CONCAT_RE.sub(lambda m: "fr" + m.group(2), text)


def official_classes(package_path: Path) -> set[str]:
    if not package_path.exists():
        raise SystemExit(f"official package path not found: {package_path}")

    classes: set[str] = set()
    # Source de vérité : CSS/SCSS (classes stylées) + templates .ejs COURANTS
    # (classes de markup, normalisées prefix -> fr). Les .ejs sous deprecated/
    # sont exclus (markup déprécié, ex. fr-card__link). Les .md/.html/.json
    # d'exemple restent exclus (ils citent des classes non officielles).
    for path in package_path.rglob("*"):
        # Seuls les CSS/SCSS et les gabarits .ejs portent des classes : filtrer
        # avant de lire évite de décoder polices, SVG et bundles JS.
        if path.suffix not in {".css", ".scss", ".ejs"} or not path.is_file():
            continue
        try:
            text = path.read_text(encoding="utf-8", errors="ignore")
        except OSError as exc:
            # Un référentiel incomplet en silence masquerait une classe inventée.
            print(f"Avertissement : lecture impossible de {path} ({exc.strerror or exc})", file=sys.stderr)
            continue
        if path.suffix in {".css", ".scss"}:
            classes.update(CSS_CLASS_RE.findall(text))
            classes.update(CLASS_RE.findall(text))
            classes.update(OFFICIAL_VAR_DEF_RE.findall(text))
            classes.update(CSS_VAR_USE_RE.findall(text))
        elif path.suffix == ".ejs" and "/deprecated/" not in path.as_posix():
            classes.update(CLASS_RE.findall(_normalize_template_prefix(text)))
    return classes


def check_official_catalog(package_path: Path) -> list[Issue]:
    component_dir = package_path / "dist" / "component"
    if not component_dir.is_dir():
        return [Issue("official_package_missing_dist", "official", f"{component_dir} is not a directory")]
    library = json.loads(LIBRARY_PATH.read_text(encoding="utf-8"))
    local = set(library.get("components", {}))
    normalized_local = {registry.official_name(component) for component in local}
    official_components = {
        path.name for path in (package_path / "dist" / "component").iterdir() if path.is_dir()
    }

    unknown_local = sorted(
        component
        for component in normalized_local - official_components
        if component not in registry.LOCAL_HELPER_COMPONENTS
    )
    missing_local = sorted(official_components - normalized_local)
    issues: list[Issue] = []

    if unknown_local:
        issues.append(
            Issue("unknown_official_component", "official-package", ", ".join(unknown_local))
        )
    if missing_local:
        issues.append(
            Issue("missing_local_component", "official-package", ", ".join(missing_local))
        )
    return issues


def check_utility_color_scales(package_path: Path) -> list[Issue]:
    """Confronte UTILITY_COLOR_SCALES du générateur au paquet officiel.

    Le générateur porte la règle hors ligne ; ce contrôle vérifie qu'elle décrit
    encore le paquet. Sans lui, le retrait d'une couleur par l'amont passerait
    inaperçu jusqu'à ce qu'une page émette une classe sans style.
    """
    css_path = package_path / "dist" / "utility" / "utility.css"
    if not css_path.exists():
        return [Issue("utility_css_absent", "official-package", str(css_path))]

    sys.dont_write_bytecode = True
    spec = importlib.util.spec_from_file_location("dsfr_generate_atom", ATOM_SCRIPT)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    css = css_path.read_text(encoding="utf-8", errors="ignore")
    officiel: dict[tuple[str, str], set[str]] = {}
    for kind, variant, color in set(re.findall(r"\.fr-(background|text)-([a-z-]+?)--([a-z0-9-]+)", css)):
        officiel.setdefault((kind, variant), set()).add(color)

    declare = {cle: set(valeurs) for cle, valeurs in module.UTILITY_COLOR_SCALES.items()}
    issues: list[Issue] = []
    for cle in sorted(set(declare) | set(officiel)):
        scope = f"{cle[0]}-{cle[1]}"
        attendu = officiel.get(cle, set())
        obtenu = declare.get(cle, set())
        if obtenu == attendu:
            continue
        en_trop = sorted(obtenu - attendu)
        manquant = sorted(attendu - obtenu)
        detail = []
        if en_trop:
            detail.append(f"déclarées absentes du paquet : {', '.join(en_trop)}")
        if manquant:
            detail.append(f"présentes au paquet mais non déclarées : {', '.join(manquant)}")
        issues.append(Issue("utility_color_scale_drift", scope, " ; ".join(detail)))
    return issues


REFERENCE_CLASS_RE = re.compile(r"^(?:fr|ri)-[a-z0-9]+(?:[-_]{1,2}[a-z0-9]+)*$")
HTML_CLASS_ATTR_RE = re.compile(r'class="([^"]*)"')


def check_reference_classes(package_path: Path, official: set[str] | None = None) -> list[Issue]:
    """Garde-fou de fidélité des fiches : toute classe fr-*/ri-* citée dans un
    bloc HTML de references/**/*.md existe dans le paquet officiel. Les gabarits
    (`fr-alert--[type]`) sont ignorés par la forme stricte du motif."""
    official = official if official is not None else official_classes(package_path)
    issues: list[Issue] = []
    for md in sorted((SKILL_DIR / "references").rglob("*.md")):
        text = md.read_text(encoding="utf-8")
        unknown: set[str] = set()
        for block in re.findall(r"```(?:html)?\n(.*?)```", text, flags=re.S):
            for attr in HTML_CLASS_ATTR_RE.findall(block):
                for token in attr.split():
                    if REFERENCE_CLASS_RE.match(token) and token not in official:
                        unknown.add(token)
        if unknown:
            issues.append(Issue("reference_unknown_class", f"reference:{md.relative_to(SKILL_DIR)}", ", ".join(sorted(unknown)[:8])))
    return issues


def check_official_classes(generated_classes: set[str], package_path: Path) -> list[Issue]:
    official = official_classes(package_path)
    missing = sorted([
        cls
        for cls in generated_classes
        if cls.startswith(("fr-", "ri-", "--"))
        and cls not in official
        and cls not in LOCAL_CSS_VAR_ALLOWLIST
    ])
    if not missing:
        return []
    return [
        Issue("unknown_official_class", "official-package",
              ", ".join(missing[:80]) + (f" (+{len(missing) - 80} non affichées)" if len(missing) > 80 else "")),
    ]


def safe_extract_tar(archive: tarfile.TarFile, target_dir: Path) -> None:
    """Extraction confinée : chemins sous la cible, fichiers et dossiers seulement
    (liens symboliques, liens durs et périphériques refusés), filtre `data`."""
    target_root = target_dir.resolve()
    for member in archive.getmembers():
        member_path = (target_dir / member.name).resolve()
        if target_root not in (member_path, *member_path.parents):
            raise SystemExit(f"unsafe path in official package archive: {member.name}")
        if not (member.isfile() or member.isdir()):
            raise SystemExit(f"unsafe member type in official package archive: {member.name}")
    archive.extractall(target_dir, filter="data")


OFFICIAL_VERSION_RE = re.compile(r"^\d+\.\d+\.\d+(?:[.-][0-9A-Za-z.]+)?$")
OFFICIAL_PACKAGE_MARKERS = ("package.json", "dist/dsfr.min.css", "dist/utility/utility.min.css", "dist/component")


def official_package_complete(package_path: Path) -> bool:
    """Un paquet officiel utilisable porte ses marqueurs ; un cache tronqué n'en est pas un."""
    return all((package_path / marker).exists() for marker in OFFICIAL_PACKAGE_MARKERS)


def resolve_official_package(version: str, cache_dir: Path) -> Path | None:
    """Return the cached official package, downloading it with npm pack if absent.

    Returns None, after an explicit SKIP line, when the package is not cached and
    DSFR_OFFICIAL_CACHE_OFFLINE=1 forbids the download: the official comparison is
    then not exercised, which the caller must report, never silently pass.
    """
    if not OFFICIAL_VERSION_RE.fullmatch(str(version)):
        raise SystemExit(f"invalid official version {version!r}: expected a version number such as 1.15.2")
    package_root = cache_dir / f"gouvfr-dsfr-{version}"
    package_path = package_root / "package"
    if package_root.exists():
        if official_package_complete(package_path):
            return package_path
        raise SystemExit(
            f"official package cache incomplete at {package_path} (expected package.json, dist/dsfr.min.css, "
            f"dist/utility/utility.min.css and dist/component/): remove {package_root} and retry"
        )

    if os.environ.get("DSFR_OFFICIAL_CACHE_OFFLINE") == "1":
        print(
            f"SKIP official package: @gouvfr/dsfr@{version} not cached at {package_path} "
            "and download disabled (DSFR_OFFICIAL_CACHE_OFFLINE=1): official comparison not exercised",
            file=sys.stderr,
        )
        return None

    if shutil.which("npm") is None:
        raise SystemExit("npm not found: cannot fetch @gouvfr/dsfr official package")

    print(
        f"official package download: npm pack @gouvfr/dsfr@{version} -> {package_root} "
        "(network access; set DSFR_OFFICIAL_CACHE_OFFLINE=1 to skip)",
        file=sys.stderr,
    )

    if package_root.exists():
        shutil.rmtree(package_root)
    package_root.mkdir(parents=True, exist_ok=True)

    with tempfile.TemporaryDirectory(prefix="dsfr-official-pack-") as tmp:
        tmp_dir = Path(tmp)
        result = subprocess.run(
            [
                "npm",
                "pack",
                f"@gouvfr/dsfr@{version}",
                "--pack-destination",
                str(tmp_dir),
                
            ],
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )
        if result.returncode != 0:
            raise SystemExit(result.stderr.strip() or f"npm pack @gouvfr/dsfr@{version} failed")

        lines = [line.strip() for line in result.stdout.splitlines() if line.strip()]
        archive_path = Path(lines[-1]) if lines else next(tmp_dir.glob("*.tgz"), None)
        if archive_path is None:
            raise SystemExit(f"npm pack @gouvfr/dsfr@{version} did not produce an archive")
        if not archive_path.is_absolute():
            archive_path = tmp_dir / archive_path
        if not archive_path.exists():
            archives = list(tmp_dir.glob("*.tgz"))
            if not archives:
                raise SystemExit(f"official package archive not found for @gouvfr/dsfr@{version}")
            archive_path = archives[0]

        with tarfile.open(archive_path, "r:gz") as archive:
            safe_extract_tar(archive, package_root)

    if not official_package_complete(package_path):
        raise SystemExit(f"official package incomplete after extraction: {package_path}")
    print(f"official package cache: {package_path}", file=sys.stderr)
    return package_path


def main() -> int:
    parser = argparse.ArgumentParser(description="Check generated DSFR outputs")
    parser.add_argument("--pages-only", action="store_true", help="check only full page outputs (skips native, atom, layout and builder outputs)")
    parser.add_argument("--forms-only", action="store_true", help="check only form-related outputs (skips native, atom, layout and builder outputs)")
    parser.add_argument("--official-package", type=Path, help="path to extracted @gouvfr/dsfr package")
    parser.add_argument(
        "--official-version",
        help="download/cache @gouvfr/dsfr version with npm pack and compare against it",
    )
    parser.add_argument(
        "--official-cache-dir",
        type=Path,
        default=DEFAULT_OFFICIAL_CACHE_DIR,
        help=f"cache directory for --official-version (default: {DEFAULT_OFFICIAL_CACHE_DIR})",
    )
    args = parser.parse_args()

    if args.pages_only and args.forms_only:
        parser.error("--pages-only and --forms-only cannot be combined")
    if args.official_package and args.official_version:
        parser.error("--official-package and --official-version cannot be combined")

    issues: list[Issue] = []
    generated_classes: set[str] = set()
    page_count = 0
    component_count = 0
    check_required_files()
    issues.extend(check_local_artifacts())
    issues.extend(check_root_contract_coverage())

    # Un générateur en échec devient un constat nommé : les autres phases et
    # les constats déjà accumulés sont conservés, sans trace Python.
    if not args.forms_only:
        try:
            page_issues, page_classes = check_pages()
            issues.extend(page_issues)
            generated_classes.update(page_classes)
            page_count = len(PAGE_TYPES)
        except RuntimeError as exc:
            issues.append(Issue("generator_failed", "pages", str(exc)[:200]))

    if not args.pages_only:
        try:
            component_issues, component_classes, component_count = check_components(
                only_forms=args.forms_only
            )
            issues.extend(component_issues)
            generated_classes.update(component_classes)
        except RuntimeError as exc:
            issues.append(Issue("generator_failed", "components", str(exc)[:200]))

    official_package = args.official_package
    official_version = args.official_version or (
        None if args.official_package else os.environ.get("DSFR_OFFICIAL_VERSION")
    )
    official_skipped = None
    if official_version:
        official_package = resolve_official_package(official_version, args.official_cache_dir)
        if official_package is None:
            # Contrat consommateur (scripts/tests/check-consumer-install.sh) : hors
            # ligne sans cache, SKIP explicite et exit 0, cache intact. Le saut est
            # nommé sur stderr et dans le résumé : jamais un PASS silencieux.
            official_skipped = f"@gouvfr/dsfr@{official_version} unavailable offline (DSFR_OFFICIAL_CACHE_OFFLINE=1): official comparison SKIPPED"

    # Sorties natives, atomes, gabarits et builder : non couvertes par
    # check_pages/check_components. Sautées en mode partiel (--pages-only,
    # --forms-only), qui ne compare alors que les classes des sorties contrôlées.
    if not (args.pages_only or args.forms_only):
        try:
            extra_classes, extra_issues = collect_extra_classes()
            issues.extend(extra_issues)
            generated_classes.update(extra_classes)
        except RuntimeError as exc:
            issues.append(Issue("generator_failed", "extra", str(exc)[:200]))

    if official_package:
        issues.extend(check_official_catalog(official_package))
        issues.extend(check_official_classes(generated_classes, official_package))
        issues.extend(check_reference_classes(official_package))
        issues.extend(check_utility_color_scales(official_package))

    if issues:
        print(f"FAIL generated outputs: {len(issues)} issue(s)")
        for issue in issues:
            print(f"{issue.code}\t{issue.scope}\t{issue.detail}")
        print(f"checked pages={page_count} components={component_count}")
        return 1

    if official_skipped:
        print(f"SKIPPED official comparison: {official_skipped}", file=sys.stderr)
        print(f"PASS generated outputs: pages={page_count} components={component_count} (official comparison SKIPPED: not exercised)")
        return 0
    print(f"PASS generated outputs: pages={page_count} components={component_count}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
