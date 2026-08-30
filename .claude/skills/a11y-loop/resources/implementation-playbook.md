# Playbook technique — a11y-loop

Reference d'implementation pour le skill `/a11y-loop`. Contient les scripts, patterns de correction, strategies de localisation et templates.

---

## 1. Script d'injection axe-core

### 1.1 Injection et execution via `evaluate_script`

Ce script est un **template parametrable**. Remplacer `__WCAG_TAGS__` par le tableau JSON de tags avant injection (voir section 1.2).

```javascript
async () => {
  // Injection axe-core via CDN Cloudflare avec timeout 10s
  if (!window.axe) {
    await new Promise((resolve, reject) => {
      const timeout = setTimeout(() => reject(new Error('axe-core CDN timeout (10s)')), 10000);
      const script = document.createElement('script');
      script.src = 'https://cdnjs.cloudflare.com/ajax/libs/axe-core/4.10.2/axe.min.js';
      script.crossOrigin = 'anonymous';
      script.onload = () => { clearTimeout(timeout); resolve(); };
      script.onerror = () => { clearTimeout(timeout); reject(new Error('axe-core CDN blocked')); };
      document.head.appendChild(script);
    });
  }

  const tags = __WCAG_TAGS__;

  const results = await axe.run(document, {
    runOnly: { type: 'tag', values: tags }
  });

  return {
    violations: results.violations.map(v => ({
      id: v.id,
      impact: v.impact,
      description: v.description,
      helpUrl: v.helpUrl,
      tags: v.tags.filter(t => t.startsWith('wcag')),
      nodes: v.nodes.map(n => ({
        target: n.target,
        html: n.html,
        failureSummary: n.failureSummary
      }))
    })),
    passes: results.passes.length,
    incomplete: results.incomplete.length,
    total_violations: results.violations.length,
    total_nodes: results.violations.reduce((sum, v) => sum + v.nodes.length, 0)
  };
}
```

### 1.2 Tags WCAG par niveau

| Niveau | Tags axe-core |
|--------|--------------|
| AA | `['wcag2a', 'wcag2aa', 'wcag21aa', 'wcag22aa']` |
| AAA | `['wcag2a', 'wcag2aa', 'wcag21aa', 'wcag22aa', 'wcag2aaa', 'wcag21aaa']` |

### 1.3 Utilisation dans evaluate_script

Avant d'injecter, remplacer le placeholder `__WCAG_TAGS__` par le tableau reel :

```javascript
const script = SCRIPT_TEMPLATE.replace('__WCAG_TAGS__', JSON.stringify(tags));
// Ex: __WCAG_TAGS__ → ['wcag2a', 'wcag2aa', 'wcag21aa', 'wcag22aa']
```

Puis appeler :
```
evaluate_script({ function: script })
```

**Si le CDN echoue** (timeout 10s ou erreur CSP), `evaluate_script` retournera une erreur. Basculer alors sur le fallback CLI (section 1.4).

### 1.5 Mise a jour de la version axe-core

Lors d'une mise a jour de version :
1. Verifier la derniere version sur `https://github.com/dequelabs/axe-core/releases`
2. Mettre a jour l'URL CDN dans le script (remplacer `4.10.2` par la nouvelle version)
3. Tester l'injection sur une page locale pour valider

### 1.4 Fallback CLI (si CSP bloque l'injection)

```bash
npx @axe-core/cli {url} --tags wcag2a,wcag2aa --reporter json
```

Parser la sortie JSON avec la meme structure que le retour evaluate_script.

Si `npx` non disponible :
```bash
npm install -g @axe-core/cli && axe {url} --tags wcag2a,wcag2aa --reporter json
```

---

## 2. Patterns de correction par type

### 2.1 Contraste insuffisant (`color-contrast` — WCAG 1.4.3 / 1.4.6)

**Seuils de ratio de contraste** :

| Niveau | Texte normal | Texte agrandi (>=18pt ou >=14pt bold) | Elements UI |
|--------|-------------|---------------------------------------|-------------|
| AA | 4.5:1 | 3:1 | 3:1 |
| AAA | 7:1 | 4.5:1 | 4.5:1 |

**Formule de luminance relative** :

```
Pour chaque composante R, G, B (valeur 0-255) :
  val = composante / 255
  lin = val <= 0.04045 ? val / 12.92 : ((val + 0.055) / 1.055) ^ 2.4

L = 0.2126 * R_lin + 0.7152 * G_lin + 0.0722 * B_lin
```

**Calcul du ratio** :
```
ratio = (L_clair + 0.05) / (L_sombre + 0.05)
```

**Algorithme de correction** :

1. Convertir la couleur de texte en HSL
2. Conserver H (teinte) et S (saturation)
3. Reduire L (luminosite) par pas de 1% jusqu'a atteindre le ratio cible
4. Si L atteint 0% sans ratio suffisant → mettre noir (`#000000`)
5. Convertir le resultat en hex

**Pattern CSS** :

```css
/* AVANT */
.element { color: #767676; }

/* APRES — ratio ajuste pour AA (4.5:1 minimum) */
.element { color: #595959; }
```

### 2.2 Alt manquant (`image-alt` — WCAG 1.1.1)

**Decision decoratif vs informatif** :

- Image dans un lien sans autre texte → **informatif** (decrire la destination)
- Image seule porteuse d'information → **informatif** (decrire le contenu)
- Image decorative (fond, separateur, icone accompagnee de texte) → `alt=""`
- En cas de doute → `alt=""` avec commentaire `<!-- TODO: ajouter alt descriptif -->`

**Patterns** :

```html
<!-- AVANT : alt manquant -->
<img src="logo.png">

<!-- APRES : decoratif -->
<img src="logo.png" alt="">

<!-- APRES : informatif -->
<img src="logo.png" alt="Logo de l'entreprise">
```

**JSX** :
```jsx
// AVANT
<img src={logo} />

// APRES
<img src={logo} alt="" />
```

### 2.3 Labels de formulaire (`label` — WCAG 1.3.1 / 4.1.2)

**Strategies par priorite** :

1. `<label for="id">` — methode preferee
2. `<label>` englobant — alternative acceptable
3. `aria-label` — quand le label visuel n'est pas souhaite
4. `aria-labelledby` — quand le texte existe ailleurs dans la page

**Patterns** :

```html
<!-- AVANT -->
<input type="text" id="email">

<!-- APRES : label explicite -->
<label for="email">Email</label>
<input type="text" id="email">
```

```html
<!-- AVANT : pas d'id pour le for -->
<input type="text" placeholder="Rechercher">

<!-- APRES : aria-label quand pas de label visuel -->
<input type="text" placeholder="Rechercher" aria-label="Rechercher">
```

### 2.4 Langue du document (`html-has-lang` — WCAG 3.1.1)

```html
<!-- AVANT -->
<html>

<!-- APRES -->
<html lang="fr">
```

**Detection de la langue** : analyser le contenu textuel visible de la page. Si majoritairement francais → `fr`, anglais → `en`, etc. En cas de doute → `fr` (contexte utilisateur).

### 2.5 Titre de page (`document-title` — WCAG 2.4.2)

```html
<!-- AVANT : pas de title -->
<head>
  <meta charset="UTF-8">
</head>

<!-- APRES -->
<head>
  <meta charset="UTF-8">
  <title>Nom de la page - Nom du site</title>
</head>
```

**Generation du titre** : extraire du `<h1>` de la page, ou du nom de fichier si pas de `<h1>`.

### 2.6 Liens vides (`link-name` — WCAG 2.4.4 / 4.1.2)

```html
<!-- AVANT : lien icone sans texte -->
<a href="/profil"><i class="icon-user"></i></a>

<!-- APRES -->
<a href="/profil" aria-label="Profil utilisateur"><i class="icon-user"></i></a>
```

```html
<!-- AVANT : lien image sans alt -->
<a href="/"><img src="home.png"></a>

<!-- APRES -->
<a href="/"><img src="home.png" alt="Accueil"></a>
```

### 2.7 Boutons vides (`button-name` — WCAG 4.1.2)

```html
<!-- AVANT -->
<button><i class="icon-close"></i></button>

<!-- APRES -->
<button aria-label="Fermer"><i class="icon-close"></i></button>
```

### 2.8 Titre d'iframe (`frame-title` — WCAG 2.4.1 / 4.1.2)

```html
<!-- AVANT -->
<iframe src="https://maps.google.com/..."></iframe>

<!-- APRES -->
<iframe src="https://maps.google.com/..." title="Carte Google Maps"></iframe>
```

### 2.9 Meta viewport (`meta-viewport` — WCAG 1.4.4)

```html
<!-- AVANT : bloque le zoom -->
<meta name="viewport" content="width=device-width, initial-scale=1, maximum-scale=1, user-scalable=no">

<!-- APRES -->
<meta name="viewport" content="width=device-width, initial-scale=1">
```

### 2.10 Champ obligatoire (`select-name` — WCAG 4.1.2)

```html
<!-- AVANT -->
<select>
  <option>Choisir...</option>
</select>

<!-- APRES -->
<label for="pays">Pays</label>
<select id="pays">
  <option>Choisir...</option>
</select>
```

---

## 3. Strategie de localisation source

### 3.1 Algorithme de recherche

Pour un noeud axe-core avec `target: ["#search-btn"]` et `html: '<button id="search-btn"><i class="fa-search"></i></button>'` :

1. **Recherche par ID** (plus fiable) :
   ```
   Grep: pattern='id="search-btn"' ou pattern='id=["']search-btn["']'
   ```

2. **Recherche par classe specifique** :
   ```
   Grep: pattern='class="fa-search"' ou pattern='className="fa-search"'
   ```

3. **Recherche par snippet partiel** :
   - Extraire un fragment unique du HTML (balise + attributs)
   - Chercher ce fragment dans les fichiers source

4. **Recherche par contenu textuel** :
   - Si l'element contient du texte visible, chercher ce texte

### 3.2 Gestion des frameworks

| Framework | Particularites |
|-----------|---------------|
| **HTML statique** | Recherche directe du snippet |
| **React (JSX/TSX)** | `className` au lieu de `class`, `htmlFor` au lieu de `for`, expressions `{}` |
| **Vue SFC** | `<template>` contient le HTML, `:class` pour bindings dynamiques, `v-bind` |
| **Svelte** | `class:nom={condition}` pour classes conditionnelles |
| **Angular** | `[class]`, `[attr.aria-label]`, templates `*ngIf` |
| **PHP/Twig/EJS** | Variables dans attributs (`<?= $var ?>`, `{{ var }}`, `<%= var %>`) |

### 3.3 Filtrage des fichiers

Limiter la recherche aux extensions pertinentes :

```
Glob: **/*.{html,htm,jsx,tsx,vue,svelte,php,ejs,twig,hbs,pug}
```

Pour les corrections CSS (contraste) :
```
Glob: **/*.{css,scss,sass,less,styled.{js,ts},module.css}
```

---

## 4. Template du rapport final

```markdown
# Rapport a11y-loop

- **URL** : {url}
- **Niveau WCAG** : {level}
- **Source** : {source}
- **Date** : {date}
- **Statut** : {statut}
- **Iterations** : {n} / {max}
- **Commit de reference** : {hash}

---

## Evolution des violations

| Iteration | Violations | Corrigees | Nouvelles | Delta |
|-----------|-----------|-----------|-----------|-------|
| 0 (initial) | {n} | — | — | — |
| 1 | {n} | {n} | {n} | -{n} |

### Graphe

```
violations
  {max} |##
        |####
        |######
        |########
      0 +----------->
        0   1   2   iterations
```

---

## Corrections appliquees ({total})

| # | Fichier | Ligne | Regle axe-core | WCAG | Confiance | Avant | Apres |
|---|---------|-------|----------------|------|-----------|-------|-------|
| 1 | src/index.html | 12 | image-alt | 1.1.1 | High | `<img src="logo.png">` | `<img src="logo.png" alt="">` |

---

## Violations restantes ({total})

| # | Regle axe-core | Impact | WCAG | Elements | Recommandation |
|---|----------------|--------|------|----------|----------------|
| 1 | aria-required-attr | serious | 4.1.2 | 2 | Ajouter les attributs ARIA requis manuellement |

---

## Prochaines etapes

- {suggestions contextuelles}
```

---

## 5. Gestion du contexte entre iterations

### Principe : summariser, ne pas accumuler

A chaque iteration, ne conserver que :

- **Compteurs** : `iteration_history` (tableau compact)
- **IDs de violations** : set des IDs pour detecter regressions/progres
- **Log des corrections** : liste compacte `{ file, line, rule_id, wcag, before, after }`
- **Statut courant** : nombre de violations, delta

Purger apres chaque iteration :
- Les resultats bruts `axe.run()` (nodes detailles, html, target)
- Les contenus de fichiers lus pour localisation

### Structure de donnees inter-iterations

```
state = {
  config: { url, source, max_iterations, level, aggressive, reload_strategy, build_cmd, commit_ref },
  iteration: 0,
  history: [
    { iteration: 0, violations: 12, violation_ids: Set([...]), fixed: 0, new: 0 }
  ],
  corrections: [
    { file: "src/index.html", line: 12, rule_id: "image-alt", wcag: "1.1.1", confidence: "high", before: "...", after: "..." }
  ],
  current_violations: [...],  // uniquement l'iteration courante
  status: "in_progress"       // in_progress | conforme | regression | no_progress | max_iterations
}
```

---

## 6. Detection de l'environnement de build

### Algorithme de detection

1. Chercher `package.json` dans le repertoire source
2. Si trouve, extraire les scripts :
   - `scripts.dev` → hot-reload probable
   - `scripts.start` → serveur de dev probable
   - `scripts.build` → build statique

3. Identifier le bundler :

| Fichier detecte | Bundler | Hot-reload | Commande build typique |
|-----------------|---------|------------|----------------------|
| `vite.config.*` | Vite | oui | `npm run build` |
| `webpack.config.*` | Webpack | probable | `npm run build` |
| `next.config.*` | Next.js | oui (dev) | `npm run build` |
| `nuxt.config.*` | Nuxt | oui (dev) | `npm run build` |
| `astro.config.*` | Astro | oui (dev) | `npm run build` |
| Aucun | Statique | non | aucune |

4. Determiner la strategie :
   - Si l'URL contient `:3000`, `:5173`, `:8080` (ports dev typiques) et bundler detecte → `navigate` (hot-reload)
   - Si build necessaire (pas de hot-reload) → `build` avec la commande extraite
   - Si fichiers statiques sans bundler → `navigate`
