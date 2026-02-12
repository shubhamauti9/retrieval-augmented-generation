import ollama
from typing import Optional

from config import settings
from services.ingestion import ingestion_service
from src.cache import (
    RedisQueryCache,
    RedisEmbeddingCache,
    RedisRateLimiter,
    get_redis
)

"""
Retrieval Service - Handle query processing and RAG with Redis caching
Service for querying the RAG pipeline
Handles:
    - Query embedding (with Redis caching)
    - Similarity search
    - Context formatting
    - LLM generation (with response caching)
    - Rate limiting
"""
class RetrievalService:
    """
    Initialize the retrieval service
    """
    def __init__(self):
        self._llm = None
        self._query_cache = None
        self._embedding_cache = None
        self._rate_limiter = None
    
    """
    Reuse embedding model from ingestion service
    """
    @property
    def embedding_model(self):
        return ingestion_service.embedding_model
    
    """
    Reuse vector store from ingestion service
    """
    @property
    def vector_store(self):
        return ingestion_service.vector_store

    """
    Lazy-load query cache
    this is optional
    """
    @property
    def query_cache(self):
        if self._query_cache is None and settings.redis_enabled:
            try:
                redis_mgr = get_redis(
                    host=settings.redis_host,
                    port=settings.redis_port,
                    db=settings.redis_db,
                    password=settings.redis_password
                )
                if redis_mgr.ping():
                    self._query_cache = RedisQueryCache(
                        redis_manager=redis_mgr,
                        ttl=settings.query_cache_ttl
                    )
            except Exception:
                pass
        return self._query_cache
    
    """
    Lazy-load embedding cache
    """
    @property
    def embedding_cache(self):
        if self._embedding_cache is None and settings.redis_enabled:
            try:
                redis_mgr = get_redis(
                    host=settings.redis_host,
                    port=settings.redis_port,
                    db=settings.redis_db,
                    password=settings.redis_password
                )
                if redis_mgr.ping():
                    self._embedding_cache = RedisEmbeddingCache(
                        redis_manager=redis_mgr,
                        model_name=settings.embedding_model,
                        ttl=settings.embedding_cache_ttl
                    )
            except Exception:
                pass
        return self._embedding_cache
    
    """
    Lazy-load rate limiter
    this is optional
    just for efficient retrieval
    """
    @property
    def rate_limiter(self):
        if self._rate_limiter is None and settings.redis_enabled:
            try:
                redis_mgr = get_redis(
                    host=settings.redis_host,
                    port=settings.redis_port,
                    db=settings.redis_db,
                    password=settings.redis_password
                )
                if redis_mgr.ping():
                    self._rate_limiter = RedisRateLimiter(
                        redis_manager=redis_mgr,
                        max_requests=settings.rate_limit_requests,
                        window_seconds=settings.rate_limit_window
                    )
            except Exception:
                pass
        return self._rate_limiter
    
    """
    Lazy-load LLM
    """
    @property
    def llm(self):
        if self._llm is None:
            self._llm = self._create_llm()
        return self._llm
    
    """
    Create LLM function
    """
    def _create_llm(self):
        try:
            
            def llm_func(prompt: str) -> str:
                response = ollama.generate(
                    model=settings.llm_model,
                    prompt=prompt
                )
                return response["response"]
            
            return llm_func
        except ImportError:
            """
            Fallback mock LLM
            could be extended
            """
            def mock_llm(prompt: str) -> str:
                return "[LLM not available - install ollama]"
            return mock_llm
    
    """
    Get embedding from cache or compute it
    """
    def _get_cached_embedding(
        self, text: str
    ):
        if self.embedding_cache:
            cached = self.embedding_cache.get(text)
            if cached is not None:
                return cached, True  # (embedding, from_cache)
        
        embedding = self.embedding_model.embed(text)
        
        if self.embedding_cache:
            self.embedding_cache.set(text, embedding)
        
        return embedding, False
    
    """
    Check if request is rate limited
    Returns:
        (is_allowed, remaining_requests)
    """
    def check_rate_limit(
        self, identifier: str
    ) -> tuple[bool, int]:
        if not self.rate_limiter:
            return True, -1  # No limit
        
        allowed = self.rate_limiter.is_allowed(identifier)
        remaining = self.rate_limiter.get_remaining(identifier)
        return allowed, remaining
    
    """
    Query the knowledge base with caching.
    Args:
        question: User's question
        collection: Optional collection filter
        top_k: Number of documents to retrieve
        include_sources: Whether to include source info
        use_cache: Whether to use query cache
    Returns:
        Query result with answer and sources
    """
    def query(
        self,
        question: str,
        collection: Optional[str] = None,
        top_k: int = 5,
        include_sources: bool = True,
        use_cache: bool = True
    ) -> dict:
        """
        step 1 - Check query cache first
        """
        if use_cache and self.query_cache:
            cached_result = self.query_cache.get(question, top_k)
            if cached_result:
                cached_result["_from_cache"] = True
                return cached_result
        
        """
        step 2 - Build filter
        """
        filter_dict = None
        if collection:
            filter_dict = {"collection": collection}
        
        """
        step 3 - Embed query (with caching)
        """
        query_embedding, from_emb_cache = self._get_cached_embedding(question)
        
        """
        step 4 - Search vector store
        """
        results = self.vector_store.similarity_search(
            query_embedding,
            k=top_k,
            filter=filter_dict
        )
        
        if not results:
            return {
                "answer": "I couldn't find any relevant information to answer your question.",
                "sources": [],
                "query": question,
                "collection": collection,
                "_from_cache": False,
                "_embedding_cached": from_emb_cache
            }
        
        """
        step 5 - Format context
        """
        context_parts = []
        sources = []
        
        for doc, score in results:
            context_parts.append(doc.page_content)
            
            if include_sources:
                sources.append({
                    "content": doc.page_content[:300] + "..." if len(doc.page_content) > 300 else doc.page_content,
                    "source": doc.metadata.get("source", "unknown"),
                    "score": score,
                    "metadata": doc.metadata
                })
        
        context = "\n\n---\n\n".join(context_parts)
        
        """
        step 6 - Build prompt
        """
        prompt = f"""Use the following context to answer the question. 
                    If you cannot answer based on the context, say so.
                    Be concise and accurate.

                    Context:
                    {context}

                    Question: {question}

                    Answer:
                """
        
        """
        step 7 - Generate answer
        """
        try:
            answer = self.llm(prompt)
        except Exception as e:
            answer = f"Error generating response: {str(e)}"
        
        result = {
            "answer": answer,
            "sources": sources,
            "query": question,
            "collection": collection,
            "_from_cache": False,
            "_embedding_cached": from_emb_cache
        }
        
        """
        step 7 - Cache the result
        """
        if use_cache and self.query_cache:
            self.query_cache.set(question, result, top_k)
        
        return result
    
    """
    Get relevant documents without LLM generation
    """
    def get_relevant_documents(
        self,
        question: str,
        collection: Optional[str] = None,
        top_k: int = 5
    ) -> list:
        filter_dict = None
        if collection:
            filter_dict = {"collection": collection}
        
        query_embedding, _ = self._get_cached_embedding(question)
        
        results = self.vector_store.similarity_search(
            query_embedding,
            k=top_k,
            filter=filter_dict
        )
        
        return [
            {
                "content": doc.page_content,
                "source": doc.metadata.get("source", "unknown"),
                "score": score,
                "metadata": doc.metadata
            }
            for doc, score in results
        ]
    
    """
    Get cache statistics
    """
    def get_cache_stats(self) -> dict:
        stats = {"redis_enabled": settings.redis_enabled}
        
        if self.embedding_cache:
            stats["embedding_cache"] = self.embedding_cache.stats()
        
        return stats
    
    """
    Clear all caches
    """
    def clear_caches(self) -> dict:
        cleared = {}
        
        if self.query_cache:
            cleared["query_cache"] = self.query_cache.clear_all()
        
        if self.embedding_cache:
            cleared["embedding_cache"] = self.embedding_cache.clear_all()
        
        return cleared


"""
Global service instance
"""
retrieval_service = RetrievalService()
