---
title: "DSFR - composants et routage"
scope: composants, portages, extensions, pages HTML
load_when: "Le livrable est une page HTML, un composant ou une intégration."
---

# DSFR - composants et routage

Utiliser un composant officiel quand il existe. Ne pas inventer un composant `DSFR-like` si un équivalent est documenté.

## Route locale

- Page HTML statique : utiliser le skill `dsfr-components` et son template.
- Composant précis : lire la section ciblée de `.claude/skills/dsfr-components/references/components.md` (chemin depuis la racine du dépôt), ou la page officielle.
- Composant interactif de contenu : accordéon, onglets, modale, menu, fil d'Ariane, sélecteur de langue ou tuile cliquable ; lire le composant ciblé, charger le JS DSFR et vérifier l'état ouvert ou actif dans le navigateur.
- Formulaire administratif : charger aussi `forms-models.md`.
- Audit de conformité : charger `verification.md` et router vers le skill d'audit adapté.
- Composant absent localement : vérifier la documentation officielle avant de conclure qu'il n'existe pas.

## Composants structurants

- Page : `fr-header`, `main`, `fr-footer`.
- Navigation : fil d'Ariane, navigation principale, menu latéral, onglets, pagination, retour haut de page.
- Actions : bouton, groupe de boutons, lien, tag cliquable, interrupteur, contrôle segmenté si disponible.
- Formulaires : input, mot de passe, select, checkbox, radio, range, upload, messages d'aide et d'erreur.
- Information : alerte, notice, badge, mise en avant, mise en exergue, tooltip.
- Contenu : accordéon, carte, tuile, tableau, citation, téléchargement, transcription, média.
- Services publics : FranceConnect, consentement cookies, paramètres d'affichage, sélecteur de langue.

## À vérifier dans la doc officielle si besoin

- `combobox` ;
- `dropdown` ;
- `segmented` ;
- `tabnav` ;
- `user_header` ;
- `composition`.

Ces composants peuvent avoir un statut bêta ou une couverture locale incomplète. Marquer `à vérifier` si la page officielle n'a pas été lue.

## Contrat de spécification

Nommer pour chaque composant clé :

- source officielle ou référence locale ;
- variante : taille, importance, état, orientation, densité ou comportement ;
- propriétés : titre, description, aide, erreur, lien, icône, pictogramme, média ;
- états : par défaut, focus, hover, actif, désactivé, erreur, succès, ouvert, fermé ;
- contraintes responsive ;
- dépendances : JS DSFR, icônes, mode clair/sombre, composant parent ;
- interdits : override structurel, style custom, token transposé entre modes, lien factice.

Si une ligne manque, continuer avec le composant officiel le plus proche et marquer `à vérifier`. Compléter avant publication ou handoff d'intégration.

## Frameworks et extensions

- Lire `package.json`, lockfile et imports avant de choisir l'intégration.
- DSFR direct : charger CSS, icônes, favicons et JS selon le package installé.
- `react-dsfr` ou `ngx-dsfr` : suivre l'API du portage et ne pas mélanger avec les snippets HTML sans preuve projet.
- Datavisualisation : chercher `dsfr-chart` ou une règle projet avant de créer une palette custom.
- Courriel : vérifier `dsfr-mail` ou un template dédié.

## Version et runtime

- Projet avec version déclarée : suivre le projet.
- Projet sans version : utiliser `DESIGN.md` et `tokens.yaml`, puis marquer `version projet à vérifier`.
- Version RC : marquer `version pré-release`, ne pas promettre une compatibilité production.
- Portage framework : le portage guide l'intégration, les principes DSFR restent l'autorité de design.
