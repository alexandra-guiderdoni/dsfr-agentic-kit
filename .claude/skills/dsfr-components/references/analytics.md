# Mesure d'audience DSFR 1.15.3 (analytics)

Le module `analytics` du paquet `@gouvfr/dsfr@1.15.3` assure la mesure
d'audience (compatible Eulerian, tarteaucitron, etc.). C'est un runtime JS :
ce document est une **référence d'intégration**, pas un générateur. Aucun
attribut ci-dessous n'est inventé — tous proviennent du paquet.

Sources du paquet : `dist/analytics/README.md`,
`src/dsfr/analytics/example/config.ejs`, `src/dsfr/analytics/example/attribute/index.ejs`.

## Dépendances

`analytics` dépend de `core`, `scheme` et des composants suivants (chargés
avant lui) : `accordion`, `button`, `breadcrumb`, `sidemenu`, `tab`,
`tooltip`, `display`, `tag`, `toggle`, `modal`, `navigation`, `password`,
`table`, `header`.

## Intégration (ordre des scripts)

Charger les scripts DSFR (module + nomodule) dans l'ordre des dépendances,
puis `analytics` en dernier (d'après `dist/analytics/README.md`) :

```html
<body>
  <!-- ...composants DSFR (core, scheme, accordion, button, navigation,
       modal, breadcrumb, toggle, sidemenu, password, tab, tooltip,
       tag, header, display, table)... -->
  <script type="module" src="js/analytics/analytics.module.min.js"></script>
  <script type="text/javascript" nomodule src="js/analytics/analytics.nomodule.min.js"></script>
</body>
```

La configuration est passée au module analytics à l'initialisation. La
structure de l'objet (extraite de `example/config.ejs`) :

```js
{
  analytics: {
    domain: 'domaine-de-suivi.fr',
    // collection: 'manual',          // manual | load | full | hash
    isActionEnabled: true,            // active le suivi des actions
    cmp: { id: 'tarteaucitron' },     // gestionnaire de consentement
    page: {
      // path, referrer, title, name   // pages virtuelles
      labels: ['category1'],
      categories: ['category1'],
      template: 'nom template',
      date: '2021-11-08',
      subtemplate: 'sous template',
      theme: 'theme page',
      subtheme: 'page sous theme',
      related: 'page liée'
      // depth, isError, current, total, filters  // pagination / erreurs
    },
    user: {
      // connect: { uid, email, isNew }
      // profile, language, type
    },
    site: {
      // environment: 'development' | 'stage' | 'production'
      entity: 'Entité responsable'
      // language, target, type
    }
  }
}
```

Le montage exact (assignation avant chargement du module) est détaillé dans
`src/dsfr/analytics/example/config.ejs` et `example/index.ejs` du paquet.

## Attributs de suivi `data-fr-analytics-*`

Posés sur les éléments interactifs (liens, boutons). La **valeur** de
l'attribut est le libellé envoyé à la mesure d'audience. Tous les attributs
ci-dessous sont attestés dans `src/dsfr/analytics` :

| Attribut | Usage |
| --- | --- |
| `data-fr-analytics-click` | Clic sur un lien/bouton (libellé envoyé). |
| `data-fr-analytics-dblclick` | Double-clic. |
| `data-fr-analytics-action` | Suivi d'action personnalisée ; `"false"` désactive le suivi automatique de l'élément. |
| `data-fr-analytics-change` | Changement de valeur (champ, select, radio/checkbox). |
| `data-fr-analytics-download` | Téléchargement de fichier. |
| `data-fr-analytics-external` | Lien externe (sortie du site). |
| `data-fr-analytics-internal` | Lien interne. |
| `data-fr-analytics-rating` | Notation / évaluation. |
| `data-fr-analytics-page-total` | Nombre total de pages (pagination). |

Exemple (d'après `example/attribute/index.ejs`) :

```html
<a href="/demarche"
   data-fr-analytics-click="Libellé envoyé à la mesure d'audience">
  Démarrer la démarche
</a>
```

Avec `isActionEnabled: true`, le suivi des actions se pose via ces attributs.
Pour désactiver le suivi automatique d'un élément précis :
`data-fr-analytics-action="false"`.

Depuis 1.15.0, la valeur `reduce` s'ajoute à ce jeu, des deux côtés :

- sur un élément, `data-fr-analytics-action="reduce"` empêche l'initialisation
  de l'instance de suivi. L'élément n'est pas tracé et aucune action n'est
  émise, là où `false` désactive l'envoi sur une instance existante ;
- en configuration, `isActionEnabled: 'reduce'` n'instrumente que les éléments
  portant un attribut `data-fr-analytics-action`, au lieu de tous les éléments
  éligibles. L'amont la destine aux pages dont le nombre d'éléments génère de
  la latence.

## API JS (introspection runtime, agent-browser + paquet 1.15.3, 2026-08-28)

`window.dsfr.analytics` est une **interface d'initialisation asynchrone**, pas
un sac de méthodes directes. Introspection sur une page chargeant
`dsfr.module.min.js` puis `analytics/analytics.module.min.js` en 1.15.3 : les
clés exposées sont `_isReady` (booléen), `_readiness` (objet), `_resolve` et
`_reject` (fonctions), `_config` et `_init` (objets), plus les deux
énumérations ci-dessous.

- `Collection` : `MANUAL` (`manual`), `LOAD` (`load`), `FULL` (`full`),
  `HASH` (`hash`) — modes de collecte, correspondant à l'option `collection`
  de la configuration.
- `PushType` : `COLLECTOR` (`collector`), `ACTION` (`action`),
  `ACTION_PARAMETER` (`actionparam`) — types d'événement poussés vers le
  collecteur. Noter la valeur `actionparam`, sans séparateur.

Les événements de haut niveau (page, route, tracking, search) transitent par
cette interface (poussés, puis résolus à l'init) ; ils ne sont pas des
méthodes énumérables directement sur `window.dsfr.analytics`. Se référer à la
documentation officielle DSFR analytics pour les signatures d'événement.

## Limites

- La mesure d'audience est un runtime JS : aucun générateur du skill ne
  produit la configuration analytics. Cette référence documente l'intégration
  et les attributs à poser manuellement.
- Le consentement (CMP) et le domaine de suivi dépendent du déploiement
  cible ; ne pas revendiquer la conformité RGPD/CNIL sans audit dédié.
- Version : 1.15.3, document entièrement rejoué le 2026-08-28. Les neuf
  attributs `data-fr-analytics-*` ont été vérifiés identiques entre 1.14.4 et
  1.15.3 sur le dépôt amont ; l'API JS a été réintrospectée en navigateur sur
  le paquet 1.15.3. Les 47 fichiers JavaScript modifiés entre les deux
  versions n'ont changé ni les clés exposées ni les valeurs des deux
  énumérations.
