# To run this code you need to install the following dependencies:
# pip install google-genai

import json
from app.config import logger
from google.genai import types
from app.config import genAiClient, model, thinking_content_config
from fastapi import HTTPException
import time 
from app.models.category_item_payload import CategoryItemPayload;



async def analyze_category_item_nutri_fact(payload: CategoryItemPayload):
    start = time.time()
    cuisineMessage = f'Diets should be {payload.country} cuisines'
    if(payload.state):
        cuisineMessage += f', specifically from the state of {payload.state}'
    if(payload.city):
        cuisineMessage += f', and the city of {payload.city}'
        
    prompt = f"""
{{
  "id": "health_goal_radiant_glow_01",
  "loggedAt": "2024-05-21T10:00:00.000Z",
  "updatedAt": "2024-05-21T10:05:00.000Z",
  "healthGoal": {payload.healthGoalId},
  "description": {payload.healthGoal},
  "isSelected": true,
  "foodLogEntryCategories": [
    {{
      "id": "fec_antioxidants_01",
      "loggedAt": "2024-05-21T10:00:00.000Z",
      "updatedAt": "2024-05-21T10:05:00.000Z",
      "item": "Antioxidant-Rich Foods",
      "description": "Foods high in antioxidants help protect your skin from damage caused by free radicals.",
      "items": [
        {{
          "id": "food_entry_berries_01",
          "name": "Mixed Berry & Spinach Smoothie",
          "servingDescription": "1 large glass (400ml)",
          "imageUrl": null,
          "loggedAt": "2024-05-21T08:00:00.000Z",
          "updatedAt": "2024-05-21T08:00:00.000Z",
          "explanation": "This smoothie is packed with antioxidants from berries and vitamin C from spinach, promoting collagen production for firm, youthful skin.",
          "healthBoost": ["skin health", "antioxidant boost"],
          "isHealthy": true,
          "time": "8:00 AM",
          "calories": {{"amount": 250, "unit": "kcal", "dailyValuePercentage": 13}},
          "carbs": {{"amount": 45, "unit": "g", "dailyValuePercentage": 15}},
          "protein": {{"amount": 15, "unit": "g", "dailyValuePercentage": 30}},
          "fat": {{"amount": 5, "unit": "g", "dailyValuePercentage": 6}},
          "nutritionFacts": {{
            "totalCarbohydrates": {{"amount": 45.0, "unit": "g"}},
            "dietaryFiber": {{"amount": 10.0, "unit": "g"}},
            "sugar": {{"amount": 25.0, "unit": "g"}},
            "addedSugars": {{"amount": 0.0, "unit": "g"}},
            "sugarAlcohols": {{"amount": 0.0, "unit": "g"}},
            "netCarbs": {{"amount": 35.0, "unit": "g"}},
            "protein": {{"amount": 15.0, "unit": "g"}},
            "totalFat": {{"amount": 5.0, "unit": "g"}},
            "saturatedFat": {{"amount": 1.0, "unit": "g"}},
            "transFat": {{"amount": 0.0, "unit": "g"}},
            "polyunsaturatedFat": {{"amount": 2.0, "unit": "g"}},
            "monounsaturatedFat": {{"amount": 1.5, "unit": "g"}},
            "cholesterol": {{"amount": 5.0, "unit": "mg"}},
            "sodium": {{"amount": 120.0, "unit": "mg"}},
            "calcium": {{"amount": 200.0, "unit": "mg"}},
            "iron": {{"amount": 2.0, "unit": "mg"}},
            "potassium": {{"amount": 600.0, "unit": "mg"}},
            "vitaminA": {{"amount": 2500.0, "unit": "IU"}},
            "vitaminC": {{"amount": 150.0, "unit": "mg"}},
            "vitaminD": {{"amount": 50.0, "unit": "IU"}}
          }},
          "healthBenefit": ["High in Vitamin C", "Rich in Antioxidants"],
          "healthRisk": []
        }},
        {{
          "id": "food_entry_salmon_02",
          "name": "Grilled Salmon with Asparagus",
          "servingDescription": "1 fillet (150g) with 1 cup asparagus",
          "imageUrl": null,
          "loggedAt": "2024-05-20T18:30:00.000Z",
          "updatedAt": "2024-05-20T18:30:00.000Z",
          "explanation": "Salmon is rich in omega-3 fatty acids, which reduce inflammation and keep skin moisturized. Asparagus provides a dose of skin-protecting antioxidants.",
          "healthBoost": ["skin hydration", "anti-inflammatory"],
          "isHealthy": true,
          "time": "6:30 PM",
          "calories": {{"amount": 450.0, "unit": "kcal", "dailyValuePercentage": 22}},
          "carbs": {{"amount": 10.0, "unit": "g", "dailyValuePercentage": 3}},
          "protein": {{"amount": 40.0, "unit": "g", "dailyValuePercentage": 80}},
          "fat": {{"amount": 28.0, "unit": "g", "dailyValuePercentage": 36}},
          "nutritionFacts": {{
            "totalCarbohydrates": {{"amount": 10.0, "unit": "g"}},
            "dietaryFiber": {{"amount": 5.0, "unit": "g"}},
            "sugar": {{"amount": 4.0, "unit": "g"}},
            "addedSugars": {{"amount": 0.0, "unit": "g"}},
            "sugarAlcohols": {{"amount": 0.0, "unit": "g"}},
            "netCarbs": {{"amount": 5.0, "unit": "g"}},
            "protein": {{"amount": 40.0, "unit": "g"}},
            "totalFat": {{"amount": 28.0, "unit": "g"}},
            "saturatedFat": {{"amount": 6.0, "unit": "g"}},
            "transFat": {{"amount": 0.0, "unit": "g"}},
            "polyunsaturatedFat": {{"amount": 12.0, "unit": "g"}},
            "monounsaturatedFat": {{"amount": 8.0, "unit": "g"}},
            "cholesterol": {{"amount": 120.0, "unit": "mg"}},
            "sodium": {{"amount": 150.0, "unit": "mg"}},
            "calcium": {{"amount": 50.0, "unit": "mg"}},
            "iron": {{"amount": 1.5, "unit": "mg"}},
            "potassium": {{"amount": 900.0, "unit": "mg"}},
            "vitaminA": {{"amount": 1500.0, "unit": "IU"}},
            "vitaminC": {{"amount": 20.0, "unit": "mg"}},
            "vitaminD": {{"amount": 500.0, "unit": "IU"}}
          }},
          "healthBenefit": ["High in Omega-3s", "Excellent source of Vitamin D"],
          "healthRisk": []
        }}
      ]
    }}
  ]
}}

Using the template above as the output format sample:

Generate the top {payload.numberOfSuggestions} foodLogEntries (diets) for "{payload.healthGoal} Diets" .

For each item:
- Ensure it aligns with {payload.healthGoal}:{payload.category}.
- Provide calories per serving.
- Specify illnesses it may help prevent or manage.
- Ensure optimal health value.
- if the attributes healthRisk and healthBenefit has no data, return an empty lists

IMPORTANT: Respond with **only** the JSON object. No explanations, no markdown, no commentary.
"""


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
        logger.error(f"Failed to parse JSON response for '{payload.healthGoal}': {e}")
        logger.error(f"Raw response: {response.text}")
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        logger.error(f"Error in analyze_nutrition_facts for '{payload.healthGoal}': {e}")
        raise HTTPException(status_code=500, detail=str(e))