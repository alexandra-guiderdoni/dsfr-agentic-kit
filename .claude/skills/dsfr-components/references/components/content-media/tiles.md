# Tuiles

Référence extraite de `../content-media.md`.

---

## Tuile verticale (standard)
```html
<div class="fr-tile fr-enlarge-link">
    <div class="fr-tile__body">
        <div class="fr-tile__content">
            <h3 class="fr-tile__title">
                <a href="/">Titre de la tuile</a>
            </h3>
            <p class="fr-tile__desc">Description courte de la tuile qui explicite le contenu ou la destination</p>
        </div>
    </div>
    <div class="fr-tile__header">
        <div class="fr-tile__pictogram">
            <svg aria-hidden="true" class="fr-artwork" viewBox="0 0 80 80" width="80" height="80">
                <use class="fr-artwork-decorative" href="/dsfr/artwork/pictograms/digital/avatar.svg#artwork-decorative"></use>
                <use class="fr-artwork-minor" href="/dsfr/artwork/pictograms/digital/avatar.svg#artwork-minor"></use>
                <use class="fr-artwork-major" href="/dsfr/artwork/pictograms/digital/avatar.svg#artwork-major"></use>
            </svg>
        </div>
    </div>
</div>
```

## Tuile horizontale
```html
<div class="fr-tile fr-tile--horizontal fr-enlarge-link">
    <div class="fr-tile__body">
        <div class="fr-tile__content">
            <h3 class="fr-tile__title">
                <a href="/">Titre de la tuile</a>
            </h3>
            <p class="fr-tile__desc">Description</p>
        </div>
    </div>
    <div class="fr-tile__header">
        <div class="fr-tile__pictogram">
            <svg aria-hidden="true" class="fr-artwork" viewBox="0 0 80 80" width="80" height="80">
                <use class="fr-artwork-decorative" href="/dsfr/artwork/pictograms/digital/avatar.svg#artwork-decorative"></use>
                <use class="fr-artwork-minor" href="/dsfr/artwork/pictograms/digital/avatar.svg#artwork-minor"></use>
                <use class="fr-artwork-major" href="/dsfr/artwork/pictograms/digital/avatar.svg#artwork-major"></use>
            </svg>
        </div>
    </div>
</div>
```

## Tuile de téléchargement
```html
<div class="fr-tile fr-tile--download fr-enlarge-link">
    <div class="fr-tile__body">
        <div class="fr-tile__content">
            <h3 class="fr-tile__title">
                <a download href="document.pdf">Télécharger le formulaire</a>
            </h3>
            <p class="fr-tile__desc">Description du document à télécharger</p>
            <div class="fr-tile__start">
                <p class="fr-tile__detail">PDF — 2,3 Mo</p>
            </div>
        </div>
    </div>
</div>
```

## Variantes de tuile
- `fr-tile--sm` : Petite tuile
- `fr-tile--horizontal` : Disposition horizontale
- `fr-tile--vertical` : Disposition verticale (défaut)
- `fr-tile--download` : Tuile de téléchargement
- `fr-tile--no-border` : Sans bordure
- `fr-tile--grey` : Fond gris
- `fr-tile--shadow` : Avec ombre portée

---
