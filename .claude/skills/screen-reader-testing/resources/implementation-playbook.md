# Playbook d'implementation - Tests avec lecteur d'ecran

Ce fichier contient les patterns detailles, checklists et exemples de code references par le skill.

## Concepts fondamentaux

### 1. Principaux lecteurs d'ecran

| Lecteur d'ecran | Plateforme | Navigateur     | Usage |
| --------------- | ---------- | -------------- | ----- |
| **VoiceOver**   | macOS/iOS  | Safari         | ~15%  |
| **NVDA**        | Windows    | Firefox/Chrome | ~31%  |
| **JAWS**        | Windows    | Chrome/IE      | ~40%  |
| **TalkBack**    | Android    | Chrome         | ~10%  |
| **Narrateur**   | Windows    | Edge           | ~4%   |

### 2. Priorite des tests

```text
Couverture minimale :
1. NVDA + Firefox (Windows)
2. VoiceOver + Safari (macOS)
3. VoiceOver + Safari (iOS)

Couverture exhaustive :
+ JAWS + Chrome (Windows)
+ TalkBack + Chrome (Android)
+ Narrateur + Edge (Windows)
```

### 3. Modes du lecteur d'ecran

| Mode                  | Fonction                    | Utilisation           |
| --------------------- | --------------------------- | --------------------- |
| **Parcours/Virtuel**  | Lire le contenu             | Lecture par defaut    |
| **Focus/Formulaires** | Interagir avec les controles | Remplissage de formulaires |
| **Application**       | Widgets personnalises       | Applications ARIA     |

## VoiceOver (macOS)

### Configuration

```text
Activer : Preferences Systeme → Accessibilite → VoiceOver
Basculer : Cmd + F5
Bascule rapide : Triple appui Touch ID
```

### Commandes essentielles

```text
Navigation :
VO = Ctrl + Option (modificateur VoiceOver)

VO + Fleche droite    Element suivant
VO + Fleche gauche    Element precedent
VO + Maj + Bas        Entrer dans un groupe
VO + Maj + Haut       Sortir d'un groupe

Lecture :
VO + A                Tout lire depuis le curseur
Ctrl                  Arreter la synthese vocale
VO + B                Lire le paragraphe courant

Interaction :
VO + Espace           Activer l'element
VO + Maj + M          Ouvrir le menu
Tab                   Element focusable suivant
Maj + Tab             Element focusable precedent

Rotor (VO + U) :
Naviguer par : Titres, Liens, Formulaires, Landmarks
Fleche gauche/droite  Changer de categorie du rotor
Fleche haut/bas       Naviguer dans la categorie
Entree                Aller a l'element

Specifique au web :
VO + Cmd + H          Titre suivant
VO + Cmd + J          Champ de formulaire suivant
VO + Cmd + L          Lien suivant
VO + Cmd + T          Tableau suivant
```

### Checklist de test VoiceOver

```markdown
## Checklist de test VoiceOver

### Chargement de la page

- [ ] Titre de la page annonce
- [ ] Landmark principal trouve
- [ ] Lien d'evitement fonctionne

### Navigation

- [ ] Tous les titres decouverts via le rotor
- [ ] Niveaux de titres logiques (H1 → H2 → H3)
- [ ] Landmarks correctement etiquetes
- [ ] Liens d'evitement fonctionnels

### Liens et boutons

- [ ] Fonction du lien claire
- [ ] Actions des boutons decrites
- [ ] Nouvelle fenetre/onglet annonce

### Formulaires

- [ ] Tous les labels lus avec les champs
- [ ] Champs obligatoires annonces
- [ ] Messages d'erreur lus
- [ ] Instructions disponibles
- [ ] Focus deplace vers les erreurs

### Contenu dynamique

- [ ] Alertes annoncees immediatement
- [ ] Etats de chargement communiques
- [ ] Mises a jour de contenu annoncees
- [ ] Modales capturent le focus correctement

### Tableaux

- [ ] En-tetes associes aux cellules
- [ ] Navigation dans le tableau fonctionne
- [ ] Tableaux complexes ont des legendes
```

### Problemes courants et corrections

```html
<!-- Probleme : le bouton n'annonce pas sa fonction -->
<button><svg>...</svg></button>

<!-- Correction -->
<button aria-label="Fermer la boite de dialogue"><svg aria-hidden="true">...</svg></button>

<!-- Probleme : contenu dynamique non annonce -->
<div id="resultats">Nouveaux resultats charges</div>

<!-- Correction -->
<div id="resultats" role="status" aria-live="polite">Nouveaux resultats charges</div>

<!-- Probleme : erreur de formulaire non lue -->
<input type="email" />
<span class="erreur">Email invalide</span>

<!-- Correction -->
<input type="email" aria-invalid="true" aria-describedby="erreur-email" />
<span id="erreur-email" role="alert">Email invalide</span>
```

## NVDA (Windows)

### Configuration

```text
Telecharger : nvaccess.org
Demarrer : Ctrl + Alt + N
Arreter : Insert + Q
```

### Commandes essentielles

```text
Navigation :
Insert = modificateur NVDA

Fleche bas          Ligne suivante
Fleche haut         Ligne precedente
Tab                 Focusable suivant
Maj + Tab           Focusable precedent

Lecture :
NVDA + Fleche bas   Tout lire
Ctrl                Arreter la synthese
NVDA + Fleche haut  Ligne courante

Titres :
H                   Titre suivant
Maj + H             Titre precedent
1-6                 Titre de niveau 1-6

Formulaires :
F                   Champ de formulaire suivant
B                   Bouton suivant
E                   Champ de saisie suivant
X                   Case a cocher suivante
C                   Liste deroulante suivante

Liens :
K                   Lien suivant
U                   Lien non visite suivant
V                   Lien visite suivant

Landmarks :
D                   Landmark suivant
Maj + D             Landmark precedent

Tableaux :
T                   Tableau suivant
Ctrl + Alt + Fleches Naviguer dans les cellules

Liste des elements (NVDA + F7) :
Affiche tous les liens, titres, champs, landmarks
```

### Mode parcours vs mode focus

```text
NVDA bascule automatiquement entre les modes :
- Mode Parcours : les fleches naviguent dans le contenu
- Mode Focus : les fleches controlent les elements interactifs

Bascule manuelle : NVDA + Espace

Points d'attention :
- Annonce "Mode parcours" lors de la navigation
- Annonce "Mode focus" en entrant dans un champ
- Le role application force le mode formulaires
```

### Script de test NVDA

```markdown
## Script de test NVDA

### Chargement initial

1. Naviguer vers la page
2. Attendre la fin du chargement
3. Appuyer sur Insert + Fleche bas pour tout lire
4. Verifier : titre de page, contenu principal identifie ?

### Navigation par landmarks

1. Appuyer plusieurs fois sur D
2. Verifier : toutes les zones principales accessibles ?
3. Verifier : landmarks correctement etiquetes ?

### Navigation par titres

1. Appuyer sur Insert + F7 → Titres
2. Verifier : structure de titres logique ?
3. Appuyer sur H pour naviguer entre les titres
4. Verifier : toutes les sections decouvrables ?

### Test des formulaires

1. Appuyer sur F pour trouver le premier champ
2. Verifier : label lu ?
3. Saisir des donnees invalides
4. Soumettre le formulaire
5. Verifier : erreurs annoncees ?
6. Verifier : focus deplace vers l'erreur ?

### Elements interactifs

1. Tabuler sur tous les elements interactifs
2. Verifier : chacun annonce son role et son etat
3. Activer les boutons avec Entree/Espace
4. Verifier : resultat annonce ?

### Contenu dynamique

1. Declencher une mise a jour de contenu
2. Verifier : changement annonce ?
3. Ouvrir une modale
4. Verifier : focus capture ?
5. Fermer la modale
6. Verifier : focus restaure ?
```

## JAWS (Windows)

### Commandes essentielles

```text
Demarrer : raccourci bureau ou Ctrl + Alt + J
Curseur virtuel : active automatiquement dans les navigateurs

Navigation :
Touches fleches      Naviguer dans le contenu
Tab                  Focusable suivant
Insert + Fleche bas  Tout lire
Ctrl                 Arreter la synthese

Touches rapides :
H                    Titre suivant
T                    Tableau suivant
F                    Champ de formulaire suivant
B                    Bouton suivant
G                    Image suivante
L                    Liste suivante
;                    Landmark suivant

Mode formulaires :
Entree               Entrer en mode formulaires
Pave num. +          Quitter le mode formulaires
F5                   Lister les champs de formulaire

Listes :
Insert + F7          Liste des liens
Insert + F6          Liste des titres
Insert + F5          Liste des champs

Tableaux :
Ctrl + Alt + Fleches Navigation dans le tableau
```

## TalkBack (Android)

### Configuration

```text
Activer : Parametres → Accessibilite → TalkBack
Basculer : Maintenir les deux boutons de volume 3 secondes
```

### Gestes

```text
Explorer : Faire glisser le doigt sur l'ecran
Suivant : Balayer vers la droite
Precedent : Balayer vers la gauche
Activer : Double appui
Defiler : Balayage a deux doigts

Controles de lecture (balayer haut puis droite) :
- Titres
- Liens
- Controles
- Caracteres
- Mots
- Lignes
- Paragraphes
```

## Scenarios de test courants

### 1. Boite de dialogue modale

```html
<!-- Structure de modale accessible -->
<div
  role="dialog"
  aria-modal="true"
  aria-labelledby="titre-dialogue"
  aria-describedby="desc-dialogue"
>
  <h2 id="titre-dialogue">Confirmer la suppression</h2>
  <p id="desc-dialogue">Cette action est irreversible.</p>
  <button>Annuler</button>
  <button>Supprimer</button>
</div>
```

```javascript
// Gestion du focus
function ouvrirModale(modale) {
  // Sauvegarder le dernier element en focus
  dernierFocus = document.activeElement;

  // Deplacer le focus vers la modale
  modale.querySelector("h2").focus();

  // Capturer le focus
  modale.addEventListener("keydown", capturerFocus);
}

function fermerModale(modale) {
  // Restaurer le focus
  dernierFocus.focus();
}

function capturerFocus(e) {
  if (e.key === "Tab") {
    const focusables = modale.querySelectorAll(
      'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])',
    );
    const premier = focusables[0];
    const dernier = focusables[focusables.length - 1];

    if (e.shiftKey && document.activeElement === premier) {
      dernier.focus();
      e.preventDefault();
    } else if (!e.shiftKey && document.activeElement === dernier) {
      premier.focus();
      e.preventDefault();
    }
  }

  if (e.key === "Escape") {
    fermerModale(modale);
  }
}
```

### 2. Regions live

```html
<!-- Messages de statut (poli) -->
<div role="status" aria-live="polite" aria-atomic="true">
  <!-- Les mises a jour seront annoncees apres la synthese en cours -->
</div>

<!-- Alertes (assertif) -->
<div role="alert" aria-live="assertive">
  <!-- Les mises a jour interrompent la synthese en cours -->
</div>

<!-- Mises a jour de progression -->
<div
  role="progressbar"
  aria-valuenow="75"
  aria-valuemin="0"
  aria-valuemax="100"
  aria-label="Progression du telechargement"
></div>

<!-- Journal (ajouts uniquement) -->
<div role="log" aria-live="polite" aria-relevant="additions">
  <!-- Les nouveaux messages sont annonces, les suppressions non -->
</div>
```

### 3. Interface a onglets

```html
<div role="tablist" aria-label="Informations produit">
  <button role="tab" id="onglet-1" aria-selected="true" aria-controls="panneau-1">
    Description
  </button>
  <button
    role="tab"
    id="onglet-2"
    aria-selected="false"
    aria-controls="panneau-2"
    tabindex="-1"
  >
    Avis
  </button>
</div>

<div role="tabpanel" id="panneau-1" aria-labelledby="onglet-1">
  Contenu de la description du produit...
</div>

<div role="tabpanel" id="panneau-2" aria-labelledby="onglet-2" hidden>
  Contenu des avis...
</div>
```

```javascript
// Navigation clavier des onglets
listeOnglets.addEventListener("keydown", (e) => {
  const onglets = [...listeOnglets.querySelectorAll('[role="tab"]')];
  const index = onglets.indexOf(document.activeElement);

  let nouvelIndex;
  switch (e.key) {
    case "ArrowRight":
      nouvelIndex = (index + 1) % onglets.length;
      break;
    case "ArrowLeft":
      nouvelIndex = (index - 1 + onglets.length) % onglets.length;
      break;
    case "Home":
      nouvelIndex = 0;
      break;
    case "End":
      nouvelIndex = onglets.length - 1;
      break;
    default:
      return;
  }

  onglets[nouvelIndex].focus();
  activerOnglet(onglets[nouvelIndex]);
  e.preventDefault();
});
```

## Methode de test clavier

### press_key vs dispatchEvent

| Methode | Fonctionnement | Fiabilite |
|---------|---------------|-----------|
| `press_key` (MCP Chrome DevTools) | Simule une frappe au niveau CDP (`Input.dispatchKeyEvent`) | Elevee — reproduit le comportement navigateur reel |
| `dispatchEvent(new KeyboardEvent)` | Cree un evenement JS synthetique | Partielle — ne deplace pas le focus sur Tab, ne reproduit pas le traitement natif |

**Regle** : toujours utiliser `press_key` pour tester les interactions clavier des widgets. `dispatchEvent` ne deplace pas reellement le focus sur Tab et ne reproduit pas le traitement natif du navigateur.

### Procedure de test clavier d'un widget

1. Identifier le pattern APG du widget (dialog, combobox, tabs, listbox)
2. Consulter la spec APG : <https://www.w3.org/WAI/ARIA/apg/patterns/>
3. Focus sur le widget declencheur (cliquer ou tabuler)
4. Tester chaque touche de la spec APG avec `press_key`
5. Verifier le focus apres chaque touche avec `evaluate_script`
6. Documenter les ecarts par rapport a la spec

## Conseils de debogage

```javascript
// Journaliser ce que le lecteur d'ecran percoit
function journaliserNomAccessible(element) {
  const styles = window.getComputedStyle(element);
  console.log({
    role: element.getAttribute("role") || element.tagName,
    nom:
      element.getAttribute("aria-label") ||
      element.getAttribute("aria-labelledby") ||
      element.textContent,
    etat: {
      deploye: element.getAttribute("aria-expanded"),
      selectionne: element.getAttribute("aria-selected"),
      coche: element.getAttribute("aria-checked"),
      desactive: element.disabled,
    },
    visible: styles.display !== "none" && styles.visibility !== "hidden",
  });
}
```

## Bonnes pratiques

### A faire

- **Tester avec de vrais lecteurs d'ecran** — Pas seulement des simulateurs
- **Utiliser le HTML semantique d'abord** — ARIA est un complement
- **Tester en mode parcours et focus** — Experiences differentes
- **Verifier la gestion du focus** — Surtout pour les SPA
- **Tester d'abord au clavier seul** — Base des tests lecteur d'ecran

### A eviter

- **Ne pas se limiter a un seul lecteur** — Tester sur plusieurs
- **Ne pas ignorer le mobile** — Base d'utilisateurs croissante
- **Ne pas tester uniquement le cas nominal** — Tester les etats d'erreur
- **Ne pas oublier le contenu dynamique** — Source des problemes les plus courants
- **Ne pas se fier aux tests visuels** — Experience differente

## Ressources

- [Guide utilisateur VoiceOver](https://support.apple.com/guide/voiceover/welcome/mac)
- [Guide utilisateur NVDA](https://www.nvaccess.org/files/nvda/documentation/userGuide.html)
- [Documentation JAWS](https://support.freedomscientific.com/Products/Blindness/JAWS)
- [Enquete WebAIM sur les lecteurs d'ecran](https://webaim.org/projects/screenreadersurvey/)
