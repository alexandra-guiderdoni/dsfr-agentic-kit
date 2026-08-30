#!/usr/bin/env python3
"""
a11y_editorial — Fonctions pures de verification editoriale pour l'accessibilite.
Partagees entre md2docx.py, md2pdf.py et md2pptx.py (PRD-069).
Zero dependance format : recoit du texte brut, retourne des resultats.
"""

import re

# ---------------------------------------------------------------------------
# Donnees partagees
# ---------------------------------------------------------------------------

GLOSSAIRE_ACRONYMES = {
    "DSFR", "RGAA", "WCAG", "SNUM", "MEF", "SG", "PDF", "HTML", "CSS",
    "DGCCRF", "DGE", "DGFiP", "DGDDI", "DGAFP", "DITP", "DAE", "DAJ",
    "ANCT", "SIEP", "SRH", "IGPDE", "INSEE", "CNCPH", "CIH", "CNH",
    "HFHI", "FIPHFP", "SIRCOM", "MIWEB", "AMOA", "AMOE", "MOA", "MOE",
    "DINUM", "ARA", "SPAN", "PAN", "AA", "OK", "KO", "SI", "RH",
    "IR", "TV", "EU", "FR",
}

CAPITALES_ACCENTUEES = {
    "ETAT": "\u00c9TAT",
    "ECONOMIE": "\u00c9CONOMIE",
    "ETABLISSEMENT": "\u00c9TABLISSEMENT",
    "EVALUATION": "\u00c9VALUATION",
    "EVENEMENT": "\u00c9V\u00c9NEMENT",
    "EVOLUTION": "\u00c9VOLUTION",
    "EDUCATION": "\u00c9DUCATION",
    "EGALITE": "\u00c9GALIT\u00c9",
    "EQUIPE": "\u00c9QUIPE",
    "ETUDE": "\u00c9TUDE",
    "ETAPE": "\u00c9TAPE",
    "ECOLE": "\u00c9COLE",
    "ELEVE": "\u00c9L\u00c8VE",
    "ENERGIE": "\u00c9NERGIE",
    "ECHANGE": "\u00c9CHANGE",
    "ECHELLE": "\u00c9CHELLE",
    "ECHEANCE": "\u00c9CH\u00c9ANCE",
    "ELECTION": "\u00c9LECTION",
}

LIENS_GENERIQUES = {
    "cliquez ici", "ici", "lien", "en savoir plus", "plus d'infos",
    "lire la suite", "voir plus", "click here", "here", "more",
}


# ---------------------------------------------------------------------------
# Fonctions pures
# ---------------------------------------------------------------------------

def detect_acronymes(texte, glossaire=None):
    """Detecte les acronymes non repertories dans le texte.

    Args:
        texte: Texte brut a analyser.
        glossaire: Set de sigles connus (defaut: GLOSSAIRE_ACRONYMES).

    Returns:
        Liste triee des acronymes non repertories.
    """
    if glossaire is None:
        glossaire = GLOSSAIRE_ACRONYMES
    trouves = set()
    for match in re.finditer(r'\b([A-Z]{2,})\b', texte):
        acr = match.group(1)
        if acr not in glossaire:
            trouves.add(acr)
    return sorted(trouves)


def corriger_capitales(texte, table=None):
    """Corrige les capitales non accentuees dans le texte.

    Args:
        texte: Texte brut a corriger.
        table: Dict {non_accentue: accentue} (defaut: CAPITALES_ACCENTUEES).

    Returns:
        Tuple (texte_corrige, nombre_corrections).
    """
    if table is None:
        table = CAPITALES_ACCENTUEES
    count = 0
    for ancien, nouveau in table.items():
        if ancien in texte:
            texte = texte.replace(ancien, nouveau)
            count += 1
    return texte, count


def detect_liens_generiques(texte, termes=None):
    """Detecte les liens avec textes generiques.

    Args:
        texte: Texte brut ou HTML a analyser.
        termes: Set de textes generiques (defaut: LIENS_GENERIQUES).

    Returns:
        Liste des textes de liens generiques trouves.
    """
    if termes is None:
        termes = LIENS_GENERIQUES
    trouves = []
    # HTML links: <a ...>texte</a>
    for match in re.finditer(r'<a[^>]*>([^<]+)</a>', texte, re.IGNORECASE):
        link_text = match.group(1).strip().lower()
        if link_text in termes:
            trouves.append(match.group(1).strip())
    # Markdown links: [texte](url)
    for match in re.finditer(r'\[([^\]]+)\]\([^)]+\)', texte):
        link_text = match.group(1).strip().lower()
        if link_text in termes:
            trouves.append(match.group(1).strip())
    return trouves


def detect_paragraphes_vides_html(html):
    """Detecte les paragraphes vides dans du HTML.

    Args:
        html: Contenu HTML a analyser.

    Returns:
        Liste des numeros de ligne des <p> vides.
    """
    lignes_vides = []
    for i, line in enumerate(html.split('\n'), 1):
        if re.search(r'<p>\s*</p>|<p>&nbsp;</p>|<p>\s*<br\s*/?>\s*</p>', line):
            lignes_vides.append(i)
    return lignes_vides
