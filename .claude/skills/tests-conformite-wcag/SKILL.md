---
name: tests-conformite-wcag
description: "Utiliser quand une page doit être testée avec Playwright sur les critères WCAG 2.2 peu couverts par axe-core : reflow, espacement, zoom, orientation, autocomplete, délais, autoplay, focus ou taille de cible. Ne pas utiliser pour un audit axe-core seul."
allowed-tools: Bash, Read, Write, Glob, Grep
argument-hint: "[url] [--tests all|reflow|spacing|zoom|orientation|focus|target|autoplay|time|autocomplete] [--output json|md]"
context: conversation
---

# Tests de conformité WCAG 2.2 avec Playwright

Ce skill exécute des tests Playwright complémentaires à `audit-accessibilite-web` pour les
critères WCAG que axe-core détecte mal ou pas du tout. Il produit un rapport
borné, jamais une déclaration complète de conformité.

## Déclencheurs

- `/tests-conformite-wcag`
- "tests WCAG Playwright", "teste le reflow", "teste l'espacement du texte"
- Vérifier zoom 200 %, orientation, focus visible, cible tactile, autoplay,
  délais ou autocomplete
- Compléter un audit axe-core par des contrôles automatisés hors axe-core

Ne pas utiliser pour un scan axe-core général : utiliser
`audit-accessibilite-web`.

## Arguments

```text
/tests-conformite-wcag https://example.com
/tests-conformite-wcag https://example.com --tests reflow,spacing,zoom
/tests-conformite-wcag https://localhost:3000 --tests focus --screenshots
```

| Argument | Description | Défaut |
|---|---|---|
| `url` | URL de la page à tester | obligatoire |
| `--tests` | `all` ou liste séparée par virgules | `all` |
| `--output` | `md` ou `json` | `md` |
| `--screenshots` | Captures des anomalies | désactivé |

Tests disponibles : `reflow`, `spacing`, `zoom`, `orientation`,
`autocomplete`, `time`, `autoplay`, `focus`, `target`.

## Pré-vol

1. Parser `url`, `--tests`, `--output` et `--screenshots`.
2. Si `url` manque, afficher l'usage et arrêter.
3. Vérifier Playwright :

```bash
npx playwright --version
```

4. Si Playwright manque, proposer `npx playwright install chromium` et arrêter.
5. Vérifier l'URL :

```bash
curl -s -o /dev/null -w "%{http_code}" "$URL"
```

6. Continuer seulement pour un code HTTP `2xx` ou `3xx`.
7. Afficher URL, tests, format, captures, puis lancer.

## Exécution

Chaque test doit être indépendant : un échec, une erreur ou un timeout sur un
test ne bloque pas les autres. Le script Playwright peut être temporaire, mais
le rapport final doit toujours garder les résultats exploitables.

Structure minimale :

```javascript
const { chromium } = require('playwright');

(async () => {
  const browser = await chromium.launch();
  const page = await browser.newPage();
  await page.goto(URL, { waitUntil: 'networkidle' });
  const results = [];
  await browser.close();
  console.log(JSON.stringify(results, null, 2));
})();
```

Contrats détaillés : lire `references/test-contracts.md` avant d'implémenter
ou de modifier un test. Matrice courte : `references/coverage-matrix.md`.

## Contrats des tests

| Test | Critères WCAG | Succès minimal |
|---|---|---|
| `reflow` | 1.4.10 AA | pas de scroll horizontal à 320 px |
| `spacing` | 1.4.12 AA | aucun texte masqué après styles d'espacement |
| `zoom` | 1.4.4 AA | contenu lisible à 200 %, zoom non bloqué |
| `orientation` | 1.3.4 AA | contenu utilisable portrait et paysage |
| `autocomplete` | 1.3.5 AA | champs personnels avec `autocomplete` adapté |
| `time` | 2.2.1 A | aucun délai imposé sans pause, arrêt ou extension |
| `autoplay` | 1.4.2 A / 2.2.2 A | média automatique contrôlable, son coupé par défaut |
| `focus` | 2.4.7 AA | focus visible, `outline: none` compensé |
| `target` | 2.5.8 AA / 2.5.5 AAA | cible AA 24 x 24 px ou espacement compensatoire |

## Rapport

Format Markdown par défaut : générer `CONFORMITE-WCAG-REPORT.md` dans le
répertoire courant.

Le rapport contient :

- URL testée, date, tests exécutés et outil ;
- tableau récapitulatif par critère WCAG ;
- détails par test : méthode, statut, valeurs mesurées, éléments non conformes ;
- recommandations classées par priorité ;
- avertissement sur les tests manuels complémentaires.

Format JSON : générer `conformite-wcag-report.json` avec `url`, `date`,
`tests.{name}.status`, `elementsTested`, `nonConformant`, `details` et
`summary`.

Captures : si `--screenshots` est actif, écrire dans
`conformite-wcag-screenshots/` avec des noms descriptifs, par exemple
`reflow-320px.png`, `spacing-before.png`, `spacing-after.png`,
`zoom-200.png`, `focus-{element}.png`.

## Gestion des erreurs

| Situation | Comportement |
|---|---|
| Playwright absent | proposer l'installation, ne pas continuer |
| URL inaccessible | erreur avec code HTTP, ne pas continuer |
| Crash d'un test | statut `error`, stack trace résumée, suite des tests |
| Timeout | statut `na` ou `error`, raison documentée, suite des tests |
| Aucun élément interactif | `focus` ou `target` en `na` avec justification |
| Aucun formulaire | `autocomplete` en `na` avec justification |
| Écriture impossible | afficher les résultats console et signaler l'échec |

## Contraintes

- TOUJOURS vérifier Playwright avant les tests.
- TOUJOURS vérifier l'accessibilité HTTP de l'URL.
- TOUJOURS associer chaque résultat à un critère WCAG et à son niveau.
- TOUJOURS produire un rapport, même avec des tests en erreur ou `na`.
- JAMAIS modifier le code source de l'application testée.
- JAMAIS déclarer une conformité WCAG complète depuis ces seuls tests.
- NE PAS masquer les limites : axe-core, tests manuels et jugement humain restent nécessaires.

## Pièges fréquents

- Confondre un test Playwright ciblé avec un audit WCAG complet.
- Arrêter toute la campagne parce qu'un seul test échoue.
- Oublier les cas `na` quand la page n'a pas de formulaire ou d'élément interactif.
- Déclarer `pass` sans mesure observable, sélecteur ou valeur de seuil.
- Écraser des captures précédentes sans nom de fichier descriptif.

## Exemple

```text
Utilisateur : /tests-conformite-wcag https://example.com --tests reflow,focus --screenshots

Assistant :
Phase 0 : Playwright OK. URL accessible (200).
Tests : reflow, focus. Format : md. Captures : oui.

Résultats :
- reflow 1.4.10 AA : fail, scrollWidth 412 px pour un seuil de 320 px
- focus 2.4.7 AA : fail, 3 boutons avec focus non visible

Rapport : CONFORMITE-WCAG-REPORT.md
Captures : conformite-wcag-screenshots/
Avertissement : ce rapport ne prouve pas une conformité WCAG complète.
```

## Checklist finale

- [ ] URL parsée, accessible et affichée.
- [ ] Playwright vérifié avant exécution.
- [ ] Tests sélectionnés exécutés ou marqués `error` / `na`.
- [ ] Chaque résultat pointe vers un critère WCAG et un niveau.
- [ ] Non-conformités listées avec sélecteur, valeur mesurée et seuil.
- [ ] Rapport Markdown ou JSON généré.
- [ ] Captures écrites si `--screenshots` est actif.
- [ ] Avertissement sur les tests manuels inclus.

## Ressources

- [Matrice de couverture](references/coverage-matrix.md)
- [Contrats détaillés des tests](references/test-contracts.md)
