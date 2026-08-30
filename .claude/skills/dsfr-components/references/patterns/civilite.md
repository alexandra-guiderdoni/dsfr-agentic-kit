# Civilité

Référence extraite de `../patterns.md`.

---

## Pattern recommandé

Le bloc fonctionnel officiel « civilité » du DSFR 1.15.2
(`example/layout/pattern/civility`) demande le sexe, avec deux boutons radio
Féminin / Masculin. C'est la structure produite par
`scripts/generate_field.py civilite` : fieldset relié par `aria-labelledby` à
sa légende et à son groupe de messages.

```html
<fieldset class="fr-fieldset" id="civilite-fieldset" aria-labelledby="civilite-legend civilite-messages">
    <legend class="fr-fieldset__legend--regular fr-fieldset__legend" id="civilite-legend">Sexe</legend>
    <div class="fr-fieldset__element">
        <div class="fr-radio-group">
            <input type="radio" id="civilite-1" name="civilite" value="feminin">
            <label class="fr-label" for="civilite-1">Féminin</label>
        </div>
    </div>
    <div class="fr-fieldset__element">
        <div class="fr-radio-group">
            <input type="radio" id="civilite-2" name="civilite" value="masculin">
            <label class="fr-label" for="civilite-2">Masculin</label>
        </div>
    </div>
    <div class="fr-messages-group" aria-live="polite" id="civilite-messages"></div>
</fieldset>
```

## Règles
- Boutons radio, PAS un select (2 options seulement).
- Ne demander le sexe (ou une civilité) que si le traitement l'exige ; sinon
  ne pas le demander.
- Une civilité Madame / Monsieur reste possible via
  `--config '{"legend":"Civilité","options":[{"label":"Madame","value":"Mme"},{"label":"Monsieur","value":"M."}]}'` ;
  elle diverge alors du bloc officiel, à documenter dans le livrable.
- `autocomplete="honorific-prefix"` peut être ajouté sur une civilité si
  pertinent.
- Si le choix est obligatoire, différer `required` jusqu'au premier `submit`.

---
