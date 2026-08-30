# Carte horizontale tier

<a id="carte-horizontale-tier"></a>
<a id="carte-didentite-numerique-display"></a>

Référence extraite de `../content-media.md`.

---

Composition locale bâtie sur la carte `fr-card--horizontal-tier`, pour
présenter une entité (organisme, service, personne) avec ses métadonnées.

**Ne pas confondre avec `display`** : le nom `display` désigne le composant
officiel « Paramètre d'affichage », documenté dans
[`content-media/display.md`](display.md) et produit par
`generate_component.py display`. La composition ci-dessous n'a pas de nom
générable ; elle s'écrit à la main.

## Structure
```html
<div class="fr-card fr-card--horizontal-tier">
    <div class="fr-card__body">
        <div class="fr-card__content">
            <h3 class="fr-card__title">
                <a href="/">Nom de l'organisme</a>
            </h3>
            <p class="fr-card__desc">Description de l'organisme ou du service</p>
            <div class="fr-card__start">
                <ul class="fr-badges-group">
                    <li><p class="fr-badge fr-badge--green-emeraude">Actif</p></li>
                </ul>
            </div>
            <div class="fr-card__end">
                <p class="fr-card__detail fr-icon-map-pin-2-line">Paris, France</p>
                <p class="fr-card__detail fr-icon-calendar-line">Créé le 15 janvier 2024</p>
            </div>
        </div>
    </div>
    <div class="fr-card__header">
        <div class="fr-card__img">
            <img class="fr-responsive-img" src="logo.png" alt="Logo de l'organisme">
        </div>
    </div>
</div>
```

**Règles** :
- Variante de la carte horizontale avec métadonnées structurées
- `fr-card__start` pour les badges/statuts, `fr-card__end` pour les détails
- `fr-card__detail` se pose sur un `<p>`, jamais sur un `<ul>` : la règle
  officielle `.fr-card__detail{display:flex;flex-direction:row}` mettrait
  les `<li>` côte à côte sur une seule ligne
- L'icône est portée par une classe `fr-icon-*` sur le paragraphe lui-même
