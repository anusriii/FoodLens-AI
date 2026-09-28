"""
FoodLens AI - AI Explanation & Grounded Q&A Engine
Generates human-readable summaries and answers user questions strictly based on
structured analysis results (ingredients, allergens, additives, nutrition, regulations).
Includes an intelligent deterministic grounded generator and optional LLM integration.
"""

import os
import re
from typing import Dict, Any, List, Optional

def generate_label_explanation(analysis_result: Dict[str, Any]) -> Dict[str, Any]:
    """
    Produces structured, easy-to-understand explanations of:
    - Key ingredients & functions
    - Detected allergens & safety guidance
    - Additives & technical roles
    - Nutritional profile breakdown
    - Regulatory status implications
    - Data uncertainties & missing metrics
    """
    ingredients_data = analysis_result.get("ingredients", {})
    allergens_data = analysis_result.get("allergens", {})
    additives_data = analysis_result.get("additives", {})
    nutrition_data = analysis_result.get("nutrition", {})
    regulations_data = analysis_result.get("regulations", {})
    completeness = analysis_result.get("completeness", {})

    ingredients = ingredients_data.get("structured_ingredients", [])
    detected_allergens = allergens_data.get("detected_allergens", [])
    possible_allergens = allergens_data.get("possible_allergens", [])
    additives = additives_data.get("detected_additives", [])
    nutrients = nutrition_data.get("nutrients", {})

    sections = []

    # 1. Product & Ingredients Overview
    if ingredients:
        top_ing = [i["normalized_name"] for i in ingredients[:5]]
        sections.append({
            "title": "Ingredients Breakdown",
            "summary": f"This product formulation contains {len(ingredients)} identified ingredient(s). Primary components include {', '.join(top_ing)}.",
            "details": [
                f"• {i['normalized_name']}: {i['purpose']} (Quantity declared: {i['quantity']})"
                for i in ingredients[:6]
            ]
        })
    else:
        sections.append({
            "title": "Ingredients Breakdown",
            "summary": "No explicit ingredients list could be extracted from this photo.",
            "details": ["Ensure the photo captures the entire 'Ingredients:' statement clearly."]
        })

    # 2. Allergen Risk Analysis
    if detected_allergens or possible_allergens:
        det_names = [a["name"] for a in detected_allergens]
        pos_names = [p["name"] for p in possible_allergens]
        det_text = f"Confirmed present: {', '.join(det_names)}" if det_names else "None confirmed in direct declaration."
        pos_text = f"Precautionary cross-contact risk: {', '.join(pos_names)}" if pos_names else "No precautionary cross-contact detected."
        sections.append({
            "title": "Allergen Advisory",
            "summary": f"Allergen warnings identified. {det_text}. {pos_text}.",
            "details": [
                f"• {a['name']}: {a['source']} ({a['severity']})" for a in detected_allergens
            ] + [
                f"• {p['name']} (Precautionary): {p['source']}" for p in possible_allergens
            ]
        })
    else:
        sections.append({
            "title": "Allergen Advisory",
            "summary": "No common priority allergens were detected in the visible label text.",
            "details": ["Always consult physical packaging packaging in case of severe anaphylactic allergies."]
        })

    # 3. Additives & Functional Roles
    if additives:
        sections.append({
            "title": "Additives & E-Numbers",
            "summary": f"{len(additives)} authorized additive(s) identified across technological classes: {', '.join(additives_data.get('additive_functions_summary', []))}.",
            "details": [
                f"• {a['code']} ({a['name']}): Acts as a {a['function']}. {a['notes']}" for a in additives
            ]
        })
    else:
        sections.append({
            "title": "Additives & E-Numbers",
            "summary": "No explicit E-numbers or chemical additive codes were detected in the visible text.",
            "details": ["The product may use traditional culinary ingredients or additives declared under colloquial names."]
        })

    # 4. Nutritional Insights
    nut_details = []
    energy = nutrients.get("energy_kcal")
    sugar = nutrients.get("total_sugars")
    fat = nutrients.get("total_fat")
    protein = nutrients.get("protein")
    sodium = nutrients.get("sodium")

    if energy and energy.get("value") is not None:
        nut_details.append(f"• Energy: {energy['value']} {energy['unit']} per {energy['basis']}")
    if sugar and sugar.get("value") is not None:
        nut_details.append(f"• Sugar content: {sugar['value']} {sugar['unit']} per {sugar['basis']}")
    if fat and fat.get("value") is not None:
        nut_details.append(f"• Total Fat: {fat['value']} {fat['unit']} per {fat['basis']}")
    if protein and protein.get("value") is not None:
        nut_details.append(f"• Protein: {protein['value']} {protein['unit']} per {protein['basis']}")
    if sodium and sodium.get("value") is not None:
        nut_details.append(f"• Sodium: {sodium['value']} {sodium['unit']} per {sodium['basis']}")

    if nut_details:
        sections.append({
            "title": "Nutritional Profile Interpretation",
            "summary": f"Nutritional information declared on a '{nutrition_data.get('declared_basis', 'per 100g')}' basis.",
            "details": nut_details
        })
    else:
        sections.append({
            "title": "Nutritional Profile Interpretation",
            "summary": "A nutrition facts table was not clearly identified in this label segment.",
            "details": ["Ensure the nutrition table panel is facing the camera in good lighting."]
        })

    # 5. Regulatory Status Summary
    comp_table = regulations_data.get("comparison_table", [])
    if comp_table:
        reg_details = []
        for item in comp_table[:4]:
            statuses = [f"{c}: {info['status']}" for c, info in item["countries"].items()]
            reg_details.append(f"• {item['substance']} ({item['code']}): {', '.join(statuses)}")
        sections.append({
            "title": "Global Regulatory Harmonization",
            "summary": f"Evaluated across India (FSSAI), USA (FDA), EU, UK, and Canada statutory databases.",
            "details": reg_details
        })

    # 6. Uncertainties / Missing Data
    missing_items = [c["name"] for c in completeness.get("criteria", []) if c["status"] == "Not detected"]
    if missing_items:
        sections.append({
            "title": "Label Completeness & Information Gaps",
            "summary": f"Label completeness evaluated at {completeness.get('completeness_score', 0)}% ({completeness.get('overall_status')}).",
            "details": [f"• Missing from photo: {item}" for item in missing_items]
        })

    return {
        "summary_paragraphs": sections,
        "disclaimer": "This explanation is automatically synthesized from optical label extraction and official food databases. It is provided for educational purposes and should not be used as medical or definitive legal advice."
    }


def answer_label_question(question: str, analysis_result: Dict[str, Any]) -> Dict[str, Any]:
    """
    Answers user queries grounded strictly on the extracted label facts:
    Examples:
    - "Does this product contain milk?"
    - "What preservatives are present?"
    - "Why is E211 used?"
    - "How much sugar would I consume if I ate 40 g?"
    - "What ingredients are allergens?"
    """
    q_lower = question.lower().strip()
    ingredients = analysis_result.get("ingredients", {}).get("structured_ingredients", [])
    allergens = analysis_result.get("allergens", {})
    additives = analysis_result.get("additives", {}).get("detected_additives", [])
    nutrition = analysis_result.get("nutrition", {})
    regulations = analysis_result.get("regulations", {})

    # 1. Allergen queries: "contain milk", "contain gluten", "peanut", "allergen"
    if any(k in q_lower for k in ["milk", "gluten", "wheat", "soy", "peanut", "egg", "fish", "nuts", "allergen", "allergens"]):
        detected = [a["name"] for a in allergens.get("detected_allergens", [])]
        possible = [p["name"] for p in allergens.get("possible_allergens", [])]
        
        # Check specific allergen mentioned
        for target in ["milk", "wheat", "gluten", "soy", "peanut", "tree nuts", "egg", "fish", "shellfish"]:
            if target in q_lower:
                is_det = any(target in d.lower() for d in detected)
                is_pos = any(target in p.lower() for p in possible)
                if is_det:
                    return {
                        "question": question,
                        "answer": f"Yes, {target.title()} is detected in this product. It was identified based on the extracted label declaration or ingredient list.",
                        "category": "allergen_inquiry",
                        "grounded": True
                    }
                elif is_pos:
                    return {
                        "question": question,
                        "answer": f"This product may contain traces of {target.title()} due to a precautionary manufacturer warning (cross-contamination statement).",
                        "category": "allergen_inquiry",
                        "grounded": True
                    }
                else:
                    return {
                        "question": question,
                        "answer": f"{target.title()} was NOT detected in the visible label text. Note: Absence of detection does not guarantee the product is completely allergen-free.",
                        "category": "allergen_inquiry",
                        "grounded": True
                    }

        # General allergen query
        if detected or possible:
            ans = f"Detected allergens: {', '.join(detected) if detected else 'None'}. Precautionary warnings: {', '.join(possible) if possible else 'None'}."
        else:
            ans = "No priority allergens were identified in the readable text on this label."
        return {
            "question": question,
            "answer": ans,
            "category": "allergen_inquiry",
            "grounded": True
        }

    # 2. Additive queries: "preservatives", "additives", "e211", "e330", "ins"
    if any(k in q_lower for k in ["preservative", "preservatives", "additive", "additives", "e-number", "ins", "e211", "e330", "e322", "e621"]):
        if "preservative" in q_lower:
            preservatives = [a for a in additives if "preservative" in a["function"].lower() or any("preservative" in fc.lower() for fc in a.get("functional_classes", []))]
            if preservatives:
                names = [f"{p['name']} ({p['code']})" for p in preservatives]
                return {
                    "question": question,
                    "answer": f"The following preservative(s) were detected: {', '.join(names)}. Function: Inhibits microbial spoilage and extends shelf-life.",
                    "category": "additive_inquiry",
                    "grounded": True
                }
            else:
                return {
                    "question": question,
                    "answer": "No specific chemical preservatives were detected in the extracted label text.",
                    "category": "additive_inquiry",
                    "grounded": True
                }

        # Specific code lookup e.g. "e211" or "e330"
        code_match = re.search(r'\b(e\s*[0-9]{3,4}[a-z]?|ins\s*[0-9]{3,4})\b', q_lower)
        if code_match:
            code_str = code_match.group(1).replace(" ", "").upper()
            matched_add = next((a for a in additives if a["code"].upper() == code_str or a["ins"] in code_str), None)
            if matched_add:
                return {
                    "question": question,
                    "answer": f"{matched_add['code']} is {matched_add['name']}. It is used as a {matched_add['function']}. {matched_add['description']} {matched_add['notes']}",
                    "category": "additive_inquiry",
                    "grounded": True
                }

        if additives:
            names = [f"{a['name']} ({a['code']} - {a['function']})" for a in additives]
            return {
                "question": question,
                "answer": f"The following food additives were identified: {'; '.join(names)}.",
                "category": "additive_inquiry",
                "grounded": True
            }
        else:
            return {
                "question": question,
                "answer": "No food additives (E-numbers or INS codes) were identified in this label.",
                "category": "additive_inquiry",
                "grounded": True
            }

    # 3. Consumption calculation query: e.g. "how much sugar if I eat 40g"
    amount_match = re.search(r'([0-9]+(?:\.[0-9]+)?)\s*(?:g|gm|grams)', q_lower)
    if amount_match and any(n in q_lower for n in ["sugar", "calories", "protein", "fat", "sodium"]):
        consumed_amt = float(amount_match.group(1))
        nutrients = nutrition.get("nutrients", {})
        basis = nutrition.get("declared_basis", "per 100 g")

        factor = consumed_amt / 100.0 if "100" in basis else 1.0

        if "sugar" in q_lower and nutrients.get("total_sugars") and nutrients["total_sugars"].get("value") is not None:
            sugar_100 = nutrients["total_sugars"]["value"]
            calc_val = round(sugar_100 * factor, 2)
            return {
                "question": question,
                "answer": f"Based on the declared value of {sugar_100} g sugar per {basis}, consuming {consumed_amt} g provides approximately {calc_val} g of sugar ({sugar_100} / 100 × {consumed_amt} = {calc_val} g).",
                "category": "consumption_calculation",
                "grounded": True
            }

        if "calorie" in q_lower or "energy" in q_lower:
            en = nutrients.get("energy_kcal")
            if en and en.get("value") is not None:
                calc_val = round(en["value"] * factor, 2)
                return {
                    "question": question,
                    "answer": f"Consuming {consumed_amt} g provides approximately {calc_val} kcal (calculated from {en['value']} kcal per {basis}).",
                    "category": "consumption_calculation",
                    "grounded": True
                }

    # 4. Default grounded fallback
    return {
        "question": question,
        "answer": f"Based on the extracted label facts: {len(ingredients)} ingredient(s), {len(additives)} additive(s), and {len(allergens.get('detected_allergens', []))} confirmed allergen(s) were recorded. Feel free to ask specifically about allergens, sugar/calories for an amount consumed, or specific additives.",
        "category": "general_grounded",
        "grounded": True
    }
