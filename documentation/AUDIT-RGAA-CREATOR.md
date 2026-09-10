# Audit RGAA Creator

`audit-rgaa-creator` permet d’initialiser et de piloter une campagne RGAA 4.1.2 multi-pages et, sur le même échantillon, une vérification DSFR bornée.
Il combine les contrats AY11, des contrôles Playwright et les skills d’audit du
kit sans produire de déclaration réglementaire automatique ni de claim de
conformité DSFR globale.

## Séparation des responsabilités

- Le kit contient le skill, le runner, les schémas et les contrôles.
- AY11 collecte des contrats et des signaux candidats.
- Playwright exerce les pages et produit des mesures complémentaires.
- L’agent applique les skills, qualifie les preuves et documente les limites.
- L’humain valide l’échantillon, les décisions éditoriales et les tests manuels.
- La campagne et ses livrables vivent hors du kit.

## Démarrage

```bash
KIT=/chemin/dsfr-agentic-kit
AY11=/chemin/ay11-pre-audit
AUDIT=/chemin/projet/audit-example

bash "$KIT/scripts/audit-rgaa-creator.sh" init https://example.gouv.fr \
  --output "$AUDIT" --ay11-root "$AY11" --skills-root "$KIT/.claude/skills"

# Relire et compléter l’échantillon avant l’exécution.
bash "$KIT/scripts/audit-rgaa-creator.sh" sample "$AUDIT/campaign.yaml" --max-pages 10
bash "$KIT/scripts/audit-rgaa-creator.sh" run "$AUDIT/campaign.yaml"
```

## Arborescence recommandée

Organisation de travail claire avec `ay11-pre-audit` en source externe :

```text
<workspace>/
├── ay11-pre-audit/
├── dsfr-agentic-kit/
└── audit-example/
```

Dans `dsfr-agentic-kit`, crée (ou adapte) `.env.local` :

```bash
cd <workspace>/dsfr-agentic-kit
export AY11_ROOT="<workspace>/ay11-pre-audit"
# Optionnel :
export AY11_EXPECTED_VERSION="1.3.0"
```

Le runner charge automatiquement ce fichier au lancement (non versionné).

Le `sample` est une proposition heuristique. Il faut conserver les gabarits et
fonctionnalités représentatifs : accueil, plan, déclaration, contenus, tableau,
formulaire, média, aide et parcours authentifié lorsqu’il est disponible.

## Cycle de campagne

```text
preflight → catalog → plan → capture → collect → browser → rgaa → dsfr → report → validate
```

- `preflight` vérifie URLs, AY11 et skills ;
- `catalog` conserve les 106 critères AY11 ;
- `plan` produit le contrat des 258 tests ;
- `capture` crée HTML rendu, arbre a11y, axe et capture par page ;
- `collect` exécute les collecteurs et probes AY11 ;
- `browser` mesure structure, contraste candidat, clavier et neuf contrats WCAG ;
- `rgaa` exécute les règles de préqualification par instance, conserve le code observé et alimente la revue des 258 tests ;
- `dsfr` inventorie chaque instance, exécute le catalogue versionné de `audit-dsfr-complet`, conserve le sélecteur et le DOM rendu, puis sépare intégration et migration vers la référence locale DSFR 1.15.2 ;
- `report` dérive matrices, pages et tickets, puis délègue à `audit-report-dsfr` le portail commun, les rapports complets et les vues par page via `generate_assembled_page.py` ;
- `validate` vérifie cohérence, preuves, ancres et garde-fous.

Les nouvelles campagnes activent `phases.rgaa_checks: true` et
`phases.dsfr_checks: true`. Une ancienne campagne reste rétrocompatible :
ajouter le champ souhaité puis exécuter `replan` pour activer la phase
correspondante.

Chaque nouvelle capture utilise `attempt-NNN`. Les preuves d’une tentative
précédente ne sont pas écrasées.

## Reprise

```bash
bash "$KIT/scripts/audit-rgaa-creator.sh" status "$AUDIT/campaign.yaml" --json
bash "$KIT/scripts/audit-rgaa-creator.sh" resume "$AUDIT/campaign.yaml"
```

### Contrôle AY11 strict (optionnel)

Mode bloquant pour l’absence d’AY11 ou une version inférieure à la version minimale attendue :

```bash
bash "$KIT/scripts/audit-rgaa-creator.sh" run "$AUDIT/campaign.yaml" --strict-ay11
```

Sans ce flag, AY11 reste non bloquant (phases AY11 ignorées avec avertissement si absent).

Une campagne est verrouillée pendant son exécution. L’état est écrit
atomiquement dans `.creator/state.json`.

Une modification de `campaign.yaml` change son empreinte et bloque la reprise.
Après vérification de la nouvelle configuration :

```bash
bash "$KIT/scripts/audit-rgaa-creator.sh" replan "$AUDIT/campaign.yaml"
bash "$KIT/scripts/audit-rgaa-creator.sh" resume "$AUDIT/campaign.yaml"
```

L’état précédent est archivé ; les preuves sont conservées.

## Qualification

Les preuves automatisées n’écrivent pas seules un verdict. Renseigner :

- `rgaa-findings.json` comme source canonique des décisions humaines par règle, test et instance ;
- `findings.json` comme adaptateur historique pour les constats et tickets ;
- `qualification.json` comme agrégat par critère pour la matrice des 106 critères.

Statuts : `NC-A`, `C-A`, `NA-A`, `NT`, `NOTE`, `RECO`.

Les constats DSFR restent séparés dans `dsfr-findings.json`. L’inventaire
utilise les statuts explicites `DETECTE_NON_AUDITE`,
`AUCUN_ECART_REGLES_EXECUTEES`, `ECART_OBSERVE`, `A_CONFIRMER`,
`NON_APPLICABLE` et `REFERENCE_INDISPONIBLE`. Un signal automatique
`FAIL_CANDIDATE` reste `A_CONFIRMER` tant qu’une qualification ne le déclare pas
`ECART_CONFIRME` avec preuve. Chaque écart v2 cite la règle, l’instance, le
sélecteur, le DOM rendu observé, la structure attendue, la source, la version,
la recommandation et la procédure de vérification. La phase ne déduit ni droit
d’usage de la marque, ni fidélité visuelle exhaustive, ni statut « conforme
DSFR ».

Une `NC-A` sans critère, test, page ou preuve locale existante échoue à la
validation. Les chemins de preuves doivent être relatifs et portables. Un exemple
complet est fourni dans
`.claude/skills/audit-rgaa-creator/examples/findings.example.json`.

## Livrables

```text
audit-example/
├── campaign.yaml
├── RUNBOOK-AGENT.md
├── findings.json
├── rgaa-findings.json
├── dsfr-findings.json
├── qualification.json
├── plan-preuves-rgaa-106.json
├── AUDIT-PAR-PAGE.html
├── PORTAIL-AUDITS.html
├── rapport-dsfr/
│   ├── BUILD.json
│   └── config/*.json
├── RAPPORT-CONSOLIDE.md
├── MATRICE-RGAA-106.md
├── VALIDATION.json
├── MANIFESTE-ARTEFACTS.json
├── pages/
├── tickets/
├── captures-ay11/
├── collectes-ay11/
├── rgaa/
│   ├── CONSTATS-INSTANCES.json
│   ├── MATRICE-TESTS-258.md
│   ├── REVUE-MANUELLE-258.json
│   ├── REVUE-MANUELLE-258.md
│   ├── RAPPORT-CONSOLIDE.md
│   ├── AUDIT-PAR-PAGE.html
│   ├── pages-html/Pxx.html
│   ├── pages/
│   └── preuves/Pxx/attempt-NNN/
├── dsfr/
│   ├── INVENTAIRE-COMPOSANTS.json
│   ├── ECARTS-COMPOSANTS.json
│   ├── MATRICE-RESPECT-DSFR.md
│   ├── RAPPORT-CONSOLIDE.md
│   ├── AUDIT-PAR-PAGE.html
│   ├── pages-html/Pxx.html
│   ├── pages/
│   └── preuves/Pxx/attempt-NNN/
├── tests-wcag/
├── interactions/
├── analyses-skills/
└── inspections-approfondies/
```

## Limites

- Une absence de signal n’est pas une conformité.
- Le score axe éventuel n’est jamais un taux RGAA.
- L’arbre Chromium n’est pas un test NVDA, JAWS ou VoiceOver.
- Les tests d’espacement, zoom, pertinence éditoriale, médias, documents et
  parcours métier conservent une validation humaine lorsque nécessaire.
- Aucun claim global d’alignement ou de conformité DSFR n’est produit : seuls les règles exécutées, signaux et qualifications sont rapportés.
- Le HTML cité est le DOM rendu ; il ne devient du « code source applicatif » que si un dépôt ou une source map est explicitement disponible.
