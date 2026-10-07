"""Shared prompts and helpers for the Radiant Glow Diet services."""
from __future__ import annotations

import json
import re
from typing import Any

from fastapi import HTTPException

from app.config import generate_json_text, logger

MAX_NAME_LENGTH = 2500

NUTRITION_JSON_TEMPLATE = '''{
  "dish": "string",
  "isProcessable": true,
  "message": null,
  "emoji": "string",
  "nutrient_proportion": {"protein": "0.30", "carbohydrates": "0.50", "fat": "0.20"},
  "calories_aggregate": "350 kcal/serving",
  "health_benefit": ["string"],
  "health_risk": ["string"],
  "ingredient": [
    {
      "name": "string",
      "quantity": "string",
      "emoji": "string",
      "risk_color": "green | yellow | red",
      "nutrient_proportion": {"protein": "0.30", "carbohydrates": "0.50", "fat": "0.20"},
      "calories_aggregate": "string",
      "health_benefit": ["string"],
      "health_risk": ["string"]
    }
  ],
  "recipe": ["string"],
  "risk_color": "green | yellow | red"
}'''

NOT_PROCESSABLE_RULE = (
    'If the request is not food or drink, or is unsafe to eat or drink, set isProcessable=false and put the '
    'reason in message. For every other field use "" for strings, "0.00" for proportions, [] for lists and '
    '"green" for risk_color. If it is processable, message must be null.'
)

NUTRITION_RULES = f'''- {NOT_PROCESSABLE_RULE}
- calories_aggregate is a string in kcal/serving, e.g. "350 kcal/serving".
- nutrient_proportion values are strings that add up to about 1.00, e.g. "0.40".
- Keep it concise: 2-3 health_benefit and 2-3 health_risk items per dish and per ingredient, one short sentence each.

risk_color rules (apply to EACH ingredient and to the overall dish):
- "green": nutrient-dense, whole or minimally processed, fine to eat regularly (vegetables, fruit, lean protein, fish, legumes, whole grains).
- "yellow": fine in moderation, with some concern (cheese, red meat, refined carbs in normal portions, salty sauces, fruit juice).
- "red": unhealthy, high in added sugar, refined flour, saturated or trans fat, or sodium, or heavily processed. Examples: cake, pastries, donuts, candy, ice cream, soda, deep-fried food, processed meats, refined sugar.
Do NOT default to "yellow". Desserts, sweet baked goods and fried foods are "red". A dish whose main ingredients are red is "red".'''


def clean_name(value: str | None, field: str = "name") -> str:
    """Trim a user supplied food name and reject empty or oversized values (it goes into a prompt)."""
    value = (value or "").strip()
    if not value:
        raise HTTPException(status_code=400, detail=f"{field} is required and cannot be empty")
    if len(value) > MAX_NAME_LENGTH:
        raise HTTPException(status_code=400, detail=f"{field} must be at most {MAX_NAME_LENGTH} characters")
    return value


async def llm_json(
    prompt: str,
    *,
    model: str | None = None,
    image_bytes: bytes | None = None,
    mime_type: str | None = None,
) -> Any:
    """Run a prompt and return the parsed JSON. Raises a 502 when the model returns invalid JSON."""
    kwargs: dict[str, Any] = {"image_bytes": image_bytes, "mime_type": mime_type}
    if model:
        kwargs["model"] = model
    text = await generate_json_text(prompt, **kwargs)
    try:
        return json.loads(text)
    except json.JSONDecodeError as e:
        logger.error(f"Model returned invalid JSON: {e}; raw response: {text}")
        raise HTTPException(status_code=502, detail="The AI model returned an invalid response")


def unwrap_list(data: Any, key: str) -> list:
    """JSON mode returns objects, so lists are requested as {key: [...]}. Accept a bare list or object too."""
    if isinstance(data, dict):
        if isinstance(data.get(key), list):
            return data[key]
        return [data]
    if isinstance(data, list):
        return data
    return []


def not_processable(message: str | None) -> dict:
    return {
        "dish": "",
        "isProcessable": False,
        "message": message,
        "emoji": "",
        "nutrient_proportion": {},
        "calories_aggregate": "",
        "health_benefit": [],
        "health_risk": [],
        "ingredient": [],
        "recipe": [],
        "risk_color": "green",
    }


_UNSAFE_SVG = re.compile(r"<\s*(script|foreignObject|iframe|image|style)\b|\bon\w+\s*=|javascript:", re.I)


def extract_svg(text: str | None) -> str | None:
    """Pull the svg markup out of a model response; None if absent or it contains active content."""
    match = re.search(r"<svg[\s\S]*</svg>", text or "")
    if not match or _UNSAFE_SVG.search(match.group(0)):
        return None
    return match.group(0)
