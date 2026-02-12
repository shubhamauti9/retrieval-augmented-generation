import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from config import settings
from routers import ingest_router, query_router, admin_router

"""
RAG Pipeline API - Main Application
FastAPI application for document ingestion and RAG queries
Create FastAPI app
"""
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="""
        RAG Pipeline API
        
        ## Features
            - **Document Ingestion**: Upload PDF, DOCX, XLSX, PPTX, TXT, MD files
            - **Knowledge Base Query**: Ask questions and get AI-powered answers
            - **Collection Management**: Organize documents into collections
            - **Source Citations**: Get references for every answer
        
        ## Collections
            - `sebi_circulars` - SEBI regulatory documents
            - `hr_policies` - Company HR policies
            - `default` - General documents
    """,
    docs_url="/docs",
    redoc_url="/redoc"
)

"""
Configure CORS
"""
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

"""
Include routers
"""
app.include_router(ingest_router)
app.include_router(query_router)
app.include_router(admin_router)

"""
Root endpoint with API information
"""
@app.get("/")
async def root():
    return {
        "name": settings.app_name,
        "version": settings.app_version,
        "docs": "/docs",
        "health": "/admin/health"
    }

"""
Health check endpoint.
Returns:
    System health status and configuration
"""
@app.get("/health", response_model=HealthResponse)
async def health_check():
    return HealthResponse(
        status="healthy",
        version=settings.app_version,
        embedding_model=settings.embedding_model,
        llm_model=settings.llm_model,
        vector_store="Redis",
        document_count=len(ingestion_service.vector_store)
    )

"""
Application startup tasks
"""
@app.on_event("startup")
async def startup():
    print(f"Starting {settings.app_name} v{settings.app_version}")
    print(f"Vector store: {settings.vector_store_dir}")
    print(f"Embedding model: {settings.embedding_model}")

"""
Application shutdown tasks
"""
@app.on_event("shutdown")
async def shutdown():
    print("Shutting down RAG Pipeline API")

"""
For running with: python -m api.main
"""
if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug
    )
