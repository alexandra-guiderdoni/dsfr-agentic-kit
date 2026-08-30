# Patterns ARIA APG avances (priorite 3)

Fiches de reference pour les patterns WAI-ARIA APG avances. Ces widgets sont moins frequents que les priorites 1-2 mais presentent une complexite ARIA elevee. Chaque fiche suit le format standard du playbook.

**Source de verite** : [WAI-ARIA Authoring Practices Guide (APG)](https://www.w3.org/WAI/ARIA/apg/patterns/)

---

## Tree view

**Reference APG** : <https://www.w3.org/WAI/ARIA/apg/patterns/treeview/>

### Attributs aria requis

| Attribut | Element | Obligatoire | Detail |
|----------|---------|-------------|--------|
| `role="tree"` | Conteneur racine | Oui | Identifie le widget comme arborescence |
| `role="treeitem"` | Chaque noeud | Oui | Identifie un element de l'arborescence |
| `role="group"` | Conteneur de sous-noeuds | Oui | Groupe les enfants d'un noeud parent |
| `aria-expanded="true/false"` | Treeitem parent | Oui | Reflete l'etat ouvert/ferme du noeud |
| `aria-selected="true/false"` | Chaque treeitem | Si selection | Indique l'etat de selection |
| `aria-level` | Chaque treeitem | Recommande | Niveau de profondeur (1 = racine) |
| `aria-setsize` | Chaque treeitem | Recommande | Nombre de freres au meme niveau |
| `aria-posinset` | Chaque treeitem | Recommande | Position dans l'ensemble de freres |
| `aria-label` ou `aria-labelledby` | tree | Oui | Nom accessible de l'arborescence |

### Clavier requis (spec APG)

| Touche | Comportement |
|--------|-------------|
| ArrowDown | Focus sur le treeitem visible suivant |
| ArrowUp | Focus sur le treeitem visible precedent |
| ArrowRight | Noeud ferme : ouvre le noeud. Noeud ouvert : focus sur le premier enfant. Noeud terminal : rien |
| ArrowLeft | Noeud ouvert : ferme le noeud. Noeud ferme ou terminal : focus sur le parent |
| Home | Focus sur le premier treeitem de l'arborescence |
| End | Focus sur le dernier treeitem visible |
| Enter | Active le treeitem (action par defaut) |
| Space | Toggle la selection du treeitem (si multi-select) |
| \* (asterisque) | Ouvre tous les noeuds freres au meme niveau |
| Type-ahead | Focus sur le treeitem correspondant aux caracteres tapes |

### Gestion du focus

- Roving tabindex ou `aria-activedescendant` pour gerer le focus
- Tab place le focus sur le tree (sur le dernier treeitem actif si existant)
- Seuls les treeitems visibles (noeuds deplies) sont navigables
- ArrowDown/Up sautent les noeuds masques (enfants de noeuds fermes)

### Verification effective

- [ ] `role="tree"` sur le conteneur racine
- [ ] Chaque noeud a `role="treeitem"`, les sous-groupes ont `role="group"`
- [ ] ArrowDown/Up navigue entre les treeitems visibles (tester avec `press_key`)
- [ ] ArrowRight ouvre un noeud ferme (tester avec `press_key`)
- [ ] ArrowLeft ferme un noeud ouvert (tester avec `press_key`)
- [ ] `aria-expanded` reflete l'etat reel du noeud
- [ ] Home/End atteignent le premier/dernier treeitem visible (tester avec `press_key`)
- [ ] `aria-level` correct sur chaque treeitem

### Snippet de reference

```html
<ul role="tree" aria-label="Explorateur de fichiers">
  <li role="treeitem" aria-expanded="true" aria-level="1" aria-setsize="2" aria-posinset="1" tabindex="0">
    Documents
    <ul role="group">
      <li role="treeitem" aria-level="2" aria-setsize="2" aria-posinset="1" tabindex="-1">rapport.pdf</li>
      <li role="treeitem" aria-level="2" aria-setsize="2" aria-posinset="2" tabindex="-1">notes.txt</li>
    </ul>
  </li>
  <li role="treeitem" aria-expanded="false" aria-level="1" aria-setsize="2" aria-posinset="2" tabindex="-1">
    Images
    <ul role="group" hidden>
      <li role="treeitem" aria-level="2" aria-setsize="1" aria-posinset="1" tabindex="-1">photo.jpg</li>
    </ul>
  </li>
</ul>
```

```javascript
// Navigation clavier du tree view
const tree = document.querySelector('[role="tree"]');

function getVisibleItems() {
  return [...tree.querySelectorAll('[role="treeitem"]')].filter(item => {
    let parent = item.parentElement.closest('[role="treeitem"]');
    while (parent) {
      if (parent.getAttribute('aria-expanded') === 'false') return false;
      parent = parent.parentElement.closest('[role="treeitem"]');
    }
    return true;
  });
}

tree.addEventListener('keydown', (e) => {
  const items = getVisibleItems();
  const index = items.indexOf(document.activeElement);
  if (index === -1) return;
  const item = items[index];

  switch (e.key) {
    case 'ArrowDown': if (index < items.length - 1) items[index + 1].focus(); break;
    case 'ArrowUp': if (index > 0) items[index - 1].focus(); break;
    case 'ArrowRight': {
      if (item.getAttribute('aria-expanded') === 'false') {
        item.setAttribute('aria-expanded', 'true');
        item.querySelector('[role="group"]')?.removeAttribute('hidden');
      } else if (item.getAttribute('aria-expanded') === 'true') {
        getVisibleItems()[index + 1]?.focus();
      }
      break;
    }
    case 'ArrowLeft': {
      if (item.getAttribute('aria-expanded') === 'true') {
        item.setAttribute('aria-expanded', 'false');
        item.querySelector('[role="group"]')?.setAttribute('hidden', '');
      } else {
        item.parentElement.closest('[role="treeitem"]')?.focus();
      }
      break;
    }
    case 'Home': items[0].focus(); break;
    case 'End': items[items.length - 1].focus(); break;
    default: return;
  }
  e.preventDefault();
});
```

---

## Grid

**Reference APG** : <https://www.w3.org/WAI/ARIA/apg/patterns/grid/>

### Attributs aria requis

| Attribut | Element | Obligatoire | Detail |
|----------|---------|-------------|--------|
| `role="grid"` | Conteneur du tableau | Oui | Identifie le widget comme grille interactive |
| `role="row"` | Chaque ligne | Oui | Identifie une ligne de la grille |
| `role="gridcell"` | Chaque cellule | Oui | Identifie une cellule interactive |
| `role="rowheader"` | En-tete de ligne | Si applicable | Identifie l'en-tete de la ligne |
| `role="columnheader"` | En-tete de colonne | Si applicable | Identifie l'en-tete de la colonne |
| `aria-colindex` | gridcell | Si colonnes virtualisees | Index de colonne (base 1) |
| `aria-rowindex` | row | Si lignes virtualisees | Index de ligne (base 1) |
| `aria-selected="true/false"` | gridcell ou row | Si selection | Indique l'etat de selection |
| `aria-readonly` | grid ou gridcell | Si en lecture seule | Indique que la cellule n'est pas editable |
| `aria-label` ou `aria-labelledby` | grid | Oui | Nom accessible de la grille |

### Clavier requis (spec APG)

| Touche | Comportement |
|--------|-------------|
| ArrowRight | Focus sur la cellule suivante dans la ligne |
| ArrowLeft | Focus sur la cellule precedente dans la ligne |
| ArrowDown | Focus sur la cellule dans la ligne suivante (meme colonne) |
| ArrowUp | Focus sur la cellule dans la ligne precedente (meme colonne) |
| Home | Focus sur la premiere cellule de la ligne |
| End | Focus sur la derniere cellule de la ligne |
| Ctrl+Home | Focus sur la premiere cellule de la grille |
| Ctrl+End | Focus sur la derniere cellule de la grille |
| Page Down | Scroll d'un viewport vers le bas (si applicable) |
| Page Up | Scroll d'un viewport vers le haut (si applicable) |
| Enter / F2 | Passe en mode edition de la cellule (si editable) |
| Escape | Sort du mode edition, retour au mode navigation |

### Gestion du focus

- Navigation bidimensionnelle : le focus se deplace cellule par cellule dans les 4 directions
- `aria-activedescendant` ou roving tabindex pour gerer le focus
- Tab quitte la grille (ne navigue pas entre les cellules)
- Deux modes : navigation (fleches deplacent le focus) et edition (fleches deplacent le curseur dans la cellule)

### Verification effective

- [ ] `role="grid"` sur le conteneur, `role="row"` sur chaque ligne, `role="gridcell"` sur chaque cellule
- [ ] ArrowRight/Left navigue entre les cellules d'une ligne (tester avec `press_key`)
- [ ] ArrowDown/Up navigue entre les lignes sur la meme colonne (tester avec `press_key`)
- [ ] Home/End atteignent la premiere/derniere cellule de la ligne (tester avec `press_key`)
- [ ] Ctrl+Home/End atteignent la premiere/derniere cellule de la grille (tester avec `press_key`)
- [ ] Tab quitte la grille (ne reste pas piege dans les cellules)
- [ ] `aria-colindex` et `aria-rowindex` corrects si grille virtualisee

### Snippet de reference

```html
<table role="grid" aria-label="Employes">
  <thead>
    <tr role="row">
      <th role="columnheader">Nom</th>
      <th role="columnheader">Poste</th>
      <th role="columnheader">Service</th>
    </tr>
  </thead>
  <tbody>
    <tr role="row">
      <td role="gridcell" tabindex="0">Dupont</td>
      <td role="gridcell" tabindex="-1">Developpeur</td>
      <td role="gridcell" tabindex="-1">Technique</td>
    </tr>
    <tr role="row">
      <td role="gridcell" tabindex="-1">Martin</td>
      <td role="gridcell" tabindex="-1">Designer</td>
      <td role="gridcell" tabindex="-1">UX</td>
    </tr>
  </tbody>
</table>
```

```javascript
// Navigation clavier bidimensionnelle du grid
const grid = document.querySelector('[role="grid"]');
const rows = [...grid.querySelectorAll('[role="row"]')];
const cells = rows.map(row => [...row.querySelectorAll('[role="gridcell"], [role="columnheader"]')]);
let currentRow = 0, currentCol = 0;

grid.addEventListener('keydown', (e) => {
  let newRow = currentRow, newCol = currentCol;

  switch (e.key) {
    case 'ArrowRight': newCol = Math.min(currentCol + 1, cells[currentRow].length - 1); break;
    case 'ArrowLeft': newCol = Math.max(currentCol - 1, 0); break;
    case 'ArrowDown': newRow = Math.min(currentRow + 1, rows.length - 1); break;
    case 'ArrowUp': newRow = Math.max(currentRow - 1, 0); break;
    case 'Home': newCol = e.ctrlKey ? (newRow = 0, 0) : 0; break;
    case 'End': newCol = e.ctrlKey ? (newRow = rows.length - 1, cells[rows.length - 1].length - 1) : cells[currentRow].length - 1; break;
    default: return;
  }

  cells[currentRow][currentCol].setAttribute('tabindex', '-1');
  currentRow = newRow;
  currentCol = Math.min(newCol, cells[currentRow].length - 1);
  cells[currentRow][currentCol].setAttribute('tabindex', '0');
  cells[currentRow][currentCol].focus();
  e.preventDefault();
});
```

---

## Carousel

**Reference APG** : <https://www.w3.org/WAI/ARIA/apg/patterns/carousel/>

### Attributs aria requis

| Attribut | Element | Obligatoire | Detail |
|----------|---------|-------------|--------|
| `role="region"` ou `role="group"` | Conteneur du carousel | Oui | Identifie le widget comme region |
| `aria-roledescription="carousel"` | Conteneur du carousel | Oui | Identifie le type de widget pour les AT |
| `aria-label` | Conteneur du carousel | Oui | Nom accessible du carousel |
| `aria-live="off"` | Conteneur des slides | Si auto-rotation | Desactive les annonces pendant la rotation |
| `aria-live="polite"` | Conteneur des slides | Si navigation manuelle | Annonce les changements de slide |
| `aria-roledescription="slide"` | Chaque slide | Oui | Identifie chaque element comme slide |
| `aria-label` | Chaque slide | Oui | Nom accessible de la slide (ex: "1 sur 5") |

### Clavier requis (spec APG)

| Touche | Comportement |
|--------|-------------|
| Tab | Deplace le focus vers les controles du carousel (boutons precedent/suivant, pause) |
| Enter / Space | Active le bouton sous le focus (precedent, suivant, pause/play) |
| ArrowLeft / ArrowRight | Slide precedente / suivante (si les controles sont sous forme de tabs) |

### Auto-rotation et accessibilite (WCAG 2.2.2)

- L'auto-rotation **doit** etre pausable via un bouton visible
- L'auto-rotation **s'arrete** quand un element du carousel recoit le focus clavier
- L'auto-rotation **s'arrete** quand le pointeur survole le carousel
- L'auto-rotation **ne reprend jamais automatiquement** apres un arret — seule une action explicite de l'utilisateur peut la relancer
- `aria-live` passe de `"off"` (auto-rotation) a `"polite"` (navigation manuelle ou pause)

### Gestion du focus

- Les controles (precedent, suivant, pause) sont dans le flux de tabulation normal
- Le contenu de la slide active est accessible par Tab apres les controles
- Les slides inactives ne sont pas dans le flux de tabulation

### Verification effective

- [ ] `aria-roledescription="carousel"` sur le conteneur
- [ ] Chaque slide a `aria-roledescription="slide"` et un `aria-label`
- [ ] Bouton pause/play present et fonctionnel (tester avec `press_key`)
- [ ] L'auto-rotation s'arrete au focus clavier sur le carousel
- [ ] L'auto-rotation s'arrete au survol souris
- [ ] `aria-live` bascule correctement entre `"off"` et `"polite"`
- [ ] Les slides inactives ne recoivent pas le focus Tab

### Snippet de reference

```html
<div role="region" aria-roledescription="carousel" aria-label="Actualites">
  <button aria-label="Mettre en pause la rotation">Pause</button>
  <button aria-label="Slide precedente">Precedent</button>
  <button aria-label="Slide suivante">Suivant</button>
  <div aria-live="off">
    <div role="group" aria-roledescription="slide" aria-label="1 sur 3">
      <h3>Titre de la premiere actualite</h3>
      <p>Description de l'actualite...</p>
    </div>
    <div role="group" aria-roledescription="slide" aria-label="2 sur 3" hidden>
      <h3>Deuxieme actualite</h3>
    </div>
  </div>
</div>
```

```javascript
// Carousel avec gestion auto-rotation et aria-live
const carousel = document.querySelector('[aria-roledescription="carousel"]');
const slides = [...carousel.querySelectorAll('[aria-roledescription="slide"]')];
const liveRegion = carousel.querySelector('[aria-live]');
const btnPause = carousel.querySelector('[aria-label*="pause" i], [aria-label*="Pause" i]');
let currentSlide = 0, timer = null;

function afficherSlide(index) {
  slides.forEach((s, i) => { s.toggleAttribute('hidden', i !== index); });
  currentSlide = index;
}

function demarrerRotation() {
  liveRegion.setAttribute('aria-live', 'off');
  timer = setInterval(() => afficherSlide((currentSlide + 1) % slides.length), 5000);
}

function arreterRotation() {
  clearInterval(timer); timer = null;
  liveRegion.setAttribute('aria-live', 'polite');
}

// Arret au focus clavier et au survol (WCAG 2.2.2)
carousel.addEventListener('focusin', arreterRotation);
carousel.addEventListener('mouseenter', arreterRotation);

btnPause?.addEventListener('click', () => {
  if (timer) arreterRotation();
  else demarrerRotation();
});
```

---

## Alertdialog

**Reference APG** : <https://www.w3.org/WAI/ARIA/apg/patterns/alertdialog/>

### Attributs aria requis

| Attribut | Element | Obligatoire | Detail |
|----------|---------|-------------|--------|
| `role="alertdialog"` | Conteneur du dialog | Oui | Identifie le widget comme alertdialog |
| `aria-modal="true"` | Conteneur du dialog | Oui | Indique que le contenu arriere-plan est inerte |
| `aria-labelledby` | Conteneur du dialog | Oui | Reference le titre du dialog |
| `aria-describedby` | Conteneur du dialog | Oui | Reference le message descriptif |

### Difference avec Dialog

- Les technologies d'assistance peuvent donner un **traitement special** aux alertdialog (son systeme, annonce prioritaire, lecture immediate du contenu)
- Utilise pour les **actions irreversibles ou critiques** (suppression, deconnexion, perte de donnees)
- Le focus initial est **recommande sur l'action la moins destructive** (bonne pratique, non explicite dans la spec APG)

### Clavier requis (spec APG)

Le clavier est identique au pattern Dialog (Modal) :

| Touche | Comportement |
|--------|-------------|
| Tab | Focus sur le prochain element focusable dans le dialog (wrap) |
| Shift+Tab | Focus sur l'element focusable precedent dans le dialog (wrap) |
| Escape | Ferme le dialog (action non-destructive, equivale a Annuler) |

### Gestion du focus

- Le focus se deplace dans le dialog a l'ouverture
- **Bonne pratique** : placer le focus initial sur le bouton Annuler (ou l'action la moins destructive)
- Focus trap identique a Dialog : Tab/Shift+Tab wrap dans le dialog
- Le focus retourne au declencheur a la fermeture
- `inert` sur les elements freres quand le dialog est ouvert

### Verification effective

- [ ] `role="alertdialog"` (et non `role="dialog"`) sur le conteneur
- [ ] `aria-modal="true"` present
- [ ] `aria-labelledby` reference le titre, `aria-describedby` reference le message
- [ ] Tab/Shift+Tab wrap dans le dialog (tester avec `press_key`)
- [ ] Escape ferme le dialog sans executer l'action destructive (tester avec `press_key`)
- [ ] Le focus initial est sur l'action la moins destructive (Annuler)
- [ ] Le focus retourne au declencheur apres fermeture

### Snippet de reference

```html
<div role="alertdialog" aria-modal="true" aria-labelledby="titre-alerte" aria-describedby="desc-alerte">
  <h2 id="titre-alerte">Supprimer le compte</h2>
  <p id="desc-alerte">Cette action est irreversible. Toutes vos donnees seront supprimees definitivement.</p>
  <button id="btn-annuler-alerte">Annuler</button>
  <button id="btn-supprimer">Supprimer definitivement</button>
</div>
```

```javascript
// Alertdialog avec focus sur l'action la moins destructive
function ouvrirAlertDialog(dialog, declencheur) {
  dialog._declencheur = declencheur;

  document.querySelectorAll('body > *:not([role="alertdialog"])').forEach(el => {
    el.setAttribute('inert', '');
  });

  dialog.removeAttribute('hidden');

  // Focus sur Annuler (action la moins destructive)
  const btnAnnuler = dialog.querySelector('[id*="annuler"], button:first-of-type');
  if (btnAnnuler) btnAnnuler.focus();

  dialog.addEventListener('keydown', function piegerFocus(e) {
    if (e.key === 'Escape') { fermerAlertDialog(dialog); return; }
    if (e.key !== 'Tab') return;

    const focusables = [...dialog.querySelectorAll('button, [href], input, [tabindex]:not([tabindex="-1"])')];
    const premier = focusables[0], dernier = focusables[focusables.length - 1];

    if (e.shiftKey && document.activeElement === premier) { dernier.focus(); e.preventDefault(); }
    else if (!e.shiftKey && document.activeElement === dernier) { premier.focus(); e.preventDefault(); }
  });
}

function fermerAlertDialog(dialog) {
  dialog.setAttribute('hidden', '');
  document.querySelectorAll('[inert]').forEach(el => el.removeAttribute('inert'));
  if (dialog._declencheur) dialog._declencheur.focus();
}
```
