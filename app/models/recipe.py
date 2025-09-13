from pydantic import BaseModel
from typing import List, Optional, Union

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
    id: Union[int, str]  # Allow string IDs for external recipes
    source: str = "internal"
    image: Optional[str] = None
    video: Optional[str] = None
    originalId: Optional[str] = None