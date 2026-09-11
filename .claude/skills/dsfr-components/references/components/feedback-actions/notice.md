# Bandeau d'information (Notice)

Référence extraite de `../feedback-actions.md`.

---

## Structure DSFR 1.15.3

Depuis DSFR 1.15.3 (#1521), `fr-notice__body` contient un `div` qui porte le
titre dans un **niveau de titre** (`h2` par défaut, `h1` à `h6` ou `p` selon
la hiérarchie de la page) avec la classe `fr-notice__title`, puis la
description optionnelle dans un `p.fr-notice__desc`, puis le lien
`a.fr-notice__link`. Les anciens `<p><span class="fr-notice__title">…` ne sont
plus le markup de référence. Le générateur `generate_component.py notice`
accepte `heading` (`h2` par défaut).

Doctrine d'accessibilité 1.15.3 : le niveau de titre dépend du contexte et ne
sera pas toujours un `h2` ; le titre doit **expliciter la nature du message**
(information, avertissement, alerte), l'icône et la couleur ne suffisant pas.
Le générateur signale sur stderr un bandeau sans titre explicite.

## Notice d'information
```html
<div class="fr-notice fr-notice--info">
    <div class="fr-container">
        <div class="fr-notice__body">
            <div>
                <h2 class="fr-notice__title">Information importante à communiquer aux usagers</h2>
            </div>
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
`role` sur un bandeau, quelle que soit la variante. DSFR 1.15.3 (#1504) retire
l'option qui posait un `role="notice"` invalide et fixe la doctrine : un
attribut `role` (`status`, `alert`) n'est ajouté que si le bandeau est inséré
dynamiquement dans le DOM après le chargement de la page, comme pour l'alerte.

```html
<div class="fr-notice fr-notice--warning">
    <div class="fr-container">
        <div class="fr-notice__body">
            <div>
                <h2 class="fr-notice__title">Avertissement important</h2>
            </div>
        </div>
    </div>
</div>
```

## Notice fermable
```html
<div class="fr-notice fr-notice--info" id="notice-1">
    <div class="fr-container">
        <div class="fr-notice__body">
            <div>
                <h2 class="fr-notice__title">Information avec possibilité de fermeture</h2>
                <p class="fr-notice__desc">Texte de description complémentaire.</p>
                <a class="fr-notice__link" href="/plus-d-informations">En savoir plus</a>
            </div>
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
            <div>
                <h2 class="fr-notice__title">Notice sans pictogramme</h2>
            </div>
        </div>
    </div>
</div>
```

---
