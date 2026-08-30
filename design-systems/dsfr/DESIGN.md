---
name: DSFR
version: "1.15"
documentation_version_ref: "1.15.2"
package_version_ref: "1.15.2"
status: canonical-local-router
language: fr-FR
source_checked_at: "2026-08-28"
refresh_when:
  - nouvelle_version_dsfr
  - publication
  - claim_conforme
  - doute_périmètre
  - contenu_ia
purpose: "Point d'entrée court pour produire, vérifier ou transmettre des artefacts alignés avec le Système de Design de l'État."
design_md_relation:
  google_format: inspired_not_compliant
  profile_function: "agentic_router_and_design_intent"
  token_source: "tokens.yaml"
  detail_source: "references/"
  primary_consumer: ".claude/skills/dsfr-components"
  migration_consumer: ".claude/skills/dsfr-changelog"
  pictogram_asset_producer: ".claude/skills/generer-pictos-svg-dsfr"
  adopted_method:
    prose_first: true
    typed_token_projection: true
    canonical_section_map: true
    cli_lint_target: false
progressive_disclosure:
  always_load:
    - DESIGN.md
    - tokens.yaml
  load_when_needed:
    index_references: "references/index.md"
    agent_recipes: "references/agent-recipes.md"
    token_coverage: "references/tokens-coverage.md"
    foundations: "references/foundations.md"
    page_shell: "references/page-shell.md"
    components: "references/components-routing.md"
    forms_models: "references/forms-models.md"
    figma_handoff: "references/figma-handoff.md"
    verification: "references/verification.md"
    advanced_rgaa_verification: "references/verification.md"
    ai_content: "references/sources.md"
    sources: "references/sources.md"
  secondary_sources:
    ay11_pre_audit: "git-hors-workflow/ay11-pre-audit"
discovery:
  canonical_path: "design-systems/dsfr/DESIGN.md"
  relative_path: "design-systems/dsfr/DESIGN.md"
  token_file: "design-systems/dsfr/tokens.yaml"
  positive_triggers:
    - DSFR
    - Système de Design de l'État
    - "@gouvfr/dsfr"
    - fr-container
    - fr-btn
    - fr-header
    - fr-footer
  weak_triggers_require_context:
    - page gouv
    - service public français
    - République française
    - Marianne
authority:
  primary: "Documentation officielle du Système de Design de l'État"
  documentation: "https://www.systeme-de-design.gouv.fr/version-courante/fr"
  local_scope: "Routeur opérationnel pour agents ; ne remplace ni la documentation officielle, ni un audit RGAA complet."
llm_operating_policy:
  default_mode: "continuer_avec_limites_explicites"
  ask_only_when:
    - périmètre_légal_ou_marque_incertain
    - domaine_gouv_fr_ou_agrément_absent_pour_publication
    - publication_ou_mise_en_ligne_demandée
    - contenu_administratif_normatif_absent
    - choix_irréversible_ou_coûteux
  do_not_block_for:
    - composant_précis_non_encore_lu
    - version_projet_absente_en_phase_maquette
    - asset_ou_logo_manquant
    - audit_rgaa_non_demandé
    - variante_figma_non_inspectée
proof_labels:
  - officiel_lu
  - local_lu
  - inféré
  - à_vérifier
  - hors_périmètre
claim_language:
  allowed:
    - "aligné DSFR avec limites"
    - "prototype DSFR à vérifier avant publication"
    - "structure inspirée des fondamentaux DSFR"
    - "composants DSFR utilisés selon les sources lues"
  forbidden_without_proof:
    - "conforme DSFR"
    - "conforme RGAA"
    - "prêt pour publication"
    - "usage autorisé de la marque de l'État"
---

# DSFR - routeur agentique local

Ce fichier est le point d'entrée progressif. Il doit rester court. Charger aussi `tokens.yaml` dans tous les cas, puis ouvrir uniquement les références utiles.

Il s'inspire du concept `DESIGN.md` comme charte lisible par agent, mais son contrat local est plus large : guider `dsfr-components`, borner les claims et préserver les preuves nécessaires au contexte DSFR.

Le DSFR vise les sites et services numériques de l'État et les contextes de service public autorisés. Si le périmètre est incertain, produire une composition administrative neutre sans bloc marque, ou demander le contexte seulement si une publication, un droit d'usage ou une reprise de page publique est en jeu.

Ce profil est une **couche de routage et d'abstraction**, pas un miroir de la surface interne des skills routés (comptes de composants natifs, atomes, types de page, générateurs). Cette surface vit dans chaque skill (`SKILL.md` + `--list`) et n'a pas à être réalignée ici quand un skill évolue. Synchroniser uniquement la version DSFR (1.15.2 figée) et les claims/tokens partagés.

## Méthode DESIGN.md adoptée

Le profil reprend la logique Google `DESIGN.md` en deux couches : des tokens de décision lisibles par machine dans `tokens.yaml`, et une prose de jugement dans ce fichier. Les titres locaux restent orientés routage pour préserver le contrat DSFR.

| Section Google | Source DSFR locale | Rôle pour l'agent |
|---|---|---|
| Overview / Brand & Style | `Intention de rendu DSFR` | décrire le caractère attendu sans inventer une esthétique hors État |
| Colors | `tokens.yaml` + `references/foundations.md` | choisir les tokens de décision par usage, pas par goût décoratif |
| Typography | `tokens.yaml` + `references/foundations.md` | garder Marianne par défaut et Spectral pour les cas éditoriaux justifiés |
| Layout & Spacing | `tokens.yaml` + `references/foundations.md` | appliquer grille, breakpoints et espacements DSFR |
| Elevation & Depth | `tokens.yaml` + `references/foundations.md` | préférer surfaces et hiérarchie DSFR aux effets custom |
| Shapes | `tokens.yaml` | garder les rayons et exceptions DSFR nommés |
| Components | `references/components-routing.md` + `dsfr-components` | router vers composants officiels et générateurs existants |
| Do's and Don'ts | `Règle de force`, `Limites connues`, `Garde de publication` | empêcher claims, marque ou composants inventés |

## Intention de rendu DSFR

Produire une interface de service public de l'État, formelle, sobre et orientée démarche ou information. L'écran doit évoquer un service `.gouv.fr` autorisé, pas une landing page SaaS, une vitrine marketing ou une simple esthétique bleu-blanc-rouge.

- Clarté avant expressivité : le contenu, l'orientation et l'action utile priment sur l'effet visuel.
- Composant officiel avant invention : si un composant DSFR existe, l'utiliser ou nommer pourquoi il est écarté.
- Densité lisible : éviter les pages décoratives, mais garder assez d'air pour la compréhension et la navigation clavier.
- Accessibilité visible : labels, focus, aides, erreurs et alternatives ne sont pas des finitions.
- Marque sous condition : Marianne, bloc marque et République française ne sont pas une esthétique générique.

## À faire et à éviter

- Faire : utiliser les composants DSFR existants et citer la source lue.
- Faire : vérifier `components-routing.md`, le skill puis la documentation officielle avant de conclure qu'un composant manque.
- Éviter : produire du `DSFR-like` par palette, Marianne, bloc marque ou rayon de bordure.
- Éviter : traiter un usage partiel ou visuellement ressemblant au DSFR comme une preuve d'usage DSFR ; sans preuve, le marquer prototype ou inspiration avec limites.
- Éviter : ajouter une surcouche graphique, un effet décoratif ou une icône custom quand une règle DSFR ou une icône DSFR/Remix convient.
- Éviter : créer un composant maison sans fallback sémantique, label `à vérifier` et justification.

## Toujours charger

- `design-systems/dsfr/DESIGN.md` : routage, politique LLM, minimum viable, handoff.
- `design-systems/dsfr/tokens.yaml` : couleurs, typographie, grille, espacements, breakpoints, composants structurants.

## Charger selon le besoin

| Besoin | Référence à charger | Pourquoi |
|---|---|---|
| choisir vite la bonne référence locale | `references/index.md` | éviter de relire tout le profil quand le besoin est ciblé |
| appliquer le profil avec `dsfr-components` | `references/agent-recipes.md` | suivre une recette page, composant, formulaire, audit ou publication |
| étendre une décision de token, état ou famille | `references/tokens-coverage.md` | couvrir sans gonfler `tokens.yaml` ni inventer un catalogue officiel |
| couleurs, typo, grille, espacement, médias, icônes, modes, contraste élevé | `references/foundations.md` | appliquer les fondamentaux sans copier toute la doc officielle |
| page HTML complète, publication, header/footer, cookies, données personnelles, mesure d'audience | `references/page-shell.md` | vérifier enveloppe de page, liens légaux, consentement, mesure |
| page ou composant HTML DSFR | `references/components-routing.md` | router vers `dsfr-components`, modèle ou composant officiel |
| pictogramme officiel à copier ou à recolorer, pictogramme absent du DSFR à créer | `.claude/skills/generer-pictos-svg-dsfr/SKILL.md` | produire l’asset SVG (copie officielle depuis le corpus ou le paquet en cache, sinon création déclarée `official: false`) ; l’embarquement HTML reste à `dsfr-components` |
| migration DSFR, comparaison de versions ou changelog | `.claude/skills/dsfr-changelog/SKILL.md` | comparer les bornes et le dépôt réel avant toute décision de montée de version |
| formulaire, connexion, création de compte, erreur | `references/forms-models.md` | partir des blocs fonctionnels et pages types |
| maquette, prototype, handoff design | `references/figma-handoff.md` | raisonner comme guideline Figma textuelle |
| conformité, preuve, claims, audit | `references/verification.md` | calibrer preuves et formulations autorisées |
| transmission ou reprise par un autre agent | `references/verification.md` | distinguer claim final, preuve couverte et non vérifié |
| audit ou pré-audit RGAA | `references/verification.md` puis source AY11 si présente | router vers le skill d'audit et les preuves candidates RGAA |
| texte, image ou vidéo généré ou assisté par IA pour une page publiable | `references/sources.md` | appliquer la note officielle de transparence IA ou marquer `non vérifié` |
| version, URL officielle, sources | `references/sources.md` | vérifier autorité, version et limites |

## Décider vite

- Prototype : continuer avec limites explicites.
- Publication : charger `references/page-shell.md`, `references/verification.md` et `references/sources.md`.
- Claim conforme : refuser, corriger ou abaisser la formulation.
- Hors périmètre État : retirer le bloc marque.
- Contenu IA visible : prévoir le marquage officiel ou écrire `non vérifié`.
- Migration de version : router vers `dsfr-changelog` sans modifier la version cible pendant l'analyse.
- Pictogramme : router l’asset SVG vers `generer-pictos-svg-dsfr` ; `dsfr-components` n’embarque qu’un pointeur `<use href>` de même origine.

## Minimum Viable DSFR

Si le contexte manque, continuer avec ce passage minimal plutôt que bloquer.

Pour une page :

- `html lang="fr"` ;
- `header`, `main`, `footer` si la page est complète ;
- grille `fr-container`, `fr-grid-row`, `fr-col-*` ou équivalent DSFR documenté ;
- tokens de décision pour couleurs et surfaces ;
- composants officiels nommés ;
- liens réels ou explicitement signalés comme non finalisés ;
- liens d'évitement en début de page pour toute page complète, avec au minimum `Accéder au contenu` ;
- labels, focus visible et ordre de titres plausibles ;
- aucun `href="#"` résiduel dans un livrable ;
- version projet nommée, ou `version projet à vérifier` ;
- mobile et desktop vérifiés, ou limites nommées.

Pour un composant :

- Un fragment ou composant isolé ne doit pas inventer d'enveloppe de page.
- source du composant nommée ;
- structure sémantique ;
- variantes et états principaux ;
- attributs d'accessibilité nécessaires ;
- pas de CSS custom intrusif ;
- écart marqué si la documentation officielle n'a pas été lue.

Ce passage minimal autorise un artefact aligné DSFR et reprenable. Il n'autorise pas à dire `conforme DSFR`.

## Garde de publication

Avant toute publication, mise en ligne ou reprise d'une page publique :

- vérifier le périmètre DSFR : service de l'État, domaine `.gouv.fr`, opérateur avec agrément ou mandat explicite ;
- pour un opérateur, ne pas dissocier DSFR et domaine `.gouv.fr` : sans preuve d'agrément SIG ou mandat, retirer bloc marque et claim DSFR ;
- charger `references/page-shell.md`, `references/verification.md` et `references/sources.md` ;
- contrôler en-tête, pied de page, liens d'évitement, mentions obligatoires, données personnelles, cookies, mesure d'audience et licence ;
- si un texte, une image ou une vidéo est produit avec aide IA, charger la source officielle et prévoir la mention de transparence ;
- nommer le mode sombre ou contraste élevé comme vérifié, non exposé ou `non vérifié` ;
- si le périmètre n'est pas prouvé, retirer le bloc marque et revendiquer seulement `structure inspirée des fondamentaux DSFR`.

## Contrat avec les skills DSFR

`dsfr-components` consomme ce profil comme contexte partagé. Le skill garde ses propres scripts, options, listes de composants, générateurs et critères de fin.

`dsfr-changelog` prend en charge les comparaisons de versions et la préparation d'une migration depuis le dépôt réel. Il documente les écarts, mais n'effectue jamais lui-même de modification de la version cible du pack.

`generer-pictos-svg-dsfr` produit les assets SVG de pictogrammes : copie exacte d’un officiel (depuis le corpus embarqué ou le paquet `@gouvfr/dsfr` en cache, contrôlée par `sha256`), recoloration `--minor-color` tracée, ou création `original-dsfr-like` toujours `official: false` et auditée. Le pack le livre sans les SVG officiels ; sans paquet en cache, il répond `NOT VERIFIED: source officielle absente`.

| Branche du skill | Ce profil apporte | À ne pas faire ici |
|---|---|---|
| page complète | intention DSFR, claims autorisés, garde de publication, références à charger | recopier les templates ou options de `generate_page.py` |
| composant isolé | règle de non-invention, source à citer, limites de fragment | créer une enveloppe de page autour du fragment |
| formulaire | exigences générales de labels, aides, erreurs et preuves | dupliquer les patterns détaillés du skill |
| audit DSFR ponctuel | niveaux de preuve, formulations et limites | produire un verdict RGAA global |

Si le skill et ce profil divergent, suivre la source la plus proche du livrable réel : scripts et références du skill pour la génération, documentation officielle pour le DSFR, ce profil pour le routage et les claims.

## Scénarios

| Demande | Route | Formulation de sortie |
|---|---|---|
| Page DSFR statique | `dsfr-components` + `components-routing.md` + `page-shell.md` | `aligné DSFR avec limites` |
| Prototype ou maquette DSFR | `agentic-design-harness` + `figma-handoff.md` | `prototype DSFR à vérifier avant publication` |
| Formulaire administratif | `forms-models.md` + `components-routing.md` | `composants DSFR utilisés selon les sources lues` |
| Audit DSFR/RGAA | skill d'audit + `verification.md` | verdict seulement après preuves |
| Style administratif hors État | composition neutre | `inspiration administrative neutre, pas DSFR officiel` |

## Règle de force

| Force | Action |
|---|---|
| obligatoire avant publication | vérifier, corriger ou demander |
| recommandé en prototype | appliquer si possible, sinon marquer `à vérifier` |
| différable avec label | continuer et nommer la limite |
| interdit sans preuve | retirer l'affirmation ou abaisser le statut |

Ne jamais revendiquer `conforme DSFR`, `conforme RGAA`, `prêt pour publication` ou `usage autorisé de la marque de l'État` sans preuve dédiée.

Ne pas utiliser Marianne, le bloc marque ou République française comme simple style graphique hors périmètre autorisé.

## Guide d'itération agent

1. Identifier la branche : page, composant, formulaire, audit ponctuel, publication ou inspiration administrative hors périmètre.
2. Charger le minimum : `DESIGN.md`, `tokens.yaml`, puis seulement les références utiles.
3. Produire ou corriger avec les composants et tokens disponibles ; ne pas inventer une classe, un composant ou un droit d'usage.
4. Vérifier la preuve minimale adaptée au risque : inspection HTML, liens, ARIA, capture, navigateur, audit spécialisé ou limite nommée.
5. Formuler le claim final avec les expressions autorisées, puis lister ce qui reste non vérifié.

## Limites connues

- `tokens.yaml` est un sous-ensemble de décision, pas un catalogue officiel complet.
- Les références locales ne prouvent pas qu'un composant, modèle ou token absent n'existe pas dans la documentation officielle.
- Les générateurs de `dsfr-components` prouvent une structure générée, pas une conformité DSFR ou RGAA globale.
- La publication exige une preuve de périmètre, de marque, de liens légaux, de données personnelles, de cookies et de mesure d'audience.
- Le format Google `DESIGN.md` est une inspiration méthodologique ; ce fichier n'est pas une cible stricte du CLI `@google/design.md`.
- La projection de tokens plus large aide les agents ; elle ne remplace ni les variables CSS du paquet DSFR, ni les classes documentées.

## Handoff minimal

```text
Statut DSFR :
Claim final autorisé :
Décision : continuer / corriger / demander / auditer
Sources lues :
Composants utilisés :
Tokens ou classes structurantes :
Niveau de règle :
Labels de preuve :
Preuve exécutée :
Ce que la preuve couvre :
Ce qui reste non vérifié :
Sources non lues :
Limites :
Prochaine vérification :
```

Critère de fin : un autre agent peut reprendre le travail sans relire la conversation.

Note : `git-hors-workflow/ay11-pre-audit` est un chemin relatif à la racine du workspace hôte, pas à ce dossier DSFR.
