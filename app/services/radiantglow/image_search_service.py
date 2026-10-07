"""Finds an image path (URL) for a food item or dish. Never waits on provider rate limits."""
from __future__ import annotations

from app.config import logger
from app.services.image_generator_service import get_image_url_if_available
from app.services.radiantglow.common import clean_name


async def get_image_path(item: str) -> str | None:
    """Image URL for the item, or None when no provider has capacity or finds one."""
    item = (item or "").strip()
    if not item:
        return None
    try:
        return await get_image_url_if_available(f"{item} food dish")
    except Exception as e:
        logger.warning(f"Image lookup failed for '{item}': {e}")
        return None


async def search_image_path(item: str) -> str | None:
    """Same as get_image_path for user input: rejects empty or oversized names first."""
    return await get_image_path(clean_name(item, "item"))
