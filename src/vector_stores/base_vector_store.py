from abc import ABC, abstractmethod
from typing import Optional

import numpy as np
from numpy.typing import NDArray

from src.utils.document import Document

"""
BaseVectorStore - Abstract base class for vector stores
Vector stores are databases optimized for storing and searching high-dimensional vectors (embeddings)
"""
"""
Abstract base class for vector stores
A vector store holds documents with their embeddings and provides similarity search functionality
"""
class BaseVectorStore(ABC):
    
    """
    Add documents with their embeddings to the store
    Args:
        documents: List of Document objects
        embeddings: Corresponding embeddings for each document
    """
    @abstractmethod
    def add_documents(
        self,
        documents: list[Document],
        embeddings: list[NDArray[np.float32]]
    ) -> None:
        pass
    
    """
    Find the k most similar documents to the query
    Args:
        query_embedding: The embedding to search for
        k: Number of results to return
        filter: Optional metadata filter
    Returns:
        List of (document, score) tuples, sorted by similarity
    """
    @abstractmethod
    def similarity_search(
        self,
        query_embedding: NDArray[np.float32],
        k: int = 4,
        filter: Optional[dict] = None
    ) -> list[tuple[Document, float]]:
        pass
    
    """
    Delete documents by their IDs
    Args:
        ids: List of document IDs to delete
    """
    @abstractmethod
    def delete(self, ids: list[str]) -> None:
        pass
    
    """
    Alias for similarity_search that returns scores
    Some implementations may override this for efficiency
    """
    def similarity_search_with_score(
        self,
        query_embedding: NDArray[np.float32],
        k: int = 4,
        filter: Optional[dict] = None
    ) -> list[tuple[Document, float]]:
        return self.similarity_search(query_embedding, k, filter)
