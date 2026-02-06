"""
Project 3: Simple API Service
Another service demonstrating independent versioning in the Lean Hub
"""

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
import sys
import os

# Add shared_libs to path for import
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from shared_libs.utils import (
    JSONLogger, 
    get_lib_info, 
    format_response,
    generate_correlation_id,
    extract_trace_id_from_header
)

app = FastAPI(title="Project 3 API", version="1.0.0")
logger = JSONLogger("project_3")

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

@app.on_event("startup")
async def startup_event():
    logger.info("Project 3 API starting up", lib_version=get_lib_info()["version"])

@app.get("/")
async def root(request: Request):
    """Root endpoint with version information"""
    lib_info = get_lib_info()
    correlation_id = getattr(request.state, "correlation_id", None)
    
    logger.info(
        "Hello from Project 3",
        correlation_id=correlation_id,
        request="root",
        lib_version=lib_info["version"]
    )
    
    return JSONResponse(
        content=format_response(
            data={
                "service": "Project 3",
                "message": "Hello from Project 3!",
                "shared_lib_version": lib_info["version"],
                "service_version": "1.0.0"
            },
            message="Project 3 API is running"
        )
    )

@app.get("/health")
async def health():
    """Health check endpoint"""
    return JSONResponse(
        content=format_response(
            data={"status": "healthy"},
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
                "shared_lib_info": lib_info
            }
        )
    )

@app.get("/status")
async def status():
    """Extended status endpoint"""
    lib_info = get_lib_info()
    logger.info("Status check requested", lib_version=lib_info["version"])
    
    return JSONResponse(
        content=format_response(
            data={
                "service": "Project 3",
                "operational": True,
                "shared_lib_version": lib_info["version"],
                "endpoints": ["/", "/health", "/version", "/status"]
            },
            message="All systems operational"
        )
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)
