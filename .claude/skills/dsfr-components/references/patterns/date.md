# Date (jj/mm/aaaa)

Référence extraite de `../patterns.md`.

---

## Pattern recommandé (3 champs séparés)
```html
<fieldset class="fr-fieldset" aria-labelledby="date-naissance-legend" role="group">
    <legend class="fr-fieldset__legend" id="date-naissance-legend">
        Date de naissance
        <span class="fr-hint-text">Exemple : 14 07 1789</span>
    </legend>
    <div class="fr-fieldset__element fr-fieldset__element--inline">
        <div class="fr-input-group">
            <label class="fr-label" for="jour">Jour</label>
            <input class="fr-input" type="text" id="jour" name="jour"
                   inputmode="numeric" maxlength="2"
                   autocomplete="bday-day">
        </div>
    </div>
    <div class="fr-fieldset__element fr-fieldset__element--inline">
        <div class="fr-input-group">
            <label class="fr-label" for="mois">Mois</label>
            <input class="fr-input" type="text" id="mois" name="mois"
                   inputmode="numeric" maxlength="2"
                   autocomplete="bday-month">
        </div>
    </div>
    <div class="fr-fieldset__element fr-fieldset__element--inline">
        <div class="fr-input-group">
                <label class="fr-label" for="annee">Année</label>
            <input class="fr-input" type="text" id="annee" name="annee"
                   inputmode="numeric" maxlength="4"
                   autocomplete="bday-year">
        </div>
    </div>
</fieldset>
```

## Alternative : champ date unique
```html
<div class="fr-input-group">
    <label class="fr-label" for="date-naissance">
        Date de naissance
        <span class="fr-hint-text">Format attendu : JJ/MM/AAAA</span>
    </label>
    <input class="fr-input" type="date" id="date-naissance" name="date-naissance"
           autocomplete="bday">
</div>
```

## Règles
- Préférer les 3 champs séparés pour les dates de naissance (meilleure accessibilité, pas de date picker)
- `inputmode="numeric"` au lieu de `type="number"` (évite les spinners inutiles)
- Largeur des champs : le DSFR 1.15.2 ne fournit pas d'utilitaire de largeur
  d'input (`fr-input--w*` n'existe pas) ; dimensionner via la grille
  (`fr-col-*`) ou le conteneur `fr-fieldset__element`, ou du CSS projet vérifié.
- `role="group"` sur le fieldset pour signaler le regroupement
- Autocomplete : `bday-day`, `bday-month`, `bday-year` (WCAG 1.3.5)
- Pour les autres dates (pas anniversaire) : utiliser `type="date"` avec hint de format
- Si la date est obligatoire ou contrainte par motif, différer `required` et
  `pattern` jusqu'au premier `submit`.

Arbitrage `inputmode` et `maxlength` : le bloc `generate_field.py date-unique`
n'en pose aucun, parce que l'exemple officiel
`example/layout/pattern/date/index.html` du paquet 1.15.2 n'en pose pas non
plus (vérifié : aucune occurrence). La règle ci-dessus vise la saisie manuelle
d'un formulaire écrit à la main ; l'ajouter au bloc généré l'écarterait de
l'officiel. Les deux artefacts divergent donc volontairement.

---
