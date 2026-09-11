# Cartes

Référence extraite de `../content-media.md`.

---

## Carte standard
```html
<div class="fr-card">
    <div class="fr-card__body">
        <div class="fr-card__content">
            <h3 class="fr-card__title">
                <a href="/">Titre de la carte</a>
            </h3>
            <p class="fr-card__desc">Description de la carte</p>
            <div class="fr-card__start">
                <p class="fr-card__detail fr-icon-arrow-right-line">Détail</p>
            </div>
        </div>
    </div>
    <div class="fr-card__header">
        <div class="fr-card__img">
            <img src="image.jpg" alt="" class="fr-responsive-img">
        </div>
    </div>
</div>
```

## Carte horizontale
```html
<div class="fr-card fr-card--horizontal">
    <div class="fr-card__body">
        <div class="fr-card__content">
            <h3 class="fr-card__title">
                <a href="/">Titre</a>
            </h3>
            <p class="fr-card__desc">Description</p>
        </div>
    </div>
    <div class="fr-card__header">
        <div class="fr-card__img">
            <img src="image.jpg" alt="" class="fr-responsive-img">
        </div>
    </div>
</div>
```

## Carte avec zone de clic étendue (enlarge-link)
```html
<div class="fr-card fr-enlarge-link">
    <div class="fr-card__body">
        <div class="fr-card__content">
            <h3 class="fr-card__title">
                <a href="/">Toute la carte est cliquable</a>
            </h3>
            <p class="fr-card__desc">Description</p>
        </div>
    </div>
</div>
```
**Note** : `fr-enlarge-link` étend la zone de clic du `<a>` à toute la carte.

## Carte avec badge
```html
<div class="fr-card">
    <div class="fr-card__body">
        <div class="fr-card__content">
            <h3 class="fr-card__title">
                <a href="/">Titre de la carte</a>
            </h3>
            <p class="fr-card__desc">Description</p>
            <div class="fr-card__start">
                <ul class="fr-badges-group">
                    <li><span class="fr-badge fr-badge--info fr-badge--sm">Nouveau</span></li>
                </ul>
            </div>
        </div>
    </div>
</div>
```

## Carte téléchargement
```html
<div class="fr-card fr-card--download">
    <div class="fr-card__body">
        <div class="fr-card__content">
            <h3 class="fr-card__title">
                <a download href="document.pdf">Télécharger le document</a>
            </h3>
            <p class="fr-card__desc">Description du document</p>
            <div class="fr-card__end">
                <p class="fr-card__detail">PDF — 1,2 Mo</p>
            </div>
        </div>
    </div>
</div>
```

## Carte sans bordure / avec fond gris
- `fr-card--no-border` : Sans bordure
- `fr-card--grey` : Fond gris
- `fr-card--shadow` : Avec ombre portée

---
