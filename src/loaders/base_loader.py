from abc import ABC, abstractmethod
from typing import Iterator

from src.utils.document import Document

"""
BaseLoader - Abstract base class for document loaders
Loaders are responsible for reading data from various sources
and converting them into Document objects
Abstract base class for document loaders
All loaders should inherit from this class and implement
the load() method
"""
class BaseLoader(ABC):
    
    """
    Load documents from the source
    Returns:
        A list of Document objects
    """
    @abstractmethod
    def load(self) -> list[Document]:
        pass
    
    """
    Lazily load documents one at a time
    This is more memory-efficient for large datasets
    Default implementation just wraps load()
    Yields:
        Document objects one at a time
    """
    def lazy_load(self) -> Iterator[Document]:
        for doc in self.load():
            yield doc
