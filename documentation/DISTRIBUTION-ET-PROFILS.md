# Installer un profil et démarrer une campagne versionnée

La voie autonome retenue est la marketplace Git. Son cache géré contient le
produit complet : scripts, références, profil DSFR et contrôles. Aucun clone
manuel supplémentaire à maintenir n’est nécessaire. L’archive historique de
`build-plugin.sh` contient des skills ; elle reste une distribution partielle
et ne constitue pas cette voie autonome.

## Choisir l’exposition

| Profil | Identifiant natif | Exposition |
| --- | --- | --- |
| Complet | `dsfr-agentic-kit@dsfr-agentic` | Les 18 skills du manifeste produit |
| Léger | `dsfr-agentic-kit-light@dsfr-agentic` | Les 17 mêmes outils, sans exposition d’`agentic-design-harness` |

Les deux profils consomment le même dépôt et peuvent être épinglés au même
commit. Leurs moteurs, ressources, protections et version DSFR sont identiques.
Le léger sélectionne l’exposition native ; il ne maintient aucun fork. Choisir
un profil par environnement pour éviter l’affichage des outils en double.

Le découpage vit dans `config/distribution-profiles.json`, avec les skills de
`config/agentic-design-packages.yaml`. `scripts/build-marketplace.py` dérive le
catalogue ; `--check` refuse une divergence. Les anciens alias ne sont pas modifiés.
Le catalogue publié suit `main`, sans champ `sha` : il ne constitue pas un pin.
Un hôte qui actualise ce plugin reçoit les nouveaux outils et leurs refus de
reprise. Cette livraison préserve les installations existantes ; conserver
les versions A nécessaires avant toute mise à jour par l’hôte.
L’exposition reprend les champs du [schéma officiel des marketplaces](https://code.claude.com/docs/en/plugins/marketplace-reference).

Dans Claude Code :

```text
/plugin marketplace add alexandra-guiderdoni/dsfr-agentic-kit
/plugin install dsfr-agentic-kit-light@dsfr-agentic
```

L’identité d’une campagne vient de son verrou, jamais du seul nom du cache ou
d’une branche `main`. Choisir un commit complet publié et préparer le projet.
`KIT_ROOT` désigne le cache natif réellement exécuté, trouvé dans les détails
de l’installation. Il doit être disjoint du projet.

## Vérifier le routage Codex depuis un consommateur

La racine du produit reste celle du script installé. Le contexte de Codex est
le répertoire courant du consommateur, ou le chemin explicite `--cwd`. Ce
répertoire doit exister hors du kit et satisfaire les contrôles natifs de
Codex, notamment le contrôle Git. La confiance reste inchangée et aucun dépôt
Git n’est créé dans le cache.

```bash
python3 -B "$KIT_ROOT/design-systems/scripts/check-dsfr-runtime-trace.py" run \
  --cwd "$PROJECT_ROOT" --output-dir "$PROJECT_ROOT/preuves/routage"
python3 -B "$KIT_ROOT/design-systems/scripts/check-dsfr-profile.py" \
  --runtime-trace "$PROJECT_ROOT/preuves/routage/pos-page-form-codex-exec-runtime.events.json"
```

Les deux sessions CLI sont fraîches, éphémères et en lecture seule : demande
DSFR explicite, puis demande proche sans DSFR. Elles ne génèrent aucun HTML.
Une lecture de référence en échec ne prouve pas son chargement. Les traces
nomment séparément le contexte consommateur et la racine produit ; leurs
sorties, y compris les fichiers redirigés par lien symbolique, restent hors
du kit. Les scénarios de test synthétiques ne remplacent pas ces sessions.

## Préparer le verrou puis initialiser

Git, Python 3.10+ et l’accès au dépôt de confiance sont nécessaires à la
préparation. Le nouvel outil récupère les objets du commit dans un dossier
temporaire, vérifie le cache natif et écrit le verrou dans le projet.
Les dépendances restent extérieures ; le remplacement d’un verrou différent
est interdit. `TRUSTED_TOOL_ROOT` désigne les outils obtenus depuis une source
de confiance distincte du cache encore inconnu. Ce dossier peut être temporaire ;
aucun deuxième clone permanent n’est nécessaire.

```bash
python3 "$TRUSTED_TOOL_ROOT/scripts/prepare-kit-lock.py" \
  --commit "$COMMIT_COMPLET" --kit-root "$KIT_ROOT" --project-root "$PROJECT_ROOT"
export DSFR_KIT_LOCK="$PROJECT_ROOT/kit.lock"
bash "$KIT_ROOT/scripts/check-prerequisites.sh"
bash "$KIT_ROOT/scripts/audit-rgaa-creator.sh" init "$URL" \
  --output "$PROJECT_ROOT/campagne"
bash "$KIT_ROOT/scripts/audit-rgaa-creator.sh" run "$PROJECT_ROOT/campagne/campaign.yaml"
```

L’outil de préparation et le vérificateur doivent eux-mêmes provenir d’une
installation de confiance. Ce mécanisme vérifie l’intégrité ; il ne signe pas
le code. Le dépôt distant doit être celui attendu. `--repository` permet un
dépôt de confiance différent, notamment une fixture locale de test. La garde
automatique du runner est ensuite une détection de divergence accidentelle,
pas une validation indépendante de code potentiellement hostile.

Le wrapper exige PyYAML ; la validation complète utilise jsonschema. Les phases
navigateur exigent Playwright Python et un navigateur disponible. Le cache du
paquet DSFR officiel reste externe. AY11 et les outils complémentaires gardent
leurs diagnostics explicites ; leur absence ne devient pas une conformité.
Définir les variables de projet dans son shell ou son environnement de projet,
sans ajouter `.env.local`, dépendances, caches Python ou sorties dans le kit.

`init` copie le verrou vérifié dans la campagne avant ses autres sorties. Un
checkout Git dont les fichiers versionnés sont intacts peut établir le verrou
depuis ses objets. Ses fichiers ignorés par Git, dont `.env.local` et les
livrables locaux, restent hors du produit vérifié. Les autres ajouts sont
refusés. Un cache sans Git exige `--kit-lock` ou `DSFR_KIT_LOCK` et refuse tout
fichier supplémentaire, même normalement ignoré. Toute commande vérifie
l’identité avant ses écritures. Une divergence refuse l’action et ne répare
rien. L’ancien contournement `--allow-inside-kit` n’est plus accepté ; les
sorties internes et les liens vers le kit sont refusés.
Avant une commande de campagne, les liens symboliques qui sortent de sa racine
sont également refusés : une redirection de `.creator` ou d’une autre sortie
ne doit pas permettre d’écrire dans l’installation après l’initialisation.

## Reprendre et conserver A

Conserver le cache A et le `kit.lock` de la campagne A lors de l’installation
de B. Invoquer explicitement le runner de A. B refuse de reprendre A ; il ne
remplace ni son verrou ni ses qualifications. Une campagne historique sans
verrou reste consultable avec `status`, mais aucune reprise ou régénération
n’adopte silencieusement le kit courant. Identifier ses sources d’origine et
les vérifier avant toute adoption explicite. L’adoption des anciennes campagnes
n’est pas outillée dans #11 et relève de #12 ; ne pas leur attribuer le verrou
du kit courant pour contourner le refus.

Avec un verrou présent, `status` vérifie aussi le kit et refuse une divergence.
Si A est indisponible, consulter directement `.creator/state.json` permet de
lire son état enregistré, sans exécuter un autre kit à sa place.

Une reprise peut recalculer les phases partielles et leur aval ; voir le
[contrat de consommation](CONSOMMATION-VERSIONNEE.md). Le commit, l’empreinte
et les phases effectivement exécutées doivent accompagner les preuves.

La réception des usages et des autres hôtes relève de #8. La bascule des
consommateurs et le retrait des anciennes copies relèvent de #12. Aucune
installation globale, nouvelle intégration AY11 ou action Studio n’est requise.
