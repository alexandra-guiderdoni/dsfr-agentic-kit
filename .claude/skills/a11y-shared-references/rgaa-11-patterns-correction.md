# RGAA 4.1.2 - Thématique 11 - Patterns de correction des formulaires

**Statut** : référence partagée de remédiation. **Portée** : ce fichier dit quoi écrire pour corriger ; `rgaa-11-formulaires.md` dit quoi collecter pour auditer. **Limite** : appliquer un pattern ne produit pas un verdict de conformité ; le test RGAA correspondant doit être rejoué et, lorsqu’il l’exige, validé par un humain.

Consultée par : `fix-accessibilite`, `a11y-loop`, `ticket-rgaa`, `pre-audit-rgaa-dsfr`.

Source éditoriale : référence HTML Living Standard et documentation RGAA
fournie par l'hôte ; aucun chemin de projet local n'est requis.

## Niveaux de confiance

Chaque pattern porte un niveau. Il conditionne le droit de l’appliquer sans décision humaine.

- **Haute** : l’information nécessaire est déjà présente dans le markup ; la correction peut être appliquée automatiquement et journalisée.
- **Moyenne** : la correction demande une information que le markup ne porte pas toujours (finalité d’un champ, texte d’erreur métier, caractère obligatoire). Appliquer seulement si cette information est disponible et vérifiée, sinon proposer.
- **Basse** : proposition seulement. La correction repose sur un jugement — regroupement logique, état de validation, pertinence d’un intitulé. Ne jamais l’appliquer automatiquement.

## 11.1 et 11.2 - Étiquette associée au champ

**Confiance** : haute quand un texte d’étiquette visible existe déjà et qu’il suffit de l’associer. Basse quand l’étiquette doit être formulée : rédiger un intitulé pertinent relève du critère `11.2`, donc de l’humain.

Incorrect, l’étiquette est visuelle mais pas associée :

```html
<p>Email</p>
<input type="email" name="email">
```

Correct, association explicite par `for` et `id` :

```html
<label for="email">Email</label>
<input type="email" id="email" name="email">
```

**Ce que ça change** : l’étiquette entre dans le nom accessible du champ. Sans association, le champ peut être restitué sans son intitulé selon les mécanismes d’étiquetage présents, et la personne qui navigue au clavier ne sait pas ce qu’elle remplit.

**Vérification** : sonde de nom accessible (`accessible-name-probe.md`), tests `11.1.1` à `11.1.3`.

**Ne pas faire** : remplacer par `aria-label` alors qu’un texte visible existe. Le nom accessible et le texte visible divergeraient. `aria-label` et `aria-labelledby` restent réservés aux champs sans étiquette visible, et doivent alors reprendre au moins le texte affiché à proximité.

## 11.5 et 11.6 - Regroupement de champs et légende

**Confiance** : basse. Décider que des champs sont de même nature, et que leur contexte commun n’est pas compréhensible par les seules étiquettes, est un jugement — `11.5` est d’ailleurs conditionné par « si nécessaire ». Proposer, ne pas appliquer.

Sans groupement, le contexte est porté par un paragraphe voisin :

```html
<p>Quel délai vous convient ?</p>
<label><input type="radio" name="delai" value="semaine"> Cette semaine</label>
<label><input type="radio" name="delai" value="mois"> Ce mois</label>
```

Avec groupement exposé programmatiquement :

```html
<fieldset>
  <legend>Quel délai vous convient ?</legend>
  <label><input type="radio" name="delai" value="semaine"> Cette semaine</label>
  <label><input type="radio" name="delai" value="mois"> Ce mois</label>
</fieldset>
```

**Ce que ça change** : la légende est restituée avec les champs du groupe. Sans regroupement exposé, chaque champ est annoncé isolément et le contexte commun se perd.

**Vérification** : tests `11.5.1` et `11.6.1`. La pertinence de la légende relève de `11.7` et reste humaine.

**Ne pas faire** : envelopper mécaniquement tout ensemble de cases à cocher ou de boutons radio dans un `fieldset`. Un regroupement inutile ajoute du bruit de restitution sans rien prouver.

## 11.10 et 11.11 - Erreurs de saisie et suggestions de correction

**Confiance** : basse pour `aria-invalid`, moyenne pour `aria-describedby` et le texte du message.

`aria-invalid` décrit un état de validation à un instant donné, pas une propriété du markup. Le poser en dur dans une source statique produit un champ annoncé en erreur avant toute saisie. Il se pose au moment où la validation échoue, et se retire quand elle passe.

```html
<label for="email">Email</label>
<input
  type="email"
  id="email"
  name="email"
  aria-invalid="true"
  aria-describedby="email-error"
  value="jean.dupont"
>

<p id="email-error">
  Le format de l’adresse email n’est pas valide.
  Exemple : jean.dupont@domaine.fr
</p>
```

**Ce que ça change** : l’état d’erreur est exposé aux technologies d’assistance, et le message rejoint la description accessible du champ au lieu de flotter à côté.

Le message doit décrire le problème plutôt que le signaler — « Le format de l’adresse email n’est pas valide » et non « Champ invalide » — et proposer une correction lorsqu’elle est connue, ce qui est l’objet du critère `11.11`. Après soumission, un résumé d’erreurs recevant le focus est une solution possible pour retrouver les champs concernés.

**Vérification** : tests `11.10.1` à `11.10.7` pour l’identification, `11.11.1` et `11.11.2` pour la suggestion.

**Ne pas faire** : poser `aria-invalid="true"` en dur dans un gabarit ; appliquer `role="alert"` à un message déjà présent au chargement. `role="alert"` et les régions `aria-live` servent à faire annoncer un message ajouté ou modifié dynamiquement, au moment où il survient.

## 11.13 - Finalité du champ et attribut autocomplete

**Confiance** : moyenne. Il faut connaître la finalité réelle du champ, et le critère ne couvre pas tous les champs de saisie.

`11.13` ne vise que les champs qui collectent des informations sur la personne qui remplit le formulaire, et dont la finalité figure parmi les finalités couvertes. Un champ de recherche, un libellé d’objet, une adresse de destination qui n’est pas celle de l’utilisateur ne sont pas concernés.

```html
<input type="text" name="given-name" autocomplete="given-name">
<input type="text" name="family-name" autocomplete="family-name">
<input type="email" name="email" autocomplete="email">
<input type="tel" name="phone" autocomplete="tel">
<input type="text" name="street" autocomplete="street-address">
<input type="text" name="postal-code" autocomplete="postal-code">
```

**Ce que ça change** : le champ expose programmatiquement sa finalité, ce dont bénéficient le remplissage automatique et les personnes que la saisie coûte — troubles moteurs, dyslexie, fatigue mnésique.

**Vérification** : test `11.13.1`. La liste des valeurs autorisées fait foi : section *Autofill* du HTML Living Standard, WHATWG.

**Ne pas faire** : ajouter `autocomplete` sur tous les champs par réflexe ; inventer une valeur hors liste. Une valeur non reconnue n’expose aucune finalité et ne satisfait donc pas le critère.

## 11.1 et 11.10 - Champs obligatoires

**Confiance** : moyenne. Savoir quels champs sont réellement obligatoires est une information métier que le markup ne porte pas toujours.

```html
<p>Les champs marqués d’un * sont obligatoires.</p>

<label for="nom">Nom *</label>
<input type="text" id="nom" name="nom" required>

<label for="prenom">Prénom</label>
<input type="text" id="prenom" name="prenom">
```

**Ce que ça change** : la distinction entre champs obligatoires et facultatifs devient perceptible et exposée programmatiquement par `required`.

**Ne pas faire** : signaler l’obligation par la seule couleur ; poser un astérisque sans l’expliciter en début de formulaire ; ajouter `required` sans indication visible correspondante — l’attribut seul ne rend pas la distinction perceptible.

## Ce que ces patterns ne prouvent pas

- Appliquer un pattern ne rend pas le test RGAA conforme. Le test doit être rejoué, et validé par un humain quand il l’exige.
- Cinq critères de la thématique ne sont couverts par aucun pattern ici : `11.3` cohérence des étiquettes répétées, `11.4` étiquette accolée à son champ, `11.8` regroupement des items d’une liste de choix, `11.9` intitulé de bouton, `11.12` formulaires modifiant ou supprimant des données. Voir `rgaa-11-formulaires.md`.
- L’absence de violation détectée après correction n’est pas une preuve de conformité.

## Sources

- `rgaa-11-formulaires.md` — contrats de preuve, critères et tests de la thématique.
- `correction-patterns.md` — patterns transverses et chaîne de vérification.
- RGAA 4.1.2, DINUM. WCAG 2.2, W3C. HTML Living Standard section *Autofill*, WHATWG.
- Correspondances WCAG citées par la source éditoriale : `1.3.1` et `3.3.2` pour l’étiquetage, `3.3.1` et `3.3.3` pour les erreurs, `1.3.5` pour la finalité des champs.
