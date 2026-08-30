#!/usr/bin/env python3
"""Génère une page DSFR complète assemblée depuis une description JSON de sections.

Réutilise les fonctions de génération de generate_component.py (composants) et la
structure de page de generate_page.py (head, header, skiplinks, footer). Aucune
sortie n'est écrite à la main : la structure DSFR reste portée par les
générateurs partagés, avec vérifications locales à rejouer avant livraison.

Format d'entrée : un objet JSON avec title, description, brand_mode, dark,
assets_prefix, et une liste sections. Chaque section a un `block` (type) et des
props. Voir references/assembly.md pour la liste des blocks et un exemple.
"""

import argparse
import inspect
import json
import subprocess
import shutil
from pathlib import Path
import os
import re
import sys
import tempfile
from html import escape
from html.parser import HTMLParser

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.dont_write_bytecode = True
sys.path.insert(0, SCRIPT_DIR)
import generate_component as gc  # noqa: E402  # pyright: ignore[reportMissingImports]
import generate_field as gf  # noqa: E402  # pyright: ignore[reportMissingImports]
import generate_page as gp  # noqa: E402  # pyright: ignore[reportMissingImports]


def esc(text) -> str:
    if text is None:
        return ""
    return escape(str(text))


_id_prefix_counter: dict = {}
_used_prefixes: set = set()
ARIA_REFERENCE_ATTRS = ("aria-controls", "aria-labelledby", "aria-describedby")
SAFE_DSFR_CLASS_RE = re.compile(r"^fr-[A-Za-z0-9_-]+$")
# Même contrat que safeHref du schéma JSON, durci contre les espaces et
# caractères de contrôle que les navigateurs tolèrent avant le deux-points.
# Liste blanche : tout schéma non listé est refusé, y compris ceux qui
# n'existaient pas à l'écriture de ce code. Une liste noire (javascript, data)
# laissait passer vbscript:, blob:, file:, about: et les URL sans schéma
# explicite (//hote).
ALLOWED_HREF_SCHEMES = frozenset({"http", "https", "mailto", "tel"})

# Attributs dont la valeur est une URL résolue par le navigateur. Contrôler le
# seul href laissait passer action (exécuté à la soumission du formulaire),
# src, cite et les autres. La validation porte sur l'attribut, pas sur le site
# d'émission : un bloc ajouté plus tard hérite du contrôle.
URL_BEARING_ATTRS = (
    "href", "src", "action", "formaction", "cite",
    "poster", "ping", "data", "xlink:href",
)

# Clés de configuration qui deviennent une URL dans la page (en plus des
# attributs ci-dessus) : `link` d'une carte, `image` d'une carte, tuile ou
# citation. Vérifiées AVANT le rendu : generate_component.py neutraliserait
# sinon en « / » sans message, et le contrat d'assembly.md promet un échec.
URL_BEARING_CONFIG_KEYS = frozenset(URL_BEARING_ATTRS) | {"link", "image", "newsletter_url", "operator_src"}


def reject_unsafe_urls(node, path: str = "config") -> None:
    """Parcourt la configuration et refuse toute URL hors liste blanche."""
    if isinstance(node, dict):
        for key, value in node.items():
            here = f"{path}.{key}"
            if key in URL_BEARING_CONFIG_KEYS and isinstance(value, str) and href_is_unsafe(value):
                # Libellé attendu par scripts/tests/check-assembled-page-rejects-unsafe-href.sh
                # du pack : « schéma d'URL interdit », comme le garde-fou aval.
                raise ValueError(
                    f"schéma d'URL interdit dans {here} (autorisés : "
                    f"{', '.join(sorted(ALLOWED_HREF_SCHEMES))}, chemins et ancres locales) : '{value[:40]}'"
                )
            reject_unsafe_urls(value, here)
    elif isinstance(node, list):
        for index, value in enumerate(node):
            reject_unsafe_urls(value, f"{path}[{index}]")

# Les navigateurs retirent tabulation, LF et CR de l'URL et ignorent les
# caractères de contrôle avant d'en résoudre le schéma (spec URL WHATWG).
# Sans cette normalisation préalable, "java<TAB>script:" ne ressemble à aucun
# schéma interdit pour une comparaison de chaîne, mais s'exécute dans un
# navigateur.
HREF_NOISE_RE = re.compile(r"[\x00-\x20\x7f]")
HREF_SCHEME_RE = re.compile(r"^([a-z][a-z0-9+.\-]*):", re.IGNORECASE)


def href_is_unsafe(href: str) -> bool:
    """Vrai si l'href ne doit pas être émis dans la page générée."""
    normalise = HREF_NOISE_RE.sub("", href)
    if not normalise:
        return False
    if normalise.startswith("//"):
        # Protocol-relative : hôte externe, schéma hérité de la page.
        return True
    scheme = HREF_SCHEME_RE.match(normalise)
    if scheme is None:
        # Chemin relatif, chemin absolu local ou ancre : pas de schéma.
        return False
    return scheme.group(1).lower() not in ALLOWED_HREF_SCHEMES


class BuilderHtmlFacts(HTMLParser):
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

    def __init__(self) -> None:
        super().__init__()
        self.ids: dict[str, int] = {}
        self.fragment_hrefs: list[str] = []
        self.unsafe_hrefs: list[str] = []
        self.aria_refs: list[tuple[str, str]] = []
        self.inline_handlers: list[str] = []
        self.main_h1_count = 0
        self.main_depth = 0
        self.modal_depth = 0
        self.stack: list[tuple[str, bool, bool]] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        data = {name.lower(): value or "" for name, value in attrs}
        element_id = data.get("id")
        if element_id:
            self.ids[element_id] = self.ids.get(element_id, 0) + 1

        href = data.get("href")
        if href and href.startswith("#"):
            self.fragment_hrefs.append(href[1:])
        for attr in URL_BEARING_ATTRS:
            valeur = data.get(attr)
            if valeur and href_is_unsafe(valeur):
                self.unsafe_hrefs.append(f"{attr}={valeur}")

        for name in data:
            if name.startswith("on"):
                self.inline_handlers.append(name)
        for attr in ARIA_REFERENCE_ATTRS:
            for target in data.get(attr, "").split():
                self.aria_refs.append((attr, target))

        classes = set(data.get("class", "").split())
        is_main = tag == "main"
        is_modal = "fr-modal" in classes
        if is_main:
            self.main_depth += 1
        if is_modal:
            self.modal_depth += 1
        if tag == "h1" and self.main_depth > 0 and self.modal_depth == 0:
            self.main_h1_count += 1

        if tag not in self.VOID_TAGS:
            self.stack.append((tag, is_main, is_modal))

    def handle_endtag(self, tag: str) -> None:
        # Une balise fermante orpheline ne vide pas la pile : elle est ignorée,
        # sinon main_depth retombe à zéro et les h1 suivants ne sont plus comptés.
        if not any(item[0] == tag for item in self.stack):
            return
        while self.stack:
            item_tag, is_main, is_modal = self.stack.pop()
            if is_main:
                self.main_depth = max(0, self.main_depth - 1)
            if is_modal:
                self.modal_depth = max(0, self.modal_depth - 1)
            if item_tag == tag:
                return

    def handle_startendtag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        self.handle_starttag(tag, attrs)
        if self.stack and self.stack[-1][0] == tag:
            _, is_main, is_modal = self.stack.pop()
            if is_main:
                self.main_depth = max(0, self.main_depth - 1)
            if is_modal:
                self.modal_depth = max(0, self.modal_depth - 1)


SKIPLINK_TARGETS = ("contenu", "navigation", "footer")
HTML_ID_RE = re.compile(r"^[A-Za-z][A-Za-z0-9_-]*$")
MAX_COLUMNS_DEPTH = 8


def _unique_prefix(block_name: str, section: dict) -> str:
    """Préfixe d'ID unique par page pour les blocks à IDs internes
    (accordion, tabs, transcription, breadcrumb). Garantit l'unicité même si le
    block est répété. Remis à zéro au début de build_main."""
    custom = section.get("id_prefix")
    if custom:
        prefix = gc._slug(str(custom), block_name)
        if prefix in _used_prefixes:
            raise ValueError(f"id_prefix '{prefix}' déjà utilisé par une autre section")
        _used_prefixes.add(prefix)
        return prefix
    # Préfixe automatique : premier libre, sans collision avec un préfixe explicite.
    n = _id_prefix_counter.get(block_name, 0)
    while True:
        n += 1
        prefix = block_name if n == 1 else f"{block_name}-{n}"
        if prefix not in _used_prefixes:
            break
    _id_prefix_counter[block_name] = n
    _used_prefixes.add(prefix)
    return prefix


def _as_int(value, name: str) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        raise ValueError(f"{name} doit être un entier")


def _bounded_int(value, name: str, min_value: int = 1, max_value: int = 12) -> int:
    value = _as_int(value, name)
    if value < min_value or value > max_value:
        raise ValueError(f"{name} doit être entre {min_value} et {max_value}")
    return value


def _safe_dsfr_class_list(value, name: str) -> str:
    if not isinstance(value, str):
        raise ValueError(f"{name} doit être une chaîne de classes DSFR")
    tokens = value.split()
    for token in tokens:
        if not SAFE_DSFR_CLASS_RE.fullmatch(token):
            raise ValueError(f"{name} contient une classe DSFR invalide : {token}")
    return " ".join(tokens)


def _col_spans(columns) -> list[int]:
    """Largeurs de grille d'une rangée de `columns` colonnes : la somme vaut
    toujours 12, les 12 % n premières colonnes reçoivent une unité de plus."""
    count = _bounded_int(columns, "columns", 1, 12)
    base, rest = divmod(12, count)
    return [base + (1 if index < rest else 0) for index in range(count)]


def _html_facts(html: str) -> BuilderHtmlFacts:
    parser = BuilderHtmlFacts()
    parser.feed(html)
    return parser


def _drop_unresolved_skiplinks(html: str) -> str:
    ids = set(_html_facts(html).ids)
    for target in SKIPLINK_TARGETS:
        if target in ids:
            continue
        html = re.sub(
            rf'\n?\s*<li><a class="fr-link" href="#{re.escape(target)}">[^<]+</a></li>',
            "",
            html,
        )
    return html


def _section_declares_h1(section: object) -> bool:
    if not isinstance(section, dict):
        return False
    block = section.get("block")
    if block in {"content", "callout", "alert"}:
        default_level = 2 if block == "content" else 3
        try:
            if _as_int(section.get("heading_level", default_level), "heading_level") == 1:
                return True
        except ValueError:
            return False
    if block == "content":
        body = section.get("body")
        if isinstance(body, str) and re.search(r"<h1\b", body, flags=re.IGNORECASE):
            return True
        structured = section.get("body_structured")
        if isinstance(structured, list) and any(
            isinstance(item, dict) and item.get("type") == "heading" and str(item.get("level")) == "1" for item in structured
        ):
            return True
    if block == "columns":
        for col in section.get("columns", []):
            sub_blocks = col.get("blocks", []) if isinstance(col, dict) else col
            if isinstance(sub_blocks, list) and any(_section_declares_h1(sub) for sub in sub_blocks):
                return True
    return False


def _auto_h1_html(config: dict, sections: list) -> str:
    if config.get("auto_h1", True) is False:
        return ""
    if any(_section_declares_h1(section) for section in sections):
        return ""
    title = config.get("main_title") or config.get("title") or "Nom du service"
    return (
        f'            <div class="fr-container fr-pt-6w fr-pb-3w">\n'
        f'                <h1>{esc(title)}</h1>\n'
        f'            </div>'
    )


# --- Builders de blocks : chacun prend la section (dict) et retourne un fragment ---

def block_notice(s):
    return gc.generate_notice(
        title=s.get("title", ""),
        variant=s.get("variant", "info"),
        closable=s.get("closable", False),
        description=s.get("description", s.get("desc")),
        link=s.get("link"),
        id=s.get("id"),
    )


def block_callout(s):
    return gc.generate_callout(
        title=s.get("title", ""),
        text=s.get("text", ""),
        icon=s.get("icon"),
        color=s.get("color"),
        heading_level=int(s.get("heading_level", 3)),
    )


def block_alert(s):
    return gc.generate_alert(
        alert_type=s.get("type", s.get("variant", "info")),
        title=s.get("title", ""),
        description=s.get("text", s.get("description", "")),
        closable=s.get("closable", False),
        heading_level=int(s.get("heading_level", 3)),
    )


def block_highlight(s):
    return gc.generate_highlight(text=s.get("text", ""), size=s.get("size"))


def block_cards(s):
    items = s.get("items", [])
    spans = _col_spans(s.get("columns", 3))
    cols = ""
    for index, it in enumerate(items):
        span = spans[index % len(spans)]
        card = gc.generate_card(
            title=it.get("title", ""),
            description=it.get("desc", it.get("description", "")),
            image=it.get("image"),
            link=it.get("href", "/"),
        )
        cols += f'\n                <div class="fr-col-12 fr-col-md-{span}">{card}\n                </div>'
    return f'<div class="fr-grid-row fr-grid-row--gutters">{cols}\n            </div>'


def block_tiles(s):
    items = s.get("items", [])
    spans = _col_spans(s.get("columns", 3))
    cols = ""
    for index, it in enumerate(items):
        span = spans[index % len(spans)]
        tile = gc.generate_tile(
            title=it.get("title", ""),
            desc=it.get("desc", ""),
            href=it.get("href", "/"),
            orientation=it.get("orientation"),
            image=it.get("image"),
        )
        cols += f'\n                <div class="fr-col-12 fr-col-md-{span}">{tile}\n                </div>'
    return f'<div class="fr-grid-row fr-grid-row--gutters">{cols}\n            </div>'


def block_accordion(s):
    return gc.generate_accordion(
        s.get("items", []), id_prefix=_unique_prefix("accordion", s),
        heading_level=_as_int(s.get("heading_level", 3), "heading_level"),
    )


def block_tabs(s):
    return gc.generate_tab(s.get("tabs", []), id_prefix=_unique_prefix("tabpanel", s))


# Source unique : la table FIELDS de generate_field.py.
FIELD_BLOCKS = dict(gf.FIELDS)


def _field_id(spec, fallback, form_id, seen, label_key: str = "label"):
    """Identifiant de champ unique dans le formulaire : `seen` recense les ids
    réellement émis, explicites ou suffixés, pour qu'aucun ne se répète."""
    explicit = spec.get("id")
    if explicit:
        if explicit in seen:
            raise ValueError(f"id de champ dupliqué dans le formulaire : {explicit}")
        seen[explicit] = 1
        return explicit
    base = f"{form_id}-{gc._slug(spec.get(label_key, ''), fallback)}"
    candidate, n = base, 1
    while candidate in seen:
        n += 1
        candidate = f"{base}-{n}"
    seen[candidate] = 1
    return candidate


def block_form(s):
    action = s.get("action", "/submit")
    method = s.get("method", "post")
    title = s.get("title", "Formulaire")
    submit_label = s.get("submit_label", "Envoyer")
    reset_label = s.get("reset_label")
    deferred = s.get("deferred", False)
    fields_spec = s.get("fields", [])
    form_id = s.get("form_id") or s.get("id") or _unique_prefix("dsfr-assembled-form", s)

    fields_html = ""
    required_ids = []
    field_ids = {}
    for i, spec in enumerate(fields_spec, 1):
        if not isinstance(spec, dict):
            raise ValueError(f"champ {i} du form : doit être un objet")
        ftype = spec.get("type", "input")
        if ftype == "field":
            fname = spec.get("name")
            fn = FIELD_BLOCKS.get(fname or "")
            if not fn:
                raise ValueError(
                    f"champ {i} : bloc fonctionnel '{fname}' inconnu. "
                    f"Disponibles : {', '.join(sorted(FIELD_BLOCKS))}"
                )
            config = dict(spec.get("config") or {})
            # Identifiant unique comme pour les autres champs : deux blocs
            # fonctionnels de même nom ne produisent plus d'ids dupliqués.
            if "id" in inspect.signature(fn).parameters:
                config["id"] = _field_id({"id": config.get("id"), "name": fname}, f"field-{i}", form_id, field_ids, label_key="name")
            fields_html += "\n                            " + fn(**config)
        elif ftype == "textarea":
            fid = _field_id(spec, f"field-{i}", form_id, field_ids)
            hint_html = f'\n                                <span class="fr-hint-text">{esc(spec.get("hint"))}</span>' if spec.get("hint") else ""
            fields_html += (
                f'\n                            <div class="fr-input-group">\n'
                f'                                <label class="fr-label" for="{esc(fid)}">{esc(spec.get("label", "Message"))}{hint_html}\n'
                f'                                </label>\n'
                f'                                <textarea class="fr-input" id="{esc(fid)}" name="{esc(spec.get("name", fid))}" rows="{spec.get("rows", 5)}"></textarea>\n'
                f'                            </div>'
            )
        elif ftype == "select":
            fid = _field_id(spec, f"field-{i}", form_id, field_ids)
            fields_html += "\n                            " + gc.generate_select(
                label=spec.get("label", "Label"), options=spec.get("options", []),
                hint=spec.get("hint"), name=spec.get("name"), id=fid,
            )
        elif ftype == "checkbox":
            fid = _field_id(spec, f"field-{i}", form_id, field_ids)
            fields_html += "\n                            " + gc.generate_checkbox(
                label=spec.get("label", "Option"), name=spec.get("name", "checkbox"), id=fid,
            )
            if spec.get("required"):
                required_ids.append(fid)
        elif ftype == "radio":
            fid = _field_id(spec, f"field-{i}", form_id, field_ids, label_key="legend")
            fields_html += "\n                            " + gc.generate_radio(
                items=spec.get("items", []), legend=spec.get("legend", "Choix"),
                name=spec.get("name", fid), inline=spec.get("inline", False), id=fid,
            )
        else:  # input : text, email, tel, number, date...
            fid = _field_id(spec, f"field-{i}", form_id, field_ids)
            input_type = spec.get("input_type", "text")
            fields_html += "\n                            " + gc.generate_form_input(
                label=spec.get("label", "Label"), input_type=input_type,
                required=False, hint=spec.get("hint"), error=spec.get("error"), id=fid,
                name=spec.get("name"),
            )
            if spec.get("required"):
                required_ids.append(fid)

    reset_html = (
        f'\n                            <button class="fr-btn fr-btn--secondary" type="reset">{esc(reset_label)}</button>'
        if reset_label else ""
    )
    deferred_script = ""
    if deferred and required_ids:
        deferred_script = gp.generate_deferred_validation_script(form_id, required_ids)

    return (
        f'<form id="{esc(form_id)}" action="{esc(action)}" method="{esc(method)}" novalidate>\n'
        f'        <fieldset class="fr-fieldset">\n'
        f'            <legend class="fr-fieldset__legend">\n'
        f'                <h2>{esc(title)}</h2>\n'
        f'            </legend>\n'
        f'            <div class="fr-fieldset__content">{fields_html}\n'
        f'                <div class="fr-btns-group">\n'
        f'                    <button class="fr-btn" type="submit">{esc(submit_label)}</button>{reset_html}\n'
        f'                </div>\n'
        f'            </div>\n'
        f'        </fieldset>{deferred_script}\n'
        f'    </form>'
    )


def block_stepper(s):
    return gc.generate_stepper(
        current=s.get("current", 1),
        total=s.get("total", 4),
        title=s.get("title", "Titre de l'étape"),
        next=s.get("next"),
    )


def block_badges(s):
    items = s.get("items", [])
    lis = "".join(
        f"\n                    <li>{gc.generate_badge(label=it.get('label', 'Badge'), variant=it.get('variant'), sm=it.get('sm', False))}</li>"
        for it in items
    )
    return f'<ul class="fr-badges-group">{lis}\n            </ul>'


def block_tags(s):
    items = s.get("items", [])
    lis = "".join(
        f"\n                    <li>{gc.generate_tag(label=it.get('label', 'Tag'), href=it.get('href'), sm=it.get('sm', False))}</li>"
        for it in items
    )
    return f'<ul class="fr-tags-group">{lis}\n            </ul>'


def block_quote(s):
    return gc.generate_quote(
        text=s.get("text", ""),
        author=s.get("author", ""),
        source=s.get("source"),
        cite=s.get("cite"),
        image=s.get("image"),
    )


RAW_HTML_MARKER = (
    "<!-- allow_raw_html : contenu HTML brut inséré sans vérification "
    "des garde-fous du générateur ; relecture humaine requise -->"
)


def block_content(s):
    body_structured = s.get("body_structured")
    if "body" in s and not s.get("allow_raw_html"):
        raise ValueError(
            "content.body contient du HTML brut : utiliser body_structured, "
            "body_text ou déclarer allow_raw_html=true pour un HTML relu"
        )
    body = s.get("body", "<p>Contenu de la section.</p>")
    if "body" in s and s.get("allow_raw_html"):
        print(
            f"Avertissement : allow_raw_html actif sur la section "
            f"'{s.get('title', 'sans titre')}' — HTML brut inséré sans "
            "vérification, relecture humaine requise",
            file=sys.stderr,
        )
        body = f"{RAW_HTML_MARKER}\n{body}"
    if body_structured is None and "body_text" in s:
        body = gc.render_rich_content(s.get("body_text"))
    return gc.generate_content(
        title=s.get("title", ""),
        lead=s.get("lead"),
        body=body,
        as_article=s.get("as_article", False),
        heading_level=_as_int(s.get("heading_level", 2), "heading_level"),
        body_structured=body_structured,
    )


def block_summary(s):
    return gc.generate_summary(
        title=s.get("title", "Sommaire"),
        items=s.get("items"),
        id_prefix=_unique_prefix("summary", s),
    )


BUTTONS_ALIGN_VALUES = ("inline-md", "right", "center")
IMAGE_RATIO_RE = re.compile(r"^[0-9]+x[0-9]+$")


def block_buttons(s):
    items = s.get("items", [])
    align = s.get("align")
    if align and align not in BUTTONS_ALIGN_VALUES:
        raise ValueError(
            f"block 'buttons' : align '{align}' invalide. "
            f"Valeurs admises : {', '.join(BUTTONS_ALIGN_VALUES)}"
        )
    group_class = "fr-btns-group" + (f" fr-btns-group--{esc(align)}" if align else "")
    lis = ""
    for it in items:
        variant = it.get("variant", "primary")
        size = it.get("size")
        icon = it.get("icon")
        icon_position = it.get("icon_position", "left")
        classes = ["fr-btn"]
        if variant in ("secondary", "tertiary", "tertiary-no-outline"):
            classes.append(f"fr-btn--{variant}")
        if size in ("sm", "lg"):
            classes.append(f"fr-btn--{size}")
        if icon:
            classes.append(f"fr-btn--icon-{icon_position}")
            classes.append(_safe_dsfr_class_list(icon, "block 'buttons' : items[].icon"))
        cls = " ".join(classes)
        label = esc(it.get("label", "Bouton"))
        href = it.get("href")
        if href is not None:
            lis += f'\n                    <li><a class="{cls}" href="{esc(href)}">{label}</a></li>'
        else:
            lis += f'\n                    <li><button class="{cls}" type="button">{label}</button></li>'
    return f'<ul class="{group_class}">{lis}\n                </ul>'


def block_breadcrumb(s):
    return gc.generate_breadcrumb(s.get("items", []), id_prefix=_unique_prefix("breadcrumb", s))


def block_columns(s):
    columns = s.get("columns", [])
    if not columns:
        raise ValueError("block 'columns' : 'columns' (liste de colonnes) requis")
    default_spans = _col_spans(len(columns))
    cols_html = ""
    for col_index, col in enumerate(columns, 1):
        default_span = default_spans[col_index - 1]
        if isinstance(col, dict):
            span = _bounded_int(col.get("span", default_span), f"columns[{col_index}].span", 1, 12)
            sub_blocks = col.get("blocks", [])
        elif isinstance(col, list):
            span = default_span
            sub_blocks = col
        else:
            raise ValueError("chaque colonne doit être un objet {span?, blocks} ou une liste de blocks")
        col_inner = ""
        for sub in sub_blocks:
            if not isinstance(sub, dict):
                raise ValueError("sous-block de colonne : doit être un objet")
            unsupported = sorted(key for key in ("id", "section_id", "heading", "container", "spacing") if key in sub)
            if unsupported:
                raise ValueError(
                    f"block 'columns' : clés de section non prises en charge dans un sous-block ({', '.join(unsupported)}) ; "
                    "les sous-blocks ne sont pas des sections (pas de conteneur ni d'ancre propres)"
                )
            sub_block = sub.get("block")
            builder = BLOCK_BUILDERS.get(sub_block or "")
            if not builder:
                raise ValueError(
                    f"sous-block '{sub_block}' inconnu dans columns. "
                    f"Blocks : {', '.join(sorted(BLOCK_BUILDERS))}"
                )
            try:
                col_inner += "\n" + builder(sub)
            except TypeError as e:
                raise ValueError(f"sous-block '{sub_block}' : paramètre invalide : {e}")
        cols_html += f'\n                <div class="fr-col-12 fr-col-md-{span}">{col_inner}\n                </div>'
    return f'<div class="fr-grid-row fr-grid-row--gutters">{cols_html}\n            </div>'


def _is_svg_src(src) -> bool:
    return bool(re.search(r"\.svg(?:[?#].*)?$", str(src), flags=re.IGNORECASE))


def block_image(s):
    src = s.get("src")
    if not src:
        raise ValueError("block 'image' : 'src' requis")
    if href_is_unsafe(str(src)):
        raise ValueError(f"block 'image' : src '{str(src)[:40]}' refusé (chemin ou URL {', '.join(sorted(ALLOWED_HREF_SCHEMES))} attendus)")
    if "alt" not in s:
        raise ValueError("block 'image' : 'alt' requis (texte alternatif ; chaîne vide pour une image décorative)")
    alt = s.get("alt")
    if not isinstance(alt, str):
        raise ValueError("block 'image' : 'alt' doit être une chaîne")
    # Un alt vide explicite déclare une image décorative (contrat du pack :
    # scripts/tests/check-assembled-page-validates-schema-constraints.sh) ;
    # `decorative: true` en est la forme documentée, facultative. Seule
    # l'absence de la clé est refusée : c'est elle qui rendait l'image
    # décorative en silence.
    if s.get("decorative") and alt.strip():
        raise ValueError("block 'image' : decorative: true exige un alt vide")
    ratio = s.get("ratio")
    if ratio and not IMAGE_RATIO_RE.match(str(ratio)):
        raise ValueError(
            f"block 'image' : ratio '{ratio}' invalide. Format attendu : "
            "largeurxhauteur en chiffres, par exemple 16x9"
        )
    if ratio and _is_svg_src(src):
        raise ValueError("block 'image' : ratio interdit sur SVG ; retirer ratio pour préserver le schéma")
    img_class = "fr-responsive-img" + (f" fr-ratio-{esc(ratio)}" if ratio else "")
    caption = s.get("caption")
    caption_html = f'\n        <figcaption class="fr-content-media__caption">{esc(caption)}</figcaption>' if caption else ""
    return (
        f'<figure class="fr-content-media">\n'
        f'        <div class="fr-content-media__img">\n'
        f'            <img class="{img_class}" src="{esc(src)}" alt="{esc(alt)}">\n'
        f'        </div>{caption_html}\n'
        f'    </figure>'
    )


def block_transcription(s):
    return gc.generate_transcription(label=s.get("label", "Transcription"), content=s.get("content", ""), id_prefix=_unique_prefix("transcription", s))


def _present(section, *keys):
    """Seules les clés fournies sont transmises : None n'écrase pas un défaut du générateur."""
    return {key: section[key] for key in keys if key in section and section[key] is not None}


def block_download(s):
    return gc.generate_download(**_present(s, "label", "href", "detail", "items"))


def block_share(s):
    return gc.generate_share(**_present(s, "title", "items"))


def block_follow(s):
    return gc.generate_follow(**_present(s, "newsletter_title", "newsletter_url", "newsletter_desc", "socials", "id"))


def block_consent(s):
    return gc.generate_consent(
        site_name=s.get("site_name", "nomdusite.gouv.fr"),
        id_prefix=_unique_prefix("consent", s),
    )


BLOCK_BUILDERS = {
    "notice": block_notice,
    "callout": block_callout,
    "alert": block_alert,
    "highlight": block_highlight,
    "cards": block_cards,
    "tiles": block_tiles,
    "accordion": block_accordion,
    "tabs": block_tabs,
    "form": block_form,
    "stepper": block_stepper,
    "badges": block_badges,
    "tags": block_tags,
    "quote": block_quote,
    "content": block_content,
    "summary": block_summary,
    "buttons": block_buttons,
    "breadcrumb": block_breadcrumb,
    "columns": block_columns,
    "image": block_image,
    "transcription": block_transcription,
    "download": block_download,
    "share": block_share,
    "follow": block_follow,
    "consent": block_consent,
}


def build_main(config) -> str:
    """Assemble le contenu du <main> depuis la liste de sections."""
    _id_prefix_counter.clear()
    _used_prefixes.clear()
    sections = config.get("sections", [])
    if not isinstance(sections, list):
        raise ValueError("'sections' doit être une liste")
    parts = []
    auto_h1 = _auto_h1_html(config, sections)
    if auto_h1:
        parts.append(auto_h1)
    for i, section in enumerate(sections):
        if not isinstance(section, dict):
            raise ValueError(f"section {i} : doit être un objet JSON")
        block = section.get("block")
        builder = BLOCK_BUILDERS.get(block or "")
        if not builder:
            raise ValueError(
                f"section {i} : block '{block}' inconnu. Blocks supportés : "
                f"{', '.join(sorted(BLOCK_BUILDERS))}"
            )
        try:
            fragment = builder(section)
        except TypeError as e:
            raise ValueError(f"section {i} (block '{block}') : paramètre invalide : {e}")
        except ValueError as e:
            raise ValueError(f"section {i} (block '{block}') : {e}")
        heading = section.get("heading")
        heading_html = f"\n            <h2 class=\"fr-h3\">{esc(heading)}</h2>" if heading else ""
        # notice apporte déjà son propre fr-container : pas de wrapper supplémentaire.
        wrap = section.get("container", block != "notice")
        spacing = _safe_dsfr_class_list(section.get("spacing", "fr-py-6w"), f"section {i}.spacing")
        section_id = section.get("section_id")
        if section_id and not wrap:
            raise ValueError(f"section {i} (block '{block}') : section_id exige container: true (l'ancre est posée sur le conteneur)")
        # form, follow et notice posent déjà `id` sur leur propre élément.
        if not section_id and block not in {"form", "follow", "notice"}:
            section_id = section.get("id")
        if section_id:
            section_id = str(section_id)
            if not HTML_ID_RE.fullmatch(section_id):
                section_id = gc._slug(section_id, "section")
        id_attr = f' id="{esc(section_id)}"' if section_id and wrap else ""
        if wrap:
            parts.append(f'            <div{id_attr} class="fr-container {spacing}">{heading_html}\n            {fragment}\n            </div>')
        else:
            parts.append(f"{fragment}" if not heading_html else f"{heading_html}\n{fragment}")
    return "\n\n".join(parts)


def validate_generated_html(html: str) -> list[str]:
    """Contrôles rapides propres au builder assemblé."""
    errors: list[str] = []
    facts = _html_facts(html)
    duplicates = sorted(key for key, count in facts.ids.items() if count > 1)
    if duplicates:
        errors.append(f"IDs dupliqués : {', '.join(duplicates[:10])}")

    ids = set(facts.ids)
    for fragment in facts.fragment_hrefs:
        if not fragment:
            errors.append('lien interdit href="#"')
        elif fragment not in ids:
            errors.append(f"ancre locale sans cible : #{fragment}")
    for attr, target in facts.aria_refs:
        if target not in ids:
            errors.append(f"cible ARIA absente : {attr}={target}")

    for href in facts.unsafe_hrefs:
        attr = href.split("=", 1)[0]
        errors.append(
            f"schéma d'URL interdit dans {attr} "
            f"(autorisés : {', '.join(sorted(ALLOWED_HREF_SCHEMES))}) : {href!r}"
        )
    if facts.inline_handlers:
        errors.append("gestionnaire d'événement inline interdit")
    if facts.main_h1_count == 0:
        errors.append("main sans h1 hors modale")
    elif facts.main_h1_count > 1:
        errors.append(f"plusieurs h1 dans main ({facts.main_h1_count}) : un seul h1 par page")
    return errors


def generate_assembled_page(config) -> str:
    """Génère une page HTML complète DSFR depuis un config (dict)."""
    header_cfg = config.get("header")
    footer_cfg = config.get("footer")
    brand_mode = config.get("brand_mode", "neutral")
    custom_header = None
    custom_footer = None
    if header_cfg:
        if not isinstance(header_cfg, dict):
            raise ValueError("'header' doit être un objet (brand_mode, service_title, tools, search, navigation, ...)")
        # header.brand_mode ne vaut que pour l'en-tête : la page et le footer
        # suivent brand_mode à la racine.
        try:
            custom_header = gc.generate_header(**header_cfg)
        except TypeError as e:
            raise ValueError(f"header : paramètre invalide : {e}")
    if footer_cfg:
        if not isinstance(footer_cfg, dict):
            raise ValueError("'footer' doit être un objet (brand_mode, service_name, content_desc, bottom_links, ...)")
        footer_params = dict(footer_cfg)
        footer_params.setdefault("brand_mode", brand_mode)
        try:
            custom_footer = gc.generate_footer(**footer_params)
        except TypeError as e:
            raise ValueError(f"footer : paramètre invalide : {e}")
    html = gp.generate_html_page(
        title=config.get("title", "Nom du service"),
        page_type="standard",
        content=build_main(config),
        dark_mode=config.get("dark", False),
        brand_mode=brand_mode,
        assets_prefix=config.get("assets_prefix"),
        raw_main=True,
        header_html=custom_header,
        footer_html=custom_footer,
        description=config.get("description"),
    )
    return _drop_unresolved_skiplinks(html)


SCHEMA_PATH = Path(__file__).resolve().parent.parent / "schemas" / "generate_assembled_page.schema.json"


def validate_config_against_schema(config) -> list[str]:
    """Erreurs de schéma, liste vide si conforme.

    jsonschema absent = échec nommé, pas un passage silencieux : un contrôle
    qui saute faute de dépendance ressemble à un contrôle qui passe.
    """
    try:
        from jsonschema.validators import validator_for
    except ImportError:
        # Même stratégie que check_assembled_page_schema.py : ré-exécution
        # sous uv avec la dépendance éphémère. Sans uv, échec nommé.
        if os.environ.get("DSFR_JSONSCHEMA_UV_ACTIVE") == "1":
            return ["jsonschema indisponible après ré-exécution uv"]
        uv = shutil.which("uv")
        if not uv:
            return ["jsonschema indisponible et uv introuvable : installer "
                    "jsonschema>=4.22,<5 (le schéma n'a pas été vérifié)"]
        env = dict(os.environ, DSFR_JSONSCHEMA_UV_ACTIVE="1")
        cmd = [uv, "run", "--quiet", "--with", "jsonschema>=4.22,<5",
               "python", str(Path(__file__).resolve()), *sys.argv[1:]]
        if not env.get("UV_CACHE_DIR"):
            cache_owner = os.getuid() if hasattr(os, "getuid") else "user"
            uv_cache_dir = Path(tempfile.gettempdir()) / (
                f"dsfr-agentic-packs-uv-cache-{cache_owner}"
            )
            uv_cache_dir.mkdir(parents=True, exist_ok=True, mode=0o700)
            if hasattr(os, "getuid") and uv_cache_dir.stat().st_uid != os.getuid():
                return [f"cache uv {uv_cache_dir} détenu par un autre utilisateur : définir UV_CACHE_DIR"]
            env["UV_CACHE_DIR"] = str(uv_cache_dir)
        try:
            result = subprocess.run(cmd, env=env, timeout=600)
        except subprocess.TimeoutExpired:
            return ["ré-exécution uv interrompue après 600 s (réseau ou index injoignable)"]
        raise SystemExit(result.returncode)
    try:
        schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return [f"schéma illisible {SCHEMA_PATH}: {exc}"]
    validator = validator_for(schema)(schema)
    try:
        return [
            f"{'/'.join(str(x) for x in err.absolute_path) or '<racine>'}: {err.message}"
            for err in sorted(validator.iter_errors(config), key=lambda e: list(e.absolute_path))
        ]
    except RecursionError:
        return ["configuration trop profondément imbriquée pour être validée"]


def _columns_depth(sections, level: int = 0) -> int:
    """Profondeur maximale des columns imbriquées (la validation de schéma croît avec elle)."""
    deepest = level
    if not isinstance(sections, list):
        return deepest
    for section in sections:
        if not isinstance(section, dict) or section.get("block") != "columns":
            continue
        for col in section.get("columns", []) or []:
            sub_blocks = col.get("blocks", []) if isinstance(col, dict) else col
            deepest = max(deepest, _columns_depth(sub_blocks, level + 1))
    return deepest


def main():
    parser = argparse.ArgumentParser(
        description=f"Générateur de pages DSFR assemblées ({len(BLOCK_BUILDERS)} blocks : {', '.join(sorted(BLOCK_BUILDERS))})"
    )
    parser.add_argument("--config-file", required=True, help="Fichier JSON décrivant la page (title, brand_mode, sections)")
    parser.add_argument("--output", help="Fichier de sortie ; refuse d'écraser un fichier existant")
    parser.add_argument("--check", action="store_true", help="Valide la configuration et le HTML généré sans écrire de fichier")
    args = parser.parse_args()

    if args.check and args.output:
        print("Erreur : --check et --output ne se combinent pas (--check ne produit aucun fichier)", file=sys.stderr)
        sys.exit(1)
    if args.output is not None and not args.output.strip():
        print("Erreur : --output vide ; omettre l'option pour écrire sur stdout", file=sys.stderr)
        sys.exit(1)
    try:
        with open(args.config_file, encoding="utf-8") as f:
            config = json.load(f)
    except FileNotFoundError:
        print(f"Erreur : fichier de configuration introuvable : {args.config_file}", file=sys.stderr)
        sys.exit(1)
    except OSError as e:
        print(f"Erreur : fichier de configuration illisible : {args.config_file} ({e.strerror})", file=sys.stderr)
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"Erreur : JSON invalide dans {args.config_file} : {e}", file=sys.stderr)
        sys.exit(1)

    if not isinstance(config, dict):
        print(f"Erreur : {args.config_file} doit contenir un objet JSON", file=sys.stderr)
        sys.exit(1)
    depth = _columns_depth(config.get("sections", []))
    if depth > MAX_COLUMNS_DEPTH:
        print(f"Erreur : profondeur d'imbrication des columns {depth} > {MAX_COLUMNS_DEPTH}", file=sys.stderr)
        sys.exit(1)

    # Le schéma n'était appliqué que par check_assembled_page_schema.py, jamais
    # par le builder : une config hors schéma produisait du HTML. La validation
    # HTML aval reste la barrière de sécurité ; le schéma est la barrière de
    # contrat, et l'agent doit la rencontrer au même endroit.
    try:
        reject_unsafe_urls(config)
    except ValueError as exc:
        print(f"Erreur : {exc}", file=sys.stderr)
        sys.exit(1)
    schema_errors = validate_config_against_schema(config)
    if schema_errors:
        for error in schema_errors:
            print(f"Erreur de schéma : {error}", file=sys.stderr)
        sys.exit(1)

    try:
        html = generate_assembled_page(config)
    except ValueError as e:
        print(f"Erreur : {e}", file=sys.stderr)
        sys.exit(1)

    errors = validate_generated_html(html)
    if errors:
        for error in errors:
            print(f"Erreur : {error}", file=sys.stderr)
        sys.exit(1)

    if args.check:
        section_count = len(config.get("sections", [])) if isinstance(config.get("sections", []), list) else 0
        print(f"OK : configuration valide ({section_count} sections, {len(html)} caractères générés)")
        return

    if args.output:
        gc.write_output(html, args.output, "Page assemblée générée")
    else:
        if hasattr(sys.stdout, "reconfigure"):
            sys.stdout.reconfigure(encoding="utf-8")
        sys.stdout.write(html)


if __name__ == "__main__":
    main()
