"""Dériver les expositions natives des profils depuis un seul manifeste produit."""

import argparse
import json
from pathlib import Path

import yaml


def codex_catalog(catalog):
    """Adapter le transport Git, sans dupliquer la sélection des compétences."""
    plugins = []
    for plugin in catalog["plugins"]:
        source = plugin["source"]
        plugins.append(
            {
                **plugin,
                "source": {
                    "source": "url",
                    "url": "git@github.com:" + source["repo"] + ".git",
                    "ref": source["ref"],
                },
                "policy": {"installation": "AVAILABLE", "authentication": "ON_INSTALL"},
                "category": "Productivity",
            }
        )
    return {
        key: value
        for key, value in {**catalog, "plugins": plugins}.items()
        if key != "$schema"
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--target", choices=("claude", "codex"))
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    product = yaml.safe_load((root / "config/agentic-design-packages.yaml").read_text())
    profiles = json.loads((root / "config/distribution-profiles.json").read_text())
    skills = product["product"]["skills"]
    catalog = json.loads((root / ".claude-plugin/marketplace.json").read_text())
    template = catalog["plugins"][0]
    plugins = []
    for name, profile in profiles["profiles"].items():
        excluded = set(profile["excluded_skills"])
        if not excluded <= set(skills):
            raise SystemExit("[FAIL] profil : exclusion absente du manifeste produit")
        plugin = {**template, "name": profile["plugin"]}
        if name == "complete":
            plugin["skills"] = ["./.claude/skills"]
        else:
            plugin["description"] = (
                "Outils DSFR et RGAA/WCAG sans orchestration avancée, issus des mêmes sources que le profil complet."
            )
            plugin["skills"] = [
                f"./.claude/skills/{skill}" for skill in skills if skill not in excluded
            ]
        plugins.append(plugin)
    expected = {**catalog, "plugins": plugins}
    if args.check:
        if catalog != expected:
            raise SystemExit(
                "[FAIL] catalogue divergent : relancer scripts/build-marketplace.py"
            )
        native = root / ".agents/plugins/marketplace.json"
        if not native.is_file() or json.loads(native.read_text()) != codex_catalog(
            expected
        ):
            raise SystemExit(
                "[FAIL] catalogue Codex divergent : régénérer avec --target codex"
            )
        print("[OK] profils Claude et Codex dérivés des mêmes sources")
    else:
        print(
            json.dumps(
                codex_catalog(expected) if args.target == "codex" else expected,
                ensure_ascii=False,
                indent=2,
            )
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
