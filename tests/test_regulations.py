import pytest
from app.regulations import evaluate_regulations

def test_regulations_evaluation_e211():
    additives = [
        {"name": "Sodium Benzoate", "code": "E211", "ins": "211", "function": "Preservative"}
    ]
    ingredients = []

    res = evaluate_regulations(additives, ingredients)
    assert len(res["supported_countries"]) == 5
    assert len(res["comparison_table"]) == 1

    row = res["comparison_table"][0]
    assert row["substance"] == "Sodium Benzoate"
    assert "India" in row["countries"]
    assert "USA" in row["countries"]
    assert "European Union" in row["countries"]
    assert row["countries"]["India"]["status"] in ["Restricted", "Allowed"]
    assert "fssai.gov.in" in row["countries"]["India"]["source"].lower()
