# Logo

Référence extraite de `../structure.md`.

---

## Logo officiel (variante bloc marque DSFR)
```html
<p class="fr-logo">
    République<br>Française
</p>
```
**Condition d'usage** : Ce bloc est requis dans un header DSFR institutionnel
officiel, mais il n'est pas injecté par défaut par ce skill (`brand-mode
neutral`). Ne l'utiliser que si le service est autorisé à afficher la marque de
l'État et si la livraison vérifie le cadre de publication.

## Logo opérateur (optionnel)
```html
<div class="fr-header__operator">
    <img class="fr-responsive-img" style="max-width:3.5rem;" src="logo-operateur.svg" alt="Nom de l'opérateur">
</div>
```
**Note** : le logo opérateur se place dans `fr-header__operator` dans le
header, à côté du logo République Française. `generate_component.py logo
--config '{"operator_src": "…"}'` pose `3.5rem`, la largeur de l'exemple
officiel au ratio 3x4, et l'expose par `operator_max_width` ; le paquet 1.15.3
utilise aussi `8rem` et `9.0625rem` pour les logos au ratio 16x9.

---
