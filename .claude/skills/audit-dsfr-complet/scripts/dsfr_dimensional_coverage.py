#!/usr/bin/env python3
"""Construit une couverture DSFR dimensionnelle pour une page de campagne."""
import json
import re
from pathlib import Path
from typing import Any

SKILLS_ROOT=Path(__file__).resolve().parents[2]
RULES_PATH=SKILLS_ROOT/"audit-dsfr-complet/rules/dsfr-rules.json"
STATE_FAMILIES={"navigation","mega_menu","modal","consent","consent_manager","consent_service","display","search","skiplink","tile","breadcrumb","share"}
KEYBOARD_FAMILIES={"navigation","mega_menu","modal","consent","consent_manager","display","search","skiplink","button","button_group","link","tile","card","tag","radio","input","breadcrumb","share"}
INTERACTIVE=KEYBOARD_FAMILIES|STATE_FAMILIES|{"enlarge_link","follow"}
PARTIAL={"A_RETESTER","GENERIC_CAPTURE_ONLY","HUMAN_REVIEW_PARTIAL","PROTOCOL_EXECUTED_PARTIAL","RULE_EXECUTED_PARTIAL","REFERENCE_INDISPONIBLE"}
LEGACY_CLASSES={"fr-btn--flickr","fr-col-md-auto","fr-consent-banner__content","fr-footer__content-item","fr-link__mega_menu","fr-mega-menu__category-no-list","fr-tile--grow"}


def build(root: Path, page_id: str) -> dict[str, Any]:
    root=root.resolve();lower=page_id.lower();rules=json.loads(RULES_PATH.read_text(encoding="utf-8"))["rules"]
    page=json.loads((root/f"dsfr/pages/{page_id}.json").read_text(encoding="utf-8"));proof_rel=f"preuves-{lower}-complet/{page_id}-COLLECTE-COMPLETE.json";collect=json.loads((root/proof_rel).read_text(encoding="utf-8"));class_counts=collect["inventory"]["classes"]
    generic=[f"preuves-{lower}-complet/desktop-initial.png",f"preuves-{lower}-complet/portrait.png",f"preuves-{lower}-complet/landscape.png"]
    rule_text={rule["rule_id"]:" ".join([rule.get("selector",""),rule.get("expected_html","")]+[str(condition.get("selector","")) for condition in rule["conditions"]]) for rule in rules}
    class_rows=[]
    for token,count in sorted(class_counts.items()):
        ids=[rule_id for rule_id,text in rule_text.items() if re.search(rf"(?<![\w-])\.?{re.escape(token)}(?![\w-])",text)]
        class_rows.append({"class":token,"instances":count,"rules":ids,"coverage_status":"RULE_TARGETED" if ids else "INVENTORIED_NOT_TARGETED","reference_status":"REFERENCE_INDISPONIBLE" if token in LEGACY_CLASSES else "REFERENCE_1_14_4_SEULEMENT"})
    family_rows=[]
    for family in page["inventory"]:
        name=family["name"];executed=family.get("rules_executed",[]);dimensions={
            "structure":{"status":"RULE_EXECUTED" if executed else "A_RETESTER","evidence":[f"dsfr/pages/{page_id}.json"] if executed else []},
            "semantics":{"status":"RULE_EXECUTED_PARTIAL" if executed else "A_RETESTER","evidence":[f"dsfr/pages/{page_id}.json"] if executed else []},
            "content_and_variant":{"status":"HUMAN_REVIEW_PARTIAL","evidence":generic},
            "responsive":{"status":"PROTOCOL_EXECUTED_PARTIAL","evidence":generic+[proof_rel]},
            "state":{"status":"PROTOCOL_EXECUTED_PARTIAL" if name in STATE_FAMILIES else ("NON_APPLICABLE_STATIC" if name not in INTERACTIVE else "A_RETESTER"),"evidence":[proof_rel] if name in STATE_FAMILIES else []},
            "keyboard":{"status":"PROTOCOL_EXECUTED_PARTIAL" if name in KEYBOARD_FAMILIES else ("NON_APPLICABLE_STATIC" if name not in INTERACTIVE else "A_RETESTER"),"evidence":[proof_rel] if name in KEYBOARD_FAMILIES else []},
            "reference_version":{"status":"REFERENCE_INDISPONIBLE","evidence":[f"dsfr/pages/{page_id}.json"]}}
        incomplete=[key for key,value in dimensions.items() if value["status"] in PARTIAL]
        family_rows.append({"component":name,"instances":family["count"],"rules":executed,"automated_status":family["status"],"dimensions":dimensions,"incomplete_dimensions":incomplete,"coverage_complete":not incomplete})
    summary={"observed_fr_classes":len(class_rows),"class_associations":sum(row["instances"] for row in class_rows),"classes_targeted_by_rule":sum(row["coverage_status"]=="RULE_TARGETED" for row in class_rows),"classes_inventory_only":sum(row["coverage_status"]=="INVENTORIED_NOT_TARGETED" for row in class_rows),"detected_families":len(family_rows),"families_with_complete_multidimensional_coverage":sum(row["coverage_complete"] for row in family_rows),"families_with_remaining_dimensions":sum(not row["coverage_complete"] for row in family_rows),"catalog_rules":len(rules)}
    result={"schema_version":1,"page":page["page"],"claim":"Cette matrice inventorie la couverture observée. Elle ne déclare aucune conformité DSFR globale.","versions":{"observed":"1.13.2 déclarée par la campagne","target":"1.15.2","exact_observed_reference_available":False,"exact_target_component_corpus_available":False},"summary":summary,"families":family_rows,"classes":class_rows,"remaining_protocols":["Référence officielle exacte 1.13.2 et artefact cible 1.15.2","Lecteurs d’écran réels","Consentement: révocation et contrôle effectif des traceurs","Modales: fond inerte, clic extérieur et scroll","Thèmes: fidélité visuelle et contrastes dans les états clair, sombre et système","Mégamenus et composants à tous les breakpoints","États hover, focus, active, disabled et erreur par variante"]}
    json_path=root/f"dsfr/{page_id}-COUVERTURE-DIMENSIONNELLE.json";md_path=json_path.with_suffix(".md");json_path.write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    labels={"observed_fr_classes":"Classes fr-* observées","class_associations":"Associations classe-élément","classes_targeted_by_rule":"Classes citées par au moins une règle","classes_inventory_only":"Classes seulement inventoriées","detected_families":"Familles détectées","families_with_complete_multidimensional_coverage":"Familles à couverture multidimensionnelle complète","families_with_remaining_dimensions":"Familles avec dimensions restantes","catalog_rules":"Règles du catalogue"}
    lines=[f"# Couverture dimensionnelle DSFR {page_id}","","Aucune conformité DSFR globale n’est revendiquée.","","## Synthèse","","| Indicateur | Valeur |","|---|---:|",*[f"| {labels[key]} | {value} |" for key,value in summary.items()],"","## Familles et dimensions","","| Famille | Instances | Règles | Dimensions restant partielles |","|---|---:|---|---|"]
    for row in family_rows:lines.append(f"| {row['component']} | {row['instances']} | {', '.join(row['rules']) or 'aucune'} | {', '.join(row['incomplete_dimensions']) or 'aucune'} |")
    lines += ["","## Classes seulement inventoriées",""]+[f"- {row['class']} - {row['instances']} instance(s)" for row in class_rows if row["coverage_status"]=="INVENTORIED_NOT_TARGETED"]
    md_path.write_text("\n".join(lines)+"\n",encoding="utf-8");return result


if __name__=="__main__":
    import sys
    if len(sys.argv)!=3:raise SystemExit("Usage: dsfr_dimensional_coverage.py CAMPAIGN_ROOT PAGE_ID")
    print(json.dumps(build(Path(sys.argv[1]),sys.argv[2])["summary"],ensure_ascii=False))
