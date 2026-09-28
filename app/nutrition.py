"""
FoodLens AI - Nutrition & Serving Size Extraction & Calculator
Extracts nutritional panel metrics, serving size, and net quantity.
Computes consumption calculations for custom amounts consumed.
"""

import re
from typing import Dict, Any, List, Optional, Tuple

NUTRIENT_DEFINITIONS = [
    {
        "key": "energy_kcal",
        "label": "Energy / Calories",
        "patterns": [
            r"(?:energy|calories|caloric\s+value|calorie)[\s\:\-]+([0-9]+(?:\.[0-9]+)?)\s*(?:kcal|cal|k\s*cal)?",
            r"([0-9]+(?:\.[0-9]+)?)\s*(?:kcal|calories)\b"
        ],
        "default_unit": "kcal"
    },
    {
        "key": "energy_kj",
        "label": "Energy (kJ)",
        "patterns": [
            r"(?:energy)[\s\:\-]+([0-9]+(?:\.[0-9]+)?)\s*(?:kj|k\s*j)\b",
            r"([0-9]+(?:\.[0-9]+)?)\s*(?:kj|k\s*j)\b"
        ],
        "default_unit": "kJ"
    },
    {
        "key": "protein",
        "label": "Protein",
        "patterns": [
            r"(?:protein|total\s+protein)[\s\:\-]+([0-9]+(?:\.[0-9]+)?)\s*(?:g|gm|grams)?\b",
        ],
        "default_unit": "g"
    },
    {
        "key": "carbohydrates",
        "label": "Total Carbohydrates",
        "patterns": [
            r"(?:total\s+carbohydrate|carbohydrates?|total\s+carbs?|carbs?)[\s\:\-]+([0-9]+(?:\.[0-9]+)?)\s*(?:g|gm|grams)?\b",
        ],
        "default_unit": "g"
    },
    {
        "key": "total_sugars",
        "label": "Total Sugars",
        "patterns": [
            r"(?:total\s+sugars?|sugars?|sugar)[\s\:\-]+([0-9]+(?:\.[0-9]+)?)\s*(?:g|gm|grams)?\b",
        ],
        "default_unit": "g"
    },
    {
        "key": "added_sugars",
        "label": "Added Sugars",
        "patterns": [
            r"(?:added\s+sugars?|incl(?:udes?)?\s+[0-9\.]+\s*g?\s*added\s+sugars?|added\s+sugar)[\s\:\-]+([0-9]+(?:\.[0-9]+)?)\s*(?:g|gm)?\b",
            r"(?:includes|including)\s*([0-9]+(?:\.[0-9]+)?)\s*(?:g|gm)?\s*(?:added\s+sugars?)"
        ],
        "default_unit": "g"
    },
    {
        "key": "total_fat",
        "label": "Total Fat",
        "patterns": [
            r"(?:total\s+fat|fat|lipids)[\s\:\-]+([0-9]+(?:\.[0-9]+)?)\s*(?:g|gm|grams)?\b",
        ],
        "default_unit": "g"
    },
    {
        "key": "saturated_fat",
        "label": "Saturated Fat",
        "patterns": [
            r"(?:saturated\s+fat|saturated\s+fatty\s+acids|saturates)[\s\:\-]+([0-9]+(?:\.[0-9]+)?)\s*(?:g|gm|grams)?\b",
        ],
        "default_unit": "g"
    },
    {
        "key": "trans_fat",
        "label": "Trans Fat",
        "patterns": [
            r"(?:trans\s+fat|trans\s+fatty\s+acids)[\s\:\-]+([0-9]+(?:\.[0-9]+)?)\s*(?:g|gm|grams)?\b",
        ],
        "default_unit": "g"
    },
    {
        "key": "fiber",
        "label": "Dietary Fiber",
        "patterns": [
            r"(?:dietary\s+fiber|dietary\s+fibre|fibre|fiber)[\s\:\-]+([0-9]+(?:\.[0-9]+)?)\s*(?:g|gm|grams)?\b",
        ],
        "default_unit": "g"
    },
    {
        "key": "sodium",
        "label": "Sodium",
        "patterns": [
            r"(?:sodium|na)[\s\:\-]+([0-9]+(?:\.[0-9]+)?)\s*(?:mg|milligrams|g)?\b",
        ],
        "default_unit": "mg"
    },
    {
        "key": "salt",
        "label": "Salt (NaCl)",
        "patterns": [
            r"(?:salt|sodium\s+chloride)[\s\:\-]+([0-9]+(?:\.[0-9]+)?)\s*(?:g|mg)?\b",
        ],
        "default_unit": "g"
    }
]


def extract_nutrition(full_text: str, lines: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Extracts structured nutrition facts, serving size, net quantity,
    and detects the basis of declaration (per 100g, per 100ml, per serving).
    """
    cleaned_text = "\n".join([line["text"] for line in lines]) if lines else full_text
    lower_text = cleaned_text.lower()

    # 1. Detect Basis
    declared_basis = "per 100 g"
    if "per 100 ml" in lower_text or "per 100ml" in lower_text:
        declared_basis = "per 100 ml"
    elif "per 100 g" in lower_text or "per 100g" in lower_text or "approx per 100g" in lower_text:
        declared_basis = "per 100 g"
    elif "per serving" in lower_text or "amount per serving" in lower_text:
        declared_basis = "per serving"

    # 2. Extract Serving Size
    serving_size_info = _extract_serving_size(cleaned_text)

    # 3. Extract Net Quantity / Package Weight
    net_quantity = _extract_net_quantity(cleaned_text)

    # 4. Extract Nutrients
    extracted_nutrients: Dict[str, Any] = {}
    found_any_nutrient = False

    for nutrient in NUTRIENT_DEFINITIONS:
        key = nutrient["key"]
        val, unit = _find_nutrient_value(cleaned_text, nutrient["patterns"], nutrient["default_unit"])
        if val is not None:
            extracted_nutrients[key] = {
                "label": nutrient["label"],
                "value": val,
                "unit": unit,
                "basis": declared_basis
            }
            found_any_nutrient = True
        else:
            extracted_nutrients[key] = None

    return {
        "nutrients": extracted_nutrients,
        "declared_basis": declared_basis,
        "serving_size": serving_size_info,
        "net_quantity": net_quantity,
        "nutrition_table_detected": found_any_nutrient,
        "notes": "Values reflect declared quantities on the physical packaging label."
    }


def _find_nutrient_value(text: str, patterns: List[str], default_unit: str) -> Tuple[Optional[float], str]:
    """Scans line by line to prevent cross-nutrient false positive capture."""
    lines = text.split("\n")
    for line in lines:
        for pat in patterns:
            match = re.search(pat, line, re.IGNORECASE)
            if match:
                try:
                    val_str = match.group(1)
                    val = float(val_str)
                    
                    # Detect unit in the line if present
                    unit = default_unit
                    line_lower = line.lower()
                    if "mg" in line_lower and "sodium" in line_lower:
                        unit = "mg"
                    elif "kcal" in line_lower:
                        unit = "kcal"
                    elif "kj" in line_lower:
                        unit = "kJ"
                    elif "g" in line_lower or "gm" in line_lower:
                        unit = "g"

                    return val, unit
                except (ValueError, IndexError):
                    continue
    return None, default_unit


def _extract_serving_size(text: str) -> Dict[str, Any]:
    """Detects declared serving size (e.g. 30g, 1 cookie (25g), 250ml)."""
    patterns = [
        r"(?:serving\s+size|serve\s+size)[\s\:\-]+([0-9]+(?:\.[0-9]+)?)\s*(g|gm|ml|grams?|ml\b)",
        r"(?:serving\s+size|serve\s+size)[\s\:\-]+([^\.\n]+)",
        r"(?:approx(?:\.|\s+)?serving\s+size)[\s\:\-]+([0-9]+(?:\.[0-9]+)?)\s*(g|gm|ml)"
    ]
    for pat in patterns:
        m = re.search(pat, text, re.IGNORECASE)
        if m:
            raw_val = m.group(0).strip()
            # Try to parse numerical value
            num_match = re.search(r'([0-9]+(?:\.[0-9]+)?)\s*(g|gm|ml|grams?)', raw_val, re.IGNORECASE)
            if num_match:
                val = float(num_match.group(1))
                unit = "ml" if "ml" in num_match.group(2).lower() else "g"
                return {
                    "raw_text": raw_val,
                    "value": val,
                    "unit": unit,
                    "detected": True
                }
            return {
                "raw_text": raw_val,
                "value": None,
                "unit": "g",
                "detected": True
            }

    return {
        "raw_text": "Serving size: Not mentioned",
        "value": None,
        "unit": "g",
        "detected": False
    }


def _extract_net_quantity(text: str) -> Dict[str, Any]:
    """Extracts declared net package quantity (e.g., 500 g, 1 kg, 250 ml)."""
    patterns = [
        r"(?:net\s+weight|net\s+wt|net\s+quantity|net\s+qty|net\s+content)[\s\:\-]+([0-9]+(?:\.[0-9]+)?)\s*(kg|g|gm|grams?|ml|l|litres?|liters?)",
        r"\b([0-9]+(?:\.[0-9]+)?)\s*(?:g|gm|grams?|kg|ml|l)\s*(?:net\s*wt|net)?\b"
    ]
    for pat in patterns:
        m = re.search(pat, text, re.IGNORECASE)
        if m:
            val_str = m.group(1)
            unit_str = m.group(2).lower() if len(m.groups()) > 1 and m.group(2) else "g"
            try:
                val = float(val_str)
                # Standardize units
                if unit_str in ["kg", "kilogram", "kilograms"]:
                    val = val * 1000
                    unit_str = "g"
                elif unit_str in ["l", "litre", "liter", "litres", "liters"]:
                    val = val * 1000
                    unit_str = "ml"
                elif unit_str in ["gm", "grams", "gram"]:
                    unit_str = "g"

                return {
                    "raw_text": m.group(0).strip(),
                    "value": val,
                    "unit": unit_str,
                    "detected": True
                }
            except ValueError:
                continue

    return {
        "raw_text": "Net quantity: Not mentioned",
        "value": None,
        "unit": "g",
        "detected": False
    }


def calculate_consumption(
    nutrition_dict: Dict[str, Any],
    consumed_amount: float,
    consumed_unit: str = "g",
    serving_size_val: Optional[float] = None
) -> Dict[str, Any]:
    """
    Computes consumed nutrients based on user amount:
    Example: 10g sugar / 100g * 35g consumed = 3.5g sugar.
    """
    if consumed_amount <= 0:
        return {"error": "Consumed amount must be greater than zero."}

    calculated_results: Dict[str, Any] = {}

    nutrients = nutrition_dict.get("nutrients", {})
    basis = nutrition_dict.get("declared_basis", "per 100 g")

    # Ratio factor relative to 100g or serving
    ratio = 1.0
    if "100" in basis:
        ratio = consumed_amount / 100.0
    elif "serving" in basis and serving_size_val and serving_size_val > 0:
        ratio = consumed_amount / serving_size_val
    else:
        # Fallback assume per 100g
        ratio = consumed_amount / 100.0

    for key, data in nutrients.items():
        if data and data.get("value") is not None:
            original_val = data["value"]
            consumed_val = round(original_val * ratio, 2)
            calculated_results[key] = {
                "label": data["label"],
                "consumed_value": consumed_val,
                "original_value": original_val,
                "unit": data["unit"],
                "basis": f"Consumed {consumed_amount} {consumed_unit}"
            }

    return {
        "amount_consumed": consumed_amount,
        "unit": consumed_unit,
        "calculated_nutrients": calculated_results,
        "calculation_basis": f"Calculated from {basis} using factor {round(ratio, 4)}"
    }
