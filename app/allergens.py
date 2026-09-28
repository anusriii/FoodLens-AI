"""
FoodLens AI - Allergen Detection Engine
Identifies major allergens (Milk, Wheat, Gluten, Soy, Peanuts, Tree Nuts, Eggs, Fish, Shellfish, Sesame, etc.)
from parsed ingredients and explicit allergen/precautionary statements.
"""

import os
import re
import json
from typing import List, Dict, Any, Tuple

DATA_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "allergens.json")

def load_allergens_db() -> List[Dict[str, Any]]:
    if not os.path.exists(DATA_PATH):
        # Fallback to root data folder if running from root
        fallback_path = os.path.join(os.path.dirname(__file__), "..", "..", "data", "allergens.json")
        if os.path.exists(fallback_path):
            with open(fallback_path, "r", encoding="utf-8") as f:
                return json.load(f)
        return []
    with open(DATA_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def detect_allergens(full_text: str, structured_ingredients: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Detects allergens from:
    1. Direct ingredients list
    2. Explicit 'Contains' or 'Allergen Advice' statements
    3. Precautionary allergen statements ('May contain', 'Processed on equipment that handles...')

    Distinguishes clearly between 'detected', 'possible', and 'no allergen detected'.
    """
    db = load_allergens_db()
    lower_text = full_text.lower()

    detected_allergens: List[Dict[str, Any]] = []
    possible_allergens: List[Dict[str, Any]] = []
    detected_ids = set()
    possible_ids = set()

    # 1. Parse explicit precautionary statements (e.g. "May contain", "Produced in a facility that handles")
    may_contain_patterns = [
        r"(?:may\s+contain|produced\s+in\s+a\s+facility|manufactured\s+in\s+a\s+facility|shared\s+equipment|traces\s+of)[\s\:\-]+([^\.\n]+)",
        r"(?:cross[\-\s]contamination\s+with)[\s\:\-]+([^\.\n]+)"
    ]
    precautionary_text = ""
    for pat in may_contain_patterns:
        match = re.search(pat, lower_text, re.IGNORECASE)
        if match:
            precautionary_text += " " + match.group(1).lower()

    # 2. Parse explicit 'Contains' statements
    contains_patterns = [
        r"(?:contains|allergen\s+advice|allergen\s+declaration|allergen\s+info(?:rmation)?)[\s\:\-]+([^\.\n]+)",
        r"(?:allergens?)[\s\:\-]+([^\.\n]+)"
    ]
    explicit_contains_text = ""
    for pat in contains_patterns:
        match = re.search(pat, lower_text, re.IGNORECASE)
        if match:
            # Exclude match if it was part of "may contain"
            full_match_span = match.span()
            preceding_str = lower_text[max(0, full_match_span[0] - 10):full_match_span[0]]
            if "may " not in preceding_str:
                explicit_contains_text += " " + match.group(1).lower()

    # 3. Check each allergen in the database
    for allergen in db:
        allergen_id = allergen["id"]
        allergen_name = allergen["name"]
        keywords = [allergen_name.lower()] + [alias.lower() for alias in allergen.get("aliases_and_derivatives", [])]
        
        # Word boundary regex pattern for accurate matching
        # Sort keywords by length descending to match longest phrases first
        sorted_kw = sorted(keywords, key=len, reverse=True)
        kw_regex = re.compile(r'\b(' + '|'.join(re.escape(k) for k in sorted_kw) + r')\b', re.IGNORECASE)

        # Check explicit contains text
        if explicit_contains_text and kw_regex.search(explicit_contains_text):
            if allergen_id not in detected_ids:
                detected_ids.add(allergen_id)
                detected_allergens.append({
                    "id": allergen_id,
                    "name": allergen_name,
                    "category": allergen.get("category", "General"),
                    "status": "detected",
                    "evidence_type": "explicit_statement",
                    "source": "Declared in allergen statement ('Contains')",
                    "description": allergen.get("description", ""),
                    "severity": allergen.get("severity", "High")
                })
                continue

        # Check ingredients list
        found_in_ingredient = None
        for ing in structured_ingredients:
            ing_raw = ing.get("raw_name", "")
            ing_norm = ing.get("normalized_name", "")
            ing_combined = f"{ing_raw} {ing_norm}".lower()
            if kw_regex.search(ing_combined):
                found_in_ingredient = ing.get("raw_name") or ing.get("normalized_name")
                break

        if found_in_ingredient:
            if allergen_id not in detected_ids:
                detected_ids.add(allergen_id)
                detected_allergens.append({
                    "id": allergen_id,
                    "name": allergen_name,
                    "category": allergen.get("category", "General"),
                    "status": "detected",
                    "evidence_type": "ingredient_match",
                    "source": f"Identified in ingredient '{found_in_ingredient}'",
                    "description": allergen.get("description", ""),
                    "severity": allergen.get("severity", "High")
                })
                continue

        # Check precautionary statement (May contain)
        if precautionary_text and kw_regex.search(precautionary_text):
            if allergen_id not in detected_ids and allergen_id not in possible_ids:
                possible_ids.add(allergen_id)
                possible_allergens.append({
                    "id": allergen_id,
                    "name": allergen_name,
                    "category": allergen.get("category", "General"),
                    "status": "possible",
                    "evidence_type": "precautionary_statement",
                    "source": "Found in precautionary warning ('May contain' or cross-contact)",
                    "description": allergen.get("description", ""),
                    "severity": allergen.get("severity", "Moderate")
                })

    has_allergens = len(detected_allergens) > 0 or len(possible_allergens) > 0

    return {
        "detected_allergens": detected_allergens,
        "possible_allergens": possible_allergens,
        "total_detected_count": len(detected_allergens),
        "total_possible_count": len(possible_allergens),
        "no_allergen_detected": not has_allergens,
        "disclaimer": "Absence of a detected allergen does not guarantee that the product is allergen-free. Cross-contact or undeclared allergens may be present.",
        "summary": _build_allergen_summary(detected_allergens, possible_allergens)
    }


def _build_allergen_summary(detected: List[Dict[str, Any]], possible: List[Dict[str, Any]]) -> str:
    parts = []
    if detected:
        names = [d["name"] for d in detected]
        parts.append(f"Contains: {', '.join(names)}")
    if possible:
        pnames = [p["name"] for p in possible]
        parts.append(f"May contain (precautionary): {', '.join(pnames)}")
    if not detected and not possible:
        parts.append("No common priority allergens were explicitly detected in the available label text.")
    return " | ".join(parts)
