"""Les quatre natures de manques : éléments absents d'un composant présent,
composants attendus mais absents, composants hors couverture du harnais,
états non exercés.

La baseline des composants attendus a été validée le 2026-09-09 : structure sur
toutes les pages, fil d'Ariane hors accueil, groupe de messages sur les formulaires.
Elle signale une absence, elle ne déclare jamais un composant non conforme.
"""

from __future__ import annotations

import json
from pathlib import Path

from .collect import Collection, PageData, TRANSVERSE, VERSION_COMPONENT

BASELINE_ALL = ("skiplink", "header", "footer", "consent")
BASELINE_NON_HOME = ("breadcrumb",)
BASELINE_FORM = ("message_group",)
HOME_TYPES = {"homepage", "home", "accueil"}
FORM_TYPES = {"form", "formulaire", "contact"}
PSEUDO_COMPONENTS = {TRANSVERSE, VERSION_COMPONENT}

STATES_NOTE = (
    "États documentés par le DSFR que les règles automatiques de cet audit n'ont pas exercés. "
    "Un composant « Conforme » l'est au repos, pas dans ces états."
)
GENERIC_STATES = ["survol", "focus visible", "vue mobile", "thème sombre"]
STATES = {
    "navigation": ["menu ouvert et refermé au clavier", "sous-menus déroulés", "vue mobile, menu dans la modale"],
    "mega_menu": ["méga-menu ouvert et refermé au clavier", "vue mobile"],
    "header": ["menu mobile ouvert", "outils repliés en vue mobile"],
    "translate": ["sélecteur de langue ouvert", "changement de langue"],
    "modal": ["ouverture et fermeture", "retour du focus sur le déclencheur", "piège de focus", "fermeture par Échap"],
    "display": ["modale des paramètres ouverte", "thème sombre appliqué", "préférence système"],
    "accordion": ["panneau ouvert", "ouverture et fermeture au clavier"],
    "tabs": ["onglet actif", "navigation par flèches"],
    "search": ["soumission d'une recherche", "champ vide", "vue mobile, barre repliée"],
    "input": ["état d'erreur après validation (exercé sur P06 seulement)", "état de succès", "état désactivé"],
    "select": ["état d'erreur", "état désactivé"],
    "checkbox": ["état d'erreur", "état désactivé", "coché"],
    "radio": ["état d'erreur", "état désactivé", "sélectionné"],
    "upload": ["fichier sélectionné", "état d'erreur"],
    "fieldset": ["état d'erreur du groupe", "légende avec aide"],
    "message_group": ["messages d'erreur affichés après validation", "message de succès"],
    "consent": ["gestionnaire ouvert", "refus global", "retour après enregistrement"],
    "consent_manager": ["finalités acceptées ou refusées une à une", "enregistrement des choix"],
    "consent_service": ["service requis désactivé", "service optionnel basculé"],
    "skiplink": ["apparition au focus", "activation et déplacement du focus vers la cible"],
    "breadcrumb": ["fil déplié sur mobile", "page courante"],
    "button": ["état désactivé", "focus visible", "variantes icône"],
    "button_group": ["empilement en vue mobile"],
    "link": ["focus visible", "lien externe signalé", "téléchargement"],
    "enlarge_link": ["focus sur la zone cliquable étendue", "survol de toute la carte"],
    "card": ["survol", "focus sur le lien étendu", "variante horizontale en mobile"],
    "tile": ["survol", "focus sur le lien étendu", "variante horizontale en mobile"],
    "follow": ["focus sur chaque réseau", "vue mobile"],
    "share": ["copie de lien", "focus sur chaque bouton"],
    "tag": ["tag cliquable sélectionné", "tag supprimable"],
    "tag_group": ["retour à la ligne en vue mobile"],
    "footer": ["vue mobile", "thème sombre"],
}


def expected_for(page: PageData) -> list[str]:
    expected = list(BASELINE_ALL)
    if page.type not in HOME_TYPES:
        expected += list(BASELINE_NON_HOME)
    if page.type in FORM_TYPES:
        expected += list(BASELINE_FORM)
    return expected


def expected_absent(collection: Collection) -> dict[str, list[str]]:
    absent: dict[str, list[str]] = {}
    for page in collection.pages:
        present = {item["name"] for item in page.inventory}
        absent[page.id] = sorted(name for name in expected_for(page) if name not in present)
    return absent


def uncovered_components(collection: Collection) -> list[str]:
    return sorted(name for name, summary in collection.components.items()
                  if name not in PSEUDO_COMPONENTS and not summary.rules_executed and not collection.groups_for(name))


def unexercised_states(component: str) -> list[str]:
    return STATES.get(component, GENERIC_STATES)


def not_verified_union(collection: Collection) -> list[str]:
    return sorted({item for page in collection.pages for item in page.not_verified})


def harness_coverage(collection: Collection, rules_path: Path | None) -> dict[str, list[str]]:
    """Pour le backlog du kit : composants détectés sans règle, règles sans composant détecté."""
    detected = {name for name in collection.components if name not in PSEUDO_COMPONENTS}
    rule_components: set[str] = set()
    if rules_path and rules_path.is_file():
        catalog = json.loads(rules_path.read_text(encoding="utf-8"))
        rule_components = {rule["component"] for rule in catalog.get("rules", [])}
    return {
        "detected_without_rule": uncovered_components(collection),
        "rules_without_detection": sorted(rule_components - detected - {"html", "idref", "state", "skiplinks"}),
    }
