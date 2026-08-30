# Patterns de faux positifs DSFR connus

Reference pour eviter les faux positifs lors de l'inspection DOM sur des sites utilisant le DSFR.

## Principe

Un composant DSFR qui se comporte conformement a sa specification n'est PAS une NC, meme si le comportement semble suspect au regard des regles WCAG generiques. Verifier la documentation DSFR AVANT de conclure.

## Faux positifs documentes

### Header DSFR — modale navigation mobile

- **Symptome** : `role="dialog"` absent sur le conteneur de navigation mobile
- **Raison** : en desktop, le header est inline (pas une modale). Le `role="dialog"` n'est ajoute qu'en mode mobile via JavaScript (`focus-trap.js`)
- **Verdict** : PAS de ticket en desktop. NOTE-INTERNE si le comportement mobile n'a pas ete verifie

### Header DSFR — focus initial modale recherche

- **Symptome** : le focus initial atterrit sur le bouton Fermer au lieu du champ de recherche
- **Raison** : `focus-trap.js` du DSFR prend le premier element focusable dans la modale
- **Verdict** : NOTE-INTERNE (comportement DSFR natif, peut etre ameliore mais pas un defaut d'integration)

### Landmarks redondants

- **Symptome** : `<header role="banner">`, `<nav role="navigation">`, `<main role="main">`
- **Raison** : le DSFR ajoute ces roles par precaution de compatibilite avec les anciens AT
- **Verdict** : RECO (bruit ARIA, pas une NC)

### Sommaire DSFR — aria-labelledby orphelin

- **Symptome** : `aria-labelledby` pointe vers un `id` absent dans le DOM
- **Raison** : defaut d'integration CMS (le DSFR prevoit l'`id`, le template Drupal/Twig l'omet)
- **Verdict** : NC (defaut d'integration, pas du DSFR natif)

### Cartes et tuiles — niveau de titre

- **Symptome** : les titres des cartes sont des `<h2>` alors que le contexte attend des `<h3>`
- **Raison** : le composant DSFR carte utilise un niveau de titre parametrable. Le defaut est dans la configuration CMS, pas dans le DSFR
- **Verdict** : NC (defaut d'integration CMS)

## Attribution de cause racine

Pour chaque defaut impliquant un composant DSFR :

1. Recuperer le markup de reference depuis `systeme-de-design.gouv.fr`
2. Comparer le code du site audite au markup DSFR natif
3. Verifier s'il existe une issue ouverte sur `github.com/GouvernementFR/dsfr`
4. **Distinguer** :
   - **Defaut DSFR natif** : imputable au design system, a remonter en issue GitHub
   - **Defaut d'integration CMS** : imputable au prestataire, a corriger dans le template

## Screenshots d'etats interactifs

Ne PAS se contenter d'un screenshot au chargement pour les composants dynamiques :

- Modale ouverte (`take_screenshot` apres `click` sur le bouton declencheur)
- Menu mobile deploye
- Accordeon ouvert
- Focus visible sur un element interactif (Tab puis `take_screenshot`)
- Emulation mobile si le composant a un comportement responsive different
