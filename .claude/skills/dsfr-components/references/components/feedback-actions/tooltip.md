# Info-bulle (Tooltip)

Référence extraite de `../feedback-actions.md`.

---

Affiche une information complémentaire au survol ou au focus.

## Structure
```html
<button class="fr-btn--tooltip fr-btn"
        id="tooltip-btn-1"
        type="button"
        aria-describedby="tooltip-1">
    Information complémentaire
</button>
<span class="fr-tooltip fr-placement" id="tooltip-1" role="tooltip">
    Contenu de l'info-bulle avec des détails complémentaires.
</span>
```
**Note** : `fr-btn--tooltip` est la classe qui déclenche l'ouverture de
l'info-bulle au clic. Sans elle, le déclencheur reste un bouton ordinaire et
l'info-bulle ne s'ouvre pas. C'est aussi la classe posée par
`generate_component.py tooltip`.

## Positionnement

| Classe | Position |
|--------|----------|
| `fr-placement` | Automatique (par défaut) |
| `fr-placement--top` | Au-dessus |
| `fr-placement--bottom` | En dessous |

Seules les positions `top` et `bottom` sont fournies par le paquet
`@gouvfr/dsfr@1.15.2` (`left`/`right` n'existent pas ; vérifié dans
`dist/dsfr.min.css`).

**Règles** :
- `aria-describedby` lie le déclencheur au tooltip
- `role="tooltip"` sur le contenu ; ne pas poser `aria-hidden` en dur dans le HTML statique
- Le tooltip doit être accessible au clavier (focus)
- Ne pas mettre de contenu interactif (liens, boutons) dans un tooltip
- Utiliser pour des informations complémentaires, pas essentielles

**Comportement depuis 1.15.0** (PR #1447) : une infobulle ne reste plus ouverte
après un clic, seulement au survol, et un second clic la referme. La fermeture
au clavier et sous iOS a été corrigée. Le markup n'est pas concerné : ces
changements sont dans le script du composant. Un test qui suppose l'ancien
comportement au clic doit être revu.
