# Classification des violations WCAG

Reference partagee pour les skills classifiant les violations.
Consulte par : a11y-loop, fix-accessibilite.

## Niveaux de confiance

| Confiance | Types de violations | Comportement |
|-----------|-------------------|--------------|
| **High** | Contraste insuffisant, alt manquant, attribut lang, labels formulaires, title page, viewport meta | Correction applicable automatiquement |
| **Low** | Roles ARIA, navigation clavier, semantique HTML, focus management, landmarks | Proposee avec avertissement, attente validation |

Les corrections Low ne sont pas verifiables sans runtime navigateur. Risque de regression.

**Regle** : en cas d'ambiguite, classifier comme **Low** par prudence.

## Priorite par severite

Trier les violations par severite decroissante :
1. Critique (bloquant)
2. Serieux (degradation majeure)
3. Modere (gene sans blocage)
4. Mineur (amelioration souhaitable)

## Regles d'application par iteration (a11y-loop)

- **Iterations 1 a 3** : appliquer UNIQUEMENT les corrections High
- **Iteration >= 4** : proposer aussi les corrections Low (avec confirmation)
- **Flag `--aggressive`** : appliquer High + Low des l'iteration 1 (sans confirmation pour Low)
