# Étalon : horloge

Création `original-dsfr-like` de référence, déclarée non officielle (`official: false`). Elle montre à quoi ressemble une création qui suit le skill de bout en bout : archétype choisi, micro-spécification complète, construction en chemins remplis, audit strict sans avertissement, planche comparée aux références, score de maturité.

- `horloge.svg` : le pictogramme, `80x80`, trois calques, uniquement des `<path>`.
- `build_horloge.py` : générateur reproductible ; `python3 -B build_horloge.py` réécrit un SVG identique octet pour octet.
- `manifest.json` : statut, références inspectées (`map/compass`, `system/success`, `digital/calendar`), champs de micro-spécification, `production_score` 9/10.
- `preview.html` : planche à 80, 40 et 24 px face aux trois références, régénérée par `scripts/build_svg_preview.py --svg-root pictos-svg/etalon --references map/compass,system/success,digital/calendar --captions --output pictos-svg/etalon/preview.html`.

Mesures de l'audit du 28 août 2026 (V2, anneau ouvert) : `major` 62 commandes et 54 % du carré, `minor` 20 commandes et 6 %, décor 62 % ; toutes dans les plages officielles p10-p90. La V1 à anneau complet passait aussi l'audit mais sa régularité la rapprochait d'une icône de bibliothèque ; la V2 reprend l'anneau ouvert de `system/success`, preuve que l'audit ne remplace pas la revue visuelle.

Statut : `production-candidate`, après validation humaine explicite d'Alex le 28 août 2026 sur la planche (V2). Limite connue : les repères d'heures fusionnent avec l'anneau à 24 px, lisible à 40 px. Ce pictogramme n'est pas une Ressource DSFR et ne doit jamais être présenté comme officiel.
