from abc import ABC, abstractmethod
from typing import Optional

from src.utils.document import Document

"""
BaseRetriever - Abstract base class for retrievers
Retrievers find and return the most relevant documents for a query
"""
"""
Abstract base class for retrievers
A retriever takes a query and returns relevant documents
Different retriever implementations use different strategies to find relevant content
"""
class BaseRetriever(ABC):
    
    """
    Retrieve relevant documents for a query
    Args:
        query: The search query
        k: Number of documents to retrieve
        filter: Optional metadata filter
    Returns:
        List of relevant Document objects
    """
    @abstractmethod
    def retrieve(
        self,
        query: str,
        k: int = 4,
        filter: Optional[dict] = None
    ) -> list[Document]:
        pass

    """
    Retrieve documents with relevance scores
    Default implementation returns documents with score 1.0
    Override this for implementations that have actual scores
    Args:
        query: The search query
        k: Number of documents to retrieve
        filter: Optional metadata filter
    Returns:
        List of (document, score) tuples
    """
    def retrieve_with_scores(
        self,
        query: str,
        k: int = 4,
        filter: Optional[dict] = None
    ) -> list[tuple[Document, float]]:
        docs = self.retrieve(query, k, filter)
        return [(doc, 1.0) for doc in docs]
