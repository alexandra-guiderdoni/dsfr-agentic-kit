# Validation différée des contraintes

Référence extraite de `../patterns.md`.

---

Ne pas laisser l'état `invalid` natif fuir au repos sur les formulaires
générés. Un champ `required` vide, ou un `pattern` déjà posé, peut être exposé
comme invalide dans l'arbre d'accessibilité avant toute action utilisateur.

Pattern recommandé :

- ne pas poser `required`, `aria-required` ou `pattern` dans le HTML statique ;
- conserver les labels, aides, `autocomplete`, `inputmode` et `maxlength` ;
- poser `required`, `aria-required` et `pattern` en JavaScript au premier
  `submit`, juste avant `checkValidity()` ou la validation DSFR personnalisée ;
- retirer ces contraintes au `reset` si le formulaire revient à l'état repos ;
- garder la validation serveur comme source de vérité. Sans JavaScript, il n'y
  a pas de validation client : c'est préférable à une erreur annoncée avant
  action sur un service public.

Qui pose quoi, dans ce skill : le script inline produit par
`generate_page.py` pose `required` et `aria-required` au premier `submit`, et
**rien d'autre**. Aucun générateur du skill n'expose d'option `pattern` et
aucun n'en émet : le `pattern` différé, appelé par `patterns/telephone.md` et
`patterns/adresse-ban.md`, est à écrire par l'intégrateur, sur le modèle de
`patternById` ci-dessous.

```javascript
var requiredFieldIds = ['prenom', 'nom', 'email'];
var patternById = { telephone: '(\\+33|0)\\s?[1-9](\\s?\\d{2}){4}' };

function applyClientConstraints() {
  requiredFieldIds.forEach(function (id) {
    var field = document.getElementById(id);
    if (!field) return;
    field.required = true;
    field.setAttribute('aria-required', 'true');
  });
  Object.keys(patternById).forEach(function (id) {
    var field = document.getElementById(id);
    if (field) field.setAttribute('pattern', patternById[id]);
  });
}
```
