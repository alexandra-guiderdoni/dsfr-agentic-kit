#!/usr/bin/env python3
"""Créateur et orchestrateur reproductible de campagnes RGAA 4.1.2.

Le runner collecte des preuves et prépare des qualifications. Il ne calcule jamais
un taux réglementaire et ne transforme pas une absence de signal en conformité.
"""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import html
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import urllib.error
import urllib.parse
import urllib.request
from collections import Counter
from contextlib import contextmanager
from html.parser import HTMLParser
from pathlib import Path
from typing import Any

try:
    import yaml
except ImportError as exc:  # pragma: no cover - traité par le wrapper du kit
    raise SystemExit(
        "PyYAML est requis. Utiliser scripts/audit-rgaa-creator.sh"
    ) from exc

from audit_report_builder import BUILDER, BUILDER_SCHEMA, generate_audit_portal
from browser_launch import (
    BrowserLaunchConfigError,
    browser_launch_options,
    browser_launch_summary,
    check_playwright_python,
)
from engine_coverage import generate_engine_coverage


class UniqueKeyLoader(yaml.SafeLoader):
    pass


def _unique_mapping(
    loader: yaml.SafeLoader, node: yaml.nodes.MappingNode, deep: bool = False
) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key_node, value_node in node.value:
        key = loader.construct_object(key_node, deep=deep)
        if key in result:
            raise ValueError(f"Clé YAML dupliquée : {key}")
        result[key] = loader.construct_object(value_node, deep=deep)
    return result


UniqueKeyLoader.add_constructor(
    yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG, _unique_mapping
)

SCRIPT = Path(__file__).resolve()
SKILL_ROOT = SCRIPT.parents[1]
KIT_ROOT = SCRIPT.parents[4]
# Statuts historiques conservés uniquement pour les sorties dérivées
# `findings.json` et `qualification.json`. Les saisies humaines canoniques
# vivent dans `rgaa-findings.json` et `dsfr-findings.json`.
STATUSES = {"NC-A", "C-A", "NA-A", "NT", "NOTE", "RECO"}
PHASES = (
    "preflight",
    "catalog",
    "plan",
    "capture",
    "collect",
    "browser",
    "rgaa",
    "dsfr",
    "protocols",
    "report",
    "report_capture",
    "validate",
)
REQUIRED_SKILLS = (
    "audit-rgaa-complet",
    "audit-dsfr-complet",
    "audit-report-dsfr",
    "tests-conformite-wcag",
    "screen-reader-testing",
    "ticket-rgaa",
)
THEMES = {
    1: ("Images", 9),
    2: ("Cadres", 2),
    3: ("Couleurs", 3),
    4: ("Multimédia", 13),
    5: ("Tableaux", 8),
    6: ("Liens", 2),
    7: ("Scripts", 5),
    8: ("Éléments obligatoires", 10),
    9: ("Structuration", 4),
    10: ("Présentation", 14),
    11: ("Formulaires", 13),
    12: ("Navigation", 11),
    13: ("Consultation", 12),
}
RGAA_REFERENTIAL = SKILL_ROOT.parent / "audit-rgaa-complet/references/rgaa-4.1.2.json"


def load_embedded_rgaa_referential() -> dict[str, Any]:
    """Charge le référentiel officiel embarqué, sans dépendre d'AY11."""
    try:
        data = json.loads(RGAA_REFERENTIAL.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError(f"Référentiel RGAA embarqué illisible : {RGAA_REFERENTIAL}: {exc}") from exc
    counts = data.get("counts", {})
    if data.get("referential_id") != "rgaa-4.1.2" or counts.get("criteria") != 106 or counts.get("tests") != 258:
        raise ValueError(f"Référentiel RGAA embarqué invalide : {RGAA_REFERENTIAL}")
    return data


def embedded_criterion_ids() -> list[str]:
    return [str(item["criterion_id"]) for item in load_embedded_rgaa_referential()["criteria"]]


CRITERION_IDS = embedded_criterion_ids()


def now() -> str:
    return dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds")


def slugify(value: str) -> str:
    value = value.lower().strip()
    value = re.sub(r"^https?://", "", value)
    value = re.sub(r"[^a-z0-9]+", "-", value).strip("-")
    return value[:60] or "site"


def read_yaml(path: Path) -> dict[str, Any]:
    data = yaml.load(path.read_text(encoding="utf-8"), Loader=UniqueKeyLoader) or {}
    if not isinstance(data, dict):
        raise ValueError(f"Configuration invalide : {path}")
    return data


def campaign_schema_errors(config: dict[str, Any]) -> list[str]:
    """Retourne les erreurs de schéma avant toute exécution de phase."""
    schema = json.loads(
        (SKILL_ROOT / "schemas/campaign.schema.json").read_text(encoding="utf-8")
    )
    try:
        import jsonschema
    except ImportError:
        messages = fallback_schema_errors(config, schema)
    else:
        messages = [
            error.message
            for error in jsonschema.Draft202012Validator(schema).iter_errors(config)
        ]
    return [f"Schéma campaign.yaml : {message}" for message in messages]


def atomic_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            handle.write(content)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def write_yaml(path: Path, data: dict[str, Any]) -> None:
    atomic_text(path, yaml.safe_dump(data, allow_unicode=True, sort_keys=False))


def write_json(path: Path, data: Any) -> None:
    atomic_text(path, json.dumps(data, ensure_ascii=False, indent=2) + "\n")


def read_json(path: Path, default: Any = None) -> Any:
    if not path.is_file():
        return default
    return json.loads(path.read_text(encoding="utf-8"))


DSFR_RULE_CATALOG = SKILL_ROOT.parent / "audit-dsfr-complet/rules/dsfr-rules.json"
DSFR_RULE_CATALOG_RELATIVE = "audit-dsfr-complet/rules/dsfr-rules.json"


def dsfr_catalog_metadata() -> dict[str, Any]:
    raw = DSFR_RULE_CATALOG.read_bytes()
    catalog = json.loads(raw.decode("utf-8"))
    return {
        "path": DSFR_RULE_CATALOG_RELATIVE,
        "sha256": hashlib.sha256(raw).hexdigest(),
        "schema_version": catalog.get("schema_version"),
        "target_version": str(catalog.get("target_version", "")),
        "rules_count": len(catalog.get("rules", [])),
    }


def dsfr_catalog_status(root: Path) -> dict[str, Any]:
    current = dsfr_catalog_metadata()
    pages = sorted((root / "dsfr/pages").glob("P*.json"))
    fingerprints: dict[str, list[str]] = {}
    missing: list[str] = []
    for path in pages:
        data = read_json(path, {}) or {}
        page_id = str((data.get("page") or {}).get("id") or path.stem)
        fingerprint = (data.get("rule_catalog") or {}).get("sha256")
        if not fingerprint:
            missing.append(page_id)
            continue
        fingerprints.setdefault(str(fingerprint), []).append(page_id)
    stale = sorted(
        page
        for fingerprint, page_ids in fingerprints.items()
        if fingerprint != current["sha256"]
        for page in page_ids
    )
    if not pages or missing:
        status = "EMPREINTE_ABSENTE"
        message = "Le rapport DSFR ne permet pas de prouver le catalogue de règles utilisé ; régénérer les archives avec l’empreinte du catalogue."
    elif stale:
        status = "CATALOGUE_OBSOLETE"
        message = f"Le rapport DSFR a été produit avec une ancienne version du catalogue de règles pour {', '.join(stale)} ; régénérer ces pages."
    elif len(fingerprints) > 1:
        status = "CATALOGUES_MULTIPLES"
        message = "Le rapport DSFR mélange plusieurs empreintes de catalogue ; régénérer toutes les pages avec une version unique."
    else:
        status = "A_JOUR"
        message = "Le rapport DSFR est produit avec l’empreinte courante du catalogue de règles."
    return {
        "status": status,
        "message": message,
        "current": current,
        "observed": sorted(fingerprints),
        "missing_pages": missing,
        "stale_pages": stale,
    }


def validate_url(value: str) -> str:
    parsed = urllib.parse.urlparse(value)
    if parsed.scheme not in {"http", "https"} or not parsed.netloc:
        raise ValueError("La cible doit être une URL HTTP(S) absolue")
    return urllib.parse.urlunparse(parsed._replace(fragment=""))


def campaign_root(config_path: Path) -> Path:
    return config_path.resolve().parent


def is_inside(path: Path, parent: Path) -> bool:
    try:
        path.resolve().relative_to(parent.resolve())
        return True
    except ValueError:
        return False


def parse_page(spec: str, index: int) -> dict[str, str]:
    # URL::Nom::type, ou ID::URL::Nom::type pour stabiliser les campagnes unitaires.
    bits = spec.split("::")
    explicit_id = len(bits) == 4
    if explicit_id:
        page_id = bits[0].strip()
        if not re.fullmatch(r"P[0-9]{2}", page_id):
            raise ValueError(
                "L’identifiant explicite d’une page doit suivre le format PXX."
            )
        url = validate_url(bits[1])
        name = (
            bits[2].strip()
            or urllib.parse.urlparse(url).path.rstrip("/").split("/")[-1]
            or "Accueil"
        )
        page_type = bits[3].strip() or "content"
    else:
        url = validate_url(bits[0])
        name = (
            bits[1].strip()
            if len(bits) > 1 and bits[1].strip()
            else urllib.parse.urlparse(url).path.rstrip("/").split("/")[-1] or "Accueil"
        )
        page_type = bits[2].strip() if len(bits) > 2 and bits[2].strip() else "content"
        page_id = f"P{index:02d}"
    return {"id": page_id, "name": name, "url": url, "type": page_type}


def version_tuple(value: str) -> tuple[int, ...]:
    match = re.search(r"(?:\d+(?:\.\d+){0,3})", value)
    if not match:
        return ()
    return tuple(int(part) for part in match.group(0).split("."))


def version_gte(actual: str, expected: str) -> bool:
    if not expected:
        return True
    actual_tuple = version_tuple(actual)
    expected_tuple = version_tuple(expected)
    if not actual_tuple:
        return False
    size = max(len(actual_tuple), len(expected_tuple))
    actual_tuple += (0,) * (size - len(actual_tuple))
    expected_tuple += (0,) * (size - len(expected_tuple))
    return actual_tuple >= expected_tuple


def detect_ay11_version(ay11: Path) -> str:
    for argv in ([str(ay11), "--version"], [str(ay11), "version"]):
        try:
            process = subprocess.run(
                argv, text=True, capture_output=True, check=False, timeout=10
            )
        except Exception:
            continue
        output = (process.stdout or process.stderr or "").strip()
        if output:
            return output.splitlines()[0].strip()
    return ""


def resolve_ay11_root(configured_root: str | None) -> Path | None:
    if not configured_root:
        return None
    root = Path(configured_root).expanduser().resolve()
    if not root.exists():
        raise SystemExit(f"Le dossier --ay11-root est introuvable : {root}")
    if not root.is_dir():
        raise SystemExit(f"--ay11-root doit être un dossier : {root}")
    candidates = (root / ".venv/bin/ay11", root / "venv/bin/ay11")
    executable = next(
        (path for path in candidates if path.is_file() and os.access(path, os.X_OK)),
        None,
    )
    if not executable:
        raise SystemExit(
            f"Le dossier --ay11-root ne contient pas d’exécutable AY11 exécutable : {root}/.venv/bin/ay11 ou {root}/venv/bin/ay11"
        )
    return root


def find_ay11(root: Path | None) -> tuple[Path | None, list[str]]:
    candidates: list[Path] = []
    warnings: list[str] = []
    if root:
        if not root.exists():
            warnings.append(f"Répertoire --ay11-root introuvable : {root}")
            return None, warnings
        if not root.is_dir():
            warnings.append(
                f"Répertoire --ay11-root invalide (pas un dossier) : {root}"
            )
            return None, warnings
        candidates.extend([root / ".venv/bin/ay11", root / "venv/bin/ay11"])
        if not any(path.is_file() and os.access(path, os.X_OK) for path in candidates):
            warnings.append(f"Aucun exécutable AY11 trouvé dans --ay11-root : {root}")
    env_root = os.environ.get("AY11_ROOT")
    if env_root:
        candidate_root = Path(env_root).expanduser()
        if not candidate_root.exists():
            warnings.append(f"Répertoire AY11_ROOT introuvable : {candidate_root}")
        elif not candidate_root.is_dir():
            warnings.append(f"AY11_ROOT invalide (pas un dossier) : {candidate_root}")
        else:
            candidates.extend(
                [candidate_root / ".venv/bin/ay11", candidate_root / "venv/bin/ay11"]
            )
    env = os.environ.get("AY11_BIN")
    if env:
        candidates.append(Path(env))
    which = shutil.which("ay11")
    if which:
        candidates.append(Path(which))
    resolved = next(
        (p.resolve() for p in candidates if p.is_file() and os.access(p, os.X_OK)), None
    )
    if not resolved and not warnings:
        warnings.append(
            "AY11 non résolu : définir --ay11-root, AY11_ROOT ou AY11_BIN, ou installer AY11 dans le PATH"
        )
    return resolved, warnings


def find_python_for_ay11(ay11: Path | None) -> Path:
    configured = os.environ.get("DSFR_AUDIT_PYTHON", "").strip()
    if configured:
        candidate = Path(configured).expanduser()
        if not candidate.is_absolute():
            resolved = shutil.which(configured)
            if resolved:
                return Path(resolved)
        return candidate
    if ay11 and ay11.parent.name == "bin":
        candidate = ay11.parent / "python"
        if candidate.is_file():
            return candidate
    return Path(sys.executable)


def state_path(root: Path) -> Path:
    return root / ".creator" / "state.json"


def campaign_digest(config_path: Path) -> str:
    normalized = yaml.safe_dump(
        read_yaml(config_path), allow_unicode=True, sort_keys=True
    ).encode("utf-8")
    return hashlib.sha256(normalized).hexdigest()


@contextmanager
def campaign_lock(root: Path):
    import fcntl

    lock_path = root / ".creator" / "campaign.lock"
    lock_path.parent.mkdir(parents=True, exist_ok=True)
    with lock_path.open("w", encoding="utf-8") as handle:
        try:
            fcntl.flock(handle.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError as exc:
            raise RuntimeError("Une autre exécution utilise cette campagne") from exc
        handle.write(f"pid={os.getpid()} started={now()}\n")
        handle.flush()
        try:
            yield
        finally:
            fcntl.flock(handle.fileno(), fcntl.LOCK_UN)


def load_state(root: Path) -> dict[str, Any]:
    return read_json(
        state_path(root),
        {"schema_version": 1, "updated_at": now(), "phases": {}, "pages": {}},
    )


def save_state(root: Path, state: dict[str, Any]) -> None:
    state["updated_at"] = now()
    write_json(state_path(root), state)


def record(state: dict[str, Any], phase: str, status: str, **details: Any) -> None:
    state.setdefault("phases", {})[phase] = {
        "status": status,
        "updated_at": now(),
        **details,
    }


def invalidate_downstream_phases(
    state: dict[str, Any], phase: str
) -> list[str]:
    """Marque les phases dérivées d’une phase rejouée comme à régénérer."""
    try:
        first_downstream = PHASES.index(phase) + 1
    except ValueError:
        return []
    invalidated: list[str] = []
    for downstream in PHASES[first_downstream:]:
        details = state.get("phases", {}).get(downstream)
        if not details or details.get("status") != "OK":
            continue
        record(
            state,
            downstream,
            "À REJOUER",
            invalidated_by=phase,
            reason=f"La phase {phase} a été rejouée ; ses sorties dérivées doivent être régénérées.",
        )
        invalidated.append(downstream)
    return invalidated


def run_command(
    argv: list[str], log_path: Path, cwd: Path | None = None, dry_run: bool = False
) -> tuple[int, str, str]:
    log_path.parent.mkdir(parents=True, exist_ok=True)
    if dry_run:
        payload = {
            "command": argv,
            "cwd": str(cwd) if cwd else None,
            "status": "DRY-RUN",
        }
        write_json(log_path, payload)
        return 0, "", ""
    proc = subprocess.run(argv, cwd=cwd, text=True, capture_output=True, check=False)
    write_json(
        log_path,
        {
            "command": argv,
            "cwd": str(cwd) if cwd else None,
            "exit_code": proc.returncode,
            "stdout": proc.stdout,
            "stderr": proc.stderr,
        },
    )
    return proc.returncode, proc.stdout, proc.stderr


def init_campaign(args: argparse.Namespace) -> int:
    target = validate_url(args.target)
    output = (
        Path(args.output).expanduser().resolve()
        if args.output
        else (
            Path.cwd() / f"audit-{slugify(target)}-{dt.date.today().isoformat()}"
        ).resolve()
    )
    if is_inside(output, KIT_ROOT) and not args.allow_inside_kit:
        raise SystemExit(
            f"Refus d’écrire les livrables dans le kit : {output}\nChoisir --output hors du kit."
        )
    if output.exists() and any(output.iterdir()):
        raise SystemExit(
            f"Le dossier existe et n’est pas vide : {output}. Choisir un nouveau dossier de campagne."
        )
    output.mkdir(parents=True, exist_ok=True)
    for rel in (
        "pages",
        "tickets",
        "findings",
        "captures-ay11",
        "collectes-ay11",
        "tests-wcag",
        "interactions",
        "analyses-skills",
        "inspections-approfondies",
        "focus-avance",
        "logs",
        ".creator",
    ):
        (output / rel).mkdir(parents=True, exist_ok=True)

    pages = [parse_page(spec, i + 1) for i, spec in enumerate(args.page or [])]
    if not pages:
        pages = [{"id": "P01", "name": "Accueil", "url": target, "type": "homepage"}]
    ay11_root = resolve_ay11_root(args.ay11_root)
    skills_roots = [
        str(Path(p).expanduser().resolve()) for p in (args.skills_root or [])
    ]
    if str(KIT_ROOT / ".claude/skills") not in skills_roots:
        skills_roots.insert(0, str(KIT_ROOT / ".claude/skills"))
    config = {
        "schema_version": 1,
        "campaign": {
            "id": args.name or f"audit-{slugify(target)}-{dt.date.today().isoformat()}",
            "name": args.name
            or f"Audit RGAA de {urllib.parse.urlparse(target).netloc}",
            "created_at": now(),
            "target": target,
            "locale": "fr-FR",
            "referential": "RGAA 4.1.2",
            "profile": "rgaa-106",
        },
        "tooling": {
            "kit_root": str(KIT_ROOT),
            "ay11_root": str(ay11_root) if ay11_root else "",
            "skills_roots": skills_roots,
        },
        "tooling_options": {
            "ay11_version": os.environ.get("AY11_EXPECTED_VERSION", "").strip(),
        },
        "sample": pages,
        "phases": {
            "ay11": True,
            "browser_checks": True,
            "rgaa_checks": True,
            "dsfr_checks": True,
            "reports": True,
            "report_capture": False,
            "tickets": True,
        },
        "browser": {
            "wait_ms": 900,
            "timeout_seconds": 30,
            "tabs_per_page": 25,
            "screenshots": True,
            "form_interactions": True,
            "axe": True,
            "launch": {"headless": True},
        },
        "limits": {
            "authenticated_scope": False,
            "real_screen_reader": False,
            "source_code_available": False,
        },
        "claims": {
            "official_compliance_rate": False,
            "dsfr_claim": "aucune conformité DSFR globale revendiquée",
        },
    }
    write_yaml(output / "campaign.yaml", config)
    write_json(output / "findings.json", {"schema_version": 1, "findings": []})
    write_json(output / "rgaa-findings.json", {"schema_version": 1, "findings": []})
    write_json(output / "dsfr-findings.json", {"schema_version": 1, "findings": []})
    write_json(
        output / "qualification.json",
        {
            "schema_version": 1,
            "criteria": {
                cid: {"status": "NT", "comment": "Validation à réaliser."}
                for cid in CRITERION_IDS
            },
        },
    )
    state = {
        "schema_version": 1,
        "created_at": now(),
        "updated_at": now(),
        "campaign_digest": campaign_digest(output / "campaign.yaml"),
        "phases": {},
        "pages": {p["id"]: {} for p in pages},
    }
    save_state(output, state)
    atomic_text(output / "RUNBOOK-AGENT.md", build_runbook(config))
    print(f"[OK] Campagne créée : {output}")
    print(f"[NEXT] Vérifier {output / 'campaign.yaml'}, puis lancer :")
    print(
        f"       {KIT_ROOT / 'scripts/audit-rgaa-creator.sh'} run {output / 'campaign.yaml'}"
    )
    return 0


class LinkParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.links: list[tuple[str, str]] = []
        self._href: str | None = None
        self._text: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag == "a":
            self._href = dict(attrs).get("href")
            self._text = []

    def handle_data(self, data: str) -> None:
        if self._href is not None:
            self._text.append(data)

    def handle_endtag(self, tag: str) -> None:
        if tag == "a" and self._href is not None:
            self.links.append((self._href, " ".join(self._text).strip()))
            self._href = None


SAMPLE_HINTS = {
    "accessibil": (100, "accessibility"),
    "plan-du-site": (95, "sitemap"),
    "mention": (80, "legal"),
    "donnees-personnelles": (85, "privacy"),
    "contact": (90, "form"),
    "formulaire": (90, "form"),
    "aide": (70, "help"),
    "faq": (70, "help"),
    "actualit": (50, "editorial"),
    "service": (40, "service"),
}


def sample_campaign(args: argparse.Namespace) -> int:
    path = Path(args.campaign).resolve()
    config = read_yaml(path)
    root = campaign_root(path)
    target = config["campaign"]["target"]
    parsed_target = urllib.parse.urlparse(target)
    req = urllib.request.Request(
        target, headers={"User-Agent": "DSFR-Agentic-Kit-Audit-Creator/1.0"}
    )
    try:
        with urllib.request.urlopen(req, timeout=args.timeout) as response:
            source = response.read(2_000_000).decode(
                response.headers.get_content_charset() or "utf-8", errors="replace"
            )
    except (OSError, urllib.error.URLError) as exc:
        raise SystemExit(f"Découverte impossible : {exc}") from exc
    parser = LinkParser()
    parser.feed(source)
    candidates: dict[str, tuple[int, str, str]] = {}
    for href, text in parser.links:
        url = urllib.parse.urljoin(target, href)
        p = urllib.parse.urlparse(url)
        if p.scheme not in {"http", "https"} or p.netloc != parsed_target.netloc:
            continue
        url = urllib.parse.urlunparse(p._replace(fragment="", query=""))
        hay = (p.path + " " + text).lower()
        score, kind = 10, "content"
        for hint, (points, candidate_kind) in SAMPLE_HINTS.items():
            if hint in hay and points > score:
                score, kind = points, candidate_kind
        if url not in candidates or score > candidates[url][0]:
            candidates[url] = (score, text or p.path, kind)
    existing = {p["url"] for p in config.get("sample", [])}
    chosen = sorted(candidates.items(), key=lambda item: (-item[1][0], item[0]))
    pages = list(config.get("sample", []))
    for url, (_, name, kind) in chosen:
        if url in existing:
            continue
        pages.append(
            {
                "id": "",
                "name": re.sub(r"\s+", " ", name).strip()[:100] or url,
                "url": url,
                "type": kind,
            }
        )
        existing.add(url)
        if len(pages) >= args.max_pages:
            break
    for i, page in enumerate(pages):
        page["id"] = f"P{i + 1:02d}"
    state = load_state(root)
    if state.get("phases"):
        raise SystemExit(
            "La campagne a déjà commencé. Modifier l’échantillon puis utiliser la commande replan."
        )
    config["sample"] = pages
    write_yaml(path, config)
    state["pages"] = {p["id"]: state.get("pages", {}).get(p["id"], {}) for p in pages}
    state["campaign_digest"] = campaign_digest(path)
    save_state(root, state)
    print(f"[OK] Échantillon : {len(pages)} page(s) dans {path}")
    for p in pages:
        print(f"  {p['id']} {p['type']:<14} {p['url']}")
    return 0


def build_runbook(config: dict[str, Any]) -> str:
    skills = "\n".join(f"- `{name}`" for name in REQUIRED_SKILLS)
    pages = "\n".join(
        f"- {p['id']} — {p['name']} — {p['url']}" for p in config["sample"]
    )
    return f"""# Runbook agent — {config["campaign"]["name"]}

## Objectif

Compléter la campagne automatisée avec des qualifications RGAA bornées et des
preuves humaines. Ne jamais revendiquer un taux RGAA officiel.

## Skills à lire

{skills}

## Échantillon

{pages}

## Qualification humaine canonique

Renseigner `rgaa-findings.json` avec les statuts RGAA v2 :
`C_CONFIRMEE`, `NC_CONFIRMEE`, `NA_CONFIRMEE`, `A_RETESTER` ou `NON_TESTE`.
Renseigner `dsfr-findings.json` séparément lorsque la phase DSFR est active.
Les fichiers `findings.json` et `qualification.json` sont des sorties dérivées
historiques produites par `report` ; ils ne sont pas modifiés directement.

- Une absence de signal ne prouve pas `C-A`.
- L’arbre d’accessibilité est une préqualification, pas un test NVDA/JAWS/VoiceOver.
- Les liens rompus sans critère directement applicable restent `RECO`.
- Les défauts systémiques sont regroupés par cause racine.

## Travail attendu

1. Relire `campaign.yaml` et les preuves sous `captures-ay11/`,
   `inspections-approfondies/`, `tests-wcag/`, `interactions/` et
   `analyses-skills/`.
2. Tester les états conditionnels, cookies, formulaires, modales, accordéons,
   médias et téléchargements pertinents.
3. Renseigner les fichiers canoniques `rgaa-findings.json` et, si nécessaire,
   `dsfr-findings.json`, sans modifier les preuves brutes.
4. Lancer `audit-rgaa-creator.sh report campaign.yaml` puis `validate`.
5. Vérifier visuellement `PORTAIL-AUDITS.html`, puis le rapport détaillé de
   chaque référentiel activé.
"""


def preflight(
    config: dict[str, Any],
    root: Path,
    state: dict[str, Any],
    dry_run: bool,
    strict_ay11: bool = False,
) -> bool:
    errors: list[str] = []
    warnings: list[str] = []
    schema_errors = campaign_schema_errors(config)
    if schema_errors:
        record(
            state,
            "preflight",
            "ECHEC",
            errors=schema_errors,
            warnings=[],
            cause="CONFIGURATION_INVALIDE",
        )
        save_state(root, state)
        return False
    try:
        validate_url(config.get("campaign", {}).get("target", ""))
    except ValueError as exc:
        errors.append(str(exc))
    pages = config.get("sample") or []
    if not pages:
        errors.append("Échantillon vide")
    ids = [p.get("id") for p in pages]
    if len(ids) != len(set(ids)):
        errors.append("Identifiants de pages dupliqués")
    for page in pages:
        try:
            validate_url(page.get("url", ""))
        except ValueError:
            errors.append(f"URL invalide pour {page.get('id', '?')}")
    ay11_root_value = config.get("tooling", {}).get("ay11_root") or ""
    ay11, ay11_diagnostics = find_ay11(
        Path(ay11_root_value) if ay11_root_value else None
    )
    expected_version = str(
        (config.get("tooling_options", {}) or {}).get("ay11_version")
        or os.environ.get("AY11_EXPECTED_VERSION", "")
    ).strip()
    ay11_version = detect_ay11_version(ay11) if ay11 else ""
    if config.get("phases", {}).get("ay11", True):
        if ay11_diagnostics and strict_ay11:
            errors.extend(ay11_diagnostics)
        elif ay11_diagnostics:
            warnings.extend(ay11_diagnostics)
        if not ay11:
            message = "Exécutable AY11 introuvable"
            if strict_ay11:
                errors.append(message)
            else:
                warnings.append(message)
        elif expected_version and not version_gte(ay11_version, expected_version):
            message = f"Version AY11 détectée '{ay11_version}' ; version minimale attendue : {expected_version}"
            if strict_ay11:
                errors.append(message)
            else:
                warnings.append(message)
    roots = [Path(p) for p in config.get("tooling", {}).get("skills_roots", [])]
    for skill in REQUIRED_SKILLS:
        if not any((candidate / skill / "SKILL.md").is_file() for candidate in roots):
            warnings.append(f"Skill non trouvé : {skill}")
    browser_phases = (
        ("browser_checks", "browser"),
        ("rgaa_checks", "rgaa"),
        ("dsfr_checks", "dsfr"),
    )
    active_browser_phases = [
        phase_name
        for config_key, phase_name in browser_phases
        if config.get("phases", {}).get(config_key, False)
    ]
    browser_python: dict[str, Any] = {
        "required": bool(active_browser_phases),
        "phases": active_browser_phases,
        "interpreter": None,
        "playwright_import": None,
    }
    try:
        browser_launch_options(config)
        browser_python["launch"] = browser_launch_summary(config)
    except BrowserLaunchConfigError as exc:
        browser_python["launch"] = {"error": str(exc)}
        if active_browser_phases:
            errors.append(str(exc))
    if active_browser_phases:
        selected_python = find_python_for_ay11(ay11)
        browser_python["interpreter"] = str(selected_python)
        import_ok, detail = check_playwright_python(selected_python)
        browser_python["playwright_import"] = detail or None
        if not import_ok:
            errors.append(
                "Playwright Python absent ou inutilisable dans l’interpréteur "
                f"sélectionné ({selected_python}) : {detail or 'import échoué'}"
            )
    network_checks: list[dict[str, Any]] = []
    blocked_infra: list[dict[str, str]] = []
    unreachable: list[dict[str, str]] = []
    if not dry_run:
        probe_urls: dict[str, str] = {}
        for candidate in [config.get("campaign", {}).get("target", "")] + [
            page.get("url", "") for page in pages
        ]:
            try:
                parsed = urllib.parse.urlparse(validate_url(candidate))
            except ValueError:
                continue
            origin = urllib.parse.urlunparse(
                (parsed.scheme, parsed.netloc, "/", "", "", "")
            )
            probe_urls.setdefault(origin, candidate)
        for origin, candidate in probe_urls.items():
            result = probe_network_url(candidate)
            network_checks.append({"origin": origin, **result})
            if result["kind"] == "BLOQUÉ-INFRA":
                blocked_infra.append(
                    {"origin": origin, "cause": result["cause"]}
                )
            elif result["kind"] == "INJOIGNABLE":
                unreachable.append({"origin": origin, "cause": result["cause"]})
            else:
                for page in pages:
                    if urllib.parse.urlparse(page["url"]).netloc == urllib.parse.urlparse(candidate).netloc:
                        state.setdefault("pages", {}).setdefault(page["id"], {})[
                            "http_status"
                        ] = result.get("http_status")
        if blocked_infra:
            errors.append(
                "Sortie réseau refusée par le proxy : "
                + ", ".join(item["origin"] for item in blocked_infra)
            )
        if unreachable:
            errors.append(
                "Cible réseau injoignable : "
                + ", ".join(item["origin"] for item in unreachable)
            )
    status = "BLOQUE_INFRA" if blocked_infra or unreachable else (
        "ECHEC" if errors else ("PARTIEL" if warnings else "OK")
    )
    record(
        state,
        "preflight",
        status,
        errors=errors,
        warnings=warnings,
        ay11=str(ay11) if ay11 else None,
        ay11_version=ay11_version or None,
        ay11_expected_version=expected_version or None,
        cause="BLOQUÉ-INFRA" if blocked_infra else "INJOIGNABLE" if unreachable else None,
        network_checks=network_checks,
        blocked_infra=blocked_infra,
        unreachable=unreachable,
        browser_python=browser_python,
    )
    save_state(root, state)
    return not errors


def run_protocols(
    config: dict[str, Any],
    root: Path,
    state: dict[str, Any],
    python: Path,
    dry_run: bool = False,
) -> tuple[list[dict[str, str]], list[dict[str, str]]]:
    """Exécute des protocoles externes avec un contexte de page canonique."""
    successes: list[dict[str, str]] = []
    failures: list[dict[str, str]] = []
    protocols = config.get("protocols", [])
    if not isinstance(protocols, list):
        return successes, [
            {"protocol": "configuration", "error": "protocols doit être une liste"}
        ]
    for protocol in protocols:
        if (
            not isinstance(protocol, dict)
            or not protocol.get("script")
            or not protocol.get("id")
        ):
            failures.append(
                {"protocol": str(protocol), "error": "id et script sont requis"}
            )
            continue
        script = Path(str(protocol["script"])).expanduser()
        if not script.is_absolute():
            script = root / script
        if not script.is_file():
            failures.append(
                {"protocol": str(protocol["id"]), "error": "script introuvable"}
            )
            continue
        selected_pages = set(
            protocol.get("pages", [page["id"] for page in config["sample"]])
        )
        for page in config["sample"]:
            if page["id"] not in selected_pages:
                continue
            context = {
                "schema_version": 1,
                "campaign_root": str(root),
                "protocol": {
                    "id": str(protocol["id"]),
                    "output": str(protocol.get("output", "")),
                },
                "page": page,
                "evidence_dir": str(
                    root / "preuves-protocoles" / page["id"] / str(protocol["id"])
                ),
            }
            context_path = (
                root / ".creator" / "protocols" / f"{page['id']}-{protocol['id']}.json"
            )
            write_json(context_path, context)
            code, out, err = run_command(
                [str(python), "-B", str(script), str(context_path)],
                root / "logs" / f"protocol-{page['id']}-{protocol['id']}.json",
                dry_run=dry_run,
            )
            if code:
                failures.append(
                    {
                        "protocol": str(protocol["id"]),
                        "page": page["id"],
                        "error": err[-500:],
                    }
                )
                continue
            output = str(protocol.get("output", "")).format(page_id=page["id"])
            if output and not dry_run:
                artifact = (root / output).resolve()
                if not is_inside(artifact, root) or not artifact.is_file():
                    failures.append(
                        {
                            "protocol": str(protocol["id"]),
                            "page": page["id"],
                            "error": "sortie déclarée absente ou hors campagne",
                        }
                    )
                    continue
                try:
                    metadata = read_json(artifact, {}).get("page", {})
                    if metadata and any(
                        str(metadata.get(key, "")) != str(page[key])
                        for key in ("id", "name", "url")
                    ):
                        failures.append(
                            {
                                "protocol": str(protocol["id"]),
                                "page": page["id"],
                                "error": "métadonnées de page incohérentes",
                            }
                        )
                        continue
                except Exception as exc:
                    failures.append(
                        {
                            "protocol": str(protocol["id"]),
                            "page": page["id"],
                            "error": f"sortie JSON invalide : {exc}",
                        }
                    )
                    continue
            successes.append({"protocol": str(protocol["id"]), "page": page["id"]})
    return successes, failures


def _run_campaign_unlocked(args: argparse.Namespace) -> int:
    config_path = Path(args.campaign).resolve()
    config = read_yaml(config_path)
    root = campaign_root(config_path)
    state = load_state(root)
    schema_errors = campaign_schema_errors(config)
    if schema_errors:
        record(
            state,
            "preflight",
            "ECHEC",
            errors=schema_errors,
            warnings=[],
            cause="CONFIGURATION_INVALIDE",
        )
        save_state(root, state)
        for error in schema_errors:
            print(f"[FAIL] {error}", file=sys.stderr)
        return 2
    digest = campaign_digest(config_path)
    if (
        state.get("campaign_digest")
        and state["campaign_digest"] != digest
        and state.get("phases")
    ):
        raise SystemExit(
            "campaign.yaml a changé depuis le dernier plan. Lancer `replan` avant de reprendre."
        )
    state["campaign_digest"] = digest
    save_state(root, state)
    selected = tuple(args.only.split(",")) if args.only else PHASES
    unknown = set(selected) - set(PHASES)
    if unknown:
        raise SystemExit(f"Phases inconnues : {', '.join(sorted(unknown))}")
    resume = bool(args.resume)

    # En mode resume, une phase explicitement sélectionnée par --only est une
    # demande de rejeu, même si son état précédent était OK. Ce rejeu doit
    # invalider les phases dérivées, notamment report et validate.
    explicit_replay = bool(args.resume and args.only)

    def skip(phase: str) -> bool:
        if phase not in selected:
            return True
        if (
            resume
            and not explicit_replay
            and state.get("phases", {}).get(phase, {}).get("status") == "OK"
        ):
            return True
        invalidated = invalidate_downstream_phases(state, phase)
        if invalidated:
            save_state(root, state)
            print(
                f"[INFO] {phase} rejouée : phases invalidées, à régénérer : {', '.join(invalidated)}"
            )
        return False

    if not skip("preflight") and not preflight(
        config,
        root,
        state,
        args.dry_run,
        strict_ay11=getattr(args, "strict_ay11", False),
    ):
        preflight_state = state.get("phases", {}).get("preflight", {})
        if preflight_state.get("status") in {"BLOQUE_INFRA", "BLOQUÉ"}:
            print(
                "[BLOQUÉ-INFRA] Pré-vol réseau bloqué ; aucune phase d’audit n’a été exécutée.",
                file=sys.stderr,
            )
            return 5
        print("[FAIL] Pré-vol en échec", file=sys.stderr)
        return 2
    ay11_root_value = config.get("tooling", {}).get("ay11_root") or ""
    ay11, _ = find_ay11(Path(ay11_root_value) if ay11_root_value else None)
    if not config.get("phases", {}).get("ay11", True):
        ay11 = None

    if not skip("catalog"):
        if not ay11:
            if not args.dry_run:
                write_json(root / "collectes-ay11/rgaa-criteria.json", embedded_rgaa_catalog())
            record(
                state,
                "catalog",
                "OK",
                source="référentiel RGAA 4.1.2 embarqué",
                reason="AY11 absent : le collecteur externe est facultatif",
            )
        else:
            code, out, err = run_command(
                [str(ay11), "rgaa", "list", "--kind", "criteria", "--format", "json"],
                root / "logs/catalog.json",
                dry_run=args.dry_run,
            )
            if code == 0 and not args.dry_run:
                try:
                    write_json(
                        root / "collectes-ay11/rgaa-criteria.json", json.loads(out)
                    )
                except json.JSONDecodeError:
                    code = 1
                    err += "\nSortie AY11 non JSON"
            record(
                state,
                "catalog",
                "OK" if code == 0 else "ECHEC",
                error=err[-1000:] if err else "",
            )
        save_state(root, state)

    if not skip("plan"):
        if not ay11:
            if not args.dry_run:
                write_json(root / "plan-preuves-rgaa-106.json", embedded_rgaa_plan())
            record(
                state,
                "plan",
                "OK",
                source="référentiel RGAA 4.1.2 embarqué",
                reason="AY11 absent : le plan officiel embarqué reste disponible",
            )
        else:
            argv = [
                str(ay11),
                "rgaa",
                "run-plan",
                "rgaa-106",
                "--include-proof-contract",
                "--execution-mode",
                "agents",
                "--json",
            ]
            code, out, err = run_command(
                argv, root / "logs/rgaa-run-plan-command.json", dry_run=args.dry_run
            )
            if code == 0 and not args.dry_run:
                try:
                    write_json(root / "plan-preuves-rgaa-106.json", json.loads(out))
                except json.JSONDecodeError:
                    code = 1
                    err += "\nSortie AY11 non JSON"
            record(
                state,
                "plan",
                "OK" if code == 0 else "ECHEC",
                error=err[-1000:] if err else "",
            )
        save_state(root, state)

    if not skip("capture"):
        if not ay11 or not config.get("phases", {}).get("ay11", True):
            record(state, "capture", "IGNORÉ", reason="AY11 absent ou désactivé")
        else:
            failures = []
            for page in config["sample"]:
                pid = page["id"]
                page_state = state.setdefault("pages", {}).setdefault(pid, {})
                attempts_root = root / "captures-ay11" / pid
                existing_attempts = [
                    int(match.group(1))
                    for path in attempts_root.glob("attempt-*")
                    if path.is_dir()
                    and (match := re.fullmatch(r"attempt-(\d+)", path.name))
                ]
                attempt = (
                    max(
                        [int(page_state.get("capture_attempt", 0)), *existing_attempts],
                        default=0,
                    )
                    + 1
                )
                page_state["capture_attempt"] = attempt
                out_dir = attempts_root / f"attempt-{attempt:03d}"
                out_dir.mkdir(parents=True, exist_ok=False)
                argv = [
                    str(ay11),
                    "preaudit",
                    "capture-browser",
                    page["url"],
                    "--output-dir",
                    str(out_dir),
                    "--wait-ms",
                    str(config.get("browser", {}).get("wait_ms", 900)),
                    "--timeout",
                    str(config.get("browser", {}).get("timeout_seconds", 30)),
                    "--json",
                ]
                if config.get("browser", {}).get("screenshots", True):
                    argv.append("--screenshot")
                if config.get("browser", {}).get("form_interactions", True):
                    argv.append("--form-interactions")
                if config.get("browser", {}).get("axe", True):
                    argv.append("--axe")
                code, out, err = run_command(
                    argv,
                    root / f"logs/capture-{pid}-attempt-{attempt:03d}.json",
                    dry_run=args.dry_run,
                )
                page_state["capture"] = "OK" if code == 0 else "ECHEC"
                page_state["capture_dir"] = str(out_dir.relative_to(root))
                if code == 0 and out and not args.dry_run:
                    try:
                        page_state["capture_manifest"] = json.loads(out)
                    except json.JSONDecodeError:
                        page_state["capture_stdout"] = out[-1000:]
                if code:
                    failures.append({"page": pid, "error": err[-500:]})
                save_state(root, state)
            record(state, "capture", "PARTIEL" if failures else "OK", failures=failures)
        save_state(root, state)

    if not skip("collect"):
        if not ay11 or not config.get("phases", {}).get("ay11", True):
            record(state, "collect", "IGNORÉ", reason="AY11 absent ou désactivé")
        elif args.dry_run:
            record(state, "collect", "OK", dry_run=True)
        else:
            failures = []
            for page in config["sample"]:
                pid = page["id"]
                page_state = state.setdefault("pages", {}).setdefault(pid, {})
                capture_dir = root / page_state.get(
                    "capture_dir", f"captures-ay11/{pid}"
                )
                attempt = int(page_state.get("capture_attempt", 0))
                destination = root / "collectes-ay11" / pid / f"attempt-{attempt:03d}"
                destination.mkdir(parents=True, exist_ok=True)
                html_files = sorted(capture_dir.glob("*-rendered.html"))
                collections = sorted(capture_dir.glob("*-browser-collection.json"))
                if not html_files or not collections:
                    failures.append(
                        {
                            "page": pid,
                            "error": "HTML rendu ou collection navigateur absent",
                        }
                    )
                    continue
                html_path, collection = html_files[0], collections[0]
                commands = [
                    (
                        "rgaa-collected-plan",
                        [
                            str(ay11),
                            "rgaa",
                            "run-plan",
                            "rgaa-106",
                            "--execution-mode",
                            "agents",
                            "--json",
                            "--collect-html",
                            str(html_path),
                            "--collect-accessible-name",
                            str(html_path),
                        ],
                    ),
                    (
                        "accessible-name",
                        [
                            str(ay11),
                            "probes",
                            "accessible-name",
                            str(html_path),
                            "--json",
                        ],
                    ),
                    (
                        "focus-visible",
                        [
                            str(ay11),
                            "probes",
                            "focus-visible",
                            str(collection),
                            "--json",
                        ],
                    ),
                    (
                        "layout-10.3",
                        [
                            str(ay11),
                            "probes",
                            "layout",
                            str(collection),
                            "--criterion",
                            "10.3",
                            "--json",
                        ],
                    ),
                    (
                        "layout-10.4",
                        [
                            str(ay11),
                            "probes",
                            "layout",
                            str(collection),
                            "--criterion",
                            "10.4",
                            "--json",
                        ],
                    ),
                    (
                        "contrast-3.2",
                        [
                            str(ay11),
                            "probes",
                            "contrast",
                            str(collection),
                            "--criterion",
                            "3.2",
                            "--json",
                        ],
                    ),
                    (
                        "contrast-3.3",
                        [
                            str(ay11),
                            "probes",
                            "contrast",
                            str(collection),
                            "--criterion",
                            "3.3",
                            "--json",
                        ],
                    ),
                    (
                        "contrast-10.5",
                        [
                            str(ay11),
                            "probes",
                            "contrast",
                            str(collection),
                            "--criterion",
                            "10.5",
                            "--json",
                        ],
                    ),
                ]
                for name, argv in commands:
                    code, out, err = run_command(
                        argv, root / f"logs/collect-{pid}-{name}.json"
                    )
                    if code == 0:
                        try:
                            write_json(destination / f"{name}.json", json.loads(out))
                        except json.JSONDecodeError:
                            code = 1
                            err += " Sortie JSON invalide"
                    if code:
                        failures.append(
                            {"page": pid, "collector": name, "error": err[-500:]}
                        )
                state.setdefault("pages", {}).setdefault(pid, {})["collect"] = (
                    "ECHEC" if any(f["page"] == pid for f in failures) else "OK"
                )
                save_state(root, state)
            record(state, "collect", "PARTIEL" if failures else "OK", failures=failures)
        save_state(root, state)

    if not skip("browser"):
        if not config.get("phases", {}).get("browser_checks", True):
            record(state, "browser", "IGNORÉ", reason="Désactivé")
        else:
            python = find_python_for_ay11(ay11)
            script = SKILL_ROOT / "scripts/browser_checks.py"
            runtime_config = root / ".creator/browser-runtime.json"
            write_json(
                runtime_config,
                {
                    **config,
                    "_campaign_root": str(root),
                    "_browser_launch": browser_launch_summary(config),
                },
            )
            argv = [str(python), str(script), str(runtime_config)]
            code, out, err = run_command(
                argv, root / "logs/browser-checks.json", dry_run=args.dry_run
            )
            record(
                state,
                "browser",
                "OK" if code == 0 else "ECHEC",
                output=out[-1000:],
                error=err[-1000:],
            )
        save_state(root, state)

    if not skip("rgaa"):
        if not config.get("phases", {}).get("rgaa_checks", False):
            record(state, "rgaa", "IGNORÉ", reason="Désactivé")
        else:
            python = find_python_for_ay11(ay11)
            script = SKILL_ROOT / "scripts/rgaa_checks.py"
            runtime_config = root / ".creator/browser-runtime.json"
            write_json(
                runtime_config,
                {
                    **config,
                    "_campaign_root": str(root),
                    "_browser_launch": browser_launch_summary(config),
                },
            )
            argv = [str(python), str(script), str(runtime_config)]
            code, out, err = run_command(
                argv, root / "logs/rgaa-checks.json", dry_run=args.dry_run
            )
            record(
                state,
                "rgaa",
                "OK" if code == 0 else "ECHEC",
                output=out[-1000:],
                error=err[-1000:],
            )
        save_state(root, state)

    if not skip("dsfr"):
        if not config.get("phases", {}).get("dsfr_checks", False):
            record(state, "dsfr", "IGNORÉ", reason="Désactivé")
        else:
            python = find_python_for_ay11(ay11)
            script = SKILL_ROOT / "scripts/dsfr_checks.py"
            runtime_config = root / ".creator/browser-runtime.json"
            write_json(
                runtime_config,
                {
                    **config,
                    "_campaign_root": str(root),
                    "_browser_launch": browser_launch_summary(config),
                },
            )
            argv = [str(python), str(script), str(runtime_config)]
            code, out, err = run_command(
                argv, root / "logs/dsfr-checks.json", dry_run=args.dry_run
            )
            record(
                state,
                "dsfr",
                "OK" if code == 0 else "ECHEC",
                output=out[-1000:],
                error=err[-1000:],
            )
        save_state(root, state)

    if not skip("protocols"):
        successes, failures = run_protocols(
            config, root, state, find_python_for_ay11(ay11), args.dry_run
        )
        record(
            state,
            "protocols",
            "ECHEC" if failures else "OK",
            successes=successes,
            failures=failures,
        )
        save_state(root, state)
    if not skip("report"):
        try:
            generate_reports(config_path)
            record(state, "report", "OK")
        except Exception as exc:
            record(state, "report", "ECHEC", error=str(exc))
            save_state(root, state)
            raise
        save_state(root, state)
    if not skip("report_capture"):
        if not config.get("phases", {}).get("report_capture", False):
            record(state, "report_capture", "IGNORÉ", reason="Désactivé")
        else:
            capture_script = (
                SKILL_ROOT.parent / "audit-report-dsfr/scripts/capture_audit_reports.py"
            )
            code, out, err = run_command(
                [str(find_python_for_ay11(ay11)), "-B", str(capture_script), str(root)],
                root / "logs/report-capture.json",
                dry_run=args.dry_run,
            )
            record(
                state,
                "report_capture",
                "OK" if code == 0 else "ECHEC",
                output=out[-1000:],
                error=err[-1000:],
            )
        save_state(root, state)
    if not skip("validate"):
        errors, warnings = validate_campaign(config_path, write_result=True)
        record(
            state,
            "validate",
            "ECHEC" if errors else ("PARTIEL" if warnings else "OK"),
            errors=errors,
            warnings=warnings,
        )
        save_state(root, state)
        if errors:
            return 3
    failed = [
        phase
        for phase, data in state.get("phases", {}).items()
        if data.get("status") == "ECHEC"
    ]
    if failed:
        print(
            f"[FAIL] Phases en échec : {', '.join(failed)}. Utiliser `resume` après correction.",
            file=sys.stderr,
        )
        return 4
    pending_phases = [
        phase
        for phase, data in state.get("phases", {}).items()
        if data.get("status") == "À REJOUER"
    ]
    if resume and pending_phases:
        print(
            "[PARTIEL] Phases invalidées non rejouées : "
            + ", ".join(pending_phases)
            + ". Relancer `resume` sans `--only` pour régénérer la chaîne aval.",
            file=sys.stderr,
        )
        return 3
    print(f"[OK] Campagne traitée : {root}")
    return 0


def run_campaign(args: argparse.Namespace) -> int:
    root = Path(args.campaign).resolve().parent
    with campaign_lock(root):
        return _run_campaign_unlocked(args)


def load_catalog(root: Path) -> dict[str, str]:
    data = read_json(root / "collectes-ay11/rgaa-criteria.json", {}) or {}
    catalog = {
        str(item.get("criterion_id")): str(item.get("title", ""))
        for item in data.get("items", [])
        if item.get("criterion_id")
    }
    if catalog:
        return catalog
    return {
        str(item["criterion_id"]): str(item.get("title", ""))
        for item in load_embedded_rgaa_referential()["criteria"]
    }


def embedded_rgaa_catalog() -> dict[str, Any]:
    """Adapte le catalogue embarqué au format historique consommé par le runner."""
    return {
        "items": [
            {"criterion_id": item["criterion_id"], "title": item.get("title", "")}
            for item in load_embedded_rgaa_referential()["criteria"]
        ],
        "source": "référentiel RGAA 4.1.2 embarqué",
    }


def embedded_rgaa_plan() -> dict[str, Any]:
    """Produit le contrat de preuve des 258 tests sans collecteur externe."""
    referential = load_embedded_rgaa_referential()
    return {
        "schema_version": 1,
        "profile": "rgaa-106",
        "source": "référentiel RGAA 4.1.2 embarqué",
        "referential": {
            "id": referential["referential_id"],
            "version": referential["version"],
            "source": referential["source"],
        },
        "proof_contract": {
            "tests": [
                {
                    "test_id": item["test_id"],
                    "criterion_id": item["criterion_id"],
                    "source_rgaa": {"url": item["source_url"], "title": item["title"]},
                    "reference_contract": {
                        "target": "Éléments concernés par le test dans le DOM rendu",
                        "expected_evidence": item.get("methodology", "Méthodologie officielle RGAA"),
                        "human_validation": "Validation humaine requise avant toute décision",
                        "limit": "La collecte automatique ne couvre pas toute la méthodologie du test",
                    },
                    "human_review_points": ["Applicabilité et cas particuliers à confirmer"],
                    "collection_status": "not_collected",
                }
                for item in referential["tests"]
            ]
        },
    }


def probe_network_url(url: str) -> dict[str, Any]:
    """Sonde une cible sans confondre proxy de sortie et erreur du site."""
    request = urllib.request.Request(
        url,
        method="HEAD",
        headers={"User-Agent": "DSFR-Agentic-Kit-Audit-Creator/1.0"},
    )
    try:
        with urllib.request.urlopen(request, timeout=15) as response:
            headers = {str(k).lower(): str(v) for k, v in response.headers.items()}
            return {
                "kind": "SITE",
                "http_status": response.status,
                "server": headers.get("server", ""),
            }
    except urllib.error.HTTPError as exc:
        headers = {str(k).lower(): str(v) for k, v in exc.headers.items()}
        deny_reason = headers.get("x-deny-reason", "").strip()
        if deny_reason:
            return {
                "kind": "BLOQUÉ-INFRA",
                "http_status": exc.code,
                "cause": f"x-deny-reason: {deny_reason}",
            }
        return {
            "kind": "SITE",
            "http_status": exc.code,
            "server": headers.get("server", ""),
            "cause": f"Réponse HTTP {exc.code} du site cible",
        }
    except (urllib.error.URLError, TimeoutError, OSError) as exc:
        cause = str(exc)
        lowered = cause.lower()
        proxy_markers = (
            "x-deny-reason",
            "proxy connection failed",
            "tunnel connection failed",
            "connection reset",
        )
        kind = "BLOQUÉ-INFRA" if any(marker in lowered for marker in proxy_markers) else "INJOIGNABLE"
        return {"kind": kind, "cause": cause or exc.__class__.__name__}


def generate_artifact_manifest(root: Path) -> None:
    items = []
    for path in sorted(root.rglob("*")):
        if (
            not path.is_file()
            or ".creator" in path.parts
            or "logs" in path.parts
            or "__pycache__" in path.parts
            or path.name in {".DS_Store", "MANIFESTE-ARTEFACTS.json", "VALIDATION.json"}
            or path.suffix.lower() in {".zip", ".pyc"}
        ):
            continue
        digest = hashlib.sha256()
        with path.open("rb") as handle:
            for block in iter(lambda: handle.read(1024 * 1024), b""):
                digest.update(block)
        items.append(
            {
                "path": str(path.relative_to(root)),
                "sha256": digest.hexdigest(),
                "bytes": path.stat().st_size,
            }
        )
    write_json(
        root / "MANIFESTE-ARTEFACTS.json",
        {"schema_version": 1, "generated_at": now(), "artifacts": items},
    )


def load_findings(root: Path) -> list[dict[str, Any]]:
    data = read_json(root / "findings.json", {"findings": []}) or {"findings": []}
    findings = data.get("findings", [])
    if not isinstance(findings, list):
        raise ValueError("findings.json : findings doit être une liste")
    return findings


def finding_priority(status: str) -> int:
    return {"NC-A": 6, "RECO": 5, "NOTE": 4, "C-A": 3, "NA-A": 2, "NT": 1}.get(
        status, 0
    )


def generate_rgaa_v2_reports(config: dict[str, Any], root: Path) -> None:
    rgaa_root = root / "rgaa"
    qualifications_path = root / "rgaa-findings.json"
    if not qualifications_path.is_file():
        write_json(qualifications_path, {"schema_version": 1, "findings": []})
    qualifications_doc = read_json(
        qualifications_path, {"schema_version": 1, "findings": []}
    ) or {"schema_version": 1, "findings": []}
    qualifications = qualifications_doc.get("findings", [])
    pages_data: list[dict[str, Any]] = []
    signals: list[dict[str, Any]] = []
    passes: list[dict[str, Any]] = []
    for page in config["sample"]:
        path = rgaa_root / "pages" / f"{page['id']}.json"
        data = read_json(path, None)
        if not isinstance(data, dict):
            data = {
                "schema_version": 1,
                "page": page,
                "audited_at": now(),
                "rules_executed": [],
                "signals": [],
                "passes": [],
                "evidence": {},
                "limits": ["Phase RGAA par instance non exécutée pour cette page."],
            }
            write_json(path, data)
        normalized = []
        matched_qualification_ids: set[str] = set()
        qualification_targets: dict[str, str] = {}
        raw_signals = [
            item
            for item in data.get("signals", [])
            if not (
                item.get("component") == "human_review"
                and item.get("signal_status") == "CONTROLE_EN_ECHEC"
            )
        ]
        for qualification in qualifications:
            qualification_id = str(qualification.get("id", ""))
            if page["id"] not in qualification.get("pages", []):
                continue
            candidates = [
                item
                for item in raw_signals
                if qualification.get("rule_id") == item.get("rule_id")
                and qualification.get("test") == item.get("test")
                and (
                    not qualification.get("selector")
                    or qualification.get("selector") == item.get("selector")
                )
                and (
                    not qualification.get("signal_id")
                    or qualification.get("signal_id") == item.get("id")
                )
                and (
                    qualification.get("instance") is None
                    or qualification.get("instance") == item.get("instance")
                )
            ]
            targeted = any(
                qualification.get(key) is not None and qualification.get(key) != ""
                for key in ("selector", "signal_id", "instance")
            )
            if not candidates and targeted:
                raise ValueError(
                    f"Qualification RGAA {qualification_id} ne cible aucune instance sur {page['id']}"
                )
            if len(candidates) > 1:
                raise ValueError(
                    f"Qualification RGAA {qualification_id} ambiguë pour {page['id']} : renseigner selector, instance ou signal_id"
                )
            if candidates:
                qualification_targets[qualification_id] = str(
                    candidates[0].get("id", "")
                )
        for item in raw_signals:
            item = dict(item)
            if (
                item.get("component") == "human_review"
                and item.get("signal_status") == "CONTROLE_EN_ECHEC"
            ):
                continue
            item.setdefault("qualification_status", "NON_TESTE")
            for qualification in qualifications:
                if (
                    page["id"] not in qualification.get("pages", [])
                    or qualification.get("rule_id") != item.get("rule_id")
                    or qualification.get("test") != item.get("test")
                ):
                    continue
                qualification_id = str(qualification.get("id", ""))
                if qualification_targets.get(qualification_id) != str(
                    item.get("id", "")
                ):
                    continue
                item["qualification_status"] = qualification.get(
                    "qualification_status", "NON_TESTE"
                )
                matched_qualification_ids.add(str(qualification.get("id", "")))
                item["qualification"] = {
                    "id": qualification.get("id"),
                    "comment": qualification.get("comment", ""),
                    "reviewed_by": qualification.get("reviewed_by", ""),
                    "reviewed_at": qualification.get("reviewed_at", ""),
                    "evidence": qualification.get("evidence", []),
                }
                if qualification.get("severity"):
                    item["severity"] = qualification["severity"]
                if qualification.get("impact"):
                    item["impact"] = qualification["impact"]
                if qualification.get("recommendation"):
                    item["recommendation"] = qualification["recommendation"]
            normalized.append(item)
            signals.append(
                {
                    **item,
                    "page": page["id"],
                    "page_name": page["name"],
                    "page_url": page["url"],
                }
            )
        human_titles = {
            "RGAA-1-8-IMAGE-TEXT-HUMAN-001": "Texte informatif intégré dans une image",
            "RGAA-11-10-REQUIRED-INDICATION-HUMAN-001": "Indication obligatoire inexacte pour le champ entreprise",
            "RGAA-11-13-AUTOCOMPLETE-HUMAN-001": "Champ entreprise sans finalité de saisie déclarée",
            "RGAA-12-7-SKIPLINK-HUMAN-002": "Lien d’accès rapide au contenu non fonctionnel",
        }
        for qualification in qualifications:
            qualification_id = str(qualification.get("id", ""))
            if (
                page["id"] not in qualification.get("pages", [])
                or qualification_id in matched_qualification_ids
                or qualification.get("qualification_status")
                not in {"NC_CONFIRMEE", "A_RETESTER"}
            ):
                continue
            rule_id = str(qualification.get("rule_id", "RGAA-HUMAN-REVIEW-001"))
            test = str(qualification.get("test", ""))
            comment = str(
                qualification.get("comment", "Constat issu de la revue humaine.")
            )
            evidence = list(
                dict.fromkeys(str(value) for value in qualification.get("evidence", []))
            )
            item = {
                "id": qualification_id,
                "rule_id": rule_id,
                "criterion": str(qualification.get("criterion", "")),
                "test": test,
                "component": "human_review",
                "instance": 1,
                "signal_status": "CONTROLE_EN_ECHEC",
                "qualification_status": qualification.get(
                    "qualification_status", "A_RETESTER"
                ),
                "severity": qualification.get("severity", "À qualifier"),
                "title": human_titles.get(rule_id, "Constat issu de la revue humaine"),
                "selector": str(qualification.get("selector", "")),
                "observed": comment,
                "observed_code": comment,
                "observed_origin": "MEASUREMENTS",
                "expected": f"Respecter le test RGAA {test} après qualification humaine.",
                "expected_code": "<!-- Corriger la cause décrite dans la revue humaine -->",
                "failed_assertions": [comment],
                "impact": str(
                    qualification.get(
                        "impact", "Impact à confirmer avec les personnes utilisatrices."
                    )
                ),
                "source": f"https://accessibilite.numerique.gouv.fr/methode/criteres-et-tests/#{test}",
                "recommendation": str(
                    qualification.get(
                        "recommendation",
                        "Corriger la cause puis rejouer le protocole humain.",
                    )
                ),
                "verification": f"Rejouer le protocole documenté du test {test}.",
                "evidence": evidence,
                "qualification": {
                    "id": qualification_id,
                    "comment": comment,
                    "reviewed_by": qualification.get("reviewed_by", ""),
                    "reviewed_at": qualification.get("reviewed_at", ""),
                    "evidence": evidence,
                },
            }
            normalized.append(item)
            signals.append(
                {
                    **item,
                    "page": page["id"],
                    "page_name": page["name"],
                    "page_url": page["url"],
                }
            )
        data["signals"] = normalized
        write_json(path, data)
        pages_data.append(data)
        passes.extend({**item, "page": page["id"]} for item in data.get("passes", []))
    grouped: dict[tuple[str, str, str, str], dict[str, Any]] = {}
    for item in signals:
        key = (
            str(item.get("rule_id")),
            str(item.get("criterion")),
            str(item.get("test")),
            str(item.get("title")),
        )
        cause = grouped.setdefault(
            key,
            {
                "rule_id": key[0],
                "criterion": key[1],
                "test": key[2],
                "title": key[3],
                "severity": item.get("severity", "À qualifier"),
                "pages": [],
                "count": 0,
                "confirmed": 0,
            },
        )
        cause["count"] += 1
        cause["confirmed"] += int(item.get("qualification_status") == "NC_CONFIRMEE")
        if item.get("page") not in cause["pages"]:
            cause["pages"].append(item.get("page"))
    severity_order = {"Bloquant": 0, "Majeur": 1, "Mineur": 2, "À qualifier": 3}
    root_causes = sorted(
        grouped.values(),
        key=lambda item: (
            severity_order.get(item["severity"], 9),
            item["criterion"],
            item["rule_id"],
        ),
    )
    confirmed = sum(
        item.get("qualification_status") == "NC_CONFIRMEE" for item in signals
    )
    retest = sum(item.get("qualification_status") == "A_RETESTER" for item in signals)
    non_tested = len(signals) - confirmed - retest
    write_json(
        rgaa_root / "CONSTATS-INSTANCES.json",
        {
            "schema_version": 1,
            "referential": "RGAA 4.1.2",
            "claim": "Préqualification instrumentée ; aucun taux RGAA officiel.",
            "signals": len(signals),
            "confirmed_nonconformities": confirmed,
            "root_causes": root_causes,
            "findings": signals,
        },
    )

    plan = read_json(root / "plan-preuves-rgaa-106.json", {}) or {}
    tests = (plan.get("proof_contract") or {}).get("tests", [])
    reviews = []
    signal_tests = Counter(item.get("test") for item in signals)
    pass_by_test: dict[str, Counter] = {}
    for item in passes:
        pass_by_test.setdefault(str(item.get("test")), Counter())[
            str(item.get("signal_status"))
        ] += 1
    qualification_tests = Counter(str(item.get("test")) for item in qualifications)
    for test in tests:
        tid = str(test.get("test_id"))
        criterion = str(test.get("criterion_id"))
        contract = test.get("reference_contract") or {}
        related_pages = sorted(
            {item["page"] for item in signals if item.get("test") == tid}
        )
        status = "DECISION_PARTIELLE" if qualification_tests[tid] else "A_REVOIR"
        priority = (
            "P0"
            if signal_tests[tid]
            else ("P1" if criterion.split(".")[0] in {"7", "10", "11", "12"} else "P2")
        )
        reviews.append(
            {
                "criterion": criterion,
                "test": tid,
                "priority": priority,
                "status": status,
                "pages": related_pages,
                "automatic_signals": signal_tests[tid],
                "automatic_coverage": dict(pass_by_test.get(tid, {})),
                "target": contract.get("target", "À déterminer"),
                "expected_evidence": contract.get(
                    "expected_evidence", "Preuve à définir"
                ),
                "human_validation": contract.get(
                    "human_validation", "Validation humaine requise"
                ),
                "limit": contract.get("limit", "Couverture automatique insuffisante"),
                "human_review_points": test.get("human_review_points", []),
                "source": (test.get("source_rgaa") or {}).get(
                    "url",
                    f"https://accessibilite.numerique.gouv.fr/methode/criteres-et-tests/#{tid}",
                ),
            }
        )
    write_json(
        rgaa_root / "REVUE-MANUELLE-258.json",
        {
            "schema_version": 1,
            "referential": "RGAA 4.1.2",
            "tests_count": len(reviews),
            "reviews": reviews,
        },
    )
    review_lines = [
        "# File de revue RGAA 4.1.2 — 258 tests",
        "",
        "> Ce document est dérivé du plan RGAA 4.1.2. Une ligne ne signifie pas que le test est exécuté. `PASS_CANDIDATE` ne vaut pas conformité.",
        "",
        f"- Tests présents : **{len(reviews)}**",
        f"- Décisions partielles : **{sum(x['status'] == 'DECISION_PARTIELLE' for x in reviews)}**",
        f"- Tests à revoir : **{sum(x['status'] == 'A_REVOIR' for x in reviews)}**",
        "",
        "| Priorité | Critère | Test | Statut | Pages signalées | Signaux | Cible | Validation humaine | Preuve attendue |",
        "|---|---|---|---|---|---:|---|---|---|",
    ]
    matrix_lines = [
        "# Matrice d’exécution des 258 tests RGAA",
        "",
        "> Couverture instrumentée et décisions humaines sont séparées.",
        "",
        "| Critère | Test | Couverture automatique | Signaux | Qualification | Statut de revue | Source |",
        "|---|---|---|---:|---|---|---|",
    ]
    for item in reviews:
        clean = lambda value: str(value).replace("|", "—").replace("\n", " ")
        review_lines.append(
            f"| {item['priority']} | {item['criterion']} | {item['test']} | **{item['status']}** | {', '.join(item['pages']) or '—'} | {item['automatic_signals']} | {clean(item['target'])} | {clean(item['human_validation'])} | {clean(item['expected_evidence'])} |"
        )
        matrix_lines.append(
            f"| {item['criterion']} | {item['test']} | `{json.dumps(item['automatic_coverage'], ensure_ascii=False)}` | {item['automatic_signals']} | {qualification_tests[item['test']]} décision(s) | **{item['status']}** | {item['source']} |"
        )
    atomic_text(rgaa_root / "REVUE-MANUELLE-258.md", "\n".join(review_lines) + "\n")
    atomic_text(rgaa_root / "MATRICE-TESTS-258.md", "\n".join(matrix_lines) + "\n")

    def links(item: dict[str, Any]) -> str:
        return (
            " · ".join(
                f"<a href='../{html.escape(str(value))}'>Preuve {index}</a>"
                for index, value in enumerate(item.get("evidence", []), 1)
            )
            or "Preuve non liée"
        )

    sections = []
    summary = []
    for data in pages_data:
        page = data["page"]
        pid = page["id"]
        page_signals = data.get("signals", [])
        page_confirmed = sum(
            x.get("qualification_status") == "NC_CONFIRMEE" for x in page_signals
        )
        summary.append(
            f"| {pid} — {page['name']} | {len(page_signals)} | {page_confirmed} | {sum(x.get('qualification_status') == 'NON_TESTE' for x in page_signals)} |"
        )
        cards = []
        for item in page_signals:
            qual = str(item.get("qualification_status", "NON_TESTE"))
            severity = str(item.get("severity", "À qualifier"))
            criterion = str(item.get("criterion", "—"))
            review = item.get("qualification", {}) or {}
            review_note = review.get(
                "comment", "Signal non encore qualifié humainement."
            )
            cards.append(
                f"<article class='finding' data-status='{html.escape(qual)}' data-severity='{html.escape(severity)}' data-criterion='{html.escape(criterion)}'><h4><code>{html.escape(str(item.get('rule_id')))}</code> — {html.escape(str(item.get('title')))}</h4><p class='badges'><span>{html.escape(qual)}</span><span>{html.escape(severity)}</span><span>critère {html.escape(criterion)}</span><span>test {html.escape(str(item.get('test')))}</span></p><p><b>Sélecteur :</b> <code>{html.escape(str(item.get('selector')))}</code> · instance {item.get('instance')}</p><p><b>Observation :</b> {html.escape(str(item.get('observed')))}</p><ul>{''.join(f'<li>{html.escape(str(value))}</li>' for value in item.get('failed_assertions', []))}</ul><div class='code-grid'><div><h5>Preuve observée — {html.escape(str(item.get('observed_origin')))}</h5><pre><code>{html.escape(str(item.get('observed_code')))}</code></pre></div><div><h5>Résultat attendu</h5><pre><code>{html.escape(str(item.get('expected_code')))}</code></pre></div></div><p class='origin'>Le DOM rendu n’est pas nécessairement le fichier source du dépôt.</p><p><b>Impact :</b> {html.escape(str(item.get('impact')))}</p><p><b>Source :</b> <a href='{html.escape(str(item.get('source')))}'>{html.escape(str(item.get('source')))}</a></p><p><b>Recommandation :</b> {html.escape(str(item.get('recommendation')))}</p><p><b>Contre-test :</b> {html.escape(str(item.get('verification')))}</p><p><b>Revue :</b> {html.escape(str(review_note))}</p><p>{links(item)}</p></article>"
            )
        sections.append(
            f"<section id='{pid}'><h2>{pid} — {html.escape(page['name'])}</h2><p><a href='{html.escape(page['url'])}'>{html.escape(page['url'])}</a></p><p>{len(page_signals)} signal(s), dont {page_confirmed} non-conformité(s) confirmée(s). Ces compteurs ne constituent pas un taux.</p>{''.join(cards) or '<p>Aucun signal d’échec sur les règles exécutées dans cet état.</p>'}<p><a href='pages/{pid}.json'>Preuve JSON de la page</a></p></section>"
        )
    nav = "".join(
        f"<li><a href='#{data['page']['id']}'>{data['page']['id']} — {html.escape(data['page']['name'])}</a></li>"
        for data in pages_data
    )
    root_rows = (
        "".join(
            f"<tr><td><code>{html.escape(x['rule_id'])}</code></td><td>{x['criterion']}</td><td>{x['test']}</td><td>{html.escape(x['severity'])}</td><td>{html.escape(x['title'])}</td><td>{x['count']}</td><td>{x['confirmed']}</td><td>{', '.join(x['pages'])}</td></tr>"
            for x in root_causes
        )
        or "<tr><td colspan='8'>Aucune cause racine.</td></tr>"
    )
    filters = "<div class='filters' role='group' aria-label='Filtres'><button type='button' data-filter='all'>Tous</button><button type='button' data-filter='NC_CONFIRMEE'>NC confirmées</button><button type='button' data-filter='A_RETESTER'>À retester</button><button type='button' data-filter='NON_TESTE'>Sans qualification</button><button type='button' data-filter='Bloquant'>Bloquants</button><label>Critère <input id='criterion-filter' size='8'></label><label>Rechercher <input id='finding-search' type='search'></label></div>"
    script = """<script>(()=>{const cards=[...document.querySelectorAll('.finding')];let active='all';const apply=()=>{const q=(document.querySelector('#finding-search').value||'').toLowerCase(),c=(document.querySelector('#criterion-filter').value||'').trim();cards.forEach(card=>card.hidden=!((active==='all'||card.dataset.status===active||card.dataset.severity===active)&&(!c||card.dataset.criterion===c)&&card.textContent.toLowerCase().includes(q)));};document.querySelectorAll('[data-filter]').forEach(b=>b.addEventListener('click',()=>{active=b.dataset.filter;apply();}));document.querySelectorAll('input').forEach(i=>i.addEventListener('input',apply));})();</script>"""
    document = f"<!doctype html><html lang='fr'><head><meta charset='utf-8'><meta name='viewport' content='width=device-width,initial-scale=1'><title>Pré-audit RGAA détaillé — {html.escape(config['campaign']['name'])}</title><style>body{{font:16px/1.55 system-ui,sans-serif;color:#161616;max-width:1220px;margin:auto;padding:1rem}}header{{border-bottom:5px solid #000091}}.warning{{background:#fff4e5;border-left:6px solid #e4794a;padding:1rem}}section{{margin:3rem 0;border-top:2px solid #ddd;padding-top:1rem}}table{{border-collapse:collapse;width:100%;display:block;overflow:auto}}th,td{{border:1px solid #ccc;padding:.6rem;text-align:left;vertical-align:top}}th{{background:#eee}}pre{{background:#f6f6f6;border:1px solid #ddd;padding:1rem;overflow:auto;max-height:26rem}}pre code{{white-space:pre-wrap}}.filters{{position:sticky;top:0;background:#fff;border:1px solid #bbb;padding:.7rem;display:flex;gap:.5rem;flex-wrap:wrap;z-index:2}}.finding{{border:2px solid #ddd;border-left:7px solid #e4794a;padding:1rem;margin:1.5rem 0}}.badges{{display:flex;gap:.5rem;flex-wrap:wrap}}.badges span{{background:#eee;padding:.2rem .55rem;font-weight:700}}.code-grid{{display:grid;grid-template-columns:1fr 1fr;gap:1rem}}.origin{{font-size:.9rem;color:#555}}[hidden]{{display:none!important}}:focus{{outline:3px solid #0a76f6;outline-offset:2px}}@media(max-width:800px){{.code-grid{{grid-template-columns:1fr}}}}</style></head><body><header><h1>Pré-audit RGAA instrumenté par règle et instance</h1><p><b>{html.escape(config['campaign']['name'])}</b></p><p class='warning'>{len(signals)} signal(s), {confirmed} NC confirmée(s), {retest} à retester, {non_tested} signal(s) sans qualification, {sum(x['status'] == 'A_REVOIR' for x in reviews)} test(s) à revoir. Aucun taux RGAA officiel.</p><p><a href='REVUE-MANUELLE-258.md'>File de revue des {len(reviews)} tests</a> · <a href='MATRICE-TESTS-258.md'>Matrice d’exécution</a></p></header><nav aria-label='Pages auditées'><h2>Accès direct</h2><ul>{nav}</ul></nav>{filters}<h2>Causes racines</h2><table><thead><tr><th>Règle</th><th>Critère</th><th>Test</th><th>Sévérité</th><th>Cause</th><th>Instances</th><th>Confirmées</th><th>Pages</th></tr></thead><tbody>{root_rows}</tbody></table><main>{''.join(sections)}</main>{script}</body></html>"
    # Le HTML publié est produit exclusivement par audit_report_builder.py.
    # ``document`` reste une représentation transitoire pour les données
    # historiques de ce générateur.
    root_md = (
        "\n".join(
            f"| `{x['rule_id']}` | {x['criterion']} | {x['test']} | {x['severity']} | {x['title'].replace('|', '—')} | {x['count']} | {x['confirmed']} | {', '.join(x['pages'])} |"
            for x in root_causes
        )
        or "| — | — | — | — | Aucune cause | 0 | 0 | — |"
    )
    report = f"""# Pré-audit RGAA détaillé — {config["campaign"]["name"]}

- **Pages :** {len(pages_data)}
- **Règles instrumentées :** {len({item.get("rule_id") for item in signals} | {item.get("rule_id") for item in passes})}
- **Signaux d’échec :** {len(signals)}
- **NC confirmées après revue :** {confirmed}
- **Signaux à retester :** {retest}
- **Signaux sans qualification :** {non_tested}
- **Tests du plan RGAA 4.1.2 :** {len(reviews)}
- **Tests restant à revoir :** {sum(x["status"] == "A_REVOIR" for x in reviews)}

> Préqualification instrumentée. Aucun taux RGAA officiel ; les tests applicables doivent être décidés humainement.

| Règle | Critère | Test | Sévérité | Cause | Instances | Confirmées | Pages |
|---|---|---|---|---|---:|---:|---|
{root_md}

## Livrables

- [Rapport HTML détaillé](AUDIT-PAR-PAGE.html)
- [File de revue des 258 tests](REVUE-MANUELLE-258.md)
- [Matrice des tests](MATRICE-TESTS-258.md)
- [Constats JSON](CONSTATS-INSTANCES.json)
"""
    atomic_text(rgaa_root / "RAPPORT-CONSOLIDE.md", report)
    consolidated = root / "RAPPORT-CONSOLIDE.md"
    if consolidated.is_file():
        value = consolidated.read_text(encoding="utf-8")
        addition = "\n## Pré-audit RGAA détaillé\n\n- [Rapport par règle et instance](rgaa/AUDIT-PAR-PAGE.html)\n- [File de revue des 258 tests](rgaa/REVUE-MANUELLE-258.md)\n"
        if "## Pré-audit RGAA détaillé" not in value:
            atomic_text(consolidated, value + addition)


def generate_dsfr_reports(config: dict[str, Any], root: Path) -> None:
    dsfr_root = root / "dsfr"
    status_labels = {
        "DETECTE_NON_AUDITE": "Détecté — non audité",
        "AUCUN_ECART_REGLES_EXECUTEES": "Aucun écart sur les règles exécutées",
        "ECART_OBSERVE": "Écart DSFR observé",
        "A_CONFIRMER": "À confirmer",
        "NON_APPLICABLE": "Non applicable",
        "REFERENCE_INDISPONIBLE": "Référence indisponible",
        "ECART_CONFIRME": "Écart confirmé après revue",
        "AUCUN_ECART_OBSERVE": "Aucun écart observé après revue",
    }
    legacy_statuses = {
        "ÉCART": "ECART_OBSERVE",
        "ALIGNÉ": "AUCUN_ECART_REGLES_EXECUTEES",
        "INDÉTERMINÉ": "DETECTE_NON_AUDITE",
    }
    qualifications_path = root / "dsfr-findings.json"
    if not qualifications_path.is_file():
        write_json(qualifications_path, {"schema_version": 1, "findings": []})
    qualifications_doc = read_json(
        qualifications_path, {"schema_version": 1, "findings": []}
    ) or {"schema_version": 1, "findings": []}
    qualifications = (
        qualifications_doc.get("findings", [])
        if isinstance(qualifications_doc.get("findings", []), list)
        else []
    )
    pages_data: list[dict[str, Any]] = []
    component_totals: dict[str, dict[str, Any]] = {}
    differences: list[dict[str, Any]] = []

    for page in config["sample"]:
        path = dsfr_root / "pages" / f"{page['id']}.json"
        data = read_json(path, None)
        if not isinstance(data, dict):
            data = {
                "schema_version": 2,
                "page": page,
                "version": {
                    "observed": [],
                    "target": "1.15.3",
                    "comparison_mode": "REFERENCE_VERSION_INDISPONIBLE",
                    "exact_observed_reference_available": False,
                },
                "reference_version": "1.15.3",
                "detected_versions": [],
                "status": "REFERENCE_INDISPONIBLE",
                "claim": "Aucune conformité DSFR globale n’est revendiquée.",
                "inventory": [],
                "differences": [],
                "sources": [],
                "not_verified": ["Phase DSFR non exécutée pour cette page"],
            }
        for item in data.get("inventory", []):
            item["status"] = legacy_statuses.get(
                str(item.get("status", "")), item.get("status", "DETECTE_NON_AUDITE")
            )
            item.setdefault("rules_executed", [])
        normalized_differences = []
        qualification_targets: dict[str, str] = {}
        raw_differences = data.get("differences", [])
        for qualification in qualifications:
            qualification_id = str(qualification.get("id", ""))
            if page["id"] not in qualification.get("pages", []):
                continue
            candidates = [
                item
                for item in raw_differences
                if qualification.get("rule_id") == item.get("rule_id")
                and (
                    not qualification.get("selector")
                    or qualification.get("selector") == item.get("selector")
                )
                and (
                    not qualification.get("signal_id")
                    or qualification.get("signal_id") == item.get("id")
                )
                and (
                    qualification.get("instance") is None
                    or qualification.get("instance") == item.get("instance")
                )
            ]
            targeted = any(
                qualification.get(key) is not None and qualification.get(key) != ""
                for key in ("selector", "signal_id", "instance")
            )
            if not candidates and targeted:
                raise ValueError(
                    f"Qualification DSFR {qualification_id} ne cible aucune instance sur {page['id']}"
                )
            if len(candidates) > 1:
                raise ValueError(
                    f"Qualification DSFR {qualification_id} ambiguë pour {page['id']} : renseigner selector, instance ou signal_id"
                )
            if candidates:
                qualification_targets[qualification_id] = str(
                    candidates[0].get("id", "")
                )
        for index, item in enumerate(raw_differences, 1):
            item = dict(item)
            item.setdefault(
                "rule_id",
                f"DSFR-LEGACY-{re.sub(r'[^A-Z0-9]+', '-', str(item.get('component', 'GLOBAL')).upper()).strip('-')}-001",
            )
            item["status"] = legacy_statuses.get(
                str(item.get("status", "")), item.get("status", "ECART_OBSERVE")
            )
            item.setdefault("signal_status", "FAIL_CANDIDATE")
            item.setdefault("qualification_status", "A_CONFIRMER")
            item.setdefault("selector", "")
            item.setdefault("instance", None)
            item.setdefault("observed_html", str(item.get("observed", "")))
            item.setdefault("observed_html_origin", "RENDERED_DOM")
            item.setdefault("expected_html", str(item.get("expected", "")))
            item.setdefault(
                "failed_conditions", [str(item.get("observed", "Écart observé"))]
            )
            item.setdefault(
                "recommendation", "Corriger l’intégration selon la référence citée."
            )
            item.setdefault("verification", "Rejouer la règle sur le DOM rendu.")
            item.setdefault(
                "evidence",
                [
                    value
                    for value in (data.get("evidence", {}) or {}).values()
                    if isinstance(value, str)
                ],
            )
            item.setdefault("assessed_against", "REFERENCE_VERSION_INDISPONIBLE")
            item.setdefault("observed_versions", data.get("detected_versions", []))
            item.setdefault(
                "reference_target_version", data.get("reference_version", "1.15.3")
            )
            for qualification in qualifications:
                if page["id"] not in qualification.get(
                    "pages", []
                ) or qualification.get("rule_id") != item.get("rule_id"):
                    continue
                qualification_id = str(qualification.get("id", ""))
                if qualification_targets.get(qualification_id) != str(
                    item.get("id", "")
                ):
                    continue
                item["qualification_status"] = qualification.get(
                    "qualification_status", "A_CONFIRMER"
                )
                item["qualification"] = {
                    "id": qualification.get("id"),
                    "comment": qualification.get("comment", ""),
                    "reviewed_by": qualification.get("reviewed_by", ""),
                    "reviewed_at": qualification.get("reviewed_at", ""),
                    "evidence": qualification.get("evidence", []),
                }
                if qualification.get("recommendation"):
                    item["recommendation"] = qualification["recommendation"]
            normalized_differences.append(item)
            differences.append(
                {
                    **item,
                    "page": page["id"],
                    "page_name": page["name"],
                    "page_url": page["url"],
                }
            )
        data["differences"] = normalized_differences
        confirmed = sum(
            item.get("qualification_status") == "ECART_CONFIRME"
            for item in normalized_differences
        )
        data["status"] = (
            "ECARTS_CONFIRMES"
            if confirmed
            else (
                "SIGNAUX_ECART_A_CONFIRMER"
                if normalized_differences
                else "AUCUN_ECART_REGLES_EXECUTEES"
            )
        )
        write_json(path, data)
        pages_data.append(data)
        for item in data.get("inventory", []):
            entry = component_totals.setdefault(
                item["name"],
                {
                    "name": item["name"],
                    "selector": item.get("selector", ""),
                    "count": 0,
                    "pages": [],
                    "status": "AUCUN_ECART_REGLES_EXECUTEES",
                    "source": item.get("source", ""),
                    "rules_executed": [],
                },
            )
            entry["count"] += int(item.get("count", 0))
            if page["id"] not in entry["pages"]:
                entry["pages"].append(page["id"])
            entry["rules_executed"] = sorted(
                set(entry["rules_executed"]) | set(item.get("rules_executed", []))
            )
            item_status = item.get("status")
            if item_status == "ECART_OBSERVE":
                entry["status"] = "ECART_OBSERVE"
            elif (
                item_status == "DETECTE_NON_AUDITE"
                and entry["status"] != "ECART_OBSERVE"
            ):
                entry["status"] = "DETECTE_NON_AUDITE"

    inventory = sorted(component_totals.values(), key=lambda item: item["name"])
    grouped: dict[tuple[str, str, str, str, str], dict[str, Any]] = {}
    for item in differences:
        key = (
            str(item.get("rule_id", "")),
            str(item.get("title", "")),
            str(item.get("component", "global")),
            str(item.get("severity", "À qualifier")),
            str(item.get("kind", "integration")),
        )
        cause = grouped.setdefault(
            key,
            {
                "rule_id": key[0],
                "title": key[1],
                "component": key[2],
                "severity": key[3],
                "kind": key[4],
                "source": item.get("source", ""),
                "pages": [],
                "selectors": [],
                "count": 0,
                "confirmed": 0,
            },
        )
        cause["count"] += 1
        cause["confirmed"] += int(item.get("qualification_status") == "ECART_CONFIRME")
        if item.get("page") not in cause["pages"]:
            cause["pages"].append(item.get("page"))
        if item.get("selector") and item["selector"] not in cause["selectors"]:
            cause["selectors"].append(item["selector"])
    severity_order = {"Bloquant": 0, "Majeur": 1, "Mineur": 2, "À qualifier": 3}
    root_causes = sorted(
        grouped.values(),
        key=lambda item: (
            severity_order.get(item["severity"], 9),
            item["rule_id"],
            item["title"],
        ),
    )
    confirmed_count = sum(
        item.get("qualification_status") == "ECART_CONFIRME" for item in differences
    )
    candidate_count = len(differences) - confirmed_count
    target_versions = sorted(
        {
            str(
                (data.get("version") or {}).get("target")
                or data.get("reference_version", "1.15.3")
            )
            for data in pages_data
        }
    )
    observed_versions = sorted(
        {
            version
            for data in pages_data
            for version in data.get("detected_versions", [])
        }
    )
    catalog_status = dsfr_catalog_status(root)
    write_json(
        dsfr_root / "INVENTAIRE-COMPOSANTS.json",
        {
            "schema_version": 2,
            "target_versions": target_versions,
            "observed_versions": observed_versions,
            "pages": len(config["sample"]),
            "status_dictionary": status_labels,
            "rule_catalog": catalog_status["current"],
            "catalog_status": catalog_status,
            "components": inventory,
        },
    )
    write_json(
        dsfr_root / "ECARTS-COMPOSANTS.json",
        {
            "schema_version": 2,
            "claim": "Aucune conformité DSFR globale n’est revendiquée.",
            "observed_html_origin": "RENDERED_DOM",
            "target_versions": target_versions,
            "observed_versions": observed_versions,
            "confirmed_count": confirmed_count,
            "candidate_count": candidate_count,
            "rule_catalog": catalog_status["current"],
            "catalog_status": catalog_status,
            "root_causes": root_causes,
            "differences": differences,
        },
    )

    matrix = [
        "# Matrice d’audit DSFR par règle et par instance",
        "",
        "> Le code affiché provient du DOM rendu. Les règles visent la référence locale ; les différences de version sont séparées comme migration.",
        "",
        "| Page | Règle | Élément | Instance | Portée | Signal | Qualification | Sévérité | Sélecteur | Source |",
        "|---|---|---|---:|---|---|---|---|---|---|",
    ]
    for data in pages_data:
        pid = data["page"]["id"]
        for item in data.get("inventory", []):
            matrix.append(
                f"| {pid} | {', '.join(item.get('rules_executed', [])) or '—'} | {item['name']} | {item.get('count', 0)} | inventaire | **{item['status']}** | — | — | `{item.get('selector', '')}` | `{item.get('source', '')}` |"
            )
        for item in data.get("differences", []):
            matrix.append(
                f"| {pid} | `{item.get('rule_id', '—')}` | {item.get('component', 'global')} | {item.get('instance') or '—'} | {item.get('kind', 'integration')} | **{item.get('status', 'ECART_OBSERVE')}** | **{item.get('qualification_status', 'A_CONFIRMER')}** | {item.get('severity', '—')} | `{str(item.get('selector', '')).replace('|', '—')}` | `{item.get('source', '')}` |"
            )
        if not data.get("inventory") and not data.get("differences"):
            matrix.append(
                f"| {pid} | — | — | — | page | **REFERENCE_INDISPONIBLE** | — | — | — | — |"
            )
    atomic_text(dsfr_root / "MATRICE-RESPECT-DSFR.md", "\n".join(matrix) + "\n")

    def evidence_links(item: dict[str, Any]) -> str:
        links = []
        for index, value in enumerate(item.get("evidence", []), 1):
            if isinstance(value, str):
                links.append(f"<a href='../{html.escape(value)}'>Preuve {index}</a>")
        return " · ".join(links) or "Preuve non liée"

    sections: list[str] = []
    summary: list[str] = []
    for data in pages_data:
        page = data["page"]
        pid = page["id"]
        diffs = data.get("differences", [])
        inv = data.get("inventory", [])
        counts = Counter(item.get("severity", "À qualifier") for item in diffs)
        page_confirmed = sum(
            item.get("qualification_status") == "ECART_CONFIRME" for item in diffs
        )
        summary.append(
            f"| {pid} — {page['name']} | {data.get('status', 'REFERENCE_INDISPONIBLE')} | {len(inv)} | {len(diffs)} | {page_confirmed} |"
        )
        inv_rows = (
            "".join(
                f"<tr data-status='{html.escape(str(item.get('status', 'DETECTE_NON_AUDITE')))}'><td>{html.escape(str(item.get('name', '—')))}</td><td><code>{html.escape(str(item.get('selector', '')))}</code></td><td>{item.get('count', 0)}</td><td>{html.escape(status_labels.get(str(item.get('status')), str(item.get('status'))))}</td><td><code>{html.escape(', '.join(item.get('rules_executed', [])) or 'Aucune règle ciblée')}</code></td></tr>"
                for item in inv
            )
            or "<tr><td colspan='5'>Aucun inventaire disponible.</td></tr>"
        )
        cards = []
        for item in diffs:
            qual = str(item.get("qualification_status", "A_CONFIRMER"))
            severity = str(item.get("severity", "À qualifier"))
            kind = str(item.get("kind", "integration"))
            rule_id = str(item.get("rule_id", "—"))
            failed = (
                "".join(
                    f"<li>{html.escape(str(message))}</li>"
                    for message in item.get("failed_conditions", [])
                )
                or "<li>Condition détaillée indisponible.</li>"
            )
            qualification_note = item.get("qualification", {}) or {}
            origin = str(item.get("observed_html_origin", "RENDERED_DOM"))
            observed_heading = {
                "RENDERED_DOM": "DOM rendu observé",
                "RESPONSE_HTML": "Réponse HTML observée",
                "REPOSITORY_SOURCE": "Code du dépôt observé",
                "RESOURCE_URLS": "Ressources chargées observées",
                "COMPUTED_VALUE": "Valeur calculée observée",
                "MEASUREMENTS": "Mesures observées",
            }.get(origin, "Preuve observée")
            origin_note = (
                "Il ne s’agit pas nécessairement du fichier source du dépôt applicatif."
                if origin == "RENDERED_DOM"
                else "Cette preuve n’est pas un extrait du code source applicatif."
            )
            review = f"<p><b>Revue :</b> {html.escape(str(qualification_note.get('comment', 'Signal non encore qualifié humainement.')))}</p>"
            cards.append(
                f"<article class='finding' data-status='{html.escape(qual)}' data-severity='{html.escape(severity)}' data-kind='{html.escape(kind)}' data-rule='{html.escape(rule_id)}'><h4><code>{html.escape(rule_id)}</code> — {html.escape(str(item.get('title', 'Écart observé')))}</h4><p class='badges'><span>{html.escape(status_labels.get(qual, qual))}</span><span>{html.escape(severity)}</span><span>{html.escape(kind.upper())}</span><span>instance {item.get('instance') or 'page'}</span></p><p><b>Sélecteur :</b> <code>{html.escape(str(item.get('selector', '—')))}</code></p><p><b>Comparaison :</b> {html.escape(str(item.get('assessed_against', 'REFERENCE_VERSION_INDISPONIBLE')))} · observée {html.escape(', '.join(item.get('observed_versions', [])) or 'inconnue')} · cible {html.escape(str(item.get('reference_target_version', '—')))}</p><p><b>Conditions en échec :</b></p><ul>{failed}</ul><div class='code-grid'><div><h5>{html.escape(observed_heading)}</h5><pre><code>{html.escape(str(item.get('observed_html', '')))}</code></pre></div><div><h5>Structure attendue</h5><pre><code>{html.escape(str(item.get('expected_html', '')))}</code></pre></div></div><p class='origin'>Origine de la preuve observée : <b>{html.escape(origin)}</b>. {html.escape(origin_note)}</p><p><b>Source :</b> <code>{html.escape(str(item.get('source', '—')))}</code></p><p><b>Recommandation :</b> {html.escape(str(item.get('recommendation', '—')))}</p><p><b>Vérification :</b> {html.escape(str(item.get('verification', '—')))}</p>{review}<p>{evidence_links(item)}</p></article>"
            )
        details = (
            "".join(cards)
            or "<p>Aucun signal d’écart pour les règles exécutées sur cette page.</p>"
        )
        version = data.get("version", {}) or {}
        versions = ", ".join(data.get("detected_versions", [])) or "non déterminée"
        sections.append(
            f"<section id='{pid}'><h2>{pid} — {html.escape(page['name'])}</h2><p><a href='{html.escape(page['url'])}'>{html.escape(page['url'])}</a></p><p><b>{html.escape(str(data.get('status', 'REFERENCE_INDISPONIBLE')))}</b> · version observée : {html.escape(versions)} · cible : {html.escape(str(version.get('target', data.get('reference_version', '—'))))} · mode : {html.escape(str(version.get('comparison_mode', 'REFERENCE_VERSION_INDISPONIBLE')))}.</p><p>{len(inv)} type(s) de composant · {len(diffs)} signal(s) · {page_confirmed} écart(s) confirmé(s). Bloquants : {counts['Bloquant']} · Majeurs : {counts['Majeur']}.</p><h3>Inventaire et couverture</h3><table class='inventory'><thead><tr><th>Composant</th><th>Sélecteur</th><th>Nombre</th><th>Statut explicite</th><th>Règles exécutées</th></tr></thead><tbody>{inv_rows}</tbody></table><h3>Constats détaillés par instance</h3>{details}<p><a href='pages/{pid}.json'>Synthèse JSON de la page</a></p></section>"
        )

    nav = "".join(
        f"<li><a href='#{data['page']['id']}'>{data['page']['id']} — {html.escape(data['page']['name'])}</a></li>"
        for data in pages_data
    )
    overall = (
        "ÉCARTS CONFIRMÉS ET SIGNAUX À QUALIFIER"
        if confirmed_count
        else (
            "SIGNAUX D’ÉCART À QUALIFIER"
            if differences
            else "AUCUN ÉCART OBSERVÉ SUR LES RÈGLES EXÉCUTÉES"
        )
    )
    root_rows = (
        "".join(
            f"<tr><td><code>{html.escape(str(item['rule_id']))}</code></td><td>{html.escape(str(item['severity']))}</td><td>{html.escape(str(item['kind']).upper())}</td><td>{html.escape(str(item['component']))}</td><td>{html.escape(str(item['title']))}</td><td>{item['count']}</td><td>{item['confirmed']}</td><td>{html.escape(', '.join(str(page) for page in item['pages']))}</td></tr>"
            for item in root_causes
        )
        or "<tr><td colspan='8'>Aucune cause racine regroupée.</td></tr>"
    )
    root_summary = f"<div class='root-causes'><h2>Causes racines consolidées</h2><table><thead><tr><th>Règle</th><th>Sévérité</th><th>Portée</th><th>Élément</th><th>Cause</th><th>Instances</th><th>Confirmées</th><th>Pages</th></tr></thead><tbody>{root_rows}</tbody></table></div>"
    filters = "<div class='filters' role='group' aria-label='Filtres des constats'><button type='button' data-filter='all'>Tous</button><button type='button' data-filter='ECART_CONFIRME'>Écarts confirmés</button><button type='button' data-filter='A_CONFIRMER'>À confirmer</button><button type='button' data-filter='Bloquant'>Bloquants</button><button type='button' data-filter='migration'>Migration</button><label>Rechercher <input id='finding-search' type='search'></label></div>"
    script = """<script>(()=>{const cards=[...document.querySelectorAll('.finding')];let active='all';const apply=()=>{const q=(document.querySelector('#finding-search')?.value||'').toLowerCase();for(const card of cards){const match=active==='all'||card.dataset.status===active||card.dataset.severity===active||card.dataset.kind===active;card.hidden=!(match&&card.textContent.toLowerCase().includes(q));}};document.querySelectorAll('[data-filter]').forEach(button=>button.addEventListener('click',()=>{active=button.dataset.filter;apply();}));document.querySelector('#finding-search')?.addEventListener('input',apply);})();</script>"""
    document = f"<!doctype html><html lang='fr'><head><meta charset='utf-8'><meta name='viewport' content='width=device-width,initial-scale=1'><title>Audit DSFR détaillé — {html.escape(config['campaign']['name'])}</title><style>body{{font:16px/1.55 system-ui,sans-serif;color:#161616;max-width:1220px;margin:auto;padding:1rem}}header{{border-bottom:5px solid #000091}}.warning{{background:#fff4e5;border-left:6px solid #e4794a;padding:1rem}}section{{margin:3rem 0;border-top:2px solid #ddd;padding-top:1rem}}table{{border-collapse:collapse;width:100%;display:block;overflow:auto}}th,td{{border:1px solid #ccc;padding:.65rem;text-align:left;vertical-align:top}}th{{background:#eee}}code{{white-space:normal}}pre{{background:#f6f6f6;border:1px solid #ddd;padding:1rem;overflow:auto;max-height:26rem}}pre code{{white-space:pre-wrap}}a{{color:#000091}}:focus{{outline:3px solid #0a76f6;outline-offset:2px}}.filters{{position:sticky;top:0;background:#fff;border:1px solid #ccc;padding:.75rem;display:flex;gap:.5rem;flex-wrap:wrap;z-index:2}}.filters button{{padding:.55rem;border:1px solid #000091;background:#eee}}.finding{{border:2px solid #ddd;border-left:7px solid #e4794a;padding:1rem;margin:1.5rem 0}}.badges{{display:flex;gap:.5rem;flex-wrap:wrap}}.badges span{{background:#eee;padding:.2rem .55rem;font-weight:700}}.code-grid{{display:grid;grid-template-columns:1fr 1fr;gap:1rem}}.origin{{font-size:.9rem;color:#555}}[hidden]{{display:none!important}}@media(max-width:800px){{.code-grid{{grid-template-columns:1fr}}}}</style></head><body><header><h1>Audit DSFR détaillé par règle et par instance</h1><p><b>{html.escape(config['campaign']['name'])}</b></p><p class='warning'>{overall}. {len(differences)} signal(s), dont {confirmed_count} confirmé(s) et {candidate_count} à qualifier. Aucune conformité DSFR globale n’est revendiquée.</p><p>Version observée : {html.escape(', '.join(observed_versions) or 'inconnue')} · cible locale : {html.escape(', '.join(target_versions))}. Les règles de composants sont classées migration quand la référence exacte observée n’est pas disponible.</p></header><nav aria-label='Pages auditées'><h2>Accès direct</h2><ul>{nav}</ul></nav>{filters}{root_summary}<main>{''.join(sections)}</main><footer><p><a href='RAPPORT-CONSOLIDE.md'>Synthèse</a> · <a href='MATRICE-RESPECT-DSFR.md'>Matrice DSFR</a> · <a href='../AUDIT-PAR-PAGE.html'>Rapport RGAA</a></p></footer>{script}</body></html>"
    # Le HTML publié est produit exclusivement par audit_report_builder.py.

    root_md = (
        "\n".join(
            f"| `{item['rule_id']}` | {item['severity']} | {item['kind'].upper()} | {item['component']} | {str(item['title']).replace('|', '—')} | {item['count']} | {item['confirmed']} | {', '.join(str(page) for page in item['pages'])} |"
            for item in root_causes
        )
        or "| — | — | — | — | Aucune cause racine regroupée | 0 | 0 | — |"
    )
    report = f"""# Rapport consolidé DSFR détaillé — {config["campaign"]["name"]}

- **Échantillon :** {len(config["sample"])} page(s), identique à la campagne RGAA
- **Version observée :** {", ".join(observed_versions) or "non déterminée"}
- **Cible locale :** {", ".join(target_versions)}
- **Statut borné :** {overall}
- **Types de composants inventoriés :** {len(inventory)}
- **Signaux d’écart par instance :** {len(differences)}
- **Écarts confirmés après revue :** {confirmed_count}
- **Signaux restant à qualifier :** {candidate_count}

> Le code cité provient du DOM rendu et pas nécessairement du dépôt applicatif. Ce rapport ne revendique ni conformité DSFR globale, ni droit d’usage de la marque de l’État.

## Causes racines consolidées

| Règle | Sévérité | Portée | Élément | Cause | Instances | Confirmées | Pages |
|---|---|---|---|---|---:|---:|---|
{root_md}

## Pages

| Page | Statut | Composants | Signaux | Confirmés |
|---|---|---:|---:|---:|
{chr(10).join(summary)}

## Livrables

- [Rapport HTML détaillé et filtrable](AUDIT-PAR-PAGE.html)
- [Matrice par règle et instance](MATRICE-RESPECT-DSFR.md)
- [Inventaire JSON](INVENTAIRE-COMPOSANTS.json)
- [Constats JSON détaillés](ECARTS-COMPOSANTS.json)

## Non vérifié

Droit d’usage de la marque, exhaustivité officielle du catalogue, fidélité visuelle exhaustive, lecteur d’écran réel, source applicative du dépôt et intégration exacte contre une référence locale correspondant à toute version observée différente de la cible.
"""
    atomic_text(dsfr_root / "RAPPORT-CONSOLIDE.md", report)


def _generate_dsfr_reports_legacy(config: dict[str, Any], root: Path) -> None:
    dsfr_root = root / "dsfr"
    pages_data = []
    component_totals: dict[str, dict[str, Any]] = {}
    differences = []
    for page in config["sample"]:
        path = dsfr_root / "pages" / f"{page['id']}.json"
        data = read_json(path, None)
        if not isinstance(data, dict):
            data = {
                "schema_version": 1,
                "page": page,
                "reference_version": "1.15.3",
                "detected_versions": [],
                "status": "RÉFÉRENCE NON VÉRIFIABLE",
                "claim": "non vérifié",
                "inventory": [],
                "differences": [],
                "sources": [],
                "not_verified": ["Phase DSFR non exécutée pour cette page"],
            }
            write_json(path, data)
        pages_data.append(data)
        differences.extend(
            [{**item, "page": page["id"]} for item in data.get("differences", [])]
        )
        for item in data.get("inventory", []):
            entry = component_totals.setdefault(
                item["name"],
                {
                    "name": item["name"],
                    "selector": item.get("selector", ""),
                    "count": 0,
                    "pages": [],
                    "status": "ALIGNÉ",
                    "source": item.get("source", ""),
                },
            )
            entry["count"] += int(item.get("count", 0))
            entry["pages"].append(page["id"])
            if item.get("status") == "ÉCART":
                entry["status"] = "ÉCART"
    inventory = sorted(component_totals.values(), key=lambda item: item["name"])
    grouped: dict[tuple[str, str, str, str], dict[str, Any]] = {}
    for item in differences:
        key = (
            str(item.get("title", "")),
            str(item.get("component", "global")),
            str(item.get("severity", "À qualifier")),
            str(item.get("source", "")),
        )
        cause = grouped.setdefault(
            key,
            {
                "title": key[0],
                "component": key[1],
                "severity": key[2],
                "source": key[3],
                "pages": [],
                "count": 0,
            },
        )
        cause["count"] += 1
        if item.get("page") not in cause["pages"]:
            cause["pages"].append(item.get("page"))
    severity_order = {"Bloquant": 0, "Majeur": 1, "Mineur": 2, "À qualifier": 3}
    root_causes = sorted(
        grouped.values(),
        key=lambda item: (severity_order.get(item["severity"], 9), item["title"]),
    )
    write_json(
        dsfr_root / "INVENTAIRE-COMPOSANTS.json",
        {
            "schema_version": 1,
            "reference_version": "1.15.3",
            "pages": len(config["sample"]),
            "components": inventory,
        },
    )
    write_json(
        dsfr_root / "ECARTS-COMPOSANTS.json",
        {
            "schema_version": 1,
            "claim": "Aucune conformité DSFR globale n’est revendiquée.",
            "root_causes": root_causes,
            "differences": differences,
        },
    )

    matrix = [
        "# Matrice de respect DSFR",
        "",
        "> Vérification bornée aux sources locales DSFR 1.15.2 lues. Aucun statut « conforme DSFR ».",
        "",
        "| Page | Élément | Type | Statut | Sévérité | Constat | Source |",
        "|---|---|---|---|---|---|---|",
    ]
    for data in pages_data:
        pid = data["page"]["id"]
        for item in data.get("inventory", []):
            matrix.append(
                f"| {pid} | {item['name']} | composant | **{item['status']}** | — | {item.get('count', 0)} occurrence(s) | `{item.get('source', '')}` |"
            )
        for item in data.get("differences", []):
            matrix.append(
                f"| {pid} | {item.get('component', 'global')} | {item.get('kind', 'global')} | **ÉCART** | {item.get('severity', '—')} | {str(item.get('title', '')).replace('|', '—')} | `{item.get('source', '')}` |"
            )
        if not data.get("inventory") and not data.get("differences"):
            matrix.append(
                f"| {pid} | — | page | **INDÉTERMINÉ** | — | Phase DSFR non exécutée. | — |"
            )
    atomic_text(dsfr_root / "MATRICE-RESPECT-DSFR.md", "\n".join(matrix) + "\n")

    sections = []
    summary = []
    for data in pages_data:
        page = data["page"]
        pid = page["id"]
        diffs = data.get("differences", [])
        inv = data.get("inventory", [])
        counts = Counter(item.get("severity", "À qualifier") for item in diffs)
        summary.append(
            f"| {pid} — {page['name']} | {data.get('status', 'INDÉTERMINÉ')} | {len(inv)} | {len(diffs)} |"
        )
        inv_rows = (
            "".join(
                f"<tr><td>{html.escape(str(item.get('name', '—')))}</td><td><code>{html.escape(str(item.get('selector', '')))}</code></td><td>{item.get('count', 0)}</td><td>{html.escape(str(item.get('status', 'INDÉTERMINÉ')))}</td></tr>"
                for item in inv
            )
            or "<tr><td colspan='4'>Aucun inventaire disponible.</td></tr>"
        )
        diff_rows = (
            "".join(
                f"<tr><td>{html.escape(str(item.get('severity', '—')))}</td><td>{html.escape(str(item.get('component', '—')))}</td><td>{html.escape(str(item.get('title', '')))}</td><td>{html.escape(str(item.get('observed', '')))}</td><td><code>{html.escape(str(item.get('source', '')))}</code></td></tr>"
                for item in diffs
            )
            or "<tr><td colspan='5'>Aucun écart observé dans le périmètre automatisé lu.</td></tr>"
        )
        versions = ", ".join(data.get("detected_versions", [])) or "non déterminée"
        evidence = data.get("evidence", {})
        evidence_links = (
            " · ".join(
                f"<a href='../{html.escape(str(evidence[key]))}'>{label}</a>"
                for key, label in (
                    ("raw", "Preuve brute"),
                    ("desktop_screenshot", "Capture desktop"),
                    ("mobile_screenshot", "Capture mobile"),
                )
                if evidence.get(key)
            )
            or "Preuves non produites"
        )
        sections.append(
            f"<section id='{pid}'><h2>{pid} — {html.escape(page['name'])}</h2><p><a href='{html.escape(page['url'])}'>{html.escape(page['url'])}</a></p><p><b>{html.escape(data.get('status', 'INDÉTERMINÉ'))}</b> · version détectée : {html.escape(versions)} · {len(inv)} type(s) de composant · {len(diffs)} écart(s).</p><p>Bloquants : {counts['Bloquant']} · Majeurs : {counts['Majeur']} · Mineurs : {counts['Mineur']}</p><h3>Inventaire</h3><table><thead><tr><th>Composant</th><th>Sélecteur</th><th>Nombre</th><th>Statut</th></tr></thead><tbody>{inv_rows}</tbody></table><h3>Écarts observés</h3><table><thead><tr><th>Sévérité</th><th>Élément</th><th>Écart</th><th>Observation</th><th>Source</th></tr></thead><tbody>{diff_rows}</tbody></table><p><a href='pages/{pid}.json'>Synthèse JSON</a> · {evidence_links}</p></section>"
        )
    nav = "".join(
        f"<li><a href='#{data['page']['id']}'>{data['page']['id']} — {html.escape(data['page']['name'])}</a></li>"
        for data in pages_data
    )
    overall = (
        "ÉCARTS OBSERVÉS"
        if differences
        else (
            "RÉFÉRENCE NON VÉRIFIABLE"
            if any(
                data.get("status") == "RÉFÉRENCE NON VÉRIFIABLE" for data in pages_data
            )
            else "AUCUN ÉCART OBSERVÉ DANS LE PÉRIMÈTRE LU"
        )
    )
    root_rows = (
        "".join(
            f"<tr><td>{html.escape(str(item['severity']))}</td><td>{html.escape(str(item['component']))}</td><td>{html.escape(str(item['title']))}</td><td>{item['count']}</td><td>{html.escape(', '.join(str(page) for page in item['pages']))}</td></tr>"
            for item in root_causes
        )
        or "<tr><td colspan='5'>Aucune cause racine regroupée.</td></tr>"
    )
    root_summary = f"<div class='root-causes'><h2>Causes racines consolidées</h2><table><thead><tr><th>Sévérité</th><th>Élément</th><th>Cause</th><th>Occurrences</th><th>Pages</th></tr></thead><tbody>{root_rows}</tbody></table></div>"
    document = f"<!doctype html><html lang='fr'><head><meta charset='utf-8'><meta name='viewport' content='width=device-width,initial-scale=1'><title>Audit DSFR — {html.escape(config['campaign']['name'])}</title><style>body{{font:16px/1.55 system-ui,sans-serif;color:#161616;max-width:1180px;margin:auto;padding:1rem}}header{{border-bottom:5px solid #000091}}.warning{{background:#fff4e5;border-left:6px solid #e4794a;padding:1rem}}section{{margin:3rem 0;border-top:2px solid #ddd;padding-top:1rem}}table{{border-collapse:collapse;width:100%;display:block;overflow:auto}}th,td{{border:1px solid #ccc;padding:.65rem;text-align:left;vertical-align:top}}th{{background:#eee}}code{{white-space:normal}}a{{color:#000091}}:focus{{outline:3px solid #0a76f6;outline-offset:2px}}</style></head><body><header><h1>Audit des composants et du respect du DSFR</h1><p><b>{html.escape(config['campaign']['name'])}</b></p><p class='warning'>{overall}. {len(differences)} écart(s) observé(s). Vérification bornée : aucune conformité DSFR globale n’est revendiquée.</p></header><nav aria-label='Pages auditées'><h2>Accès direct</h2><ul>{nav}</ul></nav>{root_summary}<main>{''.join(sections)}</main><footer><p><a href='RAPPORT-CONSOLIDE.md'>Synthèse</a> · <a href='MATRICE-RESPECT-DSFR.md'>Matrice DSFR</a> · <a href='../AUDIT-PAR-PAGE.html'>Rapport RGAA</a></p></footer></body></html>"
    # Cette fonction legacy n'est plus appelée. Le builder commun est l'unique
    # producteur des rapports HTML publiés.
    root_md = (
        "\n".join(
            f"| {item['severity']} | {item['component']} | {str(item['title']).replace('|', '—')} | {item['count']} | {', '.join(str(page) for page in item['pages'])} |"
            for item in root_causes
        )
        or "| — | — | Aucune cause racine regroupée | 0 | — |"
    )
    report = f"""# Rapport consolidé DSFR — {config["campaign"]["name"]}

- **Échantillon :** {len(config["sample"])} page(s), identique à la campagne RGAA
- **Référence locale :** DSFR 1.15.2
- **Statut borné :** {overall}
- **Types de composants inventoriés :** {len(inventory)}
- **Écarts observés :** {len(differences)}

> Ce rapport ne revendique ni conformité DSFR globale, ni droit d’usage de la marque de l’État.

## Causes racines consolidées

| Sévérité | Élément | Cause | Occurrences | Pages |
|---|---|---|---:|---|
{root_md}

## Pages

| Page | Statut | Composants | Écarts |
|---|---|---:|---:|
{chr(10).join(summary)}

## Livrables

- [Rapport HTML](AUDIT-PAR-PAGE.html)
- [Matrice de respect](MATRICE-RESPECT-DSFR.md)
- [Inventaire JSON](INVENTAIRE-COMPOSANTS.json)
- [Écarts JSON](ECARTS-COMPOSANTS.json)

## Non vérifié

Droit d’usage de la marque, exhaustivité du catalogue officiel, fidélité visuelle exhaustive, lecteur d’écran réel et états non exposés dans la capture.
"""
    atomic_text(dsfr_root / "RAPPORT-CONSOLIDE.md", report)


def generate_reports(config_path: Path) -> None:
    config = read_yaml(config_path)
    root = campaign_root(config_path)
    schema = json.loads(
        (SKILL_ROOT / "schemas/campaign.schema.json").read_text(encoding="utf-8")
    )
    schema_errors = fallback_schema_errors(config, schema)
    if schema_errors:
        raise ValueError("Configuration invalide : " + "; ".join(schema_errors))
    findings = load_findings(root)
    catalog = load_catalog(root)
    qualifications = (read_json(root / "qualification.json", {}) or {}).get(
        "criteria", {}
    )
    for finding in findings:
        if finding.get("status") not in STATUSES:
            raise ValueError(
                f"Statut invalide dans findings.json : {finding.get('status')}"
            )
    by_page = {p["id"]: [] for p in config["sample"]}
    for finding in findings:
        for pid in finding.get("pages", []):
            if pid in by_page:
                by_page[pid].append(finding)
    tickets = root / "tickets"
    tickets.mkdir(exist_ok=True)
    for old in tickets.glob("*.md"):
        old.unlink()
    for finding in findings:
        if finding.get("status") not in {"NC-A", "RECO"}:
            continue
        fid = re.sub(
            r"[^A-Za-z0-9_-]+", "-", str(finding.get("id") or "constat")
        ).strip("-")
        test = finding.get("test") or "—"
        criterion = finding.get("criterion") or "—"
        reference = (
            f"- [Méthode RGAA — test {test}](https://accessibilite.numerique.gouv.fr/methode/criteres-et-tests/#{test})"
            if test != "—"
            else "- Recommandation fonctionnelle hors critère RGAA autonome."
        )
        text = f"""# {fid} — {finding.get("title", "Constat")}

- **Statut :** {finding["status"]}
- **Pages :** {", ".join(finding.get("pages", []))}
- **Critère RGAA :** {criterion}
- **Test :** {test}
- **Sévérité :** {finding.get("severity", "À qualifier")}

## Constat

{finding.get("description", "")}

## Impact utilisateur

{finding.get("impact", "À documenter lors de la validation humaine.")}

## Preuves

{chr(10).join("- `" + str(p) + "`" for p in finding.get("evidence", [])) or "- À compléter."}

## Recommandation

{finding.get("recommendation", "À définir avec l’équipe produit.")}

## Vérification

{finding.get("verification", "Rejouer le scénario instrumenté et compléter par une validation humaine applicable.")}

## Référence

{reference}
"""
        atomic_text(tickets / f"{finding['status']}-{fid}.md", text)

    rows = []
    for cid in CRITERION_IDS:
        status = str(qualifications.get(cid, {}).get("status", "NT"))
        comment = str(
            qualifications.get(cid, {}).get("comment", "Validation à réaliser.")
        )
        related = [f for f in findings if str(f.get("criterion")) == cid]
        if related:
            winner = max(related, key=lambda f: finding_priority(str(f.get("status"))))
            status = str(winner["status"])
            comment = str(winner.get("description", comment))
        if status not in STATUSES:
            status, comment = "NT", "Statut source invalide ; validation à réaliser."
        rows.append((cid, catalog.get(cid, ""), status, comment))
    matrix_lines = [
        "# Matrice RGAA 4.1.2 — 106 critères",
        "",
        "> Préqualification instrumentée. Aucun taux réglementaire n’est calculé.",
        "",
        "| Critère | Intitulé | Statut | Qualification |",
        "|---|---|---|---|",
    ]
    matrix_lines += [
        f"| {cid} | {title.replace('|', '—')} | **{status}** | {comment.replace('|', '—')} |"
        for cid, title, status, comment in rows
    ]
    atomic_text(root / "MATRICE-RGAA-106.md", "\n".join(matrix_lines) + "\n")

    page_sections = []
    summary_rows = []
    for page in config["sample"]:
        pid = page["id"]
        fs = by_page[pid]
        nca = sum(1 for f in fs if f.get("status") == "NC-A")
        deep = read_json(root / "inspections-approfondies" / f"{pid}.json", {}) or {}
        interactions = read_json(root / "interactions" / f"{pid}.json", {}) or {}
        a11y = read_json(root / "analyses-skills" / f"{pid}.json", {}) or {}
        wcag = read_json(root / "tests-wcag" / f"{pid}.json", {}) or {}
        images = len(deep.get("images", []))
        links = deep.get("links", {}).get("total", 0)
        contrast_failures = len(deep.get("contrast", {}).get("failures", []))
        tabs = len(interactions.get("keyboard", []))
        ax_nodes = a11y.get("nodes", 0)
        wcag_done = len(wcag.get("tests", {}))
        summary_rows.append(
            f"| {pid} — {page['name']} | {nca} | {len(fs)} | [Rapport](pages/{pid}.md) |"
        )
        md = [
            f"# {pid} — {page['name']}",
            "",
            f"**URL :** {page['url']}  ",
            "**Nature :** préqualification automatisée et instrumentée ; validation humaine requise.",
            "",
            "## Résumé instrumenté",
            "",
            f"- {images} image(s), {links} lien(s), {contrast_failures} contraste(s) candidat(s) en échec.",
            f"- {tabs} tabulation(s), {ax_nodes} nœud(s) d’arbre a11y, {wcag_done}/9 contrats WCAG produits.",
            "",
            "## Constats",
            "",
            "| Critère | Test | Statut | Sévérité | Constat |",
            "|---|---|---|---|---|",
        ]
        if fs:
            md += [
                f"| {f.get('criterion', '—')} | {f.get('test', '—')} | **{f['status']}** | {f.get('severity', '—')} | {str(f.get('description', '')).replace('|', '—')} |"
                for f in fs
            ]
        else:
            md.append(
                "| — | — | **NT** | — | Aucun constat qualifié ; analyser les preuves. |"
            )
        md += [
            "",
            "## Preuves générées",
            "",
            f"- `captures-ay11/{pid}/`",
            f"- `tests-wcag/{pid}.json`",
            f"- `interactions/{pid}.json`",
            f"- `inspections-approfondies/{pid}.json`",
            f"- `analyses-skills/{pid}.json`",
            "",
            "## Limites",
            "",
            "- Aucun test réel NVDA, JAWS ou VoiceOver sauf mention explicite.",
            "- Une absence de violation automatisée ne constitue pas une conformité.",
        ]
        atomic_text(root / "pages" / f"{pid}.md", "\n".join(md) + "\n")
        frows = (
            "".join(
                f"<tr><td>{html.escape(str(f.get('criterion', '—')))}</td><td>{html.escape(str(f.get('test', '—')))}</td><td><strong class='{('bad' if f['status'] == 'NC-A' else 'note')}'>{html.escape(f['status'])}</strong></td><td>{html.escape(str(f.get('description', '')))}</td></tr>"
                for f in fs
            )
            or "<tr><td>—</td><td>—</td><td>NT</td><td>Aucun constat qualifié ; analyser les preuves.</td></tr>"
        )
        page_sections.append(
            f"<section id='{pid}'><h2>{pid} — {html.escape(page['name'])}</h2><p><a href='{html.escape(page['url'])}'>{html.escape(page['url'])}</a></p><p><b>{nca}</b> NC-A ; <b>{len(fs)}</b> constat(s).</p><ul><li>{images} image(s), {links} lien(s), {contrast_failures} contraste(s) candidat(s) en échec.</li><li>{tabs} tabulation(s), {ax_nodes} nœud(s) d’arbre a11y, {wcag_done}/9 contrats WCAG produits.</li></ul><table><thead><tr><th>Critère</th><th>Test</th><th>Statut</th><th>Constat</th></tr></thead><tbody>{frows}</tbody></table><p><a href='pages/{pid}.md'>Preuves et rapport technique</a></p></section>"
        )
    counts = Counter(status for _, _, status, _ in rows)
    consolidated = f"""# Rapport consolidé — {config["campaign"]["name"]}

- **Cible :** {config["campaign"]["target"]}
- **Référentiel :** RGAA 4.1.2 — 106 critères / 258 tests
- **Échantillon :** {len(config["sample"])} page(s)
- **NC-A consolidés :** {counts["NC-A"]}
- **Critères NT :** {counts["NT"]}

> Aucun taux RGAA officiel. Les statuts sont bornés aux preuves consignées.

## Pages

| Page | NC-A | Constats | Détail |
|---|---:|---:|---|
{chr(10).join(summary_rows)}

## Livrables

- [Rapport HTML](AUDIT-PAR-PAGE.html)
- [Matrice RGAA 106](MATRICE-RGAA-106.md)
- [Validation](VALIDATION.json)
- [Tickets](tickets/)

## Limites

L’arbre d’accessibilité est une préqualification. Aucun test réel de lecteur
d’écran ou parcours authentifié n’est revendiqué sans preuve dédiée.
"""
    atomic_text(root / "RAPPORT-CONSOLIDE.md", consolidated)
    nav = "".join(
        f"<li><a href='#{p['id']}'>{p['id']} — {html.escape(p['name'])}</a></li>"
        for p in config["sample"]
    )
    doc = f"""<!doctype html><html lang='fr'><head><meta charset='utf-8'><meta name='viewport' content='width=device-width,initial-scale=1'><title>Audit RGAA — {html.escape(config["campaign"]["name"])}</title><style>body{{font:16px/1.55 system-ui,sans-serif;color:#161616;max-width:1180px;margin:auto;padding:1rem}}header{{border-bottom:5px solid #000091}}.warning{{background:#fff4e5;border-left:6px solid #e4794a;padding:1rem}}nav ul{{columns:2}}section{{margin:3rem 0;border-top:2px solid #ddd;padding-top:1rem}}table{{border-collapse:collapse;width:100%;display:block;overflow:auto}}th,td{{border:1px solid #ccc;padding:.65rem;text-align:left;vertical-align:top}}th{{background:#eee}}.bad{{color:#ce0500}}.note{{color:#6a4800}}a{{color:#000091}}:focus{{outline:3px solid #0a76f6;outline-offset:2px}}@media(max-width:700px){{nav ul{{columns:1}}}}</style></head><body><header><h1>Audit RGAA automatisé page par page</h1><p><b>{html.escape(config["campaign"]["name"])}</b></p><p class='warning'>{counts["NC-A"]} critère(s) NC-A consolidé(s), {counts["NT"]} NT. Aucun taux RGAA officiel. Préqualification lecteur d’écran par arbre a11y uniquement.</p></header><nav aria-label='Pages auditées'><h2>Accès direct</h2><ul>{nav}</ul></nav><main>{"".join(page_sections)}</main><footer><p><a href='RAPPORT-CONSOLIDE.md'>Synthèse</a> · <a href='MATRICE-RGAA-106.md'>Matrice 106</a></p></footer></body></html>"""
    # Le portail HTML publié est produit exclusivement par le builder DSFR.
    if config.get("phases", {}).get("rgaa_checks", False):
        generate_rgaa_v2_reports(config, root)
    if config.get("phases", {}).get("dsfr_checks", False):
        generate_dsfr_reports(config, root)
    if config.get("phases", {}).get("rgaa_checks", False) or config.get(
        "phases", {}
    ).get("dsfr_checks", False):
        generate_engine_coverage(root)
    # Toujours demander au builder le portail publié, même si une campagne
    # ne garde qu'une des deux phases d'audit.
    generate_audit_portal(config, root)
    editorial_paths = list(root.glob("*.md"))
    for directory in (root / "rgaa", root / "dsfr", root / "pages", root / "tickets"):
        if directory.is_dir():
            editorial_paths.extend(
                path for path in directory.rglob("*.md") if path.is_file()
            )
    for editorial_path in sorted(set(editorial_paths)):
        if editorial_path.is_file():
            atomic_text(
                editorial_path,
                editorial_path.read_text(encoding="utf-8")
                .replace("—", "-")
                .replace("–", "-"),
            )
    generate_artifact_manifest(root)


def fallback_schema_errors(
    value: Any, schema: dict[str, Any], path: str = "$"
) -> list[str]:
    errors: list[str] = []
    expected = schema.get("type")
    checks = {
        "object": lambda x: isinstance(x, dict),
        "array": lambda x: isinstance(x, list),
        "string": lambda x: isinstance(x, str),
        "integer": lambda x: isinstance(x, int) and not isinstance(x, bool),
        "boolean": lambda x: isinstance(x, bool),
    }
    if expected in checks and not checks[expected](value):
        return [f"{path} : type {expected} attendu"]
    if "const" in schema and value != schema["const"]:
        errors.append(f"{path} : valeur attendue {schema['const']!r}")
    if "enum" in schema and value not in schema["enum"]:
        errors.append(f"{path} : valeur non autorisée")
    if isinstance(value, dict):
        properties = schema.get("properties", {})
        required = schema.get("required", [])
        for key in required:
            if key not in value:
                errors.append(f"{path}.{key} : propriété requise")
        if schema.get("additionalProperties") is False:
            for key in value.keys() - properties.keys():
                errors.append(f"{path}.{key} : propriété inconnue")
        for key, item in value.items():
            child = properties.get(key)
            if isinstance(child, dict):
                errors.extend(fallback_schema_errors(item, child, f"{path}.{key}"))
    elif isinstance(value, list):
        if len(value) < schema.get("minItems", 0):
            errors.append(f"{path} : trop peu d’éléments")
        if "maxItems" in schema and len(value) > schema["maxItems"]:
            errors.append(f"{path} : trop d’éléments")
        if schema.get("uniqueItems"):
            serial = [json.dumps(x, sort_keys=True) for x in value]
            if len(serial) != len(set(serial)):
                errors.append(f"{path} : doublons interdits")
        child = schema.get("items")
        if isinstance(child, dict):
            for index, item in enumerate(value):
                errors.extend(fallback_schema_errors(item, child, f"{path}[{index}]"))
    elif isinstance(value, str):
        if len(value) < schema.get("minLength", 0):
            errors.append(f"{path} : chaîne trop courte")
        if schema.get("pattern") and not re.search(schema["pattern"], value):
            errors.append(f"{path} : format invalide")
    elif isinstance(value, int) and not isinstance(value, bool):
        if "minimum" in schema and value < schema["minimum"]:
            errors.append(f"{path} : valeur trop petite")
        if "maximum" in schema and value > schema["maximum"]:
            errors.append(f"{path} : valeur trop grande")
    return errors


def validate_campaign(
    config_path: Path, write_result: bool = True
) -> tuple[list[str], list[str]]:
    root = campaign_root(config_path)
    errors: list[str] = []
    warnings: list[str] = []
    try:
        config = read_yaml(config_path)
    except Exception as exc:
        return [str(exc)], []
    schema = json.loads(
        (SKILL_ROOT / "schemas/campaign.schema.json").read_text(encoding="utf-8")
    )
    try:
        import jsonschema

        jsonschema.Draft202012Validator(schema).validate(config)
    except ImportError:
        errors.extend(
            f"Schéma campaign.yaml : {message}"
            for message in fallback_schema_errors(config, schema)
        )
    except Exception as exc:
        errors.append(f"Schéma campaign.yaml : {exc}")
    state = load_state(root)
    state_schema = json.loads(
        (SKILL_ROOT / "schemas/state.schema.json").read_text(encoding="utf-8")
    )
    errors.extend(
        f"Schéma state.json : {message}"
        for message in fallback_schema_errors(state, state_schema)
    )
    if config.get("schema_version") != 1:
        errors.append("schema_version doit valoir 1")
    if config.get("campaign", {}).get("profile") != "rgaa-106":
        errors.append("Le profil doit être rgaa-106")
    pages = config.get("sample") or []
    if not pages:
        errors.append("Échantillon vide")
    if len(pages) > 15:
        warnings.append("Échantillon supérieur à 15 pages")
    ids = [p.get("id") for p in pages]
    if len(ids) != len(set(ids)):
        errors.append("Identifiants de pages dupliqués")
    normalized_urls = []
    for page in pages:
        try:
            normalized_urls.append(validate_url(str(page.get("url", ""))))
        except ValueError:
            errors.append(f"URL invalide : {page.get('id', '?')}")
    if len(normalized_urls) != len(set(normalized_urls)):
        errors.append("URLs de pages dupliquées")
    for rel in (
        "findings.json",
        "qualification.json",
        "MATRICE-RGAA-106.md",
        "RAPPORT-CONSOLIDE.md",
        "PORTAIL-AUDITS.html",
        "MANIFESTE-ARTEFACTS.json",
    ):
        if not (root / rel).is_file():
            errors.append(f"Fichier absent : {rel}")
    manifest = read_json(root / "MANIFESTE-ARTEFACTS.json", {"artifacts": []}) or {
        "artifacts": []
    }
    for item in manifest.get("artifacts", []):
        artifact = root / str(item.get("path", ""))
        if not artifact.is_file():
            errors.append(f"Artefact manifesté absent : {item.get('path')}")
            continue
        digest = hashlib.sha256(artifact.read_bytes()).hexdigest()
        if digest != item.get("sha256"):
            errors.append(f"Artefact modifié depuis le rapport : {item.get('path')}")
    matrix = (
        (root / "MATRICE-RGAA-106.md").read_text(encoding="utf-8")
        if (root / "MATRICE-RGAA-106.md").is_file()
        else ""
    )
    matrix_rows = re.findall(r"^\| (\d+\.\d+) \|", matrix, re.MULTILINE)
    if len(matrix_rows) != 106 or set(matrix_rows) != set(CRITERION_IDS):
        errors.append(f"Matrice incomplète : {len(matrix_rows)}/106")
    findings_doc = read_json(
        root / "findings.json", {"schema_version": 1, "findings": []}
    )
    findings_schema = json.loads(
        (SKILL_ROOT / "schemas/findings.schema.json").read_text(encoding="utf-8")
    )
    errors.extend(
        f"Schéma findings.json : {message}"
        for message in fallback_schema_errors(findings_doc, findings_schema)
    )
    findings = load_findings(root)
    for i, finding in enumerate(findings):
        if finding.get("status") not in STATUSES:
            errors.append(f"Constat {i + 1} : statut invalide")
        unknown_pages = set(finding.get("pages", [])) - set(ids)
        if unknown_pages:
            errors.append(f"Constat {i + 1} : pages inconnues {sorted(unknown_pages)}")
        if finding.get("status") == "NC-A" and (
            not finding.get("criterion")
            or not finding.get("test")
            or not finding.get("evidence")
        ):
            errors.append(f"Constat {i + 1} : NC-A sans critère, test ou preuve")
        for evidence in finding.get("evidence", []):
            evidence_path = Path(str(evidence))
            if evidence_path.is_absolute() or ".." in evidence_path.parts:
                errors.append(f"Constat {i + 1} : chemin de preuve non portable")
            elif not (root / evidence_path).exists():
                errors.append(f"Constat {i + 1} : preuve absente {evidence}")
    html_path = root / "PORTAIL-AUDITS.html"
    if html_path.is_file():
        doc = html_path.read_text(encoding="utf-8")
        section_ids = set(re.findall(r"<section id=['\"]([^'\"]+)", doc))
        page_section_ids = {
            value for value in section_ids if re.fullmatch(r"P\d+", value)
        }
        page_cards = set(re.findall(r"<h3[^>]*>\s*(P\d+)\s*-", doc))
        all_ids = set(re.findall(r"\bid=['\"]([^'\"]+)", doc))
        anchors = re.findall(r"href=['\"]#([^'\"]+)", doc)
        if not set(ids).issubset(page_cards | page_section_ids):
            errors.append("Sections HTML différentes de l’échantillon")
        if any(anchor not in all_ids for anchor in anchors):
            errors.append("Ancre HTML interne cassée")
        if re.search(r"taux (?:de )?conformité\s*[:=]?\s*\d", doc, re.IGNORECASE):
            errors.append("Taux de conformité interdit détecté")
    if config.get("phases", {}).get("rgaa_checks", False):
        rgaa_skill = SKILL_ROOT.parent / "audit-rgaa-complet"
        rgaa_catalog = json.loads(
            (rgaa_skill / "rules/rgaa-rules.json").read_text(encoding="utf-8")
        )
        rgaa_catalog_schema = json.loads(
            (rgaa_skill / "schemas/rgaa-rules.schema.json").read_text(encoding="utf-8")
        )
        errors.extend(
            f"Catalogue RGAA v2 : {message}"
            for message in fallback_schema_errors(rgaa_catalog, rgaa_catalog_schema)
        )
        rule_ids = [item.get("rule_id") for item in rgaa_catalog.get("rules", [])]
        if len(rule_ids) != len(set(rule_ids)):
            errors.append("Catalogue RGAA v2 : rule_id dupliqué")
        rgaa_findings_doc = read_json(
            root / "rgaa-findings.json", {"schema_version": 1, "findings": []}
        ) or {"schema_version": 1, "findings": []}
        rgaa_findings_schema = json.loads(
            (rgaa_skill / "schemas/rgaa-findings.schema.json").read_text(
                encoding="utf-8"
            )
        )
        errors.extend(
            f"Schéma rgaa-findings.json : {message}"
            for message in fallback_schema_errors(
                rgaa_findings_doc, rgaa_findings_schema
            )
        )
        for index, qualification in enumerate(rgaa_findings_doc.get("findings", []), 1):
            unknown_pages = set(qualification.get("pages", [])) - set(ids)
            if unknown_pages:
                errors.append(
                    f"Qualification RGAA v2 {index} : pages inconnues {sorted(unknown_pages)}"
                )
            if qualification.get("qualification_status") in {
                "C_CONFIRMEE",
                "NC_CONFIRMEE",
                "NA_CONFIRMEE",
            } and (
                not qualification.get("reviewed_by")
                or not qualification.get("comment")
                or not qualification.get("evidence")
            ):
                errors.append(
                    f"Qualification RGAA v2 {index} : décision confirmée sans revue, justification ou preuve"
                )
            for evidence_value in qualification.get("evidence", []):
                evidence_path = Path(str(evidence_value))
                if evidence_path.is_absolute() or ".." in evidence_path.parts:
                    errors.append(
                        f"Qualification RGAA v2 {index} : preuve non portable"
                    )
                elif not (root / evidence_path).exists():
                    errors.append(
                        f"Qualification RGAA v2 {index} : preuve absente {evidence_value}"
                    )
        rgaa_required = (
            "rgaa-findings.json",
            "rgaa/CONSTATS-INSTANCES.json",
            "rgaa/REVUE-MANUELLE-258.json",
            "rgaa/REVUE-MANUELLE-258.md",
            "rgaa/MATRICE-TESTS-258.md",
            "rgaa/RAPPORT-CONSOLIDE.md",
            "rgaa/AUDIT-PAR-PAGE.html",
        )
        for rel in rgaa_required:
            if not (root / rel).is_file():
                errors.append(f"Livrable RGAA v2 absent : {rel}")
        review_doc = read_json(
            root / "rgaa/REVUE-MANUELLE-258.json", {"reviews": []}
        ) or {"reviews": []}
        review_tests = [item.get("test") for item in review_doc.get("reviews", [])]
        plan_doc = read_json(root / "plan-preuves-rgaa-106.json", {}) or {}
        plan_tests = {
            item.get("test_id")
            for item in ((plan_doc.get("proof_contract") or {}).get("tests", []))
        }
        for rule in rgaa_catalog.get("rules", []):
            if plan_tests and rule.get("test") not in plan_tests:
                errors.append(f"Catalogue RGAA v2 : test inconnu {rule.get('test')}")
        if (root / "plan-preuves-rgaa-106.json").is_file() and (
            len(review_tests) != 258 or len(set(review_tests)) != 258
        ):
            errors.append(f"File de revue RGAA incomplète : {len(review_tests)}/258")
        elif not (root / "plan-preuves-rgaa-106.json").is_file():
            warnings.append(
                "Plan AY11 absent : file de revue des 258 tests non générée"
            )
        page_schema = json.loads(
            (rgaa_skill / "schemas/rgaa-page.schema.json").read_text(encoding="utf-8")
        )
        for pid in ids:
            page_evidence = root / "rgaa/pages" / f"{pid}.json"
            if not page_evidence.is_file():
                errors.append(f"Preuve RGAA v2 de page absente : {pid}")
            else:
                data = read_json(page_evidence, {}) or {}
                if data.get("evidence"):
                    errors.extend(
                        f"Schéma RGAA v2 {pid} : {message}"
                        for message in fallback_schema_errors(data, page_schema)
                    )
                else:
                    warnings.append(
                        f"Preuves RGAA v2 instrumentées non produites : {pid}"
                    )
                for key in ("raw", "screenshot"):
                    value = (data.get("evidence") or {}).get(key)
                    if not value:
                        warnings.append(f"Preuve RGAA v2 {pid}/{key} absente")
                        continue
                    evidence_path = Path(str(value))
                    if evidence_path.is_absolute() or ".." in evidence_path.parts:
                        errors.append(f"Preuve RGAA v2 non portable : {pid}/{key}")
                    elif not (root / evidence_path).is_file():
                        errors.append(f"Preuve RGAA v2 absente : {value}")
        for decisions_path in sorted((root / "rgaa").glob("P*-DECISIONS-258.json")):
            decision_doc = read_json(decisions_path, {}) or {}
            decisions = decision_doc.get("decisions", [])
            decision_page = str(
                decision_doc.get("page", {}).get("id")
                or decisions_path.name.split("-")[0]
            )
            decision_tests = [str(item.get("test", "")) for item in decisions]
            if (
                decision_doc.get("tests_count") != 258
                or len(decisions) != 258
                or len(set(decision_tests)) != 258
            ):
                errors.append(
                    f"Matrice {decision_page} : les 258 tests uniques ne sont pas tous présents"
                )
            allowed_decisions = {
                "C_CONFIRMEE",
                "NC_CONFIRMEE",
                "NA_CONFIRMEE",
                "A_RETESTER",
            }
            if any(item.get("status") not in allowed_decisions for item in decisions):
                errors.append(f"Matrice {decision_page} : décision invalide")
            if any(not item.get("coverage_mode") for item in decisions):
                errors.append(f"Matrice {decision_page} : mode de couverture absent")
            if any(
                item.get("coverage_complete") != (item.get("status") != "A_RETESTER")
                for item in decisions
            ):
                errors.append(
                    f"Matrice {decision_page} : cohérence couverture et décision invalide"
                )
            for item in decisions:
                for evidence_value in item.get("evidence", []):
                    evidence_path = Path(str(evidence_value))
                    if evidence_path.is_absolute() or ".." in evidence_path.parts:
                        errors.append(
                            f"Matrice {decision_page} {item.get('test')} : preuve non portable"
                        )
                    elif not (root / evidence_path).exists():
                        errors.append(
                            f"Matrice {decision_page} {item.get('test')} : preuve absente {evidence_value}"
                        )
        coverage_path = root / "COUVERTURE-MOTEURS.json"
        if not coverage_path.is_file():
            errors.append("Cartographie de couverture des moteurs absente")
        else:
            coverage_summary = (read_json(coverage_path, {}) or {}).get("summary", {})
            orphan_signals = int(
                coverage_summary.get("ay11_positive_tests_unlinked_to_decision", 0)
            )
            confirmed_without_coverage = int(
                coverage_summary.get("confirmed_decisions_without_declared_coverage", 0)
            )
            remaining_protocols = int(
                coverage_summary.get("rgaa_tests_requiring_additional_protocol", 0)
            )
            if orphan_signals:
                warnings.append(
                    f"Couverture moteur : {orphan_signals} test(s) avec signaux AY11 non reliés à leur décision"
                )
            if confirmed_without_coverage:
                warnings.append(
                    f"Couverture moteur : {confirmed_without_coverage} décision(s) confirmée(s) sans mode de couverture déclaré"
                )
            if remaining_protocols:
                warnings.append(
                    f"Couverture audit : {remaining_protocols} test(s) exigent encore un protocole complémentaire"
                )
        detailed_html = root / "rgaa/AUDIT-PAR-PAGE.html"
        if detailed_html.is_file():
            detailed_doc = detailed_html.read_text(encoding="utf-8")
            detailed_sections = {
                value
                for value in re.findall(r"<section id=['\"]([^'\"]+)", detailed_doc)
                if re.fullmatch(r"P\d+", value)
            }
            if set(ids) != detailed_sections:
                errors.append("Sections HTML RGAA v2 différentes de l’échantillon")
            if re.search(
                r"(?:taux\s+(?:de\s+)?conformité|conformité\s+RGAA)\s*[:=]?\s*\d+(?:[,.]\d+)?\s*%|\bconforme\s+(?:au\s+)?RGAA\b",
                detailed_doc,
                re.IGNORECASE,
            ):
                errors.append("Claim ou taux RGAA interdit dans le rapport v2")
    if config.get("phases", {}).get("dsfr_checks", False):
        dsfr_skill = SKILL_ROOT.parent / "audit-dsfr-complet"
        dsfr_findings_doc = read_json(
            root / "dsfr-findings.json", {"schema_version": 1, "findings": []}
        ) or {"schema_version": 1, "findings": []}
        dsfr_findings_schema = json.loads(
            (dsfr_skill / "schemas/dsfr-findings.schema.json").read_text(
                encoding="utf-8"
            )
        )
        errors.extend(
            f"Schéma dsfr-findings.json : {message}"
            for message in fallback_schema_errors(
                dsfr_findings_doc, dsfr_findings_schema
            )
        )
        rules_doc = json.loads(
            (dsfr_skill / "rules/dsfr-rules.json").read_text(encoding="utf-8")
        )
        rules_schema = json.loads(
            (dsfr_skill / "schemas/dsfr-rules.schema.json").read_text(encoding="utf-8")
        )
        errors.extend(
            f"Catalogue de règles DSFR : {message}"
            for message in fallback_schema_errors(rules_doc, rules_schema)
        )
        catalog_status = dsfr_catalog_status(root)
        if catalog_status["status"] != "A_JOUR":
            message = (
                "Catalogue de règles DSFR non exploitable pour la validation : "
                + catalog_status["message"]
            )
            if catalog_status["status"] in {
                "CATALOGUE_OBSOLETE",
                "CATALOGUES_MULTIPLES",
            }:
                errors.append(message)
            else:
                warnings.append(catalog_status["message"])
        for index, qualification in enumerate(dsfr_findings_doc.get("findings", []), 1):
            unknown_pages = set(qualification.get("pages", [])) - set(ids)
            if unknown_pages:
                errors.append(
                    f"Qualification DSFR {index} : pages inconnues {sorted(unknown_pages)}"
                )
            for evidence_value in qualification.get("evidence", []):
                evidence_path = Path(str(evidence_value))
                if evidence_path.is_absolute() or ".." in evidence_path.parts:
                    errors.append(f"Qualification DSFR {index} : preuve non portable")
                elif not (root / evidence_path).exists():
                    errors.append(
                        f"Qualification DSFR {index} : preuve absente {evidence_value}"
                    )
        dsfr_required = (
            "dsfr-findings.json",
            "dsfr/INVENTAIRE-COMPOSANTS.json",
            "dsfr/ECARTS-COMPOSANTS.json",
            "dsfr/MATRICE-RESPECT-DSFR.md",
            "dsfr/RAPPORT-CONSOLIDE.md",
            "dsfr/AUDIT-PAR-PAGE.html",
        )
        for rel in dsfr_required:
            if not (root / rel).is_file():
                errors.append(f"Livrable DSFR absent : {rel}")
        for pid in ids:
            page_evidence = root / "dsfr/pages" / f"{pid}.json"
            if not page_evidence.is_file():
                errors.append(f"Preuve DSFR de page absente : {pid}")
            else:
                data = read_json(page_evidence, {}) or {}
                if data.get("page", {}).get("id") != pid:
                    errors.append(f"Preuve DSFR associée à une mauvaise page : {pid}")
                evidence = data.get("evidence", {})
                if not evidence:
                    warnings.append(f"Preuves DSFR instrumentées non produites : {pid}")
                for key in ("raw", "desktop_screenshot", "mobile_screenshot"):
                    if not evidence.get(key):
                        continue
                    evidence_path = Path(str(evidence[key]))
                    if evidence_path.is_absolute() or ".." in evidence_path.parts:
                        errors.append(f"Preuve DSFR non portable : {pid}/{key}")
                    elif not (root / evidence_path).is_file():
                        errors.append(f"Preuve DSFR absente : {evidence[key]}")
                for index, item in enumerate(data.get("differences", []), 1):
                    required_fields = (
                        (
                            "rule_id",
                            "source",
                            "expected",
                            "observed",
                            "selector",
                            "observed_html",
                            "observed_html_origin",
                            "expected_html",
                            "recommendation",
                            "verification",
                            "evidence",
                        )
                        if int(data.get("schema_version", 1)) >= 2
                        else ("source", "expected", "observed")
                    )
                    missing = [
                        field for field in required_fields if not item.get(field)
                    ]
                    if missing:
                        errors.append(
                            f"Écart DSFR {pid}/{index} incomplet : {', '.join(missing)}"
                        )
                    if item.get("status") != "ECART_OBSERVE":
                        errors.append(
                            f"Écart DSFR {pid}/{index} : statut de signal invalide"
                        )
                    if item.get("qualification_status") not in {
                        "ECART_CONFIRME",
                        "AUCUN_ECART_OBSERVE",
                        "A_CONFIRMER",
                        "NON_APPLICABLE",
                        "REFERENCE_INDISPONIBLE",
                    }:
                        errors.append(
                            f"Écart DSFR {pid}/{index} : qualification invalide"
                        )
                    if item.get("observed_html_origin") not in {
                        "RENDERED_DOM",
                        "RESPONSE_HTML",
                        "REPOSITORY_SOURCE",
                        "RESOURCE_URLS",
                        "COMPUTED_VALUE",
                        "MEASUREMENTS",
                    }:
                        errors.append(
                            f"Écart DSFR {pid}/{index} : origine du code inconnue"
                        )
                    if str(item.get("source", "")).startswith(".claude/"):
                        errors.append(f"Écart DSFR {pid}/{index} : source non portable")
                    for evidence_value in item.get("evidence", []):
                        evidence_path = Path(str(evidence_value))
                        if evidence_path.is_absolute() or ".." in evidence_path.parts:
                            errors.append(
                                f"Écart DSFR {pid}/{index} : preuve non portable"
                            )
                        elif not (root / evidence_path).exists():
                            errors.append(
                                f"Écart DSFR {pid}/{index} : preuve absente {evidence_value}"
                            )
        dsfr_html = root / "dsfr/AUDIT-PAR-PAGE.html"
        if dsfr_html.is_file():
            dsfr_doc = dsfr_html.read_text(encoding="utf-8")
            dsfr_sections = {
                value
                for value in re.findall(r"<section id=['\"]([^'\"]+)", dsfr_doc)
                if re.fullmatch(r"P\d+", value)
            }
            if set(ids) != dsfr_sections:
                errors.append("Sections HTML DSFR différentes de l’échantillon")
            if re.search(
                r"\bconforme\s+(?:au\s+)?DSFR\b|\bprêt pour publication\b|\busage autorisé de la marque",
                dsfr_doc,
                re.IGNORECASE,
            ):
                errors.append("Claim DSFR interdit détecté")
    if config.get("phases", {}).get("rgaa_checks", False) or config.get(
        "phases", {}
    ).get("dsfr_checks", False):
        build_path = root / "rapport-dsfr/BUILD.json"
        portal_path = root / "PORTAIL-AUDITS.html"
        if not build_path.is_file():
            errors.append(
                "Provenance du builder DSFR absente : rapport-dsfr/BUILD.json"
            )
        if not portal_path.is_file():
            errors.append("Portail DSFR commun absent : PORTAIL-AUDITS.html")
        build_doc = read_json(build_path, {"outputs": [], "configs": []}) or {
            "outputs": [],
            "configs": [],
        }
        expected_count = (
            1
            + (
                1 + len(ids)
                if config.get("phases", {}).get("rgaa_checks", False)
                else 0
            )
            + (
                1 + len(ids)
                if config.get("phases", {}).get("dsfr_checks", False)
                else 0
            )
        )
        if len(build_doc.get("outputs", [])) != expected_count:
            errors.append(
                f"Sorties du builder DSFR incomplètes : {len(build_doc.get('outputs', []))}/{expected_count}"
            )
        if len(build_doc.get("configs", [])) != expected_count:
            errors.append(
                f"Configurations du builder DSFR incomplètes : {len(build_doc.get('configs', []))}/{expected_count}"
            )
        if (
            build_doc.get("builder_sha256")
            != hashlib.sha256(BUILDER.read_bytes()).hexdigest()
        ):
            errors.append("Empreinte du builder DSFR invalide")
        if (
            build_doc.get("builder_schema_sha256")
            != hashlib.sha256(BUILDER_SCHEMA.read_bytes()).hexdigest()
        ):
            errors.append("Empreinte du schéma du builder DSFR invalide")
        for item in build_doc.get("inputs", []):
            source = (root / item.get("path", "")).resolve()
            if (
                root.resolve() not in source.parents
                or not source.is_file()
                or item.get("sha256") != hashlib.sha256(source.read_bytes()).hexdigest()
            ):
                errors.append(
                    f"Entrée canonique du builder modifiée ou invalide : {item.get('path', '')}"
                )
        for item in build_doc.get("outputs", []):
            rel = item.get("path", "")
            output = (root / rel).resolve()
            if root.resolve() not in output.parents:
                errors.append(f"Sortie du builder hors campagne : {rel}")
                continue
            if not output.is_file():
                errors.append(f"Sortie du builder DSFR absente : {rel}")
                continue
            if item.get("sha256") != hashlib.sha256(output.read_bytes()).hexdigest():
                errors.append(f"Empreinte du builder DSFR invalide : {rel}")
            document = output.read_text(encoding="utf-8")
            if 'data-audit-builder="dsfr-components"' not in document:
                errors.append(f"Rapport non produit par le builder DSFR : {rel}")
            if "allow_raw_html" in document:
                errors.append(f"HTML brut interdit dans le rapport DSFR : {rel}")
            for href in re.findall(r'href=["\']([^"\']+)', document):
                if href.startswith("#") or re.match(r"^(?:https?|mailto|tel):", href):
                    continue
                if href.startswith("/"):
                    errors.append(f"Lien absolu non portable dans {rel} : {href}")
                    continue
                local = urllib.parse.unquote(
                    href.split("#", 1)[0].split("?", 1)[0]
                ).replace("\\", "/")
                target = (output.parent / local).resolve()
                if root.resolve() not in target.parents:
                    errors.append(f"Lien local hors campagne dans {rel} : {href}")
                elif local and not target.exists():
                    errors.append(f"Lien local absent dans {rel} : {href}")
        for item in build_doc.get("configs", []):
            rel = item.get("path", "")
            config_path = (root / rel).resolve()
            if root.resolve() not in config_path.parents or not config_path.is_file():
                errors.append(
                    f"Configuration du builder absente ou hors campagne : {rel}"
                )
                continue
            if (
                item.get("sha256")
                != hashlib.sha256(config_path.read_bytes()).hexdigest()
            ):
                errors.append(f"Empreinte de configuration du builder invalide : {rel}")
            page_config = read_json(config_path, {}) or {}
            if page_config.get("brand_mode") != "neutral":
                errors.append(f"Rapport d’audit hors brand_mode neutral : {rel}")
            sections = page_config.get("sections", [])
            if not sections or any(
                section.get("block") != "audit_report" for section in sections
            ):
                errors.append(f"Configuration sans bloc audit_report : {rel}")
        if (
            not config.get("phases", {}).get("rgaa_checks", False)
            and (root / "rgaa/AUDIT-PAR-PAGE.html").exists()
        ):
            errors.append(
                "Rapport RGAA builder obsolète alors que la phase est inactive"
            )
        if (
            not config.get("phases", {}).get("dsfr_checks", False)
            and (root / "dsfr/AUDIT-PAR-PAGE.html").exists()
        ):
            errors.append(
                "Rapport DSFR builder obsolète alors que la phase est inactive"
            )
        for pid in ids:
            if (
                config.get("phases", {}).get("rgaa_checks", False)
                and not (root / f"rgaa/pages-html/{pid}.html").is_file()
            ):
                errors.append(f"Vue RGAA DSFR-builder absente : {pid}")
            if (
                config.get("phases", {}).get("dsfr_checks", False)
                and not (root / f"dsfr/pages-html/{pid}.html").is_file()
            ):
                errors.append(f"Vue DSFR DSFR-builder absente : {pid}")
    for pid in ids:
        if not (root / "pages" / f"{pid}.md").is_file():
            errors.append(f"Rapport de page absent : {pid}")
        expected_evidence = []
        if config.get("phases", {}).get("ay11", True):
            expected_evidence.append(f"captures-ay11/{pid}")
        if config.get("phases", {}).get("browser_checks", True):
            expected_evidence.extend(
                (
                    f"tests-wcag/{pid}.json",
                    f"interactions/{pid}.json",
                    f"inspections-approfondies/{pid}.json",
                    f"analyses-skills/{pid}.json",
                )
            )
        for rel in expected_evidence:
            if not (root / rel).exists():
                warnings.append(f"Preuve non produite : {rel}")
    rgaa_qualification_count = (
        len(rgaa_findings_doc.get("findings", []))
        if "rgaa_findings_doc" in locals()
        else 0
    )
    dsfr_qualification_count = (
        len(dsfr_findings_doc.get("findings", []))
        if "dsfr_findings_doc" in locals()
        else 0
    )
    result = {
        "valid": not errors,
        "checked_at": now(),
        "errors": errors,
        "warnings": warnings,
        "counts": {
            "pages": len(pages),
            "criteria": len(matrix_rows),
            "findings": len(findings)
            + rgaa_qualification_count
            + dsfr_qualification_count,
            "legacy_findings": len(findings),
            "rgaa_qualifications": rgaa_qualification_count,
            "dsfr_qualifications": dsfr_qualification_count,
            "tickets": len(list((root / "tickets").glob("*.md")))
            if (root / "tickets").is_dir()
            else 0,
        },
    }
    if write_result:
        write_json(root / "VALIDATION.json", result)
    return errors, warnings


def report_command(args: argparse.Namespace) -> int:
    path = Path(args.campaign).resolve()
    generate_reports(path)
    print(f"[OK] Rapports générés dans {path.parent}")
    return 0


def validate_command(args: argparse.Namespace) -> int:
    path = Path(args.campaign).resolve()
    errors, warnings = validate_campaign(path, write_result=True)
    for warning in warnings:
        print(f"[WARN] {warning}")
    for error in errors:
        print(f"[FAIL] {error}", file=sys.stderr)
    print(
        f"[{'FAIL' if errors else 'OK'}] Validation : {len(errors)} erreur(s), {len(warnings)} avertissement(s)"
    )
    return 1 if errors else 0


def replan_command(args: argparse.Namespace) -> int:
    path = Path(args.campaign).resolve()
    root = path.parent
    with campaign_lock(root):
        state = load_state(root)
        history = root / ".creator" / "history"
        history.mkdir(parents=True, exist_ok=True)
        write_json(
            history / f"state-{dt.datetime.now().strftime('%Y%m%d-%H%M%S')}.json", state
        )
        config = read_yaml(path)
        state = {
            "schema_version": 1,
            "created_at": state.get("created_at", now()),
            "updated_at": now(),
            "campaign_digest": campaign_digest(path),
            "phases": {},
            "pages": {p["id"]: {} for p in config.get("sample", [])},
            "replanned_at": now(),
        }
        save_state(root, state)
    print(
        "[OK] Plan invalidé. Les preuves brutes existantes sont conservées ; la prochaine exécution utilisera de nouvelles tentatives."
    )
    return 0


def status_command(args: argparse.Namespace) -> int:
    path = Path(args.campaign).resolve()
    state = load_state(path.parent)
    if args.json:
        print(json.dumps(state, ensure_ascii=False, indent=2))
        return 0
    print(f"Campagne : {path.parent}")
    for phase in PHASES:
        value = state.get("phases", {}).get(phase, {}).get("status", "NON LANCÉ")
        print(f"{phase:<10} {value}")
    return 0


def parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="audit-rgaa-creator",
        description="Créer et piloter une campagne RGAA 4.1.2 reproductible",
    )
    sub = p.add_subparsers(dest="command", required=True)
    init = sub.add_parser("init", help="Créer une campagne et ses contrats")
    init.add_argument("target")
    init.add_argument("--output")
    init.add_argument("--name")
    init.add_argument("--page", action="append", help="URL::Nom::type")
    init.add_argument("--ay11-root")
    init.add_argument("--skills-root", action="append")
    init.add_argument("--allow-inside-kit", action="store_true", help=argparse.SUPPRESS)
    init.set_defaults(func=init_campaign)
    sample = sub.add_parser(
        "sample", help="Proposer un échantillon depuis les liens de la cible"
    )
    sample.add_argument("campaign")
    sample.add_argument("--max-pages", type=int, default=10)
    sample.add_argument("--timeout", type=int, default=20)
    sample.set_defaults(func=sample_campaign)
    run = sub.add_parser("run", help="Exécuter les phases automatisées")
    run.add_argument("campaign")
    run.add_argument("--only", help="Liste de phases séparées par des virgules")
    run.add_argument("--dry-run", action="store_true")
    run.add_argument("--resume", action="store_true")
    run.add_argument("--strict-ay11", action="store_true")
    run.set_defaults(func=run_campaign)
    resume = sub.add_parser("resume", help="Reprendre en ignorant les phases OK")
    resume.add_argument("campaign")
    resume.add_argument("--only")
    resume.add_argument("--dry-run", action="store_true")
    resume.add_argument("--strict-ay11", action="store_true")
    resume.set_defaults(func=run_campaign, resume=True)
    report = sub.add_parser("report", help="Régénérer matrice, rapports et tickets")
    report.add_argument("campaign")
    report.set_defaults(func=report_command)
    validate = sub.add_parser("validate", help="Vérifier la cohérence de la campagne")
    validate.add_argument("campaign")
    validate.set_defaults(func=validate_command)
    replan = sub.add_parser(
        "replan", help="Accepter une configuration modifiée et invalider le plan"
    )
    replan.add_argument("campaign")
    replan.set_defaults(func=replan_command)
    status = sub.add_parser("status", help="Afficher l’état des phases")
    status.add_argument("campaign")
    status.add_argument("--json", action="store_true")
    status.set_defaults(func=status_command)
    return p


def main() -> int:
    args = parser().parse_args()
    if not hasattr(args, "resume"):
        args.resume = False
    if not hasattr(args, "strict_ay11"):
        args.strict_ay11 = False
    return int(args.func(args))


if __name__ == "__main__":
    raise SystemExit(main())
