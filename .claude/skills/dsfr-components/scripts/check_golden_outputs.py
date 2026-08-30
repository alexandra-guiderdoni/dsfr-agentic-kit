#!/usr/bin/env python3
"""Golden files / régression pour les sorties natives header, navigation, footer,
card, alert, form, accordion, tabs, et les blocs fonctionnels (civilite,
nom-prenom, email, date-unique, societe).

check_generated_outputs.py exerce aussi les natifs, mais ses contrats
conditionnés au nom de variante ne s'appliquent qu'aux variantes de la
bibliothèque ; ce harnais capture la sortie byte-exacte de configurations
natives riches pour détecter toute dérive au prochain changement.

Pour chaque cas : régénération via le générateur natif, comparaison au fichier
golden, invariants communs (cibles ARIA résolues, aucun href="#", aucune
contrainte de formulaire au repos, IDs uniques), contrat structurel du
composant, hiérarchie de titres et ancres locales. Un fichier golden orphelin
(sans cas) ou un cas sans golden est signalé. --update n'écrit qu'après
validation de tous les cas : jamais de baseline mixte.

Usage :
  python3 scripts/check_golden_outputs.py            # compare au baseline
  python3 scripts/check_golden_outputs.py --update   # (re)génère le baseline (changement délibéré)
"""

import argparse
import difflib
import sys
from pathlib import Path

sys.dont_write_bytecode = True

SCRIPTS_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPTS_DIR))
import generate_component as gc  # noqa: E402
import generate_field as gf  # noqa: E402
import check_generated_outputs as cks  # noqa: E402

GOLDEN_DIR = SCRIPTS_DIR.parent / "evals" / "golden"

GOLDEN_CASES = [
    ("header-default", gc.generate_header, {}),
    ("header-republique", gc.generate_header, {"brand_mode": "republique"}),
    (
        "header-with-tools-languages",
        gc.generate_header,
        {
            "service_title": "Mon service",
            "tools": [
                {"label": "Se connecter", "href": "/connexion"},
                {"label": "Créer un compte", "href": "/compte"},
            ],
            "languages": [
                {"code": "FR", "name": "Français", "href": "/fr", "active": True},
                {"code": "EN", "name": "English", "href": "/en"},
            ],
        },
    ),
    (
        "header-with-search",
        gc.generate_header,
        {
            "service_title": "Mon service",
            "search": {"label": "Rechercher"},
        },
    ),
    (
        "header-with-menu",
        gc.generate_header,
        {
            "service_title": "Mon service",
            "navigation": [
                {"label": "Accueil", "href": "/", "active": True},
                {"label": "Services", "href": "/services"},
            ],
        },
    ),
    ("navigation-default", gc.generate_navigation, {}),
    (
        "navigation-with-children",
        gc.generate_navigation,
        {
            "items": [
                {"label": "Accueil", "href": "/", "active": True},
                {"label": "Rubrique", "children": [{"label": "Sous-rubrique", "href": "/sous"}]},
            ]
        },
    ),
    (
        "navigation-mega-menu",
        gc.generate_navigation,
        {
            "items": [
                {"label": "Accueil", "href": "/", "active": True},
                {
                    "label": "Démarches",
                    "categories": [
                        {
                            "label": "Particuliers",
                            "href": "/particuliers",
                            "items": [
                                {"label": "Santé", "href": "/sante"},
                                {"label": "Famille", "href": "/famille"},
                            ],
                        },
                        {
                            "label": "Entreprises",
                            "href": "/entreprises",
                            "items": [{"label": "Création", "href": "/creation"}],
                        },
                    ],
                },
                {"label": "Contact", "href": "/contact", "align": "right"},
            ]
        },
    ),
    ("footer-default", gc.generate_footer, {}),
    ("footer-republique", gc.generate_footer, {"brand_mode": "republique"}),
    (
        "footer-with-partners",
        gc.generate_footer,
        {
            "brand_mode": "republique",
            "partners": {
                "title": "Nos partenaires",
                "main_partner": {
                    "href": "https://partenaire-1.gouv.fr",
                    "src": "/img/p1.svg",
                    "alt": "Partenaire principal",
                },
                "sub_partners": [
                    {"href": "https://p2.gouv.fr", "src": "/img/p2.svg", "alt": "P2"},
                ],
            },
            "bottom_links": [{"label": "Plan du site", "href": "/plan-du-site"}],
            "copyright": "Sauf mention contraire, tous les contenus de ce site sont sous licence etalab-2.0",
        },
    ),
    ("card-default", gc.generate_card, {}),
    ("alert-default", gc.generate_alert, {}),
    ("form-default", gc.generate_form, {}),
    # items=[] est remplacé par l'accordéon de démonstration : le cas fige ce
    # défaut implicite, il n'exerce pas un accordéon vide.
    ("accordion-defaut-implicite", gc.generate_accordion, {"items": []}),
    ("tabs-default", gc.generate_tab, {}),
    # Blocs fonctionnels : dérivés de la table FIELDS (source unique).
    *[(f"field-{name}", fn, {}) for name, fn in gf.FIELDS.items()],
]


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Golden files pour sorties natives header/navigation/footer/card/alert/form/accordion/tabs/fields"
    )
    parser.add_argument("--update", action="store_true", help="(re)génère le baseline")
    args = parser.parse_args()

    if args.update:
        print(
            "AVERTISSEMENT : régénération du baseline golden (--update). Vérifier "
            "le diff au commit ; ne pas utiliser pour masquer une régression.",
            file=sys.stderr,
        )
        GOLDEN_DIR.mkdir(parents=True, exist_ok=True)

    failures = []
    # Échecs qu'une mise à jour de baseline ne résout PAS : une génération
    # cassée ou un invariant violé. Un golden absent ou un diff non vide sont
    # au contraire ce que --update est censé corriger.
    bloquantes = []
    pending: list[tuple[Path, str]] = []
    expected_names = {name for name, _, _ in GOLDEN_CASES}
    if len(expected_names) != len(GOLDEN_CASES):
        failures.append("GOLDEN_CASES : noms de cas dupliqués")
    for name, fn, kwargs in GOLDEN_CASES:
        try:
            output = fn(**kwargs)
        except Exception as exc:  # noqa: BLE001 - un cas cassé ne doit pas
            # interrompre les autres : on l'enregistre et on continue.
            detail = f"{name}: génération échouée: {type(exc).__name__}: {exc}"
            failures.append(detail)
            bloquantes.append(detail)
            continue

        scope = f"golden:{name}"
        facts = cks.parse_markup(output)
        issues = list(cks.check_common(scope, output))
        component = name.split("-", 1)[0]
        if component in cks.COMPONENT_ROOT_CLASS_CONTRACTS:
            # Variante déduite des paramètres réels du cas, pas de son nom.
            brand = str(kwargs.get("brand_mode", "neutral"))
            if component == "header" and kwargs.get("search"):
                variant = f"with_search_{brand}"
            else:
                variant = "basic" if brand == "republique" else "neutral"
            issues.extend(cks.check_component_structure(component, variant, scope, facts))
        issues.extend(cks.check_heading_hierarchy(scope, facts, require_h1_first=False))
        issues.extend(cks.check_anchor_targets(scope, facts, tolerated=cks.PAGE_ANCHOR_IDS))
        for issue in issues:
            detail = f"{name}: {issue.code}: {issue.detail}"
            failures.append(detail)
            bloquantes.append(detail)

        golden_path = GOLDEN_DIR / f"{name}.html"
        if args.update:
            if issues:
                # Ne jamais figer dans l'oracle une sortie qui viole un
                # invariant : elle deviendrait la référence attendue.
                print(f"REFUS mise à jour {name}: invariants non respectés")
                continue
            # Écriture différée : aucun fichier n'est touché si un cas échoue.
            pending.append((golden_path, output))
            continue
        if not golden_path.exists():
            failures.append(f"{name}: golden manquant — lancer --update")
            continue
        expected = golden_path.read_text(encoding="utf-8")
        if output != expected:
            diff = difflib.unified_diff(
                expected.splitlines(keepends=True),
                output.splitlines(keepends=True),
                fromfile=f"{name}.html (baseline)",
                tofile=f"{name}.html (courant)",
                n=2,
            )
            failures.append(f"{name}: diff golden non vide\n{''.join(diff)}")

    on_disk = {path.stem for path in GOLDEN_DIR.glob("*.html")} if GOLDEN_DIR.exists() else set()
    orphans = sorted(on_disk - expected_names)
    if orphans:
        failures.append("golden orphelins (sans cas dans GOLDEN_CASES) : " + ", ".join(orphans))
    if args.update:
        if bloquantes or orphans:
            print(f"FAIL golden --update: {len(bloquantes) + len(orphans)} problème(s), aucun fichier écrit")
            for detail in bloquantes + [f"orphelin : {name}.html" for name in orphans]:
                print(detail)
            return 1
        for golden_path, output in pending:
            golden_path.write_text(output, encoding="utf-8")
            print(f"updated {golden_path.relative_to(SCRIPTS_DIR.parent)}")
        print(f"baseline golden mis à jour ({len(GOLDEN_CASES)} cas)")
        return 0
    if failures:
        print(f"FAIL golden: {len(failures)} problème(s)")
        for failure in failures:
            print(failure)
        return 1
    print(f"PASS golden: {len(GOLDEN_CASES)} cas inchangés + invariants OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
