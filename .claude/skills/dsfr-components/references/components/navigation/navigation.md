# Navigation

Référence extraite de `../navigation.md`.

---

## Fil d'Ariane
```html
<nav role="navigation" class="fr-breadcrumb" aria-label="vous êtes ici :">
    <button type="button" class="fr-breadcrumb__button" aria-expanded="false" aria-controls="breadcrumb">
        Voir le fil d'Ariane
    </button>
    <div class="fr-collapse" id="breadcrumb">
        <ol class="fr-breadcrumb__list">
            <li><a class="fr-breadcrumb__link" href="/">Accueil</a></li>
            <li><a class="fr-breadcrumb__link" href="/">Niveau 1</a></li>
            <li><a class="fr-breadcrumb__link" aria-current="page">Page courante</a></li>
        </ol>
    </div>
</nav>
```

## Menu de navigation
```html
<nav class="fr-nav" role="navigation" aria-label="Menu principal">
    <ul class="fr-nav__list">
        <li class="fr-nav__item">
            <button type="button" class="fr-nav__btn" aria-expanded="false" aria-controls="nav-1">
                Menu avec sous-menu
            </button>
            <div class="fr-collapse" id="nav-1">
                <ul class="fr-menu__list">
                    <li><a class="fr-nav__link" href="/">Sous-item 1</a></li>
                    <li><a class="fr-nav__link" href="/">Sous-item 2</a></li>
                </ul>
            </div>
        </li>
        <li class="fr-nav__item">
            <a class="fr-nav__link" href="/" aria-current="page">Lien actif</a>
        </li>
    </ul>
</nav>
```

## Pagination
```html
<nav role="navigation" class="fr-pagination" aria-label="Pagination">
    <ul class="fr-pagination__list">
        <li>
            <a class="fr-pagination__link fr-pagination__link--first" href="/">
                Première page
            </a>
        </li>
        <li>
            <a class="fr-pagination__link fr-pagination__link--prev" href="/">
                Page précédente
            </a>
        </li>
        <li><a class="fr-pagination__link" href="/" aria-current="page">1</a></li>
        <li><a class="fr-pagination__link" href="/">2</a></li>
        <li><a class="fr-pagination__link" href="/">3</a></li>
        <li>
            <a class="fr-pagination__link fr-pagination__link--next" href="/">
                Page suivante
            </a>
        </li>
        <li>
            <a class="fr-pagination__link fr-pagination__link--last" href="/">
                Dernière page
            </a>
        </li>
    </ul>
</nav>
```

Lien de pagination désactivé, sans `href` : c'est le seul cas où le paquet
officiel pose `role="link"`, pour que l'élément reste exposé comme un lien.

```html
<li>
    <a class="fr-pagination__link fr-pagination__link--first" title="Première page" aria-disabled="true" role="link">
        Première page
    </a>
</li>
```

## Liens de navigation latérale (Sidemenu)
```html
<nav class="fr-sidemenu" aria-labelledby="sidemenu-title">
    <div class="fr-sidemenu__inner">
        <button type="button" class="fr-sidemenu__btn" aria-controls="sidemenu-list" aria-expanded="false">
            Dans cette rubrique
        </button>
        <div class="fr-collapse" id="sidemenu-list">
            <div class="fr-sidemenu__title" id="sidemenu-title">Titre de la rubrique</div>
            <ul class="fr-sidemenu__list">
                <li class="fr-sidemenu__item">
                    <a class="fr-sidemenu__link" href="/" aria-current="page">Page active</a>
                </li>
                <li class="fr-sidemenu__item">
                    <a class="fr-sidemenu__link" href="/">Autre page</a>
                </li>
            </ul>
        </div>
    </div>
</nav>
```

---
