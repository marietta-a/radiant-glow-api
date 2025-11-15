from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import requests
from bs4 import BeautifulSoup
from typing import List
from duckduckgo_search import DDGS
from config import logger

from nutrition_fact_generatory import analyze_nutrition_facts, analyze_nutrition_facts_from_image
from image_generatory import get_duckduckgo_image_urls
from http import HTTPStatus


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
    try:
        result = analyze_nutrition_facts_from_image(image_path)
        return {"image_path": image_path, "nutrition_facts": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
 
@app.get("/api/nutrition-facts")   
async def get_nutrition_facts(food_name: str):
    try:
        # Validate input
        if not food_name or not food_name.strip():
            raise HTTPException(
                status_code=400,
                detail="Food name parameter is required and cannot be empty"
            )
        
        
        # This now returns a dictionary or None
        result = analyze_nutrition_facts(food_name)

        # Check if the analysis was successful
        if result is None:
            raise HTTPException(
                status_code=422,
                detail=f"Could not process or find nutrition facts for '{food_name}'. The AI model could not return a valid analysis."
            )
        
        # Validate that we have at least basic structure
        if not isinstance(result, dict) or 'name' not in result:
            raise HTTPException(
                status_code=422,
                detail=f"Invalid analysis result format for '{food_name}'"
            )
        
        return {
            "food_name": food_name,
            "nutrition_facts": result,
            "status": "success"
        }

    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        logger.error(f"Unexpected error for food_name '{food_name}': {e}", exc_info=True)
        raise HTTPException(
            status_code=500, 
            detail=f"An internal server error occurred while processing '{food_name}'"
        )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)