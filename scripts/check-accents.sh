#!/bin/bash
# scripts/check-accents.sh
# Détection des mots français sans accents dans les fichiers Markdown
#
# Parcourt un fichier Markdown et signale les mots français courants
# qui devraient porter des accents mais n'en ont pas.
# Avertissement informatif uniquement, jamais bloquant.
#
# Fonctionnement :
#   Reçoit un chemin de fichier en argument ($1).
#   Filtre les blocs de code (``` ... ```), les URLs, les chemins
#   et le code inline (entre backticks).
#   Cherche les mots français sans accents (case-insensitive).
#   Affiche les violations trouvées avec le numéro de ligne et la correction.
#   Un seul passage sur le fichier via awk pour la performance.
#
# Usage :
#   ./check-accents.sh fichier.md
#   ./check-accents.sh /chemin/vers/document.MD
#
# Exit codes :
#   0 = toujours (avertissement informatif, jamais bloquant)
#
# Compatibilité :
#   macOS (BSD awk) et Linux (gawk). Pas de dépendance externe.

FILE="$1"

# Vérifications silencieuses
[[ -z "$FILE" ]] && exit 0
[[ -f "$FILE" ]] || exit 0
echo "$FILE" | grep -qiE '\.(md|MD)$' || exit 0

BASENAME=$(basename "$FILE")

OUTPUT=$(LC_ALL=C awk '
BEGIN {
  count = 0
  in_code = 0
  n = 0

  # Accent grave
  w[n]="regle";         c[n]="règle";         n++
  w[n]="regles";        c[n]="règles";        n++
  w[n]="memoire";       c[n]="mémoire";       n++
  w[n]="repertoire";    c[n]="répertoire";    n++
  w[n]="systeme";       c[n]="système";       n++
  w[n]="critere";       c[n]="critère";       n++
  w[n]="modele";        c[n]="modèle";        n++
  w[n]="probleme";      c[n]="problème";      n++
  w[n]="requete";       c[n]="requête";       n++
  w[n]="bibliotheque";  c[n]="bibliothèque";  n++
  w[n]="caractere";     c[n]="caractère";     n++
  w[n]="piege";         c[n]="piège";         n++
  w[n]="theme";         c[n]="thème";         n++
  w[n]="icone";         c[n]="icône";         n++
  w[n]="premiere";      c[n]="première";      n++
  w[n]="derniere";      c[n]="dernière";      n++
  w[n]="entiere";       c[n]="entière";       n++
  w[n]="maniere";       c[n]="manière";       n++
  w[n]="matiere";       c[n]="matière";       n++

  # Accent aigu
  w[n]="securite";      c[n]="sécurité";      n++
  w[n]="accessibilite"; c[n]="accessibilité"; n++
  w[n]="conformite";    c[n]="conformité";    n++
  w[n]="qualite";       c[n]="qualité";       n++
  w[n]="propriete";     c[n]="propriété";     n++
  w[n]="specificite";   c[n]="spécificité";   n++
  w[n]="integrite";     c[n]="intégrité";     n++
  w[n]="disponibilite"; c[n]="disponibilité"; n++
  w[n]="identite";      c[n]="identité";      n++
  w[n]="stabilite";     c[n]="stabilité";     n++
  w[n]="capacite";      c[n]="capacité";      n++
  w[n]="priorite";      c[n]="priorité";      n++
  w[n]="complexite";    c[n]="complexité";    n++
  w[n]="compatibilite"; c[n]="compatibilité"; n++
  w[n]="fiabilite";     c[n]="fiabilité";     n++
  w[n]="visibilite";    c[n]="visibilité";    n++
  w[n]="fidelite";      c[n]="fidélité";      n++
  w[n]="tracabilite";   c[n]="traçabilité";   n++
  w[n]="verifie";       c[n]="vérifié";       n++
  w[n]="verifier";      c[n]="vérifier";      n++
  w[n]="genere";        c[n]="généré";        n++
  w[n]="generee";       c[n]="générée";       n++
  w[n]="cree";          c[n]="créé";          n++
  w[n]="creee";         c[n]="créée";         n++
  w[n]="modifie";       c[n]="modifié";       n++
  w[n]="modifiee";      c[n]="modifiée";      n++
  w[n]="detecte";       c[n]="détecté";       n++
  w[n]="detectee";      c[n]="détectée";      n++
  w[n]="specifie";      c[n]="spécifié";      n++
  w[n]="integre";       c[n]="intégré";       n++
  w[n]="configure";     c[n]="configuré";     n++
  w[n]="installe";      c[n]="installé";      n++
  w[n]="connecte";      c[n]="connecté";      n++
  w[n]="synchronise";   c[n]="synchronisé";   n++
  w[n]="initialise";    c[n]="initialisé";    n++
  w[n]="supprime";      c[n]="supprimé";      n++
  w[n]="methode";       c[n]="méthode";       n++
  w[n]="etape";         c[n]="étape";         n++
  w[n]="evenement";     c[n]="événement";     n++
  w[n]="element";       c[n]="élément";       n++
  w[n]="reponse";       c[n]="réponse";       n++
  w[n]="resultat";      c[n]="résultat";      n++
  w[n]="reference";     c[n]="référence";     n++
  w[n]="hierarchie";    c[n]="hiérarchie";    n++
  w[n]="necessaire";    c[n]="nécessaire";    n++
  w[n]="defaut";        c[n]="défaut";        n++
  w[n]="demarrage";     c[n]="démarrage";     n++
  w[n]="declaration";   c[n]="déclaration";   n++
  w[n]="deploiement";   c[n]="déploiement";   n++
  w[n]="reseau";        c[n]="réseau";        n++
  w[n]="resume";        c[n]="résumé";        n++

  # Accent circonflexe
  w[n]="controle";      c[n]="contrôle";      n++
  w[n]="role";          c[n]="rôle";          n++
  w[n]="en-tete";       c[n]="en-tête";       n++

  # Cédille
  w[n]="francais";      c[n]="français";      n++
  w[n]="francaise";     c[n]="française";     n++
  w[n]="lecon";         c[n]="leçon";         n++
  w[n]="recu";          c[n]="reçu";          n++
  w[n]="decu";          c[n]="déçu";          n++

  total_words = n
}

# Gestion des blocs de code
/^[[:space:]]*```/ {
  in_code = !in_code
  next
}
in_code { next }

# Ignorer les identifiants techniques YAML : les noms de skills et commandes
# restent volontairement en ASCII pour préserver le déclenchement.
/^[[:space:]]*(name|invoke)[[:space:]]*:/ { next }

{
  line = $0

  # Retirer le code inline (backticks)
  gsub(/`[^`]*`/, " ", line)

  # Retirer les cibles de liens Markdown, en conservant le libellé visible
  gsub(/\]\([^)]*\)/, "]", line)

  # Retirer les URLs
  gsub(/https?:\/\/[^ )\]"]*/, " ", line)

  # Retirer les chemins de fichiers (contenant /)
  gsub(/[a-zA-Z0-9_.~-]+\/[a-zA-Z0-9_.~\/-]+/, " ", line)

  # Convertir en minuscules pour la comparaison
  lower_line = tolower(line)

  # Chercher chaque mot du dictionnaire
  for (i = 0; i < total_words; i++) {
    word = w[i]
    wlen = length(word)
    tmp = lower_line
    pos = 1

    while ((idx = index(tmp, word)) > 0) {
      # Vérifier les limites de mot
      before_ok = 0
      if (idx == 1) {
        before_ok = 1
      } else {
        ch = substr(tmp, idx - 1, 1)
        if (ch !~ /[a-zA-Z]/) before_ok = 1
      }

      after_ok = 0
      after_pos = idx + wlen
      if (after_pos > length(tmp)) {
        after_ok = 1
      } else {
        ch = substr(tmp, after_pos, 1)
        if (ch !~ /[a-zA-Z]/) after_ok = 1
      }

      if (before_ok && after_ok) {
        found = substr(line, pos + idx - 1, wlen)
        results[count] = sprintf("  L.%d : \"%s\" -> \"%s\"", NR, found, c[i])
        count++
      }

      # Avancer après cette occurrence
      tmp = substr(tmp, idx + wlen)
      pos = pos + idx + wlen - 1
    }
  }
}

END {
  if (count > 0) {
    printf "[ACCENTS] %d mot(s) français sans accents dans %s :\n", count, basename
    for (i = 0; i < count; i++) {
      print results[i]
    }
  }
}
' basename="$BASENAME" "$FILE")

if [[ -n "$OUTPUT" ]]; then
  echo "$OUTPUT"
fi

exit 0
