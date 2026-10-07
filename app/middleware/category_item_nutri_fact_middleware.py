import logging
from fastapi import HTTPException
from app.models.server_response import ServerResponse

from app.services.category_item_nutri_fact_service import analyze_category_item_nutri_fact, CategoryItemPayload

logger = logging.getLogger(__name__)


async def process_health_goal_category_items(payload: CategoryItemPayload):
    try:
        # Validate input
        result = await analyze_category_item_nutri_fact(payload)

        # Check if the analysis was successful
        if result is None:
            raise HTTPException(
                status_code=422,
                detail=f"Could not process or find nutrition facts for '{payload.goalCategoryDescription}'. The AI model could not return a valid analysis."
            )
        
        return ServerResponse(name= payload.category, data=result, status="success")

    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        logger.error(f"Unexpected error for payload.category '{payload.category}': {e}", exc_info=True)
        raise HTTPException(
            status_code=500, 
            detail=f"An internal server error occurred while processing '{payload.category}'"
        )
