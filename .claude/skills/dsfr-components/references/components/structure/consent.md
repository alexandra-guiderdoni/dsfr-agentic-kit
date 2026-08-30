# Bandeau de consentement cookies (Consent)

Référence extraite de `../structure.md`.

---

## Structure
```html
<dialog id="fr-consent-modal" class="fr-modal" aria-labelledby="fr-consent-title">
    <div class="fr-container fr-container--fluid fr-container-md">
        <div class="fr-grid-row fr-grid-row--center">
            <div class="fr-col-12 fr-col-md-10 fr-col-lg-8">
                <div class="fr-modal__body">
                    <div class="fr-modal__header">
                        <button type="button" class="fr-btn--close fr-btn" aria-controls="fr-consent-modal" title="Fermer">
                            Fermer
                        </button>
                    </div>
                    <div class="fr-modal__content">
                        <h2 id="fr-consent-title" class="fr-modal__title">
                            Panneau de gestion des cookies
                        </h2>
                        <div class="fr-consent-manager">
                            <div class="fr-consent-service">
                                <fieldset aria-labelledby="finality-0-legend finality-0-desc" role="group" class="fr-fieldset">
                                    <legend id="finality-0-legend" class="fr-consent-service__title">Cookies obligatoires</legend>
                                    <div class="fr-consent-service__radios">
                                        <div class="fr-radio-group">
                                            <input type="radio" id="consent-essential-accept" name="consent-essential" checked disabled>
                                            <label class="fr-label" for="consent-essential-accept">Accepter</label>
                                        </div>
                                        <div class="fr-radio-group">
                                            <input type="radio" id="consent-essential-refuse" name="consent-essential" disabled>
                                            <label class="fr-label" for="consent-essential-refuse">Refuser</label>
                                        </div>
                                    </div>
                                    <p id="finality-0-desc" class="fr-consent-service__desc">Ce site utilise des cookies nécessaires à son bon fonctionnement.</p>
                                </fieldset>
                            </div>
                            <div class="fr-consent-service">
                                <fieldset aria-labelledby="finality-1-legend finality-1-desc" role="group" class="fr-fieldset">
                                    <legend id="finality-1-legend" class="fr-consent-service__title">Mesure d'audience</legend>
                                    <div class="fr-consent-service__radios">
                                        <div class="fr-radio-group">
                                            <input type="radio" id="consent-analytics-accept" name="consent-analytics">
                                            <label class="fr-label" for="consent-analytics-accept">Accepter</label>
                                        </div>
                                        <div class="fr-radio-group">
                                            <input type="radio" id="consent-analytics-refuse" name="consent-analytics">
                                            <label class="fr-label" for="consent-analytics-refuse">Refuser</label>
                                        </div>
                                    </div>
                                    <p id="finality-1-desc" class="fr-consent-service__desc">Cookies de statistiques anonymes (ex : Matomo).</p>
                                </fieldset>
                            </div>
                        </div>
                    </div>
                    <div class="fr-modal__footer">
                        <ul class="fr-consent-manager__buttons fr-btns-group fr-btns-group--right fr-btns-group--inline-sm">
                            <li>
                                <button type="button" class="fr-btn">
                                    Confirmer mes choix
                                </button>
                            </li>
                            <li>
                                <button type="button" class="fr-btn fr-btn--secondary">Tout accepter</button>
                            </li>
                            <li>
                                <button type="button" class="fr-btn fr-btn--secondary">Tout refuser</button>
                            </li>
                        </ul>
                    </div>
                </div>
            </div>
        </div>
    </div>
</dialog>
```

## Bandeau simplifié (notice de consentement)
Le bandeau qui s'affiche en bas de page avant l'interaction utilisateur :
```html
<div class="fr-consent-banner">
    <h2 class="fr-h6">À propos des cookies sur ce site</h2>
    <div class="fr-consent-banner__content">
        <p class="fr-text--sm">Bienvenue ! Nous utilisons des cookies pour améliorer votre expérience et les services disponibles sur ce site. Pour en savoir plus, visitez la page <a href="/donnees-personnelles">Données personnelles et cookies</a>. Vous pouvez, à tout moment, avoir le contrôle sur les cookies que vous souhaitez activer.</p>
    </div>
    <ul class="fr-consent-banner__buttons fr-btns-group fr-btns-group--right fr-btns-group--inline-reverse fr-btns-group--inline-sm">
        <li>
            <button type="button" class="fr-btn" title="Autoriser tous les cookies">
                Tout accepter
            </button>
        </li>
        <li>
            <button type="button" class="fr-btn" title="Refuser tous les cookies">
                Tout refuser
            </button>
        </li>
        <li>
            <button type="button" class="fr-btn fr-btn--secondary" data-fr-opened="false" aria-controls="fr-consent-modal" title="Personnaliser les cookies">
                Personnaliser
            </button>
        </li>
    </ul>
</div>
```
**Règles** :
- Le bandeau de consentement doit être vérifié avec les exigences RGPD
  applicables ; le bouton « Tout refuser » doit être aussi visible que
  « Tout accepter »
- Le couple `data-fr-opened="false"` + `aria-controls="fr-consent-modal"` est le
  mécanisme d'ouverture de modale du DSFR : le poser uniquement sur
  « Personnaliser ». Sur « Tout accepter », « Tout refuser » ou « Confirmer mes
  choix », il ferait ouvrir le panneau au lieu d'enregistrer le choix
- Chaque finalité est un `<fieldset role="group">` dont l'`aria-labelledby`
  cite le `<legend>` puis le `<p class="fr-consent-service__desc">` placé après
  les boutons radio

---
