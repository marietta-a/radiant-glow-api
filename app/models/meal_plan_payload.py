
from pydantic import BaseModel

class MealPlanPayload(BaseModel):
    """
    Model representing the payload for meal plan generation.
    """
    calories: int
    protein: int
    carbs: int
    fat: int
    country: str
    state: str
    city: str
    healthGoal: str
    promptDescription: str
    numberOfSuggestions: int