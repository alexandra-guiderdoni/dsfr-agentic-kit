# Brief - Vibe coding et harnais agentique

Produire une page DSFR assemblée qui explique la différence entre trois niveaux
d'usage de la GenIA pour le développement logiciel :

- le vibe coding, utile pour prototyper vite mais fragile si personne ne relit ;
- l'agent qui agit dans un environnement et revient avec un résultat ;
- le harnais agentique, qui donne à l'agent un contexte, des règles, des outils,
  des preuves et une condition d'arrêt.

La page s'inspire de la synthèse thématique du webinaire ENI sur les
développeurs à l'ère de la GenIA. Elle doit rester pédagogique, sobre et
opérationnelle : l'objectif n'est pas de vendre l'IA, mais de montrer pourquoi
un modèle seul ne suffit pas.

Contraintes :

- utiliser le builder assemblé depuis `page.json` ;
- utiliser `assets_prefix: "assets/dsfr"` pour éviter le CDN dans la sortie ;
- utiliser `brand_mode: neutral` tant qu'aucun droit d'usage du bloc marque
  République française n'est établi ;
- inclure un schéma SVG local sans `ratio`, afin de vérifier que le builder ne
  rogne pas les diagrammes ;
- expliquer les limites du vibe coding sans le caricaturer ;
- montrer que le harnais sert surtout aux tâches risquées, déléguées,
  multi-fichiers ou difficiles à relire manuellement ;
- ne pas revendiquer de conformité DSFR ou RGAA ;
- éviter `href="#"`, les ancres absentes, les gestionnaires inline et le HTML
  brut non relu.

Critère de réussite : `page.json` valide le schéma, `page.html` est généré par
`generate_assembled_page.py`, les checks locaux du builder passent, et la preuve
distingue les invariants vérifiés des limites non couvertes.
