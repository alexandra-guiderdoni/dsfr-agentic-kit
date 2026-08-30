---
title: "DSFR - sources et versions"
scope: sources officielles, versions, limites
load_when: "Une décision dépend de l'autorité officielle, de la version ou du périmètre."
---

# DSFR - sources et versions

Priorité :

1. documentation officielle DSFR version courante ;
2. package DSFR, code ou portage effectivement installé dans le projet ;
3. références locales du skill `dsfr-components` ;
4. fichiers du projet actif ;
5. ce profil local.

Si ce profil contredit la documentation officielle ou le code DSFR installé, suivre la source la plus proche du livrable réel et signaler l'écart.

## Version

- Documentation officielle consultée : branche DSFR `1.15`, vérifiée le 2026-08-28.
- Package npm/CDN stable consulté : `@gouvfr/dsfr` `1.15.2`.
- Des versions RC peuvent être visibles sur CDN ou dépôt : ne pas les utiliser comme référence de production sauf si le projet les utilise déjà.
- Écart paquet / documentation : aucun au 2026-08-28. La branche de
  documentation officielle est en `1.15` et le paquet de référence du pack est
  `1.15.2`, publié le 2026-08-12. La documentation officielle n'est pas lisible
  automatiquement depuis ce poste, son site étant protégé par un pare-feu
  applicatif : ce constat vient d'une vérification humaine, pas d'une mesure
  rejouable ici.

## Installation, licence et conditions d'utilisation

Depuis DSFR 1.15.0 (`#1471`, `#1476`, `#1463`, `#1372`) et 1.15.1 (`#1483`,
`#1486`), vérifié sur le paquet `@gouvfr/dsfr@1.15.2` le 2026-08-28 :

- le paquet est publié sous licence `etalab-2.0` (`package.json`, champ
  `license`) ; ses modalités d'utilisation (`doc/legal/cgu.md`,
  `cguVersion` 1.0.1 du 20 juillet 2026) doivent être acceptées ;
- `npm install @gouvfr/dsfr` exécute un hook `preinstall` qui échoue en code 1
  (`[NO_YML]`) sans fichier `.dsfr.yml` portant `accept-license` à la version
  courante, ou sans `DSFR_ACCEPT_LICENSE=1` (usage prévu pour l'intégration
  continue) ; `npm create @gouvfr/dsfr` met en place le consentement. Une
  configuration `ignore-scripts=true` masque ce blocage sans lever
  l'obligation. Mesuré le 2026-08-28 : npm 11 exécute le hook et échoue ;
  pnpm 10 n'exécute pas les scripts des dépendances sans `pnpm approve-builds`
  et procède à l'installation sans consentement ; yarn et bun non testés ;
- le code compilé n'est plus téléchargeable depuis les releases GitHub :
  passer par npm ou compiler les sources ;
- les pages générées par le pack chargent le DSFR depuis le CDN jsdelivr et ne
  sont pas concernées par le hook ; `npm pack`, utilisé pour le cache officiel
  des contrôles, ne l'exécute pas non plus.

## Références principales

- Accueil DSFR : <https://www.systeme-de-design.gouv.fr/version-courante/fr>
- Périmètre d'application : <https://www.systeme-de-design.gouv.fr/version-courante/fr/premiers-pas/perimetre-d-application>
- Note aux opérateurs : <https://www.systeme-de-design.gouv.fr/version-courante/fr/premiers-pas/note-aux-operateurs>
- Principes : <https://www.systeme-de-design.gouv.fr/version-courante/fr/fondamentaux/les-principes-a-respecter>
- Conception pour designers : <https://www.systeme-de-design.gouv.fr/version-courante/fr/premiers-pas/vous-etes-designer/conception>
- Premiers pas sur Figma : <https://www.systeme-de-design.gouv.fr/version-courante/fr/premiers-pas/vous-etes-designer/premiers-pas-sur-figma>
- Couleurs et tokens : <https://www.systeme-de-design.gouv.fr/version-courante/fr/fondamentaux/couleurs-utilisation-dans-le-dsfr>
- Typographie : <https://www.systeme-de-design.gouv.fr/version-courante/fr/fondamentaux/typographie>
- Espacement : <https://www.systeme-de-design.gouv.fr/version-courante/fr/fondamentaux/espacement>
- Grille : <https://www.systeme-de-design.gouv.fr/version-courante/fr/fondamentaux/grille-et-points-de-rupture>
- Médias : <https://www.systeme-de-design.gouv.fr/version-courante/fr/fondamentaux/medias>
- Icônes : <https://www.systeme-de-design.gouv.fr/version-courante/fr/fondamentaux/icone>
- Pictogrammes : <https://www.systeme-de-design.gouv.fr/version-courante/fr/fondamentaux/pictogramme>
- Ombres : <https://www.systeme-de-design.gouv.fr/version-courante/fr/fondamentaux/systeme-d-ombres-et-d-elevation>
- Classes d'affichage : <https://www.systeme-de-design.gouv.fr/version-courante/fr/fondamentaux/classes-css-d-affichage>
- Modes de contraste élevé : <https://www.systeme-de-design.gouv.fr/version-courante/fr/a-propos/articles-et-actualites/le-dsfr-et-les-modes-de-contraste-eleves>
- Présence de l'IA dans les contenus : <https://www.systeme-de-design.gouv.fr/version-courante/fr/a-propos/articles-et-actualites/presence-de-l-ia-dans-les-contenus>
- Composants : <https://www.systeme-de-design.gouv.fr/version-courante/fr/composants>
- En-tête : <https://www.systeme-de-design.gouv.fr/version-courante/fr/composants/en-tete>
- Pied de page : <https://www.systeme-de-design.gouv.fr/version-courante/fr/composants/pied-de-page>
- Liens d'évitement : <https://www.systeme-de-design.gouv.fr/version-courante/fr/composants/liens-d-evitement>
- Gestionnaire de consentement : <https://www.systeme-de-design.gouv.fr/version-courante/fr/composants/gestionnaire-de-consentement>
- Modèles : <https://www.systeme-de-design.gouv.fr/version-courante/fr/modeles>
- Pages types : <https://www.systeme-de-design.gouv.fr/version-courante/fr/modeles/pages-types>
- Formulaires : <https://www.systeme-de-design.gouv.fr/version-courante/fr/modeles/blocs-fonctionnels/formulaires>
- Mesure d'audience : <https://www.systeme-de-design.gouv.fr/version-courante/fr/mesure-d-audience>
- Note de version 1.15 : <https://www.systeme-de-design.gouv.fr/version-courante/fr/a-propos/notes-de-versions/note-de-version-115>
- Releases GitHub (notes de version ; le code compilé n'y est plus attaché depuis 1.15.1) : <https://github.com/GouvernementFR/dsfr/releases>
