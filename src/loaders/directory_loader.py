from pathlib import Path
from typing import Optional, Type

from src.loaders.base_loader import BaseLoader
from src.loaders.text_loader import TextLoader
from src.loaders.pdf_loader import PDFLoader
from src.utils.document import Document

"""
Mapping of file extensions to loader classes
"""
DEFAULT_LOADERS: dict[str, Type[BaseLoader]] = {
    ".txt": TextLoader,
    ".md": TextLoader,
    ".pdf": PDFLoader,
}

"""
DirectoryLoader - Load all documents from a directory
Automatically selects the appropriate loader based on file extension
"""
"""
Load all documents from a directory
Recursively scans a directory and loads all supported files
Attributes:
    directory: Path to the directory
    glob_pattern: Pattern to match files (default: all files)
    recursive: Whether to search subdirectories
Example:
    >>> loader = DirectoryLoader("./documents")
    >>> docs = loader.load()
    >>> print(f"Loaded {len(docs)} documents")
    Loaded 25 documents
"""
class DirectoryLoader(BaseLoader):
    
    """
    Initialize the DirectoryLoader
    Args:
        directory: Path to the directory to load from
        glob_pattern: Glob pattern for file matching
        recursive: Whether to search subdirectories
        loaders: Custom mapping of extensions to loader classes
        metadata: Additional metadata to add to all documents
    """
    def __init__(
        self,
        directory: str,
        glob_pattern: str = "*",
        recursive: bool = True,
        loaders: Optional[dict[str, Type[BaseLoader]]] = None,
        metadata: Optional[dict] = None
    ):
        self.directory = Path(directory)
        self.glob_pattern = glob_pattern
        self.recursive = recursive
        self.loaders = loaders or DEFAULT_LOADERS
        self.extra_metadata = metadata or {}
    
    """
    Load all documents from the directory
    Returns:
        A list of all loaded Documents
    Raises:
        FileNotFoundError: If the directory doesn't exist
    """
    def load(self) -> list[Document]:
        if not self.directory.exists():
            raise FileNotFoundError(f"Directory not found: {self.directory}")
        
        if not self.directory.is_dir():
            raise ValueError(f"Not a directory: {self.directory}")
        
        documents = []
        
        """
        Get all matching files
        """
        if self.recursive:
            files = self.directory.rglob(self.glob_pattern)
        else:
            files = self.directory.glob(self.glob_pattern)
        
        for file_path in files:
            if file_path.is_file():
                suffix = file_path.suffix.lower()
                
                if suffix in self.loaders:
                    loader_class = self.loaders[suffix]
                    loader = loader_class(str(file_path), metadata=self.extra_metadata)
                    documents.extend(loader.load())
        
        return documents
