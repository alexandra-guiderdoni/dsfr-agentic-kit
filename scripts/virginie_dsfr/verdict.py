"""Verdict par composant, rapport et manifeste.

Conforme : aucun écart confirmé, aucun signal en attente, au moins une règle
exécutée. Le libellé complet est toujours « Conforme aux N règles exécutées ».
Non conforme : au moins un écart confirmé d'intégration.
Non vérifié : aucune règle, ou signal à confirmer non arbitré, ou référence absente.
"""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass, field

from . import gaps
from .collect import Collection, Group, VERSION_COMPONENT

SEVERITY_ORDER = {"Bloquant": 3, "Majeur": 2, "Mineur": 1, "": 0}
LABELS = {"CONFORME": "Conforme", "NON_CONFORME": "Non conforme", "NON_VERIFIE": "Non vérifié"}
ORDER = {"NON_CONFORME": 0, "NON_VERIFIE": 1, "CONFORME": 2}
PENDING = {"A_CONFIRMER", "REFERENCE_INDISPONIBLE", "CONTRADICTION"}
WARNING = (
    "« Conforme » signifie ici : aucun écart constaté sur les règles exécutées par l'audit automatique, "
    "contre la version DSFR {observed} chargée par le site. Les états non exercés sont listés par composant. "
    "Aucun pourcentage de conformité DSFR n'est calculé ; ce document ne vaut pas validation de la marque de l'État."
)


def plural(count: int, singular: str, plural_form: str) -> str:
    return f"{count} {singular}" if count == 1 else f"{count} {plural_form}"


@dataclass
class Verdict:
    component: str
    status: str = "NON_VERIFIE"
    reasons: list[str] = field(default_factory=list)
    rules_executed: list[str] = field(default_factory=list)
    confirmed_groups: list[Group] = field(default_factory=list)
    pending_groups: list[Group] = field(default_factory=list)
    migration_groups: list[Group] = field(default_factory=list)
    clean_groups: list[Group] = field(default_factory=list)
    max_severity: str = ""

    @property
    def label(self) -> str:
        return LABELS[self.status]


def component_verdicts(collection: Collection, kinds: dict[str, str]) -> dict[str, Verdict]:
    verdicts: dict[str, Verdict] = {}
    for name, summary in collection.components.items():
        if name == VERSION_COMPONENT:
            continue
        groups = collection.groups_for(name)
        verdict = Verdict(name)
        for group in groups:
            status = group.status
            if status == "ECART_CONFIRME":
                target = verdict.migration_groups if kinds.get(group.group_id, "integration") == "migration" else verdict.confirmed_groups
                target.append(group)
            elif status in PENDING:
                verdict.pending_groups.append(group)
            else:
                verdict.clean_groups.append(group)
        verdict.rules_executed = sorted(summary.rules_executed | {g.rule_id for g in groups})
        count = len(verdict.rules_executed)
        if verdict.confirmed_groups:
            verdict.status = "NON_CONFORME"
            verdict.max_severity = max((g.severity for g in verdict.confirmed_groups), key=lambda s: SEVERITY_ORDER.get(s, 0))
            rules = ", ".join(sorted({g.rule_id for g in verdict.confirmed_groups}))
            verdict.reasons.append(f"{plural(len(verdict.confirmed_groups), 'écart confirmé', 'écarts confirmés')} sur {plural(count, 'règle exécutée', 'règles exécutées')} : {rules}.")
        elif verdict.pending_groups:
            verdict.reasons.append(f"{plural(len(verdict.pending_groups), 'signal à confirmer non arbitré', 'signaux à confirmer non arbitrés')} : aucun verdict possible.")
        elif count == 0:
            verdict.reasons.append(
                f"Aucune règle du harnais ne couvre ce composant ; détecté {summary.count} fois sur {len(summary.pages)} page(s).")
        else:
            verdict.status = "CONFORME"
            executed = "la règle exécutée" if count == 1 else f"les {count} règles exécutées"
            verdict.reasons.append(f"Aucun écart sur {executed} contre DSFR {', '.join(collection.observed_versions)}.")
        if verdict.migration_groups:
            verdict.reasons.append(
                f"{plural(len(verdict.migration_groups), 'écart relève', 'écarts relèvent')} de la migration vers {collection.target_version}, hors verdict.")
        verdicts[name] = verdict
    return verdicts


@dataclass
class Report:
    collection: Collection
    verdicts: dict[str, Verdict]
    components: list[str]
    migration_details: dict[str, list[str]]
    example_diffs: dict[str, dict[str, list[str]]]
    expected_absent: dict[str, list[str]]
    uncovered: list[str]
    not_verified: list[str]
    delivery_date: str
    audit_date: str
    version_group: Group | None

    @property
    def warning(self) -> str:
        return WARNING.format(observed=", ".join(self.collection.observed_versions) or "inconnue")

    @property
    def pages(self) -> list[dict]:
        return [{"id": p.id, "name": p.name, "url": p.url, "type": p.type} for p in self.collection.pages]


LOCAL_SOURCE_LIMIT = "intégration exacte contre une source locale"
LOCAL_SOURCE_NOTE = ("structure complète des composants en DSFR {observed} : les classes attendues ont été vérifiées contre le paquet "
                     "officiel {observed}, les exemples officiels ont été relus lors de la qualification, mais les règles n'ont pas été rejouées contre {observed}")


def build_report(collection: Collection, verdicts: dict[str, Verdict], migration_details: dict[str, list[str]],
                 delivery_date: str, example_diffs: dict[str, dict[str, list[str]]] | None = None,
                 reference_available: bool = False) -> Report:
    def sort_key(name: str):
        verdict = verdicts[name]
        return (ORDER[verdict.status], -SEVERITY_ORDER.get(verdict.max_severity, 0), name)

    components = sorted(verdicts, key=sort_key)
    version_groups = collection.groups_for(VERSION_COMPONENT)
    audit_dates = sorted({p.audited_at[:10] for p in collection.pages if p.audited_at})
    return Report(
        collection=collection, verdicts=verdicts, components=components, migration_details=migration_details,
        example_diffs=example_diffs or {}, expected_absent=gaps.expected_absent(collection),
        uncovered=gaps.uncovered_components(collection), not_verified=_not_verified(collection, reference_available),
        delivery_date=delivery_date, audit_date=", ".join(audit_dates), version_group=version_groups[0] if version_groups else None,
    )


def _not_verified(collection: Collection, reference_available: bool) -> list[str]:
    items = gaps.not_verified_union(collection)
    if not reference_available:
        return items
    observed = ", ".join(collection.observed_versions)
    kept = [item for item in items if LOCAL_SOURCE_LIMIT not in item]
    return kept + [LOCAL_SOURCE_NOTE.format(observed=observed)]


def build_manifest(report: Report) -> dict:
    counts = Counter(report.verdicts[name].status for name in report.components)
    return {
        "schema_version": 1,
        "title": "Synthèse DSFR par composant",
        "delivery_date": report.delivery_date,
        "audit_date": report.audit_date,
        "pages": [p["id"] for p in report.pages],
        "observed_versions": report.collection.observed_versions,
        "target_version": report.collection.target_version,
        "component_count": len(report.components),
        "verdict_counts": {status: counts.get(status, 0) for status in ORDER},
        "claim": report.warning,
        "components": [
            {
                "name": name,
                "verdict": report.verdicts[name].status,
                "pages": report.collection.components[name].pages,
                "rules_executed": report.verdicts[name].rules_executed,
                "confirmed": [g.group_id for g in report.verdicts[name].confirmed_groups],
                "pending": [g.group_id for g in report.verdicts[name].pending_groups],
                "migration": [g.group_id for g in report.verdicts[name].migration_groups],
            }
            for name in report.components
        ],
        "expected_absent": report.expected_absent,
        "uncovered_components": report.uncovered,
    }
