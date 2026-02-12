import numpy as np
from numpy.typing import NDArray
from typing import Union
from sentence_transformers import SentenceTransformer

from src.utils.document import Document

"""
EmbeddingModel - Wrapper for generating text embeddings
Embeddings are numerical representations of text that capture semantic meaning
Similar texts will have similar embeddings (close in vector space)
"""
"""
A wrapper around sentence-transformers for generating embeddings
This class provides a simple interface to convert text into dense
vector representations that capture semantic meaning
Attributes:
    model_name: The name of the sentence-transformers model to use
    model: The loaded sentence-transformers model
    dimension: The dimensionality of the embeddings
Example:
    >>> model = EmbeddingModel()
    >>> embedding = model.embed("Hello, world!")
    >>> print(embedding.shape)
    (384,)
"""
class EmbeddingModel:
    
    """
    Initialize the embedding model
    Args:
        model_name: The sentence-transformers model to use
                    Default is 'all-MiniLM-L6-v2' which is fast and lightweight
    """
    def __init__(
        self,
        model_name: str = "all-MiniLM-L6-v2"
    ):
        self.model_name = model_name
        self._model = None
        self._dimension = None
    
    """
    Lazy-load the model on first access
    """
    @property
    def model(self):
        if self._model is None:
            try:
                self._model = SentenceTransformer(self.model_name)
            except ImportError:
                raise ImportError(
                    "sentence-transformers is required. "
                    "Install with: pip install sentence-transformers"
                )
        return self._model
    
    """
    Get the embedding dimension
    """
    @property
    def dimension(self) -> int:
        if self._dimension is None:
            """
            Generate a test embedding to get dimension
            """
            test_embedding = self.embed("test")
            self._dimension = len(test_embedding)
        return self._dimension
    
    """
    Generate an embedding for a single text
    Args:
        text: The text to embed
    Returns:
        A 1D numpy array of floats representing the embedding
    """
    def embed(self, text: str) -> NDArray[np.float32]:
        embedding = self.model.encode(text, convert_to_numpy=True)
        return embedding.astype(np.float32)
    
    """
    Generate embeddings for multiple texts at once
    Args:
        texts: A list of texts to embed
    Returns:
        A 2D numpy array of shape (num_texts, embedding_dim)
    """
    def embed_batch(
        self,
        texts: list[str]
    ) -> NDArray[np.float32]:
        embeddings = self.model.encode(texts, convert_to_numpy=True)
        return embeddings.astype(np.float32)
    
    """
    Generate embeddings for a list of Document objects
    Args:
        documents: List of Document objects
    Returns:
        List of (document, embedding) tuples
    """
    def embed_documents(
        self, 
        documents: list["Document"]
    ) -> list[tuple["Document", NDArray[np.float32]]]:
        texts = [doc.page_content for doc in documents]
        embeddings = self.embed_batch(texts)
        
        return list(zip(documents, embeddings))
