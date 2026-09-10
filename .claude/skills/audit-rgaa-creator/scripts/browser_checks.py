#!/usr/bin/env python3
"""Contrôles navigateur génériques d’une campagne creator RGAA.

Les sorties sont des mesures candidates, jamais des verdicts réglementaires.
"""
from __future__ import annotations

import asyncio
import json
import math
import os
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any

try:
    from playwright.async_api import async_playwright
except ImportError as exc:
    raise SystemExit("Playwright est absent de l’environnement Python sélectionné") from exc

from navigation import goto_checked


def dump(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


SEMANTIC_JS = r'''() => {
 const visible=e=>{const s=getComputedStyle(e),r=e.getBoundingClientRect();return s.display!=='none'&&s.visibility!=='hidden'&&r.width>0&&r.height>0};
 const label=e=>(e.labels?[...e.labels].map(x=>x.textContent.trim()).join(' '):'')||e.getAttribute('aria-label')||e.getAttribute('title')||'';
 const ids=[...document.querySelectorAll('[id]')].map(e=>e.id);
 const refs=[];for(const e of document.querySelectorAll('[aria-labelledby],[aria-describedby],[aria-controls]'))for(const a of ['aria-labelledby','aria-describedby','aria-controls'])for(const id of (e.getAttribute(a)||'').split(/\s+/).filter(Boolean))if(!document.getElementById(id))refs.push({attribute:a,id,element:e.outerHTML.slice(0,300)});
 return {
  url:location.href,title:document.title,lang:document.documentElement.lang,doctype:document.doctype?.name||'',
  headings:[...document.querySelectorAll('h1,h2,h3,h4,h5,h6')].filter(visible).map(e=>({level:+e.tagName[1],text:e.textContent.trim().replace(/\s+/g,' ').slice(0,180)})),
  images:[...document.images].map(e=>({src:e.currentSrc||e.src,alt:e.getAttribute('alt'),role:e.getAttribute('role'),visible:visible(e)})),
  iframes:[...document.querySelectorAll('iframe,frame')].map(e=>({tag:e.tagName,src:e.src,title:e.title,visible:visible(e)})),
  links:{total:document.links.length,empty:[...document.links].filter(e=>visible(e)&&!(e.innerText||e.getAttribute('aria-label')||e.title||e.querySelector('img[alt]:not([alt=""])'))).map(e=>({href:e.href,html:e.outerHTML.slice(0,300)})),fragmentsWithoutTarget:[...document.querySelectorAll('a[href^="#"]')].filter(e=>{const h=e.getAttribute('href');if(!h||h==='#')return true;try{return !document.querySelector(h)}catch{return true}}).map(e=>({text:e.textContent.trim(),href:e.getAttribute('href')}))},
  lists:[...document.querySelectorAll('ul,ol,dl')].map(e=>({tag:e.tagName,items:e.matches('dl')?e.querySelectorAll(':scope>dt').length:e.querySelectorAll(':scope>li').length})),
  tables:[...document.querySelectorAll('table')].map(e=>({caption:e.caption?.textContent.trim()||'',headers:[...e.querySelectorAll('th')].map(x=>({text:x.textContent.trim(),scope:x.scope})),rows:e.rows.length})),
  forms:{fields:[...document.querySelectorAll('input,select,textarea')].filter(e=>e.type!=='hidden').map(e=>({id:e.id,name:e.name,type:e.type,visible:visible(e),label:label(e),autocomplete:e.getAttribute('autocomplete'),required:e.required,disabled:e.disabled})),groups:[...document.querySelectorAll('fieldset')].map(e=>({legend:e.querySelector(':scope>legend')?.textContent.trim()||'',visible:visible(e)}))},
  structure:{main:document.querySelectorAll('main,[role=main]').length,banner:document.querySelectorAll('[role=banner],body>header').length,navigation:document.querySelectorAll('nav,[role=navigation]').length,contentinfo:document.querySelectorAll('[role=contentinfo],body>footer').length,duplicateIds:[...new Set(ids.filter((id,i)=>ids.indexOf(id)!==i))],brokenAriaReferences:refs},
  media:[...document.querySelectorAll('audio,video,object,embed')].map(e=>({tag:e.tagName,autoplay:e.autoplay||false,controls:e.controls||false,src:e.currentSrc||e.src||e.data||''}))
 };
}'''

CONTRAST_JS = r'''() => {
 const parse=c=>{const m=c.match(/rgba?\((\d+)[ ,]+(\d+)[ ,]+(\d+)(?:[ ,/]+([\d.]+))?\)/);return m?[+m[1],+m[2],+m[3],m[4]===undefined?1:+m[4]]:null};
 const blend=(fg,bg)=>{const a=fg[3]+bg[3]*(1-fg[3]);return a?[0,1,2].map(i=>(fg[i]*fg[3]+bg[i]*bg[3]*(1-fg[3]))/a).concat(a):[255,255,255,1]};
 const bg=e=>{let stack=[],n=e;while(n){const s=getComputedStyle(n),c=parse(s.backgroundColor);if(c)stack.push(c);n=n.parentElement}let out=[255,255,255,1];for(let i=stack.length-1;i>=0;i--)out=blend(stack[i],out);return out};
 const lum=c=>{const v=c.slice(0,3).map(x=>{x/=255;return x<=.04045?x/12.92:Math.pow((x+.055)/1.055,2.4)});return .2126*v[0]+.7152*v[1]+.0722*v[2]};
 const vis=e=>{const s=getComputedStyle(e),r=e.getBoundingClientRect();return s.display!=='none'&&s.visibility!=='hidden'&&r.width>0&&r.height>0&&!e.closest(':disabled,[aria-disabled=true]')};
 const els=[...document.querySelectorAll('body *')].filter(e=>vis(e)&&[...e.childNodes].some(n=>n.nodeType===3&&n.textContent.trim())).slice(0,2500),failures=[];
 for(const e of els){const s=getComputedStyle(e),fg=parse(s.color),back=bg(e);if(!fg)continue;const f=blend(fg,back),ratio=(Math.max(lum(f),lum(back))+.05)/(Math.min(lum(f),lum(back))+.05),large=parseFloat(s.fontSize)>=24||(parseFloat(s.fontSize)>=18.66&&+s.fontWeight>=700),threshold=large?3:4.5;if(ratio+0.01<threshold)failures.push({tag:e.tagName,id:e.id,text:e.textContent.trim().replace(/\s+/g,' ').slice(0,100),ratio:+ratio.toFixed(2),threshold,color:s.color,background:back.map(x=>Math.round(x))})}
 return {tested:els.length,failures};
}'''

FOCUS_STYLE_JS = r'''e=>{const chain=[e,e.parentElement,e.parentElement?.parentElement].filter(Boolean);return chain.some(n=>{const s=getComputedStyle(n);return (s.outlineStyle!=='none'&&parseFloat(s.outlineWidth)>0)||s.boxShadow!=='none'})}'''

MAPPING_PATH = Path(__file__).resolve().parents[2] / "audit-rgaa-complet/references/axe-rgaa-mapping.json"


def resolve_axe_source() -> tuple[str | None, str]:
    """Résout axe-core sans installer de paquet pendant une campagne."""
    candidates: list[Path] = []
    configured = os.environ.get("AXE_CORE_PATH", "").strip()
    if configured:
        candidates.append(Path(configured).expanduser())
    package = os.environ.get("AXE_CORE_PACKAGE", "").strip()
    if package:
        candidates.append(Path(package).expanduser() / "axe.min.js")
        candidates.append(Path(package).expanduser() / "axe.js")
    node = shutil.which("node")
    if node:
        result = subprocess.run(
            [node, "-e", "try { process.stdout.write(require.resolve('axe-core/axe.min.js')) } catch {}"],
            text=True, capture_output=True, check=False,
        )
        if result.stdout.strip():
            candidates.append(Path(result.stdout.strip()))
    npm = shutil.which("npm")
    if npm:
        result = subprocess.run([npm, "root", "-g"], text=True, capture_output=True, check=False)
        if result.returncode == 0 and result.stdout.strip():
            global_root = Path(result.stdout.strip())
            candidates.extend(global_root.glob("@*/**/axe-core/axe.min.js"))
            candidates.extend(global_root.glob("@*/**/axe-core/axe.js"))
    for candidate in candidates:
        if candidate.is_file():
            return candidate.read_text(encoding="utf-8"), str(candidate)
    return None, "axe-core absent : définir AXE_CORE_PATH ou AXE_CORE_PACKAGE"


async def page_checks(browser: Any, page_info: dict[str, Any], config: dict[str, Any], root: Path, axe_source: str | None, axe_source_name: str) -> None:
    pid, url = page_info["id"], page_info["url"]
    timeout = int(config.get("browser", {}).get("timeout_seconds", 30)) * 1000
    wait = int(config.get("browser", {}).get("wait_ms", 900))
    context = await browser.new_context(viewport={"width": 1280, "height": 720}, locale="fr-FR")
    page = await context.new_page(); await goto_checked(page, url, timeout); await page.wait_for_timeout(wait)
    semantic = await page.evaluate(SEMANTIC_JS); contrast = await page.evaluate(CONTRAST_JS)
    semantic["contrast"] = contrast
    axe_result: dict[str, Any]
    if axe_source:
        try:
            await page.add_script_tag(content=axe_source)
            axe_raw = await page.evaluate("async () => axe.run(document)")
            mapping = json.loads(MAPPING_PATH.read_text(encoding="utf-8")) if MAPPING_PATH.is_file() else {}
            axe_result = {
                "status": "collected",
                "engine": axe_raw.get("testEngine", {}),
                "source": axe_source_name,
                "violations": axe_raw.get("violations", []),
                "rgaa_candidates": [
                    {
                        "axe_id": violation.get("id"),
                        "rule_ids": mapping.get(violation.get("id"), {}).get("rule_ids", []),
                        "criteria": mapping.get(violation.get("id"), {}).get("criteria", []),
                        "status": "A_CONFIRMER",
                        "description": violation.get("description", ""),
                    }
                    for violation in axe_raw.get("violations", [])
                ],
            }
        except Exception as exc:
            axe_result = {"status": "failed", "source": axe_source_name, "reason": str(exc)}
    else:
        axe_result = {"status": "skipped", "source": axe_source_name, "reason": axe_source_name}
    dump(root / "inspections-approfondies" / f"{pid}.json", semantic)

    client = await context.new_cdp_session(page)
    ax = await client.send("Accessibility.getFullAXTree")
    nodes = ax.get("nodes", [])
    roles: dict[str, int] = {}
    unnamed = []
    for node in nodes:
        role = (node.get("role") or {}).get("value", "")
        if role: roles[role] = roles.get(role, 0) + 1
        name = (node.get("name") or {}).get("value", "")
        if role in {"button", "link", "textbox", "combobox", "checkbox", "radio"} and not name:
            unnamed.append({"role": role, "nodeId": node.get("nodeId")})
    dump(root / "analyses-skills" / f"{pid}.json", {"kind": "accessibility-tree-prequalification", "realScreenReader": False, "nodes": len(nodes), "roles": roles, "unnamedControls": unnamed})

    keyboard = []
    for i in range(int(config.get("browser", {}).get("tabs_per_page", 25))):
        await page.keyboard.press("Tab")
        loc = page.locator(":focus")
        if not await loc.count(): continue
        item = await loc.evaluate("e=>({tag:e.tagName,id:e.id,text:(e.textContent||e.value||e.getAttribute('aria-label')||'').trim().replace(/\\s+/g,' ').slice(0,100),insideAriaHidden:!!e.closest('[aria-hidden=true]')})")
        item["tab"] = i + 1; item["indicatorCandidate"] = await loc.evaluate(FOCUS_STYLE_JS); keyboard.append(item)
    dump(root / "interactions" / f"{pid}.json", {"keyboard": keyboard, "tabsRequested": int(config.get("browser", {}).get("tabs_per_page", 25)), "focusHeuristic": "élément ou deux ancêtres avec outline/box-shadow ; revue visuelle requise"})
    await context.close()

    mobile = await browser.new_context(viewport={"width": 320, "height": 720}, locale="fr-FR")
    p = await mobile.new_page(); await goto_checked(p, url, timeout); await p.wait_for_timeout(wait)
    reflow = await p.evaluate("() => ({viewport:innerWidth,scrollWidth:document.documentElement.scrollWidth,status:document.documentElement.scrollWidth>innerWidth?'review':'pass'})")
    autocomplete = []
    for field in semantic["forms"]["fields"]:
        if field["type"] in {"text", "email", "tel", "search", "textarea"}:
            autocomplete.append(field)
    tests = {
        "reflow": reflow,
        "spacing": {"status": "review", "reason": "État forcé et validation visuelle requis"},
        "zoom": {"status": "review", "reason": "Zoom navigateur et validation visuelle requis"},
        "orientation": {"status": "review", "reason": "Émulation portrait/paysage non exercée par le collecteur générique"},
        "autocomplete": {"status": "review" if autocomplete else "na", "fields": autocomplete},
        "time": {"status": "review", "reason": "Délais dynamiques à exercer"},
        "autoplay": {"status": "review" if semantic["media"] else "na", "media": semantic["media"]},
        "focus": {"status": "review", "tested": len(keyboard), "withoutIndicatorCandidate": [x for x in keyboard if not x["indicatorCandidate"]]},
        "target": {"status": "review", "reason": "Exceptions de taille et espacement à qualifier"},
    }
    dump(root / "tests-wcag" / f"{pid}.json", {"page": page_info, "tests": tests, "axe_core": axe_result})
    await mobile.close()


async def main(config_path: Path) -> int:
    config = json.loads(config_path.read_text(encoding="utf-8")); root = Path(config.pop("_campaign_root")).resolve()
    failures = []
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        axe_source, axe_source_name = resolve_axe_source()
        for page in config["sample"]:
            try:
                await page_checks(browser, page, config, root, axe_source, axe_source_name); print(f"{page['id']} OK")
            except Exception as exc:
                failures.append({"page": page["id"], "error": str(exc)}); print(f"{page['id']} ECHEC: {exc}", file=sys.stderr)
        await browser.close()
    dump(root / "logs/browser-checks-summary.json", {"failures": failures, "pages": len(config["sample"])})
    return 1 if failures else 0


if __name__ == "__main__":
    if len(sys.argv) != 2: raise SystemExit("Usage: browser_checks.py CAMPAIGN-RUNTIME.JSON")
    raise SystemExit(asyncio.run(main(Path(sys.argv[1]).resolve())))
