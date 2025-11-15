from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import requests
from bs4 import BeautifulSoup
from typing import List

from app.middleware.nutrition_analysis_middleware import process_nutrion_fact_from_image, process_nutrition_facts
from app.middleware.image_generation_middleware import process_image, process_image_generation


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)



@app.get("/api/images-generation")
async def get_images(query: str, limit: int = 10):
    return await process_image_generation(query=query,limit=limit)

@app.get("/api/images")
async def get_images(query: str, limit: int = 10):
    return await process_image(query=query,limit=limit)

@app.get("/api/nutrition-facts-from-image")
async def get_nutrition_facts_from_image(image_path: str):
    return await process_nutrion_fact_from_image(image_path=image_path)
 
@app.get("/api/nutrition-facts")   
async def get_nutrition_facts(food_name: str):
    return await process_nutrition_facts(food_name=food_name)
    
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)