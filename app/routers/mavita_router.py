"""Endpoints for the Mavita app (see app/services/mavita)."""
from fastapi import APIRouter, Depends, File, UploadFile

from app.helper import parse_profile
from app.models.mavita.mavita_payloads import BioReportRequest, RecipeRequest, UserProfile
from app.services.mavita.mavita_service import analyze_meal_image, process_bio_report, process_longevity_plate

router = APIRouter(prefix="/api", tags=["mavita"])


@router.post("/analyze-meal")
async def analyze_meal(
    file: UploadFile = File(...),
    profile: UserProfile = Depends(parse_profile)
):
    image_bytes = await file.read()
    return analyze_meal_image(image_bytes, file.content_type, profile)


@router.post("/generate-longevity-plate")
async def generate_longevity_plate(request: RecipeRequest):
    # If this fails, the global_exception_handler catches it automatically
    recipes = process_longevity_plate(request)
    return recipes


@router.post("/generate-report")
async def get_bio_report(request: BioReportRequest):
    meals_dict = [meal.model_dump() for meal in request.meals]
    profile_dict = request.profile.model_dump()

    report = process_bio_report(meals_dict, profile_dict)
    return {"report": report}
