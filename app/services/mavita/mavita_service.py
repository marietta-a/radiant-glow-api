import json
import uuid
import time
from typing import List, Dict, Any
from fastapi import HTTPException
from app.config import logger
from google.genai import types
from app.config import mavita_model, genAiClient, image_content_config
from app.models.mavita.mavita_payloads import UserProfile;

def analyze_meal_image(base64_image: bytes, mime_type: str, profile: UserProfile):
    start = time.time()
    
    # Define the response schema for structured JSON output
    response_schema = {
        "type": "object",
        "properties": {
            "isFood": {"type": "boolean"},
            "foodName": {"type": "string"},
            "description": {"type": "string"},
            "glycemicScore": {"type": "number"},
            "iIndexScore": {"type": "number"},
            "portionAnalysis": {"type": "string"},
            "macronutrients": {
                "type": "object",
                "properties": {
                    "protein": {"type": "string"},
                    "carbs": {"type": "string"},
                    "fats": {"type": "string"},
                    "fiber": {"type": "string"}
                }
            },
            "biologicalPathways": {"type": "array", "items": {"type": "string"}},
            "pairingSuggestions": {"type": "array", "items": {"type": "string"}},
            "nutrients": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "name": {"type": "string"},
                        "benefit": {"type": "string"}
                    }
                }
            },
            "goalAlignment": {"type": "string"},
            "healthRisks": {"type": "string"}
        },
        "required": ["isFood", "foodName", "description", "glycemicScore", "iIndexScore", "portionAnalysis", "macronutrients", "biologicalPathways", "pairingSuggestions", "nutrients", "goalAlignment", "healthRisks"]
    }
    goals_str = ", ".join(profile.goals)
    primary_goal = profile.goals[0]

    prompt = f"""
    ACT AS: Clinical Bio-Nutritional Scientist.
    CONTEXT: User goals: {goals_str}.
    
    TASK: Analyze meal image for biological impact.
    
    STRICT RULES:
    1. Be concise. Accuracy is critical.
    2. Only identify nutrients verified in identified ingredients.
    3. If not food, set isFood to false.
    
    DATA SCHEMA:
    1. isFood: Boolean.
    2. foodName: Clear ID.
    3. glycemicScore: 1-10.
    4. iIndexScore: 0-100 (Inflammation).
    5. description: 1-sentence metabolic summary.
    6. portionAnalysis: Macro balance.
    7. macronutrients: Gram estimates (Protein, Carbs, Fats, Fiber).
    8. biologicalPathways: Mechanistic tags (e.g., Sirtuin, GLP-1).
    9. pairingSuggestions: Science-backed improvements.
    10. nutrients: 2-3 key micros + benefits.
    11. goalAlignment: Link to {primary_goal}.
    12. healthRisks: Mandatory metabolic triggers (High sodium, trans fats, etc).
    NOTE: The output should use the folloiwng template: {response_schema}
    """


    try:
        contents = [
            types.Content(
                role="user",
                parts=[
                    types.Part.from_text(text=prompt),
                    types.Part.from_bytes(
                        mime_type=mime_type,
                        data=base64_image,
                    )
                ],
            ),
        ]

        response = genAiClient.models.generate_content(
            model=mavita_model,
            contents=contents,
            config= image_content_config
        )
        
        # Parse the JSON response string into a Python dictionary
        result_dict = json.loads(response.text)
        
        end = time.time()
        elapsed = end - start

        print(f"Elapsed time: {elapsed} seconds")
        
        return result_dict

    except Exception as e:
        print(f"Clinical Interpretation Error: {e}")
        raise Exception("Precision mismatch. Please capture a clearer, well-lit image.")

def generate_longevity_plate(goal: str, cuisine: str) -> List[Dict[str, Any]]:
    start = time.time()
    recipe_schema = {
        "type": "array",
        "items": {
            "type": "object",
            "properties": {
                "title": {"type": "string"},
                "ingredients": {"type": "array", "items": {"type": "string"}},
                "instructions": {"type": "array", "items": {"type": "string"}},
                "biologicalBenefits": {"type": "string"}
            },
            "required": ["title", "ingredients", "instructions", "biologicalBenefits"]
        }
    }

    prompt = f"As a Medical Nutritionist, generate 3 clinical recipes for '{goal}' in '{cuisine}' style. Focus on metabolic synergy and biological longevity. The output should use the folloiwng template: '{recipe_schema}'"

    try:
        contents = [
            types.Content(
                role="user",
                parts=[
                    types.Part.from_text(text=prompt),
                ],
            ),
        ]

        generate_content_config = types.GenerateContentConfig(
            thinking_config=types.ThinkingConfig(thinking_budget=0),
            response_mime_type="application/json",
        )

        logger.info('genAI config completed')

        response = genAiClient.models.generate_content(
            model=mavita_model,
            contents=contents,
            config= generate_content_config
        )
        
        # Parse the JSON response string into a Python dictionary
        result_dict = json.loads(response.text)
        
        end = time.time()
        elapsed = end - start

        print(f"Elapsed time: {elapsed} seconds")
        
        return result_dict
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

def generate_bio_report(meals: List[Dict[str, Any]], profile: Dict[str, Any]) -> str:
    start = time.time()
    
    # Format the meal history for the prompt
    history_items = []
    for m in meals[:10]:
        history_items.append(f"- {m.get('foodName')}: Glycemic {m.get('glycemicScore')}, Inflammatory {m.get('iIndexScore')}")
    history_text = "\n".join(history_items)
    
    prompt = (
        f"Generate a Clinical Metabolic Report for {profile.get('name')} (Age: {profile.get('age')}) "
        f"based on these recent meals:\n{history_text}\n"
        f"Provide actionable healthspan advice based on their goals: {', '.join(profile.get('goals', []))}."
    )


    try:
        contents = [
            types.Content(
                role="user",
                parts=[
                    types.Part.from_text(text=prompt),
                ],
            ),
        ]

        generate_content_config = types.GenerateContentConfig(
            thinking_config=types.ThinkingConfig(thinking_budget=0),
            response_mime_type="application/json",
        )

        logger.info('genAI config completed')

        response = genAiClient.models.generate_content(
            model=mavita_model,
            contents=contents,
            config=generate_content_config
        )
        
        # Parse the JSON response string into a Python dictionary
        result_dict = json.loads(response.text)
        
        end = time.time()
        elapsed = end - start

        print(f"Elapsed time: {elapsed} seconds")
        
        return result_dict
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))