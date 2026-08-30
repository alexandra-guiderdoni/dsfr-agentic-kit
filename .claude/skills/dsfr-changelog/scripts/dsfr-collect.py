#!/usr/bin/env python3
# PDG-LARGE-FILE-JUSTIFICATION: collecteur CLI autonome dont bornage Git,
# catalogues multi-formats, provenance et restitution partagent un contrat JSON
# unique ; le scinder ajouterait des dépendances au déploiement git + stdlib.
"""Collecte déterministe d'un diff DSFR entre deux tags.

Sortie JSON sur stdout. Aucune dépendance obligatoire : PyYAML est utilisé s'il
est présent, sinon repli sur le CHANGELOG.md généré, qui porte la même
information. L'analyse ne fait aucun appel réseau ; le mode explicite
``--fetch-note`` récupère uniquement le corps d'une release GitHub.

Usage:
    dsfr-collect.py --repo <chemin> --from v1.14.4 --to v1.15.0 [--note <fichier>]
    dsfr-collect.py --fetch-note v1.15.0
"""
import argparse
import json
import os
import re
import subprocess
import sys
from urllib.parse import quote
from urllib.request import Request, urlopen

ZONES = {
    "core": ["src/dsfr/core/"],
    "composants": ["src/dsfr/component/"],
    # `page` et `pattern` sont descendus dans `layout` en v1.14.0. Les trois
    # préfixes désignent la même famille : sans les réunir, une réorganisation
    # d'arborescence se lit comme une zone « autre » massive et illisible.
    "layout": ["src/dsfr/layout/", "src/dsfr/page/", "src/dsfr/pattern/"],
    "analytics": ["src/dsfr/analytics/"],
    "scheme": ["src/dsfr/scheme/"],
    "utilitaires": ["src/dsfr/utility/"],
    "modules": ["src/module/"],
    "i18n": ["src/i18n/"],
    "distribution": ["package.json", "scripts/", "tool/"],
    "legal": ["doc/legal/", "LICENSE.md", "publiccode.yml"],
    "doc": ["doc/", "dsfr-sb/"],
}

# Le changelog est lu en priorité AU TAG, pour refléter l'état figé de la
# release et rester reproductible dans le temps. Le changelog de la branche
# courante est rétroactif : il couvre aussi les versions antérieures à son
# introduction, mais il est corrigé après coup. On ne s'y replie donc que si le
# tag ne décrit pas la version demandée.
CATALOG_REFS = ("origin/main", "origin/HEAD", "main", "HEAD")


# Un nom de ref commençant par un tiret est interprété par git comme une option
# (`--output=...` écrit un fichier). Le skill étant piloté par des agents qui
# peuvent construire ces bornes depuis une source non fiable, les refs sont
# validées avant tout appel à git.
REF_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._/-]*$")
VERSION_RE = re.compile(r"^v?(\d+)\.(\d+)(?:\.(\d+))?([A-Za-z0-9.-]*)$")
RELEASE_API = "https://api.github.com/repos/GouvernementFR/dsfr/releases/tags"

# Une fusion de pull request pose `(#id)` en fin de sujet. Une mention `#id`
# ailleurs dans le sujet est un indice plus faible, retenu à défaut et signalé
# comme tel.
PR_SUFFIX_RE = re.compile(r"\(#(\d+)\)\s*$")
PR_MENTION_RE = re.compile(r"#(\d+)")


class InvalidRef(ValueError):
    pass


class GitCommandError(RuntimeError):
    pass


def git_environment():
    """Interdire toute hydratation implicite d'un clone promisor."""
    env = os.environ.copy()
    env["GIT_NO_LAZY_FETCH"] = "1"
    return env


def check_ref(ref):
    if not REF_RE.match(ref or ""):
        raise InvalidRef(
            "ref invalide : {!r}. Attendu : lettres, chiffres, point, tiret, "
            "underscore ou barre oblique, ne commençant pas par un tiret."
            .format(ref))
    return ref


def is_git_repo(repo):
    out = subprocess.run(["git", "-C", repo, "rev-parse", "--git-dir"],
                         capture_output=True, text=True, check=False,
                         env=git_environment())
    return out.returncode == 0


def is_ancestor(repo, a, b):
    out = subprocess.run(["git", "-C", repo, "merge-base", "--is-ancestor", a, b],
                         capture_output=True, text=True, check=False,
                         env=git_environment())
    return out.returncode == 0


def git(repo, *args, required=False):
    out = subprocess.run(["git", "-C", repo, *args],
                         capture_output=True, text=True, check=False,
                         env=git_environment())
    if out.returncode == 0:
        return out.stdout
    if required:
        detail = out.stderr.strip() or "code {}".format(out.returncode)
        raise GitCommandError("git {} : {}".format(" ".join(args), detail))
    return ""


def show(repo, ref, path):
    listed = git(repo, "ls-tree", "-r", "--name-only", ref, "--", path,
                 required=True).splitlines()
    if path not in listed:
        return ""
    return git(repo, "show", "{}:{}".format(ref, path), required=True)


def catalog_refs(target_refs):
    seen, out = set(), []
    for ref in tuple(target_refs) + CATALOG_REFS:
        if ref and ref not in seen:
            seen.add(ref)
            out.append(ref)
    return out


def version_key(tag):
    match = VERSION_RE.match(tag)
    if not match:
        return (0, 0, 0, 0, ((1, tag.lower()),))
    major, minor, patch = (int(match.group(i) or 0) for i in range(1, 4))
    suffix = match.group(4)
    tokens = tuple(
        (0, int(token)) if token.isdigit() else (1, token.lower())
        for token in re.findall(r"\d+|[A-Za-z]+", suffix)
    )
    return (major, minor, patch, 1 if not suffix else 0, tokens)


def versions_between(repo, a, b):
    """Versions publiées dans l'intervalle : exclut la borne de départ, inclut
    celle d'arrivée. Un intervalle peut couvrir plusieurs releases, et le
    changelog décrit chaque version séparément."""
    merged_a = set(git(repo, "tag", "--merged", a, required=True).split())
    merged_b = set(git(repo, "tag", "--merged", b, required=True).split())
    inter = [t for t in (merged_b - merged_a) if re.match(r"^v?\d+\.\d+", t)]
    return sorted(inter, key=version_key)


def commit_sha(repo, ref):
    return git(repo, "rev-parse", "{}^{{commit}}".format(ref)).strip()


def fetch_release_note(api_base, version):
    if not VERSION_RE.match(version or ""):
        print("version de release invalide : {!r}".format(version), file=sys.stderr)
        return 2
    url = api_base.rstrip("/") + "/" + quote(version, safe="")
    request = Request(url, headers={
        "Accept": "application/vnd.github+json",
        "User-Agent": "dsfr-changelog",
    })
    try:
        with urlopen(request, timeout=30) as response:
            payload = json.loads(response.read().decode("utf-8"))
    except (OSError, ValueError) as exc:
        print("note de release indisponible : {}".format(exc), file=sys.stderr)
        return 1
    body = payload.get("body", "") if isinstance(payload, dict) else ""
    if not isinstance(body, str) or not body.strip():
        print("note de release indisponible : corps vide", file=sys.stderr)
        return 1
    sys.stdout.write(body)
    if body and not body.endswith("\n"):
        print()
    return 0


def resolve_bounds(repo, a, b):
    bounds = {}
    for label, ref in (("from", a), ("to", b)):
        sha = commit_sha(repo, ref)
        date = git(repo, "log", "-1", "--format=%cI", ref).strip()
        bounds[label] = {"ref": ref, "sha": sha[:12], "date": date, "resolved": bool(sha)}
    if not all(bounds[k]["resolved"] for k in ("from", "to")):
        bounds["status"] = "BOUNDARY_PARTIAL"
    elif not is_ancestor(repo, a, b):
        bounds["status"] = "BOUNDARY_DIVERGED"
    else:
        bounds["status"] = "BOUNDARY_OK"
    return bounds


def items_from_yaml(repo, refs, tag):
    try:
        import yaml
    except ImportError:
        return None
    for candidate in catalog_refs(refs):
        source_sha = git(repo, "rev-parse", "{}^{{commit}}".format(candidate)).strip()
        raw = show(repo, source_sha, "changelog.yml") if source_sha else ""
        if not raw:
            continue
        try:
            data = yaml.safe_load(raw)
        except Exception:
            continue
        if not isinstance(data, list):
            continue
        entry = next((e for e in data if isinstance(e, dict) and e.get("id") == tag), None)
        commits = entry.get("commits") if entry else None
        if not isinstance(commits, list) or not commits or not all(
                isinstance(commit, dict) for commit in commits):
            continue
        items = [{
            "id": str(c.get("id", "")),
            "type": c.get("type", ""),
            "scopes": c.get("scopes") if isinstance(c.get("scopes"), list) else [],
            "breaking": bool(c.get("isBreaking")),
            "title": (c.get("title") or "").strip(),
            "description": (c.get("description") or "").strip(),
            "pull": c.get("pull", ""),
        } for c in commits]
        return {"source": "changelog.yml@" + candidate, "source_sha": source_sha[:12],
                "date": str(entry.get("date", "")), "items": items}
    return None


def items_from_markdown(repo, refs, tag):
    """Repli sans PyYAML : parse le CHANGELOG.md généré."""
    head_re = re.compile(r"^#{2,3} \[" + re.escape(tag) + r"\]")
    next_re = re.compile(r"^#{2,3} \[v\d")
    item_re = re.compile(r"^#{3,4} \[#(\d+)\]\(([^)]+)\)\s*:\s*(.*)$")
    scope_re = re.compile(r"^`(\w+)\s*\(?([^)`]*)\)?`")
    for candidate in catalog_refs(refs):
        source_sha = git(repo, "rev-parse", "{}^{{commit}}".format(candidate)).strip()
        raw = show(repo, source_sha, "CHANGELOG.md") if source_sha else ""
        if not raw:
            continue
        lines = raw.splitlines()
        start = next((i for i, l in enumerate(lines) if head_re.match(l)), None)
        if start is None:
            continue
        end = next((i for i in range(start + 1, len(lines)) if next_re.match(lines[i])),
                   len(lines))
        block = lines[start:end]
        items = []
        for i, line in enumerate(block):
            m = item_re.match(line)
            if not m:
                continue
            scope_line = block[i + 1].strip() if i + 1 < len(block) else ""
            sm = scope_re.match(scope_line)
            description, blank_run = [], 0
            for detail in block[i + 2:]:
                if detail.strip() == "---" or item_re.match(detail):
                    break
                if not detail.strip():
                    blank_run += 1
                    continue
                if description and blank_run > 1:
                    description.extend([""] * (blank_run // 2))
                description.append(detail)
                blank_run = 0
            items.append({
                "id": m.group(1),
                "type": sm.group(1) if sm else "",
                "scopes": [s.strip() for s in sm.group(2).split(",") if s.strip()] if sm else [],
                "breaking": "\U0001F4A5" in line,
                "title": re.sub(r"^[^\w(]*", "", m.group(3)).strip(),
                "description": "\n".join(description),
                "pull": m.group(2),
            })
        if items:
            return {"source": "CHANGELOG.md@" + candidate,
                    "source_sha": source_sha[:12], "date": "", "items": items}
    return None


def rename_destination(path):
    """Chemin d'arrivée d'une ligne de diff.

    La détection de renommage est active par défaut depuis git 2.9 : une entrée
    déplacée s'affiche `a/{x => y}/b`, ou `x => y` sans préfixe commun. Classer
    cette chaîne telle quelle range le fichier dans la mauvaise zone, car elle
    commence par le préfixe commun et non par la destination réelle.
    """
    if "=>" not in path:
        return path
    if "{" in path and "}" in path:
        head, _, rest = path.partition("{")
        inner, _, tail = rest.partition("}")
        _, _, dest = inner.partition("=>")
        joined = head + dest.strip() + tail
        while "//" in joined:
            joined = joined.replace("//", "/")
        return joined
    return path.split("=>")[-1].strip()


def classify(path):
    path = rename_destination(path)
    for zone, prefixes in ZONES.items():
        if any(path.startswith(p) for p in prefixes):
            return zone
    return "autre"


def diff_zones(repo, a, b):
    zones, total, renames = {}, 0, 0
    raw = git(repo, "diff", "--numstat", a, b, required=True)
    for line in raw.splitlines():
        parts = line.split("\t")
        if len(parts) != 3:
            continue
        add, dele, path = parts
        total += 1
        if "=>" in path:
            renames += 1
        z = zones.setdefault(classify(path), {"fichiers": 0, "ajouts": 0, "retraits": 0})
        z["fichiers"] += 1
        z["ajouts"] += int(add) if add.isdigit() else 0
        z["retraits"] += int(dele) if dele.isdigit() else 0
    out = {"fichiers_total": total, "renommages": renames,
           "fichiers_hors_renommage": total - renames, "par_zone": zones}
    if not total:
        out["avertissement"] = ("aucun fichier dans le diff : bornes identiques, "
                                "ou git n'a rien renvoyé")
    return out


def commit_index(repo, a, b):
    """Rattache les identifiants du changelog aux commits de l'intervalle.

    Le type déclaré d'un item peut mentir sur sa portée : un item typé `docs`
    peut déplacer une arborescence entière et modifier un gabarit canonique.
    Les zones réellement touchées par son commit, elles, ne mentent pas.

    La cardinalité est un résultat, pas un détail d'implémentation : un
    identifiant peut ne correspondre à aucun commit de l'intervalle, à un seul,
    ou à plusieurs. Les trois cas sont restitués tels quels, avec la provenance
    du rattachement, et aucun n'est forcé vers un commit unique.
    """
    raw = git(repo, "log", "--no-merges", "--format=%x00%H%x09%s", "--numstat",
              "{}..{}".format(a, b), required=True)
    index, current = {}, None
    for line in raw.splitlines():
        if line.startswith("\x00"):
            sha, _, subject = line[1:].partition("\t")
            suffix = PR_SUFFIX_RE.search(subject)
            mentions = PR_MENTION_RE.findall(subject)
            if suffix:
                ident, origin = suffix.group(1), "sujet_suffixe"
            elif mentions:
                ident, origin = mentions[-1], "sujet_mention"
            else:
                current = None
                continue
            current = index.setdefault(ident, {
                "commits": [], "rattachement": origin,
                "fichiers": 0, "zones": {}})
            current["commits"].append(sha[:12])
            if origin == "sujet_suffixe":
                current["rattachement"] = origin
            continue
        parts = line.split("\t")
        if current is None or len(parts) != 3:
            continue
        current["fichiers"] += 1
        zone = classify(parts[2])
        current["zones"][zone] = current["zones"].get(zone, 0) + 1
    return index


def attach_commits(repo, a, b, items):
    """Ajoute à chaque item ses commits, sa provenance et ses zones réelles.

    Le rattachement lit l'historique complet de l'intervalle, pas seulement ses
    bornes : un clone partiel peut le refuser alors que le reste de la collecte
    aboutit. L'indisponibilité d'une mesure ne doit pas emporter les autres, la
    dégradation est donc explicite et localisée.
    """
    try:
        index = commit_index(repo, a, b)
    except GitCommandError as exc:
        for item in items:
            item["commits"] = []
            item["rattachement"] = "indisponible"
            item["fichiers"] = 0
            item["zones"] = {}
        return {"mesure": False, "raison": str(exc)}
    for item in items:
        found = index.get(item["id"])
        item["commits"] = found["commits"] if found else []
        item["rattachement"] = found["rattachement"] if found else "aucun"
        item["fichiers"] = found["fichiers"] if found else 0
        item["zones"] = found["zones"] if found else {}
    return {
        "mesure": True,
        "sans_commit": sorted((i["id"] for i in items if not i["commits"]), key=id_key),
        "multi_commits": sorted((i["id"] for i in items if len(i["commits"]) > 1),
                                key=id_key),
        "rattachement_faible": sorted(
            (i["id"] for i in items if i["rattachement"] == "sujet_mention"),
            key=id_key),
    }


def distribution_delta(repo, a, b):
    """Signaux portant sur les conditions de production, pas sur le rendu."""
    hooks = ("preinstall", "install", "postinstall", "prepare", "prepublishOnly")
    out = {}
    for label, ref in (("avant", a), ("apres", b)):
        raw = show(repo, ref, "package.json")
        try:
            pkg = json.loads(raw) if raw else {}
        except json.JSONDecodeError:
            pkg = {}
        scripts = pkg.get("scripts", {}) or {}
        out[label] = {
            "hooks_install": {k: v for k, v in scripts.items() if k in hooks},
            "files": pkg.get("files", []) or [],
            "version": pkg.get("version", ""),
        }
    a_h, b_h = out["avant"]["hooks_install"], out["apres"]["hooks_install"]
    out["hooks_ajoutes"] = sorted(set(b_h) - set(a_h))
    out["hooks_retires"] = sorted(set(a_h) - set(b_h))
    out["hooks_modifies"] = sorted(k for k in set(a_h) & set(b_h) if a_h[k] != b_h[k])
    out["files_ajoutes"] = sorted(set(out["apres"]["files"]) - set(out["avant"]["files"]))
    out["files_retires"] = sorted(set(out["avant"]["files"]) - set(out["apres"]["files"]))
    return out


def id_key(value):
    """Tri des identifiants : numérique quand c'est possible, alphabétique
    sinon. Un changelog malformé peut porter un id vide ou non numérique, ce
    qui ferait échouer un tri par int()."""
    return (0, int(value), "") if str(value).isdigit() else (1, 0, str(value))


def silent_changes(items, note_paths, versions):
    """Items présents dans le dépôt mais absents des notes de version publiées."""
    if not note_paths:
        return {"mesure": False,
                "raison": "aucune note publiée fournie (--note) : écart non mesurable"}
    assigned = {}
    if len(versions) == 1 and len(note_paths) == 1:
        spec = note_paths[0]
        prefix = versions[0] + "="
        assigned[versions[0]] = spec[len(prefix):] if spec.startswith(prefix) else spec
    else:
        for spec in note_paths:
            if "=" not in spec:
                return {"mesure": False,
                        "raison": ("intervalle multi-version : utiliser "
                                   "--note <version>=<chemin> pour chaque version")}
            version, path = spec.split("=", 1)
            if version not in versions or version in assigned or not path:
                return {"mesure": False,
                        "raison": "association de note invalide ou dupliquée : {}".format(version)}
            assigned[version] = path
        missing = [version for version in versions if version not in assigned]
        if missing:
            return {"mesure": False,
                    "raison": "notes publiées manquantes : {}".format(", ".join(missing)),
                    "notes_manquantes": missing}
    cited_by_version, contents = {}, set()
    for version in versions:
        path = assigned[version]
        try:
            with open(path, encoding="utf-8") as fh:
                content = fh.read()
        except OSError as exc:
            return {"mesure": False, "raison": str(exc)}
        if content in contents:
            return {"mesure": False,
                    "raison": "deux versions utilisent une note publiée identique"}
        contents.add(content)
        cited_by_version[version] = set(re.findall(r"#([1-9]\d*)\b", content))
    cited = set().union(*cited_by_version.values())
    repo_ids = {i["id"] for i in items}
    repo_ids_by_version = {
        version: {i["id"] for i in items if i["version"] == version}
        for version in versions
    }
    silent = {
        (version, item_id)
        for version in versions
        for item_id in repo_ids_by_version[version] - cited_by_version[version]
    }
    cited_but_absent = set().union(*(
        cited_by_version[version] - repo_ids_by_version[version]
        for version in versions
    ))
    return {
        "mesure": True,
        "notes_versions": versions,
        "cites_dans_la_note": len(cited),
        "presents_dans_le_depot": len(repo_ids),
        "silencieux": [
            i for i in items if (i["version"], i["id"]) in silent
        ],
        "cites_mais_absents_du_depot": sorted(cited_but_absent, key=id_key),
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo")
    ap.add_argument("--from", dest="a")
    ap.add_argument("--to", dest="b")
    ap.add_argument("--note", action="append", default=[],
                    help=("note publiée ; pour plusieurs versions, utiliser "
                          "<version>=<chemin> une fois par version"))
    ap.add_argument("--fetch-note", metavar="VERSION",
                    help="écrire le corps de la release GitHub sur stdout")
    ap.add_argument("--release-api-base", default=RELEASE_API,
                    help=argparse.SUPPRESS)
    args = ap.parse_args()

    if args.fetch_note:
        return fetch_release_note(args.release_api_base, args.fetch_note)
    if not args.repo or not args.a or not args.b:
        ap.error("--repo, --from et --to sont requis pour analyser un intervalle")

    if not os.path.isdir(args.repo) or not is_git_repo(args.repo):
        json.dump({"erreur": "--repo n'est pas un dépôt git : {}".format(args.repo)},
                  sys.stdout, ensure_ascii=False, indent=2)
        print()
        return 2

    try:
        check_ref(args.a)
        check_ref(args.b)
    except InvalidRef as exc:
        json.dump({"erreur": str(exc)}, sys.stdout, ensure_ascii=False, indent=2)
        print()
        return 2

    bounds = resolve_bounds(args.repo, args.a, args.b)
    if bounds["status"] != "BOUNDARY_OK":
        json.dump({"bornes": bounds,
                   "erreur": "bornes non résolues ou intervalle non chronologique"},
                  sys.stdout, ensure_ascii=False, indent=2)
        print()
        return 1

    try:
        versions = versions_between(args.repo, args.a, args.b)
        if not versions and commit_sha(args.repo, args.a) != commit_sha(args.repo, args.b):
            versions = [args.b]
        items, sources, source_shas = [], {}, {}
        for index, tag in enumerate(versions):
            catalog_candidates = versions[index:]
            ch = (items_from_yaml(args.repo, catalog_candidates, tag)
                  or items_from_markdown(args.repo, catalog_candidates, tag)
                  or {"source": "indisponible", "source_sha": "",
                      "date": "", "items": []})
            sources[tag] = ch["source"]
            source_shas[tag] = ch["source_sha"]
            for it in ch["items"]:
                it["version"] = tag
                items.append(it)

        cardinalite = attach_commits(args.repo, args.a, args.b, items)

        types = {}
        for i in items:
            types[i["type"]] = types.get(i["type"], 0) + 1

        result = {
            "bornes": bounds,
            "changelog": {
                "versions_couvertes": versions,
                "sources": sources,
                "source_shas": source_shas,
                "items_total": len(items),
                "par_type": types,
                "breaking_declares": [i["id"] for i in items if i["breaking"]],
                "cardinalite_commits": cardinalite,
                "items": items,
            },
            "diff": diff_zones(args.repo, args.a, args.b),
            "distribution": distribution_delta(args.repo, args.a, args.b),
            "changements_silencieux": silent_changes(items, args.note, versions),
        }
    except GitCommandError as exc:
        json.dump({"erreur_git": str(exc)}, sys.stdout,
                  ensure_ascii=False, indent=2)
        print()
        return 1
    json.dump(result, sys.stdout, ensure_ascii=False, indent=2)
    print()
    return 0


if __name__ == "__main__":
    sys.exit(main())
