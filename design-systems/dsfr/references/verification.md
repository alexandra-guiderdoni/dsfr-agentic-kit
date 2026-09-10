---
title: "DSFR - vérification et claims"
scope: preuves, conformité, publication, accessibilité
load_when: "Le livrable doit être vérifié, publié, audité ou transmis."
---

# DSFR - vérification et claims

La preuve doit être proportionnée au niveau de risque. Une capture montre un rendu, pas une conformité DSFR, RGAA ou juridique.

## Niveaux

| Force | Action |
|---|---|
| obligatoire avant publication | vérifier, corriger ou demander |
| recommandé en prototype | appliquer si possible, sinon marquer `à vérifier` |
| différable avec label | continuer et nommer la limite |
| interdit sans preuve | retirer l'affirmation ou abaisser le statut |

## Ce profil ne prouve pas

- conformité RGAA, taux réglementaire, déclaration ou publication ;
- droit d'usage de la marque de l'État ;
- exhaustivité officielle des tokens CSS, classes utilitaires ou composants ;
- comportement JS, clavier, focus ou lecteur d'écran sans test dédié.

## Formulations

Autorisées :

- `aucun écart observé sur les règles DSFR exécutées` ou `écarts DSFR observés à qualifier` ;
- `prototype DSFR à vérifier avant publication` ;
- `structure inspirée des fondamentaux DSFR` ;
- `composants DSFR utilisés selon les sources lues`.

Interdites sans preuve :

- `conforme DSFR` ;
- `conforme RGAA` ;
- `prêt pour publication` ;
- `usage autorisé de la marque de l'État`.

Ces formulations valent aussi pour les titres, métadonnées, commentaires HTML,
handoffs, rapports et exemples : une assertion cachée dans un artefact reste un
claim.

## Recettes de preuve

| Situation | Preuve suffisante pour continuer | Preuve avant publication |
|---|---|---|
| composant connu | nom, source, structure appliquée | page officielle lue et état interactif vérifié |
| composant incertain | fallback sémantique + `à vérifier` | confirmation qu'aucun composant officiel ne couvre le besoin |
| maquette Figma-like | composants, styles et tokens nommés | librairie Figma ou spécification projet vérifiée |
| page complète | capture mobile/desktop ou inspection équivalente | liens réels, header/footer, console, clavier, mode sombre si exposé |
| composant JS | clic ou interaction après initialisation DSFR, attributs ARIA et classe d'état observés | test clavier, focus, lecteur d'écran ou audit spécialisé selon le risque |
| enveloppe de page | `head`, liens d'évitement, landmarks et footer listés | mentions légales, accessibilité, données personnelles, cookies, licence |
| contenu administratif | source fournie ou champ marqué inconnu | source juridique ou métier validée |
| contenu généré ou assisté par IA | mention de transparence prévue ou `non vérifié` | texte IA marqué en préambule, image ou vidéo IA marquée sous le média, icône prévue, lien vers page d'information |
| marque État | contexte de prototype ou retrait du bloc marque | mandat, périmètre, agrément ou validation humaine |
| accessibilité | focus, labels, titres, alternatives plausibles | audit RGAA ou test spécialisé si conformité revendiquée |

## Routage accessibilité et RGAA

Les skills d'accessibilité exécutent les vérifications. Ce profil DSFR ne remplace pas leurs workflows.
| Situation | Skill ou source |
|---|---|
| audit WCAG d'une page ou d'un fichier | `audit-accessibilite-web` |
| audit complet mêlant WCAG, RGAA, DSFR, clavier et arbre d'accessibilité | `audit-a11y-complet` |
| audit DSFR par règle et instance avec DOM rendu, structure attendue et qualification | `audit-dsfr-complet` |
| campagne multi-pages reprenable puis portail HTML via le builder DSFR | `audit-rgaa-creator` + `audit-report-dsfr` |
| préqualification RGAA par test et instance avec revue des 258 tests | `audit-rgaa-complet` |
| audit RGAA cadré ou rapport réglementaire | `audit-rgaa-creator` puis validation humaine |
| pré-audit RGAA, triage, fiches ou tickets | `pre-audit-rgaa-dsfr` |
| reflow, zoom, focus, orientation, autocomplete, taille de cible | `tests-conformite-wcag` |
| correction après rapport | `fix-accessibilite` ou `a11y-loop` |
| test lecteur d'écran réel | `screen-reader-testing` |

Pour tout audit ou pré-audit RGAA, consulter aussi `AY11_ROOT` si cette variable
est définie ou si `--ay11-root` est fourni. Le kit ne suppose aucun chemin
relatif particulier.

AY11 est une source secondaire de preuves candidates et de contrats RGAA : référentiel local, profils `rgaa-25`, `rgaa-50`, `rgaa-106`, collecteurs HTML et navigateur, noms accessibles, signaux axe-core, DOM et arbre d'accessibilité. Il s'applique à tous les critères RGAA concernés par l'audit, pas seulement aux formulaires.

Limites :

- ne pas utiliser AY11 comme source DSFR primaire ;
- ne pas interpréter l'absence de signal AY11 comme une conformité ;
- ne pas transformer un signal AY11 en verdict RGAA sans preuve complémentaire et validation humaine ;
- ne pas charger AY11 pour une simple maquette, un prototype DSFR ou un formulaire basique sans demande d'audit RGAA.

## Checklist

- Source DSFR officielle ou locale consultée pour chaque composant non trivial.
- Version DSFR nommée.
- Aucun composant inventé quand un composant officiel existe.
- Header, main et footer présents pour une page complète.
- Liens d'évitement présents pour toute page complète, en début de page, avec au minimum `Accéder au contenu`.
- Bloc marque et liens footer conformes au périmètre du service.
- Mention accessibilité, mentions légales, données personnelles et gestion des cookies prévues avant publication.
- Tokens de décision utilisés.
- Marianne déclarée comme police de sortie.
- Grille `fr-container`, `fr-grid-row`, `fr-col-*` respectée.
- Focus visible, navigation clavier plausible, ordre de titres correct.
- Aucun `href="#"` résiduel.
- Mode sombre ou contraste élevé vérifié, ou limite nommée.
- Console sans erreur bloquante si HTML interactif.
- Composants JS vérifiés après initialisation DSFR : accordéons, onglets, modales, menus et autres ouvertures ne doivent pas être jugés avant le bind.
- Contenu généré ou assisté par IA : mention visible, icône prévue et lien vers une page d'information, ou limite `non vérifié`.
- Si une sonde langue ou RGAA 8.7 remonte un signal, relire les textes visibles, corriger les anglicismes non nécessaires et marquer les mots étrangers restants avec `lang`.

## Format de preuve minimal

Pour une page HTML locale, nommer au minimum :

- fichier inspecté ;
- présence de `html lang="fr"`, `header`, `main`, `footer` ;
- absence de `href="#"` résiduel ;
- version DSFR ou source locale suivie ;
- preuve navigateur exécutée, ou `non vérifié` avec la raison.

## Compte rendu

```text
Preuve exécutée :
Ce que la preuve couvre :
Ce que la preuve ne couvre pas :
Claim final autorisé :
Décision :
```
