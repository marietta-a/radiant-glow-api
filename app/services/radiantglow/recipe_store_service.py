"""Port of recipe_store_service.dart: recipes stored in Supabase through the recipe RPC functions.

Lookups and caching fail quietly (the caller falls back to generating); saving an edit raises.
"""
from __future__ import annotations

import asyncio

import requests

from app.config import logger, supabaseAnonKey, supabaseUrl

TIMEOUT = 12


def _rpc_sync(function: str, params: dict):
    if not supabaseUrl or not supabaseAnonKey:
        raise RuntimeError("SUPABASE_URL / SUPABASE_ANON_API_KEY are not configured")
    response = requests.post(
        f"{supabaseUrl}/rest/v1/rpc/{function}",
        headers={
            "apikey": supabaseAnonKey,
            "Authorization": f"Bearer {supabaseAnonKey}",
            "Content-Type": "application/json",
        },
        json=params,
        timeout=TIMEOUT,
    )
    if not response.ok:
        raise RuntimeError(f"{function} failed ({response.status_code}): {response.text}")
    return response.json() if response.content else None


async def _rpc(function: str, params: dict):
    return await asyncio.to_thread(_rpc_sync, function, params)


async def fetch_recipe(name: str, device_id: str | None) -> dict | None:
    """The user's edited version of a dish if they have one, otherwise the shared version."""
    try:
        rows = await _rpc("get_recipe", {"p_name": name, "p_device_id": device_id})
        if not rows:
            return None
        row = rows[0]
        data = row["data"]
        if not data.get("recipe"):
            return None
        return {"recipe": data, "is_edited": row.get("is_edited") is True}
    except Exception as e:
        logger.error(f"fetch_recipe failed: {e}")
        return None


async def search_recipe_names(query: str) -> list[str]:
    try:
        rows = await _rpc("search_recipe_names", {"p_query": query})
        return [str(row["name"]) for row in rows or []]
    except Exception as e:
        logger.error(f"search_recipe_names failed: {e}")
        return []


async def cache_recipe(name: str, recipe: dict) -> bool:
    try:
        await _rpc("cache_recipe", {"p_name": name, "p_data": recipe})
        return True
    except Exception as e:
        logger.error(f"cache_recipe failed: {e}")
        return False


async def save_recipe_edit(device_id: str, name: str, recipe: dict) -> None:
    await _rpc("save_recipe_edit", {"p_device_id": device_id, "p_name": name, "p_data": recipe})
