# Gabarit de rejeu d'audit DSFR

Utiliser ce gabarit dans le projet consommateur, jamais comme campagne
versionnée dans le kit. Remplacer tous les champs entre chevrons avant
exécution.

## Contexte

- Site : `<URL_DU_SITE>`
- Projet de sortie : `<PROJECT_ROOT>`
- Kit : `<KIT_ROOT>`
- Commit du kit : `<COMMIT_KIT>`
- Échantillon : `<PAGES_ET_URLS>`
- Version DSFR cible : lire `design-systems/dsfr/tokens.yaml`

## Contrat

Lire dans cet ordre : `DEMARRAGE-AGENT.md`, `DESIGN.md`, `tokens.yaml`, puis le
skill requis. Écrire les campagnes, preuves, captures et livrables dans
`<PROJECT_ROOT>`, jamais dans `<KIT_ROOT>`.

Ne produire que des constats bornés aux règles réellement exécutées. Ne pas
produire de taux RGAA officiel, de claim `conforme DSFR` ou de déclaration
automatique. Toute validation humaine restante doit être visible.

## Vérifications de sortie

1. vérifier la disponibilité réseau et distinguer le proxy du site cible ;
2. vérifier l'empreinte du commit du kit ;
3. conserver les preuves par page et par état ;
4. vérifier `VALIDATION.json` et les liens relatifs ;
5. relire visuellement le rapport HTML si un rapport est produit ;
6. consigner les outils absents, les phases ignorées et les résultats non
   exercés.

## Reprise

Commande de campagne :

```bash
bash "<KIT_ROOT>/scripts/audit-rgaa-creator.sh" run \
  "<PROJECT_ROOT>/campaign.yaml"
```
