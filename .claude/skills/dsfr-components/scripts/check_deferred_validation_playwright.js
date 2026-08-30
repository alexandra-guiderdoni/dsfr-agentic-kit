#!/usr/bin/env node
/*
 * Verifies that a generated DSFR form (the <form> inside <main>) does not
 * expose native invalid state before user action, does expose validation
 * state after the first submit, then cleans that state when a reset control
 * exists. The page is served locally with the cached DSFR package (no CDN).
 * Returns SKIPPED with exit code 2 when Playwright, Chromium or the cached
 * DSFR package is unavailable.
 */

const fs = require('fs');
const os = require('os');
const path = require('path');
const {
  cleanup,
  loadPlaywright,
  patchDsfrCdnToLocal,
  printSkipped,
  resolveDsfrPackage,
  startStaticServer,
} = require('./playwright_dsfr_helpers');

async function readState(page) {
  return page.evaluate(() => {
    const form = document.querySelector('main form');
    const scope = form || document;
    const controls = Array.from(scope.querySelectorAll('input, select, textarea'))
      .filter((node) => !['submit', 'reset', 'button', 'hidden'].includes(node.type))
      .map((node) => ({
        id: node.id,
        tag: node.tagName.toLowerCase(),
        type: node.getAttribute('type') || '',
        requiredAttr: node.hasAttribute('required'),
        ariaRequired: node.getAttribute('aria-required'),
        hasPattern: node.hasAttribute('pattern'),
        ariaInvalid: node.getAttribute('aria-invalid'),
        valid: node.checkValidity(),
      }));

    function visible(node) {
      if (node.hidden) return false;
      const style = window.getComputedStyle(node);
      return style.display !== 'none'
        && style.visibility !== 'hidden'
        && node.getClientRects().length > 0;
    }

    return {
      formFound: Boolean(form),
      controls,
      invalidNativeCount: controls.filter((control) => !control.valid).length,
      ariaInvalidCount: controls.filter((control) => control.ariaInvalid === 'true').length,
      requiredCount: controls.filter((control) => control.requiredAttr).length,
      // aria-required="false" n'est pas une contrainte ; pattern="" en est une.
      ariaRequiredCount: controls.filter((control) => control.ariaRequired === 'true').length,
      patternCount: controls.filter((control) => control.hasPattern).length,
      errorMessageCount: scope.querySelectorAll('.fr-error-text').length,
      visibleErrorMessageCount: Array.from(scope.querySelectorAll('.fr-error-text')).filter(visible).length,
    };
  });
}

async function main() {
  const htmlPath = process.argv[2];
  if (!htmlPath) {
    throw new Error('Usage: check_deferred_validation_playwright.js <html-file>');
  }
  const absolutePath = path.resolve(htmlPath);
  if (!fs.existsSync(absolutePath)) {
    throw new Error(`HTML file not found: ${absolutePath}`);
  }

  const { loaded, error: playwrightError } = loadPlaywright();
  if (!loaded) {
    printSkipped(playwrightError || 'Playwright module not found in local node_modules or npx cache. Run `npx playwright --version` or install `playwright` to enable this check.', { file: absolutePath });
    return;
  }
  const { dir: dsfrPackage, version: dsfrVersion, error: dsfrError } = resolveDsfrPackage();
  if (!dsfrPackage) {
    printSkipped(`${dsfrError}. Run check_generated_outputs.py --official-version 1.15.2 to seed the cache.`, { file: absolutePath });
    return;
  }

  const { playwright, version, source } = loaded;
  const tmpDir = fs.mkdtempSync(path.join(os.tmpdir(), 'dsfr-deferred-'));
  let server = null;
  let browser = null;
  const steps = [
    async () => { if (browser) await browser.close(); },
    async () => { if (server) await server.close(); },
    async () => fs.rmSync(tmpDir, { recursive: true, force: true }),
  ];
  try {
    server = await startStaticServer([
      { prefix: '/pages/', root: tmpDir },
      { prefix: '/dsfr/', root: path.join(dsfrPackage, 'dist') },
    ]);
    const html = patchDsfrCdnToLocal(fs.readFileSync(absolutePath, 'utf8'), server.origin);
    fs.writeFileSync(path.join(tmpDir, 'form.html'), html, 'utf8');

    try {
      browser = await playwright.chromium.launch({ headless: true });
    } catch (err) {
      printSkipped(
        'Playwright chromium could not launch. Run `npx playwright install chromium` to enable this check.',
        { file: absolutePath, playwright: version, source, detail: err.message }
      );
      return;
    }
    const page = await browser.newPage();
    // Une soumission qui naviguerait (formulaire sans champ requis) rendrait
    // l'état lu incohérent : la requête de soumission est bloquée.
    await page.route('**/*', (route) => {
      const request = route.request();
      if (request.isNavigationRequest() && request.frame() === page.mainFrame() && request.url() !== `${server.origin}/pages/form.html`) {
        return route.abort('aborted');
      }
      return route.continue();
    });
    await page.goto(`${server.origin}/pages/form.html`, { waitUntil: 'load' });
    const before = await readState(page);
    if (!before.formFound) {
      console.log(JSON.stringify({ status: 'FAIL', reason: 'aucun formulaire dans main : rien à soumettre', playwright: version, source, dsfrPackage, dsfrVersion, file: absolutePath }, null, 2));
      process.exitCode = 1;
      return;
    }

    // Le formulaire à vérifier vit dans <main> : l'en-tête porte son propre
    // <form> de recherche dont le bouton submit précède celui du contenu.
    const submit = page.locator('main form button[type="submit"], main form input[type="submit"]').first();
    if (await submit.count() === 0) {
      throw new Error('No submit control found');
    }
    await submit.click();
    await page.waitForFunction(
      () => document.querySelector('main form [aria-invalid="true"], main form [required]') !== null,
      null, { timeout: 2000 }
    ).catch(() => {});
    const afterSubmit = await readState(page);

    let afterReset = null;
    const reset = page.locator('main form button[type="reset"], main form input[type="reset"]').first();
    if (await reset.count() > 0) {
      await reset.click();
      await page.waitForFunction(
        () => document.querySelector('main form [aria-invalid="true"], main form [required]') === null,
        null, { timeout: 2000 }
      ).catch(() => {});
      afterReset = await readState(page);
    }

    const clean = (state) => state.invalidNativeCount === 0
      && state.ariaInvalidCount === 0
      && state.requiredCount === 0
      && state.ariaRequiredCount === 0
      && state.patternCount === 0
      && state.errorMessageCount === 0
      && state.visibleErrorMessageCount === 0;
    const beforeClean = clean(before);
    // Après soumission : contraintes natives posées, état ARIA et messages
    // d'erreur exposés (references/patterns/validation-differee.md).
    const submitExposesErrors = afterSubmit.invalidNativeCount > 0
      && afterSubmit.ariaInvalidCount > 0
      && afterSubmit.requiredCount > 0
      && afterSubmit.ariaRequiredCount > 0
      && afterSubmit.errorMessageCount > 0
      && afterSubmit.visibleErrorMessageCount === afterSubmit.errorMessageCount;
    const resetClean = !afterReset || clean(afterReset);

    const result = {
      status: before.formFound && beforeClean && submitExposesErrors && resetClean ? 'PASS' : 'FAIL',
      playwright: version,
      source,
      dsfrPackage,
      dsfrVersion,
      file: absolutePath,
      resetChecked: Boolean(afterReset),
      invalidBeforeCount: before.invalidNativeCount,
      invalidAfterCount: afterSubmit.invalidNativeCount,
      invalidResetCount: afterReset ? afterReset.invalidNativeCount : null,
      before,
      afterSubmit,
      afterReset,
    };
    console.log(JSON.stringify(result, null, 2));
    process.exitCode = result.status === 'PASS' ? 0 : 1;
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
