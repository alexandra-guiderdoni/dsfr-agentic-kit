# Preuve - Prise en main agent

Commande principale depuis la racine du dépôt source, du miroir autonome ou du
paquet généré :

```bash
SKILL_DIR=.claude/skills/dsfr-components  # adapter à l'emplacement d'installation
bash scripts/demo-dsfr-assembled-page.sh
```

Commandes détaillées équivalentes :

```bash
python3 "$SKILL_DIR"/scripts/check_assembled_page_schema.py --schema-only
python3 "$SKILL_DIR"/scripts/generate_assembled_page.py \
  --config-file "$SKILL_DIR"/examples/assembled/prise-en-main-agent/page.json \
  --check
```

Ce que la preuve couvre :

- `page.json` respecte le schéma publié ;
- la page HTML est générable depuis le JSON ;
- les ancres locales de navigation et de sommaire ont une cible ;
- `href="#"`, les gestionnaires inline, les IDs dupliqués et les cibles ARIA
  absentes sont refusés par le builder ;
- la page générée contient un `main`, un `footer` et un `<h1>` unique dans le
  contenu principal ;
- le formulaire conserve une validation différée locale pour les champs requis.

Ce qui reste non vérifié :

- conformité DSFR officielle ;
- conformité RGAA ;
- contenu métier définitif ;
- comportement navigateur complet si les checks Playwright ne sont pas lancés
  ou sortent `SKIPPED`.
