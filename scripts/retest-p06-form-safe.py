#!/usr/bin/env python3
"""Retest sûr du formulaire P06, sans requête HTTP mutante.

Le script autorise uniquement GET, HEAD et OPTIONS. Toute requête POST, PUT,
PATCH ou DELETE est enregistrée puis bloquée avant envoi. Les données et fichiers
utilisés sont synthétiques. Les preuves sont écrites dans virginie-livrables.
"""

from __future__ import annotations

import atexit
import argparse
import fcntl
import hashlib
import json
import os
import platform
import re
import shutil
import tempfile
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from virginie_dsfr.project_paths import (  # noqa: E402
    KIT_ROOT,
    require_project_root,
    safe_pipeline_lock,
    safe_write_path,
)

ROOT = KIT_ROOT
PROJECT_ROOT = ROOT
DELIVERY = ROOT / "virginie-livrables"
OUTPUT = DELIVERY / "P06-FORMULAIRES/preuves"
STAGING_ROOT = ROOT / "visual-tests/_results/staging"
PIPELINE_LOCK = ROOT / "visual-tests/_results/.p06-pipeline.lock"
P06_URL = ""
PAGE_URLS: dict[str, str] = {}
PAGE_EXPECTATIONS = {
    "P01": {
        "title": "Accueil | Portail de la Direction Générale des Douanes et Droits Indirects",
        "h1": None,
    },
    "P02": {
        "title": "Plan du site Portail de la Direction Générale des Douanes et Droits Indirects | Portail de la Direction Générale des Douanes et Droits Indirects",
        "h1": "Plan du site Portail de la Direction Générale des Douanes et Droits Indirects",
    },
    "P03": {
        "title": "Déclaration d’accessibilité du portail Doune.gouv.fr | Portail de la Direction Générale des Douanes et Droits Indirects",
        "h1": "Déclaration d’accessibilité du portail Doune.gouv.fr",
    },
    "P04": {
        "title": "Mentions légales | Portail de la Direction Générale des Douanes et Droits Indirects",
        "h1": "Mentions légales",
    },
    "P05": {
        "title": "Données personnelles | Portail de la Direction Générale des Douanes et Droits Indirects",
        "h1": "Données personnelles",
    },
    "P06": {
        "title": "Ecrivez-nous | Portail de la Direction Générale des Douanes et Droits Indirects",
        "h1": "Écrivez-nous",
    },
    "P07": {
        "title": "Voyages à l'étranger | Portail de la Direction Générale des Douanes et Droits Indirects",
        "h1": "Voyages à l'étranger",
    },
    "P08": {
        "title": "Commerce international | Portail de la Direction Générale des Douanes et Droits Indirects",
        "h1": "Commerce international",
    },
    "P09": {
        "title": "Point d'actualité sur le déploiement de DELTA IE (import et export) au 5 février 2026 | Portail de la Direction Générale des Douanes et Droits Indirects",
        "h1": "Point d'actualité sur le déploiement de DELTA IE (import et export) au 5 février 2026",
    },
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--project-root",
        type=Path,
        default=None,
        help="projet de travail existant ; défaut : DSFR_PROJECT_ROOT",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=None,
        help="dossier de preuves ; défaut : <project-root>/virginie-livrables/P06-FORMULAIRES/preuves",
    )
    return parser.parse_args()


def configure_site_urls() -> None:
    """Construit les URLs depuis la configuration du projet consommateur."""
    global P06_URL, PAGE_URLS
    base_url = os.environ.get("DSFR_AUDIT_SITE_BASE_URL", "").rstrip("/")
    if not base_url:
        raise SystemExit(
            "Hôte audité absent : définir DSFR_AUDIT_SITE_BASE_URL dans le projet "
            "avant de lancer cette recette."
        )
    P06_URL = f"{base_url}/formulaire-infos-douane-service"
    PAGE_URLS = {
        "P01": f"{base_url}/",
        "P02": f"{base_url}/plan-du-site",
        "P03": f"{base_url}/pied-de-page/declaration-daccessibilite-du-portail-dounegouvfr",
        "P04": f"{base_url}/mentions-legales",
        "P05": f"{base_url}/pied-de-page/donnees-personnelles",
        "P06": P06_URL,
        "P07": f"{base_url}/particuliers/voyages-letranger",
        "P08": f"{base_url}/professionnels/commerce-international",
        "P09": f"{base_url}/actualites/point-dactualite-sur-le-deploiement-de-delta-ie-import-et-export-au-5-fevrier-2026",
    }


def configure_paths(args: argparse.Namespace) -> argparse.Namespace:
    """Place les preuves, le staging et le verrou sous le projet."""
    project_root = require_project_root(args.project_root)
    delivery = safe_write_path(
        project_root / "virginie-livrables",
        project_root=project_root,
        label="livrables P06",
    )
    output = safe_write_path(
        args.output or delivery / "P06-FORMULAIRES/preuves",
        project_root=project_root,
        label="preuves P06",
    )
    staging_root = safe_write_path(
        project_root / "visual-tests/_results/staging",
        project_root=project_root,
        label="staging P06",
    )
    global PROJECT_ROOT, DELIVERY, OUTPUT, STAGING_ROOT, PIPELINE_LOCK
    PROJECT_ROOT = project_root
    DELIVERY = delivery
    OUTPUT = output
    STAGING_ROOT = staging_root
    PIPELINE_LOCK = safe_pipeline_lock(project_root)
    configure_site_urls()
    args.project_root = project_root
    return args


def load_playwright() -> None:
    """Importe Playwright après le contrôle de frontière du projet."""
    global Browser, BrowserContext, Page, TimeoutError, sync_playwright
    try:
        from playwright.sync_api import (
            Browser,
            BrowserContext,
            Page,
            TimeoutError,
            sync_playwright,
        )
    except ImportError as exc:
        raise SystemExit(
            "Playwright est absent de l’environnement Python sélectionné"
        ) from exc


EXPECTED_REPEATED_CONTROLS = {
    "input|search|query": {"accessible_name": "Rechercher", "label_text": "Rechercher"},
    "input|radio|fr-radios-theme-light": {
        "accessible_name": "Thème clair",
        "label_text": "Thème clair",
    },
    "input|radio|fr-radios-theme-dark": {
        "accessible_name": "Thème sombre",
        "label_text": "Thème sombre",
    },
    "input|radio|fr-radios-theme-system": {
        "accessible_name": "Système Utilise les paramètres système",
        "label_text": "Système Utilise les paramètres système",
    },
}
SAFE_METHODS = {"GET", "HEAD", "OPTIONS"}
OPTIONAL_MENTION = re.compile(r"\b(?:optionnel(?:le)?s?|facultati(?:f|ve)s?)\b", re.IGNORECASE)
SYNTHETIC_PNG = bytes.fromhex(
    "89504e470d0a1a0a0000000d49484452000000010000000108060000001f15c489"
    "0000000d4944415408d763f8cfc0f01f00050001ff89993d1d0000000049454e44ae426082"
)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


@contextmanager
def p06_pipeline_lock():
    PIPELINE_LOCK.parent.mkdir(parents=True, exist_ok=True)
    with PIPELINE_LOCK.open("a+", encoding="utf-8") as handle:
        fcntl.flock(handle.fileno(), fcntl.LOCK_EX)
        try:
            yield
        finally:
            fcntl.flock(handle.fileno(), fcntl.LOCK_UN)


def install_network_guard(
    context: BrowserContext,
    blocked: list[dict[str, str]],
    blocked_websockets: list[dict[str, str]],
) -> None:
    def guard(route: Any) -> None:
        request = route.request
        method = request.method.upper()
        if method not in SAFE_METHODS:
            route.abort("blockedbyclient")
            blocked.append(
                {
                    "method": method,
                    "url": request.url,
                    "resource_type": request.resource_type,
                    "decision": "ABORTED_BEFORE_SEND",
                }
            )
            return
        route.continue_()

    context.route("**/*", guard)

    def block_websocket(route: Any) -> None:
        route.close(code=1008, reason="Safe audit blocks WebSocket traffic")
        blocked_websockets.append(
            {"url": route.url, "decision": "CLOSED_BEFORE_APPLICATION_MESSAGES"}
        )

    context.route_web_socket("**/*", block_websocket)


def visible_texts(page: Page) -> list[dict[str, Any]]:
    return page.evaluate(
        """() => {
          const selectors = [
            '[role="alert"]', '.fr-alert--error', '.fr-message--error', '.fr-error-text',
            '[aria-live="assertive"]', '[aria-live="polite"]', '[id$="--error"]'
          ];
          const seen = new Set();
          return [...document.querySelectorAll(selectors.join(','))]
            .filter((element) => {
              if (seen.has(element)) return false;
              seen.add(element);
              let visible = !element.closest('[aria-hidden="true"], [inert]')
                && element.getClientRects().length > 0;
              for (let current = element; visible && current; current = current.parentElement) {
                const style = getComputedStyle(current);
                const rect = current.getBoundingClientRect();
                const clipped = style.clipPath === 'inset(50%)'
                  || /rect\\(0(?:px)?[, ]+0(?:px)?[, ]+0(?:px)?[, ]+0(?:px)?\\)/.test(style.clip || '');
                const onePixelClip = ['absolute', 'fixed'].includes(style.position)
                  && rect.width <= 1 && rect.height <= 1 && style.overflow === 'hidden';
                if (style.display === 'none' || ['hidden', 'collapse'].includes(style.visibility)
                    || style.opacity === '0' || clipped || onePixelClip || current.hidden) visible = false;
              }
              return visible && (element.textContent || '').trim();
            })
            .map((element) => ({
              tag: element.tagName.toLowerCase(),
              id: element.id || null,
              role: element.getAttribute('role'),
              aria_live: element.getAttribute('aria-live'),
              aria_atomic: element.getAttribute('aria-atomic'),
              text: element.textContent.trim().replace(/\\s+/g, ' '),
              source_kind: element.matches('[role="alert"], [aria-live]') ? 'live-region' : 'field-error-text',
              visually_rendered: true,
              html: element.outerHTML
            }));
        }"""
    )


def added_messages(
    before: list[dict[str, Any]], after: list[dict[str, Any]]
) -> list[dict[str, Any]]:
    before_keys = {(item.get("id"), item.get("text"), item.get("html")) for item in before}
    return [
        item
        for item in after
        if (item.get("id"), item.get("text"), item.get("html")) not in before_keys
    ]


def active_element_state(page: Page) -> dict[str, Any]:
    return page.evaluate(
        """() => {
          const element = document.activeElement;
          return element ? {
            tag: element.tagName.toLowerCase(),
            id: element.id || null,
            name: element.getAttribute('name'),
            type: element.getAttribute('type'),
            role: element.getAttribute('role')
          } : {tag: null, id: null, name: null, type: null, role: null};
        }"""
    )


def field_state(page: Page, selector: str) -> dict[str, Any]:
    return page.locator(selector).evaluate(
        """(element) => ({
          id: element.id,
          type: element.type,
          value: element.value,
          required: element.required,
          aria_required: element.getAttribute('aria-required'),
          disabled: element.disabled,
          visible: (() => {
            for (let current = element; current; current = current.parentElement) {
              const style = getComputedStyle(current);
              const rect = current.getBoundingClientRect();
              const clipped = style.clipPath === 'inset(50%)'
                || /rect\\(0(?:px)?[, ]+0(?:px)?[, ]+0(?:px)?[, ]+0(?:px)?\\)/.test(style.clip || '');
              const onePixelClip = ['absolute', 'fixed'].includes(style.position)
                && rect.width <= 1 && rect.height <= 1 && style.overflow === 'hidden';
              if (style.display === 'none' || ['hidden', 'collapse'].includes(style.visibility)
                  || style.opacity === '0' || clipped || onePixelClip || current.hidden) return false;
            }
            return !!(element.offsetWidth || element.offsetHeight || element.getClientRects().length);
          })(),
          valid: element.validity ? element.validity.valid : null,
          validation_message: element.validationMessage || '',
          aria_invalid: element.getAttribute('aria-invalid'),
          aria_describedby: element.getAttribute('aria-describedby'),
          aria_errormessage: element.getAttribute('aria-errormessage'),
          error_message_targets: (element.getAttribute('aria-errormessage') || '')
            .split(/\\s+/).filter(Boolean).map((id) => {
              const target = document.getElementById(id);
              if (!target) return {id, exists: false, text: '', visible: false};
              const style = getComputedStyle(target);
              const visible = style.display !== 'none' && !['hidden', 'collapse'].includes(style.visibility)
                && style.opacity !== '0' && !!(target.offsetWidth || target.offsetHeight || target.getClientRects().length);
              return {id, exists: true, text: target.textContent.trim(), visible};
            }),
          description_targets: (element.getAttribute('aria-describedby') || '')
            .split(/\\s+/).filter(Boolean).map((id) => {
              const target = document.getElementById(id);
              if (!target) return {id, exists: false, text: '', visible: false};
              const style = getComputedStyle(target);
              const visible = style.display !== 'none' && !['hidden', 'collapse'].includes(style.visibility)
                && style.opacity !== '0' && !!(target.offsetWidth || target.offsetHeight || target.getClientRects().length);
              return {id, exists: true, text: target.textContent.trim(), visible};
            }),
          autocomplete: element.getAttribute('autocomplete'),
          accept: element.getAttribute('accept'),
          multiple: !!element.multiple,
          files: element.files ? [...element.files].map((file) => ({
            name: file.name, type: file.type, size: file.size
          })) : [],
          labels: element.labels ? [...element.labels].map((label) => label.textContent.trim()) : [],
          label_states: element.labels ? [...element.labels].map((label) => {
            const style = getComputedStyle(label);
            const visible = style.display !== 'none' && !['hidden', 'collapse'].includes(style.visibility)
              && style.opacity !== '0' && !!(label.offsetWidth || label.offsetHeight || label.getClientRects().length);
            const fieldRect = element.getBoundingClientRect();
            const labelRect = label.getBoundingClientRect();
            return {
              text: label.textContent.trim(),
              visible,
              for: label.htmlFor || null,
              distance_px: visible ? Math.round(Math.hypot(labelRect.left - fieldRect.left, labelRect.bottom - fieldRect.top)) : null
            };
          }) : []
        })"""
    )


def close_cookie_banner(page: Page) -> str:
    button = page.locator("button.decline-button").first
    try:
        button.wait_for(state="visible", timeout=1_500)
    except TimeoutError:
        return "NOT_PRESENT"
    try:
        button.click(timeout=5_000)
        button.wait_for(state="hidden", timeout=5_000)
    except TimeoutError as error:
        raise RuntimeError("DISMISSAL_FAILED: le bandeau cookies est resté bloquant") from error
    return "DECLINE_CONFIRMED"


def load(page: Page, url: str) -> dict[str, Any]:
    response = page.goto(url, wait_until="domcontentloaded", timeout=60_000)
    page.wait_for_load_state("load", timeout=60_000)
    status = response.status if response else None
    final_url = page.url
    title = page.title().strip()
    if status != 200:
        raise RuntimeError(f"Navigation HTTP inattendue pour {url} : {status}")
    if final_url.rstrip("/") != url.rstrip("/"):
        raise RuntimeError(f"Redirection inattendue pour {url} : {final_url}")
    if not title:
        raise RuntimeError(f"Titre de page vide pour {url}")
    cookie_action = close_cookie_banner(page)
    if url == P06_URL:
        page.locator("#ids-eloquant-form").wait_for(state="visible", timeout=10_000)
    return {
        "url": final_url,
        "status": status,
        "title": title,
        "cookie_action": cookie_action,
    }


def screenshot_form(page: Page, name: str, staging: Path, run_id: str) -> dict[str, Any]:
    path = staging / name
    form = page.locator("#ids-eloquant-form")
    form.screenshot(path=str(path), timeout=30_000)
    return {
        "file": f"preuves/runs/{run_id}/{name}",
        "sha256": sha256(path),
        "bytes": path.stat().st_size,
    }


def fill_required_fields(page: Page, email: str) -> None:
    page.locator("#edit-nom").fill("Test")
    page.locator("#edit-prenom").fill("Accessibilite")
    page.locator("#edit-pays").fill("France")
    page.locator("#edit-codepostal").fill("75000")
    page.locator("#edit-adressemail").fill(email)
    page.locator("#edit-question").fill("Test synthetique d'accessibilite sans envoi.")
    checkbox = page.locator("#edit-accept-conditions")
    if not checkbox.is_checked():
        checkbox.check(force=True)


def scenario_empty_submit(
    page: Page, blocked: list[dict[str, str]], staging: Path, run_id: str
) -> dict[str, Any]:
    navigation = load(page, P06_URL)
    before = len(blocked)
    messages_before = visible_texts(page)
    page.locator("#edit-submit").click()
    page.wait_for_function("document.activeElement?.id === 'edit-nom'", timeout=5_000)
    messages_after = visible_texts(page)
    result = {
        "navigation": navigation,
        "active_element": active_element_state(page),
        "first_required_field": field_state(page, "#edit-nom"),
        "messages_before": messages_before,
        "visible_messages": added_messages(messages_before, messages_after),
        "blocked_mutating_requests": blocked[before:],
    }
    result["screenshot"] = screenshot_form(
        page, "P06-01-soumission-vide-native.png", staging, run_id
    )
    return result


def scenario_invalid_email(
    page: Page, blocked: list[dict[str, str]], staging: Path, run_id: str
) -> dict[str, Any]:
    navigation = load(page, P06_URL)
    fill_required_fields(page, "adresse-invalide")
    before = len(blocked)
    messages_before = visible_texts(page)
    page.locator("#edit-submit").click()
    page.wait_for_function("document.activeElement?.id === 'edit-adressemail'", timeout=5_000)
    messages_after = visible_texts(page)
    result = {
        "navigation": navigation,
        "active_element": active_element_state(page),
        "email": field_state(page, "#edit-adressemail"),
        "messages_before": messages_before,
        "visible_messages": added_messages(messages_before, messages_after),
        "blocked_mutating_requests": blocked[before:],
    }
    result["screenshot"] = screenshot_form(
        page, "P06-02-email-invalide-natif.png", staging, run_id
    )
    return result


def scenario_professional(
    page: Page, blocked: list[dict[str, str]], staging: Path, run_id: str
) -> dict[str, Any]:
    navigation = load(page, P06_URL)
    before = len(blocked)
    page.locator("#edit-candidate-gender").select_option("Professionnel")
    page.locator("#edit-societe").wait_for(state="visible", timeout=5_000)
    company = field_state(page, "#edit-societe")
    company_context = page.locator("#edit-societe").evaluate(
        """(element) => {
          const container = element.closest('.fr-input-group, .fr-fieldset__element, .js-form-item, .form-item') || element.parentElement;
          const legends = container ? [...container.querySelectorAll('legend')]
            .map((legend) => legend.innerText.trim()).filter(Boolean) : [];
          const labelledby = (element.getAttribute('aria-labelledby') || '').split(/\\s+/)
            .filter(Boolean).map((id) => document.getElementById(id)?.innerText.trim() || '').filter(Boolean);
          return {
            container_tag: container?.tagName.toLowerCase() || null,
            container_text: container?.innerText.trim() || '',
            legends,
            labelledby_texts: labelledby
          };
        }"""
    )
    global_instruction = page.locator("#ids-eloquant-form p").filter(
        has_text="Sauf mention contraire"
    ).first.inner_text()
    associated_visible_texts = [
        item["text"]
        for item in [*company["label_states"], *company["description_targets"]]
        if item.get("visible") and item.get("text")
    ] + [
        text
        for text in [
            company_context["container_text"],
            *company_context["legends"],
            *company_context["labelledby_texts"],
        ]
        if text
    ]
    result = {
        "navigation": navigation,
        "company": company,
        "company_context": company_context,
        "global_instruction": global_instruction.strip(),
        "associated_visible_texts": associated_visible_texts,
        "optional_mentioned": any(
            OPTIONAL_MENTION.search(text) for text in associated_visible_texts
        ),
        "blocked_mutating_requests": blocked[before:],
    }
    result["screenshot"] = screenshot_form(
        page, "P06-03-variante-professionnel.png", staging, run_id
    )
    return result


def scenario_file(
    page: Page,
    blocked: list[dict[str, str]],
    many: bool,
    staging: Path,
    run_id: str,
) -> dict[str, Any]:
    navigation = load(page, P06_URL)
    selector = page.locator("#edit-document-upload")
    before = len(blocked)
    messages_before = visible_texts(page)
    triggering_request: dict[str, str] | None = None
    if many:
        files = [
            {
                "name": f"preuve-synthetique-{index}.png",
                "mimeType": "image/png",
                "buffer": SYNTHETIC_PNG,
            }
            for index in range(1, 6)
        ]
        screenshot_name = "P06-05-cinq-fichiers-requete-bloquee.png"
        with page.expect_event(
            "requestfailed",
            predicate=lambda request: (
                request.method.upper() == "POST"
                and request.resource_type in {"xhr", "fetch"}
                and request.url.startswith(P06_URL)
                and "ajax_form=1" in request.url
                and "element_parents=fieldset/Document" in request.url
            ),
            timeout=10_000,
        ) as failed_info:
            selector.set_input_files(files)
        failed_request = failed_info.value
        post_data = failed_request.post_data_buffer or b""
        expected_file_names = [file["name"] for file in files]
        file_names_in_post_data = {
            name: name.encode("utf-8") in post_data for name in expected_file_names
        }
        if not post_data or not all(file_names_in_post_data.values()):
            raise RuntimeError(
                "Le POST intercepté ne contient pas les cinq noms de fichiers synthétiques attendus."
            )
        triggering_request = {
            "method": failed_request.method,
            "url": failed_request.url,
            "resource_type": failed_request.resource_type,
            "post_data_bytes": len(post_data),
            "post_data_sha256": hashlib.sha256(post_data).hexdigest(),
            "synthetic_file_names_in_post_data": file_names_in_post_data,
            "failure": failed_request.failure or "blocked",
        }
    else:
        files = {
            "name": "preuve-synthetique-interdite.exe",
            "mimeType": "application/octet-stream",
            "buffer": b"synthetic accessibility test - not executable",
        }
        screenshot_name = "P06-04-extension-interdite-validation-client-sans-requete.png"
        selector.set_input_files(files)
        page.locator('[aria-live], [role="alert"], .fr-error-text').filter(
            has_text="preuve-synthetique-interdite.exe"
        ).first.wait_for(state="visible", timeout=5_000)
    messages_after = visible_texts(page)
    blocked_requests = blocked[before:]
    if many:
        matching_guard_entries = [
            request
            for request in blocked_requests
            if request["method"] == triggering_request["method"]
            and request["url"] == triggering_request["url"]
            and request["resource_type"] == triggering_request["resource_type"]
        ]
        if len(matching_guard_entries) != 1:
            raise RuntimeError(
                "La requête cinq fichiers ne correspond pas exactement à une entrée de la garde."
            )
    elif blocked_requests:
        raise RuntimeError("L’extension interdite a déclenché une méthode HTTP non sûre inattendue.")
    result = {
        "navigation": navigation,
        "input": field_state(page, "#edit-document-upload"),
        "messages_before": messages_before,
        "visible_messages": added_messages(messages_before, messages_after),
        "active_element": active_element_state(page),
        "blocked_mutating_requests": blocked_requests,
        "triggering_request": triggering_request,
        "guard_correlation_exact": many and len(matching_guard_entries) == 1,
        "server_result_available": False,
        "limit": "Toute méthode HTTP non sûre est bloquée avant envoi ; une validation exclusivement serveur ne peut pas être observée.",
    }
    result["screenshot"] = screenshot_form(page, screenshot_name, staging, run_id)
    return result


def control_inventory(page: Page) -> list[dict[str, Any]]:
    return page.evaluate(
        """() => [...document.querySelectorAll(
            'input, select, textarea, output, progress, meter, datalist, optgroup, option, '
            + '[role="meter"], [role="progressbar"], [role="slider"], [role="spinbutton"], '
            + '[role="textbox"], [role="listbox"], [role="searchbox"], [role="combobox"], '
            + '[role="option"], [role="checkbox"], [role="radio"], [role="switch"]'
          )]
          .filter((element) => !['hidden', 'submit', 'button', 'image', 'reset'].includes((element.type || '').toLowerCase()))
          .map((element) => {
            const normalize = (value) => (value || '').replace(/\\s+/g, ' ').trim();
            const isVisuallyHidden = (node) => {
              for (let current = node; current && current.nodeType === Node.ELEMENT_NODE; current = current.parentElement) {
                const style = getComputedStyle(current);
                const rect = current.getBoundingClientRect();
                const clipped = style.clipPath === 'inset(50%)'
                  || /rect\\(0(?:px)?[, ]+0(?:px)?[, ]+0(?:px)?[, ]+0(?:px)?\\)/.test(style.clip || '');
                const onePixelClip = ['absolute', 'fixed'].includes(style.position)
                  && rect.width <= 1 && rect.height <= 1 && style.overflow === 'hidden';
                if (style.display === 'none' || ['hidden', 'collapse'].includes(style.visibility)
                    || style.opacity === '0' || clipped || onePixelClip || current.hidden) return true;
              }
              return false;
            };
            const visibleText = (root) => {
              const walker = document.createTreeWalker(root, NodeFilter.SHOW_TEXT);
              const parts = [];
              for (let node = walker.nextNode(); node; node = walker.nextNode()) {
                if (!isVisuallyHidden(node.parentElement)) parts.push(node.nodeValue || '');
              }
              return normalize(parts.join(' '));
            };
            const referencedIds = (attribute) => (element.getAttribute(attribute) || '').split(/\\s+/).filter(Boolean);
            const idsText = (attribute) => referencedIds(attribute)
              .filter(Boolean).map((id) => normalize(document.getElementById(id)?.textContent)).filter(Boolean).join(' ');
            const labelledbyIds = referencedIds('aria-labelledby');
            const missingLabelledbyIds = labelledbyIds.filter((id) => !document.getElementById(id));
            const labelledby = idsText('aria-labelledby');
            const visibleLabelledby = labelledbyIds
              .map((id) => document.getElementById(id)).filter(Boolean).map(visibleText).filter(Boolean).join(' ');
            const describedby = idsText('aria-describedby');
            const visibleDescribedby = referencedIds('aria-describedby')
              .map((id) => document.getElementById(id)).filter(Boolean).map(visibleText).filter(Boolean).join(' ');
            const ariaLabel = normalize(element.getAttribute('aria-label'));
            const labels = element.labels ? [...element.labels].map((label) => normalize(label.textContent)).filter(Boolean) : [];
            const visibleLabelTexts = element.labels ? [...element.labels].map(visibleText).filter(Boolean) : [];
            const tag = element.tagName.toLowerCase();
            const explicitRole = element.getAttribute('role');
            const nameFromContent = tag === 'option'
              ? normalize(element.getAttribute('label') || element.textContent)
              : tag === 'optgroup' ? normalize(element.getAttribute('label'))
              : ['option', 'checkbox', 'radio', 'switch'].includes(explicitRole) ? normalize(element.textContent)
              : '';
            const htmlLabel = labels.join(' ').trim() || nameFromContent;
            const title = normalize(element.getAttribute('title'));
            const accessibleNameCandidate = labelledby || ariaLabel || htmlLabel || title;
            const visuallyRendered = !isVisuallyHidden(element)
              && !!(element.offsetWidth || element.offsetHeight || element.getClientRects().length);
            const hiddenFromAT = !!element.closest('[aria-hidden="true"], [inert]');
            return {
              form_id: element.form?.id || null,
              tag,
              type: explicitRole || element.type || tag,
              native_type: element.type || null,
              explicit_role: explicitRole,
              id: element.id || null,
              name: element.name || null,
              required: element.required === true,
              aria_required: element.getAttribute('aria-required'),
              aria_labelledby: element.getAttribute('aria-labelledby'),
              aria_label: element.getAttribute('aria-label'),
              aria_describedby: element.getAttribute('aria-describedby'),
              aria_errormessage: element.getAttribute('aria-errormessage'),
              aria_invalid: element.getAttribute('aria-invalid'),
              autocomplete: element.getAttribute('autocomplete'),
              list_id: element.getAttribute('list'),
              parent_select_id: element.closest('select')?.id || null,
              parent_select_name: element.closest('select')?.name || null,
              option_index: tag === 'option' ? element.index : null,
              value: element.value ?? element.getAttribute('value'),
              min: element.min ?? element.getAttribute('min'),
              max: element.max ?? element.getAttribute('max'),
              aria_valuemin: element.getAttribute('aria-valuemin'),
              aria_valuenow: element.getAttribute('aria-valuenow'),
              aria_valuemax: element.getAttribute('aria-valuemax'),
              labels,
              visible_label_texts: visibleLabelTexts,
              labelledby_text: labelledby,
              visible_labelledby_text: visibleLabelledby,
              missing_labelledby_ids: missingLabelledbyIds,
              describedby_text: describedby,
              visible_describedby_text: visibleDescribedby,
              name_from_content: nameFromContent,
              title,
              accessible_name_candidate: normalize(accessibleNameCandidate),
              accessible_name_method: labelledby ? 'aria-labelledby' : ariaLabel ? 'aria-label' : htmlLabel ? 'html' : title ? 'title' : null,
              visually_rendered: visuallyRendered,
              exposed_to_at_candidate: visuallyRendered && !hiddenFromAT,
              visible: visuallyRendered
            };
          })"""
    )


def multipage_labels(page: Page) -> dict[str, Any]:
    pages: list[dict[str, Any]] = []
    for page_id, url in PAGE_URLS.items():
        try:
            navigation = load(page, url)
            main_region = page.locator("main").first
            main_region.wait_for(state="attached", timeout=10_000)
            h1_texts = [
                text.strip() for text in main_region.locator("h1").all_inner_texts() if text.strip()
            ]
            expectation = PAGE_EXPECTATIONS[page_id]
            title_matches = navigation["title"] == expectation["title"]
            h1_matches = (
                h1_texts == []
                if expectation["h1"] is None
                else h1_texts.count(expectation["h1"]) == 1
            )
            pages.append(
                {
                    "page": page_id,
                    "navigation": navigation,
                    "expected_title": expectation["title"],
                    "title_matches": title_matches,
                    "expected_main_h1": expectation["h1"],
                    "h1_texts": h1_texts,
                    "main_h1_matches": h1_matches,
                    "controls": control_inventory(page),
                }
            )
        except Exception as error:  # La preuve doit conserver un échec de page sans masquer les autres.
            pages.append({"page": page_id, "url": url, "error": repr(error), "controls": []})

    repeated: dict[str, list[dict[str, Any]]] = {}
    for page_result in pages:
        for control in page_result["controls"]:
            identity = (
                control["id"]
                if control["type"] in {"radio", "checkbox"} and control["id"]
                else control["name"] or control["id"]
            )
            if not identity:
                continue
            key = f"{control['tag']}|{control['type']}|{identity}"
            repeated.setdefault(key, []).append(
                {
                    "page": page_result["page"],
                    "id": control["id"],
                    "name": control["name"],
                    "visible": control["visible"],
                    "label_text": " ".join(control.get("labels", [])).strip(),
                    "visible_label_text": " ".join(
                        control.get("visible_label_texts", [])
                    ).strip(),
                    "accessible_name_candidate": control["accessible_name_candidate"],
                }
            )
    expected_pages = set(PAGE_URLS)
    comparisons = []
    for key, expected_texts in EXPECTED_REPEATED_CONTROLS.items():
        values = repeated.get(key, [])
        pages_seen = [value["page"] for value in values]
        names = sorted({value["accessible_name_candidate"] for value in values})
        label_texts = sorted({value["label_text"] for value in values})
        visible_label_texts = sorted({value["visible_label_text"] for value in values})
        occurrences_per_page = {
            page_id: pages_seen.count(page_id) for page_id in sorted(expected_pages)
        }
        complete = set(pages_seen) == expected_pages and all(
            count == 1 for count in occurrences_per_page.values()
        )
        comparisons.append(
            {
                "identity": key,
                "expected_accessible_name": expected_texts["accessible_name"],
                "expected_label_text": expected_texts["label_text"],
                "pages": sorted(set(pages_seen)),
                "missing_pages": sorted(expected_pages - set(pages_seen)),
                "occurrences_per_page": occurrences_per_page,
                "accessible_names": names,
                "label_texts": label_texts,
                "visible_label_texts": visible_label_texts,
                "visible_label_observed_on_all_pages": complete
                and all(
                    value["visible"]
                    and value["visible_label_text"] == expected_texts["label_text"]
                    for value in values
                ),
                "complete": complete,
                "coherent": complete
                and names == [expected_texts["accessible_name"]]
                and label_texts == [expected_texts["label_text"]],
                "occurrences": values,
            }
        )
    page_failures = []
    for page_result in pages:
        page_id = page_result["page"]
        navigation = page_result.get("navigation", {})
        final_url = navigation.get("url")
        expected_url = PAGE_URLS[page_id]
        url_matches = bool(final_url) and final_url.rstrip("/") == expected_url.rstrip("/")
        if (
            page_result.get("error")
            or navigation.get("status") != 200
            or not url_matches
            or not navigation.get("title")
            or page_result.get("title_matches") is not True
            or page_result.get("main_h1_matches") is not True
        ):
            page_failures.append(
                {
                    "page": page_id,
                    "error": page_result.get("error"),
                    "status": navigation.get("status"),
                    "expected_url": expected_url,
                    "final_url": final_url,
                    "url_matches": url_matches,
                    "title": navigation.get("title"),
                    "expected_title": page_result.get("expected_title"),
                    "title_matches": page_result.get("title_matches"),
                    "expected_main_h1": page_result.get("expected_main_h1"),
                    "main_h1_matches": page_result.get("main_h1_matches"),
                    "h1_texts": page_result.get("h1_texts", []),
                }
            )
    pages_complete = len(pages) == len(PAGE_URLS) and not page_failures
    all_expected_coherent = pages_complete and all(
        comparison["coherent"] for comparison in comparisons
    )
    unmatched_controls = [
        {"page": page_result["page"], **control}
        for page_result in pages
        for control in page_result["controls"]
        if not (control.get("name") or control.get("id"))
    ]
    detected_other_repeated_groups = sorted(
        key
        for key, values in repeated.items()
        if key not in EXPECTED_REPEATED_CONTROLS
        and len({value["page"] for value in values}) > 1
    )
    return {
        "pages": pages,
        "pages_complete": pages_complete,
        "page_failures": page_failures,
        "expected_semantic_controls": EXPECTED_REPEATED_CONTROLS,
        "repeated_control_comparisons": comparisons,
        "all_expected_repeated_dom_candidates_complete_and_coherent": all_expected_coherent,
        "unmatched_controls": unmatched_controls,
        "detected_other_repeated_identity_groups": detected_other_repeated_groups,
        "method_limit": "Cartographie explicite de quatre contrôles attendus sur P01–P09 ; la qualification de fonction identique reste humaine.",
    }


def invalidate_package_validation() -> None:
    tickets_root = DELIVERY / "TICKETS-RGAA"
    tickets_root.mkdir(parents=True, exist_ok=True)
    checksum = tickets_root / "SHA256SUMS"
    validation_path = tickets_root / "VALIDATION-TICKETS-RGAA.json"
    validation: dict[str, Any] = {}
    if validation_path.is_file():
        validation = json.loads(validation_path.read_text(encoding="utf-8"))
    validation["valid"] = False
    validation["client_transmission_ready"] = False
    validation["generation_state"] = "STALE_AFTER_P06_RETEST"
    validation["checksum_verification"] = "STALE"
    warning = (
        "Un retest P06 est en cours ou a été republié ; régénérer l’annexe puis le paquet avant contrôle d’intégrité."
    )
    warnings = validation.setdefault("warnings", [])
    if warning not in warnings:
        warnings.append(warning)
    temporary = validation_path.with_suffix(".json.tmp")
    temporary.write_text(
        json.dumps(validation, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    os.replace(temporary, validation_path)
    checksum.unlink(missing_ok=True)


def new_page(context: BrowserContext, errors: list[dict[str, str]], scenario: str) -> Page:
    page = context.new_page()

    def record_page_error(error: Any) -> None:
        message = str(error)
        errors.append(
            {
                "scenario": scenario,
                "url": page.url,
                "message": message,
                "error_family": (
                    "drupal-ajax"
                    if "Drupal.AjaxError" in message or "AJAX HTTP error" in message
                    else "page-script"
                ),
            }
        )

    page.on("pageerror", record_page_error)
    return page


def _run_locked() -> int:
    OUTPUT.mkdir(parents=True, exist_ok=True)
    STAGING_ROOT.mkdir(parents=True, exist_ok=True)
    started_at = datetime.now(timezone.utc)
    collector_path = Path(__file__).resolve()
    collector_sha256 = sha256(collector_path)
    run_id = started_at.strftime("%Y%m%dT%H%M%S%fZ") + f"-{collector_sha256[:8]}"
    staging = Path(tempfile.mkdtemp(prefix=f"p06-{run_id}-", dir=STAGING_ROOT))
    atexit.register(lambda: shutil.rmtree(staging, ignore_errors=True))
    blocked: list[dict[str, str]] = []
    blocked_websockets: list[dict[str, str]] = []
    completed_mutating_requests: list[dict[str, str]] = []
    page_errors: list[dict[str, str]] = []
    result: dict[str, Any] = {
        "schema_version": 2,
        "run_id": run_id,
        "collector": {
            "file": str(collector_path.relative_to(ROOT)),
            "sha256": collector_sha256,
        },
        "started_at": started_at.isoformat(),
        "scope": "P06 et cohérence des étiquettes sur P01 à P09",
        "mode": "SAFE_NO_MUTATING_REQUEST",
        "safety_contract": {
            "allowed_http_methods": sorted(SAFE_METHODS),
            "blocked_http_policy": "Toute méthode autre que GET, HEAD ou OPTIONS est interrompue avant envoi.",
            "websocket_policy": "Toute connexion WebSocket est fermée avant les messages applicatifs.",
            "synthetic_data_only": True,
            "valid_final_submission": False,
            "server_mutation_authorized": False,
        },
        "environment": {"python": platform.python_version(), "platform": platform.platform()},
    }

    with sync_playwright() as playwright:
        browser: Browser = playwright.chromium.launch(headless=True)
        context = browser.new_context(
            locale="fr-FR",
            service_workers="block",
            viewport={"width": 1440, "height": 1000},
            reduced_motion="reduce",
        )
        install_network_guard(context, blocked, blocked_websockets)

        def record_finished_request(request: Any) -> None:
            method = request.method.upper()
            if method not in SAFE_METHODS:
                completed_mutating_requests.append(
                    {"method": method, "url": request.url, "resource_type": request.resource_type}
                )

        context.on("requestfinished", record_finished_request)
        result["environment"]["browser"] = browser.browser_type.name
        result["environment"]["browser_version"] = browser.version

        scenarios: dict[str, Any] = {}
        for name, runner in (
            ("empty_native_submit", scenario_empty_submit),
            ("invalid_email_native", scenario_invalid_email),
            ("professional_variant", scenario_professional),
        ):
            page = new_page(context, page_errors, name)
            try:
                scenarios[name] = runner(page, blocked, staging, run_id)
            finally:
                page.close()

        for name, many in (("invalid_file_extension", False), ("five_allowed_files", True)):
            page = new_page(context, page_errors, name)
            try:
                scenarios[name] = scenario_file(page, blocked, many, staging, run_id)
            finally:
                page.close()

        page = new_page(context, page_errors, "multipage_labels")
        try:
            multipage = multipage_labels(page)
        finally:
            page.close()

        context.close()
        browser.close()

    if completed_mutating_requests:
        raise RuntimeError(
            "Échec de la garde réseau : requête(s) mutante(s) terminée(s) : "
            + json.dumps(completed_mutating_requests, ensure_ascii=False)
        )
    result["scenarios"] = scenarios
    result["multipage_labels"] = multipage
    result["network_guard"] = {
        "guard_scope": "BrowserContext",
        "blocked_requests": blocked,
        "blocked_count": len(blocked),
        "blocked_websockets": blocked_websockets,
        "blocked_websocket_count": len(blocked_websockets),
        "completed_mutating_requests": completed_mutating_requests,
        "mutating_request_completed": bool(completed_mutating_requests),
        "websocket_application_message_completed": False,
    }
    five_file_trigger = scenarios["five_allowed_files"].get("triggering_request") or {}
    five_file_guard_entries = scenarios["five_allowed_files"].get(
        "blocked_mutating_requests", []
    )
    for error in page_errors:
        same_guard_window = (
            error.get("scenario") == "five_allowed_files"
            and error.get("error_family") == "drupal-ajax"
            and error.get("url", "").rstrip("/") == P06_URL.rstrip("/")
            and five_file_trigger.get("url")
            and (
                error.get("message") == "Drupal.AjaxError"
                or five_file_trigger["url"] in error.get("message", "")
            )
            and len(five_file_guard_entries) == 1
            and five_file_guard_entries[0].get("url") == five_file_trigger.get("url")
            and five_file_guard_entries[0].get("method") == "POST"
        )
        error["attribution"] = (
            "guard-window-causality-unproven" if same_guard_window else "unresolved"
        )
    guard_window_page_errors = [
        error
        for error in page_errors
        if error.get("attribution") == "guard-window-causality-unproven"
    ]
    unexpected_page_errors = [
        error for error in page_errors if error.get("attribution") == "unresolved"
    ]
    if unexpected_page_errors:
        raise RuntimeError(
            "Erreur(s) de page inattendue(s) : "
            + json.dumps(unexpected_page_errors, ensure_ascii=False)
        )
    result["page_errors"] = page_errors
    result["guard_window_page_errors"] = guard_window_page_errors
    result["unexpected_page_errors"] = unexpected_page_errors
    result["page_error_attribution_limit"] = (
        "L’erreur Drupal.AjaxError survient dans la fenêtre de l’unique POST bloqué, "
        "mais l’API pageerror ne permet pas d’établir un lien causal avec cette requête."
    )
    completed_at = datetime.now(timezone.utc)
    result["completed_at"] = completed_at.isoformat()
    result["generated_at"] = completed_at.isoformat()
    if sha256(collector_path) != collector_sha256:
        raise RuntimeError("Le collecteur a changé pendant le run ; preuve non publiée.")
    screenshots = [scenario["screenshot"] for scenario in scenarios.values()]
    if len(screenshots) != 5:
        raise RuntimeError(f"Nombre de captures inattendu : {len(screenshots)}")
    for screenshot in screenshots:
        staged_path = staging / Path(screenshot["file"]).name
        if not staged_path.is_file():
            raise RuntimeError(f"Capture de staging absente : {staged_path.name}")
        if staged_path.stat().st_size != screenshot["bytes"] or sha256(staged_path) != screenshot["sha256"]:
            raise RuntimeError(f"Capture de staging incohérente : {staged_path.name}")

    invalidate_package_validation()
    runs_root = OUTPUT / "runs"
    runs_root.mkdir(parents=True, exist_ok=True)
    final_run = runs_root / run_id
    os.replace(staging, final_run)
    output = OUTPUT / "P06-RETEST-SAFE.json"
    temporary_output = OUTPUT / f".P06-RETEST-SAFE-{run_id}.json.tmp"
    temporary_output.write_text(
        json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    os.replace(temporary_output, output)

    print(json.dumps({
        "output": str(output.relative_to(PROJECT_ROOT)),
        "run_id": run_id,
        "collector_sha256": collector_sha256,
        "blocked_unsafe_method_requests": len(blocked),
        "blocked_websockets": len(blocked_websockets),
        "page_errors": len(page_errors),
        "multipage_comparisons": len(multipage["repeated_control_comparisons"]),
        "multipage_coherent": multipage["all_expected_repeated_dom_candidates_complete_and_coherent"],
    }, ensure_ascii=False, indent=2))
    return 0


def main() -> int:
    configure_paths(parse_args())
    load_playwright()
    with p06_pipeline_lock():
        return _run_locked()


if __name__ == "__main__":
    raise SystemExit(main())
