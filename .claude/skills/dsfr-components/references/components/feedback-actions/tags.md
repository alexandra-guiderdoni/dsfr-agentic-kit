# Tags

Référence extraite de `../feedback-actions.md`.

---

## Tag simple
```html
<p class="fr-tag">Libellé du tag</p>
```

## Tag avec lien
```html
<a href="/" class="fr-tag">Libellé du tag</a>
```

## Tag avec icône
```html
<p class="fr-tag fr-icon-arrow-right-line fr-tag--icon-left">Libellé</p>
```

Seul `fr-tag--icon-left` est officiel en DSFR 1.15.3 (`fr-tag--icon-right`
n'existe pas ; vérifié dans `dist/dsfr.min.css`).

## Tailles
- `fr-tag--sm` : Petit
- Par défaut : Moyen

## Tag supprimable
```html
<button class="fr-tag fr-tag--dismiss" type="button" aria-label="Retirer le filtre Libellé">
    Libellé
</button>
```
**Obligatoire** : `aria-label` décrivant l'action de suppression. Brancher la
suppression hors HTML statique.

## Tag sélectable
```html
<ul class="fr-tags-group">
    <li>
        <button type="button" class="fr-tag" aria-pressed="false">Tag 1</button>
    </li>
    <li>
        <button type="button" class="fr-tag" aria-pressed="true">Tag 2 (sélectionné)</button>
    </li>
</ul>
```
**Obligatoire** : `aria-pressed` pour indiquer l'état sélectionné.

## Groupe de tags
```html
<ul class="fr-tags-group">
    <li><p class="fr-tag">Tag 1</p></li>
    <li><p class="fr-tag">Tag 2</p></li>
    <li><p class="fr-tag">Tag 3</p></li>
</ul>
```

---
