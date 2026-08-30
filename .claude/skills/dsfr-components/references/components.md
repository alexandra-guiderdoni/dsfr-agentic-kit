# Référence des composants DSFR 1.15.2

Index de progressive disclosure pour les composants DSFR. Pour un composant
précis, ouvrir seulement le fichier de famille, puis le sous-fichier du
composant demandé.

| Famille | Index ciblé | Sous-références principales |
| --- | --- | --- |
| Actions et retours utilisateur | `references/components/feedback-actions.md` | Boutons, Alertes, Badges, Tags, Mise en avant (Callout), Bandeau d'information (Notice), Partage (Share), Bouton de suivi (Follow), Info-bulle (Tooltip) |
| Formulaires et services | `references/components/forms-services.md` | Formulaires, Interrupteur (Toggle), Barre de recherche (Search), FranceConnect |
| Navigation | `references/components/navigation.md` | Navigation, Pagination, Liens de navigation latérale (Sidemenu), Accordéons, Onglets, Lien d'évitement (Skiplink), Indicateur d'étapes (Stepper), Lien (Link), Sommaire (Summary), Sélecteur de langue (Translate), Fil d'Ariane avancé, Retour en haut de page (Back to top) |
| Contenus et médias | `references/components/content-media.md` | Cartes, Tableaux, Tuiles, Mise en exergue (Highlight), Citation (Quote), Téléchargement (Download), Transcription, Contenu multimédia (Content), Carte horizontale tier, Paramètre d'affichage (Display) |
| Structure de page | `references/components/structure.md` | Modales, Logo, En-tête (Header), Pied de page (Footer), Bandeau de consentement cookies (Consent) |

## Nommage du catalogue générable

- Noms canoniques locaux, clés du générateur et de la bibliothèque JSON :
  `tabs`, `skiplinks`. Alias d'entrée acceptés : `tab`, `skiplink`, qui sont
  aussi les noms des dossiers officiels `dist/component/<nom>`.
- `back_to_top` et `button_group` sont des helpers locaux composés avec des
  classes DSFR officielles, pas des dossiers de composant autonomes du paquet
  `@gouvfr/dsfr@1.15.2`.
- `segmented` est présent dans le catalogue générable depuis le paquet officiel
  DSFR 1.15.2.

## Règle de lecture ciblée

- Ne pas lire tout le catalogue pour un composant isolé.
- Partir du nom du composant demandé, ouvrir l'index de famille, puis le
  sous-fichier correspondant.
- Si le composant manque dans les références locales, citer la limite et consulter la page officielle DSFR du composant concerné seulement.
