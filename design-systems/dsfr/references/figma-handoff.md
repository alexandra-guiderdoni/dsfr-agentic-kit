---
title: "DSFR - guideline Figma textuelle"
scope: maquette, prototype, handoff, variantes, instances
load_when: "Le livrable est une maquette, un prototype ou un handoff multi-agent."
---

# DSFR - guideline Figma textuelle

Cette référence traduit les invariants des fichiers Figma DSFR en règles vérifiables par un agent. Elle ne remplace pas les fichiers Figma officiels.

## Structure côté design

- `Fondamentaux` : couleurs d'options, système de couleurs, styles de texte, grilles, espacements, ratios de médias, bloc marque, icônes.
- `Composants` : symboles dynamiques, pages par composant, planches de présentation, variantes et règles d'usage.
- `Pictogrammes` : symboles SVG organisés par catégorie.
- Fichier projet : écran ou prototype qui instancie ces librairies sans redessiner les composants officiels.

## Synchronisation

- Référencer d'abord les fondamentaux, puis les composants.
- Relier ensuite les librairies intermédiaires et fichiers de design.
- Lors d'une mise à jour DSFR, préserver la chaîne `Fondamentaux -> Composants -> Librairies intermédiaires -> Fichiers de design`.
- Ne pas traiter une instance détachée comme conforme sans raison documentée.

## Contrat d'instance

- Utiliser une instance officielle ou un composant DSFR local quand il existe.
- Modifier seulement les overrides autorisés : texte, icône, état, taille, variante, attributs, contenu.
- Documenter toute modification structurelle : besoin, composant écarté, risque DSFR, vérification faite.
- Ne pas créer une variante locale durable sans la nommer comme extension projet.
- Pour un composant interactif, livrer les états clés : normal, focus, hover, actif, désactivé, erreur ou succès si formulaire.

## Traduction maquette vers code

| Élément Figma | Équivalent DSFR attendu | Preuve |
|---|---|---|
| style de couleur | token de décision ou classe officielle | nom du token, classe ou variable |
| style de texte | Marianne ou Spectral selon usage | classe typo, police ou style appliqué |
| grille de frame | `fr-container`, `fr-grid-row`, `fr-col-*` | largeur, breakpoint, gouttières |
| composant | composant `fr-*` ou template local | source composant lue |
| variant/state | classe, attribut ou état ARIA | capture, DOM ou interaction testée |
| pictogramme | SVG DSFR ou pictogramme autorisé | calques et alternative vérifiés |

## Frames

- Mobile : vérifier au minimum `320px`; `390px` peut compléter.
- Desktop : vérifier `1440px` avec largeur utile DSFR.
- Les breakpoints `sm`, `md`, `lg`, `xl` guident les transitions.

## Handoff maquette

```text
Frames vérifiées :
Styles utilisés :
Composants / instances :
Overrides :
États :
Écarts :
Preuves :
```
