from dataclasses import dataclass, field
from typing import Any

"""
Document class - The fundamental data structure for RAG
A Document represents a piece of text with associated metadata
This is the basic unit that flows through the RAG pipeline
"""
"""
Represents a document with content and metadata
Attributes:
    page_content: The actual text content of the document
    metadata: A dictionary containing any additional information
                about the document (source, page number, etc.)
Example:
    >>> doc = Document(
    ...     page_content="Python is a programming language",
    ...     metadata={"source": "wiki.txt", "page": 1}
    ... )
    >>> print(doc.page_content)
    Python is a programming language
"""
@dataclass
class Document:
    
    page_content: str
    metadata: dict[str, Any] = field(default_factory=dict)
    
    """
    Validate the document after initialization
    """
    def __post_init__(self):
        if not isinstance(self.page_content, str):
            raise ValueError("page_content must be a string")
        if not isinstance(self.metadata, dict):
            raise ValueError("metadata must be a dictionary")
    
    """
    Return the length of the page content
    """
    def __len__(self) -> int:
        return len(self.page_content)
    
    """
    Return a string representation of the document
    """
    def __repr__(self) -> str:
        content_preview = (
            self.page_content[:50] + "..." 
            if len(self.page_content) > 50 
            else self.page_content
        )
        return f"Document(page_content='{content_preview}', metadata={self.metadata})"
