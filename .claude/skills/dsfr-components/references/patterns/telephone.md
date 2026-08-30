# Téléphone (+33)

Référence extraite de `../patterns.md`.

---

## Pattern recommandé
```html
<div class="fr-input-group">
    <label class="fr-label" for="telephone">
        Numéro de téléphone
        <span class="fr-hint-text">Format attendu : (+33) 5 36 49 68 27</span>
    </label>
    <input class="fr-input" type="tel" id="telephone" name="telephone"
           autocomplete="tel">
</div>
```

## Avec indicatif pays (international)
```html
<fieldset class="fr-fieldset" aria-labelledby="tel-legend" role="group">
    <legend class="fr-fieldset__legend" id="tel-legend">Numéro de téléphone</legend>
    <div class="fr-fieldset__element fr-fieldset__element--inline">
        <div class="fr-select-group">
            <label class="fr-label" for="tel-indicatif">Indicatif</label>
            <select class="fr-select" id="tel-indicatif" name="tel-indicatif" autocomplete="tel-country-code">
                <option value="+33" selected>+33 (France)</option>
                <option value="+32">+32 (Belgique)</option>
                <option value="+41">+41 (Suisse)</option>
                <option value="+352">+352 (Luxembourg)</option>
            </select>
        </div>
    </div>
    <div class="fr-fieldset__element fr-fieldset__element--inline">
        <div class="fr-input-group">
                <label class="fr-label" for="tel-numero">Numéro</label>
            <input class="fr-input" type="tel" id="tel-numero" name="tel-numero"
                   autocomplete="tel-national">
        </div>
    </div>
</fieldset>
```

## Règles
- `type="tel"` obligatoire (affiche le clavier numérique sur mobile)
- `autocomplete="tel"` obligatoire (WCAG 1.3.5)
- Le hint doit montrer le format attendu avec un exemple ; le bloc
  fonctionnel officiel utilise `(+33) 5 36 49 68 27` depuis DSFR 1.15.0
  (#1364, `layout/pattern/tel/i18n/fr.yml`)
- Pattern regex tolérant : accepter avec ou sans espaces, avec ou sans +33,
  mais le poser seulement après le premier `submit`
- Ne PAS imposer un format strict côté client (validation serveur)

---
