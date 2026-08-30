---
name: dsfr-changelog
description: Comparer deux versions DSFR depuis le dépôt réel. Utiliser pour migration ou écart note/dépôt ; exclure audit RGAA et intégration courante d’un composant.
allowed-tools: Bash, Read, Grep, Glob
context: conversation
---

# Analyse de version DSFR

## Promesse et périmètre

Rendre prévisible une analyse de version DSFR fondée sur le dépôt réel : établir
ce qui change, ce qui est annoncé et l'effet sur les projets comme sur leurs
conditions de production.

## Prérequis

`git` et `python3` sont les seules dépendances obligatoires. Avec PyYAML, le
collecteur lit `changelog.yml`; sans lui, il restitue le même contenu analytique
depuis `CHANGELOG.md`, avec une provenance différente.

Vérifier `command -v git && command -v python3` avant de poursuivre.
Résoudre ensuite `SKILL_DIR` comme le chemin absolu du dossier contenant ce
`SKILL.md`, sans supposer le répertoire courant, puis vérifier l'entrée :

```bash
SKILL_DIR="<dossier absolu contenant ce SKILL.md>"
test -f "$SKILL_DIR/scripts/dsfr-collect.py"
```

## Étape 0 — Préparer le dépôt

```bash
git clone --no-checkout \
  https://github.com/GouvernementFR/dsfr.git <chemin>
```

Si le clone existe déjà, vérifier d'abord `git -C <chemin> rev-parse --git-dir`.
Dans tous les cas, exécuter ensuite :

```bash
git -C <chemin> fetch --tags origin
git -C <chemin> rev-parse <version-a>^{commit} <version-b>^{commit}
git -C <chemin> merge-base --is-ancestor <version-a> <version-b>
```

Tout code non nul arrête l'analyse. Si le fetch répond `would clobber existing
tag`, le tag distant a été déplacé : ne pas forcer sa mise à jour et repartir
d'un nouveau clone pour préserver l'ancien constat.

Critère d'arrêt : les deux bornes se résolvent et la première est ancêtre de la
seconde.

## Étape 1 — Collecter

Pour chaque version sans note locale, récupérer son corps puis vérifier qu'il
n'est pas vide :

```bash
python3 "$SKILL_DIR/scripts/dsfr-collect.py" --fetch-note <version> > <note-publiée>
test -s <note-publiée>
```

Un code non nul ou un fichier vide rend l'écart communication/dépôt `non vérifié`.
L'analyse locale reste sans réseau : elle reçoit ensuite les notes par fichier
et interdit l'hydratation implicite des clones partiels.

```bash
python3 "$SKILL_DIR/scripts/dsfr-collect.py" \
  --repo <chemin> --from <version-a> --to <version-b> \
  [--note <note-publiée>]
```

Pour plusieurs versions, répéter `--note <version>=<fichier>` pour chacune.

La sortie JSON porte les bornes, versions, items, sources et SHA des catalogues,
diff par zone, delta de distribution et changements silencieux. Chaque item
porte aussi ses `commits`, son `rattachement`, son nombre de `fichiers` et ses
`zones` réelles ; `cardinalite_commits` recense les items sans commit, à
plusieurs commits, ou rattachés par simple mention. Le diff porte `renommages`
et `fichiers_hors_renommage`. Chaque version
intermédiaire vient du premier tag figé qui la décrit ; un repli sur une branche
reste identifiable par son SHA.

Critère d'arrêt : `bornes.status` vaut `BOUNDARY_OK` et la liste
`versions_couvertes` est cohérente. Si `items_total` vaut zéro mais que le diff
porte des fichiers, passer en mode `diff seul` : sauter les étapes dépendant du
changelog et marquer leurs résultats `non vérifiés`. Ne jamais découper la
collecte. Si l'analyse est répartie en lots, l'union de leurs identifiants doit
égaler `changelog.items` sans omission ni doublon.

## Étape 2 — Examiner d'abord les changements silencieux

Lire `changements_silencieux` en premier, puis tous les items annoncés. Prioriser
les `feat`, les portées vides et `cites_mais_absents_du_depot`. L'absence d'une
annonce augmente l'attention ; elle ne diminue pas la preuve. Un écart nul entre
identifiants ne prouve pas que les conséquences sont communiquées.

Trier ensuite sur la portée mesurée, pas sur le type déclaré : un item `docs`,
`chore` ou `ci` dont les `zones` touchent `composants`, `core` ou `layout` pèse
plus qu'un `feat` limité à un fichier. Le type est une intention d'auteur, les
zones sont un fait. Traiter de même tout item dont `fichiers` est disproportionné
au regard de son titre.

Lire `cardinalite_commits` : un item `sans_commit` est annoncé sans trace dans
l'intervalle, un item `multi_commits` a été livré en plusieurs fois, un item en
`rattachement_faible` repose sur une mention de sujet et non sur une fusion de
pull request. Ne jamais présenter l'un de ces trois cas comme un rattachement
établi. Si `cardinalite_commits.mesure` vaut `false`, la portée réelle des items
est `non vérifiée` pour tout l'intervalle.

Comparer enfin, pour chaque item cité des deux côtés, le libellé de la note
publiée et celui du dépôt. Un identifiant présent partout peut recouvrir deux
descriptions inconciliables, ou présenter comme nouvelle une capacité déjà
présente à la borne de départ : le vérifier sur l'artefact avant de conclure.

Critère d'arrêt : chaque item du changelog est retenu pour examen ou écarté avec
un motif d'une ligne.

## Étape 3 — Regrouper en clusters

Regrouper deux items ou plus si au moins deux conditions convergent : même PR,
même objectif, mêmes fichiers structurants, même règle ou même mécanisme. Un
item sans relation démontrée reste seul.

Critère d'arrêt : tout item retenu appartient à exactement un cluster et aucun
cluster ne mélange deux mécanismes distincts.

## Étape 4 — Vérifier le comportement avant et après

Ne jamais conclure depuis le titre d'une pull request ou le nom d'un fichier.

Comparer les artefacts réels aux deux bornes :

```bash
git -C <chemin> diff <A> <B> -- <fichier>
git -C <chemin> show <A>:<fichier>
git -C <chemin> show <B>:<fichier>
```

Ouvrir par les zones non vides de `diff.par_zone`, classées par nombre de
fichiers, et n'inspecter une famille que si sa zone est peuplée. L'ordre
ci-dessous est une liste de points d'entrée, pas une séquence à dérouler
intégralement : une zone vide se conclut en une ligne.

1. zone `legal` : `doc/legal/cgu.md`, champ `cguVersion`, puis le mécanisme qui
   le consomme.
2. zone `distribution` : `package.json`, champ `license`, hooks d'installation,
   liste `files`, puis `scripts/`, `LICENSE.md`, `publiccode.yml`.
3. zones `composants`, `core`, `layout` :
   `src/dsfr/component/<composant>/template/ejs/*.ejs` et les gabarits de
   `layout/` pour les ruptures de markup ; les fichiers sous `example/` et
   `doc/` ne sont pas canoniques.
4. `diff.renommages` non nul : établir la réorganisation avant de lire les
   contenus, avec `git -C <chemin> diff --name-status -M <A> <B>`. Un chemin
   déplacé casse les imports d'un projet sans rien changer au rendu, et un
   volume de fichiers déplacés se lit à tort comme une réécriture massive.
5. Les artefacts de release via l'API seulement si la distribution est en jeu.

Quand un gabarit porte un bloc de commentaire décrivant ses paramètres, le
comparer à son propre code : la valeur par défaut documentée et celle
effectivement retenue peuvent diverger. Retenir le code comme comportement et
conserver l'écart.

Critère d'arrêt : chaque cluster dispose d'un avant et d'un après cités depuis le
dépôt, ou d'une mention `non vérifié` motivée. Une preuve directe suffit ; sinon,
chercher trois sources convergentes et conserver toute contradiction.

## Étape 5 — Qualifier la matérialité

Attribuer un seul verdict par cluster. Ne jamais produire de note chiffrée.

`minor` : effet local ou correctif sans changement de contrat. `material` :
comportement, capacité ou règle d'usage modifié. `structural` : effet sur les
conditions de production ou les fondamentaux ; toujours l'analyser en détail.

Qualifier chaque conclusion : vérifiée directement, étayée par plusieurs
sources, interprétation raisonnable ou hypothèse.

Critère d'arrêt : chaque cluster porte exactement un niveau de matérialité et un
niveau de preuve.

## Étape 6 — Restituer

Restituer dans cet ordre : bornes et statut ; verdict de migration en une phrase ;
clusters `structural` ; clusters `material` ; changements silencieux et
communication ; ruptures de markup ; clusters `minor` en liste courte ; points
non établis ; limites. Une rubrique vide est un résultat, une rubrique absente
est une omission.

Critère d'arrêt : les neuf rubriques sont présentes et chaque fait important
cité remonte à une commande, un fichier ou une source explicite.

## Exemple minimal

```text
Entrée : migration DSFR <A> → <B>, avec une note qualifiée par version.
Sortie : BOUNDARY_OK ; chaque item dans un cluster ; neuf rubriques ; tout fait
sans preuve marqué « non vérifié ».
```

## Récupération d'erreur

- dépôt invalide ou ref refusée, sortie 2 : corriger l'entrée sans contourner la validation ;
- `BOUNDARY_PARTIAL` : refaire le fetch ; `BOUNDARY_DIVERGED` : corriger ou déclarer les historiques non comparables ;
- fetch refusé car un tag serait écrasé : arrêter, ne pas forcer ;
- source de changelog indisponible : mode `diff seul` ;
- mesure des changements silencieux fausse : fournir les notes qualifiées ou déclarer l'écart non mesuré ;
- `erreur_git` sur objet manquant : clone partiel. Hydrater explicitement l'intervalle, hors du collecteur qui interdit toute hydratation implicite, avec `git -C <chemin> log --no-merges --numstat <A>..<B> > /dev/null` puis `git -C <chemin> diff --numstat <A> <B> > /dev/null` ; à défaut, repartir d'un clone complet ;
- `cardinalite_commits.mesure` à `false` : l'historique de l'intervalle est illisible alors que ses bornes le sont ; hydrater comme ci-dessus, sinon déclarer la portée réelle des items `non vérifiée` sans invalider le reste de la collecte ;
- diff vide : vérifier si les bornes désignent le même commit ;
- clone absent et réseau inaccessible : arrêter, car les notes seules ne suffisent pas.

## Conventions et garde-fous

- Ne jamais déduire une intention depuis le code ; utiliser une PR, une documentation ou une communication explicite.
- Ne jamais inventer une PR, un fichier, un numéro ou une adoption.
- Distinguer norme déclarée, encodée et vérifiée par un mécanisme contraignant.
- Distinguer absence d'effet et absence d'information ; sinon écrire `inconnu`.
- Ne pas confondre disponibilité et adoption, ni standardisation et restriction.

## Limites connues

- Les anciennes versions peuvent exiger un catalogue de branche mutable ; citer son SHA de source.
- `isBreaking` est déclaratif : inspecter les gabarits dès qu'un composant change.
- L'API de comparaison GitHub peut tronquer les fichiers ; le clone fait foi.
- Les artefacts attachés aux releases exigent un appel d'API distinct.
- Le dépôt, sa note, ses licences et ses métadonnées peuvent se contredire ; conserver l'écart.

## Checklist finale

Avant de rendre le rapport, vérifier que :

- [ ] bornes `BOUNDARY_OK`, versions, items et clusters sont exhaustifs ;
- [ ] avant, après, `cguVersion`, gabarits, matérialité et preuves sont renseignés ;
- [ ] l'écart est mesuré ou motivé, sans note chiffrée ;
- [ ] le verdict tient en une phrase et les neuf rubriques sont présentes.

## Vérification

```bash
"$SKILL_DIR/scripts/test-collect.sh" <chemin-du-clone> [note-publiée-1.15.0]
```

Le harnais couvre références, PyYAML optionnel, intervalles, prépublication, catalogues malformés, bornes, notes, tag déplacé, structure, rattachement des items à leurs commits, normalisation des renommages, zonage et dégradation du rattachement sur clone partiel. Sans note, un contrôle est sauté ; sur un clone dont l'historique n'est pas hydraté, le contrôle de rattachement l'est aussi.
