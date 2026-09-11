# Nom et prénom

Référence extraite de `../patterns.md`.

---

## Pattern recommandé

Sortie exacte de `python3 scripts/generate_field.py nom-prenom`, alignée sur
l'exemple officiel `example/layout/pattern/name` du paquet 1.15.3 : légende
masquée `fr-sr-only` liée par `aria-labelledby`, un `fr-messages-group` par
champ relié par `aria-describedby`, `name` égal au jeton `autocomplete`, et
`spellcheck="false"`.

```html
<fieldset class="fr-fieldset" id="name-fieldset" aria-labelledby="name-legend name-messages">
    <legend class="fr-sr-only" id="name-legend">Demande de nom et prénom</legend>
        <div class="fr-fieldset__element">
            <div class="fr-input-group">
                <label class="fr-label" for="name-given-name">Prénom</label>
                <input class="fr-input" spellcheck="false" autocomplete="given-name" name="given-name" aria-describedby="name-given-name-messages" id="name-given-name" type="text">
                <div class="fr-messages-group" id="name-given-name-messages" aria-live="polite"></div>
            </div>
        </div>
        <div class="fr-fieldset__element">
            <div class="fr-input-group">
                <label class="fr-label" for="name-family-name">Nom</label>
                <input class="fr-input" spellcheck="false" autocomplete="family-name" name="family-name" aria-describedby="name-family-name-messages" id="name-family-name" type="text">
                <div class="fr-messages-group" id="name-family-name-messages" aria-live="polite"></div>
            </div>
        </div>
    <div class="fr-messages-group" aria-live="polite" id="name-messages"></div>
</fieldset>
```

Le champ « Nom d'usage » ci-dessous est une **extension hors bloc officiel** :
ni le générateur ni l'exemple 1.15.3 ne le produisent. Le reprendre suppose de
l'ajouter à la main, avec son propre groupe de messages.

```html
<div class="fr-fieldset__element">
    <div class="fr-input-group">
        <label class="fr-label" for="name-usage">Nom d'usage
            <span class="fr-hint-text">Facultatif — si différent du nom de famille</span>
        </label>
        <input class="fr-input" spellcheck="false" aria-describedby="name-usage-messages" id="name-usage" name="name-usage" type="text">
        <div class="fr-messages-group" id="name-usage-messages" aria-live="polite"></div>
    </div>
</div>
```

## Règles
- Prénom AVANT nom (ordre naturel en français)
- `autocomplete="given-name"` et `autocomplete="family-name"` obligatoires (WCAG 1.3.5)
- Si prénom et nom sont obligatoires, poser `required` au premier `submit` via
  le pattern de validation différée.
- Nom d'usage : optionnel, avec hint explicatif ; hors bloc généré, à ajouter à la main
- Ne PAS demander « civilité » avec le nom (voir pattern civilité séparé)

---
