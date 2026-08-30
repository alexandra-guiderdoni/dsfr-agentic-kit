# Citation (Quote)

Référence extraite de `../content-media.md`.

---

## Citation simple
```html
<figure class="fr-quote">
    <blockquote cite="https://example.com">
        <p>Texte de la citation qui doit être fidèle à la source originale.</p>
    </blockquote>
    <figcaption>
        <p class="fr-quote__author">Prénom Nom</p>
        <ul class="fr-quote__source">
            <li>
                <cite>Titre de l'ouvrage ou de la source</cite>
            </li>
        </ul>
    </figcaption>
</figure>
```

## Citation avec image
```html
<figure class="fr-quote fr-quote--column">
    <blockquote cite="https://example.com">
        <p>Texte de la citation.</p>
    </blockquote>
    <figcaption>
        <p class="fr-quote__author">Prénom Nom</p>
        <ul class="fr-quote__source">
            <li><cite>Source</cite></li>
        </ul>
        <div class="fr-quote__image">
            <img src="photo.jpg" alt="" class="fr-responsive-img">
        </div>
    </figcaption>
</figure>
```

**Règle** : l'alternative de l'image (`alt`) doit rester vide. L'image est
illustrative et ne doit pas être restituée aux technologies d'assistance ;
l'auteur est déjà porté par `fr-quote__author`.

## Variantes
- `fr-quote--column` : Disposition en colonne (image à côté)
- Couleurs d'accentuation : `fr-quote--green-emeraude`, etc. (mêmes que highlight/callout)

---
