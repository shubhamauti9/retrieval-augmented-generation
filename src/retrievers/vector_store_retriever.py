from typing import Optional

from src.retrievers.base_retriever import BaseRetriever
from src.vector_stores.base_vector_store import BaseVectorStore
from src.embeddings.embedding_model import EmbeddingModel
from src.utils.document import Document

"""
VectorStoreRetriever - Retrieve using vector similarity
The standard retriever that uses embeddings and vector search
"""
"""
Retriever that uses vector similarity search
This is the standard RAG retriever:
    1. Embeds the query using the same model used for documents
    2. Searches the vector store for similar embeddings
    3. Returns the corresponding documents
Attributes:
    vector_store: The vector store to search
    embedding_model: Model for embedding queries
    k: Default number of results
Example:
    >>> retriever = VectorStoreRetriever(store, model)
    >>> docs = retriever.retrieve("What is machine learning?")
""" 
class VectorStoreRetriever(BaseRetriever):
    
    """
    Initialize the retriever
    Args:
        vector_store: The vector store to search
        embedding_model: Model for embedding queries
        k: Default number of documents to retrieve
    """
    def __init__(
        self,
        vector_store: BaseVectorStore,
        embedding_model: EmbeddingModel,
        k: int = 4
    ):
        self.vector_store = vector_store
        self.embedding_model = embedding_model
        self.k = k
    
    """
    Retrieve documents similar to the query
    Args:
        query: The search query
        k: Number of documents to retrieve (uses default if None)
        filter: Optional metadata filter
    Returns:
        List of relevant Document objects
    """
    def retrieve(
        self,
        query: str,
        k: Optional[int] = None,
        filter: Optional[dict] = None
    ) -> list[Document]:
        k = k or self.k
        
        """
        Embed the query
        """
        query_embedding = self.embedding_model.embed(query)
        
        """
        Search the vector store
        """
        results = self.vector_store.similarity_search(
            query_embedding, k=k, filter=filter
        )
        
        """
        Return just the documents
        """
        return [doc for doc, score in results]
    
    """
    Retrieve documents with their similarity scores
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
        k: Optional[int] = None,
        filter: Optional[dict] = None
    ) -> list[tuple[Document, float]]:
        k = k or self.k
        
        query_embedding = self.embedding_model.embed(query)
        
        return self.vector_store.similarity_search(
            query_embedding, k=k, filter=filter
        )
