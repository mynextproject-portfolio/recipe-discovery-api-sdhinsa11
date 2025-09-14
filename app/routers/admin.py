from fastapi import APIRouter, Depends
from app.services.mealdb_service import MealDBService

router = APIRouter(prefix="/admin", tags=["admin"])

@router.get("/cache/stats")
def get_cache_stats():
    """Get cache statistics"""
    service = MealDBService()
    return service.get_cache_stats()

@router.delete("/cache/clear")
def clear_cache():
    """Clear MealDB cache"""
    service = MealDBService()
    success = service.clear_cache()
    return {"success": success, "message": "Cache cleared" if success else "Cache clear failed"}

@router.get("/cache/health")
def cache_health():
    """Check cache health"""
    service = MealDBService()
    healthy = service.cache.health_check()
    return {"healthy": healthy, "service": "redis"}