---
name: pre-audit-rgaa-dsfr
description: "Utiliser quand l'utilisateur demande un pré-audit RGAA DSFR sur une page isolée avec génération en lot de fiches NC/RECO/NOTE au format ticket-rgaa. Ne pas utiliser pour audit multi-pages, ticket unitaire déjà qualifié ou audit WCAG hors secteur public."
allowed-tools: Read, Write, Edit, Glob, Grep, Bash, Bash(agent-browser:*), WebFetch, mcp__chrome-devtools__navigate_page, mcp__chrome-devtools__take_snapshot, mcp__chrome-devtools__take_screenshot, mcp__chrome-devtools__press_key, mcp__chrome-devtools__click, mcp__chrome-devtools__evaluate_script, mcp__chrome-devtools__emulate, mcp__accesslint__audit_url, mcp__accesslint__audit_file, mcp__accesslint__list_rules
argument-hint: "<url> --projet <dossier-projets-actifs> --page <P01> --nom <nom-page> [--skip-scan] [--nc-only]"
context: conversation
---

# Tu es le pré-audit RGAA

Tu es le processus qui scanne une page, identifie tous ses défauts d'accessibilité, les trie et génère les fiches en lot. Tu orchestres le passage entre l'audit global et les tickets individuels.

## Arguments

Extraire de `$ARGUMENTS` : URL (obligatoire), `--projet` (dossier dans `projets-actifs/`), `--page` (identifiant court : P01, P02...), `--nom` (nom affiché de la page). Optionnels : `--skip-scan` (sauter phase 1), `--nc-only` (pas de RECO ni NOTE).

Si un argument obligatoire manque, demander à l'utilisateur.

## Exemple

```text
/pre-audit-rgaa-dsfr https://bo-afa2025.bercy.actimage.net/ --projet specinov-afa --page P01 --nom "Accueil"

[PRE-AUDIT-RGAA] Phase 0/4 : Pré-vol ............... OK
[PRE-AUDIT-RGAA] Phase 1/4 : Scan automatisé ....... OK (3 violations)
[PRE-AUDIT-RGAA] Phase 2/4 : Inspection DOM ......... OK (11 défauts)
  Thématiques non couvertes : 2 (cadres), 3 (couleurs partiellement), 4 (multimédia), 5 (tableaux), 13 (consultation)
[PRE-AUDIT-RGAA] Phase 3/4 : Triage ................ OK

| # | Critère RGAA | Résumé | Sévérité | Type |
|---|-------------|--------|----------|------|
| 1 | 9.1 | Titres cartes h2 au lieu de h3 | Majeur | NC |
| 2 | 1.1 | Images décoratives alt non vide | Majeur | NC |
| 3 | 11.1 | Formulaire recherche sans label visible | Majeur | NC |
| 4 | 6.1 | Lien "Accès rapide 2" placeholder | Majeur | NC |
| 5 | — | URLs partage malformées | — | RECO |
| ... | | | | |

7 NC + 4 RECO + 1 NOTE = 12 fiches. Générer ? [O/n]

[PRE-AUDIT-RGAA] Phase 4/4 : Génération ............ EN COURS
  tickets/accueil/NC-P01-001-formulaire-recherche-etiquette.md ... OK
  tickets/accueil/NC-P01-002-hierarchie-titres-cartes.md ........ OK
  [...]
  12/12 fiches générées dans tickets/accueil/
```

## Gestion d'erreurs

| Scénario | Comportement |
|----------|-------------|
| URL inaccessible (403/timeout) | Fallback navigateur (chrome-devtools MCP ou `agent-browser open`). Si échec des deux : ERREUR, demander URL valide |
| axe-core 0 violation | Continuer vers phase 2 (inspection DOM compense) |
| Snapshot DOM vide ou incomplet (SPA) | Attendre chargement complet via `evaluate_script`. Si échec : NOTE-INTERNE |
| Chrome DevTools MCP non disponible | Basculer sur `agent-browser`. Si les deux absents : marquer phase 2 comme PARTIELLE, lister les vérifications non faites |
| Mapping RGAA introuvable | Avertir, utiliser les critères WCAG en attendant confirmation |
| Tickets existants dans un format inattendu | Ignorer les fichiers non parsables, avertir l'utilisateur |

## Quand ne pas utiliser

- Audit complet multi-pages avec taux de conformité : `/audit-rgaa-dsfr`
- Fiche NC unique à partir d'un défaut déjà identifié : `/ticket-rgaa`
- Audit WCAG hors secteur public : `/audit-accessibilite-web`
- Page déjà auditée via `/audit-rgaa-dsfr` (résultats redondants)

## Références

Avant de commencer, lire les fichiers de référence dans `references/` :

- `references/table-decision-classification.md` : table de décision NC/RECO/NOTE, sévérité, défauts systémiques
- `references/thematiques-rgaa-inspection.md` : checklist d'inspection DOM par thématique RGAA
- `references/faux-positifs-dsfr.md` : patterns de faux positifs, attribution cause racine, screenshots interactifs
- `references/templates-reco-note.md` : templates de fiches RECO, NOTE-INTERNE et NC systémique
- `references/checklist-page-recherche-filtree.md` : checklist spécialisée pour les pages de recherche filtrée (Views Exposed Form, facettes, pagination) — inclut les patterns Drupal/DSFR récurrents

Lire aussi :
- Skill `a11y-shared-references`, fichier `axe-core-scan-patterns.md` : stratégie de scan (3 niveaux de fallback)
- Skill `a11y-shared-references`, fichier `accessible-name-probe.md` : tests unitaires de noms accessibles inspirés de Carnforth
- Skill `ticket-rgaa`, fichier `SKILL.md` : format de référence pour les fiches NC (structure, checklist, conventions)

Source secondaire RGAA locale :

- si `git-hors-workflow/ay11-pre-audit` existe à la racine du workspace, la consulter pour tout pré-audit RGAA comme source de contrats de preuves, profils RGAA, collecteurs HTML/navigateur et signaux candidats ;
- l'utiliser pour tous les critères RGAA concernés, pas seulement pour les formulaires ;
- ne jamais interpréter l'absence de signal AY11 comme une conformité ;
- ne jamais transformer un signal AY11 en NC, RECO ou NOTE sans preuve DOM, arbre d'accessibilité, outil ou validation humaine.

## Sources de référence DSFR

Pour chaque composant DSFR détecté sur la page, deux sources canoniques à consulter :

| Source | Chemin GitHub | Contenu |
|--------|--------------|---------|
| Template EJS | `src/dsfr/component/{composant}/template/ejs/{composant}.ejs` | Markup de référence, attributs ARIA attendus |
| Doc accessibilité | `src/dsfr/component/{composant}/_part/doc/accessibility/index.md` | Règles d'accessibilité, comportement attendu lecteur d'écran |

### Stratégie de récupération (3 niveaux)

1. **WebFetch** sur `https://www.systeme-de-design.gouv.fr/composants-et-modeles/composants/{composant}/` — souvent bloqué par Cloudflare (403)
2. **GitHub API** (fallback principal) : `gh api repos/GouvernementFR/dsfr/contents/{chemin} --jq '.content' | base64 -d` — fiable, pas de WAF
3. **Sources locales** dans `opensrc/` si synchronisées via `/opensrc-sync`

En pratique, le niveau 2 (GitHub API) est le plus fiable. Toujours récupérer **le template ET la doc accessibilité** — ils peuvent diverger (ex : le template `tag.ejs` génère `<p>` dans un `<li>`, mais la doc accessibilité recommande `<span>`).

### Composants courants et chemins

```
pagination    → template/ejs/pagination-item.ejs
tag           → template/ejs/tag.ejs + tags-group.ejs
toggle        → template/ejs/toggle.ejs
search (bar)  → template/ejs/search.ejs
card          → template/ejs/card.ejs
header        → template/ejs/header.ejs
navigation    → template/ejs/navigation.ejs
```

## Outils navigateur

Deux options pour interagir avec la page. Choisir selon la disponibilité :

### Option A : chrome-devtools MCP (prioritaire)

Outils MCP directs, plus rapides pour les opérations unitaires :

| Action | Commande |
|--------|----------|
| Naviguer | `mcp__chrome-devtools__navigate_page` |
| Snapshot DOM / arbre a11y | `mcp__chrome-devtools__take_snapshot` |
| Screenshot | `mcp__chrome-devtools__take_screenshot` |
| Cliquer (ouvrir modale, menu) | `mcp__chrome-devtools__click` |
| Tabuler (test focus) | `mcp__chrome-devtools__press_key` |
| Injecter axe-core CDN | `mcp__chrome-devtools__evaluate_script` |
| Émuler mobile | `mcp__chrome-devtools__emulate` |

### Option B : agent-browser (fallback ou complément)

CLI Playwright via Bash. Utiliser si chrome-devtools MCP n'est pas disponible, ou en complément pour les interactions complexes (formulaires multi-étapes, navigation par refs, séquences clavier élaborées) :

```bash
agent-browser open <url>                    # Naviguer
agent-browser snapshot -i                   # Éléments interactifs avec refs @e1, @e2...
agent-browser click @e1                     # Cliquer par ref
agent-browser press Tab                     # Tester la navigation clavier
agent-browser screenshot chemin.png         # Capturer l'état
agent-browser set device "iPhone 14"        # Émuler mobile
agent-browser eval "document.title"         # Exécuter du JS (injection axe-core)
agent-browser get attr @e1 aria-label       # Lire un attribut ARIA
agent-browser get html @e1                  # Extraire le HTML d'un composant
agent-browser is visible @e1                # Vérifier la visibilité
agent-browser close                         # Fermer
```

### Stratégie de choix

1. **Essayer chrome-devtools MCP d'abord** (plus léger, intégré)
2. Si MCP indisponible ou si l'interaction échoue → basculer sur `agent-browser`
3. Pour les **screenshots d'états interactifs** (modale ouverte, focus visible) : `agent-browser` est souvent plus fiable car il gère les refs et les séquences click → wait → screenshot en une chaîne
4. Pour l'**injection axe-core** : `evaluate_script` (MCP) ou `agent-browser eval` — même résultat

## Workflow

### Phase 0 : pré-vol

1. Vérifier que l'URL est accessible (HTTP 200 ou fallback navigateur si WAF — voir § Outils navigateur)
2. Créer `projets-actifs/{projet}/tickets/{nom-page-kebab}/` si absent
3. Scanner les tickets existants pour cette page (éviter les doublons)
4. Scanner les tickets des AUTRES pages pour détecter les défauts systémiques potentiels
5. Afficher : `[PRE-AUDIT-RGAA] Phase 0/4 : Pré-vol ............... OK`

### Phase 1 : scan automatisé (sauf si `--skip-scan`)

1. Scanner via axe-core selon la stratégie de `axe-core-scan-patterns.md`
2. Mapper les violations vers les critères RGAA via `resources/rgaa-mapping.md` du skill `audit-accessibilite-web`
3. Collecter : critère RGAA, élément DOM, code source fautif, sévérité axe
4. Afficher : `[PRE-AUDIT-RGAA] Phase 1/4 : Scan automatisé ............... OK (N violations)`

### Phase 2 : inspection DOM et arbre d'accessibilité

Les tests automatisés couvrent 30-50 % des critères RGAA. Cette phase complète via 4 sous-étapes.

#### 2a. Snapshot DOM et arbre d'accessibilité

1. Naviguer sur la page : `navigate_page` (MCP) ou `agent-browser open <url>`
2. Prendre un snapshot : `take_snapshot` (MCP) ou `agent-browser snapshot -i`
3. Appliquer la référence `accessible-name-probe.md` comme catalogue de tests unitaires : une cible, une assertion, une preuve, un `unit_id`. Couvrir images, SVG, `role="img"`, champs, radios, selects, fieldsets, formulaires, boutons, liens, zones d'image map, landmarks, widgets ARIA, dialogues, iframes, médias, `progress`, `meter` et éléments focusables par `tabindex`.
4. **Analyser l'arbre d'accessibilité** (pas seulement le DOM) pour détecter :
   - Noms accessibles dupliqués (double `<label for>` → nom concaténé, ex : `"Texte Texte"`)
   - Rôles manquants ou incorrects (ex : `<a>` sans `href` exposé comme `generic` au lieu de `link`)
   - Contenu parasite (placeholder, "Lorem ipsum", texte de test exposé aux technologies d'assistance)
   - Légendes de fieldset dupliquées dans l'arbre (ex : `"Par public Par public"`)
   - Éléments avec `aria-label` sur un rôle qui ne le supporte pas

#### 2b. Vérification des composants DSFR

Pour chaque composant DSFR identifié sur la page :

1. Récupérer le template et la doc accessibilité via GitHub API (voir § Sources de référence DSFR)
2. Comparer le DOM du site au markup de référence — attribut par attribut
3. Vérifier les faux positifs via `references/faux-positifs-dsfr.md`
4. Distinguer systématiquement : **défaut DSFR natif** (le template lui-même est incorrect) vs **défaut d'intégration CMS** (le template est correct mais le CMS ne le respecte pas)

#### 2c. Vérification de cohérence responsive (formulaires dupliqués)

Pattern courant sur les sites Drupal (Views Exposed Form) : le même formulaire est dupliqué pour gérer mobile et desktop. Vérifier systématiquement :

1. **Détecter les formulaires dupliqués** : `evaluate_script` pour lister tous les `<form>` et leurs IDs. Si deux formulaires partagent la même `action` et les mêmes champs (avec suffixe `--2`), c'est un doublon responsive
2. **Comparer les labels** (11.3 — cohérence) : les champs de même fonction doivent avoir la même étiquette dans les deux variantes
3. **Vérifier le masquage pour les technologies d'assistance** (10.8) : le formulaire non destiné au viewport courant doit être masqué via `display: none` (ou `hidden` / `aria-hidden="true"`). Vérifier sur **chaque élément enfant**, pas seulement le `<form>` parent — un formulaire peut être visible mais certains enfants masqués
4. **Vérifier l'unicité des IDs** (8.2) : aucun ID ne doit être dupliqué entre les deux formulaires
5. **Vérifier les landmarks** (12.6) : si les deux formulaires contiennent `role="search"`, vérifier qu'ils ont des `aria-label` distincts

#### 2d. Inspection thématique et captures

1. Vérifier chaque famille de thématiques selon `references/thematiques-rgaa-inspection.md`. **Si la page est une page de recherche filtrée** (présence de formulaire de filtres, pagination, résultats structurés), utiliser en complément `references/checklist-page-recherche-filtree.md` qui couvre les critères spécifiques (11.3 cohérence labels, 10.8 masquage responsive, 7.5 messages de statut, etc.) et les patterns Drupal récurrents
2. Prendre des screenshots d'états interactifs (modales ouvertes, menu déployé, focus visible) — pas seulement au chargement
3. Détecter les coquilles HTML (attributs suspects par distance de Levenshtein) et orthographiques
4. Détecter les contenus en langue étrangère non balisés (labels CMS non traduits, `title` anglais) → 8.7
5. Afficher l'avertissement sur les thématiques non couvertes (2, 3 partiellement, 4, 5, 13)
6. Afficher : `[PRE-AUDIT-RGAA] Phase 2/6 : Inspection DOM + a11y tree ... OK (N défauts)`

### Phase 3 : triage et validation utilisateur

1. Consolider les résultats des phases 1 et 2
2. Dédupliquer (un même défaut détecté par axe-core ET par l'inspection DOM)
3. Classifier chaque défaut selon `references/table-decision-classification.md`
4. Détecter les défauts systémiques (même critère + cause racine que tickets existants d'autres pages)
5. Trier par sévérité (Bloquant > Majeur > Mineur) puis par thématique RGAA
6. Afficher le tableau de triage :

```
| # | Critère RGAA | Résumé | Sévérité | Type |
|---|-------------|--------|----------|------|
```

7. Afficher le décompte : `N NC + N RECO + N NOTE = N fiches à générer.`
8. **ATTENDRE la validation de l'utilisateur** (il peut retirer des faux positifs, ajuster des sévérités, ajouter des défauts manqués)
9. Afficher : `[PRE-AUDIT-RGAA] Phase 3/4 : Triage ............... OK`

### Phase 4 : génération en lot

**Stratégie anti-érosion** : écrire chaque fiche sur disque immédiatement après génération (pas en lot à la fin).

1. Pour chaque NC validée : générer la fiche en **adoptant le format** de `/ticket-rgaa` (même structure de sections, mêmes conventions de nommage, même checklist). Ne PAS invoquer `/ticket-rgaa` via Skill tool. Inclure le tableau comparatif DSFR natif vs site audité si un composant DSFR est concerné. Écrire immédiatement dans `tickets/{nom-page-kebab}/`
2. Pour chaque RECO (sauf si `--nc-only`) : générer une fiche au format allégé selon `references/templates-reco-note.md`. Écrire immédiatement
3. Pour chaque NOTE-INTERNE (sauf si `--nc-only`) : générer une fiche de vérification selon `references/templates-reco-note.md`. Écrire immédiatement
4. Nommage : `NC-{PAGE}-{NUM}-{slug}.md`, `RECO-{PAGE}-{NUM}-{slug}.md`, `NOTE-INTERNE-{PAGE}-{slug}.md`
5. Après chaque tranche de 5 fiches : afficher la progression et proposer un commit intermédiaire
6. Mettre à jour l'index d'audit (`audit-rgaa-index-*.md`) dans le dossier projet
7. Afficher le bilan final avec la liste des fiches générées

### Phase 4b : vérification post-génération

Pour chaque ticket généré en phase 4, vérifier le constat contre le DOM live :

1. Re-vérifier l'extrait de code source cité : est-il exact et complet ?
2. Re-vérifier la portée : le défaut concerne-t-il tous les éléments annoncés ou seulement certains ? (ex : `aria-label` uniquement sur `--first`, pas sur `--prev`)
3. Re-vérifier les attributs DSFR attendus vs présents : le tableau comparatif est-il fidèle ?
4. Si une imprécision est détectée : corriger le ticket immédiatement avant de passer au suivant

Cette phase est rapide (1-2 vérifications DOM par ticket) mais évite les tickets imprécis qui perdent en crédibilité face à l'auditeur.

### Phase 5 : intégration retour expert (optionnelle)

Si un retour d'auditeur RGAA enrichit les constats après la génération initiale :

1. Lister les critères ou qualifications supplémentaires apportés par l'expert
2. Pour chaque ticket impacté : ajouter les critères, mettre à jour les en-têtes, enrichir l'analyse
3. Si le retour révèle de nouveaux défauts non couverts : créer les tickets manquants
4. Régénérer les DOCX des tickets modifiés
5. Afficher : `[PRE-AUDIT-RGAA] Phase 5/6 : Retour expert ............... OK (N tickets enrichis, M nouveaux)`

## Pièges fréquents

| Piège | Risque | Correction |
|---|---|---|
| Générer avant validation phase 3 | Faux positifs transformés en tickets officiels | Attendre l'accord utilisateur sur la liste triée |
| Confondre défaut DSFR natif et intégration CMS | Ticket injuste ou non actionnable | Comparer template DSFR, doc accessibilité et DOM réel |
| NE PAS vérifier le DOM après génération | Ticket imprécis face à l'auditeur | Rejouer phase 4b pour chaque fiche |
| Chaîner `/ticket-rgaa` comme skill séparé | Perte de contexte et format incohérent | Adopter son format localement |

## Contraintes impératives

- TOUJOURS vérifier le comportement DSFR natif avant de classer un composant DSFR en NC (règle anti-faux-positif)
- TOUJOURS inclure un tableau comparatif DSFR natif vs site audité pour les NC sur composants DSFR
- TOUJOURS attendre la validation utilisateur entre phase 3 et phase 4
- TOUJOURS écrire chaque fiche sur disque immédiatement (pas de batch en fin de workflow)
- TOUJOURS distinguer défaut DSFR natif vs défaut d'intégration CMS dans l'attribution de cause racine
- JAMAIS invoquer `/ticket-rgaa` via Skill tool (adopter son format, ne pas le chaîner)
- JAMAIS générer de ticket pour un comportement conforme au design system DSFR
- TOUJOURS accentuer le français dans les fiches générées (é, è, ê, à, ç, ù, etc.) — les rules globales ne suffisent pas en génération lot, le rappel ici est nécessaire

## Checklist finale

- [ ] Toutes les fiches écrites sur disque dans `tickets/{page}/md/`
- [ ] DOCX générés dans `tickets/{page}/docx/` (1:1 avec les MD)
- [ ] Fiches NC conformes au format `/ticket-rgaa` (structure, tableau DSFR, références)
- [ ] Sources DSFR citées (template EJS + doc accessibilité GitHub) pour chaque NC sur composant DSFR
- [ ] Arbre d'accessibilité analysé (noms dupliqués, rôles manquants, contenu parasite)
- [ ] Cohérence responsive vérifiée si formulaires dupliqués détectés (11.3, 10.8, 8.2, 12.6)
- [ ] Chaque ticket vérifié contre le DOM live après génération (phase 4b)
- [ ] Décompte final affiché (N NC + N RECO + N NOTE)
- [ ] Index `audit-rgaa-index-*.md` mis à jour
- [ ] Thématiques non couvertes signalées (2, 3 partiellement, 4, 5, 13)
- [ ] Aucun ticket généré pour un comportement DSFR natif conforme
- [ ] Défauts systémiques inter-pages détectés et référencés
