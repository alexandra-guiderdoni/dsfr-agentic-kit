"""Rendu Markdown : synthèse tout-en-un et fiche par composant. Listes, pas de tableaux."""

from __future__ import annotations

from . import gaps
from .collect import Group, contradiction_buckets
from .labels import STATUS_LABELS, VERDICT_LABELS, component_label, page_report_href
from .verdict import Report, Verdict


def _title(report: Report, name: str) -> str:
    selector = report.collection.components[name].selector
    return (
        f"{component_label(name)} (`{selector}`)" if selector else component_label(name)
    )


def _action(verdict: Verdict) -> str:
    if verdict.confirmed_groups:
        return (
            verdict.confirmed_groups[0].recommendation
            or verdict.confirmed_groups[0].title
        )
    return verdict.reasons[0] if verdict.reasons else ""


def _group_block(group: Group, report: Report, heading: str) -> list[str]:
    lines = [
        f"### {group.title} ({group.rule_id}, {group.severity or 'sévérité non renseignée'})",
        "",
        f"- Pages : {', '.join(group.pages)} ({len(group.occurrences)} occurrence(s))",
        f"- Sélecteur : `{group.selector}`",
        f"- Attendu : {group.expected}",
        f"- Observé : {group.observed}",
        "- Ce qui manque ou diverge :",
        *[f"  - {c}" for c in group.failed_conditions],
        "- Où le retrouver dans les rapports par page :",
        *[f"  - {o['page']} : constat `{o['id']}`" for o in group.occurrences[:12]],
    ]
    if len(group.occurrences) > 12:
        lines.append(f"  - et {len(group.occurrences) - 12} autre(s) occurrence(s)")
    if group.status == "CONTRADICTION":
        lines += [
            "",
            "Contradiction regroupée par page, état et variante DOM :",
            "",
            "| Page | État | Variante DOM | Statuts | Occurrences |",
            "|---|---|---|---|---:|",
            *[
                f"| {bucket['page']} | {bucket['state']} | `{bucket['dom_variant']}` | {', '.join(f'{status} x{count}' for status, count in sorted(bucket['statuses'].items()))} | {len(bucket['occurrences'])} |"
                for bucket in contradiction_buckets(group)
            ],
        ]
    lines += [
        "",
        "Code observé (DOM rendu) :",
        "",
        "```html",
        group.observed_html.strip(),
        "```",
        "",
        "Structure attendue :",
        "",
        "```html",
        group.expected_html.strip(),
        "```",
        "",
        f"- Correctif : {group.recommendation}",
        f"- Vérification après correction : {group.verification}",
        f"- Source de la règle : `{group.source}`",
    ]
    missing = report.migration_details.get(group.group_id)
    if missing:
        lines.append(
            f"- Classes attendues absentes de DSFR {', '.join(report.collection.observed_versions)} : {', '.join(missing)}"
        )
    if group.comments:
        lines += [
            "- Commentaires de qualification :",
            *[f"  - {c}" for c in group.comments],
        ]
    return [f"## {heading}", ""] + lines + [""] if heading else lines + [""]


def render_fiche(report: Report, name: str) -> str:
    verdict = report.verdicts[name]
    summary = report.collection.components[name]
    lines = [
        f"# {component_label(name)} - {verdict.label}",
        "",
        f"- Sélecteur : `{summary.selector}`"
        if summary.selector
        else "- Sélecteur : règles globales au document",
        f"- Verdict : **{verdict.label}**"
        + (
            f" (sévérité maximale {verdict.max_severity})"
            if verdict.max_severity
            else ""
        ),
        f"- Pages concernées : {', '.join(summary.pages)} ({summary.count} instance(s) détectée(s))",
        f"- Règles exécutées : {', '.join(verdict.rules_executed) or 'aucune'}",
        "- Rapports détaillés par page : "
        + ", ".join(f"[{p}]({page_report_href(p, 2)})" for p in summary.pages),
        "",
        "## Pourquoi",
        "",
        *[f"- {r}" for r in verdict.reasons],
        "",
    ]
    if verdict.confirmed_groups:
        lines += ["## Écarts confirmés", ""]
        for group in verdict.confirmed_groups:
            lines += _group_block(group, report, "")
    if verdict.pending_groups:
        lines += [
            "## Signaux à confirmer",
            "",
            "Ces signaux n'ont pas été arbitrés : ils empêchent tout verdict définitif.",
            "",
        ]
        for group in verdict.pending_groups:
            lines += [
                f"- {group.title} ({group.rule_id}) : {STATUS_LABELS.get(group.status, group.status)}, pages {', '.join(group.pages)}"
            ]
        contradictions = [
            group for group in verdict.pending_groups if group.status == "CONTRADICTION"
        ]
        for group in contradictions:
            lines += [""] + _group_block(group, report, "Détail de la contradiction")
        lines.append("")
    if verdict.migration_groups:
        lines += [
            f"## Ce qui change en DSFR {report.collection.target_version}",
            "",
            "Ces écarts n'existent que par rapport à la version cible : ils sont à traiter dans le plan de migration, pas comme défaut d'intégration.",
            "",
        ]
        for group in verdict.migration_groups:
            lines += _group_block(group, report, "")
    diff = report.example_diffs.get(name)
    if diff and (diff["added"] or diff["removed"]):
        lines += [
            f"Exemple officiel du composant, de {', '.join(report.collection.observed_versions)} vers {report.collection.target_version} :",
            f"- classes ajoutées : {', '.join(diff['added']) or 'aucune'}",
            f"- classes retirées : {', '.join(diff['removed']) or 'aucune'}",
            "",
        ]
    absent_pages = [p for p, names in report.expected_absent.items() if name in names]
    lines += [
        "## Ce qui manque",
        "",
        "- Dans le composant présent : "
        + (
            f"{sum(len(g.failed_conditions) for g in verdict.confirmed_groups)} condition(s) en échec, détaillées ci-dessus"
            if verdict.confirmed_groups
            else "rien sur les règles exécutées"
        ),
        "- Pages où le composant est attendu mais absent : "
        + (
            ", ".join(absent_pages)
            if absent_pages
            else "aucune dans la baseline retenue"
        ),
        "- Couverture de l'audit : "
        + (
            "aucune règle du harnais ne couvre ce composant"
            if name in report.uncovered
            else f"{len(verdict.rules_executed)} règle(s)"
        ),
        f"- États non exercés : {', '.join(gaps.unexercised_states(name))}",
        "",
        f"> {gaps.STATES_NOTE}",
        "",
    ]
    return "\n".join(lines)


def render_synthese(report: Report) -> str:
    coll = report.collection
    lines = [
        "# Synthèse DSFR par composant - portail Douane",
        "",
        f"Synthèse du {report.delivery_date}, établie à partir de l'audit du {report.audit_date} sur {len(report.pages)} pages de préproduction.",
        "",
        "## Lecture du verdict",
        "",
        f"> {report.warning}",
        "",
        "- Conforme : aucun écart sur les règles exécutées, aucun signal en attente.",
        "- Non conforme : au moins un écart confirmé après revue humaine.",
        "- Non vérifié : aucune règle disponible, ou signal non arbitré, ou référence absente. La raison est indiquée.",
        "",
        "## Échantillon",
        "",
        *[f"- {p['id']} - {p['name']} : {p['url']}" for p in report.pages],
        "",
        "## Versions DSFR",
        "",
        f"- Version chargée par le site : {', '.join(coll.observed_versions) or 'inconnue'}",
        f"- Version de référence des règles : {coll.target_version}",
        f"- Un écart compte dans le verdict seulement si les classes attendues existent en {', '.join(coll.observed_versions)} ; sinon il est classé migration.",
        "",
        "## Tableau de bord",
        "",
    ]
    for status in ("NON_CONFORME", "NON_VERIFIE", "CONFORME"):
        names = [n for n in report.components if report.verdicts[n].status == status]
        lines += [f"### {VERDICT_LABELS[status]} ({len(names)})", ""]
        for name in names:
            verdict = report.verdicts[name]
            summary = coll.components[name]
            sev = f", sévérité {verdict.max_severity}" if verdict.max_severity else ""
            lines.append(
                f"- **{_title(report, name)}** : {verdict.label}{sev}, pages {', '.join(summary.pages)}. {_action(verdict)} Fiche : `markdown/{name}.md`."
            )
        lines.append("")
    lines += [
        "## Composants attendus mais absents",
        "",
        "Baseline : liens d'évitement, en-tête, pied de page et consentement sur toutes les pages ; fil d'Ariane hors accueil ; groupe de messages sur les formulaires. Une absence est signalée, pas qualifiée.",
        "",
    ]
    absent = [(p, names) for p, names in report.expected_absent.items() if names]
    lines += [
        f"- {p} : {', '.join(component_label(n) for n in names)}" for p, names in absent
    ] or ["- Aucune absence dans la baseline retenue."]
    lines += ["", "## Hors couverture de l'audit", ""]
    lines += [
        f"- {_title(report, n)} : détecté sur {', '.join(coll.components[n].pages)}, aucune règle du harnais."
        for n in report.uncovered
    ] or ["- Tous les composants détectés ont au moins une règle."]
    lines += [
        "",
        f"## Migration {', '.join(coll.observed_versions)} vers {coll.target_version}",
        "",
    ]
    migr = [
        (n, g) for n in report.components for g in report.verdicts[n].migration_groups
    ]
    lines += [
        f"- {component_label(n)} : {g.title} ({g.rule_id}), classes absentes en {', '.join(coll.observed_versions)} : {', '.join(report.migration_details.get(g.group_id, [])) or 'non déterminées'}."
        for n, g in migr
    ] or ["- Aucun écart classé migration."]
    if report.version_group:
        lines.append(
            f"- Ressources DSFR chargées : version {', '.join(coll.observed_versions)} sur {len(report.version_group.pages)} page(s) ; {report.version_group.recommendation}"
        )
    lines += [
        "",
        "## Limites",
        "",
        *[f"- Non vérifié par cet audit : {item}" for item in report.not_verified],
        f"- {gaps.STATES_NOTE}",
        "",
    ]
    return "\n".join(lines)


def render_couverture(report: Report, coverage: dict[str, list[str]]) -> str:
    return "\n".join(
        [
            "# Couverture du harnais DSFR (interne)",
            "",
            "Pour le backlog du kit, pas pour la livraison.",
            "",
            "## Composants détectés sans règle",
            "",
            *([f"- {n}" for n in coverage["detected_without_rule"]] or ["- aucun"]),
            "",
            "## Règles du catalogue sans composant détecté dans l'échantillon",
            "",
            *([f"- {n}" for n in coverage["rules_without_detection"]] or ["- aucune"]),
            "",
            "## Signaux restés à confirmer",
            "",
            *(
                [
                    f"- {n} : {g.rule_id}"
                    for n in report.components
                    for g in report.verdicts[n].pending_groups
                ]
                or ["- aucun"]
            ),
            "",
        ]
    )
