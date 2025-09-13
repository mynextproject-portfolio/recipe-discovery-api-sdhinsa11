from fastapi import APIRouter, HTTPException, status
from typing import List
from app.models.recipe import Recipe, RecipeCreate
from app.services.recipe_service import recipe_service

router = APIRouter(prefix="/recipes", tags=["recipes"])

@router.get("/", response_model=List[Recipe])
def get_recipes():
    return recipe_service.get_all_recipes()

@router.get("/search", response_model=List[Recipe])
def search_recipes(q: str = ""):
    return recipe_service.search_recipes(q)

@router.get("/{recipe_id}", response_model=Recipe)
def get_recipe(recipe_id: int):
    recipe = recipe_service.get_recipe_by_id(recipe_id)
    if not recipe:
        raise HTTPException(status_code=404, detail="Recipe not found")
    return recipe

@router.post("/", response_model=Recipe, status_code=status.HTTP_201_CREATED)
def create_recipe(recipe: RecipeCreate):
    return recipe_service.create_recipe(recipe)

@router.put("/{recipe_id}", response_model=Recipe)
def update_recipe(recipe_id: int, recipe: RecipeCreate):
    updated_recipe = recipe_service.update_recipe(recipe_id, recipe)
    if not updated_recipe:
        raise HTTPException(status_code=404, detail="Recipe not found")
    return updated_recipe

@router.delete("/{recipe_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_recipe(recipe_id: int):
    if not recipe_service.delete_recipe(recipe_id):
        raise HTTPException(status_code=404, detail="Recipe not found")