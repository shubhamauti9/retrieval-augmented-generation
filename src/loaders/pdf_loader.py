from pathlib import Path
from typing import Optional
from pypdf import PdfReader

from src.loaders.base_loader import BaseLoader
from src.utils.document import Document

"""
PDFLoader - Load PDF documents
Extracts text content from PDF files page by page
"""
"""
Load a PDF file and extract text content
Each page becomes a separate Document with page number metadata
Attributes:
    file_path: Path to the PDF file
Example:
    >>> loader = PDFLoader("document.pdf")
    >>> docs = loader.load()
    >>> print(f"Loaded {len(docs)} pages")
    Loaded 10 pages
"""
class PDFLoader(BaseLoader):
    
    """
    Initialize the PDFLoader
    Args:
        file_path: Path to the PDF file
        metadata: Optional additional metadata
    """
    def __init__(
        self, 
        file_path: str,
        metadata: Optional[dict] = None
    ):
        self.file_path = Path(file_path)
        self.extra_metadata = metadata or {}
    
    """
    Load the PDF and extract text from each page
    Returns:
        A list of Documents, one per page
    Raises:
        FileNotFoundError: If the file doesn't exist
    """
    def load(self) -> list[Document]:
        if not self.file_path.exists():
            raise FileNotFoundError(f"File not found: {self.file_path}")
        
        reader = PdfReader(self.file_path)
        documents = []
        
        for page_num, page in enumerate(reader.pages):
            text = page.extract_text()
            
            if text.strip():  # Only add pages with content
                metadata = {
                    "source": str(self.file_path),
                    "file_name": self.file_path.name,
                    "page": page_num + 1,
                    "total_pages": len(reader.pages),
                    **self.extra_metadata
                }
                documents.append(Document(page_content=text, metadata=metadata))
        
        return documents
