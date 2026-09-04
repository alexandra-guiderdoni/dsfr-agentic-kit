# TICKET-CANDIDAT-RGAA-7.5.2 — Message d’erreur dynamique insuffisamment exposé

- **Page :** P06 — https://moa.douane.gouv.fr/formulaire-infos-douane-service
- **Critère / test :** RGAA 4.1.2 — 7.5 / 7.5.2
- **Statut :** NON_CONFORME_ETAYE dans le complément ; décision publiée à requalifier
- **Décision publiée :** NA_CONFIRMEE
- **Sévérité proposée :** Majeur

## Observation

Le message dynamique d’extension interdite est une erreur/suggestion. Le conteneur observé porte aria-live="polite", sans role et sans aria-atomic. Il ne satisfait donc ni role="alert", ni l’équivalent aria-live="assertive" avec aria-atomic="true".

Message observé :

> Le fichier sélectionné preuve-synthetique-interdite.exe ne peut pas être transféré. Seuls les fichiers avec les extensions suivantes sont autorisés : jpg, jpeg, png, pdf.

Le même type de divergence est présent dans la preuve serveur archivée : conteneur d’erreur avec `aria-live="polite"`, sans `role="alert"` et sans `aria-atomic="true"`, alors que la matrice publiée indique qu’aucun message de statut n’a été produit.

## Impact

Le message peut ne pas être restitué avec la priorité et l’intégrité attendues lorsque le focus reste ailleurs. Une personne utilisant un lecteur d’écran peut ne pas percevoir immédiatement l’erreur ni la correction proposée.

## Correction attendue

Pour un message d’erreur ou une suggestion dynamique, utiliser l’une des solutions RGAA compatibles :

```html
<div class="fr-alert fr-alert--error" role="alert">
  <p>…message d’erreur précis…</p>
</div>
```

ou, si les attributs sont explicités :

```html
<div aria-live="assertive" aria-atomic="true">
  <p>…message d’erreur précis…</p>
</div>
```

La région doit exister avant l’injection si le composant ou la pile de technologies d’assistance l’exige. Éviter les annonces concurrentes ou dupliquées.

## Vérification après correction

1. Déclencher une extension interdite sans soumettre le formulaire final.
2. Vérifier le rôle ou le couple `aria-live` / `aria-atomic` dans le DOM rendu.
3. Vérifier que le message reste visible, précis et associé au champ fichier.
4. Contrôler l’annonce avec NVDA + Firefox et VoiceOver + Safari.
5. Rejouer le retour serveur de cinq fichiers en environnement de recette isolé.

## Preuves

- [JSON du retest sûr](preuves/P06-RETEST-SAFE.json)
- [Capture extension interdite](preuves/runs/20260903T221344281418Z-42c57784/P06-04-extension-interdite-validation-client-sans-requete.png)
- [Copie intègre de l’état serveur archivé](preuves/P06-ETAT-SERVEUR-ARCHIVE.json)
