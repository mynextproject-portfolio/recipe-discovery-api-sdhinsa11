import pytest
import os
import tempfile
from fastapi.testclient import TestClient
from app.main import app
from app.dependencies import get_recipe_storage
from app.storage.memory_store import MemoryRecipeStore
from app.storage.sqlite_store import SQLiteRecipeStore

# Create a fresh client for each test
@pytest.fixture
def client():
    """Create a fresh TestClient with isolated storage for each test"""
    
    # Clear any existing cache first
    get_recipe_storage.cache_clear()
    
    # Create a temporary SQLite database for each test to prove SQLite works
    # But you can also use MemoryRecipeStore() for faster tests
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as temp_db:
        test_storage = SQLiteRecipeStore(temp_db.name)
    
    def get_test_recipe_storage():
        """Return the same storage instance for all requests in this test"""
        return test_storage
    
    # Override the dependency for this test
    app.dependency_overrides[get_recipe_storage] = get_test_recipe_storage
    
    with TestClient(app) as test_client:
        yield test_client
    
    # Clean up after test
    app.dependency_overrides.clear()
    # Clear cache again to ensure fresh storage for next test
    get_recipe_storage.cache_clear()
    
    # Clean up the temporary database file
    try:
        os.unlink(temp_db.name)
    except:
        pass

def test_ping_endpoint(client):
    """Test the health check endpoint"""
    response = client.get("/ping")
    assert response.status_code == 200
    assert response.json() == "pong"

def test_get_all_recipes(client):
    """Test getting all recipes"""
    response = client.get("/recipes")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 2  # We have 2 sample recipes
    assert data[0]["title"] == "Spaghetti Carbonara"

def test_get_recipe_by_id(client):
    """Test getting a specific recipe by ID"""
    response = client.get("/recipes/1")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == 1
    assert data["title"] == "Spaghetti Carbonara"
    assert data["cuisine"] == "Italian"

def test_get_recipe_not_found(client):
    """Test getting a non-existent recipe"""
    response = client.get("/recipes/999")
    assert response.status_code == 404
    assert response.json()["detail"] == "Recipe not found"

def test_create_recipe(client):
    """Test creating a new recipe"""
    new_recipe = {
        "title": "Test Pancakes",
        "ingredients": ["flour", "milk", "egg", "sugar"],
        "steps": ["Mix ingredients", "Cook on skillet"],
        "prepTime": "5 minutes",
        "cookTime": "10 minutes",
        "difficulty": "Easy",
        "cuisine": "American"
    }
    
    response = client.post("/recipes", json=new_recipe)
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "Test Pancakes"
    assert "id" in data
    assert data["difficulty"] == "Easy"

def test_update_recipe(client):
    """Test updating an existing recipe"""
    updated_recipe = {
        "title": "Updated Carbonara",
        "ingredients": ["pasta", "eggs", "bacon", "parmesan", "pepper"],
        "steps": ["Cook pasta", "Mix eggs with cheese", "Combine all", "Add pepper"],
        "prepTime": "8 minutes",
        "cookTime": "12 minutes",
        "difficulty": "Easy",
        "cuisine": "Italian"
    }
    
    response = client.put("/recipes/1", json=updated_recipe)
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Updated Carbonara"
    assert data["id"] == 1
    assert data["prepTime"] == "8 minutes"

def test_update_recipe_not_found(client):
    """Test updating a non-existent recipe"""
    updated_recipe = {
        "title": "Does Not Exist",
        "ingredients": ["test"],
        "steps": ["test"],
        "prepTime": "1 min",
        "cookTime": "1 min", 
        "difficulty": "Easy",
        "cuisine": "Test"
    }
    
    response = client.put("/recipes/999", json=updated_recipe)
    assert response.status_code == 404

def test_delete_recipe(client):
    """Test deleting a recipe"""
    # First, verify recipe 2 exists
    response = client.get("/recipes/2")
    assert response.status_code == 200
    assert response.json()["id"] == 2
    
    # Delete recipe 2
    response = client.delete("/recipes/2")
    assert response.status_code == 204
    
    # Verify it's deleted
    response = client.get("/recipes/2")
    assert response.status_code == 404

def test_search_recipes(client):
    """Test searching recipes by title"""
    # Search for 'pasta' (should find Carbonara)
    response = client.get("/recipes/search?q=pasta")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    
    # Search case-insensitive
    response = client.get("/recipes/search?q=CARBONARA")
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 1
    assert any("Carbonara" in recipe["title"] for recipe in data)

def test_search_no_results(client):
    """Test searching with no matches"""
    response = client.get("/recipes/search?q=nonexistent")
    assert response.status_code == 200
    data = response.json()
    assert data == []

def test_search_empty_query(client):
    """Test searching with empty query"""
    response = client.get("/recipes/search?q=")
    assert response.status_code == 200
    data = response.json()
    assert data == []
    
    # Test with no query parameter
    response = client.get("/recipes/search")
    assert response.status_code == 200
    data = response.json()
    assert data == []

def test_happy_path_crud_cycle(client):
    """Test the complete CRUD + search cycle end-to-end"""
    
    # 1. Create a new recipe
    new_recipe = {
        "title": "Happy Path Pizza",
        "ingredients": ["dough", "sauce", "cheese", "pepperoni"],
        "steps": ["Roll dough", "Add sauce", "Add toppings", "Bake"],
        "prepTime": "20 minutes",
        "cookTime": "15 minutes",
        "difficulty": "Medium",
        "cuisine": "Italian"
    }
    
    create_response = client.post("/recipes", json=new_recipe)
    assert create_response.status_code == 201
    created_recipe = create_response.json()
    recipe_id = created_recipe["id"]
    
    # 2. Get the created recipe
    get_response = client.get(f"/recipes/{recipe_id}")
    assert get_response.status_code == 200
    retrieved_recipe = get_response.json()
    assert retrieved_recipe["title"] == "Happy Path Pizza"
    
    # 3. Search for the recipe
    search_response = client.get("/recipes/search?q=pizza")
    assert search_response.status_code == 200
    search_results = search_response.json()
    assert len(search_results) >= 1
    assert any(recipe["id"] == recipe_id for recipe in search_results)
    
    # 4. Update the recipe
    updated_recipe = {
        "title": "Updated Happy Path Pizza",
        "ingredients": ["dough", "sauce", "cheese", "pepperoni", "mushrooms"],
        "steps": ["Roll dough", "Add sauce", "Add toppings", "Add mushrooms", "Bake"],
        "prepTime": "25 minutes",
        "cookTime": "15 minutes",
        "difficulty": "Medium",
        "cuisine": "Italian"
    }
    
    update_response = client.put(f"/recipes/{recipe_id}", json=updated_recipe)
    assert update_response.status_code == 200
    updated_data = update_response.json()
    
    # 5. Verify the update
    final_get_response = client.get(f"/recipes/{recipe_id}")
    assert final_get_response.status_code == 200
    final_recipe = final_get_response.json()
    assert final_recipe["title"] == "Updated Happy Path Pizza"
    assert "mushrooms" in final_recipe["ingredients"]
    assert final_recipe["prepTime"] == "25 minutes"
    
    # 6. Search for the updated recipe
    final_search_response = client.get("/recipes/search?q=Updated")
    assert final_search_response.status_code == 200
    final_search_results = final_search_response.json()
    assert len(final_search_results) >= 1
    assert any(recipe["id"] == recipe_id for recipe in final_search_results)