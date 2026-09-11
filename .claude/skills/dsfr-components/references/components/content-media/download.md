# Téléchargement (Download)

Référence extraite de `../content-media.md`.

---

**Composant déprécié en DSFR 1.15.3.** Le paquet officiel ne sert plus ce
markup que sous `example/component/download/deprecated/`. La fonctionnalité
« téléchargement de fichier » est désormais portée par deux composants
courants :

- la carte de téléchargement `fr-card--download`, voir
  [`content-media/cards.md`](cards.md) ;
- le lien de téléchargement, voir [`navigation/link.md`](../navigation/link.md).

Préférer ces deux composants pour tout nouveau service. La structure ci-dessous
reste documentée pour la maintenance de l'existant.

## Lien de téléchargement simple
```html
<div class="fr-download">
    <h3>
        <a download href="document.pdf" class="fr-download__link">
            Télécharger le document
            <span class="fr-download__detail">PDF — 1,2 Mo</span>
        </a>
    </h3>
</div>
```

## Groupe de téléchargements
```html
<div class="fr-downloads-group">
    <p class="fr-downloads-group__title">Documents à télécharger</p>
    <ul>
        <li>
            <div class="fr-download">
                <h3>
                    <a download href="rapport.pdf" class="fr-download__link">
                        Rapport annuel 2025
                        <span class="fr-download__detail">PDF — 3,4 Mo</span>
                    </a>
                </h3>
            </div>
        </li>
        <li>
            <div class="fr-download">
                <h3>
                    <a download href="annexe.xlsx" class="fr-download__link">
                        Annexe statistique
                        <span class="fr-download__detail">XLSX — 512 Ko</span>
                    </a>
                </h3>
            </div>
        </li>
    </ul>
</div>
```

**Règles** :
- L'attribut `download` sur le `<a>` force le téléchargement au lieu de
  l'ouverture dans le navigateur
- Le `<ul>` entre `fr-downloads-group` et chaque `fr-download` est requis : le
  CSS officiel ne stylise le groupe que par `.fr-downloads-group > ul` et
  `.fr-downloads-group > ul > li`
- Le niveau de titre `<h3>` est celui de l'exemple officiel ; l'adapter à la
  hiérarchie réelle de la page

**Note** : le titre de groupe `fr-downloads-group__title` n'existe en 1.15.3 que dans le gabarit déprécié du composant (`src/dsfr/component/download/deprecated/`) ; le générateur ne l'émet pas, à dessein. Détail historique : `generate_component.py download` pose bien le conteneur
`fr-download` autour du lien, en mode simple comme en mode `items`, mais place
le `<a class="fr-download__link">` sans le `<h3>` de l'exemple officiel, et le
mode `items` n'émet pas de `fr-downloads-group__title`. Ajouter le titre du
lien et celui du groupe à la main sur la sortie du générateur.

---
