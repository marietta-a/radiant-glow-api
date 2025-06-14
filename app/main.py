from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import requests
from bs4 import BeautifulSoup
import urllib.parse
import re
from typing import List
import asyncio
import aiohttp
import time
import logging
from duckduckgo_search import DDGS

from app.ai_analysis import AIAnalysis

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

food_generator = AIAnalysis()


# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def fetch_url(session: aiohttp.ClientSession, url: str, headers: dict) -> str:
    """Fetches the content of a URL asynchronously."""
    try:
        async with session.get(url, headers=headers) as response:
            response.raise_for_status()
            return await response.text()
    except aiohttp.ClientError as e:
        logger.error(f"Request failed for {url}: {e}")
        raise HTTPException(status_code=500, detail=f"Request failed: {str(e)}")

async def parse_image_urls(html: str, limit: int) -> List[str]:
    """Parses image URLs from the HTML content."""
    soup = BeautifulSoup(html, 'html.parser')
    image_elements = soup.find_all('img', {'class': 'mimg'})  # Consider more robust selectors

    urls = []
    for img in image_elements[:limit]:
        src = img.get('data-src') or img.get('src')
        if src and src.startswith('http') and 'bing.net' in src:
            clean_url = re.sub(r'&.*$', '', src)
            urls.append(clean_url)
    return list(set(urls))[:limit]

async def get_bing_image_urls(query: str, limit: int = 10, delay: float = 0.5) -> List[str]:
    """Fetches Bing image URLs for consumables (food, drinks, etc.) asynchronously with rate limiting."""
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36"  # Updated User-Agent
    }

    refined_query = f"{query} food OR dish OR drink"
    encoded_query = urllib.parse.quote(refined_query)
    url = f"https://www.bing.com/images/search?q={encoded_query}"

    try:
        async with aiohttp.ClientSession() as session:
            await asyncio.sleep(delay)  # Rate limiting: delay *before* request
            html = await fetch_url(session, url, headers)
            return await parse_image_urls(html, limit)

    except HTTPException as e:
        raise e  # Re-raise the HTTPException
    except Exception as e:
        logger.exception("Scraping failed") # Log the full exception
        raise HTTPException(status_code=500, detail="Scraping failed")

async def get_duckduckgo_image_urls(query: str, num_images: int = 2) -> list[str]:
    """Search DuckDuckGo Images and return a list of image URLs."""
    if not isinstance(num_images, int) or num_images <= 0:
        raise ValueError("num_images must be a positive integer")

    ddgs = DDGS()  # Initialize DuckDuckGo Search
    results = ddgs.images(query, max_results=num_images)  # Corrected method call
    return [result["image"] for result in results if "image" in result]


@app.get("/api/images")
async def get_images(query: str, limit: int = 10):
    try:
        # urls = await get_bing_image_urls(query, limit)
        urls = await get_duckduckgo_image_urls(query, limit)
        return {"query": query, "image_urls": urls}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@app.get("/api/food-search")
async def search_food(query):
    try:
     return food_generator.search_food(query)
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail=str(e))
    
@app.get("/api/get-diet-suggestions")
async def get_diet_suggestions(category, category_item, country=None, state=None, city=None, limit=20):
    try:
     return food_generator.get_diet_suggestions(category, category_item, country, state, city, limit)
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail=str(e))
    
@app.get("/api/get-object-count")
async def get_object_count(query):
    try:
     return food_generator.get_object_count(query)
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)