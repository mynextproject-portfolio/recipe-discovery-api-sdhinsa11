import redis
import json
import hashlib
from typing import List, Dict, Optional
from datetime import timedelta

class CacheService:
    """Redis-based caching service for external API results"""
    
    def __init__(self, redis_url: str = "redis://localhost:6379"):
        self.redis_client = redis.from_url(redis_url, decode_responses=True)
        self.default_ttl = timedelta(hours=24)  # 24-hour TTL
    
    def _generate_cache_key(self, query: str) -> str:
        """Generate a consistent cache key for MealDB search queries"""
        # Create a hash of the query for consistent, safe keys
        query_hash = hashlib.md5(query.lower().encode()).hexdigest()
        return f"mealdb:search:{query_hash}"
    
    def get_mealdb_results(self, query: str) -> Optional[List[Dict]]:
        """Get cached MealDB search results"""
        if not query:
            return None
        
        try:
            cache_key = self._generate_cache_key(query)
            cached_data = self.redis_client.get(cache_key)
            
            if cached_data:
                return json.loads(cached_data)
            return None
            
        except Exception as e:
            # Log error but don't fail the search
            print(f"Cache get error: {e}")
            return None
    
    def set_mealdb_results(self, query: str, results: List[Dict]) -> bool:
        """Cache MealDB search results"""
        if not query:
            return False
        
        try:
            cache_key = self._generate_cache_key(query)
            serialized_data = json.dumps(results)
            
            # Set with 24-hour TTL
            self.redis_client.setex(
                cache_key,
                self.default_ttl,
                serialized_data
            )
            return True
            
        except Exception as e:
            # Log error but don't fail the search
            print(f"Cache set error: {e}")
            return False
    
    def clear_mealdb_cache(self) -> bool:
        """Clear all MealDB cache entries (useful for testing)"""
        try:
            # Find all mealdb cache keys
            keys = self.redis_client.keys("mealdb:search:*")
            if keys:
                self.redis_client.delete(*keys)
            return True
        except Exception as e:
            print(f"Cache clear error: {e}")
            return False
    
    def get_cache_stats(self) -> Dict:
        """Get cache statistics for monitoring"""
        try:
            info = self.redis_client.info()
            keys = self.redis_client.keys("mealdb:search:*")
            
            return {
                "redis_connected": True,
                "cached_queries": len(keys),
                "memory_used": info.get("used_memory_human", "Unknown"),
                "uptime": info.get("uptime_in_seconds", 0)
            }
        except Exception as e:
            return {
                "redis_connected": False,
                "error": str(e)
            }
    
    def health_check(self) -> bool:
        """Check if Redis is available"""
        try:
            self.redis_client.ping()
            return True
        except Exception:
            return False