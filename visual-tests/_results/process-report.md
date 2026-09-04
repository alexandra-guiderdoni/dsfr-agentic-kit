# Process check — complément Formulaires P06

- **Mode :** hybride
- **État Git :** implémentation non suivie ; aucun « avant » adressable par commit
- **Unités contrôlées :** 5
- **Changements de comportement :** 5 attendus
- **Nouvelles erreurs :** 0
- **Surprises :** 0
- **Preuves :** 15 observations mesurées
- **Run probatoire courant :** `20260903T221344281418Z-42c57784`

## Résultats mesurés

| Unité | Avant | Après | Delta |
|---|---|---|---|
| Retest Playwright sûr | Pas de preuve courante liée au collecteur v2 | 5 scénarios, inventaire P01–P09, captures versionnées et manifeste lié au SHA du collecteur | Sortie enrichie |
| Générateur d’annexe | Pas de complément exhaustif final | Matrice exacte 34/34, deux tickets candidats HTML/Markdown et deux preuves d’archive embarquées | Sortie enrichie |
| Générateur du paquet | Pas d’intégration des deux requalifications P06 | Liens, index et contrôle explicite de 4 arbitrages source + 2 compléments | Navigation et contrat enrichis |
| Validation du paquet | Périmètre d’intégrité antérieur | 75 fichiers couverts ; 75/75 empreintes valides ; `generation_state=COMPLETE` | Périmètre étendu |
| Rendu local | Pages finales absentes ou incomplètes | 5 pages contrôlées en 1440×1000 et 390×844, sans exception ni débordement horizontal | Présentation enrichie |

## Invariant de sécurité mesuré

- Les seules méthodes autorisées par le `BrowserContext` étaient `GET`, `HEAD` et `OPTIONS`.
- Toute connexion WebSocket aurait été fermée avant les messages applicatifs ; aucune n’a été observée.
- L’extension interdite a été rejetée côté client sans méthode HTTP mutante.
- Les cinq PNG synthétiques ont déclenché un unique AJAX `POST` multipart, corrélé par endpoint et par les cinq noms de fichier ; il a été arrêté avant envoi.
- Une erreur `Drupal.AjaxError` est survenue dans la même fenêtre ; elle est publiée avec une causalité explicitement non prouvée, et non masquée comme erreur de garde.
- Aucune requête mutante n’a atteint l’état `requestfinished`.
- Aucun formulaire valide ni fichier n’a été transmis au serveur.

## Résultats RGAA P06

- **34/34 tests du thème 11 inventoriés**, sans doublon ni identifiant manquant.
- Répartition du complément : **3** conformités techniques à valider humainement, **3** non-conformités étayées, **5** NA conditionnels DOM, **17** qualifications humaines, **4** retests serveur, **2** NA à confirmer métier.
- `11.10.2` : décision publiée `C_CONFIRMEE` → **ticket candidat non conforme étayé** ; 9 contrôles `required` ne portent pas l’indication attendue dans leur étiquette ou un passage associé.
- `7.5.2` : décision publiée `NA_CONFIRMEE` → **ticket candidat non conforme étayé** ; région dynamique `aria-live="polite"` sans rôle ni atomicité équivalente.
- Les quatre retests serveur restent ouverts : `11.10.6`, `11.10.7`, `11.11.1`, `11.11.2`.

## Intégrité et présentation

- Le manifeste v2 référence le collecteur courant et cinq captures dont tailles et SHA-256 ont été revérifiés.
- Les deux JSON d’archive embarqués sont byte-identiques à leurs sources ; aucun fichier de `archives/` n’a été modifié.
- **75/75** entrées de `SHA256SUMS` sont valides.
- Une régénération d’annexe volontairement mise en échec a d’abord basculé atomiquement la validation en état non vert, puis supprimé `SHA256SUMS` ; le paquet a ensuite été restauré par une génération complète.
- Deux processus concurrents de test ont confirmé que le verrou exclusif commun sérialise les écrivains P06.
- Dix contre-exemples injectés en mémoire (33 lignes, doublon, retest serveur manquant, faux candidats, hash preuve/collecteur/capture altéré, compte réseau et attribution page incohérents) ont tous été rejetés par le validateur final.
- **243** liens ou fragments locaux ont été contrôlés dans **24** pages générées/intégrées : **0 cassé**.
- La relecture indépendante finale ne relève plus aucune anomalie P0/P1.
- Les dix captures desktop/mobile ont été inspectées visuellement ; une balise `main` et un `h1` sont présents sur chaque page contrôlée.
- Le runner ShipGuard formel n’a pas été déclaré PASS : `visual-tests/_config.yaml` est absent. Les mesures visuelles proviennent de la campagne Playwright locale directe.

## Non couvert volontairement

1. Réponse serveur réelle pour les quatre tests serveur.
2. Validation humaine sémantique, visuelle et métier.
3. Restitution réelle NVDA, JAWS ou VoiceOver.
4. Liens archive-relatifs internes aux 18 rapports sources byte-identiques.
5. Comparaison Git avant/après : les chemins d’implémentation sont non suivis dans ce dépôt.

Le paquet reste donc volontairement marqué `client_transmission_ready: false`.

Résultat machine : `visual-tests/_results/process-results.json`.
