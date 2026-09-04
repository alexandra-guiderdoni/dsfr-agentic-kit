# NC-TRANSVERSE-010 — Identifiant partagé par les liens du pied de page

**Statut** : Préqualification — NC confirmée dans les rapports sources  
**Référentiel** : RGAA 4.1.2  
**Sévérité** : Majeur  
**Justification de sévérité** : Les ancres, scripts et relations fondés sur cet identifiant peuvent cibler un contrôle arbitraire du pied de page.  
**Date** : 2026-09-04  
**Composant / gabarit** : Pied de page  
**Portée** : Transverse — P01, P02, P03, P04, P05, P06, P07, P08, P09  
**Pages affectées** : P01, P02, P03, P04, P05, P06, P07, P08, P09  
**Constats sources regroupés** : 9

> Ces conclusions proviennent d’une préqualification instrumentée. Elles ne constituent ni un taux RGAA officiel ni une validation après correction.

---

## Pages et rapports sources

| Page | Nom | URL | Rapport RGAA |
|---|---|---|---|
| P01 | Accueil | https://moa.douane.gouv.fr/ | [P01-RGAA.html](../../RGAA/P01-RGAA.html) |
| P02 | Plan du site | https://moa.douane.gouv.fr/plan-du-site | [P02-RGAA.html](../../RGAA/P02-RGAA.html) |
| P03 | Déclaration d’accessibilité | https://moa.douane.gouv.fr/pied-de-page/declaration-daccessibilite-du-portail-dounegouvfr | [P03-RGAA.html](../../RGAA/P03-RGAA.html) |
| P04 | Mentions légales | https://moa.douane.gouv.fr/mentions-legales | [P04-RGAA.html](../../RGAA/P04-RGAA.html) |
| P05 | Données personnelles | https://moa.douane.gouv.fr/pied-de-page/donnees-personnelles | [P05-RGAA.html](../../RGAA/P05-RGAA.html) |
| P06 | Formulaire Écrivez-nous | https://moa.douane.gouv.fr/formulaire-infos-douane-service | [P06-RGAA.html](../../RGAA/P06-RGAA.html) |
| P07 | Voyages à l’étranger | https://moa.douane.gouv.fr/particuliers/voyages-letranger | [P07-RGAA.html](../../RGAA/P07-RGAA.html) |
| P08 | Commerce international | https://moa.douane.gouv.fr/professionnels/commerce-international | [P08-RGAA.html](../../RGAA/P08-RGAA.html) |
| P09 | Actualité DELTA IE | https://moa.douane.gouv.fr/actualites/point-dactualite-sur-le-deploiement-de-delta-ie-import-et-export-au-5-fevrier-2026 | [P09-RGAA.html](../../RGAA/P09-RGAA.html) |

## Références RGAA

- **Critère 8.2** — Pour chaque page web, le code source généré est-il valide selon le type de document spécifié ?
- **Test 8.2.1** — Pour chaque déclaration de type de document, le code source généré de la page vérifie-t-il ces conditions ? Les balises, attributs et valeurs d’attributs respectent les règles d’écriture ; L’imbrication des balises est conforme ; L’ouverture et la fermeture des balises sont conformes ; Les valeurs d’attribut id sont uniques dans la page ; Les attributs ne sont pas doublés sur un même élément.

---

## Code source constaté

### id=footer__bottom-link présent 6 fois

```html
<a id="footer__bottom-link" href="/plan-du-site" class="fr-footer__bottom-link">Plan du site</a>

<a id="footer__bottom-link" href="/accessibilite" class="fr-footer__bottom-link">Accessibilité : partiellement conforme</a>

<a id="footer__bottom-link" href="/mentions-legales" class="fr-footer__bottom-link">Mentions légales</a>

<a id="footer__bottom-link" href="/fiche/donnees-personnelles" class="fr-footer__bottom-link">Données personnelles</a>

<a id="footer__bottom-link" href="/gestion-des-cookies" class="fr-footer__bottom-link">Gestion des cookies</a>

<button aria-controls="fr-theme-modal" data-fr-opened="false" id="footer__bottom-link" class="fr-icon-theme-fill fr-btn--icon-left fr-footer__bottom-link" data-fr-js-modal-button="true">
						Paramètres d'affichage
					</button>
```

## Inventaire des constats sources

| Page | Identifiant source | Critère / test | Sélecteur | Observation | Provenance | Preuve principale |
|---|---|---|---|---|---|---|
| P01 | `P01-RGAA-8-2-ID-UNIQUE-001-004` | 8.2 / 8.2.1 | `footer.fr-footer > div.fr-container > div.fr-footer__bottom:nth-of-type(2) > ul.fr-footer__bottom-list > li.fr-footer__bottom-item:nth-of-type(1) > a.fr-footer__bottom-link, footer.fr-footer > div.fr-container > div.fr-footer__bottom:nth-of-type(2) > ul.fr-footer__bottom-list > li.fr-footer__bottom-item:nth-of-type(2) > a.fr-footer__bottom-link, footer.fr-footer > div.fr-container > div.fr-footer__bottom:nth-of-type(2) > ul.fr-footer__bottom-list > li.fr-footer__bottom-item:nth-of-type(3) > a.fr-footer__bottom-link, footer.fr-footer > div.fr-container > div.fr-footer__bottom:nth-of-type(2) > ul.fr-footer__bottom-list > li.fr-footer__bottom-item:nth-of-type(4) > a.fr-footer__bottom-link, footer.fr-footer > div.fr-container > div.fr-footer__bottom:nth-of-type(2) > ul.fr-footer__bottom-list > li.fr-footer__bottom-item:nth-of-type(5) > a.fr-footer__bottom-link, footer.fr-footer > div.fr-container > div.fr-footer__bottom:nth-of-type(2) > ul.fr-footer__bottom-list > li.fr-footer__bottom-item:nth-of-type(6) > button.fr-icon-theme-fill.fr-btn--icon-left` | id=footer__bottom-link présent 6 fois | RENDERED_DOM | `rgaa/preuves/P01/attempt-009/raw-dom.json` |
| P02 | `P02-RGAA-8-2-ID-UNIQUE-001-004` | 8.2 / 8.2.1 | `footer.fr-footer > div.fr-container > div.fr-footer__bottom:nth-of-type(2) > ul.fr-footer__bottom-list > li.fr-footer__bottom-item:nth-of-type(1) > a.fr-footer__bottom-link, footer.fr-footer > div.fr-container > div.fr-footer__bottom:nth-of-type(2) > ul.fr-footer__bottom-list > li.fr-footer__bottom-item:nth-of-type(2) > a.fr-footer__bottom-link, footer.fr-footer > div.fr-container > div.fr-footer__bottom:nth-of-type(2) > ul.fr-footer__bottom-list > li.fr-footer__bottom-item:nth-of-type(3) > a.fr-footer__bottom-link, footer.fr-footer > div.fr-container > div.fr-footer__bottom:nth-of-type(2) > ul.fr-footer__bottom-list > li.fr-footer__bottom-item:nth-of-type(4) > a.fr-footer__bottom-link, footer.fr-footer > div.fr-container > div.fr-footer__bottom:nth-of-type(2) > ul.fr-footer__bottom-list > li.fr-footer__bottom-item:nth-of-type(5) > a.fr-footer__bottom-link, footer.fr-footer > div.fr-container > div.fr-footer__bottom:nth-of-type(2) > ul.fr-footer__bottom-list > li.fr-footer__bottom-item:nth-of-type(6) > button.fr-icon-theme-fill.fr-btn--icon-left` | id=footer__bottom-link présent 6 fois | RENDERED_DOM | `rgaa/preuves/P02/attempt-002/raw-dom.json` |
| P03 | `P03-RGAA-8-2-ID-UNIQUE-001-004` | 8.2 / 8.2.1 | `footer.fr-footer > div.fr-container > div.fr-footer__bottom:nth-of-type(2) > ul.fr-footer__bottom-list > li.fr-footer__bottom-item:nth-of-type(1) > a.fr-footer__bottom-link, footer.fr-footer > div.fr-container > div.fr-footer__bottom:nth-of-type(2) > ul.fr-footer__bottom-list > li.fr-footer__bottom-item:nth-of-type(2) > a.fr-footer__bottom-link, footer.fr-footer > div.fr-container > div.fr-footer__bottom:nth-of-type(2) > ul.fr-footer__bottom-list > li.fr-footer__bottom-item:nth-of-type(3) > a.fr-footer__bottom-link, footer.fr-footer > div.fr-container > div.fr-footer__bottom:nth-of-type(2) > ul.fr-footer__bottom-list > li.fr-footer__bottom-item:nth-of-type(4) > a.fr-footer__bottom-link, footer.fr-footer > div.fr-container > div.fr-footer__bottom:nth-of-type(2) > ul.fr-footer__bottom-list > li.fr-footer__bottom-item:nth-of-type(5) > a.fr-footer__bottom-link, footer.fr-footer > div.fr-container > div.fr-footer__bottom:nth-of-type(2) > ul.fr-footer__bottom-list > li.fr-footer__bottom-item:nth-of-type(6) > button.fr-icon-theme-fill.fr-btn--icon-left` | id=footer__bottom-link présent 6 fois | RENDERED_DOM | `rgaa/preuves/P03/attempt-001/raw-dom.json` |
| P04 | `P04-RGAA-8-2-ID-UNIQUE-001-004` | 8.2 / 8.2.1 | `footer.fr-footer > div.fr-container > div.fr-footer__bottom:nth-of-type(2) > ul.fr-footer__bottom-list > li.fr-footer__bottom-item:nth-of-type(1) > a.fr-footer__bottom-link, footer.fr-footer > div.fr-container > div.fr-footer__bottom:nth-of-type(2) > ul.fr-footer__bottom-list > li.fr-footer__bottom-item:nth-of-type(2) > a.fr-footer__bottom-link, footer.fr-footer > div.fr-container > div.fr-footer__bottom:nth-of-type(2) > ul.fr-footer__bottom-list > li.fr-footer__bottom-item:nth-of-type(3) > a.fr-footer__bottom-link, footer.fr-footer > div.fr-container > div.fr-footer__bottom:nth-of-type(2) > ul.fr-footer__bottom-list > li.fr-footer__bottom-item:nth-of-type(4) > a.fr-footer__bottom-link, footer.fr-footer > div.fr-container > div.fr-footer__bottom:nth-of-type(2) > ul.fr-footer__bottom-list > li.fr-footer__bottom-item:nth-of-type(5) > a.fr-footer__bottom-link, footer.fr-footer > div.fr-container > div.fr-footer__bottom:nth-of-type(2) > ul.fr-footer__bottom-list > li.fr-footer__bottom-item:nth-of-type(6) > button.fr-icon-theme-fill.fr-btn--icon-left` | id=footer__bottom-link présent 6 fois | RENDERED_DOM | `rgaa/preuves/P04/attempt-001/raw-dom.json` |
| P05 | `P05-RGAA-8-2-ID-UNIQUE-001-004` | 8.2 / 8.2.1 | `footer.fr-footer > div.fr-container > div.fr-footer__bottom:nth-of-type(2) > ul.fr-footer__bottom-list > li.fr-footer__bottom-item:nth-of-type(1) > a.fr-footer__bottom-link, footer.fr-footer > div.fr-container > div.fr-footer__bottom:nth-of-type(2) > ul.fr-footer__bottom-list > li.fr-footer__bottom-item:nth-of-type(2) > a.fr-footer__bottom-link, footer.fr-footer > div.fr-container > div.fr-footer__bottom:nth-of-type(2) > ul.fr-footer__bottom-list > li.fr-footer__bottom-item:nth-of-type(3) > a.fr-footer__bottom-link, footer.fr-footer > div.fr-container > div.fr-footer__bottom:nth-of-type(2) > ul.fr-footer__bottom-list > li.fr-footer__bottom-item:nth-of-type(4) > a.fr-footer__bottom-link, footer.fr-footer > div.fr-container > div.fr-footer__bottom:nth-of-type(2) > ul.fr-footer__bottom-list > li.fr-footer__bottom-item:nth-of-type(5) > a.fr-footer__bottom-link, footer.fr-footer > div.fr-container > div.fr-footer__bottom:nth-of-type(2) > ul.fr-footer__bottom-list > li.fr-footer__bottom-item:nth-of-type(6) > button.fr-icon-theme-fill.fr-btn--icon-left` | id=footer__bottom-link présent 6 fois | RENDERED_DOM | `rgaa/preuves/P05/attempt-002/raw-dom.json` |
| P06 | `P06-RGAA-8-2-ID-UNIQUE-001-006` | 8.2 / 8.2.1 | `footer.fr-footer > div.fr-container > div.fr-footer__bottom:nth-of-type(2) > ul.fr-footer__bottom-list > li.fr-footer__bottom-item:nth-of-type(1) > a.fr-footer__bottom-link, footer.fr-footer > div.fr-container > div.fr-footer__bottom:nth-of-type(2) > ul.fr-footer__bottom-list > li.fr-footer__bottom-item:nth-of-type(2) > a.fr-footer__bottom-link, footer.fr-footer > div.fr-container > div.fr-footer__bottom:nth-of-type(2) > ul.fr-footer__bottom-list > li.fr-footer__bottom-item:nth-of-type(3) > a.fr-footer__bottom-link, footer.fr-footer > div.fr-container > div.fr-footer__bottom:nth-of-type(2) > ul.fr-footer__bottom-list > li.fr-footer__bottom-item:nth-of-type(4) > a.fr-footer__bottom-link, footer.fr-footer > div.fr-container > div.fr-footer__bottom:nth-of-type(2) > ul.fr-footer__bottom-list > li.fr-footer__bottom-item:nth-of-type(5) > a.fr-footer__bottom-link, footer.fr-footer > div.fr-container > div.fr-footer__bottom:nth-of-type(2) > ul.fr-footer__bottom-list > li.fr-footer__bottom-item:nth-of-type(6) > button.fr-icon-theme-fill.fr-btn--icon-left` | id=footer__bottom-link présent 6 fois | RENDERED_DOM | `rgaa/preuves/P06/attempt-004/raw-dom.json` |
| P07 | `P07-RGAA-8-2-ID-UNIQUE-001-004` | 8.2 / 8.2.1 | `footer.fr-footer > div.fr-container > div.fr-footer__bottom:nth-of-type(2) > ul.fr-footer__bottom-list > li.fr-footer__bottom-item:nth-of-type(1) > a.fr-footer__bottom-link, footer.fr-footer > div.fr-container > div.fr-footer__bottom:nth-of-type(2) > ul.fr-footer__bottom-list > li.fr-footer__bottom-item:nth-of-type(2) > a.fr-footer__bottom-link, footer.fr-footer > div.fr-container > div.fr-footer__bottom:nth-of-type(2) > ul.fr-footer__bottom-list > li.fr-footer__bottom-item:nth-of-type(3) > a.fr-footer__bottom-link, footer.fr-footer > div.fr-container > div.fr-footer__bottom:nth-of-type(2) > ul.fr-footer__bottom-list > li.fr-footer__bottom-item:nth-of-type(4) > a.fr-footer__bottom-link, footer.fr-footer > div.fr-container > div.fr-footer__bottom:nth-of-type(2) > ul.fr-footer__bottom-list > li.fr-footer__bottom-item:nth-of-type(5) > a.fr-footer__bottom-link, footer.fr-footer > div.fr-container > div.fr-footer__bottom:nth-of-type(2) > ul.fr-footer__bottom-list > li.fr-footer__bottom-item:nth-of-type(6) > button.fr-icon-theme-fill.fr-btn--icon-left` | id=footer__bottom-link présent 6 fois | RENDERED_DOM | `rgaa/preuves/P07/attempt-002/raw-dom.json` |
| P08 | `P08-RGAA-8-2-ID-UNIQUE-001-004` | 8.2 / 8.2.1 | `footer.fr-footer > div.fr-container > div.fr-footer__bottom:nth-of-type(2) > ul.fr-footer__bottom-list > li.fr-footer__bottom-item:nth-of-type(1) > a.fr-footer__bottom-link, footer.fr-footer > div.fr-container > div.fr-footer__bottom:nth-of-type(2) > ul.fr-footer__bottom-list > li.fr-footer__bottom-item:nth-of-type(2) > a.fr-footer__bottom-link, footer.fr-footer > div.fr-container > div.fr-footer__bottom:nth-of-type(2) > ul.fr-footer__bottom-list > li.fr-footer__bottom-item:nth-of-type(3) > a.fr-footer__bottom-link, footer.fr-footer > div.fr-container > div.fr-footer__bottom:nth-of-type(2) > ul.fr-footer__bottom-list > li.fr-footer__bottom-item:nth-of-type(4) > a.fr-footer__bottom-link, footer.fr-footer > div.fr-container > div.fr-footer__bottom:nth-of-type(2) > ul.fr-footer__bottom-list > li.fr-footer__bottom-item:nth-of-type(5) > a.fr-footer__bottom-link, footer.fr-footer > div.fr-container > div.fr-footer__bottom:nth-of-type(2) > ul.fr-footer__bottom-list > li.fr-footer__bottom-item:nth-of-type(6) > button.fr-icon-theme-fill.fr-btn--icon-left` | id=footer__bottom-link présent 6 fois | RENDERED_DOM | `rgaa/preuves/P08/attempt-001/raw-dom.json` |
| P09 | `P09-RGAA-8-2-ID-UNIQUE-001-005` | 8.2 / 8.2.1 | `footer.fr-footer > div.fr-container > div.fr-footer__bottom:nth-of-type(2) > ul.fr-footer__bottom-list > li.fr-footer__bottom-item:nth-of-type(1) > a.fr-footer__bottom-link, footer.fr-footer > div.fr-container > div.fr-footer__bottom:nth-of-type(2) > ul.fr-footer__bottom-list > li.fr-footer__bottom-item:nth-of-type(2) > a.fr-footer__bottom-link, footer.fr-footer > div.fr-container > div.fr-footer__bottom:nth-of-type(2) > ul.fr-footer__bottom-list > li.fr-footer__bottom-item:nth-of-type(3) > a.fr-footer__bottom-link, footer.fr-footer > div.fr-container > div.fr-footer__bottom:nth-of-type(2) > ul.fr-footer__bottom-list > li.fr-footer__bottom-item:nth-of-type(4) > a.fr-footer__bottom-link, footer.fr-footer > div.fr-container > div.fr-footer__bottom:nth-of-type(2) > ul.fr-footer__bottom-list > li.fr-footer__bottom-item:nth-of-type(5) > a.fr-footer__bottom-link, footer.fr-footer > div.fr-container > div.fr-footer__bottom:nth-of-type(2) > ul.fr-footer__bottom-list > li.fr-footer__bottom-item:nth-of-type(6) > button.fr-icon-theme-fill.fr-btn--icon-left` | id=footer__bottom-link présent 6 fois | RENDERED_DOM | `rgaa/preuves/P09/attempt-001/raw-dom.json` |

---

## Analyse du défaut

Sur les neuf pages, cinq liens et le bouton des paramètres d’affichage partagent l’identifiant `footer__bottom-link`. Le style est déjà porté par la classe du même nom ; ces identifiants ne sont pas nécessaires et doivent être traités dans le template de pied de page.

## Impact utilisateur

Les ancres, scripts et relations fondés sur cet identifiant peuvent cibler un contrôle arbitraire du pied de page.

---

## Recommandations

### Solution 1 — Supprimer les identifiants inutiles (recommandée)

Conserver la classe réutilisable pour le style et retirer l’attribut `id` de chaque entrée non référencée.

```html
<a href="/plan-du-site" class="fr-footer__bottom-link">Plan du site</a>
<a href="/accessibilite" class="fr-footer__bottom-link">Accessibilité</a>
<button aria-controls="fr-theme-modal"
        class="fr-icon-theme-fill fr-btn--icon-left fr-footer__bottom-link">
  Paramètres d’affichage
</button>
```

## Comparaison avec le composant DSFR

**Composant concerné** : Pied de page

| Point contrôlé | DSFR / comportement attendu | Site audité |
|---|---|---|
| Style partagé | Classe CSS réutilisable | Classe et id identiques |
| Identifiants | Absents s’ils ne sont pas référencés | footer__bottom-link répété six fois |
| Cause attribuée | Template de pied de page | Attribut id ajouté à chaque entrée |

Le constat est attribué à l’intégration observée. La présence de classes `fr-*` ne suffit pas à attribuer le défaut au DSFR natif.

---

## Vérification après correction

- [ ] Vérifier l’absence de `id="footer__bottom-link"` dupliqué sur les neuf pages.
- [ ] Contrôler visuellement que les styles du pied de page sont inchangés.
- [ ] Ouvrir les paramètres d’affichage et vérifier leur fonctionnement.

La correction ne doit être considérée comme clôturée qu’après production d’une nouvelle preuve et recontrôle humain.

## Références

- [RGAA 4.1.2 — test 8.2.1](https://accessibilite.numerique.gouv.fr/methode/criteres-et-tests/#8.2.1)
- [DSFR 1.15.2 — composant footer](https://github.com/GouvernementFR/dsfr/tree/v1.15.2/src/dsfr/component/footer)
- Source factuelle : rapports HTML RGAA livrés pour les pages indiquées et constats `NC_CONFIRMEE` correspondants.
