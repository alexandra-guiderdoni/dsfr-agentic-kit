# Paramètre d'affichage (Display)

<a id="parametre-daffichage-display"></a>

Référence extraite de `../content-media.md`.

---

Composant officiel « Paramètre d'affichage » : un bouton `fr-btn--display` qui
ouvre une modale de choix de thème (clair, sombre, système). Nom générable :
`display`.

## Structure

Sortie de `generate_component.py display`, abrégée sur la grille de la modale.

```html
<button aria-controls="fr-theme-modal" data-fr-opened="false" title="Paramètres d'affichage" type="button" class="fr-btn--display fr-btn">
    Paramètres d'affichage
</button>
<dialog id="fr-theme-modal" class="fr-modal" aria-labelledby="fr-theme-modal-title">
    <div class="fr-container fr-container--fluid fr-container-md">
        <div class="fr-grid-row fr-grid-row--center">
            <div class="fr-col-12 fr-col-md-6 fr-col-lg-4">
                <div class="fr-modal__body">
                    <div class="fr-modal__header">
                        <button aria-controls="fr-theme-modal" title="Fermer" type="button" class="fr-btn--close fr-btn">Fermer</button>
                    </div>
                    <div class="fr-modal__content">
                        <h2 id="fr-theme-modal-title" class="fr-modal__title">Paramètres d'affichage</h2>
                        <div id="fr-display" class="fr-display">
                            <fieldset class="fr-fieldset" id="display-fieldset">
                                <legend class="fr-fieldset__legend fr-fieldset__legend--regular" id="display-fieldset-legend">
                                    Choisissez un thème pour personnaliser l'apparence du site.
                                </legend>
                                <div class="fr-fieldset__element">
                                    <div class="fr-radio-group">
                                        <input value="light" type="radio" id="fr-radios-theme-light" name="fr-radios-theme">
                                        <label class="fr-label" for="fr-radios-theme-light">Thème clair</label>
                                    </div>
                                </div>
                                <div class="fr-fieldset__element">
                                    <div class="fr-radio-group">
                                        <input value="dark" type="radio" id="fr-radios-theme-dark" name="fr-radios-theme">
                                        <label class="fr-label" for="fr-radios-theme-dark">Thème sombre</label>
                                    </div>
                                </div>
                                <div class="fr-fieldset__element">
                                    <div class="fr-radio-group">
                                        <input value="system" type="radio" id="fr-radios-theme-system" name="fr-radios-theme">
                                        <label class="fr-label" for="fr-radios-theme-system">Système</label>
                                    </div>
                                </div>
                            </fieldset>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
</dialog>
```

**Règles** :
- Les identifiants `fr-theme-modal` et `fr-display` sont fixés par le script
  DSFR : ne pas les renommer, sinon le changement de thème ne s'applique pas
- Le bouton se place dans `fr-header__tools-links`, à l'intérieur d'un
  `fr-btns-group`
- Un seul paramètre d'affichage par page

Pour la carte d'organisme bâtie sur `fr-card--horizontal-tier`, voir
[`content-media/carte-identite.md`](carte-identite.md).
