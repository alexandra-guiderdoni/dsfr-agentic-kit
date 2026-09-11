#!/usr/bin/env python3
"""Synthèse DSFR par composant du livrable Virginie.

Lit les archives par page d'audit-rgaa-creator, dédoublonne les écarts par
composant, applique la revue humaine, sépare intégration et migration à partir
des paquets officiels, puis rend un tableau de bord et une fiche par composant
en HTML et en Markdown. Les archives ne sont jamais modifiées.

Flux : première exécution sans fiche de revue -> écriture de
DSFR-COMPOSANTS-TRAVAIL/REVUE-A-QUALIFIER.md, exit 2. Le relecteur coche une
case par groupe. Exécution suivante -> rendu. La fiche n'est jamais réécrite
si elle existe ; la supprimer pour la régénérer. Une archive dont le catalogue
est obsolète ou mélangé exige --allow-stale-catalog pour produire une synthèse
explicitement marquée comme exception.
"""

from __future__ import annotations

import argparse
import fcntl
import json
import os
import sys
from contextlib import contextmanager
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from virginie_dsfr import collect, gaps, migration, publish, qualify, render_html, render_markdown, verdict  # noqa: E402
from virginie_dsfr.project_paths import (  # noqa: E402
    KIT_ROOT,
    require_project_root,
    safe_pipeline_lock,
    safe_write_path,
)

ROOT = KIT_ROOT
DELIVERY = ROOT / "virginie-livrables"
# Motif neutre par défaut. Une recette de projet peut fournir le nom de ses
# archives avec --pattern ; aucun nom de mission ne doit être implicite dans
# le kit.
DEFAULT_PATTERN = "audit-p{n:02d}"
RULES = ROOT / ".claude/skills/audit-dsfr-complet/rules/dsfr-rules.json"
PIPELINE_LOCK = ROOT / "visual-tests/_results/.p06-pipeline.lock"


def parse_pages(spec: str) -> list[int]:
    numbers: list[int] = []
    for part in spec.split(","):
        if "-" in part:
            start, end = part.split("-", 1)
            numbers.extend(range(int(start), int(end) + 1))
        elif part.strip():
            numbers.append(int(part))
    return numbers


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument(
        "--project-root",
        type=Path,
        default=None,
        help="projet de travail existant ; défaut : DSFR_PROJECT_ROOT",
    )
    parser.add_argument("--archives", type=Path, default=None)
    parser.add_argument("--pattern", default=DEFAULT_PATTERN, help="motif de dossier d'archive, avec {n:02d}")
    parser.add_argument("--pages", default="1-9", help="numéros de pages, ex. 1-9 ou 1,2,6")
    parser.add_argument("--output", type=Path, default=None)
    parser.add_argument("--work-dir", type=Path, default=None)
    parser.add_argument("--review-sheet", type=Path, default=None, help="défaut : <work-dir>/REVUE-A-QUALIFIER.md")
    parser.add_argument("--cache-dir", type=Path, default=Path(os.environ.get("DSFR_OFFICIAL_CACHE_DIR") or "~/.cache/dsfr-official-cache").expanduser())
    parser.add_argument("--rules", type=Path, default=RULES)
    parser.add_argument("--delivery-date", default=date.today().isoformat())
    parser.add_argument("--allow-pending", action="store_true", help="rendre malgré des signaux non arbitrés (Non vérifié)")
    parser.add_argument(
        "--allow-stale-catalog",
        action="store_true",
        help="rendre malgré un catalogue DSFR obsolète ou mélangé, en marquant l’exception",
    )
    parser.add_argument("--no-index", action="store_true", help="ne pas toucher à INDEX-LIVRABLES.html")
    return parser.parse_args()


def configure_paths(args: argparse.Namespace) -> argparse.Namespace:
    """Place toutes les destinations d’écriture sous le projet de travail."""
    project_root = require_project_root(args.project_root)
    delivery = safe_write_path(
        project_root / "virginie-livrables",
        project_root=project_root,
        label="livrables",
    )
    args.project_root = project_root
    args.archives = args.archives or project_root / "archives"
    args.output = safe_write_path(
        args.output or delivery / "DSFR-COMPOSANTS",
        project_root=project_root,
        label="sortie DSFR",
    )
    args.work_dir = safe_write_path(
        args.work_dir or delivery / "DSFR-COMPOSANTS-TRAVAIL",
        project_root=project_root,
        label="travail DSFR",
    )
    args.review_sheet = safe_write_path(
        args.review_sheet or args.work_dir / "REVUE-A-QUALIFIER.md",
        project_root=project_root,
        label="fiche de revue",
    )
    global DELIVERY, PIPELINE_LOCK
    DELIVERY = delivery
    PIPELINE_LOCK = safe_pipeline_lock(project_root)
    safe_write_path(
        DELIVERY / "INDEX-LIVRABLES.html",
        project_root=project_root,
        label="index des livrables",
    )
    return args


@contextmanager
def pipeline_lock():
    PIPELINE_LOCK.parent.mkdir(parents=True, exist_ok=True)
    with PIPELINE_LOCK.open("a+", encoding="utf-8") as handle:
        fcntl.flock(handle.fileno(), fcntl.LOCK_EX)
        try:
            yield
        finally:
            fcntl.flock(handle.fileno(), fcntl.LOCK_UN)


def load_collection(args: argparse.Namespace) -> collect.Collection:
    pages = []
    for number in parse_pages(args.pages):
        archive = args.archives / args.pattern.format(n=number)
        if not archive.is_dir():
            raise SystemExit(f"Archive absente : {archive}")
        pages.append(collect.load_page(archive))
    return collect.collect(pages)


def resolve_review(args: argparse.Namespace, collection: collect.Collection) -> tuple[Path, dict[str, str]]:
    sheet = args.review_sheet or (args.work_dir / "REVUE-A-QUALIFIER.md")
    overrides: dict[str, str] = {}
    if sheet.is_file():
        text = sheet.read_text(encoding="utf-8")
        overrides = qualify.parse_review_sheet(text)
        qualify.apply_overrides(collection, overrides, qualify.parse_review_comments(text))
    return sheet, overrides


def compute_kinds(collection: collect.Collection, cache_dir: Path) -> tuple[dict, dict, dict, migration.CssIndex]:
    observed = collection.observed_versions[0] if collection.observed_versions else collection.target_version
    index = migration.CssIndex(cache_dir, observed, collection.target_version)
    kinds, details, diffs = {}, {}, {}
    for group in collection.groups.values():
        if group.status == "ECART_CONFIRME" and group.component != collect.VERSION_COMPONENT:
            kinds[group.group_id], missing = index.classify(group.expected_html, group.failed_conditions)
            if missing:
                details[group.group_id] = missing
    for name in collection.components:
        diff = index.example_diff(name)
        if diff:
            diffs[name] = diff
    return kinds, details, diffs, index


def review_hints(collection: collect.Collection, groups: list, cache_dir: Path) -> dict[str, list[str]]:
    """Faits vérifiables pour la décision : classes attendues présentes ou non dans la version observée."""
    observed = collection.observed_versions[0] if collection.observed_versions else collection.target_version
    index = migration.CssIndex(cache_dir, observed, collection.target_version)
    hints: dict[str, list[str]] = {}
    for group in groups:
        if not index.available:
            hints[group.group_id] = [f"paquet officiel {observed} ou {collection.target_version} absent du cache : comparaison impossible"]
            continue
        kind, missing = index.classify(group.expected_html, group.failed_conditions)
        if missing:
            hints[group.group_id] = [f"classes attendues absentes de DSFR {observed} : {', '.join(missing)} ; l'écart relève de la {kind}"]
        else:
            hints[group.group_id] = [f"toutes les classes attendues existent en DSFR {observed} : si l'écart est réel, il relève de l'intégration, pas de la migration"]
        diff = index.example_diff(group.component)
        if diff and (diff["added"] or diff["removed"]):
            hints[group.group_id].append(f"exemple officiel {observed} -> {collection.target_version} : ajoutées {', '.join(diff['added']) or 'aucune'} ; retirées {', '.join(diff['removed']) or 'aucune'}")
        hints[group.group_id].append(f"exemple officiel à relire : package/example/component/{migration.EXAMPLE_FOLDERS.get(group.component, group.component)}/index.html des deux paquets")
    return hints


def main() -> int:
    args = configure_paths(parse_args())
    with pipeline_lock():
        collection = load_collection(args)
        sheet, overrides = resolve_review(args, collection)
        pending = qualify.pending_groups(collection)
        args.work_dir.mkdir(parents=True, exist_ok=True)
        if pending and not sheet.is_file():
            sheet.write_text(qualify.render_review_sheet(collection, pending, review_hints(collection, pending, args.cache_dir)), encoding="utf-8")
            print(f"[REVUE] {len(pending)} groupe(s) à qualifier -> {sheet}")
            return 2
        if pending and not args.allow_pending:
            print(f"[REVUE] {len(pending)} groupe(s) encore sans décision dans {sheet} ; ajouter --allow-pending pour rendre en Non vérifié")
            for group in pending:
                print(f"  - {group.group_id} ({group.status})")
            return 2
        catalog_status = collection.catalog_status
        stale_catalog_statuses = {"CATALOGUE_OBSOLETE", "CATALOGUES_MULTIPLES"}
        stale_catalog_allowed = (
            catalog_status["status"] in stale_catalog_statuses
            and args.allow_stale_catalog
        )
        if catalog_status["status"] in stale_catalog_statuses and not stale_catalog_allowed:
            print(
                f"[CATALOGUE] {catalog_status['message']} ; ajouter --allow-stale-catalog pour produire une synthèse d’archives explicitement marquée",
                file=sys.stderr,
            )
            return 2
        kinds, details, diffs, index = compute_kinds(collection, args.cache_dir)
        verdicts = verdict.component_verdicts(collection, kinds)
        report = verdict.build_report(collection, verdicts, details, args.delivery_date, diffs, reference_available=index.available)
        if stale_catalog_allowed:
            report.catalog_status["stale_catalog_allowed"] = True
        written = publish.write_outputs(
            report, args.output, include_parent_index=not args.no_index
        )
        (args.work_dir / "qualification-virginie-dsfr.json").write_text(json.dumps({
            "schema_version": 1, "reviewed_at": args.delivery_date, "source_sheet": sheet.name,
            "decisions": [{"group_id": gid, "qualification_status": status, "rule_id": collection.groups[gid].rule_id,
                           "pages": collection.groups[gid].pages, "selector": collection.groups[gid].selector} for gid, status in overrides.items()],
        }, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        coverage = gaps.harness_coverage(collection, args.rules)
        (args.work_dir / "COUVERTURE-HARNAIS.md").write_text(render_markdown.render_couverture(report, coverage), encoding="utf-8")
        index_state = "skipped" if args.no_index else publish.insert_index_card(DELIVERY / "INDEX-LIVRABLES.html", render_html.render_index_card(report))
        errors = publish.verify_outputs(written, index.target_classes)
        publish.update_manifest(args.output, report, errors)
        checksums = publish.write_checksums(args.output, written)
        receipt = {
            "delivery_date": args.delivery_date, "pages": [p.id for p in collection.pages], "components": len(report.components),
            "verdicts": verdict.build_manifest(report)["verdict_counts"], "groups": len(collection.groups), "overrides": len(overrides),
            "pending": len(pending), "migration_reference_available": index.available, "index_card": index_state,
            "files": len(written), "checksums": checksums.name, "errors": errors,
            "catalog_status": report.catalog_status,
            "stale_catalog_allowed": stale_catalog_allowed,
        }
        (args.work_dir / "RECU-GENERATION.json").write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print(json.dumps(receipt, ensure_ascii=False, indent=2))
        return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
