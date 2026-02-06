"""
Project 1: Simple API Service
Demonstrates the Lean Hub architecture with versioned shared libraries
"""


from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
import sys
import os

# Add shared_libs to path for import
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from shared_libs.utils import JSONLogger, get_lib_info, format_response, generate_correlation_id, extract_trace_id_from_header, setup_tracing, instrument_fastapi

app = FastAPI(title="Project 1 API", version="1.0.0")

# Initialize logger with project ID
project_id = os.getenv('GCP_PROJECT_ID', 'local-dev')
logger = JSONLogger("project_1", project_id=project_id)

# Initialize OpenTelemetry tracing
setup_tracing("project-1")
instrument_fastapi(app)

@app.middleware("http")
async def add_trace_context(request: Request, call_next):
    """
    Middleware to extract and propagate trace context.
    Sets correlation ID for request tracing across services.
    """
    # Extract trace from Cloud Run header
    trace_header = request.headers.get('X-Cloud-Trace-Context', '')
    if trace_header:
        os.environ['HTTP_X_CLOUD_TRACE_CONTEXT'] = trace_header
    
    # Generate correlation ID for this request
    correlation_id = request.headers.get('X-Correlation-ID', generate_correlation_id())
    request.state.correlation_id = correlation_id
    
    response = await call_next(request)
    
    # Add correlation ID to response headers for tracing
    response.headers['X-Correlation-ID'] = correlation_id
    
    return response

@app.on_event("startup")
async def startup_event():
    lib_info = get_lib_info()
    logger.info(
        "Project 1 API starting up",
        lib_version=lib_info["version"],
        project_id=project_id
    )

@app.get("/")
async def root(request: Request):
    """Root endpoint with version information"""
    lib_info = get_lib_info()
    correlation_id = getattr(request.state, 'correlation_id', None)
    
    logger.info(
        "Hello from Project 1",
        correlation_id=correlation_id,
        request="root",
        lib_version=lib_info["version"]
    )
    
    return JSONResponse(
        content=format_response(
            data={
                "service": "Project 1",
                "message": "Hello from Project 1!",
                "shared_lib_version": lib_info["version"],
                "service_version": "1.0.0",
                "correlation_id": correlation_id
            },
            message="Project 1 API is running"
        )
    )

@app.get("/health")
async def health(request: Request):
    """Health check endpoint"""
    correlation_id = getattr(request.state, 'correlation_id', None)
    return JSONResponse(
        content=format_response(
            data={
                "status": "healthy",
                "correlation_id": correlation_id
            },
            message="Service is operational"
        )
    )

@app.get("/version")
async def version(request: Request):
    """Version information endpoint"""
    lib_info = get_lib_info()
    correlation_id = getattr(request.state, 'correlation_id', None)
    return JSONResponse(
        content=format_response(
            data={
                "service_version": "1.0.0",
                "shared_lib_info": lib_info,
                "correlation_id": correlation_id
            }
        )
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)
