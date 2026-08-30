# Tableaux

Référence extraite de `../content-media.md`.

---

## Tableau simple
```html
<div class="fr-table" id="table-1">
    <div class="fr-table__wrapper">
        <div class="fr-table__container">
            <div class="fr-table__content">
                <table id="table-1-table">
                    <caption>Titre du tableau</caption>
                    <thead>
                        <tr>
                            <th scope="col">En-tête 1</th>
                            <th scope="col">En-tête 2</th>
                            <th scope="col">En-tête 3</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr>
                            <td>Donnée 1</td>
                            <td>Donnée 2</td>
                            <td>Donnée 3</td>
                        </tr>
                    </tbody>
                </table>
            </div>
        </div>
    </div>
</div>
```
**Note** : La structure `fr-table__wrapper > fr-table__container > fr-table__content` est obligatoire pour le défilement horizontal responsive.

## Tableau avec en-tête de ligne
```html
<tr>
    <th scope="row">Libellé de ligne</th>
    <td>Donnée 1</td>
    <td>Donnée 2</td>
</tr>
```

## Variantes de tableau
- `fr-table--bordered` : Bordures sur toutes les cellules
- `fr-table--no-scroll` : Désactive le défilement horizontal
- `fr-table--layout-fixed` : Colonnes de largeur fixe
- `fr-table--no-caption` : Masque visuellement le caption (reste accessible)

---
