"""Installer un kit épinglé pour les agents, avec sauvegarde et retour arrière."""

# PDG-LARGE-FILE-JUSTIFICATION: la transaction et son inverse partagent le reçu
# des seules entrées possédées ; le chargeur de confiance reste séparé.

import argparse
import fcntl
import importlib.util
import json
import re
import shutil
import subprocess
import sys
import tempfile
import uuid
from pathlib import Path

sys.dont_write_bytecode = True
SCRIPTS = Path(__file__).resolve().parent


def module(name):
    spec = importlib.util.spec_from_file_location(
        name.replace("-", "_"), SCRIPTS / (name + ".py")
    )
    value = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(value)
    return value


def write_json(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n")


def link(path, target):
    path.parent.mkdir(parents=True, exist_ok=True)
    pending = path.with_name(path.name + ".next-" + uuid.uuid4().hex)
    pending.symlink_to(target)
    pending.replace(path)


def present(path):
    return path.exists() or path.is_symlink()


def identity(path):
    if path.is_symlink():
        return str(path.readlink())
    if present(path):
        raise ValueError(f"entrée modifiée ou non gérée : {path}")
    return None


def restore(prefix, receipt, check=True):
    current = prefix / "current"
    if check:
        if identity(current) != receipt["release"]:
            raise ValueError("l’installation courante ne correspond pas au reçu")
        for entry in receipt["entries"]:
            if identity(Path(entry["path"])) != entry["after"]:
                raise ValueError(
                    "entrée utilisateur modifiée après installation ; retour refusé"
                )
            if entry["backup"] and not present(Path(entry["backup"])):
                raise ValueError("sauvegarde absente ; retour refusé")
    for entry in reversed(receipt["entries"]):
        path = Path(entry["path"])
        if path.is_symlink():
            path.unlink()
        if entry["backup"]:
            Path(entry["backup"]).rename(path)
    if receipt["previous"]:
        link(current, receipt["previous"])
    elif current.is_symlink():
        current.unlink()


def install(args, home, prefix):
    if not re.fullmatch(r"[0-9a-f]{40}", args.commit or ""):
        raise ValueError("commit Git complet obligatoire")
    current = prefix / "current"
    previous = identity(current)
    old = (
        json.loads((current / "installation.json").read_text())
        if previous
        else {"entries": []}
    )
    cache = (args.cache_root or home / ".cache/dsfr-agentic-kit").expanduser().resolve()
    if cache.is_relative_to(prefix) or prefix.is_relative_to(cache):
        raise ValueError("installation et cache doivent être disjoints")
    with tempfile.TemporaryDirectory(prefix="dsfr-install-objects-") as temporary:
        source = Path(temporary)
        subprocess.run(
            ["git", "init", "--bare", "-q", str(source)],
            check=True,
            capture_output=True,
        )
        check = module("verify-kit-lock")
        check.git(source, "fetch", "--depth=1", "--", args.repository, args.commit)
        lock = check.create(source, args.commit, args.repository, None)
    revision = args.commit[:12] + "-" + uuid.uuid4().hex[:12]
    release = prefix / "releases" / revision
    release.mkdir(parents=True)
    write_json(release / "config/dsfr-kit.lock", lock)
    write_json(
        release / "config/dsfr-consumer.json",
        {
            "schema_version": 1,
            "repository": args.repository,
            "commit": args.commit,
            "profile": args.profile,
            "lock": "config/dsfr-kit.lock",
            "cache_root": str(cache),
        },
    )
    product = module("use-dsfr-kit").bind(release, cache, None)
    profiles = json.loads((product / "config/distribution-profiles.json").read_text())[
        "profiles"
    ]
    excluded = profiles[args.profile]["excluded_skills"]
    skills = sorted(
        p.parent.name
        for p in (product / ".claude/skills").glob("*/SKILL.md")
        if p.parent.name not in excluded
    )
    if not skills or not (product / "scripts/use-dsfr-kit.py").is_file():
        raise ValueError("ce commit ne propose pas l’installation utilisateur")
    (release / "scripts").mkdir()
    for name in ("use-dsfr-kit.py", "install-user.py", "verify-kit-lock.py"):
        # Copies générées de bootstrap, jamais une seconde source de maintenance.
        source = product / "scripts" / name
        shutil.copyfile(source, release / "scripts" / name)
        (release / "scripts" / name).chmod(
            0o555 if name == "use-dsfr-kit.py" else 0o444
        )
    targets = {
        str(home / surface / name): str(current / ".dsfr-kit/.claude/skills" / name)
        for surface in (".claude/skills", ".codex/skills", ".agents/skills")
        for name in skills
    }
    targets[str(home / ".local/bin/dsfr-kit")] = str(
        current / "scripts/use-dsfr-kit.py"
    )
    for workspace in args.bind_workspace:
        if not workspace.expanduser().is_dir():
            raise ValueError(
                "workspace existant obligatoire pour le lien de compatibilité"
            )
        targets[str(workspace.expanduser().resolve() / ".dsfr-kit")] = str(
            current / ".dsfr-kit"
        )
    # Les noms exclus par un passage complete -> light sont retirés s’ils étaient gérés.
    old_targets = {
        entry["path"]: entry["after"] for entry in old["entries"] if entry["after"]
    }
    for path, target in old_targets.items():
        if target == str(current / ".dsfr-kit"):
            targets.setdefault(path, target)
    for path in set(old_targets) - set(targets):
        targets[path] = None
    entries = []
    for number, (name, target) in enumerate(sorted(targets.items())):
        path = Path(name)
        exists = present(path)
        owned = path.is_symlink() and str(path.readlink()) == old_targets.get(name)
        if exists and not owned and not args.adopt_existing:
            raise ValueError(
                f"entrée préexistante ; adoption explicite nécessaire : {path}"
            )
        if name in old_targets and not owned:
            raise ValueError(f"entrée gérée modifiée depuis l’installation : {path}")
        entries.append(
            {
                "path": name,
                "after": target,
                "backup": str(prefix / "backups" / revision / str(number))
                if exists
                else None,
            }
        )
    receipt = {
        "schema_version": 1,
        "commit": args.commit,
        "profile": args.profile,
        "release": str(release),
        "previous": previous,
        "entries": entries,
    }
    write_json(release / "installation.json", receipt)
    applied = []
    try:
        for entry in entries:
            path = Path(entry["path"])
            if entry["backup"]:
                backup = Path(entry["backup"])
                backup.parent.mkdir(parents=True, exist_ok=True)
                path.rename(backup)
            applied.append(entry)
            if entry["after"]:
                link(path, entry["after"])
        link(current, release)
    except BaseException:
        restore(prefix, {**receipt, "entries": applied}, check=False)
        raise
    print(
        f"[OK] installation {args.profile} : {args.commit} ; {len(skills)} compétences ; {release}"
    )


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=("install", "rollback"))
    parser.add_argument("--home", type=Path, default=Path.home())
    parser.add_argument("--prefix", type=Path)
    parser.add_argument("--cache-root", type=Path)
    parser.add_argument("--commit")
    parser.add_argument(
        "--repository",
        default="git@github.com:alexandra-guiderdoni/dsfr-agentic-kit.git",
    )
    parser.add_argument("--profile", choices=("complete", "light"), default="complete")
    parser.add_argument("--adopt-existing", action="store_true")
    parser.add_argument("--bind-workspace", type=Path, action="append", default=[])
    args = parser.parse_args()
    try:
        home = args.home.expanduser().resolve()
        prefix = (
            (args.prefix or home / ".local/share/dsfr-agentic-kit")
            .expanduser()
            .resolve()
        )
        prefix.mkdir(parents=True, exist_ok=True)
        with (prefix / ".installation.lock").open("a") as stream:
            fcntl.flock(stream, fcntl.LOCK_EX)
            if args.action == "install":
                install(args, home, prefix)
            else:
                receipt = json.loads((prefix / "current/installation.json").read_text())
                restore(prefix, receipt)
                print("[OK] retour arrière : entrées précédentes restaurées")
        return 0
    except (
        ValueError,
        OSError,
        KeyError,
        TypeError,
        subprocess.CalledProcessError,
    ) as error:
        detail = (
            "récupération Git refusée"
            if isinstance(error, subprocess.CalledProcessError)
            else str(error)
        )
        print(f"[FAIL] installation DSFR : {detail}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
