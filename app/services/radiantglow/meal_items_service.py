"""Ports of gemini_ai_meal_items_service.dart and the item-count / edibility helpers of gemini_ai_service.dart."""
from __future__ import annotations

import json
from collections import Counter

from app.config import model_lite, vision_model
from app.services.radiantglow.common import NUTRITION_RULES, llm_json, unwrap_list


async def get_meal_items(image_bytes: bytes, mime_type: str) -> list[dict]:
    """Dish name and its items (with bounding boxes) detected in a meal photo."""
    prompt = '''Analyze the image and provide a detailed breakdown of the dish. Identify the name of the dish and list its key food items or ingredients (ensure high accuracy in recognition by considering colors, textures, and common culinary patterns).
If unsure, suggest the most probable dish name and ingredients based on the visual data. Avoid assumptions without visual evidence.
If after processing it is inedible or not safe for drinking, isProcessable MUST be false and message must state the reason for not processing the image; otherwise message is null.

Return JSON as:
{"results": [{"dish": "Salad", "isProcessable": true, "message": null,
  "items": [{"label": "Avocado (sliced)", "box_2d": [65, 18, 246, 191]}]}]}
box_2d is [ymin, xmin, ymax, xmax] normalised to 0-1000.'''
    data = await llm_json(prompt, model=vision_model, image_bytes=image_bytes, mime_type=mime_type)
    return unwrap_list(data, "results")


def count_meal_items(items: list[dict]) -> list[dict]:
    """Distinct labels and how often each occurs (replaces the LLM call used by the app; counting is exact)."""
    counts: Counter = Counter()
    names: dict[str, str] = {}
    for item in items:
        label = str(item.get("label", "")).strip()
        if label:
            counts[label.lower()] += 1
            names.setdefault(label.lower(), label)
    return [{"label": names[k], "count": c} for k, c in counts.items()]


async def check_edible(items: list) -> dict:
    """Whether a list of items is fit to process. Returns {"is_edible": bool, "message": [str]}."""
    prompt = f'''Filter the list of items and say whether it should be processed. Return JSON as {{"is_edible": true, "message": ["..."]}}.
- is_edible is true when at least one item is edible and appropriate for all ages; message then lists the edible items.
- is_edible is false when no item is edible ("No edible items found"), an item is NSFW ("NSFW") or not appropriate for all ages (e.g. alcohol: "Beer is not appropriate for all ages"); message lists the reasons.

Items: {json.dumps(items)}'''
    data = await llm_json(prompt, model=model_lite)
    if isinstance(data, list):
        data = data[0] if data else {}
    message = data.get("message", [])
    return {
        "is_edible": data.get("is_edible") is True,
        "message": message if isinstance(message, list) else [str(message)],
    }


async def get_nutritional_data_from_item_count(items: list[dict]) -> list[dict]:
    """Nutrition data for [{label, count, emoji}] items."""
    prompt = f'''For each item below give: overall nutrient proportion (e.g. {{"protein": "0.65", "fat": "0.35"}}) as nutrient_proportion, emoji, calories_aggregate, health_benefit (list, which should also indicate illnesses it may help with), health_risk (list) and a risk color for each item.
Note:
1. calories_aggregate is per serving, e.g. "70 / serving".
2. color must be "green", "yellow" or "red" and must not be null.
3. Use maximum accuracy for computation.
{NUTRITION_RULES}

Return JSON as:
{{"results": [{{"label": "egg", "count": 8, "emoji": "🥚",
  "nutrient_proportion": {{"protein": "0.6", "fat": "0.3", "carbohydrate": "0.1"}},
  "calories_aggregate": "70 / serving",
  "health_benefit": ["Rich in protein and choline"], "health_risk": ["High cholesterol content"],
  "color": "yellow"}}]}}

Items: {json.dumps(items)}'''
    return unwrap_list(await llm_json(prompt, model=model_lite), "results")
