
from pydantic import BaseModel

class CategoryItemPayload(BaseModel):
    """
    Model representing the payload for meal plan generation.
    """
    healthGoalId: int
    healthGoal: str
    category: str
    categoryId: int
    description: str
    numberOfSuggestions: int
    country: str
    state: str
    city: str