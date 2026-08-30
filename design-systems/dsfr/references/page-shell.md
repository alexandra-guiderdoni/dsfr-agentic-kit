---
title: "DSFR - enveloppe de page"
scope: head, landmarks, header, footer, cookies, mesure, liens
load_when: "Le livrable est une page complète ou une sortie publiable."
---

# DSFR - enveloppe de page

Une page DSFR complète n'est pas seulement une composition de composants. Elle porte un contrat de structure, d'orientation, de mentions et de données.

## Head

- Inclure `charset`, `viewport`, titre de page et description si la page est partagée ou indexée.
- Charger CSS, icônes, favicons, polices et JS depuis la version réelle du projet.
- Si DSFR direct : importer le JS DSFR en fin de `body`.
- Ajouter `format-detection` iOS si le projet suit les exemples DSFR récents ou si des numéros, dates, adresses ou courriels sont présents.
- Ajouter les métadonnées de partage seulement si le partage social est un besoin réel.

## Repères

- Prévoir des liens d'évitement pour toute page complète, en début de page avant l'en-tête, avec au minimum `Accéder au contenu`.
- `header` doit jouer le rôle de bannière.
- `main` doit être identifiable et recevoir la cible principale des liens d'évitement.
- `footer` doit jouer le rôle `contentinfo`.
- Le lien d'accueil du header doit pointer vers l'accueil réel et annoncer l'accueil du site ou service.
- La navigation principale aide à orienter dans les grandes rubriques ; elle n'est pas obligatoire si l'arborescence ne le justifie pas.

## Footer avant publication

- Mention d'accessibilité : non conforme, partiellement conforme ou totalement conforme.
- Mentions légales.
- Données personnelles.
- Gestion des cookies.
- Mention de licence lorsque le contexte éditorial l'exige.
- Liens de référence de l'écosystème institutionnel si la page représente un service complet.
- Pied de page simple pour une page peu profonde ; pied de page complet pour un site avec listes de liens organisées.

## Données et cookies

- Ajouter le gestionnaire de consentement si des cookies non fonctionnels ou traceurs optionnels sont déposés.
- Si une mesure d'audience est intégrée, nommer la solution, le statut de consentement et la source technique.
- Ne pas inventer une politique de données personnelles : utiliser la source projet ou marquer `données personnelles à vérifier`.
- Pour un prototype, utiliser des liens explicitement non finalisés et interdire la mention `prêt pour publication`.

## Liens

- Pas de `href="#"` résiduel.
- Utiliser une ancre réelle, une URL réelle ou l'état `lien à finaliser`.
- Pour `target="_blank"`, prévoir `rel="noopener"` et signaler l'ouverture dans une nouvelle fenêtre quand le composant ou modèle l'exige.

## Preuve minimale

```text
Head vérifié :
Landmarks vérifiés :
Footer légal :
Cookies / mesure :
Liens externes :
Limites avant publication :
```
