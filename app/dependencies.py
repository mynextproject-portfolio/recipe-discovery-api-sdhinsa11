from functools import lru_cache
from app.storage.abstract import RecipeStorageInterface
from app.storage.memory_store import MemoryRecipeStore

@lru_cache()
def get_recipe_storage() -> RecipeStorageInterface:
    """Dependency that provides recipe storage instance (singleton)"""
    return MemoryRecipeStore()

# For easy database swapping later, just change the return type:
# return DatabaseRecipeStore()  # Future implementation