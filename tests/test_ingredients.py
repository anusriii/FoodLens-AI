import pytest
from app.analyzer import extract_and_structure_ingredients

def test_extract_simple_ingredients():
    sample_text = "Ingredients: Wheat flour, sugar, palm oil, milk powder, soy lecithin, salt"
    result = extract_and_structure_ingredients(sample_text, [])
    assert result["has_ingredients"] is True
    assert result["count"] >= 5

    names = [i["normalized_name"] for i in result["structured_ingredients"]]
    assert "Wheat Flour" in names
    assert "Sugar" in names

def test_nested_ingredients_and_percentages():
    sample_text = "INGREDIENTS: Wheat flour (65%), Vegetable Oil (Palm oil, Sunflower oil), Sugar, Emulsifier (INS 322), Salt"
    result = extract_and_structure_ingredients(sample_text, [])
    assert result["has_ingredients"] is True

    items = result["structured_ingredients"]
    wheat = next((i for i in items if "wheat" in i["raw_name"].lower()), None)
    assert wheat is not None
    assert wheat["quantity"] == "65%"

    # Check unmentioned quantity rule
    sugar = next((i for i in items if "sugar" in i["raw_name"].lower()), None)
    assert sugar is not None
    assert sugar["quantity"] == "Quantity: Not mentioned"
