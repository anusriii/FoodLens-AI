import os
import io
import cv2
import numpy as np
import pytest
from fastapi.testclient import TestClient

from backend.main import app

client = TestClient(app)

def create_synthetic_label_image():
    # Create high-resolution label image
    img = np.ones((800, 1100, 3), dtype=np.uint8) * 255

    # Header
    cv2.putText(img, "DELUXE CRUNCH BISCUITS", (40, 60), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 0, 0), 2)

    # Ingredients
    cv2.putText(img, "INGREDIENTS: Wheat flour (60%), Sugar, Palm oil,", (40, 120), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 2)
    cv2.putText(img, "Skimmed milk powder, Soy lecithin (INS 322),", (40, 160), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 2)
    cv2.putText(img, "Preservative (INS 211), Iodized salt.", (40, 200), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 2)

    # Allergen Statement
    cv2.putText(img, "CONTAINS: Wheat, Milk, Soy.", (40, 260), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 180), 2)
    cv2.putText(img, "May contain traces of Peanuts.", (40, 300), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 180), 2)

    # Nutrition Table
    cv2.putText(img, "NUTRITION FACTS (Per 100g):", (40, 370), cv2.FONT_HERSHEY_SIMPLEX, 0.75, (0, 0, 0), 2)
    cv2.putText(img, "Energy: 460 kcal", (40, 420), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 2)
    cv2.putText(img, "Protein: 7.2 g", (40, 460), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 2)
    cv2.putText(img, "Total Carbohydrate: 66.0 g", (40, 500), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 2)
    cv2.putText(img, "Total Sugars: 21.0 g", (40, 540), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 2)
    cv2.putText(img, "Total Fat: 18.0 g", (450, 420), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 2)
    cv2.putText(img, "Sodium: 310 mg", (450, 460), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 2)

    # Dimensions
    cv2.putText(img, "Serving Size: 25 g | Net Quantity: 200 g", (40, 620), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (50, 50, 50), 2)

    _, encoded = cv2.imencode(".png", img)
    return io.BytesIO(encoded.tobytes())

def test_health_endpoint():
    res = client.get("/health")
    assert res.status_code == 200
    assert res.json()["status"] == "healthy"

def test_analyze_endpoint_end_to_end():
    image_bytes = create_synthetic_label_image()
    files = {"file": ("test_label.png", image_bytes, "image/png")}

    res = client.post("/api/analyze", files=files)
    assert res.status_code == 200
    data = res.json()

    assert data["status"] == "success"
    assert "ocr" in data
    assert data["ocr"]["line_count"] > 0

    # Ingredients verification
    ing_names = [i["normalized_name"] for i in data["ingredients"]["structured_ingredients"]]
    assert any("wheat" in n.lower() for n in ing_names)

    # Allergens verification
    allergens = data["allergens"]
    det_ids = [a["id"] for a in allergens["detected_allergens"]]
    assert "wheat" in det_ids or "milk" in det_ids or "soy" in det_ids

    # Additives verification (INS 211 / INS 322)
    additives = data["additives"]["detected_additives"]
    assert len(additives) > 0

    # Regulations verification (5 countries)
    assert len(data["regulations"]["supported_countries"]) == 5

    # Completeness verification
    assert data["completeness"]["completeness_score"] > 50

    # Grounded AI explanation
    assert "summary_paragraphs" in data["ai_explanation"]

def test_chat_endpoint():
    sample_analysis = {
        "ingredients": {"structured_ingredients": [{"normalized_name": "Wheat Flour"}, {"normalized_name": "Sugar"}]},
        "allergens": {"detected_allergens": [{"name": "Milk", "source": "Declared on label", "severity": "High"}]},
        "additives": {"detected_additives": [{"name": "Sodium Benzoate", "code": "E211", "function": "Preservative"}]},
        "nutrition": {"nutrients": {"total_sugars": {"label": "Total Sugars", "value": 20.0, "unit": "g"}}},
        "regulations": {}
    }

    res = client.post("/api/chat", json={
        "question": "Does this product contain milk?",
        "analysis": sample_analysis
    })
    assert res.status_code == 200
    assert "Milk is detected" in res.json()["answer"]

def test_analyze_webp_image():
    from PIL import Image
    # Create synthetic RGB image and save into WEBP bytes
    pil_img = Image.new("RGB", (700, 300), color=(255, 255, 255))
    webp_io = io.BytesIO()
    pil_img.save(webp_io, format="WEBP")
    webp_io.seek(0)

    files = {"file": ("food_label.webp", webp_io, "image/webp")}
    res = client.post("/api/analyze", files=files)
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "success"
    assert "ocr" in data
