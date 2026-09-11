#!/usr/bin/env bash
# PDG-LARGE-FILE-JUSTIFICATION: suite d'intégration séquentielle dont les 21
# scénarios partagent fixtures Git temporaires, helpers, nettoyage et verdict
# agrégé ; la scinder dupliquerait ce cycle de vie et fragmenterait la preuve.
# Non-régression de dsfr-collect.py.
#
# Valeurs de référence établies le 2026-08-24 sur les diffs v1.14.4 -> v1.15.0 et
# v1.15.0 -> v1.15.2, vérifiées à la main avant d'être figées ici.
#
# Mise à jour légitime d'une référence : une valeur ne change que si le dépôt
# amont a changé (nouveau tag, changelog corrigé rétroactivement) ou si le
# comportement attendu du collecteur a changé volontairement. Dans les deux cas,
# revérifier la valeur à la main, puis la modifier ici en une seule fois, en
# citant la raison dans le message de commit. Ne jamais aligner une référence
# sur une sortie observée sans avoir compris pourquoi elle a bougé.
#
# Usage : test-collect.sh <chemin-du-clone-dsfr> [note-publiée-1.15.0]
# Le second argument est optionnel. Sans lui, un contrôle est sauté et le
# harnais l'annonce explicitement dans son résultat.
set -uo pipefail
REPO="${1:?chemin du clone DSFR attendu}"
NOTE="${2:-}"
NOTE3="${3:-}"
skipped=0

if [ ! -d "$REPO" ] || ! git -C "$REPO" rev-parse --git-dir >/dev/null 2>&1; then
  printf "ERREUR : %s n'est pas un dépôt git.\n" "$REPO" >&2
  exit 2
fi
DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
S="$DIR/dsfr-collect.py"
TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT
pass=0; fail=0
val() { python3 -c "import json,sys;d=json.load(open('$1'));print($2)"; }
same_payload() {
  python3 - "$1" "$2" <<'PY'
import json
import sys

with open(sys.argv[1], encoding="utf-8") as first:
    a = json.load(first)
with open(sys.argv[2], encoding="utf-8") as second:
    b = json.load(second)
for result in (a, b):
    result["changelog"].pop("sources", None)
print(a == b)
PY
}
contains_text() {
  python3 - "$1" "$2" <<'PY'
from pathlib import Path
import sys

print(sys.argv[2] in Path(sys.argv[1]).read_text(encoding="utf-8"))
PY
}
check() {
  if [ "$2" = "$3" ]; then printf '  PASS  %s = %s\n' "$1" "$2"; pass=$((pass+1))
  else printf '  FAIL  %s : attendu %s, obtenu %s\n' "$1" "$3" "$2"; fail=$((fail+1)); fi
}

echo "T1 nominal v1.14.4 -> v1.15.0"
python3 "$S" --repo "$REPO" --from v1.14.4 --to v1.15.0 ${NOTE:+--note "$NOTE"} > "$TMP/t1.json"
check "versions"   "$(val "$TMP/t1.json" "d['changelog']['versions_couvertes']")" "['v1.15.0']"
check "items"      "$(val "$TMP/t1.json" "d['changelog']['items_total']")" "50"
check "hooks+"     "$(val "$TMP/t1.json" "d['distribution']['hooks_ajoutes']")" "['preinstall']"
check "fichiers"   "$(val "$TMP/t1.json" "d['diff']['fichiers_total']")" "409"
if [ -n "$NOTE" ]; then
  check "silencieux" "$(val "$TMP/t1.json" "len(d['changements_silencieux']['silencieux'])")" "20"
else
    printf '  SKIP  silencieux : aucune note publiée fournie en 2e argument\n'
  skipped=$((skipped+1))
fi

echo "T2 repli sans PyYAML"
mkdir -p "$TMP/noyaml" && printf 'raise ImportError("simulation")\n' > "$TMP/noyaml/yaml.py"
PYTHONPATH="$TMP/noyaml" python3 "$S" --repo "$REPO" --from v1.14.4 --to v1.15.0 ${NOTE:+--note "$NOTE"} > "$TMP/t2.json"
check "source"     "$(val "$TMP/t2.json" "d['changelog']['sources']['v1.15.0']")" "CHANGELOG.md@v1.15.0"
check "items"      "$(val "$TMP/t2.json" "d['changelog']['items_total']")" "50"
check "contenu"    "$(same_payload "$TMP/t1.json" "$TMP/t2.json")" "True"

echo "T3 version antérieure à changelog.yml, intervalle de deux versions"
python3 "$S" --repo "$REPO" --from v1.13.0 --to v1.13.2 > "$TMP/t3.json"
check "versions"   "$(val "$TMP/t3.json" "d['changelog']['versions_couvertes']")" "['v1.13.1', 'v1.13.2']"
check "items"      "$(val "$TMP/t3.json" "d['changelog']['items_total']")" "29"
main_sha="$(git -C "$REPO" rev-parse --short=12 'origin/main^{commit}')"
check "source-sha" "$(val "$TMP/t3.json" "d['changelog']['source_shas']['v1.13.1']")" "$main_sha"
PYTHONPATH="$TMP/noyaml" python3 "$S" --repo "$REPO" --from v1.13.0 --to v1.13.2 > "$TMP/t3-noyaml.json"
check "contenu ancien" "$(same_payload "$TMP/t3.json" "$TMP/t3-noyaml.json")" "True"

echo "T6 intervalle multi-versions v1.15.0 -> v1.15.2"
python3 "$S" --repo "$REPO" --from v1.15.0 --to v1.15.2 > "$TMP/t6.json"
check "versions"   "$(val "$TMP/t6.json" "d['changelog']['versions_couvertes']")" "['v1.15.1', 'v1.15.2']"
check "items"      "$(val "$TMP/t6.json" "d['changelog']['items_total']")" "3"
check "garde-fou"  "$(val "$TMP/t6.json" "d['changements_silencieux']['mesure']")" "False"

echo "T7 intervalle de trois versions, catalogues figés à chaque tag"
python3 "$S" --repo "$REPO" --from v1.14.4 --to v1.15.2 > "$TMP/t7.json"
check "versions"   "$(val "$TMP/t7.json" "d['changelog']['versions_couvertes']")" "['v1.15.0', 'v1.15.1', 'v1.15.2']"
check "items"      "$(val "$TMP/t7.json" "d['changelog']['items_total']")" "53"
check "sources"    "$(val "$TMP/t7.json" "d['changelog']['sources']")" "{'v1.15.0': 'changelog.yml@v1.15.0', 'v1.15.1': 'changelog.yml@v1.15.2', 'v1.15.2': 'changelog.yml@v1.15.2'}"

echo "T22 version patch v1.15.2 -> v1.15.3 : neuf PR, quatre absentes de la note, écart d'attribution"
python3 "$S" --repo "$REPO" --from v1.15.2 --to v1.15.3 ${NOTE3:+--note "v1.15.3=$NOTE3"} > "$TMP/t22.json"
check "versions"   "$(val "$TMP/t22.json" "d['changelog']['versions_couvertes']")" "['v1.15.3']"
check "items"      "$(val "$TMP/t22.json" "d['changelog']['items_total']")" "9"
check "bornes"     "$(val "$TMP/t22.json" "d['bornes']['status']")" "BOUNDARY_OK"
check "types"      "$(val "$TMP/t22.json" "sorted(d['changelog']['par_type'])")" "['chore', 'docs', 'feat', 'fix']"
if [ -n "$NOTE3" ]; then
  check "silencieux" "$(val "$TMP/t22.json" "len(d['changements_silencieux']['silencieux'])")" "4"
  check "cites"      "$(val "$TMP/t22.json" "d['changements_silencieux']['cites_dans_la_note']")" "5"
  check "ids-silencieux" "$(val "$TMP/t22.json" "sorted(i['id'] for i in d['changements_silencieux']['silencieux'])")" "['1507', '1512', '1516', '1524']"
else
  printf '  SKIP  silencieux 1.15.3 : aucune note v1.15.3 fournie en 3e argument\n'
  skipped=$((skipped+1))
fi

echo "T8 intervalle inverse"
python3 "$S" --repo "$REPO" --from v1.15.2 --to v1.15.0 > "$TMP/t8.json"; code=$?
check "exit"       "$code" "1"
check "statut"     "$(val "$TMP/t8.json" "d['bornes']['status']")" "BOUNDARY_DIVERGED"

echo "T9 prépublication réelle"
python3 "$S" --repo "$REPO" --from v0.6.0 --to v1.0.0 > "$TMP/t9.json"
check "ordre"      "$(val "$TMP/t9.json" "d['changelog']['versions_couvertes']")" "['v1.0.0rc1', 'v1.0.0']"
python3 "$S" --repo "$REPO" --from v0.6.0 --to v1.0.0rc1 > "$TMP/t9-rc.json"
check "statut"     "$(val "$TMP/t9-rc.json" "d['bornes']['status']")" "BOUNDARY_OK"
check "source"     "$(val "$TMP/t9-rc.json" "d['changelog']['sources']['v1.0.0rc1']")" "indisponible"
check "items"      "$(val "$TMP/t9-rc.json" "d['changelog']['items_total']")" "0"
check "fichiers"   "$(val "$TMP/t9-rc.json" "d['diff']['fichiers_total']")" "780"

echo "T10 identifiant de pull request court"
printf '#10\n' > "$TMP/note-pr-10.md"
python3 "$S" --repo "$REPO" --from v1.0.0 --to v1.1.0 --note "$TMP/note-pr-10.md" > "$TMP/t22.json"
check "cites"      "$(val "$TMP/t22.json" "d['changements_silencieux']['cites_dans_la_note']")" "1"
check "silencieux" "$(val "$TMP/t22.json" "any(i['id'] == '10' for i in d['changements_silencieux']['silencieux'])")" "False"

echo "T11 notes associées aux versions"
printf '#1483\n#1486\n' > "$TMP/note-1.15.1.md"
printf '#1487\n' > "$TMP/note-1.15.2.md"
python3 "$S" --repo "$REPO" --from v1.15.0 --to v1.15.2 \
  --note "$TMP/note-1.15.1.md" --note "$TMP/note-1.15.1.md" > "$TMP/t11-invalid.json"
check "doublon"    "$(val "$TMP/t11-invalid.json" "d['changements_silencieux']['mesure']")" "False"
python3 "$S" --repo "$REPO" --from v1.15.0 --to v1.15.2 \
  --note "v1.15.1=$TMP/note-1.15.1.md" --note "v1.15.2=$TMP/note-1.15.2.md" > "$TMP/t11.json"
check "mesure"     "$(val "$TMP/t11.json" "d['changements_silencieux']['mesure']")" "True"
check "silencieux" "$(val "$TMP/t11.json" "len(d['changements_silencieux']['silencieux'])")" "0"
python3 "$S" --repo "$REPO" --from v1.15.0 --to v1.15.2 \
  --note "v1.15.1=$TMP/note-1.15.2.md" --note "v1.15.2=$TMP/note-1.15.1.md" > "$TMP/t11-crossed.json"
check "notes croisées" "$(val "$TMP/t11-crossed.json" "sorted((i['version'], i['id']) for i in d['changements_silencieux']['silencieux'])")" "[('v1.15.1', '1483'), ('v1.15.1', '1486'), ('v1.15.2', '1487')]"

echo "T12 changelog YAML malformé"
mkdir -p "$TMP/malformed" "$TMP/badyaml"
git -C "$TMP/malformed" init -q -b main
printf '{}\n' > "$TMP/malformed/package.json"
git -C "$TMP/malformed" add package.json
git -C "$TMP/malformed" -c user.name=test -c user.email=test@example.invalid commit -qm initial
git -C "$TMP/malformed" tag v0.9.0
printf '%s\n' '- id: v1.0.0' '  commits: invalid' > "$TMP/malformed/changelog.yml"
printf '%s\n' '## [v1.0.0]' '#### [#1](https://example.invalid/1) : correction' "\`fix \`" '---' > "$TMP/malformed/CHANGELOG.md"
git -C "$TMP/malformed" add changelog.yml CHANGELOG.md
git -C "$TMP/malformed" -c user.name=test -c user.email=test@example.invalid commit -qm version
git -C "$TMP/malformed" tag v1.0.0
printf '%s\n' 'def safe_load(raw):' '    return [{"id": "v1.0.0", "commits": "invalid"}]' > "$TMP/badyaml/yaml.py"
PYTHONPATH="$TMP/badyaml" python3 "$S" --repo "$TMP/malformed" --from v0.9.0 --to v1.0.0 > "$TMP/t12.json"
check "source"     "$(val "$TMP/t12.json" "d['changelog']['sources']['v1.0.0']")" "CHANGELOG.md@v1.0.0"
check "items"      "$(val "$TMP/t12.json" "d['changelog']['items_total']")" "1"

echo "T13 bornes au même commit"
python3 "$S" --repo "$REPO" --from v1.15.0 --to v1.15.0 > "$TMP/t13-tag.json"
same_sha="$(git -C "$REPO" rev-parse 'v1.15.0^{commit}')"
python3 "$S" --repo "$REPO" --from v1.15.0 --to "$same_sha" > "$TMP/t13-sha.json"
check "tag versions" "$(val "$TMP/t13-tag.json" "d['changelog']['versions_couvertes']")" "[]"
check "tag items"    "$(val "$TMP/t13-tag.json" "d['changelog']['items_total']")" "0"
check "tag sources"  "$(val "$TMP/t13-tag.json" "d['changelog']['sources']")" "{}"
check "sha versions" "$(val "$TMP/t13-sha.json" "d['changelog']['versions_couvertes']")" "[]"
check "sha items"    "$(val "$TMP/t13-sha.json" "d['changelog']['items_total']")" "0"
check "sha sources"  "$(val "$TMP/t13-sha.json" "d['changelog']['sources']")" "{}"

echo "T14 récupération autonome d'une note"
mkdir -p "$TMP/releases"
printf '{"body":"# Note locale\\n\\n#123\\n"}\n' > "$TMP/releases/v1.15.0"
python3 "$S" --fetch-note v1.15.0 \
  --release-api-base "file://$TMP/releases" > "$TMP/note-fetched.md"; code=$?
note_ok="$(python3 - "$TMP/note-fetched.md" <<'PY'
from pathlib import Path
import sys

print(Path(sys.argv[1]).read_text(encoding="utf-8").splitlines() == ["# Note locale", "", "#123"])
PY
)"
check "note récupérée" "$code:$note_ok" "0:True"
printf '{}\n' > "$TMP/releases/v1.15.1"
python3 "$S" --fetch-note v1.15.1 \
  --release-api-base "file://$TMP/releases" > "$TMP/note-empty.md" 2> "$TMP/note-empty.err"; code=$?
empty_refused="$(contains_text "$TMP/note-empty.err" 'corps vide')"
check "note vide refusée" "$code:$empty_refused" "1:True"

echo "T15 tag distant déplacé"
git init -q --bare "$TMP/tag-remote.git"
git init -q -b main "$TMP/tag-source"
printf 'initial\n' > "$TMP/tag-source/version.txt"
git -C "$TMP/tag-source" add version.txt
git -C "$TMP/tag-source" -c user.name=test -c user.email=test@example.invalid commit -qm initial
git -C "$TMP/tag-source" tag v1.0.0
git -C "$TMP/tag-source" remote add origin "$TMP/tag-remote.git"
git -C "$TMP/tag-source" push -q origin main v1.0.0
git clone -q "$TMP/tag-remote.git" "$TMP/tag-consumer"
local_before="$(git -C "$TMP/tag-consumer" rev-parse 'v1.0.0^{commit}')"
printf 'déplacé\n' >> "$TMP/tag-source/version.txt"
git -C "$TMP/tag-source" add version.txt
git -C "$TMP/tag-source" -c user.name=test -c user.email=test@example.invalid commit -qm suivant
moved_sha="$(git -C "$TMP/tag-source" rev-parse HEAD)"
git -C "$TMP/tag-source" push -q origin main
git --git-dir="$TMP/tag-remote.git" update-ref refs/tags/v1.0.0 "$moved_sha"
git -C "$TMP/tag-consumer" fetch --tags origin > "$TMP/tag-fetch.out" 2> "$TMP/tag-fetch.err"; code=$?
local_after="$(git -C "$TMP/tag-consumer" rev-parse 'v1.0.0^{commit}')"
remote_after="$(git --git-dir="$TMP/tag-remote.git" rev-parse 'v1.0.0^{commit}')"
clobber="$(contains_text "$TMP/tag-fetch.err" 'would clobber existing tag')"
check "fetch refusé" "$code:$clobber" "1:True"
check "tag local préservé" "$local_before" "$local_after"
check "tags distincts" "$([ "$local_after" != "$remote_after" ] && printf True || printf False)" "True"

echo "T16 structure publiable du skill"
skill="$DIR/../SKILL.md"
checklist_ok="$(python3 - "$skill" <<'PY'
from pathlib import Path
import re
import sys

print(len(re.findall(r"^- \[ \]", Path(sys.argv[1]).read_text(encoding="utf-8"), re.M)) >= 2)
PY
)"
check "checklist" "$checklist_ok" "True"
check "conventions" "$(contains_text "$skill" '## Conventions')" "True"
check "exemple" "$(contains_text "$skill" '## Exemple')" "True"

echo "T17 clone promisor sans hydratation implicite"
mkdir -p "$TMP/promisor-source"
git -C "$TMP/promisor-source" init -q -b main
printf '{"version":"1.0.0"}\n' > "$TMP/promisor-source/package.json"
git -C "$TMP/promisor-source" add package.json
git -C "$TMP/promisor-source" -c user.name=test -c user.email=test@example.invalid commit -qm initial
git -C "$TMP/promisor-source" tag v1.0.0
printf '{"version":"1.1.0"}\n' > "$TMP/promisor-source/package.json"
printf '%s\n' '## [v1.1.0]' '#### [#1](https://example.invalid/1) : correction' \
  "\`fix \`" '---' > "$TMP/promisor-source/CHANGELOG.md"
git -C "$TMP/promisor-source" add package.json CHANGELOG.md
git -C "$TMP/promisor-source" -c user.name=test -c user.email=test@example.invalid commit -qm version
git -C "$TMP/promisor-source" tag v1.1.0
git init -q --bare "$TMP/promisor-remote.git"
git --git-dir="$TMP/promisor-remote.git" config uploadpack.allowFilter true
git --git-dir="$TMP/promisor-remote.git" config uploadpack.allowAnySHA1InWant true
git -C "$TMP/promisor-source" remote add origin "$TMP/promisor-remote.git"
git -C "$TMP/promisor-source" push -q origin main --tags
git clone -q --filter=blob:none --no-checkout \
  "file://$TMP/promisor-remote.git" "$TMP/promisor-clone"
missing_oid="$(git -C "$TMP/promisor-source" rev-parse 'v1.1.0:package.json')"
GIT_NO_LAZY_FETCH=1 git -C "$TMP/promisor-clone" cat-file -e "$missing_oid" 2>/dev/null
setup_code=$?
python3 "$S" --repo "$TMP/promisor-clone" --from v1.0.0 --to v1.1.0 \
  > "$TMP/t17.json"; code=$?
GIT_NO_LAZY_FETCH=1 git -C "$TMP/promisor-clone" cat-file -e "$missing_oid" 2>/dev/null
after_code=$?
explicit_error="$(python3 - "$TMP/t17.json" <<'PY'
import json
import sys

with open(sys.argv[1], encoding="utf-8") as stream:
    print("erreur_git" in json.load(stream))
PY
)"
check "lazy fetch bloqué" "$setup_code:$code:$after_code:$explicit_error" "1:1:1:True"

echo "T4 borne inexistante"
python3 "$S" --repo "$REPO" --from v9.9.9 --to v1.15.0 > "$TMP/t4.json"; code=$?
check "exit"       "$code" "1"
check "statut"     "$(val "$TMP/t4.json" "d['bornes']['status']")" "BOUNDARY_PARTIAL"

echo "T5 sans note publiée"
python3 "$S" --repo "$REPO" --from v1.14.4 --to v1.15.0 > "$TMP/t5.json"
check "mesure"     "$(val "$TMP/t5.json" "d['changements_silencieux']['mesure']")" "False"

echo "T18 normalisation des chemins de renommage"
# Test pur : aucune dépendance au dépôt. La détection de renommage est active
# par défaut depuis git 2.9, un chemin déplacé arrive donc sous la forme
# `a/{x => y}/b` et doit être classé sur sa destination.
norm="$(python3 - "$S" <<'PY'
import importlib.util
import sys

spec = importlib.util.spec_from_file_location("collect", sys.argv[1])
collect = importlib.util.module_from_spec(spec)
spec.loader.exec_module(collect)
cases = [
    ("src/dsfr/{page/account => layout/page}/login/.package.yml",
     "src/dsfr/layout/page/login/.package.yml"),
    ("src/dsfr/{ => layout}/page/example/layout.ejs",
     "src/dsfr/layout/page/example/layout.ejs"),
    ("src/dsfr/core/style/_module.scss", "src/dsfr/core/style/_module.scss"),
]
print(all(collect.rename_destination(a) == b for a, b in cases)
      and collect.classify("src/dsfr/{page/account => layout/page}/login/x.yml") == "layout"
      and collect.classify("src/dsfr/component/modal/x.ejs") == "composants")
PY
)"
check "destination + zone" "$norm" "True"

echo "T19 rattachement des items à leurs commits, v1.13.2 -> v1.14.0"
# Valeurs vérifiées à la main le 2026-08-25 : #1069, typé `docs`, est le commit
# d6dc78b72d47 et touche 1108 fichiers, dont 806 composants et 219 layout. Le
# type déclaré ne dit rien de cette portée ; les zones du diff, si.
python3 "$S" --repo "$REPO" --from v1.13.2 --to v1.14.0 > "$TMP/t19.json"
t19_mesure="$(val "$TMP/t19.json" "d['changelog']['cardinalite_commits']['mesure']")"
if [ "$t19_mesure" = "True" ]; then
  check "commits #1069"  "$(val "$TMP/t19.json" "[i['commits'] for i in d['changelog']['items'] if i['id']=='1069']")" "[['d6dc78b72d47']]"
  check "provenance"     "$(val "$TMP/t19.json" "[i['rattachement'] for i in d['changelog']['items'] if i['id']=='1069']")" "['sujet_suffixe']"
  check "fichiers #1069" "$(val "$TMP/t19.json" "[i['fichiers'] for i in d['changelog']['items'] if i['id']=='1069']")" "[1108]"
  check "composants"     "$(val "$TMP/t19.json" "[i['zones']['composants'] for i in d['changelog']['items'] if i['id']=='1069']")" "[806]"
  check "cardinalité"    "$(val "$TMP/t19.json" "(d['changelog']['cardinalite_commits']['sans_commit'], d['changelog']['cardinalite_commits']['multi_commits'])")" "([], [])"
else
  printf '  SKIP  rattachement : historique indisponible sur ce clone (partiel non hydraté)\n'
  skipped=$((skipped+1))
fi

echo "T20 renommages et zonage, v1.13.2 -> v1.14.0"
# 1136 chemins touchés dont 192 déplacements. Sans normalisation, 213 de ces
# chemins tombaient en zone « autre » et masquaient la réorganisation.
check "renommages"    "$(val "$TMP/t19.json" "d['diff']['renommages']")" "192"
check "hors renommage" "$(val "$TMP/t19.json" "d['diff']['fichiers_hors_renommage']")" "944"
check "zone layout"   "$(val "$TMP/t19.json" "d['diff']['par_zone']['layout']['fichiers']")" "219"
check "zone autre"    "$(val "$TMP/t19.json" "d['diff']['par_zone']['autre']['fichiers']")" "9"
check "somme zones"   "$(val "$TMP/t19.json" "sum(z['fichiers'] for z in d['diff']['par_zone'].values()) == d['diff']['fichiers_total']")" "True"
check "sans renommage" "$(val "$TMP/t1.json" "d['diff']['renommages']")" "0"

echo "T21 rattachement indisponible sans emporter le reste de la collecte"
# Le diff ne lit que les deux bornes ; le rattachement lit tout l'historique de
# l'intervalle. Un clone partiel dont seules les bornes sont hydratées sépare
# donc les deux : la mesure indisponible doit dégrader seule, sans faire échouer
# bornes, zones et distribution.
mkdir -p "$TMP/deg-source"
git init -q "$TMP/deg-source" -b main
printf '{"version":"1.0.0","files":["/dist"]}\n' > "$TMP/deg-source/package.json"
mkdir -p "$TMP/deg-source/src/dsfr/core"
printf 'a\n' > "$TMP/deg-source/src/dsfr/core/f.txt"
git -C "$TMP/deg-source" add -A
git -C "$TMP/deg-source" -c user.name=test -c user.email=test@example.invalid commit -qm base
git -C "$TMP/deg-source" tag v1.0.0
printf 'intermediaire\n' > "$TMP/deg-source/src/dsfr/core/f.txt"
git -C "$TMP/deg-source" -c user.name=test -c user.email=test@example.invalid commit -qam "milieu (#4242)"
printf 'final\n' > "$TMP/deg-source/src/dsfr/core/f.txt"
printf '{"version":"1.1.0","files":["/dist"]}\n' > "$TMP/deg-source/package.json"
git -C "$TMP/deg-source" -c user.name=test -c user.email=test@example.invalid commit -qam "fin (#4243)"
git -C "$TMP/deg-source" tag v1.1.0
git init -q --bare "$TMP/deg-remote.git"
git --git-dir="$TMP/deg-remote.git" config uploadpack.allowFilter true
git --git-dir="$TMP/deg-remote.git" config uploadpack.allowAnySHA1InWant true
git -C "$TMP/deg-source" remote add origin "$TMP/deg-remote.git"
git -C "$TMP/deg-source" push -q origin main --tags
git clone -q --filter=blob:none --no-checkout "file://$TMP/deg-remote.git" "$TMP/deg-clone"
# Hydratation des seules bornes, sans toucher au commit intermédiaire.
git -C "$TMP/deg-clone" diff --numstat v1.0.0 v1.1.0 >/dev/null 2>&1
python3 "$S" --repo "$TMP/deg-clone" --from v1.0.0 --to v1.1.0 > "$TMP/t21.json"; code=$?
check "collecte aboutit"  "$code" "0"
check "mesure dégradée"   "$(val "$TMP/t21.json" "d['changelog']['cardinalite_commits']['mesure']")" "False"
check "raison présente"   "$(val "$TMP/t21.json" "bool(d['changelog']['cardinalite_commits'].get('raison'))")" "True"
check "diff préservé"     "$(val "$TMP/t21.json" "d['diff']['fichiers_total'] >= 1")" "True"
check "bornes préservées" "$(val "$TMP/t21.json" "d['bornes']['status']")" "BOUNDARY_OK"
check "distribution"      "$(val "$TMP/t21.json" "d['distribution']['apres']['version']")" "1.1.0"

printf '\nRESULTAT : %d PASS / %d FAIL' "$pass" "$fail"
if [ "$skipped" -gt 0 ]; then
  printf ' / %d SKIP (couverture réduite : relancer avec la note publiée)' "$skipped"
fi
printf '\n'
[ "$fail" -eq 0 ]
