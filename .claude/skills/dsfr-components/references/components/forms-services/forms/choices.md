# Formulaires — choix, sélecteurs et groupes

Référence extraite de `../forms.md`.

---

## Cases à cocher
```html
<div class="fr-checkbox-group">
    <input type="checkbox" id="checkbox-1" name="checkbox-1">
    <label class="fr-label" for="checkbox-1">Option 1</label>
</div>
```

### État indéterminé

Depuis DSFR 1.15.0, l'état indéterminé d'une case à cocher est stylé. Il n'a
aucune représentation en HTML : `indeterminate` est une propriété du DOM, pas
un attribut. Le markup ci-dessus reste inchangé et l'état se pose en
JavaScript.

```js
document.getElementById('checkbox-1').indeterminate = true;
```

Le style officiel cible le sélecteur CSS `:indeterminate` sur l'input. L'exemple
du paquet suffixe l'identifiant par `-indeterminate` pour que son script de
démonstration retrouve les cases concernées ; c'est une commodité d'exemple,
pas une exigence du composant.

## Boutons radio
```html
<div class="fr-radio-group">
    <input type="radio" id="radio-1" name="radio-group" value="1">
    <label class="fr-label" for="radio-1">Option 1</label>
</div>
```

## Boutons radio enrichis (avec image)
```html
<div class="fr-radio-group fr-radio-rich">
    <input type="radio" id="radio-rich-1" name="radio-rich" value="1">
    <label class="fr-label" for="radio-rich-1">Option enrichie</label>
    <div class="fr-radio-rich__img">
        <img src="image.svg" alt="">
    </div>
</div>
```

## Contrôle segmenté (segmented)
```html
<fieldset class="fr-segmented">
    <legend class="fr-segmented__legend">
        Légende
        <span class="fr-hint-text">Texte d'aide</span>
    </legend>
    <div class="fr-segmented__elements">
        <div class="fr-segmented__element">
            <input value="1" type="radio" id="segmented-1" name="segmented">
            <label class="fr-label" for="segmented-1">Libellé 1</label>
        </div>
        <div class="fr-segmented__element">
            <input value="2" type="radio" id="segmented-2" name="segmented">
            <label class="fr-label" for="segmented-2">Libellé 2</label>
        </div>
    </div>
</fieldset>
```

## Sélecteur
```html
<div class="fr-select-group">
    <label class="fr-label" for="select">Label du sélecteur</label>
    <select class="fr-select" id="select" name="select">
        <option value="" selected disabled>Sélectionner une option</option>
        <option value="1">Option 1</option>
        <option value="2">Option 2</option>
    </select>
</div>
```

L'option vide ne porte plus `hidden` depuis DSFR 1.15.0 (#1424, DSFR-63) :
`selected disabled` suffit et laisse l'invite lisible par les technologies
d'assistance.

## Fieldset (groupement de champs)
```html
<fieldset class="fr-fieldset" aria-labelledby="fieldset-legend">
    <legend class="fr-fieldset__legend" id="fieldset-legend">
        Informations personnelles
    </legend>
    <div class="fr-fieldset__element">
        <!-- Champs ici -->
    </div>
</fieldset>
```

---
