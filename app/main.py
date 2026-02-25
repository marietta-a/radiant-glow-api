from fastapi import Depends, FastAPI, UploadFile, File, Request
from fastapi.middleware.cors import CORSMiddleware
from app.helper import parse_profile
from app.middleware.middleware import global_exception_handler
from app.middleware.nutrition_analysis_middleware import process_nutrion_fact_from_image, process_nutrition_facts
from app.middleware.nutrition_analysis_middleware_new import process_nutrion_fact_from_image_new, process_nutrition_facts_new
from app.middleware.image_generation_middleware import process_image, process_image_generation
from app.middleware.meal_plan_generation_middleware import process_meal_plan_generation
from app.models.mavita.mavita_payloads import BioReportRequest, RecipeRequest, UserProfile
from app.models.meal_plan_payload import MealPlanPayload
from app.models.category_item_payload import CategoryItemPayload
from app.middleware.recipe_generation_middleware import process_recipe
from app.middleware.category_item_nutri_fact_middleware import process_health_goal_category_items
from app.services.mavita.mavita_service import analyze_meal_image, generate_bio_report, generate_longevity_plate


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


app.add_exception_handler(Exception, global_exception_handler)

#region mavita endpoints
@app.post("/api/analyze-meal")
async def analyze_meal(
    file: UploadFile = File(...),
    profile: UserProfile = Depends(parse_profile)
):
    image_bytes = await file.read()
    return analyze_meal_image(image_bytes, file.content_type, profile)

@app.post("/api/generate-longevity-plate")
async def generate_longevity_plate(request: RecipeRequest):
    # If this fails, the global_exception_handler catches it automatically
    recipes = generate_longevity_plate(request.goal, request.cuisine)
    return recipes

@app.post("/api/generate-report")
async def get_bio_report(request: BioReportRequest):
    meals_dict = [meal.model_dump() for meal in request.meals]
    profile_dict = request.profile.model_dump()
    
    report = generate_bio_report(meals_dict, profile_dict)
    return {"report": report}
#endregion

#region glamorous API Endpoints


#endregion


#region Radiant Glow Diet API Endpoints

@app.get("/api/images-generation")
async def get_images_generation(query: str, limit: int = 2):
    return await process_image_generation(query=query,limit=limit)

@app.get("/api/images")
async def get_images(query: str, limit: int = 1):
    return await process_image(query=query,limit=limit)

# @app.get("/api/nutrition-facts-from-image")
# async def get_nutrition_facts_from_image(image_path: str):
#     return await process_nutrion_fact_from_image(image_path=image_path)

@app.post("/api/nutrition-facts-from-image")
async def retrieve_nutrition_facts_from_image(file: UploadFile = File(...)):
    return await process_nutrion_fact_from_image(file=file)

@app.post("/api/nutrition-facts-from-image-new")
async def retrieve_nutrition_facts_from_image(file: UploadFile = File(...)):
    return await process_nutrion_fact_from_image_new(file=file)
 
@app.get("/api/nutrition-facts")   
async def get_nutrition_facts(food_name: str):
    return await process_nutrition_facts(food_name=food_name)

@app.get("/api/nutrition-facts-new")   
async def get_nutrition_facts(food_name: str):
    return await process_nutrition_facts_new(food_name=food_name)


@app.post("/api/meal-plan")
async def generate_meal_plan(payload: MealPlanPayload):
    return await  process_meal_plan_generation(payload=payload)



#health goal category data
@app.post("/api/health-goal-category-data")
async def generate_health_goal_category_data(payload: CategoryItemPayload):
    return await  process_health_goal_category_items(payload=payload)
 
@app.get("/api/recipe")   
async def get_recipe(food_name: str):
    return await process_recipe(food_name=food_name)

#endregion


    
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)