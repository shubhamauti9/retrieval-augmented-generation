import uuid
from typing import Optional

import numpy as np
from numpy.typing import NDArray

from src.vector_stores.base_vector_store import BaseVectorStore
from src.utils.document import Document
from src.utils.similarity import cosine_similarity

"""
InMemoryVectorStore - Simple in-memory vector storage
Perfect for learning and small datasets. Stores everything in RAM and uses brute-force similarity search
"""
"""
A simple in-memory vector store using brute-force search
This implementation stores all documents and embeddings in memory and performs exact nearest-neighbor search. It's perfect for:
    - Learning how vector stores work
    - Small to medium datasets (< 100k documents)
    - Prototyping and development
Attributes:
    documents: List of stored documents
    embeddings: Numpy array of embeddings
    ids: List of document IDs
Example:
    >>> store = InMemoryVectorStore()
    >>> store.add_documents([doc1, doc2], [emb1, emb2])
    >>> results = store.similarity_search(query_emb, k=5)
"""
class InMemoryVectorStore(BaseVectorStore):
    
    """
    Initialize an empty vector store
    """
    def __init__(self):
        self.documents: list[Document] = []
        self.embeddings: list[NDArray[np.float32]] = []
        self.ids: list[str] = []
    
    """
    Add documents with their embeddings to the store
    Args:
        documents: List of Document objects
        embeddings: Corresponding embeddings for each document
    Returns:
        List of generated document IDs
    Raises:
        ValueError: If documents and embeddings have different lengths
    """
    def add_documents(
        self,
        documents: list[Document],
        embeddings: list[NDArray[np.float32]]
    ) -> list[str]:
        if len(documents) != len(embeddings):
            raise ValueError(
                f"Number of documents ({len(documents)}) must match "
                f"number of embeddings ({len(embeddings)})"
            )
        
        new_ids = []
        for doc, emb in zip(documents, embeddings):
            doc_id = str(uuid.uuid4())
            self.documents.append(doc)
            self.embeddings.append(emb)
            self.ids.append(doc_id)
            new_ids.append(doc_id)
        
        return new_ids
    
    """
    Find the k most similar documents to the query
    Uses brute-force cosine similarity comparison against all stored embeddings
    Args:
        query_embedding: The embedding to search for
        k: Number of results to return
        filter: Optional metadata filter (key-value pairs to match)
    Returns:
        List of (document, score) tuples, sorted by descending similarity
    """
    def similarity_search(
        self,
        query_embedding: NDArray[np.float32],
        k: int = 4,
        filter: Optional[dict] = None
    ) -> list[tuple[Document, float]]:
        if not self.documents:
            return []
        
        """
        Calculate similarity to all documents
        """
        scores = []
        for i, emb in enumerate(self.embeddings):
            """
            Check filter if provided
            """
            if filter:
                doc_metadata = self.documents[i].metadata
                if not all(
                    key in doc_metadata and doc_metadata[key] == value
                    for key, value in filter.items()
                ):
                    continue
            
            score = cosine_similarity(query_embedding, emb)
            scores.append((i, score))
        
        """
        Sort by similarity (descending)
        """
        scores.sort(key=lambda x: x[1], reverse=True)
        
        """
        Return top k results
        """
        results = []
        for i, score in scores[:k]:
            results.append((self.documents[i], score))
        
        return results
    
    """
    Delete documents by their IDs
    Args:
        ids: List of document IDs to delete
    """
    def delete(self, ids: list[str]) -> None:
        ids_to_delete = set(ids)
        
        """
        Find indices to keep
        """
        new_documents = []
        new_embeddings = []
        new_ids = []
        
        for i, doc_id in enumerate(self.ids):
            if doc_id not in ids_to_delete:
                new_documents.append(self.documents[i])
                new_embeddings.append(self.embeddings[i])
                new_ids.append(doc_id)
        
        self.documents = new_documents
        self.embeddings = new_embeddings
        self.ids = new_ids
    
    """
    Return the number of documents in the store
    """
    def __len__(self) -> int:
        return len(self.documents)
    
    """
    Remove all documents from the store
    """
    def clear(self) -> None:
        self.documents = []
        self.embeddings = []
        self.ids = []
