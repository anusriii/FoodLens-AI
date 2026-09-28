"""
FoodLens AI - Country-Specific Regulation Engine
Rule-based evaluation of additives and ingredients across India (FSSAI), USA (FDA),
European Union (EFSA/EC), UK (FSA), and Canada (Health Canada).
NOTE: Uses deterministic structured data. No LLM decision-making for regulatory legality.
"""

import os
import json
from typing import List, Dict, Any, Optional

DATA_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "regulations.json")

SUPPORTED_COUNTRIES = ["India", "USA", "European Union", "UK", "Canada"]

def load_regulations_db() -> List[Dict[str, Any]]:
    if not os.path.exists(DATA_PATH):
        fallback_path = os.path.join(os.path.dirname(__file__), "..", "..", "data", "regulations.json")
        if os.path.exists(fallback_path):
            with open(fallback_path, "r", encoding="utf-8") as f:
                return json.load(f)
        return []
    with open(DATA_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def evaluate_regulations(detected_additives: List[Dict[str, Any]], detected_ingredients: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Evaluates regulatory compliance status for all detected additives and ingredients
    across the 5 target countries using the structured database.
    """
    db = load_regulations_db()

    # Collect unique identifiers (E-numbers, INS codes, standard names)
    targets_to_check = []
    seen = set()

    for item in detected_additives:
        key = item.get("name", "").strip().lower()
        if key and key not in seen:
            seen.add(key)
            targets_to_check.append({
                "name": item.get("name"),
                "code": item.get("code"),
                "ins": item.get("ins"),
                "type": "additive"
            })

    for item in detected_ingredients:
        key = item.get("normalized_name", "").strip().lower()
        if key and key not in seen:
            seen.add(key)
            targets_to_check.append({
                "name": item.get("normalized_name"),
                "code": item.get("additive_code"),
                "ins": None,
                "type": "ingredient"
            })

    country_reports: Dict[str, List[Dict[str, Any]]] = {c: [] for c in SUPPORTED_COUNTRIES}
    comparison_table: List[Dict[str, Any]] = []

    for target in targets_to_check:
        t_name = target["name"]
        t_code = (target["code"] or "").upper()
        t_ins = (target["ins"] or "")

        row: Dict[str, Any] = {
            "substance": t_name,
            "code": t_code or "N/A",
            "countries": {}
        }

        for country in SUPPORTED_COUNTRIES:
            match = _find_rule(db, country, t_name, t_code, t_ins)
            if match:
                eval_entry = {
                    "substance": t_name,
                    "code": t_code,
                    "country": country,
                    "jurisdiction": match.get("jurisdiction", "Food Authority"),
                    "status": match.get("status", "Unknown / Not enough data"),
                    "food_category": match.get("food_category", "General"),
                    "max_permitted_level": match.get("max_permitted_level"),
                    "unit": match.get("unit", "GMP"),
                    "conditions_of_use": match.get("conditions_of_use", ""),
                    "effective_date": match.get("effective_date", "N/A"),
                    "regulation_version": match.get("regulation_version", ""),
                    "official_source_url": match.get("official_source_url", ""),
                    "notes": match.get("notes", "")
                }
            else:
                eval_entry = {
                    "substance": t_name,
                    "code": t_code,
                    "country": country,
                    "jurisdiction": _get_default_jurisdiction(country),
                    "status": "Unknown / Not enough data",
                    "food_category": "Unspecified",
                    "max_permitted_level": None,
                    "unit": None,
                    "conditions_of_use": "Unable to determine regulatory status from the available label information.",
                    "effective_date": "N/A",
                    "regulation_version": "N/A",
                    "official_source_url": _get_default_source_url(country),
                    "notes": "No specific category or numerical concentration declared on label to determine strict statutory threshold."
                }

            country_reports[country].append(eval_entry)
            row["countries"][country] = {
                "status": eval_entry["status"],
                "max_level": f"{eval_entry['max_permitted_level']} {eval_entry['unit']}" if eval_entry['max_permitted_level'] is not None else (eval_entry['unit'] or "Not specified"),
                "jurisdiction": eval_entry["jurisdiction"],
                "source": eval_entry["official_source_url"]
            }

        comparison_table.append(row)

    return {
        "supported_countries": SUPPORTED_COUNTRIES,
        "country_reports": country_reports,
        "comparison_table": comparison_table,
        "rule_engine_disclaimer": "Regulatory statuses are derived deterministically from official public statutory databases. If exact food category or concentration is missing from label, status is designated as 'Unknown / Not enough data' rather than speculated."
    }


def _find_rule(db: List[Dict[str, Any]], country: str, name: str, code: str, ins: str) -> Optional[Dict[str, Any]]:
    name_clean = name.strip().lower()
    code_clean = code.strip().upper()
    ins_clean = ins.strip()

    for rule in db:
        if rule.get("country", "").lower() != country.lower():
            continue

        r_ing = rule.get("ingredient", "").lower()
        r_code = rule.get("additive_code", "").upper()
        r_ins = rule.get("ins", "")

        # Code match (e.g. E211)
        if code_clean and r_code and code_clean == r_code:
            return rule
        # INS match
        if ins_clean and r_ins and ins_clean == r_ins:
            return rule
        # Name match
        if name_clean and r_ing and (name_clean in r_ing or r_ing in name_clean):
            return rule

    return None


def _get_default_jurisdiction(country: str) -> str:
    mapping = {
        "India": "FSSAI (Food Safety and Standards Authority of India)",
        "USA": "US FDA (Food and Drug Administration)",
        "European Union": "European Commission / EFSA",
        "UK": "UK Food Standards Agency (FSA)",
        "Canada": "Health Canada"
    }
    return mapping.get(country, "National Food Safety Authority")


def _get_default_source_url(country: str) -> str:
    mapping = {
        "India": "https://www.fssai.gov.in/",
        "USA": "https://www.fda.gov/food",
        "European Union": "https://food.ec.europa.eu/safety_en",
        "UK": "https://www.food.gov.uk/",
        "Canada": "https://www.canada.ca/en/health-canada/services/food-nutrition.html"
    }
    return mapping.get(country, "#")
