"""Port of image_analysis_service.dart: nutrition analysis of a food photo."""
from __future__ import annotations

from app.config import model, vision_model
from app.services.radiantglow.common import (
    NUTRITION_JSON_TEMPLATE, NUTRITION_RULES, llm_json, not_processable, unwrap_list,
)


async def analyze_image(image_bytes: bytes, mime_type: str) -> list[dict]:
    prompt = f'''You are a nutrition analyst. Analyze the food image and return JSON.

Rules:
- Identify the dish/ingredient/item and its key ingredients. Use colors, textures and common culinary patterns for accuracy.
{NUTRITION_RULES}
- recipe: 4-7 clear steps.

Return a single JSON object with this shape:
{NUTRITION_JSON_TEMPLATE}'''
    data = await llm_json(prompt, model=vision_model, image_bytes=image_bytes, mime_type=mime_type)
    results = unwrap_list(data, "results")
    if not results:
        raise ValueError("Model returned no results")
    if results[0].get("isProcessable") is False:
        return [not_processable(results[0].get("message"))]
    return results
