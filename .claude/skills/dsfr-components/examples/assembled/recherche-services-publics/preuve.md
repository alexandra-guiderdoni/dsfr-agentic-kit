# Preuve — Résultats de recherche de services publics

## Statut

Prototype DSFR à vérifier avant publication. Ce dossier ne revendique ni
conformité DSFR ou RGAA, ni exactitude administrative, ni droit d'usage de la
marque de l'État.

Vérification DSFR bornée : **AUCUN ÉCART OBSERVÉ DANS LE PÉRIMÈTRE LU** pour
les structures page, formulaire, sélecteur, tags, cartes et liens contrôlées
avec les références locales DSFR 1.15.2. Ce statut n'est pas une conformité
globale.

## Commandes de génération et de contrôle

Depuis la racine du dépôt :

```bash
SKILL_DIR=.claude/skills/dsfr-components
python3 "$SKILL_DIR/scripts/generate_assembled_page.py" \
  --config-file "$SKILL_DIR/examples/assembled/recherche-services-publics/page.json" \
  --check
python3 "$SKILL_DIR/scripts/generate_assembled_page.py" \
  --config-file "$SKILL_DIR/examples/assembled/recherche-services-publics/page.json" \
  --output "$SKILL_DIR/examples/assembled/recherche-services-publics/page.html"
python3 "$SKILL_DIR/scripts/check_generated_outputs.py"
python3 "$SKILL_DIR/scripts/check_golden_outputs.py"
```

## Couverture visée

- configuration JSON validée par le schéma du builder ;
- page complète en français avec liens d'évitement, en-tête, `main` et pied de
  page ;
- un seul `h1`, titres ordonnés, labels associés et identifiants uniques ;
- trois filtres en listes déroulantes et quatre tags-liens ;
- aucun `href="#"`, aucune cible ARIA absente et aucun gestionnaire inline ;
- aucun CSS ou JavaScript personnalisé ;
- rendu desktop et mobile, console et parcours clavier de surface à consigner
  après génération.

## Résultats observés

- `generate_assembled_page.py --check` : **PASS**, configuration valide,
  5 sections et 15 823 caractères générés ;
- génération : **PASS**, `page.html` écrit depuis `page.json` ;
- `check_assembled_page_schema.py` : **PASS**, 6 exemples, 3 fixtures et
  1 exemple invalide de contrôle ;
- `check_golden_outputs.py` : **PASS**, 21 cas inchangés et invariants valides ;
- `check_generated_outputs.py` : **FAIL global préexistant**, 12 pages et
  136 composants inspectés puis 4 échecs hors de ce nouvel exemple : une
  attente de chemin relatif `examples/assembled` et trois cas négatifs d'icônes
  faute de `DSFR_OFFICIAL_PACKAGE_DIR` ou `DSFR_OFFICIAL_CACHE_DIR` ; le
  contrôle global complet reste donc non vérifié ;
- inspection HTML : `html lang="fr"`, en-tête, `main`, pied de page, un seul
  `h1`, trois `select`, quatre tags-liens, six cartes, aucun `href="#"` et
  aucun CSS ou JavaScript personnalisé ;
- navigateur desktop : URL `http://127.0.0.1:4173/page.html`, viewport
  1440 × 1200, capture pleine page `capture-desktop.png` (1440 × 2354) ;
- navigateur mobile : même URL, viewport 320 × 900, capture pleine page
  `capture-mobile.png` (320 × 4118), grille empilée sans texte tronqué ni
  chevauchement observé ;
- arbre d'accessibilité : liens d'évitement, recherche nommée, trois combobox
  nommées avec leurs aides, boutons de formulaire, tags-liens et titres de
  cartes exposés ; hiérarchie observée `h1` puis `h2` puis `h3` ;
- interactions : sélection de `Logement` dans la combobox confirmée, menu
  mobile ouvert puis refermé, tag `Aides au logement` menant à
  `?q=logement&type=aide` sans JavaScript ;
- clavier : focus du tag visible (`outline` bleu continu de 2 px), puis `Tab`
  déplace le focus vers `Démarches en ligne` ;
- console : aucune erreur navigateur ; initialisation DSFR 1.15.2 observée.

## Limites

- le moteur de recherche et les routes sont fictifs ;
- la soumission des formulaires n'est pas testable de bout en bout sur le
  serveur statique, qui n'implémente pas la route `/recherche` ;
- la pertinence éditoriale et administrative des résultats n'est pas validée ;
- l'absence d'écart automatisé ne vaut pas conformité RGAA ;
- les tests avec lecteur d'écran et l'audit humain exhaustif restent hors de
  cette preuve locale.
- les quatre échecs du contrôle global du harnais restent à traiter séparément
  de cette page ; ils ne sont pas masqués par les contrôles ciblés réussis.
