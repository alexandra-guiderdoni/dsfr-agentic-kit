# PRD — Un harnais DSFR autonome, consommable par les workflows

**Date** : 21 octobre 2026. **Actualisation** : 22 octobre 2026.
**Statut** : exploration réalisée ; source canonique et profils livrés ;
réception #8 et bascule #12 suivies dans [le reçu de migration](../RECEPTION-ET-BASCULE.md).

**Exploration de référence** : [issue #9](https://github.com/alexandra-guiderdoni/dsfr-agentic-kit/issues/9).

## But et parcours attendu

Faire de `dsfr-agentic-kit` l’unique dépôt source du produit DSFR : génération,
audits, références, preuves, rapports et tests. Une personne doit pouvoir
l’installer et l’utiliser sans le workflow personnel qui le produit aujourd’hui.
Ce workflow deviendra un consommateur facultatif, au même titre qu’un autre hôte.

Parcours cible, exercé dans les limites du reçu : installer une version du produit,
préparer ses dépendances déclarées, générer une page depuis un brief, exécuter
une campagne représentative et produire son rapport dans un projet distinct.
Une mise à jour doit permettre de reprendre une campagne avec son outillage
identifié, sans perdre les qualifications humaines.

## Contrat cible

- **Autonomie complète** : aucune fonction du périmètre DSFR retenu ne doit
  dépendre du code, des règles, des alias ou des caches du workflow personnel.
  L’installation prépare ou vérifie explicitement les prérequis nécessaires.
- **Source unique** : les évolutions du produit et les mises à jour DSFR sont
  maintenues dans le kit. Les distributions proviennent de ces mêmes sources ;
  aucun retour obligatoire par le workflow personnel ou par un miroir.
- **Distribution** : le plugin est l’entrée utilisateur visée et doit donner
  accès à toute la chaîne. Une installation gérée peut fournir ses ressources
  d’exécution ; un second clone à entretenir manuellement ne vaut pas preuve
  d’autonomie du plugin. Comparer l’archive produite par `build-plugin.sh` et
  l’installation marketplace, en consignant l’hôte et sa version pour chaque
  essai. Un checkout géré par l’hôte ne se confond pas avec un clone manuel.
  Chaque voie doit préserver l’arborescence attendue ou résoudre explicitement
  les racines du produit ; les calculs positionnels comme `SCRIPT.parents[4]`
  doivent être exercés dans leur disposition réelle.
- **Profil léger** : préserver la possibilité d’exposer les outils utiles sans
  métacouche d’orchestration agentique avancée. Même source et même version que
  le profil complet ; aucune copie maintenue séparément. Le contenu des profils
  sera arrêté après inventaire, sans réduire silencieusement les usages actuels.
  Hypothèse à vérifier : cette métacouche désigne l’orchestration avancée,
  notamment `agentic-design-harness`, à distinguer des règles propres à l’hôte.
  Les outils DSFR sélectionnés, leurs références métier, preuves et protections
  restent utilisables sans cette orchestration.
- **Frontière produit/projet** : campagnes, qualifications, captures et rapports
  vivent hors de l’installation. Aucun ticket, secret ou contenu privé d’un
  consommateur ne doit entrer dans la distribution publique.
- **AY11** : reste externe et optionnel, avec son raccordement actuel préservé.
  Son achèvement et une nouvelle intégration sont hors périmètre.
- **Indépendance des hôtes** : le contrat produit reste agnostique ; les entrées
  Claude, Codex ou ZCode/GLM sont des adaptateurs, sans seconde implémentation.

L’autonomie ne signifie pas embarquer Python, Node ou un navigateur dans une
archive. Elle exige une installation reproductible, des dépendances explicites
et des erreurs ou états partiels observables lorsqu’une capacité manque.

## État initial observé et choix

Le tableau suivant conserve le diagnostic du 21 octobre avant implémentation.
Les preuves et décisions postérieures sont dans [le suivi de réception](../RECEPTION-ET-BASCULE.md).

Les revues Fable 5.1 et « connus inconnus » du 21 octobre soutiennent la
centralisation, avec les réserves suivantes confirmées dans les sources :

| Affirmation | Source inspectée | Verdict | Impact |
|---|---|---|---|
| Le plugin actuel contient toute la chaîne | [Build](../../scripts/build-plugin.sh) | Faux pour l’archive : skills seuls | Résoudre les ressources et contrôles manquants |
| La portabilité des audits natifs est démontrée | [Test standalone](../../scripts/tests/check-standalone-install.sh) | Partiel : copie conservant l’arborescence du clone | Exercer l’installation native |
| Les campagnes tracent déjà tout l’outillage | [Campagne](../../.claude/skills/audit-rgaa-creator/scripts/audit_campaign.py) | Partiel : empreintes présentes, version exacte du harnais non établie | Conserver les preuves et établir la reprise |
| La séparation produit/projets est terminée | [Manifeste](../../config/agentic-design-packages.yaml) et [spec précédente](2026-09-10-durcissement-harnais-dsfr.md) | Incomplète | Inventorier la propriété avant transfert ou retrait |
| Toute écriture de campagne dans le kit est refusée | [Initialisation de campagne](../../.claude/skills/audit-rgaa-creator/scripts/audit_campaign.py) | Partiel : option masquée `--allow-inside-kit` | Identifier ses usages et proposer son retrait ou son confinement aux fixtures isolées |

| Option | Intérêt | Limite | Décision |
|---|---|---|---|
| Produit canonique autonome, distribué par plugin | Une maintenance, usage indépendant et intégration facultative aux workflows | Packaging, chemins et reprise à prouver | Cible retenue |
| Clone manuel versionné avec entrée plugin | Réutilise la disposition actuelle et facilite l’identification Git | Installation supplémentaire à gérer ; autonomie du plugin non démontrée | Transition possible, sans remplacer la cible |

Ce cadrage étend la spec de septembre et les issues [#2](https://github.com/alexandra-guiderdoni/dsfr-agentic-kit/issues/2),
[#6](https://github.com/alexandra-guiderdoni/dsfr-agentic-kit/issues/6),
[#7](https://github.com/alexandra-guiderdoni/dsfr-agentic-kit/issues/7) et
[#8](https://github.com/alexandra-guiderdoni/dsfr-agentic-kit/issues/8).
Réutiliser leurs protections et contrats ; ne pas dupliquer les moteurs.
Le contrat de consommation versionnée et son vérificateur ont été livrés dans
#6 ; #11 ajoute la vérification automatique avant les écritures de campagne.
Voir [le contrat effectivement livré](../CONSOMMATION-VERSIONNEE.md).

## Critères de réussite et preuves avant bascule

| ID | Résultat exigé | Preuve attendue |
|---|---|---|
| A1 | Installation indépendante | Environnement isolé, workflow source inaccessible, dépendances et téléchargements déclarés ; aucune résolution vers le poste personnel |
| A2 | Chaîne complète accessible | Installation native puis génération, contrôles navigateur représentatifs, campagne et rapport ; tracer les commandes, chemins et versions réellement utilisés |
| A3 | Installation intacte | Empreinte avant/après et refus des sorties internes, y compris via lien symbolique ; examiner aussi `--allow-inside-kit` et statuer sur son retrait ou son confinement aux tests, sans déroger à la frontière produit/projet |
| A4 | Campagne versionnée | Campagne en A, mise à jour B puis reprise ; A et B identifiées par commit et empreinte, A disponible, qualifications conservées et références inchangées sans migration explicite |
| A5 | Dépendances honnêtes | AY11 absent puis environnement Python différent ; phases disponibles, sauts et erreurs explicités, sans faux succès ni conformité automatique |
| A6 | Source unique et profils cohérents | Inventaire de toutes les origines actives, parité des fonctions conservées et profils dérivés des mêmes sources ; après retrait autorisé, fonctionnement sans les anciennes copies |

Une preuve sur un hôte ne valide que cet hôte. Les autres adaptateurs restent
non vérifiés tant que leur parcours n’est pas exercé. Un échec de l’archive ne
permet pas de conclure sur le marketplace, ni l’inverse. Le scénario A4 s’appuie
sur les empreintes existantes et ajoute l’identification immuable du kit ;
les qualifications et références à comparer sont fixées avant l’essai sur un
site local stable. Il ne promet pas l’identité de résultats sur un site distant
qui aurait changé.

## Précisions issues de la relecture Fable

Relecture du 21 octobre 2026 : aucun P1 bloquant pour l’exploration ; cinq P2
intégrés ci-dessous. Leur exécution et leurs limites sont désormais consignées
dans le suivi de réception ; ce tableau conserve les exigences initiales.

| Retour | Précision intégrée |
|---|---|
| P2-1 — Racines positionnelles | Contrat de distribution et essais A1/A2 dans l’arborescence installée |
| P2-2 — Deux voies plugin | Comparaison archive/marketplace ; hôte et version consignés |
| P2-3 — Métacouche du profil léger | Hypothèse de découpage explicite, à vérifier par inventaire |
| P2-4 — Identité de l’outillage | A4 complète les empreintes existantes par l’identité immuable du kit |
| P2-5 — Écriture interne masquée | A3 examine `--allow-inside-kit` et son usage ; frontière produit/projet maintenue |

## Séquence de travail

1. Ouvrir une exploration bornée : inventaire source/installation/projets,
   dépendances, profils actuels et consommateurs ; relever les recouvrements
   avec les tickets existants.
2. Dans un espace isolé, éprouver A1 à A5 sur un petit scénario local stable.
   Enregistrer chaque critère comme démontré, échoué ou non exercé. Un échec
   documenté termine l’exploration ; il ne valide pas la bascule.
3. Arrêter le contrat d’installation et de reprise sur ces preuves. Solliciter
   Ask Matt seulement pour une question technique encore bloquante ; aucune
   consultation supplémentaire n’est exécutée par ce PRD.
4. Découper les tickets d’exécution selon les dépendances observées, puis
   transférer les sources et adapter les consommateurs sans perte de fonctions.
5. Après parité et réception, autoriser séparément le retrait des copies,
   règles et synchronisations DSFR du workflow personnel et du miroir.
   Le workflow ne conserve que le branchement au produit ; les historiques
   utiles sont préservés.

## Limites de ce cadrage

Ce PRD définit la cible ; les livraisons sont retracées séparément dans le reçu.
Aucune refonte AY11 n’est incluse. Les campagnes réelles et données privées ne sont pas des fixtures.
Les audits conservent leurs limites de couverture et la qualification humaine ;
aucun résultat automatique ne devient une conformité DSFR ou RGAA générale.
Chaque exigence garde le verdict et la portée des preuves effectivement obtenues ;
les exigences non exercées ne sont pas présentées comme réussies.
