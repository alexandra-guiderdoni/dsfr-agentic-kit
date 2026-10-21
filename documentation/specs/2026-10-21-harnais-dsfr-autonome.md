# PRD — Un harnais DSFR autonome, consommable par les workflows

**Date** : 21 octobre 2026. **Statut** : cible confirmée ; exploration technique à lancer.

**Première étape** : [exploration d’autonomie — issue #9](https://github.com/alexandra-guiderdoni/dsfr-agentic-kit/issues/9).

## But et parcours attendu

Faire de `dsfr-agentic-kit` l’unique dépôt source du produit DSFR : génération,
audits, références, preuves, rapports et tests. Une personne doit pouvoir
l’installer et l’utiliser sans le workflow personnel qui le produit aujourd’hui.
Ce workflow deviendra un consommateur facultatif, au même titre qu’un autre hôte.

Parcours cible, non encore démontré : installer une version du produit,
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
  d’autonomie du plugin. Le mécanisme exact reste à éprouver.
- **Profil léger** : préserver la possibilité d’exposer les outils utiles sans
  métacouche d’orchestration agentique avancée. Même source et même version que
  le profil complet ; aucune copie maintenue séparément. Le contenu des profils
  sera arrêté après inventaire, sans réduire silencieusement les usages actuels.
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

## État observé et choix

Les revues Fable 5.1 et « connus inconnus » du 21 octobre soutiennent la
centralisation, avec les réserves suivantes confirmées dans les sources :

| Affirmation | Source inspectée | Verdict | Impact |
|---|---|---|---|
| Le plugin actuel contient toute la chaîne | [Build](../../scripts/build-plugin.sh) | Faux pour l’archive : skills seuls | Résoudre les ressources et contrôles manquants |
| La portabilité des audits natifs est démontrée | [Test standalone](../../scripts/tests/check-standalone-install.sh) | Partiel : copie conservant l’arborescence du clone | Exercer l’installation native |
| Les campagnes tracent déjà tout l’outillage | [Campagne](../../.claude/skills/audit-rgaa-creator/scripts/audit_campaign.py) | Partiel : empreintes présentes, version exacte du harnais non établie | Conserver les preuves et établir la reprise |
| La séparation produit/projets est terminée | [Manifeste](../../config/agentic-design-packages.yaml) et [spec précédente](2026-09-10-durcissement-harnais-dsfr.md) | Incomplète | Inventorier la propriété avant transfert ou retrait |

| Option | Intérêt | Limite | Décision |
|---|---|---|---|
| Produit canonique autonome, distribué par plugin | Une maintenance, usage indépendant et intégration facultative aux workflows | Packaging, chemins et reprise à prouver | Cible retenue |
| Clone versionné avec entrée plugin | Réutilise la disposition actuelle et facilite l’identification Git | Installation supplémentaire à gérer ; autonomie du plugin non démontrée | Transition possible, sans remplacer la cible |

Ce cadrage étend la spec de septembre et les issues [#2](https://github.com/alexandra-guiderdoni/dsfr-agentic-kit/issues/2),
[#6](https://github.com/alexandra-guiderdoni/dsfr-agentic-kit/issues/6),
[#7](https://github.com/alexandra-guiderdoni/dsfr-agentic-kit/issues/7) et
[#8](https://github.com/alexandra-guiderdoni/dsfr-agentic-kit/issues/8).
Réutiliser leurs protections et contrats ; ne pas dupliquer les moteurs.
Le contrat de consommation versionnée doit rester compatible avec #6.

## Critères de réussite et preuves avant bascule

| ID | Résultat exigé | Preuve attendue |
|---|---|---|
| A1 | Installation indépendante | Environnement isolé, workflow source inaccessible, dépendances et téléchargements déclarés ; aucune résolution vers le poste personnel |
| A2 | Chaîne complète accessible | Installation native puis génération, contrôles navigateur représentatifs, campagne et rapport ; tracer les commandes, chemins et versions réellement utilisés |
| A3 | Installation intacte | Empreinte avant/après et tests de refus des sorties internes, y compris via lien symbolique ; toutes les données restent dans le projet consommateur |
| A4 | Campagne versionnée | Campagne en A, mise à jour B puis reprise selon le contrat, avec A identifiable et disponible ; qualifications conservées et références inchangées sans migration explicite |
| A5 | Dépendances honnêtes | AY11 absent puis environnement Python différent ; phases disponibles, sauts et erreurs explicités, sans faux succès ni conformité automatique |
| A6 | Source unique et profils cohérents | Inventaire de toutes les origines actives, parité des fonctions conservées et profils dérivés des mêmes sources ; après retrait autorisé, fonctionnement sans les anciennes copies |

Une preuve sur un hôte ne valide que cet hôte. Les autres adaptateurs restent
non vérifiés tant que leur parcours n’est pas exercé. Le scénario A4 réutilise
les empreintes existantes ; il ne promet pas l’identité de résultats sur un
site distant qui aurait changé.

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

Aucune migration, suppression, installation de plugin ou refonte AY11 n’est
réalisée ici. Les campagnes réelles et données privées ne sont pas des fixtures.
Les audits conservent leurs limites de couverture et la qualification humaine ;
aucun résultat automatique ne devient une conformité DSFR ou RGAA générale.
Les exigences ci-dessus sont des critères futurs, pas des tests déjà réussis.
