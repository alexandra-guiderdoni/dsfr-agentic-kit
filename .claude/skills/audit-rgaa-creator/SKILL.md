---
name: audit-rgaa-creator
description: "Créer, exécuter, reprendre et valider une campagne RGAA 4.1.2 multi-pages reproductible combinant AY11, Playwright et les skills d’audit du kit."
argument-hint: "init|sample|run|`resume`|status|report|validate <url-ou-campaign.yaml>"
allowed-tools: Read, Glob, Grep, Bash, Write, Edit
context: conversation
---

# Audit RGAA Creator

Créer et piloter une campagne d’audit sans confondre collecte instrumentée et
conformité réglementaire. Les livrables sont toujours écrits dans le projet de
l’utilisateur, jamais dans le kit.

## Déclencheurs

- `/audit-rgaa-creator`
- `crée une campagne RGAA`
- `reprends la campagne d’audit`
- `audit RGAA reproductible multi-pages`

## Pré-vol agent

1. Identifier le chemin du kit et celui du projet de sortie.
2. Lire les skills suivants seulement lorsque leur phase est nécessaire :
   - `audit-rgaa-complet` ;
   - `audit-dsfr-complet` ;
   - `audit-report-dsfr` ;
   - `tests-conformite-wcag` ;
   - `screen-reader-testing` ;
   - `ticket-rgaa`.
3. Détecter AY11 via `--ay11-root`, `AY11_ROOT`, `AY11_BIN` ou le `PATH`.
4. Ne jamais installer un outil ou modifier le site cible sans demande explicite.

## CLI portable

Depuis n’importe quel projet :

```bash
bash <kit>/scripts/audit-rgaa-creator.sh --help
```

### Initialiser

```bash
bash <kit>/scripts/audit-rgaa-creator.sh init https://example.gouv.fr \
  --output ../audit-example \
  --ay11-root ../ay11-pre-audit \
  --skills-root <kit>/.claude/skills
```

### Options d'exécution AY11

- `--strict-ay11` sur `run` ou `resume` : arrêt immédiat si AY11 est attendu mais absent, ou si la version attendue n’est pas satisfaite.
- Sans `--strict-ay11` : comportement tolérant (AY11 manquant ⇒ phases AY11 ignorées avec avertissement).

Le dossier de sortie doit être vide et situé hors du kit.

Pour fournir directement des pages :

```bash
--page 'https://example.gouv.fr/::Accueil::homepage' \
--page 'https://example.gouv.fr/contact::Contact::form'
```

Pour une campagne unitaire dont l'identifiant doit être stable, utiliser :

```bash
--page 'P09::https://example.gouv.fr/actualite::Actualité::news-article'
```

### Proposer un échantillon

```bash
bash <kit>/scripts/audit-rgaa-creator.sh sample ../audit-example/campaign.yaml --max-pages 10
```

La découverte est une proposition. L’humain ou l’agent doit vérifier la
représentativité des gabarits, contenus et fonctionnalités.

### Exécuter ou reprendre

```bash
bash <kit>/scripts/audit-rgaa-creator.sh run ../audit-example/campaign.yaml
bash <kit>/scripts/audit-rgaa-creator.sh resume ../audit-example/campaign.yaml
bash <kit>/scripts/audit-rgaa-creator.sh status ../audit-example/campaign.yaml --json
```

Phases fixes : `preflight`, `catalog`, `plan`, `capture`, `collect`, `browser`,
`rgaa`, `dsfr`, `protocols`, `report`, `report_capture`, `validate`.

Le pré-vol sonde les origines des URL avant toute capture. Un refus explicite
du proxy ou une cible injoignable produit le statut machine `BLOQUE_INFRA`, le
libellé humain `BLOQUÉ-INFRA` et le code de sortie 5 ; aucune phase d’audit ne
démarre dans ce cas. Une réponse HTTP en erreur sans indice de proxy reste une
erreur du site et ne devient pas un constat RGAA ou DSFR.

`protocols` exécute des scripts déclarés dans `campaign.yaml` et leur fournit un JSON canonique contenant la campagne, la page, l’URL, le type et le répertoire de preuves. La sortie déclarée doit rester sous la campagne et restituer les métadonnées exactes de page.

`report_capture`, activé avec `phases.report_capture: true`, lit `BUILD.json` et contrôle le portail ainsi que chaque détail RGAA/DSFR. Il produit `rapport-dsfr/captures-validation/REPORT-REVIEW.json`.

La phase `rgaa`, portée par `audit-rgaa-complet`, exécute des règles de
préqualification par instance, conserve le DOM rendu observé et alimente la
file de revue des 258 tests. `rgaa-findings.json` est la qualification humaine
canonique ; `findings.json` reste l’adaptateur historique et
`qualification.json` l’agrégat par critère. Une qualification d’instance peut préciser `signal_id`, `instance`, `selector`, `state`, `viewport` et `evidence_role`; une correspondance ambiguë ou inexistante est rejetée. Lorsqu’une page est traitée
exhaustivement avant les autres, produire aussi `rgaa/Pxx-DECISIONS-258.json`
et sa vue Markdown avec exactement 258 tests uniques, leur décision et leurs
preuves. Les rapports distinguent instances automatiques, critères avec NC
confirmée et tests encore `A_RETESTER`. `COUVERTURE-MOTEURS.json` et sa vue
Markdown comparent systématiquement les 258 tests, les règles exécutables, les
signaux AY11 collectés mais non branchés et les décisions confirmées sans règle
dédiée. Ces écarts deviennent des avertissements de validation et interdisent
de présenter le moteur comme exhaustif.

La phase `report` délègue le rendu HTML à `audit-report-dsfr`. Les résultats
JSON restent canoniques ; le portail commun, les rapports RGAA/DSFR et les vues
par page sont tous produits via le bloc structuré `audit_report` de
`dsfr-components/scripts/generate_assembled_page.py`, en `brand_mode: neutral`.

La phase `dsfr`, activée par `phases.dsfr_checks`, utilise exactement le même
échantillon que le RGAA. Elle inventorie les composants, vérifie des invariants
observables contre les références locales DSFR 1.15.4 et écrit ses résultats
séparément dans `dsfr/`.

Une reprise ignore seulement les phases `OK`. Lorsqu’une phase est rejouée,
les phases dérivées déjà marquées `OK` passent à `À REJOUER` puis sont
régénérées si elles font partie de la sélection. Les captures AY11 utilisent
un répertoire de tentative distinct afin de ne pas écraser les preuves brutes.
Avec `resume --only`, les phases dérivées invalidées mais absentes de la
sélection restent `À REJOUER` et la commande retourne un statut partiel ;
relancer `resume` sans `--only` pour produire la chaîne complète.

Lorsque `browser_checks`, `rgaa_checks` ou `dsfr_checks` est actif, le prévol
valide la configuration avant toute écriture du runtime navigateur et vérifie
`playwright.async_api` dans l’interpréteur choisi. `DSFR_AUDIT_PYTHON` permet
d’imposer le même interpréteur au diagnostic autonome et à la campagne.

Si `campaign.yaml` change après démarrage, la reprise est refusée :

```bash
bash <kit>/scripts/audit-rgaa-creator.sh replan ../audit-example/campaign.yaml
```

`replan` archive l’état précédent et conserve les preuves déjà collectées.

### Compléter les qualifications

Le runner ne fabrique pas de verdict. L’agent doit :

1. lire `RUNBOOK-AGENT.md` ;
2. analyser les preuves page par page ;
3. exercer les états conditionnels pertinents ;
4. renseigner `rgaa-findings.json` et, si la phase DSFR est active,
   `dsfr-findings.json` ;
5. régénérer et valider :

```bash
bash <kit>/scripts/audit-rgaa-creator.sh report ../audit-example/campaign.yaml
bash <kit>/scripts/audit-rgaa-creator.sh validate ../audit-example/campaign.yaml
```

## Contrat AY11

Le creator utilise les interfaces stables suivantes :

```bash
ay11 rgaa list --kind criteria --format json
ay11 rgaa run-plan rgaa-106 --include-proof-contract --execution-mode agents --json
ay11 preaudit capture-browser URL --output-dir DIR --screenshot --form-interactions --axe --json
ay11 rgaa run-plan rgaa-106 --collect-html PAGE --collect-accessible-name PAGE --json
ay11 probes --help
ay11 probes SONDE --help
ay11 probes SONDE ENTRÉE [--criterion CRITÈRE] --json
```

AY11 produit des contrats et signaux candidats : jamais une décision RGAA.
Une commande non disponible ou en échec devient `ECHEC`, `PARTIEL` ou `IGNORÉ`,
pas un succès implicite.

### Découverte des sondes

La phase `collect` découvre les sondes dynamiquement : `probe_matrix.py` les lit
dans l'aide d'AY11, avec leur entrée attendue (HTML rendu, collection navigateur
ou les deux) et les critères que chacune propose. Une sonde ou un critère ajouté
en amont est collecté sans modifier le creator. Le
catalogue observé est écrit dans `collectes-ay11/catalogue-sondes.json`, et
une sonde écartée y est nommée avec son motif.

Trois propriétés d'AY11 gouvernent cette phase :

- **omettre `--criterion` ne collecte qu'un seul critère**, jamais tous ceux que
  la sonde couvre : chaque critère donne lieu à un appel distinct ;
- **une sonde sort en code 0 même sans candidat** : l'état utile est
  `collection_status`, et un code de retour nul ne vaut pas collecte réussie ;
- **`not_collected` sans capture complémentaire n'est pas un échec** : la sonde
  réclame une capture que la capture de base ne produit pas (reflow,
  orientation, états `:hover` et `:focus`). Ces critères sont listés en
  `captures_manquantes` dans l'état, et restent **non instruits** — ni conformes,
  ni non conformes.

Chaque page reçoit `collectes-ay11/<page>/attempt-XXX/sondes/<sonde>-<critère>.json`
et un `sondes-resume.json` qui sépare critères avec signal, critères sans
candidat et critères en capture manquante. L'absence de signal ne vaut jamais
conformité : elle borne ce que la sonde a pu observer.

### Trois états de couverture, jamais deux

`collect-html` ne remonte un critère que s'il a trouvé quelque chose : un critère
**couvert mais muet** est absent de sa sortie, exactement comme un critère
**non couvert**, alors que le premier appelle une revue humaine ciblée et le
second non.

AY11 ne déclare pas quels critères il sait instruire, mais il le dit à l'appel :
`rgaa collect-html --criterion X` sort en code 0 quand un collecteur existe, et en
code 1 avec « Collecteur HTML local non disponible » sinon. La phase `collect`
sonde donc les 106 critères une fois par campagne — environ 15 secondes — et écrit
`collectes-ay11/catalogue-collecteurs.json`.

| État | Sens | Suite |
|---|---|---|
| `candidat` | le collecteur signale un candidat de défaut | qualifier |
| `couvert_sans_candidat` | il a tourné sans rien trouver | **revoir humainement** |
| `non_couvert` | aucun collecteur pour ce critère | jugement humain seul |

Les preuves de 6.1, 6.2, 7.1, 11.5, 11.6, 11.9 et 12.8 ne viennent pas d'un
collecteur `collect-html` (il n'en existe pas pour ces critères) mais de
`--collect-accessible-name`, que `run-plan` fusionne dans la même sortie. Le
nombre de collecteurs disponibles et de critères instrumentés se lit dans
`collectes-ay11/catalogue-collecteurs.json`, pas dans ce fichier.

### Remontée dans la grille des 258 tests

`rgaa/SONDES-PAR-CRITERE.json` agrège la campagne, et la colonne « Sondes »
apparaît dans `MATRICE-TESTS-258.md` et `REVUE-MANUELLE-258.md`.

**Une sonde rend un critère, jamais un test.** La colonne est donc affichée sur
chaque ligne de test du critère, avec la mention explicite qu'elle vaut pour le
critère entier — elle ne doit pas se lire comme un verdict de test. Le champ
`probe_coverage.granularity` du JSON porte la même réserve.

Quatre états, volontairement distincts :

| État | Sens |
|---|---|
| `signal` | candidats à qualifier, avec le compte et les sondes concernées |
| `capture_manquante` | critère **non instruit** : ni conforme, ni non conforme |
| `aucun_candidat` | sonde exécutée sans trouver ; **ne vaut pas conformité** |
| `hors_sondes` | aucune sonde ne couvre ce critère, jugement humain seul |

La priorité de revue suit : `P0` si un signal existe, `P1` si le critère est en
capture manquante. La colonne « Qualification » reste vide — elle n'appartient
qu'à l'humain.

### Prérequis du poste de travail

| Outil | Rôle | Sans lui |
|---|---|---|
| AY11 | référentiel et sondes | phases `catalog`, `plan`, `capture`, `collect` en `IGNORÉ` |
| Chromium via Playwright | capture du DOM rendu | aucune capture |
| **`vnu`** | validateur HTML local | la phase `validator` passe par le service public du W3C, **qui limite le débit** |

Sur macOS : `brew install vnu`. `init` le détecte dans le `PATH` et écrit
`validator.command` dans `campaign.yaml` sans intervention. Le pré-vol avertit
quand aucun validateur local n'est disponible, et échoue si un validateur
déclaré est introuvable.

### Validateur HTML — la seule source du critère 8.2

La collecte AY11 rend `external_validator_executed: false` : elle ne pratique
que des contrôles structurels bornés (`complete_html_conformance: false`).
Sans phase dédiée, le critère 8.2 reste hors de portée du harnais.

La phase `validator` appelle le validateur HTML sur l'URL de chaque page, écrit
`validateur-w3c/<page>.json`, et rattache erreurs et avertissements au critère
8.2 dans la grille.

```yaml
phases:
  validator: true
validator:
  endpoint: https://validator.w3.org/nu/   # ou un vnu local
  delay_seconds: 2                          # courtoisie envers le service public
  timeout_seconds: 90
```

Elle est placée **après** `dsfr` et non avant `browser` : ses preuves ne servent
qu'au rapport, elle n'est donc dépendance amont d'aucune phase de collecte.

Trois réserves à ne pas perdre de vue :

- **le validateur porte sur le HTML servi**, pas sur le DOM rendu après
  exécution du JavaScript. Sur une application React, une partie du code audité
  par un lecteur d'écran échappe donc à ce contrôle ;
- une panne réseau ou un délai dépassé rend la phase `PARTIEL`, jamais `OK` :
  l'absence de rapport n'est pas une absence d'erreur ;
- `endpoint` accepte un `vnu` local, à préférer pour une campagne de plusieurs
  pages plutôt que de solliciter le service public du W3C.

## Qualification humaine

`rgaa-findings.json` est le fichier de saisie canonique de la qualification
RGAA. Ses statuts sont définis par `audit-rgaa-complet` :
`C_CONFIRMEE`, `NC_CONFIRMEE`, `NA_CONFIRMEE`, `A_RETESTER` et `NON_TESTE`.
Pour la phase DSFR, `dsfr-findings.json` utilise les statuts définis par
`audit-dsfr-complet`, notamment `ECART_CONFIRME`.

`findings.json` et `qualification.json` sont des sorties dérivées historiques
produites par `report`. Ils ne sont pas renseignés directement par l'agent.
Une absence de violation axe ou AY11 ne prouve jamais une conformité.

## Vérification DSFR bornée

La phase DSFR délègue son catalogue à `audit-dsfr-complet` et distingue les
résultats RGAA des statuts explicites de composants :

- `DETECTE_NON_AUDITE` : instance trouvée sans règle ciblée suffisante ;
- `AUCUN_ECART_REGLES_EXECUTEES` : toutes les règles déclarées ont produit un signal favorable dans leur seul périmètre ;
- `ECART_OBSERVE` : au moins une assertion par instance a échoué avec preuve ;
- `A_CONFIRMER` : signal non encore qualifié humainement ;
- `NON_APPLICABLE` : composant ou contrôle sans cible ;
- `REFERENCE_INDISPONIBLE` : version ou source exacte non disponible.

La qualification humaine séparée se trouve dans `dsfr-findings.json` et peut
produire `ECART_CONFIRME`. Chaque signal v2 doit citer la règle, l’instance, le
sélecteur, le DOM rendu observé, la structure attendue, la source versionnée,
la recommandation et la procédure de vérification. Les différences entre la
version observée et la cible sont classées `migration`, pas intégration de la
version installée.

Elle produit `dsfr/INVENTAIRE-COMPOSANTS.json`,
`dsfr/ECARTS-COMPOSANTS.json`, `dsfr/MATRICE-RESPECT-DSFR.md`,
`dsfr/AUDIT-PAR-PAGE.html` et les preuves par page. Le droit d’usage de la
marque, la fidélité visuelle exhaustive, les états non exposés et la pertinence
du choix des composants restent humains.

## Garde-fous

- Aucun taux RGAA officiel.
- Aucun claim « conforme RGAA » ou « conforme DSFR ».
- Aucun claim global d’alignement DSFR : seuls les règles exécutées, signaux et qualifications sont rapportés.
- Un arbre Chromium est une préqualification, jamais un test NVDA, JAWS ou
  VoiceOver.
- Les parcours authentifiés, documents, médias et décisions éditoriales non
  exercés restent explicitement `NT` ou hors périmètre.
- Ne pas utiliser `fix-accessibilite` sur un site tiers sans code et sans
  autorisation.

## Définition de fin

La campagne est transmissible lorsque :

- `MATRICE-RGAA-106.md` contient exactement 106 critères ;
- si la phase DSFR est active, chaque page figure aussi dans le rapport et la matrice DSFR ;
- chaque page possède son rapport et ses preuves ou un avertissement explicite ;
- les tickets correspondent aux causes racines ;
- les ancres du rapport HTML sont valides ;
- `VALIDATION.json` ne contient aucune erreur ;
- le rapport HTML a été relu visuellement ;
- les limites et validations humaines restantes sont visibles.
