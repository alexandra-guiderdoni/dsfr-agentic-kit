# Interrupteur (Toggle)

Référence extraite de `../forms-services.md`.

---

## Toggle simple
```html
<div class="fr-toggle">
    <input type="checkbox" class="fr-toggle__input" id="toggle-1" aria-describedby="toggle-1-hint toggle-1-messages">
    <label class="fr-toggle__label" for="toggle-1" data-fr-checked-label="Activé" data-fr-unchecked-label="Désactivé">
        Libellé de l'interrupteur
    </label>
    <p class="fr-hint-text" id="toggle-1-hint">Description additionnelle de l'interrupteur</p>
    <div class="fr-messages-group" id="toggle-1-messages" aria-live="polite">
    </div>
</div>
```
**Obligatoire** : `fr-messages-group` avec `aria-live="polite"` et une cible
`aria-describedby` résolue. `data-fr-checked-label` et
`data-fr-unchecked-label` sont requis quand l'état textuel activé/désactivé est
affiché.
**Note** : Le JavaScript DSFR ajoute automatiquement `role="switch"` sur l'input au runtime. Ne pas l'ajouter manuellement dans le HTML statique.

## Toggle désactivé
```html
<div class="fr-toggle">
    <input type="checkbox" class="fr-toggle__input" id="toggle-disabled" disabled aria-describedby="toggle-disabled-messages">
    <label class="fr-toggle__label" for="toggle-disabled" data-fr-checked-label="Activé" data-fr-unchecked-label="Désactivé">
        Interrupteur désactivé
    </label>
    <div class="fr-messages-group" id="toggle-disabled-messages" aria-live="polite">
    </div>
</div>
```

## Toggle avec label à gauche
```html
<div class="fr-toggle fr-toggle--label-left">
    <input type="checkbox" class="fr-toggle__input" id="toggle-2" aria-describedby="toggle-2-messages">
    <label class="fr-toggle__label" for="toggle-2" data-fr-checked-label="Activé" data-fr-unchecked-label="Désactivé">
        Label à gauche
    </label>
    <div class="fr-messages-group" id="toggle-2-messages" aria-live="polite">
    </div>
</div>
```

## Toggle bordé
```html
<div class="fr-toggle fr-toggle--border-bottom">
    <input type="checkbox" class="fr-toggle__input" id="toggle-3" aria-describedby="toggle-3-messages">
    <label class="fr-toggle__label" for="toggle-3" data-fr-checked-label="Activé" data-fr-unchecked-label="Désactivé">
        Avec séparateur
    </label>
    <div class="fr-messages-group" id="toggle-3-messages" aria-live="polite">
    </div>
</div>
```

## Groupe de toggles
```html
<fieldset class="fr-fieldset" id="toggle-group" aria-labelledby="toggle-group-legend toggle-group-messages">
    <legend class="fr-fieldset__legend" id="toggle-group-legend">
        Paramètres de notification
    </legend>
    <div class="fr-fieldset__element">
        <ul class="fr-toggle__list">
            <li>
                <div class="fr-toggle">
                    <input type="checkbox" class="fr-toggle__input" id="notif-email" aria-describedby="notif-email-messages">
                    <label class="fr-toggle__label" for="notif-email" data-fr-checked-label="Activé" data-fr-unchecked-label="Désactivé">
                        Notifications par courriel
                    </label>
                    <div class="fr-messages-group" id="notif-email-messages" aria-live="polite">
                    </div>
                </div>
            </li>
            <li>
                <div class="fr-toggle">
                    <input type="checkbox" class="fr-toggle__input" id="notif-sms" aria-describedby="notif-sms-messages">
                    <label class="fr-toggle__label" for="notif-sms" data-fr-checked-label="Activé" data-fr-unchecked-label="Désactivé">
                        Notifications par SMS
                    </label>
                    <div class="fr-messages-group" id="notif-sms-messages" aria-live="polite">
                    </div>
                </div>
            </li>
        </ul>
    </div>
    <div class="fr-messages-group" id="toggle-group-messages" aria-live="polite">
    </div>
</fieldset>
```

---
