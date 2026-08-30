# Preuve - Information de service

Commandes de preuve depuis la racine du workspace :

```bash
SKILL_DIR=.claude/skills/dsfr-components  # adapter à l'emplacement d'installation
python3 "$SKILL_DIR"/scripts/generate_assembled_page.py \
  --config-file "$SKILL_DIR"/examples/assembled/information-service/page.json \
  --check
python3 "$SKILL_DIR"/scripts/check_generated_outputs.py
```

Ce que la preuve couvre :

- génération de sections éditoriales, colonnes, onglets, téléchargement et
  partage ;
- contenus structurés échappés par le générateur ;
- liens d'ancre résolus ;
- absence des erreurs structurelles rapides du builder.

Ce qui reste non vérifié :

- exactitude du contenu administratif ;
- validité des documents liés ;
- conformité DSFR ou RGAA officielle ;
- comportement interactif complet au navigateur si le check Playwright est
  indisponible.
