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


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)



# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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
        urls = await get_duckduckgo_image_urls(query, limit)
        return {"query": query, "image_urls": urls}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)