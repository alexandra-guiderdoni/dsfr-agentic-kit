# Profil de style des pictogrammes DSFR

Corpus analysé : `pictos-svg/dsfr-officiels`.
Source : `@gouvfr/dsfr@1.15.2`.
Date d'analyse : 2026-08-29.
Nombre de pictogrammes officiels : 102.
Nombre de SVG dans le corpus : 102.
Empreinte du corpus (SHA256 des empreintes) : `7b410644fca7c5f3…`.

## Invariants et variantes

- Gabarit invariant : `0 0 80 80`.
- Taille recommandée pour une création : `80px x 80px`.
- Tailles observées : {"80 x 80": 8, "80px x 80px": 94}.
- Fichiers avec `fill` racine : 4.
- Calques : `artwork-decorative`, `artwork-minor`, `artwork-major`.
- Nombre de `<use>` : 3.
- Couleurs attendues : {"fr-artwork-decorative": "#ECECFF", "fr-artwork-minor": "#E1000F", "fr-artwork-major": "#000091"}.

## Exceptions documentées

- `system/system` : hrefs ['#artwork-major', '#artwork-minor', '#artwork-major'], classes ['fr-artwork-major', 'fr-artwork-minor', 'fr-artwork-major'].

## Familles

- `accessibility` : 5 ; médianes major 48 commandes, 31.6 % du carré ; minor 23 commandes, 31.2 % du carré
- `buildings` : 7 ; médianes major 163 commandes, 50.7 % du carré ; minor 125 commandes, 20.2 % du carré
- `digital` : 13 ; médianes major 97 commandes, 43.8 % du carré ; minor 78 commandes, 18.1 % du carré
- `document` : 20 ; médianes major 81.0 commandes, 41.25 % du carré ; minor 69.5 commandes, 24.5 % du carré
- `environment` : 9 ; médianes major 130 commandes, 39.4 % du carré ; minor 36 commandes, 14.0 % du carré
- `health` : 6 ; médianes major 195.0 commandes, 56.150000000000006 % du carré ; minor 41.5 commandes, 9.1 % du carré
- `institutions` : 9 ; médianes major 126 commandes, 40.5 % du carré ; minor 58 commandes, 19.2 % du carré
- `leisure` : 12 ; médianes major 112.0 commandes, 44.7 % du carré ; minor 61.0 commandes, 21.4 % du carré
- `map` : 9 ; médianes major 213 commandes, 56.0 % du carré ; minor 51 commandes, 21.9 % du carré
- `system` : 12 ; médianes major 102.5 commandes, 49.8 % du carré ; minor 25.0 commandes, 10.55 % du carré

## Complexité par calque

- `artwork-decorative` :
  - chemins par icône : min 1, p10 1, médiane 1.0, moyenne 1.02, p90 1, max 3 ;
  - commandes par icône : min 9, p10 9, médiane 18.0, moyenne 18.69, p90 30, max 42 ;
  - nombres par icône : min 48, p10 48, médiane 64.0, moyenne 76.49, p90 108, max 152 ;
  - caractères `d` par icône : min 138, p10 152, médiane 246.0, moyenne 264.19, p90 390, max 730.
- `artwork-minor` :
  - chemins par icône : min 1, p10 1, médiane 1.0, moyenne 1.05, p90 1, max 2 ;
  - commandes par icône : min 8, p10 18, médiane 51.5, moyenne 64.2, p90 133, max 310 ;
  - nombres par icône : min 36, p10 77, médiane 205.0, moyenne 256.86, p90 500, max 918 ;
  - caractères `d` par icône : min 156, p10 253, médiane 1023.5, moyenne 1358.56, p90 2807, max 7347.
- `artwork-major` :
  - chemins par icône : min 1, p10 1, médiane 1.0, moyenne 1.21, p90 1, max 8 ;
  - commandes par icône : min 18, p10 52, médiane 110.0, moyenne 131.71, p90 232, max 469 ;
  - nombres par icône : min 96, p10 218, médiane 412.0, moyenne 506.08, p90 955, max 2184 ;
  - caractères `d` par icône : min 282, p10 787, médiane 2343.5, moyenne 2745.83, p90 5497, max 12618.

## Occupation du carré par calque

Boîte englobante des chemins aplatis, en pourcentage du carré `80 x 80` ; l'aire est approximative, les évidements comptent positivement.

- `artwork-decorative` :
  - boîte englobante en % du carré : min 42, p10 56, médiane 68.0, moyenne 66.74, p90 79, max 89 ;
  - aire approximative en % du carré : min 0, p10 0, médiane 0.0, moyenne 0, p90 0, max 0 ;
  - largeur : médiane 66.5, p10 54, p90 74 ; hauteur : médiane 68.0, p10 58, p90 74 ;
  - centre médian : (40.0, 40.0) ;
  - coordonnées entières dans les `d` : 81.4 %.
- `artwork-minor` :
  - boîte englobante en % du carré : min 1, p10 3, médiane 18.0, moyenne 21.08, p90 40, max 63 ;
  - aire approximative en % du carré : min 0, p10 1, médiane 4.0, moyenne 5.46, p90 12, max 42 ;
  - largeur : médiane 35.5, p10 18, p90 58 ; hauteur : médiane 31.5, p10 14, p90 56 ;
  - centre médian : (40.0, 42.0) ;
  - coordonnées entières dans les `d` : 36.8 %.
- `artwork-major` :
  - boîte englobante en % du carré : min 20, p10 36, médiane 46.0, moyenne 46.29, p90 58, max 74 ;
  - aire approximative en % du carré : min 3, p10 6, médiane 11.0, moyenne 19.79, p90 56, max 112 ;
  - largeur : médiane 56.5, p10 44, p90 64 ; hauteur : médiane 56.0, p10 42, p90 62 ;
  - centre médian : (40.0, 40.0) ;
  - coordonnées entières dans les `d` : 35.6 %.

La base de `2 px` et les multiples de `4` ou `8` sont une grille de conception ; les coordonnées officielles sont majoritairement décimales, cette grille n'est donc pas un critère d'audit.

## Calibration de l'audit

Méthode : minimum observé des ratios officiel/médiane de trois références de même famille ; plage d'occupation observée sur le corpus ; pauvreté au p10 des commandes.

- `artwork-major` : commandes au moins 0.167 fois la médiane des références, occupation au moins 0.385 fois celle des références, occupation observée entre 20.2 % et 74.3 % du carré, seuil de pauvreté 52 commandes (p10).
- `artwork-minor` : commandes au moins 0.12 fois la médiane des références, occupation au moins 0.037 fois celle des références, occupation observée entre 0.9 % et 62.8 % du carré, seuil de pauvreté 18 commandes (p10).

## Attributs et éléments

- Attributs de `<path>` observés : {"clip-rule": 16, "d": 334, "fill-rule": 21}.
- Les symboles officiels utilisent des `<path>` ; les primitives `<line>`, `<rect>`, `<circle>` et les groupes stroke ne font pas partie du corpus.

## Règles de création DSFR-like

- Utiliser --source dsfr-replica si le nom existe dans le corpus embarqué.
- Créer en original-dsfr-like seulement après preuve d'absence officielle.
- Utiliser le gabarit 80x80, les trois symboles et les trois use canoniques pour toute création nouvelle.
- Utiliser uniquement des path dans les symboles, sans stroke, sans primitive SVG et sans couleur directe sur les chemins.
- Viser un chemin riche par calque plutôt qu'une accumulation de primitives.
- Comparer la complexité du major et du minor à trois à cinq références officielles proches.
- Comparer l'occupation du carré (boîte englobante du major et du minor) aux références inspectées ; l'audit lit les repères dans ce profil.
- La grille de 2 px est une grille de conception : les coordonnées officielles ne sont pas majoritairement entières, ne pas en faire un critère d'audit.
- Marquer toute création originale comme official=false et ne jamais la présenter comme officielle.
