"""Libellés français des composants et des verdicts, partagés par les rendus."""

from __future__ import annotations

COMPONENT_LABELS = {
    "accordion": "Accordéon", "artwork": "Pictogrammes et illustrations", "breadcrumb": "Fil d'Ariane",
    "button": "Boutons", "button_group": "Groupes de boutons", "callout": "Mise en avant", "card": "Cartes",
    "checkbox": "Cases à cocher", "consent": "Bandeau de consentement", "consent_manager": "Gestionnaire de consentement",
    "consent_service": "Services du gestionnaire de consentement", "container": "Conteneurs", "display": "Paramètres d'affichage",
    "enlarge_link": "Liens étendus", "fieldset": "Groupes de champs", "follow": "Lettre d'information et réseaux sociaux",
    "footer": "Pied de page", "grid": "Grille", "header": "En-tête", "input": "Champs de saisie", "link": "Liens",
    "logo": "Bloc-marque", "mega_menu": "Méga-menu", "message_group": "Groupes de messages", "modal": "Modales",
    "navigation": "Navigation principale", "notice": "Bandeau d'information importante", "quote": "Citations",
    "radio": "Boutons radio", "responsive_media": "Médias responsives", "search": "Barre de recherche",
    "select": "Listes déroulantes", "share": "Boutons de partage", "skiplink": "Liens d'évitement", "table": "Tableaux",
    "tag": "Tags", "tag_group": "Groupes de tags", "tile": "Tuiles", "translate": "Sélecteur de langue",
    "upload": "Ajout de fichier", "transverse": "Règles transverses (identifiants, références ARIA, focus masqué)",
}
VERDICT_LABELS = {"CONFORME": "Conforme", "NON_CONFORME": "Non conforme", "NON_VERIFIE": "Non vérifié"}
STATUS_LABELS = {
    "ECART_CONFIRME": "écart confirmé", "AUCUN_ECART_OBSERVE": "aucun écart observé après revue",
    "A_CONFIRMER": "à confirmer", "NON_APPLICABLE": "non applicable", "REFERENCE_INDISPONIBLE": "référence indisponible",
    "CONTRADICTION": "qualifications contradictoires entre pages",
}


def component_label(name: str) -> str:
    return COMPONENT_LABELS.get(name, name.replace("_", " ").capitalize())


def page_report_href(page_id: str, depth: int) -> str:
    return "../" * depth + f"DSFR/{page_id}-DSFR.html"
