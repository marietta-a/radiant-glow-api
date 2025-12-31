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
      "item": {payload.category},
      "categoryId": {payload.categoryId},
      "description": {payload.description},
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
          "healthBenefit": [ "Packed with Vitamin C from berries to boost collagen production and brighten skin", "Rich in antioxidants (anthocyanins, flavonoids) that protect against free radical damage", "Spinach provides Vitamin A and iron, supporting skin cell turnover and oxygenation", "High fiber content aids digestion, reducing skin dullness linked to poor gut health", "Hydrating base (water or plant milk) helps maintain skin moisture balance", "Contains Vitamin K from spinach, which supports skin healing and reduces inflammation", "Natural sweetness reduces reliance on refined sugar, lowering risk of skin glycation" ], 
          "healthRisk": [ "Potential pesticide residues if berries and spinach are not organic", "Excessive consumption may cause bloating due to high fiber", "Oxalates in spinach can contribute to kidney stone risk in sensitive individuals", "Added sweeteners (if used) may counteract skin benefits by promoting inflammation" ]
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
          "healthBenefit": [ "Rich in Omega-3 fatty acids that reduce skin inflammation", "Excellent source of Vitamin D for skin cell renewal", "High in antioxidants (from asparagus) that protect against free radical damage", "Supports collagen production through protein content", "Provides Vitamin E which helps maintain skin elasticity", "Contains selenium that aids in skin repair and protection", "Hydrating properties from asparagus to keep skin supple" ], 
          "healthRisk": [ "Potential mercury exposure from salmon if consumed excessively", "Risk of overcooking leading to loss of nutrients", "Possible pesticide residues in asparagus if not organic", "High sodium if seasoned heavily" ]
        }}
      ]
    }}
  ]
}}

Using the template above as the output format sample:

Generate exactly {payload.numberOfSuggestions} food log entries (diets) for the health goal: "{payload.healthGoal}" in the category: "{payload.category}".

CRITICAL REQUIREMENTS:
1. The output MUST follow the exact JSON structure shown above
2. Generate {payload.numberOfSuggestions} items inside the "items" array
3. Each item should have:
   - A unique ID starting with "food_entry_"
   - A realistic name and serving description
   - Explanation linking it to {payload.healthGoal}
   - Health boost tags relevant to {payload.healthGoal}
   - Complete nutritional information including calories, carbs, protein, fat
   - Detailed nutrition facts matching real foods
   - Health benefits and risks (empty arrays if none)

SPECIFIC INSTRUCTIONS FOR {payload.healthGoal} - {payload.category}:
- Focus on foods that specifically support {payload.healthGoal}
- Ensure nutritional values are realistic for {payload.category} foods
- Include foods that help prevent or manage illnesses related to {payload.healthGoal}
- Consider {cuisineMessage} in food selection
- Health benefits should be relevant to {payload.healthGoal}
- If no health risks exist, use empty array []

NUTRITION GUIDELINES:
- Provide realistic calorie amounts per serving
- Ensure macronutrient ratios are appropriate for {payload.healthGoal}
- Include detailed micronutrients where applicable
- Daily value percentages should be realistic

FORMAT REQUIREMENTS:
- Use null for missing image URLs
- Times should be in format like "8:00 AM"
- All measurements should have appropriate units
- Use empty arrays [] for healthRisk/healthBenefit if no data

IMPORTANT: Respond with ONLY the JSON object matching the template structure. No explanations, no markdown, no commentary outside the JSON.
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