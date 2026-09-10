---
name: screen-reader-testing
description: "Préqualifier l'accessibilité via l'arbre d'accessibilité et produire une checklist de validation humaine avec NVDA, JAWS ou VoiceOver. L'agent ne pilote pas de lecteur d'écran réel."
allowed-tools: Read, Glob, Grep, Bash, Write, Edit
argument-hint: "[url|fichier] [--lecteur voiceover|nvda|jaws] [--scope page|parcours]"
context: conversation
---

# Préqualification lecteur d'écran

Ce skill inspecte le DOM, l'arbre d'accessibilité, les noms accessibles et le
clavier lorsque l'environnement le permet. Il produit une préqualification,
jamais un test vocal réellement exécuté.

Toute sortie commence ou se termine par :

> Préqualification via arbre d'accessibilité - validation humaine avec NVDA,
> JAWS ou VoiceOver requise.

## Déclencheurs

- « teste avec un lecteur d'écran » ;
- « vérifie la compatibilité lecteur d'écran » ;
- demande explicite de checklist NVDA, JAWS ou VoiceOver.

## Arguments

| Argument | Défaut | Effet |
| --- | --- | --- |
| `url` ou `fichier` | requis | cible à préqualifier |
| `--lecteur` | à choisir par l'humain | cible de la checklist, ne lance aucun logiciel |
| `--scope` | `page` | page ou parcours à préparer |

## Ce que l'agent vérifie

1. accès à la cible, titre, langue, landmark principal et lien d'évitement ;
2. titres, landmarks, liens, boutons, formulaires et noms accessibles dans
   l'arbre ;
3. ordre de tabulation, focus visible et pièges clavier plausibles ;
4. widgets ARIA, modales, messages de statut et changements dynamiques dans le
   DOM et les états observables ;
5. cohérence des preuves : cible, sélecteur, état, viewport et capture si elle
   est disponible.

## Ce que le testeur humain vérifie

Avec NVDA, JAWS ou VoiceOver réellement installé et configuré, le testeur
vérifie les annonces vocales, la navigation par titres et landmarks, les
formulaires, les changements dynamiques, la capture et la restitution du focus,
les modales, les erreurs et le parcours complet. Ces résultats doivent être
ajoutés comme preuves humaines séparées ; l'agent ne les invente pas.

## Workflow

1. Identifier le navigateur, le lecteur cible et la plateforme sans prétendre
   l'avoir exécuté.
2. Charger la cible et prendre un snapshot ou analyser le fichier.
3. Tester d'abord le clavier et les états accessibles observables.
4. Produire une checklist humaine priorisée, avec critère WCAG et preuve
   attendue.
5. Marquer explicitement les étapes non exercées et les limites d'accès.

## Rapport minimal

- cible, navigateur, plateforme et lecteur ciblé ;
- vérifications de l'agent, preuves et limites ;
- checklist du testeur humain ;
- mention obligatoire de préqualification ci-dessus.

## Contraintes

- Ne jamais écrire « NVDA annonce » ou « VoiceOver lit » sans preuve humaine
  fournie par le testeur.
- Ne jamais présenter l'arbre Chromium comme équivalent à un lecteur d'écran.
- Ne jamais exécuter ni documenter un alias personnel de poste.
- Ne jamais déclarer une compatibilité complète avec un seul lecteur.
