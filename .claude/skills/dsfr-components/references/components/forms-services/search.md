# Barre de recherche (Search)

Référence extraite de `../forms-services.md`.

---

## Recherche simple
```html
<div class="fr-search-bar" id="search-1" role="search">
    <label class="fr-label" for="search-input">Recherche</label>
    <input class="fr-input" placeholder="Rechercher" type="search" id="search-input" name="search">
    <button type="submit" class="fr-btn" title="Rechercher">
        Rechercher
    </button>
</div>
```

## Recherche large
```html
<div class="fr-search-bar fr-search-bar--lg" id="search-2" role="search">
    <label class="fr-label" for="search-lg">Recherche</label>
    <input class="fr-input" placeholder="Rechercher" type="search" id="search-lg" name="search">
    <button type="submit" class="fr-btn" title="Rechercher">
        Rechercher
    </button>
</div>
```

## Tailles
- Par défaut : Standard
- `fr-search-bar--lg` : Grande. Dans le header DSFR 1.15.2, la contrainte de largeur vient surtout du placement dans `fr-header__tools` et du conteneur interne `fr-container fr-container-lg--fluid` documentés dans `structure.md`.

**Obligatoire** : `role="search"` sur le conteneur, `type="search"` sur l'input,
un `<label>` associé (même masqué visuellement via `fr-label`) et, depuis DSFR
1.15.0 (#1432), `type="submit"` sur le bouton.

## Intégration dans un formulaire

La barre doit être placée dans un `<form>` pour fonctionner sans JavaScript ;
le fragment ci-dessus est à insérer tel quel dans le formulaire du service :

```html
<form action="/recherche" method="get">
    <div class="fr-search-bar" id="search-1" role="search">
        …
    </div>
</form>
```

Le générateur `generate_component.py search` produit le fragment seul ; les
pages de `generate_page.py` et le composant `header` (option `search`)
posent le `<form>` eux-mêmes.

---
