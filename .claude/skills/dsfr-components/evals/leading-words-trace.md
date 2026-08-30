# Trace des mots conducteurs

Objectif : rendre observable l'effet des mots conducteurs du skill sans
prétendre prouver le déclenchement runtime du modèle.

## Scénario représentatif

Demande : « Crée une page HTML statique DSFR de demande de rendez-vous
administratif. »

## Trace attendue dans le compte rendu

| Mot conducteur | Trace observable attendue | Preuve minimale |
| --- | --- | --- |
| `aligné DSFR avec limites` | verdict borné : génération locale possible, publication et conformité RGAA exclues sans audit dédié | mention du verdict local ou d'un routage vers `audit-rgaa-dsfr` |
| `référence ciblée` | source précise citée au lieu d'une lecture large | `references/patterns/nom-prenom.md`, `references/components.md` puis sous-fichier utile, ou autre pointeur chargé |
| `preuve observable` | commande, fichier ou sortie inspectable cité | smoke HTML, sortie de script, absence de `href="#"`, absence de cible ARIA ou contrôle d'artefacts |

## Commandes de contrôle

```bash
find .claude/skills/dsfr-components \( -name '.DS_Store' -o -name '__pycache__' \) -print
python3 .claude/skills/dsfr-components/scripts/generate_page.py --type form --title "Trace mots conducteurs" >/tmp/dsfr-leading-words.html
python3 .claude/skills/dsfr-components/scripts/generate_component.py accordion >/tmp/dsfr-leading-accordion.html
rg -n 'id="prenom"|autocomplete="given-name"|id="nom"|autocomplete="family-name"|target="_blank" rel="noopener"' /tmp/dsfr-leading-words.html
rg -n 'aria-controls="accordion-1"|id="accordion-1"|aria-expanded="false"' /tmp/dsfr-leading-accordion.html
# -U : la sortie du générateur est multi-ligne ; sans lui, une contrainte posée
# sur la ligne de continuation d'une balise ouverte échappe au motif.
! rg -U -n '<(input|select|textarea)[^>]*(\s|\n)(required|aria-required=|pattern=|aria-invalid=)' /tmp/dsfr-leading-words.html
```

## Verdict attendu

PASS si :

- la recherche d'artefacts ne retourne aucune ligne ;
- le formulaire contient prénom puis nom avec `given-name` et `family-name` ;
- le formulaire généré ne contient pas de contrainte native au repos ;
- les liens externes générés avec `target="_blank"` contiennent `rel="noopener"` ;
- l'accordéon généré expose une cible `aria-controls` statique ; son
  comportement JS reste non vérifié sans preuve navigateur ;
- le compte rendu relie au moins un mot conducteur à une preuve concrète.

NO-GO si le compte rendu emploie les mots conducteurs comme slogans sans fichier,
commande ou verdict borné associé.
