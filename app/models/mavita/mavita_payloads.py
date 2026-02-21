
from typing import List, Optional
from fastapi import FastAPI, HTTPException, Body
from pydantic import BaseModel, Field


class UserProfile(BaseModel):
    name: str
    age: int
    goals: List[str]

class Macronutrients(BaseModel):
    protein: str
    carbs: str
    fats: str
    fiber: str

class Nutrient(BaseModel):
    name: str
    benefit: str

class MealAnalysis(BaseModel):
    id: str
    timestamp: int
    isFood: bool
    foodName: str
    description: str
    glycemicScore: float
    iIndexScore: float
    portionAnalysis: str
    macronutrients: Macronutrients
    biologicalPathways: List[str]
    pairingSuggestions: List[str]
    nutrients: List[Nutrient]
    goalAlignment: str
    healthRisks: str

class ImageAnalysisRequest(BaseModel):
    base64Image: str = Field(..., description="Base64 encoded string of the meal image")
    mimeType: str = Field("image/jpeg", description="The mime type of the image (e.g. image/png)")
    profile: UserProfile

class RecipeRequest(BaseModel):
    goal: str
    cuisine: str

class BioReportRequest(BaseModel):
    meals: List[MealAnalysis]
    profile: UserProfile