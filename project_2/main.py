"""
Project 2: RAG System with GPU Acceleration
Enterprise RAG service optimized for NVIDIA L4 GPUs
"""


from fastapi import FastAPI, Request
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
    extract_trace_id_from_header,
    setup_tracing,
    instrument_fastapi,
    set_correlation_id,
)

app = FastAPI(title="Project 2 - RAG API", version="1.0.0")

project_id = os.getenv('GCP_PROJECT_ID', 'local-dev')
logger = JSONLogger("project_2_rag", project_id=project_id)

setup_tracing("project-2-rag")
instrument_fastapi(app)

@app.middleware("http")
async def add_trace_context(request: Request, call_next):
    trace_header = request.headers.get("X-Cloud-Trace-Context", "")
    if trace_header:
        os.environ['HTTP_X_CLOUD_TRACE_CONTEXT'] = trace_header
    trace_id = extract_trace_id_from_header(trace_header) if trace_header else None

    correlation_id = request.headers.get("X-Correlation-ID") or generate_correlation_id()
    request.state.correlation_id = correlation_id
    request.state.trace_id = trace_id
    set_correlation_id(correlation_id)

    logger.info(
        f"Incoming request: {request.method} {request.url.path}",
        correlation_id,
        method=request.method,
        path=request.url.path
    )

    response = await call_next(request)
    response.headers["X-Correlation-ID"] = correlation_id
    if trace_id:
        response.headers["X-Cloud-Trace-Context"] = trace_header
    return response

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
    lib_info = get_lib_info()
    correlation_id = getattr(request.state, "correlation_id", None)
    logger.info(
        "Hello from Project 2 RAG",
        correlation_id,
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
async def health(request: Request):
    correlation_id = getattr(request.state, "correlation_id", None)
    logger.info("Health check", correlation_id, gpu_available=True)
    return JSONResponse(
        content=format_response(
            data={
                "status": "healthy",
                "gpu_available": True,
                "gpu_type": "NVIDIA L4",
                "correlation_id": correlation_id
            },
            message="Service is operational"
        )
    )

@app.get("/version")
async def version(request: Request):
    lib_info = get_lib_info()
    correlation_id = getattr(request.state, "correlation_id", None)
    logger.info("Version check", correlation_id, lib_version=lib_info["version"])
    return JSONResponse(
        content=format_response(
            data={
                "service_version": "1.0.0",
                "shared_lib_info": lib_info,
                "gpu_acceleration": True,
                "gpu_type": "NVIDIA L4",
                "correlation_id": correlation_id
            }
        )
    )

@app.post("/index")
async def index_documents(doc_request: DocumentRequest, request: Request):
    correlation_id = getattr(request.state, "correlation_id", None)
    logger.info(
        "Indexing documents",
        correlation_id,
        doc_count=len(doc_request.documents),
        use_gpu=True
    )
    return JSONResponse(
        content=format_response(
            data={
                "indexed_count": len(doc_request.documents),
                "status": "success",
                "gpu_accelerated": True,
                "correlation_id": correlation_id
            },
            message=f"Successfully indexed {len(doc_request.documents)} documents"
        )
    )

@app.post("/query")
async def query_rag(query_request: QueryRequest, request: Request):
    correlation_id = getattr(request.state, "correlation_id", None)
    logger.info(
        "Processing RAG query",
        correlation_id,
        query_length=len(query_request.query),
        top_k=query_request.top_k,
        gpu_enabled=query_request.use_gpu
    )
    results = [
        {
            "document": f"Sample document {i}",
            "score": 0.95 - (i * 0.1),
            "metadata": {"source": f"doc_{i}"}
        }
        for i in range(query_request.top_k)
    ]
    return JSONResponse(
        content=format_response(
            data={
                "query": query_request.query,
                "results": results,
                "gpu_accelerated": query_request.use_gpu,
                "processing_time_ms": 45,
                "correlation_id": correlation_id
            },
            message="Query processed successfully"
        )
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)
