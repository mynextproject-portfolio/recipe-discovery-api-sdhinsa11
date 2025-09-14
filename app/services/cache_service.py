import os
try:
    import redis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False
    print("⚠️ Redis package not installed. Caching will be disabled.")

import json
import hashlib
from typing import List, Dict, Optional
from datetime import timedelta

class CacheService:
    """Redis-based caching service for external API results with graceful fallback"""
    
    def __init__(self, redis_url: str = None):
        # Use environment variable or default to localhost
        if redis_url is None:
            redis_url = os.getenv("REDIS_URL", "redis://localhost:6379")
        
        self.redis_url = redis_url
        self.redis_client = None
        self.default_ttl = timedelta(hours=24)
        self.enabled = REDIS_AVAILABLE
        
        if self.enabled:
            self._connect()
        else:
            print("⚠️ Cache service disabled - Redis package not available")
    
    def _connect(self):
        """Establish Redis connection"""
        if not REDIS_AVAILABLE:
            return
            
        try:
            self.redis_client = redis.from_url(self.redis_url, decode_responses=True)
            # Test the connection
            self.redis_client.ping()
            print(f"✅ Connected to Redis at {self.redis_url}")
        except Exception as e:
            print(f"❌ Failed to connect to Redis at {self.redis_url}: {e}")
            self.redis_client = None
            self.enabled = False
    
    def _is_connected(self) -> bool:
        """Check if Redis is connected"""
        if not self.enabled or not self.redis_client:
            return False
        try:
            self.redis_client.ping()
            return True
        except:
            print("❌ Redis connection lost, attempting to reconnect...")
            self._connect()
            return self.redis_client is not None
    
    def _generate_cache_key(self, query: str) -> str:
        """Generate a consistent cache key for MealDB search queries"""
        query_hash = hashlib.md5(query.lower().encode()).hexdigest()
        return f"mealdb:search:{query_hash}"
    
    def get_mealdb_results(self, query: str) -> Optional[List[Dict]]:
        """Get cached MealDB search results"""
        if not query or not self._is_connected():
            return None
        
        try:
            cache_key = self._generate_cache_key(query)
            cached_data = self.redis_client.get(cache_key)
            
            if cached_data:
                print(f"🎯 Cache HIT for query: {query}")
                return json.loads(cached_data)
            return None
            
        except Exception as e:
            print(f"❌ Cache get error: {e}")
            return None
    
    def set_mealdb_results(self, query: str, results: List[Dict]) -> bool:
        """Cache MealDB search results"""
        if not query or not self._is_connected():
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
            print(f"💾 Cached {len(results)} results for query: {query}")
            return True
            
        except Exception as e:
            print(f"❌ Cache set error: {e}")
            return False
    
    def clear_mealdb_cache(self) -> bool:
        """Clear all MealDB cache entries"""
        if not self._is_connected():
            return False
        
        try:
            keys = self.redis_client.keys("mealdb:search:*")
            if keys:
                self.redis_client.delete(*keys)
                print(f"🗑️ Cleared {len(keys)} cache entries")
            return True
        except Exception as e:
            print(f"❌ Cache clear error: {e}")
            return False
    
    def get_cache_stats(self) -> Dict:
        """Get cache statistics for monitoring"""
        if not REDIS_AVAILABLE:
            return {
                "redis_connected": False,
                "error": "Redis package not installed"
            }
        
        if not self._is_connected():
            return {
                "redis_connected": False,
                "error": f"Cannot connect to Redis at {self.redis_url}",
                "redis_url": self.redis_url
            }
        
        try:
            info = self.redis_client.info()
            keys = self.redis_client.keys("mealdb:search:*")
            
            return {
                "redis_connected": True,
                "redis_url": self.redis_url,
                "cached_queries": len(keys),
                "memory_used": info.get("used_memory_human", "Unknown"),
                "uptime_seconds": info.get("uptime_in_seconds", 0)
            }
        except Exception as e:
            return {
                "redis_connected": False,
                "error": str(e),
                "redis_url": self.redis_url
            }
    
    def health_check(self) -> bool:
        """Check if Redis is available"""
        return self._is_connected()