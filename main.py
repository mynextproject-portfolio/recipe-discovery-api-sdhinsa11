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

@app.get("/recipes", response_model=List[Recipe]) # make sure to return data in the correct format (List of the Recipes)
def get_recipes():
    return recipes

# Second recipe endpoint
@app.get("/recipes/{recipe_id}",  response_model=Recipe)
def get_recipe(recipe_id: int):
    for recipe in recipes:
        if recipe["id"] == recipe_id:
            return recipe
    raise HTTPException(status_code=404, detail="Recipe not found")

# To test you need to use curl and open another terminal and type the command:
    #  curl -X POST "http://localhost:8000/recipes" -H "Content-Type: application/json" -d '{"title":"New Recipe","ingredients":["ingredient1","ingredient2"],"steps":["step1","step2"],"prepTime":"10 minutes","cookTime":"20 minutes","difficulty":"Easy","cuisine":"American"}'
# Use post to create a new recipe
@app.post("/recipes", response_model=Recipe, status_code=status.HTTP_201_CREATED) # sets the status to 201 (which is created)
def create_recipe(recipe: RecipeCreate):
    global next_id
    new_recipe = recipe.dict()
    new_recipe["id"] = next_id
    recipes.append(new_recipe)
    next_id += 1
    return new_recipe

# To test you need to use curl and open another terminal and type the command:
    #  curl -X PUT "http://localhost:8000/recipes/1" -H "Content-Type: application/json" -d '{"title":"Updated Recipe","ingredients":["ingredient1","ingredient2"],"steps":["step1","step2"],"prepTime":"10 minutes","cookTime":"20 minutes","difficulty":"Easy","cuisine":"American"}'
# Use put to update a recipe
@app.put("/recipes/{recipe_id}", response_model=Recipe)
def update_recipe(recipe_id: int, updated_recipe: RecipeCreate):
    for index, recipe in enumerate(recipes):
        if recipe["id"] == recipe_id:
            updated_data = updated_recipe.dict()
            updated_data["id"] = recipe_id
            recipes[index] = updated_data
            return updated_data
    raise HTTPException(status_code=404, detail="Recipe not found")

# To test you need to use curl and open another terminal and type the command:
    #  curl -X DELETE "http://localhost:8000/recipes/1"
# Use delete to remove a recipe
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

