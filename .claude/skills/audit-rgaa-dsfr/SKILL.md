---
name: audit-rgaa-dsfr
description: "Cadrer un audit RGAA 4.1.2 d'une page ou d'un petit échantillon, avec preuves et fiches bornées. Pour un site multi-pages, utiliser audit-rgaa-creator. Ne produit ni taux officiel ni déclaration."
allowed-tools: Read, Glob, Grep, Bash, WebFetch, Write, Edit
argument-hint: "[url] [--scope page|echantillon] [--theme 1-13|all] [--output rapport|fiches]"
context: conversation
---

# Cadrage RGAA DSFR

Ce skill produit une préqualification RGAA structurée pour une page ou un
petit échantillon. Il distingue les preuves instrumentées, les limites et la
qualification humaine. Pour une campagne multi-pages reprenable, utiliser
`audit-rgaa-creator`.

## Déclencheurs

- Demande de cadrage RGAA sur une page ou un petit échantillon.
- Besoin de regrouper des constats RGAA et DSFR avant une campagne complète.
- Besoin de fiches de non-conformité à partir de constats déjà étayés.

## Ne pas utiliser

- Pour un site multi-pages ou une campagne reproductible : utiliser
  `audit-rgaa-creator`.
- Pour un audit WCAG hors secteur public : utiliser
  `audit-accessibilite-web`.
- Pour une fiche unitaire déjà qualifiée : utiliser `ticket-rgaa`.
- Pour une déclaration d'accessibilité : ce kit peut seulement fournir des
  éléments préparatoires ; la déclaration est validée et signée par un humain.

## Arguments

| Argument | Défaut | Effet |
| --- | --- | --- |
| `url` | requis | page ou point d'entrée à examiner |
| `--scope` | `page` | page ou petit échantillon fourni par l'humain |
| `--theme` | `all` | une thématique RGAA ou toutes les thématiques exercées |
| `--output` | `rapport` | rapport borné ou fiches de constats |

Si l'URL manque, afficher l'utilisation et arrêter. Ne jamais inventer un
échantillon.

## Pré-vol

- Vérifier l'accès à la cible et distinguer un refus du proxy d'une réponse du
  site.
- Afficher la cible, le périmètre, les outils disponibles et les limites.
- Consulter `AY11_ROOT` seulement si cette variable est définie ou si
  `--ay11-root` est fourni. AY11 reste une source secondaire de signaux
  candidats.
- Ne jamais installer un outil ni modifier le site audité.

## Procédure

1. Lire les fiches RGAA de `a11y-shared-references` correspondant aux
   thématiques exercées.
2. Utiliser le meilleur outil disponible : Playwright, axe-core ou une analyse
   structurée du fichier fourni.
3. Conserver pour chaque signal l'URL, le sélecteur, l'extrait, le critère,
   l'outil et le chemin de preuve.
4. Exercer les vérifications manuelles pertinentes : structure, clavier,
   focus, formulaires, contenu dynamique et états responsive.
5. Classer les résultats comme `PASS_CANDIDATE`, `FAIL_CANDIDATE`,
   `A_CONFIRMER`, `REFERENCE_INDISPONIBLE` ou hors périmètre. Une absence de
   signal automatisé ne prouve jamais la conformité.
6. Produire un rapport borné et, si demandé, des fiches avec le skill
   `ticket-rgaa` comme référence de structure, sans l'invoquer en chaîne.

## Sorties autorisées

- rapport de périmètre, outils, preuves, constats et limites ;
- fiches de constats avec critère, preuve, impact et recommandation ;
- tableau des tests exercés et restant à confirmer.

Ne pas produire de taux, de score global, de déclaration ou de claim de
conformité à partir de cette préqualification.

## Statuts

Les statuts de qualification humaine canoniques sont ceux de
`audit-rgaa-complet` : `C_CONFIRMEE`, `NC_CONFIRMEE`, `NA_CONFIRMEE`,
`A_RETESTER` et `NON_TESTE`. Les statuts candidats ci-dessus ne les remplacent
pas.

## Contrôles de fin

- La cible et le périmètre sont nommés.
- Chaque constat possède une preuve ou est marqué à confirmer.
- Les tests non exercés sont visibles.
- Les limites d'AY11, de navigateur, d'authentification et de contenu sont
  explicites.
- Aucun taux, score global ou déclaration n'est présenté comme résultat.
