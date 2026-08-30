# Preuve - Suivi de dossier

Commandes de preuve depuis la racine du workspace :

```bash
SKILL_DIR=.claude/skills/dsfr-components  # adapter à l'emplacement d'installation
python3 "$SKILL_DIR"/scripts/generate_assembled_page.py \
  --config-file "$SKILL_DIR"/examples/assembled/suivi-dossier/page.json \
  --check
python3 "$SKILL_DIR"/scripts/check_generated_outputs.py
```

Ce que la preuve couvre :

- génération d'une page multi-sections avec cartes, tuiles, colonnes,
  accordéon, transcription et bloc de suivi ;
- vérification locale des IDs, ancres, cibles ARIA et liens interdits ;
- correspondance entre le JSON et le HTML versionné via le check global.

Ce qui reste non vérifié :

- données métier réelles ;
- autorisation de publication ;
- audit RGAA ;
- conformité DSFR officielle.
