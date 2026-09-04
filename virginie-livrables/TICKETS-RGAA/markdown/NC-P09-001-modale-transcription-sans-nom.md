# NC-P09-001 — Modale de transcription sans nom accessible

**Statut** : Préqualification — NC confirmée dans les rapports sources  
**Référentiel** : RGAA 4.1.2  
**Sévérité** : Majeur  
**Justification de sévérité** : Une personne utilisant un lecteur d’écran accède au texte de transcription sans connaître le nom de la fenêtre ouverte ni son lien avec le graphique.  
**Date** : 2026-09-04  
**Composant / gabarit** : Modale de transcription  
**Portée** : Locale — P09  
**Pages affectées** : P09  
**Constats sources regroupés** : 1

> Ces conclusions proviennent d’une préqualification instrumentée. Elles ne constituent ni un taux RGAA officiel ni une validation après correction.

---

## Pages et rapports sources

| Page | Nom | URL | Rapport RGAA |
|---|---|---|---|
| P09 | Actualité DELTA IE | https://moa.douane.gouv.fr/actualites/point-dactualite-sur-le-deploiement-de-delta-ie-import-et-export-au-5-fevrier-2026 | [P09-RGAA.html](../../RGAA/P09-RGAA.html) |

## Références RGAA

- **Critère 7.1** — Chaque script est-il, si nécessaire, compatible avec les technologies d’assistance ?
- **Test 7.1.1** — Chaque script qui génère ou contrôle un composant d’interface vérifie-t-il, si nécessaire, une de ces conditions ? Le nom, le rôle, la valeur, le paramétrage et les changements d’états sont accessibles aux technologies d’assistance via une API d’accessibilité ; Un composant d’interface accessible permettant d’accéder aux mêmes fonctionnalités est présent dans la page ; Une alternative accessible permet d’accéder aux mêmes fonctionnalités.

---

## Code source constaté

### P09 — dialogue observé

```html
<dialog id="fr-transcription-modal-transcription-20210" class="fr-modal" aria-labelledby="fr-transcription-modal-title" data-fr-js-modal="true">
					<div class="fr-container fr-container--fluid fr-container-md">
						<div class="fr-grid-row fr-grid-row--center">
							<div class="fr-col-12 fr-col-md-10 fr-col-lg-8">
								<div class="fr-modal__body" data-fr-js-modal-body="true">
									<div class="fr-modal__header">
										<button aria-controls="fr-transcription-modal-transcription-20210" title="Fermer" type="button" class="fr-btn--close fr-btn" data-fr-js-modal-button="true">Fermer</button>
									</div>
									<div class="fr-modal__content">
										<p>Graphique en courbes présentant l'évolution quotidienne de la part des déclarations d'exportation par type de fret entre le 8 décembre 2025 et le 3 février 2026. Le ratio cargo augmente progressivement et reste globalement le plus élevé à partir de la mi-janvier (environ 60 à 75 %). Les ratios tous frets et express sont plus irréguliers, avec plusieurs pics et chutes marquées, le fret express étant la série la plus volatile.</p>

									</div>
								</div>
							</div>
						</div>
					</div>
				</dialog>
```

## Inventaire des constats sources

| Page | Identifiant source | Critère / test | Sélecteur | Observation | Provenance | Preuve principale |
|---|---|---|---|---|---|---|
| P09 | `P09-RGAA-7-1-DIALOG-NAME-001-001` | 7.1 / 7.1.1 | `#fr-transcription-modal-transcription-20210` | aria-labelledby référence #fr-transcription-modal-title absent | RENDERED_DOM | `rgaa/preuves/P09/attempt-001/raw-dom.json` |

---

## Analyse du défaut

La modale de transcription cite `fr-transcription-modal-title` dans `aria-labelledby`, mais aucune cible rendue ne porte cet identifiant. La transcription est présente ; seul le titre programmatique du dialogue manque. Ce défaut relève du template de transcription de P09, distinct de la modale CGU.

## Impact utilisateur

Une personne utilisant un lecteur d’écran accède au texte de transcription sans connaître le nom de la fenêtre ouverte ni son lien avec le graphique.

---

## Recommandations

### Solution 1 — Ajouter un titre unique et le référencer (recommandée)

Créer un titre visible, suffixé avec l’identifiant métier de la transcription, puis mettre à jour `aria-labelledby`.

```html
<dialog id="fr-transcription-modal-transcription-20210"
        aria-labelledby="fr-transcription-modal-title-20210">
  <h2 id="fr-transcription-modal-title-20210" class="fr-modal__title">
    Transcription du graphique
  </h2>
  <!-- transcription -->
</dialog>
```

## Comparaison avec le composant DSFR

**Composant concerné** : Modale de transcription

| Point contrôlé | DSFR / comportement attendu | Site audité |
|---|---|---|
| Nom accessible | Titre présent et relié par aria-labelledby | Identifiant de titre absent |
| Contenu | Transcription disponible | Transcription présente |
| Cause attribuée | Structure DSFR nommée | Template de transcription |

Le constat est attribué à l’intégration observée. La présence de classes `fr-*` ne suffit pas à attribuer le défaut au DSFR natif.

---

## Vérification après correction

- [ ] Ouvrir la transcription au clavier.
- [ ] Contrôler que `aria-labelledby` cible un titre existant et unique.
- [ ] Vérifier le nom calculé dans l’arbre d’accessibilité puis avec un lecteur d’écran réel.
- [ ] Vérifier le retour du focus sur le déclencheur à la fermeture.

La correction ne doit être considérée comme clôturée qu’après production d’une nouvelle preuve et recontrôle humain.

## Références

- [RGAA 4.1.2 — test 7.1.1](https://accessibilite.numerique.gouv.fr/methode/criteres-et-tests/#7.1.1)
- [DSFR 1.15.2 — composant modal](https://github.com/GouvernementFR/dsfr/tree/v1.15.2/src/dsfr/component/modal)
- Source factuelle : rapports HTML RGAA livrés pour les pages indiquées et constats `NC_CONFIRMEE` correspondants.
