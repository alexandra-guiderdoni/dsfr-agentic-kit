# DSFR Agentic Kit

Boîte à outils autonome pour aider un agent IA à produire et à vérifier des
interfaces publiques françaises fondées sur le Système de Design de l’État.

## Raison d’être

> Permettre à un agent IA de produire des interfaces publiques françaises
> utiles sans confondre génération plausible et conformité prouvée.

En quatre verbes : **router, contraindre, générer, vérifier**.

- L’agent est **routé** : `design-systems/dsfr/DESIGN.md` lui indique les
  sources à charger et les revendications permises.
- Il est **contraint** : `tokens.yaml` encadre couleurs, typographie, grille et
  composants.
- Il **génère** : le skill `dsfr-components` transforme notamment un
  `page.json` en page HTML DSFR, avec liens sûrs, identifiants uniques, classes
  contrôlées et HTML brut tracé.
- Il est **vérifié** : les contrôles locaux prouvent uniquement ce qu’ils
  exercent et nomment ce qui reste non vérifié.

Parcours humain : **choisir, installer, démontrer, vérifier**.

## Démarrage en cinq minutes

Depuis la racine du kit :

```bash
bash scripts/check-prerequisites.sh
bash scripts/check-agentic-design-pack.sh
bash scripts/demo-dsfr-assembled-page.sh --quiet
```

Le diagnostic ne réalise aucune installation. La démonstration écrit sa page
dans un dossier temporaire et laisse le kit intact.

## Persister une session cloud et découvrir les skills

Le fichier `scripts/amorcage-session-cloud.sh` est la procédure de
reconstruction persistante. Conserver une copie de ce fichier dans le Projet
Cowork, qui survit à la session, puis l’exécuter au début d’une nouvelle
session :

```bash
bash amorcage-session-cloud.sh
```

Le script clone ou met à jour le kit en `--ff-only`, lit `python_minimum` et
`dsfr_version` dans le manifeste, prépare les dépendances et le cache DSFR,
puis rejoue les contrôles et les démonstrations. `--no-check` prépare seulement
l’environnement ; `--update` refuse une mise à jour si le clone est modifié.
Le script rend la session reconstructible : il ne rend pas le conteneur
permanent.

Pour une découverte native des skills dans Claude/Cowork, le kit fournit le
catalogue `.claude-plugin/marketplace.json`. Après publication du dépôt :

```text
/plugin marketplace add alexandra-guiderdoni/dsfr-agentic-kit
/plugin install dsfr-agentic-kit@dsfr-agentic
```

Le marketplace expose les skills du kit, pas les scripts de contrôle, le
profil DSFR ni le cache officiel. Conserver le clone pour les vérifications
complètes. Pour produire une archive plugin locale rattachée à un commit :

```bash
bash scripts/build-plugin.sh --version 0.1.0
```

L’archive est écrite hors du dépôt et le build vérifie la parité des 18 skills,
les `SKILL.md`, les renvois relatifs et la provenance Git.

Lire ensuite :

- [l’accueil destiné à l’agent](DEMARRAGE-AGENT.md) ;
- [l’installation et le test](documentation/INSTALLER-ET-TESTER.md) ;
- [le mode opératoire humain](documentation/MODE-OPERATOIRE.md).

## Utiliser le kit avec un projet

Le kit reste en lecture seule et les livrables vivent dans un projet voisin :

```text
workspace/
├── dsfr-agentic-kit/     # boîte à outils en lecture seule
└── mon-projet/           # briefs, pages, preuves et rapports
```

Dire à l’agent où se trouvent ces deux dossiers. Le prompt prêt à adapter est
fourni dans `DEMARRAGE-AGENT.md`. Les fichiers de `templates/` sont à fusionner
avec les instructions existantes, jamais à écraser par-dessus elles.

## Choisir le parcours

| Besoin | Entrée principale | Résultat attendu |
| --- | --- | --- |
| Générer une page simple | type de page, titre, contenu | page HTML |
| Assembler une page depuis un brief | `brief.md`, puis `page.json` | HTML et preuve |
| Produire ou intégrer un pictogramme | besoin d’asset explicite | SVG tracé ou pointeur |
| Comparer deux versions DSFR | versions source et cible | analyse de migration |
| Auditer l’intégration DSFR en détail | échantillon multi-pages | règles par instance, extraits du DOM rendu, qualification et rapport filtrable |
| Pré-auditer une page publique | URL ou HTML isolé | constats et fiches candidates |
| Créer une campagne RGAA + DSFR reproductible | URL, échantillon et chemins AY11/skills | campagne reprenable, matrices et rapports séparés RGAA/DSFR |
| Rendre les audits avec le builder DSFR | résultats RGAA/DSFR structurés | portail commun, rapports complets et vues par page en `brand_mode: neutral` |
| Approfondir un audit RGAA | campagne et preuves navigateur | règles par instance, code observé, qualification humaine et revue des 258 tests |
| Auditer selon le RGAA | périmètre et échantillon | rapport borné aux tests réalisés |
| Auditer selon WCAG 2.2 | URL ou HTML | rapport WCAG avec limites |
| Corriger après audit | audit existant et code autorisé | correctifs puis vérification |

Règle de routage accessibilité : un site public multi-pages utilise
`audit-rgaa-creator` ; une page publique isolée utilise
`pre-audit-rgaa-dsfr` ; une page ou un fichier hors secteur public avec demande
WCAG explicite utilise `audit-accessibilite-web`.

Le point d’entrée DSFR est `design-systems/dsfr/DESIGN.md`. Chaque capacité
spécialisée possède ensuite son propre `.claude/skills/<nom>/SKILL.md`.

Pour une campagne multi-pages combinant RGAA, vérification DSFR bornée, AY11,
Playwright et les skills, utiliser `scripts/audit-rgaa-creator.sh` et lire
[`documentation/AUDIT-RGAA-CREATOR.md`](documentation/AUDIT-RGAA-CREATOR.md).
Le skill `audit-dsfr-complet` porte le catalogue versionné de règles par
instance. Ses rapports distinguent intégration et migration, citent le DOM
rendu observé et la structure attendue, et n’emploient jamais une absence de
signal comme claim de conformité globale. `audit-report-dsfr` adapte ensuite
les JSON canoniques au builder DSFR pour produire le portail commun, les
rapports complets et les vues détaillées par page.

## Ce que les contrôles vérifient

Le check principal vérifie notamment :

- l’absence de surfaces de fabrication ou de chemins personnels ;
- la parité entre les skills déclarés dans le manifeste et les dossiers livrés ;
- les chemins et références nécessaires à l’exécution ;
- le routeur et les scénarios négatifs DSFR ;
- les schémas de page assemblée, les liens sûrs, les identifiants et la trace
  de l’HTML brut ;
- les composants et pictogrammes livrés ;
- la fidélité des tokens et classes au paquet DSFR officiel lorsque celui-ci
  est présent dans le cache local ;
- une génération réelle depuis le kit autonome.

Les `[WARN]` et `[SKIP]` explicitent une preuve non exercée. Ils ne doivent pas
être reformulés en succès.

## Ce que ce kit ne prouve pas

- Un check vert du kit ne prouve pas la conformité DSFR ou RGAA d’une page.
- Un audit automatisé ne remplace pas les vérifications manuelles applicables.
- Le droit d’utiliser la marque de l’État et la décision de publication restent
  des décisions humaines distinctes.
- Le code du DSFR et les pictogrammes officiels ne sont pas redistribués.

## Prérequis

- Python 3.10 minimum, 3.12 recommandé ;
- PyYAML et `jsonschema`, ou `uv` capable de les fournir ;
- Node 20 minimum, Node 22 recommandé, avec `npm` et `npx` ;
- Playwright Python facultatif pour le kit seul, mais requis dans
  l’interpréteur de la campagne lorsque `browser_checks`, `rgaa_checks` ou
  `dsfr_checks` est actif ; Playwright Node reste séparé et optionnel ;
- `rsync` requis pour la démo vitrine (`brew install rsync` ou
  `apt-get install rsync`).

Pour imposer le même interpréteur Python à la sonde des prérequis et à la
campagne, définir `DSFR_AUDIT_PYTHON` avant les contrôles.

Le paquet officiel DSFR peut être placé dans
`~/.cache/dsfr-official-cache`. En mode hors ligne, son absence produit un saut
explicite au lieu d’un téléchargement silencieux.

## Licence

Le kit est placé sous Licence Ouverte 2.0 / Open Licence 2.0 (Etalab), voir
`LICENSE`. Les conditions officielles du DSFR continuent de s’appliquer au
paquet `@gouvfr/dsfr` utilisé à l’exécution.

État : prototype standalone local, non publié.
