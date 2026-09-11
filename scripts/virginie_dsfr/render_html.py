"""Rendu HTML autonome, thème DSFR depuis le CDN comme les rapports par page livrés.

Classes DSFR écrites à la main et contrôlées contre dist/dsfr.min.css à la
génération. Pas de builder dans cette passe : décision du 2026-09-09.
"""

from __future__ import annotations

import html
import re
import sys
from pathlib import Path

from . import gaps
from .collect import Group, contradiction_buckets
from .labels import STATUS_LABELS, component_label, page_report_href
from .verdict import Report, Verdict

BUILDER_DIR = (
    Path(__file__).resolve().parents[2] / ".claude/skills/dsfr-components/scripts"
)
if str(BUILDER_DIR) not in sys.path:
    sys.path.insert(0, str(BUILDER_DIR))
from generate_component import generate_table as dsfr_builder_table

CDN = "https://cdn.jsdelivr.net/npm/@gouvfr/dsfr@1.15.2/dist/"
CLASS_ATTR_RE = re.compile(r'class="([^"]*)"')
BADGES = {
    "NON_CONFORME": "fr-badge--error",
    "CONFORME": "fr-badge--success",
    "NON_VERIFIE": "fr-badge--info",
}
DISPLAY_BADGES = {
    **BADGES,
    "NON_COUVERT": "fr-badge--new",
    "A_QUALIFIER": "fr-badge--info",
    "CONTRADICTION": "fr-badge--error",
}
DISPLAY_LABELS = {
    "NON_COUVERT": "Non couvert",
    "A_QUALIFIER": "À qualifier",
    "CONTRADICTION": "Contradiction",
}
STYLE = """pre{overflow:auto;padding:1rem;background:#f6f6f6;white-space:pre-wrap;font-size:.875rem}main{min-height:60vh}
.dashboard-summary .fr-card{height:100%}
.dashboard-summary__count{margin:0;font-size:2rem;font-weight:700;line-height:1.2}"""


def dsfr_classes(text: str) -> list[str]:
    return sorted(
        {
            token
            for attr in CLASS_ATTR_RE.findall(text)
            for token in attr.split()
            if token.startswith("fr-")
        }
    )


def e(value: str) -> str:
    return html.escape(value or "", quote=True)


def display_status(name: str, verdict: Verdict, report: Report) -> str:
    if name in report.uncovered:
        return "NON_COUVERT"
    if any(group.status == "CONTRADICTION" for group in verdict.pending_groups):
        return "CONTRADICTION"
    if verdict.pending_groups:
        return "A_QUALIFIER"
    return verdict.status


def display_label(status: str, verdict: Verdict) -> str:
    return DISPLAY_LABELS.get(status, verdict.label)


def badge(verdict: Verdict, status: str | None = None) -> str:
    display = status or verdict.status
    return f'<p class="fr-badge {DISPLAY_BADGES[display]}">{e(display_label(display, verdict))}</p>'


def table_badge(verdict: Verdict, status: str | None = None) -> str:
    display = status or verdict.status
    return f'<span class="fr-badge {DISPLAY_BADGES[display]}">{e(display_label(display, verdict))}</span>'


def builder_table(caption: str, headers: list[str], rows_html: str) -> str:
    """Construit la structure du tableau avec le builder DSFR natif.

    Le builder fournit l'enveloppe officielle ; les lignes sont injectées
    après génération pour conserver les liens, badges et en-têtes de lignes
    propres au tableau de synthèse.
    """
    skeleton = dsfr_builder_table(
        caption=caption,
        headers=headers,
        rows=[[""] * len(headers)],
        bordered=True,
    )
    skeleton = skeleton.replace(
        'class="fr-table fr-table--bordered"',
        'class="fr-table fr-table--bordered fr-table--no-scroll"',
        1,
    )
    skeleton = skeleton.replace(
        "<table>",
        '<table id="tableau-verdicts" aria-describedby="tableau-verdicts-aide">',
        1,
    )
    thead = "".join(
        f'<th id="col-{name}" scope="col">{e(label)}</th>'
        for name, label in zip(
            ("composant", "verdict", "pages", "severite", "action"), headers
        )
    )
    skeleton = re.sub(
        r"<thead>.*?</thead>",
        f"<thead>\n                        <tr>{thead}</tr>\n                    </thead>",
        skeleton,
        count=1,
        flags=re.DOTALL,
    )
    skeleton = re.sub(
        r"<tbody>.*?</tbody>",
        f"<tbody>{rows_html}\n                    </tbody>",
        skeleton,
        count=1,
        flags=re.DOTALL,
    )
    return skeleton


def shell(
    title: str,
    description: str,
    body: str,
    back_href: str | None,
    back_label: str,
    report: Report,
    main_class: str = "fr-container",
) -> str:
    warning_container_open = (
        '<div class="fr-grid-row fr-grid-row--center"><div class="fr-col-12 fr-col-lg-10">'
        if main_class == "fr-container--fluid"
        else ""
    )
    warning_container_close = "</div></div>" if warning_container_open else ""
    back = (
        f'<p><a class="fr-link fr-icon-arrow-left-line fr-link--icon-left" href="{e(back_href)}">{e(back_label)}</a></p>'
        if back_href
        else ""
    )
    return f"""<!doctype html>
<html lang="fr" data-fr-scheme="system">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{e(title)}</title>
<meta name="description" content="{e(description)}">
<link rel="stylesheet" href="{CDN}dsfr.min.css">
<link rel="stylesheet" href="{CDN}utility/icons/icons.min.css">
<style>{STYLE}</style>
</head>
<body>
<div class="fr-skiplinks"><nav class="fr-container" role="navigation" aria-label="Accès rapide"><ul class="fr-skiplinks__list"><li><a class="fr-link" href="#contenu">Contenu</a></li></ul></nav></div>
<header role="banner"><div class="fr-container fr-mt-4w">{back}<h1>{e(title)}</h1><p class="fr-text--sm">{e(description)}</p></div></header>
<main id="contenu" class="{e(main_class)} fr-mb-4w">
{warning_container_open}
<div class="fr-alert fr-alert--warning fr-mb-4w"><h2 class="fr-alert__title">Lecture du verdict</h2><p>{e(report.warning)}</p></div>
{warning_container_close}
{body}
</main>
<footer><div class="fr-container fr-mt-4w fr-mb-4w"><p class="fr-text--xs">Synthèse du {e(report.delivery_date)}, audit du {e(report.audit_date)}, DSFR {e(", ".join(report.collection.observed_versions))} observé, règles {e(report.collection.target_version)}.</p></div></footer>
</body>
</html>
"""


def _code(label: str, code: str) -> str:
    return f'<p class="fr-mb-1w"><strong>{e(label)}</strong></p><pre><code>{e(code.strip())}</code></pre>'


def _list(items: list[str]) -> str:
    return (
        "<ul>" + "".join(f"<li>{e(i)}</li>" for i in items) + "</ul>"
        if items
        else "<p>Aucun.</p>"
    )


def group_section(group: Group, report: Report) -> str:
    occurrences = "".join(
        f"<li>{e(o['page'])} : constat <code>{e(o['id'])}</code></li>"
        for o in group.occurrences[:12]
    )
    more = (
        f"<li>et {len(group.occurrences) - 12} autre(s) occurrence(s)</li>"
        if len(group.occurrences) > 12
        else ""
    )
    missing = report.migration_details.get(group.group_id)
    missing_html = (
        f"<p>Classes attendues absentes de DSFR {e(', '.join(report.collection.observed_versions))} : {e(', '.join(missing))}</p>"
        if missing
        else ""
    )
    comments = _list(group.comments) if group.comments else ""
    contradiction_html = ""
    if group.status == "CONTRADICTION":
        rows = "".join(
            f'<tr><th scope="row">{e(bucket["page"])}</th><td>{e(bucket["state"])}</td><td><code>{e(bucket["dom_variant"])}</code></td><td>{e(", ".join(f"{status} x{count}" for status, count in sorted(bucket["statuses"].items())))}</td><td>{len(bucket["occurrences"])}</td></tr>'
            for bucket in contradiction_buckets(group)
        )
        contradiction_html = f'<h4>Contradictions regroupées par page, état et variante DOM</h4><div class="fr-table fr-table--bordered"><div class="fr-table__wrapper"><div class="fr-table__content"><table><caption>Contradictions de {e(group.rule_id)}</caption><thead><tr><th scope="col">Page</th><th scope="col">État</th><th scope="col">Variante DOM</th><th scope="col">Statuts</th><th scope="col">Occurrences</th></tr></thead><tbody>{rows}</tbody></table></div></div></div>'
    return f"""<section class="fr-mt-4w"><h3>{e(group.title)} <span class="fr-badge fr-badge--sm">{e(group.rule_id)}</span> <span class="fr-badge fr-badge--sm fr-badge--new">{e(group.severity or "sévérité non renseignée")}</span></h3>
<ul><li>Pages : {e(", ".join(group.pages))} ({len(group.occurrences)} occurrence(s))</li><li>Sélecteur : <code>{e(group.selector)}</code></li><li>Attendu : {e(group.expected)}</li><li>Observé : {e(group.observed)}</li></ul>
<h4>Ce qui manque ou diverge</h4>{_list(group.failed_conditions)}
<h4>Où le retrouver dans les rapports par page</h4><ul>{occurrences}{more}</ul>
{contradiction_html}
{_code("Code observé (DOM rendu)", group.observed_html)}{_code("Structure attendue", group.expected_html)}
<div class="fr-callout"><h4 class="fr-callout__title">Correctif</h4><p class="fr-callout__text">{e(group.recommendation)}</p><p class="fr-text--sm">Vérification après correction : {e(group.verification)}</p><p class="fr-text--xs">Source de la règle : <code>{e(group.source)}</code></p></div>
{missing_html}{("<h4>Commentaires de qualification</h4>" + comments) if comments else ""}</section>"""


def render_fiche(report: Report, name: str) -> str:
    verdict = report.verdicts[name]
    summary = report.collection.components[name]
    coll = report.collection
    links = ", ".join(
        f'<a class="fr-link" href="{page_report_href(p, 1)}">{e(p)}</a>'
        for p in summary.pages
    )
    body = [
        badge(verdict, display_status(name, verdict, report)),
        "<ul>",
        f"<li>Sélecteur : <code>{e(summary.selector)}</code></li>"
        if summary.selector
        else "<li>Règles globales au document</li>",
        f"<li>Pages concernées : {e(', '.join(summary.pages))} ({summary.count} instance(s) détectée(s))</li>",
        f"<li>Règles exécutées : {e(', '.join(verdict.rules_executed) or 'aucune')}</li>",
        f"<li>Rapports détaillés par page : {links}</li></ul>",
        "<h2>Pourquoi</h2>",
        _list(verdict.reasons),
    ]
    if verdict.confirmed_groups:
        body += ["<h2>Écarts confirmés</h2>"] + [
            group_section(g, report) for g in verdict.confirmed_groups
        ]
    if verdict.pending_groups:
        body += [
            "<h2>Signaux à confirmer</h2><p>Non arbitrés : ils empêchent tout verdict définitif.</p>",
            _list(
                [
                    f"{g.title} ({g.rule_id}) : {STATUS_LABELS.get(g.status, g.status)}, pages {', '.join(g.pages)}"
                    for g in verdict.pending_groups
                ]
            ),
        ]
        contradiction_groups = [
            group for group in verdict.pending_groups if group.status == "CONTRADICTION"
        ]
        if contradiction_groups:
            body += ["<h2>Détail des contradictions</h2>"] + [
                group_section(group, report) for group in contradiction_groups
            ]
    if verdict.migration_groups:
        body += [
            f"<h2>Ce qui change en DSFR {e(coll.target_version)}</h2><p>À traiter dans le plan de migration, pas comme défaut d'intégration.</p>"
        ]
        body += [group_section(g, report) for g in verdict.migration_groups]
    diff = report.example_diffs.get(name)
    if diff and (diff["added"] or diff["removed"]):
        body += [
            f"<p>Exemple officiel, de {e(', '.join(coll.observed_versions))} vers {e(coll.target_version)} : classes ajoutées {e(', '.join(diff['added']) or 'aucune')} ; retirées {e(', '.join(diff['removed']) or 'aucune')}.</p>"
        ]
    absent_pages = [p for p, names in report.expected_absent.items() if name in names]
    conditions = sum(len(g.failed_conditions) for g in verdict.confirmed_groups)
    body += [
        "<h2>Ce qui manque</h2>",
        _list(
            [
                "Dans le composant présent : "
                + (
                    f"{conditions} condition(s) en échec, détaillées ci-dessus"
                    if conditions
                    else "rien sur les règles exécutées"
                ),
                "Pages où le composant est attendu mais absent : "
                + (", ".join(absent_pages) or "aucune dans la baseline retenue"),
                "Couverture de l'audit : "
                + (
                    "aucune règle du harnais ne couvre ce composant"
                    if name in report.uncovered
                    else f"{len(verdict.rules_executed)} règle(s)"
                ),
                "États non exercés : " + ", ".join(gaps.unexercised_states(name)),
            ]
        ),
        f'<div class="fr-highlight"><p class="fr-text--sm">{e(gaps.STATES_NOTE)}</p></div>',
    ]
    return shell(
        f"{component_label(name)} - {verdict.label}",
        f"Fiche DSFR du composant {component_label(name)} sur {len(summary.pages)} page(s).",
        "\n".join(body),
        "../INDEX-DSFR-COMPOSANTS.html",
        "Retour au tableau de bord",
        report,
    )


def render_index(report: Report, include_parent_index: bool = True) -> str:
    coll = report.collection
    counts = {
        status: sum(
            1 for name in report.components if report.verdicts[name].status == status
        )
        for status in BADGES
    }
    summary_cards = []
    for status, title, description in (
        ("NON_CONFORME", "Non conformes", "Une action corrective est à prioriser."),
        (
            "NON_VERIFIE",
            "Non vérifiés",
            "Un arbitrage ou une couverture supplémentaire est nécessaire.",
        ),
        ("CONFORME", "Conformes", "Aucun écart sur les règles exécutées."),
    ):
        summary_cards.append(
            f'<div class="fr-col-12 fr-col-md-4"><article class="fr-card fr-card--sm"><div class="fr-card__body"><div class="fr-card__content">'
            f'<p class="dashboard-summary__count">{counts[status]}</p><h4 class="fr-card__title">{e(title)}</h4><p class="fr-card__desc">{e(description)}</p>'
            f"</div></div></article></div>"
        )
    rows = []
    for name in report.components:
        verdict, summary = report.verdicts[name], coll.components[name]
        status = display_status(name, verdict, report)
        action = (
            verdict.confirmed_groups[0].recommendation
            if verdict.confirmed_groups
            else (verdict.reasons[0] if verdict.reasons else "")
        )
        rows.append(
            f'<tr><th scope="row" headers="col-composant"><a class="fr-link" href="composants/{e(name)}.html">{e(component_label(name))}</a><br><code>{e(summary.selector)}</code></th>'
            f'<td headers="col-verdict">{table_badge(verdict, status)}</td><td headers="col-pages">{e(", ".join(summary.pages))}</td>'
            f'<td headers="col-severite">{e(verdict.max_severity or "-")}</td><td headers="col-action">{e(action)}</td></tr>'
        )
    table = builder_table(
        f"Verdict par composant, {len(report.components)} composants",
        ["Composant", "Verdict", "Pages", "Sévérité", "Action"],
        "".join(rows),
    )
    absent = [
        f"{p} : {', '.join(component_label(n) for n in names)}"
        for p, names in report.expected_absent.items()
        if names
    ]
    uncovered = [
        f"{component_label(n)} : détecté sur {', '.join(coll.components[n].pages)}, aucune règle du harnais."
        for n in report.uncovered
    ]
    migr = [
        f"{component_label(n)} : {g.title} ({g.rule_id}), classes absentes en {', '.join(coll.observed_versions)} : {', '.join(report.migration_details.get(g.group_id, [])) or 'non déterminées'}."
        for n in report.components
        for g in report.verdicts[n].migration_groups
    ]
    body = [
        '<div class="fr-grid-row fr-grid-row--center"><div class="fr-col-12 fr-col-lg-10">',
        "<h2>Échantillon</h2>",
        "<ul>"
        + "".join(
            f'<li>{e(p["id"])} - {e(p["name"])} : <a class="fr-link" href="{e(p["url"])}">{e(p["url"])}</a></li>'
            for p in report.pages
        )
        + "</ul>",
        "<h2>Versions DSFR</h2>",
        _list(
            [
                f"Version chargée par le site : {', '.join(coll.observed_versions) or 'inconnue'}",
                f"Version de référence des règles : {coll.target_version}",
                f"Un écart compte dans le verdict seulement si les classes attendues existent en {', '.join(coll.observed_versions)} ; sinon il est classé migration.",
            ]
        ),
        "<h2>Tableau de bord</h2>",
        '<section class="dashboard-summary fr-mb-4w" aria-labelledby="repartition-verdicts"><h3 id="repartition-verdicts">Répartition des verdicts</h3><div class="fr-grid-row fr-grid-row--gutters">'
        + "".join(summary_cards)
        + "</div></section>",
        "</div></div>",
        '<div class="fr-grid-row fr-grid-row--gutters fr-grid-row--center"><div class="fr-col-12 fr-col-lg-11"><p id="tableau-verdicts-aide" class="fr-text--sm fr-mb-1w">Sur petit écran, les cellules se replient dans la largeur disponible ; les informations restent consultables sans défilement horizontal.</p>'
        + table
        + "</div></div>",
        '<div class="fr-grid-row fr-grid-row--center"><div class="fr-col-12 fr-col-lg-10">',
        "<h2>Composants attendus mais absents</h2><p class=\"fr-text--sm\">Baseline : liens d'évitement, en-tête, pied de page et consentement partout ; fil d'Ariane hors accueil ; groupe de messages sur les formulaires. Une absence est signalée, pas qualifiée.</p>",
        _list(absent),
        "<h2>Hors couverture de l'audit</h2>",
        _list(uncovered),
        f"<h2>Migration {e(', '.join(coll.observed_versions))} vers {e(coll.target_version)}</h2>",
        _list(migr),
        "<h2>Limites</h2>",
        _list(
            [f"Non vérifié par cet audit : {i}" for i in report.not_verified]
            + [gaps.STATES_NOTE]
        ),
        "</div></div>",
    ]
    return shell(
        "Synthèse DSFR par composant - portail Douane",
        f"Verdict par composant DSFR sur {len(report.pages)} pages de préproduction.",
        "\n".join(body),
        "../INDEX-LIVRABLES.html" if include_parent_index else None,
        "Index général des livrables",
        report,
        main_class="fr-container--fluid",
    )


def render_index_card(report: Report) -> str:
    counts = {
        s: sum(1 for n in report.components if report.verdicts[n].status == s)
        for s in BADGES
    }
    return (
        f'<article class="card"><p class="count">{len(report.components)}</p><h2>Synthèse DSFR par composant</h2>'
        f"<p>{counts['NON_CONFORME']} non conformes, {counts['CONFORME']} conformes aux règles exécutées, {counts['NON_VERIFIE']} non vérifiés.</p>"
        f'<p><a href="DSFR-COMPOSANTS/INDEX-DSFR-COMPOSANTS.html">Ouvrir la synthèse par composant</a>.</p></article>'
    )
