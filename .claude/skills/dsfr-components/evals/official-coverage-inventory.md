# Inventaire officiel DSFR 1.15.2

Inventaire généré depuis le paquet npm extrait localement. Il mesure la
surface officielle disponible ; il ne prouve pas une conformité RGAA ni
un droit de publication.

## Source

- Paquet : `@gouvfr/dsfr@1.15.2`
- Chemin : `~/.cache/dsfr-official-cache/gouvfr-dsfr-1.15.2/package`
- Commande :

```bash
SKILL_DIR=.claude/skills/dsfr-components  # adapter à l'emplacement d'installation
python3 "$SKILL_DIR/scripts/inventory_official_coverage.py" --official-version 1.15.2 --output "$SKILL_DIR/evals/official-coverage-inventory.md"
```

## Synthèse

| Surface | Total officiel | Couverture locale | Statut |
| --- | --- | --- | --- |
| Variables CSS `dsfr.min.css` | 1090 | références `tokens.md` / `tokens-advanced.md` | inventaire officiel, pas catalogue embarqué |
| Classes `dsfr.min.css` | 3383 | validation des classes générées | preuve de présence, pas audit visuel |
| Classes utilitaires `utility.min.css` | 1517 | `utilities.md` + sous-références | charger la famille utile |
| Utilitaires hors icônes/artwork | 221 | `generate_atom.py` + références | couverture partielle bornée |
| Icônes `fr-icon-*` | 1044 classes, 18 familles, 1038 SVG | `list_icons.py` | validation runtime possible |
| Icônes legacy `fr-fi-*` | 154 classes | références icônes | dépréciées, ne pas introduire |
| Pictogrammes | 102 SVG, 10 familles | `generate_atom.py pictogram` | pointer-only |
| Composants `dist/component` | 46 | 46/46 officiels couverts | claim borné aux composants officiels |
| Variantes locales | n/a | 136 variantes JSON | bibliothèque locale, pas surface officielle exhaustive |

## Familles principales

- Variables CSS : background (322), artwork (136), text (80), border (76), green (75), blue (45), brown (45), grey (36), pink (30), yellow (30), beige (15), orange (15).
- Utilitaires hors icônes/artwork : background (107), text (69), border (45).

## Composants officiels

accordion, alert, badge, breadcrumb, button, callout, card, checkbox, connect, consent, content, display, download, follow, footer, form, header, highlight, input, link, logo, modal, navigation, notice, pagination, password, quote, radio, range, search, segmented, select, share, sidemenu, skiplink, stepper, summary, tab, table, tag, tile, toggle, tooltip, transcription, translate, upload

## Écarts

- Composants officiels absents localement : aucun.
- Composants locaux non officiels : aucun hors helpers déclarés.
- Helpers locaux hors catalogue officiel : back_to_top, button_group.

## Usage agentique

- Pour valider un token précis, vérifier le paquet ou la référence ciblée.
- Pour valider une classe, charger la famille utilitaire ou le composant.
- Pour revendiquer `100 %`, citer cet inventaire et la commande rejouée.
- Pour RGAA, publication ou marque État, router vers `verification.md`.
