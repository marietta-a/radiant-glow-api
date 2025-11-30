import logging
from fastapi import HTTPException, Request
from app.models.server_response import ServerResponse
from app.services.recipe_generation_service import get_recipe


logger = logging.getLogger(__name__)


async def process_recipe(food_name: str):
    try:
        result = await get_recipe(food_name)
        return ServerResponse(name= food_name, data=result, status="success")
    except Exception as e:
        logger.error(f"Unexpected error from processing meal plan {food_name}: {e}")
        raise HTTPException(status_code=500, detail=str(e))