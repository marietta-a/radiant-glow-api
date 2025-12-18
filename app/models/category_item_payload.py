
from pydantic import BaseModel

class CategoryItemPayload(BaseModel):
    """
    Model representing the payload for meal plan generation.
    """
    
    healthGoal: str
    category: str
    numberOfSuggestions: int
    country: str
    state: str
    city: str