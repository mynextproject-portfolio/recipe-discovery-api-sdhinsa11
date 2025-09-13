from pydantic import BaseModel
from typing import List

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