# Ticket candidat RGAA 11.10.2 — Indication des champs obligatoires

- **Page :** P06 — Formulaire Écrivez-nous
- **Test :** [RGAA 4.1.2 — 11.10.2](https://accessibilite.numerique.gouv.fr/methode/criteres-et-tests/#11.10.2)
- **Décision publiée :** `C_CONFIRMEE`
- **Conclusion étayée :** `NON_CONFORME_ETAYE`
- **État :** décision publiée à requalifier

## Observation

9 champs portant required ne présentent aucune indication de caractère obligatoire dans leur étiquette, aria-labelledby ou aria-describedby. L’instruction générale n’est associée à aucun de ces champs.

Champs relevés : `#edit-question-type`, `#edit-candidate-gender`, `#edit-nom`, `#edit-prenom`, `#edit-pays`, `#edit-codepostal`, `#edit-adressemail`, `#edit-question`, `#edit-accept-conditions`.

## Impact

L’utilisateur doit mémoriser l’instruction globale puis déduire le statut de chaque champ ; aucune indication associée champ par champ ne satisfait le test 11.10.2.

## Correction attendue

Placer une indication visible dans chaque étiquette concernée, par exemple :

```html
<label for="edit-nom">Nom <span>(obligatoire)</span></label>
```

Une autre solution est un passage de texte visible associé au champ avec `aria-labelledby` ou `aria-describedby`. Ne pas se limiter à l’attribut `required`, qui répond au test 11.10.1 mais pas à 11.10.2.

## Vérification après correction

1. Inventorier chaque champ portant `required` ou `aria-required="true"` dans tous les états du formulaire.
2. Vérifier que l’indication est visible dans l’étiquette ou un passage de texte associé.
3. Vérifier l’association programmatiquement et à différents points de rupture.
4. Rejouer le contrôle avant toute soumission serveur.

## Preuves

- [JSON du retest sûr](preuves/P06-RETEST-SAFE.json)
- [Capture du formulaire](preuves/runs/20260903T221344281418Z-42c57784/P06-01-soumission-vide-native.png)
