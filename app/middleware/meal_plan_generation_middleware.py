import logging
from fastapi import HTTPException, Request
from app.models.server_response import ServerResponse
from app.services.meal_plan_generation_service import generate_meal_plan


logger = logging.getLogger(__name__)


async def process_meal_plan_generation(payload: Request):
    try:
        data = await payload.json()
        result = await generate_meal_plan(payload)
        return ServerResponse(name= data, data=result, status="success")
    except Exception as e:
        logger.error(f"Unexpected error from processing image: {e}")
        raise HTTPException(status_code=500, detail=str(e))