# To run this code you need to install the following dependencies:
# pip install google-genai
import json
from app.config import logger
from google.genai import types
from app.config import genAiClient, model_lite, thinking_content_config
from fastapi import HTTPException
import time

async def get_recipe(food_name: str):
    
    start = time.time()
    prompt = f'''
The Prompt

IMPORTANT:
NOTE: INORDER TO GENERATE RECIPE, ENSURE {food_name} IS A CONSUMABLE ITEM. IF IT IS NONCONSUMABLE, OUTPUT SHOULD BE NULL

You are a recipe generation AI. Your task is to generate the ingredients and recipe steps for {food_name} and format the output as a single, valid JSON object.
Item to Generate: {food_name}

Output Constraints & Instructions:
Strict JSON Format: The output MUST be a single JSON object with two top-level keys: ingredient and recipe.
Ingredient Details:
The ingredient key must contain an array of objects.
List all necessary ingredients for {food_name}
For each ingredient object, provide the name, a helpful explanation (with a max of 5 words) of its purpose or health benefit (if applicable), an appropriate emoji, and a realistic quantity.
Recipe Steps:
The recipe key must contain an array of strings.
Provide clear, step-by-step instructions. Structure the steps logically.
The final step should describe how to serve the components together.
Template Adherence: Strictly follow the JSON structure provided below.
JSON Output Template:
code
```json
{{
  "name": {food_name},
  "ingredient": [
    {{
      "name": "string",
      "explanation": "string",
      "emoji": "string",
      "quantity": "string"
    }}
  ],
  "recipe": [
    "string"
  ]
}}

Now, generate the complete recipe for {food_name}.
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
        
        # generate_content_config = types.GenerateContentConfig(
        #     thinking_config=thinking_content_config,  # Fixed: use positive budget
        #     response_mime_type="application/json",
        # )
        
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