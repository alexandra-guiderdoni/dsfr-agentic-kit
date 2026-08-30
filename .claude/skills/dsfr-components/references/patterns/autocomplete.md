# Récapitulatif des valeurs autocomplete

Référence extraite de `../patterns.md`.

---

| Champ | Valeur autocomplete | Critère WCAG |
|-------|-------------------|-------------|
| Prénom | `given-name` | 1.3.5 |
| Nom | `family-name` | 1.3.5 |
| Civilité | `honorific-prefix` (conditionnel, voir la note) | 1.3.5 |
| Date naissance (jour) | `bday-day` | 1.3.5 |
| Date naissance (mois) | `bday-month` | 1.3.5 |
| Date naissance (année) | `bday-year` | 1.3.5 |
| Téléphone | `tel` | 1.3.5 |
| Indicatif pays | `tel-country-code` | 1.3.5 |
| Adresse | `street-address` | 1.3.5 |
| Complément | `address-line2` | 1.3.5 |
| Code postal | `postal-code` | 1.3.5 |
| Ville | `address-level2` | 1.3.5 |
| Email | `email` | 1.3.5 |
| Mot de passe | `current-password` / `new-password` | 1.3.5 |

Ce tableau récapitule la valeur `autocomplete` attendue **par champ**, il ne
prescrit pas d'attribut sur un contrôle où le jeton n'a pas de sens.
`honorific-prefix` est un jeton d'autofill textuel : il s'applique à un champ
texte ou à une liste de civilité, pas à un groupe de `<input type="radio">`.
Le bloc `generate_field.py civilite` et l'exemple officiel
`example/layout/pattern/civility` du paquet 1.15.2 n'en posent aucun ;
`patterns/civilite.md` le donne comme facultatif (« peut être ajouté sur une
civilité si pertinent »).
