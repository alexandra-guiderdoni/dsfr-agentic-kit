# Patterns de scan axe-core

Reference partagee pour les skills utilisant axe-core.
Consulte par : audit-accessibilite-web, a11y-loop, a11y-ci, audit-rgaa.

## Strategie de scan (3 niveaux de fallback)

### Ordre normal (pas de WAF detecte)

#### 1. @accesslint/mcp (prioritaire)

Utiliser `mcp__accesslint__audit_url` avec l'URL de la page (ou `audit_file` pour un fichier local).
Resultats structures avec impact, critere WCAG, selecteurs CSS et suggestions de correction.
Pas de probleme CSP ni de CDN.
Optionnel : `mcp__accesslint__list_rules` pour informer de la couverture des tests.

#### 2. Fallback injection axe-core CDN

Si MCP non disponible, injecter axe-core via `evaluate_script` :
- AA : tags `['wcag2a', 'wcag2aa', 'wcag21aa', 'wcag22aa']`
- AAA : ajouter `['wcag2aaa', 'wcag21aaa']`
- Timeout : 10 secondes sur le chargement CDN
- Utiliser le script template du playbook (`resources/implementation-playbook.md` section 1) si disponible

#### 3. Fallback CLI

Si injection echoue (CSP, timeout CDN) :
```bash
npx @axe-core/cli {url} --tags wcag2a,wcag2aa --reporter json
```

### Ordre pour sites proteges par Cloudflare (WAF detecte)

Si un challenge Cloudflare est detecte (voir [cloudflare-bypass.md](cloudflare-bypass.md)), **inverser l'ordre** :

1. **Niveau 2 (prioritaire)** : injection axe-core CDN via `evaluate_script` dans chrome-devtools (vrai Chrome, pas de detection headless)
2. **Niveau 1 (complement)** : `mcp__accesslint__audit_url` si le fetch HTTP passe
3. **Niveau 3 (abandon)** : `npx @axe-core/cli` ne fonctionnera pas (Chromium headless bloque)

Logger dans le rapport : `Outil : axe-core CDN {version} via chrome-devtools (contournement Cloudflare)`

### Detection automatique Cloudflare

Avant de lancer le scan, verifier avec `navigate_page` + `take_snapshot` ou `evaluate_script` :
- Titre de page « Just a moment... »
- Texte « Verify you are human » ou « Checking your browser »
- Element `#challenge-form`, `.cf-challenge` ou `#turnstile-wrapper`

Si detecte : basculer sur l'ordre Cloudflare. Voir [cloudflare-bypass.md](cloudflare-bypass.md) pour les details.

## Calcul du score

```
score = max(0, 100 - somme(poids[impact] * nb_elements_affectes))
```

Poids par impact :
- critical = 10
- serious = 5
- moderate = 2
- minor = 1

Calculer egalement les scores par principe POUR separement.

## Format de stockage des resultats

Pour chaque violation :
```json
{ "id": "...", "impact": "...", "description": "...", "helpUrl": "...", "nodes": [{ "target": "...", "html": "...", "failureSummary": "..." }] }
```

Variables de suivi (pour a11y-loop) :
- `total_violations` : nombre total de violations
- `violations_list` : liste structuree ci-dessus
- `iteration_history` : `[{ iteration: N, violations: N, fixed: N, new: N }]`
