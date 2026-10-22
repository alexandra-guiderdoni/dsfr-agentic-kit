# Réception et bascule du harnais DSFR autonome

État au 22 octobre 2026. Ce reçu relie les critères aux sources exécutables ;
il ne remplace ni les qualifications humaines ni les preuves brutes des projets.

## Livraisons et critères

| Ticket | Source et preuve | État |
| --- | --- | --- |
| #3 — Catalogue sélectionné | `generate-virginie-dsfr-composants.py`, `virginie_dsfr/collect.py`, 28 tests de synthèse | Reçu sur le commit publié ci-dessous |
| #4 — Blocage d’infrastructure | `audit_campaign.py`, `navigation.py`, tests de pré-vol et navigation | Refus proxy en code 5, origine sondée une fois, qualification préservée ; DNS injecté et port local sans écoute |
| #5 — Qualification en deux passages | Générateur, reçus et deux consommateurs séparés | Codes 2 puis 0, sept pages HTML, fiche inchangée |
| #6 — Version immuable | `verify-kit-lock.py`, `CONSOMMATION-VERSIONNEE.md`, sept tests du verrou | Livré et vérifié |
| #7 — Recettes séparées | `SEPARATION-RECETTES.md`, consommateur privé avec `kit.lock` | Publié et reçu sur des archives synthétiques |
| #9 — Exploration | Essais isolés et critères A1 à A5 ; archive et marketplace distingués | Exploration réalisée ; limites ci-dessous |
| #10 — Source canonique | `product-authority.json`, `MAINTENANCE.md`, gardes des exports | Kit canonique ; anciens circuits refusés avant écriture |
| #11 — Profils et campagnes | `DISTRIBUTION-ET-PROFILS.md`, tests de distribution, installations natives | Livré sur `main` ; profils 18/17 issus des mêmes sources |
| #8 — Réception | Marketplace GitHub, deux profils et deux consommateurs séparés | Reçu le 22 octobre 2026 avec limites explicites |
| #12 — Bascule | Inventaire des consommateurs, branchements et retour arrière | Préparée après réception ; activation encore distincte |

Les états GitHub doivent être rapprochés de ces preuves avant clôture. Un ticket
ne devient pas terminé parce que sa dépendance a été livrée.

## Preuves de la livraison des profils

Le commit publié `007208fb5ed5aba6d309831f98faacf3c55fec02` a été installé
depuis la marketplace GitHub par Claude Code 2.1.306, dans un HOME isolé.
Le workflow personnel, ses caches et le voisin complet du profil léger sont
inaccessibles pendant les essais. Un vérificateur extérieur compare les
installations aux objets Git de ce commit avant leur exécution.
Les deux caches contiennent les mêmes 383 fichiers produit, préservés après
génération, navigateur, vérifications RGAA/DSFR et rapport. Le profil léger
expose 17 skills ; le complet 18. Les verrous des campagnes portent ce commit.

La recette canonique de cette livraison a terminé en code 0 : 13 tests de
distribution, 4 de sorties des traces, 7 du verrou, 13 du registre,
63 d’audit et 28 de synthèse ;
12 pages et 137 variantes générées ; 27 tokens et 155 classes retrouvés dans
le CSS officiel DSFR 1.15.4. Le hook `fr-display` non stylé n’est pas exercé
par ce contrôle CSS ; celui-ci ne prouve pas toutes les variantes possibles.

Les refus ont été éprouvés : cache divergent, sorties internes, redirection
symbolique d’une campagne vers le kit, reprise A par B, absence de verrou et
ancien contournement `--allow-inside-kit`. A conservé peut régénérer son
rapport en préservant le verrou et la qualification de la campagne A.

La livraison antérieure `c179315` et les essais de prototype restent des
preuves historiques distinctes ; leur réussite n’est pas déduite du correctif.

## Réception des consommateurs et de la revue

Les recettes publiées au commit `d7fe7982d55362be554794c441dad16d4d5d7bf4`
et le workflow préparé au commit `fffbe26b5ddc0bad0b2dd3e3aae16b28ff21b1b7`
verrouillent tous deux le kit `007208fb`. La préparation du cache consommateur
a récupéré ce commit depuis GitHub sans redirection vers une fixture Git locale.
Les deux entrées réelles ont produit `REVUE_CREEE` en code 2, sans rapport,
puis `RENDU` en code 0 : sept pages HTML et SHA-256 de la fiche inchangé.
Les trois tests de racines des recettes passent également.

La contre-revue ShipGuard du kit et des consommateurs ne relève plus de
défaut sur les constats connus et le delta corrigé. La revue initiale reste
réutilisée pour les parties inchangées ; ce n’est pas un nouvel audit intégral.
Les corrections couvrent notamment la concurrence du cache, les droits des
dossiers externes, les neuf références partagées des alias et les fichiers
de trace symboliques. Sept tests consommateur, onze tests d’alias et quatre
tests de sorties passent. Les rapports de logique ne confirment ni violation
ni risque sur les obligations examinées ; les rapports de comportement
distinguent raisonnement, mesures et nouveaux refus préventifs attendus.
Claude n’a pas fourni d’aval final après correction.

Les journaux et rapports, y compris les échecs intermédiaires, sont regroupés
dans le dossier local de livraison `dsfr-migration-rapports-20261022`, avec
index, empreintes et tableaux de revue. Aucune preuve brute de projet réel
n’est ajoutée au dépôt public.

## Portée de l’exploration et limites

| Critère | Observation | Portée |
| --- | --- | --- |
| A1/A2 | Installation native depuis GitHub puis génération/audits/rapport | CLI Claude Code 2.1.306 ; workflow personnel inaccessible |
| A3 | Empreinte préservée et refus des chemins internes ou redirigés | Cas négatifs de distribution exécutés |
| A4 | Versions A/B identifiées ; refus de B, rejeu de rapport avec A | Compatibilité interversions non promise |
| A5 | AY11 absent explicite ; pré-vol Python 3.12.14 réussi ; Python 3.14.7 sans Playwright refusé en code 2 | Campagnes natives en Python 3.14.7 ; aucun nouvel AY11 intégré |
| A6 | Kit canonique et profils communs ; consommateurs inventoriés avant bascule | Retrait des anciennes copies encore distinct |

L’archive `build-plugin.sh` contient seulement les skills : elle reste partielle.
La marketplace Git est la voie autonome retenue et exercée depuis GitHub.
L’ancien essai de marketplace locale reste identifié comme fixture. Le catalogue
publié suit `main`, sans pin implicite. Une campagne garde son commit et son
cache A ; les autres hôtes restent non vérifiés tant que leur entrée réelle
n’est pas exercée. Les essais CLI ne prouvent pas le choix autonome d’un LLM.

Les phases AY11 absentes sont ignorées, la qualification finale peut rester
partielle, et aucun taux de conformité n’est déduit d’un code 0. Le validateur
distant et la capture des rapports étaient désactivés dans la fixture native.
Python 3.10 et 3.11 ne sont pas exercés dans cette réception datée.
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
