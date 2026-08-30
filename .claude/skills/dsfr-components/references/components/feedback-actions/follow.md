# Bouton de suivi (Follow)

Référence extraite de `../feedback-actions.md`.

---

Permet à l'utilisateur de s'abonner aux mises à jour d'une page ou d'un service (newsletter, alertes).

## Structure
```html
<div class="fr-follow">
    <div class="fr-container">
        <div class="fr-grid-row">
            <div class="fr-col-12 fr-col-md-8">
                <div class="fr-follow__newsletter">
                    <div>
                        <h2 class="fr-h5">Abonnez-vous à notre lettre d'information</h2>
                        <p class="fr-text--sm">Description de la newsletter</p>
                    </div>
                    <div>
                        <button class="fr-btn" type="button" title="S'abonner à notre lettre d'information">S'abonner</button>
                    </div>
                </div>
            </div>
            <div class="fr-col-12 fr-col-md-4">
                <div class="fr-follow__social">
                    <h2 class="fr-h5">Suivez-nous sur les réseaux sociaux</h2>
                    <ul class="fr-btns-group">
                        <li>
                            <a class="fr-btn--facebook fr-btn" href="/" target="_blank" rel="noopener external" title="Suivez-nous sur Facebook - nouvelle fenêtre">Facebook</a>
                        </li>
                        <li>
                            <a class="fr-btn--twitter-x fr-btn" href="/" target="_blank" rel="noopener external" title="Suivez-nous sur X (anciennement Twitter) - nouvelle fenêtre">X (anciennement Twitter)</a>
                        </li>
                        <li>
                            <a class="fr-btn--linkedin fr-btn" href="/" target="_blank" rel="noopener external" title="Suivez-nous sur LinkedIn - nouvelle fenêtre">LinkedIn</a>
                        </li>
                        <li>
                            <a class="fr-btn--instagram fr-btn" href="/" target="_blank" rel="noopener external" title="Suivez-nous sur Instagram - nouvelle fenêtre">Instagram</a>
                        </li>
                    </ul>
                </div>
            </div>
        </div>
    </div>
</div>
```

**Règles** :
- Le bloc d'abonnement du paquet officiel 1.15.2 ne contient pas de formulaire :
  le bouton « S'abonner » ouvre le parcours d'abonnement du projet. Avec
  `newsletter_url`, `generate_component.py follow` rend à sa place un
  `<a class="fr-btn" href="…" title="S'abonner à notre lettre d'information">`
- `title` sur chaque lien social (le texte visible est masqué par l'icône), et
  mention « - nouvelle fenêtre » puisque le lien ouvre un nouvel onglet
- Placer avant le footer, en pleine largeur
