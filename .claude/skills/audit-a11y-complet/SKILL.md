---
name: audit-a11y-complet
description: "Utiliser pour orchestrer un audit accessibilité complet multi-phases : WCAG, RGAA, DSFR, tests non automatisables, arbre a11y, clavier, remédiation ou tickets, scoring /100."
argument-hint: "[url-ou-fichier] [--wcag|--rgaa|--ci|--fix|--tickets]"
allowed-tools: Read, Glob, Grep, Bash, Edit, Write, mcp__chrome-devtools__navigate_page, mcp__chrome-devtools__take_snapshot, mcp__chrome-devtools__evaluate_script, mcp__chrome-devtools__press_key, mcp__accesslint__audit_url, mcp__accesslint__audit_file, mcp__accesslint__audit_html, mcp__accesslint__diff_html, mcp__accesslint__list_rules
context: conversation
---

# Audit d'accessibilité complet

Orchestrer un audit accessibilité complet sans réimplémenter les sous-skills.
Principe central : chaque phase produit un artefact ou un statut explicite, puis
le rapport consolidé agrège preuves, limites et score.

## Déclencheurs

- `/audit-a11y-complet`
- `audit accessibilité complet`
- `audit WCAG + RGAA`
- `audite tout`
- demande mêlant audit automatisé, manuel, DSFR, remédiation ou tickets

NE PAS utiliser pour un audit WCAG seul, un audit RGAA seul, une correction seule
ou la vérification d'un seul critère.

## Arguments et modes

| Argument | Effet |
|---|---|
| `url-ou-fichier` | URL ou fichier HTML cible, obligatoire |
| `--wcag` | phases 1, 3, 4, 5 |
| `--rgaa` | phases 1, 2, 2b, 3, 4, 5 |
| `--ci` | ajoute la phase 6 |
| `--fix` | remédiation rapide : phases 1 et 5 |
| `--tickets` | site tiers : phases 1 à 4 puis tickets |

Sans mode explicite :

1. domaine `.gouv.fr` ou `.service-public.fr` : `--rgaa` ;
2. domaine `.fr` institutionnel : `--rgaa` ;
3. autre domaine ou fichier local : `--wcag`.

Si la cible manque, afficher une erreur d'usage et arrêter.

## Pré-vol

Afficher le plan avant d'exécuter :

```text
[AUDIT COMPLET] Cible : {url-ou-fichier}
[AUDIT COMPLET] Mode  : {wcag|rgaa|fix|tickets}
[AUDIT COMPLET] Phases prévues : {liste}
```

Lire les sous-skills uniquement quand la phase correspondante est active :

- `audit-accessibilite-web`
- `audit-rgaa-dsfr`
- `tests-conformite-wcag`
- `fix-accessibilite`
- `ticket-rgaa`
- `a11y-ci`

En mode `--rgaa` ou `--tickets`, si `git-hors-workflow/ay11-pre-audit` existe
à la racine du workspace, le consulter comme source secondaire de contrats de
preuves et de signaux candidats RGAA.
Ne pas interpréter l'absence de signal AY11 comme une conformité, ni transformer
un signal AY11 en verdict sans preuve complémentaire et validation humaine.

## Phase 1 : audit WCAG automatisé

Utiliser `audit-accessibilite-web` avec niveau AA par défaut.

Sorties attendues :

- `AUDIT-WCAG.md` ;
- score `/100` ;
- nombre de violations et violations critiques ;
- outil réel utilisé : `accesslint MCP`, `axe-core`, `chrome-devtools`,
  `WebFetch` ou autre preuve observable.

Progression :

```text
[AUDIT COMPLET] Phase 1 : Audit WCAG ............... {score}/100 - {n} violations
```

## Phase 1b : scanners secondaires optionnels

Exécuter Pa11y, HTML_CodeSniffer, Lighthouse ou équivalent seulement si
l'utilisateur le demande, si un runner versionné existe dans le projet, ou si le
contexte exige une comparaison multi-outils.

Garde-fous :

- Pa11y : accepter JSON tableau direct ou objet `{ issues }`.
- HTML_CodeSniffer : sérialiser `message.element` seulement si le noeud est un
  élément valide ; garder les messages globaux.
- Playwright : éviter `networkidle` seul sur pages médias.
- Lighthouse : limiter l'interprétation au score et audits accessibilité.
- NE PAS convertir ces signaux en validation des 108 critères RGAA.
- Marquer `IGNORÉE` ou `ECHEC` si aucun runner fiable n'existe.

## Phase 2 : audit RGAA

Active en mode `--rgaa`. Utiliser `audit-rgaa-dsfr`.

Collecter :

- `AUDIT-RGAA.md` ;
- taux de conformité ;
- critères conformes, non conformes ou non applicables ;
- outil réel utilisé.

Si phase inactive, afficher `IGNORÉE`.

## Phase 2b : composants DSFR

Active en mode `--rgaa` ou `--tickets`.

Pour chaque composant DSFR identifié :

- comparer le DOM au markup DSFR de référence ;
- vérifier labels dupliqués, doublons responsive exposés, landmarks `search`,
  IDs, langue, noms accessibles et attributs ARIA ;
- utiliser l'arbre d'accessibilité pour confirmer les noms et rôles.

Ne pas télécharger ou citer plus que nécessaire : noter les écarts prouvés.

## Phase 3 : tests non automatisables

Utiliser `tests-conformite-wcag`.

Collecter :

- tests passés, échoués, non applicables ;
- outil réel : Playwright, chrome-devtools MCP ou analyse statique ;
- limites des tests simulés.

Inactive en mode `--fix`.

## Phase 4 : arbre a11y et clavier

Utiliser directement chrome-devtools MCP, pas un sous-skill lecteur d'écran.

Contrôles minimaux :

- `navigate_page` vers la cible si besoin ;
- `take_snapshot` pour arbre d'accessibilité ;
- titre, `lang`, landmark `main`, liens d'évitement ;
- rôles ARIA, attributs requis, `aria-hidden` sur focusables, régions live,
  références `aria-labelledby` et `aria-describedby` ;
- navigation `Tab` et `Shift+Tab`, ordre logique, focus visible, pièges clavier ;
- widgets : modales, onglets, accordéons, menus.

Rapport : `SCREEN-READER-REPORT.md`, avec limite explicite :
analyse structurelle ARIA, pas de test lecteur d'écran réel VoiceOver/NVDA.

## Phase 5 : remédiation ou tickets

Mode `--fix` ou accès au code :

- utiliser `fix-accessibilite` ;
- partir du rapport WCAG ;
- noter corrections appliquées et corrections proposées.

Mode `--tickets` :

- utiliser `ticket-rgaa` ;
- générer fiches MD et DOCX par défaut confirmé ;
- inclure comparatifs DSFR natif vs site quand utile ;
- ne pas modifier le code du site tiers.

## Phase 6 : intégration CI

Active seulement avec `--ci`. Utiliser `a11y-ci`, passer cible et framework
détecté, puis noter la configuration générée ou la raison d'échec.

## Rapport consolidé

Produire `AUDIT-COMPLET.md` même si certaines phases échouent.

```text
Titre : Rapport audit accessibilité complet
Cible : {url-ou-fichier}
Date : {date}
Référentiel : {WCAG 2.2 AA | WCAG 2.2 AA + RGAA 4.1.2}

Phase 1 : Audit WCAG ............... {score}/100 - {n} violations
Phase 1b : Scanners secondaires ..... {statut}
Phase 2 : Audit RGAA ............... {taux}% ou IGNORÉE
Phase 2b : Composants DSFR ......... {n} écarts ou IGNORÉE
Phase 3 : Tests Playwright ......... {n} passes / {n} échoués
Phase 4 : Arbre a11y + clavier ..... {n} problèmes
Phase 5 : Remédiation/Tickets ...... {n} actions
Phase 6 : Intégration CI ........... {GÉNÉRÉE|IGNORÉE|ECHEC}

Score global : {score}/100
Niveau estimé : {A|AA|AAA|Non conforme}
Violations critiques restantes : {n}
Limites : {phases ignorées ou échouées}
```

Scoring par défaut :

| Phase | Avec RGAA | Sans RGAA |
|---|---:|---:|
| WCAG automatisé | 40 % | 50 % |
| Tests non automatisables | 25 % | 25 % |
| Arbre a11y + clavier | 20 % | 25 % |
| RGAA | 15 % | 0 % |

Redistribuer le poids des phases échouées et le signaler.

## Gestion des échecs

Si une phase échoue :

1. écrire `ECHEC ({raison})` dans le rapport ;
2. continuer les phases indépendantes ;
3. exclure la phase du score et redistribuer le poids ;
4. lister les limites en fin de rapport.

NE PAS masquer un timeout, un outil absent ou un test simulé.

## Exemple

```text
Commande : /audit-a11y-complet https://example.com --wcag

[AUDIT COMPLET] Cible : https://example.com
[AUDIT COMPLET] Mode  : wcag
[AUDIT COMPLET] Phases prévues : 1, 3, 4, 5
[AUDIT COMPLET] Phase 1 : Audit WCAG ............... 72/100 - 8 violations
[AUDIT COMPLET] Phase 2 : Audit RGAA ............... IGNORÉE
[AUDIT COMPLET] Phase 3 : Tests Playwright ......... 7 passes / 2 échoués
[AUDIT COMPLET] Phase 4 : Arbre a11y + clavier ..... 3 problèmes
[AUDIT COMPLET] Phase 5 : Remédiation .............. 5 corrections appliquées
[AUDIT COMPLET] Phase 6 : Intégration CI ........... IGNORÉE

Score global : 68/100
Niveau estimé : Non conforme AA
AUDIT-COMPLET.md généré
```

## Pièges fréquents

- Présenter un scanner secondaire comme verdict RGAA.
- Oublier de marquer une phase inactive `IGNORÉE`.
- Mélanger rapport consolidé et rapports détaillés.
- NE PAS lire le sous-skill actif avant d'exécuter sa phase.
- Modifier un sous-skill au lieu d'orchestrer.
- Conclure à un test lecteur d'écran réel depuis un arbre a11y simulé.
- Calculer un score sans nommer les phases échouées.

## Checklist finale

- [ ] Cible et mode identifiés.
- [ ] Phases prévues affichées.
- [ ] Sous-skills actifs lus avant usage.
- [ ] Chaque phase a un artefact, `IGNORÉE` ou `ECHEC`.
- [ ] Outils réellement utilisés nommés.
- [ ] Score global calculé avec pondération explicite.
- [ ] `AUDIT-COMPLET.md` généré.
- [ ] Aucun sous-skill modifié.
- [ ] Limites manuelles et tests simulés signalés.
