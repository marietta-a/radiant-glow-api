# To run this code you need to install the following dependencies:
# pip install google-genai

import json
from app.config import logger
from google.genai import types
from app.config import genAiClient, model;
from fastapi import HTTPException

async def generate_meal_plan(payload):
    prompt = '''
You are an expert nutritionist, a world cuisine specialist, a recipe developer, and a data structuring AI. Your task is to generate a daily meal plan with multiple options for each meal, structured as a single, valid JSON object, tailored to the user's specific health goals and culinary preferences.
User Inputs:
Daily Caloric Target: {{CALORIE_TARGET}} kcal
Health Goal Name: {{HEALTH_GOAL_NAME}}
Health Goal Description: {{HEALTH_GOAL_DESCRIPTION}}
Number of Suggestions per Meal: {{NUMBER_OF_SUGGESTIONS}}
Cuisine Preference: {{CUISINE_PREFERENCE}}
Output Constraints & Instructions:
Main Structure: The root of the output must be a single JSON object with three keys: "breakfast", "lunch", and "dinner". The value for each key must be an array containing exactly {{NUMBER_OF_SUGGESTIONS}} distinct meal suggestion objects.
Cuisine and Health Goal Synthesis (CRITICAL):
Authenticity: All meal suggestions—including their names, ingredients, and recipes—MUST be authentic to the specified Cuisine Preference.
Alignment: You must simultaneously ensure that each meal aligns with the Health Goal. This means selecting dishes from the specified cuisine that naturally contain the nutrients outlined in the Health Goal Description.
Justification: In the explanation field for each meal, you must justify your choice by explaining how the traditional ingredients within that specific dish contribute to the user's health goal.
Calorie Distribution: Distribute the Daily Caloric Target approximately evenly across the three meal times (e.g., breakfast ~30%, lunch ~35%, dinner ~35%). Each individual meal option must be a complete meal aiming for this per-meal calorie target.
Variety and Cultural Nuance: Ensure the {{NUMBER_OF_SUGGESTIONS}} options for each meal are distinct. Be mindful of cultural norms (e.g., breakfast in the specified cuisine might be a lighter version of a dinner meal, a porridge, or a specific pastry).
JSON Template Adherence: Every single meal suggestion object MUST strictly follow the structure and data types provided in the template below.
JSON Template for EACH Meal Suggestion Object:
code
JSON
{
"id": "string", // Generate a unique placeholder ID (e.g., "meal_lunch_option_1").
"healthBoost": ["string"], // List of benefits directly related to the Health Goal.
"isHealthy": true,
"name": "string", // The authentic name of the dish from the specified cuisine.
"time": "string", // A suggested time for the meal.
"servingDescription": "string", // A descriptive serving size.
"explanation": "string", // A 2-3 sentence justification synthesizing the cuisine and health goal.
"calories": { "amount": "number", "unit": "kcal", "dailyValuePercentage": "number" },
"carbs": { "amount": "number", "unit": "g", "dailyValuePercentage": "number" },
"protein": { "amount": "number", "unit": "g", "dailyValuePercentage": "number" },
"fat": { "amount": "number", "unit": "g", "dailyValuePercentage": "number" },
"nutritionFacts": {
// Provide realistic, estimated nutritional values for all fields.
"totalCarbohydrates": { "amount": "number", "unit": "g" },
"dietaryFiber": { "amount": "number", "unit":g" },
"sugar": { "amount": "number", "unit": "g" },
"addedSugars": { "amount": 0, "unit": "g" },
"sugarAlcohols": { "amount": 0, "unit": "g" },
"netCarbs": { "amount": "number", "unit": "g" },
"protein": { "amount": "number", "unit": "g" },
"totalFat": { "amount": "number", "unit": "g" },
"saturatedFat": { "amount": "number", "unit": "g" },
"transFat": { "amount": 0, "unit": "g" },
"polyunsaturatedFat": { "amount": "number", "unit": "g" },
"monounsaturatedFat": { "amount": "number", "unit": "g" },
"cholesterol": { "amount": "number", "unit": "mg" },
"sodium": { "amount": "number", "unit": "mg" },
"calcium": { "amount": "number", "unit": "mg" },
"iron": { "amount": "number", "unit": "mg" },
"potassium": { "amount": "number", "unit": "mg" },
"vitaminA": { "amount": "number", "unit": "IU" },
"vitaminC": { "amount": "number", "unit": "mg" },
"vitaminD": { "amount": "number", "unit": "IU" }
},
"recipe": {
"ingredient": [
{
"name": "string", // Name of an authentic ingredient (e.g., "Bitterleaf").
"explanation": "string", // Brief note on its benefit for the health goal.
"emoji": "string", // An appropriate emoji.
"quantity": "string" // Estimated quantity.
}
],
"recipe": [
"string: Step 1...",
"string: Step 2..."
]
}
}

{{CALORIE_TARGET}} ->'''  + payload.calories + '''
{{HEALTH_GOAL_NAME}} -> ''' + payload.healthGoal + '''
{{HEALTH_GOAL_DESCRIPTION}} -> ''' + payload.healthGoalPromptDescription +'''
{{NUMBER_OF_SUGGESTIONS}} -> ''' + payload.numberOfSuggestions + '''
{{CUISINE_PREFERENCE}} -> ''' + payload.country + ''' (specifically from ''' + payload.state +" " + payload.city + ''')"
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
            thinking_config=types.ThinkingConfig(thinking_budget=-1),
            response_mime_type="application/json",
        )

        logger.info('genAI config completed')

        response = genAiClient.models.generate_content(
            model=model,
            contents=contents,
            config=generate_content_config,
        )
        
        # Parse the JSON response string into a Python dictionary
        result_dict = json.loads(response.text)
        
        
        return result_dict
        
    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse JSON response for '{payload}': {e}")
        logger.error(f"Raw response: {response.text}")
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        logger.error(f"Error in analyze_nutrition_facts for '{payload}': {e}")
        raise HTTPException(status_code=500, detail=str(e))