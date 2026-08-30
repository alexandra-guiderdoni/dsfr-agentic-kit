---
name: audit-rgaa-dsfr
description: Utiliser quand il faut auditer un site public français selon le RGAA 4.1.2, calculer le taux de conformité et produire rapport, déclaration ou fiches de non-conformité.
allowed-tools: Read, Glob, Grep, Bash, WebFetch, mcp__chrome-devtools__navigate_page, mcp__chrome-devtools__take_snapshot, mcp__chrome-devtools__take_screenshot, mcp__chrome-devtools__press_key, mcp__chrome-devtools__click, mcp__chrome-devtools__evaluate_script, mcp__accesslint__audit_url, mcp__accesslint__audit_file, mcp__accesslint__list_rules
argument-hint: "[url] [scope page|échantillon] [thème 1-13|all] [sortie rapport|déclaration|fiches]"
context: conversation
---

# Audit RGAA DSFR

Réaliser un audit RGAA 4.1.2 complet ou ciblé : 106 critères, 13 thématiques,
taux de conformité officiel et livrables réglementaires pour un service public.

## Déclencheurs

- Demande d'audit RGAA, conformité légale, déclaration d'accessibilité ou taux
  de conformité.
- Site public français, service `.gouv.fr`, DSFR ou démarche réglementaire.
- Besoin de fiches de non-conformité issues d'un audit global.

## Quand NE PAS utiliser

- Ne pas utiliser pour un audit WCAG générique : router vers
  `audit-accessibilite-web`.
- Ne pas utiliser pour une fiche NC unitaire : router vers `ticket-rgaa` ou
  `pre-audit-rgaa-dsfr`.
- Ne jamais promettre une certification formelle par organisme agréé.
- Ne jamais déclarer la conformité totale sans avoir couvert les 106 critères.
- Ne jamais modifier le code source du site audité.

## Arguments

| Argument | Défaut | Effet |
| --- | --- | --- |
| `url` | requis | site ou page à auditer |
| `--scope` | `page` | `page` ou `echantillon` |
| `--theme` | `all` | thématique 1 à 13 ou audit complet |
| `--output` | `rapport` | `rapport`, `declaration`, `fiches` |
| `--niveau` | `AA` | niveau cible |

Si l'URL manque, arrêter avec un exemple d'utilisation. Ne pas deviner la cible.

## Pré-vol

- Vérifier que l'URL répond.
- Afficher le périmètre, le thème et le livrable demandé.
- Si `--scope echantillon`, constituer 8 à 15 pages : accueil, contact,
  mentions légales, plan du site, aide, authentification si présente, formulaire
  principal et contenus représentatifs.
- Nommer les limites : pages inaccessibles, outils absents, authentification ou
  contenu dynamique non testable.

## Références à lire

Lire selon le besoin, pas par réflexe :

- `a11y-shared-references/axe-core-scan-patterns.md` pour la stratégie de scan ;
- `audit-accessibilite-web/resources/rgaa-mapping.md` pour la correspondance
  axe-core, WCAG et RGAA ;
- `references/modele-declaration.md` seulement si `--output declaration` ;
- les fiches `a11y-shared-references/rgaa-{theme}-*.md` pour les tests manuels
  d'une thématique précise.

Source secondaire RGAA locale :

- si `git-hors-workflow/ay11-pre-audit` existe à la racine du workspace, la
  consulter pour tout audit RGAA comme source de contrats de preuves, profils
  RGAA, collecteurs HTML/navigateur et signaux candidats ;
- ne jamais interpréter l'absence de signal AY11 comme une conformité ;
- ne jamais transformer un signal AY11 en verdict RGAA sans preuve
  complémentaire et validation humaine.

## Phase 1 : tests automatisés

- Scanner chaque page avec le meilleur outil disponible : AccessLint MCP,
  injection axe-core ou CLI.
- Mapper les violations vers les critères RGAA.
- Identifier les critères couverts automatiquement et ceux qui restent manuels.
- Conserver les preuves : URL, sélecteur, extrait, impact et outil utilisé.

Les tests automatisés ne suffisent jamais : ils couvrent seulement une partie du
RGAA.

## Phase 2 : tests manuels

Tester les thématiques demandées :

| Thème | Cible |
| --- | --- |
| 1 à 4 | images, cadres, couleurs, multimédia |
| 5 à 8 | tableaux, liens, scripts, éléments obligatoires |
| 9 à 10 | structure et présentation |
| 11 à 13 | formulaires, navigation, consultation |

Utiliser Chrome DevTools pour la navigation clavier, l'arbre d'accessibilité, le
focus visible, les attributs ARIA et les changements de contexte.

## Phase 3 : statuts et taux

Pour chaque critère testé :

- `C` : conforme sur toutes les pages testées ;
- `NC` : au moins une non-conformité observée ;
- `NA` : critère non applicable ;
- `NT` : non testé. **Interdit dans un audit officiel** : tout critère
  applicable doit être tranché `C` ou `NC`. Un `NT` résiduel signifie que
  l'audit est incomplet.

Calculer le taux :

```text
taux = C / (C + NC) * 100
```

`NA` (non applicable) est exclu du dénominateur — c'est correct et conforme au
RGAA. `NT` ne l'est **pas** : un critère applicable non testé rend l'audit
incomplet.

- **Taux officiel** : n'est calculable que si le nombre de `NT` applicables est
  **zéro**. Sinon, le taux produit surestime la conformité en masquant les
  critères non évalués.
- S'il reste des `NT`, ne pas produire de « taux officiel ». Produire un
  **taux préliminaire** explicitement étiqueté, accompagné du décompte des
  critères non testés (« N critères sur 106 non évalués »), et ne jamais le
  reporter dans une déclaration de conformité.

## Phase 4 : livrables

Selon `--output` :

- `rapport` : périmètre, outils, échantillon, taux global, taux par thème,
  tableau des critères, détails NC, dérogations et références légales ;
- `declaration` : état de conformité, taux, non-conformités, technologies,
  environnement de test, voies de recours et date.
  **Garde-fous obligatoires avant toute production de `declaration`** :
  1. La déclaration de conformité est un acte juridique (décret 2019-768).
     Un audit produit par un agent ne peut pas s'auto-déclarer conforme.
     Ne produire qu'un **brouillon** de déclaration, marqué en tête
     « BROUILLON — à valider et signer par un auditeur humain qualifié ».
  2. Refuser de produire la déclaration si le taux n'est pas officiel
     (voir Phase 3 : zéro `NT` applicable) ou si l'échantillon est incomplet.
  3. Nommer explicitement le type d'audit (auto-audit de l'organisme ou audit
     externe) et laisser l'identité de l'auditeur humain à renseigner —
     jamais « Claude », « agent IA » ni un nom inventé ;
- `fiches` : une fiche par non-conformité avec critère, pages, éléments, impact,
  recommandation et priorité P0 à P4.

Inclure les références légales utiles : loi du 11 février 2005, décret
2019-768, arrêté du 20 septembre 2019, RGAA et voies de recours auprès du
Défenseur des droits.

## Gestion d'erreurs

| Situation | Réponse |
| --- | --- |
| URL inaccessible | arrêter et demander une URL valide |
| AccessLint indisponible | utiliser axe-core CLI ou marquer la limite |
| Chrome DevTools indisponible | marquer les tests interactifs `NT` |
| échantillon trop petit | demander ou proposer des pages supplémentaires |
| aucune violation automatique | poursuivre les tests manuels |

## Exemple

```text
Demande : /audit-rgaa https://www.example.gouv.fr --scope echantillon
Sortie : échantillon documenté, violations automatisées, tests manuels,
106 statuts C/NC/NA/NT, taux officiel et AUDIT-RGAA-REPORT.md.
```

## Pièges fréquents

- Confondre absence de violation axe-core et conformité RGAA.
- Calculer le taux en incluant les critères `NA` ou `NT`.
- Oublier les voies de recours dans une déclaration.
- Générer des fiches NC sans impact utilisateur.
- Utiliser la terminologie WCAG dans un livrable RGAA.
- Masquer les critères non testés au lieu de les justifier.

## Checklist

- [ ] URL, scope, thème et livrable confirmés.
- [ ] Échantillon documenté si demandé.
- [ ] Références RGAA utiles lues.
- [ ] Tests automatisés et manuels distingués.
- [ ] Les 106 critères sont `C`, `NC`, `NA` ou `NT`.
- [ ] Le taux exclut `NA` et `NT`.
- [ ] Livrable produit selon `--output`.
- [ ] Limites, voies de recours et références légales documentées.
