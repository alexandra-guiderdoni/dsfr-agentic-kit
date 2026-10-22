# Réception de l’installation utilisateur autonome

Réception du 22 octobre 2026. Le produit est maintenu dans le kit ; le workflow
personnel conserve des chemins de compatibilité, sans moteur produit copié.
Procédure : [installer, mettre à jour et revenir en arrière](INSTALLATION-UTILISATEUR.md).

## Version et provenance

Le candidat exécuté par Codex est `c4655dba00567aa1b802f73188c9bce740f0379e`.
La version installée depuis GitHub puis reçue par Claude est
`6386c60662edee0b18def0250c0a44e5ccdf15fe`. La comparaison des verrous de ces
deux versions ne relève qu’un changement documentaire précisant le profil léger.
Le code exécuté est identique. Les versions suivantes de ce reçu ne changent
pas implicitement l’installation épinglée.

Les preuves privées sont regroupées dans `dsfr-bascule-preuves-20261022` :
journaux complets, scripts de réception, inventaire initial, comparaisons
d’empreintes, traces natives et échecs intermédiaires. Elles restent hors du
dépôt public ; les tableaux ci-dessous bornent les affirmations du reçu.

## Scénarios exécutés

| Scénario | Preuve observable | Portée |
| --- | --- | --- |
| Validation canonique après commit du candidat | `kit-gate-committed.log` : 156 tests Python, 12 pages et 137 variantes ; 27 tokens et 155 classes retrouvés | DSFR officiel 1.15.4 ; lint externe facultatif non lancé, hook non stylé `fr-display` exclu |
| Installation distante | `installation-github.log` : commit complet récupéré en SSH, cache vérifié et 18 compétences | GitHub réel ; aucune redirection Git vers une fixture locale |
| Codex 0.163.0 indépendant | `native-codex/receipts/cli-run/summary.json` : 14 commandes réussies, page et portail HTML, captures bureau/mobile | HOME neuf, workflow personnel inaccessible ; navigateur, RGAA, DSFR et rapport `OK` |
| Découverte Codex | `skills-list.json` : 18 entrées actives issues de l’installation utilisateur | Pas de plugin DSFR ; dédoublonnage des surfaces utilisateur observé |
| Claude Code 2.1.308 personnel | `native-claude-received/receipts/verified-summary.json` : compétence découverte, six résultats d’outils sans erreur, page HTML générée | Gardes personnels conservés, workflow lisible pour ses hooks ; écritures kit, workflow et Git refusées |
| Réglages et installation | Empreintes des 391 fichiers du cache inchangées après les sessions ; réglages natifs inchangés pendant chaque essai | Aucune approbation native contournée ; authentification temporaire Codex retirée |
| Compatibilité du workflow | `final-integrity.json` : 72 liens résolus, 813 éléments protégés inchangés | Quatre compétences hors produit, profil mixte et archives préservés ; configurations Codex et ZCode inchangées |
| Outils partagés | Imports éditoriaux DOCX/PDF exercés ; neuf tests Sites Conformes, onze scénarios d’alias réussis | Liens génériques, acronymes inconnus et correction des capitales vérifiés |
| Ancienne campagne | `legacy-replay/summary.json` : rapport recalculé avec son outillage A, cinq fichiers protégés et cache inchangés | Campagne synthétique copiée, antérieure à `kit.lock` ; aucun nouveau verrou ajouté |
| Retour arrière réel | `rollback-reel.json` : 56 entrées restaurées, réglages identiques, ancien branchement et plugin rétablis | Retour effectivement joué avant réinstallation cible ; caches conservés |
| Recettes privées | `recipes-gate.log` : 35 tests réussis avec leur propre verrou reçu | Version `007208fb` conservée ; aucune requalification implicite par la mise à jour utilisateur |

Les commandes utilisateur reçues comprennent l’appel direct `dsfr-kit`, l’aide
de `audit-rgaa-creator.sh` et la génération assemblée depuis un autre dossier.
Le workflow délègue à cette installation. Son ancien chargeur, ses configurations
courantes et les implémentations de tests produit ont été remplacés ou archivés ;
ses chemins relatifs encore consommés restent reliés à `.dsfr-kit`.

Deux anciens sélecteurs de plugin Claude, dont la source synchronisée, ont été
désactivés localement. Leurs caches sont conservés. Une session neuve a confirmé
l’absence des compétences DSFR sous un espace de noms de plugin. Les autres
plugins, hooks et permissions ne font pas partie du remplacement.

## Revue et limites

La contre-revue indépendante du code et des preuves ne relève aucun P0/P1.
Son P2 documentaire sur `light` est corrigé : le profil filtre les entrées
utilisateur et ne transforme pas un workflow local déjà complet.

Les essais Claude isolés ayant échoué restent conservés : les hooks personnels
étaient inaccessibles, puis la politique de réception bloquait des fichiers
temporaires natifs. Le reçu final autorise seulement les temporaires nécessaires
et garde les protections du produit. Il démontre le parcours personnel Claude,
pas une nouvelle réception Claude sans workflow. Le scénario indépendant de
cette installation est démontré par Codex. Les commandes de réception sont
prescrites ; aucun choix autonome général d’un modèle n’est déduit de leur succès.

Le contrôle final a aussi détecté un ancien lien local `.dsfr-kit` : la cible
attendue du reçu a été restaurée, puis tous les liens ont été revérifiés.
Une entrée modifiée après installation entraîne normalement un refus de retour
arrière ; elle ne doit jamais être écrasée sans inspection.

Les données sont synthétiques. AY11 est absent, le validateur distant et les
captures des rapports sont désactivés dans la campagne native Codex : pré-vol
et validation restent `PARTIEL`. Une campagne métier réelle, une coupure brutale
pendant les renommages et les autres machines ne sont pas reçues ici.
Ces limites ne sont ni des qualifications humaines ni des taux de conformité.
