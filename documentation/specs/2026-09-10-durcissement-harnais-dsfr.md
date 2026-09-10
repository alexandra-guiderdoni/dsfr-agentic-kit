# Spec — Durcissement du harnais DSFR et séparation des recettes Douane

**Statut** : Prêt pour découpage en tickets
**Date** : 2026-09-10
**Dépôt cible** : `alexandra-guiderdoni/dsfr-agentic-kit`
**Source** : rapport Cowork et décisions validées en entretien Ask Matt

## Énoncé du problème

Le kit DSFR est fonctionnel à `f200af9`, mais plusieurs comportements peuvent
affaiblir la reproductibilité ou polluer le dépôt consommé : certains pipelines
peuvent écrire dans le kit, le générateur n’est pas couvert par la validation
canonique, `--rules` ne pilote pas entièrement la fraîcheur, et un refus réseau
peut être confondu avec un échec d’audit.

Le kit contient aussi des recettes propres au portail Douane, alors que son
contrat doit rester portable et indépendant de Loriq.

## Solution

Renforcer le contrat d’exécution du kit afin que toute campagne travaille dans
un projet séparé, que les blocages d’infrastructure soient explicitement
classés, et que les contrôles du générateur soient inclus dans la validation
canonique.

Les recettes, URLs, campagnes et scripts propres à Douane seront déplacés dans
un dépôt privé séparé nommé `dsfr-agentic-douane`. Ce dépôt consommera le kit
via un cache vérifié et un fichier `kit.lock` contenant au minimum un commit
immuable et l’empreinte attendue du kit.

## Récits utilisateurs

1. En tant qu’utilisateur du kit, je veux lancer un pipeline depuis un projet
   de travail sans modifier le clone du kit, afin de préserver son intégrité.
2. En tant que mainteneur, je veux que la validation canonique couvre le
   générateur, afin qu’un contrôle vert représente réellement le produit livré.
3. En tant qu’auditeur, je veux distinguer un refus du proxy d’un résultat du
   site, afin de ne produire aucun constat trompeur.
4. En tant que responsable d’une campagne, je veux rejouer exactement la même
   campagne avec la même version du kit, afin de garantir la traçabilité.

## Décisions d’implémentation

- Le kit reste générique et portable.
- Les recettes Douane sortent du kit et rejoignent `dsfr-agentic-douane`.
- Loriq, `.loriq/`, `CLAUDE.md` et les hooks Loriq sont hors périmètre du kit.
- Chaque campagne consomme un commit précis du kit.
- `kit.lock` est la source de vérité du projet consommateur.
- Le kit est récupéré dans un cache de travail ; il n’est pas copié dans le
  dépôt Douane et n’est pas intégré comme sous-module.
- Les rapports dérivés et manifestes sont versionnables ; les archives HTML,
  captures et preuves brutes restent dans un stockage sécurisé séparé.
- Le statut machine est `BLOQUE_INFRA` ; le libellé humain est `BLOQUÉ-INFRA`.
- Un HTTP 403 sans preuve proxy ne doit pas être classé automatiquement comme
  un blocage d’infrastructure.

## Décisions de test

- Seam : le contrôle canonique exécute aussi les tests du générateur et retourne
  un résultat reproductible.
- Seam : un pipeline lancé avec un projet séparé laisse le kit inchangé, y
  compris ses fichiers ignorés.
- Seam : un `--output` qui résout dans le kit est refusé sans écriture.
- Seam : un catalogue fourni par `--rules` est celui dont l’empreinte sert au
  calcul de fraîcheur.
- Seam : un refus proxy produit `BLOQUE_INFRA`, aucun constat et aucun verdict
  RGAA ou DSFR.
- Seam : une première qualification crée la revue sans rendre ; une seconde
  qualification rend avec la revue inchangée.
- Seam : les références Douane ne sont plus nécessaires au fonctionnement du
  kit générique.

## Hors périmètre

- Audit frais du portail Douane.
- Création effective du dépôt GitHub privé `dsfr-agentic-douane`.
- Stockage ou transfert des preuves brutes.
- Installation d’un plugin Claude ou ajout d’une intégration Loriq.
- Passage en HTTPS par défaut, gestion de `rsync` et vérification Python 3.10/3.11 ;
  ces sujets restent des améliorations ultérieures.

## Questions ouvertes

- Le fournisseur et la politique de rétention du stockage sécurisé des preuves
  brutes restent à définir dans `dsfr-agentic-douane`.
- L’emplacement exact du cache et le format complet de l’empreinte de
  `kit.lock` seront précisés dans le ticket d’intégration du consommateur.
- La liste finale des artefacts Douane à migrer doit être confirmée lors de la
  création du dépôt consommateur.

## Notes complémentaires

Le kit est actuellement sain à `f200af9` et aucun changement de comportement ne
doit être introduit sans tests. Le dépôt Douane sera privé ; le dépôt du kit
reste public et ne doit pas recevoir de données d’audit brutes.
