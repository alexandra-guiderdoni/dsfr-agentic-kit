---
name: screen-reader-testing
description: "Utiliser pour pré-qualifier l'accessibilité via l'arbre d'accessibilité (ARIA, rôles, noms accessibles, ordre de tabulation) et produire une checklist à vérifier par un testeur humain au lecteur d'écran. L'agent ne pilote pas NVDA, JAWS ni VoiceOver."
allowed-tools: Read, Glob, Grep, Bash, mcp__chrome-devtools__navigate_page, mcp__chrome-devtools__take_snapshot, mcp__chrome-devtools__take_screenshot, mcp__chrome-devtools__press_key, mcp__chrome-devtools__click, mcp__chrome-devtools__evaluate_script
argument-hint: "[url|fichier] [--lecteur voiceover|nvda|jaws] [--scope page|parcours]"
context: conversation
---

# Tests avec lecteur d'écran

Guide pratique pour tester les applications web avec les lecteurs d'écran et
valider l'accessibilité de manière exhaustive.

## Limite fondamentale — à lire avant tout

Un agent **ne peut pas piloter** NVDA, JAWS ni VoiceOver : ces logiciels ne
sont pas automatisables depuis cet environnement. Ce que l'agent peut faire :
inspecter l'**arbre d'accessibilité** exposé par `chrome-devtools`
(`take_snapshot`), lire les attributs ARIA, les rôles, les noms accessibles et
l'ordre de tabulation.

En conséquence, deux registres à ne jamais confondre :

- **Ce que l'agent produit** = une analyse de l'arbre d'accessibilité et une
  **checklist à faire vérifier par un testeur humain** avec un vrai lecteur
  d'écran. C'est une pré-qualification, jamais un verdict lecteur d'écran.
- **Interdit** : écrire « NVDA annonce X », « VoiceOver lit Y », « le lecteur
  d'écran signale Z », ou tout résultat présenté comme observé sur un lecteur
  d'écran réel. L'agent ne l'a pas exécuté ; l'affirmer est une fabrication.

Toute sortie de ce skill est étiquetée « pré-qualification via arbre
d'accessibilité — vérification humaine au lecteur d'écran requise ».

## Déclencheurs

- "/screen-reader-test", "teste avec lecteur d'écran", "test VoiceOver"
- "vérifie la compatibilité lecteur d'écran", "test NVDA", "test JAWS"
- Toute demande de validation d'accessibilité via lecteur d'écran

## Arguments

Les arguments sont passés via `$ARGUMENTS` :

```text
/screen-reader-test https://example.com
/screen-reader-test https://example.com --lecteur nvda
/screen-reader-test fichier.html --scope parcours
```

| Argument | Description | Defaut |
|----------|-------------|--------|
| `url` ou `fichier` | URL ou chemin de l'application à tester | obligatoire |
| `--lecteur` | Lecteur d'écran cible (voiceover, nvda, jaws) | voiceover (macOS) |
| `--scope` | Périmètre : page unique ou parcours utilisateur | page |

Si l'URL est manquante, afficher une ERREUR avec le format d'utilisation et
arrêter. `--lecteur` ne lance aucun logiciel : il indique seulement pour quel
lecteur d'écran la checklist humaine devra être menée.

## Utiliser ce skill quand

- Validation de la compatibilité lecteur d'écran sur un site ou une application
- Test des implémentations ARIA (rôles, états, propriétés)
- Débogage de problèmes avec les technologies d'assistance
- Verification de l'accessibilite des formulaires (labels, erreurs, champs obligatoires)
- Test des annonces de contenu dynamique (modales, alertes, mises a jour live)
- Validation de la navigation clavier et de l'ordre du focus

## Ne pas utiliser ce skill quand

- Travail hors du périmètre des tests d'accessibilité
- Besoin d'un audit WCAG complet (utiliser `audit-accessibilite-web`)
- Impossible d'accéder à l'interface ou au code source

## Workflow

### Phase 0 : analyse des arguments

Analyser `$ARGUMENTS` pour extraire l'URL, le lecteur d'écran et le scope. Si
l'URL est manquante, afficher ERREUR et arrêter. Auto-détecter le lecteur
d'écran selon la plateforme (voiceover sur macOS, nvda sur Windows) si non
spécifié.

### Phase 1 : préparation

- Identifier le lecteur d'écran disponible sur la plateforme (VoiceOver sur macOS, NVDA/JAWS sur Windows)
- Vérifier que l'URL est accessible (navigate_page) ou que le fichier existe
- Prendre un snapshot initial de la page (take_snapshot) pour analyser l'arbre d'accessibilite
- Définir le périmètre (page unique ou parcours utilisateur)

### Phase 2 : test de chargement

- Vérifier que le titre de la page est annoncé
- Vérifier la présence du landmark principal (`<main>`)
- Tester le lien d'évitement (skip link)
- Vérifier la langue de la page (`lang`)

### Phase 3 : navigation et interaction

- Tester la navigation par titres (rotor VoiceOver, H dans NVDA)
- Vérifier les landmarks (banner, main, contentinfo, nav)
- Tester tous les liens et boutons (annonce du rôle et de la fonction)
- Identifier les widgets ARIA et verifier leurs interactions clavier contre le pattern APG correspondant (consulter la spec officielle : <https://www.w3.org/WAI/ARIA/apg/patterns/>)
- Utiliser `press_key` pour les tests clavier, pas `dispatchEvent`
- Tester les formulaires (labels lus, champs obligatoires annoncés, erreurs)
- Vérifier l'ordre du focus et l'absence de pièges clavier

### Phase 4 : contenu dynamique

- Tester les modales (capture et restauration du focus)
- Vérifier les alertes et messages de statut (régions live)
- Tester les mises à jour de contenu (aria-live)
- Vérifier les onglets, accordéons et widgets personnalisés

### Phase 5 : rapport

- Lister les problèmes détectés avec critère WCAG associé
- Attribuer une sévérité (critique, sérieux, modéré, mineur)
- Fournir un extrait de code correctif pour chaque problème
- Documenter le lecteur d'écran, navigateur et plateforme utilisés

Consulter [implementation-playbook](resources/implementation-playbook.md) pour
les commandes détaillées de chaque lecteur d'écran et les checklists de test.

## Contraintes

- TOUJOURS tester d'abord au clavier seul avant d'utiliser le lecteur d'écran
- TOUJOURS tester en mode parcours ET en mode focus/formulaires
- TOUJOURS vérifier la gestion du focus (capture, restauration, ordre)
- TOUJOURS documenter le lecteur d'écran et navigateur utilisés
- JAMAIS se limiter à un seul lecteur d'écran pour une validation complète
- JAMAIS ignorer le contenu dynamique (source des problèmes les plus courants)
- JAMAIS se fier uniquement aux tests visuels (expérience différente)

## Gestion des erreurs

| Scenario | Comportement |
|----------|-------------|
| VoiceOver non disponible (Windows/Linux) | Basculer sur NVDA ou analyse de l'arbre d'accessibilite via DevTools |
| Lecteur d'écran demandé non installé | Signaler l'absence, proposer une alternative disponible |
| Composant non testable par lecteur d'écran | Analyser le code source et l'arbre ARIA via DevTools |
| URL inaccessible | Signaler l'erreur, demander une URL valide |
| Fichier HTML local introuvable | Vérifier le chemin, demander le bon emplacement |

## Exemples d'utilisation

> Rappel : les sorties ci-dessous sont des **pré-qualifications via l'arbre
> d'accessibilité**. Les colonnes de remédiation sont détectables sans lecteur
> d'écran ; toute annonce vocale reste à confirmer par un testeur humain.

### Exemple 1 : test VoiceOver sur une page

```text
Utilisateur : /screen-reader-test https://example.com

Assistant :
> Phase 1 : arbre d'accessibilité chargé via DevTools (pas d'exécution VoiceOver)
> Phase 2 : titre exposé dans l'arbre, landmark main présent, skip link OK
> Phase 3 : 3 problèmes détectés (titres, formulaire, bouton)
> Phase 4 : modale sans capture de focus, alerte sans role live (annonce à confirmer au lecteur d'écran)
> Phase 5 : Rapport produit — 5 problèmes (1 critique, 3 sérieux, 1 modéré)
>
> Extrait du rapport :
>
> | Critère WCAG | Sévérité | Description | Remédiation |
> |--------------|----------|-------------|-------------|
> | 4.1.2 (A)    | Critique | Bouton SVG sans nom accessible | Ajouter aria-label="Fermer" |
> | 1.3.1 (A)    | Sérieux  | Formulaire sans labels associés | Ajouter <label for="..."> |
> | 2.4.3 (A)    | Sérieux  | Modale sans capture de focus | Ajouter aria-modal="true" + focus trap |
> | 4.1.3 (AA)   | Sérieux  | Alerte non annoncée | Ajouter role="alert" aria-live="assertive" |
```

### Exemple 2 : test d'un formulaire

```text
Utilisateur : /screen-reader-test https://example.com/contact --scope parcours

Assistant :
> Phase 1 : arbre d'accessibilité, parcours : remplissage du formulaire de contact (pas d'exécution VoiceOver)
> Phase 2 : page chargée, titre exposé dans l'arbre
> Phase 3 : Labels lus, 2 champs sans indication de format
> Phase 4 : message de succès sans role live après soumission (annonce à confirmer)
> Phase 5 : 3 problèmes (0 critique, 2 sérieux, 1 modéré)
>
> | Critère WCAG | Sévérité | Description | Remédiation |
> |--------------|----------|-------------|-------------|
> | 3.3.2 (A)    | Sérieux  | Champ téléphone sans indication de format | Ajouter aria-describedby avec format attendu |
> | 4.1.3 (AA)   | Sérieux  | Message de succès non annoncé | Ajouter role="status" aria-live="polite" |
```

### Exemple 3 : test d'une modale

```text
Utilisateur : /screen-reader-test fichier.html --lecteur nvda

Assistant :
> Phase 1 : fichier trouvé, arbre d'accessibilité analysé (aucune exécution NVDA — pré-qualification)
> Phase 2 : Structure HTML analysée
> Phase 3 : Navigation OK, landmarks présents
> Phase 4 : Modale sans role="dialog", focus non capture, Echap inactif
> Phase 5 : 3 problèmes critiques sur la modale avec code correctif
>
> | Critère WCAG | Sévérité | Description | Remédiation |
> |--------------|----------|-------------|-------------|
> | 4.1.2 (A)    | Critique | Modale sans role="dialog" | Ajouter role="dialog" aria-modal="true" |
> | 2.4.3 (A)    | Critique | Focus non capturé dans la modale | Implémenter focus trap (pattern APG Dialog) |
> | 2.1.1 (A)    | Critique | Echap ne ferme pas la modale | Ajouter keydown handler pour Escape |
```

## Pièges fréquents

- NE PAS présenter un test DevTools comme équivalent à un vrai test lecteur
  d'écran quand le lecteur cible n'a pas été utilisé.
- NE PAS se limiter au chargement initial : les modales, alertes, erreurs et
  mises à jour live doivent être testées.
- NE PAS oublier le clavier seul avant le lecteur d'écran.
- JAMAIS déclarer une compatibilité complète avec un seul lecteur d'écran.

## Dogfooding : valider l'outil lui-même (Claude Code)

Ce skill teste les **livrables** au lecteur d'écran. En miroir, pour vérifier que
**l'outil** (Claude Code) reste utilisable au lecteur d'écran — cohérence avec
la doctrine a11y — lancer une session en mode lecteur d'écran, puis activer
VoiceOver (`Cmd+F5` sur macOS) :

```bash
claude-a11y   # alias = command claude --ax-screen-reader (cf. ~/.zshrc)
```

Le mode `--ax-screen-reader` (Claude Code 2.1.208+) linéarise l'UI : spinners,
couleurs et redraws animés désactivés, focus suivi par le curseur terminal.
**Périmètre distinct** des tests de livrables : c'est le dogfooding de
l'outillage, pas un substitut au test du site cible.

## Checklist finale

- [ ] Lecteur d'écran et navigateur identifiés et documentés
- [ ] Test clavier seul effectué avant le lecteur d'écran
- [ ] Chargement de page vérifié (titre, landmark, skip link)
- [ ] Navigation par titres et landmarks testée
- [ ] Formulaires testés (labels, erreurs, champs obligatoires)
- [ ] Contenu dynamique vérifié (modales, alertes, mises à jour)
- [ ] Chaque problème associé à un critère WCAG précis
- [ ] Code correctif fourni pour chaque problème

## Ressources

- [implementation-playbook](resources/implementation-playbook.md) pour les
  commandes détaillées de chaque lecteur d'écran, checklists et exemples de code.
