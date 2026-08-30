#!/usr/bin/env python3
"""
Générateur de blocs fonctionnels DSFR (DSFR 1.15.2).

Les blocs fonctionnels sont des patterns de champ pré-construits officiels
(https://www.systeme-de-design.gouv.fr/version-courante/fr/modeles/blocs-fonctionnels),
sourcés page par page. Ils ne sont pas des dossiers dist/component : ce sont
des assemblages documentés de composants (input, select, radio, fieldset).

Chaque bloc respecte la validation différée : aucun attribut required,
aria-required, pattern ou aria-invalid au repos (la contrainte est posée au
premier submit, cf. references/patterns.md).

Sources : pages officielles consultées le 2026-07-07 (branche 1.14), puis
chaque bloc confronté le 2026-08-28 aux exemples rendus
`example/layout/pattern/*` du paquet @gouvfr/dsfr@1.15.2 (aides, autocomplete,
aria-live) et alignés sur leur structure (légendes, liaisons
`aria-labelledby` / `aria-describedby`, groupes de messages). Seuls restent
l'ordre prénom puis nom par défaut (convention du skill, `order` configurable)
et la taille standard des radios de civilité.
"""

import argparse
import inspect
import json
import os
import sys
from html import escape


def esc(text) -> str:
    """Échappe le HTML (préserve 0 et False)."""
    if text is None:
        return ""
    return escape(str(text))


def _require_text(value, name: str) -> str:
    """Libellé, légende ou identifiant non vide : un champ sans nom accessible ou
    un id vide produit un HTML invalide sans erreur."""
    text = str(value if value is not None else "").strip()
    if not text:
        raise ValueError(f"{name} : valeur non vide obligatoire")
    return text


def _require_options(value, name: str = "options") -> list:
    if not isinstance(value, list) or not value:
        raise ValueError(f"{name} : liste non vide attendue")
    return value


def _hint_span(hint, indent: str = "        ", closing_indent: str = "    ") -> str:
    """Aide facultative : un `hint` vide ne doit pas produire un
    `<span class="fr-hint-text"></span>` creux, qui ajoute un conteneur sans
    texte dans l'arbre d'accessibilité."""
    text = str(hint if hint is not None else "").strip()
    if not text:
        return ""
    return f'\n{indent}<span class="fr-hint-text">{esc(hint)}</span>\n{closing_indent}'


def generate_civilite(legend: str = "Sexe", options: list | None = None,
                      name: str = "civilite", id: str = "civilite") -> str:
    """Bloc civilité — fieldset de radios (légende par défaut : « Sexe »).

    Source : blocs-fonctionnels/civilite, confronté à
    `example/layout/pattern/civility` (1.15.2). La civilité binaire
    madame/monsieur est déconseillée par le DSFR ; ce bloc modélise la
    structure officielle : fieldset lié par `aria-labelledby` à sa légende
    (`fr-fieldset__legend--regular`) et à son groupe de messages, radios,
    messages-group.

    Trois écarts assumés avec l'exemple rendu, tous délibérés :
    1. radios en taille standard (l'exemple emploie `fr-radio-group--sm`,
       choix de présentation) ;
    2. `value` posé sur chaque radio (`value="feminin"`) là où l'exemple n'en
       pose aucun : sans `value`, un navigateur transmet « on » et la réponse
       n'est pas exploitable côté serveur ;
    3. libellé « Féminin » accentué, l'exemple écrivant « Feminin ».
    """
    legend = _require_text(legend, "legend")
    id = _require_text(id, "id")
    name = _require_text(name, "name")
    if options is None:
        options = [{"label": "Féminin", "value": "feminin"}, {"label": "Masculin", "value": "masculin"}]
    options = _require_options(options)
    legend_id = f"{id}-legend"
    msgs_id = f"{id}-messages"
    elements = ""
    for i, opt in enumerate(options, 1):
        label = opt.get("label", f"Option {i}") if isinstance(opt, dict) else str(opt)
        value = opt.get("value", str(i)) if isinstance(opt, dict) else str(opt)
        opt_id = f"{id}-{i}"
        elements += f"""
        <div class="fr-fieldset__element">
            <div class="fr-radio-group">
                <input type="radio" id="{esc(opt_id)}" name="{esc(name)}" value="{esc(value)}">
                <label class="fr-label" for="{esc(opt_id)}">{esc(label)}</label>
            </div>
        </div>"""
    return f"""
<fieldset class="fr-fieldset" id="{esc(id)}-fieldset" aria-labelledby="{esc(legend_id)} {esc(msgs_id)}">
    <legend class="fr-fieldset__legend--regular fr-fieldset__legend" id="{esc(legend_id)}">{esc(legend)}</legend>{elements}
    <div class="fr-messages-group" aria-live="polite" id="{esc(msgs_id)}"></div>
</fieldset>"""


def generate_nom_prenom(order: str = "prenom-nom",
                        legend: str = "Demande de nom et prénom",
                        id: str = "name") -> str:
    """Bloc nom et prénom.

    Source : blocs-fonctionnels/nom-et-prenom, confronté à
    `example/layout/pattern/name` (1.15.2) : légende masquée `fr-sr-only`
    liée par `aria-labelledby` avec le groupe de messages, un
    `fr-messages-group` par champ relié par `aria-describedby`,
    `autocomplete`, `spellcheck` et `aria-live` alignés.
    Conflit de source tranché (décision 2026-07-07) : le défaut officiel 1.15.2
    met le Nom en premier, mais la convention du skill (references/patterns.md
    et generate_page.py) est prénom puis nom. Le défaut suit la convention
    skill (order=\"prenom-nom\") ; l'ordre officiel reste disponible via
    order=\"nom-prenom\".
    """
    if order not in ("prenom-nom", "nom-prenom"):
        raise ValueError(f"order '{order}' inconnu : utiliser prenom-nom ou nom-prenom")
    legend = _require_text(legend, "legend")
    id = _require_text(id, "id")
    msgs_id = f"{id}-messages"
    legend_id = f"{id}-legend"

    def field(label: str, autocomplete: str, field_id: str) -> str:
        return f"""
        <div class="fr-fieldset__element">
            <div class="fr-input-group">
                <label class="fr-label" for="{esc(field_id)}">{esc(label)}</label>
                <input class="fr-input" spellcheck="false" autocomplete="{esc(autocomplete)}" name="{esc(autocomplete)}" aria-describedby="{esc(field_id)}-messages" id="{esc(field_id)}" type="text">
                <div class="fr-messages-group" id="{esc(field_id)}-messages" aria-live="polite"></div>
            </div>
        </div>"""

    nom = field("Nom", "family-name", f"{id}-family-name")
    prenom = field("Prénom", "given-name", f"{id}-given-name")
    elements = nom + prenom if order == "nom-prenom" else prenom + nom
    return f"""
<fieldset class="fr-fieldset" id="{esc(id)}-fieldset" aria-labelledby="{esc(legend_id)} {esc(msgs_id)}">
    <legend class="fr-sr-only" id="{esc(legend_id)}">{esc(legend)}</legend>{elements}
    <div class="fr-messages-group" aria-live="polite" id="{esc(msgs_id)}"></div>
</fieldset>"""


def generate_email(label: str = "Adresse électronique",
                   hint: str = "Format attendu : nom@example.com",
                   name: str = "email", id: str = "email",
                   autocomplete: str = "email") -> str:
    """Bloc adresse électronique.

    Source : blocs-fonctionnels/adresse-electronique, confronté à
    `example/layout/pattern/email` (1.15.2) : type=email, spellcheck off,
    autocomplete="email", aide « nom@example.com » et groupe de messages
    relié par `aria-describedby` alignés.
    """
    label = _require_text(label, "label")
    id = _require_text(id, "id")
    name = _require_text(name, "name")
    return f"""
<div class="fr-input-group">
    <label class="fr-label" for="{esc(id)}">{esc(label)}{_hint_span(hint)}</label>
    <input class="fr-input" name="{esc(name)}" autocomplete="{esc(autocomplete)}" spellcheck="false" aria-describedby="{esc(id)}-messages" id="{esc(id)}" type="email">
    <div class="fr-messages-group" id="{esc(id)}-messages" aria-live="polite"></div>
</div>"""


def generate_date_unique(legend: str = "Date de naissance",
                         hint: str = "Texte de description additionnel",
                         id: str = "date") -> str:
    """Bloc date unique — 3 sous-champs Jour/Mois/Année (défaut officiel 1.15.2).

    Source : blocs-fonctionnels/date-unique, confronté à
    `example/layout/pattern/date` (1.15.2) : structure inline, aides et
    `autocomplete="bday-*"` alignés. Variante alternative possible : un champ
    unique type=\"date\" (non générée ici).
    """
    legend = _require_text(legend, "legend")
    id = _require_text(id, "id")
    legend_id = f"{id}-legend"
    msgs_id = f"{id}-messages"

    def part(label: str, example: str, field_name: str, field_id: str,
             autocomplete: str, extra: str = "") -> str:
        return f"""
        <div class="fr-fieldset__element fr-fieldset__element--inline{extra}">
            <div class="fr-input-group">
                <label class="fr-label" for="{esc(field_id)}">{esc(label)}
                    <span class="fr-hint-text">Exemple : {esc(example)}</span>
                </label>
                <input class="fr-input" name="{esc(field_name)}" autocomplete="{esc(autocomplete)}" id="{esc(field_id)}" type="text">
            </div>
        </div>"""

    # Exemple officiel pattern/date 1.15.2 : Jour et Mois en `--number` (6 rem),
    # Année en `--inline-grow --year` (8 rem), jamais les deux sur un même champ.
    jour = part("Jour", "14", "day", f"{id}-day", "bday-day", " fr-fieldset__element--number")
    mois = part("Mois", "12", "month", f"{id}-month", "bday-month", " fr-fieldset__element--number")
    annee = part("Année", "1984", "year", f"{id}-year", "bday-year",
                 " fr-fieldset__element--inline-grow fr-fieldset__element--year")
    return f"""
<fieldset class="fr-fieldset" id="{esc(id)}-fieldset" aria-labelledby="{esc(legend_id)} {esc(msgs_id)}">
    <legend class="fr-fieldset__legend--regular fr-fieldset__legend" id="{esc(legend_id)}">{esc(legend)}{_hint_span(hint)}</legend>{jour}{mois}{annee}
    <div class="fr-messages-group" id="{esc(msgs_id)}" aria-live="polite"></div>
</fieldset>"""


def generate_societe(kind: str = "siret", id: str = "siret") -> str:
    """Bloc société.

    Source : blocs-fonctionnels/societe, confronté à
    `example/layout/pattern/company` (1.15.2) : légende masquée `fr-sr-only`
    liée par `aria-labelledby` avec le groupe de messages. kind=\"siret\"
    (défaut) : numéro de SIRET + lien annuaire des entreprises.
    kind=\"type\" : liste dérivée Type de société.
    """
    if kind not in ("siret", "type"):
        raise ValueError(f"kind '{kind}' inconnu : utiliser siret ou type")
    id = _require_text(id, "id")
    if kind == "type":
        msgs_id = f"{id}-messages"
        types = [
            ("EI", "Entrepreneur individuel (EI)"),
            ("EURL", "Entreprise unipersonnelle à responsabilité limitée (EURL)"),
            ("SARL", "Société à responsabilité limitée (SARL)"),
            ("SASU", "Société par actions simplifiée unipersonnelle (SASU)"),
            ("SAS", "Société par actions simplifiée (SAS)"),
            ("SA", "Société anonyme (SA)"),
            ("SNC", "Société en nom collectif (SNC)"),
            ("SCS", "Société en commandite simple (SCS)"),
            ("SCA", "Société en commandite par actions (SCA)"),
        ]
        opts = "".join(f'\n                <option value="{esc(v)}">{esc(l)}</option>' for v, l in types)
        return f"""
<fieldset class="fr-fieldset" id="{esc(id)}-fieldset" aria-labelledby="{esc(id)}-legend {esc(msgs_id)}">
    <legend class="fr-sr-only" id="{esc(id)}-legend">Type de société</legend>
    <div class="fr-fieldset__element">
        <div class="fr-select-group">
            <label for="{esc(id)}-select" class="fr-label">Type de société</label>
            <select class="fr-select" aria-describedby="{esc(id)}-select-messages" id="{esc(id)}-select" name="structure">
                <option value="" selected disabled>Sélectionner une option</option>{opts}
            </select>
            <div class="fr-messages-group" id="{esc(id)}-select-messages" aria-live="polite"></div>
        </div>
    </div>
    <div class="fr-messages-group" id="{esc(msgs_id)}" aria-live="polite"></div>
</fieldset>"""

    field_msgs = f"{id}-messages"
    fset_msgs = f"{id}-fieldset-messages"
    return f"""
<fieldset class="fr-fieldset" id="{esc(id)}-fieldset" aria-labelledby="{esc(id)}-legend {esc(fset_msgs)}">
    <legend class="fr-sr-only" id="{esc(id)}-legend">SIRET de l'entreprise</legend>
    <div class="fr-fieldset__element">
        <div class="fr-input-group">
            <label for="{esc(id)}-input" class="fr-label">Numéro de SIRET</label>
            <input class="fr-input" aria-describedby="{esc(field_msgs)}" name="siret" type="text" id="{esc(id)}-input">
            <div class="fr-messages-group" id="{esc(field_msgs)}" aria-live="polite"></div>
        </div>
    </div>
    <div class="fr-fieldset__element fr-mt-n1v">
        <a class="fr-link" target="_blank" rel="noopener" title="Annuaire des entreprises - nouvelle fenêtre" href="https://annuaire-entreprises.data.gouv.fr/">Annuaire des entreprises</a>
    </div>
    <div class="fr-messages-group" id="{esc(fset_msgs)}" aria-live="polite"></div>
</fieldset>"""


# Source unique des blocs fonctionnels : nom public -> fonction génératrice.
# La fonction elle-même est exposée (et non une lambda de dépliage) pour que
# ses paramètres soient inspectables avant appel.
FIELDS = {
    "civilite": generate_civilite,
    "nom-prenom": generate_nom_prenom,
    "email": generate_email,
    "date-unique": generate_date_unique,
    "societe": generate_societe,
}


def list_fields() -> None:
    """Affiche les blocs fonctionnels disponibles."""
    print("Blocs fonctionnels (génération paramétrable) :")
    for name in sorted(FIELDS.keys()):
        print(f"  - {name}")


def main():
    parser = argparse.ArgumentParser(
        description=f"Générateur de blocs fonctionnels DSFR ({len(FIELDS)} blocs : civilite, nom-prenom, email, date-unique, societe)")
    parser.add_argument("field", nargs="?", help="Bloc fonctionnel à générer", choices=list(FIELDS.keys()) + ["list"])
    parser.add_argument("--config", help="Configuration JSON du bloc", type=str)
    parser.add_argument("--output", help="Fichier de sortie ; refuse d'écraser un fichier existant")
    parser.add_argument("--list", action="store_true", help="Lister les blocs disponibles")

    args = parser.parse_args()

    if args.list or args.field == "list":
        if args.output:
            # --output n'écrit que du HTML : sans ce refus, l'appelant scripté
            # croit le fichier créé alors que la liste part sur stdout.
            print("Erreur : --output est incompatible avec la liste des blocs ; retirer --output", file=sys.stderr)
            sys.exit(2)
        list_fields()
        return

    if not args.field:
        if args.config or args.output:
            print("Erreur : bloc fonctionnel à générer manquant (civilite, nom-prenom, email, date-unique, societe)", file=sys.stderr)
            sys.exit(1)
        # stdout est réservé au HTML généré : l'aide part sur stderr et le code
        # de sortie reste non nul, aucun bloc n'ayant été produit.
        parser.print_help(sys.stderr)
        sys.exit(2)

    config = {}
    if args.config:
        try:
            config = json.loads(args.config)
        except json.JSONDecodeError as e:
            print(f"Erreur : JSON invalide dans --config : {e}", file=sys.stderr)
            sys.exit(1)
        if not isinstance(config, dict):
            print("Erreur : --config doit être un objet JSON (dictionnaire de paramètres)", file=sys.stderr)
            sys.exit(1)

    # Clés inconnues rejetées avant l'appel : le `try` ne couvre plus que les
    # refus de validation du bloc, jamais un bogue interne du générateur, qui
    # serait sinon requalifié en « paramètre invalide ».
    generator = FIELDS[args.field]
    accepted = tuple(inspect.signature(generator).parameters)
    unknown = [key for key in config if key not in accepted]
    if unknown:
        print(f"Erreur : paramètre invalide pour '{args.field}' : clé(s) inconnue(s) {', '.join(sorted(unknown))} ; paramètres acceptés : {', '.join(accepted)}", file=sys.stderr)
        sys.exit(1)

    try:
        html = generator(**config)
    except ValueError as e:
        print(f"Erreur : paramètre invalide pour '{args.field}' : {e}", file=sys.stderr)
        sys.exit(1)

    if args.output is not None and not args.output.strip():
        print("Erreur : --output vide ; omettre l'option pour écrire sur stdout", file=sys.stderr)
        sys.exit(1)
    if args.output:
        output_dir = os.path.dirname(args.output)
        if output_dir and not os.path.exists(output_dir):
            print(f"Erreur : le dossier '{output_dir}' n'existe pas", file=sys.stderr)
            sys.exit(1)
        if os.path.exists(args.output):
            print(f"Erreur : le fichier '{args.output}' existe déjà. Choisir un autre chemin ou supprimer explicitement le fichier.", file=sys.stderr)
            sys.exit(1)
        try:
            with open(args.output, "w", encoding="utf-8") as f:
                f.write(html)
        except OSError as e:
            print(f"Erreur : impossible d'écrire '{args.output}' : {e.strerror}", file=sys.stderr)
            sys.exit(1)
        print(f"Bloc fonctionnel généré : {args.output}")
    else:
        if hasattr(sys.stdout, "reconfigure"):
            sys.stdout.reconfigure(encoding="utf-8")
        print(html)


if __name__ == "__main__":
    main()
