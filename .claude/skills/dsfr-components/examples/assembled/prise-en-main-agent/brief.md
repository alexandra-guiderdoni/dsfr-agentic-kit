# Brief - Prise en main agent

Produire une page DSFR assemblée qui montre le parcours complet attendu pour
un agent externe : lire un brief, transformer le besoin en `page.json`,
générer `page.html`, puis rattacher une preuve locale bornée.

La page doit présenter un service fictif d'accompagnement numérique. Elle doit
être assez réaliste pour tester la composition du builder, mais rester neutre :
pas de bloc marque République française, pas de claim de conformité DSFR ou
RGAA, pas de contenu métier définitif.

Contraintes :

- utiliser `brand_mode: neutral` ;
- fournir un `<h1>` unique dans le contenu principal ;
- relier navigation et sommaire à des ancres existantes ;
- générer des cartes, un formulaire avec validation différée, un accordéon et
  un bloc de preuve ;
- éviter `href="#"`, les gestionnaires inline et les cibles ARIA absentes ;
- écrire une preuve qui distingue ce qui est vérifié de ce qui reste hors
  périmètre.

Critère de réussite : la commande `bash scripts/demo-dsfr-assembled-page.sh`
génère une page HTML hors dépôt, valide le JSON, vérifie le builder et inspecte
la page produite.
