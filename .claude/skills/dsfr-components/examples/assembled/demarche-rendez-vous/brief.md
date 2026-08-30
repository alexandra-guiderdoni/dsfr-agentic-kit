# Brief - Demande de rendez-vous

Produire une page de démarche administrative neutre pour prendre un rendez-vous.
La page doit orienter rapidement l'usager, lister les pièces utiles, afficher
un formulaire borné et conserver la validation différée des champs requis.

Contraintes :

- utiliser `brand_mode: neutral`, sans bloc marque République française ;
- fournir un vrai `<h1>` dans le contenu ;
- éviter les liens `href="#"` ;
- relier le sommaire et la navigation à des ancres réellement présentes ;
- ne pas revendiquer de conformité DSFR ou RGAA.

Critère de réussite : le JSON génère une page complète avec header, main,
footer, formulaire labellisé, absence d'ancres cassées et validation locale du
builder.
