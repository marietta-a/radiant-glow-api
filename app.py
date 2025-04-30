from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import requests
from bs4 import BeautifulSoup
import urllib.parse
import re
from typing import List
from .app import food_generator

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_bing_image_urls(query: str, limit: int = 10) -> List[str]:
    """Alternative Bing image URL scraper that doesn't require the downloader package"""
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36"
    }
    
    encoded_query = urllib.parse.quote(query)
    url = f"https://www.bing.com/images/search?q={encoded_query}"
    
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        image_elements = soup.find_all('img', {'class': 'mimg'})
        
        urls = []
        for img in image_elements[:limit]:
            src = img.get('src')
            if src and src.startswith('http'):
                # Clean the URL (Bing sometimes appends special parameters)
                clean_url = re.sub(r'&.*$', '', src)
                urls.append(clean_url)
        
        return list(set(urls))[:limit]  # Remove duplicates
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Scraping failed: {str(e)}")

@app.get("/api/images")
async def get_images(query: str, limit: int = 10):
    try:
        urls = get_bing_image_urls(query, limit)
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

if __name__ == "__app__ ":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)