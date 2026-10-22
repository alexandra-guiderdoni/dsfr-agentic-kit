# Installer et tester DSFR Agentic Kit

Ce guide place le kit à côté du projet qui recevra les livrables. Le kit reste
remplaçable et en lecture seule pendant son utilisation.

Pour le profil complet ou léger et le verrou automatique des campagnes,
suivre [le parcours de distribution](DISTRIBUTION-ET-PROFILS.md).

## 1. Vérifier les prérequis

Depuis la racine du kit :

```bash
bash scripts/check-prerequisites.sh
```

Le diagnostic ne réalise aucune installation. Une dépendance facultative
absente produit un avertissement ; une dépendance requise absente fait échouer
la commande avec l’action attendue.

## 1 bis. Reconstituer une session Cowork

Un conteneur cloud est éphémère. Conserver `scripts/amorcage-session-cloud.sh`
dans un Projet Cowork persistant, puis lancer au début de chaque session :

```bash
bash amorcage-session-cloud.sh
```

Le script clone ou met à jour le dépôt en `--ff-only`, refuse une mise à jour
sur un clone modifié, lit les versions Python et DSFR dans le manifeste,
prépare le cache DSFR et `rsync`, puis rejoue les contrôles. Utiliser
`--no-check` pour préparer uniquement l’environnement et `--update` pour
forcer explicitement la vérification d’une mise à jour. Le fichier persistant
rend l’installation reproductible ; il ne prolonge pas la durée de vie du
conteneur.

## 1 ter. Découvrir les skills comme plugin

Le dépôt contient `.claude-plugin/marketplace.json`, catalogue versionné pour
Claude/Cowork. Après publication du dépôt, ajouter le marketplace puis
installer le plugin :

```text
/plugin marketplace add alexandra-guiderdoni/dsfr-agentic-kit
/plugin install dsfr-agentic-kit@dsfr-agentic
```

Cette voie Git fournit le checkout complet dans le cache natif : skills,
scripts et profil DSFR y sont accessibles. Les dépendances et le paquet
officiel restent à préparer séparément. La version consommée doit être
[verrouillée et vérifiée](CONSOMMATION-VERSIONNEE.md). Une archive de skills
locale, de périmètre plus restreint, peut être reconstruite depuis le clone :

```bash
bash scripts/build-plugin.sh --version 0.1.0
```

La sortie va hors du dépôt. Le build échoue si les skills déclarés, les
`SKILL.md`, les renvois relatifs ou la provenance ne sont pas cohérents.

### Convention des skills

Chaque `SKILL.md` commence par un frontmatter portable contenant `name` et
`description`, puis `argument-hint` lorsque le skill accepte une commande et
`allowed-tools` lorsque des outils sont nécessaires. Les capacités navigateur
ou les serveurs MCP sont des options décrites dans le corps du skill ; ils ne
sont pas annoncés comme outils obligatoires dans le frontmatter, car leur
disponibilité dépend de l’hôte. Les clés `whenToUse`, `user-invocable`,
`background` et les versions propres à un runtime ne font pas partie du
contrat du kit.

## 2. Vérifier le kit

```bash
bash scripts/check-agentic-design-pack.sh
```

Le contrôle inspecte l’inventaire, les chemins, les règles de génération et
les régressions produit. Il lance également une génération dans un dossier
temporaire.

Les nouvelles traces de routage Codex se rangent explicitement hors du kit :
`python3 design-systems/scripts/check-dsfr-runtime-trace.py run --output-dir /chemin/projet/traces`.
Le mode `normalize` refuse également une destination interne, y compris
redirigée par lien symbolique. Le contrôle `check` peut lire les traces
historiques livrées sans les modifier.

Lorsque le paquet officiel DSFR n’est pas disponible dans le cache local, le
contrôle de fidélité officiel peut être marqué `[SKIP]`. Ce saut ne vaut pas
preuve de fidélité.

Le contrôle exige un dépôt propre, fichiers ignorés compris. Après une
exécution manuelle de Python, supprimer les caches produits :

```bash
find . -name __pycache__ -type d -exec rm -rf {} +
```

Deux contrôles peuvent être lancés seuls, sans dépendance externe :

```bash
bash scripts/tests/check-standalone-boundary.sh
bash scripts/tests/check-skills-paths-agnostic.sh
```

Le premier vérifie qu’aucun marqueur interne ni chemin personnel n’est livré,
qu’aucun lien symbolique ni résidu Python ne subsiste, et que l’inventaire des
skills correspond au manifeste. Son périmètre est le contenu versionné : un
fichier ignoré par Git n’est jamais publié et ne le fait donc pas échouer.
Hors dépôt Git, il inspecte l’arbre complet.

## 2 bis. Contribuer au produit canonique

Les sources se maintiennent dans ce dépôt, selon [le guide de maintenance](MAINTENANCE.md).
Le garde historique de zone synchronisée reconnaît l’autorité du kit et ne
demande plus de reporter ses corrections dans un workflow personnel. Aucun
hook global ni réglage utilisateur n’est nécessaire.

## 3. Exécuter les démonstrations

```bash
bash scripts/demo-dsfr-assembled-page.sh --quiet
bash scripts/demo-dsfr-vitrine.sh --quiet
```

La démo vitrine nécessite `rsync`. Le diagnostic des prérequis signale son
absence comme un avertissement, car le reste du kit n’en dépend pas.

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

Depuis un clone propre, utiliser `git pull --ff-only`, relire `CHANGELOG.md` et
`config/agentic-design-packages.yaml`, puis relancer les prérequis, le check
principal et une démonstration avant de reprendre un travail existant. Si un
plugin est utilisé, reconstruire ensuite une archive avec une nouvelle version
et la réinstaller : la version distingue les contenus mis en cache.
