# Contrat méthode du design agentique

Cette référence sert uniquement à publier, stabiliser ou évaluer `agentic-design-harness`. Elle rend explicites les choix de méthode que le `SKILL.md` garde courts pour préserver le runtime.

## BRANCH-MAP

| Branche | Déclencheur utilisateur ou modèle | Étapes nécessaires | Références nécessaires | Critère de fin |
|---|---|---|---|---|
| Prototype HTML | `prototype HTML`, `Claude Design-like`, artefact interactif inspectable | 1. cadrer ; 2. cartographier sources ; 3. composer ; 4. vérifier rendu ; 5. transmettre | commune: `SKILL.md` ; conditionnelle: `references/sources.md` si sources externes ou prompt tiers | DONE-CRITERION: fichier HTML, variantes ou réglages attendus, URL ou chemin ouvert, captures desktop/mobile ou limite, console citée |
| Maquette, deck ou one-pager | `maquette`, `deck`, `one-pager`, écran statique | 1. cadrer format ; 2. lire charte ; 3. composer ; 4. vérifier viewport ou export ; 5. transmettre | commune: `SKILL.md` ; conditionnelle: `references/sources.md` si hiérarchie des sources à trancher | DONE-CRITERION: artefact lisible, sources et hypothèses listées, viewport ou export cité, preuve visuelle ou limite |
| Handoff multi-agent | `handoff`, reprise Claude/Codex/GLM, stabilisation d'artefact | 1. extraire chemins ; 2. lister sources ; 3. nommer preuves ; 4. nommer limites ; 5. nommer autonomie, clauses déclenchées et condition d'arrêt | commune: `SKILL.md` ; conditionnelle: sorties de vérification locales | DONE-CRITERION: handoff avec artefact, sources, preuves, limites/non vérifié, autonomie, clauses déclenchées et commande ou point d'arrêt |
| Brief ambigu | demande design réelle mais sources, droits, audience ou preuve insuffisants | 1. nommer l'ambiguïté ; 2. poser au plus trois questions ; 3. demander un brief écrit si plus est nécessaire | commune: `SKILL.md` | DONE-CRITERION: mini-brief complété ou arrêt explicite faute de brief |
| Brief suffisant ou tweak local | sources et sortie attendue assez claires | 1. cadrer rapidement ; 2. avancer sans rituel de questions ; 3. vérifier le rendu | commune: `SKILL.md` | DONE-CRITERION: artefact ou modification livrée avec preuve, ou `non vérifié` motivé |
| Reproduction propriétaire sans droits | demande de copie distinctive sans contexte légitime | 1. refuser la reproduction ; 2. proposer une direction originale ; 3. nommer les sources ou droits manquants | commune: `SKILL.md` | DONE-CRITERION: refus borné et alternative originale proposée |
| Évaluation ou publication du skill | `évalue`, `stabilise`, `publie`, baseline robuste | 1. lire le skill ; 2. lire cette référence ; 3. vérifier structure ; 4. vérifier routage ; 5. vérifier rendu représentatif | commune: `SKILL.md` ; commune: `references/method-contract.md` ; conditionnelle: `references/sources.md` | DONE-CRITERION: score structurel, smoke positif/négatif, preuve navigateur et fiche wiki si publication |

## COLOCATION

| Concept critique | Définition | Règles | Limites/pièges | Emplacement unique | Justification si dispersé |
|---|---|---|---|---|---|
| Artefact inspectable | Livrable visuel ouvert, capturé ou explicitement non vérifiable | créer le plus petit artefact utile ; vérifier rendu avant conclusion | HTML écrit sans rendu n'est pas une preuve | `SKILL.md` étapes 3 et 4 | NA |
| Routage négatif | Cas proches qui doivent rester hors contexte | refuser le déclenchement pour correction frontend cadrée, conversion documentaire, audit accessibilité spécialisé, image isolée ou composant DSFR déjà cadré | surcharge du runtime et conflit avec skills spécialisés | `SKILL.md` section `Quand l'utiliser` | NA |
| Source faible | Source utile pour patterns mais non autoritaire | prompts tiers après sources locales et officielles | ne pas copier prose, identité de runtime ou outils hôtes | `references/sources.md` | séparé car requis seulement si sources externes |
| Profil design system | Routeur partagé sous `design-systems/<system>/DESIGN.md` | lire point d'entrée, tokens et références ciblées ; ne pas copier dans le skill générique | duplication de source, surcharge de contexte, dépendance cachée à un système précis | `SKILL.md` étape 2 ; profil externe | dispersé car le skill reste agnostique et le profil sert plusieurs skills |
| Autorat d'artefact | Responsabilité du markup final et de sa cohérence | sous-agents autorisés pour exploration et vérification ; markup final consolidé dans le contexte principal | déléguer le HTML final produit des approximations non relues | `SKILL.md` étape 3 | NA |
| Handoff agnostique | Reprise par agent ou humain sans dépendre d'un modèle précis | artefact, sources, preuves, limites, autonomie, clauses déclenchées, commande ou point d'arrêt | ne pas faire d'un nom Claude, Codex ou GLM une source d'autorité | `SKILL.md` étape 5 | NA |
| Droits d'usage | Autorisation ou contexte légitime de reproduction visuelle | refuser la reproduction distinctive sans source ou droit | proposer une direction originale plutôt qu'une copie | `SKILL.md` étape 1 et contraintes | proche du cadrage et du blocage |

## LEXICAL-CANDIDATES

| Intention comportementale | Candidats | Rejetés | Retenu | Effet sémiotique | Raison |
|---|---|---|---|---|---|
| Déclencher la bonne classe de tâche | design, UI, Claude Design-like, prototype, artifact, visual harness, design agentique | UI, design, artifact, visual harness | design agentique | cadrage : lie création visuelle, agents et preuve | assez spécifique pour exclure la simple correction CSS |
| Exiger une sortie vérifiable | preuve, capture, rendu, inspectable, evidence, verification | evidence, verification | preuve | trace : force commande, capture, log ou limite | aligné avec AGENTS.md et `verifier-etat` |
| Éviter la maquette générique | source, charte, DESIGN.md, tokens, screenshot, assets | charte seule, assets seuls | source | schème : l'agent lit avant de dessiner | couvre fichiers locaux, web et prompts tiers |
| Préparer la reprise | passation, reprise, handoff, transfert, livraison | passation, transfert | handoff | institution : nomme l'objet attendu en fin de travail | vocabulaire déjà présent dans demandes multi-agents |

## INCARNATION-PROBE

| Candidat | Incarnable ? | 3-5 mouvements naturels | Limites/triage | Décision probe |
|---|---|---|---|---|
| design agentique | oui | cadrer l'intention ; lire sources ; produire artefact ; vérifier rendu ; transmettre | ne couvre pas une correction CSS locale déjà spécifiée | retenir |
| tweakable-html | incertain | exposer valeurs ; persister réglages ; relire rendu | trop spécifique hors besoin réel de HTML pilotable | écarter du runtime, garder optionnel |
| Claude Design-like | oui mais risqué | repérer expérience cible ; extraire invariants ; traduire en contrat portable | ne doit pas devenir copie de prompt ou de runtime Claude | retenir comme déclencheur, pas comme autorité |

## INVESTIGATION-WORK

| Branche | Actions d'investigation obligatoires | Preuve exigée | Critère renforcé avant split | Observation précipitation | Type de split | Décision split |
|---|---|---|---|---|---|---|
| Prototype HTML | lire sources locales ; vérifier assets ; rédiger ou consolider le markup final depuis ces sources ; ouvrir ou servir le rendu ; inspecter console | matrice de sources, captures ou limite, console, état interactif si présent | trois usages montrent que prototype et deck divergent vraiment | non observée après critères de fin | aucun | pas de split |
| Maquette, deck ou one-pager | lire charte ; vérifier format ; contrôler viewport ou export | artefact, viewport ou export, preuve visuelle ou limite | divergences de format impossibles à tenir par une branche | non observée | aucun | pas de split |
| Handoff multi-agent | relire chemins ; citer preuves ; nommer limites, autonomie, clauses déclenchées et point d'arrêt | handoff exploitable sans conversation avec commande ou chemin de reprise | un agent échoue à reprendre malgré handoff | non observée | aucun | pas de split |
| Évaluation ou publication | structure check ; smoke positif ; near-miss ; vérification navigateur ; fiche wiki | rapport robuste ou score, sorties smoke, captures, index wiki | baseline robuste reste sous 90 après correction du contrat | observée : score robuste 84 malgré preuve externe | référence conditionnelle | split en `method-contract.md` |

## LEADING-WORDS

| Mot conducteur | Comportement condensé | Répétition token | Trace observée | Test no-op |
|---|---|---|---|---|
| design agentique | transforme demande visuelle en processus agentique prouvable | description, titre, fiche wiki | smoke positif route vers `agentic-design-harness` | PASS : sans ce mot, routage précédent allait vers `generate-design` |
| source | lire avant de dessiner et classer le poids de preuve | étapes 1-2, `references/sources.md` | matrice `source-matrix.md` du scénario représentatif | PASS : retire la règle et le skill autorise une maquette générique |
| artefact | livrer un objet inspectable, pas une intention | description, étapes 1, 3, 5 | `prototype-pricing.html` produit | PASS : sans artefact, la sortie peut rester conseil |
| preuve | finir par capture, console, log ou limite | étapes 1, 4, 5, checklist | `render-report.json`, captures desktop/mobile | PASS : sans preuve, HTML écrit devient conclusion non vérifiée |
| handoff | rendre la reprise possible par un autre agent | description, étape 5, checklist | fiche wiki et rapport final listent chemins et limites | PASS : sans handoff, le travail dépend de la conversation |

## PRUNING

| Cible | Décision | Preuve comportementale de conservation |
|---|---|---|
| Duplication | conservé minimalement | `preuve`, `source` et `handoff` sont répétés seulement aux points où ils déclenchent action, critère de fin ou livraison |
| Sédiment | supprimé | outils hôtes `done`, `show_to_user`, `fork_verifier_agent`, helper Claude et EDITMODE obligatoire ne sont pas dans le runtime |
| Sprawl | déplacé | contrat méthode déplacé ici ; sans déplacement, le `SKILL.md` gonflerait pour une évaluation seulement |
| No-op | supprimé | aucune règle générale du type "sois créatif" ou "sois rigoureux" ; chaque règle exige source, artefact, preuve ou arrêt |

Saint-Exupéry : si `references/method-contract.md` était inline, le skill deviendrait moins lisible pour produire un design courant ; si elle disparaît, l'évaluation robuste ne voit plus les invariants de méthode et redevient bruitée.

## TALK-FIDELITY

| Marqueur | Couverture | Preuve |
|---|---|---|
| skill hell | présent | contrat déplacé en référence conditionnelle pour ne pas surcharger le runtime |
| Superpowers / skills invoqués par l'utilisateur | NA justifié | skill agnostique du workspace, pas méthode Superpowers |
| description comme pointeur de contexte | présent | description front-loade `Design agentique` et exclut correction CSS |
| 2PRD | NA justifié | pas un skill de PRD |
| test seam | présent | smoke positif, near-miss négatif et vérification navigateur jouent le rôle d'oracle |
| domain modeling | présent | source, artefact, preuve, handoff sont les concepts du domaine |
| context.md | NA justifié | le contexte design vient de `DESIGN.md`, tokens, CSS, screenshots et assets |
| ADR | NA justifié | pas une décision d'architecture logicielle durable |
| plan mode | présent | étape 1 cadre avant composition, mais ne force pas dix questions rituelles |
| Matt Pocock | NA justifié | référence WGS appliquée via hiérarchie, leading words et pruning |
| skill-writing-great-skills | présent | méthode alignée sur invocation, progressive disclosure, co-location et pruning |

## METHOD-COMPLETE

Scénario représentatif : produire un prototype pricing HTML depuis `DESIGN.md` et tokens CSS, avec trois variantes et preuve mobile/desktop.

Avec/sans skill : avant correction d'alias, le routage positif partait vers `generate-design`; après front-load de la description Codex, il part vers `agentic-design-harness`. Le near-miss CSS retourne `SKILL: none`.

Déclenchement modèle : prompt positif sans nommer le skill -> `SKILL: agentic-design-harness`; near-miss -> `SKILL: none`.

Trace des mots conducteurs : mini-brief, matrice de sources, artefact `prototype-pricing.html`, rapport de rendu et fiche wiki reprennent source, artefact, preuve et handoff.

Test no-op : la première capture mobile a révélé une vraie erreur CSS de grille enterprise ; la correction a changé le rendu observable. Le test n'était donc pas décoratif.

Preuve : `.claude/outputs/agentic-design-harness/2026-07-06-161208/render-report.json`, captures desktop/mobile, smoke outputs v2 et fiche wiki indexée.

Verdict : GO comportemental local. La baseline robuste initiale est stable mais médiane `84/100`, ce qui justifie cette référence conditionnelle avant une nouvelle mesure.
