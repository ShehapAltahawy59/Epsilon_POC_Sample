"""
Project Template: FastAPI Service
Copy this folder to a new project directory (for example: project_5)
and update the service constants below.
"""

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
import sys
import os

# Add shared_libs to path for import
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from shared_libs.utils import (
    JSONLogger,
    get_lib_info,
    format_response,
    generate_correlation_id,
    extract_trace_id_from_header,
    setup_tracing,
    instrument_fastapi,
)

# TODO: Update these two constants after copying this template.
SERVICE_CODE = "project_template"   # Example: project_5
SERVICE_SLUG = "project-template"   # Example: project-5

app = FastAPI(title="Project Template API", version="1.0.0")

project_id = os.getenv("GCP_PROJECT_ID", "local-dev")
logger = JSONLogger(SERVICE_CODE, project_id=project_id)

setup_tracing(SERVICE_SLUG)
instrument_fastapi(app)


@app.middleware("http")
async def add_trace_context(request: Request, call_next):
    trace_header = request.headers.get("X-Cloud-Trace-Context", "")
    if trace_header:
        os.environ["HTTP_X_CLOUD_TRACE_CONTEXT"] = trace_header

    correlation_id = request.headers.get("X-Correlation-ID", generate_correlation_id())
    request.state.correlation_id = correlation_id
    request.state.trace_id = extract_trace_id_from_header(trace_header) if trace_header else None

    response = await call_next(request)
    response.headers["X-Correlation-ID"] = correlation_id
    if trace_header:
        response.headers["X-Cloud-Trace-Context"] = trace_header
    return response


@app.on_event("startup")
async def startup_event():
    lib_info = get_lib_info()
    logger.info(
        "Template service starting up",
        lib_version=lib_info["version"],
        project_id=project_id,
    )


@app.get("/")
async def root(request: Request):
    lib_info = get_lib_info()
    correlation_id = getattr(request.state, "correlation_id", None)
    return JSONResponse(
        content=format_response(
            data={
                "service": SERVICE_CODE,
                "message": "Hello from template-based service!",
                "shared_lib_version": lib_info["version"],
                "service_version": "1.0.0",
                "correlation_id": correlation_id,
            },
            message="Service is running",
        )
    )


@app.get("/health")
async def health(request: Request):
    correlation_id = getattr(request.state, "correlation_id", None)
    return JSONResponse(
        content=format_response(
            data={
                "status": "healthy",
                "correlation_id": correlation_id,
            },
            message="Service is operational",
        )
    )


@app.get("/version")
async def version(request: Request):
    lib_info = get_lib_info()
    correlation_id = getattr(request.state, "correlation_id", None)
    return JSONResponse(
        content=format_response(
            data={
                "service_version": "1.0.0",
                "shared_lib_info": lib_info,
                "correlation_id": correlation_id,
            }
        )
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)
