# Lien (Link)

Référence extraite de `../navigation.md`.

---

## Lien simple
```html
<a class="fr-link" href="/">Libellé du lien</a>
```

## Tailles
- `fr-link--sm` : Petit
- Par défaut : Moyen
- `fr-link--lg` : Grand

## Lien avec icône
```html
<a class="fr-link fr-icon-arrow-right-line fr-link--icon-right" href="/">Lien avec icône</a>
<a class="fr-link fr-icon-arrow-left-line fr-link--icon-left" href="/">Lien avec icône à gauche</a>
```

## Lien externe
```html
<a class="fr-link" href="https://example.com" target="_blank" rel="noopener">
    Lien externe <span class="fr-sr-only">ouvre une nouvelle fenêtre</span>
</a>
```
**Obligatoire** : `rel="noopener"` et indication visuelle ou textuelle (via `fr-sr-only`) que le lien ouvre une nouvelle fenêtre.

## Lien de téléchargement
```html
<a class="fr-link fr-icon-download-line fr-link--icon-left" download href="fichier.pdf">
    Télécharger (PDF, 1,2 Mo)
</a>
```

## Lien au fil du texte
Au sein d'un paragraphe, ne pas utiliser le composant : un lien standard sans
la classe `fr-link` reprend la typographie du texte et reste souligné (gabarit
1.15.0, paramètre `inText`, #1455).
```html
<p>Consultez <a href="/demarches">la liste des démarches</a> avant de commencer.</p>
```

---
