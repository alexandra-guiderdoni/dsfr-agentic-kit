const fs = require('fs');
const http = require('http');
const os = require('os');
const path = require('path');
const Module = require('module');

const VERSION_RE = /^\d+\.\d+\.\d+(?:[.-][0-9A-Za-z.]+)?$/;
const DSFR_VERSION = process.env.DSFR_OFFICIAL_VERSION || '1.15.2';
if (!VERSION_RE.test(DSFR_VERSION)) {
  throw new Error(`DSFR_OFFICIAL_VERSION invalide (${JSON.stringify(DSFR_VERSION.slice(0, 40))}) : numéro de version attendu, par exemple 1.15.2`);
}
const DEFAULT_CACHE_DIR = expandHome(process.env.DSFR_OFFICIAL_CACHE_DIR || path.join(os.homedir(), '.cache', 'dsfr-official-cache'));
const PYTHON = process.env.PYTHON || 'python3';
const SUBPROCESS_TIMEOUT_MS = 60000;

function expandHome(value) {
  if (!value) return value;
  return value === '~' || value.startsWith('~/') ? path.join(os.homedir(), value.slice(1)) : value;
}

function hasPackageJson(candidate) {
  try {
    return fs.statSync(path.join(candidate, 'package.json')).isFile();
  } catch (_err) {
    return false;
  }
}

/**
 * Ordre documenté (evals/local-validation.md) : PLAYWRIGHT_PACKAGE_DIR, puis
 * require standard, puis le cache ~/.npm/_npx (entrée la plus récente).
 * Une variable définie mais invalide ne retombe jamais en silence sur un autre
 * candidat : elle est signalée.
 */
function findPlaywrightPackage() {
  const envPath = process.env.PLAYWRIGHT_PACKAGE_DIR;
  if (envPath) {
    const candidate = expandHome(envPath);
    if (hasPackageJson(candidate)) return { dir: candidate, error: null };
    return { dir: null, error: `PLAYWRIGHT_PACKAGE_DIR=${envPath} ne contient pas de package.json` };
  }

  try {
    return { dir: path.dirname(require.resolve('playwright/package.json')), error: null };
  } catch (_err) {
    // Continue with cache lookup.
  }

  const npxRoot = path.join(os.homedir(), '.npm', '_npx');
  const candidates = [];
  if (fs.existsSync(npxRoot)) {
    for (const entry of fs.readdirSync(npxRoot)) {
      candidates.push(path.join(npxRoot, entry, 'node_modules', 'playwright'));
    }
  }
  const found = candidates
    .filter(hasPackageJson)
    .sort((a, b) => fs.statSync(path.join(b, 'package.json')).mtimeMs - fs.statSync(path.join(a, 'package.json')).mtimeMs);
  return { dir: found[0] || null, error: null };
}

function loadPlaywright() {
  const { dir, error } = findPlaywrightPackage();
  if (!dir) return { loaded: null, error };
  const requireFromPackage = Module.createRequire(path.join(dir, 'package.json'));
  return {
    loaded: {
      playwright: requireFromPackage('playwright'),
      version: requireFromPackage('playwright/package.json').version,
      source: dir,
    },
    error: null,
  };
}

function printSkipped(reason, extra = {}) {
  console.log(JSON.stringify({
    status: 'SKIPPED',
    reason,
    ...extra,
  }, null, 2));
  process.exitCode = 2;
}

function packageLooksUsable(packageDir) {
  const distDir = path.join(packageDir, 'dist');
  return fs.existsSync(path.join(distDir, 'dsfr.min.css'))
    && fs.existsSync(path.join(distDir, 'dsfr.module.min.js'))
    && fs.existsSync(path.join(distDir, 'dsfr.nomodule.min.js'))
    && fs.existsSync(path.join(distDir, 'utility', 'icons', 'icons.min.css'));
}

function packageVersion(packageDir) {
  try {
    return String(JSON.parse(fs.readFileSync(path.join(packageDir, 'package.json'), 'utf8')).version || '');
  } catch (_err) {
    return '';
  }
}

/**
 * Paquet DSFR local : DSFR_OFFICIAL_PACKAGE_DIR s'il est défini (obligatoirement
 * utilisable, sinon signalé), sinon le cache de la version cible. La version
 * réellement lue est renvoyée avec le chemin ; un écart avec DSFR_VERSION est
 * signalé sur stderr, jamais masqué.
 */
function resolveDsfrPackage() {
  const envDir = process.env.DSFR_OFFICIAL_PACKAGE_DIR;
  if (envDir) {
    const candidate = expandHome(envDir);
    if (!packageLooksUsable(candidate)) {
      return { dir: null, version: null, error: `DSFR_OFFICIAL_PACKAGE_DIR=${envDir} ne contient pas un paquet @gouvfr/dsfr extrait (dist/ incomplet)` };
    }
    const version = packageVersion(candidate);
    if (version && version !== DSFR_VERSION) {
      console.error(`Avertissement : DSFR_OFFICIAL_PACKAGE_DIR fournit @gouvfr/dsfr@${version}, la cible est ${DSFR_VERSION}`);
    }
    return { dir: candidate, version: version || DSFR_VERSION, error: null };
  }
  const candidate = path.join(DEFAULT_CACHE_DIR, `gouvfr-dsfr-${DSFR_VERSION}`, 'package');
  if (packageLooksUsable(candidate)) {
    return { dir: candidate, version: packageVersion(candidate) || DSFR_VERSION, error: null };
  }
  return { dir: null, version: null, error: `paquet @gouvfr/dsfr@${DSFR_VERSION} introuvable dans ${DEFAULT_CACHE_DIR}` };
}

// Les ressources DSFR sont toujours servies par le serveur local : le mode
// file:// n'était exercé par aucun contrôle et masquait les erreurs CORS.
function localAssetUrl(origin, relativePath) {
  if (!origin) throw new Error('localAssetUrl : origine du serveur local requise');
  return `${origin}/dsfr/${relativePath}`;
}

function dsfrHeadTags(origin) {
  return [
    `<link rel="stylesheet" href="${localAssetUrl(origin, 'dsfr.min.css')}">`,
    `<link rel="stylesheet" href="${localAssetUrl(origin, 'utility/icons/icons.min.css')}">`,
  ].join('\n  ');
}

function dsfrScriptTags(origin) {
  return [
    `<script type="module" src="${localAssetUrl(origin, 'dsfr.module.min.js')}"></script>`,
    `<script nomodule src="${localAssetUrl(origin, 'dsfr.nomodule.min.js')}"></script>`,
  ].join('\n  ');
}

// Toute version du CDN est remplacée : le HTML audité et le paquet servi
// doivent venir du même endroit, quelle que soit la valeur interpolée.
const CDN_PREFIX_RE = /https:\/\/cdn\.jsdelivr\.net\/npm\/@gouvfr\/dsfr@[^/"']*\/dist\//g;

function patchDsfrCdnToLocal(html, origin) {
  if (!origin) throw new Error('patchDsfrCdnToLocal : origine du serveur local requise');
  const localPrefix = `${origin}/dsfr/`;
  // Fonction de remplacement : les motifs $& et $1 d'un chemin ne sont pas interprétés.
  return html.replace(CDN_PREFIX_RE, () => localPrefix);
}

function contentType(filePath) {
  const ext = path.extname(filePath);
  if (ext === '.html') return 'text/html; charset=utf-8';
  if (ext === '.css') return 'text/css; charset=utf-8';
  if (ext === '.js' || ext === '.mjs') return 'text/javascript; charset=utf-8';
  if (ext === '.json' || ext === '.webmanifest') return 'application/json; charset=utf-8';
  if (ext === '.svg') return 'image/svg+xml';
  if (ext === '.png') return 'image/png';
  if (ext === '.ico') return 'image/x-icon';
  if (ext === '.woff') return 'font/woff';
  if (ext === '.woff2') return 'font/woff2';
  return 'application/octet-stream';
}

/**
 * Confinement sous la racine servie, liens symboliques résolus : un lien
 * placé sous la racine et pointant ailleurs n'est pas servi.
 */
function resolveUnder(rootDir, relativePath) {
  let root;
  try {
    root = fs.realpathSync(rootDir);
  } catch (_err) {
    return null;
  }
  const target = path.resolve(root, relativePath);
  if (target !== root && !target.startsWith(`${root}${path.sep}`)) return null;
  let real;
  try {
    real = fs.realpathSync(target);
  } catch (_err) {
    return null;
  }
  if (real !== root && !real.startsWith(`${root}${path.sep}`)) return null;
  return real;
}

function startStaticServer(routes) {
  const normalizedRoutes = routes.map((route) => ({
    prefix: route.prefix.endsWith('/') ? route.prefix : `${route.prefix}/`,
    root: route.root,
  }));

  let origin = null;
  const server = http.createServer((req, res) => {
    res.on('error', () => {});
    if (req.method !== 'GET' && req.method !== 'HEAD') {
      res.writeHead(405);
      res.end('method not allowed');
      return;
    }
    // Serveur local éphémère : seul l'hôte de loopback annoncé est servi.
    const expectedHost = origin ? origin.replace(/^http:\/\//, '') : null;
    if (expectedHost && req.headers.host !== expectedHost) {
      res.writeHead(400);
      res.end('bad host');
      return;
    }
    let url;
    let pathname;
    try {
      url = new URL(req.url, 'http://127.0.0.1');
      pathname = decodeURIComponent(url.pathname);
    } catch (_err) {
      res.writeHead(400);
      res.end('bad request');
      return;
    }
    for (const route of normalizedRoutes) {
      if (!pathname.startsWith(route.prefix)) continue;
      const relativePath = pathname.slice(route.prefix.length);
      const filePath = resolveUnder(route.root, relativePath || 'index.html');
      if (!filePath || !fs.statSync(filePath).isFile()) {
        res.writeHead(404);
        res.end('not found');
        return;
      }
      if (req.method === 'HEAD') {
        res.writeHead(200, { 'Content-Type': contentType(filePath) });
        res.end();
        return;
      }
      const stream = fs.createReadStream(filePath);
      // L'en-tête n'est écrit qu'une fois le fichier ouvert : un fichier
      // illisible donne un 500 net, une coupure en cours d'envoi détruit
      // la réponse au lieu de laisser Playwright expirer.
      stream.once('open', () => {
        res.writeHead(200, { 'Content-Type': contentType(filePath) });
        stream.pipe(res);
      });
      stream.on('error', (err) => {
        if (!res.headersSent) {
          res.writeHead(500);
          res.end(`read error: ${err.code || err.message}`);
        } else {
          res.destroy(err);
        }
      });
      return;
    }
    res.writeHead(404);
    res.end('not found');
  });

  return new Promise((resolve, reject) => {
    server.once('error', reject);
    server.listen(0, '127.0.0.1', () => {
      const address = server.address();
      origin = `http://127.0.0.1:${address.port}`;
      // Une fois la promesse réglée, une erreur du serveur est journalisée
      // au lieu d'être avalée par un rejet sans preneur.
      server.removeListener('error', reject);
      server.on('error', (err) => console.error(`serveur statique : ${err.message}`));
      resolve({
        origin,
        close: () => new Promise((done) => server.close(() => done())),
      });
    });
  });
}

/**
 * Lance un générateur Python du skill. Sans interpréteur, le contrôle sort
 * SKIPPED (limite d'environnement nommée), jamais FAIL.
 */
function runPython(args, options = {}) {
  const childProcess = require('child_process');
  const result = childProcess.spawnSync(PYTHON, ['-B', ...args], {
    encoding: 'utf8',
    maxBuffer: 10 * 1024 * 1024,
    timeout: SUBPROCESS_TIMEOUT_MS,
    ...options,
  });
  if (result.error) {
    const code = result.error.code === 'ENOENT'
      ? `interpréteur Python introuvable (${PYTHON}) : définir PYTHON`
      : (result.error.code === 'ETIMEDOUT' ? `délai dépassé (${SUBPROCESS_TIMEOUT_MS} ms)` : result.error.message);
    return { ok: false, skip: result.error.code === 'ENOENT', error: code, stdout: '', stderr: '' };
  }
  if (result.status !== 0) {
    const why = result.signal ? `interrompu par le signal ${result.signal}` : `code de sortie ${result.status}`;
    return { ok: false, skip: false, error: (result.stderr || '').trim() || why, stdout: result.stdout || '', stderr: result.stderr || '' };
  }
  return { ok: true, skip: false, error: null, stdout: result.stdout, stderr: result.stderr };
}

/** Nettoyage tolérant : chaque étape s'exécute même si la précédente échoue. */
async function cleanup(steps) {
  for (const step of steps) {
    try {
      await step();
    } catch (_err) {
      // Une erreur de nettoyage ne doit ni masquer le verdict ni sauter les étapes suivantes.
    }
  }
}

async function waitForDsfr(page) {
  await page.waitForFunction(() => Boolean(window.dsfr && window.dsfr.internals), null, { timeout: 8000 });
  // Le runtime annonce ses internes avant d'avoir instancié tous les composants.
  await page.waitForFunction(() => document.querySelector('[data-fr-js-modal="true"], [data-fr-js-collapse="true"], [data-fr-js-tab-button="true"]') !== null, null, { timeout: 8000 }).catch(() => {});
}

module.exports = {
  DSFR_VERSION,
  PYTHON,
  cleanup,
  dsfrHeadTags,
  dsfrScriptTags,
  loadPlaywright,
  patchDsfrCdnToLocal,
  printSkipped,
  resolveDsfrPackage,
  runPython,
  startStaticServer,
  waitForDsfr,
};
