# Couleurs

Référence extraite de `../utilities.md`.

---

## Couleurs institutionnelles

| Nom | Variable CSS | Hex (clair) | Usage |
|-----|-------------|-------------|-------|
| Bleu France | `--blue-france-sun-113-625` | #000091 | Action principale, liens |
| Rouge Marianne | `--red-marianne-main-472` | #e1000f | Accents, erreurs |
| Gris défaut | `--grey-1000-50` | #161616 | Texte principal |
| Gris fond | `--grey-1000-50` | #f6f6f6 | Arrière-plan |

## Couleurs fonctionnelles

| Catégorie | Classe texte | Classe fond | Usage |
|-----------|-------------|-------------|-------|
| Info | `fr-text-default--info` | `fr-background-contrast--info` | Information |
| Succès | `fr-text-default--success` | `fr-background-contrast--success` | Validation |
| Avertissement | `fr-text-default--warning` | `fr-background-contrast--warning` | Attention |
| Erreur | `fr-text-default--error` | `fr-background-contrast--error` | Erreur |

## Couleurs de texte
- `fr-text-default--grey` : Gris par défaut (#161616)
- `fr-text-mention--grey` : Gris mention
- `fr-text-action-high--blue-france` : Bleu France
- `fr-text-default--info` : Texte information
- `fr-text-default--success` : Texte succès
- `fr-text-default--warning` : Texte avertissement
- `fr-text-default--error` : Texte erreur
- `fr-text-inverted--blue-france` : Texte inversé sur fond bleu
- `fr-text-inverted--grey` : Texte inversé sur fond sombre

## Couleurs de fond
- `fr-background-default--grey` : Fond gris par défaut
- `fr-background-contrast--grey` : Fond gris contraste
- `fr-background-alt--grey` : Fond gris alternatif
- `fr-background-contrast--info` : Fond information contrasté
- `fr-background-contrast--success` : Fond succès contrasté
- `fr-background-contrast--warning` : Fond avertissement contrasté
- `fr-background-contrast--error` : Fond erreur contrasté
- `fr-background-action-low--blue-france` : Fond bleu France clair
- `fr-background-action-high--blue-france` : Fond bleu France fort

## Palette étendue (couleurs d'accentuation)

17 couleurs d'accentuation, employées comme **suffixe de modificateur** sur
`fr-callout--`, `fr-highlight--`, `fr-quote--` et `fr-tag--` (par exemple
`fr-callout--blue-ecume`). Ce ne sont pas des variables CSS : `--blue-ecume`
n'est déclarée nulle part dans `dist/dsfr.min.css`. Les variables portent
toujours une échelle (`--blue-ecume-850-200`, `--green-tilleul-verveine-925-125`).

- `green-tilleul-verveine`, `green-bourgeon`, `green-emeraude`, `green-menthe`, `green-archipel`
- `blue-ecume`, `blue-cumulus`
- `purple-glycine`
- `pink-macaron`, `pink-tuile`
- `yellow-tournesol`, `yellow-moutarde`
- `orange-terre-battue`
- `brown-cafe-creme`, `brown-caramel`, `brown-opera`
- `beige-gris-galet`

Limite du skill : `generate_component.py` expose la couleur pour `callout` et
`highlight` seulement. `generate_tag` n'a pas de paramètre de couleur : pour un
tag coloré, écrire `fr-tag--{couleur}` à la main.

## Bordures
- `fr-border-default--grey` : Bordure grise par défaut
- `fr-border-default--blue-france` : Bordure bleu France
- `fr-border-plain--info` : Bordure information
- `fr-border-plain--success` : Bordure succès
- `fr-border-plain--warning` : Bordure avertissement
- `fr-border-plain--error` : Bordure erreur

## Couleurs retirées des utilitaires

Depuis DSFR 1.15.0, le rouge Marianne n'est plus décliné en classes utilitaires
de fond, de texte et de bordure : `src/dsfr/utility/colors/_setting.scss` porte
`exclude: red-marianne` sur les décisions `background`, `text` et `border`.
Onze classes ont disparu du paquet, dont `fr-text-action-high--red-marianne`,
`fr-background-action-low--red-marianne`,
`fr-background-action-high--red-marianne` et `fr-border-default--red-marianne`.
Motif donné par l'amont : cet usage de la couleur n'est pas autorisé.

Elles restent absentes de ce document. `scripts/generate_atom.py` les refuse,
sans les traiter comme un cas particulier : sa table `UTILITY_COLOR_SCALES`
donne, pour chaque couple rôle/variante, l'échelle réellement fournie par le
paquet, et le rouge Marianne n'y figure simplement plus pour ces rôles. Les
échelles sont irrégulières — `fr-background-default` n'accepte que `grey`,
`fr-text-title` que `blue-france` et `grey` — et
`check_generated_outputs.py` confronte la table au paquet officiel à chaque
contrôle.

Le rouge Marianne demeure disponible en `artwork` et comme variable CSS, par
exemple `--red-marianne-main-472`.
