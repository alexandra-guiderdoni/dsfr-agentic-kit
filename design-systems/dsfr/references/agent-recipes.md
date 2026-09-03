---
title: "DSFR - recettes agentiques"
scope: pages, composants, formulaires, audits, publication
load_when: "Un agent utilise le profil DSFR avec le skill dsfr-components."
---

# DSFR - recettes agentiques

Ces recettes rendent le profil DSFR directement consommable par
`dsfr-components`. Elles ne remplacent pas les scripts, options et références du
skill.

## Contrat BRANCH-MAP

| Recette | Branche(s) `dsfr-components` attendue(s) |
|---|---|
| Page complète | `page complète` |
| Composant isolé | `composant isolé` |
| Formulaire | `page complète`, `composant isolé` |
| Audit DSFR ponctuel | `routage audit DSFR ponctuel` |
| Publication | `page complète`, `routage audit DSFR ponctuel`, audit spécialisé hors skill |

## Page complète

| Point | Règle |
|---|---|
| Déclencheur | demande explicite de page HTML statique DSFR |
| Charger | `DESIGN.md`, `tokens.yaml`, `references/page-shell.md`, `references/components-routing.md` |
| Skill | `dsfr-components`, branche page complète |
| Faire | choisir le type de page, générer, remplacer les textes et liens factices |
| Ne pas faire | publier, certifier ou utiliser le bloc marque sans preuve de périmètre |
| Preuve | `html lang="fr"`, `header`, `main`, `footer`, absence de `href="#"`, version nommée |
| Claim | `composants DSFR utilisés selon les sources lues` ou `prototype DSFR à vérifier avant publication` |

## Composant isolé

| Point | Règle |
|---|---|
| Déclencheur | demande d'un fragment ou composant DSFR à insérer |
| Charger | `DESIGN.md`, `tokens.yaml`, `references/components-routing.md`, puis référence ciblée du skill |
| Skill | `dsfr-components`, branche composant isolé |
| Faire | produire un fragment sans enveloppe de page, citer la source du composant |
| Ne pas faire | inventer un composant `DSFR-like` ou ajouter header/footer autour du fragment |
| Preuve | composant nommé, structure inspectée, cibles ARIA présentes ou limite nommée |
| Claim | `composants DSFR utilisés selon les sources lues` |

## Formulaire

| Point | Règle |
|---|---|
| Déclencheur | formulaire administratif, connexion, création de compte ou champ isolé |
| Charger | `DESIGN.md`, `tokens.yaml`, `references/forms-models.md`, `references/components-routing.md` |
| Skill | `dsfr-components`, branche page, composant ou champ selon le livrable |
| Faire | associer labels, aides, erreurs, groupes et `autocomplete` utiles |
| Ne pas faire | inventer règles métier, délais, droits, montants ou contraintes natives au repos |
| Preuve | labels reliés, aide ou erreur reliée, absence d'information portée seulement par la couleur |
| Claim | `composants DSFR utilisés selon les sources lues` |

## Audit DSFR ponctuel

| Point | Règle |
|---|---|
| Déclencheur | vérifier un HTML généré ou un composant DSFR local |
| Charger | `DESIGN.md`, `references/verification.md`, source ciblée du composant si nécessaire |
| Skill | `dsfr-components`, branche audit DSFR ponctuel |
| Faire | classer les écarts sur les sources lues et nommer les inconnus |
| Ne pas faire | produire un verdict RGAA global ou un statut `conforme DSFR` |
| Preuve | fichier contrôlé, écarts classés, sources citées, limites nommées |
| Claim | statut borné aux sources lues |

## Publication

| Point | Règle |
|---|---|
| Déclencheur | mise en ligne, reprise publique, marque État ou claim de conformité |
| Charger | `DESIGN.md`, `references/page-shell.md`, `references/verification.md`, `references/sources.md` |
| Skill | `dsfr-components` seulement pour corriger ou générer ; audit spécialisé pour conformité |
| Faire | vérifier périmètre, marque, mentions, données, cookies, mesure et liens |
| Ne pas faire | revendiquer publication, RGAA ou usage marque sans validation dédiée |
| Preuve | sources de périmètre, liens réels, footer légal, audit ou limite explicite |
| Claim | abaisser vers `prototype DSFR à vérifier avant publication` si preuve incomplète |

## Handoff agent

```text
Recette appliquée :
Branche `dsfr-components` :
Références chargées :
Sources non lues :
Preuve exécutée :
Claim final :
Limites :
```
