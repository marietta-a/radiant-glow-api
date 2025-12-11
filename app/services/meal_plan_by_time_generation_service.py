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
    
    # Assuming payload has a 'mealType' attribute.
    # The 'cuisineMessage' variable should be constructed as before.

    prompt = f'''
    You are an expert nutritionist, registered dietitian, world-cuisine specialist, and a highly detailed recipe generator. 
    Your task is to generate meal suggestions for a single, specific meal type, tailored to the user's health goals, culinary preferences, and precise macronutrient targets for that meal.

    User Inputs:
    Meal Type to Generate: {payload.mealType if payload.mealType else "breakfast"}
    Meal Caloric Target: {payload.calories} kcal
    Meal Macronutrient Targets:
        Carbohydrates: {payload.carbs} g
        Protein: {payload.protein} g
        Fat: {payload.fat} g
    Health Goal Name: {payload.healthGoal}
    Health Goal Description: {payload.promptDescription}
    Number of Suggestions: {payload.numberOfSuggestions}
    {cuisineMessage}

    Output Constraints & Instructions:
    Main Structure:
        The root of the output must be a single JSON ARRAY.
        This array must contain exactly {payload.numberOfSuggestions} distinct meal suggestion objects.

    Meal Design & Target Adherence (CRITICAL):
        Target Matching:
            Each generated meal suggestion's nutrition facts (calories, carbs, protein, fat) MUST closely approximate the user's targets specified above. The provided targets are for THIS MEAL ONLY.
        
        Meal Role and Composition (based on Meal Type):
            - If "Breakfast": The meal must combine protein, fiber, healthy fats, and complex carbohydrates for sustained energy.
            - If "Lunch": The meal must be high in protein, emphasizing lean sources and vegetables for satiety and muscle support.
            - If "Dinner": The meal must be lighter, nutrient-dense, moderate in protein, and lower in carbs and fats for easier digestion.
        
        You must adhere to the rule that corresponds to the requested "{payload.mealType}".

    Cuisine and Health Goal Synthesis:
        Alignment:
            Each meal must incorporate culturally authentic ingredients from the specified cuisine that naturally support the Health Goal.
        Justification:
            The "explanation" field must explicitly connect the meal’s ingredients to:
                1. The health goal.
                2. The cultural/cuisine context.
                3. Its role as a proper {payload.mealType} (e.g., "as a high-protein lunch...").

    Variety and Cultural Nuance:
        Ensure the {payload.numberOfSuggestions} options are distinct, culturally appropriate, and avoid repeating the same core ingredients.

    IMPORTANT:
        All recipes must be detailed enough for a beginner to cook successfully.
        All ingredient quantities must be explicit.
        All nutrition values must be estimated realistically.

    JSON Template Adherence: Every single meal suggestion object in the root array MUST strictly follow the structure and data types provided in the template below.

    JSON Template for EACH Meal Suggestion Object:
    ```json
    {{
    "id": "string",
    "healthBoost": ["string"],
    "isHealthy": true,
    "name": "string",
    "time": "string", // A time appropriate for the requested meal type (e.g., "1:00 PM" for Lunch)
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
        
        generate_thinking_content_config = types.GenerateContentConfig(
            response_mime_type="application/json",
        )
        
        logger.info('genAI config completed')
        
        response = genAiClient.models.generate_content(
            model=model,
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