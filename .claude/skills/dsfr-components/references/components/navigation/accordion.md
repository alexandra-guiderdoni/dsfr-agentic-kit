# Accordéons

Référence extraite de `../navigation.md`.

---

## Structure de base
```html
<div class="fr-accordions-group">
    <section class="fr-accordion">
        <h3 class="fr-accordion__title">
            <button type="button" class="fr-accordion__btn" aria-expanded="false" aria-controls="accordion-1">
                Titre de l'accordéon
            </button>
        </h3>
        <div class="fr-collapse" id="accordion-1">
            <p>Contenu de l'accordéon</p>
        </div>
    </section>
</div>
```

## Accordéon ouvert par défaut
```html
<section class="fr-accordion">
    <h3 class="fr-accordion__title">
        <button type="button" class="fr-accordion__btn" aria-expanded="true" aria-controls="accordion-open">
            Accordéon ouvert
        </button>
    </h3>
    <div class="fr-collapse fr-collapse--expanded" id="accordion-open">
        <p>Ce contenu est visible par défaut</p>
    </div>
</section>
```
**Note** : Combiner `aria-expanded="true"` sur le bouton ET `fr-collapse--expanded` sur le contenu.

---
