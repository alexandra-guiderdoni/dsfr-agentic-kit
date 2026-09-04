# P06 — Complément de couverture RGAA « Formulaires »

**Page :** [Formulaire Écrivez-nous](https://moa.douane.gouv.fr/formulaire-infos-douane-service)  
**Référentiel :** RGAA 4.1.2 — thème 11, 34 tests  
**Mode :** retest instrumenté sûr, données synthétiques, aucune requête mutante transmise  
**Prêt à transmettre comme audit final :** **non**

## Conclusion

La matrice publiée contient bien les 34 tests, mais elle ne prouve pas les 19 conformités annoncées. Après relecture probatoire et complément Playwright :

- 3 tests sont techniquement étayés comme conformes, sans validation humaine finale signée ;
- 3 tests du thème 11 disposent d’une non-conformité étayée ;
- 5 tests sont non applicables conditionnellement dans le DOM observé ;
- 17 tests restent à qualifier humainement ;
- 2 non-applicabilités restent à confirmer par la MOA métier ;
- 4 tests exigent encore une réponse serveur réelle.

Le test **11.10.2**, publié conforme, est requalifié non conforme : les indications obligatoires ne figurent ni dans les étiquettes ni dans des passages associés. Un défaut adjacent est aussi confirmé pour **RGAA 7.5.2** : les messages d’erreur dynamiques observés n’utilisent ni `role="alert"`, ni `aria-live="assertive"` avec `aria-atomic="true"`.

## Garantie de non-soumission

- Méthodes autorisées : `GET`, `HEAD`, `OPTIONS`.
- Toute autre méthode est bloquée avant envoi.
- Toute connexion WebSocket est fermée avant les messages applicatifs.
- 1 tentative AJAX `POST` a été interceptée lors du scénario « cinq fichiers ».
- Une erreur `Drupal.AjaxError` a été observée dans la même fenêtre d’action ; `pageerror` ne permet pas d’en prouver la causalité avec la garde.
- Aucun formulaire valide ni fichier n’a été transmis au serveur.

## Résultats du retest sûr

### Étiquettes répétées sur P01 à P09

- `input|search|query` — P01, P02, P03, P04, P05, P06, P07, P08, P09 — intitulé(s) : nom accessible 'Rechercher'; libellé DOM 'Rechercher'; visible dans tous les états : **non** — correspondance DOM exacte, conformité RGAA à confirmer.
- `input|radio|fr-radios-theme-light` — P01, P02, P03, P04, P05, P06, P07, P08, P09 — intitulé(s) : nom accessible 'Thème clair'; libellé DOM 'Thème clair'; visible dans tous les états : **non** — correspondance DOM exacte, conformité RGAA à confirmer.
- `input|radio|fr-radios-theme-dark` — P01, P02, P03, P04, P05, P06, P07, P08, P09 — intitulé(s) : nom accessible 'Thème sombre'; libellé DOM 'Thème sombre'; visible dans tous les états : **non** — correspondance DOM exacte, conformité RGAA à confirmer.
- `input|radio|fr-radios-theme-system` — P01, P02, P03, P04, P05, P06, P07, P08, P09 — intitulé(s) : nom accessible 'Système Utilise les paramètres système'; libellé DOM 'Système Utilise les paramètres système'; visible dans tous les états : **non** — correspondance DOM exacte, conformité RGAA à confirmer.

### États dynamiques

- Soumission native vide : focus déplacé sur `#edit-nom` ; aucune requête mutante.
- Email invalide : focus déplacé sur `#edit-adressemail` ; message natif du navigateur et exemple visible `nom@domaine.fr`.
- Variante professionnel : Société visible, facultatif techniquement, sans mention « optionnel » et sans `autocomplete="organization"`.
- Extension `.exe` : message français visible donnant les extensions autorisées, produit sans requête mutante.
- Cinq fichiers autorisés par extension : tentative AJAX bloquée ; le véritable message serveur n’est donc pas disponible.
- Le champ fichier conserve un `aria-describedby` vers `#edit-document--description`, cible absente dans les deux états testés.

## Requalification RGAA 11.10.2

**Décision publiée :** `C_CONFIRMEE`  
**Complément :** **NON_CONFORME_ETAYE**

9 champs portant required ne présentent aucune indication de caractère obligatoire dans leur étiquette, aria-labelledby ou aria-describedby. L’instruction générale n’est associée à aucun de ces champs.

Voir le ticket candidat : [TICKET-CANDIDAT-RGAA-11.10.2.md](TICKET-CANDIDAT-RGAA-11.10.2.md).

## Requalification RGAA 7.5.2

**Décision publiée :** `NA_CONFIRMEE`  
**Complément :** **NON_CONFORME_ETAYE**

Le message dynamique d’extension interdite est une erreur/suggestion. Le conteneur observé porte aria-live="polite", sans role et sans aria-atomic. Il ne satisfait donc ni role="alert", ni l’équivalent aria-live="assertive" avec aria-atomic="true".

Message observé : « Le fichier sélectionné preuve-synthetique-interdite.exe ne peut pas être transféré. Seuls les fichiers avec les extensions suivantes sont autorisés : jpg, jpeg, png, pdf. »

Voir le ticket candidat : [TICKET-CANDIDAT-RGAA-7.5.2.md](TICKET-CANDIDAT-RGAA-7.5.2.md).

## Matrice probatoire des 34 tests

| Critère | Test | Décision publiée | Base probatoire | Conclusion du complément | Justification |
|---|---|---|---|---|---|
| 11.1 | [11.1.1](https://accessibilite.numerique.gouv.fr/methode/criteres-et-tests/#11.1.1) | `C_CONFIRMEE` | `A_RETESTER` | **À qualifier humainement** | Le relevé conserve les mécanismes d’étiquette et un candidat calculé, mais il ne constitue pas une implémentation normative d’AccName : qualification humaine maintenue. |
| 11.1 | [11.1.2](https://accessibilite.numerique.gouv.fr/methode/criteres-et-tests/#11.1.2) | `C_CONFIRMEE` | `TESTE_CONFORME` | **Conforme technique étayée — validation humaine requise** | Les preuves comportent un contrôle technique ciblé, mais la validation humaine requise par le contrat de preuve n’est pas signée dans le registre de revue. |
| 11.1 | [11.1.3](https://accessibilite.numerique.gouv.fr/methode/criteres-et-tests/#11.1.3) | `C_CONFIRMEE` | `A_RETESTER` | **À qualifier humainement** | La variante « Un professionnel » montre Société et son étiquette ensemble, mais la visibilité et la proximité de tous les champs, notamment la recherche masquée, n’ont pas été qualifiées exhaustivement : revue humaine maintenue. |
| 11.2 | [11.2.1](https://accessibilite.numerique.gouv.fr/methode/criteres-et-tests/#11.2.1) | `C_CONFIRMEE` | `NON_TESTE` | **À qualifier humainement** | La pertinence, l’applicabilité ou le rendu nécessite encore une revue humaine ciblée ; les collecteurs automatiques ne produisent pas cette décision. |
| 11.2 | [11.2.2](https://accessibilite.numerique.gouv.fr/methode/criteres-et-tests/#11.2.2) | `NA_CONFIRMEE` | `NON_APPLICABLE_CONDITIONNEL_DOM` | **Non applicable conditionnel — DOM observé** | Le DOM observé ne contient aucune cible correspondant au mécanisme testé. Cette non-applicabilité reste conditionnelle aux états capturés et à la qualification sémantique du critère parent. |
| 11.2 | [11.2.3](https://accessibilite.numerique.gouv.fr/methode/criteres-et-tests/#11.2.3) | `NA_CONFIRMEE` | `NON_APPLICABLE_CONDITIONNEL_DOM` | **Non applicable conditionnel — DOM observé** | Le DOM observé ne contient aucune cible correspondant au mécanisme testé. Cette non-applicabilité reste conditionnelle aux états capturés et à la qualification sémantique du critère parent. |
| 11.2 | [11.2.4](https://accessibilite.numerique.gouv.fr/methode/criteres-et-tests/#11.2.4) | `NA_CONFIRMEE` | `NON_APPLICABLE_CONDITIONNEL_DOM` | **Non applicable conditionnel — DOM observé** | Le DOM observé ne contient aucune cible correspondant au mécanisme testé. Cette non-applicabilité reste conditionnelle aux états capturés et à la qualification sémantique du critère parent. |
| 11.2 | [11.2.5](https://accessibilite.numerique.gouv.fr/methode/criteres-et-tests/#11.2.5) | `C_CONFIRMEE` | `NON_TESTE` | **À qualifier humainement** | La pertinence, l’applicabilité ou le rendu nécessite encore une revue humaine ciblée ; les collecteurs automatiques ne produisent pas cette décision. |
| 11.2 | [11.2.6](https://accessibilite.numerique.gouv.fr/methode/criteres-et-tests/#11.2.6) | `C_CONFIRMEE` | `NON_TESTE` | **À qualifier humainement** | La pertinence, l’applicabilité ou le rendu nécessite encore une revue humaine ciblée ; les collecteurs automatiques ne produisent pas cette décision. |
| 11.3 | [11.3.1](https://accessibilite.numerique.gouv.fr/methode/criteres-et-tests/#11.3.1) | `C_CONFIRMEE` | `NON_TESTE` | **À qualifier humainement** | La pertinence, l’applicabilité ou le rendu nécessite encore une revue humaine ciblée ; les collecteurs automatiques ne produisent pas cette décision. |
| 11.3 | [11.3.2](https://accessibilite.numerique.gouv.fr/methode/criteres-et-tests/#11.3.2) | `A_RETESTER` | `A_RETESTER` | **À qualifier humainement** | Les quatre contrôles explicitement cartographiés sur P01 à P09 — recherche et trois choix de thème — conservent le même texte de label et candidat de nom ; la visibilité effective et la qualification « même fonction » restent humaines. |
| 11.4 | [11.4.1](https://accessibilite.numerique.gouv.fr/methode/criteres-et-tests/#11.4.1) | `C_CONFIRMEE` | `A_RETESTER` | **À qualifier humainement** | La pertinence, l’applicabilité ou le rendu nécessite encore une revue humaine ciblée ; les collecteurs automatiques ne produisent pas cette décision. |
| 11.4 | [11.4.2](https://accessibilite.numerique.gouv.fr/methode/criteres-et-tests/#11.4.2) | `C_CONFIRMEE` | `A_RETESTER` | **À qualifier humainement** | La pertinence, l’applicabilité ou le rendu nécessite encore une revue humaine ciblée ; les collecteurs automatiques ne produisent pas cette décision. |
| 11.4 | [11.4.3](https://accessibilite.numerique.gouv.fr/methode/criteres-et-tests/#11.4.3) | `C_CONFIRMEE` | `A_RETESTER` | **À qualifier humainement** | La pertinence, l’applicabilité ou le rendu nécessite encore une revue humaine ciblée ; les collecteurs automatiques ne produisent pas cette décision. |
| 11.5 | [11.5.1](https://accessibilite.numerique.gouv.fr/methode/criteres-et-tests/#11.5.1) | `C_CONFIRMEE` | `A_RETESTER` | **À qualifier humainement** | La pertinence, l’applicabilité ou le rendu nécessite encore une revue humaine ciblée ; les collecteurs automatiques ne produisent pas cette décision. |
| 11.6 | [11.6.1](https://accessibilite.numerique.gouv.fr/methode/criteres-et-tests/#11.6.1) | `C_CONFIRMEE` | `TESTE_CONFORME` | **Conforme technique étayée — validation humaine requise** | Les preuves comportent un contrôle technique ciblé, mais la validation humaine requise par le contrat de preuve n’est pas signée dans le registre de revue. |
| 11.7 | [11.7.1](https://accessibilite.numerique.gouv.fr/methode/criteres-et-tests/#11.7.1) | `C_CONFIRMEE` | `NON_TESTE` | **À qualifier humainement** | La pertinence, l’applicabilité ou le rendu nécessite encore une revue humaine ciblée ; les collecteurs automatiques ne produisent pas cette décision. |
| 11.8 | [11.8.1](https://accessibilite.numerique.gouv.fr/methode/criteres-et-tests/#11.8.1) | `NA_CONFIRMEE` | `NON_TESTE` | **À qualifier humainement** | La pertinence, l’applicabilité ou le rendu nécessite encore une revue humaine ciblée ; les collecteurs automatiques ne produisent pas cette décision. |
| 11.8 | [11.8.2](https://accessibilite.numerique.gouv.fr/methode/criteres-et-tests/#11.8.2) | `NA_CONFIRMEE` | `NON_APPLICABLE_CONDITIONNEL_DOM` | **Non applicable conditionnel — DOM observé** | Le DOM observé ne contient aucune cible correspondant au mécanisme testé. Cette non-applicabilité reste conditionnelle aux états capturés et à la qualification sémantique du critère parent. |
| 11.8 | [11.8.3](https://accessibilite.numerique.gouv.fr/methode/criteres-et-tests/#11.8.3) | `NA_CONFIRMEE` | `NON_APPLICABLE_CONDITIONNEL_DOM` | **Non applicable conditionnel — DOM observé** | Le DOM observé ne contient aucune cible correspondant au mécanisme testé. Cette non-applicabilité reste conditionnelle aux états capturés et à la qualification sémantique du critère parent. |
| 11.9 | [11.9.1](https://accessibilite.numerique.gouv.fr/methode/criteres-et-tests/#11.9.1) | `C_CONFIRMEE` | `A_RETESTER` | **À qualifier humainement** | La pertinence, l’applicabilité ou le rendu nécessite encore une revue humaine ciblée ; les collecteurs automatiques ne produisent pas cette décision. |
| 11.9 | [11.9.2](https://accessibilite.numerique.gouv.fr/methode/criteres-et-tests/#11.9.2) | `C_CONFIRMEE` | `A_RETESTER` | **À qualifier humainement** | La pertinence, l’applicabilité ou le rendu nécessite encore une revue humaine ciblée ; les collecteurs automatiques ne produisent pas cette décision. |
| 11.10 | [11.10.1](https://accessibilite.numerique.gouv.fr/methode/criteres-et-tests/#11.10.1) | `NC_CONFIRMEE` | `TESTE_NON_CONFORME` | **Non conforme étayé** | Le champ Société est facultatif mais aucune mention visible ne l’indique alors que l’instruction globale annonce tous les champs obligatoires sauf mention contraire. |
| 11.10 | [11.10.2](https://accessibilite.numerique.gouv.fr/methode/criteres-et-tests/#11.10.2) | `C_CONFIRMEE` | `TESTE_NON_CONFORME` | **Non conforme étayé** | Les champs portant required ne présentent pas l’indication de leur caractère obligatoire dans leur étiquette ou un passage de texte associé ; l’instruction globale non associée ne suffit pas. |
| 11.10 | [11.10.3](https://accessibilite.numerique.gouv.fr/methode/criteres-et-tests/#11.10.3) | `C_CONFIRMEE` | `A_RETESTER` | **À qualifier humainement** | Le premier état client utilise un message de validation natif générique sans aria-invalid ; sa capacité à identifier nommément le champ reste à qualifier humainement malgré un état serveur archivé plus riche. |
| 11.10 | [11.10.4](https://accessibilite.numerique.gouv.fr/methode/criteres-et-tests/#11.10.4) | `C_CONFIRMEE` | `TESTE_CONFORME` | **Conforme technique étayée — validation humaine requise** | Les preuves comportent un contrôle technique ciblé, mais la validation humaine requise par le contrat de preuve n’est pas signée dans le registre de revue. |
| 11.10 | [11.10.5](https://accessibilite.numerique.gouv.fr/methode/criteres-et-tests/#11.10.5) | `C_CONFIRMEE` | `A_RETESTER` | **À qualifier humainement** | Plusieurs champs portent maxlength=128 sans instruction associée. La nécessité et la formulation d’une indication de format/longueur restent à qualifier humainement. |
| 11.10 | [11.10.6](https://accessibilite.numerique.gouv.fr/methode/criteres-et-tests/#11.10.6) | `A_RETESTER` | `A_RETESTER` | **À retester côté serveur** | L’adresse électronique invalide et l’extension de fichier interdite ont produit des messages visibles. Le scénario de cinq fichiers déclenche une requête AJAX qui a été bloquée avant envoi : son véritable retour serveur reste inconnu. |
| 11.10 | [11.10.7](https://accessibilite.numerique.gouv.fr/methode/criteres-et-tests/#11.10.7) | `NA_CONFIRMEE` | `A_RETESTER` | **À retester côté serveur** | Les états natifs observés ne posent pas aria-invalid. Les états serveur archivés en posent, mais le retour réel du dépassement de quatre fichiers n’a pas été obtenu en mode sûr. L’ancien NA est donc remplacé par un retest serveur. |
| 11.11 | [11.11.1](https://accessibilite.numerique.gouv.fr/methode/criteres-et-tests/#11.11.1) | `A_RETESTER` | `A_RETESTER` | **À retester côté serveur** | Le message d’extension interdite donne les types autorisés et le navigateur indique le caractère @ manquant. La suggestion associée au dépassement de quatre fichiers reste inconnue sans réponse serveur. |
| 11.11 | [11.11.2](https://accessibilite.numerique.gouv.fr/methode/criteres-et-tests/#11.11.2) | `A_RETESTER` | `A_RETESTER` | **À retester côté serveur** | L’exemple nom@domaine.fr est visible pour l’email. La nécessité et le contenu d’un exemple dans le retour « cinq fichiers » restent à qualifier après réponse serveur. |
| 11.12 | [11.12.1](https://accessibilite.numerique.gouv.fr/methode/criteres-et-tests/#11.12.1) | `NA_CONFIRMEE` | `NON_TESTE` | **Non applicable à confirmer métier** | Le formulaire de contact ne paraît ni modifier/supprimer des données existantes, ni constituer un test, ni emporter par lui-même une conséquence financière ou juridique. Cette qualification doit être confirmée par la MOA métier. |
| 11.12 | [11.12.2](https://accessibilite.numerique.gouv.fr/methode/criteres-et-tests/#11.12.2) | `NA_CONFIRMEE` | `NON_TESTE` | **Non applicable à confirmer métier** | Le formulaire de contact ne paraît ni modifier/supprimer des données existantes, ni constituer un test, ni emporter par lui-même une conséquence financière ou juridique. Cette qualification doit être confirmée par la MOA métier. |
| 11.13 | [11.13.1](https://accessibilite.numerique.gouv.fr/methode/criteres-et-tests/#11.13.1) | `NC_CONFIRMEE` | `TESTE_NON_CONFORME` | **Non conforme étayé** | Le champ Société concerne l’organisation de l’utilisateur et ne possède pas autocomplete=organization. |

## Contrôles restant à réaliser

1. Autoriser, dans un environnement de recette isolé, le retour serveur du scénario cinq fichiers avec données factices.
2. Faire qualifier humainement les intitulés, la proximité responsive, les regroupements, les boutons et la nécessité des `optgroup`.
3. Faire confirmer par la MOA métier la non-applicabilité de 11.12.1 et 11.12.2.
4. Vérifier l’annonce des erreurs avec NVDA + Firefox et/ou VoiceOver + Safari.
5. Réconcilier le registre `REVUE-MANUELLE-258` avec les décisions finales signées.

## Preuves livrées

- [Données structurées du retest sûr](preuves/P06-RETEST-SAFE.json)
- [Soumission native vide](preuves/runs/20260903T221344281418Z-42c57784/P06-01-soumission-vide-native.png)
- [Email invalide](preuves/runs/20260903T221344281418Z-42c57784/P06-02-email-invalide-natif.png)
- [Variante professionnel](preuves/runs/20260903T221344281418Z-42c57784/P06-03-variante-professionnel.png)
- [Extension interdite](preuves/runs/20260903T221344281418Z-42c57784/P06-04-extension-interdite-validation-client-sans-requete.png)
- [Cinq fichiers, requête bloquée](preuves/runs/20260903T221344281418Z-42c57784/P06-05-cinq-fichiers-requete-bloquee.png)
- [État serveur archivé, copie intègre](preuves/P06-ETAT-SERVEUR-ARCHIVE.json)
- [État Société optionnel archivé, copie intègre](preuves/P06-SOCIETE-OPTIONNEL-ARCHIVE.json)
- [Matrice JSON du complément](COUVERTURE-RGAA-11.json)

## Sources archivées non dupliquées

- `archives/audit-douane-p06-complet-rgaa-dsfr-2026-09-02/rgaa/P06-DECISIONS-258.json`
- `archives/audit-douane-p06-complet-rgaa-dsfr-2026-09-02/rgaa/REVUE-MANUELLE-258.json`

La présence d’une ligne dans une matrice ne vaut pas exécution du test. Ce document distingue volontairement inventaire, preuve technique, validation humaine et parcours serveur.
