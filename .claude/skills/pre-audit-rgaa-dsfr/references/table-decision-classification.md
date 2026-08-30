# Table de decision NC / RECO / NOTE-INTERNE

Reference pour la phase 3 (triage) du skill /pre-audit-rgaa-dsfr.

## Classification

| Signal | Classification | Exemples reels (audit AFA) |
|--------|---------------|---------------------------|
| Violation averee d'un critere RGAA avec test en echec identifiable | **NC** | `aria-labelledby` orphelin (7.1.1), hierarchie titres (9.1.1), `alt` non vide sur image decorative (1.1.1) |
| Bug fonctionnel sans critere RGAA applicable | **RECO** | URLs partage malformees (pas de critere RGAA sur la validite des cibles), faute d'orthographe dans un contenu, coquille dans un attribut `alt` |
| Comportement potentiellement non conforme mais verification manuelle necessaire | **NOTE-INTERNE** | Modale DSFR avec double comportement desktop/mobile (inline vs dialog), retour du focus apres fermeture, focus initial sur le mauvais element |
| Comportement conforme au design system meme s'il semble suspect | **PAS de ticket** | `role="dialog"` absent en desktop sur le header DSFR = comportement voulu (inline, pas une modale) |
| Anti-pattern ARIA non bloquant (ex : roles landmarks redondants) | **RECO** | `<header role="banner">` redondant — pas une NC mais du bruit |

## Regle anti-faux-positif

Avant de classer un comportement en NC sur un composant DSFR, verifier si c'est le comportement voulu du design system. Si oui : pas de ticket ou NOTE-INTERNE. Un LLM a tendance a classer en NC tout attribut ARIA manquant sans verifier le contexte.

## Severite (pour les NC uniquement)

| Niveau | Critere |
|--------|---------|
| Bloquant | Empeche l'acces au contenu ou a une fonctionnalite pour un groupe d'utilisateurs |
| Majeur | Degrade significativement l'experience (navigation, comprehension) |
| Mineur | Perfectible mais n'empeche pas l'usage |

## Defauts systemiques

Si un meme defaut (meme critere RGAA, meme cause racine) apparait sur la page en cours ET dans les tickets existants d'autres pages :

- Ne PAS generer un ticket complet duplique
- Generer un ticket allege qui reference le ticket original : « Defaut systemique — meme cause racine que NC-P01-004. Affecte aussi : PAP, PMIS, PML. Correction unique dans le template Drupal `paragraph--type--ds-carte` »
- Lister les pages affectees dans le ticket de reference original
