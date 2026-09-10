# Mode opératoire humain

Ce parcours couvre une page simple, une page assemblée depuis un brief et un
audit RGAA ou WCAG. L’humain fixe l’objectif et valide les décisions ; l’agent
produit les artefacts et les preuves bornées.

## Avant de commencer

Indiquer à l’agent deux chemins distincts :

- le kit, en lecture seule ;
- le projet, seul emplacement autorisé pour les livrables.

Utiliser le prompt de `DEMARRAGE-AGENT.md` et préciser l’entrée disponible, la
sortie attendue et le niveau de vérification demandé.

### Pipelines de livrables

Les générateurs Virginie et le retest P06 exigent un projet de travail
existant, fourni par `--project-root` ou `DSFR_PROJECT_ROOT`. Le clone du kit
reste réservé au code et aux références ; les archives, livrables, captures,
fiches de revue et verrous sont écrits dans le projet.

```bash
export DSFR_PROJECT_ROOT="/chemin/vers/mon-projet"
python3 "$KIT_ROOT/scripts/generate-virginie-dsfr-composants.py" \
  --project-root "$DSFR_PROJECT_ROOT"
```

Les destinations explicites sont contrôlées après résolution des liens
symboliques. Une destination qui se trouve dans le kit, ou hors du projet de
travail, est refusée avant toute écriture.

## 1. Écrire un mini-brief

Un brief utile tient en quelques réponses :

```text
Public visé :
Tâche principale :
Contenu obligatoire :
Actions attendues :
Résultat : page simple / page assemblée / audit
Mode de marque : neutre / République française autorisée
Preuve attendue : inspection HTML / navigateur / audit spécialisé
Contraintes ou inconnues :
```

Une information manquante doit être signalée. Elle ne doit pas être remplacée
par une donnée administrative inventée.

## 2. Choisir le parcours

| Objectif | Parcours | Artefacts principaux |
| --- | --- | --- |
| Obtenir rapidement une page structurée | A — page simple | HTML |
| Composer plusieurs blocs depuis un brief | B — page assemblée | `page.json`, HTML, preuve |
| Examiner une page existante | C — audit | rapport et fiches éventuelles |

## Parcours 1 — page simple

Demande type :

```text
Lis DESIGN.md, tokens.yaml et le SKILL.md de dsfr-components dans le kit.
Génère une page DSFR de type formulaire intitulée « Exemple de démarche ».
Écris uniquement dans mon projet et indique les contrôles réellement exécutés.
```

L’agent utilise `generate_page.py` depuis le dossier du skill. Vérifier au
minimum : langue française, région `main`, titre principal, liens sans
placeholder, structure de page et formulation de preuve bornée.

## Parcours 2 — page assemblée

1. Rédiger `brief.md` dans le projet.
2. Demander à l’agent de produire un `page.json` conforme au schéma du skill.
3. Faire vérifier le schéma avant la génération.
4. Générer `page.html` dans le projet.
5. Produire une `preuve.md` indiquant les commandes, résultats et limites.

Demande type :

```text
À partir de brief.md, construis un page.json puis une page HTML assemblée.
Utilise uniquement les composants et champs exposés par dsfr-components.
Refuse les liens dangereux, conserve des identifiants uniques et trace tout
usage autorisé d’HTML brut. Écris les sorties dans mon projet.
```

La démonstration de référence se lance depuis le kit avec :

```bash
bash scripts/demo-dsfr-assembled-page.sh --quiet
```

## Parcours C — audit RGAA ou WCAG

Choisir le skill selon le résultat attendu :

| Besoin | Skill |
| --- | --- |
| Page isolée et premières fiches | `pre-audit-rgaa-dsfr` |
| Audit DSFR par règle et instance, avec code observé et attendu | `audit-dsfr-complet` |
| Portail et rapports d’audit générés avec le builder DSFR | `audit-report-dsfr` |
| Préqualification RGAA par test et instance avec revue des 258 tests | `audit-rgaa-complet` |
| Campagne RGAA multi-pages avec vérification DSFR bornée sur le même échantillon | `audit-rgaa-creator` |
| Audit RGAA cadré | `audit-rgaa-dsfr` |
| Audit WCAG d’une URL ou d’un HTML | `audit-accessibilite-web` |
| Orchestration de plusieurs phases | `audit-a11y-complet` |
| Tests ciblés complémentaires | `tests-conformite-wcag` |
| Vérification spécialisée | `screen-reader-testing` |
| Correction après un audit autorisé | `fix-accessibilite` ou `a11y-loop` |

Demande type :

```text
Audite cette page sans modifier son code. Choisis le skill RGAA ou WCAG adapté,
nomme les tests automatisés et manuels réellement couverts, puis écris le
rapport dans le dossier audit/ de mon projet. Ne produis pas de taux officiel
si des critères applicables restent non testés.
```

Une absence de violation automatisée n’est jamais une conformité. Les tests
manuels non réalisés restent explicitement non vérifiés.

Pour une campagne de 8 à 15 pages avec captures fraîches, reprise, matrice des
106 critères et validation des livrables, suivre
`documentation/AUDIT-RGAA-CREATOR.md`.

## Définition de fin

Le travail est transmissible lorsque l’agent fournit :

- les fichiers créés ou modifiés dans le projet ;
- les sources et skills lus ;
- les commandes exécutées et leurs résultats ;
- le niveau de preuve réellement atteint ;
- les limites, sauts et vérifications humaines restantes.

La publication, l’usage de la marque de l’État et toute déclaration de
conformité restent des décisions séparées.
