# Fil d'Ariane avancé

<a id="fil-dariane-avance"></a>

Référence extraite de `../navigation.md`.

---

Complément à la section Navigation > Fil d'Ariane pour les cas avancés.

## Fil d'Ariane tronqué (pages profondes)
```html
<nav role="navigation" class="fr-breadcrumb" aria-label="vous êtes ici :">
    <button type="button" class="fr-breadcrumb__button" aria-expanded="false" aria-controls="breadcrumb-1">
        Voir le fil d'Ariane
    </button>
    <div class="fr-collapse" id="breadcrumb-1">
        <ol class="fr-breadcrumb__list">
            <li>
                <a class="fr-breadcrumb__link" href="/">Accueil</a>
            </li>
            <li>
                <a class="fr-breadcrumb__link" href="/rubrique">Rubrique</a>
            </li>
            <li>
                <a class="fr-breadcrumb__link" href="/rubrique/sous-rubrique">Sous-rubrique</a>
            </li>
            <li>
                <a class="fr-breadcrumb__link" aria-current="page">Page courante</a>
            </li>
        </ol>
    </div>
</nav>
```

**Règles** :
- Le bouton `fr-breadcrumb__button` permet de déployer le fil d'Ariane sur mobile (collapse)
- `aria-current="page"` sur le dernier élément (page courante)
- Le dernier élément ne doit PAS être un lien actif (pas de `href`)
- Sur mobile, le fil entier est replié dans le `fr-collapse` : rien n'est
  visible avant activation du bouton. À partir du point de rupture md, le
  bouton disparaît et le fil s'affiche en entier

---
