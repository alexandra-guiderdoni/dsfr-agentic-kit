---
title: "DSFR - formulaires et modèles"
scope: formulaires, blocs fonctionnels, pages types
load_when: "Le livrable contient un formulaire, une connexion, une création de compte ou une page d'erreur."
---

# DSFR - formulaires et modèles

Les formulaires administratifs doivent être sobres, groupés, explicites et compatibles avec l'autocomplétion.

## Formulaires

- Utiliser `fieldset` et `legend` pour les groupes : identité, adresse, contact, choix exclusifs.
- Dans le modèle DSFR, les champs sont obligatoires par défaut.
- Signaler les champs optionnels par la mention `(optionnel)` dans le label.
- Ajouter une mention en début de formulaire : sauf mention contraire, tous les champs sont obligatoires.
- Placer prénom avant nom.
- Ne demander la civilité que si elle est nécessaire au traitement.
- Utiliser des boutons radio pour un choix court et exclusif, pas une liste déroulante.
- Utiliser `inputmode` plutôt que `type="number"` pour les nombres qui ne sont pas des quantités.
- Ajouter `autocomplete` WCAG 1.3.5 pour les données personnelles.
- Relier les erreurs aux champs concernés.
- Ne pas signaler erreur ou succès seulement par la couleur.

Si le modèle exact n'est pas lu, produire une structure sobre et marquer `modèle formulaire à vérifier`.

## Blocs fonctionnels à chercher

- adresse électronique ;
- civilité ;
- date unique ;
- formulaires ;
- nom et prénom ;
- numéro de téléphone ;
- société.

## Pages types

- page d'erreur ;
- page de connexion ;
- page de création de compte.

Si une page type existe, partir de celle-ci ou justifier l'écart.

## Matrice d'intention

| Intention | Source DSFR à chercher d'abord | Repli si source non lue |
|---|---|---|
| connexion | page type connexion | formulaire simple + alerte d'erreur globale à vérifier |
| création de compte | page type création de compte | demander seulement les champs nécessaires |
| erreur de navigation | page type erreurs | message clair, retour accueil ou action de secours |
| adresse électronique | bloc adresse électronique | champ email sémantique, aide et autocomplete |
| identité | blocs nom, prénom, civilité | fieldset, labels explicites, civilité seulement si nécessaire |
| téléphone | bloc numéro de téléphone | input texte avec `inputmode`, aide de format |

## Règles de sobriété

- Connexion : ne demander une connexion que si l'espace privé ou personnel le justifie.
- Création de compte : permettre l'accès aux contenus ou services sans connexion quand c'est possible.
- Erreurs 404, 500, 503 : partir des modèles et adapter le contenu au contexte.
- Formulaire long : chercher les blocs fonctionnels avant de composer un séquençage libre.
- Contenu administratif : ne pas inventer lois, délais, droits, obligations, montants ou démarches.
