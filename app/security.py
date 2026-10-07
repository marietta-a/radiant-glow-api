"""API key authentication.

Clients send the key in the X-API-Key header. Admins send RADIANT_GLOW_ADMIN_KEY in X-Admin-Key
to rotate the client key (see app/routers/admin_router.py).
"""
import hmac
import os
import secrets
import tempfile
import threading
from pathlib import Path
from typing import Optional

from dotenv import dotenv_values
from fastapi import HTTPException, Security
from fastapi.security import APIKeyHeader

API_KEY_NAME = "RADIANT_GLOW_API_KEY"
ADMIN_KEY_NAME = "RADIANT_GLOW_ADMIN_KEY"
ENV_PATH = Path(__file__).resolve().parent.parent / ".env"

_api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)
_admin_key_header = APIKeyHeader(name="X-Admin-Key", auto_error=False)

_lock = threading.Lock()
_cached: tuple[float, Optional[str]] = (-1.0, None)


def _file_value() -> Optional[str]:
    """The key as stored in .env, re-read only when the file changes so every worker sees a rotation."""
    global _cached
    try:
        mtime = ENV_PATH.stat().st_mtime
    except OSError:
        return None
    if _cached[0] != mtime:
        _cached = (mtime, dotenv_values(ENV_PATH).get(API_KEY_NAME))
    return _cached[1]


def current_api_key() -> Optional[str]:
    return _file_value() or os.environ.get(API_KEY_NAME)


def _matches(provided: Optional[str], expected: Optional[str]) -> bool:
    return bool(provided and expected) and hmac.compare_digest(provided.encode(), expected.encode())


async def require_api_key(provided: Optional[str] = Security(_api_key_header)) -> None:
    expected = current_api_key()
    if not expected:
        # Fail closed: never serve requests when the server has no key configured
        raise HTTPException(status_code=503, detail=f"Server {API_KEY_NAME} is not configured")
    if not _matches(provided, expected):
        raise HTTPException(status_code=401, detail="Invalid or missing API key", headers={"WWW-Authenticate": "ApiKey"})


async def require_admin_key(provided: Optional[str] = Security(_admin_key_header)) -> None:
    expected = os.environ.get(ADMIN_KEY_NAME)
    if not expected:
        raise HTTPException(status_code=503, detail=f"Server {ADMIN_KEY_NAME} is not configured")
    if not _matches(provided, expected):
        raise HTTPException(status_code=401, detail="Invalid or missing admin key", headers={"WWW-Authenticate": "ApiKey"})


def _write_env_key(new_key: str) -> bool:
    """Replace (or add) the key line in .env atomically. False when there is no writable .env."""
    if not ENV_PATH.exists():
        return False
    lines = ENV_PATH.read_text().splitlines()
    entry = f"{API_KEY_NAME}={new_key}"
    for i, line in enumerate(lines):
        if line.startswith(f"{API_KEY_NAME}="):
            lines[i] = entry
            break
    else:
        lines.append(entry)
    fd, tmp = tempfile.mkstemp(dir=ENV_PATH.parent, prefix=".env.")
    try:
        with os.fdopen(fd, "w") as f:
            f.write("\n".join(lines) + "\n")
        os.chmod(tmp, ENV_PATH.stat().st_mode & 0o777)
        os.replace(tmp, ENV_PATH)
    except Exception:
        if os.path.exists(tmp):
            os.unlink(tmp)
        raise
    return True


def rotate_api_key() -> tuple[str, bool]:
    """Generate a new key; the old one stops working immediately. Returns (key, persisted_to_env_file)."""
    new_key = secrets.token_urlsafe(32)
    with _lock:
        try:
            persisted = _write_env_key(new_key)
        except OSError:
            persisted = False
        os.environ[API_KEY_NAME] = new_key
    return new_key, persisted
