"""
Loaders module - Load documents from various sources.
"""

from src.loaders.base_loader import BaseLoader
from src.loaders.text_loader import TextLoader
from src.loaders.pdf_loader import PDFLoader
from src.loaders.directory_loader import DirectoryLoader
from src.loaders.docx_loader import DOCXLoader
from src.loaders.excel_loader import ExcelLoader
from src.loaders.pptx_loader import PPTXLoader

__all__ = [
    "BaseLoader",
    "TextLoader",
    "PDFLoader",
    "DirectoryLoader",
    "DOCXLoader",
    "ExcelLoader",
    "PPTXLoader",
]
