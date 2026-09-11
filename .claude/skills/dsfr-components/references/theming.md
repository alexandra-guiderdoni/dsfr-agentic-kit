# Theming DSFR 1.15.3

Le DSFR supporte nativement les thèmes clair et sombre via l'attribut `data-fr-scheme` et les CSS custom properties.

---

## Activation du thème

### Par défaut (thème système)

```html
<html lang="fr" data-fr-scheme="system">
```

Le DSFR suit la préférence `prefers-color-scheme` du navigateur/OS.

### Thème forcé

```html
<!-- Thème clair forcé -->
<html lang="fr" data-fr-scheme="light">

<!-- Thème sombre forcé -->
<html lang="fr" data-fr-scheme="dark">
```

### Bouton de bascule (display settings)

Le DSFR fournit un composant natif de paramètres d'affichage : un bouton
d'ouverture et une modale `fr-modal` qui porte l'`id` `fr-theme-modal` et
le titre `fr-theme-modal-title` (sortie de `generate_component.py display`,
structure de `example/component/display/index.html` du paquet 1.15.3) :

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

Le JavaScript du DSFR (`dsfr.min.js`) gère automatiquement la bascule.

Depuis DSFR 1.15.0 (#1434), ce composant est désactivé quand l'attribut
`data-fr-scheme` est absent de la balise `html`. Une page qui omet l'attribut
n'a donc plus de sélecteur de thème fonctionnel, sans message d'erreur : poser
`data-fr-scheme` est devenu une condition de fonctionnement, pas seulement une
valeur par défaut.

### Lien dans le footer

Le lien vers les paramètres d'affichage est recommandé dans le footer quand la
page expose le composant display ; il n'est ni exigé par le paquet officiel
(`example/component/footer/index.html` liste cinq liens de bas de page sans
celui-ci) ni émis par `generate_page.py`. Le placer à la main le cas échéant.

`type="button"` est obligatoire : sans lui, un `<button>` vaut `submit` et,
copié dans le `<form>` d'une page `form`, `login` ou `account`, il soumet le
formulaire au lieu d'ouvrir la modale.

```html
<button type="button"
        class="fr-footer__bottom-link"
        aria-controls="fr-theme-modal"
        data-fr-opened="false"
        title="Paramètres d'affichage">
    Paramètres d'affichage
</button>
```

---

## Variables CSS (tokens de couleur)

Le DSFR utilise des custom properties qui s'adaptent automatiquement au thème.

Valeurs relevées dans `dist/dsfr.min.css` de `@gouvfr/dsfr@1.15.3` (blocs
`:root` et `:root[data-fr-theme=dark]`, alias `var()` résolus) ; le CSS abrège
`#ffffff` en `#fff`.

### Couleurs de fond

| Variable | Thème clair | Thème sombre |
|----------|------------|--------------|
| `--background-default-grey` | #ffffff | #161616 |
| `--background-contrast-grey` | #eeeeee | #242424 |
| `--background-alt-grey` | #f6f6f6 | #1e1e1e |
| `--background-raised-grey` | #ffffff | #1e1e1e |
| `--background-overlap-grey` | #ffffff | #242424 |
| `--background-action-high-blue-france` | #000091 | #8585f6 |
| `--background-action-low-blue-france` | #e3e3fd | #272747 |

### Couleurs de texte

| Variable | Thème clair | Thème sombre |
|----------|------------|--------------|
| `--text-default-grey` | #3a3a3a | #cecece |
| `--text-title-grey` | #161616 | #ffffff |
| `--text-mention-grey` | #666666 | #929292 |
| `--text-action-high-blue-france` | #000091 | #8585f6 |
| `--text-inverted-blue-france` | #f5f5fe | #000091 |

### Couleurs de bordure

| Variable | Thème clair | Thème sombre |
|----------|------------|--------------|
| `--border-default-grey` | #dddddd | #353535 |
| `--border-action-high-blue-france` | #000091 | #8585f6 |
| `--border-plain-grey` | #3a3a3a | #cecece |

---

## Bonnes pratiques

1. **Ne jamais hardcoder de couleurs** : utiliser les classes `fr-*` ou les variables CSS `--*`
2. **Tester les deux thèmes** : vérifier les contrastes en clair ET en sombre
3. **Pictogrammes** : les 3 calques SVG s'adaptent automatiquement (pas d'action requise)
4. **Images** : prévoir des versions alternatives si le contraste est insuffisant en mode sombre
5. **Ombres** : utiliser `--raised-shadow`, `--overlap-shadow` ou
   `--lifted-shadow`, qui s'appuient sur `--shadow-color` et s'adaptent au
   thème (aucun autre token d'ombre n'est déclaré, cf.
   `references/tokens.md`)

---

## Génération avec le skill

Pour générer une page en mode sombre :

```bash
python3 scripts/generate_page.py --type standard --title "Ma page" --dark --output page.html
```

L'option `--dark` ajoute `data-fr-scheme="dark"` sur la balise `<html>`. C'est
la seule option de thème : `system` et `light` ne sont pas exposés.

Sans `--dark`, la page sort en `<html lang="fr" data-fr-scheme="system">` : le
sélecteur de thème documenté plus haut y serait inerte, puisque le composant
est désactivé quand l'attribut manque (DSFR 1.15.0, #1434). Poser
`data-fr-scheme="system"` à la main dès que la page expose le composant
display.
