# Playbook de remediation - Corrections d'accessibilite

Patterns de correction, classification par confiance et formule de contraste WCAG pour le skill `/fix-a11y`.

## Schema du rapport d'entree

Le skill attend un rapport d'audit structure contenant des violations avec ces champs :

```text
| Critere WCAG | Severite | Description | Element | Fichier |
```

Chaque ligne de violation doit contenir au minimum : le critere WCAG (ex: 1.4.3), la severite, et le fichier source concerne.

## Classification par confiance

### Corrections haute confiance (auto-applicables)

Corrections deterministes, verifiables sans runtime navigateur.

| Type de violation | Criteres WCAG | Correction type |
|---|---|---|
| Contraste insuffisant | 1.4.3, 1.4.6, 1.4.11 | Ajuster la couleur (formule luminance) |
| Alt manquant sur image | 1.1.1 | Ajouter `alt` descriptif ou `alt=""` |
| Attribut lang manquant | 3.1.1 | Ajouter `lang="fr"` sur `<html>` |
| Label formulaire manquant | 1.3.1, 4.1.2 | Ajouter `<label for>` ou `aria-label` |
| Titre de page manquant | 2.4.2 | Ajouter/corriger `<title>` |
| Lien vide (sans texte) | 2.4.4, 4.1.2 | Ajouter texte ou `aria-label` |
| Champ obligatoire sans indicateur | 3.3.2 | Ajouter `aria-required="true"` |

### Corrections basse confiance (validation humaine requise)

Corrections dependant du contexte, du rendu ou de la navigation. Risque de regression.

| Type de violation | Criteres WCAG | Risque |
|---|---|---|
| Roles ARIA incorrects | 4.1.2 | Peut casser la navigation lecteur d'ecran |
| Navigation clavier absente | 2.1.1 | Necessite test interactif |
| Ordre de focus incorrect | 2.4.3 | Depend du layout visuel |
| Piege clavier | 2.1.2 | Necessite test clavier reel |
| Hierarchie de titres | 1.3.1 | Depend de la structure de page |
| Semantique HTML | 1.3.1, 4.1.1 | Peut affecter le rendu et le style |
| Focus management (SPA) | 2.4.3 | Depend de la logique applicative |
| Regions live manquantes | 4.1.3 | Depend du comportement dynamique |

## Patterns de correction

### Contraste insuffisant (High)

```css
/* Avant : contraste 2.5:1 */
.texte { color: #767676; }

/* Apres : contraste 4.5:1 */
.texte { color: #595959; }
```

Utiliser la formule de luminance relative (section ci-dessous) pour calculer la couleur cible.

### Alt manquant (High)

```html
<!-- Image informative : decrire le contenu -->
<img src="graphique.png" alt="Ventes en hausse de 25% au T2" />

<!-- Image decorative : alt vide -->
<img src="separateur.png" alt="" />

<!-- Image dans un lien : decrire la destination -->
<a href="/accueil"><img src="logo.png" alt="Accueil" /></a>
```

### Label formulaire manquant (High)

```html
<!-- Option 1 : label visible (prefere) -->
<label for="email">Adresse email</label>
<input id="email" type="email" />

<!-- Option 2 : aria-label (si label masque) -->
<input type="email" aria-label="Adresse email" />

<!-- Option 3 : aria-labelledby -->
<span id="email-label">Email</span>
<input type="email" aria-labelledby="email-label" />
```

### Lien vide (High)

```html
<!-- Avant -->
<a href="/profil"><i class="icon-user"></i></a>

<!-- Apres -->
<a href="/profil" aria-label="Mon profil"><i class="icon-user" aria-hidden="true"></i></a>
```

### Focus visible (High)

```css
:focus-visible {
  outline: 3px solid #005fcc;
  outline-offset: 2px;
}
```

### Rôles aria (basse confiance -- proposition seulement)

```html
<!-- Avertissement : cette correction necessite une validation avec lecteur d'ecran -->

<!-- Modale -->
<div role="dialog" aria-modal="true" aria-labelledby="modal-titre">
  <h2 id="modal-titre">Confirmation</h2>
  <!-- contenu -->
</div>

<!-- Onglets -->
<div role="tablist" aria-label="Sections">
  <button role="tab" aria-selected="true" aria-controls="panel-1">Onglet 1</button>
  <button role="tab" aria-selected="false" aria-controls="panel-2">Onglet 2</button>
</div>
<div role="tabpanel" id="panel-1">Contenu 1</div>
```

### Navigation clavier (Low -- proposition seulement)

```javascript
// Avertissement : tester avec press_key via MCP chrome-devtools apres application

// Piege a focus pour modale
function trapFocus(dialog) {
  const focusables = dialog.querySelectorAll(
    'a[href], button, input, select, textarea, [tabindex]:not([tabindex="-1"])'
  );
  const premier = focusables[0];
  const dernier = focusables[focusables.length - 1];

  dialog.addEventListener('keydown', (e) => {
    if (e.key === 'Tab') {
      if (e.shiftKey && document.activeElement === premier) {
        dernier.focus(); e.preventDefault();
      } else if (!e.shiftKey && document.activeElement === dernier) {
        premier.focus(); e.preventDefault();
      }
    }
    if (e.key === 'Escape') fermerModale();
  });

  premier.focus();
}
```

## Formule de contraste WCAG

### Luminance relative

La luminance relative d'une couleur RGB est calculee selon WCAG 2.x :

```
Pour chaque canal (R, G, B) :
  1. Convertir en sRGB : val = canal / 255
  2. Lineariser :
     - si val <= 0.04045 : lin = val / 12.92
     - sinon : lin = ((val + 0.055) / 1.055) ^ 2.4
  3. Luminance = 0.2126 * R_lin + 0.7152 * G_lin + 0.0722 * B_lin
```

### Ratio de contraste

```
ratio = (L_clair + 0.05) / (L_sombre + 0.05)
```

Ou `L_clair` est la luminance la plus elevee et `L_sombre` la plus faible.

### Seuils WCAG

| Niveau | Texte normal | Texte agrandi (18pt+) | Composants UI |
|--------|-------------|----------------------|---------------|
| AA     | 4.5:1       | 3:1                  | 3:1           |
| AAA    | 7:1         | 4.5:1                | 3:1           |

### Algorithme de correction

Pour trouver une couleur conforme tout en preservant la teinte :

```
1. Convertir la couleur en HSL
2. Fixer H (teinte) et S (saturation)
3. Reduire L (luminosite) par pas de 1% jusqu'a atteindre le ratio cible
4. Si L = 0% et ratio insuffisant : la teinte ne peut pas atteindre le contraste requis
   -> Proposer des alternatives : changer le background ou accepter une teinte differente
5. Reconvertir en hex
```

### Exemple de calcul

```
Foreground : #888888 sur Background : #FFFFFF
  R=136, G=136, B=136
  sRGB = 0.533
  Linearise = 0.250
  Luminance foreground = 0.250
  Luminance background = 1.000

  Ratio = (1.000 + 0.05) / (0.250 + 0.05) = 3.5:1
  -> Insuffisant pour AA (4.5:1 requis)

  Reduction progressive de la luminosite :
  #767676 -> ratio 4.54:1 -> CONFORME AA
```

## Gestion des cas impossibles

Quand le ratio cible est mathematiquement inatteignable avec la teinte donnee :

1. **Proposer un foreground noir** (`#000000`) : ratio maximum possible avec le background
2. **Proposer de changer le background** : eclaircir le fond pour augmenter le contraste
3. **Demander a l'utilisateur** : choix entre options avec impact visuel explique

## Workflow de mise a jour du rapport

Apres chaque correction appliquee, generer un fichier de suivi `FIX-REPORT.md` :

```markdown
# Rapport de remediation

Date : [date]
Rapport source : [fichier]

## Corrections appliquees (High)

| # | Critere | Fichier | Ligne | Avant | Apres |
|---|---------|---------|-------|-------|-------|
| 1 | 1.4.3   | Nav.tsx | 42    | #888  | #767676 |

## Suggestions en attente (Low)

| # | Critere | Fichier | Suggestion | Risque |
|---|---------|---------|-----------|--------|
| 1 | 4.1.2   | Menu.tsx | Ajouter role="menu" | Navigation lecteur d'ecran |

## Decisions humaines requises

| # | Critere | Probleme | Options |
|---|---------|----------|---------|
| 1 | 1.4.3   | Contraste impossible avec teinte actuelle | Noir, changer fond, teinte differente |
```
