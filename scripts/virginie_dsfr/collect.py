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
VOLATILE_CLASS_RE = re.compile(r"\.(?:eu-cookie-compliance-|path-|node--|page-node-|toolbar-)[\w-]*")
COMPONENT_ALIASES = {"skiplinks": "skiplink", "html": "transverse", "idref": "transverse", "state": "transverse"}
TRANSVERSE = "transverse"
VERSION_COMPONENT = "version"


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
    archive: Path


def load_page(archive: Path, page_id: str | None = None) -> PageData:
    pages_dir = archive / "dsfr" / "pages"
    candidates = sorted(pages_dir.glob("P*.json")) if page_id is None else [pages_dir / f"{page_id}.json"]
    if not candidates or not candidates[0].is_file():
        raise FileNotFoundError(f"Aucune page DSFR lisible dans {pages_dir}")
    doc = json.loads(candidates[0].read_text(encoding="utf-8"))
    page = doc["page"]
    ecarts = json.loads((archive / "dsfr" / "ECARTS-COMPOSANTS.json").read_text(encoding="utf-8"))
    differences = [d for d in ecarts.get("differences", []) if d.get("page", page["id"]) == page["id"]]
    version = doc.get("version") or {}
    return PageData(
        id=page["id"],
        name=page.get("name", page["id"]),
        url=page.get("url", ""),
        type=page.get("type", ""),
        audited_at=doc.get("audited_at", ""),
        observed_versions=list(version.get("observed") or doc.get("detected_versions") or []),
        target_version=str(version.get("target") or doc.get("reference_version") or ""),
        inventory=list(doc.get("inventory", [])),
        not_verified=list(doc.get("not_verified", [])),
        differences=differences,
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
    """Un écart dédoublonné : même composant, même règle, même sélecteur feuille normalisé."""

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


def collect(pages: list[PageData]) -> Collection:
    components: dict[str, ComponentSummary] = {}
    groups: dict[str, Group] = {}
    for page in sorted(pages, key=lambda p: p.id):
        for item in page.inventory:
            name = component_name(item["name"])
            summary = components.setdefault(name, ComponentSummary(name, item.get("selector", ""), item.get("source", "")))
            summary.count += int(item.get("count", 0))
            if page.id not in summary.pages:
                summary.pages.append(page.id)
            summary.rules_executed.update(item.get("rules_executed", []))
            summary.statuses[page.id] = item.get("status", "")
        for diff in page.differences:
            _merge_difference(groups, components, page, diff)
    return Collection(pages, components, groups)


def _merge_difference(groups: dict[str, Group], components: dict[str, ComponentSummary], page: PageData, diff: dict) -> None:
    name = component_name(diff["component"])
    selector = leaf_selector(diff.get("selector", "")) or diff["rule_id"]
    key = group_key(name, diff["rule_id"], selector)
    group = groups.get(key)
    if group is None:
        group = Group(
            name, diff["rule_id"], selector, diff.get("severity", ""), diff.get("title", ""), diff.get("expected", ""),
            diff.get("observed", ""), diff.get("expected_html", ""), diff.get("observed_html", ""), diff.get("source", ""),
            diff.get("recommendation", ""), diff.get("verification", ""),
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
    group.occurrences.append({"page": page.id, "id": diff.get("id", ""), "selector": diff.get("selector", ""), "status": status})
    comment = (diff.get("qualification") or {}).get("comment")
    if comment and comment not in group.comments:
        group.comments.append(comment)
    summary = components.setdefault(name, ComponentSummary(name, ""))
    if name in (TRANSVERSE, VERSION_COMPONENT) and page.id not in summary.pages:
        summary.pages.append(page.id)
