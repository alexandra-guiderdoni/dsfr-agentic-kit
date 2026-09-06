#!/usr/bin/env python3
"""Génère l’annexe probatoire P06 « Formulaires » dans virginie-livrables.

Le générateur ne modifie ni les archives, ni le site audité. Il rapproche :
- les 34 tests RGAA 4.1.2 du thème 11 ;
- les décisions publiées dans l’archive ;
- le registre de revue manuelle ;
- la relecture probatoire des preuves archivées ;
- le retest Playwright sûr sans requête mutante.
"""

from __future__ import annotations

import fcntl
import hashlib
import html
import json
import os
import re
import shutil
from collections import Counter
from contextlib import contextmanager
from html.parser import HTMLParser
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
ARCHIVE = ROOT / "archives/audit-douane-p06-complet-rgaa-dsfr-2026-09-02"
OUTPUT = ROOT / "virginie-livrables/P06-FORMULAIRES"
PIPELINE_LOCK = ROOT / "visual-tests/_results/.p06-pipeline.lock"
EVIDENCE = OUTPUT / "preuves/P06-RETEST-SAFE.json"
DECISIONS = ARCHIVE / "rgaa/P06-DECISIONS-258.json"
MANUAL_REVIEWS = ARCHIVE / "rgaa/REVUE-MANUELLE-258.json"
ARCHIVED_SERVER_STATE = ARCHIVE / "preuves-p06-complet/P06-ETATS-FORMULAIRE-COMPLEMENTAIRES.json"
ARCHIVED_COMPANY_STATE = ARCHIVE / "preuves-p06-complet/P06-CHAMP-SOCIETE-OPTIONNEL.json"
P06_URL = "https://moa.douane.gouv.fr/formulaire-infos-douane-service"
OFFICIAL_RGAA = "https://accessibilite.numerique.gouv.fr/methode/criteres-et-tests/"


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
REQUIRED_INDICATION = re.compile(
    r"\b(?:obligatoire|required|requis(?:e)?|exig[eé](?:e)?)\b", re.IGNORECASE
)
NEGATED_REQUIRED_INDICATION = re.compile(
    r"\b(?:non[- ]|pas\s+|n['’]est\s+pas\s+|ne\s+[^.;,:]{0,24}?\s+pas\s+)"
    r"(?:strictement\s+)?(?:obligatoire|required|requis(?:e)?|exig[eé](?:e)?)\b",
    re.IGNORECASE,
)

ARCHIVE_PROVEN_CONFORMING = {
    "11.1.2",
    "11.6.1",
    "11.10.4",
}
ARCHIVE_PROVEN_NONCONFORMING = {"11.10.1", "11.10.2", "11.13.1"}
ARCHIVE_RETEST = {
    "11.1.1",
    "11.1.3",
    "11.3.2",
    "11.4.1",
    "11.4.2",
    "11.4.3",
    "11.5.1",
    "11.9.1",
    "11.9.2",
    "11.10.6",
    "11.10.7",
    "11.10.3",
    "11.10.5",
    "11.11.1",
    "11.11.2",
}
ARCHIVE_NOT_TESTED = {
    "11.2.1",
    "11.2.5",
    "11.2.6",
    "11.3.1",
    "11.7.1",
    "11.8.1",
    "11.12.1",
    "11.12.2",
}
ARCHIVE_NA_SUPPORTED = {"11.2.2", "11.2.3", "11.2.4", "11.8.2", "11.8.3"}

TECHNICALLY_PREQUALIFIED: set[str] = set()
SERVER_RETEST = {"11.10.6", "11.10.7", "11.11.1", "11.11.2"}
BUSINESS_REVIEW = {"11.12.1", "11.12.2"}

RATIONALES = {
    "11.1.1": "Le relevé conserve les mécanismes d’étiquette et un candidat calculé, mais il ne constitue pas une implémentation normative d’AccName : qualification humaine maintenue.",
    "11.1.3": "La variante « Un professionnel » montre Société et son étiquette ensemble, mais la visibilité et la proximité de tous les champs, notamment la recherche masquée, n’ont pas été qualifiées exhaustivement : revue humaine maintenue.",
    "11.3.2": "Les quatre contrôles explicitement cartographiés sur P01 à P09 — recherche et trois choix de thème — conservent le même texte de label et candidat de nom ; la visibilité effective et la qualification « même fonction » restent humaines.",
    "11.10.6": "L’adresse électronique invalide et l’extension de fichier interdite ont produit des messages visibles. Le scénario de cinq fichiers déclenche une requête AJAX qui a été bloquée avant envoi : son véritable retour serveur reste inconnu.",
    "11.10.7": "Les états natifs observés ne posent pas aria-invalid. Les états serveur archivés en posent, mais le retour réel du dépassement de quatre fichiers n’a pas été obtenu en mode sûr. L’ancien NA est donc remplacé par un retest serveur.",
    "11.11.1": "Le message d’extension interdite donne les types autorisés et le navigateur indique le caractère @ manquant. La suggestion associée au dépassement de quatre fichiers reste inconnue sans réponse serveur.",
    "11.11.2": "L’exemple nom@domaine.fr est visible pour l’email. La nécessité et le contenu d’un exemple dans le retour « cinq fichiers » restent à qualifier après réponse serveur.",
    "11.10.1": "Le champ Société est facultatif mais aucune mention visible ne l’indique alors que l’instruction globale annonce tous les champs obligatoires sauf mention contraire.",
    "11.10.2": "Les champs portant required ne présentent pas l’indication de leur caractère obligatoire dans leur étiquette ou un passage de texte associé ; l’instruction globale non associée ne suffit pas.",
    "11.10.3": "Le premier état client utilise un message de validation natif générique sans aria-invalid ; sa capacité à identifier nommément le champ reste à qualifier humainement malgré un état serveur archivé plus riche.",
    "11.10.5": "Plusieurs champs portent maxlength=128 sans instruction associée. La nécessité et la formulation d’une indication de format/longueur restent à qualifier humainement.",
    "11.13.1": "Le champ Société concerne l’organisation de l’utilisateur et ne possède pas autocomplete=organization.",
}

STATUS_LABELS = {
    "NON_CONFORME_ETAYE": "Non conforme étayé",
    "CONFORME_TECHNIQUE_ETAYEE_A_VALIDER_HUMAINEMENT": "Conforme technique étayée — validation humaine requise",
    "NON_APPLICABLE_CONDITIONNEL_DOM": "Non applicable conditionnel — DOM observé",
    "A_QUALIFIER_HUMAINEMENT": "À qualifier humainement",
    "A_RETESTER_SERVEUR": "À retester côté serveur",
    "NON_APPLICABLE_A_CONFIRMER_METIER": "Non applicable à confirmer métier",
}

CSS = """
:root{font-family:Marianne,Arial,sans-serif;color:#161616;background:#fff;line-height:1.55}
*{box-sizing:border-box}body{margin:0}.container{max-width:78rem;margin:auto;padding:1.5rem}
.skip{position:absolute;left:-9999px}.skip:focus{left:1rem;top:1rem;background:#fff;padding:.75rem;z-index:10}
header{background:#000091;color:#fff}header a{color:#fff}h1{font-size:clamp(1.8rem,4vw,3rem);line-height:1.12}
h2{margin-top:2.5rem;border-bottom:2px solid #000091;padding-bottom:.35rem}h3{margin-top:1.8rem}
.cards{display:grid;grid-template-columns:repeat(auto-fit,minmax(14rem,1fr));gap:1rem}.card{border:1px solid #ddd;padding:1rem;border-top:4px solid #000091}.count{font-size:2rem;font-weight:700;margin:0}
.notice{border-left:5px solid #e1000f;background:#fff4f4;padding:1rem;margin:1rem 0}.safe{border-left-color:#18753c;background:#e3fdeb}.warning{border-left-color:#b34000;background:#fff4e5}
.table-wrap{overflow:auto;border:1px solid #ddd}table{border-collapse:collapse;width:100%;min-width:70rem}th,td{border-bottom:1px solid #ddd;padding:.65rem;text-align:left;vertical-align:top}th{background:#eee}code{background:#eee;padding:.1rem .25rem}.badge{display:inline-block;border-radius:1rem;padding:.18rem .55rem;font-size:.82rem;font-weight:700}.pass{background:#b8fec9;color:#0d6635}.fail{background:#ffe9e9;color:#ce0500}.pending{background:#feecc2;color:#716043}.na{background:#eee;color:#555}
a{color:#000091}pre{max-width:100%;overflow:auto;padding:.75rem;background:#eee}.evidence-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(18rem,1fr));gap:1rem}.evidence-grid figure{margin:0;border:1px solid #ddd;padding:.75rem}.evidence-grid img{width:100%;height:auto}figcaption{font-size:.9rem;margin-top:.5rem}
footer{margin-top:3rem;background:#eee}@media(max-width:48rem){.container{padding:1rem}}
"""


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def sha256(path: Path) -> str:
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


def has_positive_required_indication(value: str) -> bool:
    without_negations = NEGATED_REQUIRED_INDICATION.sub("", value)
    return REQUIRED_INDICATION.search(without_negations) is not None


def status_class(status: str) -> str:
    if status.startswith("CONFORME_TECHNIQUE"):
        return "pass"
    if status == "NON_CONFORME_ETAYE":
        return "fail"
    if status.startswith("NON_APPLICABLE"):
        return "na"
    return "pending"


def baseline_status(test_id: str) -> str:
    if test_id in ARCHIVE_PROVEN_CONFORMING:
        return "TESTE_CONFORME"
    if test_id in ARCHIVE_PROVEN_NONCONFORMING:
        return "TESTE_NON_CONFORME"
    if test_id in ARCHIVE_RETEST:
        return "A_RETESTER"
    if test_id in ARCHIVE_NOT_TESTED:
        return "NON_TESTE"
    if test_id in ARCHIVE_NA_SUPPORTED:
        return "NON_APPLICABLE_CONDITIONNEL_DOM"
    raise KeyError(test_id)


def current_status(test_id: str) -> str:
    if test_id in ARCHIVE_PROVEN_CONFORMING | TECHNICALLY_PREQUALIFIED:
        return "CONFORME_TECHNIQUE_ETAYEE_A_VALIDER_HUMAINEMENT"
    if test_id in ARCHIVE_PROVEN_NONCONFORMING:
        return "NON_CONFORME_ETAYE"
    if test_id in ARCHIVE_NA_SUPPORTED:
        return "NON_APPLICABLE_CONDITIONNEL_DOM"
    if test_id in SERVER_RETEST:
        return "A_RETESTER_SERVEUR"
    if test_id in BUSINESS_REVIEW:
        return "NON_APPLICABLE_A_CONFIRMER_METIER"
    return "A_QUALIFIER_HUMAINEMENT"


def generic_rationale(test_id: str, status: str) -> str:
    if test_id in RATIONALES:
        return RATIONALES[test_id]
    if status.startswith("CONFORME_TECHNIQUE"):
        return "Les preuves comportent un contrôle technique ciblé, mais la validation humaine requise par le contrat de preuve n’est pas signée dans le registre de revue."
    if status == "NON_APPLICABLE_CONDITIONNEL_DOM":
        return "Le DOM observé ne contient aucune cible correspondant au mécanisme testé. Cette non-applicabilité reste conditionnelle aux états capturés et à la qualification sémantique du critère parent."
    if status == "NON_APPLICABLE_A_CONFIRMER_METIER":
        return "Le formulaire de contact ne paraît ni modifier/supprimer des données existantes, ni constituer un test, ni emporter par lui-même une conséquence financière ou juridique. Cette qualification doit être confirmée par la MOA métier."
    return "La pertinence, l’applicabilité ou le rendu nécessite encore une revue humaine ciblée ; les collecteurs automatiques ne produisent pas cette décision."


def assert_safe_evidence(evidence: dict[str, Any]) -> None:
    if evidence.get("schema_version") != 2 or not evidence.get("run_id"):
        raise ValueError("Le retest ne suit pas le schéma probatoire v2 avec run_id.")
    collector = evidence.get("collector", {})
    collector_path = ROOT / collector.get("file", "")
    if (
        not collector_path.is_file()
        or collector.get("file") != "scripts/retest-p06-form-safe.py"
        or sha256(collector_path) != collector.get("sha256")
    ):
        raise ValueError("Le hash du collecteur ne correspond pas au source courant.")
    if evidence.get("unexpected_page_errors") != []:
        raise ValueError("Le retest contient une erreur de page inattendue.")
    page_errors = evidence.get("page_errors", [])
    guard_window_errors = evidence.get("guard_window_page_errors", [])
    if (
        len(page_errors) != 1
        or guard_window_errors != page_errors
        or page_errors[0].get("scenario") != "five_allowed_files"
        or page_errors[0].get("message") != "Drupal.AjaxError"
        or page_errors[0].get("attribution") != "guard-window-causality-unproven"
        or not evidence.get("page_error_attribution_limit")
    ):
        raise ValueError("La limite d’attribution de l’erreur page cinq fichiers est incohérente.")
    if evidence.get("mode") != "SAFE_NO_MUTATING_REQUEST":
        raise ValueError("Le fichier de preuve ne provient pas du mode sûr attendu.")
    contract = evidence.get("safety_contract", {})
    if set(contract.get("allowed_http_methods", [])) != {"GET", "HEAD", "OPTIONS"}:
        raise ValueError("Le contrat de sécurité n’applique pas l’allowlist HTTP attendue.")
    if contract.get("synthetic_data_only") is not True:
        raise ValueError("Le contrat de sécurité ne garantit pas des données exclusivement synthétiques.")
    if contract.get("valid_final_submission") is not False:
        raise ValueError("Le contrat de sécurité autorise ou ne documente pas la soumission finale.")
    if contract.get("server_mutation_authorized") is not False:
        raise ValueError("Le contrat de sécurité autorise ou ne documente pas une mutation serveur.")
    guard = evidence.get("network_guard", {})
    if guard.get("guard_scope") != "BrowserContext":
        raise ValueError("La garde réseau n’est pas installée au niveau du contexte navigateur.")
    if guard.get("completed_mutating_requests") != []:
        raise ValueError("La preuve contient une requête mutante terminée.")
    if guard.get("mutating_request_completed") is not False:
        raise ValueError("Une requête mutante pourrait avoir été transmise.")
    if guard.get("websocket_application_message_completed") is not False:
        raise ValueError("Un message applicatif WebSocket pourrait avoir été transmis.")
    if guard.get("blocked_count") != len(guard.get("blocked_requests", [])):
        raise ValueError("Le compteur global des requêtes bloquées est incohérent.")
    if guard.get("blocked_websocket_count") != len(guard.get("blocked_websockets", [])):
        raise ValueError("Le compteur global des WebSockets bloqués est incohérent.")
    for request in guard.get("blocked_requests", []):
        if request.get("decision") != "ABORTED_BEFORE_SEND":
            raise ValueError("Une requête mutante n’a pas la décision de blocage attendue.")
    for websocket in guard.get("blocked_websockets", []):
        if websocket.get("decision") != "CLOSED_BEFORE_APPLICATION_MESSAGES":
            raise ValueError("Une connexion WebSocket n’a pas la décision de blocage attendue.")
    multipage = evidence.get("multipage_labels", {})
    page_ids = [page.get("page") for page in multipage.get("pages", [])]
    comparisons = multipage.get("repeated_control_comparisons", [])
    if (
        multipage.get("pages_complete") is not True
        or multipage.get("page_failures") != []
        or len(page_ids) != 9
        or set(page_ids) != {f"P{index:02d}" for index in range(1, 10)}
        or len(comparisons) != 4
        or any(
            comparison.get("complete") is not True
            or comparison.get("coherent") is not True
            or set(comparison.get("pages", [])) != set(page_ids)
            for comparison in comparisons
        )
        or multipage.get("all_expected_repeated_dom_candidates_complete_and_coherent") is not True
    ):
        raise ValueError("Les quatre candidats DOM attendus ne sont pas complets et cohérents sur P01–P09.")
    scenarios = evidence.get("scenarios", {})
    if scenarios.get("empty_native_submit", {}).get("active_element", {}).get("id") != "edit-nom":
        raise ValueError("Le focus de la soumission vide n’est pas établi sur #edit-nom.")
    if scenarios.get("invalid_email_native", {}).get("active_element", {}).get("id") != "edit-adressemail":
        raise ValueError("Le focus de l’email invalide n’est pas établi sur #edit-adressemail.")
    company = scenarios.get("professional_variant", {}).get("company", {})
    if (
        company.get("visible") is not True
        or company.get("required") is not False
        or company.get("aria_required") not in {None, "false"}
        or company.get("disabled") is not False
        or not company.get("labels")
        or company.get("autocomplete") is not None
        or evidence["scenarios"]["professional_variant"].get("optional_mentioned") is not False
    ):
        raise ValueError("La variante Société ne correspond plus à la preuve attendue.")
    extension_messages = [
        message
        for message in evidence["scenarios"]["invalid_file_extension"]["visible_messages"]
        if "preuve-synthetique-interdite.exe" in message.get("text", "")
    ]
    if len(extension_messages) != 1:
        raise ValueError("Le message nominatif d’extension interdite est absent ou ambigu.")
    extension_message = extension_messages[0]
    if (
        extension_message.get("role") is not None
        or extension_message.get("aria_live") != "polite"
        or extension_message.get("aria_atomic") is not None
    ):
        raise ValueError(
            "La sémantique du message d’extension a changé ; la décision 7.5.2 doit être recalculée."
        )
    if evidence["scenarios"]["invalid_file_extension"]["blocked_mutating_requests"]:
        raise ValueError("Le scénario extension interdite ne devrait déclencher aucune requête mutante.")
    five_files = evidence["scenarios"]["five_allowed_files"]
    trigger = five_files.get("triggering_request") or {}
    if (
        len(five_files.get("blocked_mutating_requests", [])) != 1
        or guard.get("blocked_count") != 1
        or guard.get("blocked_requests") != five_files.get("blocked_mutating_requests")
        or five_files.get("guard_correlation_exact") is not True
        or trigger.get("method") != "POST"
        or trigger.get("resource_type") not in {"xhr", "fetch"}
        or "ajax_form=1" not in trigger.get("url", "")
        or "element_parents=fieldset/Document" not in trigger.get("url", "")
        or len(trigger.get("synthetic_file_names_in_post_data", {})) != 5
        or not all(trigger["synthetic_file_names_in_post_data"].values())
    ):
        raise ValueError("Le scénario cinq fichiers n’est pas corrélé exactement à la garde réseau.")
    for scenario_name, scenario in evidence.get("scenarios", {}).items():
        screenshot = scenario.get("screenshot")
        if not screenshot:
            raise ValueError(f"Capture absente pour le scénario {scenario_name}.")
        relative = screenshot.get("file", "")
        relative_path = Path(relative)
        if not relative or relative_path.is_absolute() or ".." in relative_path.parts:
            raise ValueError(f"Chemin de capture non sûr pour le scénario {scenario_name}.")
        screenshot_path = (OUTPUT / relative_path).resolve()
        if not screenshot_path.is_relative_to(OUTPUT.resolve()):
            raise ValueError(f"Capture hors complément P06 pour le scénario {scenario_name}.")
        if not screenshot_path.is_file():
            raise ValueError(f"Capture introuvable pour le scénario {scenario_name} : {relative}")
        if screenshot_path.stat().st_size != screenshot.get("bytes"):
            raise ValueError(f"Taille de capture incohérente pour le scénario {scenario_name}.")
        if sha256(screenshot_path) != screenshot.get("sha256"):
            raise ValueError(f"Empreinte de capture incohérente pour le scénario {scenario_name}.")


def build_matrix() -> tuple[dict[str, Any], dict[str, Any]]:
    reference = load_json(rgaa_reference())
    decision_doc = load_json(DECISIONS)
    manual_doc = load_json(MANUAL_REVIEWS)
    evidence = load_json(EVIDENCE)
    assert_safe_evidence(evidence)

    tests = [item for item in reference["tests"] if item["criterion_id"].startswith("11.")]
    expected = {item["test_id"] for item in tests}
    if len(tests) != 34 or len(expected) != 34:
        raise ValueError(
            f"Référentiel thème 11 inattendu : {len(tests)} lignes, {len(expected)} identifiants uniques."
        )
    classification_groups = [
        ARCHIVE_PROVEN_CONFORMING,
        ARCHIVE_PROVEN_NONCONFORMING,
        ARCHIVE_RETEST,
        ARCHIVE_NOT_TESTED,
        ARCHIVE_NA_SUPPORTED,
    ]
    classified = set().union(*classification_groups)
    overlapping = {
        test_id
        for test_id in classified
        if sum(test_id in group for group in classification_groups) != 1
    }
    if overlapping:
        raise ValueError(f"Catégories probatoires chevauchantes : {sorted(overlapping)}")
    if expected != classified:
        raise ValueError(f"Classification probatoire incomplète : {sorted(expected ^ classified)}")
    overlay_groups = [TECHNICALLY_PREQUALIFIED, SERVER_RETEST, BUSINESS_REVIEW]
    overlay_union = set().union(*overlay_groups)
    overlay_overlaps = {
        test_id
        for test_id in overlay_union
        if sum(test_id in group for group in overlay_groups) != 1
    }
    if overlay_overlaps:
        raise ValueError(f"Surcouches de conclusion chevauchantes : {sorted(overlay_overlaps)}")
    if not TECHNICALLY_PREQUALIFIED <= ARCHIVE_RETEST:
        raise ValueError("Une conformité technique ne provient pas du groupe de retest attendu.")
    if not SERVER_RETEST <= ARCHIVE_RETEST:
        raise ValueError("Un retest serveur ne provient pas du groupe de retest attendu.")
    if not BUSINESS_REVIEW <= ARCHIVE_NOT_TESTED:
        raise ValueError("Une confirmation métier ne provient pas du groupe non testé attendu.")

    decision_rows = [
        item for item in decision_doc["decisions"] if item["criterion"].startswith("11.")
    ]
    review_rows = [
        item for item in manual_doc["reviews"] if item["criterion"].startswith("11.")
    ]
    if len(decision_rows) != 34 or len({item["test"] for item in decision_rows}) != 34:
        raise ValueError("La matrice publiée ne contient pas 34 lignes thème 11 uniques.")
    if len(review_rows) != 34 or len({item["test"] for item in review_rows}) != 34:
        raise ValueError("La revue manuelle ne contient pas 34 lignes thème 11 uniques.")
    decisions = {item["test"]: item for item in decision_rows}
    reviews = {item["test"]: item for item in review_rows}
    if set(decisions) != expected or set(reviews) != expected:
        raise ValueError("La matrice publiée ou la revue manuelle ne contient pas exactement les 34 tests.")
    if decisions["11.10.2"].get("status") != "C_CONFIRMEE":
        raise ValueError(
            "La décision publiée 11.10.2 n’est plus C_CONFIRMEE ; la requalification doit être recalculée."
        )
    published_7_5_2_rows = [
        item for item in decision_doc["decisions"] if item.get("test") == "7.5.2"
    ]
    if len(published_7_5_2_rows) != 1:
        raise ValueError("La décision publiée 7.5.2 est absente ou dupliquée.")
    published_7_5_2 = published_7_5_2_rows[0]
    if published_7_5_2.get("status") != "NA_CONFIRMEE":
        raise ValueError(
            "La décision publiée 7.5.2 n’est plus NA_CONFIRMEE ; la requalification doit être recalculée."
        )

    p06_page = next(
        page for page in evidence["multipage_labels"]["pages"] if page["page"] == "P06"
    )
    unnamed_controls = [
        item
        for item in p06_page["controls"]
        if item.get("exposed_to_at_candidate") and not item.get("accessible_name_candidate")
    ]
    required_controls = [
        item
        for item in p06_page["controls"]
        if item.get("required") is True or item.get("aria_required") == "true"
    ]
    required_without_associated_indication = []
    for item in required_controls:
        associated_text = " ".join(
            [
                *item.get("visible_label_texts", []),
                item.get("visible_labelledby_text", ""),
                item.get("visible_describedby_text", ""),
            ]
        )
        if not has_positive_required_indication(associated_text):
            required_without_associated_indication.append(item)
    if not required_controls or not required_without_associated_indication:
        raise ValueError(
            "La non-conformité 11.10.2 n’est plus étayée par un champ required sans indication associée."
        )

    rows = []
    for test in tests:
        test_id = test["test_id"]
        status = current_status(test_id)
        evidence_refs = list(decisions[test_id].get("evidence", []))
        if test_id in TECHNICALLY_PREQUALIFIED | SERVER_RETEST:
            evidence_refs.insert(0, "P06-FORMULAIRES/preuves/P06-RETEST-SAFE.json")
        rows.append(
            {
                "criterion": test["criterion_id"],
                "test": test_id,
                "title": " ".join(test["title"]),
                "published_status": decisions[test_id]["status"],
                "published_coverage_complete": decisions[test_id]["coverage_complete"],
                "manual_review_status": reviews[test_id]["status"],
                "probative_baseline": baseline_status(test_id),
                "supplement_status": status,
                "supplement_label": STATUS_LABELS[status],
                "rationale": generic_rationale(test_id, status),
                "human_validation": test.get("human_validation", reviews[test_id].get("human_validation")),
                "evidence": evidence_refs,
                "official_url": f"{OFFICIAL_RGAA}#{test_id}",
            }
        )

    extension_message = next(
        message
        for message in evidence["scenarios"]["invalid_file_extension"]["visible_messages"]
        if "preuve-synthetique-interdite.exe" in message.get("text", "")
    )
    adjacent = {
        "criterion": "7.5",
        "test": "7.5.2",
        "status": "NON_CONFORME_ETAYE",
        "label": "Non conforme étayé — complément P06",
        "observation": (
            "Le message dynamique d’extension interdite est une erreur/suggestion. "
            f"Le conteneur observé porte aria-live=\"{extension_message.get('aria_live')}\", "
            "sans role et sans aria-atomic. Il ne satisfait donc ni role=\"alert\", "
            "ni l’équivalent aria-live=\"assertive\" avec aria-atomic=\"true\"."
        ),
        "message": extension_message["text"],
        "screenshot": evidence["scenarios"]["invalid_file_extension"]["screenshot"]["file"],
        "evidence": [
            "P06-FORMULAIRES/preuves/P06-RETEST-SAFE.json",
            "P06-FORMULAIRES/"
            + evidence["scenarios"]["invalid_file_extension"]["screenshot"]["file"],
            "P06-FORMULAIRES/preuves/P06-ETAT-SERVEUR-ARCHIVE.json",
        ],
        "published_status": published_7_5_2["status"],
        "requalification_required": True,
    }

    required_indication_decision = {
        "criterion": "11.10",
        "test": "11.10.2",
        "status": "NON_CONFORME_ETAYE",
        "label": "Non conforme étayé — décision publiée à requalifier",
        "published_status": decisions["11.10.2"]["status"],
        "observation": (
            f"{len(required_without_associated_indication)} "
            f"champ{'s' if len(required_without_associated_indication) != 1 else ''} portant required ne "
            "présentent aucune indication de caractère obligatoire dans leur étiquette, "
            "aria-labelledby ou aria-describedby. L’instruction générale n’est associée à aucun de ces champs."
        ),
        "affected_control_ids": [
            item.get("id") for item in required_without_associated_indication
        ],
        "screenshot": evidence["scenarios"]["empty_native_submit"]["screenshot"]["file"],
        "evidence": [
            "P06-FORMULAIRES/preuves/P06-RETEST-SAFE.json",
            "P06-FORMULAIRES/"
            + evidence["scenarios"]["empty_native_submit"]["screenshot"]["file"],
        ],
        "requalification_required": True,
    }

    counts = Counter(row["supplement_status"] for row in rows)
    manual_counts = Counter(row["manual_review_status"] for row in rows)
    baseline_counts = Counter(row["probative_baseline"] for row in rows)
    generated = {
        "schema_version": 1,
        "generated_at": evidence["generated_at"],
        "page": {"id": "P06", "name": "Formulaire Écrivez-nous", "url": P06_URL},
        "referential": "RGAA 4.1.2",
        "theme": "11 — Formulaires",
        "tests_count": len(rows),
        "audit_mode": "Complément instrumenté sûr, sans requête mutante",
        "safety": {
            "allowed_http_methods": evidence["safety_contract"]["allowed_http_methods"],
            "guard_scope": evidence["network_guard"]["guard_scope"],
            "mutating_requests_completed": evidence["network_guard"]["mutating_request_completed"],
            "completed_mutating_request_details": evidence["network_guard"]["completed_mutating_requests"],
            "blocked_mutating_requests": evidence["network_guard"]["blocked_count"],
            "blocked_request_details": evidence["network_guard"]["blocked_requests"],
            "blocked_websockets": evidence["network_guard"]["blocked_websocket_count"],
            "blocked_websocket_details": evidence["network_guard"]["blocked_websockets"],
            "websocket_application_message_completed": evidence["network_guard"]["websocket_application_message_completed"],
            "synthetic_data_only": evidence["safety_contract"]["synthetic_data_only"],
            "valid_final_submission": evidence["safety_contract"]["valid_final_submission"],
            "server_mutation_authorized": evidence["safety_contract"]["server_mutation_authorized"],
            "page_errors_observed": len(evidence["page_errors"]),
            "guard_window_page_errors": evidence["guard_window_page_errors"],
            "page_error_attribution_limit": evidence["page_error_attribution_limit"],
        },
        "published_theme_11_counts": dict(
            sorted(Counter(item["status"] for item in decision_rows).items())
        ),
        "published_full_258_counts": decision_doc["counts"],
        "probative_baseline_counts": dict(sorted(baseline_counts.items())),
        "manual_review_counts": dict(sorted(manual_counts.items())),
        "supplement_counts": dict(sorted(counts.items())),
        "client_transmission_ready": False,
        "blocking_reasons": [
            f"{counts.get('A_RETESTER_SERVEUR', 0)} branches nécessitent encore une véritable réponse serveur : 11.10.6, 11.10.7, 11.11.1 et 11.11.2.",
            "Une erreur Drupal.AjaxError a été observée dans la fenêtre du POST bloqué ; son lien causal avec la garde ne peut pas être établi par pageerror.",
            f"{counts.get('A_QUALIFIER_HUMAINEMENT', 0)} décisions restent à qualifier humainement et {counts.get('NON_APPLICABLE_A_CONFIRMER_METIER', 0)} non-applicabilités à confirmer par la MOA métier.",
            "Le test 11.10.2 publié conforme et le test adjacent 7.5.2 publié NA doivent être requalifiés en non-conformité.",
            "Aucun test réel NVDA, JAWS ou VoiceOver n’est joint.",
        ],
        "safe_retest": {
            "generated_at": evidence["generated_at"],
            "run_id": evidence["run_id"],
            "collector": evidence["collector"],
            "screenshots": {
                name: scenario["screenshot"] for name, scenario in evidence["scenarios"].items()
            },
            "p06_controls_inventoried": len(p06_page["controls"]),
            "p06_controls_without_name_candidate": len(unnamed_controls),
            "required_controls_observed": len(required_controls),
            "required_controls_without_associated_indication": len(
                required_without_associated_indication
            ),
            "required_control_violation_ids": [
                item.get("id") for item in required_without_associated_indication
            ],
            "repeated_controls_compared": len(
                evidence["multipage_labels"]["repeated_control_comparisons"]
            ),
            "repeated_controls_coherent": evidence["multipage_labels"][
                "all_expected_repeated_dom_candidates_complete_and_coherent"
            ],
            "native_empty_focus": evidence["scenarios"]["empty_native_submit"][
                "active_element"
            ],
            "native_invalid_email_focus": evidence["scenarios"]["invalid_email_native"][
                "active_element"
            ],
            "invalid_extension_message": extension_message,
            "five_files_server_response_available": evidence["scenarios"][
                "five_allowed_files"
            ]["server_result_available"],
        },
        "decisions": rows,
        "theme_requalification": required_indication_decision,
        "adjacent_decision": adjacent,
        "requalifications": [required_indication_decision, adjacent],
        "source_integrity": {
            "safe_evidence_sha256": sha256(EVIDENCE),
            "published_decisions_sha256": sha256(DECISIONS),
            "manual_reviews_sha256": sha256(MANUAL_REVIEWS),
            "archived_server_state_sha256": sha256(ARCHIVED_SERVER_STATE),
            "archived_company_state_sha256": sha256(ARCHIVED_COMPANY_STATE),
            "reference_sha256": sha256(rgaa_reference()),
        },
    }
    return generated, evidence


def markdown_table(rows: list[dict[str, Any]]) -> str:
    lines = [
        "| Critère | Test | Décision publiée | Base probatoire | Conclusion du complément | Justification |",
        "|---|---|---|---|---|---|",
    ]
    for row in rows:
        rationale = row["rationale"].replace("|", "/").replace("\n", " ")
        lines.append(
            f"| {row['criterion']} | [{row['test']}]({row['official_url']}) | "
            f"`{row['published_status']}` | `{row['probative_baseline']}` | "
            f"**{row['supplement_label']}** | {rationale} |"
        )
    return "\n".join(lines)


def render_markdown(doc: dict[str, Any], evidence: dict[str, Any]) -> str:
    counts = doc["supplement_counts"]
    blocked = doc["safety"]["blocked_mutating_requests"]
    comparisons = evidence["multipage_labels"]["repeated_control_comparisons"]
    comparison_lines = "\n".join(
        f"- `{item['identity']}` — {', '.join(item['pages'])} — intitulé(s) : "
        f"nom accessible {', '.join(repr(name) for name in item['accessible_names'])}; "
        f"libellé DOM {', '.join(repr(label) for label in item['label_texts'])}; "
        f"visible dans tous les états : **{'oui' if item['visible_label_observed_on_all_pages'] else 'non'}** — "
        "correspondance DOM exacte, conformité RGAA à confirmer."
        for item in comparisons
    )
    screenshots = {
        name: scenario["screenshot"]["file"]
        for name, scenario in evidence["scenarios"].items()
    }
    return f"""# P06 — Complément de couverture RGAA « Formulaires »

**Page :** [Formulaire Écrivez-nous]({P06_URL})  
**Référentiel :** RGAA 4.1.2 — thème 11, 34 tests  
**Mode :** retest instrumenté sûr, données synthétiques, aucune requête mutante transmise  
**Prêt à transmettre comme audit final :** **non**

## Conclusion

La matrice publiée contient bien les 34 tests, mais elle ne prouve pas les 19 conformités annoncées. Après relecture probatoire et complément Playwright :

- {counts.get('CONFORME_TECHNIQUE_ETAYEE_A_VALIDER_HUMAINEMENT', 0)} tests sont techniquement étayés comme conformes, sans validation humaine finale signée ;
- {counts.get('NON_CONFORME_ETAYE', 0)} tests du thème 11 disposent d’une non-conformité étayée ;
- {counts.get('NON_APPLICABLE_CONDITIONNEL_DOM', 0)} tests sont non applicables conditionnellement dans le DOM observé ;
- {counts.get('A_QUALIFIER_HUMAINEMENT', 0)} tests restent à qualifier humainement ;
- {counts.get('NON_APPLICABLE_A_CONFIRMER_METIER', 0)} non-applicabilités restent à confirmer par la MOA métier ;
- {counts.get('A_RETESTER_SERVEUR', 0)} tests exigent encore une réponse serveur réelle.

Le test **11.10.2**, publié conforme, est requalifié non conforme : les indications obligatoires ne figurent ni dans les étiquettes ni dans des passages associés. Un défaut adjacent est aussi confirmé pour **RGAA 7.5.2** : les messages d’erreur dynamiques observés n’utilisent ni `role="alert"`, ni `aria-live="assertive"` avec `aria-atomic="true"`.

## Garantie de non-soumission

- Méthodes autorisées : `GET`, `HEAD`, `OPTIONS`.
- Toute autre méthode est bloquée avant envoi.
- Toute connexion WebSocket est fermée avant les messages applicatifs.
- {blocked} tentative AJAX `POST` a été interceptée lors du scénario « cinq fichiers ».
- Une erreur `Drupal.AjaxError` a été observée dans la même fenêtre d’action ; `pageerror` ne permet pas d’en prouver la causalité avec la garde.
- Aucun formulaire valide ni fichier n’a été transmis au serveur.

## Résultats du retest sûr

### Étiquettes répétées sur P01 à P09

{comparison_lines}

### États dynamiques

- Soumission native vide : focus déplacé sur `#{evidence['scenarios']['empty_native_submit']['active_element']['id']}` ; aucune requête mutante.
- Email invalide : focus déplacé sur `#{evidence['scenarios']['invalid_email_native']['active_element']['id']}` ; message natif du navigateur et exemple visible `nom@domaine.fr`.
- Variante professionnel : Société visible, facultatif techniquement, sans mention « optionnel » et sans `autocomplete="organization"`.
- Extension `.exe` : message français visible donnant les extensions autorisées, produit sans requête mutante.
- Cinq fichiers autorisés par extension : tentative AJAX bloquée ; le véritable message serveur n’est donc pas disponible.
- Le champ fichier conserve un `aria-describedby` vers `#edit-document--description`, cible absente dans les deux états testés.

## Requalification RGAA 11.10.2

**Décision publiée :** `C_CONFIRMEE`  
**Complément :** **NON_CONFORME_ETAYE**

{doc['theme_requalification']['observation']}

Voir le ticket candidat : [TICKET-CANDIDAT-RGAA-11.10.2.md](TICKET-CANDIDAT-RGAA-11.10.2.md).

## Requalification RGAA 7.5.2

**Décision publiée :** `NA_CONFIRMEE`  
**Complément :** **NON_CONFORME_ETAYE**

{doc['adjacent_decision']['observation']}

Message observé : « {doc['adjacent_decision']['message']} »

Voir le ticket candidat : [TICKET-CANDIDAT-RGAA-7.5.2.md](TICKET-CANDIDAT-RGAA-7.5.2.md).

## Matrice probatoire des 34 tests

{markdown_table(doc['decisions'])}

## Contrôles restant à réaliser

1. Autoriser, dans un environnement de recette isolé, le retour serveur du scénario cinq fichiers avec données factices.
2. Faire qualifier humainement les intitulés, la proximité responsive, les regroupements, les boutons et la nécessité des `optgroup`.
3. Faire confirmer par la MOA métier la non-applicabilité de 11.12.1 et 11.12.2.
4. Vérifier l’annonce des erreurs avec NVDA + Firefox et/ou VoiceOver + Safari.
5. Réconcilier le registre `REVUE-MANUELLE-258` avec les décisions finales signées.

## Preuves livrées

- [Données structurées du retest sûr](preuves/P06-RETEST-SAFE.json)
- [Soumission native vide]({screenshots['empty_native_submit']})
- [Email invalide]({screenshots['invalid_email_native']})
- [Variante professionnel]({screenshots['professional_variant']})
- [Extension interdite]({screenshots['invalid_file_extension']})
- [Cinq fichiers, requête bloquée]({screenshots['five_allowed_files']})
- [État serveur archivé, copie intègre](preuves/P06-ETAT-SERVEUR-ARCHIVE.json)
- [État Société optionnel archivé, copie intègre](preuves/P06-SOCIETE-OPTIONNEL-ARCHIVE.json)
- [Matrice JSON du complément](COUVERTURE-RGAA-11.json)

## Sources archivées non dupliquées

- `archives/audit-douane-p06-complet-rgaa-dsfr-2026-09-02/rgaa/P06-DECISIONS-258.json`
- `archives/audit-douane-p06-complet-rgaa-dsfr-2026-09-02/rgaa/REVUE-MANUELLE-258.json`

La présence d’une ligne dans une matrice ne vaut pas exécution du test. Ce document distingue volontairement inventaire, preuve technique, validation humaine et parcours serveur.
"""


def table_html(headers: list[str], rows: list[list[str]]) -> str:
    head = "".join(f"<th scope=\"col\">{item}</th>" for item in headers)
    body = "".join(
        "<tr>" + "".join(f"<td>{cell}</td>" for cell in row) + "</tr>" for row in rows
    )
    return f'<div class="table-wrap"><table><thead><tr>{head}</tr></thead><tbody>{body}</tbody></table></div>'


def render_html(doc: dict[str, Any], evidence: dict[str, Any]) -> str:
    counts = doc["supplement_counts"]
    matrix_rows = []
    for row in doc["decisions"]:
        status = row["supplement_status"]
        matrix_rows.append(
            [
                html.escape(row["criterion"]),
                f'<a href="{html.escape(row["official_url"])}">{html.escape(row["test"])}</a>',
                f'<code>{html.escape(row["published_status"])}</code>',
                f'<code>{html.escape(row["probative_baseline"])}</code>',
                f'<span class="badge {status_class(status)}">{html.escape(row["supplement_label"])}</span>',
                html.escape(row["rationale"]),
            ]
        )
    comparison_rows = [
        [
            f'<code>{html.escape(item["identity"])}</code>',
            html.escape(", ".join(item["pages"])),
            html.escape(
                "Nom accessible : "
                + " / ".join(item["accessible_names"])
                + " — libellé : "
                + " / ".join(item["label_texts"])
            ),
            (
                '<span class="badge pass">Observé</span>'
                if item["visible_label_observed_on_all_pages"]
                else '<span class="badge pending">État visible non observé partout</span>'
            ),
            '<span class="badge pending">Candidats DOM concordants — RGAA à confirmer</span>',
        ]
        for item in evidence["multipage_labels"]["repeated_control_comparisons"]
    ]
    screenshot_figures = "".join(
        f'<figure><a href="{html.escape(evidence["scenarios"][scenario]["screenshot"]["file"], quote=True)}"><img src="{html.escape(evidence["scenarios"][scenario]["screenshot"]["file"], quote=True)}" alt="{html.escape(alt)}"></a><figcaption>{html.escape(caption)}</figcaption></figure>'
        for scenario, alt, caption in (
            ("empty_native_submit", "Formulaire avec message natif de champ obligatoire", "Soumission native vide : focus sur Nom."),
            ("invalid_email_native", "Formulaire avec adresse électronique invalide", "Email invalide : message natif, aucune soumission."),
            ("professional_variant", "Formulaire dans la variante professionnel", "Champ Société visible, facultatif et sans autocomplete."),
            ("invalid_file_extension", "Message d’erreur pour extension de fichier interdite", "Extension interdite : message client obtenu sans POST."),
            ("five_allowed_files", "Formulaire après sélection de cinq fichiers synthétiques", "Cinq fichiers : POST AJAX bloqué avant envoi."),
        )
    )
    return f"""<!doctype html>
<html lang="fr">
<head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>P06 — Complément RGAA Formulaires</title><meta name="description" content="Matrice probatoire et retest sûr des 34 tests RGAA du thème Formulaires pour P06."><style>{CSS}</style></head>
<body>
<a class="skip" href="#contenu">Aller au contenu</a>
<header><div class="container"><p><a href="../INDEX-LIVRABLES.html">← Tous les livrables</a></p><h1>P06 — Complément RGAA « Formulaires »</h1><p>34 tests rapprochés des preuves archivées et d’un retest Playwright sans requête mutante.</p></div></header>
<main id="contenu" class="container">
<div class="notice warning" role="note"><strong>Conclusion :</strong> la matrice est exhaustive mais l’audit n’est pas clôturé. Le complément sépare les décisions étayées des validations humaines, métier ou serveur encore requises.</div>
<section class="cards" aria-label="Synthèse">
<article class="card"><p class="count">34/34</p><h2>Tests inventoriés</h2><p>Aucun identifiant manquant.</p></article>
<article class="card"><p class="count">{counts.get('CONFORME_TECHNIQUE_ETAYEE_A_VALIDER_HUMAINEMENT', 0)}</p><h2>Conformités techniques</h2><p>Toutes restent à valider humainement et à signer.</p></article>
<article class="card"><p class="count">{counts.get('NON_CONFORME_ETAYE', 0)} + 1</p><h2>Non-conformités</h2><p>{counts.get('NON_CONFORME_ETAYE', 0)} au thème 11 et une requalification 7.5.2.</p></article>
<article class="card"><p class="count">{counts.get('A_RETESTER_SERVEUR', 0)}</p><h2>Retests serveur</h2><p>Maintenus ouverts par le mode sans soumission.</p></article>
</section>
<h2>Garantie de non-soumission</h2>
<div class="notice safe"><strong>Aucune requête mutante transmise.</strong> Seules GET, HEAD et OPTIONS étaient autorisées ; toute connexion WebSocket était fermée avant les messages applicatifs. Une tentative AJAX POST déclenchée par cinq fichiers a été enregistrée puis bloquée avant envoi. Données et fichiers exclusivement synthétiques.</div>
<div class="notice warning"><strong>Limite d’attribution :</strong> une erreur <code>Drupal.AjaxError</code> a été observée dans la même fenêtre d’action ; l’événement <code>pageerror</code> ne permet pas d’en prouver le lien causal avec la garde.</div>
<p><a href="preuves/P06-RETEST-SAFE.json">Consulter la preuve structurée complète</a>.</p>
<h2>Résultats ciblés</h2>
<ul>
<li>Soumission vide : focus sur <code>#{html.escape(evidence['scenarios']['empty_native_submit']['active_element']['id'])}</code>, sans requête mutante.</li>
<li>Email invalide : focus sur <code>#{html.escape(evidence['scenarios']['invalid_email_native']['active_element']['id'])}</code>, message natif et exemple visible.</li>
<li>Extension interdite : message précis donnant les extensions autorisées, sans POST.</li>
<li>Cinq fichiers : réponse serveur non observée car la tentative POST a été bloquée.</li>
<li>Le champ fichier référence toujours <code>#edit-document--description</code>, cible absente.</li>
</ul>
<h2>Cohérence multipage — 11.3.2</h2>
{table_html(['Contrôle répété','Pages','Candidats DOM','Libellé visible observé','Portée'], comparison_rows)}
<p>La comparaison couvre les neuf pages et établit seulement une correspondance exacte des candidats DOM. La visibilité dans chaque état, la notion de fonction identique et la conformité RGAA restent à qualifier humainement.</p>
<h2>Requalification nécessaire — 11.10.2</h2>
<div class="notice"><p><strong>Décision publiée :</strong> <code>C_CONFIRMEE</code><br><strong>Complément :</strong> <span class="badge fail">Non conforme étayé</span></p><p>{html.escape(doc['theme_requalification']['observation'])}</p></div>
<p><a href="TICKET-CANDIDAT-RGAA-11.10.2.html">Ouvrir le ticket candidat RGAA 11.10.2</a>.</p>
<h2>Requalification nécessaire — 7.5.2</h2>
<div class="notice"><p><strong>Décision publiée :</strong> <code>NA_CONFIRMEE</code><br><strong>Complément :</strong> <span class="badge fail">Non conforme étayé</span></p><p>{html.escape(doc['adjacent_decision']['observation'])}</p></div>
<p><a href="TICKET-CANDIDAT-RGAA-7.5.2.html">Ouvrir le ticket candidat RGAA 7.5.2</a>.</p>
<h2>Matrice probatoire des 34 tests</h2>
{table_html(['Critère','Test','Publié','Base probatoire','Complément','Justification'], matrix_rows)}
<h2>Validations encore requises</h2>
<ol><li>Réponse serveur réelle du scénario cinq fichiers en recette isolée.</li><li>Revue humaine des intitulés, placements responsive, regroupements, boutons et listes de choix.</li><li>Confirmation métier pour 11.12.1 et 11.12.2.</li><li>Test NVDA + Firefox et/ou VoiceOver + Safari des annonces dynamiques.</li><li>Réconciliation et signature du registre de revue manuelle.</li></ol>
<h2>Captures</h2><div class="evidence-grid">{screenshot_figures}</div>
<h2>Fichiers du complément</h2><ul><li><a href="COUVERTURE-RGAA-11.md">Version Markdown</a></li><li><a href="COUVERTURE-RGAA-11.json">Matrice JSON</a></li><li><a href="TICKET-CANDIDAT-RGAA-11.10.2.html">Ticket candidat 11.10.2</a></li><li><a href="TICKET-CANDIDAT-RGAA-7.5.2.html">Ticket candidat 7.5.2</a></li><li><a href="preuves/P06-ETAT-SERVEUR-ARCHIVE.json">État serveur archivé</a></li><li><a href="preuves/P06-SOCIETE-OPTIONNEL-ARCHIVE.json">État Société optionnel archivé</a></li><li><a href="../RGAA/P06-RGAA.html">Rapport RGAA P06 initial</a></li><li><a href="../TICKETS-RGAA/INDEX-TICKETS-RGAA.html">Tickets RGAA existants</a></li></ul>
</main>
<footer><div class="container"><p>Complément P06 — préqualification instrumentée, sans taux RGAA officiel.</p></div></footer>
</body></html>
"""


def render_candidate_markdown(doc: dict[str, Any]) -> str:
    adjacent = doc["adjacent_decision"]
    return f"""# TICKET-CANDIDAT-RGAA-7.5.2 — Message d’erreur dynamique insuffisamment exposé

- **Page :** P06 — {P06_URL}
- **Critère / test :** RGAA 4.1.2 — 7.5 / 7.5.2
- **Statut :** NON_CONFORME_ETAYE dans le complément ; décision publiée à requalifier
- **Décision publiée :** {adjacent['published_status']}
- **Sévérité proposée :** Majeur

## Observation

{adjacent['observation']}

Message observé :

> {adjacent['message']}

Le même type de divergence est présent dans la preuve serveur archivée : conteneur d’erreur avec `aria-live="polite"`, sans `role="alert"` et sans `aria-atomic="true"`, alors que la matrice publiée indique qu’aucun message de statut n’a été produit.

## Impact

Le message peut ne pas être restitué avec la priorité et l’intégrité attendues lorsque le focus reste ailleurs. Une personne utilisant un lecteur d’écran peut ne pas percevoir immédiatement l’erreur ni la correction proposée.

## Correction attendue

Pour un message d’erreur ou une suggestion dynamique, utiliser l’une des solutions RGAA compatibles :

```html
<div class="fr-alert fr-alert--error" role="alert">
  <p>…message d’erreur précis…</p>
</div>
```

ou, si les attributs sont explicités :

```html
<div aria-live="assertive" aria-atomic="true">
  <p>…message d’erreur précis…</p>
</div>
```

La région doit exister avant l’injection si le composant ou la pile de technologies d’assistance l’exige. Éviter les annonces concurrentes ou dupliquées.

## Vérification après correction

1. Déclencher une extension interdite sans soumettre le formulaire final.
2. Vérifier le rôle ou le couple `aria-live` / `aria-atomic` dans le DOM rendu.
3. Vérifier que le message reste visible, précis et associé au champ fichier.
4. Contrôler l’annonce avec NVDA + Firefox et VoiceOver + Safari.
5. Rejouer le retour serveur de cinq fichiers en environnement de recette isolé.

## Preuves

- [JSON du retest sûr](preuves/P06-RETEST-SAFE.json)
- [Capture extension interdite]({adjacent['screenshot']})
- [Copie intègre de l’état serveur archivé](preuves/P06-ETAT-SERVEUR-ARCHIVE.json)
"""


def render_candidate_html(doc: dict[str, Any]) -> str:
    adjacent = doc["adjacent_decision"]
    return f"""<!doctype html><html lang="fr"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Ticket candidat RGAA 7.5.2 — P06</title><style>{CSS}</style></head><body><a class="skip" href="#contenu">Aller au contenu</a><header><div class="container"><p><a href="INDEX-P06-FORMULAIRES.html">← Complément P06</a></p><h1>Ticket candidat RGAA 7.5.2 — Message d’erreur dynamique</h1><p><span class="badge fail">Non conforme étayé — décision publiée à requalifier</span></p></div></header><main id="contenu" class="container"><h2>Observation</h2><p>{html.escape(adjacent['observation'])}</p><blockquote>{html.escape(adjacent['message'])}</blockquote><h2>Impact</h2><p>Le message peut ne pas être restitué avec la priorité et l’intégrité attendues lorsque le focus reste ailleurs. Une personne utilisant un lecteur d’écran peut ne pas percevoir immédiatement l’erreur ni la correction proposée.</p><h2>Correction attendue</h2><pre><code>{html.escape('<div class="fr-alert fr-alert--error" role="alert">\n  <p>…message d’erreur précis…</p>\n</div>')}</code></pre><p>Alternative explicite : <code>aria-live="assertive"</code> avec <code>aria-atomic="true"</code>.</p><h2>Vérification</h2><ol><li>Rejouer l’extension interdite.</li><li>Vérifier le rôle ou les attributs live dans le DOM rendu.</li><li>Vérifier la visibilité et l’association au champ.</li><li>Tester NVDA + Firefox et VoiceOver + Safari.</li><li>Rejouer le retour serveur de cinq fichiers en recette isolée.</li></ol><h2>Preuves</h2><ul><li><a href="preuves/P06-RETEST-SAFE.json">JSON du retest sûr</a></li><li><a href="{html.escape(adjacent['screenshot'], quote=True)}">Capture extension interdite</a></li><li><a href="preuves/P06-ETAT-SERVEUR-ARCHIVE.json">État serveur archivé</a></li><li><a href="TICKET-CANDIDAT-RGAA-7.5.2.md">Version Markdown</a></li></ul></main><footer><div class="container"><p>P06 — ticket complémentaire à arbitrer.</p></div></footer></body></html>"""


def render_required_candidate_markdown(doc: dict[str, Any]) -> str:
    decision = doc["theme_requalification"]
    affected = ", ".join(f"`#{control_id}`" for control_id in decision["affected_control_ids"])
    return f"""# Ticket candidat RGAA 11.10.2 — Indication des champs obligatoires

- **Page :** P06 — Formulaire Écrivez-nous
- **Test :** [RGAA 4.1.2 — 11.10.2]({OFFICIAL_RGAA}#11.10.2)
- **Décision publiée :** `{decision['published_status']}`
- **Conclusion étayée :** `NON_CONFORME_ETAYE`
- **État :** décision publiée à requalifier

## Observation

{decision['observation']}

Champs relevés : {affected}.

## Impact

L’utilisateur doit mémoriser l’instruction globale puis déduire le statut de chaque champ ; aucune indication associée champ par champ ne satisfait le test 11.10.2.

## Correction attendue

Placer une indication visible dans chaque étiquette concernée, par exemple :

```html
<label for="edit-nom">Nom <span>(obligatoire)</span></label>
```

Une autre solution est un passage de texte visible associé au champ avec `aria-labelledby` ou `aria-describedby`. Ne pas se limiter à l’attribut `required`, qui répond au test 11.10.1 mais pas à 11.10.2.

## Vérification après correction

1. Inventorier chaque champ portant `required` ou `aria-required="true"` dans tous les états du formulaire.
2. Vérifier que l’indication est visible dans l’étiquette ou un passage de texte associé.
3. Vérifier l’association programmatiquement et à différents points de rupture.
4. Rejouer le contrôle avant toute soumission serveur.

## Preuves

- [JSON du retest sûr](preuves/P06-RETEST-SAFE.json)
- [Capture du formulaire]({decision['screenshot']})
"""


def render_required_candidate_html(doc: dict[str, Any]) -> str:
    decision = doc["theme_requalification"]
    affected = ", ".join(f"<code>#{html.escape(control_id)}</code>" for control_id in decision["affected_control_ids"])
    correction = html.escape('<label for="edit-nom">Nom <span>(obligatoire)</span></label>')
    return f"""<!doctype html><html lang="fr"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Ticket candidat RGAA 11.10.2 — P06</title><style>{CSS}</style></head><body><a class="skip" href="#contenu">Aller au contenu</a><header><div class="container"><p><a href="INDEX-P06-FORMULAIRES.html">← Complément P06</a></p><h1>Ticket candidat RGAA 11.10.2 — Champs obligatoires</h1><p><span class="badge fail">Non conforme étayé — décision publiée à requalifier</span></p></div></header><main id="contenu" class="container"><h2>Observation</h2><p>{html.escape(decision['observation'])}</p><p>Champs relevés : {affected}.</p><h2>Impact</h2><p>L’utilisateur doit mémoriser l’instruction globale puis déduire le statut de chaque champ ; aucune indication associée champ par champ ne satisfait le test 11.10.2.</p><h2>Correction attendue</h2><pre><code>{correction}</code></pre><p>Une autre solution est un passage visible associé avec <code>aria-labelledby</code> ou <code>aria-describedby</code>. L’attribut <code>required</code> seul répond à 11.10.1, pas à 11.10.2.</p><h2>Vérification</h2><ol><li>Inventorier tous les champs obligatoires dans chaque état.</li><li>Vérifier une indication visible dans l’étiquette ou un passage associé.</li><li>Contrôler l’association programmatiquement et en responsive.</li><li>Rejouer sans soumission serveur.</li></ol><h2>Preuves</h2><ul><li><a href="preuves/P06-RETEST-SAFE.json">JSON du retest sûr</a></li><li><a href="{html.escape(decision['screenshot'], quote=True)}">Capture du formulaire</a></li><li><a href="TICKET-CANDIDAT-RGAA-11.10.2.md">Version Markdown</a></li></ul></main><footer><div class="container"><p>P06 — ticket complémentaire à arbitrer.</p></div></footer></body></html>"""


class StructureParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.main = 0
        self.h1 = 0
        self.lang_fr = False
        self.links: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        values = dict(attrs)
        if tag == "html" and values.get("lang") == "fr":
            self.lang_fr = True
        if tag == "main":
            self.main += 1
        if tag == "h1":
            self.h1 += 1
        if tag == "a" and values.get("href"):
            self.links.append(str(values["href"]))


def validate_html(path: Path) -> list[str]:
    parser = StructureParser()
    parser.feed(path.read_text(encoding="utf-8"))
    errors = []
    if not parser.lang_fr:
        errors.append("html[lang=fr] absent")
    if parser.main != 1:
        errors.append(f"nombre de main : {parser.main}")
    if parser.h1 != 1:
        errors.append(f"nombre de h1 : {parser.h1}")
    for href in parser.links:
        if href.startswith(("http://", "https://", "#", "mailto:")):
            continue
        target = (path.parent / href.split("#", 1)[0]).resolve()
        if not target.exists():
            errors.append(f"lien absent : {href}")
    return errors


def invalidate_package_validation() -> None:
    tickets_root = ROOT / "virginie-livrables/TICKETS-RGAA"
    tickets_root.mkdir(parents=True, exist_ok=True)
    checksum = tickets_root / "SHA256SUMS"
    validation_path = tickets_root / "VALIDATION-TICKETS-RGAA.json"
    validation: dict[str, Any] = {}
    if validation_path.is_file():
        validation = load_json(validation_path)
    validation["valid"] = False
    validation["client_transmission_ready"] = False
    validation["generation_state"] = "P06_ANNEX_REGENERATION_REQUIRED"
    validation["checksum_verification"] = "STALE"
    warning = (
        "Une régénération du complément P06 est en cours ou requise ; relancer "
        "generate-virginie-rgaa-tickets.py avant toute vérification d’intégrité du paquet."
    )
    warnings = validation.setdefault("warnings", [])
    if warning not in warnings:
        warnings.append(warning)
    temporary = validation_path.with_suffix(".json.tmp")
    temporary.write_text(
        json.dumps(validation, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    os.replace(temporary, validation_path)
    checksum.unlink(missing_ok=True)


def _run_locked() -> int:
    # Toute tentative de régénération rend le paquet précédent non vert avant
    # la première lecture ou validation susceptible d’échouer.
    invalidate_package_validation()
    OUTPUT.mkdir(parents=True, exist_ok=True)
    proof_root = OUTPUT / "preuves"
    doc, evidence = build_matrix()
    json_path = OUTPUT / "COUVERTURE-RGAA-11.json"
    md_path = OUTPUT / "COUVERTURE-RGAA-11.md"
    ticket_md = OUTPUT / "TICKET-CANDIDAT-RGAA-7.5.2.md"
    required_ticket_md = OUTPUT / "TICKET-CANDIDAT-RGAA-11.10.2.md"
    html_path = OUTPUT / "INDEX-P06-FORMULAIRES.html"
    ticket_html = OUTPUT / "TICKET-CANDIDAT-RGAA-7.5.2.html"
    required_ticket_html = OUTPUT / "TICKET-CANDIDAT-RGAA-11.10.2.html"
    server_copy = proof_root / "P06-ETAT-SERVEUR-ARCHIVE.json"
    company_copy = proof_root / "P06-SOCIETE-OPTIONNEL-ARCHIVE.json"

    payloads: dict[Path, bytes] = {
        json_path: (json.dumps(doc, ensure_ascii=False, indent=2) + "\n").encode("utf-8"),
        md_path: render_markdown(doc, evidence).encode("utf-8"),
        ticket_md: render_candidate_markdown(doc).encode("utf-8"),
        required_ticket_md: render_required_candidate_markdown(doc).encode("utf-8"),
        html_path: render_html(doc, evidence).encode("utf-8"),
        ticket_html: render_candidate_html(doc).encode("utf-8"),
        required_ticket_html: render_required_candidate_html(doc).encode("utf-8"),
        server_copy: ARCHIVED_SERVER_STATE.read_bytes(),
        company_copy: ARCHIVED_COMPANY_STATE.read_bytes(),
    }
    legacy_screenshots = [
        proof_root / name
        for name in (
            "P06-01-soumission-vide-native.png",
            "P06-02-email-invalide-natif.png",
            "P06-03-variante-professionnel.png",
            "P06-04-extension-interdite-requete-bloquee.png",
            "P06-04-extension-interdite-validation-client-sans-requete.png",
            "P06-05-cinq-fichiers-requete-bloquee.png",
        )
    ]
    changed_paths = [
        path for path, payload in payloads.items() if not path.is_file() or path.read_bytes() != payload
    ] + [path for path in legacy_screenshots if path.exists()]
    proof_root.mkdir(parents=True, exist_ok=True)
    for path, payload in payloads.items():
        path.write_bytes(payload)
    for path in legacy_screenshots:
        path.unlink(missing_ok=True)

    if sha256(server_copy) != sha256(ARCHIVED_SERVER_STATE):
        raise RuntimeError(f"Copie de preuve non intègre : {server_copy.name}")
    if sha256(company_copy) != sha256(ARCHIVED_COMPANY_STATE):
        raise RuntimeError(f"Copie de preuve non intègre : {company_copy.name}")

    errors = []
    for path in (html_path, ticket_html, required_ticket_html):
        errors.extend(f"{path.name}: {error}" for error in validate_html(path))
    if errors:
        raise ValueError("Validation HTML échouée :\n- " + "\n- ".join(errors))

    runs_root = proof_root / "runs"
    if runs_root.is_dir():
        for run_path in runs_root.iterdir():
            if run_path.is_dir() and run_path.name != evidence["run_id"]:
                shutil.rmtree(run_path)

    output_paths = list(payloads)
    print(
        json.dumps(
            {
                "tests": doc["tests_count"],
                "supplement_counts": doc["supplement_counts"],
                "requalified_11_10_2": doc["theme_requalification"]["status"],
                "adjacent_7_5_2": doc["adjacent_decision"]["status"],
                "client_transmission_ready": doc["client_transmission_ready"],
                "package_validation_invalidated": True,
                "changed_outputs": [str(path.relative_to(ROOT)) for path in changed_paths],
                "outputs": [str(path.relative_to(ROOT)) for path in output_paths],
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    return 0


def main() -> int:
    with p06_pipeline_lock():
        return _run_locked()


if __name__ == "__main__":
    raise SystemExit(main())
