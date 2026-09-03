#!/usr/bin/env python3
"""Capture et vérifie génériquement les rapports assemblés d'une campagne."""
from __future__ import annotations
import argparse, asyncio, hashlib, json
from datetime import datetime, timezone
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlparse
import yaml

class Links(HTMLParser):
    def __init__(self): super().__init__(); self.ids=set(); self.hrefs=[]
    def handle_starttag(self, tag, attrs):
        values=dict(attrs)
        if values.get('id'): self.ids.add(values['id'])
        if tag == 'a' and values.get('href'): self.hrefs.append(values['href'])

def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()

def local_link_errors(path: Path) -> list[str]:
    parser=Links(); parser.feed(path.read_text(encoding='utf-8')); errors=[]
    for href in parser.hrefs:
        parsed=urlparse(href)
        if href.startswith('#'):
            if unquote(parsed.fragment) not in parser.ids: errors.append(f'ancre absente: {href}')
        elif not parsed.scheme and not parsed.netloc:
            target=(path.parent/unquote(parsed.path)).resolve()
            if not target.is_file(): errors.append(f'lien local absent: {href}')
    return errors

def discover(root: Path) -> tuple[dict, list[dict]]:
    campaign=yaml.safe_load((root/'campaign.yaml').read_text(encoding='utf-8'))
    build=json.loads((root/'rapport-dsfr/BUILD.json').read_text(encoding='utf-8'))
    outputs={entry['path'] for entry in build.get('outputs', [])}
    portal=root/'PORTAIL-AUDITS.html'
    if 'PORTAIL-AUDITS.html' not in outputs or not portal.is_file(): raise ValueError('BUILD.json ne référence pas le portail attendu.')
    reports=[{'key':'portal','type':'portal','path':portal,'page':None}]
    for page in campaign.get('sample', []):
        for report_type in ('rgaa','dsfr'):
            relative=f'{report_type}/pages-html/{page["id"]}.html'; path=root/relative
            if relative not in outputs or not path.is_file(): raise ValueError(f'BUILD.json ne référence pas {relative}.')
            reports.append({'key':f'{report_type}-{page["id"]}','type':report_type,'path':path,'page':page})
    return build,reports

async def inspect(browser, report: dict, width: int, height: int, screenshot: Path) -> dict:
    context=await browser.new_context(viewport={'width':width,'height':height},locale='fr-FR')
    page=await context.new_page(); await page.goto(report['path'].as_uri(),wait_until='networkidle')
    data=await page.evaluate("""()=>{const sample=document.querySelector('.audit-sample'),findings=[...document.querySelectorAll('.audit-finding')],tables=[...document.querySelectorAll('.fr-table__container')];return {title:document.title,h1:document.querySelector('h1')?.textContent.trim()||'',builder:!!document.querySelector('[data-audit-builder="dsfr-components"]'),innerWidth,scrollWidth:document.documentElement.scrollWidth,horizontalOverflow:document.documentElement.scrollWidth>innerWidth+1,urlFirst:!!sample&&sample.textContent.includes('URL auditée'),findings:findings.length,separators:document.querySelectorAll('hr.audit-finding-separator').length,details:document.querySelectorAll('details.audit-code').length,tables:tables.map(e=>({clientWidth:e.clientWidth,scrollWidth:e.scrollWidth,scrollable:e.scrollWidth>e.clientWidth}))}}""")
    errors=[]
    if not data['builder']: errors.append('marqueur builder absent')
    if report['page']:
        expected=f"{report['page']['id']} - {report['page']['name']} - audit {report['type'].upper()}"
        if data['title'] != expected or data['h1'] != expected: errors.append(f'titre/h1 inattendu: {data["title"]!r} / {data["h1"]!r}')
        if not data['urlFirst']: errors.append('URL auditée absente de l’identification initiale')
    interactions={}
    if report['type'] != 'portal':
        all_filter=page.locator('[data-audit-filter="all"]'); review_filter=page.locator('[data-audit-filter="review"]')
        if await all_filter.count() and await review_filter.count():
            interactions['allVisible']=await page.locator('.audit-finding:not([hidden])').count(); await review_filter.click(); interactions['reviewVisible']=await page.locator('.audit-finding:not([hidden])').count(); await all_filter.click()
        details=page.locator('details.audit-code').first
        if await details.count():
            await details.locator('summary').focus(); await page.keyboard.press('Enter'); interactions['detailsOpenByKeyboard']=await details.get_attribute('open') is not None
    data['interactions']=interactions; data['errors']=errors+local_link_errors(report['path']); data['source_sha256']=digest(report['path'])
    await page.screenshot(path=str(screenshot),full_page=True); await context.close(); return data

async def run(root: Path) -> dict:
    from playwright.async_api import async_playwright
    build,reports=discover(root); out=root/'rapport-dsfr/captures-validation'; out.mkdir(parents=True,exist_ok=True)
    result={'schema_version':1,'audited_at':datetime.now(timezone.utc).isoformat(timespec='seconds'),'build_sha256':digest(root/'rapport-dsfr/BUILD.json'),'reports':{}}
    async with async_playwright() as pw:
        browser=await pw.chromium.launch(headless=True)
        for report in reports:
            if report['type']=='portal':
                result['reports']['portal-desktop']=await inspect(browser,report,1440,1000,out/'portal-desktop.png'); result['reports']['portal-mobile']=await inspect(browser,report,390,844,out/'portal-mobile.png')
            else:
                result['reports'][report['key']]=await inspect(browser,report,1440,1000,out/f'{report["key"]}.png')
        await browser.close()
    errors=[f'{key}: {error}' for key,value in result['reports'].items() for error in value['errors']]
    result['errors']=errors; result['valid']=not errors
    (out/'REPORT-REVIEW.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    return result

def main():
    parser=argparse.ArgumentParser(); parser.add_argument('campaign_root',type=Path); parser.add_argument('--check',action='store_true'); args=parser.parse_args(); root=args.campaign_root.resolve()
    if args.check:
        _,reports=discover(root); errors=[error for report in reports for error in local_link_errors(report['path'])]
        if errors: raise SystemExit('\n'.join(errors))
        print(json.dumps({'reports':[report['key'] for report in reports],'valid':True},ensure_ascii=False)); return
    result=asyncio.run(run(root)); print(json.dumps(result,ensure_ascii=False,indent=2));
    if not result['valid']: raise SystemExit(1)
if __name__=='__main__': main()
