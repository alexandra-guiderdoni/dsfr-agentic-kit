# Démarrer avec DSFR Agentic Kit

Ce fichier est le point d’entrée du kit autonome. Le kit fournit des
sources, des skills et des contrôles à lire ; le projet utilisateur reçoit les
briefs, pages, preuves, rapports et corrections.

## Règle de séparation

```text
workspace/
├── dsfr-agentic-kit/      # boîte à outils en lecture seule
├── mon-projet/            # seul emplacement des livrables
├── AGENTS.md              # instructions Codex éventuelles
└── CLAUDE.md              # instructions Claude Code ou Verdent éventuelles
```

Ne pas créer de page, de brief ou de rapport dans le pack. Une mise à jour du
pack doit pouvoir le remplacer sans toucher au projet.

## Ce qu’il faut dire à l’agent

Remplacer les chemins entre chevrons :

```text
Utilise comme boîte à outils en lecture seule le pack situé dans :
<chemin-du-pack>

Travaille uniquement dans mon projet situé dans :
<chemin-du-projet>

Objectif : <générer une page | auditer | corriger après audit>.
Entrée : <brief, HTML, URL, audit ou fichiers source>.
Sorties attendues : <page, page.json, preuve.md, rapports ou tickets>.

Ne modifie pas le pack. Lis ses sources de vérité et le SKILL.md correspondant
au besoin. Consigne les commandes exécutées, leurs résultats, les limites et
ce qui reste à vérifier. N’affirme pas une conformité DSFR ou RGAA sans preuve
dédiée.
```

Pour une production DSFR, demander d’abord la lecture de
`design-systems/dsfr/DESIGN.md`, `design-systems/dsfr/tokens.yaml` et
`.claude/skills/dsfr-components/SKILL.md`. Ces chemins existent dans le paquet
DSFR.

Pour un audit, choisir le skill selon le résultat attendu :

- site public multi-pages : `audit-rgaa-creator`, qui délègue aux skills RGAA,
  DSFR et rapport ;
- page publique isolée : `pre-audit-rgaa-dsfr` pour une préqualification et des
  fiches candidates ;
- page ou fichier hors secteur public, avec demande WCAG explicite :
  `audit-accessibilite-web` ;

- `audit-dsfr-complet` pour un audit DSFR par règle et par instance avec code observé et attendu ;
- `audit-report-dsfr` pour rendre un portail commun RGAA/DSFR via le builder assemblé ;
- `audit-rgaa-complet` pour une préqualification RGAA par test et instance avec revue des 258 tests ;
- `audit-rgaa-creator` pour créer et reprendre une campagne RGAA multi-pages avec AY11 et une vérification DSFR bornée sur le même échantillon ;
- `audit-rgaa-dsfr` pour un cadrage RGAA ponctuel lorsque le creator n'est pas nécessaire ;
- `fix-accessibilite` seulement après audit et autorisation de modifier le
  code du projet.

## Accueillir l’agent

Les fichiers suivants sont des exemples, pas des fichiers à installer de force :

- `templates/AGENTS.md.exemple` pour Codex ;
- `templates/CLAUDE.md.exemple` pour Claude Code ou Verdent.

S’il existe déjà un `AGENTS.md` ou un `CLAUDE.md`, fusionner le bloc utile avec
les instructions présentes. Ne jamais écraser le fichier existant. Remplacer
ensuite `<chemin-du-pack>` et `<chemin-du-projet>`.

Trois régimes sont distingués :

| Régime | Contrat |
| --- | --- |
| Lecture directe | Fonctionne avec tout agent capable de lire des fichiers locaux ; c’est la référence portable. |
| Découverte native | Dépend de l’hôte et de l’emplacement où il recherche ses skills ; elle reste facultative. |
| Hooks | Sont propres à l’hôte qui les exécute et ne sont pas une garantie portable du pack. |

Codex, Claude Code, Verdent ou un autre agent peuvent utiliser la lecture
directe des chemins nommés dans les instructions du workspace. Aucun alias ni
hook n’est requis par le contrat portable du kit.

## Vérifier le pack

Depuis la racine du pack :

```bash
bash scripts/check-prerequisites.sh
bash scripts/check-agentic-design-pack.sh
```

Les `[WARN]` et `[SKIP]` explicitement documentés ne sont pas des `[FAIL]`, mais
ils désignent des preuves qui n’ont pas été exercées.

Ces contrôles vérifient la boîte à outils. La vérification d’une page ou d’un
audit se consigne séparément dans le projet, par exemple dans `preuve.md`.

## Limites

- Un check vert du pack ne prouve pas qu’une page est conforme au DSFR ou au
  RGAA.
- L’usage de la marque de l’État et la décision de publication restent des
  décisions humaines distinctes.
- Le code du DSFR n’est pas redistribué dans cette archive ; ses conditions
  d’utilisation officielles continuent de s’appliquer.

Pour l’installation détaillée, lire
`documentation/INSTALLER-ET-TESTER.md`.
