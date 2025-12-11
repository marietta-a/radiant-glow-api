import logging
from fastapi import HTTPException, Request
from app.models.server_response import ServerResponse
from app.services.meal_plan_by_time_generation_service import generate_meal_plan
from app.models.meal_plan_payload import MealPlanPayload


logger = logging.getLogger(__name__)


async def process_meal_by_time_plan_generation(payload: MealPlanPayload):
    try:
        result = await generate_meal_plan(payload)
        return ServerResponse(name= payload.healthGoal, data=result, status="success")
    except Exception as e:
        logger.error(f"Unexpected error from processing meal plan {payload}: {e}")
        raise HTTPException(status_code=500, detail=str(e))