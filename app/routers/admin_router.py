"""Admin endpoints. Authenticated with RADIANT_GLOW_ADMIN_KEY (X-Admin-Key), not the client API key."""
from fastapi import APIRouter, Depends, Response

from app.config import logger
from app.security import require_admin_key, rotate_api_key

router = APIRouter(prefix="/api/admin", tags=["admin"], dependencies=[Depends(require_admin_key)])


@router.post("/rotate-key")
async def rotate_key(response: Response):
    """Replace RADIANT_GLOW_API_KEY. The new key is returned once; the old key stops working immediately."""
    key, persisted = rotate_api_key()
    logger.warning("RADIANT_GLOW_API_KEY rotated (persisted to .env: %s)", persisted)
    response.headers["Cache-Control"] = "no-store"
    return {
        "api_key": key,
        "persisted": persisted,
        "note": None if persisted else "No .env file found: the new key lives only in this process and is lost on restart. "
        "Set RADIANT_GLOW_API_KEY in your host's environment too.",
    }
