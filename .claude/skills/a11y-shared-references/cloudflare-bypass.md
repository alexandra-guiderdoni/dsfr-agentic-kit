# Contournement Cloudflare pour les audits a11y

Reference partagee pour detecter et contourner les protections Cloudflare/WAF lors des audits d'accessibilite.
Consulte par : audit-accessibilite-web, audit-a11y-complet, a11y-loop.

## Probleme

Les sites proteges par Cloudflare (challenge « Verify you are human ») bloquent :
- Le niveau 3 (CLI) : `npx @axe-core/cli` utilise Chromium headless, detecte par Cloudflare
- Le niveau 1 (accesslint) : fetch HTTP statique, bloque par le challenge JS

Le niveau 2 (chrome-devtools MCP) utilise le vrai Chrome de l'utilisateur via DevTools protocol et **passe la protection sans detection** (valide sur economie.gouv.fr, 1er mars 2026).

## Patterns de detection

Verifier la presence d'un challenge Cloudflare **avant** de lancer l'audit axe-core.

### Via chrome-devtools (apres navigate_page)

Utiliser `take_snapshot` et chercher :

| Signal | Methode de detection |
|--------|---------------------|
| Texte « Verify you are human » | Dans le snapshot a11y |
| Texte « Just a moment... » | Dans le snapshot a11y |
| Texte « Checking your browser » | Dans le snapshot a11y |
| Titre de page « Just a moment... » | `RootWebArea` du snapshot |
| Checkbox Turnstile | Element `checkbox` avec label Cloudflare |

### Via evaluate_script (detection programmatique)

```javascript
() => {
  const body = document.body.innerText;
  const title = document.title;
  const hasCfChallenge = document.querySelector('#challenge-form, .cf-challenge, #turnstile-wrapper');
  return {
    isCloudflare: !!(
      hasCfChallenge ||
      title.includes('Just a moment') ||
      body.includes('Verify you are human') ||
      body.includes('Checking your browser')
    ),
    title: title,
    hasChallengeForm: !!hasCfChallenge
  };
}
```

### Via CLI (sortie axe-core)

Si `npx @axe-core/cli` retourne 0 violations et le HTML contient les signaux ci-dessus, le challenge a bloque l'acces au contenu reel.

## Strategie de contournement

### Ordre de priorite pour les sites proteges

Quand un challenge Cloudflare est detecte, **inverser l'ordre des niveaux** :

1. **Niveau 2 (prioritaire)** : `evaluate_script` avec injection axe-core CDN via chrome-devtools
   - Le vrai Chrome de l'utilisateur est deja authentifie
   - Pas de detection headless
   - Resultats complets (DOM rendu avec JS)

2. **Niveau 1 (complement)** : `mcp__accesslint__audit_url` pour un scan rapide en plus
   - Peut echouer si le fetch HTTP est aussi bloque

3. **Niveau 3 (abandon)** : `npx @axe-core/cli` ne fonctionnera pas sur un site Cloudflare
   - Logger : `[CLOUDFLARE] Niveau 3 (CLI) indisponible — challenge WAF detecte`

### Workflow de detection et bascule

```
1. navigate_page vers l'URL
2. take_snapshot ou evaluate_script (detection Cloudflare)
3. Si Cloudflare detecte :
   a. Logger : [CLOUDFLARE] Protection detectee sur {url}
   b. Basculer sur le niveau 2 (injection axe-core CDN)
   c. Si niveau 2 echoue : signaler ECHEC dans le rapport
4. Si pas de Cloudflare :
   a. Suivre l'ordre normal (niveau 1 > 2 > 3)
```

## Integration dans le rapport

Quand un contournement Cloudflare est active, le rapport doit mentionner :

```
Phase 1 : Audit WCAG ............... {score}/100 — {n} violations
  Outil : axe-core CDN 4.10.2 via chrome-devtools (contournement Cloudflare)
  Note : Site protege par Cloudflare — niveaux 1 (accesslint) et 3 (CLI) indisponibles
```

## Limites connues

- Le niveau 2 necessite que Chrome soit ouvert et connecte au serveur MCP chrome-devtools
- Si l'utilisateur n'a pas encore visite le site dans Chrome, le challenge peut apparaitre
  - Solution : naviguer manuellement dans Chrome une premiere fois, puis relancer l'audit
- Certains sites utilisent des protections plus agressives que Cloudflare (Akamai, Imperva)
  - Meme approche : le vrai Chrome via DevTools est le meilleur contournement
