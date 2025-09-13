import sqlite3
import json
from typing import List, Dict, Optional
from pathlib import Path
from app.storage.abstract import RecipeStorageInterface

class SQLiteRecipeStore(RecipeStorageInterface):
    def __init__(self, db_path: str = "recipes.db"):
        self.db_path = db_path
        self._init_database()
        self._seed_initial_data()
    
    def _init_database(self):
        """Initialize the database with the recipes table"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS recipes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    ingredients TEXT NOT NULL,
                    steps TEXT NOT NULL,
                    prep_time TEXT NOT NULL,
                    cook_time TEXT NOT NULL,
                    difficulty TEXT NOT NULL,
                    cuisine TEXT NOT NULL
                )
            """)
            conn.commit()
    
    def _seed_initial_data(self):
        """Seed the database with initial sample data if empty"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM recipes")
            count = cursor.fetchone()[0]
            
            if count == 0:
                # Insert the same initial data as MemoryRecipeStore
                initial_recipes = [
                    (
                        1, "Spaghetti Carbonara",
                        json.dumps(["pasta", "eggs", "bacon", "cheese"]),
                        json.dumps(["Cook pasta", "Mix eggs", "Combine all"]),
                        "10 minutes", "15 minutes", "Medium", "Italian"
                    ),
                    (
                        2, "Chicken Curry",
                        json.dumps(["chicken", "curry powder", "coconut milk", "onion", "garlic"]),
                        json.dumps(["Cook chicken", "Add onion and garlic", "Stir in curry powder and coconut milk", "Simmer"]),
                        "15 minutes", "30 minutes", "Medium", "Indian"
                    )
                ]
                
                cursor.executemany("""
                    INSERT INTO recipes (id, title, ingredients, steps, prep_time, cook_time, difficulty, cuisine)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, initial_recipes)
                
                # Set the auto-increment counter to start from 3
                cursor.execute("UPDATE sqlite_sequence SET seq = 2 WHERE name = 'recipes'")
                conn.commit()
    
    def _row_to_dict(self, row) -> Dict:
        """Convert a database row to a recipe dictionary"""
        return {
            "id": row[0],
            "title": row[1],
            "ingredients": json.loads(row[2]),
            "steps": json.loads(row[3]),
            "prepTime": row[4],
            "cookTime": row[5],
            "difficulty": row[6],
            "cuisine": row[7]
        }
    
    def get_all(self) -> List[Dict]:
        """Get all recipes"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM recipes ORDER BY id")
            rows = cursor.fetchall()
            return [self._row_to_dict(row) for row in rows]
    
    def get_by_id(self, recipe_id: int) -> Optional[Dict]:
        """Get a recipe by ID"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM recipes WHERE id = ?", (recipe_id,))
            row = cursor.fetchone()
            return self._row_to_dict(row) if row else None
    
    def create(self, recipe_data: Dict) -> Dict:
        """Create a new recipe"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO recipes (title, ingredients, steps, prep_time, cook_time, difficulty, cuisine)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                recipe_data["title"],
                json.dumps(recipe_data["ingredients"]),
                json.dumps(recipe_data["steps"]),
                recipe_data["prepTime"],
                recipe_data["cookTime"],
                recipe_data["difficulty"],
                recipe_data["cuisine"]
            ))
            
            recipe_id = cursor.lastrowid
            conn.commit()
            
            # Return the created recipe with the new ID
            recipe_data["id"] = recipe_id
            return recipe_data
    
    def update(self, recipe_id: int, recipe_data: Dict) -> Optional[Dict]:
        """Update an existing recipe"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # First check if the recipe exists
            cursor.execute("SELECT COUNT(*) FROM recipes WHERE id = ?", (recipe_id,))
            if cursor.fetchone()[0] == 0:
                return None
            
            # Update the recipe
            cursor.execute("""
                UPDATE recipes 
                SET title = ?, ingredients = ?, steps = ?, prep_time = ?, cook_time = ?, difficulty = ?, cuisine = ?
                WHERE id = ?
            """, (
                recipe_data["title"],
                json.dumps(recipe_data["ingredients"]),
                json.dumps(recipe_data["steps"]),
                recipe_data["prepTime"],
                recipe_data["cookTime"],
                recipe_data["difficulty"],
                recipe_data["cuisine"],
                recipe_id
            ))
            conn.commit()
            
            # Return the updated recipe with the ID
            recipe_data["id"] = recipe_id
            return recipe_data
    
    def delete(self, recipe_id: int) -> bool:
        """Delete a recipe"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM recipes WHERE id = ?", (recipe_id,))
            rows_affected = cursor.rowcount
            conn.commit()
            return rows_affected > 0
    
    def search(self, query: str) -> List[Dict]:
        """Search recipes by title"""
        if not query:
            return []
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT * FROM recipes WHERE title LIKE ? ORDER BY id",
                (f"%{query}%",)
            )
            rows = cursor.fetchall()
            return [self._row_to_dict(row) for row in rows]
    
    def clear(self):
        """Clear all data (useful for testing)"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM recipes")
            cursor.execute("DELETE FROM sqlite_sequence WHERE name = 'recipes'")
            conn.commit()