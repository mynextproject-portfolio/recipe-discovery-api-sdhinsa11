import httpx
from typing import List, Dict, Optional
import asyncio

class MealDBService:
    """Service for fetching recipes from TheMealDB API"""
    
    BASE_URL = "https://www.themealdb.com/api/json/v1/1"
    
    @staticmethod
    async def search_meals(query: str) -> List[Dict]:
        """Search meals by name from TheMealDB API"""
        if not query:
            return []
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{MealDBService.BASE_URL}/search.php",
                    params={"s": query},
                    timeout=5.0
                )
                response.raise_for_status()
                data = response.json()
                
                if not data or not data.get("meals"):
                    return []
                
                # Convert MealDB format to our internal format
                recipes = []
                for meal in data["meals"]:
                    # Extract ingredients (MealDB has up to 20 ingredient fields)
                    ingredients = []
                    for i in range(1, 21):
                        ingredient = meal.get(f"strIngredient{i}")
                        measure = meal.get(f"strMeasure{i}")
                        if ingredient and ingredient.strip():
                            if measure and measure.strip():
                                ingredients.append(f"{measure.strip()} {ingredient.strip()}")
                            else:
                                ingredients.append(ingredient.strip())
                    
                    # Split instructions into steps
                    instructions = meal.get("strInstructions", "")
                    steps = [step.strip() for step in instructions.split('.') if step.strip()]
                    
                    recipe = {
                        "id": f"mealdb_{meal['idMeal']}",  # Prefix to avoid ID conflicts
                        "title": meal.get("strMeal", "Unknown"),
                        "ingredients": ingredients,
                        "steps": steps,
                        "prepTime": "Unknown",  # MealDB doesn't provide prep time
                        "cookTime": "Unknown",  # MealDB doesn't provide cook time
                        "difficulty": "Medium",  # Default difficulty
                        "cuisine": meal.get("strArea", "Unknown"),
                        "source": "mealdb",
                        "image": meal.get("strMealThumb"),  # Bonus: recipe image
                        "video": meal.get("strYoutube"),     # Bonus: recipe video
                        "originalId": meal.get("idMeal")     # Keep original MealDB ID
                    }
                    recipes.append(recipe)
                
                return recipes
                
        except Exception as e:
            # Log the error in production, but don't fail the search
            print(f"Error fetching from MealDB: {e}")
            return []
    
    @staticmethod
    def search_meals_sync(query: str) -> List[Dict]:
        """Synchronous wrapper for async search"""
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        
        return loop.run_until_complete(MealDBService.search_meals(query))