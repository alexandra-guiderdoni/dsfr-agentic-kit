# Contenu multimédia (Content)

<a id="contenu-multimedia-content"></a>

Référence extraite de `../content-media.md`.

---

Composant pour intégrer des médias (vidéo, carte, iframe) de manière responsive et accessible.

**Générateur** : `generate_component.py content --config '{"image": "…", "image_alt": "…", "caption": "…"}'` produit la figure image ; `--config '{"video": "https://…/embed/…", "video_title": "…", "caption": "…"}'` produit la variante vidéo (`iframe.fr-responsive-vid`, `title` obligatoire, URL http(s) seulement). Sans `image` ni `video`, le composant est le bloc éditorial générique décrit ci-dessous.
rend le `figure.fr-content-media` de la section « Image avec légende ». Sans
`image`, il rend un bloc éditorial (`<div>` + titre + paragraphe) sans classe
DSFR. La variante vidéo ci-dessous n'est produite par aucun paramètre : elle
s'écrit à la main.

## Vidéo responsive
```html
<figure class="fr-content-media" role="group" aria-label="Titre de la vidéo">
    <div class="fr-responsive-vid fr-ratio-16x9">
        <iframe
            title="Titre de la vidéo"
            class="fr-responsive-vid__player"
            src="https://www.youtube-nocookie.com/embed/VIDEO_ID"
            allow="accelerometer; autoplay; encrypted-media; gyroscope; picture-in-picture"
            allowfullscreen>
        </iframe>
    </div>
    <figcaption class="fr-content-media__caption">
        Légende de la vidéo
    </figcaption>
</figure>
```

## Ratios disponibles

| Classe | Ratio | Usage |
|--------|-------|-------|
| `fr-ratio-16x9` | 16:9 | Vidéo standard |
| `fr-ratio-4x3` | 4:3 | Vidéo ancienne |
| `fr-ratio-1x1` | 1:1 | Carré |
| `fr-ratio-3x2` | 3:2 | Photo |
| `fr-ratio-3x4` | 3:4 | Portrait |
| `fr-ratio-2x3` | 2:3 | Portrait allongé |
| `fr-ratio-32x9` | 32:9 | Panoramique |

## Image avec legende
```html
<figure class="fr-content-media" role="group" aria-label="Description de l'image">
    <div class="fr-content-media__img">
        <img class="fr-responsive-img" src="image.jpg" alt="Description alternative">
    </div>
    <figcaption class="fr-content-media__caption">
        Légende de l'image — Crédit : Photographe
    </figcaption>
</figure>
```

**Règles** :
- `title` obligatoire sur les `<iframe>` (WCAG 2.4.1)
- Utiliser `youtube-nocookie.com` pour les vidéos YouTube (RGPD)
- `alt` obligatoire sur les images, vide si décoratif (`alt=""`)

---
