# Lien d'évitement (Skiplink)

Référence extraite de `../navigation.md`.

---

## Structure
```html
<div class="fr-skiplinks">
    <nav class="fr-container" role="navigation" aria-label="Accès rapide">
        <ul class="fr-skiplinks__list">
            <li>
                <a class="fr-link" href="#contenu">Contenu</a>
            </li>
            <li>
                <a class="fr-link" href="#navigation">Menu</a>
            </li>
            <li>
                <a class="fr-link" href="#footer">Pied de page</a>
            </li>
        </ul>
    </nav>
</div>
```
**Obligatoire** : Doit être le PREMIER élément enfant de `<body>`, avant le `<header>`.
**Note** : visible uniquement au focus clavier (touche Tab). Les ancres
`#contenu`, `#navigation` et `#footer` sont celles que `generate_page.py`
émet réellement (`<main id="contenu">`, `<nav class="fr-nav" id="navigation">`,
`<footer id="footer">`). Le paquet d'exemple officiel utilise une autre
convention (`#content`, `#header-navigation`, `#header-search`) : dans tous les
cas, chaque ancre doit correspondre à un `id` réellement présent dans la page.

---
