# FoodLens AI

## AI-Powered Global Food Label Intelligence and Safety Analysis System

FoodLens AI is an end-to-end intelligent food-label analysis web platform that uses **computer vision (OpenCV), PaddleOCR / RapidOCR, NLP, a deterministic regulatory engine, and grounded AI synthesis** to analyze food product labels from uploaded packaging photos.

The user only needs to upload a **photo of a food label (JPG, JPEG, PNG, or WebP)**. The system automatically reads and extracts:
- Ingredients (nested items, percentages, normalized aliases)
- Allergens (confirmed declarations vs precautionary cross-contact statements)
- Additives (E-numbers, INS codes, functional technological roles)
- Nutrition facts panel (preserving per 100g, per 100ml, or per serving basis)
- Serving dimensions and net package quantities
- Country-specific statutory checks (India FSSAI, USA FDA, European Union, UK FSA, Health Canada)
- Interactive consumption intake calculator
- Grounded AI safety explanation & interactive Q&A assistant
- Side-by-side product comparison

---

## 🏗️ System Architecture

```text
               Food Label Image (JPG / JPEG / PNG / WebP)
                               │
                               ▼
                      Image Preprocessing
                 (OpenCV: Contrast, Denoise, Deskew)
                               │
                               ▼
                              OCR
                    (PaddleOCR / RapidOCR)
                               │
                               ▼
                        Extracted Text
                               │
        ┌──────────────────────┼──────────────────────┐
        ▼                      ▼                      ▼
   Ingredients             Nutrition              Allergens
   Extraction              Extraction             Detection
        │                      │                      │
        ▼                      ▼                      ▼
  Normalization           Serving Size &         Confirmed vs
(Aliases & E-Codes)      Intake Calculator      Precautionary
        │
        ▼
    Additives
 (E/INS Numbers)
        │
        └──────────────────────┬──────────────────────┘
                               ▼
                   Global Regulation Engine
               (India, USA, EU, UK, Canada)
                               │
                               ▼
                    AI Explanation & Q&A
               (Grounded Strictly in Facts)
                               │
                               ▼
                    Interactive Dashboard
```

---

## 🚀 Features

1. **Food Label Image Upload**: Validates format (JPG, JPEG, PNG, WebP), limits file size to 15MB, prevents path traversal, and previews the image. Includes a 1-click Demo Sample generator for instant testing.
2. **OpenCV Preprocessing**: Resizing, grayscale conversion, CLAHE contrast enhancement, bilateral filtering, unsharp mask sharpening, and Hough-based deskew rotation correction.
3. **High-Accuracy OCR**: RapidOCR (PaddleOCR PP-OCRv4 ONNX engine) extracting text lines, coordinates, and confidence scores.
4. **Structured Ingredients Extraction**: Parses commas, semicolons, percentages (e.g. `Wheat flour (60%)`), and nested sub-ingredients in parentheses. Strictly applies the rule: *"Quantity: Not mentioned"* when an ingredient percentage is undeclared.
5. **Ingredient Normalization**: Canonical names and aliases mapped against `ingredients.json`.
6. **Allergen Detection**: Detects 9+ major priority allergens (Milk, Wheat, Gluten, Soy, Peanuts, Tree nuts, Eggs, Fish, Shellfish, Sesame, etc.). Clearly separates confirmed detected allergens from precautionary cross-contact warnings (`"May contain"`).
7. **Additives & E-Numbers**: Detects E-numbers, INS codes, and chemical names (e.g. E211, E330, E322, E500) and identifies functional classes (Preservative, Emulsifier, Acidity Regulator, Colour, etc.) using neutral evidence-based wording.
8. **Nutrition Facts Extraction**: Preserves declared basis (`per 100 g`, `per 100 ml`, `per serving`). Extracts Calories, Protein, Total Carbs, Total Sugars, Added Sugars, Fat, Saturated Fat, Trans Fat, Fiber, and Sodium.
9. **Interactive Consumption Calculator**: User enters consumed portion (grams/ml/servings); calculates estimated intake using exact formulas (e.g. `10g / 100g × 35g = 3.5g sugar`).
10. **Global Regulation Checker**: Deterministic Python rule engine checking statutory permissions across India (FSSAI), USA (FDA), European Union (EC), UK (FSA), and Canada (Health Canada).
11. **Cross-Country Comparison Matrix**: View status, permitted limits, and clickable official statutory links for any detected substance.
12. **Label Completeness Meter**: Scores label completeness (0-100%) against 7 regulatory requirements.
13. **Grounded AI Explanation**: Synthesizes structured, non-hallucinatory explanations strictly from extracted facts.
14. **Interactive Label Chat (Q&A)**: Instant grounded answers for questions like *"Does this product contain milk?"* or *"How much sugar in 40g?"*.
15. **Product Comparison Studio**: Factually compare two products side-by-side without subjective marketing bias.

---

## 🛠️ Project Structure

```text
FoodLens AI/
│
├── frontend/
│   ├── public/
│   └── src/
│       ├── components/
│       │   ├── Navbar.jsx
│       │   ├── ImageUploader.jsx
│       │   ├── OverviewCard.jsx
│       │   ├── ExtractedTextCard.jsx
│       │   ├── IngredientsCard.jsx
│       │   ├── AllergensCard.jsx
│       │   ├── AdditivesCard.jsx
│       │   ├── NutritionCard.jsx
│       │   ├── ConsumptionCalculator.jsx
│       │   ├── RegulationTable.jsx
│       │   ├── CompletenessCard.jsx
│       │   ├── AiExplanation.jsx
│       │   ├── LabelChat.jsx
│       │   ├── ProductComparison.jsx
│       │   └── RegulatoryGuide.jsx
│       ├── services/
│       │   └── api.js
│       ├── App.jsx
│       ├── main.jsx
│       └── index.css
│
├── backend/
│   ├── venv/
│   ├── main.py
│   ├── requirements.txt
│   ├── app/
│   │   ├── __init__.py
│   │   ├── ocr.py
│   │   ├── analyzer.py
│   │   ├── allergens.py
│   │   ├── additives.py
│   │   ├── nutrition.py
│   │   ├── regulations.py
│   │   └── ai.py
│   ├── data/
│   │   ├── allergens.json
│   │   ├── additives.json
│   │   ├── ingredients.json
│   │   └── regulations.json
│   └── uploads/
│
├── tests/
│   ├── test_ocr.py
│   ├── test_ingredients.py
│   ├── test_allergens.py
│   ├── test_nutrition.py
│   ├── test_regulations.py
│   └── test_api_integration.py
│
├── .gitignore
└── README.md
```

---

## ⚙️ How to Run the Application

### 1. Start the Backend Server (FastAPI)

Open a terminal in the project directory:

```powershell
cd backend
.\venv\Scripts\Activate.ps1
uvicorn main:app --reload --host 127.0.0.1 --port 8000
```

- Backend API: `http://127.0.0.1:8000`
- Interactive Swagger Documentation: `http://127.0.0.1:8000/docs`

---

### 2. Start the Frontend Application (React + Vite)

Open a second terminal:

```powershell
cd frontend
npm run dev
```

- Open your browser at: `http://localhost:5173`

---

## 🧪 Running Automated Tests

Run the full pytest suite from the project root:

```powershell
.\backend\venv\Scripts\python.exe -m pytest tests/ -v
```

All 13 unit and end-to-end integration tests will run and verify OCR, preprocessing, ingredient extraction, allergen rules, nutrition calculators, regulations engine, WebP support, and API endpoints.

---

## 🔐 Data & Safety Principles

- **No Speculated Quantities**: Missing ingredient quantities return `"Quantity: Not mentioned"`.
- **No Hallucinated Bans**: Regulatory rules are derived deterministically from public statutory registers (FSSAI, FDA, EUR-Lex, FSA, Health Canada). If data is insufficient, status is designated as *"Unknown / Not enough data"*.
- **Allergen Disclaimer**: Absence of detected allergens never implies the product is completely allergen-free.
- **Security**: Uploaded files use random UUIDs to eliminate path traversal, strict file-type whitelists, and 15MB file size limits.

AI-powered food label analyzer for ingredients, allergens, additives, nutrition, and regulations.

