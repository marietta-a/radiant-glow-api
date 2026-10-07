"""Endpoints for the Radiant Glow Diet app (see app/services/radiantglow)."""
from typing import Optional

from fastapi import APIRouter, File, HTTPException, Query, UploadFile

from app.models.radiantglow.payloads import (
    CategoryItemsPayload, DietHistoryPayload, EdiblePayload, MealItemsPayload,
    NutritionFromItemsPayload, RecipeEditPayload, RecipeStorePayload, SuggestedDietPayload,
)
from app.models.server_response import ServerResponse
from app.services.radiantglow import (
    category_service, image_analysis_service, insights_service, item_service,
    meal_items_service, recipe_service, recipe_store_service,
)
from app.services.radiantglow.common import MAX_NAME_LENGTH, clean_name

router = APIRouter(prefix="/api/radiantglow", tags=["radiantglow"])

MAX_IMAGE_BYTES = 10 * 1024 * 1024


async def _read_image(file: UploadFile) -> tuple[bytes, str]:
    if not (file.content_type or "").startswith("image/"):
        raise HTTPException(status_code=415, detail="file must be an image")
    data = await file.read(MAX_IMAGE_BYTES + 1)
    if not data:
        raise HTTPException(status_code=400, detail="file is empty")
    if len(data) > MAX_IMAGE_BYTES:
        raise HTTPException(status_code=413, detail="image must be 10MB or smaller")
    return data, file.content_type


def _ok(name: str, data) -> ServerResponse:
    return ServerResponse(name=name, data=data, status="success")


# region analysis
@router.post("/analyze-image")
async def analyze_image(file: UploadFile = File(...)):
    image, mime = await _read_image(file)
    return _ok(file.filename or "image", await image_analysis_service.analyze_image(image, mime))


@router.post("/meal-items")
async def meal_items(file: UploadFile = File(...)):
    image, mime = await _read_image(file)
    return _ok(file.filename or "image", await meal_items_service.get_meal_items(image, mime))


@router.post("/meal-items/count")
async def count_meal_items(payload: MealItemsPayload):
    return _ok("item-count", meal_items_service.count_meal_items(payload.items))


@router.post("/is-edible")
async def is_edible(payload: EdiblePayload):
    return _ok("is-edible", await meal_items_service.check_edible(payload.items))


@router.post("/nutrition-from-items")
async def nutrition_from_items(payload: NutritionFromItemsPayload):
    items = [i.model_dump(exclude_none=True) for i in payload.items]
    return _ok("nutrition", await meal_items_service.get_nutritional_data_from_item_count(items))
# endregion


# region recipes and items
@router.get("/recipe")
async def get_recipe(item: str = Query(..., max_length=MAX_NAME_LENGTH)):
    return _ok(item, await recipe_service.get_recipe(item))


@router.get("/dish-items")
async def dish_items(dish: str = Query(..., max_length=MAX_NAME_LENGTH)):
    return _ok(dish, await item_service.get_dish_items(dish))


@router.get("/search")
async def search(q: str = Query("", max_length=MAX_NAME_LENGTH)):
    return _ok(q, await item_service.search_items(q))


@router.get("/item-svg")
async def item_svg(item: str = Query(..., max_length=MAX_NAME_LENGTH)):
    svg = await item_service.generate_item_svg(item)
    if svg is None:
        raise HTTPException(status_code=422, detail=f"Could not draw '{item}'")
    return _ok(item, {"svg": svg})


@router.post("/category-items")
async def category_items(payload: CategoryItemsPayload):
    result = await category_service.get_category_items(
        payload.food_category, payload.type, payload.country, payload.state, payload.is_endorsed, payload.total,
    )
    return _ok(payload.food_category, result)
# endregion


# region insights
@router.post("/diet-history-insights")
async def diet_history_insights(payload: DietHistoryPayload):
    return _ok("insights", await insights_service.analyze_diet_history(payload.histories))


@router.post("/suggested-diet")
async def suggested_diet(payload: SuggestedDietPayload):
    result = await insights_service.get_suggested_diet(
        payload.health_goals, payload.country, payload.state, payload.time,
    )
    return _ok("suggested-diet", result)
# endregion


# region stored recipes (Supabase)
@router.get("/stored-recipe")
async def stored_recipe(name: str = Query(..., max_length=MAX_NAME_LENGTH), device_id: Optional[str] = None):
    result = await recipe_store_service.fetch_recipe(clean_name(name), device_id)
    if result is None:
        raise HTTPException(status_code=404, detail=f"No stored recipe for '{name}'")
    return _ok(name, result)


@router.get("/stored-recipe/search")
async def search_stored_recipes(q: str = Query(..., max_length=MAX_NAME_LENGTH)):
    return _ok(q, await recipe_store_service.search_recipe_names(clean_name(q, "q")))


@router.post("/stored-recipe")
async def cache_recipe(payload: RecipeStorePayload):
    stored = await recipe_store_service.cache_recipe(clean_name(payload.name), payload.recipe)
    return _ok(payload.name, {"stored": stored})


@router.put("/stored-recipe")
async def save_recipe_edit(payload: RecipeEditPayload):
    try:
        await recipe_store_service.save_recipe_edit(payload.device_id, clean_name(payload.name), payload.recipe)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Could not save the recipe: {e}")
    return _ok(payload.name, {"saved": True})
# endregion
