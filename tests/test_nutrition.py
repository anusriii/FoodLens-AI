import pytest
from app.nutrition import extract_nutrition, calculate_consumption

def test_nutrition_extraction_and_basis():
    text = """
    NUTRITIONAL FACTS (Per 100g)
    Energy: 480 kcal
    Protein: 7.5 g
    Carbohydrates: 68.0 g
    Total Sugars: 24.0 g
    Total Fat: 19.5 g
    Sodium: 350 mg
    Serving size: 25 g
    Net weight: 200 g
    """
    lines = [{"text": l.strip()} for l in text.strip().split("\n")]
    res = extract_nutrition(text, lines)

    assert res["nutrition_table_detected"] is True
    assert res["declared_basis"] == "per 100 g"
    assert res["serving_size"]["value"] == 25.0
    assert res["net_quantity"]["value"] == 200.0

    nutrients = res["nutrients"]
    assert nutrients["energy_kcal"]["value"] == 480.0
    assert nutrients["total_sugars"]["value"] == 24.0
    assert nutrients["protein"]["value"] == 7.5

def test_consumption_calculator():
    nutrition_dict = {
        "declared_basis": "per 100 g",
        "nutrients": {
            "total_sugars": {"label": "Total Sugars", "value": 10.0, "unit": "g"},
            "energy_kcal": {"label": "Energy", "value": 400.0, "unit": "kcal"}
        }
    }
    # Consuming 35 g
    # 10 / 100 * 35 = 3.5 g sugar
    # 400 / 100 * 35 = 140 kcal
    calc = calculate_consumption(nutrition_dict, consumed_amount=35.0, consumed_unit="g")
    assert "calculated_nutrients" in calc
    calc_sugar = calc["calculated_nutrients"]["total_sugars"]["consumed_value"]
    calc_energy = calc["calculated_nutrients"]["energy_kcal"]["consumed_value"]
    assert calc_sugar == 3.5
    assert calc_energy == 140.0
