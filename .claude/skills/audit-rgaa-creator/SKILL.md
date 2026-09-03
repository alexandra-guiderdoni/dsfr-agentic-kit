---
name: audit-rgaa-creator
description: "Créer, exécuter, reprendre et valider une campagne RGAA 4.1.2 multi-pages reproductible combinant AY11, Playwright et les skills d’audit du kit."
argument-hint: "init|sample|run|resume|status|report|validate <url-ou-campaign.yaml>"
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
   - `audit-a11y-complet` ;
   - `audit-rgaa-dsfr` ;
   - `audit-accessibilite-web` ;
   - `tests-conformite-wcag` ;
   - `screen-reader-testing` ;
   - `pre-audit-rgaa-dsfr` ;
   - `ticket-rgaa`.
3. Détecter AY11 via `--ay11-root`, `AY11_BIN` ou le `PATH`.
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
  --skills-root ../dsfr-agentic-packs
```

Le dossier de sortie doit être vide et situé hors du kit.

Pour fournir directement des pages :

```bash
--page 'https://example.gouv.fr/::Accueil::homepage' \
--page 'https://example.gouv.fr/contact::Contact::form'

Pour une campagne unitaire dont l’identifiant doit être stable, utiliser :

```bash
--page 'P09::https://example.gouv.fr/actualite::Actualité::news-article'
```
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
observables contre les références locales DSFR 1.15.2 et écrit ses résultats
séparément dans `dsfr/`.

Une reprise ignore seulement les phases `OK`. Les captures AY11 utilisent un
répertoire de tentative distinct afin de ne pas écraser les preuves brutes.

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
4. renseigner `findings.json` et `qualification.json` ;
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
ay11 probes accessible-name PAGE --json
ay11 probes contrast COLLECTION --criterion 3.2 --json
ay11 probes focus-visible COLLECTION --json
ay11 probes layout COLLECTION --criterion 10.3 --json
```

AY11 produit des contrats et signaux candidats : jamais une décision RGAA.
Une commande non disponible ou en échec devient `ECHEC`, `PARTIEL` ou `IGNORÉ`,
pas un succès implicite.

## Statuts de qualification

- `NC-A` : non-conformité instrumentée fortement étayée ;
- `C-A` : signal favorable strictement borné ;
- `NA-A` : aucune cible applicable après inspection documentée ;
- `NT` : validation humaine nécessaire ;
- `NOTE` : signal non encore qualifié ;
- `RECO` : recommandation fonctionnelle hors NC RGAA autonome.

Une `NC-A` doit contenir au minimum une page, un critère, un test et un chemin
de preuve. Une absence de violation axe ou AY11 ne prouve jamais `C-A`.

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
