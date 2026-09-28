import pytest
from app.allergens import detect_allergens

def test_detect_allergens_from_ingredients():
    ingredients = [
        {"raw_name": "Wheat flour", "normalized_name": "Wheat Flour"},
        {"raw_name": "Milk solids", "normalized_name": "Milk Powder"},
        {"raw_name": "Soy lecithin", "normalized_name": "Lecithin"}
    ]
    text = "Ingredients: Wheat flour, Milk solids, Soy lecithin, Sugar"
    result = detect_allergens(text, ingredients)

    assert result["no_allergen_detected"] is False
    detected_ids = [a["id"] for a in result["detected_allergens"]]
    assert "wheat" in detected_ids
    assert "milk" in detected_ids
    assert "soy" in detected_ids

def test_detect_precautionary_statement():
    text = "Ingredients: Sugar, Cocoa butter.\nMay contain traces of peanuts and tree nuts."
    result = detect_allergens(text, [])

    possible_ids = [p["id"] for p in result["possible_allergens"]]
    assert "peanuts" in possible_ids or "tree_nuts" in possible_ids
    assert "Absence of a detected allergen" in result["disclaimer"]
