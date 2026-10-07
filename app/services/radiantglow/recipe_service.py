"""Port of gemini_ai_recipe_service.dart: recipe + nutrition data for a dish."""
from __future__ import annotations

from app.config import model_lite
from app.services.radiantglow.common import (
    NUTRITION_JSON_TEMPLATE, NUTRITION_RULES, clean_name, generate_nutrition,
)


async def get_recipe(item: str) -> dict:
    item = clean_name(item, "item")
    prompt = f'''You are a chef and nutrition analyst. Generate a recipe for the requested dish/ingredient/item and return JSON.

Rules:
- Use the traditional or most common version of the dish, including regional and local dishes (e.g. ekwang, eru, ndole). List every ingredient needed with a realistic quantity for 2-4 servings.
- emoji must never be empty: one to three emojis for the dish and one for each ingredient.
{NUTRITION_RULES}
- recipe: 5-10 clear, ordered steps that include cooking times and heat levels.

Return a single JSON object with this shape:
{NUTRITION_JSON_TEMPLATE}

Generate the recipe and nutrition data for: {item}'''
    return await generate_nutrition(prompt, model=model_lite)
