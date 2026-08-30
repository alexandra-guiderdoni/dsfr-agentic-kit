# Formulaires — champs et contraintes

Référence extraite de `../forms.md`.

---

## Contraintes requises au repos

Pour un fragment de formulaire généré, ne pas poser `required`,
`aria-required`, `pattern` ou `aria-invalid` dans le HTML statique. Si un champ
doit être obligatoire ou contraint, appliquer le pattern
`references/patterns/validation-differee.md` : poser la
contrainte au premier `submit`, puis la retirer au `reset` si le formulaire
revient à l'état repos. Sans JavaScript, la validation serveur reste la source
de vérité.

Le même esprit vaut pour les contraintes natives que le contrôle automatique
ne teste pas : `maxlength` tronque la saisie sans message, `min`, `max` et
`step` déclenchent la validation native du navigateur au `submit`, `accept`
filtre le sélecteur de fichiers. Aucune n'apparaît dans les exemples du paquet
officiel. Les poser au premier `submit`, comme les autres contraintes, et
décrire la règle en clair dans le `fr-hint-text`.

## Champs de texte
```html
<div class="fr-input-group">
    <label class="fr-label" for="input-id">
        Label du champ
        <span class="fr-hint-text">Texte d'aide</span>
    </label>
    <input class="fr-input" type="text" id="input-id" name="input-name">
</div>
```

## Champs avec erreur
```html
<div class="fr-input-group fr-input-group--error">
    <label class="fr-label" for="input-error">Label</label>
    <input class="fr-input fr-input--error" type="text" id="input-error" aria-describedby="input-error-message">
    <p id="input-error-message" class="fr-error-text">Message d'erreur</p>
</div>
```

## Champs avec succès
```html
<div class="fr-input-group fr-input-group--valid">
    <label class="fr-label" for="input-valid">Label</label>
    <input class="fr-input fr-input--valid" type="text" id="input-valid" aria-describedby="input-valid-msg">
    <p id="input-valid-msg" class="fr-valid-text">Champ valide</p>
</div>
```

## Champ désactivé
```html
<div class="fr-input-group fr-input-group--disabled">
    <label class="fr-label" for="input-disabled">Label</label>
    <input class="fr-input" type="text" id="input-disabled" disabled>
</div>
```

## Zone de texte (textarea)
```html
<div class="fr-input-group">
    <label class="fr-label" for="textarea-id">
        Label
        <span class="fr-hint-text">Description</span>
    </label>
    <textarea class="fr-input" id="textarea-id" name="textarea-name" aria-describedby="textarea-id-messages"></textarea>
    <div class="fr-messages-group" id="textarea-id-messages" aria-live="polite">
        <p class="fr-message fr-message--info">0/500 caractères</p>
    </div>
</div>
```
**Note** : le `fr-messages-group` porte un `id` cité par l'`aria-describedby` du
champ : sans ce lien, ni la limite ni le décompte ne sont annoncés avec le
champ. `aria-live="polite"` fait annoncer les mises à jour du compteur.

## Champ mot de passe
```html
<div class="fr-password">
    <label class="fr-label" for="password">Mot de passe</label>
    <div class="fr-input-wrap">
        <input class="fr-password__input fr-input" type="password" id="password" name="password"
               aria-describedby="password-messages" autocomplete="current-password">
    </div>
    <div class="fr-messages-group" id="password-messages" aria-live="polite">
        <p class="fr-message fr-message--info">Votre mot de passe doit contenir au moins 8 caractères</p>
    </div>
    <div class="fr-password__checkbox fr-checkbox-group fr-checkbox-group--sm">
        <input type="checkbox" id="password-show" aria-label="Afficher le mot de passe">
        <label class="fr-label" for="password-show">Afficher</label>
    </div>
</div>
```
**Obligatoire** : `autocomplete="current-password"` ou `autocomplete="new-password"`.

## Champ numérique
```html
<div class="fr-input-group">
    <label class="fr-label" for="number-id">Quantité</label>
    <input class="fr-input" type="number" inputmode="numeric" id="number-id" name="number">
</div>
```

## Sélecteur de date
```html
<div class="fr-input-group">
    <label class="fr-label" for="date-id">
        Date de naissance
        <span class="fr-hint-text">Format attendu : JJ/MM/AAAA</span>
    </label>
    <input class="fr-input" type="date" id="date-id" name="date">
</div>
```

## Champ avec autocomplétion
```html
<div class="fr-input-group">
    <label class="fr-label" for="address">Adresse</label>
    <input class="fr-input" type="text" id="address" name="address"
           autocomplete="street-address" list="address-list">
    <datalist id="address-list">
        <option value="10 rue de la Paix, 75002 Paris">
        <option value="15 avenue des Champs-Élysées, 75008 Paris">
    </datalist>
</div>
```
**Note** : Les valeurs `autocomplete` (WCAG 1.3.5) : `name`, `email`, `tel`, `street-address`, `postal-code`, `country-name`, etc.

## Curseur (range)
```html
<div class="fr-range-group">
    <label class="fr-label" for="range-id">
        Volume
        <span class="fr-hint-text">Ajustez le volume</span>
    </label>
    <div class="fr-range">
        <span class="fr-range__output" aria-hidden="true">50</span>
        <input type="range" id="range-id" name="range" min="0" max="100" value="50" aria-describedby="range-id-messages">
        <span class="fr-range__min" aria-hidden="true">0</span>
        <span class="fr-range__max" aria-hidden="true">100</span>
    </div>
    <div class="fr-messages-group" id="range-id-messages" aria-live="polite"></div>
</div>
```
Gabarit 1.15.0 (#1407) : le label est lié par `for`/`id` (plus de
`aria-labelledby` sur le curseur simple), la sortie et les bornes sont masquées
aux technologies d'assistance. La classe `fr-range` va sur le conteneur, pas
sur l'input. Variantes : `fr-range--sm`, `fr-range--step` (avec `step`),
`fr-range--double` (deux inputs) ; états `fr-range-group--disabled` et
`fr-range-group--error`. Les attributs `data-fr-js-*` sont posés par le script
au chargement et ne se copient pas dans le HTML source.

## Téléversement de fichier (upload)
```html
<div class="fr-upload-group">
    <label class="fr-label" for="upload-id">
        Ajouter un fichier
        <span class="fr-hint-text">Taille maximale : 500 ko. Formats supportés : jpg, png, pdf</span>
    </label>
    <input class="fr-upload" type="file" id="upload-id" name="upload">
</div>
```
