# Brief — Résultats de recherche de services publics

## Mini-brief

- **Objectif** : permettre à une personne de retrouver un service public puis
  d'affiner les résultats sans dépendre de JavaScript.
- **Public visé** : grand public, sans connaissance administrative préalable.
- **Tâche principale** : rechercher par mots-clés, filtrer avec des listes
  déroulantes et utiliser des tags comme raccourcis de filtrage.
- **Artefact** : une page HTML statique complète générée par le builder DSFR
  assemblé du kit.
- **Fidélité** : composants et classes du paquet DSFR 1.15.2, sans CSS
  personnalisé et sans bloc marque République française.
- **Contenu** : exemples fictifs destinés à éprouver la hiérarchie, la densité
  et les états de la page ; aucune donnée administrative ne fait foi.
- **Droits** : mode de marque neutre ; aucun droit d'usage de la marque de
  l'État n'est présumé.
- **Preuve attendue** : schéma JSON, contrôles du builder, inspection HTML,
  rendu desktop et mobile, console et parcours clavier de surface.
- **Non vérifié** : exactitude métier des résultats, fonctionnement d'un moteur
  de recherche réel, conformité RGAA globale et droit de publication.

## Sources

| Source | Statut | Usage |
| --- | --- | --- |
| `design-systems/dsfr/DESIGN.md` | lu | intention DSFR, mode neutre, claims bornés |
| `design-systems/dsfr/tokens.yaml` | lu | grille, espacements et composants structurants |
| `design-systems/dsfr/references/page-shell.md` | lu | enveloppe, repères et liens de pied de page |
| `design-systems/dsfr/references/verification.md` | lu | niveau de preuve et limites |
| `references/components/forms-services/forms/choices.md` | lu | listes déroulantes |
| `references/components/feedback-actions/tags.md` | lu | tags-liens |
| `references/components/content-media/cards.md` | lu | cartes de résultats |
| Builder et schéma assemblés locaux | lu | composition et validation |

## Décisions de composition

- La recherche globale est placée dans l'en-tête DSFR.
- Les filtres détaillés sont groupés dans un `fieldset` par le bloc `form`.
- Les tags sont des liens GET utilisables sans JavaScript ; ils ne simulent pas
  des boutons supprimables sans comportement associé.
- Les résultats utilisent des cartes DSFR en liste sur la colonne principale.
- Sur petit écran, la grille DSFR place les filtres avant les résultats.
- Les actions et liens sont des routes de prototype explicites, sans
  `href="#"`.

