import json
from typing import Optional, Any
from contextlib import contextmanager

import redis
from redis import Redis

"""
Redis Connection Manager
Provides a centralized Redis connection for the application
Used for caching embeddings, query results, and rate limiting
"""
"""
Redis connection manager with connection pooling
Features:
    - Connection pooling for efficiency
    - Automatic reconnection
    - JSON serialization helpers
Usage:
    >>> redis_mgr = RedisManager()
    >>> redis_mgr.set("key", {"data": "value"})
    >>> data = redis_mgr.get("key")
"""
class RedisManager:
    
    """
    Initialize Redis connection manager
    Args:
        host: Redis server host
        port: Redis server port
        db: Redis database number
        password: Optional password
        decode_responses: Whether to decode bytes to strings
        max_connections: Max connections in pool
    """
    def __init__(
        self,
        host: str = "localhost",
        port: int = 6379,
        db: int = 0,
        password: Optional[str] = None,
        decode_responses: bool = True,
        max_connections: int = 10
    ):
        self.host = host
        self.port = port
        self.db = db
        self.password = password
        self.decode_responses = decode_responses
        
        """
        Create connection pool
        """
        self.pool = redis.ConnectionPool(
            host=host,
            port=port,
            db=db,
            password=password,
            decode_responses=decode_responses,
            max_connections=max_connections
        )
        
        self._client: Optional[Redis] = None
    
    """
    Get Redis client (lazy initialization)
    """
    @property
    def client(self) -> Redis:
        if self._client is None:
            self._client = Redis(connection_pool=self.pool)
        return self._client
    
    """
    Ping Redis to check connection
    """
    def ping(self) -> bool:
        try:
            return self.client.ping()
        except redis.ConnectionError:
            return False
    
    """
    Set a value in Redis with optional TTL
    Args:
        key: Cache key
        value: Value to store (will be JSON serialized)
        ttl: Time-to-live in seconds
        prefix: Optional key prefix
    Returns:
        True if successful
    """
    def set(
        self, 
        key: str, 
        value: Any, 
        ttl: Optional[int] = None,
        prefix: str = ""
    ) -> bool:
        full_key = f"{prefix}:{key}" if prefix else key
        
        """
        Serialize value to JSON
        """
        if isinstance(value, (dict, list)):
            value = json.dumps(value)
        elif not isinstance(value, str):
            value = str(value)
        
        if ttl:
            return self.client.setex(full_key, ttl, value)
        return self.client.set(full_key, value)
    
    """
    Get a value from Redis
    Args:
        key: Cache key
        prefix: Optional key prefix
    Returns:
        Stored value (JSON deserialized if applicable)
    """
    def get(
        self, 
        key: str, 
        prefix: str = ""
    ) -> Optional[Any]:
        full_key = f"{prefix}:{key}" if prefix else key
        value = self.client.get(full_key)
        
        if value is None:
            return None
        
        """
        Try to deserialize JSON
        """
        try:
            return json.loads(value)
        except (json.JSONDecodeError, TypeError):
            return value
    
    """
    Delete a key from Redis
    Args:
        key: Cache key
        prefix: Optional key prefix
    Returns:
        True if successful
    """
    def delete(self, key: str, prefix: str = "") -> bool:
        full_key = f"{prefix}:{key}" if prefix else key
        return bool(self.client.delete(full_key))
    
    """
    Check if key exists
    Args:
        key: Cache key
        prefix: Optional key prefix
    Returns:
        True if key exists
    """
    def exists(
        self, 
        key: str, 
        prefix: str = ""
    ) -> bool:
        full_key = f"{prefix}:{key}" if prefix else key
        return bool(self.client.exists(full_key))
    
    """
    Get keys matching pattern
    Args:
        pattern: Pattern to match
    Returns:
        List of keys matching pattern
    """
    def keys(
        self, 
        pattern: str = "*"
    ) -> list[str]:
        return self.client.keys(pattern)
    
    """
    Delete all keys with a given prefix
    Args:
        prefix: Prefix to match
    Returns:
        Number of keys deleted
    """
    def flush_prefix(
        self, 
        prefix: str
    ) -> int:
        pattern = f"{prefix}:*"
        keys = self.client.keys(pattern)
        if keys:
            return self.client.delete(*keys)
        return 0
    
    """
    Increment a counter
    Args:
        key: Cache key
        prefix: Optional key prefix
    Returns:
        New counter value
    """
    def incr(
        self, 
        key: str, 
        prefix: str = ""
    ) -> int:
        full_key = f"{prefix}:{key}" if prefix else key
        return self.client.incr(full_key)
    
    """
    Set TTL on an existing key
    Args:
        key: Cache key
        ttl: Time-to-live in seconds
        prefix: Optional key prefix
    Returns:
        True if successful
    """
    def expire(
        self, 
        key: str, 
        ttl: int, 
        prefix: str = ""
    ) -> bool:
        full_key = f"{prefix}:{key}" if prefix else key
        return self.client.expire(full_key, ttl)
    
    """
    Close the connection pool
    """
    def close(self):
        self.pool.disconnect()


"""
Global Redis manager instance (lazy initialized)
"""
_redis_manager: Optional[RedisManager] = None


"""
Get the global Redis manager instance
Args:
    host: Redis host
    port: Redis port
    db: Database number
    password: Optional password
Returns:
    RedisManager instance
"""
def get_redis(
    host: str = "localhost",
    port: int = 6379,
    db: int = 0,
    password: Optional[str] = None
) -> RedisManager:
    global _redis_manager
    
    if _redis_manager is None:
        _redis_manager = RedisManager(
            host=host,
            port=port,
            db=db,
            password=password
        )
    
    return _redis_manager
