from fastapi import APIRouter, HTTPException

from config import settings
from models import CollectionListResponse, CollectionInfo, HealthResponse
from services import ingestion_service
from api.services import retrieval_service
from src.cache import get_redis

router = APIRouter(prefix="/admin", tags=["Admin"])

"""
Admin Router - Management and monitoring endpoints
"""
"""
List all document collections
Returns:
    List of collections with document counts
"""
@router.get("/collections", response_model=CollectionListResponse)
async def list_collections():
    collections = ingestion_service.vector_store.list_collections()
    
    collection_infos = []
    for name in collections:
        count = ingestion_service.vector_store.get_document_count(collection=name)
        sources = ingestion_service.vector_store.list_sources(collection=name)
        
        collection_infos.append(CollectionInfo(
            name=name,
            document_count=count,
            sources=[s.get("source", "") for s in sources[:10]]  # Limit sources
        ))
    
    return CollectionListResponse(collections=collection_infos)

"""
Delete an entire collection
WARNING: This will delete all documents in the collection
Args:
    collection_name: Name of collection to delete
Returns:
    Deletion status
"""
@router.delete("/collections/{collection_name}")
async def delete_collection(collection_name: str):
    try:
        ingestion_service.vector_store.delete_collection(collection_name)
        return {
            "status": "success",
            "message": f"Deleted collection: {collection_name}"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

"""
List all document sources
Args:
    collection: Optional collection filter
Returns:
    List of sources with metadata
"""
@router.get("/sources")
async def list_sources(collection: str = None):
    sources = ingestion_service.vector_store.list_sources(collection=collection)
    return {
        "collection": collection,
        "sources": sources
    }

"""
Get detailed system statistics
Returns:
    Comprehensive system stats
"""
@router.get("/stats")
async def get_system_stats():
    stats = ingestion_service.get_stats()
    
    result = {
        "vector_store": {
            "type": "Redis",
            "host": settings.redis_host,
            "port": settings.redis_port,
            "total_documents": stats["total_documents"],
        },
        "collections": stats["collections"],
        "embedding_model": settings.embedding_model,
        "chunk_settings": {
            "chunk_size": settings.chunk_size,
            "chunk_overlap": settings.chunk_overlap
        }
    }
    
    """
    Add cache stats if Redis is enabled
    """
    if settings.redis_enabled:
        result["cache"] = retrieval_service.get_cache_stats()
    
    return result


"""
Get Redis connection status
Returns:
    Redis connection info and stats
"""
@router.get("/redis/status")
async def redis_status():
    if not settings.redis_enabled:
        return {
            "enabled": False,
            "message": "Redis is disabled"
        }
    
    try:
        redis_mgr = get_redis(
            host=settings.redis_host,
            port=settings.redis_port,
            db=settings.redis_db,
            password=settings.redis_password
        )
        
        connected = redis_mgr.ping()
        
        """
        Get some info
        """
        if connected:
            info = redis_mgr.client.info("memory")
            return {
                "enabled": True,
                "connected": True,
                "host": settings.redis_host,
                "port": settings.redis_port,
                "db": settings.redis_db,
                "memory_used": info.get("used_memory_human", "unknown"),
                "memory_peak": info.get("used_memory_peak_human", "unknown")
            }
        else:
            return {
                "enabled": True,
                "connected": False,
                "message": "Unable to connect to Redis"
            }
    except Exception as e:
        return {
            "enabled": True,
            "connected": False,
            "error": str(e)
        }

"""
Get cache statistics
Returns:
    Stats for embedding and query caches
"""
@router.get("/redis/cache-stats")
async def redis_cache_stats():
    return retrieval_service.get_cache_stats()

"""
Clear Redis caches
Args:
    cache_type: 'all', 'query', or 'embedding'
Returns:
    Number of keys cleared
"""
@router.post("/redis/clear-cache")
async def clear_redis_cache(cache_type: str = "all"):
    if cache_type == "all":
        return retrieval_service.clear_caches()
    elif cache_type == "query" and retrieval_service.query_cache:
        return {
            "query_cache": retrieval_service.query_cache.clear_all()
        }
    elif cache_type == "embedding" and retrieval_service.embedding_cache:
        return {
            "embedding_cache": retrieval_service.embedding_cache.clear_all()
        }
    else:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid cache type: {cache_type}"
        )
