# Journal des versions

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
standalone`, 134 contrôles au vert et aucun échec.

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
- tests `scripts/tests/check-virginie-dsfr-composants.sh`, 18 cas sur fixture
  synthétique. Script dédié d'abord ; passage dans le builder différé.

Ce prototype local n’est pas une release publiée.
