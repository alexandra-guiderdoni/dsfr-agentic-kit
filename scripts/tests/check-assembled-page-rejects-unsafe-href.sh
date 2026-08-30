#!/usr/bin/env bash
set -euo pipefail

# Chaque charge est jouée SEULE : une page par charge. Grouper les charges
# masquerait un contournement, la page étant déjà rejetée par une autre.
# Les variantes à espace interne (java<TAB>script:) exploitent le fait que les
# navigateurs retirent tab/LF/CR de l'URL avant de résoudre le schéma
# (spec URL WHATWG) : une comparaison sur la chaîne brute ne les voit pas.

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WORKSPACE="$(cd "$SCRIPT_DIR/../.." && pwd)"
GENERATOR="$WORKSPACE/.claude/skills/dsfr-components/scripts/generate_assembled_page.py"

tmp_dir="$(mktemp -d "${TMPDIR:-/tmp}/assembled-unsafe-href.XXXXXX")"
cleanup() {
  rm -rf "$tmp_dir"
}
trap cleanup EXIT

# Écrit une page par charge : payload-<n>.json, plus payload-<n>.label
python3 - "$tmp_dir" <<'PYEOF'
import json, pathlib, sys

out = pathlib.Path(sys.argv[1])

refuser = [
    ("javascript nominal",        "javascript:alert(1)"),
    ("casse melangee",            "JaVaScRiPt:alert(1)"),
    ("espaces de tete",           "   javascript:alert(1)"),
    ("tab interne au schema",     "java\tscript:alert(1)"),
    ("newline interne",           "java\nscript:alert(1)"),
    ("retour chariot interne",    "java\rscript:alert(1)"),
    ("null byte de tete",         "\x00javascript:alert(1)"),
    ("tab avant les deux-points", "javascript\t:alert(1)"),
    ("data nominal",              "data:text/html;base64,PHNjcmlwdD4="),
    ("data casse et espace",      " DATA:text/html;base64,PHNjcmlwdD4="),
    ("vbscript",                  "vbscript:msgbox(1)"),
    ("blob",                      "blob:https://evil.example/x"),
    ("file",                      "file:///etc/passwd"),
    ("about",                     "about:blank"),
    ("protocol-relative",         "//evil.example/x"),
]

accepter = [
    ("https absolu",   "https://example.gouv.fr/service"),
    ("chemin absolu",  "/contact"),
    ("chemin relatif", "page.html"),
    ("mailto",         "mailto:contact@example.gouv.fr"),
    ("tel",            "tel:+33123456789"),
]

def page(href):
    return {
        "title": "Test href",
        "sections": [
            {"block": "content", "title": "Section de test",
             "body_text": "Contenu de test."},
            {"block": "buttons",
             "items": [{"label": "Lien testé", "href": href}]},
        ],
    }

for i, (label, href) in enumerate(refuser):
    (out / f"ko-{i}.json").write_text(json.dumps(page(href)), encoding="utf-8")
    (out / f"ko-{i}.label").write_text(label, encoding="utf-8")

for i, (label, href) in enumerate(accepter):
    (out / f"ok-{i}.json").write_text(json.dumps(page(href)), encoding="utf-8")
    (out / f"ok-{i}.label").write_text(label, encoding="utf-8")

print(len(refuser), len(accepter))
PYEOF

echec=0

# --- charges qui DOIVENT être refusées ---
for cfg in "$tmp_dir"/ko-*.json; do
  label="$(cat "${cfg%.json}.label")"
  set +e
  python3 "$GENERATOR" --config-file "$cfg" --check \
    >"$tmp_dir/stdout" 2>"$tmp_dir/stderr"
  rc=$?
  set -e
  if [[ "$rc" -ne 1 ]]; then
    printf '[FAIL] charge acceptée alors qu%s elle doit être refusée : %s (exit %s)\n' "'" "$label" "$rc" >&2
    echec=1
    continue
  fi
  # Refus pour la BONNE raison : le message doit nommer le schéma d'URL,
  # pas un plantage ni une erreur de schéma JSON.
  if ! grep -aqiE "URL interdit|Erreur de schéma" "$tmp_dir/stderr"; then
    printf '[FAIL] refusée pour une mauvaise raison : %s\n' "$label" >&2
    sed -n '1,10p' "$tmp_dir/stderr" >&2
    echec=1
  fi
done

# --- href légitimes qui DOIVENT passer ---
for cfg in "$tmp_dir"/ok-*.json; do
  label="$(cat "${cfg%.json}.label")"
  if ! python3 "$GENERATOR" --config-file "$cfg" --check \
    >"$tmp_dir/stdout-ok" 2>"$tmp_dir/stderr-ok"; then
    printf '[FAIL] href légitime rejeté : %s\n' "$label" >&2
    sed -n '1,10p' "$tmp_dir/stderr-ok" >&2
    echec=1
  fi
done

if [[ "$echec" -ne 0 ]]; then
  exit 1
fi

# --- attributs porteurs d'URL autres que href ---
# Le parseur de validation n'inspectait que href : action, src et cite
# sortaient sans contrôle de schéma. action est exécutable à la soumission.
python3 - "$tmp_dir" <<'PYEOF2'
import json, pathlib, sys
out = pathlib.Path(sys.argv[1])
cas = [
    ("form action javascript", "action", "javascript:alert(1)"),
    ("form action tab interne", "action", "java\tscript:alert(1)"),
    ("form action vbscript",   "action", "vbscript:msgbox(1)"),
]
for i, (label, _attr, charge) in enumerate(cas):
    page = {
        "title": "Test attribut URL",
        "sections": [
            {"block": "content", "title": "S", "body_text": "x"},
            {"block": "form", "action": charge,
             "fields": [{"type": "text", "label": "L", "name": "n"}]},
        ],
    }
    (out / f"attr-{i}.json").write_text(json.dumps(page), encoding="utf-8")
    (out / f"attr-{i}.label").write_text(label, encoding="utf-8")
PYEOF2

for cfg in "$tmp_dir"/attr-*.json; do
  label="$(cat "${cfg%.json}.label")"
  set +e
  python3 "$GENERATOR" --config-file "$cfg" --check >"$tmp_dir/o" 2>"$tmp_dir/e"
  rc=$?
  set -e
  if [[ "$rc" -ne 1 ]]; then
    printf '[FAIL] attribut URL accepté : %s (exit %s)\n' "$label" "$rc" >&2
    exit 1
  fi
  if ! grep -aqiE "URL interdit|Erreur de schéma" "$tmp_dir/e"; then
    printf '[FAIL] refusé pour une mauvaise raison : %s\n' "$label" >&2
    sed -n '1,6p' "$tmp_dir/e" >&2
    exit 1
  fi
done

printf '[OK] 15 contournements href + 3 attributs URL refusés, 5 href légitimes acceptés\n'
