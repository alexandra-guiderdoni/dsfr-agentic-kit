# Contre-revue indépendante DSFR 1.15.3

**Date** : 2026-09-12

**Verdict** : clôturée pour le périmètre de cette contre-revue, après correction du journal de migration dans `dsfr-agentic-packs`. Cette conclusion ne vaut pas déclaration de conformité globale au DSFR.

## Constats vérifiés

- Le moteur `audit-rgaa-creator` traite séparément les champs en erreur dans un `fr-input-group` et hors groupe. Le rejeu des preuves P06 ne signale aucun des cinq champs groupés et relève `DSFR-INPUT-ERROR-STATE-003` sur `#edit-question`.
- Le contrôle Playwright compte les messages `fr-message--error` et conserve `fr-error-text` comme repli pour les pages tierces héritées.
- Les variantes en erreur `input`, `select` et `upload` de la bibliothèque utilisent `p.fr-message.fr-message--error`, sans `fr-error-text` ni `fr-valid`.
- La recherche générée, y compris celle du bandeau, relie le champ à un `fr-messages-group` par `aria-describedby`. Les sorties dorées et générées ont passé leurs contrôles.

## Propagation et contrôles

Les fichiers concernés du moteur, du contrôle Playwright, de la bibliothèque, du générateur et du catalogue ont été comparés entre la source, le pack et le kit ; leurs contenus sont identiques. Le catalogue contient 54 règles et exclut les champs groupés de `DSFR-INPUT-ERROR-STATE-003`.

Résultats enregistrés pendant la contre-revue : 44 tests d’audit réussis ; 21 cas dorés et invariants réussis ; contrôle des sorties contre DSFR 1.15.3 réussi sur 12 pages et 137 composants ; sync et export à sec sans écart avec leurs cibles.

## Mesures des fontes Marianne

Dans les huit faces `.woff2`, la version passe de 1.007 à 1.011 et un seul point de code est ajouté : U+202F (`narrownobreakspace`). Aucun point de code n’est retiré. Les avances de U+0020 et U+00A0 restent à 270/1000. U+202F avance de 135/1000 dans les quatre faces droites et de 131/1000 dans les quatre faces italiques.

Avec Marianne chargée dans Chromium, les pages DSFR 1.15.2 et 1.15.3 donnent, à 100 px, les mêmes largeurs : 27 px pour U+0020, 27 px pour U+00A0 et 13,5 px pour U+202F. Le texte `A B` reste sur une ligne dans les deux versions. L’effet du nouveau hinting sur d’autres moteurs et systèmes reste non mesuré.

## Journal des commits source

- `20aa4a0e6` est intitulé « Hook pre-commit : « Piste A » exclu de la capitalisation anglaise ». Son diff modifie `.git-hooks/pre-commit`, mais touche aussi les livrables et sorties Opquast sous `projets-actifs/` : 91 fichiers au total. Le titre ne décrit donc qu’une partie de sa portée.
- `3f9443fee` est intitulé « Newsletter Opquast : dossier dédié, slides et supports générés ». Son diff ne modifie que `projets-actifs/opquast/outputs/ia-slides/2026-09-12-newsletter-regles-opquast-v5/qa-livraison.md`, qui actualise le compte rendu de livraison ; le sujet et le corps décrivent des livrables qui ne figurent pas dans ce diff.

Le journal détaillé de migration et ces deux références sont consignés dans le plan d’audit du dépôt `dsfr-agentic-packs`.
