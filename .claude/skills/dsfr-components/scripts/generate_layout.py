#!/usr/bin/env python3
"""
Générateur de gabarits DSFR (DSFR 1.15.3).

Gabarits = agencements structurels composant atomes et composants :
- skeleton  : charpente de page complète (head + assets DSFR + slots)
- sidebar   : mise en page 2 colonnes (menu latéral + contenu)
- columns   : grille générique de N colonnes
- card-grid : grille de cartes
- tile-grid : grille de tuiles

Distinct de generate_page.py (types de pages avec contenu spécifique) :
les gabarits produisent la structure, l'utilisateur y place son contenu.
"""

import argparse
import json
import os
import re
import sys
from html import escape

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.dont_write_bytecode = True
sys.path.insert(0, SCRIPT_DIR)
from generate_component import esc_href, write_output  # noqa: E402  # pyright: ignore[reportMissingImports]

BRAND_MODES = {"neutral", "republique"}
DSFR_VERSION_RE = re.compile(r"^\d+\.\d+\.\d+(?:[.-][0-9A-Za-z.]+)?$")


def _dsfr_version() -> str:
    raw = os.environ.get("DSFR_OFFICIAL_VERSION") or "1.15.3"
    if not DSFR_VERSION_RE.fullmatch(raw):
        raise SystemExit(f"Erreur : DSFR_OFFICIAL_VERSION invalide ({raw[:40]!r}) : numéro de version attendu, par exemple 1.15.3")
    return raw


DSFR_VERSION = _dsfr_version()
DSFR_BASE = f"https://cdn.jsdelivr.net/npm/@gouvfr/dsfr@{DSFR_VERSION}/dist"


def esc(text) -> str:
    """Échappe le HTML (préserve 0 et False)."""
    if text is None:
        return ""
    return escape(str(text))


def generate_skeleton(title: str = "Nom du service", brand_mode: str = "neutral") -> str:
    """Génère la charpente d'une page DSFR (frame avec slots à remplir)."""
    if brand_mode not in BRAND_MODES:
        raise ValueError(f"brand_mode '{brand_mode}' inconnu : utiliser neutral ou republique")
    if not str(title or "").strip():
        raise ValueError("title : titre obligatoire (il alimente <title> et le nom du lien de marque)")
    # Structure officielle 1.15.3 (header/_part/doc/code) : body-row et
    # brand-top obligatoires ; le slot de navigation porte l'id ciblé par le
    # lien d'évitement « Menu ».
    nav_slot = ('        <div class="fr-header__menu fr-modal" id="header-menu">\n'
                '            <div class="fr-container">\n'
                '                <nav class="fr-nav" id="navigation" role="navigation" aria-label="Menu principal">\n'
                '                    <!-- Slot : navigation principale (ul.fr-nav__list) -->\n'
                '                </nav>\n'
                '            </div>\n'
                '        </div>\n')
    if brand_mode == "neutral":
        header = ('    <header role="banner" class="fr-header">\n'
                  '        <div class="fr-header__body"><div class="fr-container">\n'
                  '            <div class="fr-header__body-row">\n'
                  '                <div class="fr-header__brand fr-enlarge-link">\n'
                  '                    <div class="fr-header__brand-top"><div class="fr-header__logo"></div></div>\n'
                  '                    <div class="fr-header__service">\n'
                  f'                        <a href="/" title="Accueil - {esc(title)}"><p class="fr-header__service-title">{esc(title)}</p></a>\n'
                  '                    </div>\n'
                  '                </div>\n'
                  '            </div>\n'
                  '        </div></div>\n'
                  + nav_slot +
                  '    </header>')
    else:
        header = ('    <header role="banner" class="fr-header">\n'
                  '        <div class="fr-header__body"><div class="fr-container">\n'
                  '            <div class="fr-header__body-row">\n'
                  '                <div class="fr-header__brand fr-enlarge-link">\n'
                  '                    <div class="fr-header__brand-top"><div class="fr-header__logo">\n'
                  '                        <p class="fr-logo">République<br>Française</p>\n'
                  '                    </div></div>\n'
                  '                    <div class="fr-header__service">\n'
                  f'                        <a href="/" title="Accueil - {esc(title)}"><p class="fr-header__service-title">{esc(title)}</p></a>\n'
                  '                    </div>\n'
                  '                </div>\n'
                  '            </div>\n'
                  '        </div></div>\n'
                  + nav_slot +
                  '    </header>')
    return f"""<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1, shrink-to-fit=no">
    <title>{esc(title)}</title>
    <link rel="stylesheet" href="{DSFR_BASE}/dsfr.min.css">
    <link rel="stylesheet" href="{DSFR_BASE}/utility/icons/icons.min.css">
    <link rel="icon" href="{DSFR_BASE}/favicon/favicon.svg" type="image/svg+xml">
</head>
<body>
    <div class="fr-skiplinks">
        <nav class="fr-container" role="navigation" aria-label="Accès rapide">
            <ul class="fr-skiplinks__list">
                <li><a class="fr-link" href="#contenu">Contenu</a></li>
                <li><a class="fr-link" href="#navigation">Menu</a></li>
                <li><a class="fr-link" href="#footer">Pied de page</a></li>
            </ul>
        </nav>
    </div>
{header}
    <main id="contenu">
        <div class="fr-container">
            <!-- Slot : contenu principal -->
        </div>
    </main>
    <footer class="fr-footer" role="contentinfo" id="footer">
        <div class="fr-container">
            <!-- Slot : pied de page -->
        </div>
    </footer>
    <script type="module" src="{DSFR_BASE}/dsfr.module.min.js"></script>
    <script nomodule src="{DSFR_BASE}/dsfr.nomodule.min.js"></script>
</body>
</html>"""


def generate_sidebar(aside: str = "<!-- Slot : menu latéral -->",
                     main: str = "<!-- Slot : contenu principal -->",
                     ratio: str = "3-9") -> str:
    """Génère une mise en page 2 colonnes (menu latéral + contenu)."""
    match = re.fullmatch(r"(\d{1,2})-(\d{1,2})", str(ratio))
    if not match or int(match.group(1)) + int(match.group(2)) != 12 or int(match.group(1)) < 1:
        raise ValueError(f"ratio '{ratio}' invalide : forme aside-main dont la somme vaut 12, par exemple 3-9")
    aside_md, main_md = match.group(1), match.group(2)
    return f"""<div class="fr-grid-row fr-grid-row--gutters">
    <div class="fr-col-12 fr-col-md-{esc(aside_md)}">
        {aside}
    </div>
    <div class="fr-col-12 fr-col-md-{esc(main_md)}">
        {main}
    </div>
</div>"""


def generate_columns(cols: list | None = None, gutters: bool = True,
                     md: int | None = None) -> str:
    """Génère une grille de N colonnes (égales ou paramétrées)."""
    if cols:
        items = cols
    else:
        items = [{"content": "<!-- Slot -->"}, {"content": "<!-- Slot -->"}]
    if md is None:
        md = None
    cells = ""
    for index, c in enumerate(items):
        content = c.get("content", "<!-- Slot -->") if isinstance(c, dict) else str(c)
        # Répartition sur 12 unités : les 12 % n premières colonnes reçoivent
        # une unité de plus, la somme vaut toujours 12 (r3-z02-010).
        if md is None:
            base, rest = divmod(12, len(items))
            auto_md = base + (1 if index < rest else 0)
        else:
            auto_md = md
        col_md = _col_width(c.get("md", auto_md)) if isinstance(c, dict) else _col_width(auto_md)
        cells += f'\n    <div class="fr-col-12 fr-col-md-{col_md}">\n        {content}\n    </div>'
    gutters_cls = " fr-grid-row--gutters" if gutters else ""
    return f'<div class="fr-grid-row{gutters_cls}">{cells}\n</div>'


def _as_item(value, key: str) -> dict:
    """Une chaîne devient {key: chaîne} ; tout autre non-dictionnaire est refusé."""
    if isinstance(value, dict):
        return value
    if isinstance(value, str):
        return {key: value}
    raise ValueError(f"élément invalide : objet ou chaîne attendu, reçu {type(value).__name__}")


def _col_width(value) -> int:
    try:
        width = int(value)
    except (TypeError, ValueError):
        raise ValueError("md doit être un entier entre 1 et 12") from None
    if not 1 <= width <= 12:
        raise ValueError(f"md doit être entre 1 et 12 (reçu {width})")
    return width


def _card(title: str, desc: str, href: str = "/") -> str:
    return (f'<div class="fr-card fr-enlarge-link"><div class="fr-card__body"><div class="fr-card__content">'
            f'<h3 class="fr-card__title"><a href="{esc_href(href)}">{esc(title)}</a></h3>'
            f'<p class="fr-card__desc">{esc(desc)}</p>'
            f'</div></div></div>')


def generate_card_grid(cards: list | None = None, md: int = 4) -> str:
    """Génère une grille de cartes DSFR."""
    if cards is None:
        cards = [{"title": "Carte 1", "desc": "Description"}, {"title": "Carte 2", "desc": "Description"}]
    md = _col_width(md)
    cells = ""
    for card in cards:
        card = _as_item(card, "title")
        cells += f'\n    <div class="fr-col-12 fr-col-md-{md}">\n        {_card(card.get("title", "Titre"), card.get("desc", ""), card.get("href", "/"))}\n    </div>'
    return f'<div class="fr-grid-row fr-grid-row--gutters">{cells}\n</div>'


def _tile(title: str, desc: str, href: str = "/") -> str:
    return (f'<div class="fr-tile fr-enlarge-link"><div class="fr-tile__body"><div class="fr-tile__content">'
            f'<h3 class="fr-tile__title"><a href="{esc_href(href)}">{esc(title)}</a></h3>'
            f'<p class="fr-tile__desc">{esc(desc)}</p>'
            f'</div></div></div>')


def generate_tile_grid(tiles: list | None = None, md: int = 4) -> str:
    """Génère une grille de tuiles DSFR."""
    if tiles is None:
        tiles = [{"title": "Tuile 1", "desc": "Description"}, {"title": "Tuile 2", "desc": "Description"}]
    md = _col_width(md)
    cells = ""
    for tile in tiles:
        tile = _as_item(tile, "title")
        cells += f'\n    <div class="fr-col-12 fr-col-md-{md}">\n        {_tile(tile.get("title", "Titre"), tile.get("desc", ""), tile.get("href", "/"))}\n    </div>'
    return f'<div class="fr-grid-row fr-grid-row--gutters">{cells}\n</div>'


LAYOUTS = {
    "skeleton": lambda config: generate_skeleton(**config),
    "sidebar": lambda config: generate_sidebar(**config),
    "columns": lambda config: generate_columns(cols=config.get("cols"), **{k: v for k, v in config.items() if k != "cols"}),
    "card-grid": lambda config: generate_card_grid(**config),
    "tile-grid": lambda config: generate_tile_grid(**config),
}


def list_layouts() -> None:
    """Affiche les gabarits disponibles."""
    print("Gabarits (génération paramétrable) :")
    for name in sorted(LAYOUTS.keys()):
        print(f"  - {name}")


def main():
    parser = argparse.ArgumentParser(
        description=f"Générateur de gabarits DSFR ({len(LAYOUTS)} gabarits : skeleton, sidebar, columns, card-grid, tile-grid)")
    parser.add_argument("layout", nargs="?", help="Gabarit à générer", choices=list(LAYOUTS.keys()) + ["list"])
    parser.add_argument("--config", help="Configuration JSON du gabarit", type=str)
    parser.add_argument("--output", help="Fichier de sortie ; refuse d'écraser un fichier existant")
    parser.add_argument("--list", action="store_true", help="Lister les gabarits disponibles")

    args = parser.parse_args()

    if args.list or args.layout == "list":
        list_layouts()
        return

    if not args.layout:
        parser.print_help()
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
        html = LAYOUTS[args.layout](config)
    except (TypeError, ValueError, AttributeError) as e:
        print(f"Erreur : paramètre invalide pour '{args.layout}' : {e}", file=sys.stderr)
        sys.exit(1)

    if args.output is not None:
        write_output(html, args.output, "Gabarit généré")
    else:
        if hasattr(sys.stdout, "reconfigure"):
            sys.stdout.reconfigure(encoding="utf-8")
        print(html)


if __name__ == "__main__":
    main()
