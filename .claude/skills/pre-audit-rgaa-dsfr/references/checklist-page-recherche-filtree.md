# Checklist RGAA — Page de recherche filtrée

Checklist spécialisée pour l'audit de pages de recherche avec filtres (Views Exposed Form Drupal, facettes, recherche plein texte). Complète la checklist générique `thematiques-rgaa-inspection.md` pour ce type de page.

---

## 1. Titre de page et métadonnées (thématique 8)

### Critères 8.5 et 8.6 — Titre pertinent

- [ ] La page possède une balise `<title>`
- [ ] Le titre reprend le terme de recherche saisi
- [ ] Le titre reflète les filtres actifs (au moins leur nombre)
- [ ] Le titre inclut la pagination en cours (ex : "Page 2 sur 5")
- [ ] Le nom du site n'est pas dupliqué dans le titre
- [ ] Après application d'un filtre, le titre reste distinctif (pas de régression vers un titre générique)

### Critère 8.7 — Langue des contenus

- [ ] Les labels masqués générés par le CMS sont en français (pas de `"Fulltext search"`, `"Current page"`)
- [ ] Si un contenu est dans une autre langue, il est balisé avec `lang="xx"`

### Mise à jour dynamique (SPA / Ajax)

- [ ] Si les filtres rechargent en Ajax, le `<title>` est mis à jour dynamiquement

---

## 2. Structure et navigation (thématiques 9 et 12)

### Critère 9.1 — Hiérarchie des titres

- [ ] Un seul `<h1>` (titre de la page)
- [ ] `<h2>` pour la zone des résultats et la zone des filtres
- [ ] `<h3>` pour les titres des cartes/résultats individuels
- [ ] Pas de saut de niveau

### Critères 9.2 et 12.6 — Landmarks et zones de regroupement

- [ ] Le formulaire de recherche est dans un `role="search"`
- [ ] Les résultats sont dans un `<main>`
- [ ] Si plusieurs `role="search"` existent, ils ont des `aria-label` distincts
- [ ] Le fil d'Ariane est dans un `<nav>` avec `aria-label`

### Critère 9.3 — Structure des listes

- [ ] Les résultats sont structurés en `<ul>/<ol>` avec `<li>` (pas de succession de `<div>`)
- [ ] Les groupes de tags sont structurés en `<ul>` avec `<li>` pour chaque tag
- [ ] La pagination est dans un `<nav>` avec `<ul>/<li>`

### Critère 12.7 — Liens d'évitement

- [ ] Un lien d'évitement permet de sauter les filtres pour accéder aux résultats

### Critères 12.5 et 12.8 — Cohérence et ordre de tabulation

- [ ] Le formulaire de recherche est atteignable de la même manière sur tout le site
- [ ] Après soumission des filtres, l'ordre de tabulation reste logique
- [ ] Le focus ne se perd pas après rechargement (vérifier `document.activeElement`)

---

## 3. Formulaire de recherche et filtres (thématique 11)

### Critères 11.1 et 11.2 — Étiquettes

- [ ] Chaque champ a un `<label>` associé par `for`/`id`
- [ ] Le label est pertinent et en français
- [ ] Pas de double `<label>` pointant vers le même `id` (vérifié par arbre a11y : nom non dupliqué)
- [ ] Le `title` n'est pas vide sur les champs qui en portent un

### Critère 11.3 — Cohérence des étiquettes

- [ ] **Si formulaires dupliqués (mobile/desktop)** : les labels des champs de même fonction sont identiques entre les deux variantes

### Critères 11.5, 11.6, 11.7 — Regroupement des filtres

- [ ] Les filtres de même nature sont regroupés en `<fieldset>` avec `<legend>`
- [ ] La légende n'est pas dupliquée dans l'arbre d'accessibilité
- [ ] Pas de contenu de test (ex : "Lorem ipsum") dans les valeurs de filtre

### Critère 11.8 — Listes déroulantes

- [ ] Si `<select>` utilisé, les options de même nature sont groupées en `<optgroup>`

### Critère 11.9 — Boutons

- [ ] Le bouton de recherche a un intitulé explicite (pas juste une icône sans nom accessible)
- [ ] Les boutons "Appliquer les filtres" et "Réinitialiser" sont nommés

### Critères 11.10 et 11.11 — Contrôle de saisie

- [ ] Les champs obligatoires sont identifiés
- [ ] Les erreurs de format (date, prix) génèrent un message relié au champ

---

## 4. Scripts et mises à jour dynamiques (thématique 7)

### Critère 7.4 — Changement de contexte

- [ ] La sélection d'un filtre seule ne déclenche PAS de rechargement automatique (un bouton "Appliquer" est nécessaire)
- [ ] OU l'utilisateur est averti au préalable du rechargement automatique

### Critère 7.5 — Messages de statut

- [ ] Le nombre de résultats mis à jour est annoncé via `role="status"` ou `aria-live="polite"`
- [ ] Si rechargement complet (pas Ajax) : le critère n'est pas applicable sur ce parcours

### Critères 7.1 et 7.3 — Composants scriptés

- [ ] Les composants complexes (autocomplétion, curseur de prix, combobox) sont conformes aux patterns APG
- [ ] Tous les composants sont utilisables au clavier sans piège de focus

---

## 5. Restitution des résultats (thématiques 1, 6, 9)

### Critères 6.1 et 6.2 — Liens explicites

- [ ] Chaque lien de résultat a un intitulé explicite (titre de la carte, pas "Lire la suite")
- [ ] Les liens génériques sont complétés par le contexte (`aria-label` ou titre précédent)

### Critères 1.1 et 1.2 — Images des résultats

- [ ] Les vignettes purement illustratives ont `alt=""` (décoratives)
- [ ] Les images porteuses d'information ont un `alt` pertinent
- [ ] Le traitement est cohérent au sein de la liste (pas une image avec `alt=""` et les autres avec un texte)

---

## 6. Présentation, couleurs et mobile (thématiques 3 et 10)

### Critères 3.1 et 10.9 — Information non véhiculée uniquement par la couleur

- [ ] L'état du filtre actif est indiqué par un attribut sémantique (`aria-pressed`, `aria-current`, `aria-selected`) ou un texte masqué
- [ ] La page de pagination active a `aria-current="page"`

### Critères 3.2 et 3.3 — Contrastes

- [ ] Textes : ratio minimum 4.5:1 (3:1 pour les gros textes)
- [ ] Composants d'interface (bordures champs, boutons, checkboxes) : ratio minimum 3:1

### Critère 10.7 — Visibilité du focus

- [ ] Le focus clavier est visible sur chaque filtre, résultat, lien et bouton de pagination

### Critère 10.8 — Masquage responsive

- [ ] Si formulaires dupliqués (mobile/desktop), le formulaire non affiché est masqué pour les technologies d'assistance (`display: none` ou `aria-hidden`)
- [ ] Vérifier chaque élément enfant, pas seulement le conteneur parent

### Critère 10.11 — Zoom 400 %

- [ ] Pas de barre de défilement horizontal à 320 px
- [ ] Les filtres et résultats se redistribuent correctement

---

## 7. Pagination (composant DSFR)

### Critère 7.1.3 — Liens désactivés

- [ ] Les liens désactivés (première page, précédent quand on est en page 1) ont `aria-disabled="true"` ET `role="link"` (template DSFR)
- [ ] Pas d'`aria-label` sur les liens désactivés (non prévu par le template DSFR)
- [ ] La page courante a `aria-current="page"` et pas de `href`

### Critère 8.7 — Langue du title pagination

- [ ] Le `title` de la page courante est en français (pas `"Current page : X"`)

---

## 8. Validité du code (thématique 8)

### Critère 8.2 — Validité du code

- [ ] Pas d'IDs dupliqués entre les formulaires mobile et desktop (suffixe `--2` correct)
- [ ] Pas de double `<label for>` pointant vers le même `input`
- [ ] Structure HTML valide (`<ul>` ne contient que des `<li>`)

---

## Spécificités des Views exposed form (Drupal)

Points d'attention récurrents sur les sites Drupal avec le module Better Exposed Filters (BEF) :

| Pattern Drupal | Défaut courant | Critères impactés |
|----------------|---------------|-------------------|
| Deux formulaires (mobile/desktop) | Labels incohérents entre variantes | 11.3, 10.8 |
| Label masqué Drupal + label DSFR | Double `<label for>`, nom accessible dupliqué | 11.1, 11.2, 8.2 |
| Nom machine comme label | `"Fulltext search"` au lieu de `"Rechercher"` | 11.2, 8.7 |
| Tags dans les cartes via Views | `<ul><p class="fr-tag">` au lieu de `<ul><li><span>` | 9.3 |
| Résultats en `<div>` | Pas de structure de liste sémantique | 9.3 |
| Pagination Drupal sans `role="link"` | Liens désactivés exposés comme `generic` | 7.1 |
| Vocabulaire de test | "Lorem ipsum" dans les filtres | Contenu |
| Localisation incomplète | `title="Current page"`, labels anglais | 8.7 |
