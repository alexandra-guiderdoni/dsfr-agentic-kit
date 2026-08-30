#!/usr/bin/env python3
"""Tests unitaires pour a11y_editorial.py (PRD-069)."""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from a11y_editorial import (
    detect_acronymes, corriger_capitales,
    detect_liens_generiques, detect_paragraphes_vides_html,
    GLOSSAIRE_ACRONYMES, CAPITALES_ACCENTUEES,
)


def test_detect_acronymes_connu():
    """Les acronymes du glossaire ne sont pas signales."""
    assert detect_acronymes("Le DSFR est conforme RGAA") == []


def test_detect_acronymes_inconnu():
    """Les acronymes hors glossaire sont detectes."""
    result = detect_acronymes("Le XYZW est un acronyme inconnu")
    assert result == ["XYZW"]


def test_detect_acronymes_mixte():
    """Melange de connus et inconnus."""
    result = detect_acronymes("DSFR et FOOBAR et RGAA et BAZQUX")
    assert result == ["BAZQUX", "FOOBAR"]


def test_detect_acronymes_glossaire_custom():
    """Glossaire personnalise."""
    result = detect_acronymes("ABC DEF", glossaire={"ABC"})
    assert result == ["DEF"]


def test_corriger_capitales_remplacement():
    """Les mots en capitales sont accentues."""
    texte, count = corriger_capitales("ETAT et ECONOMIE")
    assert "\u00c9TAT" in texte
    assert "\u00c9CONOMIE" in texte
    assert count == 2


def test_corriger_capitales_deja_accentue():
    """Les mots deja accentues ne sont pas modifies."""
    texte, count = corriger_capitales("\u00c9TAT et \u00c9CONOMIE")
    assert count == 0


def test_corriger_capitales_aucun():
    """Texte sans capitales a corriger."""
    texte, count = corriger_capitales("Bonjour le monde")
    assert count == 0
    assert texte == "Bonjour le monde"


def test_detect_liens_generiques_html():
    """Detection de liens generiques en HTML."""
    html = '<a href="https://example.com">cliquez ici</a> et <a href="/ok">Documentation</a>'
    result = detect_liens_generiques(html)
    assert result == ["cliquez ici"]


def test_detect_liens_generiques_markdown():
    """Detection de liens generiques en Markdown."""
    md = "[ici](https://example.com) et [Documentation officielle](https://docs.fr)"
    result = detect_liens_generiques(md)
    assert result == ["ici"]


def test_detect_liens_generiques_aucun():
    """Pas de lien generique."""
    result = detect_liens_generiques('<a href="/doc">Guide complet</a>')
    assert result == []


def test_paragraphes_vides_detectes():
    """Les paragraphes vides sont detectes."""
    html = "<p>Contenu</p>\n<p></p>\n<p>&nbsp;</p>\n<p>OK</p>"
    result = detect_paragraphes_vides_html(html)
    assert result == [2, 3]


def test_paragraphes_vides_aucun():
    """Pas de paragraphe vide."""
    html = "<p>Un</p>\n<p>Deux</p>"
    result = detect_paragraphes_vides_html(html)
    assert result == []


# ---------------------------------------------------------------------------
# Execution
# ---------------------------------------------------------------------------

if __name__ == '__main__':
    tests = [v for k, v in sorted(globals().items()) if k.startswith('test_')]
    passed = 0
    failed = 0
    for test in tests:
        try:
            test()
            passed += 1
            print(f"  OK  {test.__name__}")
        except AssertionError as e:
            failed += 1
            print(f"  ECHEC  {test.__name__}: {e}")
        except Exception as e:
            failed += 1
            print(f"  ERREUR  {test.__name__}: {e}")

    print(f"\n{passed}/{passed + failed} tests passes")
    sys.exit(1 if failed else 0)
