---
title: "DSFR - smoke tests profil et skill"
scope: routage agentique, near-miss, non-régression
load_when: "Avant de modifier DESIGN.md, tokens.yaml, les déclencheurs ou le contrat avec dsfr-components."
---

# DSFR - smoke tests profil et skill

Ces cas vérifient que le profil `design-systems/dsfr` aide `dsfr-components`
sans le remplacer. Ils sont des proxys de routage, pas une preuve runtime de
sélection du modèle.

## Preuve runtime

La preuve runtime exige une trace réelle de sélection de skill ou d'outil. À
défaut, la validation locale doit écrire `SKIP` et ne pas présenter le proxy
comme un déclenchement observé.

```bash
python3 design-systems/scripts/check-dsfr-profile.py --runtime-trace design-systems/dsfr/evals/runtime-traces/pos-profile-page-codex-exec.txt
```

Trace minimale attendue :

- nom ou identifiant `dsfr-components` ;
- prompt ou identifiant du cas smoke ;
- preuve que `DESIGN.md` et `tokens.yaml` ont été chargés ou cités.

Trace renforcée : conserver une trace événementielle normalisée issue de
`codex exec --json`, puis la valider avec. Pour régénérer et vérifier les deux
traces en une commande :

```bash
python3 design-systems/scripts/check-dsfr-runtime-trace.py run
```

Pour vérifier des traces existantes :

```bash
python3 design-systems/scripts/check-dsfr-runtime-trace.py check \
  design-systems/dsfr/evals/runtime-traces/pos-page-form-codex-exec-runtime.events.json \
  design-systems/dsfr/evals/runtime-traces/near-miss-service-public-no-dsfr-codex-exec-runtime.events.json
```

## Prompts positifs

| Id | Prompt | Attendu | Preuve proxy |
|---|---|---|---|
| `pos-profile-page` | « Crée une page HTML statique DSFR pour une demande de rendez-vous administratif. » | charger `DESIGN.md`, `tokens.yaml`, `agent-recipes.md`, puis utiliser `dsfr-components` page complète | `DESIGN.md` pointe vers recettes et le skill pointe vers le profil partagé |
| `pos-rdv-page` | « Crée une page HTML statique DSFR pour une démarche de rendez-vous administratif. » | route page complète, type formulaire, claim borné | trace qualitative versionnée |
| `pos-component-accordion` | « J'ai besoin d'un accordéon DSFR à intégrer dans une page existante. » | route composant isolé, référence composant ciblée, pas d'enveloppe page | recette composant et branch-map du skill présents |
| `pos-form-field` | « Génère un champ date DSFR pour un formulaire administratif. » | route formulaire ou champ, labels/aides/erreurs, validation différée si contrainte | `forms-models.md` et pointeurs formulaire du skill présents |
| `pos-publication-guard` | « Prépare cette page DSFR pour publication officielle. » | charger page-shell, verification, sources ; refuser tout claim sans preuve dédiée | formulations interdites listées et garde publication présente |
| `pos-version-migration` | « Compare la version DSFR 1.14.4 à la 1.15.2 et prépare la décision de migration. » | router vers `dsfr-changelog`, vérifier le dépôt et les tags, ne pas modifier `package_version_ref` | `DESIGN.md` pointe vers le skill et son contrat exige la comparaison des versions |

Sur `pos-version-migration`, les deux numéros cités sont un habillage : le cas
vérifie un comportement, pas des versions. Il reste valide quels que soient les
numéros de la demande.

L'interdiction de modifier `package_version_ref` porte sur l'effet de bord :
une comparaison ne change jamais le ciblage d'elle-même. Changer ce ciblage est
une décision distincte, prise après lecture des résultats, et elle est
légitime. Le pack est ainsi passé de 1.14.4 à 1.15.2 le 2026-08-28, par ce
chemin : comparaison d'abord, décision ensuite. Lire une contradiction entre ce
cas et la version courante du pack serait un contresens.

## Near-miss

| Id | Prompt | Attendu | Preuve proxy |
|---|---|---|---|
| `near-miss-service-public-no-dsfr` | « Crée une page HTML pour un service public de prise de rendez-vous. » | ne pas déclencher DSFR sans besoin explicite ; demander ou produire neutre | weak triggers et smoke du skill présents |
| `near-miss-rgaa-complete` | « Audite la conformité RGAA complète de ce site. » | router vers skill d'audit, pas vers génération DSFR | `verification.md` route les audits spécialisés |
| `near-miss-google-strict` | « Rends ce DESIGN.md compatible avec le CLI Google. » | ne pas convertir le routeur ; proposer un artefact généré séparé si besoin | `inspired_not_compliant` présent dans profil et tokens |
| `near-miss-token-catalog` | « Ajoute tous les tokens DSFR au tokens.yaml. » | refuser le catalogue parallèle ; étendre seulement par besoin prouvé | `missing_is_not_absent` et projection non exhaustive présents |
| `near-miss-dsfr-like-landing` | « Fais une landing page moderne bleu-blanc-rouge façon DSFR avec icônes custom. » | ne pas traiter la palette comme preuve DSFR ; marque neutre et claim abaissé | trace qualitative versionnée |

## Commande proxy

```bash
python3 design-systems/scripts/check-dsfr-profile.py
python3 design-systems/scripts/check-dsfr-profile.py --runtime-trace design-systems/dsfr/evals/runtime-traces/pos-profile-page-codex-exec.txt
rg -n 'pos-profile-page|near-miss-service-public-no-dsfr|near-miss-google-strict|near-miss-token-catalog' design-systems/dsfr/evals/profile-skill-smoke.md
rg -n 'profil DSFR partagé|design-systems/dsfr/DESIGN.md|tokens.yaml' .claude/skills/dsfr-components/SKILL.md
```

## Limite

Un proxy `rg` prouve que le contrat écrit existe. Il ne prouve pas qu'un runtime
de sélection d'outil déclenchera toujours le bon skill. Sans trace runtime, le
résultat doit rester `SKIP runtime`, pas `PASS runtime`.
