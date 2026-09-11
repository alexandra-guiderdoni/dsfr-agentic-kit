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
- `fr-search-bar--lg` : Grande. Dans le header DSFR 1.15.3, la contrainte de largeur vient surtout du placement dans `fr-header__tools` et du conteneur interne `fr-container fr-container-lg--fluid` documentés dans `structure.md`.

## Variante avec libellé visible

Depuis DSFR 1.15.3 (#1516), `fr-search-bar--labelled` sur le conteneur rend le
libellé visible, au-dessus du champ ; par défaut il reste positionné hors écran.
Ne pas utiliser cette variante pour la recherche globale du header, où le
libellé est déjà porté par le bouton. Le générateur `generate_component.py
search` accepte `labelled`.

```html
<div class="fr-search-bar fr-search-bar--labelled" id="search-3" role="search">
    <label class="fr-label" for="search-labelled">Rechercher un service</label>
    <input class="fr-input" placeholder="Rechercher" type="search" id="search-labelled" name="search" aria-describedby="search-labelled-messages">
    <div class="fr-messages-group" id="search-labelled-messages" aria-live="polite"></div>
    <button type="submit" class="fr-btn" title="Rechercher">
        Rechercher
    </button>
</div>
```

La même version documente un message d'erreur ou de succès dans la barre : un
`div.fr-messages-group` relié au champ par `aria-describedby`, contenant un
`p.fr-message.fr-message--error` ou `--valid`. Comme les exemples officiels
1.15.3, le générateur émet ce groupe vide, `id="<champ>-messages"`, relié par
`aria-describedby` ; le service y insère son message s'il renvoie un état.

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
