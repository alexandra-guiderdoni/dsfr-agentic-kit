# Invariants d’intégration HTML et ARIA

Ces contrôles complètent les références de composants DSFR. Ils portent sur des invariants du DOM rendu indépendants de la version DSFR.

## Relations par identifiant

Pour `aria-controls`, `aria-labelledby` et `aria-describedby`, chaque identifiant référencé doit désigner un élément existant dans le même document. Une valeur peut contenir plusieurs identifiants séparés par des espaces. Chaque identifiant doit être résolu séparément.

## Contenu masqué et focus

Un descendant d’une zone `aria-hidden="true"` ne doit pas rester dans le parcours clavier. L’état ARIA, la visibilité du composant et son exposition au focus doivent être synchronisés avant tout déplacement du focus.

## Liens ouvrant un nouveau contexte

Lorsqu’un lien s’ouvre avec `target="_blank"`, son nom accessible doit annoncer la nouvelle fenêtre. Pour un lien HTTP ou HTTPS, `rel="noopener"` doit également être présent afin de neutraliser l’accès à `window.opener`.

## Qualification

Un échec instrumenté est un signal à qualifier par page et par instance. Il ne prouve jamais une conformité DSFR globale.
