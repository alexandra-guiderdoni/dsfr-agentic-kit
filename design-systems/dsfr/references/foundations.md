---
title: "DSFR - fondamentaux"
scope: couleurs, typographie, grille, espacements, médias, icônes, modes
load_when: "Le livrable touche aux choix visuels ou au rendu responsive."
---

# DSFR - fondamentaux

Utiliser cette référence après `DESIGN.md` et `tokens.yaml` quand le travail porte sur le rendu visuel.

## Couleurs

- Utiliser les tokens de décision avant toute couleur brute.
- Choisir un token par usage sémantique : fond, bordure, texte, illustration.
- Préserver les couples mode clair et mode sombre.
- Utiliser `blue-france` pour l'identité de l'État et les actions institutionnelles principales.
- Utiliser erreur, avertissement, succès et information seulement pour leur fonction.
- Ne pas créer de palette décorative hors DSFR.
- Ne pas coder une information uniquement par couleur.

Décisions courantes :

- fond de page : `background-default-grey` ;
- section alternative : `background-alt-grey` ;
- bouton primaire : `background-action-high-blue-france` ;
- action secondaire : `background-action-low-blue-france` ;
- corps de texte : `text-default-grey` ;
- titre : `text-title-grey`, ou `text-title-blue-france` si l'identité de l'État doit être portée.

## Typographie

- Marianne est la police principale.
- Spectral est secondaire et réservée aux usages éditoriaux justifiés.
- Déclarer `lang="fr"` pour les artefacts HTML.
- Garder une hiérarchie de titres sans saut.
- Utiliser les classes `fr-h*` pour le style visuel sans fausser la sémantique.
- Ne pas substituer Calibri, Aptos, Segoe UI ou une police de bureau dans un livrable final.

## Grille et layout

- Utiliser `fr-container`, `fr-grid-row`, `fr-grid-row--gutters` et `fr-col-*`.
- Concevoir au minimum mobile et desktop.
- Repères de conception : `320px` mobile, `1440px` desktop.
- Breakpoints : `sm 576px`, `md 768px`, `lg 992px`, `xl 1248px`.
- Sur desktop XL, ne pas étirer le contenu au-delà de la largeur utile DSFR.

Patterns :

- page éditoriale : `fr-container`, `fr-col-12 fr-col-md-10 fr-col-lg-8` ;
- tableau de bord public : grille 12 colonnes, cartes seulement si chaque bloc porte une décision ou une donnée ;
- formulaire : colonne lisible, groupes en `fieldset`, aide et erreur proches du champ.

## Espacements

- Base visuelle : grille de 8px et incréments de marge de 4px.
- Tokens usuels : `1v`, `2v`, `4v`, `6v`, `8v`, `12v`, `16v`, `24v`, `32v`.
- Titres et paragraphes ont par défaut un espace inférieur de `6v`.
- Ne pas corriger une composition par micro-ajustements arbitraires en pixels si un token DSFR convient.
- Signaler les espacements inférés si aucun fichier de tokens projet n'existe.

## Médias, Icônes Et Pictogrammes

- Images responsives : `fr-responsive-img`.
- Vidéos responsives : `fr-responsive-vid`.
- Ratios acceptables : 32:9, 16:9, 3:2, 4:3, 1:1, 3:4, 2:3.
- Icônes : classes `fr-icon-*`, suffixes `-line` ou `-fill`; `fr-fi` est déprécié.
- Icône décorative : `aria-hidden="true"`.
- Pictogramme décoratif : `aria-hidden="true"` si le texte adjacent porte le sens.
- Ne pas utiliser une icône ou un pictogramme comme unique porteur d'information.

## Modes

- Utiliser `data-fr-scheme="system"` par défaut lorsque le choix utilisateur est exposé.
- Tester clair et sombre si le mode est exposé.
- Pour publication ou CSS custom, mentionner le mode contraste élevé : testé ou non vérifié.
- Préserver les styles de focus DSFR et le focus système.
