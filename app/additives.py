"""
FoodLens AI - Additive Detection Engine
Detects food additives by E-numbers, INS codes, and standard chemical/functional names.
Maps additives to their regulatory functional classes (Preservative, Emulsifier, Colour, Sweetener, etc.).
"""

import os
import re
import json
from typing import List, Dict, Any, Optional

DATA_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "additives.json")

def load_additives_db() -> List[Dict[str, Any]]:
    if not os.path.exists(DATA_PATH):
        fallback_path = os.path.join(os.path.dirname(__file__), "..", "..", "data", "additives.json")
        if os.path.exists(fallback_path):
            with open(fallback_path, "r", encoding="utf-8") as f:
                return json.load(f)
        return []
    with open(DATA_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def detect_additives(full_text: str, structured_ingredients: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Scans the OCR text and structured ingredients for:
    1. E-numbers (e.g. E211, E330, E322)
    2. INS codes (e.g. INS 211, INS 500(ii), INS 322)
    3. Common additive chemical names (e.g. 'Sodium Benzoate', 'Citric Acid', 'Lecithin')

    Returns identified additives with functional classification and neutral safety notes.
    """
    db = load_additives_db()
    combined_text = full_text + " " + " ".join([i.get("raw_name", "") + " " + i.get("normalized_name", "") for i in structured_ingredients])
    lower_text = combined_text.lower()

    detected: List[Dict[str, Any]] = []
    seen_codes = set()

    # 1. Regex patterns for explicit E and INS numbers
    e_pattern = re.compile(r'\b[eE]\s*([0-9]{3,4}[a-z]?)\b')
    ins_pattern = re.compile(r'\b(?:ins|i\.n\.s\.?)\s*([0-9]{3,4}(?:\([a-z0-9ivx]+\))?[a-z]?)\b', re.IGNORECASE)

    extracted_e_matches = e_pattern.findall(combined_text)
    extracted_ins_matches = ins_pattern.findall(combined_text)

    # Normalize extracted code strings
    raw_found_codes = set()
    for m in extracted_e_matches:
        raw_found_codes.add(m.strip().lower())
    for m in extracted_ins_matches:
        # e.g., '211' or '500(ii)' -> '211', '500'
        code_clean = re.sub(r'\(.*?\)', '', m).strip().lower()
        raw_found_codes.add(code_clean)

    # Match against additive database
    for item in db:
        item_code = item["code"].lower()
        item_ins = item.get("ins", "").lower()
        num_part = re.sub(r'[^0-9]', '', item_code)

        is_matched = False
        matched_by = []

        # Check numeric code matches
        if num_part and num_part in raw_found_codes:
            is_matched = True
            matched_by.append(f"Code match (E{num_part.upper()} / INS {num_part})")
        elif item_ins and item_ins in raw_found_codes:
            is_matched = True
            matched_by.append(f"INS match ({item_ins})")

        # Check common names
        if not is_matched:
            for alias in item.get("common_names", []):
                alias_lower = alias.lower()
                # Use word boundary search
                pattern = r'\b' + re.escape(alias_lower) + r'\b'
                if re.search(pattern, lower_text):
                    is_matched = True
                    matched_by.append(f"Name match: '{alias}'")
                    break

        if is_matched and item["code"] not in seen_codes:
            seen_codes.add(item["code"])
            detected.append({
                "code": item["code"],
                "ins": item.get("ins", ""),
                "name": item["name"],
                "function": item.get("function", "Food Additive"),
                "functional_classes": item.get("functional_classes", [item.get("function")]),
                "origin": item.get("origin", "Synthetic / Natural"),
                "dietary": item.get("dietary", "General"),
                "description": item.get("description", ""),
                "notes": item.get("notes", "Used in accordance with standard good manufacturing practices."),
                "matched_by": ", ".join(matched_by)
            })

    return {
        "detected_additives": detected,
        "total_additives_count": len(detected),
        "additive_functions_summary": list(set([a["function"] for a in detected])),
        "disclaimer": "Additives are approved food ingredients evaluated for technological function and safety within regulated limits."
    }
