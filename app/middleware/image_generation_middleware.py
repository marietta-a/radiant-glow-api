from fastapi import HTTPException
from app.models.server_response import ServerResponse
from app.services.image_generator_service import get_duckduckgo_image_urls


async def process_image(query, limit):
    try:
        urls = await get_duckduckgo_image_urls(query, limit)
        return {"query": query, "image_urls": urls}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    

async def process_image_generation(query, limit):
    try:
        urls = await get_duckduckgo_image_urls(query, limit)
        return ServerResponse(data=urls,name=query,status="success")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))