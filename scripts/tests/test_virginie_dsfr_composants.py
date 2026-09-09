"""Tests de la synthèse DSFR par composant du livrable Virginie.

Fixture synthétique : deux archives par page au format des campagnes
audit-rgaa-creator (dsfr/pages/Pxx.json, dsfr/ECARTS-COMPOSANTS.json,
dsfr-findings.json). Aucune lecture des archives réelles.
"""

from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))

from virginie_dsfr import collect, gaps, migration, qualify, render_html, render_markdown, verdict  # noqa: E402

SELECTOR_P01 = (
    "html.js > body.path-frontpage.eu-cookie-compliance-popup-open > "
    "div.dialog-off-canvas-main-canvas:nth-of-type(3) > header.fr-header > div.fr-nav.menu-connection"
)
SELECTOR_P02 = (
    "html.js > body.path-plan-du-site.eu-cookie-compliance-status-null > "
    "div.dialog-off-canvas-main-canvas:nth-of-type(4) > header.fr-header > div.fr-nav.menu-connection"
)


def difference(page: str, rule: str, component: str, selector: str, status: str, kind: str = "integration", **extra):
    base = {
        "id": f"{page}-{rule}-001",
        "rule_id": rule,
        "kind": kind,
        "component": component,
        "instance": 1,
        "signal_status": "FAIL_CANDIDATE",
        "status": "ECART_OBSERVE",
        "qualification_status": status,
        "severity": "Bloquant",
        "title": f"Titre {rule}",
        "expected": "attendu",
        "observed": "observé",
        "selector": selector,
        "observed_html": '<div class="fr-nav menu-connection"></div>',
        "observed_html_origin": "RENDERED_DOM",
        "expected_html": '<nav class="fr-nav" role="navigation" aria-label="Menu"><ul class="fr-nav__list"></ul></nav>',
        "failed_conditions": ["La racine doit être nav."],
        "source": "dsfr-components/references/components/navigation/navigation.md",
        "reference_target_version": "1.15.2",
        "observed_versions": ["1.13.2"],
        "assessed_against": "MIGRATION_VERS_CIBLE",
        "evidence": [f"dsfr/preuves/{page}/attempt-001/evidence.json"],
        "recommendation": "Restaurer nav.",
        "verification": "Inspecter le DOM.",
        "page": page,
        "page_name": f"Page {page}",
        "page_url": f"https://exemple.gouv.fr/{page.lower()}",
    }
    base.update(extra)
    return base


def inventory_item(name: str, selector: str, status: str, rules: list[str], count: int = 1):
    return {"name": name, "selector": selector, "count": count, "visible": count, "status": status,
            "rules_executed": rules, "source": f"dsfr-components/references/components/{name}.md", "samples": []}


def make_archive(root: Path, page: str, name: str, page_type: str, inventory: list, differences: list) -> Path:
    archive = root / f"audit-test-{page.lower()}-2026-09-02"
    (archive / "dsfr" / "pages").mkdir(parents=True)
    page_doc = {
        "schema_version": 2,
        "page": {"id": page, "name": name, "url": f"https://exemple.gouv.fr/{page.lower()}", "type": page_type},
        "audited_at": "2026-09-02T10:00:00+00:00",
        "version": {"observed": ["1.13.2"], "target": "1.15.2", "comparison_mode": "MIGRATION_VERS_CIBLE",
                    "exact_observed_reference_available": False},
        "reference_version": "1.15.2",
        "detected_versions": ["1.13.2"],
        "inventory": inventory,
        "rule_results": [],
        "global_checks": {},
        "differences": differences,
        "not_verified": ["lecteur d’écran réel"],
        "evidence": {},
    }
    (archive / "dsfr" / "pages" / f"{page}.json").write_text(json.dumps(page_doc, ensure_ascii=False), encoding="utf-8")
    ecarts = {"schema_version": 2, "claim": "Aucune conformité DSFR globale n’est revendiquée.",
              "target_versions": ["1.15.2"], "observed_versions": ["1.13.2"], "root_causes": [], "differences": differences}
    (archive / "dsfr" / "ECARTS-COMPOSANTS.json").write_text(json.dumps(ecarts, ensure_ascii=False), encoding="utf-8")
    (archive / "dsfr-findings.json").write_text(json.dumps({"schema_version": 1, "findings": []}), encoding="utf-8")
    return archive


def build_fixture(root: Path) -> list[Path]:
    p01 = make_archive(
        root, "P01", "Accueil", "homepage",
        [inventory_item("navigation", ".fr-nav", "ECART_OBSERVE", ["DSFR-NAV-STRUCTURE-001"]),
         inventory_item("header", ".fr-header", "AUCUN_ECART_REGLES_EXECUTEES", ["DSFR-HEADER-STRUCTURE-001"]),
         inventory_item("quote", ".fr-quote", "DETECTE_NON_AUDITE", []),
         inventory_item("skiplink", ".fr-skiplinks", "AUCUN_ECART_REGLES_EXECUTEES", ["DSFR-SKIPLINK-STRUCTURE-001"]),
         inventory_item("footer", ".fr-footer", "AUCUN_ECART_REGLES_EXECUTEES", ["DSFR-FOOTER-STRUCTURE-001"]),
         inventory_item("consent", ".fr-consent-banner", "AUCUN_ECART_REGLES_EXECUTEES", ["DSFR-CONSENT-STRUCTURE-001"])],
        [difference("P01", "DSFR-NAV-STRUCTURE-001", "navigation", SELECTOR_P01, "ECART_CONFIRME")],
    )
    p02 = make_archive(
        root, "P02", "Plan du site", "sitemap",
        [inventory_item("navigation", ".fr-nav", "ECART_OBSERVE", ["DSFR-NAV-STRUCTURE-001"]),
         inventory_item("header", ".fr-header", "AUCUN_ECART_REGLES_EXECUTEES", ["DSFR-HEADER-STRUCTURE-001"]),
         inventory_item("skiplink", ".fr-skiplinks", "AUCUN_ECART_REGLES_EXECUTEES", ["DSFR-SKIPLINK-STRUCTURE-001"]),
         inventory_item("footer", ".fr-footer", "AUCUN_ECART_REGLES_EXECUTEES", ["DSFR-FOOTER-STRUCTURE-001"])],
        [difference("P02", "DSFR-NAV-STRUCTURE-001", "navigation", SELECTOR_P02, "A_CONFIRMER", kind="migration")],
    )
    return [p01, p02]


class SelectorTests(unittest.TestCase):
    def test_normalize_selector_strips_volatile_tokens(self):
        self.assertEqual(collect.normalize_selector(SELECTOR_P01), collect.normalize_selector(SELECTOR_P02))
        self.assertNotIn("nth-of-type", collect.normalize_selector(SELECTOR_P01))
        self.assertEqual(collect.leaf_selector(SELECTOR_P01), "div.fr-nav.menu-connection")

    def test_normalize_keeps_distinct_components_distinct(self):
        self.assertNotEqual(collect.normalize_selector("#edit-nom"), collect.normalize_selector("#edit-prenom"))


class CollectTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.pages = [collect.load_page(path) for path in build_fixture(Path(self.tmp.name))]
        self.collection = collect.collect(self.pages)

    def tearDown(self):
        self.tmp.cleanup()

    def test_same_leaf_selector_on_two_pages_is_one_group(self):
        groups = [g for g in self.collection.groups.values() if g.rule_id == "DSFR-NAV-STRUCTURE-001"]
        self.assertEqual(len(groups), 1)
        self.assertEqual(groups[0].pages, ["P01", "P02"])
        self.assertEqual(groups[0].statuses, {"ECART_CONFIRME": 1, "A_CONFIRMER": 1})

    def test_components_merged_across_pages(self):
        nav = self.collection.components["navigation"]
        self.assertEqual(nav.pages, ["P01", "P02"])
        self.assertEqual(nav.count, 2)
        self.assertEqual(sorted(nav.rules_executed), ["DSFR-NAV-STRUCTURE-001"])
        self.assertEqual(self.collection.components["quote"].pages, ["P01"])

    def test_contradiction_detected_without_arbitration(self):
        contradictions = qualify.detect_contradictions(self.collection)
        self.assertEqual([g.rule_id for g in contradictions], ["DSFR-NAV-STRUCTURE-001"])

    def test_review_sheet_arbitration_resolves_contradiction(self):
        group = next(iter(self.collection.groups.values()))
        sheet = qualify.render_review_sheet(self.collection, [group])
        self.assertIn(group.group_id, sheet)
        self.assertIn("- [ ] ECART_CONFIRME", sheet)
        checked = sheet.replace("- [ ] AUCUN_ECART_OBSERVE", "- [x] AUCUN_ECART_OBSERVE", 1)
        overrides = qualify.parse_review_sheet(checked)
        self.assertEqual(overrides, {group.group_id: "AUCUN_ECART_OBSERVE"})
        qualify.apply_overrides(self.collection, overrides)
        self.assertEqual(group.final_status, "AUCUN_ECART_OBSERVE")
        self.assertEqual(qualify.detect_contradictions(self.collection), [])

    def test_review_sheet_carries_hints(self):
        group = next(iter(self.collection.groups.values()))
        sheet = qualify.render_review_sheet(self.collection, [group], {group.group_id: ["toutes les classes attendues existent en DSFR 1.13.2"]})
        self.assertIn("- Repère : toutes les classes attendues existent en DSFR 1.13.2", sheet)
        self.assertEqual(qualify.parse_review_sheet(sheet), {})

    def test_review_sheet_rejects_two_checked_boxes(self):
        group = next(iter(self.collection.groups.values()))
        sheet = qualify.render_review_sheet(self.collection, [group])
        broken = sheet.replace("- [ ] ECART_CONFIRME", "- [x] ECART_CONFIRME").replace("- [ ] NON_APPLICABLE", "- [x] NON_APPLICABLE")
        with self.assertRaises(qualify.ReviewSheetError):
            qualify.parse_review_sheet(broken)


class VerdictTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.pages = [collect.load_page(path) for path in build_fixture(Path(self.tmp.name))]
        self.collection = collect.collect(self.pages)

    def tearDown(self):
        self.tmp.cleanup()

    def test_three_verdicts(self):
        group = next(iter(self.collection.groups.values()))
        qualify.apply_overrides(self.collection, {group.group_id: "ECART_CONFIRME"})
        verdicts = verdict.component_verdicts(self.collection, kinds={group.group_id: "integration"})
        self.assertEqual(verdicts["navigation"].status, "NON_CONFORME")
        self.assertEqual(verdicts["header"].status, "CONFORME")
        self.assertEqual(verdicts["quote"].status, "NON_VERIFIE")
        self.assertIn("DSFR-HEADER-STRUCTURE-001", verdicts["header"].rules_executed)
        self.assertTrue(verdicts["quote"].reasons)

    def test_migration_group_does_not_make_component_non_conforme(self):
        group = next(iter(self.collection.groups.values()))
        qualify.apply_overrides(self.collection, {group.group_id: "ECART_CONFIRME"})
        verdicts = verdict.component_verdicts(self.collection, kinds={group.group_id: "migration"})
        self.assertEqual(verdicts["navigation"].status, "CONFORME")
        self.assertEqual([g.group_id for g in verdicts["navigation"].migration_groups], [group.group_id])

    def test_pending_group_gives_non_verifie(self):
        verdicts = verdict.component_verdicts(self.collection, kinds={})
        self.assertEqual(verdicts["navigation"].status, "NON_VERIFIE")


class MigrationTests(unittest.TestCase):
    def test_kind_from_css_class_presence(self):
        with tempfile.TemporaryDirectory() as tmp:
            cache = Path(tmp)
            for version, css in (("1.13.2", ".fr-nav{}.fr-nav__list{}"), ("1.15.2", ".fr-nav{}.fr-nav__list{}.fr-nav__new{}")):
                target = cache / f"gouvfr-dsfr-{version}" / "package" / "dist"
                target.mkdir(parents=True)
                (target / "dsfr.min.css").write_text(css, encoding="utf-8")
            icons = cache / "gouvfr-dsfr-1.15.2" / "package" / "dist" / "utility" / "icons"
            icons.mkdir(parents=True)
            (icons / "icons.min.css").write_text(".fr-icon-arrow-left-line::before{}", encoding="utf-8")
            index = migration.CssIndex(cache, "1.13.2", "1.15.2")
            self.assertIn("fr-icon-arrow-left-line", index.target_classes)
            self.assertNotIn("fr-icon-arrow-left-line", index.observed_classes)
            self.assertEqual(index.classify('<nav class="fr-nav"><ul class="fr-nav__list"></ul></nav>', []), ("integration", []))
            self.assertEqual(index.classify('<ul class="fr-nav__new"></ul>', []), ("migration", ["fr-nav__new"]))
            self.assertEqual(index.classify("<div></div>", ["La classe fr-nav__new est absente."]), ("migration", ["fr-nav__new"]))
            # Un identifiant ou une cible aria-controls n'est pas une classe : pas de fausse migration.
            self.assertEqual(index.classify('<button class="fr-nav" aria-controls="fr-theme-modal" id="fr-other">x</button>', []), ("integration", []))


class GapsTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.pages = [collect.load_page(path) for path in build_fixture(Path(self.tmp.name))]
        self.collection = collect.collect(self.pages)

    def tearDown(self):
        self.tmp.cleanup()

    def test_expected_absent_uses_validated_baseline(self):
        absent = gaps.expected_absent(self.collection)
        self.assertEqual(absent["P02"], ["breadcrumb", "consent"])
        self.assertEqual(absent["P01"], [])

    def test_uncovered_components(self):
        self.assertEqual(gaps.uncovered_components(self.collection), ["quote"])


class RenderTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        root = Path(self.tmp.name)
        self.pages = [collect.load_page(path) for path in build_fixture(root)]
        self.collection = collect.collect(self.pages)
        group = next(iter(self.collection.groups.values()))
        qualify.apply_overrides(self.collection, {group.group_id: "ECART_CONFIRME"})
        self.verdicts = verdict.component_verdicts(self.collection, kinds={group.group_id: "integration"})
        self.report = verdict.build_report(self.collection, self.verdicts, migration_details={}, delivery_date="2026-09-09")

    def tearDown(self):
        self.tmp.cleanup()

    def test_markdown_outputs_have_no_absolute_paths_and_carry_warning(self):
        synthese = render_markdown.render_synthese(self.report)
        self.assertNotIn("/Users/", synthese)
        self.assertNotIn(self.tmp.name, synthese)
        self.assertIn("règles exécutées", synthese)
        fiche = render_markdown.render_fiche(self.report, "navigation")
        self.assertIn("Non conforme", fiche)
        self.assertIn("P01", fiche)

    def test_html_outputs_use_known_dsfr_classes_only(self):
        index_html = render_html.render_index(self.report)
        fiche_html = render_html.render_fiche(self.report, "navigation")
        known = {"fr-container", "fr-badge", "fr-badge--error", "fr-badge--success", "fr-badge--info", "fr-table",
                 "fr-callout", "fr-callout__title", "fr-callout__text", "fr-alert", "fr-alert--warning", "fr-alert__title",
                 "fr-skiplinks", "fr-skiplinks__list", "fr-link", "fr-grid-row", "fr-col-12", "fr-mt-4w", "fr-mb-4w",
                 "fr-h1", "fr-h2", "fr-h3", "fr-text--sm", "fr-card", "fr-card__body", "fr-card__content", "fr-card__title",
                 "fr-card__desc", "fr-tag", "fr-btn", "fr-btn--secondary", "fr-btns-group", "fr-accordion",
                 "fr-accordion__btn", "fr-accordion__title", "fr-collapse", "fr-mb-2w", "fr-mt-2w", "fr-text--xs",
                 "fr-highlight", "fr-hr", "fr-table--bordered", "fr-sr-only", "fr-icon-arrow-left-line", "fr-link--icon-left",
                 "fr-btn--icon-left", "fr-header", "fr-footer", "fr-footer__body", "fr-footer__content", "fr-footer__content-desc",
                 "fr-col-md-6", "fr-col-lg-4", "fr-grid-row--gutters", "fr-badge--sm", "fr-badge--new", "fr-mt-1w", "fr-mb-1w",
                 "fr-card--sm", "fr-table__wrapper", "fr-table__container", "fr-table__content", "fr-mb-0"}
        for html_text in (index_html, fiche_html):
            used = set(render_html.dsfr_classes(html_text))
            self.assertTrue(used, "aucune classe DSFR rendue")
            self.assertEqual(used - known, set())
            self.assertNotIn("/Users/", html_text)
            self.assertIn('lang="fr"', html_text)

    def test_local_source_limit_reworded_when_reference_available(self):
        self.pages[0].not_verified.append("intégration exacte contre une source locale DSFR 1.13.2")
        without = verdict.build_report(self.collection, self.verdicts, {}, "2026-09-09")
        self.assertTrue(any("source locale" in item for item in without.not_verified))
        with_ref = verdict.build_report(self.collection, self.verdicts, {}, "2026-09-09", reference_available=True)
        self.assertFalse(any("intégration exacte contre une source locale" in item for item in with_ref.not_verified))
        self.assertTrue(any("paquet officiel 1.13.2" in item for item in with_ref.not_verified))
        self.assertEqual(self.verdicts["header"].reasons[0], "Aucun écart sur la règle exécutée contre DSFR 1.13.2.")

    def test_manifest_counts_match_report(self):
        manifest = verdict.build_manifest(self.report)
        self.assertEqual(manifest["component_count"], len(self.report.components))
        self.assertEqual(manifest["verdict_counts"]["NON_CONFORME"], 1)
        self.assertEqual(manifest["pages"], ["P01", "P02"])
        self.assertEqual(manifest["observed_versions"], ["1.13.2"])


class PublishTests(unittest.TestCase):
    def test_index_card_inserted_then_replaced_idempotently(self):
        from virginie_dsfr import publish
        with tempfile.TemporaryDirectory() as tmp:
            index = Path(tmp) / "INDEX-LIVRABLES.html"
            self.assertEqual(publish.insert_index_card(index, "<article>x</article>"), "missing")
            index.write_text('<main><section class="cards">\n    <article>a</article>\n  </section><p>fin</p></main>', encoding="utf-8")
            self.assertEqual(publish.insert_index_card(index, "<article>carte v1</article>"), "inserted")
            first = index.read_text(encoding="utf-8")
            self.assertIn("carte v1", first)
            self.assertLess(first.index("carte v1"), first.index("</section>"))
            self.assertEqual(publish.insert_index_card(index, "<article>carte v2</article>"), "replaced")
            second = index.read_text(encoding="utf-8")
            self.assertIn("carte v2", second)
            self.assertNotIn("carte v1", second)
            self.assertEqual(second.count(publish.INDEX_START), 1)
            self.assertIn("<p>fin</p>", second)
            index.write_text("<main><p>sans section</p></main>", encoding="utf-8")
            self.assertEqual(publish.insert_index_card(index, "<article>x</article>"), "no_anchor")


if __name__ == "__main__":
    unittest.main()
