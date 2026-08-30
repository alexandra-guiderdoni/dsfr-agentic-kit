#!/usr/bin/env python3
"""
Générateur de composants DSFR
Crée des fragments HTML alignés avec le Design System de l'État français
(DSFR 1.15.2), sans revendiquer une conformité sans audit dédié.

Mode 1 : Composants natifs — génération paramétrable avec fonctions Python
Mode 2 : Bibliothèque JSON — injection directe depuis dsfr_complete_library.json
"""

import argparse
import json
import os
import re
import sys
from html import escape
from pathlib import Path
from typing import Dict, Any


SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
LIBRARY_PATH = str(Path(__file__).resolve().parent.parent / "assets" / "dsfr_complete_library.json")
sys.dont_write_bytecode = True
import dsfr_component_registry as registry  # noqa: E402


def esc(text: str) -> str:
    """Échappe le HTML pour éviter les injections XSS (préserve 0 et False)."""
    if text is None:
        return ""
    return escape(str(text))


def normalize_generated_html(html: str) -> str:
    """Retire les liens factices qui ne doivent jamais sortir du générateur."""
    return html.replace('href="#"', 'href="/"')


# Liste blanche : tout schéma non listé est neutralisé, y compris ceux qui
# n'existaient pas à l'écriture de ce code. Une liste noire (javascript, data)
# laissait passer vbscript:, blob:, file:, about: et les URL sans schéma
# explicite (//hote).
ALLOWED_HREF_SCHEMES = frozenset({"http", "https", "mailto", "tel"})

# Les navigateurs retirent tabulation, LF et CR de l'URL et ignorent les
# caractères de contrôle avant d'en résoudre le schéma (spec URL WHATWG).
# Sans cette normalisation préalable, "java<TAB>script:" ne ressemble à aucun
# schéma interdit pour une comparaison de chaîne, mais s'exécute.
HREF_NOISE_RE = re.compile(r"[\x00-\x20\x7f]")
HREF_SCHEME_RE = re.compile(r"^([a-z][a-z0-9+.\-]*):", re.IGNORECASE)


def _safe_href(value) -> str:
    """Rend un href sûr : repli sur "/" si son schéma n'est pas autorisé."""
    href = str(value or "/").strip()
    if not href or href == "#":
        return "/"
    # Les navigateurs lisent la barre oblique inverse comme une barre oblique
    # pour les schémas spéciaux : /\hote, \\hote et \/hote sont protocol-relative.
    normalise = HREF_NOISE_RE.sub("", href).replace("\\", "/")
    if not normalise:
        return "/"
    if normalise.startswith("//"):
        # Protocol-relative : hôte externe, schéma hérité de la page.
        return "/"
    scheme = HREF_SCHEME_RE.match(normalise)
    if scheme is None:
        # Chemin relatif, chemin absolu local ou ancre : pas de schéma.
        return href
    if scheme.group(1).lower() not in ALLOWED_HREF_SCHEMES:
        return "/"
    return href


def esc_src(value, name: str = "src") -> str:
    """Échappement d'un attribut src d'image : chemin ou URL http(s) obligatoire.

    Un src vide ferait recharger le document courant ; un schéma exécutable
    n'a rien à faire dans une image. Contrairement à esc_href, pas de repli :
    l'erreur remonte à l'appelant (ValueError, code 1 en ligne de commande).
    """
    src = str(value or "").strip()
    if not src:
        raise ValueError(f"{name} : chemin d'image obligatoire")
    normalise = HREF_NOISE_RE.sub("", src)
    if normalise.startswith("//"):
        raise ValueError(f"{name} : URL relative au protocole refusée")
    scheme = HREF_SCHEME_RE.match(normalise)
    if scheme and scheme.group(1).lower() not in ("http", "https"):
        raise ValueError(f"{name} : schéma '{scheme.group(1)}' refusé pour une image")
    return esc(src)


SAFE_CLASS_TOKEN_RE = re.compile(r"^(fr|ri)-[A-Za-z0-9_-]+$")
ICON_POSITIONS = ("left", "right")


def _safe_icon(icon, icon_position: str, name: str = "icon") -> tuple[str, str]:
    """Nom de classe d'icône DSFR/Remix et position validés : ils entrent dans un attribut class."""
    token = str(icon).strip()
    if not SAFE_CLASS_TOKEN_RE.fullmatch(token):
        raise ValueError(f"{name} '{token[:40]}' invalide : une classe fr-icon-* ou ri-* est attendue")
    if icon_position not in ICON_POSITIONS:
        raise ValueError(f"icon_position '{icon_position}' inconnu : utiliser left ou right")
    return token, icon_position


def _as_item(value, label_key: str = "label") -> dict:
    """Normalise un élément de liste : une chaîne devient {label_key: chaîne}."""
    if isinstance(value, dict):
        return value
    return {label_key: str(value)}


def esc_href(value) -> str:
    """Échappement HTML d'un href, schéma validé au passage.

    Tout attribut href du générateur doit passer par ici et non par esc() :
    esc() protège le contexte HTML, pas le schéma d'URL.
    """
    return esc(_safe_href(value))


def _as_list(value) -> list:
    if value is None:
        return []
    return value if isinstance(value, list) else [value]


def _heading_tag(level) -> str:
    try:
        value = int(level)
    except (TypeError, ValueError):
        raise ValueError("heading_level doit être un entier entre 1 et 6")
    if value < 1 or value > 6:
        raise ValueError("heading_level doit être un entier entre 1 et 6")
    return f"h{value}"


NEW_WINDOW_SUFFIX = " - nouvelle fenêtre"


def _link_attrs(label: str, target=None, rel=None, title=None) -> str:
    """Attributs title/target/rel d'un lien. Une cible `_blank` (casse et
    espaces ignorés) impose `rel=noopener` et un `title` qui annonce la
    nouvelle fenêtre, comme les exemples officiels 1.15.2 (share, footer)."""
    target_value = str(target or "").strip()
    rel_values = str(rel or "").split()
    title_value = str(title or "").strip()
    if target_value.lower() == "_blank":
        target_value = "_blank"
        if "noopener" not in rel_values:
            rel_values.append("noopener")
        if "nouvelle fenêtre" not in title_value.lower():
            title_value = f"{title_value or label}{NEW_WINDOW_SUFFIX}"
    title_attr = f' title="{esc(title_value)}"' if title_value else ""
    target_attr = f' target="{esc(target_value)}"' if target_value else ""
    rel_attr = f' rel="{esc(" ".join(rel_values))}"' if rel_values else ""
    return f"{title_attr}{target_attr}{rel_attr}"


def _rich_link(item: dict) -> str:
    label = item.get("label") or item.get("text") or item.get("href") or "Lien"
    href = _safe_href(item.get("href"))
    attrs = _link_attrs(str(label), item.get("target"), item.get("rel"), item.get("title"))
    return f'<a href="{esc_href(href)}"{attrs}>{esc(label)}</a>'


def _rich_inline(item) -> str:
    if isinstance(item, dict):
        if item.get("href"):
            return _rich_link(item)
        return esc(item.get("label", item.get("text", "")))
    return esc(item)


def _rich_list(items, ordered: bool = False) -> str:
    tag = "ol" if ordered else "ul"
    rows = "".join(f"\n        <li>{_rich_inline(item)}</li>" for item in _as_list(items))
    return f"<{tag}>{rows}\n    </{tag}>"


def _rich_block(block) -> str:
    if not isinstance(block, dict):
        return f"<p>{esc(block)}</p>"
    kind = block.get("type", "paragraph")
    if kind in {"paragraph", "p"}:
        return f"<p>{esc(block.get('text', ''))}</p>"
    if kind in {"heading", "title"}:
        tag = _heading_tag(block.get("level", 2))
        return f"<{tag}>{esc(block.get('text', ''))}</{tag}>"
    if kind in {"list", "ul", "ol"}:
        return _rich_list(block.get("items", []), ordered=kind == "ol" or block.get("ordered", False))
    if kind == "links":
        return _rich_list(block.get("items", []), ordered=False)
    if kind == "link":
        return f"<p>{_rich_link(block)}</p>"
    raise ValueError(f"bloc : type '{kind}' inconnu ; types attendus : paragraph, heading, list, ol, links, link")


def render_rich_content(content, default: str = "") -> str:
    """Rend un contenu éditorial structuré sans accepter de HTML brut.

    Chaîne simple : paragraphe échappé, comportement historique.
    Objet structuré : paragraphes, liste, liens ou blocks typés.
    """
    if content is None:
        return f"<p>{esc(default)}</p>"
    if isinstance(content, str):
        return f"<p>{esc(content or default)}</p>"
    if isinstance(content, list):
        return _rich_list(content)
    if not isinstance(content, dict):
        return f"<p>{esc(content)}</p>"

    fragments: list[str] = []
    for block in _as_list(content.get("blocks")):
        fragments.append(_rich_block(block))
    for paragraph in _as_list(content.get("paragraphs")):
        fragments.append(f"<p>{esc(paragraph)}</p>")
    if "list" in content:
        fragments.append(_rich_list(content.get("list"), ordered=content.get("ordered", False)))
    if "links" in content:
        fragments.append(_rich_list(content.get("links"), ordered=False))
    if content.get("link"):
        fragments.append(f"<p>{_rich_link(content['link'])}</p>")
    if not fragments:
        raise ValueError(
            f"content : structure non reconnue ({', '.join(sorted(content))}) ; clés attendues : blocks, paragraphs, list, links, link"
        )
    return "\n    ".join(fragments)


def load_library() -> Dict[str, Any]:
    """Charge la bibliothèque JSON des composants DSFR."""
    try:
        with open(LIBRARY_PATH, "r", encoding="utf-8") as f:
            library = json.load(f)
    except FileNotFoundError:
        return {}
    except (json.JSONDecodeError, UnicodeDecodeError) as e:
        print(f"Erreur : bibliothèque JSON illisible ({LIBRARY_PATH}) : {e}", file=sys.stderr)
        sys.exit(1)
    if not isinstance(library, dict) or not isinstance(library.get("components", {}), dict):
        print(f"Erreur : bibliothèque JSON invalide ({LIBRARY_PATH}) : objet 'components' attendu", file=sys.stderr)
        sys.exit(1)
    return library


def list_components(library: Dict[str, Any]) -> None:
    """Affiche la liste des composants disponibles."""
    native = sorted(NATIVE_COMPONENTS.keys())
    json_components = sorted(library.get("components", {}).keys())

    print("Composants natifs (génération paramétrable) :")
    for c in native:
        print(f"  - {c}")

    print(f"\nComposants bibliothèque JSON ({len(json_components)} disponibles) :")
    for c in json_components:
        comp = library["components"][c]
        variants = ", ".join(comp.get("variants", []))
        print(f"  - {c} ({comp.get('count', 0)} variantes : {variants})")


def generate_from_library(library: Dict[str, Any], component: str, variant: str | None = None) -> str:
    """Génère un composant depuis la bibliothèque JSON."""
    components = library.get("components", {})
    component = registry.canonical_name(component)
    if component not in components:
        print(f"Erreur : composant '{component}' introuvable dans la bibliothèque.", file=sys.stderr)
        print(f"Composants disponibles : {', '.join(sorted(components.keys()))}", file=sys.stderr)
        sys.exit(1)

    comp = components[component]
    html_variants = comp.get("html", {})
    variants = comp.get("variants", [])

    if variant:
        if variant not in html_variants:
            print(f"Erreur : variante '{variant}' introuvable pour '{component}'.", file=sys.stderr)
            print(f"Variantes disponibles : {', '.join(variants)}", file=sys.stderr)
            sys.exit(1)
        return normalize_generated_html(html_variants[variant])
    else:
        # Sans variante spécifiée : la première déclarée, sinon la première rendue
        if not html_variants:
            print(f"Erreur : le composant '{component}' n'a aucune variante dans la bibliothèque.", file=sys.stderr)
            sys.exit(1)
        first_variant = variants[0] if variants and variants[0] in html_variants else sorted(html_variants)[0]
        return normalize_generated_html(html_variants[first_variant])


# === Générateurs natifs paramétrables ===

def generate_button(variant: str = "primary", size: str = "md", label: str = "Libellé bouton",
                    icon: str | None = None, icon_position: str = "left", disabled: bool = False,
                    button_type: str = "button") -> str:
    """Génère un bouton DSFR. `button_type` vaut button (défaut), submit ou reset."""
    if button_type not in ("button", "submit", "reset"):
        raise ValueError(f"button_type '{button_type}' inconnu : utiliser button, submit ou reset")
    classes = ["fr-btn"]

    if variant == "secondary":
        classes.append("fr-btn--secondary")
    elif variant == "tertiary":
        classes.append("fr-btn--tertiary")
    elif variant == "tertiary-no-outline":
        classes.append("fr-btn--tertiary-no-outline")

    if size == "sm":
        classes.append("fr-btn--sm")
    elif size == "lg":
        classes.append("fr-btn--lg")

    if icon:
        icon, icon_position = _safe_icon(icon, icon_position)
        classes.append(f"fr-btn--icon-{icon_position}")
        classes.append(icon)

    disabled_clause = ' disabled aria-disabled="true"' if disabled else ''

    return f'<button type="{button_type}" class="{" ".join(classes)}"{disabled_clause}>{esc(label)}</button>'


def generate_alert(alert_type: str = "info", title: str = "", description: str = "", closable: bool = False,
                   heading_level: int = 3, live: bool = False) -> str:
    """Génère une alerte DSFR. Sans rôle par défaut (exemple officiel) ; `live`
    réserve `role=alert` (error/warning) ou `role=status` (success/info) aux
    alertes ajoutées après le chargement (doc accessibilité officielle 1.15.2)."""
    alert_class = f"fr-alert fr-alert--{esc(alert_type)}"
    role_attr = ""
    if live:
        role_attr = ' role="alert"' if alert_type in {"error", "warning"} else ' role="status"'

    close_button = ""
    if closable:
        close_button = """    <button type="button" class="fr-btn--close fr-btn" title="Masquer le message">
        Masquer le message
    </button>"""

    default_title = "Titre de l'alerte"
    default_desc = "Description de l'alerte"
    return f"""
<div class="{alert_class}"{role_attr}>
    <{_heading_tag(heading_level)} class="fr-alert__title">{esc(title) or default_title}</{_heading_tag(heading_level)}>
    <p>{esc(description) or default_desc}</p>
{close_button}
</div>"""


def generate_accordion(items: list, id_prefix: str = "accordion", heading_level: int = 3) -> str:
    """Génère un accordéon DSFR. `id_prefix` garantit l'unicité des IDs si
    plusieurs accordéons cohabitent dans la même page ; `heading_level` (2 à 6)
    place le titre de chaque section dans la hiérarchie de la page."""
    id_prefix = _slug(id_prefix, "accordion")
    heading_tag = _heading_tag(heading_level)
    if heading_tag == "h1":
        raise ValueError("heading_level : un accordéon ne porte pas le h1 de la page (2 à 6)")
    if not items:
        items = [{
            "title": "Titre de l'accordéon",
            "content": "Contenu de l'accordéon",
        }]

    accordion_html = '<div class="fr-accordions-group">\n'

    for i, item in enumerate(items, start=1):
        data = item if isinstance(item, dict) else {"content": item}
        cid = f"{id_prefix}-{i}"
        content = render_rich_content(data.get("content"), "Contenu de l'accordéon")
        accordion_html += f"""
    <section class="fr-accordion">
        <{heading_tag} class="fr-accordion__title">
            <button type="button" class="fr-accordion__btn" aria-expanded="false" aria-controls="{cid}">
                {esc(data.get('title', f'Titre {i}'))}
            </button>
        </{heading_tag}>
        <div class="fr-collapse" id="{cid}">
            {content}
        </div>
    </section>"""

    accordion_html += '\n</div>'
    return accordion_html


def generate_card(title: str = "", description: str = "", image: str | None = None, link: str = "/",
                  orientation: str = "vertical", image_alt: str = "") -> str:
    """Génère une carte DSFR (exemple officiel card 1.15.2) : le bloc image
    `fr-card__header` suit `fr-card__body` dans le DOM ; horizontale sur demande."""
    if orientation not in {"vertical", "horizontal"}:
        raise ValueError(f"orientation '{orientation}' inconnue : vertical ou horizontal")
    card_classes = "fr-card fr-card--horizontal" if orientation == "horizontal" else "fr-card"
    image_html = f"""
    <div class="fr-card__header">
        <div class="fr-card__img">
            <img class="fr-responsive-img" src="{esc_src(image, "image")}" alt="{esc(image_alt)}" />
        </div>
    </div>""" if image else ""

    return f"""
<div class="{card_classes}">
    <div class="fr-card__body">
        <div class="fr-card__content">
            <h3 class="fr-card__title">
                <a href="{esc_href(link)}">{esc(title) or 'Titre de la carte'}</a>
            </h3>
            <p class="fr-card__desc">{esc(description) or 'Description de la carte'}</p>
        </div>
    </div>{image_html}
</div>"""


def generate_modal(title: str = "", content: str = "", id: str = "fr-modal",
                   trigger_label: str = "Ouvrir la modale") -> str:
    """Génère une modale DSFR avec son bouton déclencheur (data-fr-opened)."""
    modal_id = _slug(id, "fr-modal")
    return f"""
<button class="fr-btn" data-fr-opened="false" aria-controls="{modal_id}" type="button">{esc(trigger_label)}</button>
<dialog id="{modal_id}" class="fr-modal" aria-labelledby="{modal_id}-title">
    <div class="fr-container fr-container--fluid fr-container-md">
        <div class="fr-grid-row fr-grid-row--center">
            <div class="fr-col-12 fr-col-md-8 fr-col-lg-6">
                <div class="fr-modal__body">
                    <div class="fr-modal__header">
                        <button class="fr-btn--close fr-btn" title="Fermer" aria-controls="{modal_id}" type="button">Fermer</button>
                    </div>
                    <div class="fr-modal__content">
                        <h2 id="{modal_id}-title" class="fr-modal__title">{esc(title) or 'Titre de la modale'}</h2>
                        <p>{esc(content) or 'Contenu de la modale'}</p>
                    </div>
                    <div class="fr-modal__footer">
                        <div class="fr-btns-group fr-btns-group--right fr-btns-group--inline-reverse fr-btns-group--inline-lg">
                            <button type="button" class="fr-btn">Action principale</button>
                            <button type="button" class="fr-btn fr-btn--secondary">Action secondaire</button>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
</dialog>"""


def generate_form_input(label: str, input_type: str = "text", required: bool = False,
                        hint: str | None = None, error: str | None = None,
                        id: str | None = None, name: str | None = None,
                        valid: str | None = None) -> str:
    """Génère un champ de formulaire DSFR ; `name` vaut l'identifiant par défaut.
    `error` ou `valid` posent l'état sur le groupe ET sur l'input (fiche fields)."""
    input_id = id or _slug(str(label), "input")
    input_name = name or input_id
    if error and valid:
        raise ValueError("error et valid sont exclusifs")
    required_hint = '<span class="fr-hint-text">Champ obligatoire</span>' if required else ''
    error_class = ' fr-input-group--error' if error else (' fr-input-group--valid' if valid else '')
    input_state = ' fr-input--error' if error else (' fr-input--valid' if valid else '')
    describedby = f' aria-describedby="{input_id}-error"' if error else (f' aria-describedby="{input_id}-valid"' if valid else '')

    hint_html = f'<span class="fr-hint-text">{esc(hint)}</span>' if hint else ''
    error_html = f'<p id="{input_id}-error" class="fr-error-text">{esc(error)}</p>' if error else ''
    if valid:
        error_html = f'<p id="{input_id}-valid" class="fr-valid-text">{esc(valid)}</p>'

    return f"""
<div class="fr-input-group{error_class}">
    <label class="fr-label" for="{esc(input_id)}">
        {esc(label)}
        {hint_html}
        {required_hint}
    </label>
    <input class="fr-input{input_state}" type="{esc(input_type)}" id="{esc(input_id)}" name="{esc(input_name)}"{describedby} />
    {error_html}
</div>"""


def generate_breadcrumb(items: list, id_prefix: str = "breadcrumb") -> str:
    """Génère un fil d'Ariane DSFR. `id_prefix` garantit l'unicité des IDs si
    plusieurs fils d'Ariane cohabitent dans la même page."""
    id_prefix = _slug(id_prefix, "breadcrumb")
    items = [_as_item(item) for item in items] or [{"label": "Accueil", "href": "/"}, {"label": "Page courante"}]
    breadcrumb_html = f"""
<nav role="navigation" class="fr-breadcrumb" aria-label="vous êtes ici :">
    <button type="button" class="fr-breadcrumb__button" aria-expanded="false" aria-controls="{id_prefix}">Voir le fil d'Ariane</button>
    <div class="fr-collapse" id="{id_prefix}">
        <ol class="fr-breadcrumb__list">"""

    for i, item in enumerate(items[:-1]):
        href = item.get("href", item.get("url", "/"))
        breadcrumb_html += f"""
            <li>
                <a class="fr-breadcrumb__link" href="{esc_href(href)}">{esc(item.get('label', f'Niveau {i+1}'))}</a>
            </li>"""

    if items:
        breadcrumb_html += f"""
            <li>
                <a class="fr-breadcrumb__link" aria-current="page">{esc(items[-1].get('label', 'Page courante'))}</a>
            </li>"""

    breadcrumb_html += """
        </ol>
    </div>
</nav>"""
    return breadcrumb_html


def generate_badge(label: str = "Badge", variant: str | None = None, sm: bool = False) -> str:
    """Génère un badge DSFR"""
    classes = ["fr-badge"]
    if variant:
        classes.append(f"fr-badge--{esc(variant)}")
    if sm:
        classes.append("fr-badge--sm")
    return f'<p class="{" ".join(classes)}">{esc(label)}</p>'


# Accentuations de tag du paquet 1.15.2 (dist/component/tag/tag.min.css).
TAG_COLORS = (
    "beige-gris-galet", "blue-cumulus", "blue-ecume", "brown-cafe-creme", "brown-caramel", "brown-opera",
    "green-archipel", "green-bourgeon", "green-emeraude", "green-menthe", "green-tilleul-verveine",
    "orange-terre-battue", "pink-macaron", "pink-tuile", "purple-glycine", "yellow-moutarde", "yellow-tournesol",
)


def generate_tag(label: str = "Tag", href: str | None = None, dismissible: bool = False,
                 sm: bool = False, icon: str | None = None, icon_position: str = "left",
                 color: str | None = None) -> str:
    """Génère un tag DSFR (statique, lien ou bouton supprimable), coloré sur demande."""
    classes = ["fr-tag"]
    if sm:
        classes.append("fr-tag--sm")
    if color:
        if color not in TAG_COLORS:
            raise ValueError(f"color '{color}' inconnue pour un tag ; couleurs attendues : {', '.join(TAG_COLORS)}")
        classes.append(f"fr-tag--{color}")
    if icon:
        icon, icon_position = _safe_icon(icon, icon_position)
        classes.append(f"fr-tag--icon-{icon_position}")
        classes.append(icon)
    class_attr = " ".join(classes)
    safe_label = esc(label)
    if dismissible:
        return (f'<button type="button" class="{class_attr} fr-tag--dismiss" '
                f'aria-label="Retirer {safe_label}">{safe_label}</button>')
    if href:
        return f'<a class="{class_attr}" href="{esc_href(href)}">{safe_label}</a>'
    return f'<p class="{class_attr}">{safe_label}</p>'


def generate_callout(title: str = "", text: str = "", icon: str | None = None, color: str | None = None,
                     heading_level: int = 3) -> str:
    """Génère une mise en avant (callout) DSFR"""
    classes = ["fr-callout"]
    if icon:
        classes.append(_safe_icon(icon, "left")[0])
    if color:
        classes.append(f"fr-callout--{esc(color)}")
    return f"""
<div class="{" ".join(classes)}">
    <{_heading_tag(heading_level)} class="fr-callout__title">{esc(title) or 'Titre de la mise en avant'}</{_heading_tag(heading_level)}>
    <p class="fr-callout__text">{esc(text) or 'Texte de la mise en avant'}</p>
</div>"""


def generate_highlight(text: str = "", size: str | None = None) -> str:
    """Génère une mise en exergue DSFR"""
    text_class = ""
    if size in ("sm", "lead"):
        text_class = f' class="fr-text--{size}"'
    return f"""
<div class="fr-highlight">
    <p{text_class}>{esc(text) or 'Texte mis en exergue'}</p>
</div>"""


def generate_notice(title: str = "", variant: str = "info", closable: bool = False,
                    description: str | None = None, desc: str | None = None,
                    link: dict | str = None, id: str | None = None) -> str:
    """Génère un bandeau d'information (notice) DSFR"""
    classes = ["fr-notice"]
    if variant:
        classes.append(f"fr-notice--{esc(variant)}")
    id_attr = f' id="{esc(id)}"' if id else ""
    description_text = description if description is not None else desc
    desc_html = f'\n                <span class="fr-notice__desc">{esc(description_text)}</span>' if description_text else ""
    link_html = ""
    if link:
        if isinstance(link, dict):
            link_label = link.get("label", "En savoir plus")
            link_href = link.get("href", "/")
            link_title = link.get("title")
            link_target = link.get("target")
            link_rel = link.get("rel")
        else:
            link_label = "En savoir plus"
            link_href = str(link)
            link_title = None
            link_target = None
            link_rel = None
        link_html = (
            f'\n                <a class="fr-notice__link" href="{esc_href(link_href)}"'
            f'{_link_attrs(str(link_label), link_target, link_rel, link_title)}>{esc(link_label)}</a>'
        )
    close_button = ""
    if closable:
        close_button = """
        <button class="fr-btn--close fr-btn" title="Masquer le message" type="button">
            Masquer le message
        </button>"""
    return f"""
<div class="{" ".join(classes)}"{id_attr}>
    <div class="fr-container">
        <div class="fr-notice__body">
            <p>
                <span class="fr-notice__title">{esc(title) or 'Information importante'}</span>{desc_html}{link_html}
            </p>{close_button}
        </div>
    </div>
</div>"""


def generate_link(label: str = "Lien", href: str = "/", size: str | None = None,
                  icon: str | None = None, icon_position: str = "left", download: bool = False) -> str:
    """Génère un lien DSFR"""
    classes = ["fr-link"]
    if size in ("sm", "lg"):
        classes.append(f"fr-link--{size}")
    if icon:
        icon, icon_position = _safe_icon(icon, icon_position)
        classes.append(f"fr-link--icon-{icon_position}")
        classes.append(icon)
    download_attr = " download" if download else ""
    return f'<a class="{" ".join(classes)}" href="{esc_href(href)}"{download_attr}>{esc(label)}</a>'


def write_output(html: str, output: str, label: str) -> None:
    """Écrit `html` dans `output` (tilde développé) sans jamais écraser un fichier
    existant (ouverture exclusive) ; messages sur stderr, code 1 sur erreur.
    Partagée par generate_page, generate_atom et generate_layout."""
    if not str(output).strip():
        print("Erreur : --output vide ; omettre l'option pour écrire sur stdout", file=sys.stderr)
        sys.exit(1)
    target = Path(output).expanduser()
    if target.is_dir():
        print(f"Erreur : le chemin '{output}' est un répertoire ; indiquer un fichier", file=sys.stderr)
        sys.exit(1)
    if not target.parent.exists():
        print(f"Erreur : le dossier '{target.parent}' n'existe pas", file=sys.stderr)
        sys.exit(1)
    try:
        with target.open("x", encoding="utf-8") as handle:
            handle.write(html)
    except FileExistsError:
        print(f"Erreur : le fichier '{output}' existe déjà. Choisir un autre chemin ou supprimer explicitement le fichier.", file=sys.stderr)
        sys.exit(1)
    except OSError as exc:
        print(f"Erreur : impossible d'écrire '{output}' : {exc.strerror or exc}", file=sys.stderr)
        sys.exit(1)
    print(f"{label} : {output}", file=sys.stderr)


def _int_value(value, name: str) -> int:
    """Entier strict (bool et flottants non entiers refusés) pour les bornes."""
    if isinstance(value, bool) or not isinstance(value, (int, float, str)):
        raise ValueError(f"{name} : entier attendu, reçu {type(value).__name__}")
    try:
        number = float(value)
    except ValueError:
        raise ValueError(f"{name} : entier attendu, reçu {value!r}") from None
    if number != int(number):
        raise ValueError(f"{name} : entier attendu, reçu {value!r}")
    return int(number)


def _slug(text: str, fallback: str) -> str:
    """Slugifie un libellé en id valide (kebab-case)."""
    cleaned = "".join(c if c.isalnum() else "-" for c in (text or "").lower().strip())
    return cleaned.strip("-") or fallback


def generate_select(label: str = "Label", options: list | None = None, hint: str | None = None,
                    placeholder: str = "Sélectionnez une option", name: str | None = None,
                    id: str | None = None) -> str:
    """Génère une liste déroulante DSFR (état neutre au repos)"""
    options = options or []
    field_id = id or _slug(label, "select")
    name_attr = name or field_id
    hint_html = f'\n        <span class="fr-hint-text">{esc(hint)}</span>' if hint else ""
    opts_html = ""
    for opt in options:
        if isinstance(opt, dict):
            val = esc(opt.get("value", opt.get("label", "")))
            txt = esc(opt.get("label", opt.get("value", "")))
        else:
            val = esc(str(opt))
            txt = val
        opts_html += f'\n        <option value="{val}">{txt}</option>'
    return f"""
<div class="fr-select-group">
    <label class="fr-label" for="{esc(field_id)}">{esc(label)}{hint_html}
    </label>
    <select class="fr-select" id="{esc(field_id)}" name="{esc(name_attr)}">
        <option value="" selected disabled>{esc(placeholder)}</option>{opts_html}
    </select>
</div>"""


def generate_checkbox(items: list | None = None, legend: str | None = None, label: str = "Option",
                      name: str | None = None, id: str | None = None) -> str:
    """Génère une case à cocher DSFR (isolée, ou groupe si legend est fourni)"""
    name_attr = name or "checkbox"
    if legend:
        field_id = id or _slug(legend, "checkboxes")
        items = items or [{"label": "Option 1"}, {"label": "Option 2"}]
        rows = ""
        for i, it in enumerate(items, 1):
            it_label = it.get("label", f"Option {i}") if isinstance(it, dict) else str(it)
            it_id = (it.get("id") if isinstance(it, dict) else None) or f"{field_id}-{i}"
            rows += f"""
        <div class="fr-checkbox-group">
            <input type="checkbox" id="{esc(it_id)}" name="{esc(name_attr)}">
            <label class="fr-label" for="{esc(it_id)}">{esc(it_label)}</label>
        </div>"""
        return f"""
<fieldset class="fr-fieldset" aria-labelledby="{esc(field_id)}-legend">
    <legend class="fr-fieldset__legend" id="{esc(field_id)}-legend">{esc(legend)}</legend>
    <div class="fr-fieldset__content">{rows}
    </div>
</fieldset>"""
    field_id = id or _slug(label, "checkbox")
    return f"""
<div class="fr-checkbox-group">
    <input type="checkbox" id="{esc(field_id)}" name="{esc(name_attr)}">
    <label class="fr-label" for="{esc(field_id)}">{esc(label)}</label>
</div>"""


def generate_radio(items: list | None = None, legend: str = "Choix", name: str | None = None,
                   inline: bool = False, id: str | None = None) -> str:
    """Génère un groupe de boutons radio DSFR"""
    items = items or [{"label": "Option 1", "value": "1"}, {"label": "Option 2", "value": "2"}]
    name_attr = name or "radio"
    field_id = id or _slug(legend, "radio")
    modifier = " fr-fieldset--inline" if inline else ""
    rows = ""
    for i, it in enumerate(items, 1):
        it_label = it.get("label", f"Option {i}") if isinstance(it, dict) else str(it)
        it_value = it.get("value", str(i)) if isinstance(it, dict) else str(it)
        it_id = (it.get("id") if isinstance(it, dict) else None) or f"{field_id}-{i}"
        rows += f"""
        <div class="fr-radio-group">
            <input type="radio" id="{esc(it_id)}" name="{esc(name_attr)}" value="{esc(it_value)}">
            <label class="fr-label" for="{esc(it_id)}">{esc(it_label)}</label>
        </div>"""
    return f"""
<fieldset class="fr-fieldset{modifier}" aria-labelledby="{esc(field_id)}-legend">
    <legend class="fr-fieldset__legend" id="{esc(field_id)}-legend">{esc(legend)}</legend>
    <div class="fr-fieldset__content">{rows}
    </div>
</fieldset>"""


def generate_toggle(label: str = "Label de l'interrupteur", hint: str | None = None,
                    state: bool = False, border: bool = False,
                    disabled: bool = False, checked: bool = False,
                    id: str | None = None, items: list | None = None, legend: str | None = None,
                    name: str | None = None) -> str:
    """Génère un interrupteur DSFR (fidèle au template toggle.ejs 1.15.2)"""
    if items is not None or legend is not None:
        group_id = id or _slug(legend or "toggle-group", "toggle-group")
        legend_text = legend or "Légende pour l'ensemble des éléments"
        group_messages_id = f"{group_id}-messages"
        rows = ""
        toggle_items = items or [{"label": "Option 1"}, {"label": "Option 2"}]
        for index, item in enumerate(toggle_items, 1):
            data = item if isinstance(item, dict) else {"label": str(item)}
            item_label = data.get("label", f"Option {index}")
            item_id = data.get("id") or f"{group_id}-{index}"
            rows += f"""
                <li>{generate_toggle(
                    label=item_label,
                    hint=data.get("hint"),
                    state=data.get("state", state),
                    border=data.get("border", False),
                    disabled=data.get("disabled", False),
                    checked=data.get("checked", False),
                    id=item_id,
                )}
                </li>"""
        return f"""
<fieldset class="fr-fieldset" id="{esc(group_id)}" aria-labelledby="{esc(group_id)}-legend {esc(group_messages_id)}">
    <legend class="fr-fieldset__legend" id="{esc(group_id)}-legend">
        {esc(legend_text)}
    </legend>
    <div class="fr-fieldset__element">
        <ul class="fr-toggle__list">{rows}
        </ul>
    </div>
    <div class="fr-messages-group" id="{esc(group_messages_id)}" aria-live="polite">
    </div>
</fieldset>"""

    field_id = id or _slug(label, "toggle")
    classes = ["fr-toggle"]
    if border:
        classes.append("fr-toggle--border-bottom")
    checked_attr = " checked" if checked else ""
    disabled_attr = " disabled" if disabled else ""
    state_attr = ' data-fr-checked-label="Activé" data-fr-unchecked-label="Désactivé"' if state else ""
    message_id = f"{field_id}-messages"
    hint_html = ""
    describedby_ids = []
    if hint:
        hint_id = f"{field_id}-hint"
        describedby_ids.append(hint_id)
        hint_html = f'\n    <p class="fr-hint-text" id="{hint_id}">{esc(hint)}</p>'
    describedby_ids.append(message_id)
    describedby = f' aria-describedby="{" ".join(esc(target) for target in describedby_ids)}"'
    return f"""
<div class="{" ".join(classes)}">
    <input type="checkbox" class="fr-toggle__input" id="{esc(field_id)}"{checked_attr}{disabled_attr}{describedby}>
    <label class="fr-toggle__label" for="{esc(field_id)}"{state_attr}>{esc(label)}</label>{hint_html}
    <div class="fr-messages-group" id="{esc(message_id)}" aria-live="polite">
    </div>
</div>"""


def generate_search(label: str = "Rechercher", placeholder: str = "Rechercher",
                    size: str | None = None, name: str = "search", id: str | None = None,
                    action: str = "/recherche") -> str:
    """Génère une barre de recherche DSFR dans son <form> (fonctionnement sans JS,
    search/_part/doc/code du paquet 1.15.2)."""
    field_id = id or "search"
    classes = ["fr-search-bar"]
    if size == "lg":
        classes.append("fr-search-bar--lg")
    return f"""
<form action="{esc_href(action)}" method="get">
    <div class="{" ".join(classes)}" role="search">
        <label class="fr-label" for="{esc(field_id)}">{esc(label)}</label>
        <input class="fr-input" placeholder="{esc(placeholder)}" type="search" id="{esc(field_id)}" name="{esc(name)}">
        <button type="submit" class="fr-btn" title="{esc(label)}">{esc(label)}</button>
    </div>
</form>"""


def generate_range(label: str = "Label du curseur", min: int = 0, max: int = 100,
                   value=None, step=None, name: str | None = None, id: str | None = None,
                   hint: str | None = None, size: str | None = None,
                   disabled: bool = False) -> str:
    """Génère un curseur (range) DSFR 1.15.2.

    Structure du gabarit officiel `range.ejs` (#1407, 1.15.0) : `fr-range-group`
    > label lié par `for`/`id` (+ `fr-hint-text`), conteneur `div.fr-range`
    (variantes `--sm`, `--step`) qui porte la sortie `fr-range__output` masquée
    aux technologies d'assistance, l'input et les bornes `fr-range__min` /
    `fr-range__max`, puis `fr-messages-group` en `aria-live="polite"`. La
    classe `fr-range` va sur le conteneur, jamais sur l'input : le script du
    composant la cible pour positionner la sortie. Source : exemple rendu
    `example/component/range/index.html` du paquet @gouvfr/dsfr@1.15.2.
    """
    field_id = id or _slug(label, "range")
    name_attr = name or field_id
    min = _int_value(min, "min")
    max = _int_value(max, "max")
    if min >= max:
        raise ValueError(f"range : min ({min}) doit être strictement inférieur à max ({max})")
    value = min if value is None else _int_value(value, "value")
    # La valeur est ramenée dans [min, max] : la sortie visible ne peut pas
    # afficher un chiffre que le champ ne porte pas.
    if value < min:
        value = min
    if value > max:
        value = max
    if step is not None:
        step = _int_value(step, "step")
        if step < 1:
            raise ValueError("range : step doit être un entier >= 1")
    range_classes = ["fr-range"]
    if size == "sm":
        range_classes.append("fr-range--sm")
    if step is not None:
        range_classes.append("fr-range--step")
    group_classes = ["fr-range-group"]
    if disabled:
        group_classes.append("fr-range-group--disabled")
    hint_html = f'\n        <span class="fr-hint-text">{esc(hint)}</span>' if hint else ""
    step_attr = f' step="{esc(step)}"' if step is not None else ""
    disabled_attr = " disabled" if disabled else ""
    messages_id = f"{field_id}-messages"
    return f"""
<div class="{' '.join(group_classes)}">
    <label class="fr-label" for="{esc(field_id)}">{esc(label)}{hint_html}
    </label>
    <div class="{' '.join(range_classes)}">
        <span class="fr-range__output" aria-hidden="true">{esc(value)}</span>
        <input type="range" id="{esc(field_id)}" name="{esc(name_attr)}" min="{esc(min)}" max="{esc(max)}" value="{esc(value)}"{step_attr}{disabled_attr} aria-describedby="{esc(messages_id)}">
        <span class="fr-range__min" aria-hidden="true">{esc(min)}</span>
        <span class="fr-range__max" aria-hidden="true">{esc(max)}</span>
    </div>
    <div class="fr-messages-group" id="{esc(messages_id)}" aria-live="polite"></div>
</div>"""


def generate_upload(label: str = "Ajouter un fichier", hint: str | None = None,
                    multiple: bool = False, name: str = "file", id: str | None = None) -> str:
    """Génère un champ d'envoi de fichier DSFR"""
    field_id = id or _slug(label, "file-upload")
    hint_html = f'\n        <span class="fr-hint-text">{esc(hint)}</span>' if hint else ""
    multiple_attr = " multiple" if multiple else ""
    return f"""
<div class="fr-upload-group">
    <label class="fr-label" for="{esc(field_id)}">{esc(label)}{hint_html}
    </label>
    <input class="fr-upload" type="file" id="{esc(field_id)}" name="{esc(name)}"{multiple_attr}>
</div>"""


def generate_stepper(current: int = 1, total: int = 4, title: str = "Titre de l'étape",
                     next: str | None = None) -> str:
    """Génère un indicateur d'étapes DSFR"""
    current = _int_value(current, "current")
    total = _int_value(total, "total")
    if total < 1:
        raise ValueError(f"stepper : total ({total}) doit être >= 1")
    if not 1 <= current <= total:
        raise ValueError(f"stepper : current ({current}) doit être compris entre 1 et total ({total})")
    details = ""
    if next:
        details = f'\n    <p class="fr-stepper__details"><span class="fr-text--bold">Étape suivante :</span> {esc(next)}</p>'
    # Exemple officiel stepper 1.15.2 : le titre précède l'état dans le h2.
    return f"""
<div class="fr-stepper">
    <h2 class="fr-stepper__title">
        {esc(title)}
        <span class="fr-stepper__state">Étape {esc(current)} sur {esc(total)}</span>
    </h2>
    <div class="fr-stepper__steps" data-fr-current-step="{esc(current)}" data-fr-steps="{esc(total)}"></div>{details}
</div>"""


def generate_pagination(current: int = 1, total: int = 5, label: str = "Pagination") -> str:
    """Génère une pagination DSFR"""
    try:
        total = int(total)
        current = int(current)
    except (TypeError, ValueError):
        raise ValueError("total et current doivent être des entiers") from None
    if total < 1:
        raise ValueError(f"total doit être au moins 1 (reçu {total})")
    if not 1 <= current <= total:
        raise ValueError(f"current doit être entre 1 et total={total} (reçu {current})")
    pages = ""
    for p in range(1, total + 1):
        if p == current:
            pages += f'\n        <li><a class="fr-pagination__link" aria-current="page" title="Page {p}">{p}</a></li>'
        else:
            pages += f'\n        <li><a class="fr-pagination__link" href="/page-{p}" title="Page {p}">{p}</a></li>'
    prev_p = max(1, current - 1)
    next_p = min(total, current + 1)
    return f"""
<nav role="navigation" class="fr-pagination" aria-label="{esc(label)}">
    <ul class="fr-pagination__list">
        <li><a class="fr-pagination__link fr-pagination__link--first" href="/page-1">Première page</a></li>
        <li><a class="fr-pagination__link fr-pagination__link--prev fr-pagination__link--lg-label" href="/page-{prev_p}">Page précédente</a></li>{pages}
        <li><a class="fr-pagination__link fr-pagination__link--next fr-pagination__link--lg-label" href="/page-{next_p}">Page suivante</a></li>
        <li><a class="fr-pagination__link fr-pagination__link--last" href="/page-{total}">Dernière page</a></li>
    </ul>
</nav>"""


def generate_tile(title: str = "Titre de la tuile", desc: str = "", href: str = "/",
                  orientation: str | None = None, image: str | None = None) -> str:
    """Génère une tuile DSFR"""
    classes = ["fr-tile"]
    if orientation in ("horizontal", "vertical"):
        classes.append(f"fr-tile--{orientation}")
    classes.append("fr-enlarge-link")
    header = ""
    if image:
        header = f"""
    <div class="fr-tile__header">
        <div class="fr-tile__img"><img src="{esc_src(image, "image")}" alt=""></div>
    </div>"""
    return f"""
<div class="{" ".join(classes)}">{header}
    <div class="fr-tile__body">
        <div class="fr-tile__content">
            <h3 class="fr-tile__title"><a href="{esc_href(href)}">{esc(title) or 'Titre de la tuile'}</a></h3>
            <p class="fr-tile__desc">{esc(desc)}</p>
        </div>
    </div>
</div>"""


def generate_quote(text: str = "", author: str = "", source: str | None = None,
                   cite: str | None = None, image: str | None = None) -> str:
    """Génère une citation DSFR"""
    cite_attr = f' cite="{esc(cite)}"' if cite else ""
    # Exemple officiel quote 1.15.2 : l'image illustrative (alt vide) suit
    # l'auteur et la source, et la figure prend `fr-quote--column`.
    img_html = ""
    if image:
        img_html = f'\n        <div class="fr-quote__image"><img class="fr-responsive-img" src="{esc_src(image, "image")}" alt=""></div>'
    source_html = ""
    if source:
        source_html = f'\n        <ul class="fr-quote__source"><li><cite>{esc(source)}</cite></li></ul>'
    figure_class = "fr-quote fr-quote--column" if image else "fr-quote"
    return f"""
<figure class="{figure_class}">
    <blockquote{cite_attr}><p>« {esc(text) or 'Citation'} »</p></blockquote>
    <figcaption>
        <p class="fr-quote__author">{esc(author) or 'Auteur'}</p>{source_html}{img_html}
    </figcaption>
</figure>"""


def generate_tooltip(text: str = "Contenu de l'infobulle", label: str = "Bouton avec infobulle",
                     id: str | None = None) -> str:
    """Génère une info-bulle DSFR et son déclencheur"""
    tip_id = id or "tooltip-1"
    return f"""<button class="fr-btn--tooltip fr-btn" type="button" aria-describedby="{esc(tip_id)}">{esc(label)}</button>
<span class="fr-tooltip fr-placement" id="{esc(tip_id)}" role="tooltip">{esc(text)}</span>"""


def generate_segmented(items: list | None = None, legend: str = "Légende", hint: str | None = None,
                       name: str = "segmented", value: str | None = None) -> str:
    """Génère un contrôle segmenté DSFR"""
    items = items or [{"label": "Libellé 1", "value": "1"}, {"label": "Libellé 2", "value": "2"}]
    hint_html = f'\n        <span class="fr-hint-text">{esc(hint)}</span>' if hint else ""
    elements = ""
    for i, it in enumerate(items, 1):
        it_label = it.get("label", f"Libellé {i}") if isinstance(it, dict) else str(it)
        it_value = it.get("value", str(i)) if isinstance(it, dict) else str(it)
        it_id = f"{name}-{i}"
        checked = " checked" if (value is not None and str(value) == str(it_value)) else ""
        elements += f"""
        <div class="fr-segmented__element">
            <input value="{esc(it_value)}" type="radio" id="{esc(it_id)}" name="{esc(name)}"{checked}>
            <label class="fr-label" for="{esc(it_id)}">{esc(it_label)}</label>
        </div>"""
    return f"""
<fieldset class="fr-segmented">
    <legend class="fr-segmented__legend">{esc(legend)}{hint_html}
    </legend>
    <div class="fr-segmented__elements">{elements}
    </div>
</fieldset>"""


CSS_LENGTH_RE = re.compile(r"^\d+(\.\d+)?(rem|em|px)$")


def generate_logo(brand: str = "republique", operator_src: str | None = None, operator_alt: str | None = None,
                  operator_max_width: str = "3.5rem") -> str:
    """Génère un bloc marque DSFR (République française ou opérateur). Le logo
    opérateur suit l'exemple officiel header 1.15.2 : `fr-responsive-img` et
    une largeur maximale en ligne."""
    if brand == "operator" or operator_src:
        if not CSS_LENGTH_RE.match(str(operator_max_width)):
            raise ValueError(f"operator_max_width '{operator_max_width}' invalide : longueur CSS attendue (ex. 3.5rem)")
        return (f'<div class="fr-header__operator">\n    <img class="fr-responsive-img" style="max-width:{operator_max_width};" '
                f'src="{esc_src(operator_src, "operator_src")}" alt="{esc(operator_alt or "Opérateur")}">\n</div>')
    return '<p class="fr-logo">République<br>Française</p>'


# Variantes officielles du bouton connect (i18n/fr.yml du paquet). Le libellé
# de marque reste « FranceConnect » pour `plus` : le « + » est ajouté par
# `.fr-connect--plus:after` en CSS, l'écrire dans le markup le doublerait.
# `pro` est apparu en DSFR 1.15.0 ; son logo vient de `.fr-connect--pro:before`.
CONNECT_VARIANTS = {
    "default": ("", "FranceConnect", "https://franceconnect.gouv.fr/", "Qu'est-ce que FranceConnect ?"),
    "plus": (" fr-connect--plus", "FranceConnect", "https://franceconnect.gouv.fr/france-connect-plus", "Qu'est-ce que FranceConnect+ ?"),
    "pro": (" fr-connect--pro", "ProConnect", "https://proconnect.gouv.fr/", "Qu'est-ce que ProConnect ?"),
}


def generate_connect(brand: str = "plus", help_url: str | None = None,
                     help_label: str | None = None) -> str:
    """Génère un bouton FranceConnect ou ProConnect DSFR.

    `brand` vaut `default`, `plus` ou `pro` (variantes officielles 1.15.2).
    `help_url` et `help_label` surchargent le lien d'aide de la variante.
    """
    if brand not in CONNECT_VARIANTS:
        raise ValueError(
            f"variante connect '{brand}' inconnue : utiliser {' ou '.join(CONNECT_VARIANTS)}"
        )
    variant, label, default_url, default_label = CONNECT_VARIANTS[brand]
    help_url = help_url or default_url
    help_label = help_label or default_label
    return f"""<div class="fr-connect-group">
    <button type="button" class="fr-connect{variant}">
        <span class="fr-connect__login">S'identifier avec</span>
        <span class="fr-connect__brand">{esc(label)}</span>
    </button>
    <p>
        <a href="{esc_href(help_url)}" target="_blank" rel="noopener" title="{esc(help_label)} - nouvelle fenêtre">
            {esc(help_label)}
        </a>
    </p>
</div>"""


def generate_download(label: str = "Télécharger le document", href: str = "/document.pdf",
                      detail: str = "PDF – 2,3 Mo", items: list | None = None) -> str:
    """Génère un lien ou un groupe de téléchargement DSFR"""
    if items:
        rows = ""
        for it in items:
            it = _as_item(it)
            rows += (f'\n        <li>\n            <div class="fr-download">\n                <a class="fr-download__link" href="{esc_href(it.get("href", "/"))}" download>'
                     f'\n                    {esc(it.get("label", "Document"))}'
                     f'\n                    <span class="fr-download__detail">\n                        {esc(it.get("detail", ""))}'
                     f'\n                    </span>\n                </a>\n            </div>\n        </li>')
        return f'<div class="fr-downloads-group">\n    <ul>{rows}\n    </ul>\n</div>'
    # Conteneur fr-download (classe stylée du paquet 1.15.2) autour du lien.
    return f"""<div class="fr-download">
    <a class="fr-download__link" href="{esc_href(href)}" download>
        {esc(label)}
        <span class="fr-download__detail">
            {esc(detail)}
        </span>
    </a>
</div>"""


def generate_content(title: str = "Titre de niveau 2", lead: str | None = None,
                     body: str = "<p>Contenu de la section.</p>", as_article: bool = False,
                     heading_level: int = 2, body_structured=None, body_text: str | None = None,
                     image: str | None = None, image_alt: str = "", caption: str | None = None,
                     video: str | None = None, video_title: str | None = None) -> str:
    """Génère un bloc de contenu éditorial DSFR, ou, avec `image` ou `video`, le
    composant officiel « Contenu média » (figure.fr-content-media, exemple
    content 1.15.2 ; la vidéo est un iframe fr-responsive-vid dont le title
    décrit le média).

    `body` est inséré brut (HTML non échappé) : c'est du contenu éditorial
    maîtrisé. Ne pas y passer de contenu non fiable (risque d'injection HTML).
    """
    if image and video:
        raise ValueError("content : image et video sont exclusifs")
    if video:
        if not str(video_title or "").strip():
            raise ValueError("content : video_title obligatoire (titre accessible de l'iframe)")
        video_src = _safe_href(video)
        if not str(video_src).startswith(("http://", "https://")):
            raise ValueError("content : video doit être une URL http(s) d'intégration")
        caption_text = caption or title
        return f"""<figure role="group" class="fr-content-media" aria-label="{esc(caption_text)}">
    <iframe title="{esc(video_title)}" class="fr-responsive-vid" src="{esc_href(video_src)}" allow="accelerometer; autoplay; encrypted-media; gyroscope; picture-in-picture" allowfullscreen></iframe>
    <figcaption class="fr-content-media__caption">{esc(caption_text)}</figcaption>
</figure>"""
    if image:
        caption_text = caption or title
        return f"""<figure role="group" class="fr-content-media" aria-label="{esc(caption_text)}">
    <div class="fr-content-media__img">
        <img class="fr-responsive-img" src="{esc_src(image, "image")}" alt="{esc(image_alt)}">
    </div>
    <figcaption class="fr-content-media__caption">{esc(caption_text)}</figcaption>
</figure>"""
    tag = "article" if as_article else "div"
    heading_tag = _heading_tag(heading_level)
    lead_html = f'\n    <p class="fr-text--lead">{esc(lead)}</p>' if lead else ""
    if body_structured is not None:
        body_html = render_rich_content(body_structured)
    elif body_text is not None:
        body_html = f"<p>{esc(body_text)}</p>"
    else:
        body_html = body
    return f"""<{tag}>
    <{heading_tag}>{esc(title)}</{heading_tag}>{lead_html}
    {body_html}
</{tag}>"""


def generate_summary(title: str = "Sommaire", items: list | None = None, id_prefix: str = "summary") -> str:
    """Génère un sommaire DSFR"""
    title_id = f"{_slug(id_prefix, 'summary')}-title"
    items = items or [{"label": "Section 1", "href": "#section-1"}, {"label": "Section 2", "href": "#section-2"}]
    rows = ""
    for i, it in enumerate(items, 1):
        it = _as_item(it)
        sub = ""
        for s in it.get("children", []):
            s = _as_item(s)
            sub += f'\n                <li><a class="fr-summary__link" href="{esc_href(s.get("href", "/"))}">{esc(s.get("label", ""))}</a></li>'
        sub_html = f'\n            <ol>{sub}\n            </ol>' if sub else ""
        rows += f'\n        <li>\n            <a class="fr-summary__link" href="{esc_href(it.get("href", "/"))}">{esc(it.get("label", f"Section {i}"))}</a>{sub_html}\n        </li>'
    return f"""<nav class="fr-summary" role="navigation" aria-labelledby="{esc(title_id)}">
    <h2 class="fr-summary__title" id="{esc(title_id)}">{esc(title)}</h2>
    <ol>{rows}
    </ol>
</nav>"""


def generate_share(title: str = "Partager la page", items: list | None = None) -> str:
    """Génère un bloc de partage DSFR"""
    if items is None:
        items = [
        {"platform": "facebook", "label": "Partager sur Facebook", "href": "/"},
        {"platform": "twitter", "label": "Partager sur Twitter", "href": "/"},
        {"platform": "linkedin", "label": "Partager sur LinkedIn", "href": "/"},
        {"platform": "mail", "label": "Envoyer par email", "href": "mailto:?subject=Partage"},
    ]
    rows = ""
    for it in items:
        it = _as_item(it, "platform")
        label = str(it.get("label", "Partager"))
        href = str(it.get("href", "/"))
        # Exemple officiel share 1.15.2 : nouvelle fenêtre annoncée dans le
        # title pour les réseaux ; l'envoi par courriel reste dans l'onglet.
        attrs = _link_attrs(label, None if href.startswith("mailto:") else "_blank", None, None if href.startswith("mailto:") else label)
        rows += (f'\n        <li>\n            <a class="fr-share__link fr-share__link--{esc(it.get("platform", ""))}"'
                 f'{attrs} href="{esc_href(href)}">\n                {esc(label)}\n            </a>\n        </li>')
    return f"""<div class="fr-share">
    <p class="fr-share__title">{esc(title)}</p>
    <ul class="fr-share__group">{rows}
    </ul>
</div>"""


def generate_translate(current: str = "FR", languages: list | None = None,
                       id: str = "translate-menu") -> str:
    """Génère un sélecteur de langue DSFR 1.15.2.

    Structure de la documentation officielle depuis 1.15.0 (#1431) :
    `div.fr-translate.fr-nav` (plus de `nav` ni de `role="navigation"`)
    contenant un `fr-nav__item` avec le bouton `fr-translate__btn` et le menu
    `fr-collapse`. La classe `fr-translate__language` est réservée aux liens.
    Chaque langue : `code`, `label` (nom complet) et `href` optionnel. Source :
    exemple rendu `example/component/translate/index.html` du paquet 1.15.2.
    """
    languages = languages or [
        {"code": "fr", "label": "Français", "href": "/fr/"},
        {"code": "en", "label": "English", "href": "/en/"},
    ]
    current_code = str(current).lower()
    if not any(str(lang.get("code", "")).lower() == current_code for lang in languages):
        raise ValueError(f"current '{current}' absent de languages ({', '.join(str(l.get('code', '')) for l in languages)})")
    rows = ""
    current_label = ""
    for lang in languages:
        code = str(lang.get("code", ""))
        label = str(lang.get("label", code.upper()))
        if label.upper().startswith(code.upper() + " - "):
            label = label[len(code) + 3:]
        is_current = code.lower() == current_code
        if is_current:
            current_label = label
        cur = ' aria-current="true"' if is_current else ""
        rows += (f'\n                <li>\n'
                 f'                    <a class="fr-translate__language fr-nav__link" hreflang="{esc(code)}" lang="{esc(code)}"'
                 f' href="{esc_href(lang.get("href", "/"))}"{cur}>{esc(code.upper())} - {esc(label)}</a>\n'
                 f'                </li>')
    button_label = f'{esc(current.upper())}<span class="fr-hidden-lg">&nbsp;- {esc(current_label)}</span>'
    return f"""<div class="fr-translate fr-nav">
    <div class="fr-nav__item">
        <button type="button" class="fr-translate__btn fr-btn fr-btn--tertiary" aria-controls="{esc(id)}" aria-expanded="false" title="Sélectionner une langue">{button_label}</button>
        <div class="fr-collapse fr-translate__menu fr-menu" id="{esc(id)}">
            <ul class="fr-menu__list">{rows}
            </ul>
        </div>
    </div>
</div>"""


def generate_transcription(label: str = "Transcription", content: str = "Contenu de la transcription...", id_prefix: str = "transcription") -> str:
    """Génère un bloc de transcription DSFR. `id_prefix` garantit l'unicité des
    IDs si plusieurs transcriptions cohabitent dans la même page."""
    id_prefix = _slug(id_prefix, "transcription")
    tid = f"{id_prefix}-1"
    modal_id = f"fr-transcription-modal-{tid}"
    # Exemple officiel transcription 1.15.2 : le bouton « Agrandir » ouvre une
    # modale plein écran qui reprend le titre et le contenu.
    return f"""<div class="fr-transcription">
    <button type="button" class="fr-transcription__btn" aria-expanded="false" aria-controls="{tid}">
        {esc(label)}
    </button>
    <div class="fr-collapse" id="{tid}">
        <div class="fr-transcription__footer">
            <div class="fr-transcription__actions-group">
                <button type="button" class="fr-btn--fullscreen fr-btn" aria-controls="{modal_id}" aria-label="Agrandir la transcription" data-fr-opened="false">
                    Agrandir
                </button>
            </div>
        </div>
        <div id="{modal_id}" class="fr-modal" aria-labelledby="{modal_id}-title">
            <div class="fr-container fr-container--fluid fr-container-md">
                <div class="fr-grid-row fr-grid-row--center">
                    <div class="fr-col-12 fr-col-md-10 fr-col-lg-8">
                        <div class="fr-modal__body">
                            <div class="fr-modal__header">
                                <button type="button" class="fr-btn--close fr-btn" aria-controls="{modal_id}" title="Fermer">Fermer</button>
                            </div>
                            <div class="fr-modal__content">
                                <h2 id="{modal_id}-title" class="fr-modal__title">{esc(label)}</h2>
                                <p>{esc(content)}</p>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
        <div class="fr-transcription__content">
            <p>{esc(content)}</p>
        </div>
    </div>
</div>"""


def generate_password(label: str = "Mot de passe", id: str = "password-input",
                      name: str = "password", autocomplete: str = "current-password",
                      new: bool = False) -> str:
    """Génère un champ de mot de passe DSFR (champ masqué, neutre au repos)"""
    show_id = f"{id}-show"
    autocomplete = "new-password" if new else autocomplete
    # Exemple officiel password 1.15.2 : le groupe de messages porte un id et
    # l'input le référence par aria-describedby (vide au repos sans `new`).
    messages_id = f"{id}-messages"
    if new:
        messages = f"""
        <div class="fr-messages-group" id="{esc(messages_id)}" aria-live="polite">
            <p class="fr-message">Votre mot de passe doit contenir :</p>
            <p class="fr-message fr-message--info">12 caractères minimum</p>
            <p class="fr-message fr-message--info">1 majuscule et 1 minuscule</p>
            <p class="fr-message fr-message--info">1 chiffre</p>
        </div>"""
    else:
        messages = f"""
        <div class="fr-messages-group" id="{esc(messages_id)}" aria-live="polite"></div>"""
    return f"""<div class="fr-password" id="password">
    <label class="fr-password__label fr-label" for="{esc(id)}">{esc(label)}
    </label>
    <div class="fr-input-wrap">
        <input class="fr-password__input fr-input" type="password" id="{esc(id)}" name="{esc(name)}" autocomplete="{esc(autocomplete)}" aria-describedby="{esc(messages_id)}">
    </div>{messages}
    <div class="fr-password__checkbox fr-checkbox-group fr-checkbox-group--sm">
        <input type="checkbox" id="{esc(show_id)}" aria-label="Afficher le mot de passe">
        <label class="fr-label" for="{esc(show_id)}">Afficher</label>
    </div>
</div>"""


def generate_table(caption: str = "", headers: list | None = None, rows: list | None = None,
                   bordered: bool = False) -> str:
    """Génère un tableau DSFR"""
    headers = headers or ["Colonne 1", "Colonne 2"]
    rows = rows or [["Donnée 1", "Donnée 2"]]
    modifier = " fr-table--bordered" if bordered else ""
    head = "".join(f"<th scope=\"col\">{esc(h)}</th>" for h in headers)
    if not isinstance(rows, list) or any(not isinstance(row, (list, tuple)) for row in rows):
        raise ValueError("rows : liste de lignes attendue, chaque ligne étant une liste de cellules")
    body = ""
    for row in rows:
        cells = "".join(f"<td>{esc(c)}</td>" for c in row)
        body += f"\n            <tr>{cells}</tr>"
    return f"""
<div class="fr-table{modifier}">
    <div class="fr-table__wrapper">
        <div class="fr-table__container">
            <div class="fr-table__content">
                <table>
                    <caption>{esc(caption) or 'Titre du tableau'}</caption>
                    <thead>
                        <tr>{head}</tr>
                    </thead>
                    <tbody>{body}
                    </tbody>
                </table>
            </div>
        </div>
    </div>
</div>"""


def generate_tab(tabs: list | None = None, label: str = "Onglets", id_prefix: str = "tabpanel") -> str:
    """Génère un système d'onglets DSFR. `id_prefix` garantit l'unicité des IDs
    si plusieurs systèmes d'onglets cohabitent dans la même page."""
    id_prefix = _slug(id_prefix, "tabpanel")
    tabs = tabs or [{"label": "Onglet 1", "content": "Contenu 1"}, {"label": "Onglet 2", "content": "Contenu 2"}]
    list_html = ""
    panels = ""
    first = True
    tabs = [_as_item(t) for t in tabs]
    explicit = any(t.get("selected") for t in tabs)
    for i, t in enumerate(tabs, 1):
        tab_id = f"{id_prefix}-{i}"
        selected = bool(t.get("selected")) if explicit else first
        selected_attr = "true" if selected else "false"
        tabindex = "0" if selected else "-1"
        panel_class = "fr-tabs__panel fr-tabs__panel--selected" if selected else "fr-tabs__panel"
        list_html += (f'\n        <li role="presentation">'
                      f'\n            <button type="button" id="{tab_id}" class="fr-tabs__tab" tabindex="{tabindex}"'
                      f' role="tab" aria-selected="{selected_attr}" aria-controls="{tab_id}-panel">'
                      f'{esc(t.get("label", f"Onglet {i}"))}</button>'
                      f'\n        </li>')
        content = render_rich_content(t.get("content", ""))
        panels += (f'\n    <div id="{tab_id}-panel" class="{panel_class}" role="tabpanel"'
                   f' aria-labelledby="{tab_id}" tabindex="0">\n        {content}\n    </div>')
        first = False
    return f"""
<div class="fr-tabs">
    <ul class="fr-tabs__list" role="tablist" aria-label="{esc(label)}">{list_html}
    </ul>{panels}
</div>"""


def generate_skiplinks(links: list | None = None) -> str:
    """Génère des liens d'évitement DSFR"""
    links = links or [
        {"label": "Contenu", "target": "#contenu"},
        {"label": "Menu", "target": "#navigation"},
        {"label": "Pied de page", "target": "#footer"},
    ]
    items = "".join(f'\n            <li><a class="fr-link" href="{esc_href(l.get("target", "/"))}">{esc(l.get("label", "Accès"))}</a></li>' for l in links)
    return f"""<div class="fr-skiplinks">
    <nav class="fr-container" role="navigation" aria-label="Accès rapide">
        <ul class="fr-skiplinks__list">{items}
        </ul>
    </nav>
</div>"""


def generate_sidemenu(title: str = "Titre menu", items: list | None = None,
                      label: str = "Menu latéral") -> str:
    """Génère un menu latéral DSFR"""
    items = items or [{"label": "Accueil", "href": "/", "active": True}, {"label": "Rubrique", "href": "/"}]
    rows = ""
    for i, it in enumerate(items, 1):
        it = _as_item(it)
        current = ' aria-current="page"' if it.get("active") else ""
        if it.get("children"):
            sub_id = f"sidemenu-sub-{i}"
            sub_items = "".join(f'\n                    <li class="fr-sidemenu__item"><a class="fr-sidemenu__link" href="{esc_href(c.get("href", "/"))}">{esc(c.get("label", ""))}</a></li>' for c in map(_as_item, it["children"]))
            rows += f'\n            <li class="fr-sidemenu__item">\n                <button type="button" class="fr-sidemenu__btn" aria-expanded="false" aria-controls="{sub_id}">{esc(it.get("label", f"Rubrique {i}"))}</button>\n                <div class="fr-collapse" id="{sub_id}">\n                    <ul class="fr-sidemenu__list">{sub_items}\n                    </ul>\n                </div>\n            </li>'
        else:
            rows += f'\n            <li class="fr-sidemenu__item">\n                <a class="fr-sidemenu__link" href="{esc_href(it.get("href", "/"))}"{current}>{esc(it.get("label", ""))}</a>\n            </li>'
    return f"""<nav class="fr-sidemenu" aria-label="{esc(label)}">
    <div class="fr-sidemenu__inner">
        <button type="button" class="fr-sidemenu__btn" aria-controls="fr-sidemenu-wrapper" aria-expanded="false">
            {esc(label)}
        </button>
        <div class="fr-collapse" id="fr-sidemenu-wrapper">
            <div class="fr-sidemenu__title">{esc(title)}</div>
            <ul class="fr-sidemenu__list">{rows}
            </ul>
        </div>
    </div>
</nav>"""


def generate_navigation(items: list | None = None, label: str = "Menu principal") -> str:
    """Génère une navigation principale DSFR"""
    items = items or [{"label": "Accueil", "href": "/", "active": True}, {"label": "Rubrique", "href": "/"}]
    rows = ""
    items = [_as_item(it) for it in items]
    for i, it in enumerate(items, 1):
        item_label = it.get("label", f"Rubrique {i}")
        current = ' aria-current="page"' if it.get("active") else ""
        item_cls = "fr-nav__item fr-nav__item--align-right" if it.get("align") == "right" else "fr-nav__item"
        if it.get("categories"):
            menu_id = f"nav-menu-{i}"
            cats = ""
            for cat in it["categories"]:
                cat_sub = ""
                for c in cat.get("items", []):
                    cat_sub += f'\n                            <li><a class="fr-nav__link" href="{esc_href(c.get("href", "/"))}" target="_self">{esc(c.get("label", ""))}</a></li>'
                cats += (f'\n                        <div class="fr-col-12 fr-col-lg-3">\n'
                         f'                            <h5 class="fr-mega-menu__category">\n'
                         f'                                <a class="fr-nav__link" href="{esc_href(cat.get("href", "/"))}" target="_self">{esc(cat.get("label", ""))}</a>\n'
                         f'                            </h5>\n'
                         f'                            <ul class="fr-mega-menu__list">{cat_sub}\n'
                         f'                            </ul>\n'
                         f'                        </div>')
            rows += (f'\n            <li class="{item_cls}">\n'
                     f'                <button type="button" class="fr-nav__btn" aria-expanded="false" aria-controls="{menu_id}">{esc(item_label)}</button>\n'
                     f'                <div class="fr-collapse fr-mega-menu" id="{menu_id}">\n'
                     f'                    <div class="fr-container fr-container--fluid fr-container-lg">\n'
                     f'                        <div class="fr-grid-row fr-grid-row-lg--gutters">\n'
                     f'                            <div class="fr-col-12 fr-mb-n3v">\n'
                     f'                                <button type="button" class="fr-btn--close fr-btn" aria-controls="{menu_id}" id="{menu_id}-close" title="Fermer">Fermer</button>\n'
                     f'                            </div>{cats}\n'
                     f'                        </div>\n'
                     f'                    </div>\n'
                     f'                </div>\n'
                     f'            </li>')
        elif it.get("children"):
            menu_id = f"nav-menu-{i}"
            sub_items = "".join(f'\n                        <li><a class="fr-nav__link" href="{esc_href(c.get("href", "/"))}" target="_self">{esc(c.get("label", ""))}</a></li>' for c in map(_as_item, it["children"]))
            rows += f'\n            <li class="{item_cls}">\n                <button type="button" class="fr-nav__btn" aria-expanded="false" aria-controls="{menu_id}">{esc(item_label)}</button>\n                <div class="fr-collapse fr-menu" id="{menu_id}">\n                    <ul class="fr-menu__list">{sub_items}\n                    </ul>\n                </div>\n            </li>'
        else:
            rows += f'\n            <li class="{item_cls}">\n                <a class="fr-nav__link" href="{esc_href(it.get("href", "/"))}" target="_self"{current}>{esc(item_label)}</a>\n            </li>'
    return f"""<nav class="fr-nav" id="navigation" role="navigation" aria-label="{esc(label)}">
    <ul class="fr-nav__list">{rows}
    </ul>
</nav>"""


def generate_header(brand_mode: str = "neutral", service_title: str = "Nom du service",
                    service_tagline: str = "Baseline - précisions sur l'organisation",
                    tools: list | None = None, languages: list | None = None,
                    search: dict | None = None, navigation: list | None = None,
                    translate_id: str = "header-translate-menu") -> str:
    """Génère un en-tête DSFR (sans bloc marque en mode neutral).

    Variantes riches (PRD-140), optionnelles et opt-in :
    - tools : liens d'accès rapide (fr-header__tools-links / fr-btns-group).
    - languages : sélecteur de langue (fr-translate) dans fr-header__tools-links.
    - search : barre de recherche (fr-header__navbar bouton fr-btn--search +
      fr-header__search fr-modal + fr-search-bar).
    - navigation : menu modale (fr-header__navbar bouton fr-btn--menu +
      fr-header__menu fr-modal contenant la navigation).
    Sources : paquet @gouvfr/dsfr@1.15.2 header.ejs / header-brand.ejs /
    header-navbar.ejs / header-menu.ejs / search.ejs, et header de
    generate_page.py comme référence locale validée.
    search et navigation exigent brand-top + fr-header__navbar, émis seulement
    quand l'un des deux est fourni. Sans tools, languages, search ni navigation,
    la sortie reste identique à l'en-tête minimal (baseline golden stable).
    """
    # `search: true` ou `{}` activent la barre avec ses valeurs par défaut ;
    # normalisé ici car `bool(search)` est testé plus bas (navbar, bouton loupe,
    # bloc outils) avant la construction de la barre elle-même.
    if search is True or (isinstance(search, dict) and not search):
        search = {"label": "Rechercher"}
    service_block = f"""                    <div class="fr-header__service">
                        <a href="/" title="Accueil - {esc(service_title)}">
                            <p class="fr-header__service-title">{esc(service_title)}</p>
                        </a>
                        <p class="fr-header__service-tagline">{esc(service_tagline)}</p>
                    </div>"""

    needs_navbar = bool(search or navigation)
    navbar_buttons = ""
    if search:
        navbar_buttons += '\n                                <button id="header-search-button" class="fr-btn--search fr-btn" data-fr-opened="false" aria-controls="header-search" title="Rechercher" type="button">Rechercher</button>'
    if navigation:
        navbar_buttons += '\n                                <button id="header-menu-button" class="fr-btn--menu fr-btn" data-fr-opened="false" aria-controls="header-menu" aria-haspopup="menu" title="Menu" type="button">Menu</button>'
    navbar_div = f'<div class="fr-header__navbar">{navbar_buttons}\n                            </div>' if needs_navbar else ""

    logo_block = ('                        <div class="fr-header__logo">\n'
                  '                            <p class="fr-logo">République<br>Française</p>\n'
                  '                        </div>')

    if brand_mode == "neutral":
        if needs_navbar:
            brand = (f'                <div class="fr-header__brand fr-enlarge-link">\n'
                     f'                    <div class="fr-header__brand-top">\n'
                     f'{navbar_div}\n'
                     f'                    </div>\n'
                     f'{service_block}\n'
                     f'                </div>')
        else:
            brand = f'                <div class="fr-header__brand fr-enlarge-link">\n{service_block}\n                </div>'
    else:
        if needs_navbar:
            brand = (f'                <div class="fr-header__brand fr-enlarge-link">\n'
                     f'                    <div class="fr-header__brand-top">\n'
                     f'{logo_block}\n'
                     f'{navbar_div}\n'
                     f'                    </div>\n'
                     f'{service_block}\n'
                     f'                </div>')
        else:
            brand = (f'                <div class="fr-header__brand fr-enlarge-link">\n'
                     f'                    <div class="fr-header__brand-top">\n'
                     f'{logo_block}\n'
                     f'                    </div>\n'
                     f'{service_block}\n'
                     f'                </div>')

    tools = tools or []
    languages = languages or []
    tools_html = ""
    if tools or languages or search:
        inner = ""
        if tools:
            if len(tools) == 1:
                t = tools[0]
                inner += f'\n                <a class="fr-btn fr-btn--tertiary"{_link_attrs(str(t.get("label", "")), t.get("target"), t.get("rel"), t.get("title"))} href="{esc_href(t.get("href", "/"))}">{esc(t.get("label", ""))}</a>'
            else:
                inner += '\n                <ul class="fr-btns-group">'
                for t in tools:
                    inner += f'\n                    <li><a class="fr-btn fr-btn--tertiary"{_link_attrs(str(t.get("label", "")), t.get("target"), t.get("rel"), t.get("title"))} href="{esc_href(t.get("href", "/"))}">{esc(t.get("label", ""))}</a></li>'
                inner += '\n                </ul>'
        if languages:
            active = next((l for l in languages if l.get("active")), languages[0])
            btn_label = f'{esc(str(active.get("code", "FR")).upper())}<span class="fr-hidden-lg">&nbsp;- {esc(active.get("label") or active.get("name", ""))}</span>'
            # Distinct du défaut de generate_translate (translate-menu) : un
            # en-tête et un sélecteur de langue autonome peuvent coexister.
            collapse_id = _slug(str(translate_id), "header-translate-menu")
            lang_items = ""
            for l in languages:
                cur = ' aria-current="true"' if l.get("active") else ""
                l_code = str(l.get("code", "")).lower()
                lang_items += (f'\n                            <li><a class="fr-translate__language fr-nav__link" hreflang="{esc(l_code)}" lang="{esc(l_code)}" href="{esc_href(l.get("href", "/"))}"{cur}>'
                               f'{esc(l_code.upper())}<span class="fr-hidden-lg">&nbsp;- {esc(l.get("label") or l.get("name", ""))}</span></a></li>')
            inner += (f'\n                <div class="fr-translate fr-nav">\n'
                      f'                    <div class="fr-nav__item">\n'
                      f'                        <button type="button" class="fr-btn--tertiary fr-translate__btn fr-btn" aria-controls="{collapse_id}" aria-expanded="false" title="Sélectionner une langue">{btn_label}</button>\n'
                      f'                        <div class="fr-collapse fr-translate__menu fr-menu" id="{collapse_id}">\n'
                      f'                            <ul class="fr-menu__list">{lang_items}\n'
                      f'                            </ul>\n'
                      f'                        </div>\n'
                      f'                    </div>\n'
                      f'                </div>')

        tools_links_html = ""
        if inner:
            tools_links_html = f'\n                <div class="fr-header__tools-links">{inner}\n                </div>'

        search_html = ""
        if search:
            label = esc(search.get("label", "Rechercher"))
            # DSFR 1.15.0 (#1432) : le bouton est `type="submit"` et la barre vit
            # dans un `<form>` pour fonctionner sans JavaScript.
            action = esc_href(search.get("action", "/recherche"))
            search_html = (f'\n                <div class="fr-header__search fr-modal" id="header-search" aria-labelledby="header-search-button">\n'
                           f'                    <div class="fr-container fr-container-lg--fluid">\n'
                           f'                        <button class="fr-btn--close fr-btn" aria-controls="header-search" title="Fermer" type="button">\n'
                           f'                            Fermer\n'
                           f'                        </button>\n'
                           f'                        <form action="{action}" method="get">\n'
                           f'                            <div class="fr-search-bar" id="header-search-bar" role="search">\n'
                           f'                                <label class="fr-label" for="header-search-input">\n'
                           f'                                    {label}\n'
                           f'                                </label>\n'
                           f'                                <input class="fr-input" type="search" id="header-search-input" name="search">\n'
                           f'                                <button type="submit" class="fr-btn" title="{label}">\n'
                           f'                                    {label}\n'
                           f'                                </button>\n'
                           f'                            </div>\n'
                           f'                        </form>\n'
                           f'                    </div>\n'
                           f'                </div>')

        tools_html = f'\n            <div class="fr-header__tools">{tools_links_html}{search_html}\n            </div>'

    menu_modal = ""
    if navigation:
        nav_html = generate_navigation(items=navigation, label="Menu principal")
        menu_modal = (f'\n        <div class="fr-header__menu fr-modal" id="header-menu" aria-labelledby="header-menu-button">\n'
                      f'            <div class="fr-container">\n'
                      f'                <button class="fr-btn--close fr-btn" aria-controls="header-menu" title="Fermer" type="button">\n'
                      f'                    Fermer\n'
                      f'                </button>\n'
                      f'                <div class="fr-header__menu-links"></div>\n'
                      f'                {nav_html}\n'
                      f'            </div>\n'
                      f'        </div>')

    return f"""<header role="banner" class="fr-header">
    <div class="fr-header__body">
        <div class="fr-container">
            <div class="fr-header__body-row">
{brand}{tools_html}
            </div>
        </div>
    </div>{menu_modal}
</header>"""


def generate_footer(brand_mode: str = "neutral", service_name: str = "Nom du service",
                    content_desc: str = "Description du service et informations complémentaires.",
                    content_links: list | None = None, partners: dict | None = None,
                    bottom_links: list | None = None, copyright: str | None = None) -> str:
    """Génère un pied de page DSFR.

    Variantes riches (P2 PRD-140), optionnelles et opt-in :
    - partners : bloc fr-footer__partners (titre, partenaire principal, sous-partenaires).
    - bottom_links + copyright : bloc fr-footer__bottom (liens légaux + copyright).
    Sources : paquet @gouvfr/dsfr@1.15.2 footer.ejs / footer-partners.ejs / footer-bottom.ejs.
    Sans ces paramètres, la sortie reste identique au footer minimal (baseline golden stable).
    """
    if brand_mode == "neutral":
        brand = f'            <div class="fr-footer__brand">\n                <p>{esc(service_name)}</p>\n            </div>'
    else:
        brand = (f'            <div class="fr-footer__brand fr-enlarge-link">\n'
                 f'                <a href="/" title="Retour à l\'accueil">\n'
                 f'                    <p class="fr-logo">République<br>Française</p>\n                </a>\n            </div>')

    if content_links is None:
        content_links = [
            {"label": "info.gouv.fr", "href": "https://info.gouv.fr"},
            {"label": "service-public.gouv.fr", "href": "https://service-public.gouv.fr"},
            {"label": "legifrance.gouv.fr", "href": "https://legifrance.gouv.fr"},
            {"label": "data.gouv.fr", "href": "https://data.gouv.fr"},
        ]

    content_links_html = ""
    if content_links:
        rows = ""
        for link in content_links:
            href = _safe_href(link.get("href", "/"))
            label = link.get("label", href)
            # Lien absolu : nouvelle fenêtre par défaut, annoncée et `external`
            # comme le pied de page officiel ; l'appelant peut forcer target.
            target = link.get("target", "_blank" if href.startswith("http") else None)
            rel = link.get("rel", "noopener external" if href.startswith("http") and "target" not in link else None)
            rows += (
                f'\n                    <li class="fr-footer__content-item">'
                f'<a class="fr-footer__content-link"{_link_attrs(str(label), target, rel, link.get("title"))} href="{esc_href(href)}">{esc(label)}</a></li>'
            )
        content_links_html = f'\n                <ul class="fr-footer__content-list">{rows}\n                </ul>'

    def _partner_link(p: dict) -> str:
        if not str(p.get("alt", "")).strip():
            raise ValueError("partners : alt obligatoire pour chaque logo (nom du partenaire, seul nom accessible du lien)")
        title_attr = f' title="{esc(p["title"])}"' if p.get("title") else ""
        return (f'<a class="fr-footer__partners-link"{title_attr} href="{esc_href(p.get("href", "/"))}">'
                f'<img class="fr-footer__logo fr-responsive-img" src="{esc_src(p.get("src"), "partners src")}" alt="{esc(p.get("alt", ""))}" /></a>')

    partners_html = ""
    if partners:
        title = esc(partners.get("title", "Partenaires"))
        main = partners.get("main_partner")
        subs = partners.get("sub_partners") or []
        partners_html = (f'\n            <div class="fr-footer__partners">\n'
                         f'                <h2 class="fr-footer__partners-title">{title}</h2>\n'
                         f'                <div class="fr-footer__partners-logos">')
        if main:
            partners_html += f'\n                    <div class="fr-footer__partners-main">\n                        {_partner_link(main)}\n                    </div>'
        if subs:
            partners_html += '\n                    <div class="fr-footer__partners-sub">\n                        <ul>'
            for sp in subs:
                partners_html += f'\n                            <li>{_partner_link(sp)}</li>'
            partners_html += '\n                        </ul>\n                    </div>'
        partners_html += '\n                </div>\n            </div>'

    bottom_html = ""
    if bottom_links or copyright:
        bottom_html = '\n            <div class="fr-footer__bottom">'
        if bottom_links:
            bottom_html += '\n                <ul class="fr-footer__bottom-list">'
            for bl in bottom_links:
                bottom_html += f'\n                    <li class="fr-footer__bottom-item">\n                        <a class="fr-footer__bottom-link" href="{esc_href(bl.get("href", "/"))}">{esc(bl.get("label", ""))}</a>\n                    </li>'
            bottom_html += '\n                </ul>'
        if copyright:
            bottom_html += f'\n                <div class="fr-footer__bottom-copy">\n                    <p>{esc(copyright)}</p>\n                </div>'
        bottom_html += '\n            </div>'

    return f"""<footer class="fr-footer" role="contentinfo" id="footer">
    <div class="fr-container">
        <div class="fr-footer__body">
{brand}
            <div class="fr-footer__content">
                <p class="fr-footer__content-desc">{esc(content_desc)}</p>{content_links_html}
            </div>
        </div>{partners_html}{bottom_html}
    </div>
</footer>"""


def generate_form(action: str = "/submit", method: str = "post", title: str = "Formulaire",
                  fields: list | None = None, submit_label: str = "Envoyer",
                  reset_label: str | None = None) -> str:
    """Génère un formulaire DSFR (champs neutres au repos)"""
    fields = fields or [{"label": "Nom", "type": "text"}, {"label": "Email", "type": "email"}]
    fields_html = ""
    seen_ids: set = set()
    for i, field in enumerate(fields, 1):
        field = _as_item(field)
        flabel = field.get("label", f"Champ {i}")
        fid = field.get("id") or _slug(flabel, f"field-{i}")
        if not field.get("id"):
            base, n = fid, 1
            while fid in seen_ids:
                n += 1
                fid = f"{base}-{n}"
        elif fid in seen_ids:
            raise ValueError(f"id de champ dupliqué : {fid}")
        seen_ids.add(fid)
        ftype = field.get("type", "text")
        fname = field.get("name", fid)
        hint = field.get("hint")
        hint_html = f'\n                                <span class="fr-hint-text">{esc(hint)}</span>' if hint else ""
        if ftype == "textarea":
            fields_html += f'\n                            <div class="fr-input-group">\n                                <label class="fr-label" for="{esc(fid)}">{esc(flabel)}{hint_html}\n                                </label>\n                                <textarea class="fr-input" id="{esc(fid)}" name="{esc(fname)}" rows="5"></textarea>\n                            </div>'
        elif ftype == "select":
            opts = "".join(f'\n                                    <option value="{esc(o.get("value", ""))}">{esc(o.get("label", ""))}</option>' for o in field.get("options", []))
            fields_html += f'\n                            <div class="fr-select-group">\n                                <label class="fr-label" for="{esc(fid)}">{esc(flabel)}{hint_html}\n                                </label>\n                                <select class="fr-select" id="{esc(fid)}" name="{esc(fname)}">\n                                    <option value="" selected disabled>Sélectionnez</option>{opts}\n                                </select>\n                            </div>'
        elif ftype == "checkbox":
            fields_html += f'\n                            <div class="fr-checkbox-group">\n                                <input type="checkbox" id="{esc(fid)}" name="{esc(fname)}">\n                                <label class="fr-label" for="{esc(fid)}">{esc(flabel)}</label>\n                            </div>'
        else:
            fields_html += f'\n                            <div class="fr-input-group">\n                                <label class="fr-label" for="{esc(fid)}">{esc(flabel)}{hint_html}\n                                </label>\n                                <input class="fr-input" type="{esc(ftype)}" id="{esc(fid)}" name="{esc(fname)}">\n                            </div>'
    reset_html = f'\n                            <button class="fr-btn fr-btn--secondary" type="reset">{esc(reset_label)}</button>' if reset_label else ""
    return f"""<form action="{esc_href(action)}" method="{esc(method)}" novalidate>
    <fieldset class="fr-fieldset">
        <legend class="fr-fieldset__legend">
            <h2>{esc(title)}</h2>
        </legend>
        <div class="fr-fieldset__content">{fields_html}
            <div class="fr-btns-group">
                <button class="fr-btn" type="submit">{esc(submit_label)}</button>{reset_html}
            </div>
        </div>
    </fieldset>
</form>"""


def generate_follow(newsletter_title: str = "Abonnez-vous à notre lettre d'information",
                    newsletter_url: str | None = None,
                    newsletter_desc: str = "Description de la newsletter",
                    socials: list | None = None, id: str | None = None) -> str:
    """Génère un bloc de suivi (newsletter + réseaux) DSFR"""
    if socials is None:
        socials = [{"platform": "facebook", "label": "Facebook"}, {"platform": "twitter-x", "label": "X (anciennement Twitter)"}, {"platform": "linkedin", "label": "LinkedIn"}]
    social_label_map = {
        "twitter": ("twitter-x", "X (anciennement Twitter)"),
        "twitter-x": ("twitter-x", "X (anciennement Twitter)"),
    }
    social_items = ""
    for s in socials:
        s = _as_item(s, "platform")
        platform = s.get("platform", "")
        platform, default_label = social_label_map.get(platform, (platform, s.get("label", "")))
        label = s.get("label") or default_label
        href = s.get("href", "/")
        title = s.get("title") or f"Suivez-nous sur {label} - nouvelle fenêtre"
        social_items += f'\n                        <li>\n                            <a class="fr-btn--{esc(platform)} fr-btn" href="{esc_href(href)}" target="_blank" rel="noopener external" title="{esc(title)}">{esc(label)}</a>\n                        </li>'
    id_attr = f' id="{esc(id)}"' if id else ""
    # Sans URL, le bouton officiel (ouverture d'un formulaire par le projet) ; avec
    # newsletter_url, un lien d'abonnement réel (assembly.md, schéma safeHref).
    if newsletter_url:
        subscribe_html = f'<a class="fr-btn" href="{esc_href(newsletter_url)}" title="S\'abonner à notre lettre d\'information">S\'abonner</a>'
    else:
        subscribe_html = '<button class="fr-btn" type="button" title="S\'abonner à notre lettre d\'information">S\'abonner</button>'
    return f"""<div class="fr-follow"{id_attr}>
    <div class="fr-container">
        <div class="fr-grid-row">
            <div class="fr-col-12 fr-col-md-8">
                <div class="fr-follow__newsletter">
                    <div>
                        <h2 class="fr-h5">{esc(newsletter_title)}</h2>
                        <p class="fr-text--sm">{esc(newsletter_desc)}</p>
                    </div>
                    <div>
                        {subscribe_html}
                    </div>
                </div>
            </div>
            <div class="fr-col-12 fr-col-md-4">
                <div class="fr-follow__social">
                    <h2 class="fr-h5">Suivez-nous sur les réseaux sociaux</h2>
                    <ul class="fr-btns-group">{social_items}
                    </ul>
                </div>
            </div>
        </div>
    </div>
</div>"""


def generate_consent(site_name: str = "nomdusite.gouv.fr", id_prefix: str = "consent") -> str:
    """Génère un bandeau de consentement cookies DSFR"""
    modal_id = f"{_slug(id_prefix, 'consent')}-modal"
    title_id = f"{modal_id}-title"
    return f"""<div class="fr-consent-banner">
    <h2 class="fr-h6">À propos des cookies sur {esc(site_name)}</h2>
    <div class="fr-consent-banner__content">
        <p class="fr-text--sm">Bienvenue ! Nous utilisons des cookies pour améliorer votre expérience et les services disponibles sur ce site.</p>
    </div>
    <ul class="fr-consent-banner__buttons fr-btns-group fr-btns-group--right fr-btns-group--inline-reverse fr-btns-group--inline-sm">
        <li><button type="button" class="fr-btn" title="Autoriser tous les cookies">Tout accepter</button></li>
        <li><button type="button" class="fr-btn" title="Refuser tous les cookies">Tout refuser</button></li>
        <li><button type="button" class="fr-btn fr-btn--secondary" data-fr-opened="false" aria-controls="{esc(modal_id)}" title="Personnaliser les cookies">Personnaliser</button></li>
    </ul>
</div>
<dialog id="{esc(modal_id)}" class="fr-modal" aria-labelledby="{esc(title_id)}">
    <div class="fr-container fr-container--fluid fr-container-md">
        <div class="fr-grid-row fr-grid-row--center">
            <div class="fr-col-12 fr-col-md-8">
                <div class="fr-modal__body">
                    <div class="fr-modal__header">
                        <button type="button" class="fr-btn--close fr-btn" aria-controls="{esc(modal_id)}" title="Fermer">Fermer</button>
                    </div>
                    <div class="fr-modal__content">
                        <h2 id="{esc(title_id)}" class="fr-modal__title">Personnalisation des cookies</h2>
                        <p class="fr-text--sm">Ajoutez ici la gestion détaillée des finalités de cookies.</p>
                    </div>
                </div>
            </div>
        </div>
    </div>
</dialog>"""


def generate_display() -> str:
    """Génère le bouton et la modale des paramètres d'affichage DSFR"""
    return """<button aria-controls="fr-theme-modal" data-fr-opened="false" title="Paramètres d'affichage" type="button" class="fr-btn--display fr-btn">
    Paramètres d'affichage
</button>
<dialog id="fr-theme-modal" class="fr-modal" aria-labelledby="fr-theme-modal-title">
    <div class="fr-container fr-container--fluid fr-container-md">
        <div class="fr-grid-row fr-grid-row--center">
            <div class="fr-col-12 fr-col-md-6 fr-col-lg-4">
                <div class="fr-modal__body">
                    <div class="fr-modal__header">
                        <button aria-controls="fr-theme-modal" title="Fermer" type="button" class="fr-btn--close fr-btn">Fermer</button>
                    </div>
                    <div class="fr-modal__content">
                        <h2 id="fr-theme-modal-title" class="fr-modal__title">Paramètres d'affichage</h2>
                        <div id="fr-display" class="fr-display">
                            <fieldset class="fr-fieldset" id="display-fieldset">
                                <legend class="fr-fieldset__legend fr-fieldset__legend--regular" id="display-fieldset-legend">
                                    Choisissez un thème pour personnaliser l'apparence du site.
                                </legend>
                                <div class="fr-fieldset__element">
                                    <div class="fr-radio-group">
                                        <input value="light" type="radio" id="fr-radios-theme-light" name="fr-radios-theme">
                                        <label class="fr-label" for="fr-radios-theme-light">Thème clair</label>
                                    </div>
                                </div>
                                <div class="fr-fieldset__element">
                                    <div class="fr-radio-group">
                                        <input value="dark" type="radio" id="fr-radios-theme-dark" name="fr-radios-theme">
                                        <label class="fr-label" for="fr-radios-theme-dark">Thème sombre</label>
                                    </div>
                                </div>
                                <div class="fr-fieldset__element">
                                    <div class="fr-radio-group">
                                        <input value="system" type="radio" id="fr-radios-theme-system" name="fr-radios-theme">
                                        <label class="fr-label" for="fr-radios-theme-system">Système</label>
                                    </div>
                                </div>
                            </fieldset>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
</dialog>"""


# === Générateurs natifs : dispatch ===

NATIVE_COMPONENTS = {
    "button": lambda config: generate_button(**config),
    "alert": lambda config: generate_alert(**config),
    "accordion": lambda config: generate_accordion(config.get("items", []), **{k: v for k, v in config.items() if k != "items"}),
    "card": lambda config: generate_card(**config),
    "modal": lambda config: generate_modal(**config),
    "input": lambda config: generate_form_input(config.get("label", "Label"), **{k: v for k, v in config.items() if k != "label"}),
    "breadcrumb": lambda config: generate_breadcrumb(config.get("items", []), **{k: v for k, v in config.items() if k != "items"}),
    "badge": lambda config: generate_badge(**config),
    "tag": lambda config: generate_tag(**config),
    "callout": lambda config: generate_callout(**config),
    "highlight": lambda config: generate_highlight(**config),
    "notice": lambda config: generate_notice(**config),
    "link": lambda config: generate_link(**config),
    "select": lambda config: generate_select(options=config.get("options"), **{k: v for k, v in config.items() if k != "options"}),
    "checkbox": lambda config: generate_checkbox(items=config.get("items"), **{k: v for k, v in config.items() if k != "items"}),
    "radio": lambda config: generate_radio(items=config.get("items"), **{k: v for k, v in config.items() if k != "items"}),
    "toggle": lambda config: generate_toggle(**config),
    "search": lambda config: generate_search(**config),
    "range": lambda config: generate_range(**config),
    "upload": lambda config: generate_upload(**config),
    "stepper": lambda config: generate_stepper(**config),
    "pagination": lambda config: generate_pagination(**config),
    "tile": lambda config: generate_tile(**config),
    "quote": lambda config: generate_quote(**config),
    "tooltip": lambda config: generate_tooltip(**config),
    "segmented": lambda config: generate_segmented(items=config.get("items"), **{k: v for k, v in config.items() if k != "items"}),
    "logo": lambda config: generate_logo(**config),
    "connect": lambda config: generate_connect(**config),
    "download": lambda config: generate_download(**config),
    "content": lambda config: generate_content(**config),
    "summary": lambda config: generate_summary(**config),
    "share": lambda config: generate_share(**config),
    "translate": lambda config: generate_translate(**config),
    "transcription": lambda config: generate_transcription(**config),
    "password": lambda config: generate_password(**config),
    "table": lambda config: generate_table(**config),
    "tabs": lambda config: generate_tab(**config),
    "skiplinks": lambda config: generate_skiplinks(**config),
    "sidemenu": lambda config: generate_sidemenu(**config),
    "navigation": lambda config: generate_navigation(**config),
    "header": lambda config: generate_header(**config),
    "footer": lambda config: generate_footer(**config),
    "form": lambda config: generate_form(**config),
    "follow": lambda config: generate_follow(**config),
    "consent": lambda config: generate_consent(**config),
    "display": lambda config: generate_display(**config),
}


def main():
    library = load_library()
    all_components = sorted(set(
        list(NATIVE_COMPONENTS.keys()) +
        list(library.get("components", {}).keys()) +
        list(registry.input_aliases())
    ))

    parser = argparse.ArgumentParser(
        description=f"Générateur de fragments DSFR alignés avec limites ({len(library.get('components', {}))} composants via bibliothèque JSON + {len(NATIVE_COMPONENTS)} natifs paramétrables)")
    parser.add_argument("component", nargs="?", help="Composant à générer", choices=all_components + ["list"])
    parser.add_argument("--variant", help="Variante du composant (pour le mode bibliothèque)")
    parser.add_argument("--config", help="Configuration JSON (pour les composants natifs)", type=str)
    parser.add_argument("--output", help="Fichier de sortie ; refuse d'écraser un fichier existant")
    parser.add_argument("--list", action="store_true", help="Lister tous les composants disponibles")

    args = parser.parse_args()

    if args.list or args.component == "list":
        if not library:
            print(f"Avertissement : bibliothèque JSON introuvable ({LIBRARY_PATH}), mode --variant indisponible", file=sys.stderr)
        list_components(library)
        return

    if not args.component:
        # Aucune cible : usage invalide, aide sur stderr, code 2 (comme generate_field).
        parser.print_help(sys.stderr)
        sys.exit(2)
        return

    config = {}
    if args.config:
        try:
            config = json.loads(args.config)
        except json.JSONDecodeError as e:
            print(f"Erreur : JSON invalide dans --config : {e}", file=sys.stderr)
            sys.exit(1)
        if not isinstance(config, dict):
            print("Erreur : --config doit être un objet JSON (dictionnaire de paramètres)", file=sys.stderr)
            sys.exit(1)
    if args.variant and args.config:
        print("Erreur : --config et --variant ne se combinent pas : --variant rend une variante figée de la bibliothèque, --config paramètre le générateur natif", file=sys.stderr)
        sys.exit(1)

    # Renommer les clés pour éviter les conflits avec les builtins Python
    if "type" in config and args.component == "alert":
        config["alert_type"] = config.pop("type")
    if "type" in config and args.component == "input":
        config["input_type"] = config.pop("type")
    if "type" in config and args.component == "notice":
        config["variant"] = config.pop("type")

    # Normaliser les alias (tab→tabs, skiplink→skiplinks) pour le dispatch natif
    component = registry.canonical_name(args.component)

    # Priorité : natif (paramétrable) > bibliothèque JSON
    html = ""
    if component in NATIVE_COMPONENTS and not args.variant:
        try:
            html = normalize_generated_html(NATIVE_COMPONENTS[component](config))
        except (TypeError, ValueError, KeyError, AttributeError, IndexError) as e:
            print(f"Erreur : paramètre invalide pour '{args.component}' : {e}", file=sys.stderr)
            sys.exit(1)
    elif library:
        if args.config and not args.variant:
            print(f"Avertissement : '{args.component}' n'existe qu'en variante de bibliothèque ; --config est sans effet.", file=sys.stderr)
        html = generate_from_library(library, args.component, args.variant)
    elif component in NATIVE_COMPONENTS:
        print(f"Erreur : bibliothèque JSON introuvable ({LIBRARY_PATH}) : la variante figée --variant est indisponible ; retirer --variant pour la génération native de '{args.component}'.", file=sys.stderr)
        sys.exit(1)
    else:
        print(f"Erreur : composant '{args.component}' non disponible en mode natif et bibliothèque JSON introuvable.", file=sys.stderr)
        print(f"Vérifiez que {LIBRARY_PATH} existe.", file=sys.stderr)
        sys.exit(1)

    if args.output:
        write_output(html, args.output, "Composant généré")
    else:
        print(html)


if __name__ == "__main__":
    main()
