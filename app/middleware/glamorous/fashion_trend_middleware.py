import logging
from fastapi import HTTPException
from typing import Dict, Optional
from app.models.server_response import ServerResponse

from app.services.glamorous.fashion_trend_service import fetch_vogue_trends

logger = logging.getLogger(__name__)


async def process_fashion_trend():
    try:
        result = fetch_vogue_trends()
        return ServerResponse(name= 'fashion trend', data=result, status="success")
    except Exception as e:
        logger.error(f"Unexpected error from processing image: {e}")
        raise HTTPException(status_code=500, detail=str(e))
