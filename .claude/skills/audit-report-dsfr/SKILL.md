---
name: audit-report-dsfr
description: Générer un portail et des rapports d’audit RGAA/DSFR avec le builder DSFR du harnais, depuis des résultats structurés, sans HTML arbitraire ni confusion entre référentiels.
allowed-tools: Read, Glob, Grep, Bash, Write, Edit
---

# Rapports d’audit construits avec le builder DSFR

Ce skill rend les résultats ; il ne collecte pas les preuves et ne modifie pas
les qualifications. `audit-rgaa-complet` et `audit-dsfr-complet` restent les
sources sémantiques. `audit-rgaa-creator` orchestre la génération.

## Contrat

Le rendu passe obligatoirement par :

```text
dsfr-components/scripts/generate_assembled_page.py
```

et son bloc structuré `audit_report`. Les extraits observés sont des chaînes
échappées. Aucun constat ne peut fournir de HTML brut, de script ou de classe
DSFR arbitraire.

## Sorties

- `PORTAIL-AUDITS.html` : entrée commune ;
- `rgaa/AUDIT-PAR-PAGE.html` : rapport RGAA complet ;
- `dsfr/AUDIT-PAR-PAGE.html` : rapport DSFR complet ;
- `rgaa/pages-html/Pxx.html` : détail RGAA par page ;
- `dsfr/pages-html/Pxx.html` : détail DSFR par page ;
- `rapport-dsfr/config/*.json` : configurations validées du builder ;
- `rapport-dsfr/BUILD.json` : provenance et empreintes des entrées canoniques,
  configurations, sorties, builder et schéma.

## Règles de présentation

- `brand_mode: neutral` : un rapport d’audit n’obtient pas implicitement le droit
  d’utiliser le bloc-marque République française ;
- portail commun, mais statuts et causes RGAA/DSFR séparés ;
- chaque rapport commence par les pages de l’échantillon ; chaque vue détaillée
  commence par l’identification et l’URL de la page auditée ;
- grille, conteneurs, gouttières et marges reposent sur les classes DSFR du builder ;
- un sommaire DSFR relie échantillon, périmètre, indicateurs, causes et constats ;
- les indicateurs utilisent des mises en avant DSFR, les actions des groupes de
  boutons DSFR et chaque rapport propose un retour en haut de page ;
- aucun taux RGAA officiel et aucun claim `conforme DSFR` ;
- intégration et migration DSFR restent distinguées ;
- la rédaction utilise uniquement le tiret simple `-`, jamais de tiret cadratin ;
- chaque titre de constat commence par le problème, avant l’identifiant technique ;
- les séparateurs horizontaux délimitent uniquement les groupes de critères RGAA, jamais les instances ou les catégories DSFR ;
- une page détaillée conserve sélecteur, code observé/attendu, source,
  recommandation, contre-test et preuves ;
- sans JavaScript, tous les constats restent consultables ; les filtres sont une
  amélioration progressive ;
- les liens de preuve sont relatifs et portables dans l’archive ;
- le thème DSFR 1.15.2 est chargé depuis le CDN par défaut ; sans réseau, le
  contenu sémantique reste lisible mais la présentation DSFR n’est pas garantie.

## Pipeline

```text
résultats JSON canoniques
→ adaptateur audit_report_builder.py
→ configurations page.json
→ validation du schéma du builder
→ generate_assembled_page.py --check
→ génération HTML DSFR
→ capture native des rapports depuis `BUILD.json`
→ contrôles structurels, accessibilité et portabilité
```

Après génération, lancer la revue réutilisable :

```bash
python3 "<dossier-du-skill>/scripts/capture_audit_reports.py" <campagne>
```

Le helper découvre les pages dans `campaign.yaml` et `BUILD.json`, produit les captures dans `rapport-dsfr/captures-validation/` et écrit `REPORT-REVIEW.json`. Le mode `--check` vérifie la découverte et les liens locaux sans lancer Playwright.

## Garde-fous

- Ne jamais reconstruire les verdicts depuis le HTML.
- Ne jamais mélanger `NC_CONFIRMEE` et `ECART_CONFIRME`.
- Ne jamais injecter `observed_code` via `innerHTML` ou `allow_raw_html`.
- Ne pas masquer les constats lorsque JavaScript est désactivé.
- Ne pas transformer le style DSFR du rapport en preuve de conformité du site audité.
- Le DOM rendu observé n’est pas présenté comme le fichier source du dépôt.

## Définition de fin

- chaque sortie contient `data-audit-builder="dsfr-components"` ;
- toutes les configurations passent le schéma assemblé et `--check` ;
- le portail relie les rapports et les pages détaillées ;
- les nombres du HTML correspondent aux JSON canoniques ;
- les extraits malveillants sont échappés ;
- les ancres, identifiants, liens et contrôles clavier sont vérifiés ;
- `rapport-dsfr/BUILD.json` référence toutes les sorties ;
- `VALIDATION.json` ne contient aucune erreur.
