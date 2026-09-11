#!/usr/bin/env python3
"""Énumère et valide les icônes DSFR (Remix Icon) du paquet @gouvfr/dsfr@1.15.3.

Lit `dist/utility` AU RUNTIME — la liste (1044 classes en 1.15.3) n'est jamais
embarquée dans le script ni chargée en contexte. Résout le paquet via
`DSFR_OFFICIAL_PACKAGE_DIR` puis le cache officiel
(`DSFR_OFFICIAL_CACHE_DIR`, peuplé par
`check_generated_outputs.py --official-version 1.15.3`).

Usage :
  python3 list_icons.py                       # compte + catégories (défaut)
  python3 list_icons.py --filter account      # icônes contenant "account"
  python3 list_icons.py --validate account-circle-line   # exit 0 si officielle
  python3 list_icons.py --all                 # liste complète (1044 en 1.15.3)
"""

import argparse
import os
import re
import sys
from pathlib import Path

DSFR_VERSION = os.environ.get("DSFR_OFFICIAL_VERSION") or "1.15.3"
DEFAULT_CACHE = os.path.expanduser(os.environ.get("DSFR_OFFICIAL_CACHE_DIR") or "~/.cache/dsfr-official-cache")
# L'échappement CSS `\@` fait partie du nom des classes à point de rupture
# (`fr-cell--fixed@sm`…) : sans lui, la classe est tronquée au `@` et repliée
# sur un préfixe déjà compté.
CLASS_RE = re.compile(r"\.((?:fr|ri)-(?:[A-Za-z0-9_-]|\\@)+)")


def resolve_package():
    """Paquet officiel : DSFR_OFFICIAL_PACKAGE_DIR (obligatoirement valide s'il est
    défini, tilde développé), sinon le cache officiel de la version cible."""
    env_dir = os.environ.get("DSFR_OFFICIAL_PACKAGE_DIR")
    if env_dir:
        candidate = Path(os.path.expanduser(env_dir))
        if (candidate / "dist" / "utility" / "utility.min.css").is_file():
            return candidate
        print(f"Erreur : DSFR_OFFICIAL_PACKAGE_DIR={env_dir} ne contient pas dist/utility/utility.min.css", file=sys.stderr)
        sys.exit(2)
    candidate = Path(DEFAULT_CACHE) / f"gouvfr-dsfr-{DSFR_VERSION}" / "package"
    if (candidate / "dist" / "utility" / "utility.min.css").is_file():
        return candidate
    return None


def package_version(package) -> str:
    """Version réellement lue (package.json), affichée à la place de la cible."""
    try:
        import json
        return str(json.loads((package / "package.json").read_text(encoding="utf-8")).get("version") or DSFR_VERSION)
    except (OSError, ValueError):
        return DSFR_VERSION


def load_icons(package):
    """Icônes du CSS utilitaire. Décodage strict : `errors="ignore"` supprimait
    les octets invalides d'un fichier corrompu, donc des icônes, et faisait
    répondre « KO » pour une icône réellement présente."""
    path = package / "dist" / "utility" / "utility.min.css"
    try:
        css = path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError) as exc:
        print(f"Erreur : {path} illisible ({exc.__class__.__name__}) : paquet officiel corrompu", file=sys.stderr)
        sys.exit(2)
    icons = sorted({match.group(1).replace("\\", "") for match in CLASS_RE.finditer(css)
                    if match.group(1).startswith("fr-icon-")})
    if not icons:
        print(f"Erreur : aucune classe fr-icon-* dans {path} : fichier tronqué ou paquet non officiel", file=sys.stderr)
        sys.exit(2)
    return icons


def categories(package):
    base = package / "dist" / "utility" / "icons"
    if not base.is_dir():
        return []
    return sorted(d.name.replace("icons-", "") for d in base.iterdir() if d.is_dir() and d.name.startswith("icons-"))


def main():
    parser = argparse.ArgumentParser(description="Énumère et valide les icônes DSFR 1.15.3 (runtime).")
    parser.add_argument("--filter", help="Ne garder que les icônes contenant ce terme")
    parser.add_argument("--validate", help="Sortie 0 si l'icône est officielle 1.15.3, 1 sinon")
    parser.add_argument("--all", action="store_true", help="Liste complète")
    parser.add_argument("--count", action="store_true", help="Compte + catégories (comportement par défaut ; ignoré si --validate, --all ou --filter est présent)")
    args = parser.parse_args()

    # Les erreurs d'arguments doivent rester déterministes, même lorsque le
    # paquet officiel n'est pas disponible en mode hors ligne. Une garde de
    # dépendance placée avant cette validation transformait une faute de saisie
    # en erreur de cache et faisait échouer les tests négatifs du générateur.
    if args.validate is not None:
        name = args.validate.strip()
        if not name:
            print("Erreur : --validate exige un nom d'icône (par exemple account-circle-line)", file=sys.stderr)
            sys.exit(2)
        if name.startswith("ri-"):
            print(f"Erreur : {name} est un nom Remix Icon (ri-*) ; le paquet n'expose que les classes fr-icon-* (essayer fr-icon-{name[3:]})", file=sys.stderr)
            sys.exit(2)
    if args.filter is not None and not args.filter.strip():
        print("Erreur : --filter exige un terme non vide", file=sys.stderr)
        sys.exit(2)

    package = resolve_package()
    if not package:
        print(
            "Erreur : paquet @gouvfr/dsfr@" + DSFR_VERSION + " introuvable. "
            "Définir DSFR_OFFICIAL_PACKAGE_DIR ou DSFR_OFFICIAL_CACHE_DIR "
            "(lancer check_generated_outputs.py --official-version " + DSFR_VERSION + " pour peupler le cache).",
            file=sys.stderr,
        )
        sys.exit(2)

    icons = load_icons(package)
    version = package_version(package)

    # --count nomme le comportement par défaut : il est ignoré dès qu'un autre
    # mode est demandé, ce que l'appelant doit voir plutôt que le deviner.
    if args.count and (args.validate is not None or args.all or args.filter is not None):
        print("Avertissement : --count ignoré (--validate, --all ou --filter a la priorité)", file=sys.stderr)

    if args.validate is not None:
        name = args.validate.strip()
        if not name.startswith("fr-icon-"):
            name = f"fr-icon-{name}"
        if name in icons:
            print(f"OK : {name} est une icône officielle {version}")
            sys.exit(0)
        print(f"KO : {name} n'est pas une icône officielle {version}", file=sys.stderr)
        sys.exit(1)

    if args.all:
        print("\n".join(icons))
        return

    if args.filter is not None:
        matched = [icon for icon in icons if args.filter.lower() in icon.lower()]
        print(f"{len(matched)} icône(s) contenant « {args.filter} » :")
        for icon in matched:
            print(f"  {icon}")
        return

    cats = categories(package)
    print(f"DSFR {version} : {len(icons)} icônes officielles (fr-icon-*)")
    if cats:
        print(f"Catégories ({len(cats)}) : {', '.join(cats)}")


if __name__ == "__main__":
    main()
