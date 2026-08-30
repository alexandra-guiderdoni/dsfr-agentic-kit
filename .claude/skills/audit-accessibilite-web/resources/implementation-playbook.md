# Playbook d'implementation - Audit d'accessibilite web

Patterns, checklists et extraits de code pour les audits WCAG 2.2. Ce playbook combine tests automatises, checklist exhaustive par critere WCAG et patterns de remediation.

## Outils de scan automatise

### Ligne de commande

```bash
# axe-core en ligne de commande
npx @axe-core/cli https://example.com --tags wcag2a,wcag2aa

# pa11y (audit WCAG AA)
npx pa11y https://example.com --standard WCAG2AA

# Lighthouse accessibilite
lighthouse https://example.com --only-categories=accessibility --output json
```

### Test de composant avec jest-axe

```javascript
import { render } from "@testing-library/react";
import { axe, toHaveNoViolations } from "jest-axe";
expect.extend(toHaveNoViolations);

it("ne doit avoir aucune violation", async () => {
  const { container } = render(<MonComposant />);
  expect(await axe(container)).toHaveNoViolations();
});
```

### Integration axe-core en JavaScript

```javascript
const axe = require('axe-core');

async function lancerAuditAccessibilite(page) {
  await page.addScriptTag({ path: require.resolve('axe-core') });

  const resultats = await page.evaluate(async () => {
    return await axe.run(document, {
      runOnly: {
        type: 'tag',
        values: ['wcag2a', 'wcag2aa', 'wcag21aa', 'wcag22aa']
      }
    });
  });

  return {
    violations: resultats.violations,
    reussites: resultats.passes,
    incomplets: resultats.incomplete
  };
}
```

### Exemple de test Playwright

```javascript
test('ne doit avoir aucune violation d accessibilite', async ({ page }) => {
  await page.goto('/');
  const resultats = await lancerAuditAccessibilite(page);

  expect(resultats.violations).toHaveLength(0);
});
```

## Seuils de contraste WCAG

| Niveau | Texte normal | Texte agrandi (18pt+) | Composants UI |
|--------|-------------|----------------------|---------------|
| AA     | 4.5:1       | 3:1                  | 3:1           |
| AAA    | 7:1         | 4.5:1                | 3:1           |

Outils : WebAIM Contrast Checker, axe DevTools.

```css
/* Support du mode contraste eleve */
@media (prefers-contrast: high) {
  a { text-decoration: underline !important; }
  button, input { border: 2px solid #000 !important; }
}
```

## Checklist WCAG par principe POUR

### Concepts fondamentaux

```text
Niveaux de conformite :
  A    — Accessibilite minimale (base legale)
  AA   — Conformite standard (la plupart des normes)
  AAA  — Accessibilite renforcee (besoins specialises)

Violations courantes par impact :
  Critique (bloquant) :
  ├── Texte alternatif manquant sur les images fonctionnelles
  ├── Pas d'acces clavier aux elements interactifs
  ├── Labels de formulaire manquants
  └── Medias en lecture automatique sans controles

  Serieux :
  ├── Contraste de couleur insuffisant
  ├── Liens d'evitement manquants
  ├── Widgets personnalises inaccessibles
  └── Titres de page manquants

  Modere :
  ├── Attribut de langue manquant
  ├── Texte de lien ambigu
  ├── Landmarks manquants
  └── Hierarchie de titres incorrecte
```

## Perceptible (principe 1)

### 1.1 Alternatives textuelles

#### 1.1.1 Contenu non textuel (niveau A)

- [ ] Toutes les images ont un texte alternatif
- [ ] Les images decoratives ont alt=""
- [ ] Les images complexes ont des descriptions longues
- [ ] Les icones significatives ont des noms accessibles
- [ ] Les CAPTCHAs ont des alternatives

```html
<!-- Bon -->
<img src="graphique.png" alt="Les ventes ont augmente de 25% du T1 au T2" />
<img src="ligne-decorative.png" alt="" />

<!-- Mauvais -->
<img src="graphique.png" />
<img src="ligne-decorative.png" alt="ligne decorative" />
```

### 1.2 Medias temporels

#### 1.2.1 Audio seul et video seule (niveau A)

- [ ] L'audio a une transcription textuelle
- [ ] La video a une audio-description ou transcription

#### 1.2.2 Sous-titres (niveau A)

- [ ] Toutes les videos ont des sous-titres synchronises
- [ ] Les sous-titres sont precis et complets
- [ ] L'identification du locuteur est incluse

#### 1.2.3 Audio-description (niveau A)

- [ ] La video a une audio-description pour le contenu visuel

### 1.3 Adaptable

#### 1.3.1 Information et relations (niveau A)

- [ ] Les titres utilisent les balises appropriees (h1-h6)
- [ ] Les listes utilisent ul/ol/dl
- [ ] Les tableaux ont des en-tetes
- [ ] Les champs de formulaire ont des labels
- [ ] Les landmarks ARIA sont presents

```html
<!-- Hierarchie des titres -->
<h1>Titre de la page</h1>
<h2>Section</h2>
<h3>Sous-section</h3>
<h2>Autre section</h2>

<!-- En-tetes de tableau -->
<table>
  <thead>
    <tr>
      <th scope="col">Nom</th>
      <th scope="col">Prix</th>
    </tr>
  </thead>
</table>
```

#### 1.3.2 Ordre significatif (niveau A)

- [ ] L'ordre de lecture est logique
- [ ] Le positionnement CSS ne casse pas l'ordre
- [ ] L'ordre du focus correspond a l'ordre visuel

#### 1.3.3 Caracteristiques sensorielles (niveau A)

- [ ] Les instructions ne reposent pas uniquement sur la forme/couleur
- [ ] "Cliquez sur le bouton rouge" devient "Cliquez sur Valider (bouton rouge)"

### 1.4 Distinguable

#### 1.4.1 Utilisation de la couleur (niveau A)

- [ ] La couleur n'est pas le seul moyen de transmettre l'information
- [ ] Les liens sont distinguables sans la couleur
- [ ] Les etats d'erreur ne dependent pas uniquement de la couleur

#### 1.4.3 Contraste minimum (niveau AA)

- [ ] Texte : ratio de contraste 4.5:1
- [ ] Texte agrandi (18pt+) : ratio 3:1
- [ ] Composants d'interface : ratio 3:1

#### 1.4.4 Redimensionnement du texte (niveau AA)

- [ ] Le texte se redimensionne a 200% sans perte
- [ ] Pas de defilement horizontal a 320px
- [ ] Le contenu se reorganise correctement

#### 1.4.10 Redistribution (niveau AA)

- [ ] Le contenu se redistribue a 400% de zoom
- [ ] Pas de defilement bidimensionnel
- [ ] Tout le contenu accessible a 320px de largeur

#### 1.4.11 Contraste des elements non textuels (niveau AA)

- [ ] Les composants d'interface ont un contraste de 3:1
- [ ] Les indicateurs de focus sont visibles
- [ ] Les objets graphiques sont distinguables

#### 1.4.12 Espacement du texte (niveau AA)

- [ ] Pas de perte de contenu avec un espacement augmente
- [ ] Hauteur de ligne 1.5x la taille de police
- [ ] Espacement des paragraphes 2x la taille de police
- [ ] Espacement des lettres 0.12x la taille de police
- [ ] Espacement des mots 0.16x la taille de police

## Utilisable (principe 2)

### 2.1 Accessible au clavier

#### 2.1.1 Clavier (niveau A)

- [ ] Toutes les fonctionnalites sont accessibles au clavier
- [ ] Pas de pieges clavier
- [ ] L'ordre de tabulation est logique
- [ ] Les widgets personnalises sont utilisables au clavier

```javascript
// Un bouton personnalise doit etre accessible au clavier
<div role="button" tabindex="0"
     onkeydown="if(event.key === 'Enter' || event.key === ' ') activate()">
```

#### 2.1.2 Pas de piege clavier (niveau A)

- [ ] Le focus peut quitter tous les composants
- [ ] Les modales capturent correctement le focus
- [ ] Le focus revient apres la fermeture d'une modale

### 2.2 Delai suffisant

#### 2.2.1 Delai ajustable (niveau A)

- [ ] Les delais de session peuvent etre prolonges
- [ ] L'utilisateur est prevenu avant l'expiration
- [ ] Option pour desactiver le rafraichissement automatique

#### 2.2.2 Pause, arret, masquage (niveau A)

- [ ] Le contenu en mouvement peut etre mis en pause
- [ ] Le contenu mis a jour automatiquement peut etre mis en pause
- [ ] Les animations respectent prefers-reduced-motion

```css
@media (prefers-reduced-motion: reduce) {
  * {
    animation: none !important;
    transition: none !important;
  }
}
```

### 2.3 Crises et reactions physiques

#### 2.3.1 Trois flashs (niveau A)

- [ ] Aucun contenu ne clignote plus de 3 fois/seconde
- [ ] La zone de clignotement est petite (<25% du viewport)

### 2.4 Navigable

#### 2.4.1 Contourner les blocs (niveau A)

- [ ] Lien d'evitement vers le contenu principal present
- [ ] Regions landmark definies
- [ ] Structure de titres correcte

```html
<a href="#main" class="skip-link">Aller au contenu principal</a>
<main id="main">...</main>
```

#### 2.4.2 Titre de page (niveau A)

- [ ] Titres de page uniques et descriptifs
- [ ] Le titre reflete le contenu de la page

#### 2.4.3 Ordre du focus (niveau A)

- [ ] L'ordre du focus correspond a l'ordre visuel
- [ ] tabindex utilise correctement

#### 2.4.4 Fonction du lien dans le contexte (niveau A)

- [ ] Les liens sont comprehensibles hors contexte
- [ ] Pas de "cliquez ici" ou "en savoir plus" seuls

```html
<!-- Mauvais -->
<a href="rapport.pdf">Cliquez ici</a>

<!-- Bon -->
<a href="rapport.pdf">Telecharger le rapport des ventes T4 (PDF)</a>
```

#### 2.4.6 Titres et labels (niveau AA)

- [ ] Les titres decrivent le contenu
- [ ] Les labels decrivent la fonction

#### 2.4.7 Focus visible (niveau AA)

- [ ] L'indicateur de focus est visible sur tous les elements
- [ ] Les styles de focus personnalises respectent le contraste

```css
:focus-visible {
  outline: 3px solid #005fcc;
  outline-offset: 2px;
}
```

#### 2.4.11 Focus non masque (niveau AA) - WCAG 2.2

- [ ] L'element en focus n'est pas entierement cache
- [ ] Les en-tetes fixes ne masquent pas le focus

## Comprehensible (principe 3)

### 3.1 Lisible

#### 3.1.1 Langue de la page (niveau A)

- [ ] Attribut HTML lang defini
- [ ] Langue correcte pour le contenu

```html
<html lang="fr">
```

#### 3.1.2 Langue des parties (niveau AA)

- [ ] Les changements de langue sont indiques

```html
<p>Le mot anglais <span lang="en">hello</span> signifie bonjour.</p>
```

### 3.2 Previsible

#### 3.2.1 Au focus (niveau A)

- [ ] Pas de changement de contexte au focus seul
- [ ] Pas de popups inattendues au focus

#### 3.2.2 A la saisie (niveau A)

- [ ] Pas de soumission automatique de formulaire
- [ ] L'utilisateur est prevenu avant un changement de contexte

#### 3.2.3 Navigation coherente (niveau AA)

- [ ] Navigation coherente entre les pages
- [ ] Composants repetes dans le meme ordre

#### 3.2.4 Identification coherente (niveau AA)

- [ ] Meme fonctionnalite = meme label
- [ ] Icones utilisees de maniere coherente

### 3.3 Assistance a la saisie

#### 3.3.1 Identification des erreurs (niveau A)

- [ ] Les erreurs sont clairement identifiees
- [ ] Le message d'erreur decrit le probleme
- [ ] L'erreur est liee au champ

```html
<input aria-describedby="email-erreur" aria-invalid="true" />
<span id="email-erreur" role="alert">Veuillez saisir un email valide</span>
```

#### 3.3.2 Labels ou instructions (niveau A)

- [ ] Tous les champs ont des labels visibles
- [ ] Les champs obligatoires sont indiques
- [ ] Les indications de format sont fournies

#### 3.3.3 Suggestion d'erreur (niveau AA)

- [ ] Les erreurs incluent une suggestion de correction
- [ ] Les suggestions sont specifiques

#### 3.3.4 Prevention des erreurs (niveau AA)

- [ ] Les formulaires juridiques/financiers sont reversibles
- [ ] Les donnees sont verifiees avant soumission
- [ ] L'utilisateur peut relire avant de soumettre

## Robuste (principe 4)

### 4.1 Compatible

#### 4.1.1 Analyse syntaxique (niveau A) - obsolete dans WCAG 2.2

- [ ] HTML valide (bonne pratique)
- [ ] Pas d'IDs dupliques
- [ ] Balises ouvrantes/fermantes completes

#### 4.1.2 Nom, role, valeur (niveau A)

- [ ] Les widgets personnalises ont des noms accessibles
- [ ] Les roles ARIA sont corrects
- [ ] Les changements d'etat sont annonces

```html
<!-- Case a cocher personnalisee accessible -->
<div role="checkbox"
     aria-checked="false"
     tabindex="0"
     aria-labelledby="label">
</div>
<span id="label">Accepter les conditions</span>
```

#### 4.1.3 Messages de statut (niveau AA)

- [ ] Les mises a jour de statut sont annoncees
- [ ] Les regions live sont utilisees correctement

```html
<div role="status" aria-live="polite">3 articles ajoutes au panier</div>

<div role="alert" aria-live="assertive">Erreur : la soumission du formulaire a echoue</div>
```

## Modeles essentiels aria (patterns APG)

Les fiches ci-dessous sont derivees de la [WAI-ARIA Authoring Practices Guide (APG)](https://www.w3.org/WAI/ARIA/apg/patterns/). Toujours consulter la spec APG comme source de verite pour les interactions clavier.

Pour les patterns avances (Tree view, Grid, Carousel, Alertdialog), lire `resources/aria-patterns-avances.md`.

### Dialog (Modal)

**Reference APG** : <https://www.w3.org/WAI/ARIA/apg/patterns/dialog-modal/>

#### Attributs aria requis

| Attribut | Element | Obligatoire | Detail |
|----------|---------|-------------|--------|
| `role="dialog"` | Conteneur du dialog | Oui | Identifie le widget comme dialog |
| `aria-modal="true"` | Conteneur du dialog | Oui | Indique aux technologies d'assistance que le contenu en arriere-plan est inerte |
| `aria-label` ou `aria-labelledby` | Conteneur du dialog | Oui | Nom accessible du dialog |
| `aria-describedby` | Conteneur du dialog | Non | Reference au contenu descriptif du dialog |
| `inert` | Elements freres du dialog | Recommande | Empeche l'interaction avec l'arriere-plan (complement a aria-modal) |

#### Clavier requis (spec APG)

| Touche | Comportement attendu |
|--------|---------------------|
| Tab | Deplace le focus vers le prochain element focusable dans le dialog. Si le focus est sur le dernier element, retour au premier (wrap) |
| Shift+Tab | Deplace le focus vers l'element focusable precedent dans le dialog. Si le focus est sur le premier element, retour au dernier (wrap) |
| Escape | Ferme le dialog |

#### Gestion du focus

- Le focus se deplace dans le dialog a l'ouverture (premier element focusable ou element le plus pertinent)
- Le focus retourne au declencheur a la fermeture
- Focus trap : Tab/Shift+Tab wrap dans le dialog (le focus ne sort jamais)

#### Verification effective pour NVDA

- [ ] `aria-modal="true"` present sur le conteneur `role="dialog"`
- [ ] Attribut `inert` sur les elements freres quand le dialog est ouvert
- [ ] Tab depuis le dernier element focusable retourne au premier (tester avec `press_key`)
- [ ] Shift+Tab depuis le premier element focusable retourne au dernier (tester avec `press_key`)
- [ ] Escape ferme le dialog et retourne le focus au declencheur (tester avec `press_key`)
- [ ] Le curseur virtuel NVDA ne sort pas du dialog (necessite `aria-modal="true"`)

#### Snippet de reference

```html
<div role="dialog" aria-modal="true" aria-labelledby="titre-dialog" aria-describedby="desc-dialog">
  <h2 id="titre-dialog">Confirmer la suppression</h2>
  <p id="desc-dialog">Cette action est irreversible.</p>
  <button id="btn-annuler">Annuler</button>
  <button id="btn-confirmer">Supprimer</button>
</div>
```

```javascript
function ouvrirDialog(dialog, declencheur) {
  // Sauvegarder le declencheur pour restaurer le focus
  dialog._declencheur = declencheur;

  // Rendre l'arriere-plan inerte
  document.querySelectorAll('body > *:not([role="dialog"])').forEach(el => {
    el.setAttribute('inert', '');
  });

  dialog.removeAttribute('hidden');

  // Focus sur le premier element focusable (ou le plus pertinent)
  const focusables = dialog.querySelectorAll(
    'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
  );
  if (focusables.length) focusables[0].focus();

  // Focus trap
  dialog.addEventListener('keydown', function piegerFocus(e) {
    if (e.key === 'Escape') {
      fermerDialog(dialog);
      return;
    }
    if (e.key !== 'Tab') return;

    const premier = focusables[0];
    const dernier = focusables[focusables.length - 1];

    if (e.shiftKey && document.activeElement === premier) {
      dernier.focus();
      e.preventDefault();
    } else if (!e.shiftKey && document.activeElement === dernier) {
      premier.focus();
      e.preventDefault();
    }
  });
}

function fermerDialog(dialog) {
  dialog.setAttribute('hidden', '');

  // Retirer inert de l'arriere-plan
  document.querySelectorAll('[inert]').forEach(el => {
    el.removeAttribute('inert');
  });

  // Restaurer le focus au declencheur
  if (dialog._declencheur) dialog._declencheur.focus();
}
```

### Combobox avec popup dialog

**Reference APG** : <https://www.w3.org/WAI/ARIA/apg/patterns/combobox/>

#### Attributs aria requis sur le trigger

| Attribut | Detail |
|----------|--------|
| `role="combobox"` | Identifie le widget comme combobox (ou justification si `button` utilise) |
| `aria-haspopup="dialog"` | Indique que le popup est un dialog (variante dialog du combobox) |
| `aria-expanded="true/false"` | Reflete l'etat ouvert/ferme du popup |
| `aria-controls="id-popup"` | Reference le conteneur du popup |
| `aria-labelledby` | Nom accessible du combobox |
| `aria-describedby` | Description ou instructions complementaires |
| `aria-activedescendant` | Reference l'option active dans la liste (si applicable) |

#### Clavier requis sur le trigger (spec APG)

| Touche | Popup ferme | Popup ouvert |
|--------|-------------|--------------|
| ArrowDown | Ouvre le popup et deplace le focus dans le popup | Deplace le focus vers l'option suivante |
| ArrowUp | Ouvre le popup et deplace le focus sur la derniere option | Deplace le focus vers l'option precedente |
| Enter | Ouvre le popup | Selectionne l'option active et ferme le popup |
| Space | Ouvre le popup | Depend du contexte (toggle selection si listbox) |
| Escape | - | Ferme le popup et retourne le focus au trigger |
| Alt+ArrowDown | Ouvre le popup sans deplacer le focus | - |
| Alt+ArrowUp | - | Ferme le popup et retourne le focus au trigger |
| Home | - | Deplace le focus vers la premiere option |
| End | - | Deplace le focus vers la derniere option |

#### Clavier dans le popup dialog

Le popup dialog suit le pattern Dialog (Modal) ci-dessus. Touches supplementaires si le dialog contient une listbox :

| Touche | Comportement |
|--------|-------------|
| ArrowDown/ArrowUp | Navigation entre les options de la liste |
| Home/End | Premiere/derniere option |
| Space | Toggle la selection de l'option active |

#### Verification effective

- [ ] `role="combobox"` sur le trigger (ou justification documentee si `button` utilise)
- [ ] `aria-expanded` reflete l'etat reel du popup
- [ ] Fleche bas ouvre le popup (tester avec `press_key` sur trigger ferme)
- [ ] Enter ouvre le popup (tester avec `press_key` sur trigger ferme)
- [ ] Escape ferme le popup et retourne le focus au trigger (tester avec `press_key` dans le dialog)
- [ ] Le popup respecte le pattern Dialog (Modal) ci-dessus
- [ ] Navigation interne avec fleches, Home/End si listbox presente

#### Snippet de reference

```html
<div class="combobox-container">
  <label id="label-date">Date de debut</label>
  <button role="combobox"
          aria-haspopup="dialog"
          aria-expanded="false"
          aria-controls="popup-calendrier"
          aria-labelledby="label-date"
          id="trigger-date">
    Choisir une date
  </button>
  <div id="popup-calendrier"
       role="dialog"
       aria-modal="true"
       aria-label="Calendrier"
       hidden>
    <!-- Contenu du calendrier / listbox -->
    <div role="listbox" aria-label="Options disponibles">
      <div role="option" id="opt-1" aria-selected="false">Option 1</div>
      <div role="option" id="opt-2" aria-selected="false">Option 2</div>
    </div>
    <button>Valider</button>
  </div>
</div>
```

```javascript
class ComboboxDialog {
  constructor(trigger, popup) {
    this.trigger = trigger;
    this.popup = popup;
    this.options = popup.querySelectorAll('[role="option"]');
    this.activeIndex = -1;

    this.trigger.addEventListener('keydown', (e) => this.onTriggerKeydown(e));
    this.popup.addEventListener('keydown', (e) => this.onPopupKeydown(e));
  }

  onTriggerKeydown(e) {
    const estOuvert = this.trigger.getAttribute('aria-expanded') === 'true';

    switch (e.key) {
      case 'ArrowDown':
        if (!estOuvert) this.ouvrir();
        if (!e.altKey) this.focusOption(0);
        e.preventDefault();
        break;
      case 'ArrowUp':
        if (!estOuvert) this.ouvrir();
        if (!e.altKey) this.focusOption(this.options.length - 1);
        e.preventDefault();
        break;
      case 'Enter':
      case ' ':
        if (!estOuvert) this.ouvrir();
        e.preventDefault();
        break;
    }
  }

  onPopupKeydown(e) {
    switch (e.key) {
      case 'ArrowDown':
        this.focusOption(Math.min(this.activeIndex + 1, this.options.length - 1));
        e.preventDefault();
        break;
      case 'ArrowUp':
        this.focusOption(Math.max(this.activeIndex - 1, 0));
        e.preventDefault();
        break;
      case 'Home':
        this.focusOption(0);
        e.preventDefault();
        break;
      case 'End':
        this.focusOption(this.options.length - 1);
        e.preventDefault();
        break;
      case 'Escape':
        this.fermer();
        e.preventDefault();
        break;
      case 'Enter':
        this.selectionner();
        e.preventDefault();
        break;
    }
  }

  ouvrir() {
    this.trigger.setAttribute('aria-expanded', 'true');
    this.popup.removeAttribute('hidden');
  }

  fermer() {
    this.trigger.setAttribute('aria-expanded', 'false');
    this.popup.setAttribute('hidden', '');
    this.trigger.focus();
  }

  focusOption(index) {
    if (index < 0 || index >= this.options.length) return;
    this.activeIndex = index;
    this.options[index].focus();
  }

  selectionner() {
    if (this.activeIndex >= 0) {
      this.trigger.textContent = this.options[this.activeIndex].textContent;
    }
    this.fermer();
  }
}
```

### Onglets (Tabs)

**Reference APG** : <https://www.w3.org/WAI/ARIA/apg/patterns/tabs/>

#### Attributs aria requis

| Attribut | Element | Obligatoire | Detail |
|----------|---------|-------------|--------|
| `role="tablist"` | Conteneur des onglets | Oui | Identifie le groupe d'onglets |
| `aria-label` ou `aria-labelledby` | tablist | Oui | Nom accessible du groupe |
| `aria-orientation` | tablist | Non | `"horizontal"` (defaut) ou `"vertical"` |
| `role="tab"` | Chaque onglet | Oui | Identifie l'element comme onglet |
| `aria-selected="true/false"` | Chaque tab | Oui | Indique l'onglet actif |
| `aria-controls` | Chaque tab | Oui | Reference le tabpanel associe |
| `tabindex="-1"` | Tabs inactifs | Oui | Roving tabindex : seul l'actif a `tabindex="0"` |
| `role="tabpanel"` | Chaque panneau | Oui | Identifie le panneau de contenu |
| `aria-labelledby` | Chaque tabpanel | Oui | Reference le tab associe |

#### Clavier requis (spec APG)

| Touche | Comportement |
|--------|-------------|
| ArrowRight | Onglet suivant (wrap au premier si dernier) |
| ArrowLeft | Onglet precedent (wrap au dernier si premier) |
| Home | Premier onglet |
| End | Dernier onglet |
| Tab | Quitte le tablist vers le tabpanel actif |
| Shift+Tab | Depuis le tabpanel, retour a l'onglet actif |
| ArrowDown/ArrowUp | Remplace ArrowRight/Left si `aria-orientation="vertical"` |

Deux modes d'activation existent :

- **Automatique** : l'onglet s'active au focus (ArrowRight active directement le panneau)
- **Manuel** : l'onglet recoit le focus, Enter/Space necessaire pour l'activer

#### Gestion du focus

- Roving tabindex : seul l'onglet actif a `tabindex="0"`, les autres ont `tabindex="-1"`
- Tab depuis l'exterieur place le focus sur l'onglet actif (pas le premier)
- Tab depuis l'onglet actif deplace le focus dans le tabpanel
- ArrowRight/Left deplacent le focus ET changent `aria-selected` (mode automatique)
- Le panneau actif est visible, les autres sont masques (`hidden`)

#### Verification effective

- [ ] `role="tablist"` present sur le conteneur
- [ ] Chaque onglet a `role="tab"` et `aria-controls` pointant vers son panneau
- [ ] Un seul onglet a `aria-selected="true"` a la fois
- [ ] Les onglets inactifs ont `tabindex="-1"` (roving tabindex)
- [ ] Fleche droite deplace le focus et active l'onglet suivant (tester avec `press_key`)
- [ ] Fleche gauche deplace le focus et active l'onglet precedent (tester avec `press_key`)
- [ ] Home/End atteignent le premier/dernier onglet (tester avec `press_key`)
- [ ] Tab depuis le tablist deplace le focus dans le tabpanel
- [ ] Le panneau affiche correspond a l'onglet actif

#### Snippet de reference

```html
<div role="tablist" aria-label="Informations produit">
  <button role="tab" id="onglet-1" aria-selected="true" aria-controls="panneau-1" tabindex="0">
    Description
  </button>
  <button role="tab" id="onglet-2" aria-selected="false" aria-controls="panneau-2" tabindex="-1">
    Avis
  </button>
  <button role="tab" id="onglet-3" aria-selected="false" aria-controls="panneau-3" tabindex="-1">
    Specifications
  </button>
</div>
<div role="tabpanel" id="panneau-1" aria-labelledby="onglet-1">
  Contenu de la description...
</div>
<div role="tabpanel" id="panneau-2" aria-labelledby="onglet-2" hidden>
  Contenu des avis...
</div>
<div role="tabpanel" id="panneau-3" aria-labelledby="onglet-3" hidden>
  Contenu des specifications...
</div>
```

```javascript
// Navigation clavier des onglets avec roving tabindex
class TabsAccessibles {
  constructor(tablist) {
    this.tablist = tablist;
    this.tabs = [...tablist.querySelectorAll('[role="tab"]')];
    this.panneaux = this.tabs.map(tab =>
      document.getElementById(tab.getAttribute('aria-controls'))
    );

    this.tablist.addEventListener('keydown', (e) => this.onKeydown(e));
    this.tabs.forEach(tab => tab.addEventListener('click', () => this.activer(tab)));
  }

  onKeydown(e) {
    const index = this.tabs.indexOf(document.activeElement);
    if (index === -1) return;

    let nouvelIndex;
    switch (e.key) {
      case 'ArrowRight':
        nouvelIndex = (index + 1) % this.tabs.length;
        break;
      case 'ArrowLeft':
        nouvelIndex = (index - 1 + this.tabs.length) % this.tabs.length;
        break;
      case 'Home':
        nouvelIndex = 0;
        break;
      case 'End':
        nouvelIndex = this.tabs.length - 1;
        break;
      default:
        return;
    }

    this.activer(this.tabs[nouvelIndex]);
    e.preventDefault();
  }

  activer(tab) {
    // Desactiver tous les onglets (roving tabindex)
    this.tabs.forEach((t, i) => {
      t.setAttribute('aria-selected', 'false');
      t.setAttribute('tabindex', '-1');
      this.panneaux[i].setAttribute('hidden', '');
    });

    // Activer l'onglet cible
    const index = this.tabs.indexOf(tab);
    tab.setAttribute('aria-selected', 'true');
    tab.setAttribute('tabindex', '0');
    tab.focus();
    this.panneaux[index].removeAttribute('hidden');
  }
}
```

### Listbox

**Reference APG** : <https://www.w3.org/WAI/ARIA/apg/patterns/listbox/>

#### Attributs aria requis

| Attribut | Element | Obligatoire | Detail |
|----------|---------|-------------|--------|
| `role="listbox"` | Conteneur de la liste | Oui | Identifie le widget comme liste de selection |
| `role="option"` | Chaque option | Oui | Identifie un element selectionnable |
| `aria-label` ou `aria-labelledby` | listbox | Oui | Nom accessible de la liste |
| `aria-selected="true/false"` | Chaque option | Oui | Indique l'etat de selection |
| `aria-multiselectable="true"` | listbox | Si multi | Autorise la selection multiple |
| `aria-activedescendant` | listbox | Non | Reference l'option active (alternative au roving tabindex) |

#### Clavier requis (spec APG)

| Touche | Comportement |
|--------|-------------|
| ArrowDown | Deplace le focus vers l'option suivante |
| ArrowUp | Deplace le focus vers l'option precedente |
| Home | Premiere option |
| End | Derniere option |
| Space | Toggle la selection de l'option active (multi-select) |
| Shift+ArrowDown/Up | Etend la selection contigue (multi-select) |
| Ctrl+A | Selectionne toutes les options (multi-select) |
| Type-ahead | Focus sur l'option correspondant aux caracteres tapes |

#### Gestion du focus

- Focus gere par `aria-activedescendant` (le listbox conserve le focus DOM) ou roving tabindex (focus DOM sur chaque option)
- Tab place le focus sur le listbox (option selectionnee si existante)
- En single-select, la selection suit le focus (ArrowDown selectionne l'option suivante)

#### Verification effective

- [ ] `role="listbox"` present sur le conteneur
- [ ] Chaque option a `role="option"` et `aria-selected`
- [ ] Fleche bas/haut deplace le focus entre les options (tester avec `press_key`)
- [ ] Home/End atteignent la premiere/derniere option (tester avec `press_key`)
- [ ] Space toggle la selection en mode multi-select (tester avec `press_key`)
- [ ] Type-ahead fonctionne (taper un caractere deplace le focus)

#### Snippet de reference

```html
<label id="label-fruits">Fruits preferes</label>
<ul role="listbox" aria-labelledby="label-fruits" aria-activedescendant="opt-pomme" tabindex="0">
  <li role="option" id="opt-pomme" aria-selected="true">Pomme</li>
  <li role="option" id="opt-banane" aria-selected="false">Banane</li>
  <li role="option" id="opt-cerise" aria-selected="false">Cerise</li>
</ul>
```

```javascript
// Navigation clavier du listbox
const listbox = document.querySelector('[role="listbox"]');
const options = [...listbox.querySelectorAll('[role="option"]')];
let activeIndex = Math.max(0, options.findIndex(o => o.getAttribute('aria-selected') === 'true'));

listbox.addEventListener('keydown', (e) => {
  let nouvelIndex;
  switch (e.key) {
    case 'ArrowDown': nouvelIndex = Math.min(activeIndex + 1, options.length - 1); break;
    case 'ArrowUp': nouvelIndex = Math.max(activeIndex - 1, 0); break;
    case 'Home': nouvelIndex = 0; break;
    case 'End': nouvelIndex = options.length - 1; break;
    default: return;
  }
  options.forEach(o => o.setAttribute('aria-selected', 'false'));
  activeIndex = nouvelIndex;
  options[activeIndex].setAttribute('aria-selected', 'true');
  listbox.setAttribute('aria-activedescendant', options[activeIndex].id);
  e.preventDefault();
});
```

### Menu / Menu bar

**Reference APG** : <https://www.w3.org/WAI/ARIA/apg/patterns/menubar/>

#### Attributs aria requis

| Attribut | Element | Obligatoire | Detail |
|----------|---------|-------------|--------|
| `role="menubar"` | Conteneur barre de menus | Oui | Identifie la barre de menus horizontale |
| `role="menu"` | Sous-menu | Oui | Identifie un menu vertical |
| `role="menuitem"` | Chaque item | Oui | Identifie un element de menu |
| `role="menuitemcheckbox"` | Item a cocher | Si applicable | Item avec etat coche/decoche |
| `role="menuitemradio"` | Item radio | Si applicable | Item dans un groupe exclusif |
| `aria-haspopup="true"` | menuitem parent | Si sous-menu | Indique un sous-menu associe |
| `aria-expanded="true/false"` | menuitem parent | Si sous-menu | Reflete l'etat ouvert/ferme |
| `aria-label` ou `aria-labelledby` | menubar/menu | Oui | Nom accessible du menu |

#### Clavier requis (spec APG)

| Touche | Menubar (horizontal) | Menu/Sous-menu (vertical) |
|--------|---------------------|---------------------------|
| ArrowRight | Menuitem suivant | Ouvre sous-menu imbrique |
| ArrowLeft | Menuitem precedent | Ferme sous-menu, retour parent |
| ArrowDown | Ouvre sous-menu, focus premier item | Menuitem suivant |
| ArrowUp | Ouvre sous-menu, focus dernier item | Menuitem precedent |
| Enter / Space | Active ou ouvre sous-menu | Active le menuitem |
| Home / End | Premier / dernier menuitem | Premier / dernier menuitem |
| Escape | Ferme le menu actif | Ferme, focus sur parent/trigger |

#### Gestion du focus

- Roving tabindex dans le menubar : seul le menuitem actif a `tabindex="0"`
- Tab place le focus sur le premier menuitem du menubar
- Tab depuis le menubar quitte le widget (ne descend pas dans les sous-menus)
- ArrowDown/Up wrap au debut/fin de la liste dans un sous-menu

#### Verification effective

- [ ] `role="menubar"` sur la barre, `role="menu"` sur les sous-menus
- [ ] Chaque item a `role="menuitem"` (ou `menuitemcheckbox`/`menuitemradio`)
- [ ] ArrowRight/Left navigue entre les items du menubar (tester avec `press_key`)
- [ ] ArrowDown ouvre le sous-menu depuis le menubar (tester avec `press_key`)
- [ ] Escape ferme le sous-menu et retourne au parent (tester avec `press_key`)
- [ ] Enter active le menuitem ou ouvre le sous-menu (tester avec `press_key`)
- [ ] `aria-haspopup` et `aria-expanded` presents sur les items avec sous-menu

#### Snippet de reference

```html
<nav aria-label="Application">
  <ul role="menubar" aria-label="Menu principal">
    <li role="none">
      <button role="menuitem" aria-haspopup="true" aria-expanded="false" tabindex="0">
        Fichier
      </button>
      <ul role="menu" aria-label="Fichier">
        <li role="none"><button role="menuitem" tabindex="-1">Nouveau</button></li>
        <li role="none"><button role="menuitem" tabindex="-1">Ouvrir</button></li>
        <li role="none"><button role="menuitem" tabindex="-1">Enregistrer</button></li>
      </ul>
    </li>
    <li role="none">
      <button role="menuitem" tabindex="-1">Edition</button>
    </li>
  </ul>
</nav>
```

```javascript
// Navigation clavier du menubar (touches essentielles)
const menubar = document.querySelector('[role="menubar"]');
const items = [...menubar.querySelectorAll(':scope > li > [role="menuitem"]')];

menubar.addEventListener('keydown', (e) => {
  const index = items.indexOf(document.activeElement);
  if (index === -1) return;

  switch (e.key) {
    case 'ArrowRight': items[(index + 1) % items.length].focus(); break;
    case 'ArrowLeft': items[(index - 1 + items.length) % items.length].focus(); break;
    case 'ArrowDown': {
      const menu = items[index].nextElementSibling;
      if (menu) { items[index].setAttribute('aria-expanded', 'true'); menu.querySelector('[role="menuitem"]')?.focus(); }
      break;
    }
    case 'Escape': {
      const parent = document.activeElement.closest('[role="menu"]');
      if (parent?.previousElementSibling) { parent.previousElementSibling.setAttribute('aria-expanded', 'false'); parent.previousElementSibling.focus(); }
      break;
    }
    case 'Home': items[0].focus(); break;
    case 'End': items[items.length - 1].focus(); break;
    default: return;
  }
  e.preventDefault();
});
```

### Disclosure

**Reference APG** : <https://www.w3.org/WAI/ARIA/apg/patterns/disclosure/>

#### Attributs aria requis

| Attribut | Element | Obligatoire | Detail |
|----------|---------|-------------|--------|
| `aria-expanded="true/false"` | Bouton declencheur | Oui | Reflete l'etat ouvert/ferme |
| `aria-controls` | Bouton declencheur | Recommande | Reference le conteneur du contenu controle |

Le declencheur doit etre un `<button>` (ou `role="button"` avec `tabindex="0"`). Pas de role supplementaire necessaire : c'est le pattern ARIA le plus simple.

#### Clavier requis (spec APG)

| Touche | Comportement |
|--------|-------------|
| Enter | Toggle l'etat du disclosure (ouvrir/fermer) |
| Space | Toggle l'etat du disclosure (ouvrir/fermer) |

Pas de navigation clavier specifique au-dela de Enter/Space. Le focus n'est jamais piege.

#### Gestion du focus

- Le bouton declencheur est focusable nativement (pas de gestion speciale)
- Quand le contenu est affiche, Tab deplace le focus dans le contenu
- Pas de focus trap : le contenu s'insere dans le flux normal de tabulation
- Pour un groupe d'accordeons, chaque bouton est un stop Tab independant

#### Verification effective

- [ ] Le declencheur est un `<button>` (ou `role="button"` avec `tabindex="0"`)
- [ ] `aria-expanded` reflete l'etat reel du contenu (tester avec `press_key` : Enter sur le bouton)
- [ ] `aria-controls` reference le conteneur du contenu (si present)
- [ ] Le contenu est masque visuellement ET pour les technologies d'assistance quand ferme (`hidden` ou `display: none`)
- [ ] Enter et Space togglent le disclosure (tester avec `press_key`)

#### Snippet de reference

```html
<button aria-expanded="false" aria-controls="contenu-faq-1">
  Comment reinitialiser mon mot de passe ?
</button>
<div id="contenu-faq-1" hidden>
  <p>Rendez-vous sur la page de connexion et cliquez sur "Mot de passe oublie".</p>
</div>
```

```javascript
document.querySelectorAll('[aria-controls]').forEach(bouton => {
  bouton.addEventListener('click', () => {
    const estOuvert = bouton.getAttribute('aria-expanded') === 'true';
    const contenu = document.getElementById(bouton.getAttribute('aria-controls'));

    bouton.setAttribute('aria-expanded', String(!estOuvert));
    contenu.toggleAttribute('hidden');
  });
});
```

### Tooltip

**Reference APG** : <https://www.w3.org/WAI/ARIA/apg/patterns/tooltip/>

**Attention** : ce pattern est marque « under development » par le W3C (pas encore de consensus du groupe de travail). La spec ci-dessous reflete l'etat actuel du draft. Toujours consulter la page officielle comme source de verite.

#### Attributs aria requis

| Attribut | Element | Obligatoire | Detail |
|----------|---------|-------------|--------|
| `role="tooltip"` | Element du tooltip | Oui | Identifie le widget comme tooltip |
| `aria-describedby` | Element declencheur | Oui | Reference le tooltip (description complementaire) |

Le tooltip fournit une **description** (pas un label). Si le texte est le label principal de l'element, utiliser `aria-labelledby` au lieu de `aria-describedby`.

#### Clavier requis (spec APG)

| Touche | Comportement |
|--------|-------------|
| Escape | Ferme le tooltip |

Le tooltip apparait au focus clavier (pas seulement au survol souris). Il disparait quand le focus quitte le declencheur ou quand Escape est presse.

#### Gestion du focus

- Le focus reste sur l'element declencheur (jamais dans le tooltip)
- Le tooltip ne contient jamais d'elements interactifs (sinon c'est un dialog non-modal)
- Apparition : au focus clavier ET au survol souris
- Disparition : perte de focus, fin du survol, ou Escape
- Le tooltip reste visible tant que le declencheur a le focus ou est survole

#### Verification effective

- [ ] `role="tooltip"` present sur l'element tooltip
- [ ] `aria-describedby` sur le declencheur reference le tooltip
- [ ] Le tooltip apparait au focus clavier sur le declencheur (tester avec `press_key` Tab)
- [ ] Escape ferme le tooltip (tester avec `press_key`)
- [ ] Le tooltip ne contient aucun element interactif (liens, boutons)
- [ ] Le tooltip reste visible tant que le declencheur est en focus

#### Snippet de reference

```html
<button aria-describedby="tooltip-supprimer">
  <svg aria-hidden="true"><!-- icone corbeille --></svg>
  <span class="sr-only">Supprimer</span>
</button>
<div role="tooltip" id="tooltip-supprimer" hidden>
  Supprimer definitivement cet element
</div>
```

```javascript
// Gestion du tooltip (apparition au focus et au survol)
function initTooltip(declencheur, tooltip) {
  const afficher = () => tooltip.removeAttribute('hidden');
  const masquer = () => tooltip.setAttribute('hidden', '');

  declencheur.addEventListener('mouseenter', afficher);
  declencheur.addEventListener('mouseleave', masquer);
  declencheur.addEventListener('focus', afficher);
  declencheur.addEventListener('blur', masquer);
  declencheur.addEventListener('keydown', (e) => { if (e.key === 'Escape') masquer(); });
}
```

### Formulaire accessible

```html
<label for="email">Email <span aria-label="obligatoire">*</span></label>
<input id="email" required aria-required="true" aria-describedby="erreur-email">
<span id="erreur-email" role="alert" aria-live="polite"></span>
```

### Regions live

```html
<!-- Statut (poli, n'interrompt pas) -->
<div role="status" aria-live="polite">3 articles ajoutes au panier</div>

<!-- Alerte (assertif, interrompt) -->
<div role="alert" aria-live="assertive">Erreur : soumission echouee</div>
```

## Checklist de tests manuels

### Navigation clavier

- [ ] Tous les elements interactifs accessibles via Tab
- [ ] Les boutons s'activent avec Entree/Espace
- [ ] La touche Echap ferme les modales
- [ ] L'indicateur de focus est toujours visible
- [ ] Pas de pieges clavier
- [ ] Ordre de tabulation logique

### Lecteur d'ecran

- [ ] Titre de page descriptif
- [ ] Les titres creent un plan logique (h1, h2, h3)
- [ ] Les images ont un texte alternatif
- [ ] Les champs de formulaire ont des labels
- [ ] Les messages d'erreur sont annonces
- [ ] Les mises a jour dynamiques sont annoncees

### Visuel

- [ ] Le texte se redimensionne a 200% sans perte
- [ ] La couleur n'est pas le seul moyen d'information
- [ ] Les indicateurs de focus ont un contraste suffisant
- [ ] Le contenu se redistribue a 320px
- [ ] Les animations respectent prefers-reduced-motion

### Cognitif

- [ ] Instructions claires et simples
- [ ] Messages d'erreur utiles et specifiques
- [ ] Pas de limite de temps sur les formulaires
- [ ] Navigation coherente entre les pages
- [ ] Actions importantes reversibles

### Checklist clavier par type de widget

Quand un widget ARIA est detecte, verifier les touches specifiques a son pattern APG. Utiliser `press_key` (MCP Chrome DevTools) pour des frappes reelles, pas `dispatchEvent`.

#### Dialog (role="dialog")

- [ ] Tab/Shift+Tab wrap dans le dialog
- [ ] Escape ferme le dialog
- [ ] Focus retourne au declencheur apres fermeture
- [ ] `aria-modal="true"` present
- [ ] Contenu arriere-plan inert

#### Combobox (role="combobox" ou button[aria-haspopup])

- [ ] Fleche bas ouvre le popup
- [ ] Enter/Space ouvre le popup
- [ ] Escape ferme le popup
- [ ] Focus retourne au trigger apres fermeture
- [ ] Navigation interne (fleches, Home/End si applicable)

#### Onglets (role="tablist")

- [ ] Fleche gauche/droite entre les onglets
- [ ] Home/End premier/dernier onglet
- [ ] Tab quitte le tablist vers le tabpanel

#### Listbox (role="listbox")

- [ ] Fleche bas/haut entre les options
- [ ] Home/End premiere/derniere option
- [ ] Space toggle selection (multi-select)
- [ ] `aria-selected` sur chaque option

#### Menu (role="menubar" ou role="menu")

- [ ] ArrowRight/Left dans le menubar
- [ ] ArrowDown/Up dans les sous-menus
- [ ] Enter/Space active le menuitem
- [ ] Escape ferme le sous-menu
- [ ] `aria-haspopup` et `aria-expanded` sur les items parents

#### Disclosure (aria-expanded)

- [ ] Enter/Space toggle le disclosure
- [ ] `aria-expanded` reflete l'etat reel
- [ ] Contenu masque pour les AT quand ferme

#### Tooltip (role="tooltip")

- [ ] Apparait au focus clavier
- [ ] Escape ferme le tooltip
- [ ] Aucun element interactif dans le tooltip

#### Tree view (role="tree") — voir `resources/aria-patterns-avances.md`

- [ ] ArrowDown/Up entre les treeitems visibles
- [ ] ArrowRight ouvre un noeud, ArrowLeft ferme
- [ ] `aria-expanded` sur les noeuds parents
- [ ] `aria-level` correct sur chaque treeitem

#### Grid (role="grid") — voir `resources/aria-patterns-avances.md`

- [ ] Fleches 4 directions entre les cellules
- [ ] Home/End debut/fin de ligne
- [ ] Ctrl+Home/End premiere/derniere cellule
- [ ] Tab quitte la grille

#### Carousel (aria-roledescription="carousel") — voir `resources/aria-patterns-avances.md`

- [ ] Bouton pause/play present et fonctionnel
- [ ] Auto-rotation s'arrete au focus clavier
- [ ] `aria-live` bascule entre "off" et "polite"

#### Alertdialog (role="alertdialog") — voir `resources/aria-patterns-avances.md`

- [ ] Tab/Shift+Tab wrap dans le dialog
- [ ] Escape ferme sans action destructive
- [ ] Focus initial sur l'action la moins destructive

## Patterns de remediation courants

### Correction : images sans texte alternatif

```html
<!-- Avant -->
<img src="graphique.png" />

<!-- Apres : image informative -->
<img src="graphique.png" alt="Ventes en hausse de 25% au T2" />

<!-- Apres : image decorative -->
<img src="separateur.png" alt="" />
```

### Correction : labels de formulaire manquants

```html
<!-- Avant -->
<input type="email" placeholder="Email" />

<!-- Apres : option 1 - label visible -->
<label for="email">Adresse email</label>
<input id="email" type="email" />

<!-- Apres : option 2 - aria-label -->
<input type="email" aria-label="Adresse email" />

<!-- Apres : option 3 - aria-labelledby -->
<span id="email-label">Email</span>
<input type="email" aria-labelledby="email-label" />
```

### Correction : contraste de couleur insuffisant

```css
/* Avant : contraste 2.5:1 */
.texte {
  color: #767676;
}

/* Apres : contraste 4.5:1 */
.texte {
  color: #595959;
}
```

### Correction : lien ambigu

```html
<!-- Avant -->
<a href="rapport.pdf">Cliquez ici</a>

<!-- Apres -->
<a href="rapport.pdf">Telecharger le rapport T4 (PDF)</a>
```

### Correction : focus visible

```css
:focus-visible {
  outline: 3px solid #005fcc;
  outline-offset: 2px;
}
```

### Correction : navigation clavier pour widget personnalise (conforme APG)

```javascript
// Widget combobox conforme au pattern APG
// Ref : https://www.w3.org/WAI/ARIA/apg/patterns/combobox/
class DropdownAccessible extends HTMLElement {
  connectedCallback() {
    this.setAttribute("tabindex", "0");
    this.setAttribute("role", "combobox");
    this.setAttribute("aria-expanded", "false");
    this.setAttribute("aria-haspopup", "listbox");

    const listbox = this.querySelector('[role="listbox"]');
    if (listbox) this.setAttribute("aria-controls", listbox.id);

    this.addEventListener("keydown", (e) => {
      const estOuvert = this.getAttribute("aria-expanded") === "true";

      switch (e.key) {
        case "Enter":
        case " ":
          if (!estOuvert) { this.ouvrir(); }
          else { this.selectionner(); }
          e.preventDefault();
          break;
        case "Escape":
          if (estOuvert) this.fermer();
          break;
        case "ArrowDown":
          if (e.altKey) { this.ouvrir(); }
          else if (!estOuvert) { this.ouvrir(); this.focusPremier(); }
          else { this.focusSuivant(); }
          e.preventDefault();
          break;
        case "ArrowUp":
          if (e.altKey && estOuvert) { this.fermer(); }
          else if (!estOuvert) { this.ouvrir(); this.focusDernier(); }
          else { this.focusPrecedent(); }
          e.preventDefault();
          break;
        case "Home":
          if (estOuvert) { this.focusPremier(); e.preventDefault(); }
          break;
        case "End":
          if (estOuvert) { this.focusDernier(); e.preventDefault(); }
          break;
      }
    });
  }

  ouvrir() { this.setAttribute("aria-expanded", "true"); }
  fermer() { this.setAttribute("aria-expanded", "false"); this.focus(); }
  focusPremier() { /* focus premiere option */ }
  focusDernier() { /* focus derniere option */ }
  focusSuivant() { /* focus option suivante */ }
  focusPrecedent() { /* focus option precedente */ }
  selectionner() { /* selectionne et ferme */ this.fermer(); }
}
```

### Correction : animations reduites

```css
@media (prefers-reduced-motion: reduce) {
  * {
    animation: none !important;
    transition: none !important;
  }
}
```

## Format de sortie attendu

1. **Score d'accessibilite** : conformite globale (0-100)
2. **Tableau de violations** : critere WCAG, severite, description, remediation
3. **Resultats des tests** : automatises et manuels
4. **Code correctif** : extraits prets a integrer pour chaque violation
5. **Risques residuels** : points non testables ou necessitant validation humaine

## Bonnes pratiques

### A faire

- **Commencer tot** — L'accessibilite des la phase de conception
- **Tester avec de vrais utilisateurs** — Les utilisateurs handicapes fournissent les meilleurs retours
- **Automatiser ce qui est possible** — 30-50% des problemes detectables
- **Utiliser le HTML semantique** — Reduit le besoin d'ARIA
- **Documenter les patterns** — Construire une bibliotheque de composants accessibles

### A eviter

- **Ne pas se fier uniquement aux tests automatises** — Les tests manuels sont indispensables
- **Ne pas utiliser ARIA en premier recours** — HTML natif d'abord
- **Ne pas masquer les indicateurs de focus** — Les utilisateurs clavier en ont besoin
- **Ne pas desactiver le zoom** — Les utilisateurs doivent pouvoir redimensionner
- **Ne pas utiliser la couleur seule** — Indicateurs multiples necessaires

## Roadmap des patterns APG

Roadmap des patterns WAI-ARIA APG a ajouter dans ce playbook. Chaque pattern doit suivre le format des fiches existantes (Dialog, Combobox) : reference APG, attributs requis, clavier requis, gestion du focus, checklist de verification, snippet de reference.

### Priorite 1 — promotion du pattern compact existant

| Pattern | Statut actuel | Travail restant | Reference APG |
|---------|--------------|-----------------|---------------|
| Tabs | **Complet** | Fiche complete avec attributs, clavier, gestion focus, checklist, snippet JS | <https://www.w3.org/WAI/ARIA/apg/patterns/tabs/> |

### Priorite 2 — patterns frequents en audit

| Pattern | Statut | Cas d'usage | Reference APG |
|---------|--------|-------------|---------------|
| Listbox | **Complet** | Listes de selection personnalisees | <https://www.w3.org/WAI/ARIA/apg/patterns/listbox/> |
| Menu / Menu bar | **Complet** | Menus de navigation, menus contextuels | <https://www.w3.org/WAI/ARIA/apg/patterns/menubar/> |
| Disclosure | **Complet** | Accordeons, FAQ, sections repliables | <https://www.w3.org/WAI/ARIA/apg/patterns/disclosure/> |
| Tooltip | **Complet** | Infobulles sur icones et controles | <https://www.w3.org/WAI/ARIA/apg/patterns/tooltip/> |

### Priorite 3 — patterns avances

| Pattern | Statut | Cas d'usage | Reference APG |
|---------|--------|-------------|---------------|
| Tree view | **Complet** | Arborescences de fichiers, menus hierarchiques | <https://www.w3.org/WAI/ARIA/apg/patterns/treeview/> |
| Grid | **Complet** | Tableaux editables, data grids | <https://www.w3.org/WAI/ARIA/apg/patterns/grid/> |
| Carousel | **Complet** | Carrousels de contenu | <https://www.w3.org/WAI/ARIA/apg/patterns/carousel/> |
| Alertdialog | **Complet** | Dialogues de confirmation critiques | <https://www.w3.org/WAI/ARIA/apg/patterns/alertdialog/> |

### Format de fiche attendu pour chaque pattern

```text
### Nom du pattern

**Reference APG** : lien

#### Attributs aria requis
(tableau : attribut, element, obligatoire, detail)

#### Clavier requis (spec APG)
(tableau : touche, comportement attendu)

#### Gestion du focus
(liste des regles de deplacement du focus)

#### Verification effective
(checklist avec items testables via press_key)

#### Snippet de reference
(HTML + JS minimal conforme)
```

## References externes

- [WAI-ARIA Authoring Practices Guide (APG)](https://www.w3.org/WAI/ARIA/apg/) — source de verite pour les patterns d'interaction clavier
- [Patterns APG](https://www.w3.org/WAI/ARIA/apg/patterns/) — liste complete des patterns par widget
- [Directives WCAG 2.2](https://www.w3.org/TR/WCAG22/)
- [Documentation axe-core](https://github.com/dequelabs/axe-core)
- [pa11y](https://pa11y.org/)
- [WebAIM](https://webaim.org/)
- [Checklist A11y Project](https://www.a11yproject.com/checklist/)
