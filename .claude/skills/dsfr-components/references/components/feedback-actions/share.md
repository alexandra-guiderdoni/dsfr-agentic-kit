# Partage (Share)

Référence extraite de `../feedback-actions.md`.

---

## Boutons de partage
```html
<div class="fr-share">
    <p class="fr-share__title">Partager la page</p>
    <ul class="fr-share__group">
        <li>
            <a class="fr-share__link fr-share__link--facebook" title="Partager sur Facebook - nouvelle fenêtre" href="https://www.facebook.com/sharer/sharer.php?u=[URL]" target="_blank" rel="noopener">
                Partager sur Facebook
            </a>
        </li>
        <li>
            <a class="fr-share__link fr-share__link--twitter-x" title="Partager sur X (anciennement Twitter) - nouvelle fenêtre" href="https://x.com/intent/tweet?url=[URL]" target="_blank" rel="noopener">
                Partager sur X (anciennement Twitter)
            </a>
        </li>
        <li>
            <a class="fr-share__link fr-share__link--linkedin" title="Partager sur LinkedIn - nouvelle fenêtre" href="https://www.linkedin.com/shareArticle?url=[URL]" target="_blank" rel="noopener">
                Partager sur LinkedIn
            </a>
        </li>
        <li>
            <a class="fr-share__link fr-share__link--mail" title="Partager par email" href="mailto:?subject=[TITRE]&body=[URL]">
                Partager par email
            </a>
        </li>
        <li>
            <button class="fr-share__link fr-share__link--copy" type="button" title="Copier dans le presse-papier">
                Copier dans le presse-papier
            </button>
        </li>
    </ul>
</div>
```

**Règles** :
- Les liens de partage utilisent `fr-share__link` et son modificateur de
  plateforme, jamais `fr-btn` : le CSS du composant ne stylise que
  `fr-share__link`
- Modificateurs disponibles : `--facebook`, `--twitter`, `--twitter-x`,
  `--linkedin`, `--mail`, `--bluesky`, `--mastodon`, `--threads`, `--copy`
- Chaque lien ouvert en `target="_blank"` porte `rel="noopener"` et un `title`
  suffixé par « - nouvelle fenêtre »

---
