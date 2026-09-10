# Synchronisation agent - travaux depuis l’installation du kit

Date de consolidation : 2026-09-03

Ce document décrit les travaux effectués dans et autour de `dsfr-agentic-kit` depuis son installation, afin de permettre à un autre agent de reprendre le contexte sans interpréter les audits comme des preuves de conformité globale.

## État Git

- Aucun commit ni tag de release n’a été créé pendant ces travaux.
- Le working tree contient des fichiers modifiés et de nombreux ajouts non suivis.
- Les campagnes d’audit P01 à P09 sont des livrables séparés, hors du kit. Elles ne doivent pas être ajoutées au package du harnais par défaut.

## Capacités ajoutées au kit

Quatre skills d’audit ont été ajoutés sous `.claude/skills/` :

- `audit-rgaa-creator` : orchestration d’une campagne RGAA + DSFR reproductible.
- `audit-rgaa-complet` : préqualification RGAA 4.1.2 par instance, revue des 258 tests et décisions humaines.
- `audit-dsfr-complet` : inventaire et écarts DSFR par composant, règle, instance et version.
- `audit-report-dsfr` : adaptation des JSON canoniques au builder DSFR pour le portail et les rapports.

Entrées associées :

- `scripts/audit-rgaa-creator.sh`
- `documentation/AUDIT-RGAA-CREATOR.md`
- `scripts/tests/test_audit_rgaa_creator.py`
- `scripts/tests/check-audit-rgaa-creator.sh`

## Règles et garde-fous adoptés

- RGAA 4.1.2 : 106 critères et 258 tests.
- Statuts humains RGAA : `C_CONFIRMEE`, `NC_CONFIRMEE`, `NA_CONFIRMEE`, `A_RETESTER`, `NON_TESTE`.
- Un signal automatique ne suffit jamais seul à produire une `NC_CONFIRMEE`.
- Aucun taux RGAA officiel si des tests applicables, validations humaines, zoom natif ou technologies d’assistance restent requis.
- DSFR : séparation stricte entre écart d’intégration et candidat de migration.
- Aucun claim global ou pourcentage de conformité DSFR.
- Les rapports commencent par la page auditée et son URL.
- Les titres de constats sont formulés problème d’abord, puis identifiant technique.
- Seuls les rapports RGAA utilisent des séparateurs horizontaux, uniquement entre critères distincts.
- Le tiret simple `-` est requis dans les rapports, sans tiret cadratin ou demi-cadratin.

## Évolutions du builder DSFR

Fichiers principaux :

- `.claude/skills/dsfr-components/scripts/generate_assembled_page.py`
- `.claude/skills/dsfr-components/schemas/generate_assembled_page.schema.json`
- `.claude/skills/dsfr-components/SKILL.md`
- `.claude/skills/dsfr-components/references/`

Évolutions :

- ajout du bloc structuré `audit_report` ;
- génération du portail commun, rapports RGAA/DSFR complets et détails PXX ;
- échappement des extraits observés, sans HTML arbitraire ;
- filtres progressifs et consultation possible sans JavaScript ;
- séparation visuelle RGAA par critère uniquement ;
- titres de constats en ordre problème puis règle ;
- prise en compte de `DSFR-DISPLAY-TRIGGER-002` comme règle `VERSION_INDEPENDENT` ;
- documentation de références DSFR 1.13.2 et 1.15.2 pour le déclencheur d’affichage.

## Campagnes et livrables hors kit

Les campagnes d’audit ne sont pas distribuées avec le kit. Chaque projet
consommateur conserve ses propres preuves, matrices, rapports, validations et
archives dans un espace adapté à leur sensibilité.

Important : ne pas modifier les dossiers ni archives d’une campagne existante
lors d’une évolution du kit. Utiliser une nouvelle campagne isolée et consigner
le commit exact du kit utilisé.

## Incidents rencontrés et corrections appliquées

### Identifiant de page au démarrage

Le format historique `--page URL::Nom::type` attribuait automatiquement P01 à la première page. Une campagne P09 a donc nécessité une correction manuelle.

Correction : `init --page` accepte maintenant :

```bash
--page 'P09::https://example.gouv.fr/actualite::Actualité::news-article'
```

Le format historique reste compatible.

### Qualification ambiguë par instance

Une qualification RGAA ou DSFR qui ne précisait pas de cible pouvait s’appliquer à plusieurs instances de même règle/test.

Correction : les qualifications peuvent préciser :

- `signal_id`
- `instance`
- `selector`
- `state`
- `viewport` avec `width` et `height`
- `evidence_role` : `assertion`, `state`, `inventory`, `manual`

Le moteur rejette les correspondances absentes ou ambiguës.

Schémas concernés :

- `.claude/skills/audit-rgaa-complet/schemas/rgaa-findings.schema.json`
- `.claude/skills/audit-dsfr-complet/schemas/dsfr-findings.schema.json`

### Scripts spécifiques P08/P09

Les scripts ad hoc P08 réemployés pour P09 ont laissé des identifiants, noms ou chemins P08 dans des sorties P09.

Correction : une phase `protocols` générique est disponible dans `audit-rgaa-creator`.

Exemple de configuration :

```yaml
protocols:
  - id: contenu-profond
    script: scripts/mon-protocole.py
    output: preuves-protocoles/{page_id}/result.json
```

Le protocole reçoit un fichier JSON de contexte avec campagne, page, URL, type et répertoire de preuves. Sa sortie déclarée doit être sous la campagne et restituer les métadonnées exactes de la page.

### Manifestes et caches Python

Des fichiers `__pycache__` pouvaient être manifestés puis supprimés avant validation.

Correction : le manifeste ignore désormais :

- `__pycache__/`
- fichiers `.pyc`
- `.DS_Store`
- archives ZIP
- logs et répertoire `.creator`

### Capture des rapports codée en dur

Les scripts de capture P08 ne pouvaient pas servir à P09 sans couplage.

Correction : nouveau script générique :

```text
.claude/skills/audit-report-dsfr/scripts/capture_audit_reports.py
```

Il lit `campaign.yaml` et `rapport-dsfr/BUILD.json`, découvre le portail et tous les détails PXX, puis vérifie :

- titre et H1 attendus ;
- URL de la page auditée ;
- marqueur `data-audit-builder="dsfr-components"` ;
- ancres et liens locaux ;
- débordement horizontal ;
- filtres ;
- ouverture clavier des détails.

Activation dans une campagne :

```yaml
phases:
  report_capture: true
```

Sortie :

```text
rapport-dsfr/captures-validation/REPORT-REVIEW.json
```

### Portail multi-pages

Le portail ne traitait auparavant qu’un seul fichier de décisions PXX ou de couverture DSFR.

Correction : les décisions et couvertures sont mappées par identifiant de page. Le portail et chaque détail PXX lient désormais les ressources propres à chaque page :

- `rgaa/PXX-DECISIONS-258.md`
- `dsfr/PXX-COUVERTURE-DIMENSIONNELLE.md`

### Signaux AY11 non reliés

Les signaux AY11 non reliés étaient seulement comptés dans un avertissement global.

Correction : `COUVERTURE-MOTEURS.json` et `COUVERTURE-MOTEURS.md` créent désormais des décisions traçables `A_RETESTER` :

- identifiant `AY11-UNLINKED-*` ;
- critère et test ;
- codes candidats AY11 ;
- chemins des preuves ;
- motif du protocole complémentaire.

Fichier concerné :

```text
.claude/skills/audit-rgaa-creator/scripts/engine_coverage.py
```

## Validation effectuée

Dernière validation réalisée sur le kit :

```text
python3 -m unittest scripts.tests.test_audit_rgaa_creator
```

Résultat : 35 tests réussis.

Également validés :

```text
python3 -m py_compile .claude/skills/audit-rgaa-creator/scripts/*.py
python3 -m py_compile .claude/skills/audit-report-dsfr/scripts/capture_audit_reports.py
python3 -m json.tool .claude/skills/audit-rgaa-creator/schemas/campaign.schema.json
python3 -m json.tool .claude/skills/audit-rgaa-complet/schemas/rgaa-findings.schema.json
python3 -m json.tool .claude/skills/audit-dsfr-complet/schemas/dsfr-findings.schema.json
git diff --check
```

## Reprise conseillée par un autre agent

1. Lire `README.md`, `DEMARRAGE-AGENT.md` et `documentation/AUDIT-RGAA-CREATOR.md`.
2. Lire les quatre `SKILL.md` d’audit sous `.claude/skills/` avant d’exécuter une phase correspondante.
3. Vérifier le working tree avec `git status --short` avant toute modification.
4. Ne pas mélanger les changements du kit et les livrables de campagne.
5. Lancer les tests avant toute release.
6. Créer ensuite un commit explicite et un tag de release avant distribution.

## Fichiers particulièrement importants

```text
.claude/skills/audit-rgaa-creator/scripts/audit_campaign.py
.claude/skills/audit-rgaa-creator/scripts/audit_report_builder.py
.claude/skills/audit-rgaa-creator/scripts/engine_coverage.py
.claude/skills/audit-report-dsfr/scripts/capture_audit_reports.py
.claude/skills/audit-rgaa-complet/schemas/rgaa-findings.schema.json
.claude/skills/audit-dsfr-complet/schemas/dsfr-findings.schema.json
scripts/audit-rgaa-creator.sh
scripts/tests/test_audit_rgaa_creator.py
documentation/AUDIT-RGAA-CREATOR.md
```
