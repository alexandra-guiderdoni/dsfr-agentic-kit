# Réception et bascule du harnais DSFR autonome

État au 22 octobre 2026. Ce reçu relie les critères aux sources exécutables ;
il ne remplace ni les qualifications humaines ni les preuves brutes des projets.

## Livraisons et critères

| Ticket | Source et preuve | État |
| --- | --- | --- |
| #3 — Catalogue sélectionné | `generate-virginie-dsfr-composants.py`, `virginie_dsfr/collect.py`, tests de synthèse | Correctif ciblé vérifié ; recette complète à consigner |
| #4 — Blocage d’infrastructure | `audit_campaign.py`, `navigation.py`, tests de pré-vol et navigation | Refus proxy en code 5, origine sondée une fois, qualification préservée ; DNS injecté et port local sans écoute |
| #5 — Qualification en deux passages | Générateur de synthèse, reçu et tests du premier passage | Correctif ciblé vérifié ; recette complète à consigner |
| #6 — Version immuable | `verify-kit-lock.py`, `CONSOMMATION-VERSIONNEE.md`, sept tests du verrou | Livré et vérifié |
| #7 — Recettes séparées | `SEPARATION-RECETTES.md`, consommateur privé avec `kit.lock` | Extrait et publié ; réception du consommateur en cours |
| #9 — Exploration | Essais isolés et critères A1 à A5 ; archive et marketplace distingués | Exploration réalisée ; limites ci-dessous |
| #10 — Source canonique | `product-authority.json`, `MAINTENANCE.md`, gardes des exports | Kit canonique ; anciens circuits refusés avant écriture |
| #11 — Profils et campagnes | `DISTRIBUTION-ET-PROFILS.md`, tests de distribution, installations natives | Livré sur `main` ; profils 18/17 issus des mêmes sources |
| #8 — Réception | Parcours installé et consommateur séparé après corrections | En cours |
| #12 — Bascule | Inventaire des consommateurs, branchements et retour arrière | Après réception ; aucun retrait irréversible exécuté |

Les états GitHub doivent être rapprochés de ces preuves avant clôture. Un ticket
ne devient pas terminé parce que sa dépendance a été livrée.

## Preuves de la livraison des profils

Le commit `c179315535b51e4cd47a234fea5f7766c2065c27` a été exercé dans deux
installations natives Claude Code 2.1.306 isolées du workflow personnel.
Les deux caches contiennent les mêmes 381 fichiers produit, préservés après
génération, navigateur, vérifications RGAA/DSFR et rapport. Le profil léger
expose 17 skills ; le complet 18. Les verrous des campagnes portent ce commit.

La recette canonique de cette livraison a terminé en code 0 : 12 tests de
distribution, 7 du verrou, 13 du registre, 60 d’audit et 25 de synthèse ;
12 pages et 137 variantes générées ; 27 tokens et 155 classes retrouvés dans
le CSS officiel DSFR 1.15.4. Le hook `fr-display` non stylé n’est pas exercé
par ce contrôle CSS ; celui-ci ne prouve pas toutes les variantes possibles.

Les refus ont été éprouvés : cache divergent, sorties internes, redirection
symbolique d’une campagne vers le kit, reprise A par B, absence de verrou et
ancien contournement `--allow-inside-kit`. A conservé peut régénérer son
rapport en préservant le verrou et la qualification de la campagne A.

## Portée de l’exploration et limites

| Critère | Observation | Portée |
| --- | --- | --- |
| A1/A2 | Installation Git native puis chaîne génération/audits/rapport | CLI Claude Code ; workflow personnel inaccessible |
| A3 | Empreinte préservée et refus des chemins internes ou redirigés | Cas négatifs de distribution exécutés |
| A4 | Versions A/B identifiées ; refus de B, rejeu de rapport avec A | Compatibilité interversions non promise |
| A5 | AY11 absent explicite ; pré-vol Python 3.12 réussi ; Python sans Playwright refusé | Aucun nouvel AY11 intégré |
| A6 | Kit canonique et profils communs ; consommateurs inventoriés avant bascule | Retrait des anciennes copies encore distinct |

L’archive `build-plugin.sh` contient seulement les skills : elle reste partielle.
La marketplace Git est la voie autonome retenue ; la recette locale épinglée
ne prouve pas l’installation depuis GitHub après publication. Le catalogue
publié suit `main`, sans pin implicite. Une campagne garde son commit et son
cache A ; les autres hôtes restent non vérifiés tant que leur entrée réelle
n’est pas exercée. Les essais CLI ne prouvent pas le choix autonome d’un LLM.

Les phases AY11 absentes sont ignorées, la qualification finale peut rester
partielle, et aucun taux de conformité n’est déduit d’un code 0. Le validateur
distant et la capture des rapports étaient désactivés dans la fixture native.
Le dépôt n’atteste pas de CI distante ; les commandes locales constituent les
preuves décrites ici. Les données réelles et les preuves privées restent hors
du dépôt public.

## Ordre de réception et retour arrière

Recevoir le produit et les recettes (#8) avant de modifier les branchements
actifs (#12). Conserver l’identité et le cache des campagnes antérieures,
les qualifications humaines, les archives et les fonctions non DSFR du
workflow. Une ancienne campagne sans verrou n’est pas adoptée en lui donnant
simplement le verrou courant.

Chaque consommateur reçu doit nommer le commit, l’entrée réellement résolue,
le parcours exercé et le retour à sa version précédente. Le retrait des
copies et circuits obsolètes exige une liste concrète ; aucun effacement
irréversible ni suppression de dépôt ou branche n’est déduit de ce reçu.
