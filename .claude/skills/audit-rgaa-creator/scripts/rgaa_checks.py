#!/usr/bin/env python3
"""Collecte RGAA v2 par règle et instance sur le DOM rendu."""

from __future__ import annotations

import asyncio
import datetime as dt
import json
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


SOURCE = "https://accessibilite.numerique.gouv.fr/methode/criteres-et-tests/"
CATALOG_PATH = (
    Path(__file__).resolve().parents[2] / "audit-rgaa-complet/rules/rgaa-rules.json"
)
AXE_MAPPING_PATH = (
    Path(__file__).resolve().parents[2]
    / "audit-rgaa-complet/references/axe-rgaa-mapping.json"
)
_catalog = json.loads(CATALOG_PATH.read_text(encoding="utf-8"))
_catalog_rules = {item["rule_id"]: item for item in _catalog.get("rules", [])}
if not _catalog_rules or len(_catalog_rules) != len(_catalog.get("rules", [])):
    raise RuntimeError("Catalogue RGAA absent ou identifiants de règle dupliqués")
RULES = _catalog_rules


def dump(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )


def load_axe_result(root: Path, pid: str) -> dict[str, Any]:
    """Charge la collecte axe-core produite par la phase navigateur."""
    path = root / "tests-wcag" / f"{pid}.json"
    if not path.is_file():
        return {
            "status": "absent",
            "reason": "La phase navigateur n’a pas produit de collecte axe-core.",
        }
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return {"status": "failed", "reason": f"Collecte axe-core illisible : {exc}"}
    value = data.get("axe_core")
    return (
        value
        if isinstance(value, dict)
        else {"status": "absent", "reason": "Collecte axe-core absente."}
    )


def load_axe_mapping() -> dict[str, Any]:
    if not AXE_MAPPING_PATH.is_file():
        return {}
    try:
        data = json.loads(AXE_MAPPING_PATH.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise RuntimeError(
            f"Cartographie axe-core illisible : {AXE_MAPPING_PATH}: {exc}"
        ) from exc
    return data if isinstance(data, dict) else {}


def signal(
    pid: str,
    index: int,
    rule_id: str,
    instance: int,
    selector: str,
    observed: str,
    observed_code: str,
    origin: str,
    assertions: list[str],
    evidence: list[str],
    signal_status: str = "FAIL_CANDIDATE",
) -> dict[str, Any]:
    rule = RULES[rule_id]
    return {
        "id": f"{pid}-{rule_id}-{index:03d}",
        "rule_id": rule_id,
        "criterion": rule["criterion"],
        "test": rule["test"],
        "component": rule["component"],
        "instance": instance,
        "signal_status": signal_status,
        "qualification_status": "NON_TESTE",
        "severity": rule["severity"],
        "title": rule["title"],
        "selector": selector,
        "observed": observed,
        "observed_code": observed_code,
        "observed_origin": origin,
        "expected": rule["expected"],
        "expected_code": rule["expected_code"],
        "failed_assertions": assertions,
        "impact": rule["impact"],
        "source": f"{SOURCE}#{rule['test']}",
        "recommendation": rule["recommendation"],
        "verification": rule["verification"],
        "evidence": evidence,
    }


async def inspect_page(
    browser: Any, page_info: dict[str, Any], config: dict[str, Any], root: Path
) -> dict[str, Any]:
    pid, url = page_info["id"], page_info["url"]
    attempts_root = root / "rgaa/preuves" / pid
    existing = [
        int(path.name.split("-")[-1])
        for path in attempts_root.glob("attempt-[0-9][0-9][0-9]")
        if path.is_dir()
    ]
    attempt = max(existing, default=0) + 1
    attempt_root = attempts_root / f"attempt-{attempt:03d}"
    attempt_root.mkdir(parents=True, exist_ok=False)
    raw_path = str((attempt_root / "raw-dom.json").relative_to(root))
    screenshot_path = str((attempt_root / "desktop.png").relative_to(root))
    evidence_files = [raw_path, screenshot_path]
    timeout = int(config.get("browser", {}).get("timeout_seconds", 30)) * 1000
    wait = int(config.get("browser", {}).get("wait_ms", 900))
    tabs = int(config.get("browser", {}).get("tabs_per_page", 25))
    context = await browser.new_context(
        viewport={"width": 1440, "height": 1000}, locale="fr-FR"
    )
    page = await context.new_page()
    await goto_checked(page, url, timeout)
    await page.wait_for_timeout(wait)
    raw = await page.evaluate(r"""() => {
      const clip=(v,n=3500)=>String(v||'').slice(0,n);const visible=e=>{const s=getComputedStyle(e),r=e.getBoundingClientRect();return s.display!=='none'&&s.visibility!=='hidden'&&r.width>0&&r.height>0};
      const cssPath=e=>{if(!e||!e.tagName)return'';if(e.id&&document.querySelectorAll(`#${CSS.escape(e.id)}`).length===1)return`#${CSS.escape(e.id)}`;const p=[];let n=e;while(n&&n.nodeType===1&&p.length<6){let x=n.tagName.toLowerCase()+[...n.classList].slice(0,2).map(c=>`.${CSS.escape(c)}`).join('');const s=n.parentElement?[...n.parentElement.children].filter(y=>y.tagName===n.tagName):[];if(s.length>1)x+=`:nth-of-type(${s.indexOf(n)+1})`;p.unshift(x);n=n.parentElement;}return p.join(' > ')};
      const labelled=e=>!!(e.labels?.length||(e.getAttribute('aria-label')||'').trim()||(e.getAttribute('aria-labelledby')||'').split(/\s+/).filter(Boolean).some(id=>document.getElementById(id))||(e.getAttribute('title')||'').trim());
      const ids=[...document.querySelectorAll('[id]')];const labelsBroken=[...document.querySelectorAll('label[for]')].filter(e=>{const id=(e.getAttribute('for')||'').trim();return !id||!document.getElementById(id)}).map(e=>({for:e.getAttribute('for')||'',selector:cssPath(e),html:clip(e.outerHTML)}));const duplicate=[...new Set(ids.map(e=>e.id).filter((id,i,a)=>a.indexOf(id)!==i))].map(id=>({id,instances:ids.filter(e=>e.id===id).map(e=>({selector:cssPath(e),html:clip(e.outerHTML,1500)}))}));
      const invalidAnchorTypes=[...document.querySelectorAll('a[type]')].filter(e=>!/^[-!#$%&'*+.^_`|~0-9A-Za-z]+\/[-!#$%&'*+.^_`|~0-9A-Za-z]+(?:\s*;.*)?$/.test((e.getAttribute('type')||'').trim())).map(e=>({value:e.getAttribute('type')||'',selector:cssPath(e),html:clip(e.outerHTML,1500)}));
      const broken=[];for(const e of document.querySelectorAll('[aria-labelledby],[aria-describedby],[aria-controls]'))for(const attr of ['aria-labelledby','aria-describedby','aria-controls']){const value=(e.getAttribute(attr)||'').trim();for(const id of value.split(/\s+/).filter(Boolean))if(!document.getElementById(id))broken.push({attribute:attr,id,selector:cssPath(e),tag:e.tagName,role:e.getAttribute('role'),html:clip(e.outerHTML)});}
      const headings=[...document.querySelectorAll('h1,h2,h3,h4,h5,h6')].filter(visible).map(e=>({level:+e.tagName.slice(1),text:e.textContent.trim().slice(0,250),selector:cssPath(e),html:clip(e.outerHTML,1500)}));
      const skips=[...document.querySelectorAll('.fr-skiplinks a,a[href^="#"]')].filter(e=>e.closest('.fr-skiplinks')||/contenu/i.test(e.textContent)).map(e=>{const href=e.getAttribute('href')||'';let target=false;try{target=href.startsWith('#')&&href.length>1&&!!document.querySelector(href)}catch{}return{text:e.textContent.trim(),href,target,selector:cssPath(e),html:clip(e.outerHTML)}});
      const englishWords=/\b(the|and|or|of|to|for|with|from|close|open|next|previous|submit|cancel|search|download|help|settings|menu|content|page|your|is|are)\b/gi;
      const languageCandidates=[...document.querySelectorAll('body *')].filter(e=>visible(e)&&([...e.childNodes].some(n=>n.nodeType===3&&n.textContent.trim())||e.hasAttribute('aria-label')||e.hasAttribute('title')));
      const languageChanges=languageCandidates.map(e=>{const ownText=[...e.childNodes].filter(n=>n.nodeType===3).map(n=>n.textContent||'').join(' '),value=(e.getAttribute('aria-label')||e.getAttribute('title')||ownText).trim(),lang=(e.closest('[lang]')?.getAttribute('lang')||'').toLowerCase(),matches=value.match(englishWords)||[];return{value,lang,matches:matches.length,selector:cssPath(e),html:clip(e.outerHTML)}}).filter(x=>x.matches>=2&&!x.lang.startsWith('en'));
      const presentationNames=['align','alink','background','bgcolor','border','cellpadding','cellspacing','char','charoff','clear','color','compact','frameborder','hspace','link','marginheight','marginwidth','text','valign','vlink','vspace'],dimensionAllowed=new Set(['img','object','embed','canvas','svg']);
      const dimensionAllowedOn=e=>dimensionAllowed.has(e.tagName.toLowerCase())||(e.tagName.toLowerCase()==='source'&&e.parentElement?.tagName.toLowerCase()==='picture');
      const sourceDimensionMetadata=[...document.querySelectorAll('picture > source[width],picture > source[height]')].map(e=>({selector:cssPath(e),width:e.getAttribute('width'),height:e.getAttribute('height'),html:clip(e.outerHTML)}));
      const decorativeSvgIssues=[...document.querySelectorAll('svg[aria-hidden="true"]')].filter(e=>(e.getAttribute('aria-label')||'').trim()||(e.getAttribute('aria-labelledby')||'').trim()||(e.getAttribute('title')||'').trim()||e.querySelector('title')).map(e=>({selector:cssPath(e),html:clip(e.outerHTML)}));
      const emptyPresentation=[...document.querySelectorAll('p:empty')].filter(e=>{const s=getComputedStyle(e),r=e.getBoundingClientRect();return e.getClientRects().length&&(r.height>0||parseFloat(s.minHeight)>0||parseFloat(s.paddingTop)>0||parseFloat(s.paddingBottom)>0)}).map(e=>({selector:cssPath(e),html:clip(e.outerHTML),style:{margin:getComputedStyle(e).margin,padding:getComputedStyle(e).padding,minHeight:getComputedStyle(e).minHeight}}));
      const radioGroupIssues=[];const radioNames=[...new Set([...document.querySelectorAll('input[type="radio"][name]')].map(e=>e.name))];for(const name of radioNames){const radios=[...document.querySelectorAll(`input[type="radio"][name="${CSS.escape(name)}"]`)];if(radios.length<2)continue;const groups=[...new Set(radios.map(e=>e.closest('fieldset,[role="group"],[role="radiogroup"]')))].filter(Boolean);if(groups.length!==1||radios.some(e=>!e.closest('fieldset,[role="group"],[role="radiogroup"]')))radioGroupIssues.push({name,count:radios.length,selector:radios.map(cssPath).join(', '),html:radios.map(e=>clip(e.outerHTML)).join('\n')});}
      const presentationalTags=[...document.querySelectorAll('basefont,big,blink,center,font,marquee,s,strike,tt')].map(e=>({tag:e.tagName.toLowerCase(),selector:cssPath(e),html:clip(e.outerHTML)}));
      const fieldsetsWithoutLegend=[...document.querySelectorAll('fieldset')].filter(e=>{const legend=[...e.children].find(x=>x.tagName.toLowerCase()==='legend');return !legend||!(legend.textContent||'').trim()}).map(e=>({selector:cssPath(e),html:clip(e.outerHTML)}));
      const presentationalAttributes=[];for(const e of document.querySelectorAll('*')){const tag=e.tagName.toLowerCase(),attributes=[];for(const name of presentationNames)if(e.hasAttribute(name))attributes.push({name,value:e.getAttribute(name)});if(e.hasAttribute('size')&&tag!=='select')attributes.push({name:'size',value:e.getAttribute('size')});for(const name of ['width','height'])if(e.hasAttribute(name)&&!dimensionAllowedOn(e))attributes.push({name,value:e.getAttribute(name)});if(attributes.length)presentationalAttributes.push({tag,attributes,selector:cssPath(e),html:clip(e.outerHTML)});}
      return {doctype:document.doctype?.name||'',doctypePublic:document.doctype?.publicId||'',doctypeSystem:document.doctype?.systemId||'',doctypeBeforeHtml:!!document.doctype&&!!document.documentElement&&!!(document.doctype.compareDocumentPosition(document.documentElement)&Node.DOCUMENT_POSITION_FOLLOWING),lang:document.documentElement.lang,title:document.title,languageChanges,
        images:[...document.querySelectorAll('img')].filter(e=>!e.hasAttribute('alt')).map(e=>({selector:cssPath(e),html:clip(e.outerHTML)})),
        iframes:[...document.querySelectorAll('iframe')].filter(e=>!(e.getAttribute('title')||'').trim()).map(e=>({selector:cssPath(e),html:clip(e.outerHTML)})),
        emptyLinks:[...document.querySelectorAll('a[href]')].filter(e=>{const s=getComputedStyle(e);return s.display!=='none'&&s.visibility!=='hidden'&&!(e.textContent||'').trim()&&!(e.getAttribute('aria-label')||'').trim()&&!(e.getAttribute('title')||'').trim()&&!e.querySelector('img[alt]:not([alt=""])')}).map(e=>({selector:cssPath(e),html:clip(e.outerHTML)})),
        fields:[...document.querySelectorAll('input,select,textarea')].filter(e=>visible(e)&&!['hidden','submit','button','reset','image'].includes(e.type)&&!labelled(e)).map(e=>({selector:cssPath(e),html:clip(e.outerHTML)})),
        duplicate,invalidAnchorTypes,labelsBroken,broken,headings,skips,decorativeSvgIssues,emptyPresentation,radioGroupIssues,presentationalTags,presentationalAttributes,sourceDimensionMetadata,fieldsetsWithoutLegend,banners:[...document.querySelectorAll('header,[role=banner]')].filter(e=>visible(e)&&(e.getAttribute('role')==='banner'||!e.closest('article,aside,main,nav,section'))).map(e=>({selector:cssPath(e),html:clip(e.outerHTML,1800)}))};
    }""")
    await page.screenshot(path=str(attempt_root / "desktop.png"), full_page=False)
    keyboard = []
    for tab in range(1, tabs + 1):
        await page.keyboard.press("Tab")
        state = await page.evaluate(
            r"""tab=>{const e=document.activeElement;if(!e)return null;const clip=(v,n=1800)=>String(v||'').slice(0,n);const css=e=>e.id?`#${CSS.escape(e.id)}`:e.tagName.toLowerCase()+[...e.classList].slice(0,2).map(c=>`.${CSS.escape(c)}`).join('');const hidden=e.closest('[aria-hidden="true"]');return{tab,selector:css(e),html:clip(e.outerHTML),insideAriaHidden:!!hidden,hiddenHtml:hidden?clip(hidden.outerHTML):''}}""",
            tab,
        )
        if state:
            keyboard.append(state)
    await page.set_viewport_size({"width": 320, "height": 800})
    await page.wait_for_timeout(150)
    reflow = await page.evaluate(
        "() => ({viewport:innerWidth,scrollWidth:document.documentElement.scrollWidth})"
    )
    await context.close()

    signals: list[dict[str, Any]] = []
    passes = []

    def add(
        rule_id: str,
        instance: int,
        selector: str,
        observed: str,
        code: str,
        origin: str,
        assertions: list[str],
        status: str = "FAIL_CANDIDATE",
    ) -> None:
        signals.append(
            signal(
                pid,
                len(signals) + 1,
                rule_id,
                instance,
                selector,
                observed,
                code,
                origin,
                assertions,
                evidence_files,
                status,
            )
        )

    for index, item in enumerate(raw["images"], 1):
        add(
            "RGAA-1-1-IMAGE-ALT-001",
            index,
            item["selector"],
            "Attribut alt absent",
            item["html"],
            "RENDERED_DOM",
            ["img ne possède pas d’attribut alt."],
        )
    for index, item in enumerate(raw["decorativeSvgIssues"], 1):
        add(
            "RGAA-1-2-DECORATIVE-SVG-002",
            index,
            item["selector"],
            "SVG aria-hidden=true avec mécanisme de nommage",
            item["html"],
            "RENDERED_DOM",
            ["La racine décorative conserve un nom accessible potentiel."],
        )
    for index, item in enumerate(raw["iframes"], 1):
        add(
            "RGAA-2-1-IFRAME-TITLE-001",
            index,
            item["selector"],
            "Attribut title absent",
            item["html"],
            "RENDERED_DOM",
            ["iframe ne possède pas de title non vide."],
        )
    for index, item in enumerate(raw["emptyLinks"], 1):
        add(
            "RGAA-6-2-LINK-NAME-001",
            index,
            item["selector"],
            "Nom accessible vide",
            item["html"],
            "RENDERED_DOM",
            ["Aucun texte, aria-label, title ou image alternative."],
        )
    dialog_broken = [
        item
        for item in raw["broken"]
        if item["attribute"] == "aria-labelledby" and item["tag"] in {"DIALOG"}
    ]
    for index, item in enumerate(dialog_broken, 1):
        add(
            "RGAA-7-1-DIALOG-NAME-001",
            index,
            item["selector"],
            f"aria-labelledby référence #{item['id']} absent",
            item["html"],
            "RENDERED_DOM",
            [f"La cible {item['id']} n’existe pas."],
        )
    relation_broken = [
        item
        for item in raw["broken"]
        if not (item["attribute"] == "aria-labelledby" and item["tag"] == "DIALOG")
    ]
    for index, item in enumerate(relation_broken, 1):
        add(
            "RGAA-7-1-ARIA-REFERENCE-002",
            index,
            item["selector"],
            f"{item['attribute']} référence #{item['id']} absent",
            item["html"],
            "RENDERED_DOM",
            [f"La cible {item['id']} n’existe pas."],
        )
    if raw["doctype"].lower() != "html":
        add(
            "RGAA-8-1-DOCTYPE-001",
            1,
            "document",
            "Doctype absent ou différent de html",
            f"<!doctype {raw['doctype']}>"
            if raw["doctype"]
            else "<!-- doctype absent -->",
            "RENDERED_DOM",
            ["document.doctype.name n’est pas html."],
        )
    if raw["doctype"].lower() != "html" or raw["doctypePublic"] or raw["doctypeSystem"]:
        add(
            "RGAA-8-1-DOCTYPE-VALID-002",
            1,
            "document",
            f"Doctype name={raw['doctype']!r}, publicId={raw['doctypePublic']!r}, systemId={raw['doctypeSystem']!r}",
            f"<!doctype {raw['doctype']}>",
            "RENDERED_DOM",
            ["Le doctype ne correspond pas à la déclaration HTML5 attendue."],
        )
    if not raw["doctypeBeforeHtml"]:
        add(
            "RGAA-8-1-DOCTYPE-POSITION-003",
            1,
            "document",
            "Le doctype ne précède pas html",
            "<!-- ordre des nœuds racine invalide -->",
            "RENDERED_DOM",
            ["Le doctype n’est pas situé avant l’élément html."],
        )
    for index, group in enumerate(raw["duplicate"], 1):
        add(
            "RGAA-8-2-ID-UNIQUE-001",
            index,
            ", ".join(x["selector"] for x in group["instances"]),
            f"id={group['id']} présent {len(group['instances'])} fois",
            "\n\n".join(x["html"] for x in group["instances"]),
            "RENDERED_DOM",
            [f"L’identifiant {group['id']} n’est pas unique."],
        )
    for index, item in enumerate(raw["invalidAnchorTypes"], 1):
        add(
            "RGAA-8-2-ANCHOR-TYPE-002",
            index,
            item["selector"],
            f"type={item['value']!r} n’est pas un type MIME valide sur a",
            item["html"],
            "RENDERED_DOM",
            [
                "La valeur de type ne respecte pas la syntaxe type/sous-type d’un type MIME."
            ],
        )
    if not raw["lang"].strip():
        add(
            "RGAA-8-3-DOCUMENT-LANG-001",
            1,
            "html",
            "Attribut lang vide",
            "<html>",
            "RENDERED_DOM",
            ["La langue principale n’est pas déclarée."],
        )
    if not raw["title"].strip():
        add(
            "RGAA-8-5-DOCUMENT-TITLE-001",
            1,
            "title",
            "Title vide",
            "<title></title>",
            "RENDERED_DOM",
            ["Le titre de page est vide."],
        )
    for index, item in enumerate(raw["languageChanges"], 1):
        add(
            "RGAA-8-7-LANGUAGE-CHANGE-001",
            index,
            item["selector"],
            f"Intitulé anglais sans lang=en : {item['value']}",
            item["html"],
            "RENDERED_DOM",
            ["Un changement de langue probable n’est pas indiqué dans le DOM rendu."],
            "A_CONFIRMER",
        )
    for index, item in enumerate(raw["emptyPresentation"], 1):
        add(
            "RGAA-8-9-EMPTY-PRESENTATION-001",
            index,
            item["selector"],
            f"Paragraphe vide avec marge {item['style']['margin']}",
            item["html"],
            "MEASUREMENTS",
            [
                "Un paragraphe vide produit un espacement visible via ses styles calculés."
            ],
        )
    if not any(x["level"] == 1 for x in raw["headings"]):
        add(
            "RGAA-9-1-HEADING-H1-001",
            1,
            "h1",
            "Aucun h1 visible détecté",
            "<!-- aucun h1 visible -->",
            "RENDERED_DOM",
            ["Le titre principal n’est pas matérialisé par un h1 visible."],
        )
    previous = None
    order_index = 0
    for item in raw["headings"]:
        if previous is not None and item["level"] > previous + 1:
            order_index += 1
            add(
                "RGAA-9-1-HEADING-ORDER-002",
                order_index,
                item["selector"],
                f"Passage de h{previous} à h{item['level']}",
                item["html"],
                "RENDERED_DOM",
                ["Saut de niveau détecté ; cohérence éditoriale à confirmer."],
                "A_CONFIRMER",
            )
        previous = item["level"]
    for index, item in enumerate(raw["presentationalTags"], 1):
        add(
            "RGAA-10-1-PRESENTATIONAL-TAG-001",
            index,
            item["selector"],
            f"Balise de présentation <{item['tag']}> présente",
            item["html"],
            "RENDERED_DOM",
            ["Une balise de présentation est présente dans le code source généré."],
        )
    for index, item in enumerate(raw["presentationalAttributes"], 1):
        attrs = ", ".join(
            f"{entry['name']}={entry['value']!r}" for entry in item["attributes"]
        )
        add(
            "RGAA-10-1-PRESENTATIONAL-ATTRIBUTE-002",
            index,
            item["selector"],
            f"Attributs de présentation sur <{item['tag']}> : {attrs}",
            item["html"],
            "RENDERED_DOM",
            ["Un attribut de présentation est présent hors exception du test 10.1.2."],
        )
    hidden = [x for x in keyboard if x["insideAriaHidden"]]
    for index, item in enumerate(hidden, 1):
        code = item["html"] + "\n\nAncêtre masqué:\n" + item["hiddenHtml"]
        add(
            "RGAA-7-1-SCRIPT-ARIA-HIDDEN-003",
            index,
            item["selector"],
            f"Contrôle scripté focalisé à la tabulation {item['tab']} sous aria-hidden=true",
            code,
            "KEYBOARD_TRACE",
            [
                "Le composant scripté visible ne restitue pas correctement ce contrôle aux API d’accessibilité."
            ],
        )
        add(
            "RGAA-10-8-HIDDEN-FOCUS-001",
            index,
            item["selector"],
            f"Focus atteint à la tabulation {item['tab']} sous aria-hidden=true",
            code,
            "KEYBOARD_TRACE",
            ["L’élément actif appartient à un ancêtre aria-hidden=true."],
        )
    if reflow["scrollWidth"] > reflow["viewport"]:
        add(
            "RGAA-10-11-REFLOW-001",
            1,
            "html",
            json.dumps(reflow),
            f"<!-- viewport={reflow['viewport']}, scrollWidth={reflow['scrollWidth']} -->",
            "MEASUREMENTS",
            ["scrollWidth dépasse 320 CSS pixels."],
        )
    for index, item in enumerate(raw["fields"], 1):
        add(
            "RGAA-11-1-FIELD-LABEL-001",
            index,
            item["selector"],
            "Champ visible sans nom accessible",
            item["html"],
            "RENDERED_DOM",
            ["Aucun label, aria-label, title ou aria-labelledby résolu."],
        )
    for index, item in enumerate(raw["labelsBroken"], 1):
        add(
            "RGAA-11-1-LABEL-FOR-002",
            index,
            item["selector"],
            f"label for={item['for']!r} sans champ correspondant",
            item["html"],
            "RENDERED_DOM",
            ["La valeur de for ne résout aucun identifiant de champ."],
        )
    for index, item in enumerate(raw["radioGroupIssues"], 1):
        add(
            "RGAA-11-5-RADIO-GROUP-001",
            index,
            item["selector"],
            f"Groupe radio {item['name']} réparti hors d’un regroupement unique",
            item["html"],
            "RENDERED_DOM",
            ["Les boutons radio de même nom ne partagent pas un groupe unique."],
        )
    for index, item in enumerate(raw["fieldsetsWithoutLegend"], 1):
        add(
            "RGAA-11-6-FIELDSET-LEGEND-002",
            index,
            item["selector"],
            "Fieldset sans légende directe non vide",
            item["html"],
            "RENDERED_DOM",
            ["Aucun élément legend direct et non vide n’est présent."],
        )
    invalid = [
        x for x in raw["skips"] if "contenu" in x["text"].lower() and not x["target"]
    ]
    for index, item in enumerate(invalid, 1):
        add(
            "RGAA-12-7-SKIPLINK-001",
            index,
            item["selector"],
            f"{item['href']} ne cible aucun élément",
            item["html"],
            "RENDERED_DOM",
            ["Le fragment du lien d’évitement est sans cible."],
        )

    axe_result = load_axe_result(root, pid)
    axe_mapping = load_axe_mapping()
    axe_candidates: list[dict[str, Any]] = []
    existing_signal_keys = {(item["rule_id"], item["selector"]) for item in signals}
    if axe_result.get("status") == "collected":
        for violation in axe_result.get("violations", []):
            axe_id = str(violation.get("id", ""))
            mapping = axe_mapping.get(axe_id, {})
            rule_ids = mapping.get("rule_ids", []) if isinstance(mapping, dict) else []
            for rule_id in rule_ids:
                if rule_id not in RULES:
                    continue
                for instance, node in enumerate(violation.get("nodes", []), 1):
                    targets_for_node = node.get("target", [])
                    selector = " ".join(
                        str(target) for target in targets_for_node
                    ) or "document"
                    key = (rule_id, selector)
                    axe_candidates.append(
                        {
                            "axe_id": axe_id,
                            "rule_id": rule_id,
                            "selector": selector,
                            "instance": instance,
                            "deduplicated": key in existing_signal_keys,
                        }
                    )
                    if key in existing_signal_keys:
                        continue
                    observed = str(
                        violation.get(
                            "help", violation.get("description", axe_id)
                        )
                    )
                    observed_code = str(
                        node.get("html", "<!-- cible axe-core non fournie -->")
                    )
                    add(
                        rule_id,
                        instance,
                        selector,
                        f"Violation axe-core {axe_id} : {observed}",
                        observed_code,
                        "AXE_RESULT",
                        [
                            f"axe-core a signalé la règle {axe_id} ; qualification RGAA humaine requise."
                        ],
                    )
                    existing_signal_keys.add(key)

    targets = {
        "RGAA-1-1-IMAGE-ALT-001": len(raw["images"]),
        "RGAA-1-2-DECORATIVE-SVG-002": len(raw["decorativeSvgIssues"]),
        "RGAA-2-1-IFRAME-TITLE-001": len(raw["iframes"]),
        "RGAA-6-2-LINK-NAME-001": len(raw["emptyLinks"]),
        "RGAA-7-1-DIALOG-NAME-001": len(dialog_broken),
        "RGAA-7-1-ARIA-REFERENCE-002": len(relation_broken),
        "RGAA-7-1-SCRIPT-ARIA-HIDDEN-003": len(keyboard),
        "RGAA-8-1-DOCTYPE-001": 1,
        "RGAA-8-1-DOCTYPE-VALID-002": 1,
        "RGAA-8-1-DOCTYPE-POSITION-003": 1,
        "RGAA-8-2-ID-UNIQUE-001": len(raw["duplicate"]),
        "RGAA-8-2-ANCHOR-TYPE-002": len(raw["invalidAnchorTypes"]),
        "RGAA-8-3-DOCUMENT-LANG-001": 1,
        "RGAA-8-5-DOCUMENT-TITLE-001": 1,
        "RGAA-8-7-LANGUAGE-CHANGE-001": len(raw["languageChanges"]),
        "RGAA-8-9-EMPTY-PRESENTATION-001": len(raw["emptyPresentation"]),
        "RGAA-9-1-HEADING-H1-001": len(raw["headings"]),
        "RGAA-9-1-HEADING-ORDER-002": len(raw["headings"]),
        "RGAA-10-1-PRESENTATIONAL-TAG-001": 1,
        "RGAA-10-1-PRESENTATIONAL-ATTRIBUTE-002": max(
            1,
            len(raw["presentationalAttributes"]) + len(raw["sourceDimensionMetadata"]),
        ),
        "RGAA-10-8-HIDDEN-FOCUS-001": len(keyboard),
        "RGAA-10-11-REFLOW-001": 1,
        "RGAA-11-1-FIELD-LABEL-001": len(raw["fields"]),
        "RGAA-11-1-LABEL-FOR-002": len(raw["labelsBroken"]),
        "RGAA-11-5-RADIO-GROUP-001": len(raw["radioGroupIssues"]),
        "RGAA-11-6-FIELDSET-LEGEND-002": len(raw["fieldsetsWithoutLegend"]),
        "RGAA-12-7-SKIPLINK-001": len(raw["skips"]),
    }
    failed_rules = {x["rule_id"] for x in signals}
    for rule_id in RULES:
        status = (
            "FAIL_CANDIDATE"
            if rule_id in failed_rules
            else (
                "NON_APPLICABLE_CANDIDAT"
                if targets.get(rule_id, 0) == 0
                else "PASS_CANDIDATE"
            )
        )
        passes.append(
            {
                "rule_id": rule_id,
                "criterion": RULES[rule_id]["criterion"],
                "test": RULES[rule_id]["test"],
                "signal_status": status,
                "targets_observed": targets.get(rule_id, 0),
            }
        )
    dump(attempt_root / "raw-dom.json", raw)
    result = {
        "schema_version": 1,
        "page": page_info,
        "audited_at": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"),
        "rules_executed": sorted(RULES),
        "signals": signals,
        "passes": passes,
        "axe_core": {
            "status": axe_result.get("status", "absent"),
            "source": axe_result.get("source"),
            "mapped_candidates": axe_candidates,
            "unmapped_violations": [
                str(item.get("id", ""))
                for item in axe_result.get("violations", [])
                if not (
                    axe_mapping.get(str(item.get("id", "")), {}) or {}
                ).get("rule_ids")
            ],
        },
        "evidence": {
            "attempt": attempt,
            "raw": raw_path,
            "screenshot": screenshot_path,
        },
        "limits": [
            "Les signaux automatiques ne sont pas des décisions RGAA.",
            "La pertinence éditoriale, les états non exercés, les documents, médias et lecteurs d’écran réels restent humains.",
            "Le code cité est le DOM rendu, pas nécessairement le fichier source du dépôt.",
        ],
    }
    dump(attempt_root / "evidence.json", result)
    dump(root / "rgaa/pages" / f"{pid}.json", result)
    return result


async def main(config_path: Path) -> int:
    config = json.loads(config_path.read_text(encoding="utf-8"))
    root = Path(config.pop("_campaign_root")).resolve()
    (root / "rgaa/preuves").mkdir(parents=True, exist_ok=True)
    failures = []
    async with async_playwright() as p:
        browser = await p.chromium.launch(**browser_launch_options(config))
        for page in config["sample"]:
            try:
                result = await inspect_page(browser, page, config, root)
                print(f"{page['id']} {len(result['signals'])} signal(s)")
            except Exception as exc:
                failures.append({"page": page["id"], "error": str(exc)})
                print(f"{page['id']} ECHEC: {exc}", file=sys.stderr)
        await browser.close()
    dump(
        root / "logs/rgaa-checks-summary.json",
        {
            "failures": failures,
            "pages": len(config["sample"]),
            "rules": len(RULES),
            "browser_launch": browser_launch_summary(config),
        },
    )
    return 1 if failures else 0


if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit("Usage: rgaa_checks.py CAMPAIGN-RUNTIME.JSON")
    raise SystemExit(asyncio.run(main(Path(sys.argv[1]).resolve())))
