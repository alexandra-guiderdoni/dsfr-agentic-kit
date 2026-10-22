"""Épingler un cache installé depuis un commit Git explicite, sans clone permanent."""

import argparse
import json
import re
import subprocess
import sys
import tempfile
from pathlib import Path

sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parent / "lib"))
from campaign_kit import IDENTITY_ERRORS, verifier


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--commit", required=True)
    parser.add_argument("--kit-root", type=Path, required=True)
    parser.add_argument("--project-root", type=Path, required=True)
    parser.add_argument(
        "--repository",
        default="git@github.com:alexandra-guiderdoni/dsfr-agentic-kit.git",
    )
    args = parser.parse_args()
    try:
        if not re.fullmatch(r"[0-9a-f]{40}", args.commit):
            raise ValueError("commit Git complet obligatoire, jamais une branche")
        root, project = args.kit_root.resolve(), args.project_root.resolve()
        if not project.is_dir():
            raise ValueError("projet existant obligatoire")
        check = verifier(Path(__file__).resolve().parents[1])
        # Les objets sont téléchargés une fois puis supprimés. Le cache natif
        # reste l’unique installation exécutée ; aucune dépendance n’est installée.
        with tempfile.TemporaryDirectory(prefix="dsfr-trusted-objects-") as temporary:
            source = Path(temporary)
            subprocess.run(
                ["git", "init", "--bare", "-q", str(source)],
                check=True,
                capture_output=True,
            )
            check.git(source, "fetch", "--depth=1", "--", args.repository, args.commit)
            lock = check.create(source, args.commit, args.repository, None)
        check.verify(lock, root, project)
        destination = project / "kit.lock"
        if destination.exists():
            if json.loads(destination.read_text()) != lock:
                raise ValueError("kit.lock existant différent : remplacement interdit")
        else:
            with destination.open("x", encoding="utf-8") as stream:
                stream.write(
                    json.dumps(lock, ensure_ascii=False, indent=2, sort_keys=True)
                    + "\n"
                )
        print(f"[OK] kit.lock préparé et cache vérifié : {args.commit}")
        return 0
    except IDENTITY_ERRORS as error:
        detail = (
            "récupération Git refusée"
            if isinstance(error, subprocess.CalledProcessError)
            else str(error)
        )
        print(f"[FAIL] kit.lock : {detail}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
