from abc import ABC, abstractmethod
from typing import Optional

from src.utils.document import Document

"""
BaseTextSplitter - Abstract base class for text splitters
Text splitters break large documents into smaller chunks that:
1. Fit within embedding model context windows
2. Contain semantically coherent information
3. Allow for precise retrieval
"""
"""
Abstract base class for text splitters
Text splitters divide text into smaller chunks while trying to maintain semantic coherence
Different strategies work better for different types of content
Attributes:
    chunk_size: Maximum size of each chunk
    chunk_overlap: Number of characters to overlap between chunks
"""
class BaseTextSplitter(ABC):
    
    """
    Initialize the text splitter
    Args:
        chunk_size: Target size for each chunk (in characters)
        chunk_overlap: Number of characters to overlap between
                        adjacent chunks for context continuity
    """
    def __init__(
        self,
        chunk_size: int = 1000,
        chunk_overlap: int = 200
    ):
        if chunk_overlap >= chunk_size:
            raise ValueError("chunk_overlap must be less than chunk_size")
        
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
    
    """
    Split text into chunks
    Args:
        text: The text to split
    Returns:
        A list of text chunks
    """
    @abstractmethod
    def split_text(self, text: str) -> list[str]:
        pass
    
    """
    Split a list of documents into smaller documents
    Each chunk becomes a new Document with the original metadata
    plus chunk index information
    Args:
        documents: List of Documents to split
    Returns:
        A list of smaller Document objects
    """
    def split_documents(self, documents: list[Document]) -> list[Document]:
        result = []
        
        for doc in documents:
            chunks = self.split_text(doc.page_content)
            
            for i, chunk in enumerate(chunks):
                new_metadata = {
                    **doc.metadata,
                    "chunk_index": i,
                    "chunk_count": len(chunks),
                }
                result.append(Document(page_content=chunk, metadata=new_metadata))
        
        return result
    
    """
    Merge small splits into chunks of appropriate size
    Args:
        splits: List of text pieces
        separator: String to use when joining pieces
    Returns:
        List of merged chunks
    """
    def _merge_splits(
        self, 
        splits: list[str], 
        separator: str = ""
    ) -> list[str]:
        chunks = []
        current_chunk: list[str] = []
        current_length = 0
        
        for split in splits:
            split_length = len(split)
            
            """
            If adding this split would exceed chunk_size
            """
            if current_length + split_length > self.chunk_size and current_chunk:
                """
                Save current chunk
                """
                chunks.append(separator.join(current_chunk))
                
                """
                Start new chunk with overlap
                """
                overlap_length = 0
                overlap_start = len(current_chunk)
                
                for j in range(len(current_chunk) - 1, -1, -1):
                    overlap_length += len(current_chunk[j])
                    if overlap_length >= self.chunk_overlap:
                        overlap_start = j
                        break
                
                current_chunk = current_chunk[overlap_start:]
                current_length = sum(len(s) for s in current_chunk)
            
            current_chunk.append(split)
            current_length += split_length
        
        """
        Don't forget the last chunk
        """
        if current_chunk:
            chunks.append(separator.join(current_chunk))
        
        return chunks
