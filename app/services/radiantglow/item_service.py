"""Port of gemini_ai_item_service.dart and item_search_service.dart (search suggestions + item svg)."""
from __future__ import annotations

from app.config import model_lite
from app.services.radiantglow.common import clean_name, extract_svg, llm_json, unwrap_list

SVG_SIZE = 256
_SVG_CACHE_MAX = 500
_svg_cache: dict[str, str] = {}


async def get_dish_items(dish: str) -> list[dict]:
    """Edible items (as label) used in preparing a dish."""
    dish = clean_name(dish, "dish")
    prompt = f'''Generate the list of edible items used in preparing the dish below. Return JSON as
{{"items": [{{"label": "Garri"}}, {{"label": "Okra"}}, {{"label": "Palm Oil"}}]}}
Use plain names (e.g. "Pepper (Chili)", "Seasoning Cubes (e.g., Maggi, Knorr)"), no descriptions.

Dish: {dish}'''
    items = unwrap_list(await llm_json(prompt, model=model_lite), "items")
    return [{"label": str(i["label"]).strip()} for i in items if isinstance(i, dict) and i.get("label")]


async def search_items(search_key: str) -> list[str]:
    """Food and drink names matching a search key; empty if it is not a food."""
    if not search_key or not search_key.strip():
        return []
    search_key = clean_name(search_key, "search key")
    prompt = f'''You suggest foods and drinks for a recipe search. Given a search key, return up to 15 distinct food or drink names that start with or contain it, as JSON: {{"names": ["string"]}}
- Cover the different varieties of the key (e.g. "cake" gives chocolate cake, carrot cake, red velvet cake, ...), as well as ingredients and local or regional dishes that match.
- Every name must be something that can be eaten or drunk. If the search key is not a food or drink, or is unsafe to eat or drink, return {{"names": []}}.
- Use plain names, no descriptions or numbering.

Search key: {search_key}'''
    data = await llm_json(prompt, model=model_lite)
    names = data.get("names", []) if isinstance(data, dict) else data
    return [str(n).strip() for n in names if str(n).strip()]


async def generate_item_svg(item: str) -> str | None:
    """A flat illustration of the item as svg markup; None if the model produced nothing usable."""
    item = clean_name(item, "item")
    key = item.lower()
    if key in _svg_cache:
        return _svg_cache[key]

    prompt = f'''Draw a flat, colourful, appetising illustration of the food item: {item}
Return JSON as {{"svg": "<svg ...>...</svg>"}} where the value is only the svg markup.
Rules:
- root element: <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {SVG_SIZE} {SVG_SIZE}">
- the food is centred and fills most of the canvas, no background
- use only path, circle, ellipse, rect, polygon, line, g, linearGradient and radialGradient
- style with attributes only (fill, stroke, opacity); no <style>, class, filter, mask, text, image or script
- at most 40 shapes'''
    data = await llm_json(prompt, model=model_lite)
    svg = extract_svg(data.get("svg") if isinstance(data, dict) else None)
    if svg:
        if len(_svg_cache) >= _SVG_CACHE_MAX:
            _svg_cache.pop(next(iter(_svg_cache)))
        _svg_cache[key] = svg
    return svg
