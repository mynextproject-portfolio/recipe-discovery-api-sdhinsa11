from fastapi import FastAPI, HTTPException

app = FastAPI()

recipes = [
    {
        "id": 1,
        "name": "Spaghetti Bolognese",
        "ingredients": ["spaghetti", "ground beef", "tomato sauce", "onion", "garlic"],
        "instructions": "Cook pasta. Brown beef with onion and garlic. Add tomato sauce. Combine."
    },
    {
        "id": 2,
        "name": "Chicken Curry",
        "ingredients": ["chicken", "curry powder", "coconut milk", "onion", "garlic"],
        "instructions": "Cook chicken. Add onion and garlic. Stir in curry powder and coconut milk. Simmer."
    },
    {
        "id": 3,
        "name": "Pancakes",
        "ingredients": ["flour", "milk", "egg", "sugar", "butter"],
        "instructions": "Mix ingredients into batter. Cook on skillet until golden brown."
    }
]

# First recipe endpoint
@app.get("/recipes")
def get_recipes():
    return recipes

# Second recipe endpoint
@app.get("/recipes/{recipe_id}")
def get_recipe(recipe_id: int):
    for recipe in recipes:
        if recipe["id"] == recipe_id:
            return recipe
    raise HTTPException(status_code=404, detail="Recipe not found")


# Health check endpoint 
@app.get("/ping")
def ping():
    return "pong"

