from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel
from typing import List, Optional

app = FastAPI()

class RecipeBase(BaseModel):
    title: str
    ingredients: List[str]
    steps: List[str]
    prepTime: str
    cookTime: str
    difficulty: str
    cuisine: str

class RecipeCreate(RecipeBase):
    pass

class Recipe(RecipeBase):
    id: int

# --- In-memory storage ---
recipes: List[dict] = [
    {
        "id": 1,
        "title": "Spaghetti Carbonara",
        "ingredients": ["pasta", "eggs", "bacon", "cheese"],
        "steps": ["Cook pasta", "Mix eggs", "Combine all"],
        "prepTime": "10 minutes",
        "cookTime": "15 minutes",
        "difficulty": "Medium",
        "cuisine": "Italian"
    },
    {
        "id": 2,
        "title": "Chicken Curry",
        "ingredients": ["chicken", "curry powder", "coconut milk", "onion", "garlic"],
        "steps": ["Cook chicken", "Add onion and garlic", "Stir in curry powder and coconut milk", "Simmer"],
        "prepTime": "15 minutes",
        "cookTime": "30 minutes",
        "difficulty": "Medium",
        "cuisine": "Indian"
    }


]
next_id = 3

# --- Endpoints ---

@app.get("/recipes", response_model=List[Recipe]) # Response model ensures the correct format of the 
def get_recipes():
    return recipes

@app.get("/recipes/search", response_model=List[Recipe]) # FastAPI will automatically convert it to HTTP 200 status code
def search_recipes(q: str=""):
    if not q:
        return []
    matching_recipes = []
    for recipe in recipes:
        if q.lower() in recipe["title"].lower():
            matching_recipes.append(recipe)
    return matching_recipes

# Second recipe endpoint
@app.get("/recipes/{recipe_id}",  response_model=Recipe)
def get_recipe(recipe_id: int):
    for recipe in recipes:
        if recipe["id"] == recipe_id:
            return recipe
    raise HTTPException(status_code=404, detail="Recipe not found")


@app.post("/recipes", response_model=Recipe, status_code=status.HTTP_201_CREATED)
def create_recipe(recipe: RecipeCreate):
    global next_id
    new_recipe = recipe.model_dump()
    new_recipe["id"] = next_id
    recipes.append(new_recipe)
    next_id += 1
    return new_recipe

@app.put("/recipes/{recipe_id}", response_model=Recipe)
def update_recipe(recipe_id: int, updated_recipe: RecipeCreate):
    for index, recipe in enumerate(recipes):
        if recipe["id"] == recipe_id:
            updated_data = updated_recipe.model_dump()
            updated_data["id"] = recipe_id
            recipes[index] = updated_data
            return updated_data
    raise HTTPException(status_code=404, detail="Recipe not found")

@app.delete("/recipes/{recipe_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_recipe(recipe_id: int):
    for index, recipe in enumerate(recipes):
        if recipe["id"] == recipe_id:
            recipes.pop(index)
            return
    raise HTTPException(status_code=404, detail="Recipe not found") 


# Health check endpoint 
@app.get("/ping")
def ping():
    return "pong"

