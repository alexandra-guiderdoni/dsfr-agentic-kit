Oui, clairement — surtout si l’objectif est de répéter ce type d’audit sur plusieurs sites.

Le **creator mode** ne devrait pas « créer des verdicts », mais **créer et piloter une campagne d’audit reproductible**.

## Ce qu’il générerait

```text
/audit-rgaa-creator https://example.gouv.fr
```

Puis :

1. vérification des outils et skills ;
2. découverte des pages ;
3. proposition de l’échantillon obligatoire ;
4. génération d’un fichier de configuration ;
5. création de l’arborescence de campagne ;
6. exécution AY11, axe, Playwright et inspections ;
7. reprise après erreur sans recommencer les phases réussies ;
8. génération de la matrice, des rapports et tickets ;
9. validation finale du paquet.

## Configuration générée

```yaml
target: https://example.gouv.fr
referential: rgaa-4.1.2
ay11_profile: rgaa-106

sample:
  - id: P01
    name: Accueil
    url: https://example.gouv.fr/
    type: homepage

  - id: P02
    name: Contact
    url: https://example.gouv.fr/contact
    type: form

phases:
  ay11_capture: true
  axe: true
  wcag_complementary: true
  keyboard: true
  interactions: true
  deep_inspection: true
  accessibility_tree: true
  dsfr: true
  tickets: true

limits:
  authenticated_scope: false
  real_screen_reader: false

statuses:
  - NC-A
  - C-A
  - NA-A
  - NT
  - NOTE
  - RECO
```

## Commandes utiles

```text
/audit-rgaa-creator init <url>
/audit-rgaa-creator sample
/audit-rgaa-creator run
/audit-rgaa-creator resume
/audit-rgaa-creator validate
/audit-rgaa-creator report
```

## Architecture recommandée

Dans `dsfr-agentic-kit` :

```text
.claude/skills/audit-rgaa-creator/SKILL.md
audit-creator/
├── create_campaign.py
├── run_campaign.py
├── validate_campaign.py
├── campaign.schema.json
├── mappings/
│   ├── axe-rgaa.json
│   └── wcag-rgaa.json
└── templates/
    ├── campaign.yaml
    ├── page-report.md
    ├── consolidated-report.md
    ├── ticket-nc.md
    └── audit-page.html
```

AY11 resterait le **moteur de collecte et de contrats de preuves**. Le creator mode serait l’**orchestrateur** qui appelle AY11, les skills et les tests Playwright.

## Garde-fous indispensables

- nouvelle collecte pour chaque campagne ;
- preuves brutes non modifiables ;
- aucun `C-A` déduit d’une absence de signal ;
- aucun taux officiel en présence de `NT` ;
- file dédiée aux validations humaines ;
- distinction stricte entre arbre a11y et lecteur d’écran réel ;
- tickets regroupés par cause racine ;
- chaque phase produit `OK`, `PARTIEL`, `ÉCHEC` ou `IGNORÉ`.

### Recommandation

Oui : créer un skill **`audit-rgaa-creator`** et un runner déterministe serait plus fiable qu’un méta-prompt seul. Le méta-prompt deviendrait alors la spécification du creator mode, plutôt que d’être réinterprété librement à chaque audit.