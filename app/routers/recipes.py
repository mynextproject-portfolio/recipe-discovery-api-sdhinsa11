from fastapi import APIRouter, HTTPException, status, Depends
from typing import List, Union
from app.models.recipe import Recipe, RecipeCreate
from app.storage.abstract import RecipeStorageInterface
from app.services.recipe_service import RecipeService, get_recipe_service
from app.dependencies import get_recipe_storage

router = APIRouter(prefix="/recipes", tags=["recipes"])

def get_service(storage: RecipeStorageInterface = Depends(get_recipe_storage)) -> RecipeService:
    return get_recipe_service(storage)

@router.get("/", response_model=List[Recipe])
def get_recipes(service: RecipeService = Depends(get_service)):
    return service.get_all_recipes()

@router.get("/search", response_model=List[Recipe])
def search_recipes(q: str = "", service: RecipeService = Depends(get_service)):
    """Search both internal recipes and TheMealDB API"""
    return service.search_recipes(q)

@router.get("/{recipe_id}", response_model=Recipe)
def get_recipe(recipe_id: Union[int, str], service: RecipeService = Depends(get_service)):
    # Handle external recipe IDs (they're strings with prefix)
    if isinstance(recipe_id, str) and recipe_id.startswith("mealdb_"):
        raise HTTPException(
            status_code=404, 
            detail="External recipes can only be accessed through search"
        )
    
    # Convert to int for internal recipes
    try:
        recipe_id = int(recipe_id)
    except ValueError:
        raise HTTPException(status_code=404, detail="Recipe not found")
    
    recipe = service.get_recipe_by_id(recipe_id)
    if not recipe:
        raise HTTPException(status_code=404, detail="Recipe not found")
    return recipe

@router.post("/", response_model=Recipe, status_code=status.HTTP_201_CREATED)
def create_recipe(recipe: RecipeCreate, service: RecipeService = Depends(get_service)):
    return service.create_recipe(recipe)

@router.put("/{recipe_id}", response_model=Recipe)
def update_recipe(recipe_id: int, recipe: RecipeCreate, service: RecipeService = Depends(get_service)):
    updated_recipe = service.update_recipe(recipe_id, recipe)
    if not updated_recipe:
        raise HTTPException(status_code=404, detail="Recipe not found")
    return updated_recipe

@router.delete("/{recipe_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_recipe(recipe_id: int, service: RecipeService = Depends(get_service)):
    if not service.delete_recipe(recipe_id):
        raise HTTPException(status_code=404, detail="Recipe not found")