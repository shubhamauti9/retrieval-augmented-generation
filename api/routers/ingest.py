from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from typing import Optional

from models import IngestionResponse, BatchIngestionResponse
from services import ingestion_service

router = APIRouter(prefix="/ingest", tags=["Ingestion"])

"""
Ingestion Router - Document upload and processing endpoints
"""
"""
Upload and ingest a single document
Supported formats: 
    .txt, .md, .pdf, .docx, .xlsx, .pptx
Args:
    file: The document file to upload
    collection: Collection name (e.g., "sebi_circulars", "hr_policies")
    metadata: Optional JSON string with additional metadata
Returns:
    Ingestion result with document IDs and chunk count
"""
@router.post("/upload", response_model=IngestionResponse)
async def upload_document(
    file: UploadFile = File(...),
    collection: str = Form(default="default"),
    metadata: Optional[str] = Form(default=None)
):
    """
    Parse metadata if provided
    """
    extra_metadata = None
    if metadata:
        try:
            import json
            extra_metadata = json.loads(metadata)
        except:
            pass
    
    """
    Process file
    """
    result = ingestion_service.ingest_file(
        file=file.file,
        filename=file.filename,
        collection=collection,
        metadata=extra_metadata
    )
    
    """
    Return result
    """
    if result["status"] == "error":
        raise HTTPException(
            status_code=400,
            detail=result["message"]
        )
    
    return IngestionResponse(**result)

"""
Upload and ingest multiple documents at once
Args:
    files: List of document files
    collection: Collection name for all files
Returns:
    Batch ingestion result with per-file status
"""
@router.post("/batch", response_model=BatchIngestionResponse)
async def upload_batch(
    files: list[UploadFile] = File(...),
    collection: str = Form(default="default")
):
    results = []
    successful = 0
    failed = 0
    
    for file in files:
        result = ingestion_service.ingest_file(
            file=file.file,
            filename=file.filename,
            collection=collection
        )
        
        results.append(IngestionResponse(**result))
        
        if result["status"] == "success":
            successful += 1
        else:
            failed += 1
    
    return BatchIngestionResponse(
        status="completed",
        total_files=len(files),
        successful=successful,
        failed=failed,
        results=results
    )

"""
Delete all documents from a specific source
Args:
    source_name: Name of the source file to delete
Returns:
    Deletion status
"""
@router.delete("/source/{source_name}")
async def delete_source(source_name: str):
    success = ingestion_service.delete_source(source_name)
    
    if success:
        return {
            "status": "success",
            "message": f"Deleted documents from {source_name}"
        }
    else:
        raise HTTPException(
            status_code=404,
            detail="Source not found"
        )

"""
Get ingestion statistics
Returns:
    Statistics about ingested documents
"""
@router.get("/stats")
async def get_ingestion_stats():
    return ingestion_service.get_stats()
