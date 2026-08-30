# Installer et tester DSFR Agentic Kit

Ce guide place le kit à côté du projet qui recevra les livrables. Le kit reste
remplaçable et en lecture seule pendant son utilisation.

## 1. Vérifier les prérequis

Depuis la racine du kit :

```bash
bash scripts/check-prerequisites.sh
```

Le diagnostic ne réalise aucune installation. Une dépendance facultative
absente produit un avertissement ; une dépendance requise absente fait échouer
la commande avec l’action attendue.

## 2. Vérifier le kit

```bash
bash scripts/check-agentic-design-pack.sh
```

Le contrôle inspecte l’inventaire, les chemins, les règles de génération et
les régressions produit. Il lance également une génération dans un dossier
temporaire.

Lorsque le paquet officiel DSFR n’est pas disponible dans le cache local, le
contrôle de fidélité officiel peut être marqué `[SKIP]`. Ce saut ne vaut pas
preuve de fidélité.

## 3. Exécuter les démonstrations

```bash
bash scripts/demo-dsfr-assembled-page.sh --quiet
bash scripts/demo-dsfr-vitrine.sh --quiet
```

Les commandes affichent les chemins de leurs sorties temporaires. La vitrine
indique aussi comment servir le résultat localement si une inspection visuelle
est souhaitée.

## 4. Préparer le workspace

Arborescence recommandée :

```text
workspace/
├── dsfr-agentic-kit/
├── mon-projet/
├── AGENTS.md      # facultatif, à fusionner pour Codex
└── CLAUDE.md      # facultatif, à fusionner pour Claude Code ou Verdent
```

Copier le bloc pertinent depuis `templates/`, remplacer les chemins entre
chevrons et le fusionner avec les instructions déjà présentes. Ne jamais
écraser un fichier d’instructions existant.

## 5. Tester depuis le projet

Créer un brief dans `mon-projet/`, puis transmettre à l’agent le prompt de
`DEMARRAGE-AGENT.md`. Vérifier ensuite que :

- les pages, preuves et rapports sont dans `mon-projet/` ;
- aucun livrable n’est écrit dans le kit ;
- l’agent cite les commandes réellement exécutées ;
- les limites et preuves non exercées restent visibles.

## Mettre à jour

Remplacer le dossier du kit après avoir conservé le projet séparément. Relancer
les prérequis, le check principal et une démonstration avant de reprendre un
travail existant.
