# Maintenir le produit DSFR dans le kit

Le kit est la cible de maintenance du produit défini par les 18 skills de
`config/agentic-design-packages.yaml`, leur profil, leurs références, scripts
et tests. `config/product-authority.json` interdit les exports entrants du
workflow. Une évolution du produit commence ici ; elle n’exige pas de corriger
une copie dans un workflow personnel ou un miroir.

## Propriété et provenance

| Ensemble | Propriétaire | Provenance et protection |
| --- | --- | --- |
| 18 skills, profil DSFR, références et contrôles partagés | Kit | Importés dans l’historique du kit par les exports ; réutilisés sans réécriture |
| Packaging, installation, guides et contrôles de distribution | Kit | Ancien overlay du workflow ; maintenance désormais dans le kit |
| Synthèse par composant et protection des chemins projet | Kit | Modules `scripts/virginie_dsfr` réutilisables, nom historique conservé pour les appels existants |
| Recettes de tickets et formulaire, constats et paramètres métier | Consommateur privé de recettes | Extraction #7 ; jamais une seconde copie des moteurs génériques |
| Campagnes, qualifications, captures et archives brutes | Projet de travail | Hors produit, aucun déplacement ni ajout aux distributions |
| Alias et instructions des runtimes | Consommateurs facultatifs | Versions explicites ; transition et réception avant retrait (#8, #12) |
| Présentations DSFR et compétences spécialisées hors manifeste | Workflow actuel | Hors transfert : leur propriété finale reste à décider |

Les exports historiques sont documentés dans `CHANGELOG.md`. L’état reçu est
le parent de cette modification ; le diff conserve les moteurs et l’historique
Git du kit. Les traces observées et le rapport historique ne sont pas réécrits
pour leur donner l’apparence d’une nouvelle exécution.

Les anciennes copies du workflow et du miroir restent disponibles pendant la
transition. Elles ne sont plus des cibles d’évolution du produit. Les gardes
du workflow ont été activés et publiés avant le kit : ils refusent les exports
entrants et les applications du miroir avant toute écriture. La publication
coordonnée livre ensuite le kit, puis le verrou du consommateur de recettes.
Aucun alias actif n’est modifié. Ne pas relancer un ancien exporteur non protégé
sur le kit canonique.

## Faire évoluer le DSFR

1. Lire `.claude/skills/dsfr-changelog/SKILL.md` et comparer les versions depuis
   le dépôt officiel. Relever composants, styles, scripts, ressources et limites.
2. Mettre à jour dans ce dépôt les références, générateurs, règles, profil et
   tests réellement affectés. Les preuves des anciennes campagnes gardent leurs
   versions ; une mise à jour n’en fait pas de nouvelles campagnes.
3. Lancer `bash scripts/check-agentic-design-pack.sh` et examiner les sauts,
   puis exercer le parcours installé touché par la modification. Un check vert
   n’atteste pas les états, variables CSS ou sorties qu’il n’exerce pas.
4. Livrer une version immuable selon [le contrat de consommation](CONSOMMATION-VERSIONNEE.md).
   Les profils complet et léger livrés dans #11 partagent les mêmes sources ;
   conserver le commit éprouvé et les limites de chaque hôte.
5. Faire recevoir les consommateurs (#8) avant la bascule et le retrait (#12).

AY11 reste externe et facultatif. Le kit conserve son connecteur existant ;
aucun nouveau branchement n’est requis pour maintenir le produit.

État de réception et de transition : [suivi et preuves](RECEPTION-ET-BASCULE.md).
