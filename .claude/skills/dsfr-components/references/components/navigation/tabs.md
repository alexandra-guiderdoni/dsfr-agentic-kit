# Onglets

Référence extraite de `../navigation.md`.

---

## Structure de base
```html
<div class="fr-tabs">
    <ul class="fr-tabs__list" role="tablist" aria-label="Navigation par onglets">
        <li role="presentation">
            <button type="button" id="tab-1" class="fr-tabs__tab" tabindex="0" role="tab"
                    aria-selected="true" aria-controls="tabpanel-1">
                Onglet 1
            </button>
        </li>
        <li role="presentation">
            <button type="button" id="tab-2" class="fr-tabs__tab" tabindex="-1" role="tab"
                    aria-selected="false" aria-controls="tabpanel-2">
                Onglet 2
            </button>
        </li>
    </ul>
    <div id="tabpanel-1" class="fr-tabs__panel fr-tabs__panel--selected"
         role="tabpanel" aria-labelledby="tab-1" tabindex="0">
        <p>Contenu onglet 1</p>
    </div>
    <div id="tabpanel-2" class="fr-tabs__panel"
         role="tabpanel" aria-labelledby="tab-2" tabindex="0">
        <p>Contenu onglet 2</p>
    </div>
</div>
```

## Onglets avec icônes
```html
<button type="button" id="tab-icon" class="fr-tabs__tab fr-icon-file-line fr-tabs__tab--icon-left" tabindex="0" role="tab"
        aria-selected="true" aria-controls="tabpanel-icon">
    Documents
</button>
```

---
