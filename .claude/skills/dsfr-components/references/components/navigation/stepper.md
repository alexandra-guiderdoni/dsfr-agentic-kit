# Indicateur d'étapes (Stepper)

Référence extraite de `../navigation.md`.

---

## Structure
```html
<div class="fr-stepper">
    <h2 class="fr-stepper__title">
        Titre de l'étape en cours
        <span class="fr-stepper__state">Étape 2 sur 4</span>
    </h2>
    <div class="fr-stepper__steps" data-fr-current-step="2" data-fr-steps="4"></div>
    <p class="fr-stepper__details">
        <span class="fr-text--bold">Étape suivante :</span> Titre de l'étape 3
    </p>
</div>
```
**Obligatoire** : `data-fr-current-step` et `data-fr-steps` pour le rendu visuel de la barre de progression.
**Note** : le `fr-stepper__state` est placé APRÈS le titre dans le `<h2>`, comme
dans le paquet officiel. La barre visuelle (`fr-stepper__steps`) est décorative.
Le bloc `fr-stepper__details` est optionnel (peut être omis à la dernière
étape).

---
