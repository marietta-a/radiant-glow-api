"""Lets a client check whether its API key is valid before making real calls."""
from typing import Optional

from fastapi import APIRouter, HTTPException, Security
from fastapi.security import APIKeyHeader

from app.security import API_KEY_NAME, _matches, current_api_key

router = APIRouter(prefix="/api/auth", tags=["auth"])

_api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)


@router.get("/verify")
async def verify(provided: Optional[str] = Security(_api_key_header)):
    """Always 200 with {"valid": true|false}, so clients can read the answer without handling a 401."""
    expected = current_api_key()
    if not expected:
        raise HTTPException(status_code=503, detail=f"Server {API_KEY_NAME} is not configured")
    return {"valid": _matches(provided, expected)}
