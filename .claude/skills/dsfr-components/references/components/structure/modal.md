# Modales

Référence extraite de `../structure.md`.

---

## Structure de base
```html
<dialog id="modal-1" class="fr-modal" aria-labelledby="modal-1-title">
    <div class="fr-container fr-container--fluid fr-container-md">
        <div class="fr-grid-row fr-grid-row--center">
            <div class="fr-col-12 fr-col-md-8 fr-col-lg-6">
                <div class="fr-modal__body">
                    <div class="fr-modal__header">
                        <button type="button" class="fr-btn--close fr-btn" title="Fermer la fenêtre modale" aria-controls="modal-1">
                            Fermer
                        </button>
                    </div>
                    <div class="fr-modal__content">
                        <h2 id="modal-1-title" class="fr-modal__title">
                            Titre de la modale
                        </h2>
                        <p>Contenu de la modale</p>
                    </div>
                    <div class="fr-modal__footer">
                        <div class="fr-btns-group fr-btns-group--right fr-btns-group--inline-reverse fr-btns-group--inline-lg">
                            <button type="button" class="fr-btn">Action principale</button>
                            <button type="button" class="fr-btn fr-btn--secondary">Action secondaire</button>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
</dialog>
```

**Règles** :
- `<dialog>` porte déjà le rôle `dialog` : ne pas ajouter `role="dialog"`
- Le titre de la modale est un `<h2>`, comme dans le paquet officiel : un `<h1>`
  produirait un second `<h1>` dans une page qui a déjà le sien

## Ouverture de modale
```html
<button type="button" class="fr-btn" data-fr-opened="false" aria-controls="modal-1">
    Ouvrir la modale
</button>
```

---
