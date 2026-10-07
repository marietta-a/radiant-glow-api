"""Port of image_analysis_service.dart: nutrition analysis of a food photo."""
from __future__ import annotations

from app.config import model, vision_model
from app.services.radiantglow.common import (
    NUTRITION_JSON_TEMPLATE, NUTRITION_RULES, generate_nutrition,
)


async def analyze_image(image_bytes: bytes, mime_type: str) -> list[dict]:
    prompt = f'''You are a nutrition analyst. Analyze the food image and return JSON.

Rules:
- Identify the dish/ingredient/item and its key ingredients. Use colors, textures and common culinary patterns for accuracy.
{NUTRITION_RULES}
- recipe: 4-7 clear steps.

Return a single JSON object with this shape:
{NUTRITION_JSON_TEMPLATE}'''
    return [await generate_nutrition(prompt, model=vision_model, image_bytes=image_bytes, mime_type=mime_type)]
