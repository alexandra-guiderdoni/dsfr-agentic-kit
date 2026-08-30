#!/usr/bin/env python3
"""Registre canonique des composants DSFR (issue #8 du miroir).

Caractérise les deux parcours de noms et prouve que le générateur, les
validations structurelles et l'inventaire officiel consomment un seul
registre. Lancer avec `python3 -B` : les modules du skill sont importés sans
écrire de `__pycache__` dans le paquet.
"""

from __future__ import annotations

import importlib
import json
import os
import subprocess
import sys
import unittest
from pathlib import Path

WORKSPACE = Path(os.environ.get("AGENTIC_DESIGN_WORKSPACE", Path(__file__).resolve().parents[2]))
SKILL_SCRIPTS = WORKSPACE / ".claude" / "skills" / "dsfr-components" / "scripts"
LIBRARY = SKILL_SCRIPTS.parent / "assets" / "dsfr_complete_library.json"

sys.dont_write_bytecode = True
sys.path.insert(0, str(SKILL_SCRIPTS))


def module(name: str):
    return importlib.import_module(name)


def library_components() -> set[str]:
    return set(json.loads(LIBRARY.read_text(encoding="utf-8")).get("components", {}))


class ParcoursAliasVersCanonique(unittest.TestCase):
    """Alias d'entrée → nom canonique local (sens du générateur)."""

    def test_alias_connus(self) -> None:
        registry = module("dsfr_component_registry")
        self.assertEqual(registry.canonical_name("tab"), "tabs")
        self.assertEqual(registry.canonical_name("skiplink"), "skiplinks")

    def test_nom_canonique_inchange(self) -> None:
        registry = module("dsfr_component_registry")
        for name in ("alert", "tabs", "skiplinks", "back_to_top"):
            self.assertEqual(registry.canonical_name(name), name)

    def test_alias_tries_pour_la_cli(self) -> None:
        registry = module("dsfr_component_registry")
        self.assertEqual(registry.input_aliases(), ("skiplink", "tab"))


class ParcoursLocalVersOfficiel(unittest.TestCase):
    """Nom local (canonique ou alias) → dossier officiel `dist/component/<nom>`."""

    def test_canonique_vers_officiel(self) -> None:
        registry = module("dsfr_component_registry")
        self.assertEqual(registry.official_name("tabs"), "tab")
        self.assertEqual(registry.official_name("skiplinks"), "skiplink")

    def test_alias_vers_officiel_passe_par_le_canonique(self) -> None:
        registry = module("dsfr_component_registry")
        self.assertEqual(registry.official_name("tab"), "tab")
        self.assertEqual(registry.official_name("skiplink"), "skiplink")

    def test_nom_officiel_par_defaut(self) -> None:
        registry = module("dsfr_component_registry")
        self.assertEqual(registry.official_name("alert"), "alert")
        self.assertEqual(registry.official_name("accordion"), "accordion")


class CoherenceDuRegistre(unittest.TestCase):
    """Le registre ne contient que des noms qui existent réellement."""

    def test_cibles_des_alias_sont_des_composants(self) -> None:
        registry = module("dsfr_component_registry")
        generate = module("generate_component")
        known = set(generate.NATIVE_COMPONENTS) | library_components()
        for alias, target in registry.INPUT_ALIASES.items():
            self.assertIn(target, known, f"alias {alias} vise un composant inconnu : {target}")
            self.assertNotIn(alias, known, f"alias {alias} est déjà un composant : il ne doit pas être un alias")

    def test_cles_officielles_sont_canoniques_et_connues(self) -> None:
        registry = module("dsfr_component_registry")
        generate = module("generate_component")
        known = set(generate.NATIVE_COMPONENTS) | library_components()
        for local, official in registry.OFFICIAL_NAMES.items():
            self.assertNotIn(local, registry.INPUT_ALIASES, f"{local} est un alias d'entrée, pas un nom canonique")
            self.assertIn(local, known, f"{local} n'est ni natif ni dans la bibliothèque")
            self.assertNotEqual(local, official)

    def test_helpers_locaux_sont_dans_la_bibliotheque_et_pas_natifs(self) -> None:
        registry = module("dsfr_component_registry")
        generate = module("generate_component")
        for helper in registry.LOCAL_HELPER_COMPONENTS:
            self.assertIn(helper, library_components())
            self.assertNotIn(helper, generate.NATIVE_COMPONENTS)


class ConsommateursDuRegistre(unittest.TestCase):
    """Générateur, validations et inventaire lisent le registre, pas une copie."""

    def test_aucun_dictionnaire_local_d_alias(self) -> None:
        for name in ("generate_component", "check_generated_outputs", "inventory_official_coverage"):
            source = (SKILL_SCRIPTS / f"{name}.py").read_text(encoding="utf-8")
            self.assertNotIn("COMPONENT_ALIASES = {", source, f"{name}.py définit encore son propre registre d'alias")
            self.assertNotIn("LOCAL_HELPER_COMPONENTS = {", source, f"{name}.py définit encore ses helpers locaux")
            self.assertIn("dsfr_component_registry", source, f"{name}.py n'importe pas le registre")

    def test_generateur_accepte_l_alias_et_produit_le_meme_html(self) -> None:
        def render(component: str) -> str:
            result = subprocess.run(
                [sys.executable, "-B", str(SKILL_SCRIPTS / "generate_component.py"), component],
                capture_output=True, text=True, check=True,
            )
            return result.stdout
        self.assertEqual(render("tab"), render("tabs"))
        self.assertEqual(render("skiplink"), render("skiplinks"))
        self.assertIn("fr-tabs", render("tab"))

    def test_validation_normalise_le_local_vers_l_officiel(self) -> None:
        checks = module("check_generated_outputs")
        registry = module("dsfr_component_registry")
        normalized = {registry.official_name(component) for component in library_components()}
        self.assertIn("tab", normalized)
        self.assertNotIn("tabs", normalized)
        self.assertTrue(hasattr(checks, "check_official_catalog"))

    def test_inventaire_ne_passe_plus_par_les_validations_pour_les_alias(self) -> None:
        source = (SKILL_SCRIPTS / "inventory_official_coverage.py").read_text(encoding="utf-8")
        self.assertNotIn("checks.COMPONENT_ALIASES", source)
        self.assertNotIn("checks.LOCAL_HELPER_COMPONENTS", source)


if __name__ == "__main__":
    unittest.main(verbosity=2)
