# To run this code you need to install the following dependencies:
# pip install google-genai
import json
from app.config import logger
from google.genai import types
from app.config import genAiClient, model_lite
from fastapi import HTTPException
from app.models.meal_plan_payload import MealPlanPayload

async def generate_meal_plan(payload: MealPlanPayload):
    
    cuisineMessage = f'The cuisine preference is {payload.country}'
    if(payload.state):
        cuisineMessage += f', specifically from the state of {payload.state}'
    if(payload.city):
        cuisineMessage += f', and the city of {payload.city}'
    
    prompt = f'''
You are an expert nutritionist, a world cuisine specialist, a recipe developer, and a data structuring AI. Your task is to generate a daily meal plan with multiple options for each meal, structured as a single, valid JSON object, tailored to the user's specific health, culinary, and precise macronutrient goals.

User Inputs:
Daily Caloric Target: {payload.calories} kcal
Daily Macronutrient Targets:
    Carbohydrates: {payload.carbs} g
    Protein: {payload.protein} g
    Fat: {payload.fat} g
Health Goal Name: {payload.healthGoal}
Health Goal Description: {payload.promptDescription}
Number of Suggestions per Meal: {payload.numberOfSuggestions}
{cuisineMessage}

Output Constraints & Instructions:
Main Structure: The root of the output must be a single JSON object with three keys: "breakfast", "lunch", and "dinner". The value for each key must be an array containing exactly {payload.numberOfSuggestions} distinct meal suggestion objects.

Daily Plan Structure & Macro Targets (CRITICAL):
    Overall Goal: The sum of macros for any combination of one breakfast, one lunch, and one dinner should closely approximate the user's daily targets ({payload.carbs}g Carbs, {payload.protein}g Protein, {payload.fat}g Fat).
    Strategic Macro Distribution: Each individual meal option must be designed to fit into a balanced daily structure. Adhere to this nutritional strategy:
        Breakfast: Focus on sustained energy and fiber. This meal should be higher in complex carbohydrates and moderate in protein.
        Lunch: Emphasize lean protein and vegetables for satiety and muscle support. This meal should be the highest in protein.
        Dinner: Design lighter, nutrient-rich meals. This meal should be moderate in protein and lighter on carbohydrates and fats, making it easier to digest.

Cuisine and Health Goal Synthesis:
    Authenticity: All meal suggestions—including their names, ingredients, and recipes—MUST be authentic to the specified Cuisine Preference.
    Alignment: Simultaneously, each meal must align with the Health Goal by using traditional ingredients rich in the nutrients mentioned in the Health Goal Description.
    Justification: The `explanation` field must justify the meal choice by connecting its authentic ingredients to both the health goal and its role in the daily macro plan.

Variety and Cultural Nuance: Ensure the {payload.numberOfSuggestions} options for each meal are distinct and culturally appropriate for the specified cuisine.

JSON Template Adherence: Every single meal suggestion object MUST strictly follow the structure and data types provided in the template below.

JSON Template for EACH Meal Suggestion Object:
```json
{{
  "id": "string",
  "healthBoost": ["string"],
  "isHealthy": true,
  "name": "string",
  "time": "string", /// time of the day e.g "8:00 AM", "1:00 PM", "6:00 PM"
  "servingDescription": "string",
  "explanation": "string",
  "calories": {{ "amount": "number", "unit": "kcal", "dailyValuePercentage": "number" }},
  "carbs": {{ "amount": "number", "unit": "g", "dailyValuePercentage": "number" }},
  "protein": {{ "amount": "number", "unit": "g", "dailyValuePercentage": "number" }},
  "fat": {{ "amount": "number", "unit": "g", "dailyValuePercentage": "number" }},
  "nutritionFacts": {{
    "totalCarbohydrates": {{ "amount": "number", "unit": "g" }},
    "dietaryFiber": {{ "amount": "number", "unit": "g" }},
    "sugar": {{ "amount": "number", "unit": "g" }},
    "addedSugars": {{ "amount": 0, "unit": "g" }},
    "sugarAlcohols": {{ "amount": 0, "unit": "g" }},
    "netCarbs": {{ "amount": "number", "unit": "g" }},
    "protein": {{ "amount": "number", "unit": "g" }},
    "totalFat": {{ "amount": "number", "unit": "g" }},
    "saturatedFat": {{ "amount": "number", "unit": "g" }},
    "transFat": {{ "amount": 0, "unit": "g" }},
    "polyunsaturatedFat": {{ "amount": "number", "unit": "g" }},
    "monounsaturatedFat": {{ "amount": "number", "unit": "g" }},
    "cholesterol": {{ "amount": "number", "unit": "mg" }},
    "sodium": {{ "amount": "number", "unit": "mg" }},
    "calcium": {{ "amount": "number", "unit": "mg" }},
    "iron": {{ "amount": "number", "unit": "mg" }},
    "potassium": {{ "amount": "number", "unit": "mg" }},
    "vitaminA": {{ "amount": "number", "unit": "IU" }},
    "vitaminC": {{ "amount": "number", "unit": "mg" }},
    "vitaminD": {{ "amount": "number", "unit": "IU" }}
  }},
  "recipe": {{
    "ingredient": [
      {{
        "name": "string",
        "explanation": "string",
        "emoji": "string",
        "quantity": "string"
      }}
    ],
    "recipe": [
      "string: Step 1...",
      "string: Step 2..."
    ]
  }}
}}
'''

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
            thinking_config=types.ThinkingConfig(thinking_budget=10000),  # Fixed: use positive budget
            response_mime_type="application/json",
        )
        
        logger.info('genAI config completed')
        
        response = genAiClient.models.generate_content(
            model=model_lite,
            contents=contents,
            config=generate_content_config,
        )
        # Parse the JSON response string into a Python dictionary
        result_dict = json.loads(response.text)
        return result_dict
        
    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse JSON response: {e}")
        logger.error(f"Raw response: {response.text}")
        raise HTTPException(status_code=500, detail="Failed to generate valid meal plan response")
    except AttributeError as e:
        logger.error(f"Attribute error - possible missing response: {e}")
        raise HTTPException(status_code=500, detail="Internal server error in meal plan generation")
    except Exception as e:
        logger.error(f"Error in generate_meal_plan: {e}")
        raise HTTPException(status_code=500, detail=str(e))