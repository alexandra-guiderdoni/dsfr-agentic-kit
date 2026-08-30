# Transcription

Référence extraite de `../content-media.md`.

---

Permet d'afficher/masquer la transcription textuelle d'un contenu multimédia (vidéo, audio).

## Structure
```html
<div class="fr-transcription" id="transcription-1">
    <button type="button" class="fr-transcription__btn"
            aria-expanded="false"
            aria-controls="fr-transcription-collapse-1">
        Transcription
    </button>
    <div class="fr-collapse" id="fr-transcription-collapse-1">
        <div class="fr-transcription__footer">
            <div class="fr-transcription__actions-group">
                <button type="button" class="fr-btn fr-btn--fullscreen"
                        aria-controls="fr-transcription-modal-1"
                        data-fr-opened="false"
                        aria-label="Agrandir la transcription">
                    Agrandir
                </button>
            </div>
        </div>
        <div id="fr-transcription-modal-1" class="fr-modal" aria-labelledby="fr-transcription-modal-title-1">
            <div class="fr-container fr-container--fluid fr-container-md">
                <div class="fr-grid-row fr-grid-row--center">
                    <div class="fr-col-12 fr-col-md-10 fr-col-lg-8">
                        <div class="fr-modal__body">
                            <div class="fr-modal__header">
                                <button type="button" class="fr-btn--close fr-btn"
                                        aria-controls="fr-transcription-modal-1"
                                        title="Fermer">
                                    Fermer
                                </button>
                            </div>
                            <div class="fr-modal__content">
                                <h2 id="fr-transcription-modal-title-1" class="fr-modal__title">
                                    Transcription
                                </h2>
                                <p>Contenu de la transcription textuelle du média...</p>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
</div>
```

**Règles** :
- Obligatoire pour toute vidéo ou audio (RGAA critère 4.1)
- Le bouton `aria-expanded` bascule entre `true`/`false`
- La modale plein écran est optionnelle mais recommandée pour les longs textes
- Le nom accessible du bouton plein écran passe par `aria-label` : sans lui,
  plusieurs médias sur une même page donnent autant de boutons « Agrandir »
  indistincts
