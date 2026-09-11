#!/usr/bin/env node
/*
 * Browser smoke for the interactive header/navigation variants
 * (header search/menu modals, navigation menu + mega-menu, translate dropdown).
 *
 * Generates the REAL fragments via generate_component.py (no shell — args are
 * passed directly through spawnSync, so French config strings are safe),
 * wraps them with local DSFR assets, and asserts runtime behaviour after DSFR
 * init: aria-expanded toggles, modal/collapse open classes, and a clean console.
 *
 * Viewport matters: fr-header__navbar (search/menu buttons) is mobile-only,
 * while fr-header__tools-links (translate) and fr-nav (menu/mega triggers)
 * are desktop-only. The check switches the page viewport between phases.
 *
 * Returns SKIPPED with exit code 2 when Playwright, Chromium, Python or the
 * cached DSFR package is unavailable — a named limit, not a browser PASS.
 */

const fs = require('fs');
const os = require('os');
const path = require('path');
const {
  cleanup,
  dsfrHeadTags,
  dsfrScriptTags,
  loadPlaywright,
  printSkipped,
  resolveDsfrPackage,
  runPython,
  startStaticServer,
  waitForDsfr,
} = require('./playwright_dsfr_helpers');

const GEN = path.join(__dirname, 'generate_component.py');
const MOBILE = { width: 375, height: 740 };
const DESKTOP = { width: 1280, height: 720 };
const STEP_TIMEOUT = 3000;

function generateFragment(component, config) {
  // spawnSync bypasses the shell: the JSON config is a single argv element,
  // so French labels and quoting are safe.
  return runPython([GEN, component, '--config', JSON.stringify(config)], { cwd: path.resolve(__dirname, '..') });
}

function wrapPage(fragment, dsfrPackage, origin, title) {
  return `<!doctype html>
<html lang="fr" data-fr-scheme="system">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>${title}</title>
  ${dsfrHeadTags(origin)}
</head>
<body>
  ${fragment}
  <main class="fr-container fr-py-4w" id="contenu">
    <h1>${title}</h1>
    <p>Contenu factice pour le contrôle navigateur.</p>
  </main>
  ${dsfrScriptTags(origin)}
</body>
</html>`;
}

async function attributeBecomes(locator, name, expected) {
  await locator.evaluate(
    (node, [attr, value]) => new Promise((resolve, reject) => {
      const check = () => {
        if (node.getAttribute(attr) === value) { resolve(true); return true; }
        return false;
      };
      if (check()) return;
      const observer = new MutationObserver(() => { if (check()) observer.disconnect(); });
      observer.observe(node, { attributes: true });
      setTimeout(() => { observer.disconnect(); reject(new Error(`${attr} n'a pas atteint ${value}`)); }, 3000);
    }),
    [name, expected]
  ).catch(() => {});
  return locator.getAttribute(name);
}

async function classBecomes(page, selector, className, present) {
  await page.waitForFunction(
    ([sel, cls, want]) => {
      const node = document.querySelector(sel);
      return Boolean(node) && node.classList.contains(cls) === want;
    },
    [selector, className, present],
    { timeout: STEP_TIMEOUT }
  ).catch(() => {});
  return page.locator(selector).evaluate((node, cls) => node.classList.contains(cls), className);
}

async function guardedWait(page, context) {
  try {
    await waitForDsfr(page);
    return true;
  } catch (err) {
    if (process.env.DSFR_INTERACTIVE_SKIP_ON_RUNTIME_LOAD === '1') {
      printSkipped('DSFR runtime could not load before timeout from local assets.', { ...context, detail: err.message });
      return false;
    }
    throw err;
  }
}

async function main() {
  const { loaded, error: playwrightError } = loadPlaywright();
  if (!loaded) {
    printSkipped(playwrightError || 'Playwright module not found in local node_modules or npx cache.');
    return;
  }
  const { dir: dsfrPackage, version: dsfrVersion, error: dsfrError } = resolveDsfrPackage();
  if (!dsfrPackage) {
    printSkipped(`${dsfrError}. Run check_generated_outputs.py --official-version 1.15.3 to seed the cache.`);
    return;
  }

  const headerResult = generateFragment('header', {
    service_title: 'Mon service',
    search: { label: 'Rechercher' },
    navigation: [
      { label: 'Accueil', href: '/', active: true },
      { label: 'Services', href: '/services' },
    ],
    languages: [
      { code: 'FR', label: 'Français', href: '/fr', active: true },
      { code: 'EN', label: 'English', href: '/en' },
    ],
  });
  const navResult = generateFragment('navigation', {
    items: [
      { label: 'Rubrique', children: [{ label: 'Sous-rubrique', href: '/sous' }] },
      { label: 'Démarches', categories: [{ label: 'Particuliers', href: '/p', items: [{ label: 'Santé', href: '/sante' }] }] },
    ],
  });
  for (const result of [headerResult, navResult]) {
    if (result.skip) {
      printSkipped(result.error, { dsfrPackage, dsfrVersion });
      return;
    }
    if (!result.ok) {
      console.log(JSON.stringify({ status: 'FAIL', phase: 'generation', error: result.error }, null, 2));
      process.exitCode = 1;
      return;
    }
  }

  const { playwright, version, source } = loaded;
  const context = { playwright: version, source, dsfrPackage, dsfrVersion };
  let tmpDir = null;
  let server = null;
  let browser = null;
  const steps = [
    async () => { if (browser) await browser.close(); },
    async () => { if (server) await server.close(); },
    async () => { if (tmpDir) fs.rmSync(tmpDir, { recursive: true, force: true }); },
  ];
  try {
    tmpDir = fs.mkdtempSync(path.join(os.tmpdir(), 'dsfr-header-nav-'));
    server = await startStaticServer([
      { prefix: '/pages/', root: tmpDir },
      { prefix: '/dsfr/', root: path.join(dsfrPackage, 'dist') },
    ]);
    fs.writeFileSync(path.join(tmpDir, 'header.html'), wrapPage(headerResult.stdout, dsfrPackage, server.origin, 'Smoke en-tête'), 'utf8');
    fs.writeFileSync(path.join(tmpDir, 'nav.html'), wrapPage(navResult.stdout, dsfrPackage, server.origin, 'Smoke navigation'), 'utf8');

    try {
      browser = await playwright.chromium.launch({ headless: true });
    } catch (err) {
      printSkipped('Playwright chromium could not launch. Run `npx playwright install chromium` to enable this check.', { ...context, detail: err.message });
      return;
    }
    const browserContext = await browser.newContext();
    const page = await browserContext.newPage();
    const errors = [];
    page.on('console', (message) => {
      if (message.type() === 'error') errors.push(message.text());
    });
    page.on('pageerror', (err) => errors.push(err.message));

    const checks = {};
    // --- Header at MOBILE viewport : search + menu navbar buttons ---
    await page.setViewportSize(MOBILE);
    await page.goto(`${server.origin}/pages/header.html`, { waitUntil: 'domcontentloaded' });
    if (!(await guardedWait(page, context))) return;

    // Header navbar modal buttons carry data-fr-opened + aria-controls (no
    // aria-expanded: they open a modal, not a disclosure). The proof is the
    // modal opening then closing on the Fermer button.
    await page.locator('#header-search-button').click();
    checks.searchModalOpened = await classBecomes(page, '#header-search', 'fr-modal--opened', true);
    await page.locator('#header-search .fr-btn--close').click();
    checks.searchModalClosed = !(await classBecomes(page, '#header-search', 'fr-modal--opened', false));

    await page.locator('#header-menu-button').click();
    checks.menuModalOpened = await classBecomes(page, '#header-menu', 'fr-modal--opened', true);
    await page.locator('#header-menu .fr-btn--close').click();
    checks.menuModalClosed = !(await classBecomes(page, '#header-menu', 'fr-modal--opened', false));

    // --- Header at DESKTOP viewport : translate (fr-header__tools-links) ---
    await page.setViewportSize(DESKTOP);
    await page.goto(`${server.origin}/pages/header.html`, { waitUntil: 'domcontentloaded' });
    if (!(await guardedWait(page, context))) return;
    // Scope to the tools-links instance: DSFR duplicates the translate button
    // into the mobile menu modal (fr-header__menu-links).
    const translateButton = page.locator('.fr-header__tools-links .fr-translate__btn');
    checks.translateBefore = await translateButton.getAttribute('aria-expanded');
    await translateButton.click();
    checks.translateAfter = await attributeBecomes(translateButton, 'aria-expanded', 'true');
    checks.translateOpened = await classBecomes(page, '#header-translate-menu', 'fr-collapse--expanded', true);
    checks.translateLinksHaveLang = await page.locator('#header-translate-menu .fr-translate__language').evaluateAll(
      (nodes) => nodes.length > 0 && nodes.every((node) => node.getAttribute('hreflang') && node.getAttribute('lang'))
    );

    // --- Navigation at DESKTOP viewport : menu + mega-menu ---
    await page.goto(`${server.origin}/pages/nav.html`, { waitUntil: 'domcontentloaded' });
    if (!(await guardedWait(page, context))) return;
    // Les déclencheurs sont identifiés par la nature de leur cible, pas par leur rang.
    const buttons = await page.locator('.fr-nav__btn').evaluateAll((nodes) => nodes.map((node) => {
      const target = document.getElementById(node.getAttribute('aria-controls'));
      return { id: node.getAttribute('aria-controls'), mega: Boolean(target && target.classList.contains('fr-mega-menu')), menu: Boolean(target && target.classList.contains('fr-menu')) };
    }));
    const menuTarget = buttons.find((item) => item.menu && !item.mega);
    const megaTarget = buttons.find((item) => item.mega);
    checks.menuTargetIsMenu = Boolean(menuTarget);
    checks.megaTargetIsMegaMenu = Boolean(megaTarget);
    if (menuTarget) {
      const button = page.locator(`.fr-nav__btn[aria-controls="${menuTarget.id}"]`);
      checks.navMenuBefore = await button.getAttribute('aria-expanded');
      await button.click();
      checks.navMenuAfter = await attributeBecomes(button, 'aria-expanded', 'true');
      checks.navMenuOpened = await classBecomes(page, `#${menuTarget.id}`, 'fr-collapse--expanded', true);
    }
    if (megaTarget) {
      const button = page.locator(`.fr-nav__btn[aria-controls="${megaTarget.id}"]`);
      checks.megaBefore = await button.getAttribute('aria-expanded');
      await button.click();
      checks.megaAfter = await attributeBecomes(button, 'aria-expanded', 'true');
      checks.megaCollapseOpened = await classBecomes(page, `#${megaTarget.id}`, 'fr-collapse--expanded', true);
    }

    const pass = checks.searchModalOpened === true
      && checks.searchModalClosed === true
      && checks.menuModalOpened === true
      && checks.menuModalClosed === true
      && checks.translateBefore === 'false'
      && checks.translateAfter === 'true'
      && checks.translateOpened === true
      && checks.translateLinksHaveLang === true
      && checks.menuTargetIsMenu === true
      && checks.megaTargetIsMegaMenu === true
      && checks.navMenuBefore === 'false'
      && checks.navMenuAfter === 'true'
      && checks.navMenuOpened === true
      && checks.megaBefore === 'false'
      && checks.megaAfter === 'true'
      && checks.megaCollapseOpened === true
      && errors.length === 0;

    console.log(JSON.stringify({
      status: pass ? 'PASS' : 'FAIL',
      ...context,
      checks,
      consoleErrors: errors,
    }, null, 2));
    process.exitCode = pass ? 0 : 1;
  } finally {
    await cleanup(steps);
  }
}

main().catch((err) => {
  // Sortie standard analysable même sur exception ; la pile va sur stderr.
  console.log(JSON.stringify({ status: 'ERROR', reason: err && err.message ? err.message : String(err) }, null, 2));
  console.error(err && err.stack ? err.stack : err);
  process.exitCode = 1;
});
