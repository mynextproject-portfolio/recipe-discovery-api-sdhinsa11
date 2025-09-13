from typing import List, Dict, Optional

class RecipeStore:
    def __init__(self):
        self.recipes: List[Dict] = [
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
        self.next_id = 3
    
    def get_all(self) -> List[Dict]:
        return self.recipes
    
    def get_by_id(self, recipe_id: int) -> Optional[Dict]:
        return next((r for r in self.recipes if r["id"] == recipe_id), None)
    
    def create(self, recipe_data: Dict) -> Dict:
        recipe_data["id"] = self.next_id
        self.recipes.append(recipe_data)
        self.next_id += 1
        return recipe_data
    
    def update(self, recipe_id: int, recipe_data: Dict) -> Optional[Dict]:
        for i, recipe in enumerate(self.recipes):
            if recipe["id"] == recipe_id:
                recipe_data["id"] = recipe_id
                self.recipes[i] = recipe_data
                return recipe_data
        return None
    
    def delete(self, recipe_id: int) -> bool:
        for i, recipe in enumerate(self.recipes):
            if recipe["id"] == recipe_id:
                self.recipes.pop(i)
                return True
        return False
    
    def search(self, query: str) -> List[Dict]:
        if not query:
            return []
        return [r for r in self.recipes if query.lower() in r["title"].lower()]

# Global instance
recipe_store = RecipeStore()