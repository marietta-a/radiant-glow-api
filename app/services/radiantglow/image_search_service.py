"""Finds an image path (URL) for a food item or dish. Never waits on provider rate limits."""
from __future__ import annotations

from app.config import logger
from app.services.image_generator_service import find_image_if_available
from app.services.radiantglow.common import clean_name


async def get_image(item: str) -> dict:
    """{"image_path": url | None, "credit": attribution | None} for the item.

    credit is set for Unsplash photos and must be shown next to them ("Photo by <photographer> on
    Unsplash", linking photographer_url and unsplash_url).
    """
    item = (item or "").strip()
    if item:
        try:
            url, credit = await find_image_if_available(f"{item} food dish")
            return {"image_path": url, "credit": credit}
        except Exception as e:
            logger.warning(f"Image lookup failed for '{item}': {e}")
    return {"image_path": None, "credit": None}


async def get_image_path(item: str) -> str | None:
    """Image URL for the item, or None when no provider has capacity or finds one."""
    return (await get_image(item))["image_path"]


async def search_image(item: str) -> dict:
    """Same as get_image for user input: rejects empty or oversized names first."""
    return await get_image(clean_name(item, "item"))
