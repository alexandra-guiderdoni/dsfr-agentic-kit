# En-tête (Header)

Référence extraite de `../structure.md`.

---

## Header simple
```html
<header role="banner" class="fr-header">
    <div class="fr-header__body">
        <div class="fr-container">
            <div class="fr-header__body-row">
                <div class="fr-header__brand fr-enlarge-link">
                    <div class="fr-header__brand-top">
                        <div class="fr-header__logo">
                            <p class="fr-logo">
                                République<br>Française
                            </p>
                        </div>
                    </div>
                    <div class="fr-header__service">
                        <a href="/" title="Accueil — Nom du service — République Française">
                            <p class="fr-header__service-title">Nom du service</p>
                        </a>
                        <p class="fr-header__service-tagline">Baseline — précisions sur le service</p>
                    </div>
                </div>
            </div>
        </div>
    </div>
</header>
```

## Header avec navigation et recherche
```html
<header role="banner" class="fr-header">
    <div class="fr-header__body">
        <div class="fr-container">
            <div class="fr-header__body-row">
                <div class="fr-header__brand fr-enlarge-link">
                    <div class="fr-header__brand-top">
                        <div class="fr-header__logo">
                            <p class="fr-logo">République<br>Française</p>
                        </div>
                        <div class="fr-header__navbar">
                            <button type="button" class="fr-btn--search fr-btn" data-fr-opened="false" aria-controls="modal-search" title="Rechercher">
                                Rechercher
                            </button>
                            <button type="button" class="fr-btn--menu fr-btn" data-fr-opened="false" aria-controls="modal-menu" aria-haspopup="menu" title="Menu">
                                Menu
                            </button>
                        </div>
                    </div>
                    <div class="fr-header__service">
                        <a href="/" title="Accueil — Nom du service">
                            <p class="fr-header__service-title">Nom du service</p>
                        </a>
                        <p class="fr-header__service-tagline">Baseline du service</p>
                    </div>
                </div>
                <div class="fr-header__tools">
                    <div class="fr-header__tools-links">
                        <ul class="fr-btns-group">
                            <li>
                                <a class="fr-btn fr-icon-lock-line" href="/connexion">Se connecter</a>
                            </li>
                        </ul>
                    </div>
                    <div class="fr-header__search fr-modal" id="modal-search">
                        <div class="fr-container fr-container-lg--fluid">
                            <button type="button" class="fr-btn--close fr-btn" aria-controls="modal-search" title="Fermer">
                                Fermer
                            </button>
                            <form action="/recherche" method="get">
                                <div class="fr-search-bar" id="header-search" role="search">
                                    <label class="fr-label" for="search-header">Recherche</label>
                                    <input class="fr-input" placeholder="Rechercher" type="search" id="search-header" name="search">
                                    <button type="submit" class="fr-btn" title="Rechercher">Rechercher</button>
                                </div>
                            </form>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
    <div class="fr-header__menu fr-modal" id="modal-menu">
        <div class="fr-container">
            <button type="button" class="fr-btn--close fr-btn" aria-controls="modal-menu" title="Fermer">
                Fermer
            </button>
            <div class="fr-header__menu-links"></div>
            <nav class="fr-nav" role="navigation" aria-label="Menu principal">
                <ul class="fr-nav__list">
                    <li class="fr-nav__item">
                        <a class="fr-nav__link" href="/" aria-current="page">Accueil</a>
                    </li>
                    <li class="fr-nav__item">
                        <button type="button" class="fr-nav__btn" aria-expanded="false" aria-controls="mega-menu-1">
                            Rubrique
                        </button>
                        <div class="fr-collapse fr-menu" id="mega-menu-1">
                            <ul class="fr-menu__list">
                                <li><a class="fr-nav__link" href="/">Sous-rubrique 1</a></li>
                                <li><a class="fr-nav__link" href="/">Sous-rubrique 2</a></li>
                            </ul>
                        </div>
                    </li>
                </ul>
            </nav>
        </div>
    </div>
</header>
```

## Header avec opérateur
Ajouter dans `fr-header__brand-top` :
```html
<div class="fr-header__operator">
    <img src="logo-operateur.svg" alt="Nom de l'opérateur" class="fr-responsive-img" style="max-width: 9.0625rem;">
</div>
```

## Accès rapides (tools-links)
Les liens d'accès rapide dans le header (connexion, inscription, langue) sont placés dans `fr-header__tools-links` :
```html
<ul class="fr-btns-group">
    <li><a class="fr-btn fr-icon-account-line" href="/compte">Mon compte</a></li>
    <li><a class="fr-btn fr-icon-mail-line" href="/contact">Contact</a></li>
</ul>
```

---
