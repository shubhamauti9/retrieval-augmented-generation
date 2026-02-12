import hashlib
from pathlib import Path
from typing import Optional, BinaryIO
import shutil

from config import settings
from src.embeddings import EmbeddingModel
from src.vector_stores import RedisVectorStore

from src.loaders import (
    TextLoader,
    PDFLoader,
    DOCXLoader,
    ExcelLoader,
    PPTXLoader
)

"""
Supported file extensions and their loaders
"""
SUPPORTED_EXTENSIONS = {
    ".txt": "text",
    ".md": "text",
    ".pdf": "pdf",
    ".docx": "docx",
    ".xlsx": "excel",
    ".pptx": "pptx",
}

loaders = {
    "text": TextLoader,
    "pdf": PDFLoader,
    "docx": DOCXLoader,
    "excel": ExcelLoader,
    "pptx": PPTXLoader,
}

"""
Ingestion Service - Handle document processing pipeline
Handles:
    - File type detection
    - Document loading
    - Text splitting
    - Embedding generation
    - Vector store insertion
"""
class IngestionService:
    """
    Initialize the ingestion service
    """
    def __init__(self):
        self._embedding_model = None
        self._vector_store = None
        self._text_splitter = None
    
    """
    Lazy-load embedding model
    """
    @property
    def embedding_model(self):
        if self._embedding_model is None:
            self._embedding_model = EmbeddingModel(settings.embedding_model)
        return self._embedding_model
    
    """
    Lazy-load vector store (Redis-based)
    """
    @property
    def vector_store(self):
        if self._vector_store is None:
            self._vector_store = RedisVectorStore(
                host=settings.redis_host,
                port=settings.redis_port,
                db=settings.redis_db,
                password=settings.redis_password
            )
        return self._vector_store
    
    """
    Lazy-load text splitter
    """
    @property
    def text_splitter(self):
        if self._text_splitter is None:
            from src.text_splitters import RecursiveCharacterTextSplitter
            self._text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=settings.chunk_size,
                chunk_overlap=settings.chunk_overlap
            )
        return self._text_splitter
    
    """
    Detect file type from filename
    """
    def detect_file_type(
        self, filename: str
    ) -> Optional[str]:
        ext = Path(filename).suffix.lower()
        return self.SUPPORTED_EXTENSIONS.get(ext)
    
    """
    Save uploaded file to disk
    """
    def save_uploaded_file(
        self, 
        file: BinaryIO, 
        filename: str,
        collection: str = "default"
    ) -> Path:
        """
        Create collection directory
        """
        collection_dir = settings.uploads_dir / collection
        collection_dir.mkdir(parents=True, exist_ok=True)
        
        # Save file
        file_path = collection_dir / filename
        with open(file_path, "wb") as f:
            shutil.copyfileobj(file, f)
        
        return file_path
    
    """
    Load a document using the appropriate loader
    """
    def load_document(
        self, file_path: Path, file_type: str
    ):        
        loader_class = loaders.get(file_type)
        if not loader_class:
            raise ValueError(f"Unsupported file type: {file_type}")
        
        loader = loader_class(str(file_path))
        return loader.load()
    
    """
    Ingest a single file into the vector store.
    Args:
        file: File-like object
        filename: Original filename
        collection: Collection to store in
        metadata: Additional metadata
    Returns:
        Ingestion result dict
    """
    def ingest_file(
        self,
        file: BinaryIO,
        filename: str,
        collection: str = "default",
        metadata: Optional[dict] = None
    ) -> dict:
        """
        step 1 - Detect file type
        """
        file_type = self.detect_file_type(filename)
        if not file_type:
            return {
                "status": "error",
                "message": f"Unsupported file type: {Path(filename).suffix}",
                "document_ids": [],
                "chunk_count": 0,
                "source": filename
            }
        
        try:
            """
            step 2 - Save file
            """
            file_path = self.save_uploaded_file(file, filename, collection)
            
            """
            step 3 - Load document
            """
            documents = self.load_document(file_path, file_type)
            
            """
            step 4 - Add collection to metadata
            """
            for doc in documents:
                doc.metadata["collection"] = collection
                if metadata:
                    doc.metadata.update(metadata)
            
            """
            step 5 - Split into chunks
            """
            chunks = self.text_splitter.split_documents(documents)
            
            """
            step 6 - Generate embeddings
            """
            embeddings = self.embedding_model.embed_batch(
                [chunk.page_content for chunk in chunks]
            )
            
            """
            step 7 - Store in vector store
            """
            doc_ids = self.vector_store.add_documents(
                chunks, 
                list(embeddings),
                collection=collection
            )
            
            return {
                "status": "success",
                "message": f"Successfully ingested {filename}",
                "document_ids": doc_ids,
                "chunk_count": len(chunks),
                "source": filename
            }    
        except Exception as e:
            return {
                "status": "error",
                "message": str(e),
                "document_ids": [],
                "chunk_count": 0,
                "source": filename
            }
    
    """
    Delete all documents from a source
    """
    def delete_source(
        self, source: str
    ) -> bool:
        try:
            self.vector_store.delete_by_source(source)
            return True
        except:
            return False
    
    """
    Get ingestion statistics
    """
    def get_stats(self) -> dict:
        return {
            "total_documents": len(self.vector_store),
            "collections": self.vector_store.list_collections(),
            "sources": self.vector_store.list_sources()
        }

"""
Global service instance
"""
ingestion_service = IngestionService()
