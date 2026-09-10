---
name: audit-accessibilite-web
description: "Auditer une page ou un fichier hors campagne selon WCAG 2.2, avec tests automatisés, clavier et remédiations. Utiliser explicitement WCAG ; pour un service public français ou un site multi-pages, router vers audit-rgaa-creator."
allowed-tools: Read, Glob, Grep, Bash, WebFetch, Write, Edit
argument-hint: "[url|fichier] [--level AA|AAA] [--scope page|site] [--principe 1|2|3|4]"
context: conversation
---

# Audit d'accessibilité web WCAG

Ce skill est la voie WCAG explicite pour une page, un fichier ou un périmètre
hors campagne. Il produit des constats et des indicateurs techniques bornés,
pas une conclusion RGAA ou juridique.

## Déclencheurs

- demande explicite d'audit WCAG 2.2 ;
- audit d'une page ou d'un fichier hors secteur public français ;
- vérification d'un principe POUR ou d'un pattern d'accessibilité.

Pour un site public français, une demande RGAA ou un échantillon multi-pages,
utiliser `audit-rgaa-creator`.

## Arguments

| Argument | Défaut | Effet |
| --- | --- | --- |
| `url` ou `fichier` | requis | cible à examiner |
| `--level` | `AA` | niveau WCAG visé |
| `--scope` | `page` | page ou périmètre explicitement fourni |
| `--principe` | tous | filtrer un principe POUR |

Si la cible manque, afficher l'utilisation et arrêter.

## Pré-vol

- Vérifier l'accès à l'URL ou l'existence du fichier.
- Identifier Playwright, axe-core ou le navigateur disponible.
- Afficher le périmètre, le niveau et les limites.
- Ne jamais modifier le site audité.

## Procédure

1. Lire `a11y-shared-references/axe-core-scan-patterns.md`.
2. Exécuter le scan automatisé disponible et conserver URL, sélecteur,
   impact, règle et preuve.
3. Vérifier au clavier les landmarks, titres, focus, formulaires, widgets ARIA
   et états dynamiques pertinents.
4. Associer chaque constat à un critère WCAG précis et à un principe POUR.
5. Proposer une remédiation reliée au code ou à l'élément observé.

Si `--referentiel rgaa` est demandé, ne pas convertir le scan en résultat RGAA :
utiliser `audit-rgaa-creator` ou `audit-rgaa-dsfr`, selon le périmètre, et
présenter au besoin une correspondance candidate sans taux ni référence
juridique automatique.

## Rapport

Le rapport contient :

- cible, niveau, périmètre et outils ;
- violations et résultats manuels séparés ;
- critère WCAG, impact, preuve et recommandation pour chaque constat ;
- couverture, éléments non testés et limites.

Un éventuel score fourni par axe-core est repris comme indicateur de l'outil,
jamais comme score global de conformité.

## Contraintes

- Ne jamais présenter un scan automatisé comme exhaustif.
- Ne jamais produire de taux RGAA, de déclaration ou de claim de conformité.
- Ne jamais confondre absence de violation et conformité.
- Ne jamais lancer un lecteur d'écran réel depuis ce skill ; router la demande
  vers `screen-reader-testing` pour la checklist humaine.
