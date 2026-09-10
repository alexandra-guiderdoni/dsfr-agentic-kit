"""Lecture des archives par page et dédoublonnage des écarts DSFR par composant.

Sources : dsfr/pages/Pxx.json (inventaire, versions) et
dsfr/ECARTS-COMPOSANTS.json (différences qualifiées) de chaque archive.
Les archives sont lues, jamais modifiées.
"""

from __future__ import annotations

import hashlib
import json
import re
from collections import Counter
from dataclasses import dataclass, field
from pathlib import Path

NTH_RE = re.compile(r":nth-(?:of-type|child)\(\d+\)")
VOLATILE_CLASS_RE = re.compile(
    r"\.(?:eu-cookie-compliance-|path-|node--|page-node-|toolbar-)[\w-]*"
)
WHITESPACE_RE = re.compile(r"\s+")
COMPONENT_ALIASES = {
    "skiplinks": "skiplink",
    "html": "transverse",
    "idref": "transverse",
    "state": "transverse",
}
TRANSVERSE = "transverse"
VERSION_COMPONENT = "version"
RULE_CATALOG_PATH = (
    Path(__file__).resolve().parents[2]
    / ".claude/skills/audit-dsfr-complet/rules/dsfr-rules.json"
)


def normalize_selector(selector: str) -> str:
    """Retire les positions nth-* et les classes d'état Drupal, volatiles d'une page à l'autre."""
    segments = []
    for raw in selector.split(">"):
        segment = VOLATILE_CLASS_RE.sub("", NTH_RE.sub("", raw.strip()))
        if segment:
            segments.append(segment)
    return " > ".join(segments)


def leaf_selector(selector: str) -> str:
    normalized = normalize_selector(selector)
    return normalized.rsplit(" > ", 1)[-1] if normalized else ""


def component_name(raw: str) -> str:
    return COMPONENT_ALIASES.get(raw, raw)


def group_key(component: str, rule_id: str, selector: str) -> str:
    digest = hashlib.sha1(selector.encode("utf-8")).hexdigest()[:8]
    return f"{component}--{rule_id}--{digest}"


def dom_variant_key(observed_html: str) -> str:
    """Retourne une empreinte stable de la variante DOM observée."""
    normalized = WHITESPACE_RE.sub(" ", str(observed_html or "")).strip()
    digest = hashlib.sha1(normalized.encode("utf-8")).hexdigest()[:10]
    return f"DOM-{digest}" if normalized else "DOM-INCONNU"


def occurrence_state(diff: dict) -> str:
    """Récupère l’état exercé, avec un état explicite pour les archives anciennes."""
    for key in ("state", "dom_state", "interaction_state", "variant_state"):
        value = diff.get(key)
        if value not in (None, ""):
            return str(value)
    return "REPOS"


def contradiction_buckets(group: Group) -> list[dict]:
    """Regroupe les occurrences par page, état et variante DOM."""
    buckets: dict[tuple[str, str, str], dict] = {}
    for occurrence in group.occurrences:
        key = (
            str(occurrence.get("page", "")),
            str(occurrence.get("state", "REPOS")),
            str(occurrence.get("dom_variant", "DOM-INCONNU")),
        )
        bucket = buckets.setdefault(
            key,
            {
                "page": key[0],
                "state": key[1],
                "dom_variant": key[2],
                "statuses": Counter(),
                "occurrences": [],
            },
        )
        bucket["statuses"][str(occurrence.get("status", "A_CONFIRMER"))] += 1
        bucket["occurrences"].append(occurrence)
    return sorted(
        buckets.values(),
        key=lambda item: (item["page"], item["state"], item["dom_variant"]),
    )


@dataclass
class PageData:
    id: str
    name: str
    url: str
    type: str
    audited_at: str
    observed_versions: list[str]
    target_version: str
    inventory: list[dict]
    not_verified: list[str]
    differences: list[dict]
    rule_catalog: dict | None
    archive: Path


def load_page(archive: Path, page_id: str | None = None) -> PageData:
    pages_dir = archive / "dsfr" / "pages"
    candidates = (
        sorted(pages_dir.glob("P*.json"))
        if page_id is None
        else [pages_dir / f"{page_id}.json"]
    )
    if not candidates or not candidates[0].is_file():
        raise FileNotFoundError(f"Aucune page DSFR lisible dans {pages_dir}")
    doc = json.loads(candidates[0].read_text(encoding="utf-8"))
    page = doc["page"]
    ecarts = json.loads(
        (archive / "dsfr" / "ECARTS-COMPOSANTS.json").read_text(encoding="utf-8")
    )
    differences = [
        d
        for d in ecarts.get("differences", [])
        if d.get("page", page["id"]) == page["id"]
    ]
    version = doc.get("version") or {}
    return PageData(
        id=page["id"],
        name=page.get("name", page["id"]),
        url=page.get("url", ""),
        type=page.get("type", ""),
        audited_at=doc.get("audited_at", ""),
        observed_versions=list(
            version.get("observed") or doc.get("detected_versions") or []
        ),
        target_version=str(version.get("target") or doc.get("reference_version") or ""),
        inventory=list(doc.get("inventory", [])),
        not_verified=list(doc.get("not_verified", [])),
        differences=differences,
        rule_catalog=doc.get("rule_catalog") or ecarts.get("rule_catalog"),
        archive=archive,
    )


@dataclass
class ComponentSummary:
    name: str
    selector: str = ""
    source: str = ""
    count: int = 0
    pages: list[str] = field(default_factory=list)
    rules_executed: set[str] = field(default_factory=set)
    statuses: dict[str, str] = field(default_factory=dict)


@dataclass
class Group:
    """Un écart dédoublonné par composant, règle et sélecteur feuille normalisé."""

    component: str
    rule_id: str
    selector: str
    severity: str
    title: str
    expected: str
    observed: str
    expected_html: str
    observed_html: str
    source: str
    recommendation: str
    verification: str
    failed_conditions: list[str] = field(default_factory=list)
    kinds_observed: set[str] = field(default_factory=set)
    pages: list[str] = field(default_factory=list)
    occurrences: list[dict] = field(default_factory=list)
    statuses: Counter = field(default_factory=Counter)
    comments: list[str] = field(default_factory=list)
    final_status: str | None = None

    @property
    def group_id(self) -> str:
        return group_key(self.component, self.rule_id, self.selector)

    @property
    def status(self) -> str:
        if self.final_status:
            return self.final_status
        distinct = set(self.statuses)
        return next(iter(distinct)) if len(distinct) == 1 else "CONTRADICTION"


@dataclass
class Collection:
    pages: list[PageData]
    components: dict[str, ComponentSummary]
    groups: dict[str, Group]

    @property
    def observed_versions(self) -> list[str]:
        return sorted({v for p in self.pages for v in p.observed_versions})

    @property
    def target_version(self) -> str:
        return next((p.target_version for p in self.pages if p.target_version), "")

    def groups_for(self, component: str) -> list[Group]:
        return [g for g in self.groups.values() if g.component == component]

    @property
    def catalog_status(self) -> dict:
        raw = RULE_CATALOG_PATH.read_bytes()
        current = {
            "path": "audit-dsfr-complet/rules/dsfr-rules.json",
            "sha256": hashlib.sha256(raw).hexdigest(),
        }
        observed = [
            p.rule_catalog.get("sha256")
            for p in self.pages
            if p.rule_catalog and p.rule_catalog.get("sha256")
        ]
        missing = [
            p.id
            for p in self.pages
            if not p.rule_catalog or not p.rule_catalog.get("sha256")
        ]
        stale = [
            p.id
            for p in self.pages
            if p.rule_catalog and p.rule_catalog.get("sha256") != current["sha256"]
        ]
        if missing:
            status = "EMPREINTE_ABSENTE"
            message = "Les archives ne permettent pas toutes de prouver l’empreinte du catalogue de règles utilisé."
        elif stale:
            status = "CATALOGUE_OBSOLETE"
            message = f"Les archives {', '.join(stale)} ont été produites avec une ancienne version du catalogue de règles."
        elif len(set(observed)) > 1:
            status = "CATALOGUES_MULTIPLES"
            message = (
                "Les archives mélangent plusieurs empreintes de catalogue de règles."
            )
        else:
            status = "A_JOUR"
            message = (
                "Les archives portent l’empreinte courante du catalogue de règles."
            )
        return {
            "status": status,
            "message": message,
            "current": current,
            "observed": sorted(set(observed)),
            "missing_pages": missing,
            "stale_pages": stale,
        }


def collect(pages: list[PageData]) -> Collection:
    components: dict[str, ComponentSummary] = {}
    groups: dict[str, Group] = {}
    for page in sorted(pages, key=lambda p: p.id):
        for item in page.inventory:
            name = component_name(item["name"])
            summary = components.setdefault(
                name,
                ComponentSummary(
                    name, item.get("selector", ""), item.get("source", "")
                ),
            )
            summary.count += int(item.get("count", 0))
            if page.id not in summary.pages:
                summary.pages.append(page.id)
            summary.rules_executed.update(item.get("rules_executed", []))
            summary.statuses[page.id] = item.get("status", "")
        for diff in page.differences:
            _merge_difference(groups, components, page, diff)
    return Collection(pages, components, groups)


def _merge_difference(
    groups: dict[str, Group],
    components: dict[str, ComponentSummary],
    page: PageData,
    diff: dict,
) -> None:
    name = component_name(diff["component"])
    selector = leaf_selector(diff.get("selector", "")) or diff["rule_id"]
    key = group_key(name, diff["rule_id"], selector)
    group = groups.get(key)
    if group is None:
        group = Group(
            name,
            diff["rule_id"],
            selector,
            diff.get("severity", ""),
            diff.get("title", ""),
            diff.get("expected", ""),
            diff.get("observed", ""),
            diff.get("expected_html", ""),
            diff.get("observed_html", ""),
            diff.get("source", ""),
            diff.get("recommendation", ""),
            diff.get("verification", ""),
        )
        groups[key] = group
    for condition in diff.get("failed_conditions", []):
        if condition not in group.failed_conditions:
            group.failed_conditions.append(condition)
    group.kinds_observed.add(diff.get("kind", ""))
    if page.id not in group.pages:
        group.pages.append(page.id)
    status = diff.get("qualification_status") or diff.get("status") or "A_CONFIRMER"
    group.statuses[status] += 1
    group.occurrences.append(
        {
            "page": page.id,
            "id": diff.get("id", ""),
            "selector": diff.get("selector", ""),
            "status": status,
            "state": occurrence_state(diff),
            "dom_variant": str(
                diff.get("dom_variant")
                or diff.get("variant_dom")
                or dom_variant_key(diff.get("observed_html", ""))
            ),
            "kind": diff.get("kind", "integration"),
        }
    )
    comment = (diff.get("qualification") or {}).get("comment")
    if comment and comment not in group.comments:
        group.comments.append(comment)
    summary = components.setdefault(name, ComponentSummary(name, ""))
    if name in (TRANSVERSE, VERSION_COMPONENT) and page.id not in summary.pages:
        summary.pages.append(page.id)
