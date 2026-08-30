---
title: "DSFR - couverture des tokens de décision"
scope: tokens, états, familles, preuves
load_when: "Un besoin dépasse tokens.yaml ou demande une décision de famille, état, média, formulaire ou composant."
---

# DSFR - couverture des tokens de décision

Cette référence étend `tokens.yaml` sans en faire un catalogue officiel. Elle
sert à décider quoi charger, quoi vérifier et quoi marquer `à vérifier`.

## Règle d'usage

- Garder `tokens.yaml` comme index court et source de décision rapide.
- Ajouter ici les familles détaillées, les états attendus et les preuves.
- Promouvoir dans `tokens.yaml` seulement les décisions stables et utiles à
  plusieurs générations.
- Ne jamais conclure qu'un token ou composant DSFR n'existe pas depuis cette
  référence seule.

## Portes vers 100 %

| Claim demandé | Source à charger | Preuve minimale | Statut sans preuve |
|---|---|---|---|
| `100 % tokens CSS DSFR` | skill `dsfr-components` : `evals/official-coverage-inventory.md`, `references/tokens.md`, `references/tokens-advanced.md` | inventaire officiel rejoué, version citée | `non revendiqué` |
| `100 % classes utilitaires` | skill `dsfr-components` : `evals/official-coverage-inventory.md`, `references/utilities.md` et sous-référence utile | classe attestée ou absence vérifiée dans le paquet | `à vérifier` |
| `100 % composants` | skill `dsfr-components` : `evals/official-coverage-inventory.md` (1.15.2), `evals/couverture-officielle-1-14-4.md` (instantané 1.14.4 conservé tel quel, périmètre 46/46 revérifié en 1.15.2) | périmètre `46/46` et variantes couvertes cités | couverture locale bornée |
| `prêt publication` | `verification.md`, `page-shell.md`, `sources.md` | checklist publication, liens réels et mandat marque | prototype à vérifier |
| `conforme RGAA` | `verification.md` puis skill d'audit adapté | rapport spécialisé, taux ou décision humaine | `non revendiqué` |

## Couverture par famille

| Famille | Couvrir | Source à charger |
|---|---|---|
| couleurs | fonds, textes, bordures, artwork, états sémantiques | `foundations.md` puis package DSFR si besoin |
| typographie | Marianne, Spectral, tailles visuelles, langue, hiérarchie | `foundations.md` |
| espacements | tokens `v`, gaps, marges, bandes de page | `foundations.md` |
| grille | containers, lignes, colonnes, breakpoints, largeurs utiles | `foundations.md` |
| régions | skiplinks, header, breadcrumb, main, footer | `page-shell.md` |
| interaction | focus, hover, active, selected, open, disabled | composant ciblé + `verification.md` |
| formulaires | labels, aides, erreurs, fieldset, autocomplete, required différé | `forms-models.md` + patterns du skill |
| navigation | breadcrumb, tabs, pagination, sidemenu, navigation principale | `components-routing.md` |
| contenu | cards, tiles, accordions, tables, downloads, media, quote | `components-routing.md` |
| feedback | alert, notice, badge, tooltip, messages d'erreur | `components-routing.md` |
| services | FranceConnect, consentement, affichage, langue | `page-shell.md` ou skill ciblé |
| médias | images, vidéos, ratios, légendes, alternatives | `foundations.md` |
| icônes | `fr-icon-*`, line/fill, décoratif vs informatif | `foundations.md` |

## États minimaux

Pour un composant interactif, raisonner au moins sur :

- état par défaut ;
- focus visible ;
- hover si pertinent ;
- actif, sélectionné ou ouvert si applicable ;
- désactivé si l'action peut être indisponible ;
- erreur ou succès si le composant porte un retour utilisateur.

Ne jamais supprimer le focus DSFR. Ne jamais porter une information seulement
par la couleur, l'icône ou le pictogramme.

## Formulaires

Décisions à vérifier avant livraison :

- label programmatique pour chaque champ ;
- aide ou erreur reliée au champ quand elle existe ;
- `fieldset` et `legend` pour les groupes ;
- `autocomplete` pour les données personnelles ;
- ordre prénom puis nom ;
- pas de `required`, `aria-required`, `pattern` ou `aria-invalid` au repos sans
  arbitrage documenté.

## Navigation et régions

Pour une page complète, vérifier :

- liens d'évitement en début de page ;
- `header`, `main`, `footer` ;
- fil d'Ariane si la profondeur de navigation le justifie ;
- liens réels et aucun `href="#"` résiduel ;
- pied de page compatible avec le statut prototype ou publication.

## Médias, icônes et pictogrammes

- Image responsive : `fr-responsive-img`.
- Vidéo responsive : `fr-responsive-vid`.
- Ratios usuels : 32:9, 16:9, 3:2, 4:3, 1:1, 3:4, 2:3.
- Icône DSFR : `fr-icon-<nom>-line` ou `fr-icon-<nom>-fill`.
- Préfixe `fr-fi` : déprécié, ne pas l'introduire.
- Décoratif : `aria-hidden="true"` si le texte adjacent porte le sens.
- Informatif : prévoir un nom accessible ou un texte visible équivalent.

## Preuve attendue

| Situation | Preuve minimale |
|---|---|
| extension de token | famille, usage, provenance et source locale cités |
| composant interactif | cible ARIA, état ouvert ou actif, focus ou limite nommée |
| formulaire | labels, aides, erreurs, autocomplete et contrainte différée vérifiés |
| page complète | régions, skiplinks, liens réels et version DSFR inspectés |
| média ou icône | rôle décoratif ou informatif explicitement tranché |

## Limite

Cette référence augmente la couverture agentique. Elle ne remplace ni la
documentation officielle DSFR, ni le package installé, ni un audit RGAA.
