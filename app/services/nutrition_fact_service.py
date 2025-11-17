# To run this code you need to install the following dependencies:
# pip install google-genai

import json
from app.config import logger
from google.genai import types
from app.config import genAiClient, model;


def analyze_nutrition_facts_from_image(image_bytes: bytes, mime_type: str):
    prompt = '''
{
"id": "27712345",
"healthBoost": ["heart health boost"],
"isHealthy": "true",
"name": "Roasted tiger nuts",
"servingDescription": "Roasted tiger nuts (28 g)",
"imageUrl": null,
"loggedAt": null,
"updatedAt": null,
"explanation": "Roasted tiger nuts are a nutritious snack rich in dietary fiber and healthy fats, which can support digestive health and provide sustained energy. They are low in protein but offer essential minerals like potassium and iron, making them a wholesome choice for a balanced diet. Overall, they make a great addition to a healthy lifestyle when enjoyed in moderation.",
"calories": {
"amount": 120.0,
"unit": "",
"dailyValuePercentage": 8
},
"carbs": {
"amount": 24.0,
"unit": "g",
"dailyValuePercentage": 12
},
"protein": {
"amount": 1.0,
"unit": "g",
"dailyValuePercentage": 1
},
"fat": {
"amount": 3.0,
"unit": "g",
"dailyValuePercentage": 7
},
"nutritionFacts": {
"totalCarbohydrates": { "amount": 24.0, "unit": "g" },
"dietaryFiber": { "amount": 8.0, "unit": "g" },
"sugar": { "amount": 5.0, "unit": "g" },
"addedSugars": { "amount": 0.0, "unit": "g" },
"sugarAlcohols": { "amount": 0.0, "unit": "g" },
"netCarbs": { "amount": 16.0, "unit": "g" },
"protein": { "amount": 1.0, "unit": "g" },
"totalFat": { "amount": 3.0, "unit": "g" },
"saturatedFat": { "amount": 0.5, "unit": "g" },
"transFat": { "amount": 0.0, "unit": "g" },
"polyunsaturatedFat": { "amount": 1.0, "unit": "g" },
"monounsaturatedFat": { "amount": 1.5, "unit": "g" },
"cholesterol": { "amount": 0.0, "unit": "mg" },
"sodium": { "amount": 5.0, "unit": "mg" },
"calcium": { "amount": 50.0, "unit": "mg" },
"iron": { "amount": 1.5, "unit": "mg" },
"potassium": { "amount": 300.0, "unit": "mg" },
"vitaminA": { "amount": 0.0, "unit": "IU" },
"vitaminC": { "amount": 0.0, "unit": "mg" },
"vitaminD": { "amount": 0.0, "unit": "IU" }
}
}

using the template above, analysed the attached food image.
Note:

All fields should be null if it is not in the following categories [edibles, beverages, nutrition, or groceries]

If it is unhealthy, isHealthy should be false

healthBoost: the top important list of health boosts for the food

use optimal accuracy

id: should be a unique key (created from timestamp of the current time of prompt generation) with max length of 16
IMPORTANT: You must respond with only the JSON object. Do not include any other text, explanations, or markdown formatting like ```json
    '''

    try:
        contents = [
            types.Content(
                role="user",
                parts=[
                    types.Part.from_text(text=prompt),
                    # types.Part.from_bytes(
                    #     mime_type="image/jpeg",
                    #     data=open(image_path, "rb").read(),
                    # )
                    types.Part.from_bytes(
                        mime_type=mime_type,
                        data=image_bytes,
                    )
                ],
            ),
        ]

        generate_content_config = types.GenerateContentConfig(
            thinking_config = types.ThinkingConfig(
                thinking_budget=-1,
            ),
            image_config=types.ImageConfig(
                image_size="1K",
            ),
            response_mime_type="application/json",
        )

        response = genAiClient.models.generate_content(
            model=model,
            contents=contents,
            config=generate_content_config,
        )
        
        # Parse the JSON response string into a Python dictionary
        result_dict = json.loads(response.text)
        
        return result_dict
        
    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse JSON response for image: {e}")
        logger.error(f"Raw response: {response.text}")
        return None
    except Exception as e:
        logger.error(f"Error in analyze_nutrition_facts for image: {e}")
        return None
    



async def analyze_nutrition_facts(food_name: str):
    prompt = '''
{
"id": "27712345",
"healthBoost": ["heart health"],
"isHealthy": "true",
"name": "Roasted tiger nuts",
"servingDescription": "Roasted tiger nuts (28 g)",
"imageUrl": null,
"loggedAt": null,
"updatedAt": null,
"explanation": "Roasted tiger nuts are a nutritious snack rich in dietary fiber and healthy fats, which can support digestive health and provide sustained energy. They are low in protein but offer essential minerals like potassium and iron, making them a wholesome choice for a balanced diet. Overall, they make a great addition to a healthy lifestyle when enjoyed in moderation.",
"calories": {
"amount": 120.0,
"unit": "",
"dailyValuePercentage": 8
},
"carbs": {
"amount": 24.0,
"unit": "g",
"dailyValuePercentage": 12
},
"protein": {
"amount": 1.0,
"unit": "g",
"dailyValuePercentage": 1
},
"fat": {
"amount": 3.0,
"unit": "g",
"dailyValuePercentage": 7
},
"nutritionFacts": {
"totalCarbohydrates": { "amount": 24.0, "unit": "g" },
"dietaryFiber": { "amount": 8.0, "unit": "g" },
"sugar": { "amount": 5.0, "unit": "g" },
"addedSugars": { "amount": 0.0, "unit": "g" },
"sugarAlcohols": { "amount": 0.0, "unit": "g" },
"netCarbs": { "amount": 16.0, "unit": "g" },
"protein": { "amount": 1.0, "unit": "g" },
"totalFat": { "amount": 3.0, "unit": "g" },
"saturatedFat": { "amount": 0.5, "unit": "g" },
"transFat": { "amount": 0.0, "unit": "g" },
"polyunsaturatedFat": { "amount": 1.0, "unit": "g" },
"monounsaturatedFat": { "amount": 1.5, "unit": "g" },
"cholesterol": { "amount": 0.0, "unit": "mg" },
"sodium": { "amount": 5.0, "unit": "mg" },
"calcium": { "amount": 50.0, "unit": "mg" },
"iron": { "amount": 1.5, "unit": "mg" },
"potassium": { "amount": 300.0, "unit": "mg" },
"vitaminA": { "amount": 0.0, "unit": "IU" },
"vitaminC": { "amount": 0.0, "unit": "mg" },
"vitaminD": { "amount": 0.0, "unit": "IU" }
}
}
using the template above, analyse ''' + food_name + '''.
Note:
All fields should be null if it is not in the following categories [edibles, beverages, nutrition, or groceries ]
If it is unhealthy, isHealthy should be false
healthBoost: [top preventive health boost(s) it provides. list of 1–3 concise health benefit tags (e.g., "digestive health", "heart health", "bone strength")]
use optimal accuracy
id: should be a unique key (created from timestamp of the current time of prompt generation) with max length of 16

IMPORTANT: You must respond with only the JSON object. Do not include any other text, explanations, or markdown formatting like ```json
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
        logger.error(f"Failed to parse JSON response for '{food_name}': {e}")
        logger.error(f"Raw response: {response.text}")
        return None
    except Exception as e:
        logger.error(f"Error in analyze_nutrition_facts for '{food_name}': {e}")
        return None