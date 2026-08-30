# Templates de fiches RECO et NOTE-INTERNE

Reference pour la phase 4 (generation en lot) du skill /pre-audit-rgaa-dsfr.

## Template RECO

```markdown
# RECO-{PAGE}-{NUM} — {Titre court du defaut}

**Page** : {identifiant} - {nom}
**URL** : {url}
**Type** : Recommandation (hors perimetre strict RGAA)
**Date** : {YYYY-MM-DD}

---

## Constat

{Description factuelle du probleme observe}

## Code source concerne

{Bloc HTML si pertinent}

## Recommandation

{Correction proposee avec justification}

## Contexte

Cette recommandation ne correspond pas a une non-conformite RGAA 4.1.2
mais ameliore la qualite globale du site (ergonomie, robustesse, SEO,
bonnes pratiques HTML).
```

## Template NOTE-INTERNE

```markdown
# NOTE-INTERNE-{PAGE} — {Titre court du point a verifier}

**Page** : {identifiant} - {nom}
**URL** : {url}
**Type** : Note interne (verification manuelle necessaire)
**Date** : {YYYY-MM-DD}

---

## Observation

{Description de ce qui a ete observe et pourquoi c'est suspect}

## Verification necessaire

{Ce que l'auditeur humain doit verifier et avec quels outils}

## Hypothese

{Ce que le skill pense du comportement : conforme DSFR, defaut d'integration, ou indetermine}

## Criteres RGAA potentiellement concernes

{Liste des criteres qui pourraient etre en echec si l'hypothese se confirme}
```

## Template NC systemique (allege)

Pour les defauts deja documentes sur une autre page :

```markdown
# NC-{PAGE}-{NUM} — {Titre court} (systemique)

**Page** : {identifiant} - {nom}
**URL** : {url}
**Critere RGAA** : {numero} — {intitule}
**Severite** : {identique au ticket de reference}
**Date** : {YYYY-MM-DD}

---

## Defaut systemique

Meme cause racine que **{reference au ticket original}**.

**Pages affectees** : {liste des pages ou le defaut a ete constate}

**Correction unique** : {indication du template CMS ou du composant a corriger une seule fois}

Voir le ticket de reference pour l'analyse detaillee et les recommandations.
```

## Nommage des fichiers

| Type | Format | Exemple |
|------|--------|---------|
| NC | `NC-{PAGE}-{NUM}-{slug}.md` | `NC-P01-001-formulaire-recherche-etiquette.md` |
| RECO | `RECO-{PAGE}-{NUM}-{slug}.md` | `RECO-P01-001-urls-partage-malformees.md` |
| NOTE | `NOTE-INTERNE-{PAGE}-{slug}.md` | `NOTE-INTERNE-P01-modales-header-focus-aria.md` |
