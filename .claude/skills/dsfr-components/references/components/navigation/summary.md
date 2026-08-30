# Sommaire (Summary)

Référence extraite de `../navigation.md`.

---

Le sommaire permet de naviguer rapidement dans une page longue via des ancres.

## Structure
```html
<nav class="fr-summary" role="navigation" aria-labelledby="fr-summary-title">
    <p class="fr-summary__title" id="fr-summary-title">Sommaire</p>
    <ol>
        <li>
            <a class="fr-summary__link" href="#section-1">Première section</a>
        </li>
        <li>
            <a class="fr-summary__link" href="#section-2">Deuxième section</a>
        </li>
        <li>
            <a class="fr-summary__link" href="#section-3">Troisième section</a>
        </li>
    </ol>
</nav>
```

**Règles** :
- Utiliser `<ol>` (liste ordonnée) car l'ordre des sections a du sens
- Chaque `href` doit correspondre à un `id` existant dans la page
- Placer le sommaire avant le contenu principal, après le titre h1
- `role="navigation"` + `aria-labelledby` obligatoires

---
