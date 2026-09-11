# Adresse (BAN)

Référence extraite de `../patterns.md`.

---

## Pattern recommandé (avec autocomplétion BAN)
```html
<fieldset class="fr-fieldset" aria-labelledby="adresse-legend">
    <legend class="fr-fieldset__legend" id="adresse-legend">Adresse</legend>
    <div class="fr-fieldset__element">
        <div class="fr-input-group">
            <label class="fr-label" for="adresse-recherche">
                Rechercher votre adresse
                    <span class="fr-hint-text">Saisissez votre adresse, elle sera complétée automatiquement</span>
            </label>
            <input class="fr-input" type="text" id="adresse-recherche" name="adresse-recherche"
                   autocomplete="street-address" aria-describedby="adresse-recherche-hint">
            <p class="fr-hint-text" id="adresse-recherche-hint">
                Source : Base Adresse Nationale (BAN)
            </p>
        </div>
    </div>
    <div class="fr-fieldset__element">
        <div class="fr-input-group">
            <label class="fr-label" for="adresse-complement">
                    Complément d'adresse
                    <span class="fr-hint-text">Bâtiment, étage, appartement, lieu-dit</span>
            </label>
            <input class="fr-input" type="text" id="adresse-complement" name="adresse-complement"
                   autocomplete="address-line2">
        </div>
    </div>
    <div class="fr-fieldset__element fr-fieldset__element--inline">
        <div class="fr-input-group">
            <label class="fr-label" for="code-postal">Code postal</label>
            <input class="fr-input" type="text" id="code-postal" name="code-postal"
                   autocomplete="postal-code" inputmode="numeric" maxlength="5">
        </div>
    </div>
    <div class="fr-fieldset__element fr-fieldset__element--inline">
        <div class="fr-input-group">
            <label class="fr-label" for="ville">Ville</label>
            <input class="fr-input" type="text" id="ville" name="ville"
                   autocomplete="address-level2">
        </div>
    </div>
</fieldset>
```

## Règles
- Proposer un champ de recherche avec autocomplétion BAN (api-adresse.data.gouv.fr).
  Le DSFR 1.15.3 ne fournit aucun attribut `data-fr-*` ni script pour cela :
  l'autocomplétion est à brancher par le projet (voir l'exemple ci-dessous).
- Toujours laisser la saisie manuelle possible (fallback si l'API est indisponible)
- `autocomplete` : `street-address`, `address-line2`, `postal-code`, `address-level2` (WCAG 1.3.5)
- Code postal : `inputmode="numeric"`, `maxlength="5"` ; différer le
  `pattern="[0-9]{5}"` jusqu'au premier `submit` si une validation client est
  nécessaire
- Complément d'adresse : toujours optionnel
- Largeur du code postal : le DSFR 1.15.3 ne fournit pas d'utilitaire
  `fr-input--w*` ; dimensionner via la grille (`fr-col-*`) ou du CSS projet
  vérifié (`max-width`), et garder `maxlength="5"`.

## Intégration API BAN (JavaScript)

Quatre garde-fous, tous nécessaires sur un service public : garde sur l'élément
absent, anti-rebond, annulation de la requête précédente, et erreurs rattrapées
avec repli sur la saisie manuelle.

```javascript
// Autocomplétion via api-adresse.data.gouv.fr
const input = document.getElementById('adresse-recherche');
// Garde : l'identifiant peut avoir été renommé par l'intégrateur ; sans elle,
// la ligne suivante lève une TypeError qui interrompt le script de la page.
if (input) {
  let timer = null;
  let controller = null;

  input.addEventListener('input', (e) => {
    const query = e.target.value.trim();
    window.clearTimeout(timer);
    if (query.length < 3) return;
    // Anti-rebond : sans lui, une frappe rapide déclenche un appel par caractère.
    timer = window.setTimeout(async () => {
      // La requête précédente devient inutile dès qu'une nouvelle part.
      if (controller) controller.abort();
      controller = new AbortController();
      try {
        const response = await fetch(
          `https://api-adresse.data.gouv.fr/search/?q=${encodeURIComponent(query)}&limit=5`,
          { signal: controller.signal }
        );
        // Sans ce test, une réponse 429 ou 500 casse le parsage JSON.
        if (!response.ok) return;
        const data = await response.json();
        // Afficher les suggestions dans un datalist ou une liste personnalisée
      } catch (error) {
        // Service indisponible ou requête annulée : aucune suggestion, la
        // saisie manuelle reste possible (règle ci-dessus).
        if (error.name !== 'AbortError') {
          // Journaliser côté projet si nécessaire ; ne jamais bloquer la saisie.
        }
      }
    }, 300);
  });
}
```
