# Matrice de couverture WCAG 2.2

Tests automatises Playwright et leur couverture. Ces tests completent axe-core qui ne detecte pas ces criteres.

| Test | Critere WCAG | Niveau | Detectable par axe-core | Description |
|------|-------------|--------|------------------------|-------------|
| reflow | 1.4.10 | AA | Non | Redistribution sans scroll horizontal a 320px |
| spacing | 1.4.12 | AA | Non | Espacement du texte sans perte de contenu |
| zoom | 1.4.4 | AA | Partiel | Redimensionnement du texte a 200% |
| orientation | 1.3.4 | AA | Non | Pas de verrouillage d'orientation |
| autocomplete | 1.3.5 | AA | Partiel | Attribut autocomplete sur champs d'identite |
| time | 2.2.1 | A | Non | Limites de temps controlables |
| autoplay | 1.4.2 / 2.2.2 | A | Non | Controle du contenu audio/video automatique |
| focus | 2.4.7 | AA | Partiel | Indicateur de focus visible |
| target | 2.5.5 / 2.5.8 | AA | Partiel | Taille minimale des cibles tactiles |

## Complémentarité avec `audit-a11y-complet`

`audit-a11y-complet` couvre les familles WCAG demandées via axe-core et des tests manuels. `tests-conformite-wcag` ajoute les tests automatisés que axe-core détecte mal ou pas du tout ; cette complémentarité ne constitue pas une couverture exhaustive.
