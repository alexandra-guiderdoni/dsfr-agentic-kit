# Exemples de pages assemblées

Ces exemples montrent le parcours attendu du builder :

1. `brief.md` fixe le besoin produit et les limites.
2. `page.json` décrit la page consommable par `generate_assembled_page.py`.
3. `page.html` est la sortie DSFR générée depuis ce JSON.
4. `preuve.md` liste les vérifications locales et leurs limites.

La preuve reste bornée : ces pages sont des prototypes DSFR à vérifier avant
publication, pas des preuves de conformité DSFR ou RGAA.

## Assets locaux

Les exemples versionnés peuvent rester sur le CDN DSFR par défaut. Pour une
démo locale ou un partage sans CDN DSFR, ajouter `"assets_prefix": "assets/dsfr"`
dans `page.json` et servir le dossier `assets/dsfr` à côté du HTML généré. Cela
ne change pas la limite de preuve : la page reste un prototype à vérifier avant
publication.

## Contenu éditorial

Pour un contenu produit ou transformé par agent, utiliser `body_structured`
pour les contenus riches et `body_text` pour un texte simple. Le champ `body`
accepte du HTML brut seulement si le bloc déclare `allow_raw_html: true` ; il
est réservé à du HTML relu par un opérateur expert.

Les blocs qui contiennent des contrôles internes reçoivent des préfixes d'IDs
uniques quand ils sont répétés. Pour les formulaires, `form_id` et les `id` de
champs peuvent être fournis si une ancre stable est nécessaire ; sinon les IDs
des champs simples sont générés depuis le formulaire et le libellé, puis
dédupliqués.

Pour les schémas SVG, ne pas renseigner `ratio` sur le block `image` : le
builder le refuse afin d'éviter un rendu rogné. Utiliser `ratio` seulement pour
des images matricielles dont le cadrage est maîtrisé.

## Scénarios

- `demarche-rendez-vous` : démarche administrative avec formulaire, validation
  différée et aide.
- `information-service` : page d'information structurée avec alerte, onglets,
  téléchargement et partage.
- `prise-en-main-agent` : démo produit guidée pour un agent externe, avec
  commande exécutable hors dépôt.
- `suivi-dossier` : page de suivi avec cartes, colonnes, accordéon, transcription
  et abonnement.
- `vibe-coding-harnais-agentique` : page pédagogique avec assets DSFR locaux,
  SVG non rogné et comparaison vibe coding / agent / harnais.

## Démo exécutable

Depuis la racine du dépôt source, du miroir autonome ou du paquet généré :

```bash
bash scripts/demo-dsfr-assembled-page.sh
```

La commande lit `prise-en-main-agent/brief.md`, valide `page.json`, génère une
page HTML dans un dossier temporaire, inspecte les ancres et affiche les chemins
du brief, du JSON, de la sortie HTML et de la preuve.

## Régénération

Depuis la racine du workspace, `SKILL_DIR` désignant le dossier du skill :

```bash
SKILL_DIR=.claude/skills/dsfr-components  # adapter à l'emplacement d'installation
python3 "$SKILL_DIR/scripts/generate_assembled_page.py" \
  --config-file "$SKILL_DIR/examples/assembled/demarche-rendez-vous/page.json" \
  --check
```

Le contrôle global `python3 "$SKILL_DIR/scripts/check_generated_outputs.py"`
valide aussi les `page.json` contre le schéma et vérifie que chaque `page.html`
versionné correspond à son `page.json`.

Pour vérifier seulement le contrat du builder assemblé :

```bash
python3 "$SKILL_DIR/scripts/check_assembled_page_schema.py"
```
