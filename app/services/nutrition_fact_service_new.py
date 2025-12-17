# To run this code you need to install the following dependencies:
# pip install google-genai

import json
import time
from app.config import logger
from google.genai import types
from app.config import genAiClient, model;
from fastapi import HTTPException


def analyze_nutrition_facts_from_image(image_bytes: bytes, mime_type: str):
    
    start = time.time()
    prompt = '''
{
"id": "1678887080198",
"healthBenefit": [
"Nightshade-free, safe for individuals sensitive to nightshade vegetables (tomatoes, peppers, potatoes).",
"Provides essential vitamins and minerals, supporting overall health and reducing inflammation.",
"Allergy Management: Replace nightshades with sweet potatoes and leafy greens. Roast sweet potatoes and sauté kale with garlic and olive oil.",
"Promotes healthy digestion.",
"Supports a healthy immune system."
],
"healthRisk": [
"Possible allergic reaction (kale, rare)",
"May cause gas or bloating in some individuals.",
"Ensure kale is cooked thoroughly to reduce bitterness."
],
"healthBoost": [
"rich in antioxidants",
"good source of fiber",
"vitamins and minerals"
],
"isHealthy": true,
"name": "Apple Cranberry Salad with Maple Dressing",
"time": "12:00 PM",
"servingDescription": "1 large bowl (approx. 400g)",
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
},
"recipe": {
"ingredient": [
{
"name": "mixed greens",
"explanation": "Provides vitamins A, C, K, and folate.",
"emoji": "🥬",
"quantity": "6 cups"
},
{
"name": "apple",
"explanation": "Source of fiber and vitamin C.",
"emoji": "🍎",
"quantity": "1 medium, diced"
},
{
"name": "dried cranberries",
"explanation": "Rich in antioxidants.",
"emoji": "🍒",
"quantity": "1/2 cup"
},
{
"name": "slivered almonds",
"explanation": "Provides healthy fats and vitamin E.",
"emoji": "🌰",
"quantity": "1/4 cup"
},
{
"name": "maple syrup",
"explanation": "Natural sweetener.",
"emoji": "🍁",
"quantity": "2 tablespoons"
},
{
"name": "olive oil",
"explanation": "Healthy monounsaturated fats.",
"emoji": "🫒",
"quantity": "3 tablespoons"
},
{
"name": "apple cider vinegar",
"emoji": "🍶",
"quantity": "1 tablespoon"
},
{
"name": "Dijon mustard",
"emoji": "🍯",
"quantity": "1 teaspoon"
},
{
"name": "salt",
"emoji": "🧂",
"quantity": "1/4 teaspoon"
},
{
"name": "black pepper",
"emoji": "🌶️",
"quantity": "1/8 teaspoon"
}
],
"recipe": [
"In a large bowl, combine mixed greens, diced apple, dried cranberries, and slivered almonds.",
"In a small bowl, whisk together maple syrup, olive oil, apple cider vinegar, Dijon mustard, salt, and pepper until well combined.",
"Pour the dressing over the salad and toss gently to coat.",
"Serve immediately."
]
}
}

Using the template above, analysed the attached food image  (ensure high accuracy in recognition by considering colors, textures, and common culinary patterns).
If unsure, suggest the most probable dish name and ingredients based on the visual data. Avoid assumptions without visual evidence.
Note:
All fields should be null if it is not in the following categories [edibles, beverages, nutrition, or groceries]

If it is unhealthy, isHealthy should be false

healthBoost: the top important list of health boosts for the food (max of 5 words, e.g., heart health boost, eye health boost)
explanation: for each ingredient, explanation is the nutrient the ingredient is rich in (max 5 words)

use optimal accuracy

id: should be a unique key (created from timestamp of the current time of prompt generation) with max length of 16
IMPORTANT: You must respond with only the JSON object. Do not include any other text, explanations, or markdown formatting like
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
        
        end = time.time()
        elapsed = end - start

        print(f"Elapsed time: {elapsed} seconds")
        
        return result_dict
        
    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse JSON response for image: {e}")
        logger.error(f"Raw response: {response.text}")
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        logger.error(f"Error in analyze_nutrition_facts for image: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    



async def analyze_nutrition_facts(food_name: str):
    
    start = time.time()
    prompt = '''
{
"id": "1678887080198",
"healthBenefit": [
"Nightshade-free, safe for individuals sensitive to nightshade vegetables (tomatoes, peppers, potatoes).",
"Provides essential vitamins and minerals, supporting overall health and reducing inflammation.",
"Allergy Management: Replace nightshades with sweet potatoes and leafy greens. Roast sweet potatoes and sauté kale with garlic and olive oil.",
"Promotes healthy digestion.",
"Supports a healthy immune system."
],
"healthRisk": [
"Possible allergic reaction (kale, rare)",
"May cause gas or bloating in some individuals.",
"Ensure kale is cooked thoroughly to reduce bitterness."
],
"healthBoost": [
"rich in antioxidants",
"good source of fiber",
"vitamins and minerals"
],
"isHealthy": true,
"name": "Apple Cranberry Salad with Maple Dressing",
"time": "12:00 PM",
"servingDescription": "1 large bowl (approx. 400g)",
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
},
"recipe": {
"ingredient": [
{
"name": "mixed greens",
"explanation": "Provides vitamins A, C, K, and folate.",
"emoji": "🥬",
"quantity": "6 cups"
},
{
"name": "apple",
"explanation": "Source of fiber and vitamin C.",
"emoji": "🍎",
"quantity": "1 medium, diced"
},
{
"name": "dried cranberries",
"explanation": "Rich in antioxidants.",
"emoji": "🍒",
"quantity": "1/2 cup"
},
{
"name": "slivered almonds",
"explanation": "Provides healthy fats and vitamin E.",
"emoji": "🌰",
"quantity": "1/4 cup"
},
{
"name": "maple syrup",
"explanation": "Natural sweetener.",
"emoji": "🍁",
"quantity": "2 tablespoons"
},
{
"name": "olive oil",
"explanation": "Healthy monounsaturated fats.",
"emoji": "🫒",
"quantity": "3 tablespoons"
},
{
"name": "apple cider vinegar",
"emoji": "🍶",
"quantity": "1 tablespoon"
},
{
"name": "Dijon mustard",
"emoji": "🍯",
"quantity": "1 teaspoon"
},
{
"name": "salt",
"emoji": "🧂",
"quantity": "1/4 teaspoon"
},
{
"name": "black pepper",
"emoji": "🌶️",
"quantity": "1/8 teaspoon"
}
],
"recipe": [
"In a large bowl, combine mixed greens, diced apple, dried cranberries, and slivered almonds.",
"In a small bowl, whisk together maple syrup, olive oil, apple cider vinegar, Dijon mustard, salt, and pepper until well combined.",
"Pour the dressing over the salad and toss gently to coat.",
"Serve immediately."
]
}
}

using the template above, analyse ''' + food_name + '''.
Note:
All fields should be null if it is not in the following categories [edibles, beverages, nutrition, or groceries]

If it is unhealthy, isHealthy should be false

healthBoost: the top important list of health boosts for the food (max of 5 words, e.g., heart health boost, eye health boost)
explanation: for each ingredient, explanation is the nutrient the ingredient is rich in (max 5 words)

use optimal accuracy

id: should be a unique key (created from timestamp of the current time of prompt generation) with max length of 16
if the''' + food_name + ''' is incorrectly spelled due to user error, deduce from best match
IMPORTANT: You must respond with only the JSON object. Do not include any other text, explanations, or markdown formatting like
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
        
        end = time.time()
        elapsed = end - start

        print(f"Elapsed time: {elapsed} seconds")
        
        return result_dict
        
    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse JSON response for '{food_name}': {e}")
        logger.error(f"Raw response: {response.text}")
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        logger.error(f"Error in analyze_nutrition_facts for '{food_name}': {e}")
        raise HTTPException(status_code=500, detail=str(e))