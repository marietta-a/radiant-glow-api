# To run this code you need to install the following dependencies:
# pip install google-genai

import json
from app.config import logger
from google.genai import types
from app.config import genAiClient, model;
from fastapi import HTTPException


def analyze_nutrition_facts_from_image(image_bytes: bytes, mime_type: str):
    prompt = '''
{
  "id": "1678887080198",
  "healthBoost": [
    "rich in antioxidants",
    "good source of fiber",
    "vitamins and minerals"
  ],
  "isHealthy": true,
  "name": "Apple Cranberry Salad with Maple Dressing",
  "time": "12:00 PM",
  "servingDescription": "1 large bowl (approx. 400g)",
  "explanation": "This vibrant salad combines nutrient-dense greens with the natural sweetness of apples and the tartness of cranberries. Packed with vitamins, minerals, and fiber, it supports overall health and provides sustained energy. The maple dressing adds a touch of natural sweetness without being overpowering.",
  "calories": {
    "amount": 350,
    "unit": "kcal",
    "dailyValuePercentage": 17.5
  },
  "carbs": {
    "amount": 50,
    "unit": "g",
    "dailyValuePercentage": 18.2
  },
  "protein": {
    "amount": 6,
    "unit": "g",
    "dailyValuePercentage": 12
  },
  "fat": {
    "amount": 15,
    "unit": "g",
    "dailyValuePercentage": 19.2
  },
  "nutritionFacts": {
    "totalCarbohydrates": {
      "amount": 50,
      "unit": "g"
    },
    "dietaryFiber": {
      "amount": 10,
      "unit": "g"
    },
    "sugar": {
      "amount": 35,
      "unit": "g"
    },
    "addedSugars": {
      "amount": 10,
      "unit": "g"
    },
    "sugarAlcohols": {
      "amount": 0,
      "unit": "g"
    },
    "netCarbs": {
      "amount": 40,
      "unit": "g"
    },
    "protein": {
      "amount": 6,
      "unit": "g"
    },
    "totalFat": {
      "amount": 15,
      "unit": "g"
    },
    "saturatedFat": {
      "amount": 2,
      "unit": "g"
    },
    "transFat": {
      "amount": 0,
      "unit": "g"
    },
    "polyunsaturatedFat": {
      "amount": 4,
      "unit": "g"
    },
    "monounsaturatedFat": {
      "amount": 9,
      "unit": "g"
    },
    "cholesterol": {
      "amount": 0,
      "unit": "mg"
    },
    "sodium": {
      "amount": 200,
      "unit": "mg"
    },
    "calcium": {
      "amount": 80,
      "unit": "mg"
    },
    "iron": {
      "amount": 3,
      "unit": "mg"
    },
    "potassium": {
      "amount": 500,
      "unit": "mg"
    },
    "vitaminA": {
      "amount": 6000,
      "unit": "IU"
    },
    "vitaminC": {
      "amount": 50,
      "unit": "mg"
    },
    "vitaminD": {
      "amount": 0,
      "unit": "IU"
    }
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
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        logger.error(f"Error in analyze_nutrition_facts for image: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    



async def analyze_nutrition_facts(food_name: str):
    prompt = '''
{
  "id": "1678887080198",
  "healthBoost": [
    "rich in antioxidants",
    "good source of fiber",
    "vitamins and minerals"
  ],
  "isHealthy": true,
  "name": "Apple Cranberry Salad with Maple Dressing",
  "time": "12:00 PM",
  "servingDescription": "1 large bowl (approx. 400g)",
  "explanation": "This vibrant salad combines nutrient-dense greens with the natural sweetness of apples and the tartness of cranberries. Packed with vitamins, minerals, and fiber, it supports overall health and provides sustained energy. The maple dressing adds a touch of natural sweetness without being overpowering.",
  "calories": {
    "amount": 350,
    "unit": "kcal",
    "dailyValuePercentage": 17.5
  },
  "carbs": {
    "amount": 50,
    "unit": "g",
    "dailyValuePercentage": 18.2
  },
  "protein": {
    "amount": 6,
    "unit": "g",
    "dailyValuePercentage": 12
  },
  "fat": {
    "amount": 15,
    "unit": "g",
    "dailyValuePercentage": 19.2
  },
  "nutritionFacts": {
    "totalCarbohydrates": {
      "amount": 50,
      "unit": "g"
    },
    "dietaryFiber": {
      "amount": 10,
      "unit": "g"
    },
    "sugar": {
      "amount": 35,
      "unit": "g"
    },
    "addedSugars": {
      "amount": 10,
      "unit": "g"
    },
    "sugarAlcohols": {
      "amount": 0,
      "unit": "g"
    },
    "netCarbs": {
      "amount": 40,
      "unit": "g"
    },
    "protein": {
      "amount": 6,
      "unit": "g"
    },
    "totalFat": {
      "amount": 15,
      "unit": "g"
    },
    "saturatedFat": {
      "amount": 2,
      "unit": "g"
    },
    "transFat": {
      "amount": 0,
      "unit": "g"
    },
    "polyunsaturatedFat": {
      "amount": 4,
      "unit": "g"
    },
    "monounsaturatedFat": {
      "amount": 9,
      "unit": "g"
    },
    "cholesterol": {
      "amount": 0,
      "unit": "mg"
    },
    "sodium": {
      "amount": 200,
      "unit": "mg"
    },
    "calcium": {
      "amount": 80,
      "unit": "mg"
    },
    "iron": {
      "amount": 3,
      "unit": "mg"
    },
    "potassium": {
      "amount": 500,
      "unit": "mg"
    },
    "vitaminA": {
      "amount": 6000,
      "unit": "IU"
    },
    "vitaminC": {
      "amount": 50,
      "unit": "mg"
    },
    "vitaminD": {
      "amount": 0,
      "unit": "IU"
    }
  }
}
using the template above, analyse ''' + food_name + '''.
Note:
All fields should be null if it is not in the following categories [edibles, beverages, nutrition, or groceries ]
If it is unhealthy, isHealthy should be false
healthBoost: [top preventive health boost(s) it provides. list of 1–3 concise health benefit tags (e.g., "digestive health", "heart health", "bone strength")]
use optimal accuracy
id: should be a unique key (created from timestamp of the current time of prompt generation) with max length of 16
if the''' + food_name + ''' is incorrectly spelled due to user error, deduce from best match

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
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        logger.error(f"Error in analyze_nutrition_facts for '{food_name}': {e}")
        raise HTTPException(status_code=500, detail=str(e))