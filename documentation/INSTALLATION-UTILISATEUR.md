# Installer le kit une fois pour ses agents

Cette installation facultative expose les mêmes compétences dans les dossiers
utilisateur Claude Code, Codex et `.agents`. Aucun plugin, hook global ou réglage
de confiance n’est ajouté. Le kit reste utilisable par checkout ou marketplace.

## Installation et mise à jour

Depuis un checkout de confiance du kit, choisir explicitement un commit complet :

```bash
python3 -B scripts/install-user.py install --commit <commit-complet>
```

Le programme vérifie les objets Git et prépare un cache en lecture seule avant
de changer les entrées utilisateur. Une entrée existante provoque un refus.
Après inspection des entrées concernées, `--adopt-existing` autorise leur
déplacement dans une sauvegarde ; aucun dossier de compétence étranger n’est
fusionné ou effacé. Le profil `--profile light` expose 17 compétences au lieu
des 18 du profil `complete`.

L’installation se trouve dans `~/.local/share/dsfr-agentic-kit/`. Son lien
`current` sélectionne une révision qui contient le verrou, le branchement du
produit et les copies générées des trois scripts de bootstrap. Ces copies
proviennent du commit vérifié ; elles ne sont pas des sources à modifier.
Les moteurs restent dans `~/.cache/dsfr-agentic-kit/commits/<commit>`.
Le vérificateur de confiance est conservé hors de ce cache.

Les compétences utilisateur sont des liens vers ce produit. La commande
`~/.local/bin/dsfr-kit` vérifie le cache avant chaque exécution déléguée :

```bash
dsfr-kit
dsfr-kit --exec scripts/audit-rgaa-creator.sh -- --help
dsfr-kit --exec scripts/demo-dsfr-assembled-page.sh -- --quiet
```

`~/.local/bin` doit être dans `PATH`, sinon employer son chemin complet.
Une nouvelle session de l’agent peut être nécessaire pour redécouvrir les
compétences ; un inventaire de liens ne prouve pas cette découverte.
Les dépendances Python, Playwright et DSFR officiel restent externes.

Pour mettre à jour, relancer la même installation avec le nouveau commit.
Les anciennes révisions et caches ne sont pas purgés. Ne jamais substituer
le verrou courant au verrou d’une ancienne campagne : son outillage A reste
exécutable avec `dsfr-kit --workspace <consommateur-épinglé-A> --exec ...`.
Ce consommateur doit posséder sa configuration et son verrou d’origine.
Les campagnes avec `kit.lock` suivent aussi le contrat de consommation versionnée.

## Compatibilité avec un workflow existant

`--bind-workspace <dossier>` pose uniquement le lien `.dsfr-kit` de ce dossier
vers l’installation utilisateur. Les liens relatifs existants peuvent ainsi
conserver leurs noms, leurs imports partagés et leur profil sans dupliquer les
moteurs. Les mises à jour conservent automatiquement ce branchement géré.
La propriété de ces liens est inscrite dans le reçu de transaction.
Le profil `light` filtre les compétences utilisateur : il ne transforme pas
les liens locaux d’un workflow complet existant. Ce workflow conserve ses
18 entrées et doit rester consommateur du profil `complete`.

`--home`, `--prefix` et `--cache-root` permettent une réception isolée. La
configuration et le cache sont disjoints ; aucun réglage des agents n’est écrit.

## Retour arrière

```bash
python3 -B ~/.local/share/dsfr-agentic-kit/current/scripts/install-user.py rollback
```

Le retour vérifie d’abord que les entrées gérées n’ont pas été changées depuis
l’installation, puis restaure les sauvegardes et le pointeur précédent.
Une modification utilisateur ultérieure entraîne un refus avant restauration.
Les caches et les campagnes sont conservés. Une interruption brutale pendant
les renommages exige l’inspection du reçu `installation.json` et des sauvegardes ;
la résistance à une coupure du processus n’est pas garantie par les tests locaux.

Les essais `test_user_installation.py` couvrent les conflits, le retour réel,
les profils, la conservation de A et le refus d’un cache altéré. Ils emploient
un dépôt Git synthétique : la réception des agents et du navigateur reste distincte.
