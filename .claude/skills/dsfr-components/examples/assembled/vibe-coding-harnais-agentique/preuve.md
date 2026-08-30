# Preuve - Vibe coding et harnais agentique

Commandes principales depuis la racine du dépôt source, du miroir autonome ou
du paquet généré :

```bash
SKILL_DIR=.claude/skills/dsfr-components  # adapter à l'emplacement d'installation
python3 "$SKILL_DIR"/scripts/check_assembled_page_schema.py
python3 "$SKILL_DIR"/scripts/generate_assembled_page.py \
  --config-file "$SKILL_DIR"/examples/assembled/vibe-coding-harnais-agentique/page.json \
  --check
python3 "$SKILL_DIR"/scripts/check_generated_outputs.py
```

Ce que la preuve couvre :

- `page.json` respecte le schéma publié du builder assemblé ;
- `page.html` est généré depuis le JSON et reste synchronisé avec lui ;
- la page référence ses ressources DSFR en relatif (`assets_prefix: "assets/dsfr"`)
  et ne dépend pas du CDN ; le dossier `assets/dsfr` n'est pas versionné : le
  peupler depuis le paquet officiel avant d'ouvrir la page (`mkdir -p assets/dsfr
  && cp -R ~/.cache/dsfr-official-cache/gouvfr-dsfr-1.15.2/package/dist/. assets/dsfr/`,
  après `check_generated_outputs.py --official-version 1.15.2` qui remplit le cache) ;
- le schéma SVG local est référencé sans `ratio`, afin d'éviter un rognage de
  diagramme ;
- les ancres locales de navigation et de sommaire ont une cible ;
- `href="#"`, les gestionnaires inline, les IDs dupliqués et les cibles ARIA
  absentes sont refusés par le builder ;
- le contenu principal contient un `<h1>`.

Ce qui reste non vérifié :

- rendu de la page tant que `assets/dsfr` n'a pas été peuplé localement (la
  page versionnée seule s'ouvre sans CSS ni JavaScript DSFR) ;
- conformité DSFR officielle ;
- conformité RGAA ;
- droit d'usage du bloc marque République française, volontairement non activé
  dans cet exemple ;
- contenu éditorial définitif ;
- comportement navigateur complet si les checks Playwright ne sont pas lancés
  ou sortent `SKIPPED`.
