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
    <li><span class="fr-tag">Tag 1</span></li>
    <li><span class="fr-tag">Tag 2</span></li>
    <li><span class="fr-tag">Tag 3</span></li>
</ul>
```

Le builder reprend les groupes statiques en `span` des exemples DSFR 1.15.4
(PR 1539). Un tag statique isolé garde `p` ; les liens et boutons gardent leur
comportement. `generate_tag(..., markup="span")` permet ce contexte sans
changer le format `page.json`.

Limite de la référence officielle : `tags-group.ejs` ne force pas la balise
et `tag.ejs` conserve le défaut `p`. Le contrôle des sorties du builder exige
donc `span` dans ses groupes, tandis que l’audit général accepte les textes
valides en `p` ou `span` sans interdire tous les groupes en `p`.

---
