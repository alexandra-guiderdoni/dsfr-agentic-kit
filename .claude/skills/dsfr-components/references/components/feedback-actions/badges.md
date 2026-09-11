# Badges

Référence extraite de `../feedback-actions.md`.

---

## Types de badges
- `fr-badge` : Badge standard (gris)
- `fr-badge fr-badge--info` : Information (bleu)
- `fr-badge fr-badge--success` : Succès (vert)
- `fr-badge fr-badge--warning` : Avertissement (orange)
- `fr-badge fr-badge--error` : Erreur (rouge)
- `fr-badge fr-badge--new` : Nouveau (vert menthe)

## Tailles
- `fr-badge--sm` : Petit
- Par défaut : Moyen

## Badges avec icônes
```html
<p class="fr-badge fr-badge--success fr-badge--icon-left fr-icon-check-line">
    Validé
</p>
```

## Groupe de badges
```html
<ul class="fr-badges-group">
    <li><span class="fr-badge fr-badge--info">Badge 1</span></li>
    <li><span class="fr-badge fr-badge--success">Badge 2</span></li>
</ul>
```

Depuis DSFR 1.15.3 (#1498), un badge dans un groupe est un `span`, jamais un
`p` : dès que le badge est placé dans un élément qui possède sa propre
sémantique (`li`, `p`…), utiliser `span`. Le badge isolé reste un `p`. Le
générateur `generate_component.py badge` accepte `markup` (`p` ou `span`) ; le
bloc `badges` du builder assemblé émet des `span`.

---
