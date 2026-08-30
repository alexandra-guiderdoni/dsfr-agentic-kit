# Sources pour le design agentique

Ce fichier sert à classer les sources avant de produire un artefact design. Il ne remplace pas les fichiers locaux du projet : il aide seulement à décider quoi lire et quel poids donner à chaque source.

## Hiérarchie des sources

1. Sources locales du projet : `AGENTS.md`, `CLAUDE.md` utile, `DESIGN.md`, tokens, CSS, composants, assets, screenshots, tests visuels et commandes du dépôt.
2. Sources officielles et actuelles : documentation Anthropic/Claude, Google `design.md`, standards de design tokens, documentation du runtime ou de l'outil utilisé.
3. Sources de recherche : STORM, Co-STORM et méthodes d'enquête multi-perspectives pour élargir les questions avant de figer un workflow.
4. Sources communautaires ou prompts tiers : utiles pour repérer des patterns, jamais source d'autorité sans recoupement.

Les liens externes ci-dessous sont des pointeurs, pas une preuve d'actualité. Si une décision dépend d'une version, d'une fonctionnalité récente, d'une disponibilité d'outil ou d'un claim officiel, ouvrir la source actuelle pendant la tâche ou marquer `non vérifié`.

## Sources à consulter selon le cas

| Cas | Sources prioritaires | Usage dans le harnais |
|---|---|---|
| Reproduire une expérience Claude Design-like | Annonce Claude Design, documentation Claude Code Artifacts, prompts tiers recoupés | Traduire en contrat agnostique : artefact, sources, vérification, export, handoff |
| Créer ou lire une charte persistante | Google `design.md`, `DESIGN.md` local, tokens CSS ou DTCG | Séparer tokens structurés et prose de design, marquer les inférences |
| Produire ou vérifier un artefact DSFR | `design-systems/dsfr/DESIGN.md`, `design-systems/dsfr/tokens.yaml`, références ciblées sous `design-systems/dsfr/references/`, documentation officielle DSFR, skill `dsfr-components` si page ou composant HTML | Charger le routeur DSFR et les tokens, puis seulement les références utiles : foundations, page-shell, components-routing, forms-models, figma-handoff, verification ou sources |
| Produire un HTML autonome | Claude Code Artifacts, contraintes locales frontend, navigateur | Livrer un fichier inspectable, partageable et vérifié |
| Travailler avec plusieurs agents | `config/agent-capabilities.yaml`, guide subagents Codex, hooks/mémoire/skills Claude | Nommer capacité, adaptateur, preuve et condition d'arrêt sans dépendre d'un modèle |
| Recherche profonde préalable | STORM et Co-STORM | Construire une matrice de perspectives, sources et inconnues avant de spécifier |

## Références externes suivies

- Claude Design, annonce officielle Anthropic : <https://www.anthropic.com/news/claude-design-anthropic-labs>
- Claude Code Artifacts : <https://code.claude.com/docs/en/artifacts>
- Claude Code skills : <https://code.claude.com/docs/en/skills>
- Claude Code memory : <https://code.claude.com/docs/en/memory>
- Claude Code hooks : <https://code.claude.com/docs/en/hooks>
- Claude Code subagents : <https://code.claude.com/docs/en/sub-agents>
- Claude Code settings : <https://code.claude.com/docs/en/settings>
- Anthropic, Building effective agents : <https://www.anthropic.com/engineering/building-effective-agents>
- Anthropic, Effective context engineering : <https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents>
- Google Labs `design.md` : <https://github.com/google-labs-code/design.md>
- Google `design.md` README brut : <https://raw.githubusercontent.com/google-labs-code/design.md/main/README.md>
- Google `design.md` philosophy : <https://raw.githubusercontent.com/google-labs-code/design.md/main/PHILOSOPHY.md>
- Google Stitch et `design.md` : <https://blog.google/innovation-and-ai/models-and-research/google-labs/stitch-design-md/>
- W3C Design Tokens Community Group : <https://tr.designtokens.org/format/>
- Agent Skills standard : <https://agentskills.io/>
- STORM, Stanford : <https://storm-project.stanford.edu/research/storm/>
- STORM paper : <https://arxiv.org/abs/2402.14207>
- Co-STORM paper : <https://arxiv.org/abs/2408.15232>
- STORM/Co-STORM implementation : <https://github.com/stanford-oval/storm>
- Prompt tiers CL4R1T4S Claude Design : <https://raw.githubusercontent.com/elder-plinius/CL4R1T4S/main/ANTHROPIC/Claude-Design-Sys-Prompt.txt>

## Règles de reprise du prompt tiers

- Reprendre les invariants, pas la formulation : lire les sources, créer un artefact inspectable, préserver les assets nécessaires, vérifier par rendu, transmettre clairement.
- Classer cette source `faible/non officielle` dans la matrice, même si elle est utile.
- Ne pas copier des blocs longs ou une identité de runtime dans une règle durable du harnais.
- Adapter les mécanismes propres à Claude en équivalents agnostiques : commentaire, localStorage, capture, diff, vérification indépendante ou script local.

## Écarts volontaires avec CL4R1T4S

- Ne pas reprendre les outils hôtes `done`, `show_to_user`, `fork_verifier_agent`, `questions_v2`, `copy_starter_component` ou `register_assets` comme obligations transverses : les traduire en preuves locales disponibles.
- Ne pas reprendre le helper d'appel Claude depuis HTML comme invariant : il dépend du viewer Claude et n'est pas portable.
- Ne pas reprendre le protocole complet `EDITMODE` comme règle obligatoire : l'équivalent agnostique est un tweak visible, persisté et vérifiable ; le protocole hôte reste optionnel si l'environnement le fournit.
- Ne pas reprendre la règle d'email domain pour l'IP : le harnais exige plutôt des droits d'usage explicités dans le mini-brief et refuse la reproduction distinctive quand ces droits sont absents.
