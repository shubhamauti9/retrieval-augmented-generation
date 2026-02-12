from pydantic import BaseModel, Field
from typing import Optional, Any
from datetime import datetime

"""
Pydantic models for API requests and responses
"""
"""
Metadata for a document
"""
class DocumentMetadata(BaseModel):
    source: str
    file_name: Optional[str] = None
    file_type: Optional[str] = None
    collection: str = "default"
    page: Optional[int] = None
    chunk_index: Optional[int] = None
    extra: Optional[dict[str, Any]] = None

"""
Response model for a document
"""
class DocumentResponse(BaseModel):
    id: str
    content: str
    metadata: DocumentMetadata
    created_at: datetime
    updated_at: datetime

"""
Response model for a document
"""
class DocumentListResponse(BaseModel):
    documents: list[DocumentResponse]
    total: int
    page: int = 1
    page_size: int = 20

"""
Request for URL-based ingestion
"""
class IngestionRequest(BaseModel):
    url: str
    collection: str = "default"
    metadata: Optional[dict[str, Any]] = None

"""
Response after ingestion
"""
class IngestionResponse(BaseModel):
    status: str  # "success", "error", "processing"
    message: str
    document_ids: list[str] = []
    chunk_count: int = 0
    source: str = ""

"""
Response for batch ingestion
"""
class BatchIngestionResponse(BaseModel):
    status: str
    total_files: int
    successful: int
    failed: int
    results: list[IngestionResponse]

"""
Request for querying the knowledge base
"""
class QueryRequest(BaseModel):
    question: str = Field(min_length=1, max_length=1000)
    collection: Optional[str] = None
    top_k: int = Field(default=5, ge=1, le=20)
    include_sources: bool = True
    filters: Optional[dict[str, Any]] = None

"""
Information about a retrieved source
"""
class SourceInfo(BaseModel):
    content: str
    source: str
    score: float
    metadata: Optional[dict[str, Any]] = None

"""
Response from a query
"""
class QueryResponse(BaseModel):
    answer: str
    sources: list[SourceInfo] = []
    query: str
    collection: Optional[str] = None

"""
Information about a collection
"""
class CollectionInfo(BaseModel):
    name: str
    document_count: int
    sources: list[str] = []

"""
Response for listing collections
"""
class CollectionListResponse(BaseModel):
    collections: list[CollectionInfo]

"""
Health check response
"""
class HealthResponse(BaseModel):
    status: str
    version: str
    embedding_model: str
    llm_model: str
    vector_store: str
    document_count: int