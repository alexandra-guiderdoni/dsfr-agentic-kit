# Réception et bascule du harnais DSFR autonome

État au 22 octobre 2026. Ce reçu relie les critères aux sources exécutables ;
il ne remplace ni les qualifications humaines ni les preuves brutes des projets.

La bascule ultérieure vers l’installation utilisateur, sans plugin obligatoire,
est décrite dans le [reçu du branchement utilisateur](RECEPTION-INSTALLATION-UTILISATEUR.md).
Les sections ci-dessous conservent leurs versions et leurs observations historiques.

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
| #12 — Bascule | Inventaire des consommateurs, branchements et retour arrière | Activée après réception et publiée ; archives préservées |

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
et le workflow reçu au commit `fffbe26b5ddc0bad0b2dd3e3aae16b28ff21b1b7`
verrouillent tous deux le kit `007208fb`. La préparation du cache consommateur
a récupéré ce commit depuis GitHub sans redirection vers une fixture Git locale.
Les deux entrées réelles ont produit `REVUE_CREEE` en code 2, sans rapport,
puis `RENDU` en code 0 : sept pages HTML et SHA-256 de la fiche inchangé.
Les trois tests de racines des recettes passent également.

La réception #8 a été publiée dans le kit au commit `71f5a345` avant
l’activation du workflow. Sa bascule est publiée sur `main` au commit
`24d18ccdb60fa94789e2b6bdf838ad219b3601d9`, identique au distant.
Ce dernier ajoute au code consommateur reçu un correctif du contrôle de
changelog et sa documentation : une longue liste de fichiers archivés ne provoque plus
un faux rejet par SIGPIPE. Douze tests passent, dont l’acceptation avec
changelog et le refus sans mise à jour ; une contre-revue ciblée puis le
vrai push ont confirmé le résultat sans contournement du hook.

Les 749 fichiers historiques sont archivés à l’identique et 13 fichiers
locaux de bytecode conservés. Les 68 liens actifs, dont 36 entrées de
compétences, résolvent le cache vérifié `007208fb`. La synchronisation ciblée
des 17 alias Codex en actualise deux et conserve les quinze autres, sans
suppression. Les campagnes, qualifications et deux journaux étrangers sont
hors du lot ; les 2 872 fichiers ignorés du kit sont inchangés.

Les profils natifs complet et léger déjà installés ont été rejoués après
activation, sur le workflow `fffbe26b` : navigateur, RGAA, DSFR et rapport
restent `OK`, avec les 383 empreintes et permissions inchangées dans chacun
des deux caches. Le workflow personnel est inaccessible pendant ces essais,
ainsi que le voisin complet pour le profil léger. Prévol et validation
restent `PARTIEL` pour les capacités facultatives déclarées absentes.

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
| A6 | Kit canonique et profils communs ; consommateurs reçus puis basculés, anciennes sources archivées | Branchement réversible ; aucune suppression irréversible |

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

Lors de la première réception, Codex 0.163.0 refusait le cache comme
répertoire de confiance, en code 1 avant toute trace. Le contrôle global
retournait 0 malgré une URL de push ShipGuard non neutralisée. Ces deux
écarts historiques ont été traités dans le complément ci-dessous.

## Complément reçu : routage Codex et diagnostic ShipGuard

Le kit `3628c241123c65429104eed8c9b66b10a45e8991` a été publié avant
le verrou consommateur du workflow `cfd35aeb40625583c43436728ab5745bc35e34d8`.
La préparation réelle a récupéré cette version depuis GitHub en SSH. Les
68 liens actifs résolvent son cache vérifié de 384 fichiers ; le cache
historique `007208fb` de 383 fichiers et les campagnes restent conservés.

Deux nouveaux essais CLI Codex 0.163.0 ont été exécutés depuis le workflow,
avec le script réellement installé et des sorties externes au kit :

- demande DSFR : 12 commandes réussies, dont les lectures du skill,
  du profil et des références de formulaire ; branche page complète `form` ;
- demande proche sans DSFR : aucune commande outil ni lecture DSFR ;
- vérification des deux traces et du profil : codes 0, sans erreur runtime ;
- contexte dans le cache ou redirigé, sortie interne, répertoire de sortie
  redirigé et fichier de trace symbolique : cinq refus en code 2 avant appel ;
- empreintes et permissions des fichiers et répertoires du cache inchangées,
  configuration Codex inchangée, aucune génération HTML par ces scénarios.

La racine produit reste immuable ; seul le contexte transmis à Codex devient
celui du consommateur. Aucun réglage de confiance ni dépôt Git dans le cache
n’a été ajouté. Le vérificateur du profil utilise les formulations réellement
déclarées par les références ; le profil lui-même n’est pas assoupli.
La recette complète du kit termine en code 0 avec 135 tests Python, les
contrôles CSS officiels et les sorties générées. Le hook CSS non stylé
`fr-display` reste exclu, et le lint externe facultatif n’a pas été lancé.

La maintenance canonique du workflow réapplique le seul `origin.pushurl`
ShipGuard autorisé. Deux réapplications réelles conservent les mêmes octets
de configuration Git, l’URL de récupération, les autres remotes et le code
tiers. Le diagnostic direct et le diagnostic global terminent en code 0,
sans `FAIL`. Les échecs requis sont désormais propagés ; l’absence facultative
reste acceptée. Les suites du workflow comptent 42 tests et 13 scénarios verts.

La contre-revue ShipGuard des candidats `614c4d17` et `18100aad` a relevé
trois défauts moyens : génération en échec masquée, métadonnées Git partagées
et destinations effectives de push mal vérifiées. Les corrections `3628c241`
et `739177f3` ont chacune leur régression et une vérification indépendante
ciblée réussie. Les rapports initiaux restent intacts, avec reçus de correction
séparés ; aucun nouvel audit intégral ni aval Claude n’est revendiqué.

Cette réception prouve le routage CLI dans le contexte personnel. Elle ne
prouve ni une installation autonome du plugin Codex, ni la conformité HTML,
ni les autres hôtes. Les cinq issues Astra des recettes, AY11 et Studio sont
hors de ce complément. Le dossier privé `dsfr-reception-native-preuves-20261022`
contient les traces fraîches, les échecs avant correction et les rapports.

## Complément reçu : installation indépendante Codex

Le commit publié `d23d77dfc4fb1ce3375cc87a542942f3f054adee` a été installé
depuis GitHub par Codex 0.163.0 dans deux HOME neufs, un par profil.
Le workflow personnel est inaccessible ; le voisin complet est également
inaccessible au léger. L’entrée native `skills/list` expose respectivement
18 et 17 compétences activées, sans ajout de racine de compétences.

L’essai a révélé puis corrigé deux incompatibilités : le transport Git du
catalogue Claude était ignoré par Codex, et le manifeste généré par l’hôte
était refusé comme fichier supplémentaire. Le catalogue Codex est maintenant
dérivé des mêmes profils. Le manifeste de l’hôte doit correspondre exactement
au catalogue verrouillé, types JSON compris ; aucun autre ajout n’est accepté.
Le catalogue Claude et les compétences existantes sont inchangés.

Les deux installations ont généré une page, exécuté le navigateur, les
contrôles RGAA et DSFR, puis produit leur portail de rapports. Ces quatre
phases sont `OK`. Les 385 fichiers produit, leurs modes exécutables et le
manifeste de l’hôte sont préservés ; les verrous portent le commit publié.
Les accès au workflow, au voisin complet et en écriture dans le cache ont
également leurs tests de refus explicites.

Une session fraîche du modèle `gpt-6.1-sol`, via le serveur natif Codex,
a ensuite chargé le skill installé et appelé son générateur dans un troisième
projet vide. La page ainsi produite a été auditée jusqu’au rapport, avec les
mêmes quatre phases `OK` et une nouvelle vérification du verrou après exécution.
La configuration et l’authentification personnelles gardent leurs empreintes.

Le contrôle complet du kit termine en code 0 : 140 tests Python, contrôles
produit, générations et fidélité CSS officielle, dont 27 tokens et 155 classes.
Le hook non stylé `fr-display` et le lint externe facultatif restent exclus.
La contre-revue indépendante a relevé deux P2 : lien symbolique du catalogue
dans un export sans Git et confusion entre `false` et `0` dans le manifeste.
Les deux corrections disposent de tests de régression réussis.

Cette réception utilise le mode officiel `externalSandbox` du serveur Codex
sous une politique macOS effective. Le premier essai `codex exec` en sandbox
imbriquée a échoué avec `sandbox_apply: Operation not permitted` ; il ne
constitue pas une réussite CLI. Les dépendances Python, Playwright et le paquet
officiel DSFR sont réutilisés depuis un dossier externe déclaré, sans nouvelle
installation. AY11 est absent, le validateur distant et la capture des rapports
sont désactivés : prévol et validation restent `PARTIEL`. Aucune conformité
globale ni installation de l’application graphique n’est revendiquée.

Les traces, échecs intermédiaires, inventaires et rapports restent dans le
dossier privé de réception `dsfr-codex-autonome-20261022`. Les essais sur
catalogue local sont distingués des réinstallations GitHub réussies.
Les consommateurs existants et leurs campagnes ne sont pas migrés par cet essai.

## Complément reçu : parcours CLI Codex

Le commit publié `1360b15c964fe1b0180dfcc66fc60153a7496627` a été installé
depuis GitHub dans deux nouveaux HOME, un par profil. Deux véritables sessions
`codex exec` ont généré une page, exécuté Chromium et les contrôles RGAA/DSFR,
puis produit leur portail : quatre phases `OK`, codes CLI 0, respectivement
11 et 14 commandes. Une recherche d’inventaire du léger retourne 1 avant
la lecture correcte des ressources ; aucune phase requise n’échoue.

Ces sessions utilisent un confinement macOS externe unique, fourni par la
politique installée `templates/codex-macos-isolation.sb`. La seconde couche
interne est désactivée uniquement sous cette politique ; l’incompatibilité
de l’imbrication n’est pas présentée comme corrigée dans Codex ou macOS.
Le [lancement documenté](DISTRIBUTION-ET-PROFILS.md#codex-exec-et-navigateur-sur-macos)
conserve le workflow inaccessible et les écritures bornées.

Le wrapper respecte maintenant `DSFR_AUDIT_PYTHON` dès son premier import,
sans adaptation de `PATH` dans les essais finaux. Les tests refusent aussi
un interpréteur invalide sans repli et les déplacements des cinq parents du
cache, y compris `.codex`, vers le projet. La contre-revue a reproduit puis
confirmé la correction de ce dernier défaut sur des fixtures indépendantes.

Les 386 fichiers produit et le manifeste de chaque cache gardent leurs
empreintes et modes ; les verrous externes sont revérifiés après exécution.
La lecture du profil voisin est refusée dans les deux sens. Configuration et
authentification personnelles restent identiques ; leurs copies temporaires
sont retirées. Le contrôle global sur ce commit termine en code 0 avec
143 tests Python, 12 pages, 137 variantes, 27 tokens et 155 classes CSS.
`fr-display` et le lint externe facultatif restent hors de cette vérification.

Les preuves et échecs intermédiaires sont conservés dans le dossier privé
`dsfr-codex-exec-20261022`. Dépendances extérieures réutilisées, données
synthétiques, AY11 absent, validateur distant et capture des rapports désactivés :
prévol et validation restent `PARTIEL`. Cette réception concerne macOS et
Codex 0.163.0 ; elle ne migre pas les consommateurs existants.

## Ordre de réception et retour arrière

Recevoir le produit et les recettes (#8) avant de modifier les branchements
actifs (#12) : cet ordre a été respecté. Conserver l’identité et le cache des campagnes antérieures,
les qualifications humaines, les archives et les fonctions non DSFR du
workflow. Une ancienne campagne sans verrou n’est pas adoptée en lui donnant
simplement le verrou courant.

Chaque consommateur reçu doit nommer le commit, l’entrée réellement résolue,
le parcours exercé et le retour à sa version précédente. Le retrait des
copies et circuits obsolètes exige une liste concrète ; aucun effacement
irréversible ni suppression de dépôt ou branche n’est déduit de ce reçu.

Le workflow garde les caches A/B et peut revenir à un couple configuration /
verrou antérieur par `scripts/use-dsfr-kit.py`, sans purge automatique.
Son organisation historique reste accessible au commit `04807782`, avec
les archives conservées ; préparer le retour en préservant les changements
postérieurs et les données. Voir son
[guide consommateur publié](https://github.com/Alexmacapple/claude-workflow-perso/blob/24d18ccdb60fa94789e2b6bdf838ad219b3601d9/documentation/guides/consommer-dsfr-agentic-kit.md).
