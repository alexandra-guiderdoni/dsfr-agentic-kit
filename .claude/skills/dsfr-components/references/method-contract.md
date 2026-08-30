# Contrat de méthode

Référence ciblée pour publication, scoring, refactor du skill ou investigation
de prévisibilité. Ne pas charger pour une génération simple de page ou de
composant : `SKILL.md` suffit alors.

## INVESTIGATION-WORK

| Branche | Actions d'investigation obligatoires | Preuve exigée | Critère renforcé avant split | Observation précipitation | Type de split | Décision split |
| --- | --- | --- | --- | --- | --- | --- |
| page complète | lire profil partagé si présent, vérifier type, sortie, template et HTML généré | commande lancée, fichier ou stdout inspecté, limites citées | si deux variantes de page réclament des workflows incompatibles | non observée après clarification type/sortie | aucun | garder dans ce skill |
| composant isolé | chercher la section exacte, vérifier variante, générer, inspecter liens/ARIA | nom du composant, référence ciblée, fragment produit | si un composant exige une logique métier autonome | non observée ; la recherche ciblée suffit | aucun | garder dans ce skill |
| audit DSFR ponctuel | distinguer vérification DSFR locale, audit RGAA complet, conformité globale et publication | tableau d'écarts borné sans statut `conforme`, ou routage vers `audit-rgaa-dsfr` / `audit-accessibilite-web` | si l'audit devient remédiation multi-fichiers ou audit complet | possible hors génération | invocation | ne pas importer les grilles RGAA ici : router vers le skill d'audit dont le mot conducteur est l'audit, ce qui évite le coût de contexte permanent |

## COLOCATION

| Concept critique | Définition | Règles | Limites/pièges | Emplacement unique | Justification si dispersé |
| --- | --- | --- | --- | --- | --- |
| revendication DSFR/RGAA | dire seulement ce qui a été vérifié | ne pas écrire `conforme` sans preuve dédiée | les scripts produisent un point de départ, pas une certification | cette table définit la règle ; `Quand NE PAS utiliser` et `Vérification` l'appliquent | dispersion volontaire pour bloquer le claim au déclenchement et à la livraison |
| sortie générée | page ou fragment HTML statique | ne jamais écraser ; remplacer les liens factices ; vérifier ARIA | stdout si `--output` absent | cette table définit la règle ; `Types et arguments`, `Génération`, checklist l'appliquent | dispersion volontaire entre contrat CLI, commande et critère final |
| référence ciblée | charger seulement la section utile | ne pas lire toute une famille de composants | fallback WebFetch seulement si local manque | cette table définit la règle ; `CONTEXT-POINTERS` l'applique | dispersion volontaire car les pointeurs contiennent les chemins exacts |
| déclenchement DSFR | déclencher sur demande DSFR explicite, pas sur service public seul | couvrir positifs, audit ponctuel et near-miss ; déclarer proxy si runtime non observable | le modèle peut confondre page administrative, audit RGAA et génération DSFR | cette table définit la règle ; `Déclencheurs`, `BRANCH-MAP` et `evals/model-trigger-smoke.md` l'appliquent | dispersion volontaire entre sélection, routage et preuve de non-régression |

## LEXICAL-CANDIDATES

| Intention comportementale | Candidats | Rejetés | Retenu | Effet sémiotique | Raison |
| --- | --- | --- | --- | --- | --- |
| empêcher les claims abusifs | conforme, certifié, officiel, proche, aligné, prouvé, limité | conforme, certifié, officiel | `aligné DSFR avec limites` | cadrage: bloque la certification implicite | exprime la génération utile sans promettre l'audit |
| forcer la preuve de fin | vérifier, relire, prouver, observer, tester, constater | vérifier seul | `preuve observable` | trace: exige commande, fichier ou verdict borné | évite une fin déclarative |
| réduire la charge de contexte | tout lire, chercher, cibler, router, filtrer, pointer | tout lire | `référence ciblée` | schème: lecture minimale suffisante | stabilise la progressive disclosure |

## LEADING-WORDS

| Mot conducteur | Comportement condensé | Répétition token | Trace observée | Test no-op |
| --- | --- | --- | --- | --- |
| `aligné DSFR avec limites` | générer sans revendiquer la conformité | description, promesse, contraintes, findings | `evals/local-validation.md` consigne les checks locaux et exclut le GO publication sans audit | PASS si le retrait réintroduit `conforme DSFR/RGAA` ou un GO publication |
| `référence ciblée` | lire seulement la source utile | routage, pièges, checklist | `evals/local-validation.md` rattache le correctif formulaire à `references/patterns/nom-prenom.md` | PASS si le retrait pousse à lire toute la référence |
| `preuve observable` | finir par une sortie vérifiable | branches, vérification, checklist | `evals/local-validation.md` donne les commandes et sorties `PASS generated outputs: pages=12 components=136`, `PASS golden: 21 cas inchangés + invariants OK`, `aria_targets PASS` | PASS si le retrait permet un simple ressenti |

## INCARNATION-PROBE

| Candidat | Incarnable ? | 3-5 mouvements naturels | Limites/triage | Décision probe |
| --- | --- | --- | --- | --- |
| `aligné DSFR avec limites` | oui | choisir script ; lire référence ciblée ; générer ; vérifier liens/ARIA ; nommer limites | ne promet pas publication ni conformité RGAA | retenir |
| `preuve observable` | oui | produire stdout ou fichier ; inspecter HTML ; lancer smoke ; citer verdict ; nommer non-vérifié | ne remplace pas audit humain | retenir |
| `référence ciblée` | oui | chercher section ; lire seulement l'extrait ; citer chemin ; fallback officiel si absent | ne force pas lecture exhaustive | retenir |

## PRUNING

| Cible | Décision | Preuve comportementale de conservation | Saint-Exupéry | Ce qui casserait, se dégraderait ou deviendrait imprévisible |
| --- | --- | --- | --- | --- |
| Duplication | garder `BRANCH-MAP`, garder `CONTEXT-POINTERS`, réduire le routage à un index court | retirer `BRANCH-MAP` rend les fins de branche implicites ; retirer les pointeurs force une lecture large | retirer tout ce qui ne sert pas une branche, une source ou une preuve | sans `BRANCH-MAP`, le skill peut générer sans critère de fin |
| Sédiment | supprimer les revendications de conformité sans preuve dédiée | conserver le claim contredit `aligné DSFR avec limites` et pousse au faux GO publication | retirer les claims agréables qui ne prouvent rien | la livraison redevient imprévisible sur RGAA/publication |
| Sprawl | garder les catalogues et le contrat de méthode hors `SKILL.md` dans `references/` | réintégrer les catalogues ou le contrat complet noie les étapes ; les retirer casse la génération ciblée ou le scoring WGS | garder seulement le pointeur en contexte | lire le skill deviendrait coûteux et la référence ciblée se dégraderait |
| No-op | remplacer `vérifier` par critères observables : liens, ARIA, sortie, limites | les critères forcent une preuve observable au lieu d'une fin déclarative | retirer les injonctions qui ne changent pas le comportement | le compte rendu pourrait se limiter à une impression |

## TALK-FIDELITY

| Marqueur | Couverture | Preuve |
| --- | --- | --- |
| skill hell | NA justifié | skill mono-domaine DSFR, pas routeur |
| Superpowers / skills invoqués par l'utilisateur | NA justifié | pas une méthode de développement |
| description comme pointeur de contexte | présent | frontmatter déclenche trois branches réelles |
| 2PRD | NA justifié | pas un livrable PRD |
| test seam | présent | smoke prompts et near-miss |
| domain modeling | NA justifié | pas de modèle métier durable |
| context.md | NA justifié | références locales déjà dédiées |
| ADR | NA justifié | pas de décision d'architecture |
| plan mode | présent | audit routé hors génération pour éviter la précipitation |
| mots conducteurs dans les traces | présent | `LEADING-WORDS` impose trace observée et test no-op |
| Matt Pocock | NA justifié | pas un skill utilisateur manuel |
| skill-writing-great-skills | présent | branches, mots conducteurs et pruning appliqués |

## METHOD-COMPLETE

Scénario représentatif : « Crée une page HTML statique DSFR de demande de rendez-vous administratif ».
Avec skill : profil DSFR lu si présent, page `form` générée, liens/ARIA vérifiés,
limites citées. Sans skill : risque de page visuelle DSFR avec liens factices ou
claim de conformité.
Déclenchement modèle : smoke prompts positifs, audit ponctuel et near-miss
négatifs dans `evals/model-trigger-smoke.md`, dont le cas service public sans
DSFR explicite.
Trace des mots conducteurs : le compte rendu doit contenir `aligné DSFR avec
limites`, `référence ciblée` ou `preuve observable`, et rattacher le mot à une
commande, un fichier ou un verdict observé.
Test no-op : retirer ces mots réintroduit des claims de conformité, de la lecture
large ou une fin non prouvée.
Preuve observée : `evals/local-validation.md` porte le bloc de commandes
minimales et ses sorties réelles : `PASS generated outputs: pages=12
components=136`, `PASS golden: 21 cas inchangés + invariants OK`,
`aria_targets PASS`, scans `href="#"` et contraintes au repos, contrôle
d'accents et absence d'artefact local. `evals/leading-words-trace.md` relie chaque mot conducteur à
un fichier, une commande ou un statut borné observé.
Runtime modèle : PASS réel seulement si la surface de sélection du modèle est
observable ; depuis Codex, déclarer le proxy `evals/model-trigger-smoke.md` et
le scan des exclusions dans `SKILL.md` sans les présenter comme validation
runtime.
Verdict : GO local borné aux scripts et références lus ; GO publication exclu
sans audit dédié.
