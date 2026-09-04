# Audit logique final — pipeline P06

**Périmètre :** collecte Playwright sûre, publication de l’annexe P06 et validation du paquet Virginie.

## Verdict

Aucune violation P0/P1 confirmée sur l’état final. Les contre-exemples qui permettaient auparavant un paquet faussement vert, une liste RGAA incomplète, une chaîne de preuve périmée ou une attribution causale abusive sont désormais bloqués ou publiés comme limites explicites.

## Invariants vérifiés

- Les trois écrivains P06 utilisent le même verrou exclusif interprocessus.
- Les invalidations écrivent atomiquement `valid: false` / `STALE` avant de supprimer `SHA256SUMS`.
- Toute invocation de l’annexe invalide le paquet avant la première lecture faillible.
- Le POST multipart synthétique est bloqué avant envoi ; aucune requête mutante n’est terminée.
- `Drupal.AjaxError` est exposée comme événement de même fenêtre avec **causalité non prouvée** ; elle n’est plus masquée comme erreur induite par la garde.
- La matrice contient exactement 34 identifiants uniques du thème 11.
- Le groupe serveur ouvert est exactement `11.10.6`, `11.10.7`, `11.11.1`, `11.11.2`.
- Les deux seules requalifications supplémentaires sont `11.10.2` et `7.5.2`.
- La détection 11.10.2 utilise le texte associé visible et rejette les formulations négatives ainsi que l’astérisque isolé.
- Le validateur final recalcule la chaîne collecteur → preuve → matrice → captures → sources d’archive.
- Le paquet reste explicitement `client_transmission_ready: false` tant que les six arbitrages demeurent.

## Mesures finales

- Run probatoire : `20260903T221344281418Z-42c57784`.
- Hash collecteur : `42c57784840455795d7e7e9586ff9c2ddf3f5acf58fe9f843cf5fa6d930e8dd8`.
- 34/34 tests du thème 11, sans doublon.
- 10 contre-exemples injectés en mémoire : 10 rejetés.
- Deux processus concurrents de test : sérialisation confirmée par le verrou.
- Injection d’échec annexe : validation non verte et checksum absent avant restauration complète.
- 75/75 empreintes SHA-256 valides.
- Relecture indépendante du snapshot final : aucune anomalie P0/P1 restante.
- 243 liens/fragments locaux sur 24 pages : 0 cassé.

## Risques résiduels

1. **Moyen — remplacement multi-fichier de l’annexe.** Une interruption entre deux remplacements finaux peut laisser une annexe mêlant anciennes et nouvelles versions. Le paquet est déjà non vert, les anciens runs ne sont supprimés qu’après validation HTML complète, et une régénération restaure l’ensemble.
2. **Faible — verrou coopératif.** Un processus externe qui modifie volontairement les fichiers sans prendre le verrou reste hors du protocole de sérialisation.

## Non couverts par le mode sûr

- Réponses serveur réelles pour `11.10.6`, `11.10.7`, `11.11.1`, `11.11.2`.
- Validation humaine des qualifications sémantiques, visuelles et métier.
- Tests réels NVDA, JAWS ou VoiceOver.
- Historique Git avant/après : les chemins de travail sont non suivis.
