# Preuve - Demande de rendez-vous

Commandes de preuve depuis la racine du workspace :

```bash
SKILL_DIR=.claude/skills/dsfr-components  # adapter à l'emplacement d'installation
python3 "$SKILL_DIR"/scripts/generate_assembled_page.py \
  --config-file "$SKILL_DIR"/examples/assembled/demarche-rendez-vous/page.json \
  --check
python3 "$SKILL_DIR"/scripts/check_generated_outputs.py
```

Ce que la preuve couvre :

- JSON chargeable par le builder assemblé ;
- page HTML complète générable depuis `page.json` ;
- absence de `href="#"`, d'ancres locales cassées, d'IDs dupliqués et de cibles
  ARIA absentes ;
- présence d'un `<h1>` dans `<main>` ;
- formulaire labellisé avec validation différée locale.

Ce qui reste non vérifié :

- conformité DSFR officielle ;
- conformité RGAA ;
- contenu métier définitif ;
- comportement navigateur complet hors checks Playwright disponibles.
