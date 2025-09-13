from typing import List, Optional
from app.models.recipe import Recipe, RecipeCreate
from app.storage.memory_store import recipe_store

class RecipeService:
    def __init__(self):
        self.store = recipe_store
    
    def get_all_recipes(self) -> List[dict]:
        return self.store.get_all()
    
    def get_recipe_by_id(self, recipe_id: int) -> Optional[dict]:
        return self.store.get_by_id(recipe_id)
    
    def create_recipe(self, recipe: RecipeCreate) -> dict:
        recipe_data = recipe.model_dump()
        return self.store.create(recipe_data)
    
    def update_recipe(self, recipe_id: int, recipe: RecipeCreate) -> Optional[dict]:
        recipe_data = recipe.model_dump()
        return self.store.update(recipe_id, recipe_data)
    
    def delete_recipe(self, recipe_id: int) -> bool:
        return self.store.delete(recipe_id)
    
    def search_recipes(self, query: str) -> List[dict]:
        return self.store.search(query)

# Global instance
recipe_service = RecipeService()