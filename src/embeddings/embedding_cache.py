import hashlib
import json
import os
from pathlib import Path
from typing import Optional

import numpy as np
from numpy.typing import NDArray

"""
EmbeddingCache - Cache embeddings to avoid redundant computation
Generating embeddings can be slow, so caching is crucial for performance
This cache stores text->embedding mappings in memory and optionally on disk
"""
"""
A simple cache for storing text embeddings
The cache uses a hash of the text as the key and stores the
embedding as the value. Can persist to disk for reuse between sessions
Attributes:
    cache_dir: Directory for persistent cache storage (optional)
    cache: In-memory cache dictionary
Example:
    >>> cache = EmbeddingCache()
    >>> cache.set("hello", np.array([0.1, 0.2, 0.3]))
    >>> embedding = cache.get("hello")
    >>> print(embedding)
    [0.1 0.2 0.3]
"""
class EmbeddingCache:
    
    """
    Initialize the embedding cache
    Args:
        cache_dir: Optional directory path for persistent storage
                    If None, cache is in-memory only
    """
    def __init__(
        self,
        cache_dir: Optional[str] = None
    ):
        self.cache_dir = Path(cache_dir) if cache_dir else None
        self._cache: dict[str, NDArray[np.float32]] = {}
        
        if self.cache_dir:
            self.cache_dir.mkdir(parents=True, exist_ok=True)
            self._load_from_disk()
    
    """
    Generate a hash key for a text string
    """
    def _hash_text(self, text: str) -> str:
        return hashlib.sha256(text.encode()).hexdigest()[:16]
    
    """
    Get an embedding from the cache
    Args:
        text: The original text
    Returns:
        The cached embedding, or None if not found
    """
    def get(self, text: str) -> Optional[NDArray[np.float32]]:
        key = self._hash_text(text)
        return self._cache.get(key)
    
    """
    Store an embedding in the cache
    Args:
        text: The original text
        embedding: The embedding to cache
    """
    def set(
        self,
        text: str,
        embedding: NDArray[np.float32]
    ) -> None:
        key = self._hash_text(text)
        self._cache[key] = embedding
    
    """
    Check if a text is in the cache
    Args:
        text: The original text
    Returns:
        True if the text is in the cache, False otherwise
    """
    def has(self, text: str) -> bool:
        key = self._hash_text(text)
        return key in self._cache
    
    """
    Clear all cached embeddings
    """
    def clear(self) -> None:
        self._cache.clear()
    
    """
    Save the cache to disk
    """
    def save_to_disk(self) -> None:
        if not self.cache_dir:
            raise ValueError("No cache directory specified")
        
        cache_file = self.cache_dir / "embeddings.npz"
        np.savez(cache_file, **{k: v for k, v in self._cache.items()})
    
    """
    Load the cache from disk
    """
    def _load_from_disk(self) -> None:
        if not self.cache_dir:
            return
        
        cache_file = self.cache_dir / "embeddings.npz"
        if cache_file.exists():
            data = np.load(cache_file)
            self._cache = {k: data[k] for k in data.files}
    
    """
    Return the number of cached embeddings
    """
    def __len__(self) -> int:
        return len(self._cache)
    
    """
    Check if a text is in the cache
    """
    def __contains__(self, text: str) -> bool:
        return self.has(text)
