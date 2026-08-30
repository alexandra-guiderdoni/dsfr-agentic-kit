# Boutons

Référence extraite de `../feedback-actions.md`.

---

## Variantes principales
- `fr-btn` : Bouton principal (fond bleu)
- `fr-btn fr-btn--secondary` : Bouton secondaire (contour bleu)
- `fr-btn fr-btn--tertiary` : Bouton tertiaire (sans contour)
- `fr-btn fr-btn--tertiary-no-outline` : Bouton tertiaire sans bordure

## Tailles
- `fr-btn--sm` : Petit
- Par défaut : Moyen
- `fr-btn--lg` : Grand

## Icônes
- `fr-btn--icon-left fr-icon-[nom]` : Icône à gauche
- `fr-btn--icon-right fr-icon-[nom]` : Icône à droite

## Bouton icône seule (icon-only)
```html
<button type="button" class="fr-btn fr-icon-add-line" title="Ajouter un élément">Ajouter un élément</button>
```
**Règle** : garder le libellé dans le bouton, comme le paquet officiel — le CSS
le tronque visuellement et le nom accessible survit à une copie partielle.
`title` recommandé ; `aria-label` seulement si aucun texte ne peut rester dans
le bouton.

## Groupe de boutons
```html
<ul class="fr-btns-group">
    <li><button type="button" class="fr-btn">Action principale</button></li>
    <li><button type="button" class="fr-btn fr-btn--secondary">Action secondaire</button></li>
</ul>
```

Variantes de groupe :
- `fr-btns-group--inline` : Boutons en ligne (défaut : empilés)
- `fr-btns-group--inline-sm` / `--inline-md` / `--inline-lg` : En ligne à partir du breakpoint
- `fr-btns-group--icon-left` / `--icon-right` : Position des icônes du groupe
- `fr-btns-group--sm` / `--lg` : Taille uniforme du groupe

## États
- `disabled` : bouton désactivé, retiré du parcours clavier
- `aria-disabled="true"` : bouton conservé focusable, indisponibilité annoncée
  — ne pas cumuler avec `disabled`
- `aria-pressed` n'est piloté par le script DSFR que sur `fr-tag` (voir
  [`feedback-actions/tags.md`](tags.md)). Sur un `fr-btn`, l'état reste figé sur
  sa valeur initiale tant que le JS du service ne le met pas à jour

---
