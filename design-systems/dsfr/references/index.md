---
title: "DSFR - index de chargement"
scope: routage, références, preuves
load_when: "Un agent doit choisir rapidement les références DSFR locales."
---

# DSFR - index de chargement

Cet index aide à choisir les références locales. Il ne remplace pas
`DESIGN.md`, `tokens.yaml`, la documentation officielle DSFR ni le skill
`dsfr-components`.

## Ordre court

1. Charger `DESIGN.md` et `tokens.yaml`.
2. Identifier la branche : page, composant, formulaire, maquette, audit,
   publication ou version.
3. Ouvrir seulement les références utiles ci-dessous.
4. Produire ou vérifier avec le skill spécialisé quand il existe.
5. Finir par une preuve nommée et un claim autorisé.

## Carte de chargement

| Besoin | Charger | Décision portée | Preuve attendue |
|---|---|---|---|
| choisir une route DSFR | `DESIGN.md`, `tokens.yaml` | branche, limites, claim possible | sources citées ou absence nommée |
| étendre la couverture des tokens | `references/tokens-coverage.md` | familles, états, preuves par type | extension courte ou limite nommée |
| rendu visuel, couleurs, typo, grille | `references/foundations.md` | tokens, classes, modes, responsive | tokens ou classes cités |
| page complète ou publiable | `references/page-shell.md` | head, landmarks, footer, liens, données | inspection structurelle ou limite |
| composant HTML ou intégration | `references/components-routing.md` | composant officiel, famille, dépendances | source composant nommée |
| formulaire ou page type | `references/forms-models.md` | blocs fonctionnels, labels, erreurs | champs et aides inspectés |
| maquette ou handoff | `references/figma-handoff.md` | instances, variants, frames, overrides | styles et composants listés |
| preuve, audit ou transmission | `references/verification.md` | niveau de preuve, formulation, routage audit | claim final borné |
| version, autorité ou périmètre | `references/sources.md` | source prioritaire, version, limite officielle | URL, version ou source citée |
| usage avec `dsfr-components` | `references/agent-recipes.md` | recette page, composant, formulaire, audit, publication | recette appliquée et preuve |
| dérive profil-skill | `../evals/profile-skill-smoke.md` | prompts positifs et near-miss | proxy smoke ou limite runtime |

## Règle de priorité

Si deux sources divergent, suivre la source la plus proche du livrable réel :

1. documentation officielle DSFR ou package installé ;
2. scripts et références de `dsfr-components` pour la génération ;
3. références locales `design-systems/dsfr/references/` ;
4. `tokens.yaml` pour les décisions de rendu ;
5. `DESIGN.md` pour le routage, les limites et les claims.

## Sortie minimale

```text
Route choisie :
Références chargées :
Source la plus autoritaire :
Preuve exécutée :
Claim final autorisé :
Limites :
```
