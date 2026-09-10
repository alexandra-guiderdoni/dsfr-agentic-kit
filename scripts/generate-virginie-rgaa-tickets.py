#!/usr/bin/env python3
"""Génère les tickets RGAA unitaires du livrable Virginie.

Les constats confirmés des rapports RGAA P01 à P09 sont regroupés par cause
racine. Les sorties client ne contiennent aucun chemin absolu local.
"""

from __future__ import annotations

import argparse
import fcntl
import hashlib
import html
import json
import os
import re
import shutil
import unicodedata
from collections import Counter, defaultdict
from contextlib import contextmanager
from datetime import date
from html.parser import HTMLParser
from pathlib import Path
from typing import Any

from virginie_dsfr.project_paths import (  # noqa: E402
    KIT_ROOT,
    require_project_root,
    safe_pipeline_lock,
    safe_write_path,
)

ROOT = KIT_ROOT
ARCHIVES = ROOT / "archives"
DELIVERY = ROOT / "virginie-livrables"
TICKETS_ROOT = DELIVERY / "TICKETS-RGAA"
PIPELINE_LOCK = ROOT / "visual-tests/_results/.p06-pipeline.lock"
MD_ROOT = TICKETS_ROOT / "markdown"
HTML_ROOT = TICKETS_ROOT / "html"
DELIVERY_DATE = date.today().isoformat()


def resolve_ay11_root() -> Path:
    """Racine locale du dépôt ay11-pre-audit, lue dans l'environnement.

    Aucune valeur par défaut : la disposition des dossiers varie d'un poste à
    l'autre, et un chemin codé en dur ne ferait que déplacer l'erreur au
    premier accès au fichier. `AY11_ROOT` est le nom documenté ; le nom
    historique `AY11_PRE_AUDIT_ROOT` reste accepté.
    """
    valeur = os.environ.get("AY11_ROOT") or os.environ.get("AY11_PRE_AUDIT_ROOT")
    if not valeur:
        raise SystemExit(
            "AY11_ROOT n'est pas défini : indiquer la racine locale du dépôt "
            "ay11-pre-audit, par exemple\n"
            '    export AY11_ROOT="/chemin/vers/ay11-pre-audit"\n'
            "Le fichier .env.local du kit peut porter cette variable."
        )
    racine = Path(valeur).expanduser()
    if not racine.is_dir():
        raise SystemExit(f"AY11_ROOT ne désigne pas un dossier existant : {racine}")
    return racine


def rgaa_reference() -> Path:
    """Référentiel RGAA normalisé, résolu depuis AY11_ROOT."""
    return resolve_ay11_root() / "references/rgaa/normalized/rgaa-4.1.2.json"

PAGE_IDS = [f"P{i:02d}" for i in range(1, 10)]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--project-root",
        type=Path,
        default=None,
        help="projet de travail existant ; défaut : DSFR_PROJECT_ROOT",
    )
    parser.add_argument(
        "--archives",
        type=Path,
        default=None,
        help="dossier d’archives ; défaut : <project-root>/archives",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=None,
        help="dossier de livraison ; défaut : <project-root>/virginie-livrables",
    )
    parser.add_argument("--delivery-date", default=date.today().isoformat())
    return parser.parse_args()


def configure_paths(args: argparse.Namespace) -> argparse.Namespace:
    """Place toutes les destinations de génération sous le projet."""
    project_root = require_project_root(args.project_root)
    delivery = safe_write_path(
        args.output or project_root / "virginie-livrables",
        project_root=project_root,
        label="livrables RGAA",
    )
    global ARCHIVES, DELIVERY, TICKETS_ROOT, PIPELINE_LOCK, MD_ROOT, HTML_ROOT, DELIVERY_DATE
    ARCHIVES = args.archives or project_root / "archives"
    DELIVERY = delivery
    TICKETS_ROOT = safe_write_path(
        delivery / "TICKETS-RGAA",
        project_root=project_root,
        label="tickets RGAA",
    )
    MD_ROOT = safe_write_path(
        TICKETS_ROOT / "markdown",
        project_root=project_root,
        label="tickets RGAA Markdown",
    )
    HTML_ROOT = safe_write_path(
        TICKETS_ROOT / "html",
        project_root=project_root,
        label="tickets RGAA HTML",
    )
    PIPELINE_LOCK = safe_pipeline_lock(project_root)
    DELIVERY_DATE = args.delivery_date
    args.project_root = project_root
    return args


def clean_reference_text(value: str) -> str:
    value = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", value)
    value = value.replace("\u00a0", " ")
    return re.sub(r"\s+", " ", value).strip()


def slugify(value: str) -> str:
    value = unicodedata.normalize("NFKD", value).encode("ascii", "ignore").decode()
    value = re.sub(r"[^a-zA-Z0-9]+", "-", value).strip("-").lower()
    return value


def md_cell(value: Any) -> str:
    return str(value).replace("|", "—").replace("\n", " ").strip()


def inline_html(value: str) -> str:
    escaped = html.escape(value)
    return re.sub(r"`([^`]+)`", r"<code>\1</code>", escaped)


def paragraphs_html(value: str) -> str:
    return "".join(
        f"<p>{inline_html(paragraph.strip())}</p>"
        for paragraph in value.split("\n\n")
        if paragraph.strip()
    )


def unique(values: list[str]) -> list[str]:
    return list(dict.fromkeys(value for value in values if value))


def finding_evidence(finding: dict[str, Any]) -> list[str]:
    qualification = finding.get("qualification") or {}
    return unique(
        [str(value) for value in finding.get("evidence", [])]
        + [str(value) for value in qualification.get("evidence", [])]
    )


def ticket_scope(pages: list[dict[str, str]]) -> str:
    if len(pages) == 1:
        return f"Locale — {pages[0]['id']}"
    return "Transverse — " + ", ".join(page["id"] for page in pages)


def severity_rank(value: str) -> int:
    return {"Mineur": 1, "Majeur": 2, "Bloquant": 3}.get(value, 0)


def archive_for(page: str) -> Path:
    number = int(page[1:])
    return ARCHIVES / f"audit-douane-p{number:02d}-complet-rgaa-dsfr-2026-09-02"


def load_sources() -> tuple[
    list[dict[str, Any]],
    dict[str, dict[str, str]],
    dict[str, dict[str, str]],
    Counter[str],
]:
    reference = json.loads(rgaa_reference().read_text(encoding="utf-8"))
    criteria = {
        item["criterion_id"]: {
            "title": clean_reference_text(item["title"]),
            "url": item["source_url"],
        }
        for item in reference["criteria"]
    }
    tests = {
        item["test_id"]: {
            "title": clean_reference_text(" ".join(item["title"])),
            "url": item["source_url"],
        }
        for item in reference["tests"]
    }

    findings: list[dict[str, Any]] = []
    status_counts: Counter[str] = Counter()
    for page in PAGE_IDS:
        source = archive_for(page) / "rgaa/CONSTATS-INSTANCES.json"
        data = json.loads(source.read_text(encoding="utf-8"))
        status_counts.update(item.get("qualification_status", "INCONNU") for item in data["findings"])
        for finding in data["findings"]:
            if finding.get("qualification_status") == "NC_CONFIRMEE":
                findings.append(finding)
    return findings, criteria, tests, status_counts


TICKET_SPECS: list[dict[str, Any]] = [
    {
        "id": "NC-TRANSVERSE-001",
        "slug": "recherche-visible-sous-aria-hidden",
        "title": "Recherche visible et focalisable sous aria-hidden",
        "rules": [
            "RGAA-7-1-SCRIPT-ARIA-HIDDEN-003",
            "RGAA-10-8-HIDDEN-FOCUS-001",
        ],
        "methodological_alert": (
            "Le rattachement au test 10.8.1 est direct. Le rattachement secondaire au test 7.1.1 doit rester "
            "appuyé par la preuve d’arbre d’accessibilité montrant la perte de restitution du composant."
        ),
        "analysis": (
            "Le formulaire de recherche conserve `aria-hidden=\"true\"` alors que son champ et son bouton "
            "sont visibles et atteints par la tabulation. L’attribut retire le sous-arbre de l’arbre "
            "d’accessibilité sans le retirer du parcours clavier. La personne au clavier peut donc placer le "
            "focus sur des contrôles qu’un lecteur d’écran ne restitue pas. Une même cause racine met en échec "
            "les tests 7.1.1 et 10.8.1. Le défaut provient du gabarit d’en-tête commun aux neuf pages."
        ),
        "impact": (
            "La navigation clavier et la restitution vocale sont désynchronisées. Le champ et le bouton peuvent "
            "être impossibles à identifier ou à utiliser avec une technologie d’assistance."
        ),
        "solutions": [
            {
                "title": "Synchroniser l’état masqué et l’état ouvert (recommandée)",
                "text": (
                    "Lorsque la recherche est fermée, retirer tout le panneau du rendu et du parcours clavier "
                    "avec `hidden` ou le mécanisme natif du composant DSFR. Retirer cet état avant de déplacer le "
                    "focus dans la recherche. Ne pas maintenir `aria-hidden=\"true\"` sur un formulaire visible."
                ),
                "code": """<!-- État ouvert : le formulaire est exposé et utilisable -->
<div id="header-search" class="fr-header__search fr-modal">
  <form action="/recherche" method="get" class="fr-search-bar"
        id="search" role="search">
    <label class="fr-label" for="search-input">Rechercher</label>
    <input class="fr-input" id="search-input" name="query" type="search">
    <button class="fr-btn" id="search-btn" type="submit">Rechercher</button>
  </form>
</div>""",
            },
            {
                "title": "Reprendre le cycle d’ouverture du composant DSFR",
                "text": (
                    "Aligner le template Drupal et son JavaScript sur le composant d’en-tête DSFR : le panneau "
                    "fermé ne doit pas exposer de contrôles focalisables et le panneau ouvert ne doit pas rester "
                    "masqué aux technologies d’assistance."
                ),
                "code": """<!-- État fermé : aucun descendant ne reçoit le focus -->
<div id="header-search" class="fr-header__search fr-modal" hidden>
  <!-- formulaire de recherche -->
</div>""",
            },
        ],
        "dsfr": {
            "component": "En-tête / barre de recherche",
            "rows": [
                ("État ouvert", "Contenu exposé dans l’arbre d’accessibilité", "Formulaire encore aria-hidden"),
                ("Parcours clavier", "Contrôles atteignables uniquement à l’ouverture", "Champ et bouton atteignables sous aria-hidden"),
                ("Cause attribuée", "Comportement géré par le composant", "Intégration / synchronisation d’état"),
            ],
            "links": [
                ("DSFR 1.15.2 — composant search", "https://github.com/GouvernementFR/dsfr/tree/v1.15.2/src/dsfr/component/search"),
                ("DSFR 1.15.2 — composant header", "https://github.com/GouvernementFR/dsfr/tree/v1.15.2/src/dsfr/component/header"),
            ],
        },
        "verification": [
            "Tester les états fermé puis ouvert au clavier sur chaque gabarit.",
            "Vérifier qu’aucun descendant d’un élément `aria-hidden=\"true\"` ne reçoit le focus.",
            "À l’ouverture, contrôler le rôle, le nom et la présence des contrôles dans l’arbre d’accessibilité.",
            "Compléter par NVDA + Firefox ou VoiceOver + Safari avant clôture.",
        ],
    },
    {
        "id": "NC-P06-004",
        "slug": "modale-cgu-sans-nom-ni-contenu",
        "title": "Modale CGU sans nom accessible ni contenu utile",
        "rules": ["RGAA-7-1-DIALOG-NAME-001"],
        "pages_filter": ["P06"],
        "analysis": (
            "La modale CGU cite `cgu-ids-modal-title` dans `aria-labelledby`, mais aucun élément ne porte cet "
            "identifiant dans le DOM rendu. Dans l’état observé, le conteneur de contenu est également vide. "
            "Le rôle de dialogue est présent, mais son nom programmatique et l’information attendue ne peuvent "
            "pas être restitués."
        ),
        "impact": (
            "À l’ouverture, une personne utilisant un lecteur d’écran peut entendre seulement « dialogue » sans "
            "identifier les conditions générales ni accéder à leur contenu."
        ),
        "solutions": [
            {
                "title": "Créer le titre et charger le contenu avant l’ouverture (recommandée)",
                "text": (
                    "Ajouter un titre pertinent avec l’identifiant exact référencé par `aria-labelledby`. "
                    "Charger le contenu utile de la modale avant de l’exposer et d’y déplacer le focus."
                ),
                "code": """<dialog id="cgu-ids-modal" class="fr-modal"
        aria-labelledby="cgu-ids-modal-title">
  <div class="fr-modal__body">
    <div class="fr-modal__content">
      <h2 id="cgu-ids-modal-title" class="fr-modal__title">
        Conditions générales d’utilisation
      </h2>
      <!-- contenu utile des CGU -->
    </div>
  </div>
</dialog>""",
            },
        ],
        "dsfr": {
            "component": "Modale CGU",
            "rows": [
                ("Nom accessible", "Titre présent et relié par aria-labelledby", "Identifiant de titre absent"),
                ("Contenu", "Contenu disponible à l’ouverture", "Conteneur vide dans l’état observé"),
                ("Cause attribuée", "Structure DSFR nommée", "Chargement / intégration de la modale CGU"),
            ],
            "links": [
                ("DSFR 1.15.2 — composant modal", "https://github.com/GouvernementFR/dsfr/tree/v1.15.2/src/dsfr/component/modal"),
            ],
        },
        "verification": [
            "Ouvrir la modale CGU au clavier.",
            "Contrôler que `aria-labelledby` cible un titre existant et unique.",
            "Vérifier que le contenu est présent avant le déplacement du focus.",
            "Contrôler le nom calculé puis la restitution avec un lecteur d’écran réel.",
        ],
    },
    {
        "id": "NC-P09-001",
        "slug": "modale-transcription-sans-nom",
        "title": "Modale de transcription sans nom accessible",
        "rules": ["RGAA-7-1-DIALOG-NAME-001"],
        "pages_filter": ["P09"],
        "analysis": (
            "La modale de transcription cite `fr-transcription-modal-title` dans `aria-labelledby`, mais aucune "
            "cible rendue ne porte cet identifiant. La transcription est présente ; seul le titre programmatique "
            "du dialogue manque. Ce défaut relève du template de transcription de P09, distinct de la modale CGU."
        ),
        "impact": (
            "Une personne utilisant un lecteur d’écran accède au texte de transcription sans connaître le nom "
            "de la fenêtre ouverte ni son lien avec le graphique."
        ),
        "solutions": [
            {
                "title": "Ajouter un titre unique et le référencer (recommandée)",
                "text": "Créer un titre visible, suffixé avec l’identifiant métier de la transcription, puis mettre à jour `aria-labelledby`.",
                "code": """<dialog id="fr-transcription-modal-transcription-20210"
        aria-labelledby="fr-transcription-modal-title-20210">
  <h2 id="fr-transcription-modal-title-20210" class="fr-modal__title">
    Transcription du graphique
  </h2>
  <!-- transcription -->
</dialog>""",
            },
        ],
        "dsfr": {
            "component": "Modale de transcription",
            "rows": [
                ("Nom accessible", "Titre présent et relié par aria-labelledby", "Identifiant de titre absent"),
                ("Contenu", "Transcription disponible", "Transcription présente"),
                ("Cause attribuée", "Structure DSFR nommée", "Template de transcription"),
            ],
            "links": [
                ("DSFR 1.15.2 — composant modal", "https://github.com/GouvernementFR/dsfr/tree/v1.15.2/src/dsfr/component/modal"),
            ],
        },
        "verification": [
            "Ouvrir la transcription au clavier.",
            "Contrôler que `aria-labelledby` cible un titre existant et unique.",
            "Vérifier le nom calculé dans l’arbre d’accessibilité puis avec un lecteur d’écran réel.",
            "Vérifier le retour du focus sur le déclencheur à la fermeture.",
        ],
    },
    {
        "id": "NC-TRANSVERSE-003",
        "slug": "lien-evitement-cible-absente",
        "title": "Lien d’évitement vers une cible absente",
        "rules": ["RGAA-12-7-SKIPLINK-001", "RGAA-12-7-SKIPLINK-HUMAN-002"],
        "analysis": (
            "Sur P07 et P08, le premier lien d’accès rapide pointe vers `#content`, alors qu’aucun élément ne "
            "porte cet identifiant. L’activation ne rejoint donc pas la zone de contenu principal. Sur P08, la "
            "revue du test 12.7.2 confirme aussi que le mécanisme répété n’est pas fonctionnel. Les deux tests "
            "relèvent de la même cause racine et sont réunis dans un seul ticket."
        ),
        "impact": (
            "Les personnes naviguant au clavier ne peuvent pas éviter l’en-tête et doivent parcourir tous ses "
            "contrôles avant d’atteindre le contenu principal."
        ),
        "solutions": [
            {
                "title": "Créer la cible sur la zone principale (recommandée)",
                "text": (
                    "Conserver la destination `#content` et appliquer cet identifiant à l’unique élément `main` "
                    "visible. Si le navigateur ne déplace pas le focus de façon fiable, prévoir un "
                    "repositionnement contrôlé et testé."
                ),
                "code": """<div class="fr-skiplinks">
  <nav class="fr-container" aria-label="Accès rapide">
    <ul class="fr-skiplinks__list">
      <li><a class="fr-link" href="#content">Contenu</a></li>
    </ul>
  </nav>
</div>

<main id="content">
  <!-- contenu principal -->
</main>""",
            },
            {
                "title": "Corriger la destination existante",
                "text": "Si le contenu principal possède déjà un autre identifiant stable, modifier le `href` du lien pour viser exactement cette cible.",
                "code": """<a class="fr-link" href="#contenu-principal">Contenu</a>
<main id="contenu-principal">…</main>""",
            },
        ],
        "dsfr": {
            "component": "Liens d’évitement",
            "rows": [
                ("Lien", "Destination correspondant à une cible réelle", "href=#content sans cible"),
                ("Fonctionnement", "Accès direct au contenu principal", "Activation sans déplacement utile"),
                ("Cause attribuée", "Composant DSFR paramétrable", "Intégration / identifiant de cible"),
            ],
            "links": [
                ("DSFR 1.15.2 — composant skiplink", "https://github.com/GouvernementFR/dsfr/tree/v1.15.2/src/dsfr/component/skiplink"),
            ],
        },
        "verification": [
            "Depuis le haut de P07 et P08, afficher le lien avec Tab puis l’activer avec Entrée.",
            "Vérifier que l’URL reçoit l’ancre attendue et que la lecture reprend au contenu principal.",
            "Contrôler sa position, son ordre et sa visibilité au focus sur les deux pages.",
        ],
    },
    {
        "id": "A-REQUALIFIER-RGAA-002",
        "slug": "description-bandeau-cookies-absente",
        "title": "Description du bandeau de cookies non reliée",
        "rules": ["RGAA-7-1-ARIA-REFERENCE-002"],
        "observations": ["aria-describedby référence #popup-text absent"],
        "delivery_status": "À requalifier avant transmission comme non-conformité",
        "methodological_alert": (
            "Un aria-describedby orphelin ne suffit pas, à lui seul, à établir l’échec de 7.1.1 si le nom, le "
            "rôle, les états et les informations nécessaires restent accessibles. P08 et P09 classent d’ailleurs "
            "ce même signal A_RETESTER. Une vérification fonctionnelle est requise."
        ),
        "analysis": (
            "Le bandeau de consentement cite `popup-text` dans `aria-describedby` sur P01 à P07, mais cette cible "
            "est absente. La relation ne transmet une description que si l’identifiant référencé existe dans le "
            "même document. Le défaut relève du template de consentement commun."
        ),
        "impact": (
            "Le lecteur d’écran ne restitue pas la description attendue du bandeau. La personne peut manquer "
            "l’explication utile avant de choisir ses préférences de cookies."
        ),
        "solutions": [
            {
                "title": "Créer une description utile et la relier (recommandée)",
                "text": "Ajouter un texte utile avec l’identifiant exact `popup-text`, puis conserver `aria-describedby`.",
                "code": """<div id="sliding-popup" role="alertdialog"
     aria-describedby="popup-text" aria-label="Gestion des cookies">
  <p id="popup-text">Ce site utilise des cookies…</p>
  <!-- actions -->
</div>""",
            },
            {
                "title": "Supprimer une référence obsolète",
                "text": "Si le bandeau est autonome sans description dédiée, retirer l’attribut. Ne pas créer un élément vide.",
                "code": """<div id="sliding-popup" role="alertdialog"
     aria-label="Gestion des cookies">
  <!-- contenu complet et autonome -->
</div>""",
            },
        ],
        "dsfr": {
            "component": "Bandeau de consentement",
            "rows": [
                ("Relation de description", "Chaque IDREF cible un élément existant", "popup-text absent"),
                ("Texte d’aide", "Présent et relié lorsqu’il est nécessaire", "Description non restituable"),
                ("Cause attribuée", "Contrat ARIA valide", "Template de consentement intégré"),
            ],
            "links": [
                ("DSFR 1.15.2 — composant consent", "https://github.com/GouvernementFR/dsfr/tree/v1.15.2/src/dsfr/component/consent"),
            ],
        },
        "verification": [
            "Contrôler que `popup-text` existe et reste unique si `aria-describedby` est conservé.",
            "Inspecter la description calculée du bandeau.",
            "Vérifier la restitution avec un lecteur d’écran réel.",
        ],
    },
    {
        "id": "A-REQUALIFIER-RGAA-003",
        "slug": "aide-televersement-non-reliee",
        "title": "Aide du champ de téléversement non reliée",
        "rules": ["RGAA-7-1-ARIA-REFERENCE-002"],
        "observations": ["aria-describedby référence #edit-document--description absent"],
        "delivery_status": "À requalifier avant transmission comme non-conformité",
        "methodological_alert": (
            "La relation orpheline est un défaut technique observable, mais le test 7.1.1 exige de démontrer que "
            "l’information est nécessaire au composant. Requalifier après contrôle du texte d’aide visible et, "
            "si nécessaire, du test 11.10.5 relatif aux indications de format."
        ),
        "analysis": (
            "Sur P06, le champ de téléversement cite `edit-document--description` dans `aria-describedby`, mais "
            "aucun élément ne porte cet identifiant. Cette cause est propre au composant de téléversement et "
            "nécessite un correctif distinct du bandeau de cookies."
        ),
        "impact": (
            "Les formats, limites ou consignes attendus ne sont pas associés au champ pour une personne utilisant "
            "un lecteur d’écran."
        ),
        "solutions": [
            {
                "title": "Créer le texte d’aide référencé (recommandée)",
                "text": "Ajouter un texte d’aide utile avec l’identifiant exact généré par le champ.",
                "code": """<label class="fr-label" for="edit-document-upload">Document</label>
<input id="edit-document-upload" type="file"
       aria-describedby="edit-document--description">
<p id="edit-document--description" class="fr-hint-text">
  Formats acceptés : JPG, PNG ou PDF.
</p>""",
            },
            {
                "title": "Référencer le texte d’aide déjà présent",
                "text": "Si une aide existe sous un autre identifiant, corriger la valeur de `aria-describedby` au lieu de dupliquer le texte.",
                "code": """<input id="edit-document-upload" type="file"
       aria-describedby="document-formats-aide">
<p id="document-formats-aide" class="fr-hint-text">Formats acceptés…</p>""",
            },
        ],
        "dsfr": {
            "component": "Champ de téléversement",
            "rows": [
                ("Relation de description", "IDREF vers une aide existante", "edit-document--description absent"),
                ("Consignes", "Reliées au champ", "Aide non restituable"),
                ("Cause attribuée", "Composant paramétrable", "Génération du champ Drupal"),
            ],
            "links": [
                ("DSFR 1.15.2 — composant upload", "https://github.com/GouvernementFR/dsfr/tree/v1.15.2/src/dsfr/component/upload"),
            ],
        },
        "verification": [
            "Contrôler que chaque identifiant cité par le champ existe et reste unique.",
            "Inspecter la description accessible calculée pour `#edit-document-upload`.",
            "Tester le champ avec un lecteur d’écran et vérifier que l’aide est annoncée une seule fois.",
        ],
    },
    {
        "id": "NC-TRANSVERSE-005",
        "slug": "identifiant-button-menu-duplique",
        "title": "Identifiant button-menu dupliqué dans l’en-tête",
        "rules": ["RGAA-8-2-ID-UNIQUE-001"],
        "observations": ["id=button-menu présent 2 fois"],
        "analysis": (
            "Sur les neuf pages, le bouton d’ouverture et le bouton de fermeture du menu partagent "
            "l’identifiant `button-menu`. Un identifiant doit désigner un seul élément dans le document. Cette "
            "cause relève du template d’en-tête et possède un correctif distinct des autres duplications."
        ),
        "impact": "Les scripts ou relations qui ciblent `button-menu` peuvent résoudre le mauvais bouton et produire un comportement imprévisible.",
        "solutions": [
            {
                "title": "Donner un identifiant distinct à chaque bouton (recommandée)",
                "text": "Conserver `aria-controls=\"modal-menu\"` mais utiliser deux identifiants uniques, ou retirer les `id` s’ils ne sont référencés nulle part.",
                "code": """<button id="button-menu-open" aria-controls="modal-menu">Menu</button>
<button id="button-menu-close" aria-controls="modal-menu">Fermer</button>""",
            },
        ],
        "dsfr": {
            "component": "En-tête",
            "rows": [
                ("Boutons du menu", "Identifiants uniques par contrôle", "button-menu présent deux fois"),
                ("Cible contrôlée", "aria-controls peut viser la même modale", "modal-menu partagé, ce qui est attendu"),
                ("Cause attribuée", "Instances distinctes", "Template d’en-tête intégré"),
            ],
            "links": [("DSFR 1.15.2 — composant header", "https://github.com/GouvernementFR/dsfr/tree/v1.15.2/src/dsfr/component/header")],
        },
        "verification": [
            "Vérifier l’unicité de `button-menu` sur les neuf pages.",
            "Rejouer l’ouverture et la fermeture du menu sur desktop et mobile.",
            "Contrôler que les scripts ciblent toujours les bons boutons.",
        ],
    },
    {
        "id": "NC-TRANSVERSE-009",
        "slug": "identifiant-bouton-megamenu-duplique",
        "title": "Identifiant de fermeture du méga-menu dupliqué",
        "rules": ["RGAA-8-2-ID-UNIQUE-001"],
        "observations": ["id=button-2835 présent 2 fois"],
        "analysis": (
            "Sur les neuf pages, deux boutons de fermeture appartenant à des méga-menus différents partagent "
            "l’identifiant `button-2835`. La correction doit être appliquée dans la boucle qui génère les entrées "
            "de navigation, indépendamment du correctif de l’en-tête."
        ),
        "impact": "Une association ou un script fondé sur cet identifiant peut agir sur le mauvais méga-menu.",
        "solutions": [
            {
                "title": "Dériver l’identifiant de la cible contrôlée (recommandée)",
                "text": "Générer un identifiant stable et unique depuis la clé métier de chaque entrée de navigation.",
                "code": """<button id="button-menu-la-douane" aria-controls="menu-la-douane">Fermer</button>
<button id="button-menu-services" aria-controls="menu-services-aides">Fermer</button>""",
            },
        ],
        "dsfr": {
            "component": "Navigation / méga-menu",
            "rows": [
                ("Boutons de fermeture", "Un identifiant par instance", "button-2835 partagé par deux menus"),
                ("Génération", "Clé propre à l’entrée", "Constante réutilisée"),
                ("Cause attribuée", "Template paramétré", "Boucle de navigation Drupal"),
            ],
            "links": [("DSFR 1.15.2 — composant navigation", "https://github.com/GouvernementFR/dsfr/tree/v1.15.2/src/dsfr/component/navigation")],
        },
        "verification": [
            "Vérifier l’unicité de tous les boutons de fermeture des méga-menus.",
            "Ouvrir et fermer chaque entrée de navigation au clavier.",
            "Contrôler la cohérence entre chaque bouton et son `aria-controls`.",
        ],
    },
    {
        "id": "NC-TRANSVERSE-010",
        "slug": "identifiant-liens-footer-duplique",
        "title": "Identifiant partagé par les liens du pied de page",
        "rules": ["RGAA-8-2-ID-UNIQUE-001"],
        "observations": ["id=footer__bottom-link présent 6 fois"],
        "analysis": (
            "Sur les neuf pages, cinq liens et le bouton des paramètres d’affichage partagent l’identifiant "
            "`footer__bottom-link`. Le style est déjà porté par la classe du même nom ; ces identifiants ne sont "
            "pas nécessaires et doivent être traités dans le template de pied de page."
        ),
        "impact": "Les ancres, scripts et relations fondés sur cet identifiant peuvent cibler un contrôle arbitraire du pied de page.",
        "solutions": [
            {
                "title": "Supprimer les identifiants inutiles (recommandée)",
                "text": "Conserver la classe réutilisable pour le style et retirer l’attribut `id` de chaque entrée non référencée.",
                "code": """<a href="/plan-du-site" class="fr-footer__bottom-link">Plan du site</a>
<a href="/accessibilite" class="fr-footer__bottom-link">Accessibilité</a>
<button aria-controls="fr-theme-modal"
        class="fr-icon-theme-fill fr-btn--icon-left fr-footer__bottom-link">
  Paramètres d’affichage
</button>""",
            },
        ],
        "dsfr": {
            "component": "Pied de page",
            "rows": [
                ("Style partagé", "Classe CSS réutilisable", "Classe et id identiques"),
                ("Identifiants", "Absents s’ils ne sont pas référencés", "footer__bottom-link répété six fois"),
                ("Cause attribuée", "Template de pied de page", "Attribut id ajouté à chaque entrée"),
            ],
            "links": [("DSFR 1.15.2 — composant footer", "https://github.com/GouvernementFR/dsfr/tree/v1.15.2/src/dsfr/component/footer")],
        },
        "verification": [
            "Vérifier l’absence de `id=\"footer__bottom-link\"` dupliqué sur les neuf pages.",
            "Contrôler visuellement que les styles du pied de page sont inchangés.",
            "Ouvrir les paramètres d’affichage et vérifier leur fonctionnement.",
        ],
    },
    {
        "id": "NC-TRANSVERSE-006",
        "slug": "nom-anglais-bandeau-cookies",
        "title": "Nom anglais du bandeau de cookies sans langue déclarée",
        "rules": ["RGAA-8-7-LANGUAGE-CHANGE-001"],
        "observations": ["Intitulé anglais sans lang=en : Cookie compliance banner"],
        "analysis": (
            "Le bandeau de cookies porte le nom accessible anglais « Cookie compliance banner » alors que les "
            "pages sont déclarées en français. Aucun changement de langue ne s’applique à ce nom. Cette cause "
            "relève du template de consentement commun à P01 à P08."
        ),
        "impact": "Une synthèse vocale française peut prononcer ce nom avec des règles phonétiques inadaptées.",
        "solutions": [
            {
                "title": "Traduire le nom du bandeau (recommandée)",
                "text": "Employer un nom accessible français cohérent avec le titre visible du composant.",
                "code": """<div id="sliding-popup" role="alertdialog"
     aria-label="Bandeau de gestion des cookies">…</div>""",
            },
            {
                "title": "Borner la langue au nom anglais si celui-ci est conservé",
                "text": (
                    "Faire porter le nom par un texte dédié déclaré en anglais avec `aria-labelledby`. Ne pas "
                    "appliquer `lang=\"en\"` au dialogue entier, car son contenu reste en français."
                ),
                "code": """<div id="sliding-popup" role="alertdialog"
     aria-labelledby="cookie-banner-name">
  <span id="cookie-banner-name" class="fr-sr-only" lang="en">
    Cookie compliance banner
  </span>
  … contenu du bandeau en français …
</div>""",
            },
        ],
        "dsfr": {
            "component": "Bandeau de consentement",
            "rows": [
                ("Langue de page", "Français", "Français"),
                ("Nom accessible", "Français ou langue déclarée", "Anglais sans lang=en"),
                ("Cause attribuée", "Libellé paramétrable", "Traduction du template de consentement"),
            ],
            "links": [("DSFR 1.15.2 — composant consent", "https://github.com/GouvernementFR/dsfr/tree/v1.15.2/src/dsfr/component/consent")],
        },
        "verification": [
            "Contrôler le nom accessible du bandeau sur P01 à P08.",
            "Vérifier qu’il est traduit ou qu’un texte dédié `lang=\"en\"` fournit le nom via `aria-labelledby`.",
            "Vérifier que le contenu français du dialogue n’hérite pas de la langue anglaise.",
            "Écouter le nom avec un lecteur d’écran configuré en français.",
        ],
    },
    {
        "id": "NC-TRANSVERSE-011",
        "slug": "lien-english-content-sans-langue",
        "title": "Lien English content sans langue déclarée",
        "rules": ["RGAA-8-7-LANGUAGE-CHANGE-001"],
        "observations": ["Intitulé anglais sans lang=en : English content"],
        "analysis": (
            "Le lien « English content » est intégré dans des pages françaises sans attribut `lang=\"en\"`. "
            "Il apparaît dans plusieurs emplacements rendus de P02 à P08. Il s’agit d’un passage anglais explicite "
            "et non d’un nom propre."
        ),
        "impact": "Une synthèse vocale française peut rendre cette destination moins compréhensible.",
        "solutions": [
            {
                "title": "Déclarer la langue du lien anglais (recommandée)",
                "text": "Ajouter `lang=\"en\"` sur toutes les occurrences rendues du lien.",
                "code": """<a href="/english-content" class="fr-nav__link" lang="en">
  English content
</a>""",
            },
            {
                "title": "Fournir un intitulé français",
                "text": "Lorsque le contexte éditorial le permet, traduire l’intitulé du lien.",
                "code": """<a href="/english-content" class="fr-nav__link">
  Contenus en anglais
</a>""",
            },
        ],
        "dsfr": {
            "component": "Navigation et liens éditoriaux",
            "rows": [
                ("Passage anglais", "Langue déclarée au plus près", "Aucun lang=en"),
                ("Occurrences", "Configuration cohérente dans tous les menus", "Libellé répété sans langue"),
                ("Cause attribuée", "Contenu paramétrable", "Configuration éditoriale Drupal"),
            ],
            "links": [("DSFR 1.15.2 — composant navigation", "https://github.com/GouvernementFR/dsfr/tree/v1.15.2/src/dsfr/component/navigation")],
        },
        "verification": [
            "Rechercher « English content » dans P02 à P08.",
            "Vérifier chaque occurrence, y compris les variantes de navigation masquées puis ouvertes.",
            "Écouter le lien avec un lecteur d’écran configuré en français.",
        ],
    },
    {
        "id": "A-REQUALIFIER-RGAA-004",
        "slug": "libelles-french-customs-noms-propres",
        "title": "Libellés French Customs à requalifier comme noms propres",
        "rules": ["RGAA-8-7-LANGUAGE-CHANGE-001"],
        "observations": [
            "Intitulé anglais sans lang=en : French Customs for business",
            "Intitulé anglais sans lang=en : French Customs presentation",
        ],
        "delivery_status": "À requalifier avant transmission comme non-conformité",
        "methodological_alert": (
            "Le test 8.7.1 exclut notamment les noms propres. Il faut décider éditorialement si « French Customs » "
            "est un nom de service ou de rubrique à traiter comme nom propre avant de maintenir ces constats en NC."
        ),
        "analysis": (
            "Les rapports sources classent « French Customs for business » et « French Customs presentation » "
            "comme passages anglais sans langue déclarée. Ces chaînes sont répétées dans la navigation de P02 à "
            "P07. Leur statut RGAA dépend toutefois de l’exception relative aux noms propres."
        ),
        "impact": "Sans langue déclarée, une synthèse vocale française peut appliquer une prononciation inadaptée ; l’applicabilité RGAA reste à arbitrer.",
        "solutions": [
            {
                "title": "Déclarer la langue si ces libellés sont des passages anglais",
                "text": "Si l’exception de nom propre n’est pas retenue, ajouter `lang=\"en\"` sur toutes les occurrences.",
                "code": """<a href="/professionnels/french-customs-business"
   class="fr-nav__link" lang="en">
  French Customs for business
</a>""",
            },
            {
                "title": "Tracer l’exception de nom propre",
                "text": "Si « French Customs » est le nom propre officiel de la rubrique, documenter l’exception et reclasser les constats concernés.",
                "code": """<!-- Décision éditoriale documentée : nom propre officiel -->
<a href="/professionnels/french-customs-business" class="fr-nav__link">
  French Customs for business
</a>""",
            },
        ],
        "dsfr": {
            "component": "Navigation et liens éditoriaux",
            "rows": [
                ("Langue", "À déclarer pour un passage étranger", "Aucun lang=en"),
                ("Exception", "Nom propre exclu du test 8.7.1", "Qualification non documentée"),
                ("Cause attribuée", "Contenu paramétrable", "Décision éditoriale Drupal"),
            ],
            "links": [("DSFR 1.15.2 — composant navigation", "https://github.com/GouvernementFR/dsfr/tree/v1.15.2/src/dsfr/component/navigation")],
        },
        "verification": [
            "Faire arbitrer le statut de nom propre par l’auditeur et l’équipe éditoriale.",
            "Si l’exception est écartée, vérifier `lang=\"en\"` sur chaque occurrence.",
            "Si l’exception est retenue, consigner la justification et reclasser les constats sources.",
        ],
    },
    {
        "id": "NC-P06-006",
        "slug": "textes-formulaire-anglais-sans-langue",
        "title": "Textes anglais du formulaire sans langue déclarée",
        "rules": ["RGAA-8-7-LANGUAGE-CHANGE-001"],
        "observations": [
            "Intitulé anglais sans lang=en : Maximum 2000 characters",
            "Intitulé anglais sans lang=en : Conditions and submission",
        ],
        "analysis": (
            "Deux textes du formulaire P06 restent en anglais : l’aide « Maximum 2000 characters » et la légende "
            "masquée « Conditions and submission ». Aucun attribut `lang=\"en\"` ne s’applique. Ces textes "
            "relèvent du template du formulaire, distinct des libellés de navigation."
        ),
        "impact": "Les instructions peuvent être mal prononcées et moins bien comprises par une personne utilisant une synthèse vocale française.",
        "solutions": [
            {
                "title": "Traduire les deux textes d’interface (recommandée)",
                "text": "Employer des formulations françaises cohérentes avec le reste du formulaire.",
                "code": """<span class="fr-hint-text">Maximum 2 000 caractères</span>
<legend class="fr-sr-only">Conditions et envoi</legend>""",
            },
            {
                "title": "Déclarer la langue si l’anglais est conservé",
                "text": "Ajouter `lang=\"en\"` directement sur chaque élément concerné.",
                "code": """<span class="fr-hint-text" lang="en">Maximum 2000 characters</span>
<legend class="fr-sr-only" lang="en">Conditions and submission</legend>""",
            },
        ],
        "dsfr": {
            "component": "Formulaire",
            "rows": [
                ("Aides et légendes", "Français ou langue déclarée", "Deux textes anglais sans lang=en"),
                ("Cause attribuée", "Libellés paramétrables", "Traduction du template du formulaire"),
            ],
            "links": [("DSFR 1.15.2 — composant input", "https://github.com/GouvernementFR/dsfr/tree/v1.15.2/src/dsfr/component/input")],
        },
        "verification": [
            "Contrôler les deux formulations dans le DOM rendu de P06.",
            "Vérifier qu’elles sont traduites ou explicitement déclarées en anglais.",
            "Écouter l’aide et la légende avec un lecteur d’écran configuré en français.",
        ],
    },
    {
        "id": "NC-TRANSVERSE-007",
        "slug": "paragraphes-vides-presentation",
        "title": "Paragraphes vides utilisés pour l’espacement",
        "rules": ["RGAA-8-9-EMPTY-PRESENTATION-001"],
        "analysis": (
            "Le bandeau de consentement contient deux paragraphes vides qui produisent une marge de 16 pixels. "
            "Une balise `p` représente un paragraphe de contenu ; elle ne doit pas être créée uniquement pour "
            "obtenir un espacement. Le défaut est répété par le même template sur P01 à P06."
        ),
        "impact": (
            "La structure exposée peut contenir des paragraphes sans contenu et la présentation dépend d’un "
            "balisage sémantique détourné."
        ),
        "solutions": [
            {
                "title": "Supprimer les paragraphes vides et utiliser le CSS (recommandée)",
                "text": "Conserver uniquement le paragraphe utile et appliquer la marge au conteneur ou à ce paragraphe avec une classe DSFR/CSS.",
                "code": """<div class="fr-consent-banner__content fr-mb-2w">
  <p>Ce site utilise des cookies afin de vous proposer…</p>
</div>""",
            }
        ],
        "dsfr": {
            "component": "Bandeau de consentement",
            "rows": [
                ("Paragraphes", "Contenu textuel réel", "Deux éléments p vides"),
                ("Espacement", "Classes utilitaires ou CSS", "Marge portée par des paragraphes vides"),
                ("Cause attribuée", "Structure du composant", "Template de consentement intégré"),
            ],
            "links": [
                ("DSFR 1.15.2 — composant consent", "https://github.com/GouvernementFR/dsfr/tree/v1.15.2/src/dsfr/component/consent"),
            ],
        },
        "verification": [
            "Inspecter le DOM rendu du bandeau sur P01 à P06.",
            "Vérifier qu’aucun paragraphe vide ne sert à créer une marge.",
            "Désactiver les styles et contrôler que la structure conserve son sens.",
        ],
    },
    {
        "id": "NC-TRANSVERSE-008",
        "slug": "type-link-invalide",
        "title": "Valeur type=link invalide sur un lien",
        "rules": ["RGAA-8-2-ANCHOR-TYPE-002"],
        "analysis": (
            "Le lien « Nous rejoindre » porte `type=\"link\"` sur P05 à P09. Pour un élément `a`, l’attribut "
            "`type` décrit le type MIME de la ressource cible ; la valeur `link` n’est pas un type MIME. "
            "L’attribut est inutile pour donner le rôle de lien, déjà fourni par la balise et son `href`."
        ),
        "impact": (
            "Le code source généré n’est pas valide. Cette erreur réduit la robustesse d’interprétation et peut "
            "perturber des outils qui exploitent le type déclaré de la ressource."
        ),
        "solutions": [
            {
                "title": "Supprimer l’attribut type (recommandée)",
                "text": "La ressource étant une page HTML ordinaire, supprimer l’attribut ajouté par le template de navigation.",
                "code": """<a id="menu-nous-rejoindre"
   href="/devenir-douanier"
   class="fr-nav__link">
  Nous rejoindre
</a>""",
            },
            {
                "title": "Déclarer un type MIME réel uniquement si nécessaire",
                "text": "Si la cible possède un type utile et connu, employer une valeur MIME valide telle que `application/pdf`.",
                "code": """<a href="/document.pdf" type="application/pdf">Télécharger le document</a>""",
            },
        ],
        "dsfr": {
            "component": "Navigation",
            "rows": [
                ("Rôle du lien", "Fourni par a[href]", "Attribut type=link ajouté"),
                ("Attribut type", "Absent ou type MIME valide", "Valeur non MIME"),
                ("Cause attribuée", "Lien HTML standard", "Template de navigation intégré"),
            ],
            "links": [
                ("DSFR 1.15.2 — composant navigation", "https://github.com/GouvernementFR/dsfr/tree/v1.15.2/src/dsfr/component/navigation"),
            ],
        },
        "verification": [
            "Rechercher `a[type]` dans le DOM rendu de P05 à P09.",
            "Supprimer `type=\"link\"` et valider le code HTML généré.",
            "Vérifier que le lien « Nous rejoindre » conserve son fonctionnement.",
        ],
    },
    {
        "id": "NC-P06-001",
        "slug": "attributs-size-presentation",
        "title": "Attributs size utilisés pour dimensionner les champs",
        "rules": ["RGAA-10-1-PRESENTATIONAL-ATTRIBUTE-002"],
        "analysis": (
            "Sept champs du formulaire P06 utilisent l’attribut HTML `size` avec les valeurs 22, 40 ou 60. "
            "Pour le test 10.1.2, `size` est un attribut de présentation interdit, sauf sur l’élément `select`. "
            "La largeur des champs doit être pilotée par les feuilles de styles."
        ),
        "impact": (
            "La présentation dépend du code HTML au lieu des styles. Elle devient plus difficile à adapter aux "
            "différents écrans, zooms et préférences d’affichage."
        ),
        "solutions": [
            {
                "title": "Retirer size et dimensionner avec les styles (recommandée)",
                "text": "Supprimer les sept attributs `size` du template Drupal et utiliser les classes de grille ou une règle CSS adaptée au contexte.",
                "code": """<label class="fr-label" for="edit-nom">Nom</label>
<input class="fr-input" autocomplete="family-name"
       id="edit-nom" name="Nom" type="text" maxlength="128">""",
            }
        ],
        "dsfr": {
            "component": "Champ de saisie / téléversement",
            "rows": [
                ("Largeur", "Contrôlée par classes et CSS", "Attributs size sur sept champs"),
                ("Code HTML", "Sémantique et contraintes de saisie", "Présentation mêlée au balisage"),
                ("Cause attribuée", "Composants stylés", "Génération du formulaire Drupal"),
            ],
            "links": [
                ("DSFR 1.15.2 — composant input", "https://github.com/GouvernementFR/dsfr/tree/v1.15.2/src/dsfr/component/input"),
                ("DSFR 1.15.2 — composant upload", "https://github.com/GouvernementFR/dsfr/tree/v1.15.2/src/dsfr/component/upload"),
            ],
        },
        "verification": [
            "Contrôler l’absence de `size` sur les sept champs inventoriés.",
            "Tester la mise en page à 320 px, à 200 % de zoom et avec l’agrandissement des textes.",
            "Vérifier que les contraintes métier comme `maxlength` restent inchangées.",
        ],
    },
    {
        "id": "NC-P06-002",
        "slug": "champ-entreprise-optionnel-non-indique",
        "title": "Champ entreprise optionnel annoncé comme obligatoire",
        "rules": ["RGAA-11-10-REQUIRED-INDICATION-HUMAN-001"],
        "methodological_alert": (
            "La note technique du critère 11.10 autorise l’instruction globale « tous les champs sont "
            "obligatoires sauf… » uniquement si chaque champ facultatif porte une mention visible dans son "
            "libellé ou sa légende, et si les autres champs conservent required ou aria-required=true."
        ),
        "analysis": (
            "L’instruction générale annonce que tous les champs sont obligatoires sauf mention contraire. Dans "
            "la variante « Un professionnel », le champ « Nom de l’entreprise » est visible, accepte une valeur "
            "vide et ne porte aucune mention « optionnel ». L’information donnée avant la saisie est donc "
            "contradictoire avec la validation réelle du formulaire."
        ),
        "impact": (
            "La personne peut croire à tort qu’elle doit fournir le nom de son entreprise, ce qui augmente la "
            "charge de saisie et peut conduire à communiquer une donnée non requise."
        ),
        "solutions": [
            {
                "title": "Indiquer explicitement que le champ est optionnel (recommandée)",
                "text": "Conserver le comportement métier actuel et ajouter une mention visible dans l’étiquette du champ.",
                "code": """<label class="fr-label" for="edit-societe">
  Nom de l’entreprise
  <span class="fr-hint-text">Optionnel</span>
</label>
<input class="fr-input" id="edit-societe" name="Societe" type="text">""",
            },
            {
                "title": "Rendre le champ réellement obligatoire après décision métier",
                "text": "Si la donnée est indispensable, ajouter l’indication visible et l’attribut `required`. Ne pas appliquer cette option sans validation métier.",
                "code": """<label class="fr-label" for="edit-societe">
  Nom de l’entreprise <span aria-hidden="true">*</span>
</label>
<input class="fr-input" id="edit-societe" name="Societe"
       type="text" required>""",
            },
        ],
        "dsfr": {
            "component": "Champ de saisie",
            "rows": [
                ("Information avant saisie", "Caractère obligatoire ou optionnel cohérent", "Instruction globale inexacte"),
                ("Validation native", "Cohérente avec l’indication visible", "Le champ accepte une valeur vide"),
                ("Cause attribuée", "Libellé paramétrable", "Règle métier / template du formulaire"),
            ],
            "links": [
                ("DSFR 1.15.2 — composant input", "https://github.com/GouvernementFR/dsfr/tree/v1.15.2/src/dsfr/component/input"),
            ],
        },
        "verification": [
            "Sélectionner la variante « Un professionnel ».",
            "Vérifier que le caractère optionnel ou obligatoire est visible avant la saisie.",
            "Soumettre le formulaire sans valeur après validation métier et contrôler la cohérence du comportement.",
        ],
    },
    {
        "id": "NC-P06-003",
        "slug": "autocomplete-entreprise-absent",
        "title": "Finalité du champ entreprise non déclarée",
        "rules": ["RGAA-11-13-AUTOCOMPLETE-HUMAN-001"],
        "analysis": (
            "Dans la variante « Un professionnel », le champ « Nom de l’entreprise » collecte une information "
            "sur l’utilisateur mais ne possède aucun attribut `autocomplete`. La valeur standard "
            "`organization` permet aux aides à la saisie d’identifier cette finalité."
        ),
        "impact": (
            "Les outils de remplissage automatique et les adaptations personnalisées ne peuvent pas reconnaître "
            "le nom de l’organisation attendu dans ce champ."
        ),
        "solutions": [
            {
                "title": "Ajouter autocomplete=organization (recommandée)",
                "text": "Déclarer la finalité avec la valeur normalisée correspondant au nom d’une entreprise ou organisation.",
                "code": """<label class="fr-label" for="edit-societe">Nom de l’entreprise</label>
<input class="fr-input" id="edit-societe" name="Societe"
       type="text" autocomplete="organization">""",
            }
        ],
        "dsfr": {
            "component": "Champ de saisie",
            "rows": [
                ("Finalité", "Attribut autocomplete pertinent", "Attribut absent"),
                ("Valeur attendue", "organization", "Aucune"),
                ("Cause attribuée", "Attribut HTML supporté", "Configuration du champ Drupal"),
            ],
            "links": [
                ("DSFR 1.15.2 — composant input", "https://github.com/GouvernementFR/dsfr/tree/v1.15.2/src/dsfr/component/input"),
                ("HTML — valeurs autocomplete", "https://html.spec.whatwg.org/multipage/form-control-infrastructure.html#autofill"),
            ],
        },
        "verification": [
            "Afficher la variante « Un professionnel » et inspecter `#edit-societe`.",
            "Vérifier la présence exacte de `autocomplete=\"organization\"`.",
            "Tester avec un gestionnaire de saisie automatique compatible.",
        ],
    },
    {
        "id": "A-REQUALIFIER-RGAA-001",
        "slug": "ouverture-nouvelle-fenetre-non-annoncee",
        "title": "Ouvertures de liens dans une nouvelle fenêtre à requalifier",
        "rules": ["RGAA-13-2-NEW-WINDOW-HUMAN-001"],
        "delivery_status": "À requalifier avant transmission comme non-conformité",
        "analysis": (
            "Les rapports sources classent sous le test 13.2.1 des liens `target=\"_blank\"` dont le nom "
            "accessible n’annonce pas la nouvelle fenêtre. Cette recommandation est utile, mais le test RGAA "
            "13.2.1 vérifie l’absence d’ouverture automatique au chargement, sans action de l’utilisateur. "
            "L’activation d’un lien constitue une action. Si aucune fenêtre ne s’ouvre automatiquement, le "
            "mapping en non-conformité 13.2.1 doit être retiré ou remplacé par une recommandation."
        ),
        "impact": (
            "Une nouvelle fenêtre non annoncée peut surprendre certaines personnes. Cet impact justifie une "
            "amélioration, mais ne suffit pas à établir l’échec du test 13.2.1 décrit dans la méthode officielle."
        ),
        "solutions": [
            {
                "title": "Éviter l’ouverture forcée (recommandée)",
                "text": "Supprimer `target=\"_blank\"` lorsque l’ouverture dans un nouvel onglet n’est pas indispensable.",
                "code": """<a href="https://www.facebook.com/douanefrancaise/"
   rel="external" class="fr-btn--facebook fr-btn">
  Facebook
</a>""",
            },
            {
                "title": "Annoncer le changement de contexte si target=_blank est conservé",
                "text": "Ajouter une mention perceptible dans le nom du lien et conserver `rel=\"noopener\"`.",
                "code": """<a href="https://www.facebook.com/douanefrancaise/"
   target="_blank" rel="noopener external"
   class="fr-btn--facebook fr-btn">
  Facebook <span class="fr-sr-only">— nouvelle fenêtre</span>
</a>""",
            },
        ],
        "dsfr": {
            "component": "Liens externes / suivi sur les réseaux sociaux",
            "rows": [
                ("Ouverture", "Même fenêtre par défaut", "target=_blank"),
                ("Information", "Changement de contexte explicite s’il est imposé", "Mention absente selon la mesure"),
                ("Qualification RGAA", "13.2.1 vise l’ouverture automatique", "Mapping source à revalider"),
            ],
            "links": [
                ("DSFR 1.15.2 — composant follow", "https://github.com/GouvernementFR/dsfr/tree/v1.15.2/src/dsfr/component/follow"),
            ],
        },
        "verification": [
            "Recharger chaque page sans action et vérifier qu’aucune nouvelle fenêtre ne s’ouvre.",
            "Si aucune ouverture automatique n’existe, reclasser ces constats en recommandation hors NC 13.2.1.",
            "Si `target=_blank` est maintenu, vérifier que le changement de contexte est annoncé de façon cohérente.",
        ],
        "methodological_alert": (
            "Ne pas transmettre ce fichier comme non-conformité RGAA 13.2.1 sans arbitrage d’un auditeur. "
            "La méthode officielle locale consultée valide le test lorsqu’aucune fenêtre ne s’ouvre au chargement."
        ),
    },
]


def matches_spec(finding: dict[str, Any], spec: dict[str, Any]) -> bool:
    if finding["rule_id"] not in spec["rules"]:
        return False
    if "observations" in spec and finding.get("observed") not in spec["observations"]:
        return False
    if "pages_filter" in spec and finding.get("page") not in spec["pages_filter"]:
        return False
    return True


def first_finding(findings: list[dict[str, Any]], rule: str, *, selector: str | None = None) -> dict[str, Any]:
    for finding in findings:
        if finding["rule_id"] != rule:
            continue
        if selector is not None and finding.get("selector") != selector:
            continue
        return finding
    raise KeyError(f"Constat introuvable : {rule} / {selector}")


def tag_containing(code: str, marker: str) -> str:
    position = code.find(marker)
    if position < 0:
        return code.strip()[:1200]
    start = code.rfind("<", 0, position)
    if start < 0:
        start = 0
    end = code.find(">", position)
    if end < 0:
        end = min(len(code) - 1, position + 600)
    # Si le marqueur est du texte, inclure sa balise fermante proche.
    if position > code.find(">", start, position) >= 0:
        closing_start = code.find("</", position)
        closing_end = code.find(">", closing_start + 2) if closing_start >= 0 else -1
        if 0 <= closing_end - start <= 1200:
            end = closing_end
    return code[start : end + 1].strip()


def supporting_new_window_code() -> str:
    source = archive_for("P02") / "dsfr/preuves/P02/attempt-004/evidence.json"
    data = json.loads(source.read_text(encoding="utf-8"))
    candidates: list[str] = []

    def walk(value: Any) -> None:
        if isinstance(value, dict):
            for child in value.values():
                walk(child)
        elif isinstance(value, list):
            for child in value:
                walk(child)
        elif isinstance(value, str) and "target=\"_blank\"" in value and "<a " in value:
            candidates.append(value)

    walk(data)
    for candidate in candidates:
        match = re.search(r'<a\b[^>]*id="rs-facebook"[^>]*>.*?</a>', candidate, flags=re.S)
        if match:
            return match.group(0).strip()
    raise RuntimeError("Exemple target=_blank introuvable dans la preuve P02")


def observed_code_samples(spec: dict[str, Any], findings: list[dict[str, Any]], all_findings: list[dict[str, Any]]) -> list[tuple[str, str]]:
    rules = set(spec["rules"])
    key = spec["id"]
    samples: list[tuple[str, str]] = []

    if key == "NC-TRANSVERSE-001":
        finding = first_finding(findings, "RGAA-10-8-HIDDEN-FOCUS-001")
        code = finding["observed_code"]
        ancestor = code.split("Ancêtre masqué:", 1)[-1].strip()
        samples.append(("P01 — formulaire de recherche et état observé", ancestor))
    elif key in {"NC-P06-004", "NC-P09-001"}:
        finding = findings[0]
        samples.append((f"{finding['page']} — dialogue observé", finding["observed_code"].strip()))
    elif key == "NC-TRANSVERSE-003":
        finding = next(item for item in findings if item["rule_id"] == "RGAA-12-7-SKIPLINK-001")
        samples.append(("P07/P08 — lien sans cible correspondante", finding["observed_code"].strip()))
    elif key in {"A-REQUALIFIER-RGAA-002", "A-REQUALIFIER-RGAA-003"}:
        finding = findings[0]
        marker_match = re.search(r"#([^ ]+) absent", finding.get("observed", ""))
        marker = marker_match.group(1) if marker_match else finding.get("selector", "")
        samples.append((f"Référence absente : {marker}", tag_containing(finding["observed_code"], marker)))
    elif key in {"NC-TRANSVERSE-005", "NC-TRANSVERSE-009", "NC-TRANSVERSE-010"}:
        seen: set[str] = set()
        for finding in findings:
            observation = finding["observed"]
            if observation not in seen:
                seen.add(observation)
                samples.append((observation, finding["observed_code"].strip()))
    elif key in {"NC-TRANSVERSE-006", "NC-TRANSVERSE-011", "A-REQUALIFIER-RGAA-004", "NC-P06-006"}:
        seen = set()
        for finding in findings:
            observation = finding["observed"]
            if observation in seen:
                continue
            seen.add(observation)
            phrase = observation.split(": ", 1)[-1]
            samples.append((observation, tag_containing(finding["observed_code"], phrase)))
    elif key == "NC-TRANSVERSE-007":
        for code in unique([item["observed_code"].strip() for item in findings]):
            samples.append(("Paragraphe vide observé", code))
    elif key == "NC-TRANSVERSE-008":
        samples.append(("Lien de navigation observé", findings[0]["observed_code"].strip()))
    elif key == "NC-P06-001":
        seen = set()
        for finding in findings:
            observation = finding["observed"]
            if observation not in seen:
                seen.add(observation)
                samples.append((observation, finding["observed_code"].strip()))
    elif key in {"NC-P06-002", "NC-P06-003"}:
        support = first_finding(
            [item for item in all_findings if item["rule_id"] == "RGAA-10-1-PRESENTATIONAL-ATTRIBUTE-002"],
            "RGAA-10-1-PRESENTATIONAL-ATTRIBUTE-002",
            selector="#edit-societe",
        )
        code = support["observed_code"].strip()
        label = "P06 — champ Société observé dans la collecte initiale"
        if key == "NC-P06-002":
            code += (
                "\n<!-- État interactif mesuré après sélection « Un professionnel » :\n"
                "     instruction globale : « Sauf mention contraire, tous les champs sont obligatoires. » ;\n"
                "     visible=true ; required=false ; aria-required absent ;\n"
                "     valeur vide acceptée ; aucune mention « optionnel ». -->"
            )
            label = "P06 — champ Société et état interactif mesuré"
        samples.append((label, code))
    elif key == "A-REQUALIFIER-RGAA-001":
        samples.append(("P02 — exemple de lien mesuré", supporting_new_window_code()))
    else:
        for finding in findings[:3]:
            samples.append((finding["page"], finding["observed_code"].strip()))

    deduplicated: list[tuple[str, str]] = []
    seen_codes: set[str] = set()
    for label, code in samples:
        code = code.strip()
        if code and code not in seen_codes:
            seen_codes.add(code)
            deduplicated.append((label, code))
    return deduplicated


def group_pages(findings: list[dict[str, Any]]) -> list[dict[str, str]]:
    by_id: dict[str, dict[str, str]] = {}
    for finding in findings:
        by_id[finding["page"]] = {
            "id": finding["page"],
            "name": finding["page_name"],
            "url": finding["page_url"],
        }
    return [by_id[key] for key in sorted(by_id)]


def criterion_lines(spec_findings: list[dict[str, Any]], criteria: dict[str, dict[str, str]]) -> list[tuple[str, str]]:
    ids = sorted({item["criterion"] for item in spec_findings}, key=lambda value: [int(x) for x in value.split(".")])
    return [(criterion, criteria[criterion]["title"]) for criterion in ids]


def test_lines(spec_findings: list[dict[str, Any]], tests: dict[str, dict[str, str]]) -> list[tuple[str, str]]:
    ids = sorted({item["test"] for item in spec_findings}, key=lambda value: [int(x) for x in value.split(".")])
    return [(test, tests[test]["title"]) for test in ids]


def render_markdown(
    spec: dict[str, Any],
    findings: list[dict[str, Any]],
    all_findings: list[dict[str, Any]],
    criteria: dict[str, dict[str, str]],
    tests: dict[str, dict[str, str]],
) -> str:
    pages = group_pages(findings)
    criteria_rows = criterion_lines(findings, criteria)
    test_rows = test_lines(findings, tests)
    severity = max((item["severity"] for item in findings), key=severity_rank)
    status = spec.get("delivery_status", "Préqualification — NC confirmée dans les rapports sources")
    component = spec.get("dsfr", {}).get("component", "Composant personnalisé")
    code_samples = observed_code_samples(spec, findings, all_findings)

    lines = [
        f"# {spec['id']} — {spec['title']}",
        "",
        f"**Statut** : {status}  ",
        f"**Référentiel** : RGAA 4.1.2  ",
        f"**Sévérité** : {severity}  ",
        f"**Justification de sévérité** : {spec['impact']}  ",
        f"**Date** : {DELIVERY_DATE}  ",
        f"**Composant / gabarit** : {component}  ",
        f"**Portée** : {ticket_scope(pages)}  ",
        f"**Pages affectées** : {', '.join(page['id'] for page in pages)}  ",
        f"**Constats sources regroupés** : {len(findings)}",
        "",
        "> Ces conclusions proviennent d’une préqualification instrumentée. Elles ne constituent ni un taux RGAA officiel ni une validation après correction.",
    ]
    if spec.get("methodological_alert"):
        lines += ["", f"> **Alerte méthodologique :** {spec['methodological_alert']}"]
    lines += ["", "---", "", "## Pages et rapports sources", "", "| Page | Nom | URL | Rapport RGAA |", "|---|---|---|---|"]
    for page in pages:
        lines.append(
            f"| {page['id']} | {md_cell(page['name'])} | {page['url']} | "
            f"[{page['id']}-RGAA.html](../../RGAA/{page['id']}-RGAA.html) |"
        )

    lines += ["", "## Références RGAA", ""]
    for criterion, title in criteria_rows:
        lines.append(f"- **Critère {criterion}** — {title}")
    for test, title in test_rows:
        lines.append(f"- **Test {test}** — {title}")

    lines += ["", "---", "", "## Code source constaté", ""]
    for label, code in code_samples:
        lines += [f"### {label}", "", "```html", code, "```", ""]

    lines += [
        "## Inventaire des constats sources",
        "",
        "| Page | Identifiant source | Critère / test | Sélecteur | Observation | Provenance | Preuve principale |",
        "|---|---|---|---|---|---|---|",
    ]
    for finding in sorted(findings, key=lambda item: (item["page"], item["criterion"], item["test"], item["id"])):
        selector = finding.get("selector") or "Mesure documentée"
        evidence = finding_evidence(finding)
        primary_evidence = evidence[0] if evidence else "Intégrée au rapport HTML"
        provenance = finding.get("observed_origin") or (finding.get("qualification") or {}).get("reviewed_by") or "Rapport source"
        lines.append(
            f"| {finding['page']} | `{md_cell(finding['id'])}` | {finding['criterion']} / {finding['test']} | "
            f"`{md_cell(selector)}` | {md_cell(finding['observed'])} | {md_cell(provenance)} | "
            f"`{md_cell(primary_evidence)}` |"
        )

    lines += [
        "",
        "---",
        "",
        "## Analyse du défaut",
        "",
        spec["analysis"],
        "",
        "## Impact utilisateur",
        "",
        spec["impact"],
        "",
        "---",
        "",
        "## Recommandations",
        "",
    ]
    for number, solution in enumerate(spec["solutions"], 1):
        lines += [
            f"### Solution {number} — {solution['title']}",
            "",
            solution["text"],
            "",
            "```html",
            solution["code"],
            "```",
            "",
        ]

    dsfr = spec.get("dsfr")
    if dsfr:
        lines += [
            "## Comparaison avec le composant DSFR",
            "",
            f"**Composant concerné** : {dsfr['component']}",
            "",
            "| Point contrôlé | DSFR / comportement attendu | Site audité |",
            "|---|---|---|",
        ]
        for expected, target, observed in dsfr["rows"]:
            lines.append(f"| {md_cell(expected)} | {md_cell(target)} | {md_cell(observed)} |")
        lines.append("")
        lines.append(
            "Le constat est attribué à l’intégration observée. La présence de classes `fr-*` ne suffit pas à "
            "attribuer le défaut au DSFR natif."
        )

    lines += ["", "---", "", "## Vérification après correction", ""]
    lines.extend(f"- [ ] {item}" for item in spec["verification"])
    lines += [
        "",
        "La correction ne doit être considérée comme clôturée qu’après production d’une nouvelle preuve et recontrôle humain.",
        "",
        "## Références",
        "",
    ]
    for test, _ in test_rows:
        lines.append(f"- [RGAA 4.1.2 — test {test}]({tests[test]['url']})")
    if dsfr:
        for label, url in dsfr["links"]:
            lines.append(f"- [{label}]({url})")
    lines += [
        "- Source factuelle : rapports HTML RGAA livrés pour les pages indiquées et constats `NC_CONFIRMEE` correspondants.",
        "",
    ]
    return "\n".join(lines)


HTML_CSS = """
:root{--blue:#000091;--red:#ce0500;--orange:#b34000;--grey:#f6f6f6;--border:#ddd;--text:#161616}
*{box-sizing:border-box}html{scroll-behavior:smooth}body{margin:0;color:var(--text);font:1rem/1.55 system-ui,-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif;background:#fff}
a{color:var(--blue);text-underline-offset:.18em}a:hover{text-decoration-thickness:.16em}a:focus-visible,button:focus-visible{outline:3px solid #0a76f6;outline-offset:3px}
.skip-link{position:absolute;left:-999rem;top:.5rem;background:#fff;padding:.75rem 1rem;z-index:10}.skip-link:focus{left:.5rem}.container{width:min(76rem,calc(100% - 2rem));margin:auto}
header{border-top:6px solid var(--blue);border-bottom:1px solid var(--border);padding:1.5rem 0}header p{max-width:68rem}.back{display:inline-block;margin-bottom:1rem}
main{padding:2rem 0 4rem}h1{font-size:clamp(2rem,4vw,3rem);line-height:1.15}h2{margin-top:3rem;border-top:2px solid var(--border);padding-top:1.25rem}h3{margin-top:2rem}code{font-family:ui-monospace,SFMono-Regular,Consolas,monospace;background:#eee;padding:.08em .25em;border-radius:.15rem}
pre{overflow:auto;padding:1rem;background:#1e1e1e;color:#f8f8f2;border-radius:.25rem;white-space:pre;tab-size:2}pre code{background:transparent;padding:0;color:inherit}.meta{display:grid;grid-template-columns:repeat(auto-fit,minmax(15rem,1fr));gap:.5rem 1.5rem;padding:1rem;background:var(--grey);border-left:4px solid var(--blue)}.meta p{margin:.2rem 0}
.alert{padding:1rem;border-left:6px solid var(--orange);background:#fff4e5;margin:1.5rem 0}.warning{padding:1rem;border-left:6px solid #e4794a;background:#fff4e5}.badge{display:inline-block;padding:.2rem .55rem;border-radius:1rem;background:#eee;font-weight:700}.badge.blocking{background:#ffe9e9;color:#8f0000}.badge.major{background:#fff4e5;color:#6a3a00}
.table-wrap{overflow-x:auto;margin:1rem 0}table{border-collapse:collapse;width:100%;min-width:45rem}th,td{border:1px solid #bbb;padding:.65rem;text-align:left;vertical-align:top}th{background:#eee}tbody tr:nth-child(even){background:#fafafa}.inventory td:nth-child(2),.inventory td:nth-child(4){font-family:ui-monospace,SFMono-Regular,Consolas,monospace;font-size:.88rem;overflow-wrap:anywhere}
.solution{border-left:4px solid var(--blue);padding-left:1rem;margin:2rem 0}.checklist{list-style:none;padding-left:0}.checklist li{margin:.65rem 0;padding-left:1.8rem;position:relative}.checklist li::before{content:"☐";position:absolute;left:0;font-size:1.2rem}footer{border-top:1px solid var(--border);padding:2rem 0;background:var(--grey)}
.cards{display:grid;grid-template-columns:repeat(auto-fit,minmax(19rem,1fr));gap:1rem}.card{border:1px solid var(--border);padding:1rem}.card h2,.card h3{border:0;margin-top:0;padding-top:0}.count{font-size:2rem;font-weight:700;color:var(--blue)}
@media(max-width:45rem){.container{width:min(100% - 1rem,76rem)}header,main{padding-left:.25rem;padding-right:.25rem}table{min-width:38rem}}
@media(prefers-reduced-motion:reduce){html{scroll-behavior:auto}}
@media print{.skip-link,.back{display:none}.container{width:100%}body{font-size:10pt}a{color:#000}pre{white-space:pre-wrap;color:#000;background:#f5f5f5;border:1px solid #aaa}h2{break-after:avoid}.solution,pre,table{break-inside:avoid}}
"""


def table_html(headers: list[str], rows: list[list[str]], class_name: str = "") -> str:
    heads = "".join(f"<th scope=\"col\">{html.escape(value)}</th>" for value in headers)
    body = "".join("<tr>" + "".join(f"<td>{value}</td>" for value in row) + "</tr>" for row in rows)
    return f'<div class="table-wrap"><table class="{class_name}"><thead><tr>{heads}</tr></thead><tbody>{body}</tbody></table></div>'


def render_html(
    spec: dict[str, Any],
    findings: list[dict[str, Any]],
    all_findings: list[dict[str, Any]],
    criteria: dict[str, dict[str, str]],
    tests: dict[str, dict[str, str]],
) -> str:
    pages = group_pages(findings)
    criteria_rows = criterion_lines(findings, criteria)
    test_rows = test_lines(findings, tests)
    severity = max((item["severity"] for item in findings), key=severity_rank)
    status = spec.get("delivery_status", "Préqualification — NC confirmée dans les rapports sources")
    component = spec.get("dsfr", {}).get("component", "Composant personnalisé")
    code_samples = observed_code_samples(spec, findings, all_findings)
    alert = ""
    if spec.get("methodological_alert"):
        alert = f'<div class="alert" role="note"><strong>Alerte méthodologique :</strong> {inline_html(spec["methodological_alert"])}</div>'

    page_rows = []
    for page in pages:
        page_rows.append([
            html.escape(page["id"]),
            html.escape(page["name"]),
            f'<a href="{html.escape(page["url"])}">{html.escape(page["url"])}</a>',
            f'<a href="../../RGAA/{page["id"]}-RGAA.html">Rapport {page["id"]}</a>',
        ])
    refs_rgaa = "".join(
        f"<li><strong>Critère {html.escape(criterion)}</strong> — {inline_html(title)}</li>"
        for criterion, title in criteria_rows
    ) + "".join(
        f"<li><strong>Test {html.escape(test)}</strong> — {inline_html(title)}</li>"
        for test, title in test_rows
    )
    sources_code = "".join(
        f"<h3>{html.escape(label)}</h3><pre><code>{html.escape(code)}</code></pre>"
        for label, code in code_samples
    )
    finding_rows = []
    for finding in sorted(findings, key=lambda item: (item["page"], item["criterion"], item["test"], item["id"])):
        selector = finding.get("selector") or "Mesure documentée"
        evidence = finding_evidence(finding)
        primary_evidence = evidence[0] if evidence else "Intégrée au rapport HTML"
        provenance = finding.get("observed_origin") or (finding.get("qualification") or {}).get("reviewed_by") or "Rapport source"
        finding_rows.append([
            html.escape(finding["page"]),
            f"<code>{html.escape(finding['id'])}</code>",
            html.escape(f"{finding['criterion']} / {finding['test']}"),
            f"<code>{html.escape(selector)}</code>",
            html.escape(finding["observed"]),
            html.escape(provenance),
            f"<code>{html.escape(primary_evidence)}</code>",
        ])
    solutions = ""
    for number, solution in enumerate(spec["solutions"], 1):
        solutions += (
            f'<section class="solution"><h3>Solution {number} — {html.escape(solution["title"])}</h3>'
            f'{paragraphs_html(solution["text"])}'
            f'<pre><code>{html.escape(solution["code"])}</code></pre></section>'
        )
    dsfr_block = ""
    dsfr = spec.get("dsfr")
    if dsfr:
        rows = [[html.escape(a), html.escape(b), html.escape(c)] for a, b, c in dsfr["rows"]]
        dsfr_block = (
            '<h2 id="comparaison-dsfr">Comparaison avec le composant DSFR</h2>'
            f'<p><strong>Composant concerné :</strong> {html.escape(dsfr["component"])}</p>'
            + table_html(["Point contrôlé", "DSFR / comportement attendu", "Site audité"], rows)
            + '<p>Le constat est attribué à l’intégration observée. La présence de classes <code>fr-*</code> ne suffit pas à attribuer le défaut au DSFR natif.</p>'
        )
    reference_links = "".join(
        f'<li><a href="{html.escape(tests[test]["url"])}">RGAA 4.1.2 — test {html.escape(test)}</a></li>'
        for test, _ in test_rows
    )
    if dsfr:
        reference_links += "".join(
            f'<li><a href="{html.escape(url)}">{html.escape(label)}</a></li>'
            for label, url in dsfr["links"]
        )
    checks = "".join(f"<li>{inline_html(item)}</li>" for item in spec["verification"])
    badge_class = "blocking" if severity == "Bloquant" else "major"

    return f"""<!doctype html>
<html lang="fr">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{html.escape(spec['id'])} — {html.escape(spec['title'])}</title>
  <meta name="description" content="Ticket RGAA unitaire : {html.escape(spec['title'])}">
  <style>{HTML_CSS}</style>
</head>
<body>
<a class="skip-link" href="#contenu">Aller au contenu</a>
<header>
  <div class="container">
    <a class="back" href="../INDEX-TICKETS-RGAA.html">← Index des tickets RGAA</a>
    <h1>{html.escape(spec['id'])} — {html.escape(spec['title'])}</h1>
    <div class="meta">
      <p><strong>Statut :</strong> {html.escape(status)}</p>
      <p><strong>Référentiel :</strong> RGAA 4.1.2</p>
      <p><strong>Sévérité :</strong> <span class="badge {badge_class}">{html.escape(severity)}</span></p>
      <p><strong>Date :</strong> {DELIVERY_DATE}</p>
      <p><strong>Composant / gabarit :</strong> {html.escape(component)}</p>
      <p><strong>Portée :</strong> {html.escape(ticket_scope(pages))}</p>
      <p><strong>Pages :</strong> {html.escape(', '.join(page['id'] for page in pages))}</p>
      <p><strong>Constats sources regroupés :</strong> {len(findings)}</p>
    </div>
    <p><strong>Justification de sévérité :</strong> {inline_html(spec['impact'])}</p>
    <div class="warning" role="note"><strong>Limite :</strong> préqualification instrumentée, sans taux RGAA officiel ni validation après correction.</div>
    {alert}
  </div>
</header>
<main id="contenu" class="container">
  <h2>Pages et rapports sources</h2>
  {table_html(["Page", "Nom", "URL", "Rapport RGAA"], page_rows)}
  <h2>Références RGAA</h2>
  <ul>{refs_rgaa}</ul>
  <h2>Code source constaté</h2>
  {sources_code}
  <h2>Inventaire des constats sources</h2>
  {table_html(["Page", "Identifiant source", "Critère / test", "Sélecteur", "Observation", "Provenance", "Preuve principale"], finding_rows, "inventory")}
  <h2>Analyse du défaut</h2>
  {paragraphs_html(spec['analysis'])}
  <h2>Impact utilisateur</h2>
  {paragraphs_html(spec['impact'])}
  <h2>Recommandations</h2>
  {solutions}
  {dsfr_block}
  <h2>Vérification après correction</h2>
  <ul class="checklist">{checks}</ul>
  <p><strong>Condition de clôture :</strong> produire une nouvelle preuve et faire recontrôler la correction humainement.</p>
  <h2>Références</h2>
  <ul>{reference_links}<li>Source factuelle : rapports HTML RGAA livrés et constats <code>NC_CONFIRMEE</code> correspondants.</li></ul>
</main>
<footer><div class="container"><p>Échantillon Douane — tickets RGAA P01 à P09.</p></div></footer>
</body>
</html>
"""


def render_index_html(manifest: dict[str, Any]) -> str:
    rows = []
    for ticket in manifest["tickets"]:
        pages = ", ".join(ticket["pages"])
        criteria = ", ".join(ticket["criteria"])
        status = ticket["delivery_status"]
        rows.append([
            f'<a href="html/{html.escape(ticket["html_file"])}">{html.escape(ticket["id"])}</a>',
            html.escape(ticket["title"]),
            html.escape(criteria),
            html.escape(ticket["severity"]),
            html.escape(pages),
            str(ticket["source_findings"]),
            html.escape(status),
            f'<a href="markdown/{html.escape(ticket["markdown_file"])}">Markdown</a>',
        ])
    page_rows = []
    for page in manifest["pages"]:
        page_rows.append([
            html.escape(page["id"]),
            html.escape(page["name"]),
            f'<a href="../RGAA/{page["id"]}-RGAA.html">RGAA</a>',
            f'<a href="../DSFR/{page["id"]}-DSFR.html">DSFR</a>',
        ])
    return f"""<!doctype html>
<html lang="fr">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Index des tickets RGAA — Échantillon Douane</title>
  <meta name="description" content="Index des tickets RGAA unitaires P01 à P09.">
  <style>{HTML_CSS}</style>
</head>
<body>
<a class="skip-link" href="#contenu">Aller au contenu</a>
<header><div class="container">
  <a class="back" href="../INDEX-LIVRABLES.html">← Index général des livrables</a>
  <h1>Tickets unitaires RGAA — Échantillon Douane</h1>
  <p>Les {manifest['source_confirmed_findings']} constats <code>NC_CONFIRMEE</code> des neuf rapports HTML sont regroupés par cause racine en {manifest['ticket_count']} fiches : {manifest['nc_ticket_count']} tickets NC et {manifest['requalification_count']} fiches à requalifier.</p>
  <div class="warning" role="note"><strong>Limite :</strong> ces fiches dérivent d’une préqualification instrumentée. Aucun taux RGAA officiel n’est produit. Chaque correction doit faire l’objet d’un recontrôle.</div>
  <div class="alert" role="note"><strong>Avant transmission comme non-conformités :</strong> arbitrer les {manifest['requalification_count']} fiches sources <code>A-REQUALIFIER-RGAA-*</code> et les 2 tickets candidats du complément P06. Le drapeau <code>valid</code> du contrôle JSON décrit l’intégrité technique du paquet, pas ces 6 arbitrages méthodologiques.</div>
</div></header>
<main id="contenu" class="container">
  <h2>Accès aux tickets</h2>
  {table_html(["Ticket", "Titre", "Critère(s)", "Sévérité", "Pages", "Constats", "Statut", "Source"], rows)}
  <h2>Complément de couverture P06</h2>
  <div class="alert" role="note"><strong>Deux nouvelles requalifications :</strong> le complément sûr P06 étaye 11.10.2 comme non conforme alors qu’il était publié conforme, et 7.5.2 comme non conforme alors qu’il était publié NA. Elles restent séparées des {manifest['ticket_count']} fiches dérivées des constats sources.</div>
  <p><a href="../P06-FORMULAIRES/TICKET-CANDIDAT-RGAA-11.10.2.html">Ouvrir le ticket candidat 11.10.2</a> · <a href="../P06-FORMULAIRES/TICKET-CANDIDAT-RGAA-7.5.2.html">Ouvrir le ticket candidat 7.5.2</a> · <a href="../P06-FORMULAIRES/INDEX-P06-FORMULAIRES.html">Consulter la matrice probatoire des 34 tests Formulaires</a>.</p>
  <h2>Rapports des neuf pages</h2>
  {table_html(["Page", "Nom", "Rapport RGAA", "Rapport DSFR"], page_rows)}
  <h2>Méthode de regroupement</h2>
  <ul>
    <li>Une fiche par cause racine, conformément au creator mode, avec une structure enrichie issue du canevas <code>ticket-rgaa</code>.</li>
    <li>Les constats 7.1.1 et 10.8.1 sur la recherche partagent une même correction et sont regroupés.</li>
    <li>Les constats 12.7.1 et 12.7.2 sur la cible <code>#content</code> sont regroupés.</li>
    <li>Chaque fiche conserve les identifiants sources, les observations, les pages et les liens vers les rapports HTML.</li>
  </ul>
  <h2>Fichiers de contrôle</h2>
  <ul>
    <li><a href="MANIFESTE-TICKETS-RGAA.json">Manifeste JSON</a></li>
    <li><a href="VALIDATION-TICKETS-RGAA.json">Validation JSON</a></li>
    <li><a href="SHA256SUMS">Empreintes SHA-256</a></li>
    <li><a href="README.md">Note de livraison</a></li>
  </ul>
</main>
<footer><div class="container"><p>Échantillon Douane — P01 à P09 — {DELIVERY_DATE}.</p></div></footer>
</body>
</html>
"""


def render_root_index(manifest: dict[str, Any]) -> str:
    cards = []
    for page in manifest["pages"]:
        complement = (
            '<br><a href="P06-FORMULAIRES/INDEX-P06-FORMULAIRES.html">Complément Formulaires P06</a>'
            if page["id"] == "P06"
            else ""
        )
        cards.append(
            f'<article class="card"><h3>{html.escape(page["id"])} — {html.escape(page["name"])}</h3>'
            f'<p><a href="RGAA/{page["id"]}-RGAA.html">Rapport RGAA</a><br>'
            f'<a href="DSFR/{page["id"]}-DSFR.html">Rapport DSFR</a>{complement}</p></article>'
        )
    return f"""<!doctype html>
<html lang="fr">
<head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>Livrables d’audit Douane — Virginie</title><style>{HTML_CSS}</style></head>
<body>
<a class="skip-link" href="#contenu">Aller au contenu</a>
<header><div class="container"><h1>Livrables d’audit Douane</h1><p>Échantillon P01 à P09 : rapports RGAA, rapports DSFR, tickets RGAA unitaires et complément de couverture du formulaire P06.</p></div></header>
<main id="contenu" class="container">
  <section class="cards" aria-label="Synthèse des livrables">
    <article class="card"><p class="count">9</p><h2>Rapports RGAA</h2><p>Un rapport HTML détaillé par page.</p></article>
    <article class="card"><p class="count">9</p><h2>Rapports DSFR</h2><p>Un rapport HTML détaillé par page.</p></article>
    <article class="card"><p class="count">{manifest['ticket_count']}</p><h2>Fiches de cause racine</h2><p>{manifest['nc_ticket_count']} tickets NC et {manifest['requalification_count']} fiches à arbitrer.</p><p><a href="TICKETS-RGAA/INDEX-TICKETS-RGAA.html">Ouvrir l’index des tickets RGAA</a>.</p></article>
    <article class="card"><p class="count">34</p><h2>Complément Formulaires P06</h2><p>Matrice probatoire, retest sans soumission et tickets candidats RGAA 11.10.2 / 7.5.2.</p><p><a href="P06-FORMULAIRES/INDEX-P06-FORMULAIRES.html">Ouvrir le complément P06</a>.</p></article>
  </section>
  <h2>Rapports par page</h2>
  <div class="cards">{''.join(cards)}</div>
  <h2>Limites</h2>
  <div class="warning" role="note">Préqualification instrumentée. Aucun taux RGAA officiel. Aucun test réel NVDA, JAWS ou VoiceOver n’est revendiqué sans preuve dédiée. Les 18 rapports sont des copies sources : leurs liens relatifs vers les archives ne sont pas embarqués dans ce paquet.</div>
</main>
<footer><div class="container"><p>Livraison du {DELIVERY_DATE}.</p></div></footer>
</body></html>
"""


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


@contextmanager
def p06_pipeline_lock():
    PIPELINE_LOCK.parent.mkdir(parents=True, exist_ok=True)
    with PIPELINE_LOCK.open("a+", encoding="utf-8") as handle:
        fcntl.flock(handle.fileno(), fcntl.LOCK_EX)
        try:
            yield
        finally:
            fcntl.flock(handle.fileno(), fcntl.LOCK_UN)


def validate_p06_supplement(
    matrix: dict[str, Any], tests: dict[str, dict[str, str]]
) -> list[str]:
    """Revalide la chaîne probatoire P06 avant de déclarer le paquet intègre."""
    errors: list[str] = []
    supplement_root = DELIVERY / "P06-FORMULAIRES"
    expected_tests = {test_id for test_id in tests if test_id.startswith("11.")}
    if len(expected_tests) != 34:
        errors.append("Référentiel RGAA local : le thème 11 ne contient pas exactement 34 tests")
    if matrix.get("client_transmission_ready") is not False:
        errors.append("Complément P06 : client_transmission_ready doit rester explicitement faux")
    decisions = matrix.get("decisions")
    if not isinstance(decisions, list):
        errors.append("Complément P06 : liste decisions absente")
        decisions = []
    decision_ids = [item.get("test") for item in decisions if isinstance(item, dict)]
    if (
        matrix.get("tests_count") != 34
        or len(decisions) != 34
        or len(decision_ids) != 34
        or len(set(decision_ids)) != 34
        or set(decision_ids) != expected_tests
    ):
        errors.append("Complément P06 : les 34 décisions thème 11 exactes et uniques sont requises")
    computed_counts = Counter(
        item.get("supplement_status") for item in decisions if isinstance(item, dict)
    )
    if dict(sorted(computed_counts.items())) != matrix.get("supplement_counts"):
        errors.append("Complément P06 : supplement_counts ne correspond pas aux décisions")
    server_tests = {
        item.get("test")
        for item in decisions
        if isinstance(item, dict) and item.get("supplement_status") == "A_RETESTER_SERVEUR"
    }
    if server_tests != {"11.10.6", "11.10.7", "11.11.1", "11.11.2"}:
        errors.append("Complément P06 : les quatre retests serveur exacts ne sont pas conservés")

    expected_requalifications = {
        "11.10.2": ("C_CONFIRMEE", "NON_CONFORME_ETAYE"),
        "7.5.2": ("NA_CONFIRMEE", "NON_CONFORME_ETAYE"),
    }
    requalifications = matrix.get("requalifications")
    if not isinstance(requalifications, list):
        requalifications = []
    requalification_by_test = {
        item.get("test"): item for item in requalifications if isinstance(item, dict)
    }
    if (
        len(requalifications) != 2
        or len(requalification_by_test) != 2
        or set(requalification_by_test) != set(expected_requalifications)
    ):
        errors.append("Complément P06 : exactement deux requalifications uniques 11.10.2 et 7.5.2 sont requises")
    else:
        for test_id, (published_status, status) in expected_requalifications.items():
            item = requalification_by_test[test_id]
            if (
                item.get("published_status") != published_status
                or item.get("status") != status
                or item.get("requalification_required") is not True
            ):
                errors.append(f"Complément P06 : requalification {test_id} incohérente")
        if requalification_by_test.get("11.10.2") != matrix.get("theme_requalification"):
            errors.append("Complément P06 : theme_requalification diverge de requalifications")
        if requalification_by_test.get("7.5.2") != matrix.get("adjacent_decision"):
            errors.append("Complément P06 : adjacent_decision diverge de requalifications")

    evidence_path = supplement_root / "preuves/P06-RETEST-SAFE.json"
    if not evidence_path.is_file():
        errors.append("Complément P06 : preuve P06-RETEST-SAFE.json absente")
        return errors
    try:
        evidence = json.loads(evidence_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        errors.append(f"Complément P06 : preuve sûre illisible ({error})")
        return errors
    integrity = matrix.get("source_integrity", {})
    if sha256_file(evidence_path) != integrity.get("safe_evidence_sha256"):
        errors.append("Complément P06 : hash de la preuve sûre incohérent")
    safe_retest = matrix.get("safe_retest", {})
    collector = evidence.get("collector", {})
    collector_path = ROOT / "scripts/retest-p06-form-safe.py"
    if (
        evidence.get("schema_version") != 2
        or not evidence.get("run_id")
        or collector.get("file") != "scripts/retest-p06-form-safe.py"
        or not collector_path.is_file()
        or sha256_file(collector_path) != collector.get("sha256")
        or safe_retest.get("run_id") != evidence.get("run_id")
        or safe_retest.get("collector") != collector
    ):
        errors.append("Complément P06 : preuve v2, run_id ou collecteur courant incohérent")
    safety = matrix.get("safety", {})
    guard = evidence.get("network_guard", {})
    contract = evidence.get("safety_contract", {})
    page_errors = evidence.get("page_errors", [])
    guard_window_errors = evidence.get("guard_window_page_errors", [])
    five_files = evidence.get("scenarios", {}).get("five_allowed_files", {})
    if (
        set(safety.get("allowed_http_methods", [])) != {"GET", "HEAD", "OPTIONS"}
        or safety.get("guard_scope") != "BrowserContext"
        or safety.get("mutating_requests_completed") is not False
        or safety.get("completed_mutating_request_details") != []
        or safety.get("valid_final_submission") is not False
        or safety.get("server_mutation_authorized") is not False
        or safety.get("synthetic_data_only") is not True
        or guard.get("completed_mutating_requests") != []
        or guard.get("mutating_request_completed") is not False
        or contract.get("synthetic_data_only") is not True
        or evidence.get("unexpected_page_errors") != []
        or len(page_errors) != 1
        or guard_window_errors != page_errors
        or page_errors[0].get("scenario") != "five_allowed_files"
        or page_errors[0].get("message") != "Drupal.AjaxError"
        or page_errors[0].get("attribution") != "guard-window-causality-unproven"
        or not evidence.get("page_error_attribution_limit")
        or safety.get("page_errors_observed") != 1
        or safety.get("guard_window_page_errors") != guard_window_errors
        or safety.get("page_error_attribution_limit")
        != evidence.get("page_error_attribution_limit")
        or guard.get("blocked_count") != len(guard.get("blocked_requests", []))
        or guard.get("blocked_count") != 1
        or guard.get("blocked_requests") != five_files.get("blocked_mutating_requests")
        or safety.get("blocked_mutating_requests") != guard.get("blocked_count")
        or safety.get("blocked_request_details") != guard.get("blocked_requests")
        or guard.get("blocked_websocket_count") != len(guard.get("blocked_websockets", []))
        or safety.get("blocked_websockets") != guard.get("blocked_websocket_count")
        or safety.get("blocked_websocket_details") != guard.get("blocked_websockets")
    ):
        errors.append("Complément P06 : contrat de sécurité ou garde réseau incohérent")

    scenario_screenshots = {
        name: scenario.get("screenshot")
        for name, scenario in evidence.get("scenarios", {}).items()
        if isinstance(scenario, dict)
    }
    matrix_screenshots = safe_retest.get("screenshots")
    if matrix_screenshots != scenario_screenshots or len(scenario_screenshots) != 5:
        errors.append("Complément P06 : manifeste des cinq captures incohérent")
    else:
        for name, screenshot in scenario_screenshots.items():
            if not isinstance(screenshot, dict):
                errors.append(f"Complément P06 : capture {name} absente")
                continue
            relative = Path(str(screenshot.get("file", "")))
            path = (supplement_root / relative).resolve()
            if (
                relative.is_absolute()
                or ".." in relative.parts
                or not path.is_relative_to(supplement_root.resolve())
                or not path.is_file()
                or path.stat().st_size != screenshot.get("bytes")
                or sha256_file(path) != screenshot.get("sha256")
            ):
                errors.append(f"Complément P06 : capture {name} absente ou altérée")

    p06_archive = archive_for("P06")
    source_paths = {
        "published_decisions_sha256": p06_archive / "rgaa/P06-DECISIONS-258.json",
        "manual_reviews_sha256": p06_archive / "rgaa/REVUE-MANUELLE-258.json",
        "archived_server_state_sha256": p06_archive
        / "preuves-p06-complet/P06-ETATS-FORMULAIRE-COMPLEMENTAIRES.json",
        "archived_company_state_sha256": p06_archive
        / "preuves-p06-complet/P06-CHAMP-SOCIETE-OPTIONNEL.json",
        "reference_sha256": rgaa_reference(),
    }
    for key, path in source_paths.items():
        if not path.is_file() or sha256_file(path) != integrity.get(key):
            errors.append(f"Complément P06 : intégrité source incohérente ({key})")
    bundled_pairs = (
        (
            source_paths["archived_server_state_sha256"],
            supplement_root / "preuves/P06-ETAT-SERVEUR-ARCHIVE.json",
        ),
        (
            source_paths["archived_company_state_sha256"],
            supplement_root / "preuves/P06-SOCIETE-OPTIONNEL-ARCHIVE.json",
        ),
    )
    for source, bundled in bundled_pairs:
        if (
            not source.is_file()
            or not bundled.is_file()
            or sha256_file(source) != sha256_file(bundled)
        ):
            errors.append(f"Complément P06 : copie d’archive altérée ({bundled.name})")
    return errors


class LinkAndStructureParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.links: list[str] = []
        self.ids: list[str] = []
        self.lang_fr = False
        self.main_count = 0
        self.h1_count = 0

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        values = dict(attrs)
        if tag == "html" and values.get("lang") == "fr":
            self.lang_fr = True
        if tag == "main":
            self.main_count += 1
        if tag == "h1":
            self.h1_count += 1
        if values.get("id"):
            self.ids.append(str(values["id"]))
        if tag == "a" and values.get("href"):
            self.links.append(str(values["href"]))


def validate_html_file(path: Path) -> list[str]:
    errors: list[str] = []
    parser = LinkAndStructureParser()
    parser.feed(path.read_text(encoding="utf-8"))
    if not parser.lang_fr:
        errors.append(f"{path.name}: html lang=fr absent")
    if parser.main_count != 1:
        errors.append(f"{path.name}: {parser.main_count} élément(s) main")
    if parser.h1_count != 1:
        errors.append(f"{path.name}: {parser.h1_count} élément(s) h1")
    duplicate_ids = sorted({value for value in parser.ids if parser.ids.count(value) > 1})
    if duplicate_ids:
        errors.append(f"{path.name}: identifiants dupliqués {duplicate_ids}")
    for href in parser.links:
        if href.startswith(("http://", "https://", "mailto:", "#")):
            continue
        target_value = href.split("#", 1)[0]
        if not target_value:
            continue
        target = (path.parent / target_value).resolve()
        if not target.exists():
            errors.append(f"{path.name}: lien interne absent {href}")
    return errors


def build_manifest(grouped: list[tuple[dict[str, Any], list[dict[str, Any]]]], pages: list[dict[str, str]]) -> dict[str, Any]:
    tickets = []
    for spec, findings in grouped:
        base = f"{spec['id']}-{spec['slug']}"
        severity = max((item["severity"] for item in findings), key=severity_rank)
        tickets.append(
            {
                "id": spec["id"],
                "title": spec["title"],
                "delivery_status": spec.get("delivery_status", "Préqualification — NC confirmée dans les rapports sources"),
                "severity": severity,
                "severity_justification": spec["impact"],
                "component_or_template": spec.get("dsfr", {}).get("component", "Composant personnalisé"),
                "scope": ticket_scope(group_pages(findings)),
                "pages": [page["id"] for page in group_pages(findings)],
                "criteria": sorted({item["criterion"] for item in findings}, key=lambda value: [int(x) for x in value.split(".")]),
                "tests": sorted({item["test"] for item in findings}, key=lambda value: [int(x) for x in value.split(".")]),
                "rule_ids": spec["rules"],
                "methodological_alert": spec.get("methodological_alert"),
                "source_findings": len(findings),
                "source_finding_ids": sorted(item["id"] for item in findings),
                "occurrences": [
                    {
                        "id": item["id"],
                        "page": item["page"],
                        "page_url": item["page_url"],
                        "criterion": item["criterion"],
                        "test": item["test"],
                        "rule_id": item["rule_id"],
                        "source_status": item["qualification_status"],
                        "selector": item.get("selector") or None,
                        "observed": item["observed"],
                        "provenance": item.get("observed_origin") or (item.get("qualification") or {}).get("reviewed_by"),
                        "evidence": finding_evidence(item),
                    }
                    for item in sorted(findings, key=lambda value: value["id"])
                ],
                "markdown_file": f"{base}.md",
                "html_file": f"{base}.html",
            }
        )
    return {
        "schema_version": 1,
        "generated_at": DELIVERY_DATE,
        "scope": "Échantillon Douane P01 à P09",
        "referential": "RGAA 4.1.2",
        "claim": "Préqualification instrumentée ; aucun taux RGAA officiel.",
        "grouping": "Une fiche par cause racine ; regroupement des tests partageant une correction.",
        "source_confirmed_findings": sum(item["source_findings"] for item in tickets),
        "source_rule_ids": sorted({rule for item in tickets for rule in item["rule_ids"]}),
        "ticket_count": len(tickets),
        "nc_ticket_count": sum(item["id"].startswith("NC-") for item in tickets),
        "requalification_count": sum(item["id"].startswith("A-REQUALIFIER-") for item in tickets),
        "pages": pages,
        "tickets": tickets,
    }


def _run_locked() -> int:
    findings, criteria, tests, source_status_counts = load_sources()
    if len(findings) != 145:
        raise RuntimeError(f"Le gel contractuel attend 145 constats NC_CONFIRMEE, source courante : {len(findings)}")
    evidence_refs = sorted(
        {
            (finding["page"], evidence)
            for finding in findings
            for evidence in finding_evidence(finding)
        }
    )
    unsafe_evidence = [evidence for _, evidence in evidence_refs if Path(evidence).is_absolute() or "/Users/" in evidence]
    if unsafe_evidence:
        raise RuntimeError(f"Chemins de preuve non livrables : {unsafe_evidence}")
    missing_evidence = [
        f"{page}:{evidence}"
        for page, evidence in evidence_refs
        if not (archive_for(page) / evidence).is_file()
    ]
    if missing_evidence:
        raise RuntimeError(f"Preuves archivées absentes : {missing_evidence}")

    by_rule: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for finding in findings:
        by_rule[finding["rule_id"]].append(finding)

    expected_rules = {rule for spec in TICKET_SPECS for rule in spec["rules"]}
    actual_rules = set(by_rule)
    if expected_rules != actual_rules:
        missing = sorted(actual_rules - expected_rules)
        stale = sorted(expected_rules - actual_rules)
        raise RuntimeError(f"Mapping incomplet. Non mappées={missing}; sans source={stale}")

    mapped_ids: list[str] = []
    grouped: list[tuple[dict[str, Any], list[dict[str, Any]]]] = []
    for spec in TICKET_SPECS:
        spec_findings = [item for item in findings if matches_spec(item, spec)]
        if not spec_findings:
            raise RuntimeError(f"Aucun constat source pour {spec['id']}")
        grouped.append((spec, spec_findings))
        mapped_ids.extend(item["id"] for item in spec_findings)
    source_ids = [item["id"] for item in findings]
    if sorted(mapped_ids) != sorted(source_ids) or len(mapped_ids) != len(set(mapped_ids)):
        raise RuntimeError("Chaque constat source doit être mappé exactement une fois")

    pages_by_id: dict[str, dict[str, str]] = {}
    for finding in findings:
        pages_by_id[finding["page"]] = {
            "id": finding["page"],
            "name": finding["page_name"],
            "url": finding["page_url"],
        }
    pages = [pages_by_id[page] for page in PAGE_IDS]

    if TICKETS_ROOT.exists():
        shutil.rmtree(TICKETS_ROOT)
    MD_ROOT.mkdir(parents=True)
    HTML_ROOT.mkdir(parents=True)

    for spec, spec_findings in grouped:
        base = f"{spec['id']}-{spec['slug']}"
        markdown = render_markdown(spec, spec_findings, findings, criteria, tests)
        html_document = render_html(spec, spec_findings, findings, criteria, tests)
        (MD_ROOT / f"{base}.md").write_text(markdown, encoding="utf-8")
        (HTML_ROOT / f"{base}.html").write_text(html_document, encoding="utf-8")

    manifest = build_manifest(grouped, pages)
    manifest["source_status_counts"] = dict(sorted(source_status_counts.items()))
    manifest["evidence_policy"] = (
        "Les chemins de preuve sont conservés pour la traçabilité vers les archives de travail ; "
        "les fichiers volumineux ne sont pas dupliqués. Les extraits utiles sont embarqués dans les fiches."
    )
    manifest["archive_evidence_references"] = len(evidence_refs)
    manifest["bundled_evidence_files"] = 0
    (TICKETS_ROOT / "MANIFESTE-TICKETS-RGAA.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    (TICKETS_ROOT / "INDEX-TICKETS-RGAA.html").write_text(render_index_html(manifest), encoding="utf-8")
    (DELIVERY / "INDEX-LIVRABLES.html").write_text(render_root_index(manifest), encoding="utf-8")

    readme_lines = [
        "# Tickets RGAA — Échantillon Douane P01 à P09",
        "",
        f"- **Date de génération :** {DELIVERY_DATE}",
        "- **Référentiel :** RGAA 4.1.2",
        f"- **Occurrences RGAA sources :** {sum(manifest['source_status_counts'].values())} "
        f"({manifest['source_status_counts'].get('NC_CONFIRMEE', 0)} `NC_CONFIRMEE`, "
        f"{manifest['source_status_counts'].get('A_RETESTER', 0)} `A_RETESTER`, "
        f"{manifest['source_status_counts'].get('NON_TESTE', 0)} `NON_TESTE`, "
        f"{manifest['source_status_counts'].get('C_CONFIRMEE', 0)} `C_CONFIRMEE`)",
        f"- **Constats `NC_CONFIRMEE` transformés :** {manifest['source_confirmed_findings']}",
        f"- **Causes racines livrées :** {manifest['ticket_count']}",
        f"- **Tickets NC :** {manifest['nc_ticket_count']}",
        f"- **Fiches à requalifier :** {manifest['requalification_count']}",
        "",
        "## Contenu",
        "",
        "- `INDEX-TICKETS-RGAA.html` : accès principal aux fiches ;",
        "- `html/` : fiches client autonomes et imprimables ;",
        "- `markdown/` : sources structurées, enrichies à partir du canevas `ticket-rgaa` ;",
        "- `MANIFESTE-TICKETS-RGAA.json` : correspondance exhaustive entre constats et tickets ;",
        "- `VALIDATION-TICKETS-RGAA.json` : résultat des contrôles déterministes ;",
        "- `SHA256SUMS` : empreintes des fichiers du répertoire livrable ;",
        "- `../P06-FORMULAIRES/` : matrice probatoire des 34 tests, retest sûr et tickets candidats 11.10.2 / 7.5.2.",
        "",
        "## Principe de regroupement",
        "",
        "Une fiche est produite par cause racine. Les défauts systémiques listent toutes les pages affectées au lieu de dupliquer une fiche complète pour chaque page. Les constats 7.1.1 et 10.8.1 relatifs à la recherche sont regroupés, de même que les constats 12.7.1 et 12.7.2 relatifs au lien vers `#content`.",
        "",
        "Les occurrences `A_RETESTER`, `NON_TESTE` et `C_CONFIRMEE` restent dans les rapports sources et ne sont pas transformées en tickets NC.",
        "",
        "Les chemins de preuve mentionnés dans les inventaires assurent la traçabilité vers les archives de travail ; ces archives volumineuses ne sont pas dupliquées dans ce répertoire. Chaque fiche embarque néanmoins l’extrait de code nécessaire à sa compréhension.",
        "",
        "## Limite",
        "",
        "Ces fiches dérivent d’une préqualification instrumentée. Elles ne constituent pas un taux RGAA officiel. Toute correction revendiquée doit être recontrôlée avant clôture.",
        "",
        "Les rapports RGAA/DSFR sont conservés byte-identiques à leurs sources. Leurs liens relatifs vers les preuves et portails d’archive ne sont pas embarqués ; la validation des liens porte uniquement sur les fichiers générés du paquet.",
        "",
    ]
    (TICKETS_ROOT / "README.md").write_text("\n".join(readme_lines), encoding="utf-8")
    # L’index lie ces fichiers. Un état non vert est écrit avant tout contrôle afin
    # qu’une interruption ne puisse jamais laisser une validation positive périmée.
    validation_path = TICKETS_ROOT / "VALIDATION-TICKETS-RGAA.json"
    checksum_path = TICKETS_ROOT / "SHA256SUMS"
    validation_path.write_text(
        json.dumps(
            {
                "valid": False,
                "client_transmission_ready": False,
                "generation_state": "IN_PROGRESS",
                "checksum_verification": "PENDING",
            },
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    checksum_path.write_text("", encoding="utf-8")

    errors: list[str] = []
    warnings: list[str] = []
    supplement_root = DELIVERY / "P06-FORMULAIRES"
    supplement_matrix_path = supplement_root / "COUVERTURE-RGAA-11.json"
    supplement_html_files = [
        supplement_root / "INDEX-P06-FORMULAIRES.html",
        supplement_root / "TICKET-CANDIDAT-RGAA-11.10.2.html",
        supplement_root / "TICKET-CANDIDAT-RGAA-7.5.2.html",
    ]
    supplement_arbitrations = 0
    supplement_test_count = 0
    supplement_ready = False
    if not supplement_matrix_path.is_file():
        errors.append("Complément P06 absent : COUVERTURE-RGAA-11.json")
    else:
        try:
            supplement_matrix = json.loads(supplement_matrix_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as error:
            errors.append(f"Complément P06 illisible : {error}")
        else:
            supplement_ready = supplement_matrix.get("client_transmission_ready") is True
            matrix_decisions = supplement_matrix.get("decisions")
            supplement_test_count = len(matrix_decisions) if isinstance(matrix_decisions, list) else 0
            supplement_errors = validate_p06_supplement(supplement_matrix, tests)
            errors.extend(supplement_errors)
            if not supplement_errors:
                supplement_arbitrations = 2
    # Vérifier que les rapports HTML livrés portent le même nombre de NC que le JSON.
    source_count_by_page = defaultdict(int)
    for finding in findings:
        source_count_by_page[finding["page"]] += 1
    for page in PAGE_IDS:
        report = DELIVERY / "RGAA" / f"{page}-RGAA.html"
        if not report.is_file():
            errors.append(f"Rapport RGAA absent : {report.name}")
            continue
        html_count = report.read_text(encoding="utf-8").count('data-audit-status="NC_CONFIRMEE"')
        if html_count != source_count_by_page[page]:
            errors.append(f"{page}: HTML={html_count}, JSON={source_count_by_page[page]}")
    warnings.append(
        "Les 18 rapports RGAA/DSFR sont des copies sources byte-identiques : leurs liens relatifs vers "
        "les portails et preuves d’archive ne sont pas embarqués ni inclus dans la validation de liens."
    )

    markdown_files = sorted(MD_ROOT.glob("*.md"))
    html_files = sorted(HTML_ROOT.glob("*.html"))
    if len(markdown_files) != manifest["ticket_count"]:
        errors.append(f"Nombre de fiches Markdown inattendu : {len(markdown_files)}")
    if len(html_files) != manifest["ticket_count"]:
        errors.append(f"Nombre de fiches HTML inattendu : {len(html_files)}")
    for path in html_files + supplement_html_files + [
        TICKETS_ROOT / "INDEX-TICKETS-RGAA.html",
        DELIVERY / "INDEX-LIVRABLES.html",
    ]:
        if not path.is_file():
            errors.append(f"Fichier HTML attendu absent : {path.relative_to(DELIVERY)}")
            continue
        errors.extend(validate_html_file(path))
    required_markers = [
        "## Code source constaté",
        "## Analyse du défaut",
        "## Impact utilisateur",
        "## Recommandations",
        "## Vérification après correction",
        "## Références",
    ]
    for path in markdown_files:
        content = path.read_text(encoding="utf-8")
        for marker in required_markers:
            if marker not in content:
                errors.append(f"{path.name}: section absente {marker}")
        if "```html" not in content:
            errors.append(f"{path.name}: aucun extrait HTML")
        for href in re.findall(r"\]\(([^)]+)\)", content):
            if href.startswith(("http://", "https://", "mailto:", "#")):
                continue
            target_value = href.split("#", 1)[0]
            if target_value and not (path.parent / target_value).resolve().exists():
                errors.append(f"{path.name}: lien Markdown absent {href}")
    generated_text_paths = markdown_files + html_files + supplement_html_files + [
        supplement_root / "COUVERTURE-RGAA-11.md",
        supplement_root / "TICKET-CANDIDAT-RGAA-11.10.2.md",
        supplement_root / "TICKET-CANDIDAT-RGAA-7.5.2.md",
        TICKETS_ROOT / "README.md",
        TICKETS_ROOT / "INDEX-TICKETS-RGAA.html",
        DELIVERY / "INDEX-LIVRABLES.html",
    ]
    for path in generated_text_paths:
        if not path.is_file():
            errors.append(f"Fichier texte attendu absent : {path.relative_to(DELIVERY)}")
            continue
        content = path.read_text(encoding="utf-8")
        if "/Users/" in content:
            errors.append(f"{path.name}: chemin personnel exposé")
    if manifest["source_confirmed_findings"] != 145:
        errors.append(
            f"Le gel contractuel compte 145 constats ; la source courante en compte {manifest['source_confirmed_findings']}."
        )
    if manifest["requalification_count"]:
        warnings.append(
            "Quatre groupes de constats sources sont isolés en fiches à requalifier : target=_blank/13.2.1, "
            "références aria-describedby orphelines et libellés French Customs susceptibles de relever de "
            "l’exception des noms propres."
        )
    if supplement_arbitrations:
        warnings.append(
            "Le complément P06 ajoute deux requalifications : 11.10.2, publié conforme, pour les "
            "indications de champs obligatoires, et 7.5.2, publié NA, pour les messages dynamiques."
        )

    hash_targets = sorted(
        path
        for path in DELIVERY.rglob("*")
        if path.is_file()
        and path.name not in {".DS_Store", "SHA256SUMS", "VALIDATION-TICKETS-RGAA.json"}
    )
    total_arbitrations = manifest["requalification_count"] + supplement_arbitrations
    client_ready_after_verification = not errors and total_arbitrations == 0 and supplement_ready
    validation = {
        "valid": False,
        "generation_state": "CHECKSUM_PENDING",
        "checksum_verification": "PENDING",
        "validation_scope": (
            "Intégrité des fichiers générés, structure, liens internes générés, comptages et traçabilité. "
            "Les liens internes des 18 rapports sources byte-identiques sont explicitement exclus."
        ),
        "client_transmission_ready": False,
        "validation_file_hashed": False,
        "methodological_arbitrations_required": total_arbitrations,
        "source_methodological_arbitrations_required": manifest["requalification_count"],
        "supplemental_arbitrations_required": supplement_arbitrations,
        "copied_report_links_validated": False,
        "checked_at": DELIVERY_DATE,
        "errors": errors,
        "warnings": warnings,
        "counts": {
            "pages": len(PAGE_IDS),
            "source_confirmed_findings": len(findings),
            "source_rule_ids": len(actual_rules),
            "root_cause_files": manifest["ticket_count"],
            "nc_tickets": manifest["nc_ticket_count"],
            "requalification_files": manifest["requalification_count"],
            "p06_form_tests": supplement_test_count,
            "supplemental_candidate_tickets": supplement_arbitrations,
            "supplement_bundled_archive_evidence_files": 2,
            "copied_report_files": 18,
            "markdown_files": len(markdown_files),
            "html_files": len(html_files),
            "archive_evidence_references": len(evidence_refs),
            "missing_archive_evidence": len(missing_evidence),
            "bundled_evidence_files": 0,
            "hashed_files": len(hash_targets),
        },
    }
    validation_path.write_text(
        json.dumps(validation, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    try:
        checksum_lines = [
            f"{sha256_file(path)}  {path.relative_to(DELIVERY).as_posix()}"
            for path in hash_targets
        ]
        checksum_path.write_text("\n".join(checksum_lines) + "\n", encoding="utf-8")
        for line in checksum_lines:
            expected, relative = line.split("  ", 1)
            if sha256_file(DELIVERY / relative) != expected:
                raise RuntimeError(f"Empreinte SHA-256 instable : {relative}")
    except Exception as error:
        validation["generation_state"] = "FAILED"
        validation["checksum_verification"] = "FAILED"
        validation["valid"] = False
        validation["client_transmission_ready"] = False
        validation["errors"].append(f"Échec de génération ou vérification SHA-256 : {error}")
        validation_path.write_text(
            json.dumps(validation, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        raise

    validation["generation_state"] = "COMPLETE"
    validation["checksum_verification"] = "PASSED"
    validation["valid"] = not errors
    validation["client_transmission_ready"] = client_ready_after_verification
    validation_path.write_text(
        json.dumps(validation, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(validation, ensure_ascii=False, indent=2))
    return 0 if not errors else 1


def verifier_donnees_entree() -> None:
    """Arrête avant tout effet de bord si les archives de campagne manquent.

    Le kit publie ce générateur mais pas `archives/` (voir .gitignore). Les neuf
    pages de la campagne sont vérifiées : une archive partielle produirait un
    livrable incomplet présenté comme complet.
    """
    if not ARCHIVES.is_dir():
        raise SystemExit(
            f"Données d'entrée absentes : {ARCHIVES}\n"
            "Ce générateur consomme les archives d'une campagne d'audit, qui ne "
            "sont pas publiées avec le kit.\n"
            "Aucun fichier n'a été modifié."
        )
    manquantes = [page for page in PAGE_IDS if not archive_for(page).is_dir()]
    if manquantes:
        raise SystemExit(
            "Archives de campagne incomplètes, pages manquantes : "
            + ", ".join(manquantes)
            + f"\nAttendues sous {ARCHIVES}.\nAucun fichier n'a été modifié."
        )


def main() -> int:
    configure_paths(parse_args())
    verifier_donnees_entree()
    with p06_pipeline_lock():
        return _run_locked()


if __name__ == "__main__":
    raise SystemExit(main())
