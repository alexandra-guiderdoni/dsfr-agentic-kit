# Retour en haut de page (Back to top)

Nom générable : `back_to_top` (tiret bas, pas de tiret haut).

Référence extraite de `../navigation.md`.

---

Lien d'ancre pour revenir en haut de la page, affiché en bas de contenu long.

## Structure
```html
<a class="fr-link fr-icon-arrow-up-fill fr-link--icon-left" href="#top">
    Haut de page
</a>
```

**Règles** :
- L'attribut `href="#top"` pointe vers l'`id="top"` de la balise `<body>` ou du `<header>`
- Placer en fin de contenu principal, avant le footer
- Utiliser `fr-link--icon-left` avec l'icône `fr-icon-arrow-up-fill`
