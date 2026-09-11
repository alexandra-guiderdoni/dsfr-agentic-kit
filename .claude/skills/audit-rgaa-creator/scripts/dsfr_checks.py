#!/usr/bin/env python3
"""Audit DSFR v2 par règle et par instance.

Les sorties séparent les signaux automatiques, la qualification humaine et la
migration de version. Elles ne constituent jamais une déclaration globale de
conformité DSFR ou RGAA.
"""

from __future__ import annotations

import asyncio
import datetime as dt
import hashlib
import json
import re
import sys
from pathlib import Path
from typing import Any

try:
    from playwright.async_api import async_playwright
except ImportError as exc:
    raise SystemExit(
        "Playwright est absent de l’environnement Python sélectionné"
    ) from exc

from navigation import goto_checked
from browser_launch import browser_launch_options, browser_launch_summary


COMPONENTS: dict[str, tuple[str, str]] = {
    "header": (".fr-header", "components/structure/header.md"),
    "footer": (".fr-footer", "components/structure/footer.md"),
    "navigation": (".fr-nav", "components/navigation/navigation.md"),
    "search": (".fr-search-bar", "components/forms-services/search.md"),
    "consent": (".fr-consent-banner", "components/structure/consent.md"),
    "consent_manager": (".fr-consent-manager", "components/structure/consent.md"),
    "consent_service": (".fr-consent-service", "components/structure/consent.md"),
    "modal": (".fr-modal", "components/structure/modal.md"),
    "notice": (".fr-notice", "components/feedback-actions/notice.md"),
    "card": (".fr-card", "components/content-media/cards.md"),
    "tile": (".fr-tile", "components/content-media/tiles.md"),
    "accordion": (".fr-accordion", "components/navigation/accordion.md"),
    "tabs": (".fr-tabs", "components/navigation/tabs.md"),
    "alert": (".fr-alert", "components/feedback-actions/alerts.md"),
    "callout": (".fr-callout", "components/feedback-actions/callout.md"),
    "badge": (".fr-badge", "components/feedback-actions/badges.md"),
    "tag": (".fr-tag", "components/feedback-actions/tags.md"),
    "button_group": (".fr-btns-group", "components/feedback-actions/buttons.md"),
    "button": (".fr-btn", "components/feedback-actions/buttons.md"),
    "link": (".fr-link", "components/navigation/link.md"),
    "skiplink": (".fr-skiplinks", "components/navigation/skiplink.md"),
    "mega_menu": (".fr-mega-menu", "components/navigation/navigation.md"),
    "breadcrumb": (".fr-breadcrumb", "components/navigation/breadcrumb-advanced.md"),
    "summary": (".fr-summary", "components/navigation/summary.md"),
    "table": (".fr-table", "components/content-media/tables.md"),
    "input": (".fr-input-group,.fr-input", "components/forms-services/forms/fields.md"),
    "select": (".fr-select-group", "components/forms-services/forms/choices.md"),
    "upload": (".fr-upload-group", "components/forms-services/forms/fields.md"),
    "message_group": (
        ".fr-messages-group",
        "components/forms-services/forms/fields.md",
    ),
    "checkbox": (".fr-checkbox-group", "components/forms-services/forms/choices.md"),
    "fieldset": (".fr-fieldset", "components/forms-services/forms/choices.md"),
    "radio": (".fr-radio-group", "components/forms-services/forms/choices.md"),
    "toggle": (".fr-toggle", "components/forms-services/toggle.md"),
    "translate": (".fr-translate", "components/navigation/translate.md"),
    "download": (".fr-download", "components/content-media/download.md"),
    "quote": (".fr-quote", "components/content-media/quote.md"),
    "highlight": (".fr-highlight", "components/content-media/highlight.md"),
    "display": (".fr-display", "components/content-media/display.md"),
    "logo": (".fr-logo", "components/structure/logo.md"),
    "follow": (".fr-follow", "components/feedback-actions/follow.md"),
    "share": (".fr-share", "components/feedback-actions/share.md"),
    "franceconnect": (".fr-connect", "components/forms-services/franceconnect.md"),
    "stepper": (".fr-stepper", "components/navigation/stepper.md"),
    "sidemenu": (".fr-sidemenu", "components/navigation.md"),
    "pagination": (".fr-pagination", "components/navigation.md"),
    "password": (".fr-password", "components/forms-services/forms/fields.md"),
    "range": (".fr-range-group,.fr-range", "components/forms-services/forms/fields.md"),
    "segmented": (".fr-segmented", "components/forms-services/forms/choices.md"),
    "tooltip": (".fr-tooltip", "components/feedback-actions/tooltip.md"),
    "back_to_top": (".fr-back-to-top", "components/navigation/back-to-top.md"),
    "transcription": (".fr-transcription", "components/content-media/transcription.md"),
    "tag_group": (".fr-tags-group", "components/feedback-actions/tags.md"),
    "artwork": ("svg.fr-artwork", "components/content-media/artwork.md"),
    "responsive_media": (".fr-responsive-img", "components/content-media/images.md"),
    "grid": (".fr-grid-row", "utilities/grid.md"),
    "container": (".fr-container,.fr-container--fluid", "utilities/grid.md"),
    "enlarge_link": (".fr-enlarge-link", "components/content-media/enlarge-link.md"),
}

SKILLS_ROOT = Path(__file__).resolve().parents[2]
RULES_PATH = SKILLS_ROOT / "audit-dsfr-complet/rules/dsfr-rules.json"
VERIFY_SOURCE = "audit-dsfr-complet/references/integration-invariants.md"
TARGET_DESIGN_SOURCE = "audit-dsfr-complet/references/version-migration.md"
RULE_CATALOG_RELATIVE_PATH = "audit-dsfr-complet/rules/dsfr-rules.json"


def dump(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )


def load_rules_with_metadata() -> tuple[dict[str, Any], dict[str, Any]]:
    try:
        raw = RULES_PATH.read_bytes()
        catalog = json.loads(raw.decode("utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise RuntimeError(
            f"Catalogue de règles DSFR illisible : {RULES_PATH}: {exc}"
        ) from exc
    if catalog.get("schema_version") != 1 or not isinstance(catalog.get("rules"), list):
        raise RuntimeError(f"Catalogue de règles DSFR invalide : {RULES_PATH}")
    metadata = {
        "path": RULE_CATALOG_RELATIVE_PATH,
        "sha256": hashlib.sha256(raw).hexdigest(),
        "schema_version": catalog["schema_version"],
        "target_version": str(catalog["target_version"]),
        "rules_count": len(catalog["rules"]),
    }
    return catalog, metadata


def load_rules() -> dict[str, Any]:
    return load_rules_with_metadata()[0]


def version_tuple(value: str) -> tuple[int, ...]:
    """Normalise une version DSFR pour une comparaison prudente."""
    match = re.match(r"^(\d+(?:\.\d+){1,2})", str(value).strip())
    return tuple(int(part) for part in match.group(1).split(".")) if match else ()


def requires_migration(
    rule: dict[str, Any], observed_versions: list[str], target_version: str
) -> bool:
    """Ne classe en migration qu’une version observée antérieure à la borne."""
    minimum = str(rule.get("minimum_version") or target_version)
    minimum_value = version_tuple(minimum)
    return bool(
        rule.get("version_scope") == "TARGET_VERSION"
        and minimum_value
        and any(
            version_tuple(version) and version_tuple(version) < minimum_value
            for version in observed_versions
        )
    )


def difference(
    pid: str,
    index: int,
    rule_id: str,
    kind: str,
    component: str,
    severity: str,
    title: str,
    expected: str,
    observed: str,
    source: str,
    selector: str,
    observed_html: str,
    expected_html: str,
    recommendation: str,
    verification: str,
    failed_conditions: list[str],
    evidence: list[str],
    observed_versions: list[str],
    target_version: str,
    instance: int | None = None,
    observed_html_origin: str = "RENDERED_DOM",
    status: str = "ECART_OBSERVE",
) -> dict[str, Any]:
    return {
        "id": f"{pid}-{rule_id}-{index:03d}",
        "rule_id": rule_id,
        "kind": kind,
        "component": component,
        "instance": instance,
        "signal_status": "FAIL_CANDIDATE",
        "status": status,
        "qualification_status": "A_CONFIRMER",
        "severity": severity,
        "title": title,
        "expected": expected,
        "observed": observed,
        "selector": selector,
        "observed_html": observed_html,
        "observed_html_origin": observed_html_origin,
        "expected_html": expected_html,
        "failed_conditions": failed_conditions,
        "source": source,
        "reference_target_version": target_version,
        "observed_versions": observed_versions,
        "assessed_against": "CONTROLE_EN_ECHEC"
        if status == "CONTROLE_EN_ECHEC"
        else "VERSION_CIBLE"
        if target_version in observed_versions
        else (
            "VERSION_INDEPENDANTE"
            if kind == "integration"
            else (
                "MIGRATION_VERS_CIBLE"
                if observed_versions
                else "REFERENCE_VERSION_INDISPONIBLE"
            )
        ),
        "evidence": evidence,
        "recommendation": recommendation,
        "verification": verification,
    }


async def inspect_page(
    browser: Any,
    page_info: dict[str, Any],
    config: dict[str, Any],
    root: Path,
    catalog: dict[str, Any],
    catalog_metadata: dict[str, Any] | None = None,
) -> dict[str, Any]:
    pid, url = page_info["id"], page_info["url"]
    if catalog_metadata is None:
        _catalog, catalog_metadata = load_rules_with_metadata()
    attempts_root = root / "dsfr/preuves" / pid
    existing = [
        int(path.name.split("-")[-1])
        for path in attempts_root.glob("attempt-[0-9][0-9][0-9]")
        if path.is_dir()
    ]
    attempt = max(existing, default=0) + 1
    attempt_root = attempts_root / f"attempt-{attempt:03d}"
    attempt_root.mkdir(parents=True, exist_ok=False)
    evidence_path = str((attempt_root / "evidence.json").relative_to(root))
    desktop_path = str((attempt_root / "desktop.png").relative_to(root))
    mobile_path = str((attempt_root / "mobile.png").relative_to(root))
    evidence_files = [evidence_path, desktop_path, mobile_path]
    timeout = int(config.get("browser", {}).get("timeout_seconds", 30)) * 1000
    wait = int(config.get("browser", {}).get("wait_ms", 900))
    context = await browser.new_context(
        viewport={"width": 1440, "height": 1000}, locale="fr-FR"
    )
    page = await context.new_page()
    console_errors: list[str] = []
    resource_failures: list[dict[str, str]] = []
    page.on(
        "console",
        lambda msg: (
            console_errors.append(msg.text[:500]) if msg.type == "error" else None
        ),
    )
    page.on(
        "requestfailed",
        lambda request: resource_failures.append(
            {"url": request.url, "error": request.failure or "Échec réseau"}
        ),
    )
    page.on(
        "response",
        lambda response: resource_failures.append(
            {"url": response.url, "error": f"HTTP {response.status}"}
        )
        if response.status >= 400
        else None,
    )
    await goto_checked(page, url, timeout)
    await page.wait_for_timeout(wait)

    selectors = {name: selector for name, (selector, _source) in COMPONENTS.items()}
    raw = await page.evaluate(
        r"""payload => {
      const {selectors,rules}=payload;
      const visible=e=>{const s=getComputedStyle(e),r=e.getBoundingClientRect();return s.display!=='none'&&s.visibility!=='hidden'&&r.width>0&&r.height>0};
      const clip=(value,max=4000)=>String(value||'').slice(0,max);
      const cssPath=e=>{
        if(!e||!e.tagName)return '';
        if(e.id&&document.querySelectorAll(`#${CSS.escape(e.id)}`).length===1)return `#${CSS.escape(e.id)}`;
        const parts=[];let node=e;
        while(node&&node.nodeType===1&&parts.length<6){
          let part=node.tagName.toLowerCase();
          const classes=[...node.classList].slice(0,3).map(x=>`.${CSS.escape(x)}`).join('');part+=classes;
          const siblings=node.parentElement?[...node.parentElement.children].filter(x=>x.tagName===node.tagName):[];
          if(siblings.length>1)part+=`:nth-of-type(${siblings.indexOf(node)+1})`;
          parts.unshift(part);node=node.parentElement;
        }
        return parts.join(' > ');
      };
      const hasLabel=e=>{
        if(e.labels?.length)return true;
        if((e.getAttribute('aria-label')||'').trim())return true;
        const ids=(e.getAttribute('aria-labelledby')||'').trim().split(/\s+/).filter(Boolean);
        return ids.length>0&&ids.every(id=>document.getElementById(id));
      };
      const conditionPass=(root,c)=>{
        if(c.type==='tag_in')return c.values.includes(root.tagName);
        if(c.type==='attribute_equals')return root.getAttribute(c.name)===c.value;
        if(c.type==='attribute_non_empty')return !!(root.getAttribute(c.name)||'').trim();
        if(c.type==='attribute_present')return root.hasAttribute(c.name);
        if(c.type==='attribute_not_values')return !c.values.includes(root.getAttribute(c.name)||'');
        if(c.type==='attribute_contains')return (root.getAttribute(c.name)||'').toLowerCase().includes(String(c.value||'').toLowerCase());
        if(c.type==='one_attribute_non_empty')return c.names.some(name=>(root.getAttribute(name)||'').trim());
        if(c.type==='aria_reference_exists'){
          const value=(root.getAttribute(c.name)||'').trim();if(!value)return !!c.optional;
          return value.split(/\s+/).every(id=>document.getElementById(id));
        }
        if(c.type==='self_selector')return root.matches(c.selector);
        if(c.type==='self_labelled')return hasLabel(root);
        if(c.type==='descendant_min')return root.querySelectorAll(c.selector).length>=c.min;
        if(c.type==='descendant_max')return root.querySelectorAll(c.selector).length<=c.max;
        if(c.type==='attribute_tokens_contain')return String(root.getAttribute(c.name)||'').split(/\s+/).includes(c.value);
        if(c.type==='accessible_name_contains'){const name=(root.getAttribute('aria-label')||root.getAttribute('title')||root.textContent||'').toLowerCase();return (c.values||[]).some(value=>name.includes(String(value).toLowerCase()));}
        if(c.type==='prohibited')return false;
        if(c.type==='descendant_text_non_empty'){const nodes=[...root.querySelectorAll(c.selector)];return nodes.length>0&&nodes.every(node=>!!node.textContent.trim());}
        if(c.type==='descendant_labelled'){
          const nodes=[...root.querySelectorAll(c.selector)];return nodes.length>0&&nodes.every(hasLabel);
        }
        if(c.type==='descendant_attribute_contains'){
          const nodes=[...root.querySelectorAll(c.selector)];return nodes.length>0&&nodes.every(node=>(node.getAttribute(c.name)||'').toLowerCase().includes(String(c.value||'').toLowerCase()));
        }
        if(c.type==='descendant_fragment_targets_exist'){
          const nodes=[...root.querySelectorAll(c.selector)];return nodes.length>0&&nodes.every(node=>{const href=(node.getAttribute('href')||'').trim();return href.startsWith('#')&&href.length>1&&!!document.getElementById(href.slice(1));});
        }
        if(c.type==='descendant_fragment_targets_exposed'){
          const nodes=[...root.querySelectorAll(c.selector)];return nodes.length>0&&nodes.every(node=>{const href=(node.getAttribute('href')||'').trim(),target=href.startsWith('#')?document.getElementById(href.slice(1)):null;return !!target&&!target.closest('[aria-hidden="true"]');});
        }
        if(c.type==='referenced_by_control'){
          return !!root.id&&!!document.querySelector(`[aria-controls="${CSS.escape(root.id)}"]`);
        }
        if(c.type==='referenced_by_attribute'){
          return !!root.id&&[...document.querySelectorAll(`[${c.name}]`)].some(node=>(node.getAttribute(c.name)||'').trim().split(/\s+/).includes(root.id));
        }
        if(c.type==='referenced_by_attribute_or_empty'){
          return !root.textContent.trim()||!!root.id&&[...document.querySelectorAll(`[${c.name}]`)].some(node=>(node.getAttribute(c.name)||'').trim().split(/\s+/).includes(root.id));
        }
        if(c.type==='tag_semantics'){
          if(root.tagName==='P')return !!root.textContent.trim();
          if(root.tagName==='A')return !!(root.getAttribute('href')||'').trim();
          if(root.tagName==='BUTTON')return !!(root.getAttribute('type')||'').trim()&&(!root.classList.contains('fr-tag--dismiss')||(root.getAttribute('aria-label')||'').trim())&&(!root.closest('.fr-tags-group')||(root.hasAttribute('aria-pressed')||root.classList.contains('fr-tag--dismiss')));
          return false;
        }
        if(c.type==='ancestor_or_self_attribute'){
          let node=root;while(node){if(node.getAttribute?.(c.name)===c.value)return true;node=node.parentElement;}return false;
        }
        if(c.type==='ancestor_or_self_selector')return !!root.closest(c.selector);
        if(c.type==='button_or_link_target'){
          if(root.tagName==='BUTTON')return !!(root.getAttribute('type')||'').trim()||!root.closest('form');
          if(root.tagName==='INPUT'&&['button','submit','reset','image'].includes((root.getAttribute('type')||'').toLowerCase()))return !!(root.getAttribute('value')||root.getAttribute('alt')||'').trim();
          if(root.tagName==='A'){const href=(root.getAttribute('href')||'').trim();return !!href&&href!=='#';}
          return false;
        }
        return false;
      };
      const components={};
      for(const [name,selector] of Object.entries(selectors)){
        const nodes=[...document.querySelectorAll(selector)];
        if(nodes.length)components[name]={selector,count:nodes.length,visible:nodes.filter(visible).length,samples:nodes.slice(0,3).map((e,index)=>({instance:index+1,selector:cssPath(e),tag:e.tagName,id:e.id,classes:[...e.classList],role:e.getAttribute('role'),html:clip(e.outerHTML,1600)}))};
      }
      const ruleResults=[];
      for(const rule of rules){
        const nodes=[...document.querySelectorAll(rule.selector)].filter(e=>!rule.exclude_selector||!e.matches(rule.exclude_selector));
        nodes.forEach((root,index)=>{
          const failed=rule.conditions.filter(c=>!conditionPass(root,c)).map(c=>c.message);
          ruleResults.push({rule_id:rule.rule_id,component:rule.component,instance:index+1,selector:cssPath(root),signal_status:failed.length?'FAIL_CANDIDATE':'PASS_CANDIDATE',failed_conditions:failed,observed_html:clip(root.outerHTML)});
        });
      }
      const resources=[...document.querySelectorAll('link[href],script[src]')].map(e=>e.href||e.src).filter(Boolean);
      const idNodes=[...document.querySelectorAll('[id]')];const ids=idNodes.map(e=>e.id);const duplicateIds=[...new Set(ids.filter((id,i)=>ids.indexOf(id)!==i))];
      const duplicateInstances=duplicateIds.map(id=>({id,instances:idNodes.filter(e=>e.id===id).map(e=>({selector:cssPath(e),html:clip(e.outerHTML,1200)}))}));
      const skips=[...document.querySelectorAll('.fr-skiplinks a,a[href^="#"]')].filter(e=>(e.closest('.fr-skiplinks')||/contenu|menu|recherche|pied/i.test(e.textContent))).map(e=>{const href=e.getAttribute('href')||'';let target=false;try{target=href.startsWith('#')&&href.length>1&&!!document.querySelector(href)}catch{}return{text:e.textContent.trim(),href,target,selector:cssPath(e),html:clip(e.outerHTML,1200)}});
      const footer=document.querySelector('.fr-footer,footer');const footerText=footer?.textContent||'';const bodyStyle=getComputedStyle(document.body);
      return {
        title:document.title,lang:document.documentElement.lang,viewport:document.querySelector('meta[name=viewport]')?.content||'',
        dsfrInitialized:document.documentElement.getAttribute('data-fr-js')==='true'||document.documentElement.classList.contains('fr-js'),
        dsfrRuntimeVersion:globalThis.dsfr?.version||globalThis.dsfr?.inspector?.version||null,
        resources,components,ruleResults,skips,duplicateIds,duplicateInstances,fontFamily:bodyStyle.fontFamily,
        bodyOpenTag:`<body class="${document.body.className}"${document.body.id?` id="${document.body.id}"`:''}>`,
        shell:{header:document.querySelectorAll('header,.fr-header,[role=banner]').length,main:document.querySelectorAll('main,[role=main]').length,footer:document.querySelectorAll('footer,.fr-footer,[role=contentinfo]').length,examples:[...document.querySelectorAll('header,.fr-header,main,[role=main],footer,.fr-footer')].slice(0,4).map(e=>({selector:cssPath(e),html:clip(e.outerHTML,900)}))},
        grid:{containers:document.querySelectorAll('.fr-container,.fr-container--fluid').length,rows:document.querySelectorAll('.fr-grid-row').length,columns:document.querySelectorAll('[class*="fr-col-"]').length},
        legal:{accessibility:/accessibilit/i.test(footerText),legal:/mentions? légales?/i.test(footerText),personalData:/données personnelles|vie privée/i.test(footerText),cookies:/cookies|gestionnaire de consentement/i.test(footerText),selector:footer?cssPath(footer):'',html:footer?clip(footer.outerHTML,2400):''},
        hrefHash:[...document.querySelectorAll('a[href="#"]')].filter(visible).map(e=>({text:e.textContent.trim().slice(0,120),selector:cssPath(e),html:clip(e.outerHTML,1200)})),
        customStylesheets:resources.filter(x=>/\.css(?:[?#]|$)/i.test(x)&&!/dsfr(?:\.min)?\.css|@gouvfr\/dsfr/i.test(x)),inlineStyles:document.querySelectorAll('[style]').length
      };
    }""",
        {"selectors": selectors, "rules": catalog["rules"]},
    )

    await page.screenshot(path=str(attempt_root / "desktop.png"), full_page=False)
    mobile = await browser.new_context(
        viewport={"width": 375, "height": 812}, locale="fr-FR"
    )
    mobile_page = await mobile.new_page()
    await goto_checked(mobile_page, url, timeout)
    await mobile_page.wait_for_timeout(wait)
    await mobile_page.screenshot(path=str(attempt_root / "mobile.png"), full_page=False)
    mobile_metrics = await mobile_page.evaluate(
        "() => ({viewport:innerWidth,scrollWidth:document.documentElement.scrollWidth})"
    )
    await mobile.close()
    await context.close()

    version_candidates: list[str] = []
    if raw.get("dsfrRuntimeVersion"):
        version_candidates.append(str(raw["dsfrRuntimeVersion"]))
    for resource in raw["resources"]:
        match = re.search(
            r"(?:@gouvfr/dsfr@|dsfr[-./])v?(\d+\.\d+(?:\.\d+)?)",
            resource,
            re.IGNORECASE,
        )
        if match:
            version_candidates.append(match.group(1))
    observed_versions = sorted(set(version_candidates))
    target_version = str(catalog["target_version"])
    raw["detectedVersions"] = observed_versions
    raw["consoleErrors"] = console_errors
    raw["resourceFailures"] = resource_failures
    raw["mobile"] = mobile_metrics
    dsfr_resource_failures = [
        item
        for item in resource_failures
        if re.search(r"dsfr|marianne|font|woff|\.css(?:[?#]|$)|\.js(?:[?#]|$)", item["url"], re.I)
    ]
    dsfr_console_failure = [
        message
        for message in console_errors
        if re.search(r"failed to load resource|net::err|dsfr|marianne|woff", message, re.I)
    ]
    resource_failure = bool(dsfr_resource_failures or dsfr_console_failure)
    resource_failure_detail = json.dumps(
        {"requests": dsfr_resource_failures, "console": dsfr_console_failure},
        ensure_ascii=False,
    )

    differences: list[dict[str, Any]] = []
    state_component_rules: dict[str, set[str]] = {}

    def add(
        rule_id: str,
        kind: str,
        component: str,
        severity: str,
        title: str,
        expected: str,
        observed: str,
        source: str = VERIFY_SOURCE,
        selector: str = "",
        observed_html: str = "",
        expected_html: str = "",
        recommendation: str = "Corriger l’intégration selon la référence citée.",
        verification: str = "Rejouer la règle sur le DOM rendu.",
        failed_conditions: list[str] | None = None,
        instance: int | None = None,
        observed_html_origin: str = "RENDERED_DOM",
        status: str = "ECART_OBSERVE",
    ) -> None:
        differences.append(
            difference(
                pid,
                len(differences) + 1,
                rule_id,
                kind,
                component,
                severity,
                title,
                expected,
                observed,
                source,
                selector,
                observed_html,
                expected_html,
                recommendation,
                verification,
                failed_conditions or [],
                evidence_files,
                observed_versions,
                target_version,
                instance,
                observed_html_origin,
                status,
            )
        )

    state_candidates = [
        root / "preuves-p01-complet/P01-ETATS-DSFR-COMPLEMENTAIRES.json",
        root / f"preuves-{pid.lower()}-complet/{pid}-COLLECTE-COMPLETE.json",
        root
        / f"preuves-{pid.lower()}-complet/{pid}-ETATS-FORMULAIRE-COMPLEMENTAIRES.json",
    ]
    for extended_state_path in state_candidates:
        if not extended_state_path.is_file():
            continue
        extended_states = json.loads(extended_state_path.read_text(encoding="utf-8"))
        component_focus = [
            {
                "label": item.get("label", "Modale"),
                "restored": item.get("focus_restored"),
                "raw": item,
            }
            for item in extended_states.get("component_states", [])
            if item.get("label") in {"Consentement", "Thème"}
        ]
        positive_labels = {
            item["label"] for item in component_focus if item.get("restored") is True
        }
        focus_checks = (
            component_focus
            + [
                {
                    "label": item.get("trigger", "Modale"),
                    "restored": item.get("escape_focus_restored"),
                    "raw": item,
                }
                for item in extended_states.get("focus_traps", [])
                if item.get("trigger", "Modale") not in positive_labels
            ]
            + [
                {
                    "label": item.get("label", "Modale"),
                    "restored": item.get("focus_after_escape"),
                    "raw": item,
                }
                for item in extended_states.get("modal_focus_loops", [])
                if item.get("label", "Modale") not in positive_labels
            ]
        )
        for instance, focus_check in enumerate(
            (item for item in focus_checks if item.get("restored") is False), 1
        ):
            label = str(focus_check["label"])
            is_theme = label in {"Paramètres d’affichage", "Thème"}
            selector = (
                '[aria-controls="fr-theme-modal"]:not(.fr-btn--close)'
                if is_theme
                else '[aria-controls="fr-consent-modal"]:not(.fr-btn--close)'
            )
            target_label = "Paramètres d’affichage" if is_theme else "Personnaliser"
            add(
                "DSFR-MODAL-FOCUS-RESTORE-002",
                "integration",
                "modal",
                "Bloquant",
                f"Focus non restauré après fermeture de la modale {label}",
                f"Après Échap, le focus revient au déclencheur {target_label}",
                json.dumps(focus_check["raw"], ensure_ascii=False),
                selector=selector,
                observed_html=f'<button aria-controls="{("fr-theme-modal" if is_theme else "fr-consent-modal")}">{target_label}</button>',
                expected_html=f'<button aria-controls="{("fr-theme-modal" if is_theme else "fr-consent-modal")}">{target_label}</button>',
                recommendation="Restaurer le focus sur le déclencheur exact après la fermeture au clavier.",
                verification="Ouvrir la modale, parcourir ses contrôles, presser Échap puis contrôler document.activeElement.",
                failed_conditions=["Le focus ne revient pas sur le déclencheur."],
                instance=instance,
                observed_html_origin="MEASUREMENTS",
            )
            state_evidence = str(extended_state_path.relative_to(root))
            if state_evidence not in differences[-1]["evidence"]:
                differences[-1]["evidence"].append(state_evidence)
        error_state = extended_states.get("server_error_state", {})
        for instance, field in enumerate(
            (
                item
                for item in error_state.get("errors", [])
                if item.get("tag") in {"input", "textarea"}
                and "fr-input" in str(item.get("class", "")).split()
                and "fr-input--error" not in str(item.get("class", "")).split()
            ),
            1,
        ):
            selector = (
                f"#{field.get('id')}"
                if field.get("id")
                else ".fr-input[aria-invalid=true]"
            )
            add(
                "DSFR-INPUT-ERROR-STATE-002",
                "migration"
                if requires_migration(
                    {"version_scope": "TARGET_VERSION", "minimum_version": target_version},
                    observed_versions,
                    target_version,
                )
                else "integration",
                "input",
                "Majeur",
                "Champ en erreur sans modificateur DSFR",
                "Le groupe et le champ portent leurs modificateurs error et le message est relié",
                "fr-input--error absent",
                "dsfr-components/references/components/forms-services/forms/fields.md",
                selector=selector,
                observed_html=str(field.get("parentHtml") or field.get("html") or ""),
                expected_html='<div class="fr-input-group fr-input-group--error"><input class="fr-input fr-input--error" aria-invalid="true" aria-describedby="champ-erreur"><p id="champ-erreur" class="fr-error-text">Erreur</p></div>',
                recommendation="Ajouter fr-input--error au champ tout en conservant le groupe et le message relié.",
                verification="Déclencher la validation serveur puis inspecter chaque champ en erreur.",
                failed_conditions=["Le champ en erreur ne porte pas fr-input--error."],
                instance=instance,
                observed_html_origin="RENDERED_DOM",
            )
            state_component_rules.setdefault("input", set()).add(
                "DSFR-INPUT-ERROR-STATE-002"
            )
            state_evidence = str(extended_state_path.relative_to(root))
            if state_evidence not in differences[-1]["evidence"]:
                differences[-1]["evidence"].append(state_evidence)

    if (
        raw["shell"]["header"] == 0
        or raw["shell"]["main"] != 1
        or raw["shell"]["footer"] == 0
    ):
        add(
            "DSFR-SHELL-STRUCTURE-001",
            "integration",
            "page-shell",
            "Bloquant",
            "Enveloppe de page incomplète",
            "Un header, un main unique et un footer",
            json.dumps(raw["shell"], ensure_ascii=False),
            selector="html",
            observed_html="\n".join(item["html"] for item in raw["shell"]["examples"]),
            expected_html='<header>…</header><main id="content">…</main><footer>…</footer>',
            recommendation="Restaurer les trois régions principales et une seule zone main.",
            verification="Contrôler les landmarks dans l’arbre d’accessibilité.",
            failed_conditions=["Nombre attendu de régions principales non observé."],
        )
    valid_content_skips = [
        item
        for item in raw["skips"]
        if item["target"] and re.search(r"contenu", item["text"], re.IGNORECASE)
    ]
    if not valid_content_skips:
        invalid = next(
            (
                item
                for item in raw["skips"]
                if re.search(r"contenu", item["text"], re.IGNORECASE)
            ),
            None,
        )
        add(
            "DSFR-SKIPLINK-CONTENT-001",
            "integration",
            "skiplinks",
            "Bloquant",
            "Lien d’évitement vers le contenu absent ou invalide",
            "Un lien d’évitement vers une cible de contenu existante",
            json.dumps(raw["skips"], ensure_ascii=False),
            selector=(invalid or {}).get("selector", ".fr-skiplinks"),
            observed_html=(invalid or {}).get(
                "html", "<!-- Aucun lien d’évitement vers le contenu détecté -->"
            ),
            expected_html='<a class="fr-link" href="#content">Contenu</a><main id="content">…</main>',
            recommendation="Créer une cible de contenu existante et y transférer le focus lors de l’activation.",
            verification="Activer le premier lien au clavier et vérifier sa destination.",
            failed_conditions=["Aucune cible de contenu valide n’a été trouvée."],
        )
    if not raw["lang"].lower().startswith("fr"):
        add(
            "DSFR-DOCUMENT-LANG-001",
            "integration",
            "language",
            "Bloquant",
            "Langue principale française absente",
            "html lang=fr",
            f"lang={raw['lang']!r}",
            selector="html",
            observed_html=f'<html lang="{raw["lang"]}">',
            expected_html='<html lang="fr">',
            recommendation="Déclarer la langue principale française.",
            verification="Inspecter l’attribut lang de html.",
            failed_conditions=["lang ne commence pas par fr."],
        )
    if "width=device-width" not in raw["viewport"]:
        add(
            "DSFR-VIEWPORT-001",
            "integration",
            "viewport",
            "Majeur",
            "Viewport mobile incomplet",
            "meta viewport avec width=device-width",
            raw["viewport"] or "absent",
            selector="meta[name=viewport]",
            observed_html=f'<meta name="viewport" content="{raw["viewport"]}">'
            if raw["viewport"]
            else "<!-- meta viewport absente -->",
            expected_html='<meta name="viewport" content="width=device-width, initial-scale=1">',
            recommendation="Déclarer un viewport adapté aux terminaux mobiles.",
            verification="Recharger à 375 px et vérifier la largeur de mise en page.",
            failed_conditions=["width=device-width est absent."],
        )
    if any(
        version_tuple(version) and version_tuple(version) < version_tuple(target_version)
        for version in observed_versions
    ):
        add(
            "DSFR-VERSION-MIGRATION-001",
            "migration",
            "version",
            "Majeur",
            "Migration DSFR à qualifier",
            f"Cible locale DSFR {target_version}",
            ", ".join(observed_versions),
            TARGET_DESIGN_SOURCE,
            selector="link[href],script[src]",
            observed_html="\n".join(raw["resources"]),
            expected_html=f"<!-- Ressources DSFR {target_version} après plan de migration -->",
            recommendation=f"Auditer d’abord l’intégration contre une source épinglée {observed_versions[0]}, puis planifier séparément la migration vers {target_version}.",
            verification="Vérifier les versions CSS et JS réellement chargées et exécuter les tests de migration.",
            failed_conditions=[
                f"La version observée diffère de la cible locale {target_version}."
            ],
            observed_html_origin="RESOURCE_URLS",
        )
    if len(observed_versions) > 1:
        add(
            "DSFR-VERSION-COHERENCE-001",
            "integration",
            "version",
            "Majeur",
            "Versions DSFR multiples détectées",
            "Une version CSS/JS cohérente",
            ", ".join(observed_versions),
            TARGET_DESIGN_SOURCE,
            selector="link[href],script[src]",
            observed_html="\n".join(raw["resources"]),
            expected_html="<!-- Même version DSFR pour les ressources CSS et JavaScript -->",
            recommendation="Aligner toutes les ressources DSFR sur une seule version.",
            verification="Inspecter les URL et les métadonnées de version.",
            failed_conditions=["Plusieurs versions ont été détectées."],
            observed_html_origin="RESOURCE_URLS",
        )
    if not raw["dsfrInitialized"]:
        add(
            "DSFR-JS-INITIALIZATION-001",
            "control_failure" if resource_failure else "integration",
            "javascript",
            "Majeur",
            "Initialisation JavaScript DSFR non observée",
            "Initialisation DSFR visible après chargement",
            "data-fr-js/fr-js absent",
            selector="html",
            observed_html=resource_failure_detail if resource_failure else "<html>",
            expected_html='<html data-fr-js="true">',
            recommendation="Charger et initialiser le JavaScript DSFR avant les interactions.",
            verification="Contrôler data-fr-js après chargement.",
            failed_conditions=["Aucun marqueur d’initialisation DSFR n’a été observé."],
            status="CONTROLE_EN_ECHEC" if resource_failure else "ECART_OBSERVE",
        )
    if raw["duplicateIds"]:
        add(
            "DSFR-HTML-ID-UNIQUE-001",
            "integration",
            "html",
            "Bloquant",
            "Identifiants dupliqués dans les composants",
            "Identifiants uniques",
            ", ".join(raw["duplicateIds"]),
            selector=", ".join(f"#{value}" for value in raw["duplicateIds"]),
            observed_html="\n\n".join(
                instance["html"]
                for group in raw["duplicateInstances"]
                for instance in group["instances"]
            ),
            expected_html="<!-- Un identifiant unique par élément et par variante de gabarit -->",
            recommendation="Rendre uniques les identifiants des variantes desktop et mobile puis mettre à jour leurs références.",
            verification="Recalculer les occurrences de chaque id dans le DOM rendu.",
            failed_conditions=[
                f"Identifiants présents plusieurs fois : {', '.join(raw['duplicateIds'])}."
            ],
        )
    if raw["grid"]["containers"] == 0 or raw["grid"]["rows"] == 0:
        add(
            "DSFR-GRID-STRUCTURE-001",
            "migration"
            if requires_migration(
                {"version_scope": "TARGET_VERSION", "minimum_version": target_version},
                observed_versions,
                target_version,
            )
            else "integration",
            "grid",
            "Majeur",
            "Grille DSFR non observée",
            "fr-container et fr-grid-row pour une page complète",
            json.dumps(raw["grid"], ensure_ascii=False),
            selector="body",
            observed_html=raw["bodyOpenTag"],
            expected_html='<div class="fr-container"><div class="fr-grid-row">…</div></div>',
            recommendation="Utiliser les primitives de grille lorsque le gabarit de page le requiert.",
            verification="Inspecter les conteneurs, lignes et colonnes à chaque breakpoint.",
            failed_conditions=["fr-container ou fr-grid-row est absent."],
        )
    if "Marianne" not in raw["fontFamily"]:
        add(
            "DSFR-TYPOGRAPHY-MARIANNE-001",
            "control_failure" if resource_failure else (
                "migration"
                if any(
                    version_tuple(version) and version_tuple(version) < version_tuple(target_version)
                    for version in observed_versions
                )
                else "integration"
            ),
            "typography",
            "Majeur",
            "Police Marianne non observée sur le corps",
            "Marianne avec repli Arial",
            raw["fontFamily"],
            selector="body",
            observed_html=raw["bodyOpenTag"],
            expected_html="body { font-family: Marianne, arial, sans-serif; }",
            recommendation="Vérifier le chargement des fontes et les tokens typographiques DSFR.",
            verification="Contrôler la police calculée du corps et des composants.",
            failed_conditions=["La police calculée ne contient pas Marianne."],
            observed_html_origin="COMPUTED_VALUE",
            status="CONTROLE_EN_ECHEC" if resource_failure else "ECART_OBSERVE",
        )
    if raw["mobile"]["scrollWidth"] > raw["mobile"]["viewport"]:
        add(
            "DSFR-RESPONSIVE-OVERFLOW-001",
            "integration",
            "responsive",
            "Majeur",
            "Débordement horizontal mobile",
            "Aucun débordement à 375 px",
            json.dumps(raw["mobile"]),
            selector="html",
            observed_html=f"<!-- scrollWidth={raw['mobile']['scrollWidth']}, viewport={raw['mobile']['viewport']} -->",
            expected_html="<!-- scrollWidth <= viewport -->",
            recommendation="Identifier l’instance débordante et corriger ses contraintes de largeur.",
            verification="Tester à 320 px et 375 px avec zoom et espacement du texte.",
            failed_conditions=["scrollWidth dépasse la largeur du viewport."],
            observed_html_origin="MEASUREMENTS",
        )
    missing_legal = [
        name
        for name in ("accessibility", "legal", "personalData", "cookies")
        if not raw["legal"][name]
    ]
    if missing_legal:
        add(
            "DSFR-FOOTER-LEGAL-001",
            "integration",
            "footer",
            "Majeur",
            "Liens ou mentions de pied de page incomplets",
            "Accessibilité, mentions légales, données personnelles et cookies",
            ", ".join(missing_legal),
            "dsfr-components/references/components/structure/footer.md",
            selector=raw["legal"]["selector"],
            observed_html=raw["legal"]["html"],
            expected_html='<footer class="fr-footer">… liens institutionnels et politiques …</footer>',
            recommendation="Ajouter les liens institutionnels manquants dans la zone documentée du pied de page.",
            verification="Contrôler les intitulés, destinations et disponibilité des liens.",
            failed_conditions=[f"Mentions absentes : {', '.join(missing_legal)}."],
        )

    rule_by_id = {rule["rule_id"]: rule for rule in catalog["rules"]}
    for item in raw["ruleResults"]:
        if item["signal_status"] != "FAIL_CANDIDATE":
            continue
        rule = rule_by_id[item["rule_id"]]
        kind = "migration" if requires_migration(rule, observed_versions, target_version) else "integration"
        add(
            rule["rule_id"],
            kind,
            rule["component"],
            rule["severity"],
            rule["title"],
            rule["expected"],
            "; ".join(item["failed_conditions"]),
            rule["source"],
            selector=item["selector"],
            observed_html=item["observed_html"],
            expected_html=rule["expected_html"],
            recommendation=rule["recommendation"],
            verification=rule["verification"],
            failed_conditions=item["failed_conditions"],
            instance=item["instance"],
        )

    inventory: list[dict[str, Any]] = []
    component_rules: dict[str, list[dict[str, Any]]] = {}
    for item in raw["ruleResults"]:
        component_rules.setdefault(item["component"], []).append(item)
    for name, item in sorted(raw["components"].items()):
        results = component_rules.get(name, [])
        state_rules = state_component_rules.get(name, set())
        if not results and not state_rules:
            status = "DETECTE_NON_AUDITE"
        elif state_rules or any(
            result["signal_status"] == "FAIL_CANDIDATE" for result in results
        ):
            status = "ECART_OBSERVE"
        else:
            status = "AUCUN_ECART_REGLES_EXECUTEES"
        inventory.append(
            {
                "name": name,
                "selector": item["selector"],
                "count": item["count"],
                "visible": item["visible"],
                "status": status,
                "rules_executed": sorted(
                    {result["rule_id"] for result in results} | state_rules
                ),
                "source": "dsfr-components/references/" + COMPONENTS[name][1],
                "samples": item["samples"],
            }
        )

    comparison_mode = (
        "VERSION_CIBLE"
        if target_version in observed_versions
        else (
            "MIGRATION_VERS_CIBLE"
            if observed_versions
            else "REFERENCE_VERSION_INDISPONIBLE"
        )
    )
    result = {
        "schema_version": 2,
        "page": page_info,
        "audited_at": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"),
        "rule_catalog": catalog_metadata,
        "version": {
            "observed": observed_versions,
            "target": target_version,
            "comparison_mode": comparison_mode,
            "exact_observed_reference_available": target_version in observed_versions,
        },
        "reference_version": target_version,
        "detected_versions": observed_versions,
        "status": "SIGNAUX D’ÉCART OBSERVÉS"
        if differences
        else "AUCUN ÉCART OBSERVÉ SUR LES RÈGLES EXÉCUTÉES",
        "claim": "Aucune conformité DSFR globale n’est revendiquée.",
        "inventory": inventory,
        "rule_results": raw["ruleResults"],
        "global_checks": raw,
        "differences": differences,
        "sources": [
            VERIFY_SOURCE,
            TARGET_DESIGN_SOURCE,
            "audit-dsfr-complet/rules/dsfr-rules.json",
            "dsfr-components/assets/dsfr_complete_library.json",
        ],
        "not_verified": [
            "droit d’usage de la marque de l’État",
            "exhaustivité officielle des composants",
            "fidélité visuelle exhaustive",
            "lecteur d’écran réel",
        ]
        + (
            []
            if target_version in observed_versions
            else [
                f"intégration exacte contre une source locale DSFR {observed_versions[0] if observed_versions else 'observée'}"
            ]
        ),
        "evidence": {
            "attempt": attempt,
            "raw": evidence_path,
            "desktop_screenshot": desktop_path,
            "mobile_screenshot": mobile_path,
        },
    }
    dump(attempt_root / "evidence.json", result)
    dump(root / "dsfr/pages" / f"{pid}.json", result)
    return result


async def main(config_path: Path) -> int:
    config = json.loads(config_path.read_text(encoding="utf-8"))
    root = Path(config.pop("_campaign_root")).resolve()
    (root / "dsfr/preuves").mkdir(parents=True, exist_ok=True)
    catalog, catalog_metadata = load_rules_with_metadata()
    failures: list[dict[str, str]] = []
    async with async_playwright() as playwright:
        browser = await playwright.chromium.launch(**browser_launch_options(config))
        for page_info in config["sample"]:
            try:
                result = await inspect_page(
                    browser, page_info, config, root, catalog, catalog_metadata
                )
                print(f"{page_info['id']} {result['status']}")
            except Exception as exc:
                failures.append({"page": page_info["id"], "error": str(exc)})
                print(f"{page_info['id']} ECHEC: {exc}", file=sys.stderr)
        await browser.close()
    dump(
        root / "logs/dsfr-checks-summary.json",
        {
            "failures": failures,
            "pages": len(config["sample"]),
            "rules": len(catalog["rules"]),
            "target_version": catalog["target_version"],
            "rule_catalog": catalog_metadata,
            "browser_launch": browser_launch_summary(config),
        },
    )
    return 1 if failures else 0


if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit("Usage: dsfr_checks.py CAMPAIGN-RUNTIME.JSON")
    raise SystemExit(asyncio.run(main(Path(sys.argv[1]).resolve())))
