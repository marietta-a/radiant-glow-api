"""Port of gemini_ai_recipe_service.dart: recipe + nutrition data for a dish."""
from __future__ import annotations

from app.config import model_lite
from app.services.radiantglow.common import (
    NUTRITION_JSON_TEMPLATE, NUTRITION_RULES, clean_name, llm_json, not_processable, unwrap_list,
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
    results = unwrap_list(await llm_json(prompt, model=model_lite), "results")
    if not results:
        raise ValueError("Model returned no results")
    if results[0].get("isProcessable") is False:
        return not_processable(results[0].get("message"))
    return results[0]
