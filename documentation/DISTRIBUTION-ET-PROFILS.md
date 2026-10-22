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

Dans Codex CLI, le catalogue `.agents/plugins/marketplace.json` adapte le
transport Git et les politiques d’installation depuis les mêmes profils :

```bash
codex plugin marketplace add git@github.com:alexandra-guiderdoni/dsfr-agentic-kit.git
codex plugin add dsfr-agentic-kit-light@dsfr-agentic
codex plugin list --json
```

Remplacer l’identifiant léger par `dsfr-agentic-kit` pour le profil complet.
Le format suit la [documentation officielle des plugins Codex](https://developers.openai.com/plugins/build/plugins).
Le manifeste `.codex-plugin/plugin.json` créé par l’hôte est accepté uniquement
si son contenu correspond exactement à un profil du catalogue verrouillé,
sans clé supplémentaire ni permission d’exécution. Le catalogue est vérifié
par son empreinte avant de servir à cette comparaison. Tout autre ajout reste
refusé ; aucune exclusion globale de `.codex-plugin` n’est introduite.

L’identité d’une campagne vient de son verrou, jamais du seul nom du cache ou
d’une branche `main`. Choisir un commit complet publié et préparer le projet.
`KIT_ROOT` désigne le cache natif réellement exécuté, trouvé dans les détails
de l’installation. Il doit être disjoint du projet.

## Vérifier le routage Codex depuis un consommateur

Pour la génération et l’audit navigateur par `codex exec` sur macOS, voir
[le confinement CLI autonome](#codex-exec-et-navigateur-sur-macos).

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

## Codex exec et navigateur sur macOS

Les sandboxes macOS ne s’imbriquent pas dans la réception exercée. De plus,
le sandbox natif de Codex refuse l’enregistrement du service Mach de Chromium.
Le parcours de réception CLI utilise donc un seul confinement macOS externe,
fourni par `templates/codex-macos-isolation.sb`. Il laisse fonctionner les
services système du navigateur et impose les restrictions de fichiers aux
processus CLI et à leurs descendants.

Préparer un HOME isolé authentifié, un projet Git neuf, un kit installé vérifié
par son verrou et des dépendances extérieures. Utiliser des chemins absolus
résolus, des racines disjointes et un dossier temporaire dédié. Le projet,
le HOME isolé et les reçus restent hors du kit et du workflow interdit.
`PERSONAL_HOME` désigne le HOME réel avant le lancement isolé ;
`CODEX_RUNTIME_ROOT` désigne le dossier du binaire réel de Codex et de ses
ressources, sans inclure sa configuration personnelle. `OTHER_PROFILE_ROOT`
désigne l’installation voisine à rendre inaccessible, ou un chemin inexistant.

```bash
env HOME="$ISOLATED_HOME" CODEX_HOME="$ISOLATED_HOME/.codex" TMPDIR="$TMP_ROOT" \
  /usr/bin/sandbox-exec \
  -D "WORKFLOW_ROOT=$WORKFLOW_ROOT" -D "PERSONAL_HOME=$PERSONAL_HOME" \
  -D "CODEX_RUNTIME_ROOT=$CODEX_RUNTIME_ROOT" -D "PROJECT_ROOT=$PROJECT_ROOT" \
  -D "TMP_ROOT=$TMP_ROOT" -D "ISOLATED_HOME=$ISOLATED_HOME" \
  -D "RECEIPTS_ROOT=$RECEIPTS_ROOT" -D "KIT_ROOT=$KIT_ROOT" \
  -D "OTHER_PROFILE_ROOT=$OTHER_PROFILE_ROOT" \
  -f "$KIT_ROOT/templates/codex-macos-isolation.sb" \
  "$CODEX_BINARY" --no-daemon exec --sandbox danger-full-access \
  --ephemeral --json -C "$PROJECT_ROOT" -
```

L’option `danger-full-access` désactive ici seulement la seconde couche
interne : elle doit rester dans cette commande sous `sandbox-exec`, avec la
politique complète. L’exécuter seule supprimerait le confinement attendu.
La politique d’approbation native reste distincte ; aucun réglage global ni
option `--dangerously-bypass-*` n’est nécessaire. Des paramètres manquants
font échouer la compilation de la politique avant le lancement.

Avant une génération, éprouver dans ce même lancement le refus de lecture du
workflow et de son alias, des écritures dans le kit et son alias, dans `.git`
et hors des dossiers autorisés, ainsi qu’une écriture réussie dans le projet.
Un code CLI 0 sans fichiers produits ni phases navigateur réussies ne suffit pas.
Le rapport conserve les limites des capacités absentes et des contrôles désactivés.

Choisir l’interpréteur Python via `DSFR_AUDIT_PYTHON` : le wrapper de campagne
l’utilise dès son premier import, puis la campagne le réutilise pour ses enfants.
Une valeur explicite invalide échoue sans repli silencieux vers un autre Python.
Le choix automatique antérieur reste disponible lorsque la variable est absente.
Ce parcours est spécifique à macOS et à la CLI reçue ; les autres plateformes
ne sont pas couvertes par cette preuve. Sources :
[permissions Codex](https://learn.chatgpt.com/docs/permissions) et
[CLI non interactive](https://learn.chatgpt.com/docs/non-interactive-mode).
