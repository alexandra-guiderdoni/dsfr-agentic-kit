---
name: agentic-design-harness
description: "Utiliser quand une demande de design agentique vise un artefact inspectable ou un handoff visuel depuis brief, DESIGN.md, design system, code, site, screenshot ou assets : Claude Design-like, prototype HTML, maquette, deck, one-pager, variantes ou tweaks. Ne pas utiliser pour une correction CSS/frontend déjà cadrée."
allowed-tools: Read, Glob, Grep, Bash, Write, Edit, WebFetch
context: conversation
---

# Agentic design harness - produire un artefact design prouvable

## Quand l'utiliser

- L'utilisateur demande une expérience de type Claude Design, mais portable entre Claude, Codex, GLM ou un autre runtime.
- Le livrable attendu est un artefact visuel inspectable : HTML autonome, prototype, écran, deck, one-pager, système de design ou paquet de handoff.
- Le design doit s'appuyer sur un système existant : `DESIGN.md`, tokens, CSS, composants, site, screenshot, logo, charte ou dépôt.
- Ne pas utiliser pour une correction CSS isolée, une conversion Markdown vers HTML accessible, des slides DSFR déjà cadrées, ou un audit accessibilité spécialisé : utiliser alors le skill dédié.

Routage positif rapide : déclencher seulement si la sortie attendue combine une intention visuelle avec un artefact inspectable ou un handoff réutilisable. Sans artefact ni preuve de rendu attendue, rester sur la réponse directe, le skill spécialisé ou la correction locale.

Routage négatif rapide : si la demande porte seulement sur une correction frontend déjà spécifiée, une conversion documentaire, un audit RGAA/WCAG, une génération d'image isolée ou un composant DSFR déjà cadré, ne pas déclencher ce skill. Nommer l'action ou le skill plus adapté et garder `agentic-design-harness` hors du contexte.

## Procédure pas-à-pas

### Étape 1 - Cadrer le contrat

Nommer l'intention produit, l'audience, l'artefact cible, la fidélité, le nombre de variantes, les axes de tweak, les sources disponibles, les droits d'usage, le chemin de sortie et la preuve attendue. Pour un nouveau travail ambigu, poser au plus trois questions ciblées ; si plus de trois réponses sont nécessaires, demander un brief écrit. Pour un petit tweak ou un brief suffisant, avancer.

Si l'utilisateur demande de recréer une interface, marque ou structure propriétaire distinctive sans source, autorisation ou contexte de travail légitime, ne pas reproduire : proposer une direction originale inspirée des objectifs, pas une copie.

**Critère de fin** : un mini-brief contient `objectif`, `sources`, `artefact`, `droits`, `preuve`, `non vérifié`.

**Exemple minimal** : "prototype onboarding depuis screenshot + CSS" devient "artefact HTML autonome, sources screenshot/CSS, preuve capture desktop/mobile + console sans erreur".

### Étape 2 - Cartographier les sources

Lire les sources réelles avant de dessiner. Priorité : fichiers locaux de design et composants, `DESIGN.md`, tokens, CSS, assets requis, screenshots ou capture navigateur, documentation officielle, puis prompts tiers. Pour un dépôt, un arbre de fichiers est un menu, pas une preuve : importer ou ouvrir les fichiers concrets. Pour un site, une page web textuelle ne prouve pas le rendu : obtenir une capture ou ouvrir la page si le rendu visuel compte. Si le travail dépend de sources externes, lire `references/sources.md` avant de décider de la hiérarchie des sources.

Quand un profil local `design-systems/<system>/DESIGN.md` existe, le traiter comme routeur partagé : lire son point d'entrée, son fichier de tokens déclaré, puis seulement les références ciblées par le besoin. Ne pas copier le profil dans ce skill et ne pas le résumer comme source unique : il doit rester réutilisable par les skills spécialisés, les audits et les autres runtimes.

Dans ce workspace, si le brief mentionne DSFR, Système de Design de l'État, page `.gouv.fr`, service public français, République française, Marianne ou classes `fr-*`, traiter `design-systems/dsfr/DESIGN.md` comme routeur spécialisé : lire ce point d'entrée, `design-systems/dsfr/tokens.yaml`, puis seulement les références que le routeur désigne pour le besoin. Pour une page ou un composant HTML, basculer vers `dsfr-components`; pour conformité, audit ou correction RGAA/WCAG, basculer vers les skills d'accessibilité. Ne pas recopier ici le routage DSFR ni charger toutes ses références : ce skill reste le harnais générique.

**Critère de fin** : une matrice courte indique pour chaque source `chemin ou URL`, `lu`, `extrait`, `inféré`, `absent` ou `faible`, puis résume le vocabulaire visuel observé : copie, palette, ton, états, animation, ombres, cartes, layout et densité.

**Exemple minimal** : `DESIGN.md` lu, `tokens.css` lu, logo absent, screenshot inféré pour les espacements.

### Étape 3 - Composer l'artefact

Produire le plus petit artefact inspectable qui répond au brief. Nommer les HTML de façon descriptive et préserver l'ancienne version lors d'une révision significative. Préférer un fichier unique avec modes, variantes ou tweaks persistés quand l'exploration le demande ; viser au moins trois variantes si l'objectif est exploratoire, et créer plusieurs fichiers seulement si le handoff ou le format l'exige.

Pour un artefact cohérent, rédiger ou consolider le markup final dans le contexte principal depuis les sources lues. Les sous-agents peuvent explorer, lister les composants, chercher des sources ou vérifier, mais ne doivent pas être l'auteur non relu du markup final.

Copier uniquement les assets nécessaires, sans référencer directement un autre projet et sans copie massive de dossiers. Si une icône, image ou composant manque, utiliser un placeholder honnête plutôt qu'une fausse reproduction. Éviter le contenu de remplissage, les chiffres décoratifs et l'iconographie inutile. Marquer les valeurs inférées, réutiliser les couleurs de marque ou `oklch` pour étendre une palette, et n'utiliser les emojis que si les sources le font déjà.

Pour les artefacts multi-écrans, ajouter `data-screen-label` avec numérotation humaine 1-indexée. Pour decks, vidéos ou parcours, persister la position avec `localStorage`. Pour HTML/JS, éviter `scrollIntoView` dans les apps intégrées, épingler les dépendances externes quand elles existent, nommer les objets globaux de façon spécifique, et scinder tout fichier qui approche 1 000 lignes.

**Critère de fin** : l'artefact existe, ses hypothèses sont localisables, ses assets requis sont présents, et les variantes ou réglages attendus sont accessibles.

**Exemple minimal** : `prototype-checkout.html` contient trois variantes activables, lit les images copiées dans `assets/`, et documente les tokens inférés dans un bloc de commentaire court.

### Étape 4 - Vérifier le rendu

Ouvrir ou servir l'artefact, vérifier la console, produire au moins une preuve visuelle quand le rendu est le résultat. Pour une interface, vérifier les états naturels, les tailles desktop/mobile, l'absence de blanc involontaire, de chevauchement, de texte coupé et de contraste manifestement insuffisant. Faire aussi un contrôle accessibilité de surface : focus visible, libellés évidents, navigation clavier plausible et aucune régression RGAA/DSFR manifeste. Si l'objectif principal est l'accessibilité, basculer vers le skill d'audit ou de correction adapté. Si une vérification navigateur est impossible, le dire explicitement.

Pour un design system local, utiliser son routeur de vérification avant les contrôles ad hoc. Pour DSFR, suivre le routeur local de vérification, appliquer le prompt de conformité de `dsfr-components` si une page ou un composant HTML DSFR est produit, et router vers les skills d'accessibilité si un audit RGAA/WCAG est demandé. Une preuve statique ne remplace pas le rendu chargé : les états interactifs, messages d'erreur, modales, menus, focus et classes de display doivent être observés dans la page quand ils conditionnent le résultat. Pour les composants DSFR pilotés par JavaScript, attendre l'initialisation du DSFR avant de conclure qu'un clic ou une ouverture échoue.

La preuve navigateur minimale contient `chemin ou URL ouvert`, `viewport`, `capture ou export`, `résultat console`, `état ou interaction observé`, et `non vérifié` pour ce qui n'a pas été exercé. Pour un écran statique, une capture ciblée peut suffire ; pour une interface responsive ou interactive, vérifier desktop et mobile, ou expliquer pourquoi l'un des deux manque.

**Critère de fin** : la preuve cite la commande ou l'URL, le viewport, la capture ou le log, le résultat console et la limite observée.

**Exemple minimal** : `python3 -m http.server 4173`, captures `pricing-desktop.png` et `pricing-mobile.png`, console sans erreur bloquante, onglets et focus vérifiés, animation non vérifiée si absente du brief.

### Étape 5 - Transmettre

Clore avec la pyramide `résultat -> preuve -> limites -> reprise`. Le handoff doit être agnostique : chemins, sources, conventions, commandes et limites, pas un nom de modèle comme source d'autorité. Quand un rendu a été vérifié, la preuve transmise reprend les éléments observables exacts : chemin ou URL, viewport, capture ou export, résultat console ou log, et état ou interaction observé. Si l'un manque, l'écrire dans `limites/non vérifié`. Le handoff contient `artefact`, `sources`, `preuves`, `limites/non vérifié`, `autonomie` (questions posées, hypothèses ou arrêt), `clauses déclenchées` (droits, DSFR, accessibilité, sources externes) et `reprise` (commande ou prochain point d'arrêt). Abaisser les claims au niveau de preuve réellement produit : ne pas écrire `conforme DSFR`, `conforme RGAA`, `prêt pour publication` ou équivalent sans vérification dédiée.

**Critère de fin** : un autre agent peut reprendre sans relire la conversation, avec commande, fichiers, preuves et limites nommés.

**Exemple minimal** : "artefact : `prototype-checkout.html`; sources : `DESIGN.md`, `tokens.css`; preuves : captures desktop/mobile + console ; limites : logo non fourni ; autonomie : aucune question ; clauses : sources locales seulement ; reprise : ouvrir `prototype-checkout.html`".

## Exemple complet end-to-end

```text
Demande : "Implémenter un prototype Claude Design-like pour la page pricing à
partir du repo local et du screenshot fourni."

Actions :
1. Lire AGENTS.md, DESIGN.md, CSS/tokens et screenshot.
2. Produire la matrice : DESIGN.md extrait, CSS extrait, screenshot extrait,
   prompt tiers non officiel utilisé seulement comme inspiration de workflow.
3. Créer public/prototype-pricing.html avec variantes "dense", "editorial" et
   "enterprise", assets copiés un par un.
4. Lancer : python3 -m http.server 4173 -d public
5. Vérifier par navigateur : capture desktop, capture mobile, console.

Sortie attendue :
- public/prototype-pricing.html existe ;
- les variantes sont activables sans rechargement ;
- la preuve mentionne captures et erreurs console ;
- les inférences de design sont marquées.
```

## Pièges connus

- Copier un prompt propriétaire ou tiers : extraire des invariants de harnais, ne pas reprendre une prose ou une identité d'outil comme règle transverse.
- Confondre inspiration et source de vérité : un prompt communautaire est `faible`, une documentation officielle ou un fichier local lu est prioritaire.
- Produire une maquette générique : si les sources visuelles existent, réutiliser leurs tokens, composants, contraintes et assets.
- Omettre la preuve navigateur : un fichier HTML écrit n'est pas un rendu vérifié.
- Écraser un artefact existant : créer une variante nommée ou demander confirmation si le remplacement change le travail d'un autre agent.

## Contraintes et blocages

- JAMAIS reproduire une interface propriétaire distinctive sans droits d'usage explicités dans le mini-brief.
- JAMAIS inventer une marque, un logo, des chiffres, une image ou une fonctionnalité comme si la source les fournissait.
- JAMAIS conclure qu'un artefact visuel est bon sans rendu ouvert, capture, console ou limite de vérification nommée.
- NE PAS utiliser un prompt tiers comme autorité si une source locale ou officielle contredit son workflow.
- TOUJOURS marquer `Unknown` ou demander une source quand le design system, les droits, l'audience ou le comportement attendu changent le résultat.
- Si les assets sont absents : utiliser des placeholders honnêtes et lister les assets manquants.
- Si l'artefact ne se charge pas, si la console casse ou si le rendu est vide : corriger avant transmission, ou déclarer `NO-GO rendu` avec la ligne d'erreur décisive.
- Si le fichier existant peut appartenir à un autre agent : créer une version nommée ou demander confirmation avant remplacement.

## Checklist de livraison

Avant de conclure, vérifier :

- [ ] Mini-brief et matrice des sources présents dans le compte rendu ou le fichier.
- [ ] Artefact inspectable créé ou modifié au chemin annoncé.
- [ ] Assets nécessaires copiés sans copie massive inutile.
- [ ] Inférences et valeurs extraites distinguées.
- [ ] Vérification visuelle, accessibilité de surface ou limite de vérification nommée.
- [ ] Claims de conformité limités au niveau de preuve produit.
- [ ] Handoff agnostique avec artefact, sources, preuves, limites, autonomie, clauses déclenchées et commande de reprise.

## Pour aller plus loin

Lire `references/sources.md` quand il faut justifier les sources, mettre à jour la méthode ou départager un prompt tiers, une documentation officielle et les fichiers locaux.

Pour publier, stabiliser ou évaluer ce skill lui-même, lire `references/method-contract.md` avant le verdict. Ne pas charger cette référence pendant une production design courante : elle documente le contrat de méthode du skill, pas le workflow utilisateur.
