"""Port of gemini_ai_nutritional_data_category_service.dart: healthy food suggestions grouped by category."""
from __future__ import annotations

from app.config import model_lite
from app.services.radiantglow.common import clean_name, llm_json, unwrap_list


async def get_category_items(
    food_category: str,
    type: str | None = None,
    country: str | None = None,
    state: str | None = None,
    is_endorsed: bool = False,
    total: int = 10,
) -> list[dict]:
    food_category = clean_name(food_category, "food_category")
    where = f" ({country}[{state}])" if country and not is_endorsed else ""
    subject = f"{type}: {food_category}" if type else food_category
    prompt = f'''Generate the top {total} {subject}{where} optimal health food items (green health range).
Return JSON as:
{{"results": [{{
  "category": "string", "description": "string",
  "items": [{{
    "label": "string",
    "emoji": "string (emoji wrapped in a string)",
    "nutrient_proportion": {{"protein": "0.40", "carbohydrates": "0.35", "fat": "0.25"}},
    "calories_aggregate": "300 kcal/serving",
    "health_benefit": ["string"],
    "health_risk": ["string"],
    "ingredient": [{{"name": "string", "quantity": "string", "emoji": "string"}}],
    "recipe": ["string"],
    "risk_color": "green"
  }}]
}}]}}
Health benefits should include tips on how {type or "the goal"} can be achieved. Recipes must be detailed and contain all ingredients.'''
    return unwrap_list(await llm_json(prompt, model=model_lite), "results")
