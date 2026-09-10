# Prompt gouverné — rejeu de l’audit DSFR de l’échantillon Douane

À transmettre à Claude dans un Projet Cowork persistant. Ce prompt pilote un
rejeu traçable et produit le livrable HTML attendu ; il ne transforme pas une
synthèse d’archives en preuve d’audit frais.

## Objectif

Refaire, avec la pointe vérifiée du dépôt
`https://github.com/alexandra-guiderdoni/dsfr-agentic-kit`, l’audit DSFR de
l’échantillon Douane P01 à P09, puis produire exactement :

`PROJECT_ROOT/virginie-livrables/DSFR-COMPOSANTS/INDEX-DSFR-COMPOSANTS.html`

Le chemin `PROJECT_ROOT` désigne la racine persistante du Projet Cowork qui
contient les archives ou les entrées nécessaires à l’audit. Sur le poste local
comme dans Cowork, utiliser le chemin réellement monté dans le Projet, sans
supposer un chemin macOS et sans utiliser `/Volumes`.

## Contexte vérifié à reprendre

- Site audité : `https://moa.douane.gouv.fr/`.
- Pages attendues : P01 à P09, décrites dans
  `virginie-livrables/echantillon-douane.md`.
- Date des archives historiques : 2026-09-02.
- Version DSFR observée dans l’échantillon : 1.13.2.
- Version DSFR cible du kit : lire `runtime.dsfr_version` dans
  `config/agentic-design-packages.yaml` ; ne jamais la deviner.
- Règles DSFR à utiliser :
  `.claude/skills/audit-dsfr-complet/rules/dsfr-rules.json`.
- Script de production du livrable :
  `scripts/generate-virginie-dsfr-composants.py`.
- Fiche de revue humaine :
  `virginie-livrables/DSFR-COMPOSANTS-TRAVAIL/REVUE-A-QUALIFIER.md`.

Le script de production lit des archives d’audit et ne capture pas le site à
lui seul. Il faut donc distinguer explicitement :

1. un audit frais, réalisé avec le catalogue courant et de nouvelles preuves ;
2. une synthèse d’archives existantes, qui peut produire l’HTML mais ne
   prouve pas qu’une nouvelle règle a été rejouée sur le site.

## Variables à établir avant toute commande

Déterminer et afficher dans le compte rendu les valeurs réelles de ces
variables, sans les inventer :

```text
PROJECT_ROOT   = racine persistante du Projet contenant l’échantillon
KIT_ROOT       = clone local du dépôt dsfr-agentic-kit
ARCHIVES_ROOT  = PROJECT_ROOT/archives
OUT_DIR        = PROJECT_ROOT/virginie-livrables/DSFR-COMPOSANTS
WORK_DIR       = PROJECT_ROOT/virginie-livrables/DSFR-COMPOSANTS-TRAVAIL
REVIEW_SHEET   = WORK_DIR/REVUE-A-QUALIFIER.md
RULES          = KIT_ROOT/.claude/skills/audit-dsfr-complet/rules/dsfr-rules.json
CACHE_DIR      = cache DSFR officiel réellement disponible
DELIVERY_DATE  = date UTC de l’exécution
```

Si le clone n’existe pas, l’amorcer depuis le dépôt GitHub avec
`scripts/amorcage-session-cloud.sh`, puis vérifier son commit et son état. Ne
pas copier une version arbitraire du script depuis un autre projet.

## Contraintes non négociables

- Travailler sur une copie ou une nouvelle campagne ; ne jamais modifier les
  archives historiques ni leurs manifestes, captures, findings ou sommes de
  contrôle.
- Ne jamais supprimer un ancien livrable. Si une nouvelle sortie est
  nécessaire, la conserver dans un répertoire daté ou déplacer uniquement une
  sortie générée après vérification de son origine.
- Ne jamais fabriquer une archive, un finding, une empreinte de catalogue, une
  décision humaine ou une preuve de conformité.
- Ne pas réutiliser aveuglément un ancien `campaign.yaml` contenant des chemins
  absolus ou une phase DSFR déjà marquée comme terminée. Un `resume` ancien ne
  constitue pas un rejeu du catalogue courant.
- Si une empreinte de catalogue est absente, ancienne ou différente de celle
  du catalogue courant, le signaler comme archive obsolète. Ne pas le présenter
  comme une preuve actuelle.
- Le simple ajout d’une règle `quote` dans le catalogue ne prouve pas qu’elle a
  été exercée. Pour déclarer `quote` couvert, il faut une nouvelle archive
  produite avec le catalogue courant et un signal traçable sur P09.
- Ne cocher aucune case de `REVUE-A-QUALIFIER.md` sans décision humaine
  explicite et justifiée. Avec `--allow-pending`, les éléments non arbitrés
  restent `NON VÉRIFIÉ`.
- Distinguer visuellement et sémantiquement `NON COUVERT`, `À QUALIFIER` et
  `CONTRADICTION`. Ne pas les fondre dans un même libellé « non vérifié ».
- Regrouper les contradictions par page, état de revue et variante DOM ;
  conserver la page, le composant, la règle, le sélecteur et l’empreinte de
  variante qui permettent de remonter à la preuve.
- Ne pas annoncer de conformité DSFR ou RGAA globale. Le livrable est un état
  d’audit borné par l’échantillon, les règles, les archives et les décisions
  humaines réellement disponibles.
- Ne pas utiliser `--no-index` pour masquer une erreur ; ici il sert seulement
  à éviter de modifier l’index général du Projet Cowork.
- Toute absence de cache DSFR, de navigateur, d’archives, de dépendance ou de
  source doit apparaître en `SKIP`, `NON VÉRIFIÉ` ou `NO-GO` selon le cas, avec
  sa cause. Un contrôle non exécuté n’est pas un contrôle réussi.

## Procédure gouvernée

### 1. Prévol et source de vérité

Vérifier :

- `git rev-parse --show-toplevel`, branche et commit du kit ;
- l’URL du remote, qui doit viser
  `git@github.com:alexandra-guiderdoni/dsfr-agentic-kit.git` ou le dépôt
  GitHub canonique équivalent ;
- l’absence de modifications locales dans le kit ;
- les contrôles de prérequis et du pack ;
- l’existence de `DESIGN.md`, `tokens.yaml`, du catalogue de règles, de la
  fiche d’échantillon et de la fiche de revue.

Lire avant l’exécution les sources qui gouvernent le résultat :
`design-systems/dsfr/DESIGN.md`, `design-systems/dsfr/tokens.yaml`,
`audit-dsfr-complet/SKILL.md`, le catalogue JSON et le script Virginie.

### 2. Contrôle des entrées P01 à P09

Pour chaque page P01 à P09, vérifier la présence d’une archive complète,
lisible et identifiable. Relever dans le compte rendu :

- le chemin exact de l’archive ;
- la page et l’URL associées ;
- la date et la version DSFR observées ;
- l’empreinte du catalogue enregistrée, ou son absence ;
- les erreurs de manifeste, de somme ou de lecture.

Si une entrée manque, arrêter la prétention à un audit complet des neuf pages.
Une synthèse partielle n’est possible que si elle est explicitement annoncée
comme telle.

### 3. Choix entre audit frais et synthèse d’archives

Comparer l’empreinte de chaque archive au catalogue courant.

- Si les sources du site, le navigateur, les dépendances et le contexte de
  campagne sont disponibles, lancer une nouvelle campagne isolée, dans un
  répertoire daté, avec le kit courant et la phase DSFR activée. Ne pas
  écraser les archives du 2026-09-02. Rejouer ensuite la collecte et la
  validation prévues par `audit-rgaa-creator`.
- Si les anciennes archives sont les seules entrées disponibles, produire une
  synthèse honnête avec leur statut de fraîcheur. Le résultat peut être livré
  pour revue, mais le verdict final doit dire « synthèse d’archives — rejeu
  frais non prouvé ».
- Si les entrées sont incomplètes ou illisibles, ne pas fabriquer de résultat.
  Produire un compte rendu `NO-GO` indiquant précisément l’entrée manquante.

Dans tous les cas, vérifier spécialement la règle de citation du composant
`.fr-quote` sur P09 : présence dans le catalogue, présence d’un signal dans
les nouvelles preuves si audit frais, et statut explicite sinon.

### 4. Production du livrable

Après avoir établi les entrées et leur fraîcheur, exécuter le script du kit,
avec des chemins absolus résolus dans la session :

```bash
python3 "$KIT_ROOT/scripts/generate-virginie-dsfr-composants.py" \
  --archives "$ARCHIVES_ROOT" \
  --pattern 'audit-douane-p{n:02d}-complet-rgaa-dsfr-2026-09-02' \
  --pages 1-9 \
  --output "$OUT_DIR" \
  --work-dir "$WORK_DIR" \
  --review-sheet "$REVIEW_SHEET" \
  --cache-dir "$CACHE_DIR" \
  --rules "$RULES" \
  --delivery-date "$DELIVERY_DATE" \
  --allow-pending \
  --no-index
```

Si une campagne fraîche possède un autre motif d’archive, remplacer
`--pattern` par le motif réellement produit et le consigner. Ne pas pointer
vers une archive inventée pour faire passer le script.

### 5. Vérification indépendante de la sortie

Ne pas conclure au seul code retour du générateur. Vérifier séparément :

- la présence de `OUT_DIR/INDEX-DSFR-COMPOSANTS.html` ;
- la présence et la lecture de `MANIFESTE-DSFR-COMPOSANTS.json` et
  `SHA256SUMS` ;
- neuf pages P01 à P09 lorsque les neuf entrées sont annoncées ;
- l’absence de liens ou chemins de poste `/Volumes`, `/Users`, `/home` ou
  `/private/tmp` dans le livrable portable ;
- `lang="fr"`, les liens internes vers les fiches composant et l’absence de
  liens cassés ;
- la présence de `quote` dans l’inventaire et son statut réellement prouvé ;
- la distinction visible entre `NON COUVERT`, `À QUALIFIER` et
  `CONTRADICTION` ;
- le regroupement des contradictions par page, état et variante DOM ;
- le nombre de composants, de groupes, de pages et de signaux en attente ;
- `errors: []` dans le manifeste, ou la liste exacte des erreurs si ce n’est
  pas le cas.

Contrôler aussi que la fiche de revue reste inchangée si aucune décision
humaine n’a été fournie. Comparer son empreinte avant/après.

## Sortie attendue de Claude

Répondre avec un compte rendu court et vérifiable, dans cet ordre :

1. `GO-AUDIT-FRAIS`, `GO-SYNTHÈSE-D’ARCHIVES` ou `NO-GO` ;
2. chemin exact du fichier HTML produit ;
3. commit du kit, version DSFR cible, empreinte du catalogue et état de
   fraîcheur des archives ;
4. pages effectivement traitées et comptages du manifeste ;
5. statut de `.fr-quote` sur P09 ;
6. nombre de `NON COUVERT`, `À QUALIFIER`, `CONTRADICTION` et `NON VÉRIFIÉ` ;
7. décisions humaines manquantes, erreurs, contrôles sautés et limites ;
8. commandes de vérification réellement exécutées.

Le résultat est `NO-GO` si le HTML demandé n’est pas produit, si des entrées
indispensables manquent, si les erreurs du manifeste ne sont pas vides sans
explication, ou si le statut de fraîcheur est impossible à établir. Un HTML
présent avec des signaux non arbitrés peut être remis comme
`GO-SYNTHÈSE-D’ARCHIVES`, jamais comme conformité établie.
