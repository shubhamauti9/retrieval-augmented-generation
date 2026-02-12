from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from typing import Optional
import json

from models import QueryRequest, QueryResponse, SourceInfo
from services import retrieval_service

router = APIRouter(prefix="/query", tags=["Query"])

"""
Query the knowledge base.
This endpoint:
    1. Embeds the question
    2. Retrieves relevant documents
    3. Generates an answer using LLM
Args:
    request: Query request with question and options
Returns:
    Answer with source citations
"""
@router.post("/pipeline", response_model=QueryResponse)
async def query_knowledge_base(request: QueryRequest):
    result = retrieval_service.query(
        question=request.question,
        collection=request.collection,
        top_k=request.top_k,
        include_sources=request.include_sources
    )
    
    return QueryResponse(
        answer=result["answer"],
        sources=[SourceInfo(**s) for s in result["sources"]],
        query=result["query"],
        collection=result["collection"]
    )

"""
Retrieve relevant documents without LLM generation.
Useful for:
    - Debugging retrieval quality
    - Custom generation pipelines
    - Document exploration
Args:
    request: Query request
Returns:
    List of relevant documents with scores
"""
@router.post("/retrieve")
async def retrieve_documents(request: QueryRequest):
    results = retrieval_service.get_relevant_documents(
        question=request.question,
        collection=request.collection,
        top_k=request.top_k
    )
    
    return {
        "query": request.question,
        "collection": request.collection,
        "documents": results
    }

"""
Query with streaming response.
Returns server-sent events for real-time LLM output.
Args:
    request: Query request
Returns:
    Streaming response with answer chunks
"""
@router.post("/stream")
async def query_stream(
    request: QueryRequest
):
    async def generate():
        """
        step 1 - retrieve documents
        """
        result = retrieval_service.query(
            question=request.question,
            collection=request.collection,
            top_k=request.top_k,
            include_sources=request.include_sources
        )
        
        """
        step 2 - Send sources first
        """
        yield f"data: {json.dumps({'type': 'sources', 'data': result['sources']})}\n\n"
        
        """
        step 3 - Then send the answer
        In a real implementation, you'd stream from the LLM
        """
        yield f"data: {json.dumps({'type': 'answer', 'data': result['answer']})}\n\n"
        
        """
        step 4 - Signal completion
        """
        yield f"data: {json.dumps({'type': 'done'})}\n\n"
    
    return StreamingResponse(
        generate(),
        media_type="text/event-stream"
    )
