import argparse
import contextlib
import hashlib
import importlib.util
import json
import math
import os
import re
import shutil
import stat
import subprocess
import sys
import tempfile
import unittest
import unittest.mock
import xml.etree.ElementTree as ET
from pathlib import Path


SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "generate_pictos_svg.py"
ANALYZE_SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "analyze_dsfr_corpus.py"
PREVIEW_SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "build_svg_preview.py"
AUDIT_SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "audit_original_pictos.py"
OFFICIAL_CORPUS = Path(__file__).resolve().parents[1] / "pictos-svg" / "dsfr-officiels"
STYLE_GUIDE = Path(__file__).resolve().parents[1] / "references" / "guide-style-pictogrammes-dsfr.md"
PROMPT_PROFILE = Path(__file__).resolve().parents[1] / "references" / "dsfr-prompt-profile.json"
ETALON = Path(__file__).resolve().parents[1] / "pictos-svg" / "etalon"


def dsfr_fixture(width: str = "80px", height: str = "80px", use_block: str | None = None, style_minor: str = "#E1000F") -> str:
    uses = (
        """<use class="fr-artwork-decorative" href="#artwork-decorative"/>
<use class="fr-artwork-minor" href="#artwork-minor"/>
<use class="fr-artwork-major" href="#artwork-major"/>"""
        if use_block is None
        else use_block
    )
    return f"""<svg width="{width}" height="{height}" viewBox="0 0 80 80" xmlns="http://www.w3.org/2000/svg">
<style>
.fr-artwork-decorative {{ fill: #ECECFF; }}
.fr-artwork-minor {{ fill: {style_minor}; }}
.fr-artwork-major {{ fill: #000091; }}
</style>
<symbol id="artwork-decorative"><path d="M8 8a1 1 0 1 1-2 0 1 1 0 0 1 2 0Z"/></symbol>
<symbol id="artwork-minor"><path d="M24 24h16v16H24z"/></symbol>
<symbol id="artwork-major"><path d="M16 16h48v48H16z"/></symbol>
{uses}
</svg>
"""


class GeneratePictosSvgTest(unittest.TestCase):
    def test_generates_parseable_svg_and_manifest(self):
        with tempfile.TemporaryDirectory() as tmp:
            result = subprocess.run(
                [
                    sys.executable,
                    "-B",
                    str(SCRIPT),
                    "--source",
                    "generated",
                    "--icons",
                    "document,ai,shield,pencil,house",
                    "--output-dir",
                    tmp,
                    "--preset",
                    "dsfr",
                ],
                check=True,
                text=True,
                capture_output=True,
            )

            self.assertIn("document.svg", result.stdout)
            for name in ["document", "ai", "shield", "pencil", "house"]:
                svg_path = Path(tmp) / f"{name}.svg"
                self.assertTrue(svg_path.exists())
                root = ET.parse(svg_path).getroot()
                self.assertEqual(root.attrib["viewBox"], "0 0 256 256")
                self.assertIn("aria-labelledby", root.attrib)

            manifest = json.loads((Path(tmp) / "manifest.json").read_text(encoding="utf-8"))
            self.assertEqual(manifest["source"], "generated")
            self.assertEqual([item["name"] for item in manifest["icons"]], ["ai", "document", "house", "pencil", "shield"])
            self.assertEqual(
                [item["file"] for item in manifest["icons"]],
                ["ai.svg", "document.svg", "house.svg", "pencil.svg", "shield.svg"],
            )
            self.assertEqual(manifest["color"], "#000091")

    def test_unknown_icon_fails_clearly(self):
        with tempfile.TemporaryDirectory() as tmp:
            result = subprocess.run(
                [
                    sys.executable,
                    "-B",
                    str(SCRIPT),
                    "--source",
                    "generated",
                    "--icons",
                    "documnt",
                    "--output-dir",
                    tmp,
                ],
                text=True,
                capture_output=True,
            )

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("Picto inconnu", result.stderr)
            self.assertIn("document", result.stderr)

    def test_lists_known_dsfr_artwork_names(self):
        result = subprocess.run(
            [sys.executable, "-B", str(SCRIPT), "--list-dsfr-names"],
            check=True,
            text=True,
            capture_output=True,
        )

        self.assertIn("digital/application", result.stdout)
        self.assertIn("health/doctor", result.stdout)
        self.assertIn("map/map-pin", result.stdout)
        self.assertIn("system/warning", result.stdout)
        self.assertEqual(len(result.stdout.strip().splitlines()), 102)

    def test_cli_help_describes_current_generation_modes(self):
        result = subprocess.run(
            [sys.executable, "-B", str(SCRIPT), "--help"],
            check=True,
            text=True,
            capture_output=True,
        )

        self.assertIn("Reproduire, copier ou générer des pictogrammes SVG", result.stdout)
        self.assertIn("dsfr-artwork", result.stdout)
        self.assertIn("dsfr-replica", result.stdout)

    def test_embeds_actionable_dsfr_style_guide(self):
        guide = STYLE_GUIDE.read_text(encoding="utf-8")
        required = [
            'viewBox="0 0 80 80"',
            "artwork-decorative",
            "artwork-minor",
            "artwork-major",
            "#ECECFF",
            "#E1000F",
            "#000091",
            "formes remplies",
            "ne pas utiliser `stroke-width`",
            "trois références officielles",
            "multiples de `4` ou `8`",
            "60 / 30 / 10",
            "80 px, 40 px et 24 px",
            "Signature visuelle DSFR",
            "audit_original_pictos.py",
            "icône de bibliothèque",
            "Pipeline de prompt DSFR-like",
            "Prompt1 interne",
            "dsfr-prompt-profile.json",
            "borrowed_grammar",
            "concept_metaphor",
            "unique_minor_accent",
            "series_difference",
            "puce électronique",
            "motif rouge réutilisé",
            "primary_archetype",
            "preserved_grammar",
            "semantic_delta",
            "path_edit_budget",
            "visual_delta_check",
            "archétype d’abord",
            "dsfr-grammar-transplant",
            "Grille de maturité production",
            "dsfr_native_feel",
            "semantic_delta_integration",
            "red_accent_sobriety",
            "small_size_legibility",
            "standalone_usability",
            "production-candidate",
            "PNG référence d’abord",
            "png_reference_role",
            "selected_png_candidate",
            "visual_features_to_preserve",
            "raster_features_to_discard",
            "native_svg_reconstruction",
            "autotrace",
            "PNG embarqué",
            "planche PNG",
            "SVG natif",
        ]
        for marker in required:
            self.assertIn(marker, guide)

    def test_embeds_dsfr_prompt_profile_for_originals(self):
        profile = json.loads(PROMPT_PROFILE.read_text(encoding="utf-8"))
        skill = (Path(__file__).resolve().parents[1] / "SKILL.md").read_text(encoding="utf-8")
        guide = STYLE_GUIDE.read_text(encoding="utf-8")
        prompt1_keys = [
            "concept",
            "official_status",
            "official_references",
            "major_subject",
            "minor_accent",
            "decorative_role",
            "composition_80x80",
            "path_strategy",
            "density_targets",
            "validation",
        ]

        self.assertEqual(profile["id"], "dsfr-pictogram-prompt-profile-v1")
        self.assertIn("prompt_core", profile)
        self.assertIn("visual_signature", profile)
        self.assertIn("concept_specificity", profile)
        self.assertIn("archetype_first", profile)
        self.assertIn("png_reference_first", profile)
        self.assertIn("production_maturity", profile)
        self.assertIn("avoid", profile)
        self.assertIn("quality_checkpoints", profile)
        self.assertIn("prompt_pipeline", profile)
        self.assertEqual(profile["prompt_pipeline"]["prompt1_keys"], prompt1_keys)
        self.assertEqual(
            profile["concept_specificity"]["required_fields"],
            ["borrowed_grammar", "concept_metaphor", "unique_minor_accent", "series_difference"],
        )
        self.assertEqual(
            profile["archetype_first"]["required_fields"],
            ["primary_archetype", "preserved_grammar", "semantic_delta", "path_edit_budget", "visual_delta_check"],
        )
        self.assertEqual(
            profile["png_reference_first"]["required_fields"],
            [
                "png_reference_role",
                "selected_png_candidate",
                "visual_features_to_preserve",
                "raster_features_to_discard",
                "native_svg_reconstruction",
            ],
        )
        self.assertEqual(
            profile["production_maturity"]["criteria"],
            [
                "dsfr_native_feel",
                "semantic_delta_integration",
                "red_accent_sobriety",
                "small_size_legibility",
                "standalone_usability",
            ],
        )
        for key in prompt1_keys:
            self.assertIn(key, skill)
            self.assertIn(key, guide)
        for field in profile["concept_specificity"]["required_fields"]:
            self.assertIn(field, skill)
            self.assertIn(field, guide)
        for field in profile["archetype_first"]["required_fields"]:
            self.assertIn(field, skill)
            self.assertIn(field, guide)
        for field in profile["png_reference_first"]["required_fields"]:
            self.assertIn(field, skill)
            self.assertIn(field, guide)
        for forbidden in [
            "stroke-width",
            "rect",
            "circle",
            "icône de bibliothèque recolorée",
            "même squelette géométrique pour toute une série",
            "motif rouge réutilisé",
            "assemblage libre de formes compatibles DSFR",
            "création sans primary_archetype",
            "autotrace comme livrable final",
            "PNG embarqué présenté comme SVG vectoriel DSFR",
            "artefact raster conservé dans le SVG final",
        ]:
            self.assertIn(forbidden, profile["avoid"])
        self.assertIn("ne jamais réutiliser le même motif rouge pour des concepts différents", profile["prompt_pipeline"]["prompt2_guardrails"])
        self.assertIn("préserver l'occupation, la densité et le rythme d'un primary_archetype pour les créations haute fidélité", profile["prompt_pipeline"]["prompt2_guardrails"])
        self.assertIn("utiliser le mode PNG référence d'abord seulement comme référence de rendu, puis reconstruire en SVG DSFR natif", profile["prompt_pipeline"]["prompt2_guardrails"])
        self.assertIn("ne jamais livrer un autotrace ou un PNG embarqué comme pictogramme SVG de production", profile["prompt_pipeline"]["prompt2_guardrails"])
        self.assertIn("series_difference distingue les pictogrammes d'une même série", profile["quality_checkpoints"]["semantic_markers"])
        self.assertIn("primary_archetype utilisé comme patron de rendu haute fidélité", profile["quality_checkpoints"]["style_markers"])
        self.assertIn("mode PNG référence d'abord utilisé seulement comme référence de direction artistique", profile["quality_checkpoints"]["style_markers"])
        self.assertIn("selected_png_candidate documente le candidat PNG retenu quand le mode PNG référence d'abord est utilisé", profile["quality_checkpoints"]["semantic_markers"])
        self.assertIn("production_score renseigné pour les créations visant la production", profile["quality_checkpoints"]["style_markers"])
        self.assertIn("dsfr-grammar-transplant", skill)
        self.assertIn("dsfr-grammar-transplant", guide)
        self.assertIn("PNG référence d’abord", skill)
        self.assertIn("PNG référence d’abord", guide)
        self.assertIn("SVG natif reconstruit", skill)
        self.assertIn("production_score", skill)

    def test_builds_svg_preview_contact_sheet(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "pictos"
            root.mkdir()
            (root / "sample.svg").write_text(dsfr_fixture(), encoding="utf-8")
            output = Path(tmp) / "preview.html"

            result = subprocess.run(
                [
                    sys.executable,
                    "-B",
                    str(PREVIEW_SCRIPT),
                    "--svg-root",
                    str(root),
                    "--output",
                    str(output),
                ],
                check=True,
                text=True,
                capture_output=True,
            )

            html = output.read_text(encoding="utf-8")
            self.assertIn("Prévisualisation des pictogrammes SVG DSFR", html)
            self.assertIn("sample.svg", html)
            self.assertIn("80 px", html)
            self.assertIn("40 px", html)
            self.assertIn("24 px", html)
            self.assertIn("1 SVG", result.stdout)

    def test_builds_svg_preview_with_official_references(self):
        self.require_embedded_corpus()
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "pictos"
            root.mkdir()
            (root / "heart.svg").write_text(dsfr_fixture(), encoding="utf-8")
            output = Path(tmp) / "preview.html"

            result = subprocess.run(
                [
                    sys.executable,
                    "-B",
                    str(PREVIEW_SCRIPT),
                    "--svg-root",
                    str(root),
                    "--references",
                    "health/health,system/success",
                    "--output",
                    str(output),
                ],
                check=True,
                text=True,
                capture_output=True,
            )

            html = output.read_text(encoding="utf-8")
            self.assertIn("Comparaison avec les références officielles", html)
            self.assertIn("health/health", html)
            self.assertIn("health-health.svg", html)
            self.assertIn("system/success", html)
            self.assertIn("system-success.svg", html)
            self.assertIn("1 SVG, 2 référence(s)", result.stdout)

    def test_svg_preview_excludes_official_corpus_by_default(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "pictos"
            official = root / "dsfr-officiels"
            official.mkdir(parents=True)
            (root / "sample.svg").write_text(dsfr_fixture(), encoding="utf-8")
            (official / "official.svg").write_text(dsfr_fixture(), encoding="utf-8")
            output = Path(tmp) / "preview.html"

            subprocess.run(
                [
                    sys.executable,
                    "-B",
                    str(PREVIEW_SCRIPT),
                    "--svg-root",
                    str(root),
                    "--output",
                    str(output),
                ],
                check=True,
                text=True,
                capture_output=True,
            )

            html = output.read_text(encoding="utf-8")
            self.assertIn("sample.svg", html)
            self.assertNotIn("official.svg", html)

    def test_svg_preview_unknown_reference_fails_clearly(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "pictos"
            root.mkdir()
            (root / "sample.svg").write_text(dsfr_fixture(), encoding="utf-8")

            result = subprocess.run(
                [
                    sys.executable,
                    "-B",
                    str(PREVIEW_SCRIPT),
                    "--svg-root",
                    str(root),
                    "--references",
                    "health/healt",
                    "--output",
                    str(Path(tmp) / "preview.html"),
                ],
                text=True,
                capture_output=True,
            )

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("Référence officielle inconnue : health/healt", result.stderr)
            self.assertIn("health/health", result.stderr)

    def test_copies_and_validates_official_dsfr_artwork_shape(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "dsfr-artwork" / "dist" / "artwork" / "pictograms"
            source = root / "digital"
            source.mkdir(parents=True)
            (source / "application.svg").write_text(dsfr_fixture(), encoding="utf-8")
            output = Path(tmp) / "out"

            subprocess.run(
                [
                    sys.executable,
                    "-B",
                    str(SCRIPT),
                    "--source",
                    "dsfr-artwork",
                    "--icons",
                    "digital/application",
                    "--dsfr-artwork-root",
                    str(Path(tmp) / "dsfr-artwork"),
                    "--output-dir",
                    str(output),
                ],
                check=True,
                text=True,
                capture_output=True,
            )

            copied = output / "digital-application.svg"
            self.assertTrue(copied.exists())
            manifest = json.loads((output / "manifest.json").read_text(encoding="utf-8"))
            self.assertEqual(manifest["source"], "dsfr-artwork")
            self.assertTrue(Path(manifest["source_root"]).is_absolute() and manifest["source_root"].endswith("dist/artwork/pictograms"), manifest["source_root"])
            self.assertEqual(manifest["icons"][0]["name"], "digital/application")
            self.assertEqual(manifest["icons"][0]["file"], "digital-application.svg")
            self.assertEqual(manifest["icons"][0]["source"], "digital/application.svg")
            self.assertRegex(manifest["icons"][0]["sha256"], r"^[a-f0-9]{64}$")

    def test_accepts_future_dsfr_name_when_file_exists(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "dist" / "artwork" / "pictograms" / "future"
            root.mkdir(parents=True)
            (root / "new-picto.svg").write_text(dsfr_fixture(), encoding="utf-8")

            subprocess.run(
                [
                    sys.executable,
                    "-B",
                    str(SCRIPT),
                    "--source",
                    "dsfr-artwork",
                    "--icons",
                    "future/new-picto",
                    "--dsfr-artwork-root",
                    str(Path(tmp)),
                    "--output-dir",
                    str(Path(tmp) / "out"),
                ],
                check=True,
                text=True,
                capture_output=True,
            )

            self.assertTrue((Path(tmp) / "out" / "future-new-picto.svg").exists())

    def test_resolves_dsfr_npm_package_from_project_root(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "node_modules" / "@gouvfr" / "dsfr" / "dist" / "artwork" / "pictograms" / "digital"
            root.mkdir(parents=True)
            (root / "application.svg").write_text(dsfr_fixture(), encoding="utf-8")

            subprocess.run(
                [
                    sys.executable,
                    "-B",
                    str(SCRIPT),
                    "--source",
                    "dsfr-artwork",
                    "--icons",
                    "digital/application",
                    "--dsfr-artwork-root",
                    str(Path(tmp)),
                    "--output-dir",
                    str(Path(tmp) / "out"),
                ],
                check=True,
                text=True,
                capture_output=True,
            )

            self.assertTrue((Path(tmp) / "out" / "digital-application.svg").exists())

    def test_rejects_dsfr_symbol_paths_with_fill_or_stroke(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "dist" / "artwork" / "pictograms" / "digital"
            root.mkdir(parents=True)
            (root / "application.svg").write_text(
                dsfr_fixture().replace('<path d="M8 8a1 1 0 1 1-2 0 1 1 0 0 1 2 0Z"/>', '<path fill="#fff" d="M8 8a1 1 0 1 1-2 0 1 1 0 0 1 2 0Z"/>'),
                encoding="utf-8",
            )

            result = subprocess.run(
                [
                    sys.executable,
                    "-B",
                    str(SCRIPT),
                    "--source",
                    "dsfr-artwork",
                    "--icons",
                    "digital/application",
                    "--dsfr-artwork-root",
                    str(Path(tmp)),
                    "--output-dir",
                    str(Path(tmp) / "out"),
                ],
                text=True,
                capture_output=True,
            )

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("attribut interdit fill", result.stderr)

    def test_accepts_official_dsfr_size_without_px(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "dist" / "artwork" / "pictograms" / "digital"
            root.mkdir(parents=True)
            (root / "smartphone.svg").write_text(dsfr_fixture(width="80", height="80"), encoding="utf-8")

            subprocess.run(
                [
                    sys.executable,
                    "-B",
                    str(SCRIPT),
                    "--source",
                    "dsfr-artwork",
                    "--icons",
                    "digital/smartphone",
                    "--dsfr-artwork-root",
                    str(Path(tmp)),
                    "--output-dir",
                    str(Path(tmp) / "out"),
                ],
                check=True,
                text=True,
                capture_output=True,
            )

            self.assertTrue((Path(tmp) / "out" / "digital-smartphone.svg").exists())

    def test_rejects_dsfr_svg_without_use_layers(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "dist" / "artwork" / "pictograms" / "digital"
            root.mkdir(parents=True)
            (root / "application.svg").write_text(dsfr_fixture(use_block=""), encoding="utf-8")

            result = subprocess.run(
                [
                    sys.executable,
                    "-B",
                    str(SCRIPT),
                    "--source",
                    "dsfr-artwork",
                    "--icons",
                    "digital/application",
                    "--dsfr-artwork-root",
                    str(Path(tmp)),
                    "--output-dir",
                    str(Path(tmp) / "out"),
                ],
                text=True,
                capture_output=True,
            )

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("trois <use>", result.stderr)

    def test_rejects_dsfr_svg_with_wrong_style_color(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "dist" / "artwork" / "pictograms" / "digital"
            root.mkdir(parents=True)
            (root / "application.svg").write_text(dsfr_fixture(style_minor="#FF0000"), encoding="utf-8")

            result = subprocess.run(
                [
                    sys.executable,
                    "-B",
                    str(SCRIPT),
                    "--source",
                    "dsfr-artwork",
                    "--icons",
                    "digital/application",
                    "--dsfr-artwork-root",
                    str(Path(tmp)),
                    "--output-dir",
                    str(Path(tmp) / "out"),
                ],
                text=True,
                capture_output=True,
            )

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("#E1000F", result.stderr)

    def test_replicates_embedded_official_svg_exactly(self):
        self.require_official_source()
        with tempfile.TemporaryDirectory() as tmp:
            subprocess.run(
                [
                    sys.executable,
                    "-B",
                    str(SCRIPT),
                    "--source",
                    "dsfr-replica",
                    "--icons",
                    "buildings/house",
                    "--output-dir",
                    tmp,
                ],
                check=True,
                text=True,
                capture_output=True,
            )

            source = self.official_svg("buildings-house.svg")
            output = Path(tmp) / "buildings-house.svg"
            self.assertEqual(output.read_bytes(), source.read_bytes())

            manifest = json.loads((Path(tmp) / "manifest.json").read_text(encoding="utf-8"))
            self.assertEqual(manifest["source"], "dsfr-replica")
            self.assertEqual(manifest["reproduction"], "exact-copy-from-embedded-official-corpus")
            self.assertEqual(manifest["icons"][0]["name"], "buildings/house")
            self.assertEqual(manifest["icons"][0]["file"], "buildings-house.svg")
            self.assertRegex(manifest["icons"][0]["sha256"], r"^[a-f0-9]{64}$")

    def test_replicates_all_embedded_official_svgs(self):
        self.require_embedded_corpus()
        with tempfile.TemporaryDirectory() as tmp:
            subprocess.run(
                [
                    sys.executable,
                    "-B",
                    str(SCRIPT),
                    "--source",
                    "dsfr-replica",
                    "--icons",
                    "all",
                    "--output-dir",
                    tmp,
                ],
                check=True,
                text=True,
                capture_output=True,
            )

            svg_files = sorted(Path(tmp).glob("*.svg"))
            manifest = json.loads((Path(tmp) / "manifest.json").read_text(encoding="utf-8"))
            self.assertEqual(len(svg_files), 102)
            self.assertEqual(len(manifest["icons"]), 102)
            for item in manifest["icons"]:
                source = OFFICIAL_CORPUS / item["replica_file"]
                output = Path(tmp) / item["file"]
                self.assertEqual(output.read_bytes(), source.read_bytes())
                self.assertRegex(item["sha256"], r"^[a-f0-9]{64}$")

    def test_analyzes_official_corpus_style_profile(self):
        self.require_embedded_corpus()
        with tempfile.TemporaryDirectory() as tmp:
            json_output = Path(tmp) / "profile.json"
            md_output = Path(tmp) / "profile.md"
            subprocess.run(
                [
                    sys.executable,
                    "-B",
                    str(ANALYZE_SCRIPT),
                    "--json-output",
                    str(json_output),
                    "--md-output",
                    str(md_output),
                ],
                check=True,
                text=True,
                capture_output=True,
            )

            profile = json.loads(json_output.read_text(encoding="utf-8"))
            self.assertEqual(profile["icon_count"], 102)
            self.assertEqual(profile["observed_sizes"]["80px x 80px"], 94)
            self.assertEqual(profile["observed_sizes"]["80 x 80"], 8)
            self.assertEqual(profile["symbol_order_counts"]["artwork-decorative > artwork-minor > artwork-major"], 102)
            self.assertEqual(profile["use_pattern_exceptions"][0]["name"], "system/system")
            self.assertIn("path_attribute_counts", profile)
            self.assertIn("numbers_per_icon", profile["layer_stats"]["artwork-major"])
            self.assertIn("p90", profile["layer_stats"]["artwork-major"]["commands_per_icon"])

    def test_audits_sparse_original_dsfr_like_icon(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            svg_path = root / "sample.svg"
            manifest_path = root / "manifest.json"
            svg_path.write_text(dsfr_fixture(), encoding="utf-8")
            manifest_path.write_text(
                json.dumps(
                    {
                        "official": False,
                        "references_inspected": ["health/health", "health/doctor", "system/success"],
                        "icons": [{"name": "sample", "file": "sample.svg", "reproduction": "original-dsfr-like"}],
                    },
                    ensure_ascii=False,
                ),
                encoding="utf-8",
            )

            result = subprocess.run(
                [
                    sys.executable,
                    "-B",
                    str(AUDIT_SCRIPT),
                    "--svg",
                    str(svg_path),
                    "--manifest",
                    str(manifest_path),
                    "--strict",
                ],
                text=True,
                capture_output=True,
            )

            self.assertEqual(result.returncode, 2)
            self.assertIn("AVERTISSEMENT", result.stdout)
            self.assertIn("artwork-major", result.stdout)

    def test_official_corpus_manifest_matches_embedded_files(self):
        self.require_embedded_corpus()
        manifest = json.loads((OFFICIAL_CORPUS / "manifest.json").read_text(encoding="utf-8"))
        icons = manifest["icons"]
        self.assertEqual(len(icons), 102)
        embedded = sorted(path.name for path in OFFICIAL_CORPUS.glob("*.svg"))
        self.assertEqual(sorted(item["file"] for item in icons), embedded)
        for item in icons:
            digest = hashlib.sha256((OFFICIAL_CORPUS / item["file"]).read_bytes()).hexdigest()
            self.assertEqual(digest, item["sha256"], item["file"])

    def test_style_profile_version_matches_source_declaration(self):
        source = (OFFICIAL_CORPUS / "SOURCE.md").read_text(encoding="utf-8")
        declared = re.search(r"@gouvfr/dsfr@([0-9.]+)", source)
        self.assertIsNotNone(declared)
        profile = json.loads(
            (Path(__file__).resolve().parents[1] / "references" / "dsfr-style-profile.json").read_text(encoding="utf-8")
        )
        self.assertEqual(profile["source_version"], declared.group(1))
        self.assertEqual(profile["icon_count"], 102)

    def load_analyze_module(self):
        return self.load_module(ANALYZE_SCRIPT)

    def test_path_geometry_handles_absolute_relative_and_curves(self):
        analyze = self.load_analyze_module()
        square = analyze.path_geometry("M10 10H30V30H10Z")
        self.assertEqual([round(v) for v in square["bbox"]], [10, 10, 30, 30])
        self.assertAlmostEqual(square["area"], 400, delta=1)
        relative = analyze.path_geometry("m10 10h20v20h-20z")
        self.assertEqual([round(v) for v in relative["bbox"]], [10, 10, 30, 30])
        disc = analyze.path_geometry("M8 8a1 1 0 1 1-2 0 1 1 0 0 1 2 0Z")
        self.assertEqual([round(v) for v in disc["bbox"]], [6, 7, 8, 9])
        self.assertAlmostEqual(disc["area"], math.pi, delta=0.2)
        cubic = analyze.path_geometry("M0 0C0 10 10 10 10 0")
        self.assertAlmostEqual(cubic["bbox"][3], 7.5, delta=0.1)
        self.assertEqual(analyze.path_geometry("M10 10H30V30H10ZM40 40h4v4h-4z")["subpaths"], 2)

    def test_style_profile_measures_layer_geometry_and_families(self):
        self.require_embedded_corpus()
        with tempfile.TemporaryDirectory() as tmp:
            json_output = Path(tmp) / "profile.json"
            md_output = Path(tmp) / "profile.md"
            subprocess.run(
                [sys.executable, "-B", str(ANALYZE_SCRIPT), "--json-output", str(json_output), "--md-output", str(md_output)],
                check=True,
                text=True,
                capture_output=True,
            )
            profile = json.loads(json_output.read_text(encoding="utf-8"))
            major = profile["layer_stats"]["artwork-major"]
            self.assertIn("bbox_pct_per_icon", major)
            self.assertTrue(20 <= major["bbox_pct_per_icon"]["median"] <= 90)
            self.assertIn("area_pct_per_icon", major)
            geometry = profile["icons"][0]["layers"]["artwork-major"]["geometry"]
            self.assertEqual(len(geometry["bbox"]), 4)
            self.assertIn("bbox_pct", geometry)
            self.assertEqual(profile["family_stats"]["document"]["count"], 20)
            self.assertIn("major_commands_median", profile["family_stats"]["document"])
            self.assertIn("integer_coordinate_share_pct", profile["layer_stats"]["artwork-major"])
            markdown = md_output.read_text(encoding="utf-8")
            self.assertIn("## Occupation du carré par calque", markdown)
            self.assertIn("grille de conception", markdown)

    def test_audit_reads_thresholds_from_profile_and_reports_occupation(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            svg_path = root / "sample.svg"
            svg_path.write_text(dsfr_fixture(), encoding="utf-8")
            profile = json.loads(
                (Path(__file__).resolve().parents[1] / "references" / "dsfr-style-profile.json").read_text(encoding="utf-8")
            )
            profile["layer_stats"]["artwork-major"]["commands_per_icon"]["p10"] = 999
            fake_profile = root / "profile.json"
            fake_profile.write_text(json.dumps(profile), encoding="utf-8")
            result = subprocess.run(
                [
                    sys.executable,
                    "-B",
                    str(AUDIT_SCRIPT),
                    "--svg",
                    str(svg_path),
                    "--references",
                    "health/health,health/doctor,system/success",
                    "--profile",
                    str(fake_profile),
                ],
                text=True,
                capture_output=True,
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("p10 officiel 999", result.stdout)
            self.assertIn("Occupation du carré par calque", result.stdout)
            self.assertIn("artwork-major=36 %", result.stdout)
            with tempfile.TemporaryDirectory() as sandbox:
                scripts_copy = Path(sandbox) / "scripts"
                shutil.copytree(Path(AUDIT_SCRIPT).parent, scripts_copy, ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))
                sandboxed = subprocess.run([sys.executable, str(scripts_copy / "audit_original_pictos.py"), "--svg", str(svg_path), "--references", "health/health,health/doctor,system/success", "--profile", str(fake_profile)], text=True, capture_output=True)
                self.assertIn(sandboxed.returncode, (0, 1, 2), sandboxed.stderr)
                self.assertFalse((scripts_copy / "__pycache__").exists(), "l'audit ne doit écrire aucun __pycache__ même lancé sans -B")

    def test_style_guide_defers_figures_to_profile(self):
        guide = STYLE_GUIDE.read_text(encoding="utf-8")
        self.assertNotIn("p10-médiane-p90", guide)
        self.assertIn("grille de conception", guide)
        self.assertIn("dsfr-style-profile.md", guide)

    @property
    def ANNOTATION_KEYS(self):
        cached = getattr(type(self), "_annotation_keys", None)
        if cached is None:
            cached = tuple(self.load_module(SCRIPT).ANNOTATION_KEYS)
            type(self)._annotation_keys = cached
        return cached

    def test_official_corpus_is_semantically_annotated(self):
        manifest = json.loads((OFFICIAL_CORPUS / "manifest.json").read_text(encoding="utf-8"))
        self.assertIn("annotation", manifest)
        for item in manifest["icons"]:
            for key in self.ANNOTATION_KEYS:
                self.assertTrue(str(item.get(key, "")).strip(), f"{item['name']} sans {key}")

    def test_replica_propagates_titles_and_descriptions(self):
        with tempfile.TemporaryDirectory() as tmp:
            corpus = Path(tmp) / "corpus"
            corpus.mkdir()
            (corpus / "buildings-house.svg").write_bytes((self.official_svg("buildings-house.svg")).read_bytes())
            (corpus / "manifest.json").write_text(
                json.dumps(
                    {
                        "icons": [
                            {
                                "name": "buildings/house",
                                "file": "buildings-house.svg",
                                "source": "buildings/house.svg",
                                "title": "Maison",
                                "description": "Maison avec toit et arbre ; fenêtre en accent.",
                                "major": "maison",
                                "minor": "fenêtre",
                                "decorative": "points périphériques",
                            }
                        ]
                    },
                    ensure_ascii=False,
                ),
                encoding="utf-8",
            )
            output = Path(tmp) / "out"
            subprocess.run(
                [sys.executable, "-B", str(SCRIPT), "--source", "dsfr-replica", "--replica-root", str(corpus), "--icons", "buildings/house", "--output-dir", str(output)],
                check=True,
                text=True,
                capture_output=True,
            )
            manifest = json.loads((output / "manifest.json").read_text(encoding="utf-8"))
            self.assertEqual(manifest["icons"][0]["title"], "Maison")
            self.assertEqual(manifest["icons"][0]["minor"], "fenêtre")

    def test_dsfr_artwork_refresh_preserves_annotations(self):
        with tempfile.TemporaryDirectory() as tmp:
            source = Path(tmp) / "dist" / "artwork" / "pictograms" / "buildings"
            source.mkdir(parents=True)
            (source / "house.svg").write_bytes((self.official_svg("buildings-house.svg")).read_bytes())
            output = Path(tmp) / "out"
            output.mkdir()
            (output / "manifest.json").write_text(
                json.dumps(
                    {
                        "annotation": {"status": "revue visuelle assistée", "date": "2026-08-28"},
                        "icons": [{"name": "buildings/house", "file": "buildings-house.svg", "title": "Maison", "description": "d", "major": "m", "minor": "n", "decorative": "p"}],
                    },
                    ensure_ascii=False,
                ),
                encoding="utf-8",
            )
            subprocess.run(
                [sys.executable, "-B", str(SCRIPT), "--source", "dsfr-artwork", "--dsfr-artwork-root", str(Path(tmp)), "--icons", "buildings/house", "--output-dir", str(output)],
                check=True,
                text=True,
                capture_output=True,
            )
            manifest = json.loads((output / "manifest.json").read_text(encoding="utf-8"))
            self.assertEqual(manifest["icons"][0]["title"], "Maison")
            self.assertEqual(manifest["annotation"]["date"], "2026-08-28")
            self.assertRegex(manifest["icons"][0]["sha256"], r"^[a-f0-9]{64}$")
            self.assertEqual(manifest["icons"][0]["sha256"], hashlib.sha256((output / "buildings-house.svg").read_bytes()).hexdigest(), "le sha256 doit être recalculé sur la copie, pas hérité")

    def test_prompt_profile_carries_worked_examples_from_official_corpus(self):
        profile = json.loads(PROMPT_PROFILE.read_text(encoding="utf-8"))
        manifest = json.loads((OFFICIAL_CORPUS / "manifest.json").read_text(encoding="utf-8"))
        by_name = {item["name"]: item for item in manifest["icons"]}
        examples = profile["worked_examples"]
        self.assertGreaterEqual(len(examples), 3)
        for example in examples:
            self.assertIn(example["official_reference"], by_name)
            for key in ("major_subject", "minor_accent", "decorative_role", "composition_80x80", "path_strategy", "density_targets"):
                self.assertTrue(str(example[key]).strip(), f"{example['official_reference']} sans {key}")
            self.assertEqual(example["major_subject"], by_name[example["official_reference"]]["major"])

    def test_svg_preview_captions_show_manifest_annotations(self):
        self.require_embedded_corpus()
        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp) / "preview.html"
            subprocess.run(
                [sys.executable, "-B", str(PREVIEW_SCRIPT), "--svg-root", str(OFFICIAL_CORPUS), "--include-official", "--captions", "--output", str(output)],
                check=True,
                text=True,
                capture_output=True,
            )
            page = output.read_text(encoding="utf-8")
            self.assertIn("Recherche", page)
            self.assertIn("loupe", page)
            self.assertIn("caption", page)

    def test_replica_minor_color_uses_dsfr_main_palette_only(self):
        self.require_official_source()
        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp) / "out"
            result = subprocess.run(
                [sys.executable, "-B", str(SCRIPT), "--source", "dsfr-replica", "--icons", "digital/search", "--minor-color", "green-emeraude-main-632", "--output-dir", str(output)],
                text=True,
                capture_output=True,
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            svg = (output / "digital-search.svg").read_text(encoding="utf-8")
            self.assertIn("#00A95F", svg.upper())
            self.assertNotIn("#E1000F", svg.upper())
            original = (self.official_svg("digital-search.svg")).read_text(encoding="utf-8")
            self.assertEqual(svg.replace("#00a95f", "#E1000F").replace("#00A95F", "#E1000F"), original)
            manifest = json.loads((output / "manifest.json").read_text(encoding="utf-8"))
            self.assertEqual(manifest["icons"][0]["minor_color"], "green-emeraude-main-632")
            self.assertEqual(manifest["icons"][0]["reproduction"], "exact-copy-minor-recolored")
            self.assertEqual(manifest["minor_color_source"], "@gouvfr/dsfr src/module/color/variable/_options.scss, valeur du thème clair")

            refused = subprocess.run(
                [sys.executable, "-B", str(SCRIPT), "--source", "dsfr-replica", "--icons", "digital/search", "--minor-color", "#123456", "--output-dir", str(Path(tmp) / "refused")],
                text=True,
                capture_output=True,
            )
            self.assertNotEqual(refused.returncode, 0)
            self.assertIn("palette DSFR", refused.stderr)

            low = subprocess.run(
                [sys.executable, "-B", str(SCRIPT), "--source", "dsfr-replica", "--icons", "digital/search", "--minor-color", "beige-gris-galet-main-702", "--output-dir", str(Path(tmp) / "low")],
                text=True,
                capture_output=True,
            )
            self.assertEqual(low.returncode, 0, low.stderr)
            self.assertIn("contraste", (low.stdout + low.stderr).lower())

    def test_replica_export_png_is_explicit_and_traced(self):
        self.require_official_source()
        if shutil.which("qlmanage") is None:
            self.skipTest("qlmanage absent sur ce poste")
        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp) / "out"
            result = subprocess.run(
                [sys.executable, "-B", str(SCRIPT), "--source", "dsfr-replica", "--icons", "system/success", "--export-png", "256", "--output-dir", str(output)],
                text=True,
                capture_output=True,
            )
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            png = output / "system-success-256.png"
            self.assertTrue(png.exists())
            self.assertEqual(png.read_bytes()[:8], b"\x89PNG\r\n\x1a\n")
            manifest = json.loads((output / "manifest.json").read_text(encoding="utf-8"))
            export = manifest["icons"][0]["raster_exports"][0]
            self.assertEqual(export["size"], 256)
            self.assertEqual(export["file"], "system-success-256.png")
            self.assertIn("renderer", export)

    def test_etalon_passes_strict_audit_and_is_reproducible(self):
        manifest = json.loads((ETALON / "manifest.json").read_text(encoding="utf-8"))
        self.assertIs(manifest["official"], False)
        self.assertEqual(manifest["status"], "production-candidate")
        self.assertRegex(manifest["icons"][0]["human_review"], r"^validé par ")
        self.assertEqual(manifest["icons"][0]["primary_archetype"], "map/compass")
        result = subprocess.run(
            [sys.executable, "-B", str(AUDIT_SCRIPT), "--svg", str(ETALON / "horloge.svg"), "--manifest", str(ETALON / "manifest.json"), "--strict"],
            text=True,
            capture_output=True,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertNotIn("AVERTISSEMENT", result.stdout)
        with tempfile.TemporaryDirectory() as tmp:
            builder = Path(tmp) / "build_horloge.py"
            builder.write_text((ETALON / "build_horloge.py").read_text(encoding="utf-8"), encoding="utf-8")
            subprocess.run([sys.executable, "-B", str(builder)], check=True, text=True, capture_output=True)
            self.assertEqual((Path(tmp) / "horloge.svg").read_bytes(), (ETALON / "horloge.svg").read_bytes())

    # --- Non-régression audit ShipGuard 2026-08-29, generate_pictos_svg.py ---

    @contextlib.contextmanager
    def unwritable_dir(self):
        if os.geteuid() == 0:
            self.skipTest("exécuté en root : aucun dossier n'est non inscriptible")
        with tempfile.TemporaryDirectory() as tmp:
            locked = Path(tmp) / "verrou"
            locked.mkdir()
            locked.chmod(0o500)
            try:
                yield locked
            finally:
                locked.chmod(0o700)

    def run_gen(self, *args, env=None):
        return subprocess.run([sys.executable, "-B", str(SCRIPT), *args], text=True, capture_output=True, env=env)

    def official_manifest(self):
        return json.loads((OFFICIAL_CORPUS / "manifest.json").read_text(encoding="utf-8"))

    def official_entry(self, filename):
        """Entrée du manifeste embarqué et version déclarée ; un nom inconnu ou une version absente est une erreur de test, pas un saut."""
        manifest = self.official_manifest()
        version = manifest.get("dsfr_version")
        if not isinstance(version, str) or not version:
            self.fail("le manifeste embarqué ne déclare pas dsfr_version")
        entry = next((item for item in manifest["icons"] if item["file"] == filename), None)
        if entry is None:
            self.fail(f"fixture inconnue du manifeste embarqué : {filename}")
        return entry, version

    def official_svg(self, filename):
        """SVG officiel de fixture : copie embarquée, sinon paquet officiel en cache, sinon test sauté."""
        embedded = OFFICIAL_CORPUS / filename
        if embedded.exists():
            return embedded
        entry, version = self.official_entry(filename)
        cache = Path(os.environ.get("DSFR_OFFICIAL_CACHE_DIR") or Path.home() / ".cache" / "dsfr-official-cache").expanduser()
        candidate = cache / f"gouvfr-dsfr-{version}" / "package" / "dist" / "artwork" / "pictograms" / entry["source"]
        if candidate.is_file():
            return candidate
        self.skipTest(f"corpus officiel absent : ni {embedded} ni {candidate}")

    def require_official_source(self):
        """Les tests qui copient un officiel exigent une source : SVG embarqués ou paquet officiel en cache."""
        if any(OFFICIAL_CORPUS.glob("*.svg")):
            return
        manifest = self.official_manifest()
        cache = Path(os.environ.get("DSFR_OFFICIAL_CACHE_DIR") or Path.home() / ".cache" / "dsfr-official-cache").expanduser()
        if not (cache / f"gouvfr-dsfr-{manifest.get('dsfr_version')}" / "package" / "dist" / "artwork" / "pictograms").is_dir():
            self.skipTest("aucune source officielle : ni SVG embarqués ni paquet officiel en cache (DSFR_OFFICIAL_CACHE_DIR)")

    def require_embedded_corpus(self):
        if not any(OFFICIAL_CORPUS.glob("*.svg")):
            self.skipTest("distribution sans SVG officiels embarqués : la reproduction est couverte par test_replica_resolves_official_svgs_from_cache")

    def make_corpus_without_svgs(self, tmp):
        """Manifeste embarqué copié seul : le cas d'une distribution qui ne redistribue pas les SVG officiels."""
        corpus = Path(tmp) / "corpus"
        corpus.mkdir()
        shutil.copy(OFFICIAL_CORPUS / "manifest.json", corpus / "manifest.json")
        return corpus

    def make_official_cache(self, tmp, filenames, mutate=None):
        """Cache officiel factice sous gouvfr-dsfr-<version>/package/dist/artwork/pictograms/<famille>/<nom>.svg."""
        root = Path(tmp) / "cache"
        for filename in filenames:
            entry, version = self.official_entry(filename)
            pictos = root / f"gouvfr-dsfr-{version}" / "package" / "dist" / "artwork" / "pictograms"
            target = pictos / entry["source"]
            target.parent.mkdir(parents=True, exist_ok=True)
            content = self.official_svg(filename).read_bytes()
            target.write_bytes(mutate(content) if mutate else content)
        return root

    def make_artwork_root(self, tmp, names=("digital/search", "digital/avatar", "buildings/house")):
        root = Path(tmp) / "dist" / "artwork" / "pictograms"
        for name in names:
            family, base = name.split("/")
            (root / family).mkdir(parents=True, exist_ok=True)
            (root / family / f"{base}.svg").write_bytes(self.official_svg(f"{family}-{base}.svg").read_bytes())
        return Path(tmp)

    def make_qlmanage_stub(self, tmp, body):
        bindir = Path(tmp) / "bin"
        bindir.mkdir()
        stub = bindir / "qlmanage"
        stub.write_text("#!/bin/sh\n" + body + "\n", encoding="utf-8")
        stub.chmod(stub.stat().st_mode | stat.S_IEXEC)
        env = dict(os.environ)
        env["PATH"] = f"{bindir}:{env['PATH']}"
        return env

    def test_minor_color_is_validated_before_any_write(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "out"
            result = self.run_gen("--source", "dsfr-replica", "--icons", "digital/search", "--minor-color", "couleur-bidon", "--output-dir", str(out))
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("palette DSFR", result.stderr)
            self.assertFalse(out.exists() and any(out.iterdir()), "aucun fichier ne doit être écrit avant la validation")

    def test_export_png_size_is_bounded(self):
        with tempfile.TemporaryDirectory() as tmp:
            for size in ("0", "-5", "5000"):
                result = self.run_gen("--source", "dsfr-replica", "--icons", "digital/search", "--export-png", size, "--output-dir", str(Path(tmp) / size.strip("-")))
                self.assertNotEqual(result.returncode, 0, size)
                self.assertIn("--export-png", result.stderr)
            self.assertFalse(any(Path(tmp).rglob("*.svg")))

    def test_prefix_cannot_escape_output_dir(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "out"
            for prefix in ("../evade-", "sub/", "a b"):
                result = self.run_gen("--source", "dsfr-replica", "--icons", "digital/search", "--prefix", prefix, "--output-dir", str(out))
                self.assertNotEqual(result.returncode, 0, prefix)
                self.assertIn("--prefix", result.stderr)
            self.assertFalse(list(Path(tmp).glob("evade-*")))

    def test_export_png_failure_keeps_manifest_truthful_and_diagnostic(self):
        self.require_official_source()
        with tempfile.TemporaryDirectory() as tmp:
            env = self.make_qlmanage_stub(tmp, "echo 'quicklook cassé' >&2; exit 1")
            out = Path(tmp) / "out"
            result = self.run_gen("--source", "dsfr-replica", "--icons", "system/success", "--minor-color", "green-emeraude-main-632", "--export-png", "128", "--output-dir", str(out), env=env)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("code 1", result.stdout + result.stderr)
            self.assertIn("quicklook cassé", result.stdout + result.stderr)
            manifest = json.loads((out / "manifest.json").read_text(encoding="utf-8"))
            icon = manifest["icons"][0]
            self.assertEqual(icon["reproduction"], "exact-copy-minor-recolored")
            self.assertEqual(icon["sha256"], hashlib.sha256((out / "system-success.svg").read_bytes()).hexdigest())

    def test_qlmanage_timeout_is_reported(self):
        self.require_official_source()
        with tempfile.TemporaryDirectory() as tmp:
            env = self.make_qlmanage_stub(tmp, "sleep 5")
            env["PICTOS_QLMANAGE_TIMEOUT"] = "1"
            out = Path(tmp) / "out"
            result = self.run_gen("--source", "dsfr-replica", "--icons", "system/success", "--export-png", "128", "--output-dir", str(out), env=env)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("délai", (result.stdout + result.stderr).lower())

    def test_partial_refresh_keeps_untouched_manifest_entries(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = self.make_artwork_root(tmp)
            out = Path(tmp) / "out"
            self.assertEqual(self.run_gen("--source", "dsfr-artwork", "--dsfr-artwork-root", str(root), "--icons", "all", "--output-dir", str(out)).returncode, 0)
            manifest = json.loads((out / "manifest.json").read_text(encoding="utf-8"))
            for icon in manifest["icons"]:
                icon["title"] = "Titre humain " + icon["name"]
            (out / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False), encoding="utf-8")
            result = self.run_gen("--source", "dsfr-artwork", "--dsfr-artwork-root", str(root), "--icons", "digital/search", "--output-dir", str(out))
            self.assertEqual(result.returncode, 0, result.stderr)
            refreshed = json.loads((out / "manifest.json").read_text(encoding="utf-8"))
            names = sorted(icon["name"] for icon in refreshed["icons"])
            self.assertEqual(names, ["buildings/house", "digital/avatar", "digital/search"])
            self.assertEqual({icon["name"]: icon["title"] for icon in refreshed["icons"]}["buildings/house"], "Titre humain buildings/house")
            out2 = Path(tmp) / "out2"
            self.assertEqual(self.run_gen("--source", "dsfr-replica", "--icons", "digital/search,buildings/house", "--output-dir", str(out2)).returncode, 0)
            self.assertEqual(self.run_gen("--source", "dsfr-replica", "--icons", "digital/search", "--output-dir", str(out2)).returncode, 0)
            self.assertEqual(len(json.loads((out2 / "manifest.json").read_text(encoding="utf-8"))["icons"]), 2)

    def test_replica_refresh_keeps_human_annotation_and_block(self):
        self.require_official_source()
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "out"
            self.assertEqual(self.run_gen("--source", "dsfr-replica", "--icons", "digital/search", "--output-dir", str(out)).returncode, 0)
            manifest = json.loads((out / "manifest.json").read_text(encoding="utf-8"))
            manifest["icons"][0]["title"] = "TITRE RELU PAR UN HUMAIN"
            manifest["annotation"] = {"status": "revue humaine"}
            (out / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False), encoding="utf-8")
            self.assertEqual(self.run_gen("--source", "dsfr-replica", "--icons", "digital/search", "--output-dir", str(out)).returncode, 0)
            refreshed = json.loads((out / "manifest.json").read_text(encoding="utf-8"))
            self.assertEqual(refreshed["icons"][0]["title"], "TITRE RELU PAR UN HUMAIN")
            self.assertEqual(refreshed["annotation"]["status"], "revue humaine")

    def test_corrupt_existing_manifest_refuses_to_overwrite(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "out"
            out.mkdir()
            (out / "manifest.json").write_text("{not json", encoding="utf-8")
            result = self.run_gen("--source", "dsfr-replica", "--icons", "digital/search", "--output-dir", str(out))
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("illisible", result.stderr)
            self.assertEqual((out / "manifest.json").read_text(encoding="utf-8"), "{not json")

    def test_generated_manifest_is_merged_with_dsfr_artwork(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = self.make_artwork_root(tmp)
            out = Path(tmp) / "out"
            self.assertEqual(self.run_gen("--source", "generated", "--icons", "document,ai", "--output-dir", str(out)).returncode, 0)
            result = self.run_gen("--source", "dsfr-artwork", "--dsfr-artwork-root", str(root), "--icons", "digital/search", "--output-dir", str(out))
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertNotIn("AVERTISSEMENT", result.stdout)
            manifest = json.loads((out / "manifest.json").read_text(encoding="utf-8"))
            self.assertEqual(manifest["source"], "mixed")
            self.assertEqual(manifest["sources"], ["dsfr-artwork", "generated"])
            self.assertIs(manifest["official"], False)
            by_file = {icon["file"]: icon for icon in manifest["icons"]}
            self.assertEqual(sorted(by_file), ["ai.svg", "digital-search.svg", "document.svg"])
            self.assertIs(by_file["digital-search.svg"]["official"], True)
            self.assertEqual(by_file["digital-search.svg"]["origin"], "dsfr-artwork")
            self.assertIs(by_file["ai.svg"]["official"], False)

    def test_icons_all_on_empty_corpus_fails_clearly(self):
        with tempfile.TemporaryDirectory() as tmp:
            corpus = Path(tmp) / "corpus"
            corpus.mkdir()
            (corpus / "manifest.json").write_text('{"icons": []}', encoding="utf-8")
            result = self.run_gen("--source", "dsfr-replica", "--replica-root", str(corpus), "--icons", "all", "--output-dir", str(Path(tmp) / "out"))
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("aucun pictogramme", result.stderr.lower())
            bad = Path(tmp) / "bad" / "Digital"
            bad.mkdir(parents=True)
            (bad / "App.svg").write_bytes((self.official_svg("digital-search.svg")).read_bytes())
            result = self.run_gen("--source", "dsfr-artwork", "--dsfr-artwork-root", str(Path(tmp) / "bad"), "--icons", "all", "--output-dir", str(Path(tmp) / "out2"))
            self.assertNotEqual(result.returncode, 0)

    def test_resolve_pictograms_dir_prefers_dsfr_package_over_stray_svg(self):
        with tempfile.TemporaryDirectory() as tmp:
            project = Path(tmp)
            (project / "docs").mkdir()
            (project / "docs" / "schema.svg").write_text("<svg xmlns='http://www.w3.org/2000/svg'/>", encoding="utf-8")
            pkg = project / "node_modules" / "@gouvfr" / "dsfr" / "dist" / "artwork" / "pictograms" / "digital"
            pkg.mkdir(parents=True)
            (pkg / "search.svg").write_bytes((self.official_svg("digital-search.svg")).read_bytes())
            result = self.run_gen("--source", "dsfr-artwork", "--dsfr-artwork-root", str(project), "--icons", "digital/search", "--output-dir", str(project / "out"))
            self.assertEqual(result.returncode, 0, result.stderr)

    def test_mid_batch_failure_leaves_no_orphan_copy(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = self.make_artwork_root(tmp, names=("digital/search",))
            avatar_dir = root / "dist" / "artwork" / "pictograms" / "digital"
            broken = (self.official_svg("digital-avatar.svg")).read_text(encoding="utf-8").replace("<path ", '<path fill="#000" ', 1)
            (avatar_dir / "avatar.svg").write_text(broken, encoding="utf-8")
            out = Path(tmp) / "out"
            result = self.run_gen("--source", "dsfr-artwork", "--dsfr-artwork-root", str(root), "--icons", "digital/search,digital/avatar", "--output-dir", str(out))
            self.assertNotEqual(result.returncode, 0)
            self.assertFalse((out / "digital-search.svg").exists(), "rien ne doit être copié si une source est invalide")

    def test_no_manifest_never_touches_existing_manifest(self):
        self.require_official_source()
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "out"
            out.mkdir()
            foreign = '{"source": "manifeste-etranger", "icons": [{"name": "autre/chose", "file": "autre.svg"}]}'
            (out / "manifest.json").write_text(foreign, encoding="utf-8")
            result = self.run_gen("--source", "dsfr-replica", "--icons", "digital/search", "--no-manifest", "--minor-color", "green-emeraude-main-632", "--output-dir", str(out))
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual((out / "manifest.json").read_text(encoding="utf-8"), foreign)
            self.assertIn("non tracé", result.stdout)

    def test_previous_png_exports_are_listed_in_manifest(self):
        self.require_official_source()
        if shutil.which("qlmanage") is None:
            self.skipTest("qlmanage absent")
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "out"
            for size in ("128", "256"):
                result = self.run_gen("--source", "dsfr-replica", "--icons", "system/success", "--export-png", size, "--output-dir", str(out))
                self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            manifest = json.loads((out / "manifest.json").read_text(encoding="utf-8"))
            sizes = sorted(export["size"] for export in manifest["icons"][0]["raster_exports"])
            self.assertEqual(sizes, [128, 256])

    def test_manifests_use_boolean_official_flags(self):
        corpus = json.loads((OFFICIAL_CORPUS / "manifest.json").read_text(encoding="utf-8"))
        self.assertTrue(all(item["official"] is True for item in corpus["icons"]))
        with tempfile.TemporaryDirectory() as tmp:
            root = self.make_artwork_root(tmp, names=("digital/search",))
            out = Path(tmp) / "out"
            self.assertEqual(self.run_gen("--source", "dsfr-artwork", "--dsfr-artwork-root", str(root), "--icons", "digital/search", "--output-dir", str(out)).returncode, 0)
            self.assertIs(json.loads((out / "manifest.json").read_text(encoding="utf-8"))["icons"][0]["official"], True)
            out2 = Path(tmp) / "out2"
            self.assertEqual(self.run_gen("--source", "dsfr-replica", "--icons", "digital/search", "--minor-color", "green-emeraude-main-632", "--output-dir", str(out2)).returncode, 0)
            icon = json.loads((out2 / "manifest.json").read_text(encoding="utf-8"))["icons"][0]
            self.assertIs(icon["official_reference"], True)
            self.assertIs(icon["official"], False)

    def test_validate_rejects_non_canonical_symbol_order(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = self.make_artwork_root(tmp, names=("system/success",))
            svg_path = root / "dist" / "artwork" / "pictograms" / "system" / "success.svg"
            text = svg_path.read_text(encoding="utf-8")
            blocks = re.findall(r"<symbol id=\"artwork-[a-z]+\">.*?</symbol>", text, re.S)
            self.assertEqual(len(blocks), 3)
            permuted = text.replace(blocks[0], "@@A@@").replace(blocks[2], blocks[0]).replace("@@A@@", blocks[2])
            svg_path.write_text(permuted, encoding="utf-8")
            result = self.run_gen("--source", "dsfr-artwork", "--dsfr-artwork-root", str(root), "--icons", "system/success", "--output-dir", str(Path(tmp) / "out"))
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("ordre", result.stderr.lower())

    def test_flattened_name_collision_is_refused(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "dist" / "artwork" / "pictograms"
            for name in ("a/b-c", "a-b/c"):
                family, base = name.split("/")
                (root / family).mkdir(parents=True, exist_ok=True)
                (root / family / f"{base}.svg").write_bytes((self.official_svg("digital-search.svg")).read_bytes())
            result = self.run_gen("--source", "dsfr-artwork", "--dsfr-artwork-root", str(Path(tmp)), "--icons", "all", "--output-dir", str(Path(tmp) / "out"))
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("collision", result.stderr.lower())

    def test_style_validation_rejects_unexpected_minor_color_before_recoloring(self):
        # La validation de style exige #E1000F avant toute recoloration : la branche « format non pris en charge »
        # de recolor_minor était inatteignable, elle n'existe plus.
        self.assertNotIn("pas au format #RRGGBB", SCRIPT.read_text(encoding="utf-8"))
        with tempfile.TemporaryDirectory() as tmp:
            corpus = Path(tmp) / "corpus"
            corpus.mkdir()
            (corpus / "system-success.svg").write_text((self.official_svg("system-success.svg")).read_text(encoding="utf-8").replace("#E1000F", "#E10"), encoding="utf-8")
            (corpus / "manifest.json").write_text(json.dumps({"icons": [{"name": "system/success", "file": "system-success.svg"}]}), encoding="utf-8")
            result = self.run_gen("--source", "dsfr-replica", "--replica-root", str(corpus), "--icons", "system/success", "--minor-color", "green-emeraude-main-632", "--output-dir", str(Path(tmp) / "out"))
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("ne déclare pas la couleur attendue #E1000F", result.stderr)
            self.assertFalse((Path(tmp) / "out" / "system-success.svg").exists(), "rien ne doit être écrit avant la validation")

    def test_main_reports_os_errors_cleanly(self):
        self.require_official_source()
        with self.unwritable_dir() as locked:
            result = self.run_gen("--source", "dsfr-replica", "--icons", "digital/search", "--output-dir", str(locked / "nope"))
        self.assertNotEqual(result.returncode, 0)
        self.assertNotIn("Traceback", result.stderr)
        self.assertIn("Permission denied", result.stderr)
        self.assertIn("verrou", result.stderr)

    def test_xml_with_doctype_is_refused(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = self.make_artwork_root(tmp, names=("digital/search",))
            svg_path = root / "dist" / "artwork" / "pictograms" / "digital" / "search.svg"
            svg_path.write_text('<!DOCTYPE svg [<!ENTITY x "y">]>\n' + svg_path.read_text(encoding="utf-8"), encoding="utf-8")
            result = self.run_gen("--source", "dsfr-artwork", "--dsfr-artwork-root", str(root), "--icons", "digital/search", "--output-dir", str(Path(tmp) / "out"))
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("DOCTYPE", result.stderr)

    # --- Non-régression audit ShipGuard 2026-08-29, analyze_dsfr_corpus.py et audit_original_pictos.py ---

    def load_module(self, script):
        """Charge un script comme module, sans laisser de trace dans sys.modules ni sys.path après le test."""
        previous_flag, previous_path = sys.dont_write_bytecode, list(sys.path)
        sys.dont_write_bytecode = True
        spec = importlib.util.spec_from_file_location(script.stem, script)
        module = importlib.util.module_from_spec(spec)
        sys.modules[spec.name] = module  # requis par dataclass avec annotations différées
        self.addCleanup(sys.modules.pop, spec.name, None)
        self.addCleanup(lambda: sys.path.__setitem__(slice(None), previous_path))
        self.addCleanup(setattr, sys, "dont_write_bytecode", previous_flag)
        spec.loader.exec_module(module)
        return module

    def test_path_geometry_rejects_malformed_paths_with_value_error(self):
        analyze = self.load_analyze_module()
        for bad in ("M10", "M0 0A5 5 0 1", "M0 0C0 10 10", "M10 L20 30 x"):
            with self.assertRaises(ValueError, msg=bad):
                analyze.path_geometry(bad)

    def test_path_geometry_accepts_compact_arc_flags(self):
        analyze = self.load_analyze_module()
        compact = analyze.path_geometry("M0 0a5 5 0 11.5 2")
        spaced = analyze.path_geometry("M0 0a5 5 0 1 1 .5 2")
        self.assertEqual(compact["bbox"], spaced["bbox"])

    def test_integer_share_counts_coordinates_only(self):
        analyze = self.load_analyze_module()
        self.assertEqual(analyze.symbol_geometry(["M0 0a1 1 0 1 1 2 0Z"])["integer_share_pct"], 100.0)
        self.assertEqual(analyze.symbol_geometry(["M0.5 0a1 1 0 1 1 2.5 0Z"])["integer_share_pct"], 50.0)

    def test_read_manifest_and_analyze_icon_report_clean_errors(self):
        analyze = self.load_analyze_module()
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "manifest.json").write_text("[]", encoding="utf-8")
            with self.assertRaises(ValueError):
                analyze.read_manifest(root)
            (root / "manifest.json").write_text("{not json", encoding="utf-8")
            with self.assertRaises(ValueError):
                analyze.read_manifest(root)
            with self.assertRaises(ValueError):
                analyze.analyze_icon(root, {"nom": "x"})
            with self.assertRaises(ValueError):
                analyze.analyze_icon(root, {"name": "a/b", "file": "../evade.svg"})

    def test_percentile_rounds_half_up_consistently(self):
        analyze = self.load_analyze_module()
        stats = analyze.summarize_numbers([10, 20, 30])
        self.assertEqual((stats["p25"], stats["p75"]), (20, 30))
        self.assertEqual(analyze.summarize_numbers([1, 2, 3, 4, 5])["p25"], 2)

    def test_build_profile_handles_empty_corpus(self):
        analyze = self.load_analyze_module()
        with tempfile.TemporaryDirectory() as tmp:
            (Path(tmp) / "manifest.json").write_text('{"icons": []}', encoding="utf-8")
            profile = analyze.build_profile(Path(tmp))
            self.assertEqual(profile["icon_count"], 0)
            self.assertIn("corpus_sha256", profile)

    def test_profile_outputs_default_to_skill_and_are_written_atomically(self):
        analyze = self.load_analyze_module()
        parser = analyze.build_parser()
        for option in ("json_output", "md_output"):
            default = Path(parser.get_default(option))
            self.assertTrue(default.is_absolute(), option)
            self.assertEqual(default.parent.name, "references")
        with tempfile.TemporaryDirectory() as tmp:
            json_path, md_path = Path(tmp) / "p.json", Path(tmp) / "p.md"
            with self.assertRaises(KeyError):
                analyze.write_outputs({"source": "x"}, json_path, md_path)
            self.assertFalse(json_path.exists(), "le JSON ne doit pas être écrit si le Markdown échoue")

    def test_committed_profile_matches_regeneration(self):
        self.require_embedded_corpus()
        analyze = self.load_analyze_module()
        committed = json.loads((Path(__file__).resolve().parents[1] / "references" / "dsfr-style-profile.json").read_text(encoding="utf-8"))
        fresh = analyze.build_profile(OFFICIAL_CORPUS)
        for volatile in ("analysis_date",):
            committed.pop(volatile, None)
            fresh.pop(volatile, None)
        self.assertEqual(committed, fresh, "profil committé désynchronisé : régénérer avec scripts/analyze_dsfr_corpus.py")

    def test_audit_import_does_not_shadow_stdlib(self):
        self.load_module(AUDIT_SCRIPT)
        resolved = [Path(entry).resolve() for entry in sys.path if entry]
        stdlib = Path(os.__file__).resolve().parent
        scripts_dir = AUDIT_SCRIPT.parent.resolve()
        self.assertIn(scripts_dir, resolved)
        self.assertIn(stdlib, resolved)
        self.assertGreater(resolved.index(scripts_dir), resolved.index(stdlib), "scripts/ doit rester après la bibliothèque standard")

    def test_audit_reference_medians_skip_missing_and_use_true_median(self):
        audit = self.load_module(AUDIT_SCRIPT)
        profile = {"icons": [
            {"name": "a", "layers": {"artwork-major": {"commands": 10, "geometry": {"bbox_pct": 10}}}},
            {"name": "b", "layers": {"artwork-major": {"commands": 30, "geometry": {"bbox_pct": 30}}}},
            {"name": "c", "layers": {"artwork-major": {"geometry": {"bbox_pct": 50}}}},
            {"name": "d", "layers": {"artwork-major": {"commands": 20, "geometry": {"bbox_pct": 20}}}},
        ]}
        medians = audit.official_reference_medians(profile, ["a", "b", "c", "d"], "commands")
        self.assertEqual(medians["artwork-major"], 20)
        self.assertEqual(audit.official_reference_medians(profile, ["a", "b", "c", "d"], "bbox_pct")["artwork-major"], 25)

    def run_audit(self, *args):
        return subprocess.run([sys.executable, "-B", str(AUDIT_SCRIPT), *args], text=True, capture_output=True)

    def test_audit_exit_codes_distinguish_findings_and_crashes(self):
        with tempfile.TemporaryDirectory() as tmp:
            svg = Path(tmp) / "bad.svg"
            svg.write_text(dsfr_fixture().replace('d="M16 16h48v48H16z"', 'd="M16"'), encoding="utf-8")
            result = self.run_audit("--svg", str(svg), "--references", "health/health,health/doctor,system/success")
            self.assertEqual(result.returncode, 1, result.stderr)
            self.assertNotIn("Traceback", result.stderr)
            self.assertIn("chemin", result.stderr.lower())
            missing = self.run_audit("--svg", str(svg), "--manifest", str(Path(tmp) / "absent.json"))
            self.assertEqual(missing.returncode, 3)
            self.assertNotIn("Traceback", missing.stderr)
            broken = Path(tmp) / "broken.json"
            broken.write_text("{nope", encoding="utf-8")
            self.assertEqual(self.run_audit("--svg", str(svg), "--manifest", str(broken)).returncode, 3)

    def test_audit_official_guard_holds_for_empty_manifest(self):
        with tempfile.TemporaryDirectory() as tmp:
            empty = Path(tmp) / "m.json"
            empty.write_text("{}", encoding="utf-8")
            result = self.run_audit("--svg", str(ETALON / "horloge.svg"), "--manifest", str(empty), "--references", "map/compass,system/success,digital/calendar")
            self.assertEqual(result.returncode, 1)
            self.assertIn("official: false", result.stderr)

    def test_audit_refuses_exact_official_copy_declared_original(self):
        with tempfile.TemporaryDirectory() as tmp:
            copy = Path(tmp) / "mon-original.svg"
            copy.write_bytes((self.official_svg("buildings-house.svg")).read_bytes())
            manifest = Path(tmp) / "m.json"
            manifest.write_text(json.dumps({"official": False, "references_inspected": ["buildings/school", "buildings/city-hall", "system/success"]}), encoding="utf-8")
            result = self.run_audit("--svg", str(copy), "--manifest", str(manifest), "--strict")
            self.assertEqual(result.returncode, 1)
            self.assertIn("buildings/house", result.stderr)

    def test_audit_refuses_doctype_and_accepts_defs_like_validator(self):
        with tempfile.TemporaryDirectory() as tmp:
            doc = Path(tmp) / "doc.svg"
            doc.write_text('<!DOCTYPE svg [<!ENTITY x "y">]>\n' + dsfr_fixture(), encoding="utf-8")
            self.assertEqual(self.run_audit("--svg", str(doc)).returncode, 1)
            defs = Path(tmp) / "defs.svg"
            text = dsfr_fixture()
            first = text.index("<symbol"); last = text.index("<use")
            defs.write_text(text[:first] + "<defs>\n" + text[first:last] + "</defs>\n" + text[last:], encoding="utf-8")
            result = self.run_audit("--svg", str(defs), "--references", "health/health,health/doctor,system/success")
            self.assertEqual(result.returncode, 0, result.stderr)

    def test_calibration_flags_at_most_ten_officials_with_same_family_references(self):
        self.require_embedded_corpus()
        # Un officiel audité tel quel sort toujours en code 1 (copie exacte refusée) : la calibration
        # géométrique se lit donc dans les AVERTISSEMENT imprimés, jamais dans le code de sortie.
        manifest = json.loads((OFFICIAL_CORPUS / "manifest.json").read_text(encoding="utf-8"))
        by_family = {}
        for item in manifest["icons"]:
            by_family.setdefault(item["name"].split("/")[0], []).append(item)
        flagged, evaluated = [], 0
        with tempfile.TemporaryDirectory() as tmp:
            for family, items in by_family.items():
                for item in items:
                    refs = [other["name"] for other in items if other["name"] != item["name"]][:3]
                    if len(refs) < 3:
                        refs += [name for name in ("system/success", "digital/search", "document/document") if name not in refs][: 3 - len(refs)]
                    declared = Path(tmp) / "m.json"
                    declared.write_text(json.dumps({"official": False, "references_inspected": refs}), encoding="utf-8")
                    result = self.run_audit("--svg", str(OFFICIAL_CORPUS / item["file"]), "--manifest", str(declared), "--strict")
                    self.assertEqual(result.returncode, 1, f"{item['name']} : copie exacte attendue en code 1\n{result.stderr}")
                    self.assertIn("copie exacte du pictogramme officiel", result.stderr)
                    self.assertIn("Occupation du carré par calque", result.stdout, "la calibration doit être évaluée malgré l'erreur")
                    evaluated += 1
                    if re.search(r"^AVERTISSEMENT : artwork-(major|minor) ", result.stdout, re.M):
                        flagged.append(item["name"])
        self.assertEqual(evaluated, len(manifest["icons"]))
        self.assertLessEqual(len(flagged), 10, f"{len(flagged)} officiels signalés par la calibration : {flagged[:12]}")

    # --- Non-régression audit ShipGuard 2026-08-29, build_svg_preview.py et build_horloge.py ---

    def run_preview(self, *args, env=None):
        return subprocess.run([sys.executable, "-B", str(PREVIEW_SCRIPT), *args], text=True, capture_output=True, env=env)

    def test_preview_sizes_are_bounded_and_validated(self):
        preview = self.load_module(PREVIEW_SCRIPT)
        with self.assertRaises(argparse.ArgumentTypeError):
            preview.parse_sizes("999999")
        with self.assertRaises(argparse.ArgumentTypeError):
            preview.parse_sizes("abc")
        self.assertEqual(preview.parse_sizes("80,40"), (80, 40))

    def test_preview_explains_official_exclusion(self):
        self.require_embedded_corpus()
        with tempfile.TemporaryDirectory() as tmp:
            result = self.run_preview("--svg-root", str(OFFICIAL_CORPUS), "--output", str(Path(tmp) / "p.html"))
            self.assertEqual(result.returncode, 1)
            self.assertIn("--include-official", result.stderr)

    def test_preview_reports_bad_manifest_cleanly(self):
        with tempfile.TemporaryDirectory() as tmp:
            corpus = Path(tmp) / "corpus"
            corpus.mkdir()
            (corpus / "manifest.json").write_text("[]", encoding="utf-8")
            (corpus / "a.svg").write_bytes((self.official_svg("digital-search.svg")).read_bytes())
            result = self.run_preview("--svg-root", str(Path(tmp) / "corpus"), "--official-root", str(corpus), "--references", "digital/search", "--output", str(Path(tmp) / "p.html"))
            self.assertEqual(result.returncode, 1)
            self.assertNotIn("Traceback", result.stderr)
            (corpus / "manifest.json").write_text(json.dumps({"icons": [{"name": "digital/search", "file": "../evade.svg"}]}), encoding="utf-8")
            result = self.run_preview("--svg-root", str(corpus), "--official-root", str(corpus), "--references", "digital/search", "--output", str(Path(tmp) / "p.html"))
            self.assertEqual(result.returncode, 1)
            self.assertNotIn("Traceback", result.stderr)

    def test_preview_captions_fail_loudly_on_corrupt_manifest_and_warn_when_absent(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "svgs"
            root.mkdir()
            (root / "a.svg").write_bytes((self.official_svg("digital-search.svg")).read_bytes())
            absent = self.run_preview("--svg-root", str(root), "--captions", "--output", str(Path(tmp) / "p.html"))
            self.assertEqual(absent.returncode, 0, absent.stderr)
            self.assertIn("AVERTISSEMENT", absent.stdout + absent.stderr)
            (root / "manifest.json").write_text("{corrompu", encoding="utf-8")
            broken = self.run_preview("--svg-root", str(root), "--captions", "--output", str(Path(tmp) / "p2.html"))
            self.assertEqual(broken.returncode, 1)
            self.assertNotIn("Traceback", broken.stderr)

    def test_preview_captions_are_labelled_and_accessible(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "svgs"
            root.mkdir()
            (root / "a#1.svg").write_bytes((self.official_svg("digital-search.svg")).read_bytes())
            (root / "b.svg").write_bytes((self.official_svg("system-success.svg")).read_bytes())
            (root / "manifest.json").write_text(json.dumps({"icons": [
                {"name": "x/a", "file": "a#1.svg", "title": "Titre A", "description": "Description seule utile."},
                {"name": "x/b", "file": "b.svg", "title": "Titre B", "major": "cercle", "minor": "coche"}]}), encoding="utf-8")
            out = Path(tmp) / "p.html"
            result = self.run_preview("--svg-root", str(root), "--captions", "--references", "digital/search", "--output", str(out))
            self.assertEqual(result.returncode, 0, result.stderr)
            page = out.read_text(encoding="utf-8")
            self.assertIn("Description seule utile.", page)
            self.assertIn("sujet", page.lower())
            self.assertIn("accent rouge", page.lower())
            self.assertNotIn("<br> ; <span", page)
            self.assert_preview_page_is_accessible(page)
            self.assertIn('alt="Titre B, 80 px"', page)
            self.assertIn("a%231.svg", page)
            self.assertNotIn('alt=""', page)
            self.assertLess(page.index("comparison"), page.rindex("</main>"))

    def test_preview_main_reports_os_errors_cleanly(self):
        with self.unwritable_dir() as locked:
            result = self.run_preview("--svg-root", str(ETALON), "--output", str(locked / "nope" / "p.html"))
        self.assertEqual(result.returncode, 1)
        self.assertNotIn("Traceback", result.stderr)

    def test_preview_relative_href_refuses_absolute_fallback(self):
        preview = self.load_module(PREVIEW_SCRIPT)
        original = preview.os.path.relpath
        preview.os.path.relpath = lambda *a, **k: (_ for _ in ()).throw(ValueError("volumes"))
        try:
            with self.assertRaises(ValueError):
                preview.relative_href(Path("/a/b.svg"), Path("/c/out.html"))
        finally:
            preview.os.path.relpath = original

    def test_horloge_builder_normalizes_zero_and_guards_capsule(self):
        builder = self.load_module(ETALON / "build_horloge.py")
        self.assertEqual(builder.fmt(-0.0), "0")
        self.assertEqual(builder.fmt(-0.001), "0")
        with self.assertRaises(ValueError):
            builder.capsule(1, 1, 1, 1, 2)
        svg_text = (ETALON / "horloge.svg").read_text(encoding="utf-8")
        self.assertNotRegex(svg_text, r"-0(?![.\d])", "aucun zéro négatif résiduel, quel que soit le caractère qui suit")

    # --- Couverture des options CLI (audit ShipGuard r1-z01-034) ---

    def test_cli_option_bounds_and_modes(self):
        self.require_official_source()
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "out"
            stroke = self.run_gen("--source", "generated", "--icons", "document", "--stroke-width", "1", "--output-dir", str(out))
            self.assertEqual(stroke.returncode, 2)
            self.assertIn("--stroke-width doit être compris entre 2 et 18", stroke.stderr)
            size = self.run_gen("--source", "generated", "--icons", "document", "--size", "16", "--output-dir", str(out))
            self.assertEqual(size.returncode, 2)
            self.assertIn("--size doit être compris entre 32 et 2048", size.stderr)
            minor = self.run_gen("--source", "generated", "--icons", "document", "--minor-color", "green-emeraude-main-632", "--output-dir", str(out))
            self.assertEqual(minor.returncode, 2)
            self.assertIn("s'appliquent aux copies officielles", minor.stderr)
            for background in ("tile", "disk"):
                result = self.run_gen("--source", "generated", "--icons", "document", "--background", background, "--preset", "slides-ia", "--output-dir", str(out / background))
                self.assertEqual(result.returncode, 0, result.stderr)
                svg = (out / background / "document.svg").read_text(encoding="utf-8")
                self.assertIn("<rect" if background == "tile" else "<circle", svg)
            prefixed = self.run_gen("--source", "dsfr-replica", "--icons", "digital/search", "--prefix", "ok-", "--no-manifest", "--output-dir", str(out / "p"))
            self.assertEqual(prefixed.returncode, 0, prefixed.stderr)
            self.assertTrue((out / "p" / "ok-digital-search.svg").exists())
            self.assertFalse((out / "p" / "manifest.json").exists())
            listing = self.run_gen("--list")
            self.assertEqual(listing.returncode, 0)
            self.assertIn("document", listing.stdout)

    # --- Manifeste d'interface, source par défaut et mode generated (audit ShipGuard, zone infra) ---

    def test_openai_manifest_contract_and_twin_parity(self):
        source = Path(__file__).resolve().parents[1] / "agents" / "openai.yaml"
        text = source.read_text(encoding="utf-8")
        short_match = re.search(r'short_description: "(.*)"', text)
        prompt_match = re.search(r'default_prompt: "(.*)"', text)
        self.assertIsNotNone(short_match, "short_description absente du manifeste")
        self.assertIsNotNone(prompt_match, "default_prompt absent du manifeste")
        short, prompt = short_match.group(1), prompt_match.group(1)
        self.assertTrue(20 <= len(short) <= 64, len(short))
        self.assertLessEqual(len(prompt), 240, "une phrase : le plus long du parc était à 256")
        self.assertIn("official: false", prompt)
        self.assertIn("NOT VERIFIED: source officielle absente", prompt, "reprendre le code documenté, pas le préfixe nu")
        self.assertNotIn("policy:", text, "bloc policy non supporté par les runtimes : ne pas le déclarer")
        self.assertIn("generate_pictos_svg.py", prompt, "le prompt doit nommer le script porteur de --source")
        self.assertIn("audit_original_pictos.py", prompt, "le prompt doit nommer le script porteur de --strict")
        # Jumeaux : la racine vient de git, jamais d'un comptage de parents (un parents[3] a rendu ce contrôle mort).
        toplevel = subprocess.run(["git", "rev-parse", "--show-toplevel"], cwd=Path(__file__).parent, text=True, capture_output=True)
        if toplevel.returncode != 0:
            self.skipTest("skill distribué hors dépôt git : pas de jumeau .agents à comparer")
        twins_root = Path(toplevel.stdout.strip()) / ".agents" / "skills"
        if not twins_root.is_dir():
            self.skipTest(f"pas de dossier {twins_root} : jumeaux non gérés par ce dépôt")
        twin = twins_root / "generer-pictos-svg-dsfr" / "agents" / "openai.yaml"
        produced_twins = [twins_root / name / "agents" / "openai.yaml" for name in ("dsfr-components", "dsfr-changelog")]
        if not twin.exists() and not any(candidate.exists() for candidate in produced_twins):
            self.skipTest(f"{twins_root} n'héberge pas de jumeau .agents pour les skills produit (dossier réservé à d'autres skills) : parité non gérée par ce dépôt")
        self.assertTrue(twin.is_file(), f"jumeau attendu : {twin}")
        self.assertEqual(twin.read_text(encoding="utf-8"), text, "le jumeau .agents doit rester identique à la source")
        codex = Path.home() / ".codex" / "skills" / "generer-pictos-svg-dsfr" / "agents" / "openai.yaml"
        if codex.is_file():
            self.assertEqual(codex.read_text(encoding="utf-8"), text, "la copie Codex doit rester identique à la source")

    def test_default_source_is_official_corpus_and_generated_is_flagged(self):
        self.require_official_source()
        module = self.load_module(SCRIPT)
        self.assertEqual(module.build_parser().get_default("source"), "dsfr-replica")
        with tempfile.TemporaryDirectory() as tmp:
            result = self.run_gen("--source", "generated", "--icons", "document", "--output-dir", str(Path(tmp) / "g"))
            self.assertEqual(result.returncode, 0, result.stderr)
            manifest = json.loads((Path(tmp) / "g" / "manifest.json").read_text(encoding="utf-8"))
            self.assertIs(manifest["official"], False)
            self.assertEqual(manifest["reproduction"], "generated-legacy")
            default = self.run_gen("--icons", "digital/search", "--output-dir", str(Path(tmp) / "d"))
            self.assertEqual(default.returncode, 0, default.stderr)
            self.assertIn('viewBox="0 0 80 80"', (Path(tmp) / "d" / "digital-search.svg").read_text(encoding="utf-8"))

    def test_audit_reads_sibling_manifest_without_flag(self):
        refs = "health/health,health/doctor,system/success"
        with tempfile.TemporaryDirectory() as tmp:
            svg = Path(tmp) / "orig.svg"
            svg.write_text(dsfr_fixture(), encoding="utf-8")
            (Path(tmp) / "manifest.json").write_text(json.dumps({"official": True, "icons": [{"file": "orig.svg"}]}), encoding="utf-8")
            result = self.run_audit("--svg", str(svg), "--references", refs)
            self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
            self.assertIn("official: false", result.stdout + result.stderr)
            (Path(tmp) / "manifest.json").write_text(json.dumps({"official": False, "icons": [{"file": "orig.svg"}]}), encoding="utf-8")
            result = self.run_audit("--svg", str(svg), "--references", refs)
            self.assertNotIn("official: false", result.stdout + result.stderr)
            self.assertIn("manifest.json", result.stdout + result.stderr)
            # Un manifeste voisin qui ne décrit pas le SVG (copies officielles à côté d'une création) est ignoré.
            (Path(tmp) / "manifest.json").write_text(json.dumps({"official": True, "icons": [{"file": "autre.svg"}]}), encoding="utf-8")
            result = self.run_audit("--svg", str(svg), "--references", refs)
            self.assertNotIn("le manifeste doit déclarer official: false", result.stderr)
            self.assertIn("ignoré", result.stdout)

    def test_generated_mode_merges_existing_manifest_and_keeps_annotations(self):
        self.require_official_source()
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "mixte"
            self.assertEqual(self.run_gen("--source", "dsfr-replica", "--icons", "map/compass", "--output-dir", str(out)).returncode, 0)
            manifest_path = out / "manifest.json"
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            manifest["icons"][0]["title"] = "Boussole annotée à la main"
            manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
            result = self.run_gen("--source", "generated", "--icons", "document", "--output-dir", str(out))
            self.assertEqual(result.returncode, 0, result.stderr)
            merged = json.loads(manifest_path.read_text(encoding="utf-8"))
            files = {item["file"]: item for item in merged["icons"]}
            self.assertIn("map-compass.svg", files, "l'entrée dsfr-replica doit survivre à un run generated")
            self.assertEqual(files["map-compass.svg"]["title"], "Boussole annotée à la main")
            self.assertIs(files["map-compass.svg"]["official"], True)
            self.assertIs(files["document.svg"]["official"], False)
            self.assertEqual(files["document.svg"]["origin"], "generated")
            self.assertEqual(files["map-compass.svg"]["origin"], "dsfr-replica")
            self.assertEqual(merged["source"], "mixed", "un dossier qui mélange les sources ne doit pas mentir sur sa provenance")
            self.assertEqual(sorted(merged["sources"]), ["dsfr-replica", "generated"])
            self.assertIs(merged["official"], False)
            # Manifeste illisible : refusé, jamais écrasé, même en mode generated.
            manifest_path.write_text("{corrompu", encoding="utf-8")
            broken = self.run_gen("--source", "generated", "--icons", "ai", "--output-dir", str(out))
            self.assertNotEqual(broken.returncode, 0)
            self.assertEqual(manifest_path.read_text(encoding="utf-8"), "{corrompu")

    # --- Contre-audit ShipGuard du 2026-08-29, lot B (medium) ---

    def assert_preview_page_is_accessible(self, page):
        self.assertIn('<html lang="fr">', page)
        self.assertIn('<meta name="viewport"', page)
        body = page.split("<body>", 1)[1]
        before_main = body.split("<main>", 1)[0]
        self.assertRegex(before_main, r"<header>[\s\S]*<h1>[\s\S]*</h1>[\s\S]*</header>", "le titre et le résumé doivent vivre dans un point de repère")
        self.assertNotRegex(before_main.split("</header>", 1)[1], r"<(p|h\d|div)\b", "aucun contenu hors point de repère avant <main>")
        self.assertEqual(page.count("<h1>"), 1)
        for card in re.findall(r'<article class="card"[\s\S]*?</article>', page):
            alts = re.findall(r'alt="([^"]*)"', card)
            self.assertEqual(len(alts), len(set(alts)), f"alt dupliqués dans une carte : {alts}")
            for alt in alts:
                self.assertRegex(alt, r", \d+ px$", "chaque alt doit distinguer la taille rendue")

    def test_etalon_preview_is_reproducible_and_landmarked(self):
        self.require_embedded_corpus()
        etalon = Path(__file__).resolve().parents[1] / "pictos-svg" / "etalon"
        committed = (etalon / "preview.html").read_text(encoding="utf-8")
        self.assert_preview_page_is_accessible(committed)
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "etalon"
            root.mkdir()
            shutil.copy(etalon / "horloge.svg", root / "horloge.svg")
            shutil.copy(etalon / "manifest.json", root / "manifest.json")
            out = root / "preview.html"
            result = self.run_preview("--svg-root", str(root), "--captions", "--references", "map/compass,system/success,digital/calendar", "--output", str(out))
            self.assertEqual(result.returncode, 0, result.stderr)
            strip = lambda text: re.sub(r'src="[^"]*"', 'src="…"', text)
            self.assertEqual(strip(out.read_text(encoding="utf-8")), strip(committed), "la planche committée doit être la sortie réelle du générateur")

    def test_audit_rejects_malformed_calibration_profile_with_runtime_code(self):
        profile = json.loads((Path(__file__).resolve().parents[1] / "references" / "dsfr-style-profile.json").read_text(encoding="utf-8"))
        profile["audit_calibration"]["bbox_pct_range"]["artwork-major"] = [1, 2, 3]
        with tempfile.TemporaryDirectory() as tmp:
            bad = Path(tmp) / "profile.json"
            bad.write_text(json.dumps(profile), encoding="utf-8")
            svg = Path(tmp) / "orig.svg"
            svg.write_text(dsfr_fixture(), encoding="utf-8")
            result = self.run_audit("--svg", str(svg), "--references", "health/health,health/doctor,system/success", "--profile", str(bad))
            self.assertEqual(result.returncode, 3, result.stdout + result.stderr)
            self.assertIn("ERREUR D'EXÉCUTION", result.stderr)
            self.assertIn("audit_calibration", result.stderr)
            self.assertNotIn("Traceback", result.stderr)

    def test_manifest_source_root_is_the_resolved_root(self):
        self.require_official_source()
        with tempfile.TemporaryDirectory() as tmp:
            corpus = Path(tmp) / "corpus-copie"
            shutil.copytree(OFFICIAL_CORPUS, corpus)
            out = Path(tmp) / "out"
            self.assertEqual(self.run_gen("--source", "dsfr-replica", "--replica-root", str(corpus), "--icons", "map/compass", "--output-dir", str(out)).returncode, 0)
            self.assertEqual(json.loads((out / "manifest.json").read_text(encoding="utf-8"))["source_root"], str(corpus.resolve()))
            root = self.make_artwork_root(tmp)
            out2 = Path(tmp) / "out2"
            self.assertEqual(self.run_gen("--source", "dsfr-artwork", "--dsfr-artwork-root", str(root), "--icons", "digital/search", "--output-dir", str(out2)).returncode, 0)
            source_root = Path(json.loads((out2 / "manifest.json").read_text(encoding="utf-8"))["source_root"])
            self.assertTrue(source_root.is_absolute() and (source_root / "digital" / "search.svg").is_file(), source_root)
            self.assertTrue(str(source_root).startswith(str(Path(root).resolve())), source_root)

    def test_mixed_dsfr_sources_get_mixed_header(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = self.make_artwork_root(tmp)
            out = Path(tmp) / "out"
            self.assertEqual(self.run_gen("--source", "dsfr-artwork", "--dsfr-artwork-root", str(root), "--icons", "digital/search", "--output-dir", str(out)).returncode, 0)
            self.assertEqual(self.run_gen("--source", "dsfr-replica", "--icons", "map/compass", "--output-dir", str(out)).returncode, 0)
            manifest = json.loads((out / "manifest.json").read_text(encoding="utf-8"))
            self.assertEqual(manifest["source"], "mixed")
            self.assertEqual(manifest["sources"], ["dsfr-artwork", "dsfr-replica"])
            self.assertNotIn("reproduction", {k: v for k, v in manifest.items() if v == "exact-copy-from-embedded-official-corpus"})
            self.assertEqual({icon["file"]: icon["origin"] for icon in manifest["icons"]}, {"digital-search.svg": "dsfr-artwork", "map-compass.svg": "dsfr-replica"})

    def test_export_failure_still_lists_produced_svgs_and_exits_1(self):
        self.require_official_source()
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "out"
            env = {**os.environ, "PATH": str(Path(tmp) / "vide")}
            result = self.run_gen("--source", "dsfr-replica", "--icons", "map/compass,system/success", "--output-dir", str(out), "--export-png", "128", env=env)
            self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
            self.assertNotIn("usage:", result.stderr)
            self.assertIn("Export PNG incomplet", result.stderr)
            self.assertIn(str(out / "map-compass.svg"), result.stdout)
            self.assertIn(str(out / "system-success.svg"), result.stdout)

    def test_doctype_beyond_4096_bytes_is_refused_everywhere(self):
        payload = "<!-- " + "x" * 5000 + " -->\n<!DOCTYPE svg [<!ENTITY e \"boum\">]>\n" + dsfr_fixture().replace("<svg", "<svg data-e=\"&e;\"", 1)
        module = self.load_module(SCRIPT)
        with tempfile.TemporaryDirectory() as tmp:
            svg = Path(tmp) / "doctype.svg"
            svg.write_text(payload, encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "DOCTYPE"):
                module.validate_dsfr_artwork_svg(svg)
            audit = self.run_audit("--svg", str(svg), "--references", "health/health,health/doctor,system/success")
            self.assertEqual(audit.returncode, 1)
            self.assertIn("DOCTYPE", audit.stderr)
            corpus = Path(tmp) / "corpus"
            corpus.mkdir()
            (corpus / "system-success.svg").write_text(payload, encoding="utf-8")
            (corpus / "manifest.json").write_text(json.dumps({"icons": [{"name": "system/success", "file": "system-success.svg"}]}), encoding="utf-8")
            analysis = subprocess.run([sys.executable, "-B", str(ANALYZE_SCRIPT), "--corpus-root", str(corpus), "--json-output", str(Path(tmp) / "p.json"), "--md-output", str(Path(tmp) / "p.md")], text=True, capture_output=True)
            self.assertNotEqual(analysis.returncode, 0)
            self.assertIn("DOCTYPE", analysis.stderr)

    def test_qlmanage_timeout_env_is_validated(self):
        with tempfile.TemporaryDirectory() as tmp:
            env = self.make_qlmanage_stub(tmp, 'out=$(echo "$@" | sed "s/.*-o //;s/ .*//"); name=$(basename "$1" 2>/dev/null); exit 0')
            for value in ("abc", "0", "-5"):
                out = Path(tmp) / f"out-{value.strip('-')}"
                result = self.run_gen("--source", "dsfr-replica", "--icons", "map/compass", "--output-dir", str(out), "--export-png", "64", env={**env, "PICTOS_QLMANAGE_TIMEOUT": value})
                self.assertNotEqual(result.returncode, 0, value)
                self.assertIn("PICTOS_QLMANAGE_TIMEOUT", result.stderr, value)
                self.assertNotIn("Traceback", result.stderr)

    def test_corpus_analysis_refuses_missing_layer(self):
        self.require_embedded_corpus()
        with tempfile.TemporaryDirectory() as tmp:
            corpus = Path(tmp) / "corpus"
            corpus.mkdir()
            names = ["map/compass", "system/success", "digital/search", "buildings/house"]
            for name in names:
                file = name.replace("/", "-") + ".svg"
                shutil.copy(OFFICIAL_CORPUS / file, corpus / file)
            broken = corpus / "map-compass.svg"
            broken.write_text(broken.read_text(encoding="utf-8").replace('id="artwork-minor"', 'id="artwork-MINOR-casse"'), encoding="utf-8")
            (corpus / "manifest.json").write_text(json.dumps({"icons": [{"name": n, "file": n.replace("/", "-") + ".svg"} for n in names]}), encoding="utf-8")
            result = subprocess.run([sys.executable, "-B", str(ANALYZE_SCRIPT), "--corpus-root", str(corpus), "--json-output", str(Path(tmp) / "p.json"), "--md-output", str(Path(tmp) / "p.md")], text=True, capture_output=True)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("artwork-minor", result.stderr)
            self.assertIn("map-compass.svg", result.stderr)
            self.assertFalse((Path(tmp) / "p.json").exists(), "aucun profil ne doit être écrit sur un corpus corrompu")

    def test_corpus_analysis_handles_single_icon(self):
        with tempfile.TemporaryDirectory() as tmp:
            corpus = Path(tmp) / "corpus"
            corpus.mkdir()
            shutil.copy(self.official_svg("map-compass.svg"), corpus / "map-compass.svg")
            (corpus / "manifest.json").write_text(json.dumps({"icons": [{"name": "map/compass", "file": "map-compass.svg"}]}), encoding="utf-8")
            result = subprocess.run([sys.executable, "-B", str(ANALYZE_SCRIPT), "--corpus-root", str(corpus), "--json-output", str(Path(tmp) / "p.json"), "--md-output", str(Path(tmp) / "p.md")], text=True, capture_output=True)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("AVERTISSEMENT", result.stderr)
            profile = json.loads((Path(tmp) / "p.json").read_text(encoding="utf-8"))
            self.assertEqual(profile["audit_calibration"]["reference_command_ratio"], {})

    def test_output_dir_is_required_for_generation(self):
        with tempfile.TemporaryDirectory() as tmp:
            result = subprocess.run([sys.executable, "-B", str(SCRIPT), "--source", "dsfr-replica", "--icons", "map/compass"], text=True, capture_output=True, cwd=tmp)
            self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
            self.assertIn("--output-dir", result.stderr)
            self.assertEqual(sorted(p.name for p in Path(tmp).iterdir()), [], "rien ne doit être écrit dans le dossier courant")
            self.assertEqual(self.run_gen("--list").returncode, 0)
            self.assertEqual(self.run_gen("--list-dsfr-names").returncode, 0)

    def test_interrupted_recoloring_leaves_files_and_manifest_consistent(self):
        self.require_official_source()
        module = self.load_module(SCRIPT)
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "out"
            args = module.build_parser().parse_args(["--source", "dsfr-replica", "--icons", "map/compass,system/success", "--output-dir", str(out), "--minor-color", "green-emeraude-main-632"])
            generated = module.write_dsfr_replica_icons(args)
            before = {p.name: p.read_bytes() for p in out.iterdir()}
            calls = {"n": 0}
            real = module.validate_dsfr_artwork_svg

            def failing(svg_path, expected_fills=None):
                calls["n"] += 1
                if calls["n"] == 2:
                    raise ValueError("validation simulée en échec sur la deuxième icône")
                return real(svg_path, expected_fills=expected_fills)

            with unittest.mock.patch.object(module, "validate_dsfr_artwork_svg", failing):
                with self.assertRaisesRegex(ValueError, "deuxième icône"):
                    module.postprocess_dsfr_outputs(args, generated)
            after = {p.name: p.read_bytes() for p in out.iterdir()}
            self.assertEqual(after, before, "aucun fichier ne doit changer si la recoloration échoue en cours de route")

    def test_openai_manifest_parses_as_yaml(self):
        try:
            import yaml  # type: ignore[import-not-found]
        except ImportError:
            self.skipTest("PyYAML absent : structure du manifeste non vérifiée par un parseur")
        source = Path(__file__).resolve().parents[1] / "agents" / "openai.yaml"
        data = yaml.safe_load(source.read_text(encoding="utf-8"))
        self.assertEqual(set(data), {"interface"}, "seul le bloc interface est documenté par le schéma OpenAI")
        self.assertTrue({"display_name", "short_description", "default_prompt"} <= set(data["interface"]))
        self.assertTrue(all(isinstance(v, str) and v.strip() for v in data["interface"].values()))

    # --- Contre-audit ShipGuard du 2026-08-29, lot C (low) ---

    def test_render_options_are_refused_for_dsfr_sources(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "out"
            for option in (("--size", "999"), ("--stroke-width", "17"), ("--preset", "slides-ia"), ("--color", "#123456"), ("--background", "disk"), ("--accent", "#123456"), ("--background-color", "#ffffff")):
                result = self.run_gen("--source", "dsfr-replica", "--icons", "map/compass", "--output-dir", str(out), *option)
                self.assertEqual(result.returncode, 2, option)
                self.assertIn(option[0], result.stderr, option)
                self.assertIn("generated", result.stderr, option)
                self.assertFalse(out.exists(), "rien ne doit être écrit quand une option est refusée")

    def test_prefix_cannot_produce_hidden_files(self):
        with tempfile.TemporaryDirectory() as tmp:
            result = self.run_gen("--source", "dsfr-replica", "--icons", "map/compass", "--output-dir", str(Path(tmp) / "out"), "--prefix", ".")
            self.assertEqual(result.returncode, 2)
            self.assertIn("--prefix", result.stderr)
            self.assertFalse((Path(tmp) / "out" / ".map-compass.svg").exists())

    def test_duplicate_icon_names_are_collapsed(self):
        self.require_official_source()
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "out"
            result = self.run_gen("--source", "dsfr-replica", "--icons", "map/compass,map/compass", "--output-dir", str(out))
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(sorted(p.name for p in out.glob("*.svg")), ["map-compass.svg"])
            self.assertNotIn("Collision", result.stderr)

    def test_missing_manifest_during_postprocessing_is_an_error(self):
        self.require_official_source()
        module = self.load_module(SCRIPT)
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "out"
            args = module.build_parser().parse_args(["--source", "dsfr-replica", "--icons", "map/compass", "--output-dir", str(out), "--minor-color", "green-emeraude-main-632"])
            generated = module.write_dsfr_replica_icons(args)
            (out / "manifest.json").unlink()
            with self.assertRaisesRegex(ValueError, "manifest.json"):
                module.postprocess_dsfr_outputs(args, generated)

    def test_previous_png_renderer_survives_a_new_export(self):
        self.require_official_source()
        if shutil.which("qlmanage") is None:
            self.skipTest("qlmanage absent sur ce poste")
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "out"
            self.assertEqual(self.run_gen("--source", "dsfr-replica", "--icons", "system/success", "--output-dir", str(out), "--export-png", "64").returncode, 0)
            first = json.loads((out / "manifest.json").read_text(encoding="utf-8"))["icons"][0]["raster_exports"][0]["renderer"]
            self.assertNotIn("inconnu", first)
            self.assertEqual(self.run_gen("--source", "dsfr-replica", "--icons", "system/success", "--output-dir", str(out), "--export-png", "128").returncode, 0)
            exports = {e["size"]: e["renderer"] for e in json.loads((out / "manifest.json").read_text(encoding="utf-8"))["icons"][0]["raster_exports"]}
            self.assertEqual(exports[64], first, "le moteur tracé au premier export ne doit pas être dégradé")
            self.assertIn(128, exports)

    def test_official_file_given_directly_still_requires_include_official(self):
        self.require_embedded_corpus()
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "p.html"
            result = self.run_preview("--svg-root", str(self.official_svg("system-success.svg")), "--output", str(out))
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("--include-official", result.stderr)
            self.assertFalse(out.exists())
            ok = self.run_preview("--svg-root", str(self.official_svg("system-success.svg")), "--output", str(out), "--include-official")
            self.assertEqual(ok.returncode, 0, ok.stderr)

    def test_captions_never_render_null_and_do_not_guess_between_homonyms(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "svgs"
            (root / "a").mkdir(parents=True)
            (root / "b").mkdir(parents=True)
            for sub in ("a", "b"):
                (root / sub / "same.svg").write_bytes((self.official_svg("system-success.svg")).read_bytes())
            (root / "manifest.json").write_text(json.dumps({"icons": [
                {"name": "x/same", "file": "same.svg", "title": "Légende ambiguë", "description": None},
                {"name": "y/z", "file": "b/same.svg", "title": "Légende de b", "major": None}]}), encoding="utf-8")
            out = Path(tmp) / "p.html"
            result = self.run_preview("--svg-root", str(root), "--captions", "--output", str(out))
            self.assertEqual(result.returncode, 0, result.stderr)
            page = out.read_text(encoding="utf-8")
            self.assertNotIn("None", page)
            self.assertIn("Légende de b", page)
            self.assertNotIn("Légende ambiguë", page, "un nom de base partagé ne doit pas servir de repli")
            self.assertIn("AVERTISSEMENT", result.stdout + result.stderr)

    def test_preview_reports_malformed_official_manifest_entries(self):
        with tempfile.TemporaryDirectory() as tmp:
            official = Path(tmp) / "officiels"
            official.mkdir()
            shutil.copy(self.official_svg("system-success.svg"), official / "system-success.svg")
            (official / "manifest.json").write_text(json.dumps({"icons": [{"name": "system/success", "file": "system-success.svg"}, "cassée", {"name": 3}]}), encoding="utf-8")
            svgs = Path(tmp) / "svgs"
            svgs.mkdir()
            shutil.copy(self.official_svg("map-compass.svg"), svgs / "map-compass.svg")
            out = Path(tmp) / "p.html"
            result = self.run_preview("--svg-root", str(svgs), "--official-root", str(official), "--references", "system/success", "--output", str(out))
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("AVERTISSEMENT", result.stdout + result.stderr)
            self.assertIn("2 entrée", result.stdout + result.stderr)

    def test_generated_render_options_and_preview_sizes_are_applied(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "out"
            result = self.run_gen("--source", "generated", "--icons", "document", "--output-dir", str(out), "--color", "#123456", "--accent", "#654321", "--background", "disk", "--background-color", "#ABCDEF")
            self.assertEqual(result.returncode, 0, result.stderr)
            svg = (out / "document.svg").read_text(encoding="utf-8")
            for value in ("#123456", "#ABCDEF"):
                self.assertIn(value, svg)
            manifest = json.loads((out / "manifest.json").read_text(encoding="utf-8"))
            self.assertEqual((manifest["color"], manifest["accent"]), ("#123456", "#654321"))
            page = Path(tmp) / "p.html"
            preview = self.run_preview("--svg-root", str(out), "--output", str(page), "--sizes", "96,48")
            self.assertEqual(preview.returncode, 0, preview.stderr)
            html = page.read_text(encoding="utf-8")
            self.assertIn('width="96" height="96"', html)
            self.assertIn('width="48" height="48"', html)
            self.assertNotIn('width="80" height="80"', html)

    def test_dsfr_artwork_source_path_never_falls_back_silently(self):
        # Garde textuelle de non-régression : l'ancien repli « source_ref = source.name » masquait une source hors
        # racine ; le comportement attendu (provenance relative à la racine, sinon erreur « provenance non traçable »)
        # est prouvé par test_copies_and_validates_official_dsfr_artwork_shape (manifest["icons"][0]["source"]).
        self.assertNotIn("source_ref = source.name", SCRIPT.read_text(encoding="utf-8"))

    def test_replica_validates_all_sources_before_first_copy(self):
        # SKILL.md : « toutes les sources sont validées avant la première copie », aussi en mode dsfr-replica.
        with tempfile.TemporaryDirectory() as tmp:
            corpus = Path(tmp) / "corpus"
            corpus.mkdir()
            (corpus / "buildings-house.svg").write_bytes((self.official_svg("buildings-house.svg")).read_bytes())
            broken = (self.official_svg("digital-avatar.svg")).read_text(encoding="utf-8").replace("<path ", '<path fill="#000" ', 1)
            (corpus / "digital-avatar.svg").write_text(broken, encoding="utf-8")
            (corpus / "manifest.json").write_text(
                json.dumps({"icons": [{"name": "buildings/house", "file": "buildings-house.svg"}, {"name": "digital/avatar", "file": "digital-avatar.svg"}]}),
                encoding="utf-8",
            )
            out = Path(tmp) / "out"
            result = self.run_gen("--source", "dsfr-replica", "--replica-root", str(corpus), "--icons", "buildings/house,digital/avatar", "--output-dir", str(out))
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("digital-avatar.svg", result.stderr)
            self.assertFalse(out.exists() and any(out.iterdir()), "rien ne doit être copié si une source du corpus est invalide")

    def test_manifest_writes_are_atomic(self):
        # Un échec pendant l'écriture ne doit laisser ni manifeste tronqué ni fichier temporaire.
        module = self.load_module(SCRIPT)
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp)
            manifest = out / "manifest.json"
            original = json.dumps({"source": "dsfr-replica", "icons": [{"name": "buildings/house", "file": "buildings-house.svg", "origin": "dsfr-replica"}]}, ensure_ascii=False, indent=2) + "\n"
            manifest.write_text(original, encoding="utf-8")
            with unittest.mock.patch.object(module.os, "replace", side_effect=OSError("disque plein")):
                with self.assertRaises(OSError):
                    module.rewrite_manifest(out, lambda data: data.__setitem__("touched", True))
                with self.assertRaises(OSError):
                    module.merge_manifest(out, json.loads(original), {"source": "dsfr-replica"}, [{"name": "buildings/house", "file": "buildings-house.svg", "origin": "dsfr-replica"}])
            self.assertEqual(manifest.read_text(encoding="utf-8"), original, "le manifeste d'origine doit rester intact")
            self.assertEqual(sorted(path.name for path in out.iterdir()), ["manifest.json"], "aucun fichier temporaire ne doit rester")

    def test_raster_export_entries_without_file_are_ignored(self):
        module = self.load_module(SCRIPT)
        with tempfile.TemporaryDirectory() as tmp:
            svg = Path(tmp) / "system-success.svg"
            svg.write_bytes((self.official_svg("system-success.svg")).read_bytes())
            listed = [{"size": 64}, {"file": None, "size": 64}, "system-success-64.png", {"file": "system-success-64.png", "size": 64, "renderer": "x", "source": svg.name}]
            self.assertEqual([entry["file"] for entry in module.valid_raster_entries(listed)], ["system-success-64.png"])
            result = module.existing_raster_exports(svg, listed)
            self.assertEqual([entry["file"] for entry in result], ["system-success-64.png"], "les entrées sans nom de fichier ne doivent ni survivre ni produire une clé « None »")

    def test_qlmanage_timeout_rejects_non_finite_value(self):
        with tempfile.TemporaryDirectory() as tmp:
            env = self.make_qlmanage_stub(tmp, "exit 0")
            env["PICTOS_QLMANAGE_TIMEOUT"] = "inf"
            out = Path(tmp) / "out"
            result = self.run_gen("--source", "dsfr-replica", "--icons", "system/success", "--export-png", "64", "--output-dir", str(out), env=env)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("PICTOS_QLMANAGE_TIMEOUT", result.stderr)
            self.assertIn("fini", result.stderr)
            self.assertNotIn("Traceback", result.stderr)
            self.assertFalse(out.exists() and any(out.iterdir()), "aucun fichier ne doit être écrit quand le délai est invalide")

    def test_official_manifest_declares_the_verified_dsfr_version(self):
        with self.assertRaises(AssertionError):
            self.official_entry("inconnu.svg")
        manifest = self.official_manifest()
        declared = re.search(r"@gouvfr/dsfr@(\d+\.\d+\.\d+)", (OFFICIAL_CORPUS / "SOURCE.md").read_text(encoding="utf-8"))
        self.assertIsNotNone(declared)
        self.assertEqual(manifest["dsfr_version"], declared.group(1), "le manifeste embarqué doit déclarer la version vérifiée dans SOURCE.md")

    def test_replica_resolves_official_svgs_from_cache(self):
        with tempfile.TemporaryDirectory() as tmp:
            corpus = self.make_corpus_without_svgs(tmp)
            cache = self.make_official_cache(tmp, ["buildings-house.svg"])
            out = Path(tmp) / "out"
            env = {**os.environ, "DSFR_OFFICIAL_CACHE_DIR": str(cache)}
            result = self.run_gen("--source", "dsfr-replica", "--replica-root", str(corpus), "--icons", "buildings/house", "--output-dir", str(out), env=env)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual((out / "buildings-house.svg").read_bytes(), self.official_svg("buildings-house.svg").read_bytes())
            manifest = json.loads((out / "manifest.json").read_text(encoding="utf-8"))
            self.assertEqual(manifest["source"], "dsfr-replica")
            self.assertEqual(manifest["icons"][0]["resolved_from"], "official-cache")
            self.assertTrue(manifest["icons"][0]["official"])

    def test_replica_refuses_cache_file_with_wrong_sha256(self):
        with tempfile.TemporaryDirectory() as tmp:
            corpus = self.make_corpus_without_svgs(tmp)
            cache = self.make_official_cache(tmp, ["buildings-house.svg"], mutate=lambda data: data.replace(b"</svg>", b" </svg>"))
            out = Path(tmp) / "out"
            env = {**os.environ, "DSFR_OFFICIAL_CACHE_DIR": str(cache)}
            result = self.run_gen("--source", "dsfr-replica", "--replica-root", str(corpus), "--icons", "buildings/house", "--output-dir", str(out), env=env)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("ne correspond pas au manifeste", result.stderr)
            self.assertFalse(out.exists() and any(out.iterdir()), "rien ne doit être écrit depuis un cache qui ne correspond pas au manifeste")

    def test_replica_without_corpus_nor_cache_is_not_verified(self):
        with tempfile.TemporaryDirectory() as tmp:
            corpus = self.make_corpus_without_svgs(tmp)
            empty_cache = Path(tmp) / "cache-vide"
            empty_cache.mkdir()
            out = Path(tmp) / "out"
            env = {**os.environ, "DSFR_OFFICIAL_CACHE_DIR": str(empty_cache)}
            result = self.run_gen("--source", "dsfr-replica", "--replica-root", str(corpus), "--icons", "buildings/house", "--output-dir", str(out), env=env)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("NOT VERIFIED: source officielle absente", result.stderr)
            self.assertIn("npm pack @gouvfr/dsfr@1.15.2 --ignore-scripts", result.stderr)
            self.assertNotIn("Traceback", result.stderr)
            self.assertFalse(out.exists() and any(out.iterdir()), "rien ne doit être écrit sans source officielle")
            manifest = json.loads((corpus / "manifest.json").read_text(encoding="utf-8"))
            manifest.pop("dsfr_version")
            (corpus / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False), encoding="utf-8")
            unversioned = self.run_gen("--source", "dsfr-replica", "--replica-root", str(corpus), "--icons", "buildings/house", "--output-dir", str(out), env=env)
            self.assertNotEqual(unversioned.returncode, 0)
            self.assertIn("dsfr_version", unversioned.stderr)
            self.assertNotIn("@None", unversioned.stderr)

    def test_preview_references_resolve_from_official_cache(self):
        with tempfile.TemporaryDirectory() as tmp:
            corpus = self.make_corpus_without_svgs(tmp)
            cache = self.make_official_cache(tmp, ["system-success.svg"])
            creations = Path(tmp) / "creations"
            creations.mkdir()
            (creations / "essai.svg").write_bytes(self.official_svg("digital-search.svg").read_bytes())
            output = Path(tmp) / "planche.html"
            env = {**os.environ, "DSFR_OFFICIAL_CACHE_DIR": str(cache)}
            result = self.run_preview("--svg-root", str(creations), "--official-root", str(corpus), "--references", "system/success", "--output", str(output), env=env)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("system/success", output.read_text(encoding="utf-8"))
            empty_cache = Path(tmp) / "cache-vide"
            empty_cache.mkdir()
            missing = self.run_preview("--svg-root", str(creations), "--official-root", str(corpus), "--references", "system/success", "--output", str(output), env={**os.environ, "DSFR_OFFICIAL_CACHE_DIR": str(empty_cache)})
            self.assertNotEqual(missing.returncode, 0)
            self.assertIn("NOT VERIFIED: source officielle absente", missing.stderr)
            self.assertIn("npm pack @gouvfr/dsfr@1.15.2", missing.stderr)
            manifest = json.loads((corpus / "manifest.json").read_text(encoding="utf-8"))
            manifest.pop("dsfr_version")
            (corpus / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False), encoding="utf-8")
            unversioned = self.run_preview("--svg-root", str(creations), "--official-root", str(corpus), "--references", "system/success", "--output", str(output), env={**os.environ, "DSFR_OFFICIAL_CACHE_DIR": str(empty_cache)})
            self.assertNotEqual(unversioned.returncode, 0)
            self.assertIn("dsfr_version", unversioned.stderr, "sans version déclarée, le message doit le dire")
            self.assertNotIn("@None", unversioned.stderr)

    def test_replica_cache_resolution_requires_declared_sha256(self):
        # Sans sha256 déclaré, une copie depuis le cache ne serait pas contrôlable : refus explicite, rien d'écrit.
        with tempfile.TemporaryDirectory() as tmp:
            corpus = self.make_corpus_without_svgs(tmp)
            cache = self.make_official_cache(tmp, ["buildings-house.svg"])
            manifest = json.loads((corpus / "manifest.json").read_text(encoding="utf-8"))
            for item in manifest["icons"]:
                if item["file"] == "buildings-house.svg":
                    item.pop("sha256")
            (corpus / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False), encoding="utf-8")
            out = Path(tmp) / "out"
            env = {**os.environ, "DSFR_OFFICIAL_CACHE_DIR": str(cache)}
            result = self.run_gen("--source", "dsfr-replica", "--replica-root", str(corpus), "--icons", "buildings/house", "--output-dir", str(out), env=env)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("sha256", result.stderr)
            self.assertNotIn("Traceback", result.stderr)
            self.assertFalse(out.exists() and any(out.iterdir()), "rien ne doit être écrit sans sha256 déclaré")

    def test_replica_cache_sha256_comparison_is_case_insensitive(self):
        with tempfile.TemporaryDirectory() as tmp:
            corpus = self.make_corpus_without_svgs(tmp)
            cache = self.make_official_cache(tmp, ["buildings-house.svg"])
            manifest = json.loads((corpus / "manifest.json").read_text(encoding="utf-8"))
            for item in manifest["icons"]:
                if item["file"] == "buildings-house.svg":
                    item["sha256"] = item["sha256"].upper()
            (corpus / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False), encoding="utf-8")
            out = Path(tmp) / "out"
            result = self.run_gen("--source", "dsfr-replica", "--replica-root", str(corpus), "--icons", "buildings/house", "--output-dir", str(out), env={**os.environ, "DSFR_OFFICIAL_CACHE_DIR": str(cache)})
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertTrue((out / "buildings-house.svg").exists())

    def test_replica_malformed_dsfr_version_is_reported_not_used(self):
        with tempfile.TemporaryDirectory() as tmp:
            corpus = self.make_corpus_without_svgs(tmp)
            manifest = json.loads((corpus / "manifest.json").read_text(encoding="utf-8"))
            manifest["dsfr_version"] = "1.15 .0"
            (corpus / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False), encoding="utf-8")
            out = Path(tmp) / "out"
            result = self.run_gen("--source", "dsfr-replica", "--replica-root", str(corpus), "--icons", "buildings/house", "--output-dir", str(out), env={**os.environ, "DSFR_OFFICIAL_CACHE_DIR": str(Path(tmp) / "vide")})
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("dsfr_version", result.stderr)
            self.assertNotIn("npm pack @gouvfr/dsfr@1.15 .0", result.stderr, "une version malformée ne doit pas produire une commande npm cassée")
            self.assertFalse(out.exists() and any(out.iterdir()))


if __name__ == "__main__":
    unittest.main()
