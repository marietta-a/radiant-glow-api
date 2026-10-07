from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel, Field


class ItemCount(BaseModel):
    label: str
    count: int = 1
    emoji: Optional[str] = None


class MealItemsPayload(BaseModel):
    items: list[dict[str, Any]] = Field(..., description="Items as returned by /meal-items (each has a label)")


class EdiblePayload(BaseModel):
    items: list[str]


class NutritionFromItemsPayload(BaseModel):
    items: list[ItemCount]


class CategoryItemsPayload(BaseModel):
    food_category: str
    type: Optional[str] = None
    country: Optional[str] = None
    state: Optional[str] = None
    is_endorsed: bool = False
    total: int = Field(10, ge=1, le=20)


class DietHistoryPayload(BaseModel):
    histories: list[dict[str, Any]] = []


class SuggestedDietPayload(BaseModel):
    health_goals: str
    country: Optional[str] = None
    state: Optional[str] = None
    time: Optional[datetime] = None


class RecipeStorePayload(BaseModel):
    name: str
    recipe: dict[str, Any]


class RecipeEditPayload(RecipeStorePayload):
    device_id: str
