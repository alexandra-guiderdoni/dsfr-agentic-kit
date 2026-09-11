# Sélecteur de langue (Translate)

<a id="selecteur-de-langue-translate"></a>

Référence extraite de `../navigation.md`.

---

Permet de changer la langue du site. Placé dans les accès rapides du header
(`fr-header__tools-links`).

## Structure

Depuis DSFR 1.15.0 (#1431), le conteneur est un `<div>` : plus de balise `nav`
ni de `role="navigation"`. La classe `fr-translate__language` est réservée aux
liens de langue ; le bouton porte le code de la langue courante et son nom
complet masqué en desktop.

```html
<div class="fr-translate fr-nav">
    <div class="fr-nav__item">
        <button type="button" class="fr-translate__btn fr-btn fr-btn--tertiary"
                aria-controls="translate-menu"
                aria-expanded="false"
                title="Sélectionner une langue">
            FR<span class="fr-hidden-lg">&nbsp;- Français</span>
        </button>
        <div class="fr-collapse fr-translate__menu fr-menu" id="translate-menu">
            <ul class="fr-menu__list">
                <li>
                    <a class="fr-translate__language fr-nav__link" hreflang="fr" lang="fr" href="/fr/" aria-current="true">FR - Français</a>
                </li>
                <li>
                    <a class="fr-translate__language fr-nav__link" hreflang="en" lang="en" href="/en/">EN - English</a>
                </li>
                <li>
                    <a class="fr-translate__language fr-nav__link" hreflang="de" lang="de" href="/de/">DE - Deutsch</a>
                </li>
            </ul>
        </div>
    </div>
</div>
```

Source : `example/component/translate/index.html` du paquet 1.15.3 ;
générateur `generate_component.py translate` (options `current`, `languages`
avec `code`, `label`, `href`, et `id` du menu).

**Règles** :
- Attributs `hreflang` et `lang` obligatoires sur chaque lien de langue
- `aria-current="true"` sur la langue active
- `title` sur le bouton et `aria-controls` vers le menu `fr-collapse`
- `fr-hidden-lg` applique `display:none` à partir de 62em : le complément est
  retiré de l'arbre d'accessibilité pour tout le monde, et le nom accessible du
  bouton se réduit alors à « FR ». Pour garder un nom complet, ajouter un
  `fr-sr-only` ou un `aria-label` sur le bouton

---
