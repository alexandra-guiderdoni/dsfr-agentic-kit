# Alertes

Référence extraite de `../feedback-actions.md`.

---

## Types d'alertes
- `fr-alert--info` : Information (bleu)
- `fr-alert--success` : Succès (vert)
- `fr-alert--warning` : Avertissement (orange)
- `fr-alert--error` : Erreur (rouge)

## Structure
```html
<div class="fr-alert fr-alert--[type]">
    <h3 class="fr-alert__title">Titre</h3>
    <p>Description de l'alerte</p>
</div>
```

## Alerte petite (sans description)
```html
<div class="fr-alert fr-alert--info fr-alert--sm">
    <p>Message court d'information</p>
</div>
```
**Note** : le titre `<h3 class="fr-alert__title">` reste possible en
`fr-alert--sm` ; il est simplement souvent omis pour un message court. Aucune
règle CSS ne le masque dans cette variante.

## Alerte fermable
```html
<div class="fr-alert fr-alert--info">
    <h3 class="fr-alert__title">Titre</h3>
    <p>Description de l'alerte</p>
    <button class="fr-btn--close fr-btn" type="button" title="Masquer le message">
        Masquer le message
    </button>
</div>
```
**Règles** :
- Le texte visible « Masquer le message » sert de nom accessible : ne pas y
  ajouter d'`aria-label` qui le recopierait
- Poser `role="alert"` uniquement sur une alerte insérée dynamiquement dans le
  DOM après le chargement de la page. Sur une alerte statique, la région live
  n'annonce rien et fausse le comportement attendu
- Brancher le comportement de fermeture hors HTML statique

---
