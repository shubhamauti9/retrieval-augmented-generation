import hashlib
import json
from typing import Optional

import numpy as np
from numpy.typing import NDArray

from src.cache.redis_manager import RedisManager, get_redis

PREFIX = "emb"
DEFAULT_TTL = 86400 * 7  #7days

"""
Redis-based Embedding Cache
Efficiently caches embeddings to avoid re-computation
"""
"""
Cache embeddings in Redis to avoid recomputing
Features:
    - Hash-based keys for text lookup
    - TTL support for cache expiration
    - Batch operations
Example:
    >>> cache = RedisEmbeddingCache()
    >>> cache.set("Hello world", embedding_vector)
    >>> cached = cache.get("Hello world")
"""
class RedisEmbeddingCache:
    
    """
    Initialize the embedding cache
    Args:
        redis_manager: Redis manager instance
        model_name: Embedding model name (for key namespacing)
        ttl: Cache TTL in seconds
    """
    def __init__(
        self,
        redis_manager: Optional[RedisManager] = None,
        model_name: str = "default",
        ttl: int = DEFAULT_TTL
    ):
        self.redis = redis_manager or get_redis()
        self.model_name = model_name
        self.ttl = ttl
    
    """
    Create a cache key from text
    """
    def _make_key(self, text: str) -> str:
        text_hash = hashlib.sha256(text.encode()).hexdigest()[:16]
        return f"{self.PREFIX}:{self.model_name}:{text_hash}"
    
    """
    Get cached embedding for text
    Args:
        text: Input text
    Returns:
        Cached embedding or None
    """
    def get(self, text: str) -> Optional[NDArray[np.float32]]:
        key = self._make_key(text)
        data = self.redis.get(key)
        
        if data is None:
            return None
        
        """
        Convert list back to numpy array
        """
        return np.array(data, dtype=np.float32)
    
    """
    Cache an embedding
    Args:
        text: Input text
        embedding: Embedding vector
        ttl: Optional custom TTL
    Returns:
        True if successful
    """
    def set(
        self, 
        text: str, 
        embedding: NDArray[np.float32],
        ttl: Optional[int] = None
    ) -> bool:
        key = self._make_key(text)
        """
        Convert numpy array to list for JSON serialization
        """
        return self.redis.set(
            key, 
            embedding.tolist(),
            ttl=ttl or self.ttl
        )
    
    """
    Get cached embeddings for multiple texts
    Args:
        texts: List of texts
    Returns:
        Dict mapping text to embedding (or None if not cached)
    """
    def get_batch(
        self, 
        texts: list[str]
    ) -> dict[str, Optional[NDArray[np.float32]]]:
        result = {}
        for text in texts:
            result[text] = self.get(text)
        return result
    
    """
    Cache multiple embeddings
    Args:
        texts: List of texts
        embeddings: Corresponding embeddings
    Returns:
        Number of embeddings cached
    """
    def set_batch(
        self, 
        texts: list[str], 
        embeddings: list[NDArray[np.float32]]
    ) -> int:
        count = 0
        for text, emb in zip(texts, embeddings):
            if self.set(text, emb):
                count += 1
        return count
    
    """
    Invalidate a cached embedding
    """
    def invalidate(self, text: str) -> bool:
        key = self._make_key(text)
        return self.redis.delete(key)
    
    """
    Clear all cached embeddings
    Returns:
        Number of keys deleted
    """
    def clear_all(self) -> int:
        return self.redis.flush_prefix(f"{self.PREFIX}:{self.model_name}")
    
    """
    Get cache statistics
    Returns:
        Dict with cache statistics
    """
    def stats(self) -> dict:
        pattern = f"{self.PREFIX}:{self.model_name}:*"
        keys = self.redis.keys(pattern)
        return {
            "model": self.model_name,
            "cached_embeddings": len(keys),
            "ttl_seconds": self.ttl
        }
