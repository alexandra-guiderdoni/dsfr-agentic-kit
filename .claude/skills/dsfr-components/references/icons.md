# Icônes DSFR 1.15.3

Format : `fr-icon-[nom]-[style]` avec `-line` (contour) ou `-fill` (rempli).

CDN : `@gouvfr/dsfr@1.15.3/dist/utility/icons/icons.min.css`

> Liste indicative d'exemples (1047 icônes officielles). Les noms exacts varient
> (ex. `folder-2-line`, `ship-2-line`, `store-line`). Valider toute icône avec
> `list_icons.py --validate <nom>` avant usage ; ne pas inventer de nom.

---

## Utilisation

```html
<!-- Dans un bouton -->
<button class="fr-btn fr-btn--icon-left fr-icon-arrow-right-line">Suivant</button>

<!-- Icône seule (décorative) -->
<span class="fr-icon-check-line" aria-hidden="true"></span>

<!-- Icône seule (informative) -->
<span class="fr-icon-warning-fill" role="img" aria-label="Attention"></span>
```

**Règle** : `aria-hidden="true"` si l'icône est décorative, `role="img"` + `aria-label` si informative.

---

## Catalogue par famille

### Système
- `fr-icon-arrow-right-line` / `-fill`
- `fr-icon-arrow-left-line` / `-fill`
- `fr-icon-arrow-up-line` / `-fill`
- `fr-icon-arrow-down-line` / `-fill`
- `fr-icon-arrow-go-back-line` / `-fill`
- `fr-icon-arrow-go-forward-line` / `-fill`
- `fr-icon-arrow-right-down-circle-fill` (ajoutée en 1.15.0)
- `fr-icon-arrow-right-up-circle-fill` (ajoutée en 1.15.0)
- `fr-icon-check-line`
- `fr-icon-close-line`
- `fr-icon-add-line`
- `fr-icon-subtract-line`
- `fr-icon-menu-fill`
- `fr-icon-more-line` / `-fill`
- `fr-icon-search-line` / `-fill`
- `fr-icon-refresh-line` / `-fill`
- `fr-icon-filter-line` / `-fill`
- `fr-icon-sort-asc` / `fr-icon-sort-desc`
- `fr-icon-external-link-line` / `-fill`
- `fr-icon-links-line` / `-fill`
- `fr-icon-share-line` / `-fill`
- `fr-icon-download-line` / `-fill`
- `fr-icon-upload-line` / `-fill`
- `fr-icon-delete-line` / `-fill`
- `fr-icon-edit-line` / `-fill`
- `fr-icon-eye-line` / `-fill`
- `fr-icon-eye-off-line` / `-fill`
- `fr-icon-settings-5-line` / `-fill`
- `fr-icon-equalizer-line` / `-fill`

### Alertes et statuts
- `fr-icon-info-line` / `-fill`
- `fr-icon-warning-line` / `-fill`
- `fr-icon-error-line` / `-fill`
- `fr-icon-success-line` / `-fill`
- `fr-icon-question-line` / `-fill`
- `fr-icon-notification-3-line` / `-fill`
- `fr-icon-checkbox-circle-line` / `-fill`
- `fr-icon-close-circle-line` / `-fill`
- `fr-icon-alert-line` / `-fill`
- `fr-icon-shield-line` / `-fill`
- `fr-icon-lock-line` / `-fill`
- `fr-icon-lock-unlock-line` / `-fill`

### Utilisateur et compte
- `fr-icon-user-line` / `-fill`
- `fr-icon-user-add-line` / `-fill`
- `fr-icon-user-setting-line` / `-fill`
- `fr-icon-account-line` / `-fill`
- `fr-icon-account-circle-line` / `-fill`
- `fr-icon-group-line` / `-fill`
- `fr-icon-team-line` / `-fill`
- `fr-icon-parent-line` / `-fill`
- `fr-icon-admin-line` / `-fill`

### Communication
- `fr-icon-mail-line` / `-fill`
- `fr-icon-mail-open-line` / `-fill`
- `fr-icon-chat-3-line` / `-fill`
- `fr-icon-discuss-line` / `-fill`
- `fr-icon-phone-line` / `-fill`
- `fr-icon-smartphone-line` / `-fill`
- `fr-icon-questionnaire-line` / `-fill`
- `fr-icon-message-2-line` / `-fill`
- `fr-icon-feedback-line` / `-fill`

### Fichiers et documents
- `fr-icon-file-line` / `-fill`
- `fr-icon-file-add-line` / `-fill`
- `fr-icon-file-download-line` / `-fill`
- `fr-icon-file-pdf-line` / `-fill`
- `fr-icon-file-text-line` / `-fill`
- `fr-icon-folder-2-line` / `-fill`
- `fr-icon-clipboard-line` / `-fill`
- `fr-icon-draft-line` / `-fill`
- `fr-icon-article-line` / `-fill`
- `fr-icon-newspaper-line` / `-fill`
- `fr-icon-book-2-line` / `-fill`
- `fr-icon-booklet-line` / `-fill`
- `fr-icon-archive-line` / `-fill`

### Temps et calendrier
- `fr-icon-calendar-line` / `-fill`
- `fr-icon-calendar-2-line` / `-fill`
- `fr-icon-calendar-event-line` / `-fill`
- `fr-icon-time-line` / `-fill`
- `fr-icon-timer-line` / `-fill`

### Localisation
- `fr-icon-map-pin-2-line` / `-fill`
- `fr-icon-road-map-line` / `-fill`
- `fr-icon-earth-line` / `-fill`
- `fr-icon-france-line` / `-fill`
- `fr-icon-compass-3-line` / `-fill`
- `fr-icon-home-4-line` / `-fill`
- `fr-icon-building-line` / `-fill`
- `fr-icon-government-line` / `-fill`
- `fr-icon-community-line` / `-fill`
- `fr-icon-hotel-line` / `-fill`
- `fr-icon-hospital-line` / `-fill`
- `fr-icon-store-line` / `-fill`

### Media
- `fr-icon-image-line` / `-fill`
- `fr-icon-camera-line` / `-fill`
- `fr-icon-video-chat-line` / `-fill`
- `fr-icon-music-2-line` / `-fill`
- `fr-icon-volume-up-line` / `-fill`
- `fr-icon-volume-mute-line` / `-fill`
- `fr-icon-mic-line` / `-fill`
- `fr-icon-play-circle-line` / `-fill`
- `fr-icon-pause-circle-line` / `-fill`
- `fr-icon-stop-circle-line` / `-fill`

### Meteo et nature
- `fr-icon-sun-line` / `-fill`
- `fr-icon-moon-line` / `-fill`
- `fr-icon-cloud-line` / `-fill`
- `fr-icon-flashlight-line` / `-fill`
- `fr-icon-leaf-line` / `-fill`
- `fr-icon-plant-line` / `-fill`
- `fr-icon-seedling-line` / `-fill`

### Transport
- `fr-icon-car-line` / `-fill`
- `fr-icon-bus-line` / `-fill`
- `fr-icon-train-line` / `-fill`
- `fr-icon-ship-2-line` / `-fill`
- `fr-icon-bike-line` / `-fill`

### Finance et commerce
- `fr-icon-money-euro-circle-line` / `-fill`
- `fr-icon-coin-fill`
- `fr-icon-bank-line` / `-fill`
- `fr-icon-shopping-cart-2-line` / `-fill`
- `fr-icon-gift-line` / `-fill`
- `fr-icon-bank-card-line` / `-fill`

### Santé
- `fr-icon-heart-line` / `-fill`
- `fr-icon-heart-pulse-line` / `-fill`
- `fr-icon-stethoscope-line` / `-fill`
- `fr-icon-capsule-line` / `-fill`
- `fr-icon-first-aid-kit-line` / `-fill`
- `fr-icon-virus-line` / `-fill`
- `fr-icon-lungs-line` / `-fill`
- `fr-icon-mental-health-line` / `-fill`

### Reseaux sociaux
- `fr-icon-facebook-circle-fill`
- `fr-icon-twitter-x-fill`
- `fr-icon-linkedin-box-fill`
- `fr-icon-instagram-fill`
- `fr-icon-youtube-fill`
- `fr-icon-github-fill`
- `fr-icon-twitch-fill`
- `fr-icon-snapchat-fill`
- `fr-icon-tiktok-fill`
- `fr-icon-mastodon-fill`
- `fr-icon-dailymotion-fill`

### Technologie
- `fr-icon-computer-line` / `-fill`
- `fr-icon-terminal-line` / `-fill`
- `fr-icon-code-line` / `-fill`
- `fr-icon-database-line` / `-fill`
- `fr-icon-wifi-line` / `-fill`
- `fr-icon-bluetooth-line` / `-fill`
- `fr-icon-printer-line` / `-fill`
- `fr-icon-qr-code-line` / `-fill`

---

## Tailles

Valeurs de `--icon-size` relevées dans `dist/dsfr.min.css` du paquet 1.15.3
(source SCSS : `src/dsfr/core/style/icon/_setting.scss`, `$icon-size-map`) :

- Par défaut, icône seule hors bouton, badge et lien externe : 1.5rem (24px)
- `fr-icon--xs` : 0.75rem (12px)
- `fr-icon--sm` : 1rem (16px)
- `fr-icon--md` : 1.5rem (24px)
- `fr-icon--lg` : 2rem (32px)

Dans un bouton, un badge ou un lien externe, la règle du composant reprend la
main : la taille effective y est contextualisée (1rem pour `fr-btn--icon-left`
ou `fr-badge--icon-left`, par exemple), indépendamment de ces classes.

`fr-icon--xl` n'existe pas en DSFR 1.15.3 (tailles officielles : `xs`, `sm`,
`md`, `lg` ; vérifié dans `dist/dsfr.min.css`).
