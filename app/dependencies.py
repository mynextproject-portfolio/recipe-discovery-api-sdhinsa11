from functools import lru_cache
import os
from app.storage.abstract import RecipeStorageInterface
from app.storage.memory_store import MemoryRecipeStore
from app.storage.sqlite_store import SQLiteRecipeStore

@lru_cache()
def get_recipe_storage() -> RecipeStorageInterface:
    """Dependency that provides recipe storage instance (singleton)"""
    # Use SQLite for production, memory for testing
    if os.getenv("TESTING") == "true":
        return MemoryRecipeStore()
    else:
        return SQLiteRecipeStore("recipes.db")

# For easy storage swapping, you can also use environment variables:
# storage_type = os.getenv("STORAGE_TYPE", "sqlite")
# if storage_type == "memory":
#     return MemoryRecipeStore()
# else:
#     return SQLiteRecipeStore("recipes.db")