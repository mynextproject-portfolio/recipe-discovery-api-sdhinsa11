from typing import List, Optional
from app.models.recipe import Recipe, RecipeCreate
from app.storage.abstract import RecipeStorageInterface

class RecipeService:
    def __init__(self, storage: RecipeStorageInterface):
        self.storage = storage
    
    def get_all_recipes(self) -> List[dict]:
        return self.storage.get_all()
    
    def get_recipe_by_id(self, recipe_id: int) -> Optional[dict]:
        return self.storage.get_by_id(recipe_id)
    
    def create_recipe(self, recipe: RecipeCreate) -> dict:
        recipe_data = recipe.model_dump()
        return self.storage.create(recipe_data)
    
    def update_recipe(self, recipe_id: int, recipe: RecipeCreate) -> Optional[dict]:
        recipe_data = recipe.model_dump()
        return self.storage.update(recipe_id, recipe_data)
    
    def delete_recipe(self, recipe_id: int) -> bool:
        return self.storage.delete(recipe_id)
    
    def search_recipes(self, query: str) -> List[dict]:
        return self.storage.search(query)

def get_recipe_service(storage: RecipeStorageInterface) -> RecipeService:
    """Factory function for recipe service"""
    return RecipeService(storage)