# Gestionnaire de consentement

Référence vérifiée dans les exemples officiels DSFR 1.13.2 et 1.15.2 :

- https://unpkg.com/@gouvfr/dsfr@1.13.2/example/component/consent/index.html
- https://unpkg.com/@gouvfr/dsfr@1.15.2/example/component/consent/index.html

## Bandeau

```html
<div class="fr-consent-banner">
  <h2 class="fr-h6">À propos des cookies</h2>
  <div class="fr-consent-banner__content"><p class="fr-text--sm">Information</p></div>
  <ul class="fr-consent-banner__buttons fr-btns-group">
    <li><button class="fr-btn" type="button">Tout accepter</button></li>
    <li><button class="fr-btn" type="button">Tout refuser</button></li>
    <li><button class="fr-btn fr-btn--secondary" type="button" aria-controls="fr-consent-modal">Personnaliser</button></li>
  </ul>
</div>
```

## Gestionnaire dans une modale

```html
<dialog id="fr-consent-modal" class="fr-modal" aria-labelledby="fr-consent-modal-title">
  <div class="fr-modal__body">
    <div class="fr-modal__header"><button class="fr-btn fr-btn--close" type="button" aria-controls="fr-consent-modal">Fermer</button></div>
    <div class="fr-modal__content">
      <h2 id="fr-consent-modal-title" class="fr-modal__title">Panneau de gestion des cookies</h2>
      <div class="fr-consent-manager">
        <div class="fr-consent-service">
          <fieldset class="fr-fieldset">
            <legend class="fr-consent-service__title">Cookies obligatoires</legend>
            <div class="fr-consent-service__radios">
              <div class="fr-radio-group"><input type="radio" value="required" checked><label class="fr-label">Accepter</label></div>
              <div class="fr-radio-group"><input type="radio" value="off" disabled><label class="fr-label">Refuser</label></div>
            </div>
            <p class="fr-consent-service__desc">Description</p>
          </fieldset>
        </div>
      </div>
      <ul class="fr-consent-manager__buttons fr-btns-group">
        <li><button class="fr-btn" type="button">Confirmer mes choix</button></li>
      </ul>
    </div>
  </div>
</dialog>
```

## Règles

- L’acceptation d’un service obligatoire est cochée mais n’est pas désactivée.
- Le refus du service obligatoire est désactivé.
- Le groupe `fr-consent-manager__buttons` reste dans le contenu de la modale, après `fr-consent-manager`, et n’exige pas de `fr-modal__footer`.
