"""Ports of analyzeDietHistoryInsights and getSuggestedDiet from gemini_ai_service.dart.

The app read the meal history and user profile from local storage; here the client sends them.
"""
from __future__ import annotations

import json
from datetime import datetime

from app.config import model
from app.services.radiantglow.common import llm_json, unwrap_list


async def analyze_diet_history(histories: list[dict]) -> dict:
    prompt = f'''Analyze the user's meal history below and return JSON with exactly these attributes:
- potential_disease: list of diseases the eating pattern may lead to
- projected_time: text estimating when these risks could arise if the pattern continues
- limitations: list of caveats of this assessment (single meal/day data, approximate calories, not medical advice)
If no data is available, every attribute must have the value "no data provided for analysis".

Meal history: {json.dumps(histories)}'''
    return await llm_json(prompt, model=model)


async def get_suggested_diet(
    health_goals: str, country: str | None, state: str | None, time: datetime | None = None
) -> list[dict]:
    when = (time or datetime.now()).isoformat()
    prompt = f'''Suggest meals based on the local cuisines of the user's location and the time of day (morning: breakfast, afternoon: lunch, evening: dinner).
Each suggested meal/fruit/snack must meet the user's health goals and have a color of green or yellow. Suggest at most 4 foods.

Return JSON as {{"results": [{{
  "food_name": "name of food/fruit/snack",
  "item": "name of the item in the meal",
  "quantity_str": "predicted quantity (e.g. 2 slices)",
  "calories": "calories for the quantity, with a short reason for the value",
  "nutritive_value": "string",
  "color": "green | yellow",
  "health_goals": ["string"],
  "health_benefits": ["string"],
  "potential_disease_risks": ["string"]
}}]}}

Goals: {health_goals}
Location: country {country or "unknown"}, state {state or "unknown"}
Time: {when}'''
    return unwrap_list(await llm_json(prompt, model=model), "results")
