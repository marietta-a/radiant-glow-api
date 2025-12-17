import logging
from fastapi import HTTPException
from typing import Dict, Optional
from app.models.server_response import ServerResponse

from app.services.nutrition_fact_service_new import analyze_nutrition_facts, analyze_nutrition_facts_from_image

logger = logging.getLogger(__name__)


async def process_nutrion_fact_from_image_new(file):
    try:
        image_bytes = await file.read()
        result = analyze_nutrition_facts_from_image(image_bytes, file.content_type)
        return ServerResponse(name= file.filename, data=result, status="success")
    except Exception as e:
        logger.error(f"Unexpected error from processing image: {e}")
        raise HTTPException(status_code=500, detail=str(e))

async def process_nutrition_facts_new(food_name: str):
    try:
        # Validate input
        if not food_name or not food_name.strip():
            raise HTTPException(
                status_code=400,
                detail="Food name parameter is required and cannot be empty"
            )
        
        
        # This now returns a dictionary or None
        result = await analyze_nutrition_facts(food_name)

        # Check if the analysis was successful
        if result is None:
            raise HTTPException(
                status_code=422,
                detail=f"Could not process or find nutrition facts for '{food_name}'. The AI model could not return a valid analysis."
            )
        
        # Validate that we have at least basic structure
        if not isinstance(result, dict) or 'name' not in result:
            raise HTTPException(
                status_code=422,
                detail=f"Invalid analysis result format for '{food_name}'"
            )
        
        return ServerResponse(name= food_name, data=result, status="success")

    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        logger.error(f"Unexpected error for food_name '{food_name}': {e}", exc_info=True)
        raise HTTPException(
            status_code=500, 
            detail=f"An internal server error occurred while processing '{food_name}'"
        )
