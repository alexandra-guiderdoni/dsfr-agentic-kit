# Accessibilité

Référence extraite de `../utilities.md`.

---

## Classes d'assistance
- `fr-sr-only` : Visible uniquement par les lecteurs d'écran
- `fr-enlarge-link` : Zone cliquable étendue
- `fr-responsive-vid` : Vidéo responsive
- `fr-responsive-img` : Image responsive

`fr-sr-only-focusable` et `fr-link--no-underline` ne sont pas des classes
officielles DSFR 1.15.3 (vérifié dans `dist/dsfr.min.css`) : les retirer du
vocabulaire du skill.

## Attributs ARIA importants
- `role="navigation"` : Pour les éléments de navigation
- `role="search"` : Pour les formulaires de recherche
- `role="main"` : Pour le contenu principal
- `role="complementary"` : Pour les contenus complémentaires
- `role="alert"` : Pour les messages d'alerte
- `aria-label` : Label pour les éléments sans texte visible
- `aria-labelledby` : Référence à un élément servant de label
- `aria-describedby` : Référence à un élément de description
- `aria-current="page"` : Page courante dans la navigation
- `aria-expanded` : État ouvert/fermé
- `aria-controls` : Élément contrôlé
- `aria-hidden="true"` : Masqué aux lecteurs d'écran

## Focus et navigation clavier
- Tous les éléments interactifs doivent être accessibles au clavier
- L'ordre de tabulation doit être logique
- Le focus doit être visible
- Les raccourcis clavier ne doivent pas entrer en conflit avec ceux du système

## Contrastes
Les tokens DSFR sont conçus pour le système de contraste du DSFR, mais ce skill
ne prouve pas une conformité WCAG ou RGAA globale. Vérifier les contrastes sur
la page réelle, avec le thème, le contexte et les contenus finaux.
