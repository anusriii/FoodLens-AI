"""
FoodLens AI - Backend Main Application
FastAPI Server providing complete REST endpoints for food label processing,
OCR extraction, safety analysis, consumption calculation, regulatory checks, and grounded Q&A.
"""

import os
import sys
import uuid
import shutil
from typing import Dict, Any, Optional
from fastapi import FastAPI, File, UploadFile, HTTPException, Query, Body
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

# Ensure app package is discoverable
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.analyzer import analyze_food_label_image
from app.nutrition import calculate_consumption
from app.ai import generate_label_explanation, answer_label_question

UPLOAD_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)

ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp"}
MAX_FILE_SIZE = 15 * 1024 * 1024  # 15 MB

app = FastAPI(
    title="FoodLens AI API",
    description="AI-Powered Global Food Label Intelligence and Safety Analysis System",
    version="1.0.0"
)

# CORS setup
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows frontend from Vite dev server and local network
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve static uploaded files for preview in UI
app.mount("/uploads", StaticFiles(directory=UPLOAD_DIR), name="uploads")


# Pydantic Request Models
class ConsumptionRequest(BaseModel):
    nutrition: Dict[str, Any]
    consumed_amount: float = Field(..., gt=0, description="Amount consumed by user")
    unit: str = Field(default="g", description="Unit of measurement: g or ml")
    serving_size_val: Optional[float] = Field(default=None, description="Serving size if available")


class ChatRequest(BaseModel):
    question: str = Field(..., min_length=2, description="User question about the food label")
    analysis: Dict[str, Any] = Field(..., description="Full analysis result of the product")


class CompareRequest(BaseModel):
    product_a: Dict[str, Any]
    product_b: Dict[str, Any]


@app.get("/")
def root():
    return {
        "project": "FoodLens AI",
        "description": "AI-Powered Global Food Label Intelligence and Safety Analysis System",
        "status": "online",
        "docs": "/docs"
    }


@app.get("/health")
def health_check():
    return {"status": "healthy", "service": "foodlens-ai-backend"}


@app.post("/api/analyze")
async def analyze_label_endpoint(file: UploadFile = File(...)):
    """
    Primary endpoint: Upload food label image (JPG, JPEG, PNG, or WebP).
    Validates file, preprocesses image, runs OCR, extracts ingredients, allergens,
    additives, nutrition, runs 5-country regulation engine, and generates AI explanation.
    """
    # 1. Validate filename and extension
    original_filename = file.filename or "uploaded_label.jpg"
    ext = os.path.splitext(original_filename)[1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file format '{ext}'. Please upload JPG, JPEG, PNG, or WEBP."
        )

    # 2. Secure file writing with UUID to prevent path traversal
    file_id = str(uuid.uuid4())
    safe_filename = f"{file_id}{ext}"
    saved_image_path = os.path.join(UPLOAD_DIR, safe_filename)

    try:
        content = await file.read()
        if len(content) > MAX_FILE_SIZE:
            raise HTTPException(
                status_code=413,
                detail="File size exceeds maximum permitted limit of 15MB."
            )
        if len(content) < 100:
            raise HTTPException(
                status_code=400,
                detail="Uploaded file is too small or empty."
            )

        with open(saved_image_path, "wb") as f:
            f.write(content)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save uploaded image: {str(e)}")

    # 3. Execute Analysis Pipeline
    try:
        analysis_result = analyze_food_label_image(saved_image_path)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis pipeline error: {str(e)}")

    # 4. Generate Grounded AI Explanation
    explanation = generate_label_explanation(analysis_result)
    analysis_result["ai_explanation"] = explanation

    # 5. Attach Public Preview URLs
    analysis_result["image_urls"] = {
        "original": f"/uploads/{safe_filename}",
        "preprocessed": f"/uploads/{file_id}_preprocessed.jpg" if os.path.exists(os.path.join(UPLOAD_DIR, f"{file_id}_preprocessed.jpg")) else None,
        "filename": original_filename
    }

    return analysis_result


@app.post("/api/calculate-consumption")
def calculate_consumption_endpoint(payload: ConsumptionRequest):
    """Calculates nutrient intake based on user specified consumed amount."""
    try:
        result = calculate_consumption(
            nutrition_dict=payload.nutrition,
            consumed_amount=payload.consumed_amount,
            consumed_unit=payload.unit,
            serving_size_val=payload.serving_size_val
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/api/chat")
def chat_about_label_endpoint(payload: ChatRequest):
    """Answers questions regarding the analyzed product grounded in extracted facts."""
    try:
        answer_data = answer_label_question(payload.question, payload.analysis)
        return answer_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/compare")
def compare_products_endpoint(payload: CompareRequest):
    """Compares two analyzed food products factually across ingredients, nutrition, and regulations."""
    a = payload.product_a
    b = payload.product_b

    # Nutrition comparison
    nutrients_a = a.get("nutrition", {}).get("nutrients", {})
    nutrients_b = b.get("nutrition", {}).get("nutrients", {})
    all_keys = set(list(nutrients_a.keys()) + list(nutrients_b.keys()))

    nut_comp = []
    for k in all_keys:
        val_a = nutrients_a.get(k, {}) if nutrients_a.get(k) else {}
        val_b = nutrients_b.get(k, {}) if nutrients_b.get(k) else {}
        nut_comp.append({
            "nutrient_key": k,
            "label": val_a.get("label") or val_b.get("label", k),
            "product_a": val_a.get("value"),
            "product_b": val_b.get("value"),
            "unit": val_a.get("unit") or val_b.get("unit", "")
        })

    # Allergens comparison
    allergens_a = [x["name"] for x in a.get("allergens", {}).get("detected_allergens", [])]
    allergens_b = [x["name"] for x in b.get("allergens", {}).get("detected_allergens", [])]

    # Additives comparison
    additives_a = [f"{x['name']} ({x['code']})" for x in a.get("additives", {}).get("detected_additives", [])]
    additives_b = [f"{x['name']} ({x['code']})" for x in b.get("additives", {}).get("detected_additives", [])]

    return {
        "nutrition_comparison": nut_comp,
        "allergens_a": allergens_a,
        "allergens_b": allergens_b,
        "additives_a": additives_a,
        "additives_b": additives_b,
        "summary": "Factual comparison presented without subjective commercial endorsement."
    }
