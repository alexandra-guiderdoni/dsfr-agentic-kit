# Thematiques RGAA — checklist d'inspection DOM

Reference pour la phase 2 (inspection DOM complementaire) du skill /pre-audit-rgaa-dsfr.

## Thematiques inspectables par le skill

### Theme 1 — Images

- `alt` vides sur images informatives
- `alt` non vides sur images decoratives
- Pertinence des alternatives textuelles
- Images complexes sans description detaillee

### Theme 6 — Liens

- Intitules explicites (pas de « cliquez ici », « en savoir plus » sans contexte)
- Liens placeholders (href="#", href vide)
- Doublons (meme intitule, cibles differentes)
- Liens images sans alternative

### Theme 7 — Scripts

- Compatibilite AT des composants interactifs (modales, accordeons, onglets)
- **Attention faux positifs** : certains composants DSFR ont un double comportement desktop/mobile (ex : header-modal = inline en desktop, vraie modale en mobile). Verifier le comportement du design system AVANT de classer en NC

### Theme 8 — Elements obligatoires

- `<li>` vides dans les listes
- Balises de presentation (`<b>`, `<i>`, `<font>`, `<center>`)
- Attributs HTML suspects (distance de Levenshtein : `clas`, `classs`, `stlye`, `ariia-label`)
- Validation de la langue par defaut

### Theme 9 — Structuration

- Hierarchie des titres (extraire tous les hN, verifier la coherence : pas de saut h2->h4)
- Listes structurees (ul/ol vs paragraphes a puces manuelles)
- Citations balisees

### Theme 10 — Presentation

- Focus visible sur elements interactifs
- Reflow 320px, espacement du texte — classer en NOTE-INTERNE si non verifiable sans outil visuel

### Theme 11 — Formulaires

- Etiquettes visibles (`<label>` associe, pas seulement `aria-label` ou `placeholder`)
- Regroupements de champs (`<fieldset>` + `<legend>`)
- Messages d'erreur associes aux champs

### Theme 12 — Navigation

- Liens d'evitement (presence, fonctionnement, ancres valides)
- Systemes de navigation (menu, plan du site, moteur de recherche)
- Ordre de tabulation coherent

## Thematiques non couvertes (avertissement obligatoire)

En fin de phase 2, afficher un avertissement listant les thematiques non verifiees :

- **Theme 2 — Cadres** : necessite inspection manuelle des iframes
- **Theme 3 — Couleurs** : contrastes exacts necessitent mesure instrumentale (outil /outils-wcag)
- **Theme 4 — Multimedia** : necessite presence de contenus audio/video
- **Theme 5 — Tableaux** : necessite presence de tableaux de donnees
- **Theme 13 — Consultation** : limites de temps, orientation, gestes complexes — necessite tests manuels

## Detection de coquilles HTML et orthographiques

- Scanner les attributs HTML suspects par distance de Levenshtein (ex : `clas` au lieu de `class`, `classs`, `stlye`, `ariia-label`)
- Detecter les fautes d'orthographe evidentes dans les contenus textuels visibles (titres, paragraphes, liens) — classer en RECO, pas en NC
