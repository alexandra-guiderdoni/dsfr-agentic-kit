---
title: "DSFR - verdict qualitatif routage LLM"
scope: profil DSFR, dsfr-components, near-miss
load_when: "Après une modification de DESIGN.md qui vise le comportement LLM."
---

# DSFR - verdict qualitatif routage LLM

Évaluation exécutée le 2026-07-09 avec deux probes `codex exec` en lecture seule.

## Cas testés

| Cas | Trace | Verdict |
|---|---|---|
| page rendez-vous DSFR | `runtime-traces/pos-rdv-page-codex-exec.txt` | PASS qualitatif |
| landing `DSFR-like` bleu-blanc-rouge | `runtime-traces/near-miss-dsfr-like-landing-codex-exec.txt` | PASS qualitatif avec limite runtime |

## Observations

- Le cas positif route vers `dsfr-components`, branche page complète, type formulaire.
- Le profil DSFR partagé est cité : `DESIGN.md`, `tokens.yaml` et `SKILL.md`.
- Le near-miss ne traite pas la palette bleu-blanc-rouge comme preuve DSFR.
- Le near-miss garde une marque neutre et abaisse le claim vers `structure inspirée des fondamentaux DSFR`.

## Verdict

Le profil DSFR aide utilement le LLM à distinguer une vraie demande DSFR d'une demande `DSFR-like`.

## Limites

- Ce sont des self-reports Codex, pas une trace interne opaque de sélection runtime.
- Aucun HTML n'a été généré.
- Aucun rendu navigateur, test clavier, audit DSFR ou audit RGAA n'a été exécuté.
