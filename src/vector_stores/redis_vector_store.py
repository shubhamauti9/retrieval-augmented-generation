import hashlib
import json
import uuid
from datetime import datetime
from typing import Optional, Any

import numpy as np
from numpy.typing import NDArray

from src.cache.redis_manager import RedisManager, get_redis
from src.vector_stores.base_vector_store import BaseVectorStore
from src.utils.document import Document
from src.utils.similarity import cosine_similarity

PREFIX = "rag"
DOC_PREFIX = "doc"
COLLECTION_IDX = "idx:collection"
SOURCE_IDX = "idx:source"
ALL_DOCS_KEY = "all_docs"

"""
RedisVectorStore - Vector storage and similarity search using Redis
Stores document embeddings in Redis and performs similarity search
"""
"""
Vector store using Redis for persistence
Stores documents and embeddings in Redis with support for:
    - Similarity search (brute-force cosine similarity)
    - Metadata filtering
    - Collection management
    - Document versioning
Data Structure:
    - doc:{id} -> JSON with content, metadata, embedding
    - idx:collection:{name} -> Set of doc IDs in collection
    - idx:source:{name} -> Set of doc IDs from source
Example:
    >>> store = RedisVectorStore()
    >>> store.add_documents([doc], [embedding], collection="hr_policies")
    >>> results = store.similarity_search(query_emb, k=5)
"""
class RedisVectorStore(BaseVectorStore):
    
    """
    Initialize Redis vector store
    Args:
        redis_manager: Optional existing Redis manager
        host: Redis host
        port: Redis port
        db: Redis database number
        password: Optional password
    """
    def __init__(
        self,
        redis_manager: Optional[RedisManager] = None,
        host: str = "localhost",
        port: int = 6379,
        db: int = 0,
        password: Optional[str] = None
    ):
        if redis_manager:
            self.redis = redis_manager
        else:
            self.redis = get_redis(host, port, db, password)
    
    """
    Generate document key
    Args:
        doc_id: Document ID
    Returns:
        Document key
    """
    def _doc_key(self, doc_id: str) -> str:
        return f"{self.PREFIX}:{self.DOC_PREFIX}:{doc_id}"
    
    """
    Generate collection key
    Args:
        collection: Collection name
    Returns:
        Collection key
    """
    def _collection_key(self, collection: str) -> str:
        return f"{self.PREFIX}:{self.COLLECTION_IDX}:{collection}"
    
    """
    Generate source key
    Args:
        source: Source name
    Returns:
        Source key
    """
    def _source_key(self, source: str) -> str:
        source_hash = hashlib.md5(source.encode()).hexdigest()[:12]
        return f"{self.PREFIX}:{self.SOURCE_IDX}:{source_hash}"
    
    """
    Generate all documents key
    Returns:
        All documents key
    """
    def _all_docs_key(self) -> str:
        return f"{self.PREFIX}:{self.ALL_DOCS_KEY}"
    
    """
    Add documents with embeddings to the store
    Args:
        documents: List of Document objects
        embeddings: Corresponding embeddings
        collection: Collection name
    Returns:
        List of document IDs
    """
    def add_documents(
        self,
        documents: list[Document],
        embeddings: list[NDArray[np.float32]],
        collection: Optional[str] = None
    ) -> list[str]:
        if len(documents) != len(embeddings):
            raise ValueError("Documents and embeddings must have same length")
        
        doc_ids = []
        pipe = self.redis.client.pipeline()
        
        for doc, emb in zip(documents, embeddings):
            doc_id = str(uuid.uuid4())
            coll = collection or doc.metadata.get("collection", "default")
            source = doc.metadata.get("source", "unknown")
            
            """
            Prepare document data
            """
            doc_data = {
                "id": doc_id,
                "content": doc.page_content,
                "embedding": emb.tolist(),
                "collection": coll,
                "source": source,
                "metadata": doc.metadata,
                "created_at": datetime.now().isoformat(),
            }
            
            """
            Store document
            """
            pipe.set(self._doc_key(doc_id), json.dumps(doc_data))
            
            """
            Add to indices
            """
            pipe.sadd(self._all_docs_key(), doc_id)
            pipe.sadd(self._collection_key(coll), doc_id)
            pipe.sadd(self._source_key(source), doc_id)
            
            doc_ids.append(doc_id)
        
        pipe.execute()
        return doc_ids
    
    """
    Get document data by ID
    Args:
        doc_id: Document ID
    Returns:
        Document data or None if not found
    """
    def _get_document(self, doc_id: str) -> Optional[dict]:
        data = self.redis.client.get(self._doc_key(doc_id))
        if data:
            return json.loads(data)
        return None
    
    """
    Get all documents, optionally filtered by collection
    Args:
        collection: Optional collection name
    Returns:
        List of document data
    """
    def _get_all_documents(
        self, 
        collection: Optional[str] = None
    ) -> list[dict]:
        if collection:
            doc_ids = self.redis.client.smembers(self._collection_key(collection))
        else:
            doc_ids = self.redis.client.smembers(self._all_docs_key())
        
        documents = []
        for doc_id in doc_ids:
            doc_data = self._get_document(doc_id)
            if doc_data:
                documents.append(doc_data)
        
        return documents
    
    """
    Find k most similar documents using cosine similarity
    Args:
        query_embedding: Query vector
        k: Number of results to return
        filter: Optional metadata filter (e.g., {"collection": "hr_policies"})
    Returns:
        List of (Document, similarity_score) tuples
    """
    def similarity_search(
        self,
        query_embedding: NDArray[np.float32],
        k: int = 4,
        filter: Optional[dict] = None
    ) -> list[tuple[Document, float]]:
        """
        Get collection filter if specified
        """
        collection = filter.get("collection") if filter else None
        
        """
        Get all candidate documents
        """
        documents = self._get_all_documents(collection)
        
        if not documents:
            return []
        
        """
        Apply additional metadata filters
        """
        if filter:
            filtered_docs = []
            for doc_data in documents:
                match = True
                for key, value in filter.items():
                    if key == "collection":
                        if doc_data.get("collection") != value:
                            match = False
                            break
                    elif doc_data.get("metadata", {}).get(key) != value:
                        match = False
                        break
                if match:
                    filtered_docs.append(doc_data)
            documents = filtered_docs
        
        """
        Compute similarities
        """
        scores = []
        for doc_data in documents:
            doc_embedding = np.array(doc_data["embedding"], dtype=np.float32)
            similarity = cosine_similarity(query_embedding, doc_embedding)
            scores.append((doc_data, similarity))
        
        """
        Sort by similarity (descending)
        """
        scores.sort(key=lambda x: x[1], reverse=True)
        
        """
        Return top k
        """
        results = []
        for doc_data, score in scores[:k]:
            doc = Document(
                page_content=doc_data["content"],
                metadata=doc_data.get("metadata", {})
            )
            results.append((doc, float(score)))
        
        return results
    
    """
    Delete documents by their IDs
    """
    def delete(self, ids: list[str]) -> None:
        pipe = self.redis.client.pipeline()
        
        for doc_id in ids:
            doc_data = self._get_document(doc_id)
            if doc_data:
                """
                Remove from indices
                """
                pipe.srem(self._all_docs_key(), doc_id)
                pipe.srem(self._collection_key(doc_data["collection"]), doc_id)
                pipe.srem(self._source_key(doc_data["source"]), doc_id)
                """
                Delete document
                """
                pipe.delete(self._doc_key(doc_id))
        
        pipe.execute()
    
    """
    Delete documents by source
    """
    def delete_by_source(self, source: str) -> int:
        doc_ids = self.redis.client.smembers(self._source_key(source))
        if doc_ids:
            self.delete(list(doc_ids))
            return len(doc_ids)
        return 0
    
    """
    Delete all documents in a collection
    """
    def delete_collection(self, collection: str) -> int:
        doc_ids = self.redis.client.smembers(self._collection_key(collection))
        if doc_ids:
            self.delete(list(doc_ids))
            return len(doc_ids)
        return 0
    
    """
    List all unique collections
    """
    def list_collections(self) -> list[str]:
        pattern = f"{self.PREFIX}:{self.COLLECTION_IDX}:*"
        keys = self.redis.keys(pattern)
        
        collections = []
        prefix_len = len(f"{self.PREFIX}:{self.COLLECTION_IDX}:")
        for key in keys:
            collection_name = key[prefix_len:]
            """
            Only include non-empty collections
            """
            if self.redis.client.scard(key) > 0:
                collections.append(collection_name)
        
        return collections
    
    """
    List all document sources
    """
    def list_sources(self, collection: Optional[str] = None) -> list[dict]:
        documents = self._get_all_documents(collection)
        
        sources = {}
        for doc in documents:
            source = doc.get("source", "unknown")
            if source not in sources:
                sources[source] = {
                    "source": source,
                    "count": 0,
                    "created_at": doc.get("created_at")
                }
            sources[source]["count"] += 1
        
        return list(sources.values())
    
    """
    Get total document count
    """
    def get_document_count(self, collection: Optional[str] = None) -> int:
        if collection:
            return self.redis.client.scard(self._collection_key(collection))
        return self.redis.client.scard(self._all_docs_key())
    
    """
    Clear all documents from the store
    """
    def clear_all(self) -> int:
        doc_ids = self.redis.client.smembers(self._all_docs_key())
        if doc_ids:
            self.delete(list(doc_ids))
            return len(doc_ids)
        return 0
    
    """
    Return the number of documents in the store
    """
    def __len__(self) -> int:
        return self.get_document_count()
