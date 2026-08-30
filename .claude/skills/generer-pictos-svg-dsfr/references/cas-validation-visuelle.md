# Cas de validation visuelle

Ces cas servent à relire des créations `original-dsfr-like` avant diffusion. Ils ne prouvent pas un statut officiel : ils aident à comparer une création au corpus DSFR embarqué.

## Protocole court

1. Prouver que le pictogramme demandé n’existe pas dans `pictos-svg/dsfr-officiels/manifest.json`.
2. Générer une planche avec la création et les références officielles :

```bash
python3 scripts/build_svg_preview.py \
  --svg-root pictos-svg/<dossier> \
  --references health/health,health/doctor,system/success \
  --output outputs/<dossier>-preview.html
```

3. Lancer l’audit de structure et de densité :

```bash
python3 scripts/audit_original_pictos.py \
  --svg pictos-svg/<dossier>/<picto>.svg \
  --manifest pictos-svg/<dossier>/manifest.json \
  --references health/health,health/doctor,system/success \
  --strict
```

4. Relire à `80 px`, `40 px` et `24 px`.
5. Noter la proximité DSFR, la lisibilité, la densité des chemins et le rôle du rouge.
6. Publier seulement après revue humaine explicite.

## Grille de notation

| Critère | 0 | 1 | 2 |
|---------|---|---|---|
| Lisibilité à `80 px` | sujet confus | sujet compris mais hésitant | sujet immédiat |
| Lisibilité à `40 px` | détails perdus | sujet lisible, accent fragile | sujet et accent lisibles |
| Lisibilité à `24 px` | pictogramme inutilisable | silhouette lisible seule | silhouette et intention lisibles |
| Proximité DSFR | icône générique | quelques codes DSFR | gabarit, calques et densité cohérents |
| Rôle du rouge | décoratif ou arbitraire | utile mais trop présent | accent de sens net et sobre |
| Densité du sujet | `major` trop pauvre | sujet lisible mais sous les références | richesse proche des références inspectées |
| Structure SVG | non conforme | conforme avec réserves | conforme sans réserve |

Seuil recommandé : ne pas publier sous 11/14, sous 2/2 sur la structure SVG, ou avec un avertissement d’audit non justifié.

## Signaux de reprise immédiate

- Le SVG est conforme mais ressemble à une icône générique recolorée.
- Le rouge porte la majorité du sujet au lieu d’un accent de sens.
- Le `major` reste lisible, mais il est beaucoup plus pauvre que les références inspectées.
- Le pictogramme tient par un seul objet diagonal sans support, base, scène ou détail DSFR.
- Les points décoratifs sont utilisés pour donner une impression DSFR alors que le sujet principal est trop pauvre.

## Prompts de test

| Prompt | Références officielles à inspecter | Points d’attention |
|--------|------------------------------------|--------------------|
| Créer un cœur de santé publique | `health/health`, `health/doctor`, `system/success` | Le cœur bleu doit rester lisible sans le rouge ; le rouge porte santé, attention ou validation, pas toute la forme. Éviter le simple cœur de bibliothèque. |
| Créer une fusée de lancement de service | `digital/innovation`, `system/success`, `map/airport` | La fusée doit avoir une silhouette riche et un accent de lancement ; éviter la petite fusée logo, les flammes trop rouges ou l’illustration détaillée. |
| Créer un crayon d’annotation administrative | `document/document-signature`, `document/sign-document`, `leisure/paint` | Un crayon seul en diagonale est fragile : ajouter une grammaire de support, trace ou action proche des références. Le rouge signale l’annotation. |
| Créer une rose pour une action culturelle | `environment/leaf`, `leisure/culture`, `leisure/art` | La fleur ne doit pas devenir un objet rouge complet ; garder une structure bleue dominante et un rouge limité à un pétale, une pousse ou un point focal. |
| Créer un microscope de recherche | `health/medical-research`, `health/virus`, `digital/data-visualization` | Le major doit porter l’objet scientifique ; le minor peut porter l’échantillon ou le point focal. |
| Créer une chaîne de traitement de données | `digital/data-visualization`, `digital/coding`, `system/flow-list` | Éviter les traits filaires ; utiliser des formes remplies et une composition aérée. |
| Créer un bouclier de conformité | `system/padlock`, `institutions/justice`, `system/success` | Le rouge doit signaler la coche, le verrou ou le point de contrôle. |
| Créer un serveur souverain | `digital/internet`, `system/padlock`, `buildings/factory` | Le serveur ne doit pas devenir une icône technique générique `256x256`. |
| Créer une carte de parcours usager | `map/map`, `map/map-pin`, `digital/avatar` | Le rouge doit désigner le point de destination ou l’étape active. |
| Créer une assistance conversationnelle | `digital/avatar`, `digital/mail-send`, `system/information` | La bulle ou l’avatar doit rester lisible à `24 px` sans texte visible. |

## Verdict attendu

Pour chaque création, consigner :

- le statut `official: false` ;
- les trois à cinq références officielles inspectées ;
- le résultat de `audit_original_pictos.py`, avec justification des avertissements ;
- le score de la grille ;
- l’écart assumé avec les références ;
- la décision humaine : `accepté`, `à reprendre` ou `refusé`.
