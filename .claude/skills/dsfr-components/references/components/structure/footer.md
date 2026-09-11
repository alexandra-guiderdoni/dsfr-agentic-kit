# Pied de page (Footer)

Référence extraite de `../structure.md`.

---

## Footer standard
```html
<footer class="fr-footer" role="contentinfo" id="footer">
    <div class="fr-container">
        <div class="fr-footer__body">
            <div class="fr-footer__brand fr-enlarge-link">
                <p class="fr-logo">
                    République<br>Française
                </p>
                <a class="fr-footer__brand-link" href="/" title="Retour à l'accueil du site — Nom du service — République Française">
                    <p>Nom du service</p>
                </a>
            </div>
            <div class="fr-footer__content">
                <p class="fr-footer__content-desc">Description du service ou de l'organisme.</p>
                <ul class="fr-footer__content-list">
                    <li class="fr-footer__content-item">
                        <a class="fr-footer__content-link" title="info.gouv.fr - nouvelle fenêtre" target="_blank" rel="noopener external" href="https://info.gouv.fr">info.gouv.fr</a>
                    </li>
                    <li class="fr-footer__content-item">
                        <a class="fr-footer__content-link" title="service-public.gouv.fr - nouvelle fenêtre" target="_blank" rel="noopener external" href="https://service-public.gouv.fr">service-public.gouv.fr</a>
                    </li>
                    <li class="fr-footer__content-item">
                        <a class="fr-footer__content-link" title="legifrance.gouv.fr - nouvelle fenêtre" target="_blank" rel="noopener external" href="https://legifrance.gouv.fr">legifrance.gouv.fr</a>
                    </li>
                    <li class="fr-footer__content-item">
                        <a class="fr-footer__content-link" title="data.gouv.fr - nouvelle fenêtre" target="_blank" rel="noopener external" href="https://data.gouv.fr">data.gouv.fr</a>
                    </li>
                </ul>
            </div>
        </div>
        <div class="fr-footer__bottom">
            <ul class="fr-footer__bottom-list">
                <li class="fr-footer__bottom-item">
                    <a class="fr-footer__bottom-link" href="/plan-du-site">Plan du site</a>
                </li>
                <li class="fr-footer__bottom-item">
                    <a class="fr-footer__bottom-link" href="/accessibilite">Accessibilité : statut à renseigner</a>
                </li>
                <li class="fr-footer__bottom-item">
                    <a class="fr-footer__bottom-link" href="/mentions-legales">Mentions légales</a>
                </li>
                <li class="fr-footer__bottom-item">
                    <a class="fr-footer__bottom-link" href="/donnees-personnelles">Données personnelles</a>
                </li>
                <li class="fr-footer__bottom-item">
                    <a class="fr-footer__bottom-link" href="/gestion-cookies">Gestion des cookies</a>
                </li>
            </ul>
            <div class="fr-footer__bottom-copy">
                <p>Sauf mention contraire, tous les contenus de ce site sont sous
                    <a href="https://github.com/etalab/licence-ouverte/blob/master/LO.md" target="_blank" rel="noopener">licence etalab-2.0</a>
                </p>
            </div>
        </div>
    </div>
</footer>
```

## Footer avec menu supérieur (colonnes de liens)
Le bloc officiel est `fr-footer__top`, placé dans `fr-footer` avant le
`fr-container` du corps. Depuis DSFR 1.15.0 (#1393), le titre de chaque
catégorie est un `<h2 class="fr-footer__top-cat">` par défaut (un autre niveau
reste possible selon la structure de la page). Les classes
`fr-footer__content-title` et assimilées n'existent pas dans le paquet : ne pas
les inventer.
```html
<div class="fr-footer__top">
    <div class="fr-container">
        <div class="fr-grid-row fr-grid-row--gutters">
            <div class="fr-col-12 fr-col-sm-3 fr-col-md-2">
                <h2 class="fr-footer__top-cat">Nom de la catégorie</h2>
                <ul class="fr-footer__top-list">
                    <li><a class="fr-footer__top-link" href="/rubrique-1">Lien de navigation</a></li>
                    <li><a class="fr-footer__top-link" href="/rubrique-2">Lien de navigation</a></li>
                </ul>
            </div>
            <div class="fr-col-12 fr-col-sm-3 fr-col-md-2">
                <h2 class="fr-footer__top-cat">Autre catégorie</h2>
                <ul class="fr-footer__top-list">
                    <li><a class="fr-footer__top-link" href="/rubrique-3">Lien de navigation</a></li>
                </ul>
            </div>
        </div>
    </div>
</div>
```
Source : `example/component/footer/index.html` du paquet 1.15.3. Le générateur
`generate_component.py footer` ne produit pas ce bloc : l'ajouter à la main
selon ce markup.

## Footer avec partenaires
```html
<div class="fr-footer__partners">
    <h2 class="fr-footer__partners-title">Nos partenaires</h2>
    <div class="fr-footer__partners-logos">
        <div class="fr-footer__partners-main">
            <a class="fr-footer__partners-link" href="/">
                <img class="fr-footer__logo fr-responsive-img" src="partenaire-principal.svg" alt="Partenaire principal" style="max-width: 9.0625rem;">
            </a>
        </div>
        <div class="fr-footer__partners-sub">
            <ul>
                <li>
                    <a class="fr-footer__partners-link" href="/">
                        <img class="fr-footer__logo fr-responsive-img" src="partenaire-2.svg" alt="Partenaire 2" style="max-width: 9.0625rem;">
                    </a>
                </li>
            </ul>
        </div>
    </div>
</div>
```

## Liens obligatoires du footer
Le footer DSFR **doit** contenir au minimum ces liens dans `fr-footer__bottom` :
1. Plan du site
2. Accessibilité (avec niveau audité si disponible ; ne pas écrire `conforme`
   sans preuve dédiée)
3. Mentions légales
4. Données personnelles
5. Gestion des cookies

---
