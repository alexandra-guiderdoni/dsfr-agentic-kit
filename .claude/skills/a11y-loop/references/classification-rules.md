# Classification des corrections axe-core

## High (auto-apply)

Corrections mecaniques a faible risque de regression :

| ID axe-core | Critere WCAG | Correction type |
|--------------|--------------|-----------------|
| `image-alt` | 1.1.1 | Ajouter `alt=""` (decoratif) ou `alt="description"` (informatif) |
| `input-image-alt` | 1.1.1 | Ajouter `alt` sur `<input type="image">` |
| `label` | 1.3.1 / 4.1.2 | Ajouter `<label for="id">` ou `aria-label` |
| `color-contrast` | 1.4.3 | Ajuster couleur via algorithme HSL (voir playbook) |
| `html-has-lang` | 3.1.1 | Ajouter `lang="fr"` sur `<html>` |
| `html-lang-valid` | 3.1.1 | Corriger le code langue invalide |
| `document-title` | 2.4.2 | Ajouter `<title>` dans `<head>` |
| `link-name` | 2.4.4 / 4.1.2 | Ajouter texte ou `aria-label` sur liens vides |
| `button-name` | 4.1.2 | Ajouter texte ou `aria-label` sur boutons vides |
| `select-name` | 4.1.2 | Associer label au `<select>` |
| `frame-title` | 2.4.1 / 4.1.2 | Ajouter `title` sur `<iframe>` |
| `meta-viewport` | 1.4.4 | Retirer `maximum-scale=1` ou `user-scalable=no` |

## Low (validation requise)

Corrections necessitant jugement humain :

| ID axe-core | Critere WCAG | Raison |
|--------------|--------------|--------|
| `aria-*` | 4.1.2 | Roles et attributs ARIA : semantique contextuelle |
| `keyboard-*` | 2.1.1 | Navigation clavier : logique applicative |
| `focus-order-*` | 2.4.3 | Ordre de focus : depend du design |
| `heading-order` | 1.3.1 | Hierarchie titres : decision editoriale |
| `landmark-*` | 1.3.1 / 4.1.1 | Semantique HTML : choix architectural |
| `region` | 1.3.1 | Structuration en regions : depend du layout |
| `tabindex` | 2.4.3 | Valeurs tabindex > 0 : impact global navigation |
| `aria-live-*` | 4.1.3 | Regions live : depend des interactions dynamiques |
