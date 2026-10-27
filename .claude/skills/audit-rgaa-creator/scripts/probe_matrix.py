#!/usr/bin/env python3
"""Découverte dynamique des sondes AY11 et construction du plan d'appels.

La liste des sondes et des critères couverts n'est pas codée en dur : elle est
lue dans l'aide d'AY11. Une sonde ou un critère ajouté en amont est donc pris en
compte sans modifier ce fichier.

Trois faits mesurés sur AY11 le 18 septembre 2026 gouvernent ce module :

1. Omettre ``--criterion`` ne collecte qu'un seul critère par défaut, jamais
   tous ceux que la sonde couvre. Chaque critère est donc appelé explicitement.
2. Les sondes sortent en code 0 même sans candidat. L'état utile est porté par
   ``collection_status``, pas par le code de retour.
3. ``not_collected`` avec ``additional_capture_count`` à zéro signale une
   capture manquante et non un échec : la sonde réclame une capture
   complémentaire (reflow, orientation, états :hover et :focus) que la capture
   de base ne produit pas.
"""

from __future__ import annotations

import json
import re
import subprocess
from pathlib import Path
from typing import Any

from validator_results import validator_result

INPUT_HTML = "html"
INPUT_COLLECTION = "collection"
INPUT_BOTH = "both"

#: Statuts de collecte qui ne constituent pas un échec d'exécution.
NON_FAILING_STATUSES = frozenset(
    {
        "collected",
        "collected_no_candidate",
        "partially_collected",
        "not_collected",
        "ok",
    }
)
#: Statuts signalant une preuve absente faute de capture adaptée.
MISSING_CAPTURE_STATUSES = frozenset({"not_collected", "not_collected_static_html"})

#: Clés listant les signaux observés, par ordre de préférence.
SIGNAL_KEYS = (
    "observed_evidence",
    "signals",
    "results",
    "candidates",
    "document_candidates",
)


def criterion_sort_key(criterion: str) -> tuple[int, ...]:
    """Trie 10.3 après 1.8, ce qu'un tri alphabétique ne fait pas."""
    parts = []
    for piece in str(criterion).split("."):
        try:
            parts.append(int(piece))
        except ValueError:
            return (9999,)
    return tuple(parts)


def _help_text(ay11: str, *args: str) -> str:
    proc = subprocess.run(
        [ay11, "probes", *args, "--help"], text=True, capture_output=True, check=False
    )
    return proc.stdout or proc.stderr or ""


def _usage_line(help_text: str) -> str:
    """Réduit le bloc ``usage:`` à une ligne, l'aide argparse étant repliée."""
    lines: list[str] = []
    for line in help_text.splitlines():
        if line.startswith("usage:") or lines and line.startswith(" "):
            lines.append(line)
        elif lines:
            break
    return re.sub(r"\s+", " ", " ".join(lines))


def _positionals(help_text: str) -> list[str]:
    names: list[str] = []
    inside = False
    for line in help_text.splitlines():
        if line.startswith("positional arguments:"):
            inside = True
            continue
        if inside:
            if line.startswith("options:") or (line and not line.startswith(" ")):
                break
            match = re.fullmatch(r" {2}(\w+)", line.rstrip())
            if match:
                names.append(match.group(1))
    return names


def _input_kind(positionals: list[str]) -> str | None:
    has_html = any("html" in name for name in positionals)
    has_collection = any("collection" in name for name in positionals)
    if has_html and has_collection:
        return INPUT_BOTH
    if has_html:
        return INPUT_HTML
    if has_collection:
        return INPUT_COLLECTION
    return None


def _criteria(usage: str) -> tuple[list[str], bool]:
    """Rend les critères proposés et le caractère obligatoire de ``--criterion``."""
    match = re.search(r"(\[)?--criterion \{([^}]*)\}", usage)
    if not match:
        return [], False
    values = [
        item for item in (piece.strip() for piece in match.group(2).split(",")) if item
    ]
    return values, match.group(1) is None


def discover_probes(ay11: str) -> dict[str, Any]:
    """Cartographie les sondes exposées par AY11 et leurs entrées attendues."""
    usage = _usage_line(_help_text(ay11))
    match = re.search(r"probes \[-h\] \{([^}]+)\}", usage)
    names = [name.strip() for name in match.group(1).split(",")] if match else []
    probes: list[dict[str, Any]] = []
    skipped: list[dict[str, str]] = []
    for name in names:
        help_text = _help_text(ay11, name)
        kind = _input_kind(_positionals(help_text))
        criteria, required = _criteria(_usage_line(help_text))
        if kind is None:
            skipped.append(
                {"probe": name, "reason": "entrée positionnelle non reconnue"}
            )
            continue
        if required and not criteria:
            skipped.append(
                {
                    "probe": name,
                    "reason": "aucun critère proposé pour un --criterion obligatoire",
                }
            )
            continue
        probes.append(
            {
                "probe": name,
                "input": kind,
                "criteria": criteria,
                "criterion_required": required,
            }
        )
    return {
        "schema_version": 1,
        "kind": "ay11_probe_catalog",
        "probe_count": len(probes),
        "criteria_count": len({c for p in probes for c in p["criteria"]}),
        "probes": sorted(probes, key=lambda item: item["probe"]),
        "skipped": skipped,
    }


def build_probe_plan(
    catalog: dict[str, Any], html_path: Path, collection_path: Path
) -> list[dict[str, Any]]:
    """Construit un appel par couple sonde/critère, l'omission n'étant pas exhaustive."""
    plan: list[dict[str, Any]] = []
    for probe in catalog.get("probes", []):
        name, kind = probe["probe"], probe["input"]
        if kind == INPUT_BOTH:
            inputs = [str(html_path), str(collection_path)]
        elif kind == INPUT_HTML:
            inputs = [str(html_path)]
        else:
            inputs = [str(collection_path)]
        for criterion in probe["criteria"] or [None]:
            argv = ["probes", name, *inputs]
            if criterion:
                argv += ["--criterion", criterion]
            plan.append(
                {
                    "name": f"{name}-{criterion}" if criterion else name,
                    "probe": name,
                    "criterion": criterion,
                    "input": kind,
                    "argv": [*argv, "--json"],
                }
            )
    return plan


#: Marqueurs de statut indiquant un candidat de défaut. Testés avant les
#: marqueurs favorables, car « candidat_focus_non_visible » contient « visible ».
ADVERSE_MARKERS = (
    "insuffisant",
    "non_visible",
    "non_conforme",
    "absent",
    "manquant",
    "echec",
)
#: Marqueurs indiquant que la sonde n'a pas trouvé de candidat sur cet élément.
CLEAR_MARKERS = ("suffisant", "visible", "conforme", "present")

#: Un statut « candidat » nu vaut candidat de défaut.
ADVERSE_EXACT = frozenset({"candidat"})


def classify_entry(entry: Any) -> str:
    """Classe une entrée de sonde en défavorable, sans candidat ou indéterminé.

    Une entrée sans statut est indéterminée, pas un défaut : la sonde a inspecté
    l'élément sans pouvoir conclure. Compter ces entrées comme des signaux
    gonflerait la file de revue et orienterait l'audit à faux.
    """
    if not isinstance(entry, dict):
        return "indetermine"
    status = str(entry.get("status") or "").lower()
    if not status:
        return "indetermine"
    if status in ADVERSE_EXACT or any(m in status for m in ADVERSE_MARKERS):
        return "defavorable"
    if any(m in status for m in CLEAR_MARKERS):
        return "sans_candidat"
    return "indetermine"


def classify_payload(payload: Any) -> dict[str, Any]:
    """Sépare l'état de collecte, les candidats de défaut et la capture manquante.

    ``signal_count`` ne compte que les entrées **défavorables**. Le nombre
    d'éléments inspectés est porté à part par ``inspected_count`` : confondre les
    deux ferait passer 109 éléments contrôlés pour 109 défauts.
    """
    if not isinstance(payload, dict):
        return {
            "status": "sortie_inattendue",
            "signal_count": 0,
            "inspected_count": 0,
            "undetermined_count": 0,
            "missing_capture": False,
            "criterion_id": None,
        }
    status = (
        payload.get("collection_status") or payload.get("human_review_status") or "ok"
    )
    entries: list[Any] = []
    for key in SIGNAL_KEYS:
        value = payload.get(key)
        if isinstance(value, list):
            entries = value
            break
    buckets = {"defavorable": 0, "sans_candidat": 0, "indetermine": 0}
    for entry in entries:
        buckets[classify_entry(entry)] += 1
    criteria = payload.get("criteria")
    return {
        "status": status,
        "signal_count": buckets["defavorable"],
        "inspected_count": len(entries),
        "undetermined_count": buckets["indetermine"],
        "missing_capture": status in MISSING_CAPTURE_STATUSES
        and not payload.get("additional_capture_count"),
        "criterion_id": payload.get("criterion_id")
        or (criteria[0] if isinstance(criteria, list) and criteria else None),
    }


def summarise(entries: list[dict[str, Any]]) -> dict[str, Any]:
    """Résume une collecte de page en distinguant signal, absence et capture manquante."""
    by_criterion: dict[str, dict[str, Any]] = {}
    for entry in entries:
        criterion = entry.get("criterion") or entry.get("criterion_id")
        if not criterion:
            continue
        slot = by_criterion.setdefault(
            criterion,
            {
                "probes": [],
                "signal_count": 0,
                "inspected_count": 0,
                "undetermined_count": 0,
                "missing_capture": False,
            },
        )
        slot["probes"].append(entry["name"])
        for key in ("signal_count", "inspected_count", "undetermined_count"):
            slot[key] += int(entry.get(key) or 0)
        slot["missing_capture"] = slot["missing_capture"] or bool(
            entry.get("missing_capture")
        )
    return {
        "schema_version": 1,
        "kind": "ay11_probe_collection_summary",
        "produces_audit": False,
        "produces_conformity": False,
        "produces_decision": False,
        "guardrails": [
            "Un signal est un fait technique candidat, jamais une non-conformité RGAA.",
            "L'absence de signal ne vaut pas conformité : elle borne seulement ce que la sonde a pu observer.",
            "Un critère en capture manquante n'est pas instruit et reste dû à la revue humaine.",
        ],
        "call_count": len(entries),
        "criteria_with_signal": sorted(
            (c for c, v in by_criterion.items() if v["signal_count"]),
            key=criterion_sort_key,
        ),
        "criteria_to_examine": sorted(
            (
                c
                for c, v in by_criterion.items()
                if not v["signal_count"] and v["undetermined_count"]
            ),
            key=criterion_sort_key,
        ),
        "criteria_missing_capture": sorted(
            (c for c, v in by_criterion.items() if v["missing_capture"]),
            key=criterion_sort_key,
        ),
        "criteria": {
            c: by_criterion[c] for c in sorted(by_criterion, key=criterion_sort_key)
        },
    }


#: États rendus dans les rapports, du plus informatif au moins informatif.
STATE_SIGNAL = "signal"
STATE_TO_EXAMINE = "a_examiner"
STATE_MISSING_CAPTURE = "capture_manquante"
STATE_NO_CANDIDATE = "aucun_candidat"
STATE_UNCOVERED = "hors_sondes"


def load_campaign_summaries(campaign_root: Path) -> dict[str, Any]:
    """Agrège les ``sondes-resume.json`` de la campagne, par critère.

    Une sonde rend un **critère**, jamais un test : l'agrégat reste donc au
    niveau du critère, et c'est au rendu de dire explicitement que la couverture
    affichée sur une ligne de test vaut pour le critère entier.
    """
    by_criterion: dict[str, dict[str, Any]] = {}
    pages: list[str] = []
    call_count = 0
    collectes = campaign_root / "collectes-ay11"
    for page_dir in sorted(p for p in collectes.glob("*") if p.is_dir()):
        attempts = sorted(page_dir.glob("attempt-*/sondes-resume.json"))
        if not attempts:
            continue
        try:
            summary = json.loads(attempts[-1].read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        page_id = page_dir.name
        pages.append(page_id)
        call_count += int(summary.get("call_count") or 0)
        for criterion, detail in (summary.get("criteria") or {}).items():
            slot = by_criterion.setdefault(
                criterion,
                {
                    "pages": [],
                    "signal_count": 0,
                    "inspected_count": 0,
                    "undetermined_count": 0,
                    "missing_capture": False,
                    "probes": [],
                },
            )
            slot["pages"].append(page_id)
            for key in ("signal_count", "inspected_count", "undetermined_count"):
                slot[key] += int(detail.get(key) or 0)
            slot["missing_capture"] = slot["missing_capture"] or bool(
                detail.get("missing_capture")
            )
            for name in detail.get("probes") or []:
                if name not in slot["probes"]:
                    slot["probes"].append(name)
    for slot in by_criterion.values():
        slot["pages"] = sorted(set(slot["pages"]))
        slot["probes"] = sorted(slot["probes"])
    collect_html = load_collect_html(campaign_root)
    axe = load_axe(campaign_root)
    validateur = load_validator(campaign_root)
    catalogue = {}
    chemin_catalogue = campaign_root / "collectes-ay11" / "catalogue-collecteurs.json"
    if chemin_catalogue.is_file():
        try:
            catalogue = json.loads(chemin_catalogue.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            catalogue = {}
    capables = set(catalogue.get("capable") or [])
    # Un critère que le collecteur sait instruire mais où il n'a rien trouvé doit
    # rester visible : il appelle une revue humaine, contrairement à un critère
    # qu'aucune source ne couvre.
    sans_candidat = capables - set(collect_html)
    instrumentes = (
        set(by_criterion) | set(collect_html) | set(axe) | set(validateur) | capables
    )
    return {
        "schema_version": 2,
        "kind": "ay11_instrumentation_campaign_summary",
        "produces_audit": False,
        "produces_conformity": False,
        "produces_decision": False,
        "guardrails": [
            "Trois sources indépendantes : sondes AY11, collect-html et axe-core.",
            "Un candidat est un fait technique à qualifier, jamais une non-conformité.",
            "L'absence de candidat ne vaut pas conformité.",
            "Le rattachement axe vers RGAA est une table revue à la main, à vérifier.",
        ],
        "pages": sorted(set(pages)),
        "call_count": call_count,
        "instrumented_criteria_count": len(instrumentes),
        "criteria": {
            c: by_criterion[c] for c in sorted(by_criterion, key=criterion_sort_key)
        },
        "collect_html": {
            c: collect_html[c] for c in sorted(collect_html, key=criterion_sort_key)
        },
        "axe": {c: axe[c] for c in sorted(axe, key=criterion_sort_key)},
        "validator": validateur,
        "collect_html_catalog": {
            "capable_count": len(capables),
            "capable": sorted(capables, key=criterion_sort_key),
            "covered_without_candidate": sorted(sans_candidat, key=criterion_sort_key),
        },
    }


#: Rattachement axe-core → RGAA de repli, établi règle par règle et revu à la main.
#: Il ne sert QUE pour les règles qu'axe ne rattache pas lui-même : la plupart
#: portent une étiquette ``RGAA-x.y.z`` native, source plus riche et autoritaire.
#: Piège connu : ``region`` relève de 9.2 et non de 12.6 — axe le confirme par
#: son étiquette ``RGAA-9.2.1``.
AXE_VERS_RGAA = {
    "empty-heading": ["9.1"],  # axe ne rattache pas : titre sans contenu textuel
    "heading-order": ["9.1"],  # axe ne rattache pas : hiérarchie des titres
}

#: Étiquette axe marquant une bonne pratique, et non un échec WCAG.
AXE_BEST_PRACTICE = "best-practice"


def _criteres_axe(regle: dict[str, Any]) -> tuple[list[str], str]:
    """Rend les critères RGAA d'une règle axe, et l'origine du rattachement.

    Les étiquettes ``RGAA-x.y.z`` portées par axe font foi. La table locale ne
    sert que de repli pour les règles qu'axe ne rattache pas.
    """
    tags = regle.get("tags") or []
    natifs = sorted(
        {
            t.split("-", 1)[1].rsplit(".", 1)[0]
            for t in tags
            if str(t).startswith("RGAA-")
        },
        key=criterion_sort_key,
    )
    if natifs:
        return natifs, "etiquette_axe"
    return AXE_VERS_RGAA.get(str(regle.get("id")), []), "table_locale"


#: Sévérités déclarées par `collect-html` qui désignent un défaut candidat.
COLLECT_SEVERITES_DEFAUT = frozenset({"warn", "fail", "error", "critical"})
#: Code de preuve portant une suspicion explicite, quelle que soit sa sévérité.
COLLECT_SUSPICION = "suspicion_invalide"
#: Suffixe des codes de preuve qui portent un candidat.
COLLECT_CANDIDATE_SUFFIX = "_candidate"
#: Codes descriptifs, à ne jamais compter.
COLLECT_IGNORED = frozenset(
    {
        "test_id",
        "source_rgaa_locale",
        "target_count",
        "target_nodes",
        "scope",
        "inspectability",
        "inspection_limits",
        "human_review_question",
        "human_validation_result",
        "rendered_text_sample",
        "source_text_sample",
    }
)


def _severites(value: Any) -> set[str]:
    """Relève les sévérités déclarées dans une valeur de preuve, à un niveau."""
    trouvees: set[str] = set()
    if isinstance(value, dict):
        sev = value.get("severity")
        if isinstance(sev, str):
            trouvees.add(sev.lower())
    elif isinstance(value, list):
        for item in value:
            if isinstance(item, dict) and isinstance(item.get("severity"), str):
                trouvees.add(item["severity"].lower())
    return trouvees


def _collect_html_candidates(test: dict[str, Any]) -> dict[str, list[str]]:
    """Sépare les candidats `collect-html` en défauts et en points à examiner.

    La plupart des codes suffixés ``_candidate`` sont des **inventaires** :
    ``header_element_candidate`` vaut ``["header#fr-header"]`` et dit seulement
    que l'en-tête existe ; ``button_element_candidate`` vaut ``true``. Les
    compter comme des défauts gonflerait la file de revue, exactement comme
    compter les éléments inspectés pour des signaux de sonde.

    Un code ne vaut défaut que s'il porte une **sévérité déclarée**, ou s'il
    s'agit de la suspicion explicite ``suspicion_invalide``. Tout le reste est
    un point à examiner, pas un défaut.
    """
    defauts: list[str] = []
    a_examiner: list[str] = []
    for item in test.get("observed_evidence") or []:
        code, value = str(item.get("code") or ""), item.get("value")
        if not code or code in COLLECT_IGNORED:
            continue
        if not (code == COLLECT_SUSPICION or code.endswith(COLLECT_CANDIDATE_SUFFIX)):
            continue
        if isinstance(value, dict):
            if str(value.get("status", "")).startswith("not_collected"):
                continue
            if value.get("candidate") is False:
                continue
        if value in (None, False, "", [], {}):
            continue
        if code == COLLECT_SUSPICION or (_severites(value) & COLLECT_SEVERITES_DEFAUT):
            defauts.append(code)
        else:
            a_examiner.append(code)
    return {"defauts": sorted(set(defauts)), "a_examiner": sorted(set(a_examiner))}


#: États de couverture d'un critère, du plus informatif au moins informatif.
COUVERTURE_CANDIDAT = "candidat"
COUVERTURE_SANS_CANDIDAT = "couvert_sans_candidat"
COUVERTURE_ABSENTE = "non_couvert"

#: Message d'AY11 quand aucun collecteur HTML n'existe pour un critère.
MARQUEUR_SANS_COLLECTEUR = "Collecteur HTML local non disponible"


def discover_collect_html(
    ay11: str, html_path: Path, profil: str = "rgaa-106"
) -> dict[str, Any]:
    """Relève les critères pour lesquels AY11 expose un collecteur HTML.

    AY11 ne déclare pas cette capacité : il faut la sonder. Un appel par critère
    sort en code 0 quand un collecteur existe, et en code 1 avec le message
    « Collecteur HTML local non disponible » sinon. Environ 0,15 s par critère,
    soit une quinzaine de secondes pour les 106 — une fois par campagne.

    Sans cette capacité, un critère couvert mais sans candidat est indiscernable
    d'un critère non couvert : l'un appelle une revue humaine ciblée, l'autre non.
    """
    capables: list[str] = []
    absents: list[str] = []
    for criterion in sorted(criteres_du_referentiel(ay11), key=criterion_sort_key):
        proc = subprocess.run(
            [
                ay11,
                "rgaa",
                "collect-html",
                "--profile",
                profil,
                "--criterion",
                criterion,
                "--json",
                str(html_path),
            ],
            capture_output=True,
            text=True,
            check=False,
        )
        if proc.returncode == 0:
            capables.append(criterion)
        else:
            absents.append(criterion)
    return {
        "schema_version": 1,
        "kind": "ay11_collect_html_catalog",
        "profile_id": profil,
        "capable_count": len(capables),
        "capable": capables,
        "unsupported": absents,
        "guardrails": [
            "Un collecteur disponible ne garantit pas qu'il trouvera une cible.",
            "Un critère couvert sans candidat n'est pas conforme : il est à revoir.",
        ],
    }


def criteres_du_referentiel(ay11: str) -> list[str]:
    """Rend les identifiants de critères du profil RGAA complet, depuis AY11."""
    # `rgaa profile --json` ne rend qu'un décompte, pas les identifiants :
    # c'est `rgaa list --kind criteria` qui les porte, sous la clé `items`.
    proc = subprocess.run(
        [ay11, "rgaa", "list", "--kind", "criteria", "--format", "json"],
        capture_output=True,
        text=True,
        check=False,
    )
    try:
        donnees = json.loads(proc.stdout or "{}")
    except json.JSONDecodeError:
        return []
    entrees = (
        donnees
        if isinstance(donnees, list)
        else donnees.get("items") or donnees.get("criteria") or []
    )
    return [str(e.get("criterion_id")) for e in entrees if e.get("criterion_id")]


def load_collect_html(campaign_root: Path) -> dict[str, dict[str, Any]]:
    """Agrège les preuves `collect-html` par critère, sur la dernière tentative."""
    par_critere: dict[str, dict[str, Any]] = {}
    for page_dir in sorted(
        d for d in (campaign_root / "collectes-ay11").glob("*") if d.is_dir()
    ):
        plans = sorted(page_dir.glob("attempt-*/rgaa-collected-plan.json"))
        if not plans:
            continue
        try:
            plan = json.loads(plans[-1].read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        for test in (plan.get("proof_contract") or {}).get("tests") or []:
            evidence = test.get("observed_evidence") or []
            if not evidence:
                continue
            criterion = str(test.get("criterion_id"))
            slot = par_critere.setdefault(
                criterion,
                {
                    "pages": [],
                    "evidence_count": 0,
                    "candidates": [],
                    "to_examine": [],
                    "tests": [],
                },
            )
            if page_dir.name not in slot["pages"]:
                slot["pages"].append(page_dir.name)
            slot["evidence_count"] += len(evidence)
            slot["tests"].append(str(test.get("test_id")))
            tri = _collect_html_candidates(test)
            for code in tri["defauts"]:
                if code not in slot["candidates"]:
                    slot["candidates"].append(code)
            for code in tri["a_examiner"]:
                if code not in slot["to_examine"]:
                    slot["to_examine"].append(code)
    for slot in par_critere.values():
        slot["tests"] = sorted(set(slot["tests"]))
        slot["candidates"] = sorted(slot["candidates"])
        slot["to_examine"] = sorted(slot["to_examine"])
    return par_critere


def load_axe(campaign_root: Path) -> dict[str, dict[str, Any]]:
    """Agrège les règles axe-core déclenchées, rattachées au RGAA par AXE_VERS_RGAA."""
    par_critere: dict[str, dict[str, Any]] = {}
    for page_dir in sorted(
        d for d in (campaign_root / "captures-ay11").glob("*") if d.is_dir()
    ):
        bruts = sorted(page_dir.glob("attempt-*/*axe-core-raw.json"))
        if not bruts:
            continue
        try:
            brut = json.loads(bruts[-1].read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        resultats = (
            brut.get("results") if isinstance(brut.get("results"), dict) else brut
        )
        for genre in ("violations", "incomplete"):
            for regle in resultats.get(genre) or []:
                rid = str(regle.get("id"))
                criteres, origine = _criteres_axe(regle)
                bonne_pratique = AXE_BEST_PRACTICE in (regle.get("tags") or [])
                for criterion in criteres:
                    slot = par_critere.setdefault(
                        criterion,
                        {
                            "pages": [],
                            "violations": 0,
                            "incomplete": 0,
                            "rules": [],
                            "best_practice_only": True,
                            "mapping_sources": [],
                        },
                    )
                    if page_dir.name not in slot["pages"]:
                        slot["pages"].append(page_dir.name)
                    slot[genre] += len(regle.get("nodes") or [])
                    # Une seule règle WCAG suffit à sortir le critère de la
                    # simple bonne pratique.
                    if genre == "violations" and not bonne_pratique:
                        slot["best_practice_only"] = False
                    if origine not in slot["mapping_sources"]:
                        slot["mapping_sources"].append(origine)
                    marque = " [bonne pratique]" if bonne_pratique else ""
                    entree = f"{rid} ({genre}){marque}"
                    if entree not in slot["rules"]:
                        slot["rules"].append(entree)
    for slot in par_critere.values():
        slot["rules"] = sorted(slot["rules"])
        slot["mapping_sources"] = sorted(slot["mapping_sources"])
        if not slot["violations"]:
            slot["best_practice_only"] = False
    return par_critere


#: Critère RGAA instruit par le validateur HTML.
VALIDATOR_CRITERION = "8.2"


def load_validator(campaign_root: Path) -> dict[str, dict[str, Any]]:
    """Agrège les rapports du validateur HTML, rattachés au critère 8.2.

    Le validateur externe est la seule source capable d'instruire 8.2 : la
    collecte AY11 rend ``external_validator_executed: false`` et ne pratique que
    des contrôles structurels bornés.
    """
    pages: list[str] = []
    erreurs = 0
    avertissements = 0
    echantillons: list[str] = []
    unexecuted_pages: list[str] = []
    dossier = campaign_root / "validateur-w3c"
    for rapport in sorted(dossier.glob("*.json")):
        try:
            payload = json.loads(rapport.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            unexecuted_pages.append(rapport.stem)
            continue
        result = validator_result(payload)
        if not result["executed"]:
            unexecuted_pages.append(rapport.stem)
            continue
        messages = payload["messages"]
        pages.append(rapport.stem)
        for message in messages:
            if message.get("type") == "error":
                erreurs += 1
                texte = str(message.get("message") or "")[:120]
                if texte and texte not in echantillons and len(echantillons) < 5:
                    echantillons.append(texte)
            elif message.get("subType") == "warning":
                avertissements += 1
    if not pages and not unexecuted_pages:
        return {}
    return {
        VALIDATOR_CRITERION: {
            "pages": sorted(set(pages)),
            "errors": erreurs,
            "warnings": avertissements,
            "samples": echantillons,
            "unexecuted_pages": sorted(set(unexecuted_pages)),
        }
    }


def criterion_sources(aggregate: dict[str, Any], criterion: str) -> dict[str, Any]:
    """Rend, pour un critère, ce que chaque source d'instrumentation a produit."""
    ch = (aggregate.get("collect_html") or {}).get(criterion) or {}
    ax = (aggregate.get("axe") or {}).get(criterion) or {}
    va = (aggregate.get("validator") or {}).get(criterion) or {}
    sondes = (aggregate.get("criteria") or {}).get(criterion) or {}
    sources = []
    if sondes:
        sources.append("sondes")
    if ch:
        sources.append("collect-html")
    if ax:
        sources.append("axe")
    if va.get("pages"):
        sources.append("validateur")
    catalogue = aggregate.get("collect_html_catalog") or {}
    capable = criterion in set(catalogue.get("capable") or [])
    if ch.get("candidates"):
        couverture = COUVERTURE_CANDIDAT
    elif capable or ch:
        couverture = COUVERTURE_SANS_CANDIDAT
        if "collect-html" not in sources:
            sources.append("collect-html")
    else:
        couverture = COUVERTURE_ABSENTE
    return {
        "sources": sources,
        "collect_html_coverage": couverture,
        "collect_html_capable": capable,
        "validator_errors": int(va.get("errors") or 0),
        "validator_warnings": int(va.get("warnings") or 0),
        "validator_samples": va.get("samples") or [],
        "validator_unexecuted_pages": va.get("unexecuted_pages") or [],
        "instrumente": bool(sources),
        "collect_html_candidates": ch.get("candidates") or [],
        "collect_html_to_examine": ch.get("to_examine") or [],
        "collect_html_evidence": int(ch.get("evidence_count") or 0),
        "axe_rules": ax.get("rules") or [],
        "axe_violations": int(ax.get("violations") or 0),
        "axe_best_practice_only": bool(ax.get("best_practice_only")),
        "axe_mapping_sources": ax.get("mapping_sources") or [],
    }


def criterion_state(aggregate: dict[str, Any], criterion: str) -> dict[str, Any]:
    """Rend l'état d'un critère pour le rendu, sans jamais conclure à la conformité."""
    detail = (aggregate.get("criteria") or {}).get(criterion)
    if not detail:
        autres = criterion_sources(aggregate, criterion)
        return {
            "state": STATE_UNCOVERED,
            "signal_count": 0,
            "inspected_count": 0,
            "undetermined_count": 0,
            "probes": [],
            "pages": [],
            "label": "—",
            "comment": (
                "Aucune sonde ne couvre ce critère ; il est instrumenté par "
                + " et ".join(autres["sources"])
                + "."
                if autres["instrumente"]
                else "Aucune sonde ne couvre ce critère."
            ),
        }
    inspected = int(detail.get("inspected_count") or 0)
    undetermined = int(detail.get("undetermined_count") or 0)
    adverse = int(detail.get("signal_count") or 0)
    if detail.get("missing_capture"):
        label, state = "capture manquante", STATE_MISSING_CAPTURE
        comment = "Capture complémentaire absente : critère non instruit."
    elif adverse:
        label, state = (
            f"{adverse} candidat(s) sur {inspected} inspecté(s)",
            STATE_SIGNAL,
        )
        comment = "Candidats de défaut à qualifier."
    elif undetermined:
        label = f"{undetermined} à examiner sur {inspected} inspecté(s)"
        state, comment = (
            STATE_TO_EXAMINE,
            "La sonde a inspecté sans pouvoir conclure ; jugement humain requis.",
        )
    else:
        label, state = f"aucun candidat sur {inspected} inspecté(s)", STATE_NO_CANDIDATE
        comment = "Sonde exécutée sans candidat ; ne vaut pas conformité."
    return {
        "state": state,
        "signal_count": adverse,
        "inspected_count": inspected,
        "undetermined_count": undetermined,
        "probes": detail.get("probes") or [],
        "pages": detail.get("pages") or [],
        "label": label,
        "comment": comment,
    }


def main() -> int:
    import argparse

    parser = argparse.ArgumentParser(description="Cartographier les sondes AY11")
    parser.add_argument("ay11")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    catalog = discover_probes(args.ay11)
    if args.json:
        print(json.dumps(catalog, ensure_ascii=False, indent=2))
        return 0
    print(
        f"{catalog['probe_count']} sondes, {catalog['criteria_count']} critères distincts"
    )
    for probe in catalog["probes"]:
        criteria = ", ".join(probe["criteria"]) or "sans critère"
        print(f"  {probe['probe']:<24}{probe['input']:<12}{criteria}")
    for item in catalog["skipped"]:
        print(f"  IGNORÉE {item['probe']} : {item['reason']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
