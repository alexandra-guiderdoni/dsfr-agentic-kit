#!/usr/bin/env python3
"""
Générateur d'atomes DSFR (DSFR 1.15.2).

Atomes = primitives sous le niveau composant :
- typographie : title, text, lead, bold
- icône : icon
- layout : container, grid (grille), col (colonnage), spacing (espacements)
- illustration : pictogram (pointer-only, l'art SVG relève du skill
  séparé generer-pictos-svg-dsfr)
- couleur : color (utilitaire couleur DSFR : fr-background-* / fr-text-*)

Aligné avec le Design System de l'État français, sans revendiquer une
conformité sans audit dédié. Le composant officiel correspondant reste
généré par generate_component.py ; ce script ne génère que des atomes.
"""

import argparse
import json
import os
import re
import sys
from html import escape

sys.dont_write_bytecode = True
from generate_component import esc_href, write_output  # noqa: E402


def esc(text) -> str:
    """Échappe le HTML (préserve 0 et False)."""
    if text is None:
        return ""
    return escape(str(text))


def _int_in_range(value, name: str, low: int, high: int) -> int:
    """Entier borné : les classes DSFR n'existent que pour ces valeurs."""
    if isinstance(value, bool):
        raise ValueError(f"{name} doit être un entier entre {low} et {high}")
    try:
        number = int(value)
    except (TypeError, ValueError):
        raise ValueError(f"{name} doit être un entier entre {low} et {high}") from None
    if not low <= number <= high:
        raise ValueError(f"{name} doit être entre {low} et {high} (reçu {number})")
    return number


def _choice(value, name: str, allowed) -> str:
    """Valeur d'une liste blanche : toute autre chaîne produirait une classe inventée."""
    if value not in allowed:
        raise ValueError(f"{name} '{value}' inconnu : utiliser {', '.join(sorted(str(a) for a in allowed))}")
    return value


TITLE_DISPLAYS = ("xs", "sm", "md", "lg", "xl")
TEXT_SIZES = ("xs", "sm", "md", "lg", "xl", "lead", "alt", "light", "regular", "heavy", "bold")
ICON_NAME_RE = re.compile(r"^[a-z0-9][a-z0-9-]*$")
SPACING_DIRECTIONS = ("", "t", "b", "l", "r", "x", "y")
COLOR_TAGS = ("span", "div", "p")


def generate_title(level: int = 1, text: str = "Titre", display: str | None = None) -> str:
    """Génère un titre DSFR (h1-h6, option fr-display--{xs..xl})."""
    lvl = _int_in_range(level, "level", 1, 6)
    if display is not None:
        _choice(display, "display", TITLE_DISPLAYS)
    cls = f' class="fr-display--{display}"' if display else ""
    return f"<h{lvl}{cls}>{esc(text)}</h{lvl}>"


TEXT_TAGS = ("p", "span", "div")


def generate_text(text: str = "Texte", size: str | None = None, tag: str = "p") -> str:
    """Génère un bloc texte DSFR (taille utilitaire fr-text--*).

    `tag` vaut `p`, `span` ou `div` : la balise est validée, jamais échappée
    (un nom de balise échappé n'est pas un élément valide).
    """
    if tag not in TEXT_TAGS:
        raise ValueError(f"tag de texte '{tag}' inconnu : utiliser p, span ou div")
    if size is not None:
        _choice(size, "size", TEXT_SIZES)
    cls = f' class="fr-text--{size}"' if size else ""
    return f"<{tag}{cls}>{esc(text)}</{tag}>"


def generate_lead(text: str = "Texte d'introduction") -> str:
    """Génère un chapô (fr-text--lead)."""
    return generate_text(text=text, size="lead")


def generate_bold(text: str = "Texte en gras") -> str:
    """Génère un segment en gras."""
    return f"<strong>{esc(text)}</strong>"


def generate_icon(name: str = "information-line", size: str | None = None, title: str | None = None) -> str:
    """Génère une icône DSFR (fr-icon-{name}) ; avec `title`, une image nommée (role=img)."""
    if not ICON_NAME_RE.fullmatch(str(name or "")):
        raise ValueError(f"name '{name}' invalide : nom d'icône DSFR attendu (minuscules, chiffres, tirets)")
    classes = [f"fr-icon-{name}"]
    if size in ("sm", "lg"):
        classes.append(f"fr-icon--{size}")
    if title:
        return f'<span class="{" ".join(classes)}" role="img" aria-label="{esc(title)}"></span>'
    return f'<span class="{" ".join(classes)}" aria-hidden="true"></span>'


def generate_container(content: str = "", size: str | None = None, fluid: bool = False) -> str:
    """Génère un conteneur DSFR (fr-container[-{sm|md|lg|xl}][--fluid])."""
    base = "fr-container"
    if size in ("sm", "md", "lg", "xl"):
        base += f"-{size}"
    if fluid:
        base += "--fluid"
    return f'<div class="{base}">\n    {content}\n</div>'


def generate_col(content: str = "", span=None, sm=None, md=None, lg=None, offset=None,
                 tag: str = "div", offset_sm=None, offset_md=None, offset_lg=None, offset_xl=None) -> str:
    """Génère une colonne DSFR (fr-col, fr-col-N, fr-col-{sm|md|lg}-N, fr-col-offset-N,
    fr-col-offset-{sm|md|lg|xl}-N). `content` est inséré brut, comme pour les autres atomes.

    `tag` vaut `div` ou `li` : `li` sert aux grilles en forme de liste
    (DSFR 1.15.0).
    """
    if tag not in ("div", "li"):
        raise ValueError(f"tag de colonne '{tag}' inconnu : utiliser div ou li")
    classes = ["fr-col"]
    if span is not None:
        classes.append(f"fr-col-{_int_in_range(span, 'span', 1, 12)}")
    elif any(value is not None for value in (sm, md, lg)):
        # Sans largeur de base, la colonne s'empile en pleine largeur sous le
        # premier point de rupture déclaré (fr-col-md-6 ne vaut qu'à partir de 48em).
        classes.append("fr-col-12")
    if sm is not None:
        classes.append(f"fr-col-sm-{_int_in_range(sm, 'sm', 1, 12)}")
    if md is not None:
        classes.append(f"fr-col-md-{_int_in_range(md, 'md', 1, 12)}")
    if lg is not None:
        classes.append(f"fr-col-lg-{_int_in_range(lg, 'lg', 1, 12)}")
    if offset is not None:
        classes.append(f"fr-col-offset-{_int_in_range(offset, 'offset', 1, 11)}")
    for breakpoint, value in (("sm", offset_sm), ("md", offset_md), ("lg", offset_lg), ("xl", offset_xl)):
        if value is not None:
            classes.append(f"fr-col-offset-{breakpoint}-{_int_in_range(value, f'offset_{breakpoint}', 1, 11)}")
    return f'<{tag} class="{" ".join(classes)}">\n        {content}\n    </{tag}>'


def generate_grid(cols: list | None = None, gutters: bool = False,
                  align: str | None = None, justify: str | None = None,
                  tag: str = "div") -> str:
    """Génère une grille DSFR (fr-grid-row) contenant des colonnes.

    `tag` vaut `div`, `ul` ou `ol`. Depuis DSFR 1.15.0, `ul.fr-grid-row` et
    `ol.fr-grid-row` sont pris en charge : le style neutralise puces et
    compteurs (`core/style/grid/module/_row.scss`). Les colonnes deviennent
    alors des `li`.
    """
    if tag not in ("div", "ul", "ol"):
        raise ValueError(f"tag de grille '{tag}' inconnu : utiliser div, ul ou ol")
    # Seule l'absence (None) vaut démonstration : une liste vide donne une grille vide.
    if cols is None:
        cols = [{"content": "Colonne 1", "md": 6}, {"content": "Colonne 2", "md": 6}]
    if not isinstance(cols, list):
        raise ValueError("cols : liste de colonnes attendue")
    classes = ["fr-grid-row"]
    if gutters:
        classes.append("fr-grid-row--gutters")
    if align in ("top", "bottom", "middle"):
        classes.append(f"fr-grid-row--{align}")
    if justify in ("left", "center", "right"):
        classes.append(f"fr-grid-row--{justify}")
    cols_html = ""
    for c in cols:
        if not isinstance(c, dict):
            c = {"content": str(c)}
        cols_html += "\n        " + generate_col(**c, tag="li" if tag in ("ul", "ol") else "div")
    return f'<{tag} class="{" ".join(classes)}">{cols_html}\n    </{tag}>'


def generate_spacing(content: str = "", kind: str = "margin",
                     direction: str | None = None, size=4, unit: str = "w") -> str:
    """Génère un wrapper d'espacement DSFR (fr-m-*/fr-p-* avec unité w ou v)."""
    _choice(kind, "kind", ("margin", "padding"))
    prefix = "p" if kind == "padding" else "m"
    direction = _choice(direction or "", "direction", SPACING_DIRECTIONS)
    unit = _choice(unit, "unit", ("w", "v"))
    # Échelle du paquet 1.15.2 : v de 0 à 32, w de 0 à 16 (fr-mb-30w n'existe pas).
    size = _int_in_range(size, "size", 0, 32 if unit == "v" else 16)
    return f'<div class="fr-{prefix}{direction}-{size}{unit}">\n    {content}\n</div>'


def generate_pictogram(src: str | None = None, size=80) -> str:
    """Génère un pictogramme DSFR POINTER-ONLY (fr-artwork + 3 calques <use>).

    Référence un asset SVG officiel via <use href> ; ne génère jamais le SVG
    art inline (rôle du skill séparé generer-pictos-svg-dsfr). Le viewBox
    reste 0 0 80 80 (l'artboard officiel) ; `size` ne pilote que width/height.
    `src` doit être servi depuis la même origine que la page : un `<use href>`
    vers un domaine tiers n'est résolu par aucun navigateur moderne et donne un
    pictogramme vide, sans erreur. D'où le défaut en chemin absolu d'origine.
    Source : references/pictograms.md + paquet @gouvfr/dsfr@1.15.2.
    """
    src = src or "/dsfr/artwork/pictograms/digital/internet.svg"
    size = _int_in_range(size if size else 80, "size", 16, 512)
    return (f'<svg aria-hidden="true" class="fr-artwork" viewBox="0 0 80 80" width="{esc(size)}" height="{esc(size)}">\n'
            f'    <use class="fr-artwork-decorative" href="{esc_href(src)}#artwork-decorative"></use>\n'
            f'    <use class="fr-artwork-minor" href="{esc_href(src)}#artwork-minor"></use>\n'
            f'    <use class="fr-artwork-major" href="{esc_href(src)}#artwork-major"></use>\n'
            f'</svg>')


# Échelles de couleur réellement fournies par les utilitaires DSFR, relevées sur
# `dist/utility/utility.css` du paquet 1.15.2. Elles sont irrégulières : chaque
# couple rôle/variante a la sienne, et aucune règle simple ne les résume. Émettre
# une combinaison absente produirait un markup sans style et sans erreur.
# `red-marianne` n'y figure plus pour `background`, `text` et `border` depuis
# DSFR 1.15.0 ; il n'est pas traité comme une exception, il est simplement
# absent, au même titre que toute autre combinaison inexistante.
# `check_generated_outputs.py` compare cette table au paquet officiel.
ACCENT_COLORS = frozenset({
    "beige-gris-galet", "blue-cumulus", "blue-ecume", "blue-france",
    "brown-cafe-creme", "brown-caramel", "brown-opera", "green-archipel",
    "green-bourgeon", "green-emeraude", "green-menthe", "green-tilleul-verveine",
    "orange-terre-battue", "pink-macaron", "pink-tuile", "purple-glycine",
    "yellow-moutarde", "yellow-tournesol",
})
STATE_COLORS = frozenset({"error", "info", "success", "warning"})
PALETTE_COLORS = ACCENT_COLORS | {"grey"}
PALETTE_AND_STATE_COLORS = PALETTE_COLORS | STATE_COLORS

COLOR_KINDS = frozenset({"background", "text"})
UTILITY_COLOR_SCALES: dict[tuple[str, str], frozenset[str]] = {
    ("background", "action-high"): PALETTE_AND_STATE_COLORS,
    ("background", "action-low"): ACCENT_COLORS,
    ("background", "alt"): PALETTE_COLORS,
    ("background", "contrast"): PALETTE_AND_STATE_COLORS,
    ("background", "default"): frozenset({"grey"}),
    ("background", "flat"): PALETTE_AND_STATE_COLORS,
    ("text", "action-high"): PALETTE_COLORS,
    ("text", "default"): STATE_COLORS | {"grey"},
    ("text", "inverted"): PALETTE_AND_STATE_COLORS,
    ("text", "label"): PALETTE_COLORS,
    ("text", "mention"): frozenset({"grey"}),
    ("text", "title"): frozenset({"blue-france", "grey"}),
}


def generate_color(kind: str = "background", variant: str | None = None,
                   color: str = "blue-france", content: str = "Texte",
                   tag: str | None = None) -> str:
    """Génère un élément portant un utilitaire couleur DSFR 1.15.2.

    kind="background" -> fr-background-{variant}[--{color}] (variant par défaut
    "alt" ; variants officiels : alt, default, contrast, flat).
    kind="text" -> fr-text-{variant}[--{color}] (variant par défaut "action-high"
    qui accepte toute la palette, comme label ; inverted accepte la palette,
    grey et les états ; default n'accepte que {error, grey, info, success,
    warning} ; mention n'accepte que grey ; title n'accepte que blue-france
    et grey).
    `color` doit appartenir à l'échelle du couple rôle/variante : voir
    UTILITY_COLOR_SCALES, relevée sur le paquet. Sans `color`, seule la base
    sémantique est émise.
    Sources : dist/utility/utility.css du paquet @gouvfr/dsfr@1.15.2 (107
    classes background distinctes, 657 déclarations, + les classes text). Le check --official-version valide
    que la classe émise est officielle.
    """
    if kind not in COLOR_KINDS:
        raise ValueError(
            f"rôle '{kind}' inconnu : utiliser {' ou '.join(sorted(COLOR_KINDS))}"
        )
    if kind == "text":
        variant = variant or "action-high"
        element = tag or "span"
    else:
        variant = variant or "alt"
        element = tag or "div"
    if (kind, variant) not in UTILITY_COLOR_SCALES:
        raise ValueError(f"variant '{variant}' inconnu pour '{kind}' en DSFR 1.15.2")
    _choice(element, "tag", COLOR_TAGS)
    base = f"fr-text-{variant}" if kind == "text" else f"fr-background-{variant}"
    if color:
        scale = UTILITY_COLOR_SCALES.get((kind, variant))
        if scale is None or color not in scale:
            raise ValueError(
                f"couleur '{color}' indisponible pour '{base}' en DSFR 1.15.2"
            )
    cls = f"{base}--{esc(color)}" if color else base
    # `content` est inséré brut, même sémantique que container, col, spacing et grid.
    return f'<{element} class="{cls}">{content}</{element}>'


ATOMS = {
    "title": lambda config: generate_title(**config),
    "text": lambda config: generate_text(**config),
    "lead": lambda config: generate_lead(**config),
    "bold": lambda config: generate_bold(**config),
    "icon": lambda config: generate_icon(**config),
    "container": lambda config: generate_container(**config),
    "grid": lambda config: generate_grid(cols=config.get("cols"), **{k: v for k, v in config.items() if k != "cols"}),
    "col": lambda config: generate_col(**config),
    "spacing": lambda config: generate_spacing(**config),
    "pictogram": lambda config: generate_pictogram(**config),
    "color": lambda config: generate_color(**config),
}


def list_atoms() -> None:
    """Affiche les atomes disponibles."""
    print("Atomes (génération paramétrable) :")
    for name in sorted(ATOMS.keys()):
        print(f"  - {name}")


def main():
    parser = argparse.ArgumentParser(
        description=f"Générateur d'atomes DSFR ({len(ATOMS)} atomes : typographie, icône, container, grille, colonne, espacements, pictogram, couleur)")
    parser.add_argument("atom", nargs="?", help="Atome à générer", choices=list(ATOMS.keys()) + ["list"])
    parser.add_argument("--config", help="Configuration JSON de l'atome", type=str)
    parser.add_argument("--output", help="Fichier de sortie ; refuse d'écraser un fichier existant")
    parser.add_argument("--list", action="store_true", help="Lister les atomes disponibles")

    args = parser.parse_args()

    if args.list or args.atom == "list":
        list_atoms()
        return

    if not args.atom:
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

    try:
        html = ATOMS[args.atom](config)
    except (TypeError, ValueError, AttributeError) as e:
        print(f"Erreur : paramètre invalide pour '{args.atom}' : {e}", file=sys.stderr)
        sys.exit(1)

    if args.output is not None:
        write_output(html, args.output, "Atome généré")
    else:
        if hasattr(sys.stdout, "reconfigure"):
            sys.stdout.reconfigure(encoding="utf-8")
        print(html)


if __name__ == "__main__":
    main()
