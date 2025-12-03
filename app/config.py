
import os
from google import genai
from dotenv import load_dotenv
import logging

# Load environment variables from .env file
load_dotenv()

genAiClient = genai.Client(
    api_key=os.environ.get("GEMINI_API_KEY"),
)

model = "gemini-2.5-flash-lite"
model_lite = "gemini-2.0-flash-lite"



# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)