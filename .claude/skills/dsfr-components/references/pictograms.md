# Pictogrammes DSFR 1.15.2

Les pictogrammes sont des illustrations vectorielles SVG plus détaillées que les icônes. Ils servent à illustrer des concepts dans les tuiles, callouts et pages d'information.

Source dans le paquet : `@gouvfr/dsfr@1.15.2/dist/artwork/pictograms/`.

**Les pictogrammes doivent être servis depuis la même origine que la page.**
Un `<use href>` pointant vers un domaine tiers, CDN compris, n'est résolu par
aucun navigateur moderne : le `<svg>` occupe sa boîte mais reste vide, sans
erreur visible. Mesuré le 2026-08-28 sur une page servie en HTTP, avec le même
pictogramme des deux façons : depuis un CDN tiers la boîte englobante rendue est
de 0 × 0, depuis la même origine elle est de 60 × 64. Résultat identique en
1.14.4 et en 1.15.2 — ce n'est pas un effet du durcissement de 1.15.0, qui ne
concerne que le polyfill d'injection sur Internet Explorer 11.

Copier donc `dist/artwork/pictograms/` dans les assets du service et référencer
un chemin de la même origine, comme le fait le défaut de
`scripts/generate_atom.py pictogram` (`/dsfr/artwork/pictograms/...`). La feuille
de style et le script du DSFR, eux, peuvent rester sur un CDN : la restriction
ne porte que sur les références `<use>`.

Pour une copie sélective et vérifiée plutôt qu’une copie en bloc (structure DSFR,
trois calques, `sha256` contre le manifeste annoté des 102 pictogrammes), utiliser
le skill `generer-pictos-svg-dsfr` livré avec ce pack, depuis son dossier :
`python3 scripts/generate_pictos_svg.py --source dsfr-replica --icons digital/internet --output-dir <assets>`.
Le pack ne redistribue pas les SVG officiels : le skill les lit dans le paquet
officiel en cache (`DSFR_OFFICIAL_CACHE_DIR`, le même que les contrôles) et
répond `NOT VERIFIED: source officielle absente` s’il manque. Un pictogramme
absent du DSFR se crée avec ce même skill, toujours `official: false`.

---

## Utilisation

```html
<!-- Dans une tuile -->
<div class="fr-tile fr-tile--horizontal">
    <div class="fr-tile__body">
        <h3 class="fr-tile__title"><a href="/">Mon service</a></h3>
        <p class="fr-tile__desc">Description du service</p>
    </div>
    <div class="fr-tile__header">
        <div class="fr-tile__pictogram">
            <svg aria-hidden="true" class="fr-artwork" viewBox="0 0 80 80" width="80" height="80">
                <use class="fr-artwork-decorative" href="/dsfr/artwork/pictograms/digital/internet.svg#artwork-decorative"></use>
                <use class="fr-artwork-minor" href="/dsfr/artwork/pictograms/digital/internet.svg#artwork-minor"></use>
                <use class="fr-artwork-major" href="/dsfr/artwork/pictograms/digital/internet.svg#artwork-major"></use>
            </svg>
        </div>
    </div>
</div>
```

**Structure SVG** : chaque pictogramme utilise 3 calques (`artwork-decorative`, `artwork-minor`, `artwork-major`) qui s'adaptent automatiquement au thème clair/sombre.

**Règle** : toujours `aria-hidden="true"` car les pictogrammes sont décoratifs (le texte adjacent porte le sens).

---

## Catalogue par famille

<!-- Catalogue généré depuis dist/artwork/pictograms du paquet officiel
     @gouvfr/dsfr@1.15.2 ; vérifié par scripts/check_pictograms_doc.sh du skill
     du dépôt de développement, script non distribué avec le skill.
     Ne pas ajouter un nom à la main : un pictogramme absent du paquet
     documenté comme officiel est exactement le mode d'échec --bf500. -->

### Accessibility (accessibility)

- `accessibility/accessibility.svg`
- `accessibility/ear-off.svg`
- `accessibility/eye-off.svg`
- `accessibility/mental-disabilities.svg`
- `accessibility/wheelchair.svg`

### Bâtiments (buildings)

- `buildings/base.svg`
- `buildings/city-hall.svg` : mairie
- `buildings/companie.svg`
- `buildings/factory.svg` : usine
- `buildings/house.svg` : maison
- `buildings/nuclear-plant.svg`
- `buildings/school.svg` : école

### Numérique (digital)

- `digital/application.svg` : application
- `digital/avatar.svg` : avatar
- `digital/calendar.svg` : calendrier
- `digital/coding.svg`
- `digital/data-visualization.svg` : visualisation de données
- `digital/ecosystem.svg`
- `digital/in-progress.svg`
- `digital/innovation.svg`
- `digital/internet.svg` : internet
- `digital/mail-send.svg` : envoi de courrier
- `digital/search.svg` : recherche
- `digital/self-training.svg`
- `digital/smartphone.svg`

### Document et administratif (document)

- `document/archive.svg`
- `document/binders.svg`
- `document/conclusion.svg`
- `document/contract.svg` : contrat
- `document/document-add.svg`
- `document/document-download.svg`
- `document/document-search.svg`
- `document/document-signature.svg`
- `document/document.svg` : document générique
- `document/driving-licence.svg` : permis de conduire
- `document/driving-license-new.svg`
- `document/international-driving-license-new.svg`
- `document/international-driving-license.svg`
- `document/national-identity-card-passport.svg`
- `document/national-identity-card.svg` : CNI
- `document/passport.svg` : passeport
- `document/presse-card.svg`
- `document/sign-document.svg`
- `document/tax-stamp.svg`
- `document/vehicle-registration.svg` : carte grise

### Environnement (environment)

- `environment/environment.svg`
- `environment/food.svg` : alimentation
- `environment/grocery.svg` : épicerie
- `environment/human-cooperation.svg` : coopération
- `environment/leaf.svg` : feuille / écologie
- `environment/moon.svg`
- `environment/mountain.svg`
- `environment/sun.svg` : soleil
- `environment/tree.svg` : arbre

### Santé (health)

- `health/doctor.svg`
- `health/health.svg` : santé générique
- `health/hospital.svg` : hôpital
- `health/medical-research.svg`
- `health/vaccine.svg` : vaccin
- `health/virus.svg`

### Institutions (institutions)

- `institutions/army-tank.svg`
- `institutions/astronaut.svg`
- `institutions/firefighter.svg`
- `institutions/gendarmerie.svg`
- `institutions/justice.svg`
- `institutions/money.svg`
- `institutions/navy-anchor.svg`
- `institutions/navy-bachi.svg`
- `institutions/police.svg`

### Loisirs (leisure)

- `leisure/art.svg`
- `leisure/audio.svg`
- `leisure/book.svg` : livre
- `leisure/catalog.svg`
- `leisure/community.svg` : communauté
- `leisure/culture.svg` : culture
- `leisure/digital-art.svg` : art numérique
- `leisure/paint.svg` : peinture
- `leisure/pictures.svg`
- `leisure/podcast.svg`
- `leisure/video-games.svg`
- `leisure/video.svg`

### Localisation (map)

- `map/airport.svg`
- `map/backpack.svg`
- `map/compass.svg`
- `map/location-france.svg` : localisation France
- `map/location-overseas-france.svg`
- `map/luggage.svg`
- `map/map-pin.svg`
- `map/map.svg` : carte
- `map/travel-back.svg`

### Système (system)

- `system/connection-lost.svg`
- `system/error.svg` : erreur
- `system/flow-list.svg`
- `system/flow-settings.svg`
- `system/information.svg` : information
- `system/language.svg`
- `system/notification.svg` : notification
- `system/padlock.svg`
- `system/success.svg` : succès
- `system/system.svg`
- `system/technical-error.svg` : erreur technique
- `system/warning.svg` : avertissement

## Tailles

Deux tailles seulement sont attestées dans le paquet 1.15.2 :

- `width="80" height="80"` : taille par défaut, artboard officiel des 102 SVG
  (`viewBox="0 0 80 80"`). Les 102 fichiers de `dist/artwork/pictograms`
  déclarent tous une largeur de 80 (94 sous la forme `80px`, 8 sous la forme
  `80`), et 685 des 691 balises `fr-artwork` des exemples officiels emploient
  `80px`.
- `width="160" height="200"` : seule autre taille attestée, réservée aux
  compositions des pages de réponse officielles
  (`example/layout/page/response/`), où le pictogramme est translaté de
  `40, 60` au-dessus du fond `dist/artwork/background/ovoid.svg`. Ce n'est pas
  un simple agrandissement : le `viewBox` change avec la composition.

Les valeurs 100 et 48 ne figurent ni dans les SVG du paquet ni dans ses
exemples : ne pas les employer comme conventions officielles.

## Intégration avec le thème

Les 3 calques SVG utilisent des variables CSS du DSFR :
- `artwork-decorative` : couleur de fond (s'adapte au thème)
- `artwork-minor` : couleur secondaire
- `artwork-major` : couleur principale (Bleu France par défaut)

Aucune personnalisation CSS nécessaire : le passage en mode sombre est automatique.
