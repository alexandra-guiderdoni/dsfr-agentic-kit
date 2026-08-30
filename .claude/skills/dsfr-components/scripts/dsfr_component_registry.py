"""Registre canonique des composants DSFR du skill.

Une seule définition des noms, alias et métadonnées réellement communs à la
génération (`generate_component.py`), aux validations structurelles
(`check_generated_outputs.py`) et à l'inventaire officiel
(`inventory_official_coverage.py`). Avant ce module, chacun portait son
propre dictionnaire, dans des sens opposés : `skiplink → skiplinks` à
l'entrée du générateur, `skiplinks → skiplink` vers le paquet officiel dans
les validations, et l'inventaire lisait celui des validations.

Trois vocabulaires coexistent, volontairement :

- le nom d'entrée, tapé par l'agent ou l'utilisateur (`tab`, `tabs`) ;
- le nom canonique local, clé des composants natifs et de la bibliothèque
  JSON (`tabs`, `skiplinks`) ;
- le nom officiel, dossier `dist/component/<nom>` du paquet `@gouvfr/dsfr`
  (`tab`, `skiplink`).

Le registre ne liste pas les composants eux-mêmes : les composants natifs
restent définis par leur rendu dans `generate_component.py` et les autres
par `assets/dsfr_complete_library.json`. Les règles riches de validation
(classes racines attendues, contrats de formulaire) restent dans les
validations : ce module n'est pas un registre généraliste.
"""

from __future__ import annotations

# Alias d'entrée acceptés par le générateur, vers le nom canonique local.
INPUT_ALIASES: dict[str, str] = {
    "skiplink": "skiplinks",
    "tab": "tabs",
}

# Nom canonique local vers le nom du dossier officiel `dist/component/<nom>`.
# Absent du dictionnaire : le nom officiel est le nom canonique.
OFFICIAL_NAMES: dict[str, str] = {
    "skiplinks": "skiplink",
    "tabs": "tab",
}

# Composants de la bibliothèque locale sans dossier officiel dédié : aides de
# composition, pas des composants du catalogue DSFR.
LOCAL_HELPER_COMPONENTS: frozenset[str] = frozenset({"back_to_top", "button_group"})


def canonical_name(name: str) -> str:
    """Nom canonique local d'un nom d'entrée (alias résolu, sinon inchangé)."""
    return INPUT_ALIASES.get(name, name)


def official_name(name: str) -> str:
    """Nom du dossier officiel d'un nom d'entrée ou canonique."""
    canonical = canonical_name(name)
    return OFFICIAL_NAMES.get(canonical, canonical)


def input_aliases() -> tuple[str, ...]:
    """Alias d'entrée, triés, pour les choix de ligne de commande."""
    return tuple(sorted(INPUT_ALIASES))
