#!/usr/bin/env python3
"""
Générateur de pages DSFR complètes
Crée des pages HTML avec la structure et les composants DSFR
"""

import argparse
import json
import os
import re
import sys
from html import escape

sys.dont_write_bytecode = True
from generate_component import write_output  # noqa: E402

BRAND_MODES = {"neutral", "republique"}
# Version cible, surchargeable par DSFR_OFFICIAL_VERSION comme dans
# list_icons.py et playwright_dsfr_helpers.js : un seul point de bascule pour
# toute la chaîne d'exécution.
DSFR_VERSION_RE = re.compile(r"^\d+\.\d+\.\d+(?:[.-][0-9A-Za-z.]+)?$")


def _dsfr_version() -> str:
    """Version DSFR cible : DSFR_OFFICIAL_VERSION si elle est un numéro de version, sinon le repli."""
    raw = os.environ.get("DSFR_OFFICIAL_VERSION") or "1.15.3"
    if not DSFR_VERSION_RE.fullmatch(raw):
        raise SystemExit(f"Erreur : DSFR_OFFICIAL_VERSION invalide ({raw[:40]!r}) : numéro de version attendu, par exemple 1.15.3")
    return raw


DSFR_VERSION = _dsfr_version()
DSFR_ASSETS_BASE = f"https://cdn.jsdelivr.net/npm/@gouvfr/dsfr@{DSFR_VERSION}/dist/"


def esc(text: str) -> str:
    """Échappe le HTML pour éviter les injections XSS."""
    return "" if text is None else escape(str(text))


ASSETS_NOISE_RE = re.compile(r"[\x00-\x20\x7f]")
ASSETS_SCHEME_RE = re.compile(r"^([a-z][a-z0-9+.\-]*):", re.IGNORECASE)
ASSETS_FORBIDDEN_CHARS = frozenset('"\'<>')


def _safe_assets_prefix(prefix) -> str:
    """Valide le préfixe d'assets : URL http(s) ou chemin, sans caractère de
    rupture d'attribut. La valeur est ensuite échappée à l'interpolation."""
    value = str(prefix).strip()
    if not value:
        raise ValueError("assets : préfixe vide")
    if any(ch.isspace() or ch in ASSETS_FORBIDDEN_CHARS for ch in value):
        raise ValueError("assets : caractères interdits dans le préfixe (espace, guillemet, chevron)")
    normalised = ASSETS_NOISE_RE.sub("", value)
    scheme = ASSETS_SCHEME_RE.match(normalised)
    if scheme and scheme.group(1).lower() not in ("http", "https"):
        raise ValueError(f"assets : schéma '{scheme.group(1)}' refusé (http, https ou chemin)")
    return value


def normalize_generated_html(html: str) -> str:
    """Retire les liens factices qui ne doivent jamais sortir du générateur."""
    normalized = html.replace('href="#"', 'href="/"').replace("href='#'", "href='/'")
    return "\n".join(line.rstrip() for line in normalized.splitlines()) + "\n"


# Source unique des types de page. check_generated_outputs.py la lit d'ici :
# une liste dupliquée dans le validateur finissait par diverger sans bruit.
PAGE_TYPES = [
    "standard", "landing", "form", "dashboard", "error", "login",
    "account", "search", "confirmation", "list", "detail", "sitemap",
]


def _js_string(value) -> str:
    """Littéral de chaîne JavaScript sûr pour inclusion dans un <script>."""
    return json.dumps(str(value)).replace("</", "<\\/")


def generate_deferred_validation_script(form_id: str, required_ids: list[str]) -> str:
    """Ajoute les contraintes natives seulement après tentative d'envoi."""
    # Contexte JavaScript : json.dumps produit un littéral de chaîne JS valide
    # et échappe quotes, barres obliques inverses et </script>. esc() ne
    # protège que le contexte HTML et laisserait une apostrophe casser le
    # script, ou une séquence ');… l'injecter.
    ids = ", ".join(_js_string(field_id) for field_id in required_ids)
    return f"""
                    <script>
                    (function () {{
                      var form = document.getElementById({_js_string(form_id)});
                      if (!form) return;
                      var requiredFieldIds = [{ids}];
                      var fields = requiredFieldIds
                        .map(function (id) {{ return document.getElementById(id); }})
                        .filter(function (field) {{ return Boolean(field); }});

                      function groupOf(field) {{
                        return field.closest('.fr-input-group, .fr-select-group, .fr-checkbox-group, .fr-password');
                      }}

                      function errorId(field) {{
                        return field.id + '-error';
                      }}

                      function messageFor(field) {{
                        var v = field.validity;
                        if (v.valueMissing) {{
                          if (field.type === 'checkbox') return "Veuillez cocher cette case.";
                          if (field.tagName === 'SELECT') return "Veuillez sélectionner une option.";
                          return "Ce champ est obligatoire.";
                        }}
                        if (v.typeMismatch && field.type === 'email') return "Format invalide (ex. : nom@domaine.fr).";
                        if (v.badInput) return "La valeur saisie est invalide.";
                        return "Ce champ est invalide.";
                      }}

                      function applyClientConstraints() {{
                        fields.forEach(function (field) {{
                          field.required = true;
                          field.setAttribute('aria-required', 'true');
                        }});
                      }}

                      function setError(field, message) {{
                        var group = groupOf(field);
                        var id = errorId(field);
                        var err = document.getElementById(id);
                        if (message) {{
                          field.setAttribute('aria-invalid', 'true');
                          field.setAttribute('aria-describedby', id);
                          if (group && group.classList.contains('fr-input-group')) group.classList.add('fr-input-group--error');
                          if (group && group.classList.contains('fr-select-group')) group.classList.add('fr-select-group--error');
                          if (!err) {{
                            err = document.createElement('p');
                            err.id = id;
                            err.className = 'fr-message fr-message--error';
                            var messages = group ? group.querySelector('.fr-messages-group') : null;
                            if (!messages) {{
                              messages = document.createElement('div');
                              messages.className = 'fr-messages-group';
                              messages.setAttribute('aria-live', 'polite');
                              if (group) {{
                                group.appendChild(messages);
                              }} else {{
                                field.insertAdjacentElement('afterend', messages);
                              }}
                            }}
                            messages.appendChild(err);
                          }}
                          err.textContent = message;
                        }} else {{
                          field.removeAttribute('aria-invalid');
                          field.removeAttribute('aria-describedby');
                          if (group) group.classList.remove('fr-input-group--error', 'fr-select-group--error');
                          if (err) err.remove();
                        }}
                      }}

                      function validateField(field) {{
                        var valid = field.checkValidity();
                        setError(field, valid ? '' : messageFor(field));
                        return valid;
                      }}

                      function dropClientConstraints() {{
                        fields.forEach(function (field) {{
                          field.required = false;
                          field.removeAttribute('required');
                          field.removeAttribute('aria-required');
                        }});
                      }}

                      function clearClientConstraints() {{
                        dropClientConstraints();
                        fields.forEach(function (field) {{ setError(field, ''); }});
                      }}

                      form.addEventListener('submit', function (event) {{
                        applyClientConstraints();
                        var invalid = fields.filter(function (field) {{ return !validateField(field); }});
                        if (invalid.length) {{
                          event.preventDefault();
                          form.reportValidity();
                        }}
                      }});

                      fields.forEach(function (field) {{
                        field.addEventListener('input', function () {{
                          if (field.hasAttribute('required')) validateField(field);
                        }});
                        field.addEventListener('change', function () {{
                          if (field.hasAttribute('required')) validateField(field);
                        }});
                      }});

                      form.addEventListener('reset', clearClientConstraints);
                      // Au chargement : aucune contrainte native au repos, mais les
                      // messages d'erreur rendus côté serveur sont conservés.
                      dropClientConstraints();
                    }})();
                    </script>"""


def generate_skiplinks(include_header: bool = True, include_footer: bool = True) -> str:
    """Génère les liens d'évitement DSFR, limités aux cibles présentes."""
    links = ['                <li><a class="fr-link" href="#contenu">Contenu</a></li>']
    if include_header:
        links.append('                <li><a class="fr-link" href="#navigation">Menu</a></li>')
    if include_footer:
        links.append('                <li><a class="fr-link" href="#footer">Pied de page</a></li>')
    items = "\n".join(links)
    return f"""
    <div class="fr-skiplinks">
        <nav class="fr-container" role="navigation" aria-label="Accès rapide">
            <ul class="fr-skiplinks__list">
{items}
            </ul>
        </nav>
    </div>"""


def generate_html_page(
    title: str = "Nom du service",
    page_type: str = "standard",
    content: str = "",
    include_header: bool = True,
    include_footer: bool = True,
    dark_mode: bool = False,
    brand_mode: str = "neutral",
    assets_prefix: str | None = None,
    raw_main: bool = False,
    header_html: str | None = None,
    footer_html: str | None = None,
    description: str | None = None
) -> str:
    """Génère une page HTML complète avec DSFR"""
    if brand_mode not in BRAND_MODES:
        raise ValueError(f"brand_mode must be one of {sorted(BRAND_MODES)}")

    if not str(title or "").strip():
        raise ValueError("title : titre de page obligatoire (il alimente <title> et <h1>)")
    # data-fr-scheme est une condition de fonctionnement du paramètre
    # d'affichage (references/theming.md) : « system » par défaut, « dark » avec --dark.
    dark_scheme = ' data-fr-scheme="dark"' if dark_mode else ' data-fr-scheme="system"'
    safe_title = esc(title)
    meta_description = (
        f'\n    <meta name="description" content="{esc(description)}">'
        if description else ""
    )
    assets_base = (
        esc(_safe_assets_prefix(assets_prefix).rstrip("/") + "/") if assets_prefix is not None else DSFR_ASSETS_BASE
    )
    # Le contenu fourni par l'appelant est inséré après la normalisation du
    # gabarit : les liens factices du générateur sont réécrits, le contenu
    # utilisateur (dont un éventuel exemple de code) reste intact.
    user_content = content or ""
    marker = "\x00DSFR-USER-CONTENT\x00" if user_content else ""
    if raw_main:
        main_inner = marker
    else:
        main_inner = f'<div class="fr-container">\n            {generate_page_content(page_type, marker, title)}\n        </div>'

    head_block = header_html if header_html is not None else (generate_header(brand_mode) if include_header else "")
    foot_block = footer_html if footer_html is not None else (generate_footer(brand_mode) if include_footer else "")
    # Les liens d'évitement suivent le markup effectif : un en-tête ou un pied
    # de page fourni sans ses ancres ne reçoit pas de lien orphelin.
    skiplinks_html = generate_skiplinks('id="navigation"' in head_block, 'id="footer"' in foot_block)

    html = f"""<!DOCTYPE html>
<html lang="fr"{dark_scheme}>
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1, shrink-to-fit=no">
    <title>{safe_title}</title>
    {meta_description}

    <!-- DSFR CSS -->
    <link rel="stylesheet" href="{assets_base}dsfr.min.css">
    <link rel="stylesheet" href="{assets_base}utility/icons/icons.min.css">

    <!-- Favicon -->
    <link rel="apple-touch-icon" href="{assets_base}favicon/apple-touch-icon.png">
    <link rel="icon" href="{assets_base}favicon/favicon.svg" type="image/svg+xml">
</head>
<body id="top">
    {skiplinks_html}
    {head_block}

    <main id="contenu">
        {main_inner}
    </main>

    {foot_block}

    <!-- DSFR JS -->
    <script type="module" src="{assets_base}dsfr.module.min.js"></script>
    <script nomodule src="{assets_base}dsfr.nomodule.min.js"></script>
</body>
</html>"""

    html = normalize_generated_html(html)
    return html.replace(marker, user_content) if marker else html


def generate_header(brand_mode: str = "neutral") -> str:
    """Génère l'en-tête DSFR"""
    if brand_mode not in BRAND_MODES:
        raise ValueError(f"brand_mode must be one of {sorted(BRAND_MODES)}")

    brand_identity = ""
    if brand_mode == "republique":
        brand_identity = """
                            <div class="fr-header__logo">
                                <a href="/" title="Accueil - Nom du site">
                                    <p class="fr-logo">République<br>Française</p>
                                </a>
                            </div>"""

    return f"""
    <header role="banner" class="fr-header">
        <div class="fr-header__body">
            <div class="fr-container">
                <div class="fr-header__body-row">
                    <div class="fr-header__brand fr-enlarge-link">
                        <div class="fr-header__brand-top">
                            {brand_identity}
                            <div class="fr-header__navbar">
                                <button id="button-search" class="fr-btn--search fr-btn" data-fr-opened="false" aria-controls="modal-search" title="Rechercher" type="button">
                                    Rechercher
                                </button>
                                <button id="button-menu" class="fr-btn--menu fr-btn" data-fr-opened="false" aria-controls="modal-menu" aria-haspopup="menu" title="Menu" type="button">
                                    Menu
                                </button>
                            </div>
                        </div>
                        <div class="fr-header__service">
                            <a href="/" title="Accueil - Nom du site">
                                <p class="fr-header__service-title">Nom du service</p>
                            </a>
                            <p class="fr-header__service-tagline">Baseline - précisions sur l'organisation</p>
                        </div>
                    </div>
                    <div class="fr-header__tools">
                        <div class="fr-header__tools-links">
                            <ul class="fr-btns-group">
                                <li>
                                    <a class="fr-btn fr-btn--icon-left fr-icon-account-circle-line" href="/connexion">
                                        Se connecter
                                    </a>
                                </li>
                            </ul>
                        </div>
                        <div class="fr-header__search fr-modal" id="modal-search" aria-labelledby="button-search">
                            <div class="fr-container fr-container-lg--fluid">
                                <button class="fr-btn--close fr-btn" aria-controls="modal-search" title="Fermer" type="button">
                                    Fermer
                                </button>
                                <form action="/recherche" method="get">
                                    <div class="fr-search-bar" id="search-header" role="search">
                                        <label class="fr-label" for="search-header-input">
                                            Rechercher
                                        </label>
                                        <input class="fr-input" type="search" id="search-header-input" name="search">
                                        <button type="submit" class="fr-btn" title="Rechercher">
                                            Rechercher
                                        </button>
                                    </div>
                                </form>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
        <div class="fr-header__menu fr-modal" id="modal-menu" aria-labelledby="button-menu">
            <div class="fr-container">
                <button class="fr-btn--close fr-btn" aria-controls="modal-menu" title="Fermer" type="button">
                    Fermer
                </button>
                <div class="fr-header__menu-links"></div>
                <nav class="fr-nav" id="navigation" role="navigation" aria-label="Menu principal">
                    <ul class="fr-nav__list">
                        <li class="fr-nav__item">
                            <a class="fr-nav__link" href="/" target="_self">Accueil</a>
                        </li>
                        <li class="fr-nav__item">
                            <a class="fr-nav__link" href="/services" target="_self">Services</a>
                        </li>
                        <li class="fr-nav__item">
                            <a class="fr-nav__link" href="/documentation" target="_self">Documentation</a>
                        </li>
                        <li class="fr-nav__item">
                            <a class="fr-nav__link" href="/contact" target="_self">Contact</a>
                        </li>
                    </ul>
                </nav>
            </div>
        </div>
    </header>"""


def generate_footer(brand_mode: str = "neutral") -> str:
    """Génère le pied de page DSFR"""
    if brand_mode not in BRAND_MODES:
        raise ValueError(f"brand_mode must be one of {sorted(BRAND_MODES)}")

    brand_html = """
                <div class="fr-footer__brand">
                    <p>Nom du service</p>
                </div>"""
    if brand_mode == "republique":
        brand_html = """
                <div class="fr-footer__brand fr-enlarge-link">
                    <a href="/" title="Accueil">
                        <p class="fr-logo">République<br>Française</p>
                    </a>
                </div>"""

    return f"""
    <footer class="fr-footer" role="contentinfo" id="footer">
        <div class="fr-container">
            <div class="fr-footer__body">
                {brand_html}
                <div class="fr-footer__content">
                    <p class="fr-footer__content-desc">Description du service et de ses fonctionnalités</p>
                    <ul class="fr-footer__content-list">
                        <li class="fr-footer__content-item">
                            <a class="fr-footer__content-link" target="_blank" rel="noopener external" title="legifrance.gouv.fr - nouvelle fenêtre" href="https://legifrance.gouv.fr">legifrance.gouv.fr</a>
                        </li>
                        <li class="fr-footer__content-item">
                            <a class="fr-footer__content-link" target="_blank" rel="noopener external" title="gouvernement.fr - nouvelle fenêtre" href="https://gouvernement.fr">gouvernement.fr</a>
                        </li>
                        <li class="fr-footer__content-item">
                            <a class="fr-footer__content-link" target="_blank" rel="noopener external" title="service-public.gouv.fr - nouvelle fenêtre" href="https://service-public.gouv.fr">service-public.gouv.fr</a>
                        </li>
                        <li class="fr-footer__content-item">
                            <a class="fr-footer__content-link" target="_blank" rel="noopener external" title="data.gouv.fr - nouvelle fenêtre" href="https://data.gouv.fr">data.gouv.fr</a>
                        </li>
                    </ul>
                </div>
            </div>
            <div class="fr-footer__bottom">
                <ul class="fr-footer__bottom-list">
                    <li class="fr-footer__bottom-item">
                        <a class="fr-footer__bottom-link" href="/plan-du-site">Plan du site</a>
                    </li>
                    <li class="fr-footer__bottom-item">
                        <a class="fr-footer__bottom-link" href="/accessibilite">Accessibilité : non conforme</a>
                    </li>
                    <li class="fr-footer__bottom-item">
                        <a class="fr-footer__bottom-link" href="/mentions-legales">Mentions légales</a>
                    </li>
                    <li class="fr-footer__bottom-item">
                        <a class="fr-footer__bottom-link" href="/donnees-personnelles">Données personnelles</a>
                    </li>
                    <li class="fr-footer__bottom-item">
                        <a class="fr-footer__bottom-link" href="/gestion-des-cookies">Gestion des cookies</a>
                    </li>
                </ul>
                <div class="fr-footer__bottom-copy">
                    <p>Sauf mention contraire, tous les contenus de ce site sont sous <a href="https://github.com/etalab/licence-ouverte/blob/master/LO.md" target="_blank" rel="noopener external" title="licence etalab-2.0 - nouvelle fenêtre">licence etalab-2.0</a></p>
                </div>
            </div>
        </div>
    </footer>"""


def generate_page_content(page_type: str, custom_content: str = "", title: str = "") -> str:
    """Génère le contenu principal selon le type de page"""
    heading = esc(title) if title else "Titre de la page"
    if page_type not in PAGE_TYPES:
        raise ValueError(f"type de page '{page_type}' inconnu : utiliser {', '.join(PAGE_TYPES)}")

    if page_type == "landing":
        return f"""
            <div class="fr-grid-row fr-grid-row--center fr-py-8w">
                <div class="fr-col-12 fr-col-md-10 fr-col-lg-8">
                    <h1>{heading}</h1>
                    <p class="fr-text--lead">Service numérique de l'État français pour simplifier vos démarches administratives.</p>

                    <div class="fr-callout">
                        <h2 class="fr-callout__title">Information importante</h2>
                        <p class="fr-callout__text">Ce service est en phase de test. Vos retours nous aident à l'améliorer.</p>
                    </div>

                    <div class="fr-grid-row fr-grid-row--gutters fr-mt-6w">
                        <div class="fr-col-12 fr-col-md-4">
                            <div class="fr-tile fr-enlarge-link">
                                <div class="fr-tile__body">
                                    <div class="fr-tile__content">
                                        <h3 class="fr-tile__title">
                                        <a href="/services/service-1">Service 1</a>
                                    </h3>
                                        <p class="fr-tile__desc">Description du premier service</p>
                                    </div>
                                </div>
                            </div>
                        </div>
                        <div class="fr-col-12 fr-col-md-4">
                            <div class="fr-tile fr-enlarge-link">
                                <div class="fr-tile__body">
                                    <div class="fr-tile__content">
                                        <h3 class="fr-tile__title">
                                        <a href="/services/service-2">Service 2</a>
                                    </h3>
                                        <p class="fr-tile__desc">Description du deuxième service</p>
                                    </div>
                                </div>
                            </div>
                        </div>
                        <div class="fr-col-12 fr-col-md-4">
                            <div class="fr-tile fr-enlarge-link">
                                <div class="fr-tile__body">
                                    <div class="fr-tile__content">
                                        <h3 class="fr-tile__title">
                                        <a href="/services/service-3">Service 3</a>
                                    </h3>
                                        <p class="fr-tile__desc">Description du troisième service</p>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                    {custom_content}
                </div>
            </div>"""

    elif page_type == "form":
        return f"""
            <div class="fr-grid-row fr-grid-row--center fr-py-8w">
                <div class="fr-col-12 fr-col-md-8 fr-col-lg-6">
                    <h1>{heading}</h1>

                    <p class="fr-text--sm">Sauf mention contraire, tous les champs sont obligatoires.</p>
                    <form id="dsfr-generated-form" action="/submit" method="post" novalidate>
                        <fieldset class="fr-fieldset" aria-labelledby="identity-legend">
                            <legend class="fr-fieldset__legend" id="identity-legend">Vos informations</legend>

                            <div class="fr-input-group">
                                <label class="fr-label" for="prenom">Prénom
                                    <span class="fr-hint-text">Tel qu'il figure sur votre pièce d'identité</span>
                                </label>
                                <input class="fr-input" type="text" id="prenom" name="prenom"
                                       autocomplete="given-name">
                            </div>

                            <div class="fr-input-group">
                                <label class="fr-label" for="nom">Nom de famille
                                    <span class="fr-hint-text">Tel qu'il figure sur votre pièce d'identité</span>
                                </label>
                                <input class="fr-input" type="text" id="nom" name="nom"
                                       autocomplete="family-name">
                            </div>

                            <div class="fr-input-group">
                                <label class="fr-label" for="email">Adresse électronique
                                    <span class="fr-hint-text">Format : nom@domaine.fr</span>
                                </label>
                                <input class="fr-input" type="email" id="email" name="email"
                                       autocomplete="email">
                            </div>

                            <div class="fr-input-group">
                                <label class="fr-label" for="message">Message</label>
                                <textarea class="fr-input" id="message" name="message" rows="5"></textarea>
                            </div>

                            <div class="fr-checkbox-group">
                                <input type="checkbox" id="conditions" name="conditions">
                                <label class="fr-label" for="conditions">
                                    J'accepte les conditions générales d'utilisation
                                </label>
                            </div>
                        </fieldset>

                        <ul class="fr-btns-group fr-btns-group--right">
                            <li>
                                <button class="fr-btn" type="submit">
                                    Envoyer
                                </button>
                            </li>
                            <li>
                                <button class="fr-btn fr-btn--secondary" type="reset">
                                    Annuler
                                </button>
                            </li>
                        </ul>
                    </form>
                    {generate_deferred_validation_script("dsfr-generated-form", ["prenom", "nom", "email", "message", "conditions"])}
                    {custom_content}
                </div>
            </div>"""

    elif page_type == "dashboard":
        return f"""
            <div class="fr-py-8w">
                <h1>{heading}</h1>

                <div class="fr-tabs">
                    <ul class="fr-tabs__list" role="tablist" aria-label="Navigation par onglets">
                        <li role="presentation">
                            <button type="button" id="tabpanel-1" class="fr-tabs__tab" tabindex="0" role="tab" aria-selected="true" aria-controls="tabpanel-1-panel">Vue d'ensemble</button>
                        </li>
                        <li role="presentation">
                            <button type="button" id="tabpanel-2" class="fr-tabs__tab" tabindex="-1" role="tab" aria-selected="false" aria-controls="tabpanel-2-panel">Statistiques</button>
                        </li>
                        <li role="presentation">
                            <button type="button" id="tabpanel-3" class="fr-tabs__tab" tabindex="-1" role="tab" aria-selected="false" aria-controls="tabpanel-3-panel">Paramètres</button>
                        </li>
                    </ul>
                    <div id="tabpanel-1-panel" class="fr-tabs__panel fr-tabs__panel--selected" role="tabpanel" aria-labelledby="tabpanel-1" tabindex="0">
                        <div class="fr-grid-row fr-grid-row--gutters">
                            <div class="fr-col-12 fr-col-md-3">
                                <div class="fr-callout">
                                        <h2 class="fr-callout__title">Utilisateurs actifs</h2>
                                        <p class="fr-callout__text"><span class="fr-text--bold fr-text--lg">1 234</span></p>
                                    </div>
                            </div>
                            <div class="fr-col-12 fr-col-md-3">
                                <div class="fr-callout">
                                        <h2 class="fr-callout__title">Nouveaux cette semaine</h2>
                                        <p class="fr-callout__text"><span class="fr-text--bold fr-text--lg">567</span></p>
                                    </div>
                            </div>
                            <div class="fr-col-12 fr-col-md-3">
                                <div class="fr-callout">
                                        <h2 class="fr-callout__title">Taux de satisfaction</h2>
                                        <p class="fr-callout__text"><span class="fr-text--bold fr-text--lg">89%</span></p>
                                    </div>
                            </div>
                            <div class="fr-col-12 fr-col-md-3">
                                <div class="fr-callout">
                                        <h2 class="fr-callout__title">Tickets en attente</h2>
                                        <p class="fr-callout__text"><span class="fr-text--bold fr-text--lg">12</span></p>
                                    </div>
                            </div>
                        </div>

                        <div class="fr-table fr-mt-6w">
                            <div class="fr-table__wrapper">
                                <div class="fr-table__container">
                                    <div class="fr-table__content">
                                        <table>
                                            <caption>Dernières activités</caption>
                                            <thead>
                                                <tr>
                                                    <th scope="col">Date</th>
                                                    <th scope="col">Utilisateur</th>
                                                    <th scope="col">Action</th>
                                                    <th scope="col">Statut</th>
                                                </tr>
                                            </thead>
                                            <tbody>
                                                <tr>
                                                    <td>20/10/2025</td>
                                                    <td>Jean Dupont</td>
                                                    <td>Création de compte</td>
                                                    <td><span class="fr-badge fr-badge--success">Succès</span></td>
                                                </tr>
                                                <tr>
                                                    <td>20/10/2025</td>
                                                    <td>Marie Martin</td>
                                                    <td>Modification profil</td>
                                                    <td><span class="fr-badge fr-badge--success">Succès</span></td>
                                                </tr>
                                                <tr>
                                                    <td>19/10/2025</td>
                                                    <td>Pierre Durand</td>
                                                    <td>Tentative connexion</td>
                                                    <td><span class="fr-badge fr-badge--error">Échec</span></td>
                                                </tr>
                                            </tbody>
                                        </table>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                    <div id="tabpanel-2-panel" class="fr-tabs__panel" role="tabpanel" aria-labelledby="tabpanel-2" tabindex="0">
                        <p>Contenu de l'onglet Statistiques. Ajoutez vos graphiques et indicateurs ici.</p>
                    </div>
                    <div id="tabpanel-3-panel" class="fr-tabs__panel" role="tabpanel" aria-labelledby="tabpanel-3" tabindex="0">
                        <p>Contenu de l'onglet Paramètres. Ajoutez vos options de configuration ici.</p>
                    </div>
                </div>
                {custom_content}
            </div>"""

    elif page_type == "error":
        return f"""
            <div class="fr-grid-row fr-grid-row--center fr-py-8w">
                <div class="fr-col-12 fr-col-md-8 fr-col-lg-6" style="text-align: center;">
                    <h1>{heading}</h1>
                    <p class="fr-text--lead">Erreur 404</p>
                    <p class="fr-text--lg fr-mb-4w">La page que vous cherchez est introuvable. Excusez-nous pour la gêne occasionnée.</p>
                    <p class="fr-mb-2w">Si vous avez tapé l'adresse web dans le navigateur, vérifiez qu'elle est correcte. La page n'est peut-être plus disponible.</p>
                    <ul class="fr-btns-group fr-btns-group--inline-md fr-btns-group--center">
                        <li>
                            <a class="fr-btn" href="/">Retourner à l'accueil</a>
                        </li>
                        <li>
                            <a class="fr-btn fr-btn--secondary" href="/contact">Contactez-nous</a>
                        </li>
                    </ul>
                    {custom_content}
                </div>
            </div>"""

    elif page_type == "login":
        return f"""
            <div class="fr-grid-row fr-grid-row--center fr-py-8w">
                <div class="fr-col-12 fr-col-md-6 fr-col-lg-4">
                    <h1>{heading}</h1>

                    <div class="fr-connect-group fr-mb-6w">
                        <button type="button" class="fr-connect" id="fc-button">
                            <span class="fr-connect__login">S'identifier avec</span>
                            <span class="fr-connect__brand">FranceConnect</span>
                        </button>
                        <p>
                            <a href="https://franceconnect.gouv.fr/" target="_blank" rel="noopener"
                               title="Qu'est-ce que FranceConnect ? - nouvelle fenêtre">
                                Qu'est-ce que FranceConnect ?
                            </a>
                        </p>
                    </div>

                    <div class="fr-hr-or">ou</div>

                    <p class="fr-text--sm fr-mt-4w">Sauf mention contraire, tous les champs sont obligatoires.</p>
                    <form id="dsfr-login-form" action="/login" method="post" novalidate>
                        <div class="fr-input-group">
                            <label class="fr-label" for="login-email">Adresse électronique</label>
                            <input class="fr-input" type="email" id="login-email" name="email"
                                   autocomplete="email">
                        </div>

                        <div class="fr-password">
                            <label class="fr-label" for="login-password">Mot de passe</label>
                            <div class="fr-input-wrap">
                                <input class="fr-password__input fr-input" type="password" id="login-password"
                                       name="password" autocomplete="current-password">
                            </div>
                            <div class="fr-password__checkbox fr-checkbox-group fr-checkbox-group--sm">
                                <input type="checkbox" id="login-show-pwd" aria-label="Afficher le mot de passe">
                                <label class="fr-label" for="login-show-pwd">Afficher</label>
                            </div>
                        </div>

                        <p class="fr-mt-2w">
                            <a href="/mot-de-passe-oublie" class="fr-link">Mot de passe oublié ?</a>
                        </p>

                        <ul class="fr-btns-group fr-mt-4w">
                            <li>
                                <button class="fr-btn" type="submit">Se connecter</button>
                            </li>
                            <li>
                                <a class="fr-btn fr-btn--secondary" href="/inscription">Créer un compte</a>
                            </li>
                        </ul>
                    </form>
                    {generate_deferred_validation_script("dsfr-login-form", ["login-email", "login-password"])}
                    {custom_content}
                </div>
            </div>"""

    elif page_type == "account":
        return f"""
            <div class="fr-grid-row fr-grid-row--center fr-py-8w">
                <div class="fr-col-12 fr-col-md-7 fr-col-lg-5">
                    <h1>{heading}</h1>

                    <div class="fr-connect-group fr-mb-6w">
                        <button type="button" class="fr-connect" id="fc-button">
                            <span class="fr-connect__login">S'identifier avec</span>
                            <span class="fr-connect__brand">FranceConnect</span>
                        </button>
                        <p>
                            <a href="https://franceconnect.gouv.fr/" target="_blank" rel="noopener"
                               title="Qu'est-ce que FranceConnect ? - nouvelle fenêtre">
                                Qu'est-ce que FranceConnect ?
                            </a>
                        </p>
                    </div>

                    <div class="fr-hr-or">ou</div>

                    <p class="fr-text--sm fr-mt-4w">Sauf mention contraire, tous les champs sont obligatoires.</p>
                    <form id="dsfr-account-form" action="/inscription" method="post" novalidate>
                        <div class="fr-input-group">
                            <label class="fr-label" for="account-firstname">Prénom</label>
                            <input class="fr-input" type="text" id="account-firstname" name="given-name"
                                   autocomplete="given-name">
                        </div>

                        <div class="fr-input-group">
                            <label class="fr-label" for="account-lastname">Nom</label>
                            <input class="fr-input" type="text" id="account-lastname" name="family-name"
                                   autocomplete="family-name">
                        </div>

                        <div class="fr-input-group">
                            <label class="fr-label" for="account-email">Adresse électronique</label>
                            <input class="fr-input" type="email" id="account-email" name="email"
                                   autocomplete="email">
                        </div>

                        <div class="fr-password">
                            <label class="fr-label" for="account-password">Mot de passe</label>
                            <div class="fr-input-wrap">
                                <input class="fr-password__input fr-input" type="password" id="account-password"
                                       name="new-password" autocomplete="new-password">
                            </div>
                            <div class="fr-password__checkbox fr-checkbox-group fr-checkbox-group--sm">
                                <input type="checkbox" id="account-show-pwd" aria-label="Afficher le mot de passe">
                                <label class="fr-label" for="account-show-pwd">Afficher</label>
                            </div>
                        </div>

                        <ul class="fr-btns-group fr-mt-4w">
                            <li>
                                <button class="fr-btn" type="submit">Créer un compte</button>
                            </li>
                        </ul>
                    </form>
                    {generate_deferred_validation_script("dsfr-account-form", ["account-firstname", "account-lastname", "account-email", "account-password"])}
                    {custom_content}
                </div>
            </div>"""

    elif page_type == "search":
        return f"""
            <div class="fr-py-8w">
                <div class="fr-grid-row fr-grid-row--center fr-mb-6w">
                    <div class="fr-col-12 fr-col-md-8">
                        <h1>{heading}</h1>
                        <form action="/recherche" method="get">
                            <div class="fr-search-bar fr-search-bar--lg" id="search-page" role="search">
                                <label class="fr-label" for="search-main">Recherche</label>
                                <input class="fr-input" placeholder="Rechercher une démarche, un service..." type="search" id="search-main" name="q">
                                <button type="submit" class="fr-btn" title="Rechercher">Rechercher</button>
                            </div>
                        </form>
                    </div>
                </div>

                <div class="fr-grid-row fr-grid-row--gutters">
                    <div class="fr-col-12 fr-col-md-3">
                        <nav class="fr-sidemenu" aria-label="Filtres">
                            <div class="fr-sidemenu__inner">
                                <div class="fr-sidemenu__title">Filtrer par</div>
                                <ul class="fr-sidemenu__list">
                                    <li class="fr-sidemenu__item">
                                        <a class="fr-sidemenu__link" href="/recherche" aria-current="page">Tous les résultats</a>
                                    </li>
                                    <li class="fr-sidemenu__item">
                                        <a class="fr-sidemenu__link" href="/recherche?categorie=services">Services</a>
                                    </li>
                                    <li class="fr-sidemenu__item">
                                        <a class="fr-sidemenu__link" href="/recherche?categorie=demarches">Démarches</a>
                                    </li>
                                    <li class="fr-sidemenu__item">
                                        <a class="fr-sidemenu__link" href="/recherche?categorie=documents">Documents</a>
                                    </li>
                                </ul>
                            </div>
                        </nav>
                    </div>
                    <div class="fr-col-12 fr-col-md-9">
                        <p class="fr-mb-4w"><strong>12 résultats</strong> pour votre recherche</p>
                        <div class="fr-card fr-enlarge-link fr-card--horizontal fr-mb-3w">
                            <div class="fr-card__body">
                                <div class="fr-card__content">
                                    <h2 class="fr-card__title">
                                        <a href="/resultats/1">Titre du premier résultat</a>
                                    </h2>
                                    <p class="fr-card__desc">Description du résultat avec un extrait du contenu correspondant à la recherche.</p>
                                </div>
                            </div>
                        </div>
                        <div class="fr-card fr-enlarge-link fr-card--horizontal fr-mb-3w">
                            <div class="fr-card__body">
                                <div class="fr-card__content">
                                    <h2 class="fr-card__title">
                                        <a href="/resultats/2">Titre du deuxième résultat</a>
                                    </h2>
                                    <p class="fr-card__desc">Description du deuxième résultat.</p>
                                </div>
                            </div>
                        </div>
                        <nav role="navigation" class="fr-pagination" aria-label="Pagination">
                            <ul class="fr-pagination__list">
                                <li><a class="fr-pagination__link" href="/recherche?page=1" aria-current="page">1</a></li>
                                <li><a class="fr-pagination__link" href="/recherche?page=2">2</a></li>
                                <li><a class="fr-pagination__link" href="/recherche?page=3">3</a></li>
                                <li>
                                    <a class="fr-pagination__link fr-pagination__link--next" href="/recherche?page=2">
                                        Page suivante
                                    </a>
                                </li>
                            </ul>
                        </nav>
                    </div>
                </div>
                {custom_content}
            </div>"""

    elif page_type == "confirmation":
        return f"""
            <div class="fr-grid-row fr-grid-row--center fr-py-8w">
                <div class="fr-col-12 fr-col-md-8 fr-col-lg-6" style="text-align: center;">
                    <div class="fr-alert fr-alert--success fr-mb-4w">
                        <p class="fr-alert__title">Votre demande a bien été enregistrée</p>
                        <p>Vous recevrez une confirmation par courriel dans les prochaines minutes.</p>
                    </div>

                    <h1>{heading}</h1>

                    <div class="fr-callout fr-mt-4w">
                        <h2 class="fr-callout__title">Récapitulatif</h2>
                        <p class="fr-callout__text">
                            <strong>Numéro de dossier :</strong> 2026-XXXX-XXXX<br>
                            <strong>Date de la demande :</strong> 10 mars 2026<br>
                            <strong>Délai de traitement estimé :</strong> 15 jours ouvrés
                        </p>
                    </div>

                    <div class="fr-highlight fr-mt-4w">
                        <p>Conservez votre numéro de dossier. Il vous sera demandé pour tout suivi de votre demande.</p>
                    </div>

                    <ul class="fr-btns-group fr-btns-group--center fr-mt-6w">
                        <li>
                            <a class="fr-btn fr-icon-download-line fr-btn--icon-left" download href="/recapitulatif.pdf">
                                Télécharger le récapitulatif
                            </a>
                        </li>
                        <li>
                            <a class="fr-btn fr-btn--secondary" href="/">Retourner à l'accueil</a>
                        </li>
                    </ul>
                    {custom_content}
                </div>
            </div>"""

    elif page_type == "list":
        return f"""
            <div class="fr-py-8w">
                <h1>{heading}</h1>
                <p class="fr-text--lead fr-mb-6w">Retrouvez l'ensemble des services disponibles.</p>

                <div class="fr-grid-row fr-grid-row--gutters">
                    <div class="fr-col-12 fr-col-md-4">
                        <div class="fr-card fr-enlarge-link">
                            <div class="fr-card__body">
                                <div class="fr-card__content">
                                    <h2 class="fr-card__title">
                                        <a href="/service/1">Premier service</a>
                                    </h2>
                                    <p class="fr-card__desc">Description du premier service disponible.</p>
                                    <div class="fr-card__start">
                                        <ul class="fr-badges-group">
                                            <li><span class="fr-badge fr-badge--info fr-badge--sm">En ligne</span></li>
                                        </ul>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                    <div class="fr-col-12 fr-col-md-4">
                        <div class="fr-card fr-enlarge-link">
                            <div class="fr-card__body">
                                <div class="fr-card__content">
                                    <h2 class="fr-card__title">
                                        <a href="/service/2">Deuxième service</a>
                                    </h2>
                                    <p class="fr-card__desc">Description du deuxième service disponible.</p>
                                    <div class="fr-card__start">
                                        <ul class="fr-badges-group">
                                            <li><span class="fr-badge fr-badge--success fr-badge--sm">Gratuit</span></li>
                                        </ul>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                    <div class="fr-col-12 fr-col-md-4">
                        <div class="fr-card fr-enlarge-link">
                            <div class="fr-card__body">
                                <div class="fr-card__content">
                                    <h2 class="fr-card__title">
                                        <a href="/service/3">Troisième service</a>
                                    </h2>
                                    <p class="fr-card__desc">Description du troisième service disponible.</p>
                                    <div class="fr-card__start">
                                        <ul class="fr-badges-group">
                                            <li><span class="fr-badge fr-badge--warning fr-badge--sm">Maintenance</span></li>
                                        </ul>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>

                <nav role="navigation" class="fr-pagination fr-mt-6w" aria-label="Pagination">
                    <ul class="fr-pagination__list">
                        <li><a class="fr-pagination__link" href="/services?page=1" aria-current="page">1</a></li>
                        <li><a class="fr-pagination__link" href="/services?page=2">2</a></li>
                        <li><a class="fr-pagination__link" href="/services?page=3">3</a></li>
                        <li>
                            <a class="fr-pagination__link fr-pagination__link--next" href="/services?page=2">Page suivante</a>
                        </li>
                    </ul>
                </nav>
                {custom_content}
            </div>"""

    elif page_type == "detail":
        return f"""
            <div class="fr-py-8w">
                <nav role="navigation" class="fr-breadcrumb" aria-label="vous êtes ici :">
                    <button type="button" class="fr-breadcrumb__button" aria-expanded="false" aria-controls="breadcrumb-detail">Voir le fil d'Ariane</button>
                    <div class="fr-collapse" id="breadcrumb-detail">
                        <ol class="fr-breadcrumb__list">
                            <li><a class="fr-breadcrumb__link" href="/">Accueil</a></li>
                            <li><a class="fr-breadcrumb__link" href="/services">Services</a></li>
                            <li><a class="fr-breadcrumb__link" aria-current="page">Détail du service</a></li>
                        </ol>
                    </div>
                </nav>

                <div class="fr-grid-row fr-grid-row--gutters fr-mt-4w">
                    <div class="fr-col-12 fr-col-md-8">
                        <h1>{heading}</h1>
                        <ul class="fr-badges-group fr-mb-4w">
                            <li><span class="fr-badge fr-badge--info">Catégorie</span></li>
                            <li><span class="fr-badge fr-badge--success">Disponible</span></li>
                        </ul>

                        <p class="fr-text--lead">Description détaillée du service avec toutes les informations nécessaires pour l'usager.</p>

                        <h2>Conditions</h2>
                        <p>Détails des conditions d'éligibilité et des pièces à fournir.</p>

                        <h2>Démarche</h2>
                        <div class="fr-stepper">
                            <h3 class="fr-stepper__title">
                                <span class="fr-stepper__state">Étape 1 sur 3</span>
                                Préparer les documents
                            </h3>
                            <div class="fr-stepper__steps" data-fr-current-step="1" data-fr-steps="3"></div>
                            <p class="fr-stepper__details">
                                <span class="fr-text--bold">Étape suivante :</span> Remplir le formulaire
                            </p>
                        </div>

                        <h2>Textes de référence</h2>
                        <ul>
                            <li><a href="https://www.legifrance.gouv.fr/" class="fr-link" target="_blank" rel="noopener external" title="Article L.XXX du Code Y - nouvelle fenêtre">Article L.XXX du Code Y</a></li>
                            <li><a href="https://www.legifrance.gouv.fr/" class="fr-link" target="_blank" rel="noopener external" title="Décret n° 2025-XXX du XX/XX/2025 - nouvelle fenêtre">Décret n° 2025-XXX du XX/XX/2025</a></li>
                        </ul>
                    </div>
                    <div class="fr-col-12 fr-col-md-4">
                        <div class="fr-callout">
                            <h3 class="fr-callout__title">Informations pratiques</h3>
                            <p class="fr-callout__text">
                                <strong>Délai :</strong> 15 jours ouvrés<br>
                                <strong>Coût :</strong> Gratuit<br>
                                <strong>En ligne :</strong> Oui
                            </p>
                            <a class="fr-btn" href="/formulaire">Commencer la démarche</a>
                        </div>

                        <div class="fr-callout fr-callout--brown-cafe-creme fr-mt-4w">
                            <h3 class="fr-callout__title">Besoin d'aide ?</h3>
                            <p class="fr-callout__text">
                                Contactez-nous au 3939<br>
                                Du lundi au vendredi, 8h30-18h
                            </p>
                        </div>
                    </div>
                </div>
                {custom_content}
            </div>"""

    elif page_type == "sitemap":
        return f"""
            <div class="fr-grid-row fr-grid-row--center fr-py-8w">
                <div class="fr-col-12 fr-col-md-10 fr-col-lg-8">
                    <h1>{heading}</h1>
                    <p class="fr-text--lead">Retrouvez l'ensemble des rubriques et des pages du site.</p>

                    <div class="fr-grid-row fr-grid-row--gutters fr-mt-4w">
                        <div class="fr-col-12 fr-col-md-6">
                            <h2>Démarches et services</h2>
                            <ul>
                                <li><a href="/demarches/rendez-vous">Demande de rendez-vous</a></li>
                                <li><a href="/demarches/suivi">Suivi de dossier</a></li>
                                <li><a href="/demarches/formulaires">Formulaires administratifs</a></li>
                                <li><a href="/demarches/paiement">Paiement en ligne</a></li>
                            </ul>
                        </div>
                        <div class="fr-col-12 fr-col-md-6">
                            <h2>Informations pratiques</h2>
                            <ul>
                                <li><a href="/informations/contact">Contact et horaires</a></li>
                                <li><a href="/informations/faq">Questions fréquentes</a></li>
                                <li><a href="/informations/acces">Accès et plan d'accès</a></li>
                                <li><a href="/informations/urgence">Numéros d'urgence</a></li>
                            </ul>
                        </div>
                        <div class="fr-col-12 fr-col-md-6">
                            <h2>Le service</h2>
                            <ul>
                                <li><a href="/a-propos">À propos du service</a></li>
                                <li><a href="/actualites">Actualités</a></li>
                                <li><a href="/emploi">Recrutement</a></li>
                                <li><a href="/statistiques">Données et statistiques</a></li>
                            </ul>
                        </div>
                        <div class="fr-col-12 fr-col-md-6">
                            <h2>Aide et légale</h2>
                            <ul>
                                <li><a href="/aide">Centre d'aide</a></li>
                                <li><a href="/accessibilite">Accessibilité</a></li>
                                <li><a href="/mentions-legales">Mentions légales</a></li>
                                <li><a href="/donnees-personnelles">Données personnelles</a></li>
                            </ul>
                        </div>
                    </div>
                    {custom_content}
                </div>
            </div>"""

    else:  # Standard page
        return f"""
            <div class="fr-grid-row fr-grid-row--center fr-py-8w">
                <div class="fr-col-12 fr-col-md-10 fr-col-lg-8">
                    <h1>{heading}</h1>
                    <p class="fr-text--lead">Introduction ou résumé du contenu de la page.</p>

                    <h2>Section principale</h2>
                    <p>Contenu de la section principale avec tous les détails nécessaires.</p>

                    <h3>Sous-section</h3>
                    <p>Détails supplémentaires organisés en sous-sections pour une meilleure lisibilité.</p>

                    {custom_content if custom_content else '<p>Ajoutez votre contenu personnalisé ici.</p>'}
                </div>
            </div>"""


def main():
    parser = argparse.ArgumentParser(description="Générateur de pages DSFR")
    parser.add_argument("--title", default="Nom du service", help="Titre de la page")
    parser.add_argument("--type", default="standard",
                       choices=PAGE_TYPES,
                       help="Type de page à générer")
    parser.add_argument("--content", default="", help="Contenu HTML personnalisé à insérer")
    parser.add_argument("--no-header", action="store_true", help="Exclure l'en-tête")
    parser.add_argument("--no-footer", action="store_true", help="Exclure le pied de page")
    parser.add_argument("--dark", action="store_true", help="Activer le mode sombre")
    parser.add_argument("--brand-mode", default="neutral", choices=sorted(BRAND_MODES),
                       help="Mode marque : neutral par défaut, republique seulement si le droit d'usage est établi")
    parser.add_argument("--output", help="Fichier de sortie")
    parser.add_argument("--assets", help="Préfixe d'URL pour les assets DSFR (CSS, JS, favicons) au lieu du CDN jsdelivr (offline/souveraineté)")

    args = parser.parse_args()

    try:
        html = generate_html_page(
            title=args.title,
            page_type=args.type,
            content=args.content,
            include_header=not args.no_header,
            include_footer=not args.no_footer,
            dark_mode=args.dark,
            brand_mode=args.brand_mode,
            assets_prefix=args.assets
        )
    except ValueError as e:
        print(f"Erreur : {e}", file=sys.stderr)
        sys.exit(1)

    if args.output is not None:
        write_output(html, args.output, "Page générée")
    else:
        if hasattr(sys.stdout, "reconfigure"):
            sys.stdout.reconfigure(encoding="utf-8")
        print(html)


if __name__ == "__main__":
    main()
