# Contrats détaillés des tests WCAG Playwright

Ces contrats guident l'implémentation des neuf tests de
`tests-conformite-wcag`. Ils complètent la matrice de couverture.

## Reflow

Critère : WCAG 1.4.10 Redistribution, niveau AA.

Méthode :

1. Utiliser un viewport `320 x 256`.
2. Mesurer `document.documentElement.scrollWidth`.
3. Vérifier `scrollWidth <= 320`.
4. Scanner les débordements avec `getBoundingClientRect()`.
5. Identifier les conteneurs avec `overflow-x: scroll` ou `overflow-x: auto`.

Succès : aucun scroll horizontal et aucun contenu inaccessible à 320 px.

Échec : `scrollWidth > 320` ou élément qui déborde du viewport.

## Spacing

Critère : WCAG 1.4.12 Espacement du texte, niveau AA.

Méthode :

1. Capturer les dimensions initiales des éléments textuels.
2. Injecter les styles suivants :

```css
* {
  line-height: 1.5 !important;
  letter-spacing: 0.12em !important;
  word-spacing: 0.16em !important;
}
p, li, dd, dt, blockquote, td, th, caption, label, legend {
  margin-bottom: 2em !important;
}
```

3. Re-mesurer les éléments textuels.
4. Détecter les conteneurs `overflow: hidden` ou `overflow: clip`.
5. Comparer `scrollHeight > clientHeight` et `scrollWidth > clientWidth`.

Succès : aucun contenu textuel masqué ou tronqué.

Échec : texte perdu, masqué ou tronqué après injection.

## Zoom

Critère : WCAG 1.4.4 Redimensionnement du texte, niveau AA.

Méthode :

1. Capturer la page à `1280 x 720`.
2. Simuler le zoom 200 % avec un viewport `640 x 360`.
3. Détecter débordements, chevauchements et texte tronqué.
4. Vérifier que `meta viewport` ne bloque pas le zoom.

Succès : contenu lisible et fonctionnel à 200 %.

Échec : contenu tronqué, chevauchement, `user-scalable=no` ou
`maximum-scale < 2`.

## Orientation

Critère : WCAG 1.3.4 Orientation, niveau AA.

Méthode :

1. Charger en portrait `375 x 812`, puis en paysage `812 x 375`.
2. Chercher des media queries d'orientation qui masquent du contenu.
3. Chercher `transform: rotate(90deg)` sur le `body` ou les conteneurs majeurs.
4. Chercher les messages demandant de tourner l'appareil.

Succès : contenu utilisable en portrait et paysage.

Échec : contenu masqué, message de rotation forcée ou orientation imposée.

## Autocomplete

Critère : WCAG 1.3.5 Identification de la finalité de la saisie, niveau AA.

Méthode :

1. Scanner `input`, `select` et `textarea`.
2. Inférer la finalité avec `name`, `id`, `placeholder`, `label` et `type`.
3. Vérifier l'attribut `autocomplete` attendu.
4. Couvrir identité, contact, adresse, paiement, authentification et données
   personnelles usuelles.

Valeurs fréquentes : `name`, `given-name`, `family-name`, `email`, `tel`,
`street-address`, `postal-code`, `cc-number`, `username`, `new-password`,
`current-password`, `bday`, `organization`.

Succès : les champs personnels ont un `autocomplete` approprié.

Échec : champ personnel sans `autocomplete` ou avec valeur incorrecte.

## Time

Critère : WCAG 2.2.1 Réglage du délai, niveau A.

Méthode :

1. Détecter `<meta http-equiv="refresh">`.
2. Détecter les comptes à rebours.
3. Intercepter `setTimeout` et `setInterval` qui redirigent ou modifient
   fortement le DOM.
4. Chercher les mécanismes de pause, arrêt ou extension.

Succès : aucun délai imposé sans contrôle utilisateur.

Échec : redirection temporisée, compte à rebours ou expiration sans contrôle.

## Autoplay

Critères : WCAG 1.4.2 Contrôle du son et 2.2.2 Mettre en pause, arrêter,
masquer, niveau A.

Méthode :

1. Détecter `audio` et `video` en `autoplay`.
2. Détecter les appels JavaScript `play()`.
3. Vérifier `muted`, la durée et les contrôles de pause.
4. Détecter les animations de plus de cinq secondes.
5. Vérifier la prise en compte de `prefers-reduced-motion`.

Succès : média automatique contrôlable, son coupé par défaut si nécessaire.

Échec : audio automatique non muet, média sans pause, animation longue sans
contrôle.

## Focus

Critère : WCAG 2.4.7 Visibilité du focus, niveau AA.

Méthode :

1. Lister liens, boutons, champs et éléments `tabindex >= 0`.
2. Simuler le focus avec `element.focus()` ou `Tab`.
3. Capturer `outline`, `box-shadow`, `border`, `background-color` et `color`.
4. Comparer les styles avant et pendant le focus.
5. Détecter `outline: none` sans remplacement visible.

Succès : chaque élément interactif a un indicateur de focus visible.

Échec : focus invisible, contraste insuffisant ou suppression d'outline sans
remplacement.

## Target

Critères : WCAG 2.5.8 Taille de la cible minimum, niveau AA, et 2.5.5 Taille
de la cible, niveau AAA.

Méthode :

1. Lister `a`, `button`, `input`, `select`, `textarea`, rôles interactifs,
   `onclick` et `[tabindex]`.
2. Mesurer largeur, hauteur et espacement avec `getBoundingClientRect()`.
3. Évaluer le seuil AA `24 x 24 px` ou un espacement compensatoire.
4. Signaler le seuil AAA `44 x 44 px` sans en faire le verdict AA.
5. Exclure les liens inline et les tailles imposées par l'agent utilisateur.

Succès : chaque cible respecte le seuil AA ou son exception documentée.

Échec : cible inférieure à `24 x 24 px` sans compensation ni exception.
