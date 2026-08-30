---
name: audit-accessibilite-web
description: "Utiliser pour auditer l'accessibilité web WCAG 2.2 d'une URL ou d'un fichier HTML avec tests automatisés, checklist POUR et remédiations. Ne pas utiliser pour RGAA dédié, CI/CD, critère unique ou certification légale."
allowed-tools: Read, Glob, Grep, Bash, WebFetch, mcp__chrome-devtools__navigate_page, mcp__chrome-devtools__take_snapshot, mcp__chrome-devtools__take_screenshot, mcp__chrome-devtools__press_key, mcp__chrome-devtools__click, mcp__chrome-devtools__evaluate_script, mcp__accesslint__audit_url, mcp__accesslint__audit_file, mcp__accesslint__list_rules
argument-hint: "[url|fichier] [--level AA|AAA] [--scope page|site] [--principe 1|2|3|4]"
context: conversation
---

# Audit d'accessibilité web

Audits complets d'accessibilité web selon WCAG 2.2 avec tests automatisés, checklist POUR exhaustive et patterns de remédiation actionnables.

## Déclencheurs

- "/audit-a11y", "audite l'accessibilité", "teste l'accessibilité"
- "/wcag-patterns", "checklist WCAG", "vérifie les critères WCAG"
- Toute demande d'audit d'accessibilité web ou de référence WCAG

## Arguments

Les arguments sont passes via `$ARGUMENTS` :

```text
/audit-a11y https://example.com
/audit-a11y https://example.com --level AAA
/audit-a11y https://example.com --scope site
/audit-a11y https://example.com --principe 2
/audit-a11y fichier.html
```

| Argument | Description | Défaut |
|----------|-------------|--------|
| `url` ou `fichier` | URL ou chemin de l'application a auditer | obligatoire |
| `--level` | Niveau WCAG cible (AA ou AAA) | AA |
| `--scope` | Périmètre : page unique ou site entier | page |
| `--principe` | Filtrer par principe POUR (1=Perceptible, 2=Utilisable, 3=Comprehensible, 4=Robuste) | tous |
| `--baseline` | Fichier d'un audit precedent pour comparer les scores | aucun |
| `--referentiel` | Référentiel de sortie : wcag (critères WCAG) ou rgaa (critères RGAA 4.1.2) | wcag |

Si l'URL est manquante, afficher une ERREUR avec le format d'utilisation et arreter.

## Utiliser ce skill quand

- Réalisation d'audits complets d'accessibilité web selon les standards WCAG
- Correction de violations WCAG avec patterns de remédiation
- Implémentation de composants accessibles (formulaires, modales, navigation)
- Préparation à la conformité ADA/Section 508/RGAA
- Identification des barrières d'accessibilité et priorisation de la remédiation

## Ne pas utiliser ce skill quand

- Revues générales d'interface sans focus accessibilité
- Besoin d'un avis juridique ou d'une certification formelle
- Impossible d'examiner l'interface ou le code source

## Workflow

### Phase 0 : parsing des arguments

Analyser `$ARGUMENTS` pour extraire l'URL, le niveau WCAG, le scope et le principe POUR. Si l'URL est manquante, afficher ERREUR et arrêter. Utiliser les valeurs par défaut pour les arguments optionnels non spécifiés.

### Phase 1 : pre-flight

- Vérifier que l'URL est accessible (code HTTP 200) ou que le fichier existe
- Identifier les outils disponibles (axe-core, Lighthouse, navigateur)
- Afficher le niveau WCAG cible (défaut AA, sans demander confirmation)
- Définir le périmètre exact (pages, parcours critiques)
- Si `--principe` spécifié, filtrer la checklist

### Phase 2 : tests automatises

Lire [axe-core-scan-patterns](../a11y-shared-references/axe-core-scan-patterns.md) pour la stratégie de scan (3 niveaux de fallback : @accesslint/mcp, injection CDN, CLI) et la formule de calcul du score.

- Analyser le contraste des couleurs sur les éléments textuels
- Collecter les violations avec impact, critère WCAG et éléments concernés
- Calculer le score d'accessibilité initial et les scores par principe POUR

### Phase 3 : tests manuels par checklist POUR

- Parcourir la checklist du playbook pour chaque principe applicable
- Tester la navigation clavier et vérifier les patterns APG des widgets détectés (Dialog, Combobox, Tabs, etc.) avec `press_key` (voir checklist clavier par widget dans le playbook)
- Vérifier les indicateurs de focus, l'ordre du focus et la compatibilité lecteur d'écran
- Tester les formulaires (labels, erreurs, champs obligatoires)
- Vérifier le contenu dynamique (alertes, mises à jour, modales)

### Phase 4 : cartographie des constats

- Associer chaque violation à un critère WCAG précis (ex: 1.4.3, 2.1.1)
- Attribuer une sévérité : critique, sérieux, modéré ou mineur
- Évaluer l'impact réel sur l'utilisateur
- Regrouper les violations par principe POUR (Perceptible, Utilisable, Comprehensible, Robuste)
- Si `--referentiel rgaa` : utiliser la table [rgaa-mapping](resources/rgaa-mapping.md) pour traduire chaque critère WCAG en critère RGAA. Le rapport cite les numéros RGAA (ex: "Critère 3.2" au lieu de "1.4.3")
- Si `--referentiel rgaa` et si `git-hors-workflow/ay11-pre-audit` existe à la racine du workspace : consulter AY11 comme source secondaire de contrats de preuves et de signaux candidats RGAA. Ne pas interpréter l'absence de signal AY11 comme une conformité, ni transformer un signal AY11 en verdict sans preuve complémentaire et validation humaine.

### Phase 5 : rapport et remédiation

- Produire le rapport structuré avec :
  - **Score global /100** (formule pondérée Phase 2)
  - **Scores par principe POUR** (Perceptible, Utilisable, Comprehensible, Robuste)
  - **Delta** si `--baseline` fourni : comparer avec un audit précédent et afficher la progression
  - Violations et recommandations
- Fournir des exemples de code correctif pour chaque violation
- Prioriser les corrections par sévérité
- Documenter les risques résiduels et le statut de conformité
- Si `--referentiel rgaa` : produire le rapport au format RGAA avec taux de conformité (critères conformes / critères applicables * 100) et références légales

Consulter [implementation-playbook](resources/implementation-playbook.md) pour les checklists détaillées, patterns ARIA et exemples de code.

## Contraintes

- TOUJOURS utiliser le niveau WCAG cible spécifié (défaut AA) sans poser de question
- TOUJOURS inclure des tests manuels en complément des tests automatisés
- TOUJOURS associer chaque violation à un critère WCAG précis
- TOUJOURS fournir un extrait de code correctif pour chaque violation
- JAMAIS déclarer la conformité légale sans revue par un expert
- JAMAIS modifier le code source de l'application pendant l'audit
- JAMAIS se limiter aux tests automatisés (couvrent 30-50% des problèmes)

## Gestion des erreurs

| Scénario | Comportement |
|----------|-------------|
| URL inaccessible | Signaler l'erreur, demander une URL valide |
| Navigateur non disponible | Basculer sur tests manuels et analyse du code source |
| Timeout lors du scan | Réduire le scope, retenter page par page |
| Aucune violation détectée | Confirmer avec tests manuels, documenter le résultat |
| Fichier HTML local introuvable | Vérifier le chemin, demander le bon emplacement |
| Critère WCAG non applicable | Documenter comme "non applicable" avec justification |

## Exemples d'utilisation

### Exemple 1 : audit WCAG AA complet

```text
Utilisateur : /audit-a11y https://example.com

Assistant :
> Phase 1 : URL accessible (200 OK), niveau AA confirmé
> Phase 2 : Scan automatisé — 12 violations détectées
> Phase 3 : Tests manuels — 5 violations supplémentaires
> Phase 4 : Cartographie — 17 violations (3 critiques, 7 sérieuses, 7 modérées)
> Phase 5 : Rapport produit avec score 58/100
>
> Extrait du rapport :
>
> | Critère WCAG | Sévérité | Description | Remédiation |
> |--------------|----------|-------------|-------------|
> | 1.1.1 (A)    | Critique | 3 images sans alt | Ajouter alt descriptif |
> | 1.4.3 (AA)   | Sérieux  | Contraste 2.8:1 sur .nav-link | Passer a #595959 (4.5:1) |
> | 2.4.7 (AA)   | Sérieux  | Focus invisible sur boutons | Ajouter outline: 3px solid |
> | 4.1.2 (A)    | Critique | Role manquant sur dropdown | Ajouter role="combobox" |
```

### Exemple 2 : audit filtre par principe

```text
Utilisateur : /audit-a11y https://example.com --principe 2

Assistant :
> Phase 1 : Filtre actif — Principe 2 (Utilisable) uniquement
> Phase 2 : Scan automatisé — 3 violations clavier détectées
> Phase 3 : Checklist Utilisable — navigation clavier, focus, délais
> Phase 4 : 5 violations (1 critique, 3 sérieuses, 1 modérée)
> Phase 5 : Rapport avec patterns de remédiation clavier
>
> | Critère WCAG | Sévérité | Description | Remédiation |
> |--------------|----------|-------------|-------------|
> | 2.1.1 (A)    | Critique | Dropdown non accessible au clavier | Implementer pattern APG Combobox |
> | 2.4.7 (AA)   | Sérieux  | Focus invisible sur 5 boutons | Ajouter :focus-visible avec outline 3px |
> | 2.4.11 (AA)  | Sérieux  | Focus masqué par header sticky | Ajouter scroll-padding-top |
```

### Exemple 3 : audit WCAG AAA d'un fichier local

```text
Utilisateur : /audit-a11y ./index.html --level AAA

Assistant :
> Phase 1 : Fichier index.html trouvé, niveau AAA (critères renforcés)
> Phase 2 : Analyse du code source — contraste 7:1 requis
> Phase 3 : Checklist complète AAA — espacement, langue, aide contextuelle
> Phase 4 : 10 violations (1 critique, 4 sérieuses, 5 modérées)
> Phase 5 : Rapport avec code correctif pour chaque violation
>
> | Critère WCAG | Sévérité | Description | Remédiation |
> |--------------|----------|-------------|-------------|
> | 1.4.6 (AAA)  | Sérieux  | Contraste 5.2:1 sur .subtitle | Passer a #333 (7.5:1) |
> | 1.4.12 (AA)  | Sérieux  | Perte de contenu avec espacement augmenté | Corriger overflow: hidden |
```

## Pièges fréquents

- Déclarer une conformité légale à partir d'un scan technique.
- Oublier les tests clavier et focus parce qu'axe-core ne remonte plus d'erreur.
- Auditer tout un site sans périmètre de pages ou parcours critiques.
- Fournir des corrections génériques sans extrait de code relié à chaque violation.

## Checklist finale

- [ ] Niveau WCAG cible identifié (AA par défaut ou spécifié par l'utilisateur)
- [ ] 4 principes POUR couverts (ou principe filtré documenté)
- [ ] Tests automatisés exécutés (axe-core, Lighthouse ou analyse du code)
- [ ] Tests manuels effectués (clavier, focus, lecteur d'écran)
- [ ] Chaque violation associée à un critère WCAG précis
- [ ] Sévérité attribuée à chaque violation (critique, sérieux, modéré, mineur)
- [ ] Code correctif fourni pour chaque violation
- [ ] Rapport structuré produit avec score global

## Ressources

- [implementation-playbook](resources/implementation-playbook.md) pour les checklists détaillées, patterns ARIA et exemples de code.
