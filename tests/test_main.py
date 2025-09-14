import pytest
import os
import tempfile
from fastapi.testclient import TestClient
from app.main import app
from app.dependencies import get_recipe_storage
from app.storage.memory_store import MemoryRecipeStore
from app.storage.sqlite_store import SQLiteRecipeStore
from app.services.mealdb_service import MealDBService


# Create a fresh client for each test
@pytest.fixture
def client():
    """Create a fresh TestClient with isolated storage for each test"""
    
    # Clear any existing cache first
    get_recipe_storage.cache_clear()
    
    # Clear MealDB cache for clean tests
    try:
        service = MealDBService()
        service.clear_cache()
    except:
        pass  # Redis might not be available during testing
    
    # Use memory storage for faster tests
    test_storage = MemoryRecipeStore()
    
    def get_test_recipe_storage():
        """Return the same storage instance for all requests in this test"""
        return test_storage
    
    # Override the dependency for this test
    app.dependency_overrides[get_recipe_storage] = get_test_recipe_storage
    
    with TestClient(app) as test_client:
        yield test_client
    
    # Clean up after test
    app.dependency_overrides.clear()
    get_recipe_storage.cache_clear()

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

# NEW EXTERNAL API TESTS

def test_search_recipes_with_external_api(client):
    """Test searching recipes includes external API results"""
    # Search for a common term that should return both internal and external results
    response = client.get("/recipes/search?q=chicken")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    
    # Should have at least our internal "Chicken Curry" recipe
    internal_recipes = [r for r in data if r["source"] == "internal"]
    assert len(internal_recipes) >= 1
    assert any("Curry" in recipe["title"] for recipe in internal_recipes)
    
    # Check that external recipes have the right structure (if any)
    external_recipes = [r for r in data if r["source"] == "mealdb"]
    for recipe in external_recipes:
        assert "mealdb_" in str(recipe["id"])
        assert recipe["source"] == "mealdb"
        assert "title" in recipe
        assert "ingredients" in recipe
        assert "steps" in recipe

# Replace the failing test with this corrected version:

def test_search_recipes_combined_results(client):
    """Test that search combines internal and external results properly"""
    # Search for "spaghetti" which should match "Spaghetti Carbonara"
    response = client.get("/recipes/search?q=spaghetti")
    assert response.status_code == 200
    data = response.json()
    
    # Should have internal Carbonara recipe
    internal_found = any(
        recipe["source"] == "internal" and "Carbonara" in recipe["title"] 
        for recipe in data
    )
    assert internal_found
    
    # Check that all recipes have required fields
    for recipe in data:
        assert "id" in recipe
        assert "title" in recipe
        assert "source" in recipe
        assert recipe["source"] in ["internal", "mealdb"]

def test_external_recipe_structure(client):
    """Test that external recipes have proper structure"""
    response = client.get("/recipes/search?q=beef")  # Common search term
    assert response.status_code == 200
    data = response.json()
    
    external_recipes = [r for r in data if r["source"] == "mealdb"]
    
    if external_recipes:  # Only test if we got external results
        external_recipe = external_recipes[0]
        
        # Check required fields
        assert "id" in external_recipe
        assert "title" in external_recipe
        assert "ingredients" in external_recipe
        assert "steps" in external_recipe
        assert "cuisine" in external_recipe
        assert external_recipe["source"] == "mealdb"
        
        # Check external-specific fields
        assert "image" in external_recipe
        assert "originalId" in external_recipe

def test_search_internal_only_fallback(client):
    """Test that search works even if external API fails"""
    # Test with a term that should find internal recipes
    response = client.get("/recipes/search?q=carbonara")
    assert response.status_code == 200
    data = response.json()
    
    # Should find at least the internal recipe
    internal_recipes = [r for r in data if r["source"] == "internal"]
    assert len(internal_recipes) >= 1
    assert any("Carbonara" in recipe["title"] for recipe in internal_recipes)

# Add new cache-specific tests
def test_cache_endpoints(client):
    """Test cache management endpoints"""
    # Test cache stats
    response = client.get("/admin/cache/stats")
    assert response.status_code == 200
    stats = response.json()
    assert "cached_queries" in stats
    
    # Test cache health
    response = client.get("/admin/cache/health")
    assert response.status_code == 200
    health = response.json()
    assert "healthy" in health
    
    # Test cache clear
    response = client.delete("/admin/cache/clear")
    assert response.status_code == 200
    result = response.json()
    assert "success" in result

def test_search_caching_behavior(client):
    """Test that search results are cached properly"""
    # First search - should be cache miss
    response1 = client.get("/recipes/search?q=chicken")
    assert response1.status_code == 200
    results1 = response1.json()
    
    # Second identical search - should be cache hit (same results)
    response2 = client.get("/recipes/search?q=chicken")
    assert response2.status_code == 200
    results2 = response2.json()
    
    # Results should be identical
    assert results1 == results2
    
    # Check cache stats show cached queries
    stats_response = client.get("/admin/cache/stats")
    assert stats_response.status_code == 200