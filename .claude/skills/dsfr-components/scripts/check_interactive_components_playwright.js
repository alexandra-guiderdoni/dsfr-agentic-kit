#!/usr/bin/env node
/*
 * Browser smoke for DSFR interactive components, on the fragments REALLY
 * produced by generate_component.py (accordion, tabs, modal, display): a
 * regression of a generator is caught here, not masked by a hand-written
 * fixture. Returns SKIPPED with exit code 2 when Playwright, Chromium, Python
 * or the cached DSFR package is unavailable.
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
const STEP_TIMEOUT = 3000;

function generateFragment(component, config) {
  const args = [GEN, component];
  if (config) args.push('--config', JSON.stringify(config));
  return runPython(args, { cwd: path.resolve(__dirname, '..') });
}

function pageHtml(fragments, dsfrPackage, origin) {
  return `<!doctype html>
<html lang="fr" data-fr-scheme="system">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Smoke composants interactifs DSFR</title>
  ${dsfrHeadTags(origin)}
</head>
<body>
  <main class="fr-container fr-py-4w">
    <h1>Smoke composants interactifs DSFR</h1>
    ${fragments.join('\n    ')}
  </main>
  ${dsfrScriptTags(origin)}
</body>
</html>`;
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

async function attributeBecomes(page, selector, name, expected) {
  await page.waitForFunction(
    ([sel, attr, value]) => {
      const node = document.querySelector(sel);
      return Boolean(node) && node.getAttribute(attr) === value;
    },
    [selector, name, expected],
    { timeout: STEP_TIMEOUT }
  ).catch(() => {});
  return page.locator(selector).getAttribute(name);
}

async function isDialogOpen(page, selector) {
  return page.locator(selector).evaluate((node) => node.hasAttribute('open') || node.classList.contains('fr-modal--opened'));
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

  const generated = [
    generateFragment('accordion', { id_prefix: 'accordion-smoke', heading_level: 2, items: [{ title: 'Section A', content: 'Contenu A' }, { title: 'Section B', content: 'Contenu B' }] }),
    generateFragment('tabs', { id_prefix: 'tab-smoke', tabs: [{ label: 'Onglet 1', content: 'Contenu 1' }, { label: 'Onglet 2', content: 'Contenu 2' }] }),
    generateFragment('modal', { id: 'modal-smoke', title: 'Modale de test', content: 'Contenu de la modale', trigger_label: 'Ouvrir la modale' }),
    generateFragment('display', null),
  ];
  for (const result of generated) {
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
  const context = { playwright: version, source, dsfrPackage, dsfrVersion, fixture: 'generate_component.py accordion/tabs/modal/display' };
  let tmpDir = null;
  let server = null;
  let browser = null;
  const steps = [
    async () => { if (browser) await browser.close(); },
    async () => { if (server) await server.close(); },
    async () => { if (tmpDir) fs.rmSync(tmpDir, { recursive: true, force: true }); },
  ];
  try {
    tmpDir = fs.mkdtempSync(path.join(os.tmpdir(), 'dsfr-interactive-'));
    server = await startStaticServer([
      { prefix: '/pages/', root: tmpDir },
      { prefix: '/dsfr/', root: path.join(dsfrPackage, 'dist') },
    ]);
    fs.writeFileSync(path.join(tmpDir, 'interactive.html'), pageHtml(generated.map((item) => item.stdout), dsfrPackage, server.origin), 'utf8');

    try {
      browser = await playwright.chromium.launch({ headless: true });
    } catch (err) {
      printSkipped('Playwright chromium could not launch. Run `npx playwright install chromium` to enable this check.', { ...context, detail: err.message });
      return;
    }
    const page = await browser.newPage();
    const errors = [];
    page.on('console', (message) => {
      if (message.type() === 'error') errors.push(message.text());
    });
    page.on('pageerror', (err) => errors.push(err.message));

    const checks = {};
    await page.goto(`${server.origin}/pages/interactive.html`, { waitUntil: 'domcontentloaded' });
    try {
      await waitForDsfr(page);
    } catch (err) {
      if (process.env.DSFR_INTERACTIVE_SKIP_ON_RUNTIME_LOAD === '1') {
        printSkipped('DSFR runtime could not load before timeout from local assets.', { ...context, detail: err.message });
        return;
      }
      throw err;
    }

    // Accordéon : l'attribut du bouton ET l'ouverture réelle du panneau.
    const accordionButton = '.fr-accordion__btn[aria-controls="accordion-smoke-1"]';
    checks.accordionBefore = await page.locator(accordionButton).getAttribute('aria-expanded');
    checks.accordionPanelBefore = await page.locator('#accordion-smoke-1').evaluate((node) => node.classList.contains('fr-collapse--expanded'));
    await page.locator(accordionButton).click();
    checks.accordionAfter = await attributeBecomes(page, accordionButton, 'aria-expanded', 'true');
    checks.accordionPanelAfter = await classBecomes(page, '#accordion-smoke-1', 'fr-collapse--expanded', true);

    // Onglets : sélection du second ET désélection du premier (roving tabindex).
    await page.locator('#tab-smoke-2').click();
    checks.secondTabSelected = await attributeBecomes(page, '#tab-smoke-2', 'aria-selected', 'true');
    checks.secondPanelSelected = await classBecomes(page, '#tab-smoke-2-panel', 'fr-tabs__panel--selected', true);
    checks.firstTabDeselected = (await page.locator('#tab-smoke-1').getAttribute('aria-selected')) === 'false';
    checks.firstPanelDeselected = !(await page.locator('#tab-smoke-1-panel').evaluate((node) => node.classList.contains('fr-tabs__panel--selected')));
    checks.rovingTabindex = (await page.locator('#tab-smoke-2').getAttribute('tabindex')) === '0'
      && (await page.locator('#tab-smoke-1').getAttribute('tabindex')) === '-1';

    // Modale native : déclencheur généré, ouverture puis fermeture.
    const modalButton = page.locator('[aria-controls="modal-smoke"][data-fr-opened]').first();
    checks.modalTargetPresent = await page.locator('#modal-smoke').count();
    await modalButton.click();
    checks.modalOpen = await classBecomes(page, '#modal-smoke', 'fr-modal--opened', true) || await isDialogOpen(page, '#modal-smoke');
    await page.locator('#modal-smoke .fr-btn--close').click();
    checks.modalClosed = !(await classBecomes(page, '#modal-smoke', 'fr-modal--opened', false)) && !(await isDialogOpen(page, '#modal-smoke'));

    // Paramètres d'affichage : modale officielle et ses trois thèmes.
    const displayButton = page.locator('.fr-btn--display').first();
    checks.displayButtonControls = await displayButton.getAttribute('aria-controls');
    checks.displayTargetPresent = await page.locator('#fr-theme-modal').count();
    await displayButton.click();
    checks.displayModalOpen = await classBecomes(page, '#fr-theme-modal', 'fr-modal--opened', true) || await isDialogOpen(page, '#fr-theme-modal');
    checks.displayRadioCount = await page.locator('input[name="fr-radios-theme"]').count();
    await page.locator('#fr-theme-modal .fr-btn--close').click();
    checks.displayModalClosed = !(await classBecomes(page, '#fr-theme-modal', 'fr-modal--opened', false)) && !(await isDialogOpen(page, '#fr-theme-modal'));

    const pass = checks.accordionBefore === 'false'
      && checks.accordionPanelBefore === false
      && checks.accordionAfter === 'true'
      && checks.accordionPanelAfter === true
      && checks.secondTabSelected === 'true'
      && checks.secondPanelSelected === true
      && checks.firstTabDeselected === true
      && checks.firstPanelDeselected === true
      && checks.rovingTabindex === true
      && checks.modalTargetPresent === 1
      && checks.modalOpen === true
      && checks.modalClosed === true
      && checks.displayButtonControls === 'fr-theme-modal'
      && checks.displayTargetPresent === 1
      && checks.displayModalOpen === true
      && checks.displayModalClosed === true
      && checks.displayRadioCount === 3
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
