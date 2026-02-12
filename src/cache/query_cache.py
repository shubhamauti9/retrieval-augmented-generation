import hashlib
import json
from typing import Optional, Any
from datetime import datetime

from src.cache.redis_manager import RedisManager, get_redis

PREFIX = "query"
PREFIX = "ratelimit"
DEFAULT_TTL = 3600  #1hour

"""
Redis-based Query Cache
Caches RAG query results to speed up repeated queries
"""
"""
Cache query results in Redis
Useful for:
    - Caching expensive LLM responses
    - Rate limiting identical queries
    - Analytics and logging
Example:
    >>> cache = RedisQueryCache()
    >>> cache.set("What is leave policy?", {"answer": "...", "sources": [...]})
    >>> result = cache.get("What is leave policy?")
"""
class RedisQueryCache:
    
    """
    Initialize the query cache
    Args:
        redis_manager: Redis manager instance
        collection: Collection name for namespacing
        ttl: Cache TTL in seconds
    """
    def __init__(
        self,
        redis_manager: Optional[RedisManager] = None,
        collection: str = "default",
        ttl: int = DEFAULT_TTL
    ):
        self.redis = redis_manager or get_redis()
        self.collection = collection
        self.ttl = ttl
    
    """
    Create a cache key from query
    Args:
        query: User query
        top_k: Number of results (affects cache key)
    Returns:
        Cache key
    """
    def _make_key(
        self, 
        query: str, 
        top_k: int = 5
    ) -> str:
        """
        Include collection and top_k in hash for specificity
        """
        data = f"{self.collection}:{query}:{top_k}"
        query_hash = hashlib.sha256(data.encode()).hexdigest()[:16]
        return f"{self.PREFIX}:{self.collection}:{query_hash}"
    
    """
    Get cached query result
    Args:
        query: User query
        top_k: Number of results (affects cache key)
    Returns:
        Cached result or None
    """
    def get(
        self, 
        query: str, 
        top_k: int = 5
    ) -> Optional[dict]:
        key = self._make_key(query, top_k)
        return self.redis.get(key)
    
    """
    Cache a query result
    Args:
        query: User query
        result: Query result to cache
        top_k: Number of results
        ttl: Optional custom TTL
    Returns:
        True if successful
    """
    def set(
        self, 
        query: str, 
        result: dict,
        top_k: int = 5,
        ttl: Optional[int] = None
    ) -> bool:
        key = self._make_key(query, top_k)
        
        # Add metadata
        cache_data = {
            **result,
            "_cached_at": datetime.now().isoformat(),
            "_collection": self.collection,
            "_top_k": top_k
        }
        
        return self.redis.set(key, cache_data, ttl=ttl or self.ttl)
    
    """
    Invalidate a cached query
    Args:
        query: User query
        top_k: Number of results (affects cache key)
    Returns:
        True if successful
    """
    def invalidate(self, query: str, top_k: int = 5) -> bool:
        key = self._make_key(query, top_k)
        return self.redis.delete(key)
    
    """
    Clear all cached queries for this collection
    """
    def clear_collection(self) -> int:
        return self.redis.flush_prefix(f"{self.PREFIX}:{self.collection}")
    
    """
    Clear all cached queries
    """
    def clear_all(self) -> int:
        return self.redis.flush_prefix(self.PREFIX)
    
    """
    Get cache statistics
    Returns:
        Dict with cache statistics
    """
    def stats(self) -> dict:
        pattern = f"{self.PREFIX}:{self.collection}:*"
        keys = self.redis.keys(pattern)
        return {
            "collection": self.collection,
            "cached_queries": len(keys),
            "ttl_seconds": self.ttl
        }

"""
Rate limiter using Redis
Implements sliding window rate limiting for API endpoints
Example:
    >>> limiter = RedisRateLimiter(max_requests=100, window_seconds=60)
    >>> if limiter.is_allowed("user_ip_123"):
    ...     process_request()
    ... else:
    ...     return "Rate limited"
"""
class RedisRateLimiter:
    
    """
    Initialize rate limiter
    Args:
        redis_manager: Redis manager instance
        max_requests: Max requests per window
        window_seconds: Window size in seconds
    """
    def __init__(
        self,
        redis_manager: Optional[RedisManager] = None,
        max_requests: int = 100,
        window_seconds: int = 60
    ):
        self.redis = redis_manager or get_redis()
        self.max_requests = max_requests
        self.window_seconds = window_seconds
    
    """
    Create rate limit key
    Args:
        identifier: Unique identifier (IP, user ID, API key)
    Returns:
        Rate limit key
    """
    def _make_key(self, identifier: str) -> str:
        return f"{self.PREFIX}:{identifier}"
    
    """
    Check if request is allowed
    Args:
        identifier: Unique identifier (IP, user ID, API key)
    Returns:
        True if request is allowed
    """
    def is_allowed(self, identifier: str) -> bool:
        key = self._make_key(identifier)
        current = self.redis.client.get(key)
        
        if current is None:
            """
            First request in window
            """
            self.redis.set(key, "1", ttl=self.window_seconds)
            return True
        
        count = int(current)
        if count >= self.max_requests:
            return False
        
        """
        Increment counter
        """
        self.redis.incr(key)
        return True
    
    """
    Get remaining requests in current window
    Args:
        identifier: Unique identifier (IP, user ID, API key)
    Returns:
        Remaining requests in current window
    """
    def get_remaining(self, identifier: str) -> int:
        key = self._make_key(identifier)
        current = self.redis.client.get(key)
        
        if current is None:
            return self.max_requests
        
        return max(0, self.max_requests - int(current))
    
    """
    Reset rate limit for identifier
    Args:
        identifier: Unique identifier (IP, user ID, API key)
    Returns:
        True if successful
    """
    def reset(self, identifier: str) -> bool:
        key = self._make_key(identifier)
        return self.redis.delete(key)
