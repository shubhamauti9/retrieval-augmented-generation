from pathlib import Path
from typing import Optional

from src.loaders.base_loader import BaseLoader
from src.utils.document import Document

"""
TextLoader - Load plain text files
The simplest loader - reads a text file and returns it as a Document
"""
"""
Load a plain text file as a Document
Attributes:
    file_path: Path to the text file
    encoding: Character encoding (default: utf-8)
Example:
    >>> loader = TextLoader("example.txt")
    >>> docs = loader.load()
    >>> print(docs[0].page_content[:50])
    This is the content of the text file...
"""
class TextLoader(BaseLoader):
    
    """
    Initialize the TextLoader
    Args:
        file_path: Path to the text file to load
        encoding: Character encoding of the file
        metadata: Optional additional metadata to add to the document
    """
    def __init__(
        self, 
        file_path: str, 
        encoding: str = "utf-8",
        metadata: Optional[dict] = None
    ):
        self.file_path = Path(file_path)
        self.encoding = encoding
        self.extra_metadata = metadata or {}
    
    """
    Load the text file as a Document
    Returns:
        A list containing a single Document with the file contents
    Raises:
        FileNotFoundError: If the file doesn't exist
    """
    def load(self) -> list[Document]:
        if not self.file_path.exists():
            raise FileNotFoundError(f"File not found: {self.file_path}")
        
        with open(self.file_path, "r", encoding=self.encoding) as f:
            content = f.read()
        
        metadata = {
            "source": str(self.file_path),
            "file_name": self.file_path.name,
            **self.extra_metadata
        }
        
        return [Document(page_content=content, metadata=metadata)]
