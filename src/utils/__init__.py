"""
Utils module - Core utilities for RAG.
"""

from src.utils.document import Document
from src.utils.similarity import cosine_similarity, euclidean_distance

__all__ = ["Document", "cosine_similarity", "euclidean_distance"]
