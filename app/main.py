from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import requests
from bs4 import BeautifulSoup
from typing import List
from duckduckgo_search import DDGS

from middleware.nutrition_analysis_middleware import process_nutrion_fact_from_image, process_nutrition_facts
from services.nutrition_fact_service import analyze_nutrition_facts, analyze_nutrition_facts_from_image
from image_generatory import get_duckduckgo_image_urls


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)




@app.get("/api/images")
async def get_images(query: str, limit: int = 10):
    try:
        urls = await get_duckduckgo_image_urls(query, limit)
        return {"query": query, "image_urls": urls}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    

@app.get("/api/nutrition-facts-from-image")
async def get_nutrition_facts_from_image(image_path: str):
    return await process_nutrion_fact_from_image(image_path=image_path)
 
@app.get("/api/nutrition-facts")   
async def get_nutrition_facts(food_name: str):
    return await process_nutrition_facts(food_name=food_name)
    
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)