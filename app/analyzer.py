"""
FoodLens AI - Central Analyzer & Label Intelligence Pipeline
Coordinates OCR text extraction, ingredient parsing, allergen detection,
additive identification, nutrition parsing, regulatory checks, and completeness validation.
"""

import os
import re
import json
from typing import Dict, Any, List, Optional, Tuple

from app.ocr import extract_text
from app.allergens import detect_allergens
from app.additives import detect_additives
from app.nutrition import extract_nutrition
from app.regulations import evaluate_regulations

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")

def load_ingredients_db() -> List[Dict[str, Any]]:
    path = os.path.join(DATA_DIR, "ingredients.json")
    if not os.path.exists(path):
        fallback = os.path.join(os.path.dirname(__file__), "..", "..", "data", "ingredients.json")
        if os.path.exists(fallback):
            with open(fallback, "r", encoding="utf-8") as f:
                return json.load(f)
        return []
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def analyze_food_label_image(image_path: str) -> Dict[str, Any]:
    """
    Core end-to-end pipeline:
    1. Preprocess & OCR image
    2. Extract and structure ingredients
    3. Detect allergens (direct + precautionary)
    4. Detect additives and functional classes
    5. Extract nutritional panel, serving size, net quantity
    6. Evaluate statutory regulations across 5 countries
    7. Check label completeness
    """
    # Step 1: OCR
    ocr_result = extract_text(image_path)
    full_text = ocr_result["full_text"]
    lines = ocr_result["lines"]

    # Step 2: Extract Ingredients
    ingredients_data = extract_and_structure_ingredients(full_text, lines)

    # Step 3: Detect Allergens
    allergens_data = detect_allergens(full_text, ingredients_data["structured_ingredients"])

    # Step 4: Detect Additives
    additives_data = detect_additives(full_text, ingredients_data["structured_ingredients"])

    # Step 5: Extract Nutrition & Serving Size
    nutrition_data = extract_nutrition(full_text, lines)

    # Step 6: Regulation Engine
    regulations_data = evaluate_regulations(
        additives_data["detected_additives"],
        ingredients_data["structured_ingredients"]
    )

    # Step 7: Check Label Completeness
    completeness_data = evaluate_label_completeness(
        full_text=full_text,
        has_ingredients=ingredients_data["has_ingredients"],
        has_nutrition=nutrition_data["nutrition_table_detected"],
        has_serving_size=nutrition_data["serving_size"]["detected"],
        has_net_quantity=nutrition_data["net_quantity"]["detected"],
        has_allergens=not allergens_data["no_allergen_detected"]
    )

    return {
        "status": "success",
        "ocr": ocr_result,
        "ingredients": ingredients_data,
        "allergens": allergens_data,
        "additives": additives_data,
        "nutrition": nutrition_data,
        "regulations": regulations_data,
        "completeness": completeness_data
    }


def extract_and_structure_ingredients(full_text: str, lines: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Locates the ingredient block in label text and parses items cleanly,
    handling commas, semicolons, nested parentheses, percentages, and aliases.
    """
    ingredients_db = load_ingredients_db()

    raw_ingredient_text = _locate_ingredient_block(full_text)
    has_ingredients = bool(raw_ingredient_text.strip())

    items = _split_ingredient_items(raw_ingredient_text) if has_ingredients else []
    structured_items: List[Dict[str, Any]] = []

    for item_str in items:
        cleaned_item = item_str.strip()
        if not cleaned_item or len(cleaned_item) < 2:
            continue

        # Extract percentage if declared, e.g. "Wheat Flour (65%)" or "Sugar 20%"
        pct_match = re.search(r'([0-9]+(?:\.[0-9]+)?)\s*%', cleaned_item)
        if pct_match:
            quantity_str = f"{pct_match.group(1)}%"
        else:
            # Mandatory rule: If quantity is not present, return "Quantity: Not mentioned"
            quantity_str = "Quantity: Not mentioned"

        # Check for nested sub-ingredients in parentheses
        nested_match = re.search(r'\((.*?)\)', cleaned_item)
        sub_ingredients = []
        if nested_match:
            inside = nested_match.group(1).strip()
            # Split inside by commas or semicolons
            sub_items = [s.strip() for s in re.split(r'[,;]', inside) if s.strip()]
            sub_ingredients = sub_items

        # Clean name for matching
        base_name = re.sub(r'\(.*?\)', '', cleaned_item)
        base_name = re.sub(r'[0-9]+(?:\.[0-9]+)?\s*%', '', base_name).strip(" :.-,")

        # Match against ingredients database
        matched_info = _match_ingredient(base_name, ingredients_db)

        structured_items.append({
            "raw_name": cleaned_item,
            "cleaned_name": base_name,
            "normalized_name": matched_info.get("standard_name", base_name.title()),
            "category": matched_info.get("category", "General Food Ingredient"),
            "purpose": matched_info.get("purpose", "Component of food product formulation"),
            "quantity": quantity_str,
            "sub_ingredients": sub_ingredients,
            "additive_code": matched_info.get("additive_code"),
            "allergen_relationship": matched_info.get("allergen_relationship"),
            "dietary": matched_info.get("dietary", "General"),
            "concerns": matched_info.get("concerns", "No specific safety concern at standard dietary intake.")
        })

    return {
        "has_ingredients": has_ingredients,
        "raw_text": raw_ingredient_text if has_ingredients else "Ingredient list not detected in the image.",
        "count": len(structured_items),
        "structured_ingredients": structured_items
    }


def _locate_ingredient_block(full_text: str) -> str:
    """Finds the text following 'INGREDIENTS:' or similar header."""
    headers = [
        r"(?:ingredients?|ingrédients?|ingrediente|सामग्री|घटक)[\s\:\-]+",
        r"\b(?:contains\s+ingredients?)[\s\:\-]+"
    ]

    for h in headers:
        m = re.search(h, full_text, re.IGNORECASE)
        if m:
            start_pos = m.end()
            remaining = full_text[start_pos:]
            
            # Find end of ingredient block: typically stopped by Nutrition, Allergen info, Mfg, etc.
            stop_headers = [
                r"\n\s*(?:nutrition|nutritional|allergen|contains\s*:|manufactured|mfg|best\s+before|storage|net\s+wt|m\.r\.p)",
                r"\n\s*\n"
            ]
            min_stop = len(remaining)
            for sh in stop_headers:
                sm = re.search(sh, remaining, re.IGNORECASE)
                if sm and sm.start() < min_stop:
                    min_stop = sm.start()

            block = remaining[:min_stop].replace("\n", " ").strip()
            return block

    return ""


def _split_ingredient_items(text: str) -> List[str]:
    """Splits ingredients by commas or semicolons outside of balanced parentheses."""
    items = []
    current = []
    depth = 0

    for char in text:
        if char == '(':
            depth += 1
            current.append(char)
        elif char == ')':
            if depth > 0:
                depth -= 1
            current.append(char)
        elif (char == ',' or char == ';') and depth == 0:
            item = "".join(current).strip()
            if item:
                items.append(item)
            current = []
        else:
            current.append(char)

    last_item = "".join(current).strip()
    if last_item:
        items.append(last_item)

    return items


def _match_ingredient(name: str, db: List[Dict[str, Any]]) -> Dict[str, Any]:
    name_lower = name.lower().strip()
    for item in db:
        if name_lower == item["standard_name"].lower():
            return item
        for alias in item.get("aliases", []):
            if name_lower == alias.lower() or alias.lower() in name_lower:
                return item
    return {}


def evaluate_label_completeness(
    full_text: str,
    has_ingredients: bool,
    has_nutrition: bool,
    has_serving_size: bool,
    has_net_quantity: bool,
    has_allergens: bool
) -> Dict[str, Any]:
    """
    Evaluates presence of mandatory and advisory labelling components:
    - Ingredient list
    - Nutrition information
    - Serving size
    - Net quantity
    - Allergen information
    - Manufacturer information
    - Date / Lot code
    """
    lower = full_text.lower()

    # Manufacturer / brand / distributor
    mfg_patterns = [r"\b(?:manufactured|mfg|packed|marketed|distributed|lic(?:ence)?|license|fssai|corp|ltd|llc|inc)\b"]
    has_mfg = any(bool(re.search(p, lower)) for p in mfg_patterns)

    # Date / lot / batch
    date_patterns = [r"\b(?:best\s+before|expiry|exp|use\s+by|mfg\s+date|batch|lot|pkg)\b"]
    has_date = any(bool(re.search(p, lower)) for p in date_patterns)

    criteria = [
        {"name": "Ingredient List", "status": "Detected" if has_ingredients else "Not detected", "weight": 25},
        {"name": "Nutrition Table", "status": "Detected" if has_nutrition else "Not detected", "weight": 25},
        {"name": "Serving Size", "status": "Detected" if has_serving_size else "Not detected", "weight": 10},
        {"name": "Net Quantity", "status": "Detected" if has_net_quantity else "Not detected", "weight": 10},
        {"name": "Allergen Declaration", "status": "Detected" if has_allergens else "Not detected", "weight": 10},
        {"name": "Manufacturer Information", "status": "Detected" if has_mfg else "Not detected", "weight": 10},
        {"name": "Date / Lot Information", "status": "Detected" if has_date else "Not detected", "weight": 10}
    ]

    total_weight = sum(c["weight"] for c in criteria)
    earned_weight = sum(c["weight"] for c in criteria if c["status"] == "Detected")
    score_percentage = int((earned_weight / total_weight) * 100)

    if score_percentage >= 80:
        overall_status = "Complete"
    elif score_percentage >= 40:
        overall_status = "Partially complete"
    else:
        overall_status = "Missing / Incomplete"

    return {
        "overall_status": overall_status,
        "completeness_score": score_percentage,
        "criteria": criteria,
        "disclaimer": "Completeness evaluation is based on OCR optical detection within the uploaded image boundary and does not constitute statutory legal verification."
    }
