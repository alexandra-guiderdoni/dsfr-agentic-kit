# FranceConnect et ProConnect

Référence extraite de `../forms-services.md`.

---

Boutons officiels d'authentification : FranceConnect et FranceConnect+ pour
les usagers, ProConnect (variante `fr-connect--pro`, DSFR 1.15.0, #1388) pour
les agents et professionnels.

## FranceConnect standard
```html
<div class="fr-connect-group">
    <button type="button" class="fr-connect">
        <span class="fr-connect__login">S'identifier avec</span>
        <span class="fr-connect__brand">FranceConnect</span>
    </button>
    <p>
        <a href="https://franceconnect.gouv.fr/" target="_blank" rel="noopener"
           title="Qu'est-ce que FranceConnect ? - nouvelle fenêtre">
            Qu'est-ce que FranceConnect ?
        </a>
    </p>
</div>
```

## FranceConnect+
```html
<div class="fr-connect-group">
    <button type="button" class="fr-connect fr-connect--plus">
        <span class="fr-connect__login">S'identifier avec</span>
        <span class="fr-connect__brand">FranceConnect</span>
    </button>
    <p>
        <a href="https://franceconnect.gouv.fr/france-connect-plus" target="_blank" rel="noopener"
           title="Qu'est-ce que FranceConnect+ ? - nouvelle fenêtre">
            Qu'est-ce que FranceConnect+ ?
        </a>
    </p>
</div>
```

Le libellé reste « FranceConnect » : le signe `+` est ajouté par le style
`.fr-connect--plus::after` du paquet ; l'écrire dans le markup le double.

## ProConnect
```html
<div class="fr-connect-group">
    <button type="button" class="fr-connect fr-connect--pro">
        <span class="fr-connect__login">S'identifier avec</span>
        <span class="fr-connect__brand">ProConnect</span>
    </button>
    <p>
        <a href="https://proconnect.gouv.fr/" target="_blank" rel="noopener"
           title="Qu'est-ce que ProConnect ? - nouvelle fenêtre">
            Qu'est-ce que ProConnect ?
        </a>
    </p>
</div>
```

Source : `example/component/connect/index.html` du paquet 1.15.3 ; générateur
`generate_component.py connect --config '{"brand":"default|plus|pro"}'`.

**Règles** :
- Le bouton a un style spécifique imposé (ne pas personnaliser)
- `fr-connect--plus` pour FranceConnect+ (niveau de sécurité supérieur),
  `fr-connect--pro` pour ProConnect
- Le lien « Qu'est-ce que … ? » est obligatoire
- `target="_blank"` avec `rel="noopener"` sur le lien externe

---
