from abc import ABC, abstractmethod
from typing import List, Dict, Optional

class RecipeStorageInterface(ABC):
    """Abstract interface for recipe storage operations"""
    
    @abstractmethod
    def get_all(self) -> List[Dict]:
        pass
    
    @abstractmethod
    def get_by_id(self, recipe_id: int) -> Optional[Dict]:
        pass
    
    @abstractmethod
    def create(self, recipe_data: Dict) -> Dict:
        pass
    
    @abstractmethod
    def update(self, recipe_id: int, recipe_data: Dict) -> Optional[Dict]:
        pass
    
    @abstractmethod
    def delete(self, recipe_id: int) -> bool:
        pass
    
    @abstractmethod
    def search(self, query: str) -> List[Dict]:
        pass