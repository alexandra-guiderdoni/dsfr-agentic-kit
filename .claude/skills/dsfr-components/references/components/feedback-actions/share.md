# Partage

Référence vérifiée dans les exemples officiels DSFR 1.13.2 et 1.15.3 :

- https://unpkg.com/@gouvfr/dsfr@1.13.2/example/component/share/index.html
- https://unpkg.com/@gouvfr/dsfr@1.15.3/example/component/share/index.html

## Boutons de partage par défaut

```html
<div class="fr-share">
  <p class="fr-share__title">Partager la page</p>
  <ul class="fr-btns-group">
    <li><a class="fr-btn fr-btn--facebook" href="https://example.test" target="_blank" rel="noopener external">Partager sur Facebook</a></li>
    <li><a class="fr-btn fr-btn--mail" href="mailto:?subject=Titre&amp;body=URL">Partager par email</a></li>
    <li><button class="fr-btn fr-btn--copy" type="button">Copier dans le presse-papier</button></li>
  </ul>
</div>
```

## Version inactive

```html
<div class="fr-share">
  <p class="fr-share__title">Partager la page</p>
  <p class="fr-share__text">Veuillez autoriser le dépôt de cookies pour partager sur les réseaux sociaux.</p>
  <ul class="fr-btns-group">
    <li><a class="fr-btn fr-btn--facebook" aria-disabled="true" role="link">Partager sur Facebook</a></li>
    <li><button class="fr-btn fr-btn--copy" type="button">Copier dans le presse-papier</button></li>
  </ul>
</div>
```

## Règles

- Le groupe actuel utilise `fr-btns-group`.
- Les actions utilisent `fr-btn` et un modificateur de plateforme ou d’action.
- Les liens réellement ouverts dans une nouvelle fenêtre utilisent `target="_blank"` et `rel="noopener external"`.
- La variante historique avec `fr-share__group` et `fr-share__link` est dépréciée dans les exemples 1.13.2 et 1.15.3.
