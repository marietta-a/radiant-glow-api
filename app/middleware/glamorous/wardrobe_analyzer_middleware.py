import logging
from fastapi import HTTPException
from typing import Dict, Optional
from app.models.server_response import ServerResponse

from app.services.glamorous.wardrobe_analyzer_service import analyze_closet

logger = logging.getLogger(__name__)


async def process_wardrobe_analyzer(file):
    try:
        image_bytes = await file.read()
        result = analyze_closet(image_bytes, file.content_type)
        return ServerResponse(name= file.filename, data=result, status="success")
    except Exception as e:
        logger.error(f"Unexpected error from processing image: {e}")
        raise HTTPException(status_code=500, detail=str(e))
