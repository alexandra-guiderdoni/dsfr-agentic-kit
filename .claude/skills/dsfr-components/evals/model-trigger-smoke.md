# Smoke de déclenchement modèle

Objectif : vérifier que le skill se déclenche sur une demande DSFR sans que le
prompt utilisateur nomme `dsfr-components`, et qu'il refuse les demandes qui
relèvent d'un audit RGAA complet, d'une application front-end ou d'un contexte
service public sans demande DSFR explicite.

| ID | Prompt utilisateur sans nom du skill | Décision attendue | Critère PASS |
| --- | --- | --- | --- |
| `pos-page-form` | « Crée une page HTML statique DSFR pour une demande de rendez-vous administratif. » | Déclencher la branche `page complète`. | Le compte rendu mentionne `generate_page.py`, le type `form`, la référence ciblée et les limites. |
| `pos-component-accordion` | « J'ai besoin d'un composant accordéon DSFR à intégrer dans une page service public. » | Déclencher la branche `composant isolé`. | Le compte rendu mentionne `generate_component.py accordion`, la section accordéons et l'absence de conteneur vide. |
| `pos-audit-local` | « Vérifie si ce HTML généré respecte les composants DSFR utilisés. » | Déclencher la branche `routage audit DSFR ponctuel` si le HTML ou fichier est fourni. | Le compte rendu applique `references/prompt-conformite-dsfr.md`, cite les sources lues et produit un statut borné. |
| `pos-js-accordion-proof` | « Vérifie ce composant accordéon DSFR généré, y compris son comportement JS. » | Déclencher la branche `routage audit DSFR ponctuel` si le HTML est fourni ; sinon demander le HTML à contrôler. | Le compte rendu sépare cibles ARIA statiques et preuve navigateur ; sans navigateur, le comportement JS est déclaré non vérifié. |
| `near-miss-rgaa` | « Audite la conformité RGAA complète de ce site existant. » | Ne pas générer ; router vers `audit-rgaa-dsfr` ou `audit-accessibilite-web`. | Le compte rendu indique le routage et ne produit pas de page DSFR. |
| `near-miss-react` | « Crée une application React DSFR avec composants dynamiques. » | Ne pas utiliser ce skill seul. | Le compte rendu indique que le skill produit seulement du HTML statique et propose un cadrage front-end séparé. |
| `near-miss-service-public-no-dsfr` | « Crée une page HTML pour un service public de prise de rendez-vous. » | Ne pas déclencher ce skill automatiquement. | Le compte rendu demande si DSFR est requis ou traite la page hors skill DSFR ; aucune référence DSFR n'est chargée sans confirmation. |
| `near-miss-publication` | « Prépare cette page DSFR pour publication officielle et conformité RGAA. » | Ne pas conclure avec ce skill seul ; router la conformité complète. | Le compte rendu retire tout claim `conforme`, nomme les preuves manquantes et propose `audit-rgaa-dsfr` ou `audit-accessibilite-web`. |

Un PASS modèle réel exige d'observer la décision du runtime qui choisit les
skills. Quand cette surface n'est pas disponible, ce fichier sert de
spécification de smoke et la limite doit être nommée.

## Proxy local non runtime

Depuis Codex, la sélection runtime des skills n'est pas observable. Le proxy
minimal consiste à vérifier que les prompts positifs et near-miss restent
présents dans cette fiche et que `SKILL.md` contient les exclusions
correspondantes :

```bash
SKILL_DIR=.claude/skills/dsfr-components  # adapter à l'emplacement d'installation
rg -n 'pos-page-form|pos-component-accordion|pos-audit-local|pos-js-accordion-proof|near-miss-rgaa|near-miss-react|near-miss-service-public-no-dsfr|near-miss-publication' $SKILL_DIR/evals/model-trigger-smoke.md
rg -n 'React|Vue|Angular' $SKILL_DIR/SKILL.md
rg -n 'audit RGAA complet|publication|certification' $SKILL_DIR/SKILL.md
rg -n 'Besoin DSFR explicite|service public' $SKILL_DIR/SKILL.md
```

PASS proxy signifie seulement que le contrat de déclenchement est couvert dans
les sources du skill. Il ne prouve pas que le runtime sélectionne réellement le
skill.
