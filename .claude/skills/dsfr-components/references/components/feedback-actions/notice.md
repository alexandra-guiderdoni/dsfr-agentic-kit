# Bandeau d'information (Notice)

Référence extraite de `../feedback-actions.md`.

---

## Notice d'information
```html
<div class="fr-notice fr-notice--info">
    <div class="fr-container">
        <div class="fr-notice__body">
            <p class="fr-notice__title">Information importante à communiquer aux usagers</p>
        </div>
    </div>
</div>
```

## Types de notice

Bandeaux génériques :
- `fr-notice` : Notice sans type (neutre)
- `fr-notice--info` : Information (bleu)
- `fr-notice--warning` : Avertissement (orange)
- `fr-notice--alert` : Alerte urgente (rouge)

Bandeaux de vigilance météo :
- `fr-notice--weather-orange` : Vigilance orange
- `fr-notice--weather-red` : Vigilance rouge
- `fr-notice--weather-purple` : Vigilance violette

Bandeaux d'alerte gouvernementale :
- `fr-notice--attack` : Attaque en cours
- `fr-notice--cyberattack` : Cyberattaque
- `fr-notice--kidnapping` : Alerte enlèvement
- `fr-notice--witness` : Appel à témoins

Modificateur d'affichage :
- `fr-notice--no-icon` : Notice sans pictogramme

**Note** : ni le paquet officiel ni `generate_component.py notice` ne posent de
`role` sur un bandeau, quelle que soit la variante. N'ajouter une région live
que si la notice est insérée dynamiquement dans le DOM après le chargement de
la page.

```html
<div class="fr-notice fr-notice--warning">
    <div class="fr-container">
        <div class="fr-notice__body">
            <p class="fr-notice__title">Avertissement important</p>
        </div>
    </div>
</div>
```

## Notice fermable
```html
<div class="fr-notice fr-notice--info" id="notice-1">
    <div class="fr-container">
        <div class="fr-notice__body">
            <p>
                <span class="fr-notice__title">Information avec possibilité de fermeture</span>
                <span class="fr-notice__desc">Texte de description complémentaire.</span>
                <a class="fr-notice__link" href="/plus-d-informations">En savoir plus</a>
            </p>
            <button class="fr-btn--close fr-btn" title="Masquer le message" type="button">
                Masquer le message
            </button>
        </div>
    </div>
</div>
```

## Notice sans icône
```html
<div class="fr-notice fr-notice--info fr-notice--no-icon">
    <div class="fr-container">
        <div class="fr-notice__body">
            <p class="fr-notice__title">Notice sans pictogramme</p>
        </div>
    </div>
</div>
```

---
