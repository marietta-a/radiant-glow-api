from __future__ import annotations

import asyncio
import base64
import logging
import os
import re
import time

import requests
from dotenv import load_dotenv
from google import genai
from google.genai import types

from app.rate_limiter import RateLimiter

# Load environment variables from .env file
load_dotenv()

# Any OpenAI-compatible chat completions API works. The defaults use Groq's free tier
# (https://console.groq.com/keys). To switch provider, change the three env vars, e.g.
#   OpenRouter: LLM_BASE_URL=https://openrouter.ai/api/v1  (use ":free" models)
#   Ollama:     LLM_BASE_URL=http://localhost:11434/v1     (fully local, no limits)
LLM_BASE_URL = os.environ.get("LLM_BASE_URL", "https://api.groq.com/openai/v1")
LLM_API_KEY = os.environ.get("LLM_API_KEY") or os.environ.get("GROQ_API_KEY")

model = os.environ.get("LLM_MODEL", "openai/gpt-oss-120b")
model_lite = os.environ.get("LLM_MODEL_LITE", "openai/gpt-oss-20b")
vision_model = os.environ.get("LLM_VISION_MODEL", "qwen/qwen3.8-27b")

# Gemini is still used by the Mavita and category-item nutrition services.
genAiKey = os.environ.get("GEMINI_API_KEY")
# Optional: only created when a key is set, so Groq-only setups can still start.
genAiClient = genai.Client(api_key=genAiKey) if genAiKey else None

supabaseUrl = os.environ.get("SUPABASE_URL")
supabaseAnonKey = os.environ.get("SUPABASE_ANON_API_KEY")
supabaseUserId = os.environ.get("SUPABASE_USER_ID")

gemini_model = "gemini-flash-lite-latest"
mavita_model = "gemini-3-flash-preview"

# ImageConfig.image_size only exists in newer google-genai releases (not available on Python 3.9).
_image_config = types.ImageConfig(image_size="1K") if "image_size" in types.ImageConfig.model_fields else None
image_content_config = types.GenerateContentConfig(
    thinking_config=types.ThinkingConfig(thinking_budget=0),
    image_config=_image_config,
    response_mime_type="application/json",
)
thinking_content_config = types.GenerateContentConfig(
    thinking_config=types.ThinkingConfig(thinking_budget=0),
    response_mime_type="application/json",
)

# Groq's free tier allows ~30 requests/minute per model; stay under it and queue the rest.
LLM_REQUESTS_PER_MINUTE = int(os.environ.get("LLM_REQUESTS_PER_MINUTE", 25))
LLM_MAX_CONCURRENCY = int(os.environ.get("LLM_MAX_CONCURRENCY", 4))
_llm_limiters: dict[str, RateLimiter] = {}
_llm_semaphore: asyncio.Semaphore | None = None

LLM_TIMEOUT = 60
LLM_MAX_RETRIES = 3

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def _generate_json_text_sync(prompt: str, model_name: str, image_bytes: bytes | None, mime_type: str | None) -> str:
    if not LLM_API_KEY:
        raise RuntimeError("Missing LLM_API_KEY (or GROQ_API_KEY) environment variable")

    if image_bytes is not None:
        encoded = base64.b64encode(image_bytes).decode()
        content = [
            {"type": "text", "text": prompt},
            {"type": "image_url", "image_url": {"url": f"data:{mime_type or 'image/jpeg'};base64,{encoded}"}},
        ]
    else:
        content = prompt

    payload = {
        "model": model_name,
        "messages": [{"role": "user", "content": content}],
        "response_format": {"type": "json_object"},
        "temperature": 0.2,
    }
    headers = {"Authorization": f"Bearer {LLM_API_KEY}"}

    for attempt in range(LLM_MAX_RETRIES):
        response = requests.post(
            f"{LLM_BASE_URL}/chat/completions", json=payload, headers=headers, timeout=LLM_TIMEOUT
        )
        if response.status_code == 429 and attempt < LLM_MAX_RETRIES - 1:
            wait = float(response.headers.get("retry-after", 2 ** (attempt + 1)))
            logger.warning(f"LLM rate limited, retrying in {wait}s")
            time.sleep(min(wait, 20))
            continue
        # The model sometimes returns an empty/invalid JSON generation; a retry normally succeeds
        if response.status_code == 400 and "json_validate_failed" in response.text and attempt < LLM_MAX_RETRIES - 1:
            logger.warning(f"LLM returned invalid JSON for {model_name}, retrying")
            continue
        if not response.ok:
            logger.error(f"LLM request failed ({response.status_code}) for {model_name}: {response.text[:500]}")
        response.raise_for_status()
        text =response.json()["choices"][0]["message"]["content"].strip()
        # Some models wrap JSON in markdown fences despite JSON mode
        return re.sub(r"^```(?:json)?\s*|\s*```$", "", text)


async def generate_json_text(
    prompt: str,
    model: str = model,
    image_bytes: bytes | None = None,
    mime_type: str | None = None,
) -> str:
    """Send a prompt (optionally with an image) and return the model's JSON text."""
    if image_bytes is not None:
        model = vision_model
    global _llm_semaphore
    if _llm_semaphore is None:
        _llm_semaphore = asyncio.Semaphore(LLM_MAX_CONCURRENCY)
    limiter = _llm_limiters.setdefault(model, RateLimiter(LLM_REQUESTS_PER_MINUTE, 60))
    async with _llm_semaphore:
        await limiter.acquire()  # waits (FIFO) when the per-minute budget for this model is used up
        return await asyncio.to_thread(_generate_json_text_sync, prompt, model, image_bytes, mime_type)
