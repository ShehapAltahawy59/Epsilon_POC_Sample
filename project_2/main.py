"""
Project 2: RAG System with GPU Acceleration
Enterprise RAG service optimized for NVIDIA L4 GPUs
"""

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import sys
import os
from typing import List, Optional

# Add shared_libs to path for import
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from shared_libs.utils import (
    JSONLogger, 
    get_lib_info, 
    format_response,
    generate_correlation_id,
    extract_trace_id_from_header
)

app = FastAPI(title="Project 2 - RAG API", version="1.0.0")
logger = JSONLogger("project_2_rag")

# Middleware for correlation ID and trace context
@app.middleware("http")
async def add_trace_context(request: Request, call_next):
    """
    Extract or generate correlation ID and trace context.
    Adds correlation_id to request state for use in endpoints.
    """
    # Extract or generate correlation ID
    correlation_id = request.headers.get("X-Correlation-ID") or generate_correlation_id()
    
    # Extract Cloud Trace context
    trace_header = request.headers.get("X-Cloud-Trace-Context")
    trace_id = extract_trace_id_from_header(trace_header) if trace_header else None
    
    # Store in request state
    request.state.correlation_id = correlation_id
    request.state.trace_id = trace_id
    
    # Log request
    logger.info(
        f"Incoming request: {request.method} {request.url.path}",
        correlation_id=correlation_id,
        trace_id=trace_id,
        method=request.method,
        path=request.url.path
    )
    
    response = await call_next(request)
    
    # Add correlation ID to response headers
    response.headers["X-Correlation-ID"] = correlation_id
    if trace_id:
        response.headers["X-Cloud-Trace-Context"] = trace_header
    
    return response

# Pydantic models
class QueryRequest(BaseModel):
    query: str
    top_k: Optional[int] = 5
    use_gpu: Optional[bool] = True

class DocumentRequest(BaseModel):
    documents: List[str]
    metadata: Optional[dict] = None

@app.on_event("startup")
async def startup_event():
    lib_info = get_lib_info()
    logger.info(
        "Project 2 RAG API starting up",
        lib_version=lib_info["version"],
        gpu_enabled=True,
        gpu_type="NVIDIA L4"
    )

@app.get("/")
async def root(request: Request):
    """Root endpoint with version information"""
    lib_info = get_lib_info()
    correlation_id = getattr(request.state, "correlation_id", None)
    
    logger.info(
        "Hello from Project 2 RAG",
        correlation_id=correlation_id,
        request="root",
        lib_version=lib_info["version"]
    )
    
    return JSONResponse(
        content=format_response(
            data={
                "service": "Project 2 - RAG System",
                "message": "Hello from RAG Service!",
                "shared_lib_version": lib_info["version"],
                "service_version": "1.0.0",
                "gpu_enabled": True,
                "gpu_type": "NVIDIA L4"
            },
            message="RAG API is running with GPU acceleration"
        )
    )

@app.get("/health")
async def health():
    """Health check endpoint with GPU status"""
    # In production, this would check actual GPU availability
    gpu_available = True
    
    return JSONResponse(
        content=format_response(
            data={
                "status": "healthy",
                "gpu_available": gpu_available,
                "gpu_type": "NVIDIA L4"
            },
            message="Service is operational"
        )
    )

@app.get("/version")
async def version():
    """Version information endpoint"""
    lib_info = get_lib_info()
    return JSONResponse(
        content=format_response(
            data={
                "service_version": "1.0.0",
                "shared_lib_info": lib_info,
                "gpu_acceleration": True,
                "gpu_type": "NVIDIA L4"
            }
        )
    )

@app.post("/index")
async def index_documents(request: DocumentRequest):
    """
    Index documents for RAG retrieval.
    In production, this would use vector embeddings and GPU acceleration.
    """
    logger.info(
        "Indexing documents",
        doc_count=len(request.documents),
        use_gpu=True
    )
    
    return JSONResponse(
        content=format_response(
            data={
                "indexed_count": len(request.documents),
                "status": "success",
                "gpu_accelerated": True
            },
            message=f"Successfully indexed {len(request.documents)} documents"
        )
    )

@app.post("/query")
async def query_rag(request: QueryRequest):
    """
    Query the RAG system for relevant documents.
    In production, this would use GPU-accelerated embeddings and similarity search.
    """
    logger.info(
        "Processing RAG query",
        query_length=len(request.query),
        top_k=request.top_k,
        gpu_enabled=request.use_gpu
    )
    
    # Simulated response - in production would use actual RAG pipeline
    results = [
        {
            "document": f"Sample document {i}",
            "score": 0.95 - (i * 0.1),
            "metadata": {"source": f"doc_{i}"}
        }
        for i in range(request.top_k)
    ]
    
    return JSONResponse(
        content=format_response(
            data={
                "query": request.query,
                "results": results,
                "gpu_accelerated": request.use_gpu,
                "processing_time_ms": 45
            },
            message="Query processed successfully"
        )
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)
