# 007 — Extraire la recette Douane du kit générique

**À construire :** les URLs, campagnes, prompts et scripts spécifiques au
portail Douane sont retirés du kit générique et préparés pour le dépôt privé
`dsfr-agentic-douane`.

**Bloqué par :** création et initialisation du dépôt privé
`alexandra-guiderdoni/dsfr-agentic-douane`.

**Statut :** bloqué

- [ ] La liste des artefacts Douane à déplacer est établie.
- [ ] Les recettes migrées consomment le kit par `kit.lock`.
- [ ] Les URLs Douane ne sont plus nécessaires aux contrôles génériques du kit.
- [ ] Les archives et preuves brutes ne sont pas ajoutées au dépôt public du
  kit.
- [ ] Un contrôle prouve que le kit générique fonctionne sans la recette Douane.

**Preuve attendue :** inventaire avant/après, contrôle standalone et rejeu d’une
recette depuis le dépôt privé consommateur.
