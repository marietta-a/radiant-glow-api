
import os
from google import genai
from dotenv import load_dotenv
import logging
from google.genai import types

# Load environment variables from .env file
load_dotenv()

genAiClient = genai.Client(
    api_key=os.environ.get("GEMINI_API_KEY"),
)

model = "gemini-2.5-flash-lite"
model_lite = "gemini-2.0-flash-lite"

image_content_config = types.GenerateContentConfig(
    thinking_config = types.ThinkingConfig(
        thinking_budget=0,
    ),
    image_config=types.ImageConfig(
        image_size="1K",
    ),
    response_mime_type="application/json",
)
thinking_content_config = types.GenerateContentConfig(
    thinking_config = types.ThinkingConfig(
        thinking_budget=0,
    ),
    response_mime_type="application/json",
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)