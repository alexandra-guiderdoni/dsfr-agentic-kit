"""Qualification humaine des signaux DSFR à confirmer, par fiche de revue Markdown.

La fiche est écrite par le script, cochée par le relecteur, puis relue.
Une seule case par groupe. Les archives ne sont jamais modifiées.
"""

from __future__ import annotations

import re

from .collect import Collection, Group, VERSION_COMPONENT

DECISIONS = ("ECART_CONFIRME", "AUCUN_ECART_OBSERVE", "NON_APPLICABLE")
PENDING = {"A_CONFIRMER", "REFERENCE_INDISPONIBLE", "CONTRADICTION"}
HEADING_RE = re.compile(r"^## (\S+)\s*$", re.MULTILINE)
CHECKED_RE = re.compile(r"^- \[[xX]\] (ECART_CONFIRME|AUCUN_ECART_OBSERVE|NON_APPLICABLE)\s*$", re.MULTILINE)
COMMENT_RE = re.compile(r"^Commentaire de revue :\s*\n(.*?)(?=\n## |\Z)", re.MULTILINE | re.DOTALL)


class ReviewSheetError(ValueError):
    """Fiche de revue illisible ou ambiguë."""


def pending_groups(collection: Collection) -> list[Group]:
    return [g for g in collection.groups.values()
            if g.component != VERSION_COMPONENT and g.final_status is None and g.status in PENDING]


def detect_contradictions(collection: Collection) -> list[Group]:
    return [g for g in collection.groups.values() if g.final_status is None and g.status == "CONTRADICTION"]


def render_review_sheet(collection: Collection, groups: list[Group], hints: dict[str, list[str]] | None = None) -> str:
    lines = [
        "# Revue des signaux DSFR à qualifier",
        "",
        f"Observé DSFR {', '.join(collection.observed_versions) or 'inconnu'}, règles écrites pour {collection.target_version or 'inconnu'}.",
        "",
        "Consignes : pour chaque groupe, cocher une seule case `[x]`. Ne pas modifier les titres `## `.",
        "Un groupe regroupe toutes les pages où la même règle échoue sur le même sélecteur.",
        "Les groupes marqués CONTRADICTION portent des qualifications différentes selon la page : la décision ici les unifie.",
        "",
    ]
    for group in sorted(groups, key=lambda g: (g.component, g.rule_id, g.selector)):
        statuses = ", ".join(f"{status} x{count}" for status, count in sorted(group.statuses.items()))
        lines += [
            f"## {group.group_id}",
            "",
            f"- Composant : {group.component}",
            f"- Règle : {group.rule_id} - {group.title}",
            f"- Sévérité : {group.severity}",
            f"- Pages : {', '.join(group.pages)} ({len(group.occurrences)} occurrence(s))",
            f"- Sélecteur feuille : `{group.selector}`",
            f"- Statuts relevés dans les archives : {statuses}",
            f"- Statut actuel : {group.status}",
            f"- Attendu : {group.expected}",
            f"- Observé : {group.observed}",
            "- Conditions en échec :",
            *[f"  - {condition}" for condition in group.failed_conditions],
        ]
        if group.comments:
            lines += ["- Commentaires déjà posés dans les archives :", *[f"  - {comment}" for comment in group.comments]]
        for hint in (hints or {}).get(group.group_id, []):
            lines.append(f"- Repère : {hint}")
        lines += [
            f"- Source de la règle : {group.source}",
            "",
            "HTML observé (DOM rendu) :",
            "",
            "```html",
            group.observed_html.strip(),
            "```",
            "",
            "Structure attendue par la règle :",
            "",
            "```html",
            group.expected_html.strip(),
            "```",
            "",
            "Décision (cocher une seule case) :",
            "",
            *[f"- [ ] {decision}" for decision in DECISIONS],
            "",
            "Commentaire de revue :",
            "",
            "",
        ]
    return "\n".join(lines)


def parse_review_sheet(text: str) -> dict[str, str]:
    headings = list(HEADING_RE.finditer(text))
    overrides: dict[str, str] = {}
    for index, heading in enumerate(headings):
        end = headings[index + 1].start() if index + 1 < len(headings) else len(text)
        section = text[heading.end():end]
        checked = CHECKED_RE.findall(section)
        if len(checked) > 1:
            raise ReviewSheetError(f"{heading.group(1)} : plusieurs cases cochées ({', '.join(checked)})")
        if checked:
            overrides[heading.group(1)] = checked[0]
    return overrides


def parse_review_comments(text: str) -> dict[str, str]:
    headings = list(HEADING_RE.finditer(text))
    comments: dict[str, str] = {}
    for index, heading in enumerate(headings):
        end = headings[index + 1].start() if index + 1 < len(headings) else len(text)
        match = COMMENT_RE.search(text[heading.end():end])
        if match and match.group(1).strip():
            comments[heading.group(1)] = match.group(1).strip()
    return comments


def apply_overrides(collection: Collection, overrides: dict[str, str], comments: dict[str, str] | None = None) -> None:
    for group_id, status in overrides.items():
        if status not in DECISIONS:
            raise ReviewSheetError(f"{group_id} : décision inconnue {status}")
        group = collection.groups.get(group_id)
        if group is None:
            raise ReviewSheetError(f"{group_id} : groupe absent des archives lues")
        group.final_status = status
        if comments and comments.get(group_id):
            group.comments.append(f"Revue : {comments[group_id]}")
