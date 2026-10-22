# Journal des versions

## Installation utilisateur autonome — 22 octobre 2026

- chargeur de confiance maintenu dans le kit, avec cache vérifié en lecture
  seule et sélection explicite de la version ;
- installation commune aux agents, adoption avec sauvegardes, liens de
  compatibilité facultatifs et retour arrière refusant les modifications tierces ;
- anciennes versions et qualifications conservées, sans plugin obligatoire.

## Parcours CLI Codex confiné — 22 octobre 2026

- politique macOS de confinement externe pour `codex exec` et Chromium,
  avec kit immuable, workflow interdit et écritures bornées ; les parents
  du cache natif sont protégés contre les déplacements ;
- interpréteur `DSFR_AUDIT_PYTHON` respecté dès l’entrée du wrapper de
  campagne ; valeur invalide refusée sans repli, sélection automatique préservée.

## Installation native Codex — 22 octobre 2026

- catalogue Codex dérivé des mêmes profils complet et léger, avec transport
  Git SSH reconnu par l’hôte et politiques d’installation explicites ;
- manifeste généré par Codex comparé exactement au catalogue verrouillé,
  sans tolérer d’autres fichiers, des clés ajoutées ou un exécutable ;
- catalogue Claude, sources des compétences et verrous des consommateurs
  existants conservés.

## Réception et clôture du harnais autonome — 22 octobre 2026

- fraîcheur calculée avec le catalogue effectivement sélectionné par `--rules`,
  empreinte et nombre de règles tracés, catalogue non canonique signalé ;
- qualification en deux passages, y compris sans groupe à arbitrer ; reçu
  de phase et empreinte de la fiche humaine conservée ;
- documentation structurante alignée sur les profils livrés et leur portée ;
  réception et bascule des consommateurs tracées séparément.

## Profils et campagnes versionnées — 22 octobre 2026

- profils marketplace complet et léger issus des mêmes sources : 18 et
  17 skills exposés, sans fork des moteurs ni ressources ;
- préparation explicite du verrou d’un cache natif, sans clone permanent ;
- vérification automatique avant les écritures de campagne, refus d’une
  divergence et de l’adoption silencieuse d’une campagne historique ;
- protection du cache contre le bytecode des processus enfants en appel Python
  direct ; contrôle des profils dans le checkout explicitement ciblé ;
- clones Git compatibles avec leurs fichiers ignorés, tout en contrôlant les
  fichiers versionnés ; caches natifs maintenus stricts ;
- retrait du contournement masqué `--allow-inside-kit` ; alias et consommateurs
  actifs préservés, réception et bascule distinctes de cette livraison.

## Source unique et consommation versionnée — 22 octobre 2026

- #6 : contrat `kit.lock`, vérificateur explicite et refus des divergences ;
- #7 : trois scripts de recette et leur retour d’expérience publiés dans le
  dépôt privé de recettes, synthèse et protection des chemins génériques
  maintenues dans le kit ;
- #10 : autorité du kit et maintenance directe documentées, garde historique
  adapté ; refus des exports activé et publié dans le workflow avant le kit ;
- publication coordonnée des gardes, du kit puis du verrou des recettes ;
  bascule des consommateurs et migration de preuves brutes hors de ce lot.


## Cadrage du harnais DSFR autonome — 21 octobre 2026

- [PRD de migration](documentation/specs/2026-10-21-harnais-dsfr-autonome.md) :
  kit cible canonique et autonome, workflow personnel consommateur facultatif,
  profil léger issu des mêmes sources et AY11 maintenu externe ;
- critères d’installation isolée, de reprise versionnée et de parité définis
  avant tout retrait des anciens circuits ; aucune migration exécutée.
- [Issue #9](https://github.com/alexandra-guiderdoni/dsfr-agentic-kit/issues/9)
  ouverte pour éprouver la chaîne complète avant le découpage de la migration.
- cinq précisions de Fable intégrées au PRD et à l’exploration : racines
  installées, archive/marketplace, profil léger, identité immuable du kit
  et examen de `--allow-inside-kit` ; aucun comportement du produit modifié.

## Retours ShipGuard sur DSFR 1.15.4 — 21 octobre 2026

Export depuis la source `9a1b96676275b37d723bc1a3eb854f52e3858e9e`.

- exemption du rapport historique bornée à son empreinte reçue ; tout
  ajout au même chemin est refusé, y compris un texte ordinaire ;
- rapport, archives et autres zones propres préservés ; recette complète
  du kit réussie avant la copie ;
- exporteur source corrigé pour préserver aussi le fichier Git des
  worktrees ; copie complète exercée, lien Git et HEAD conservés.

## Migration DSFR 1.15.4 — 21 octobre 2026

Export direct depuis la source
`d4222680b32e346ec4cedb2a775e4baad5bcecf3`, avec l’overlay du kit.

- cible active 1.15.4 pour les générateurs, ressources des nouvelles pages,
  profil, inventaire, catalogue et nouveaux rapports ;
- tags statiques groupés en `span`, tags isolés et liens/boutons conservés ;
  audit acceptant les balises textuelles valides sans interdire les anciens `p` ;
- couverture dimensionnelle reprenant les versions des résultats, bornes des
  constats historiques préservées, pictogrammes revérifiés sans changer les SVG ;
- découverte dynamique des sondes AY11 reçue avec `probe_matrix.py` et ses
  tests ; décomptes courants issus des catalogues de campagne ;
- contre-revue 1.15.3 préservée comme rapport historique propre au kit ;
  contrôle de portabilité distinguant ce rapport et les traces observées des
  dépendances actives, avec cas négatifs ;
- archives, qualifications humaines, outillage, tickets et campagne Douane
  figée en 1.15.2 conservés ; aucune publication ni conformité générale déclarée.

## Migration DSFR 1.15.3

Premier export appliqué depuis la source par `export-dsfr-agentic-kit.sh` ;
les zones propres du kit (outillage et livrables Virginie, tickets, tests
visuels, documents) ne sont ni comparées ni écrites par l'export.

- cible du kit portée de `@gouvfr/dsfr@1.15.2` à `1.15.3` : profil, routeur,
  sources, typographie (nouvelle Marianne), `runtime.dsfr_version` de
  l'amorçage cloud, replis de version des générateurs et des contrôles ;
- bandeau d'information aligné sur `notice.ejs` 1.15.3 : titre porté par un
  niveau de titre (`h2` par défaut, paramètre `heading`), description en
  paragraphe, aucun `role`, avertissement si le titre n'explicite pas la
  nature du message ;
- badges en `span` dans les groupes ; état des champs porté par le groupe
  seulement, message dans `fr-messages-group`, validation client alignée ;
  variante `fr-search-bar--labelled` ;
- catalogue de règles DSFR : cible 1.15.3, structure du bandeau, règle du
  champ en groupe recentrée (`DSFR-INPUT-ERROR-STATE-002`) et nouvelle règle
  du champ hors groupe (`DSFR-INPUT-ERROR-STATE-003`) ; toute archive
  d'audit portant l'ancienne empreinte devient `CATALOGUE_OBSOLETE`, la
  campagne Douane P01 à P09 reste figée en 1.15.2 ;
- pages assemblées régénérées, inventaire de couverture et profil de style
  des pictogrammes régénérés sur le paquet 1.15.3, cas `v1.15.2 → v1.15.3`
  du collecteur de changelog.

## Fiabilisation des audits DSFR et RGAA

- correction du markup généré des groupes de boutons DSFR en `ul/li`, avec
  contrôle croisé entre le générateur, les exemples et l’évaluateur ;
- ajout des portées de version explicites aux règles DSFR et distinction entre
  écart d’intégration, migration et contrôle non exercé ;
- embarquement du référentiel RGAA 4.1.2 (106 critères et 258 tests), avec
  AY11 conservé comme collecteur optionnel ;
- ajout d’un scan axe-core direct via Playwright, de son mapping RGAA borné et
  d’une trace des violations non mappées ;
- correction des faux négatifs sur les liens vides et les champs étiquetés par
  `title`, et généralisation de l’heuristique de changement de langue ;
- blocage explicite des refus réseau (`BLOQUÉ-INFRA`) et refus des sorties
  écrites dans le clone du kit ;
- rapports détaillés RGAA/DSFR produits par le builder commun, sans claim de
  conformité globale.
- suppression du reliquat de score global dans la procédure de contournement
  Cloudflare.

## Nettoyage du harnais et portabilité

- alignement du routage et de la qualification sur les skills RGAA/DSFR v2,
  sans taux ou score global produit par les skills unitaires ;
- suppression des données de mission tierce, des transcripts de conversation
  et du prompt de campagne propre à un site audité ;
- ajout d’un gabarit neutre de rejeu, d’un contrôle de frontmatter, de renvois
  morts, de clôture Markdown et de chemins personnels ;
- sortie PNG des pictogrammes portable entre macOS et Linux, avec moteur
  réellement utilisé tracé ;
- les générateurs `generate-virginie-*` restent livrés pour la sortie par
  composant demandée par Virginie, tandis que leurs hôtes de campagne sont
  fournis par le projet consommateur.

## Fiabilité du rejeu et diagnostics navigateur

- invalidation explicite des phases de rapport dérivées lorsqu’une phase amont
  est rejouée, avec le statut `À REJOUER` et régénération automatique lorsque
  ces phases sont sélectionnées ;
- `resume --only` signale désormais les phases aval invalidées qui n’ont pas été
  rejouées et retourne un statut partiel ;
- contrôle bloquant de Playwright Python dans l’interpréteur sélectionné par
  AY11 pour les phases navigateur, et contrôle distinct de Playwright Node
  utilisé par les démos JavaScript ;
- validation du schéma de campagne dès le prévol, avant l’écriture du runtime
  navigateur, et sonde `playwright.async_api` alignée sur l’interpréteur choisi ;
- ajout du bloc `browser.launch` dans `campaign.yaml` pour gouverner le mode
  headless, le proxy, les arguments, le canal et l’exécutable, avec trace
  expurgée de la configuration effective ;
- validation bloquante des pages DSFR dont l’empreinte de catalogue est
  obsolète ou mélangée, avec exception documentaire explicite
  `--allow-stale-catalog` pour les synthèses d’archives ;
- test des prérequis indépendant de l’emplacement système ou utilisateur de
  Playwright Python, import tardif du retest P06 et correction de son chemin de
  staging ;
- diagnostic Playwright sans effet de bord, avec suggestion utilisant
  l’interpréteur sélectionné et test portable sous Linux ;
- manifeste Virginie enrichi de `errors`, checklist alignée sur les clés
  réellement livrées et suppression du lien parent en mode `--no-index`.

## Frontière d’écriture des pipelines

- les quatre pipelines Virginie/P06 exigent un projet de travail séparé,
  partagent une garde de destination et déplacent leurs sorties et leur verrou
  hors du clone du kit ;

## Validation canonique du générateur

- intégration du contrôle du générateur DSFR à la validation produit canonique,
  avec propagation des échecs et scénario négatif vérifiant leur visibilité ;

## Durabilité d’installation et distribution

- correction de `generate-p06-form-annex.py` pour restaurer la compatibilité
  Python 3.10 annoncée par le manifeste ;
- ajout du bootstrap `scripts/amorcage-session-cloud.sh`, qui reconstruit une
  session cloud depuis les versions du manifeste et refuse les clones salis ;
- ajout du catalogue `.claude-plugin/marketplace.json` et du builder
  `scripts/build-plugin.sh`, avec parité des skills, validation des renvois et
  provenance du commit dans l’archive ;
- ajout d’un `SKILL.md` canonique à `a11y-shared-references` ;
- suppression de `dist/` des sorties ignorées du kit, puisque la frontière
  standalone interdit cette surface dans le dépôt.

## Prototype standalone

- réunion des capacités DSFR et RGAA/WCAG dans un seul kit consommateur ;
- ajout d’un accueil autonome pour l’humain et pour l’agent ;
- manifeste réduit aux capacités livrées ;
- contrôle standalone sans dépendance à une usine de fabrication ;
- conservation des preuves et évaluations réellement exercées ;
- ajout du mode `audit-rgaa-creator` : campagnes RGAA multi-pages, intégration
  AY11/Playwright, reprise par phase, preuves par tentative, matrice 106,
  rapports, tickets et validation déterministe ;
- extension du creator avec une phase DSFR optionnelle sur le même échantillon :
  inventaire des composants, écarts observables, captures mobile/desktop,
  matrice et rapport DSFR séparés ;
- ajout du skill `audit-dsfr-complet` et de l’audit DSFR v2 par règle et par
  instance : statuts explicites, DOM rendu observé, structure attendue,
  qualification humaine séparée, distinction intégration/migration et rapport
  HTML filtrable ;
- ajout du skill `audit-rgaa-complet` et d’une phase RGAA v2 : signaux par test
  et instance, code observé/attendu, qualification humaine canonique dans
  `rgaa-findings.json`, causes racines et file de revue dérivée des 258 tests
  AY11 ;
- ajout de `audit-report-dsfr` et du bloc structuré `audit_report` au builder
  assemblé DSFR : portail commun RGAA/DSFR, rapports complets et vues par page,
  extraits échappés, configurations conservées et provenance `BUILD.json`.

## Correctifs de portabilité et fiabilité des contrôles

Série issue d'un retour d'installation par un tiers, complétée par un audit des
contrôles eux-mêmes.

- suppression des chemins absolus du poste d'origine dans `meta-prompt.md`,
  `documentation/AUDIT-RGAA-CREATOR.md` et les deux générateurs, remplacés par
  des marques de substitution et par la variable `AY11_ROOT`, seul nom employé
  par la documentation et par le skill `audit-rgaa-creator` ;
- retrait du suivi des livrables d'audit et des sorties de run, qui sont
  produits par le kit et non livrés avec lui ;
- correction du contrôle de frontière standalone : il s'interrompait après un
  seul de ses six contrôles dès que la sortie dépassait le tampon de tube, et
  rendait un verdict qu'il n'avait pas calculé ; son périmètre porte désormais
  sur le contenu versionné et non sur l'arbre de travail ;
- élargissement du motif de détection des chemins personnels aux formes qui lui
  échappaient, sans y inclure les chemins portables recommandés par ailleurs ;
- suppression de l'énumération d'extensions du contrôle de portabilité des
  skills, qui laissait hors du scan tout format non prévu ;
- fermeture du bloc de code du skill `audit-report-dsfr`, dont les sections
  « Garde-fous » et « Définition de fin » étaient rendues comme du code et donc
  invisibles en tant que contenu normatif ;
- arrêt des générateurs avant tout effet de bord lorsque leurs données d'entrée
  sont absentes : l'un d'eux invalidait le paquet de tickets précédent puis
  échouait, rendant un livrable valide non transmissible et non reconstructible ;
- ajout d'un garde de zone synchronisée, qui signale au moment du commit les
  fichiers recopiés depuis le workspace source.

Contrôle complet exercé sur un clone neuf, hors du poste d'origine :
`scripts/check-agentic-design-pack.sh` se termine par `[OK] DSFR Agentic Kit
standalone`, sans échec ; les contrôles produits incluent désormais le
générateur DSFR par composant, sa frontière projet/kit et les conventions du
harnais.

## Synthèse DSFR par composant

- ajout de `scripts/generate-virginie-dsfr-composants.py` et du paquet
  `scripts/virginie_dsfr/` : post-traitement des archives par page en une fiche
  unique par composant, verdict Conforme / Non conforme / Non vérifié borné aux
  règles exécutées, quatre natures de manques et états non exercés ;
- fiche de revue Markdown pour la qualification humaine des signaux à confirmer,
  une case par groupe dédoublonné, repères vérifiables contre les paquets
  officiels ; les archives restent en lecture seule ;
- séparation intégration / migration prouvée par `dist/dsfr.min.css` de la
  version observée et de la version cible, identifiants exclus des classes
  attendues ;
- rendu HTML sous thème DSFR et Markdown, manifeste, empreintes, carte
  idempotente dans l’index général des livrables, contrôle des classes émises
  contre la version cible ;
- tests `scripts/tests/check-virginie-dsfr-composants.sh`, 22 cas sur fixture
  synthétique, intégrés à la validation produit canonique.

Ce prototype local n’est pas une release publiée.
