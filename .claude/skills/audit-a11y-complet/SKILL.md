---
name: audit-a11y-complet
description: "Orchestrer un audit accessibilité multi-phases combinant WCAG, RGAA, DSFR, tests clavier et remédiation. Pour une campagne RGAA multi-pages reprenable, utiliser audit-rgaa-creator. Ne produit aucun score global ni taux RGAA."
allowed-tools: Read, Glob, Grep, Bash, Edit, Write
argument-hint: "[url-ou-fichier] [--wcag|--rgaa|--fix|--tickets]"
context: conversation
---

# Audit d'accessibilité complet

Ce skill orchestre des vérifications d'accessibilité et rassemble leurs
preuves. Chaque phase garde son statut, ses limites et ses constats ; aucune
phase ne transforme un signal automatisé en conformité réglementaire.

## Déclencheurs

- `audit accessibilité complet` lorsque plusieurs familles de tests sont
  demandées ;
- une demande combinant WCAG, RGAA, DSFR, clavier et remédiation ;
- une demande d'orchestration hors campagne `audit-rgaa-creator`.

Pour un site public multi-pages ou une campagne reprenable, router vers
`audit-rgaa-creator`.

## Arguments

| Argument | Effet |
| --- | --- |
| `url-ou-fichier` | cible obligatoire |
| `--wcag` | vérifications WCAG 2.2 et checklist POUR |
| `--rgaa` | préqualification RGAA avec limites explicites |
| `--fix` | préparer des corrections à partir de preuves existantes |
| `--tickets` | structurer des fiches à partir de constats qualifiés |

Sans mode, choisir WCAG pour une cible générique et router une cible de
service public vers `audit-rgaa-creator`.

## Pré-vol

Afficher la cible, le mode, les phases prévues et les outils disponibles.
Consulter `AY11_ROOT` si la variable est définie ; son absence est une limite,
jamais une preuve favorable. Ne jamais modifier un site tiers pendant l'audit.

## Phases

1. **Préparation** - vérifier la cible, le périmètre et la disponibilité du
   navigateur.
2. **Inspection automatisée** - exécuter axe-core ou l'outil disponible et
   conserver les sélecteurs, impacts et preuves.
3. **Inspection manuelle** - exercer clavier, focus, structure, formulaires,
   états dynamiques et patterns ARIA pertinents.
4. **Préqualification RGAA ou WCAG** - associer chaque signal à une règle et
   séparer les correspondances candidates des décisions humaines.
5. **Remédiation ou fiches** - proposer des changements reliés aux preuves ;
   ne modifier le code que si l'utilisateur fournit le dépôt et le demande.

Chaque phase est marquée `OK`, `PARTIEL`, `ECHEC` ou `IGNORÉ`, avec les tests
effectivement exercés et ceux qui restent à faire.

## Contrat des résultats

- Un score axe éventuel est un indicateur technique de l'outil, jamais un taux
  RGAA ni un verdict global.
- Une correspondance WCAG-RGAA est candidate tant qu'elle n'est pas vérifiée
  contre le test RGAA et une preuve humaine.
- Pour le RGAA, utiliser les statuts de `audit-rgaa-complet` :
  `C_CONFIRMEE`, `NC_CONFIRMEE`, `NA_CONFIRMEE`, `A_RETESTER` et `NON_TESTE`.
- Pour le DSFR, conserver les statuts de `audit-dsfr-complet` séparément.
- Les sorties indiquent toujours la couverture, les inconnus et les limites.

## Ressources

Lire seulement les références nécessaires :

- `a11y-shared-references/axe-core-scan-patterns.md` pour les replis ;
- `audit-accessibilite-web/resources/rgaa-mapping.md` pour une correspondance
  candidate ;
- `tests-conformite-wcag` pour les vérifications responsive et clavier ;
- `screen-reader-testing` pour la préqualification de l'arbre d'accessibilité
  et la checklist humaine.

## Fin de traitement

- La cible, le périmètre et les outils sont documentés.
- Les résultats automatisés et manuels sont séparés.
- Les signaux non confirmés restent visibles.
- Aucun score global, taux RGAA ou déclaration n'est produit par ce skill.
