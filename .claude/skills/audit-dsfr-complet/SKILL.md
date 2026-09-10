---
name: audit-dsfr-complet
description: Auditer les composants et l’intégration DSFR d’un échantillon multi-pages, par règle et par instance, avec extraits HTML, références versionnées, qualification humaine et rapport actionnable.
allowed-tools: Read, Glob, Grep, Bash, Write, Edit, WebFetch
---

# Audit DSFR complet

Auditer l’intégration du Système de Design de l’État sans transformer une
absence de signal en conformité globale. Ce skill travaille par règle et par
instance de composant ; il ne remplace ni un audit RGAA ni une validation du
droit d’usage de la marque de l’État.

## Déclencheurs

- `/audit-dsfr-complet`
- `audite les composants DSFR de ces pages`
- `vérifie le respect du DSFR avec le code source`
- `compare l’intégration DSFR à la version courante`

## Orchestration recommandée

Pour un échantillon multi-pages, utiliser `audit-rgaa-creator` et activer
`phases.dsfr_checks`. La phase DSFR réutilise exactement `sample` et produit ses
livrables dans `dsfr/`. La phase `report` délègue ensuite à
`audit-report-dsfr` : `dsfr/AUDIT-PAR-PAGE.html`, les vues
`dsfr/pages-html/Pxx.html` et le portail commun sont générés par le builder
DSFR assemblé, jamais par concaténation de HTML non structuré.

```bash
bash <kit>/scripts/audit-rgaa-creator.sh run <audit>/campaign.yaml --only dsfr,report,validate
```

## Statuts automatisés

- `DETECTE_NON_AUDITE` : classe ou racine DSFR détectée, sans règle assez ciblée ;
- `AUCUN_ECART_REGLES_EXECUTEES` : toutes les règles déclarées ont produit un signal favorable, dans leur seul périmètre ;
- `ECART_OBSERVE` : au moins une règle a échoué sur une instance avec preuve ;
- `A_CONFIRMER` : état, variante ou source insuffisante ;
- `NON_APPLICABLE` : aucune cible pour une règle applicable conditionnellement ;
- `REFERENCE_INDISPONIBLE` : la source versionnée requise n’a pas été lue.

Ne jamais raccourcir ces statuts en `ALIGNÉ`, `ÉCART` ou `INDÉTERMINÉ` dans un
rapport transmis : ces termes masquent le périmètre réellement exercé.

## Qualification humaine

Les signaux `FAIL_CANDIDATE` deviennent des écarts confirmés seulement dans
`dsfr-findings.json` :

- `ECART_CONFIRME` ;
- `AUCUN_ECART_OBSERVE` ;
- `A_CONFIRMER` ;
- `NON_APPLICABLE` ;
- `REFERENCE_INDISPONIBLE`.

Un `ECART_CONFIRME` cite obligatoirement la règle, les pages, une preuve locale
et un commentaire. L’agent vérifie le code observé, la référence et la variante
avant de confirmer.

## Preuve minimale par instance

Chaque signal d’échec doit exposer :

- identifiant stable de règle ;
- page et URL ;
- composant et numéro d’instance ;
- sélecteur reproductible ;
- version DSFR observée et version cible ;
- HTML observé ;
- structure attendue ;
- conditions en échec ;
- source locale ou officielle lue ;
- recommandation et procédure de vérification ;
- chemin de preuve et captures desktop/mobile.

## Comparaison de versions

Toujours séparer :

1. **intégration** : structure d’un composant par rapport aux règles lues ;
2. **migration** : différence entre la version DSFR observée et la version cible.

Une page en DSFR 1.13.2 n’est pas automatiquement mal intégrée parce que la
référence courante est 1.15.2. Le rapport nomme la version observée, la cible et
l’absence éventuelle d’une source locale correspondant exactement à la version
installée.

## Catalogue de règles

Le catalogue machine est `rules/dsfr-rules.json`. Une règle contient une source,
une version cible, des conditions observables et un exemple de structure
attendue. L’inventaire inclut aussi les sous-composants réellement détectés,
notamment liens d’évitement, méga-menus, groupes de boutons, gestionnaire de
consentement, services de consentement, fieldsets, paramètre d’affichage et
bloc marque. Chaque état conditionnel présent doit être ouvert et conservé
dans une preuve reproductible. Ajouter une règle uniquement lorsqu’une référence ciblée est lue et
que l’échec peut être expliqué sans jugement esthétique implicite.

## Garde-fous

- Aucun claim `conforme DSFR`.
- Aucun pourcentage de conformité ou de couverture sans inventaire attendu officiel.
- Une classe `.fr-*` ne prouve pas qu’un composant est correctement assemblé.
- Un passage de règle ne valide pas les états non exercés.
- Les choix de composant, tokens sémantiques, espacements, marque et fidélité visuelle restent humains.
- Les écarts RGAA restent dans les statuts RGAA et ne sont jamais mélangés aux écarts DSFR.

## Définition de fin

- chaque page de l’échantillon possède une preuve versionnée ;
- chaque écart affiche le code observé et attendu ;
- chaque règle cite sa source et sa version cible ;
- les signaux non qualifiés sont visibles ;
- les causes racines regroupent leurs pages et instances ;
- le rapport commence par la liste des pages de l’échantillon ; chaque vue Pxx
  commence par la page auditée et son URL ;
- le rapport HTML est filtrable et relu visuellement ;
- `VALIDATION.json` ne contient aucune erreur.
