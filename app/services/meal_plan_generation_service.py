# To run this code you need to install the following dependencies:
# pip install google-genai
import json
from app.config import logger
from google.genai import types
from app.config import genAiClient, model_lite, model, thinking_content_config
from fastapi import HTTPException
from app.models.meal_plan_payload import MealPlanPayload
import time

async def generate_meal_plan(payload: MealPlanPayload):
    start = time.time()
    
    cuisineMessage = f'Diets should be {payload.country} cuisines'
    if(payload.state):
        cuisineMessage += f', specifically from the state of {payload.state}'
    if(payload.city):
        cuisineMessage += f', and the city of {payload.city}'
    
    prompt = f'''
You are an expert nutritionist, registered dietitian, world‑cuisine specialist, and a highly detailed recipe generator. 
Your task is to generate a daily meal plan tailored to the user's specific health goals, culinary preferences, and precise 
macronutrient targets when provided.

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
Main Structure:
    The root of the output must be a single JSON object with three keys: "breakfast", "lunch", and "dinner".
    Each key must map to an array containing exactly {payload.numberOfSuggestions} distinct meal suggestion objects.

Meal Suggestion Object Structure (MANDATORY FIELDS):
Each meal suggestion object must contain:
    - "name": The meal name.
    - "ingredients": A list of ingredients with exact quantities (grams, ml, cups, or pieces).
    - "instructions": A step-by-step recipe with clear cooking methods and timing.
    - "nutrition": Estimated nutrition facts including:
        * calories
        * carbohydrates (g)
        * protein (g)
        * fat (g)
        * fiber (g)
        * key micronutrients relevant to the health goal (e.g., iron, magnesium, omega‑3, potassium).
    - "explanation": A justification connecting:
        * how the meal supports the Health Goal,
        * how the ingredients align with the cuisine,
        * how the meal fits into the daily macro distribution strategy.

Daily Plan Structure & Macro Targets (CRITICAL):
    Overall Goal:
        The sum of macros for any combination of one breakfast, one lunch, and one dinner should closely approximate 
        the user's daily targets ({payload.carbs}g Carbs, {payload.protein}g Protein, {payload.fat}g Fat).

    Strategic Macro Distribution:
        Breakfast:
            - Must combine protein, fiber, healthy fats, and complex carbohydrates.
        Lunch:
            - Must be the highest-protein meal of the day.
            - Must emphasize lean protein and vegetables for satiety and muscle support.
        Dinner:
            - Must be lighter, nutrient-dense, moderate in protein, and lower in carbs and fats for easier digestion.

Cuisine and Health Goal Synthesis:
    Alignment:
        Each meal must incorporate culturally authentic ingredients that naturally support the Health Goal described 
        in {payload.promptDescription}.
    Justification:
        The "explanation" field must explicitly connect the meal’s ingredients to:
            - the health goal,
            - the cultural/cuisine context,
            - the macro distribution strategy.

Variety and Cultural Nuance:
    Ensure the {payload.numberOfSuggestions} options for each meal are distinct, culturally appropriate, and avoid 
    repeating the same core ingredients unless required by the cuisine.

IMPORTANT:
    A MUST: All meal suggested for (breakfast, lunch, and dinner) should {payload.promptDescription}
    All recipes must be detailed enough for a beginner to cook successfully.
    All ingredient quantities must be explicit.
    All nutrition values must be estimated realistically.
    The cummulative calorie distribution for breakfast, lunch, and dinner should be approximately equal to {payload.calories}
    The cummulative macronutrients distribution for breakfast, lunch, and dinner should be approximately equal to [fat: {payload.fat}g; protein: {payload.protein}g; carbohydrate: {payload.carbs}g]

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
        
        logger.info('genAI config completed')
        
        response = genAiClient.models.generate_content(
            model=model_lite,
            contents=contents,
            config=thinking_content_config,
        )
        # Parse the JSON response string into a Python dictionary
        result_dict = json.loads(response.text)

        end = time.time()
        elapsed = end - start

        print(f"Elapsed time: {elapsed} seconds")

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