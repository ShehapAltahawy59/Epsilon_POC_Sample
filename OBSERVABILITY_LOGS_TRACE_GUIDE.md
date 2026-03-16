# Google Cloud Logs, Trace, and Correlation Guide

This guide explains how to debug requests end-to-end in Google Cloud using logs, traces, and correlation IDs.

It is based on:

- `test_api_gateway.py` for endpoint testing through API Gateway
- `shared_libs/utils.py` for structured logging and trace fields
- service middleware pattern in `project_1/main.py` (same across all projects)

## How It Works

Every incoming request is automatically assigned a `correlation_id` by the service middleware.  
Developers do **not** need to pass it manually — it is injected into every log automatically.

Flow per request:
1. Middleware generates `correlation_id` (or reads from `X-Correlation-ID` header)
2. `set_correlation_id()` stores it in a per-request `ContextVar`
3. Every `logger.info()` / `logger.error()` call reads it automatically
4. Response body includes `correlation_id` for client-side lookup

## What Is in Every Log Entry

All services emit structured JSON logs to stdout with these fields:

```json
{
  "timestamp": "2026-03-16T18:03:46.416992Z",
  "severity": "INFO",
  "message": "Incoming request: GET /",
  "service": "project_1",
  "correlation_id": "fe35155f-7bd5-4e27-a945-a268aee8fa77",
  "trace": "projects/my-lean-hub-project/traces/6db458e12a9ea03ecdfc13e468f14ae8",
  "trace_id": "6db458e12a9ea03ecdfc13e468f14ae8",
  "span_id": "4464115068629571334",
  "method": "GET",
  "path": "/"
}
```

Each request produces at minimum **2 log entries**:
- Middleware log: `Incoming request: <METHOD> <PATH>`
- Route handler log: e.g. `Hello from Project 1`, `Health check`, `Version check`

## End-to-End Debug Workflow

1. Run tests through the gateway
2. Copy a `correlation_id` from any response body
3. Search Cloud Logging with that ID
4. Jump from logs to Cloud Trace for latency analysis

## 1) Run Gateway Tests

From repo root (PowerShell):

```powershell
$env:PYTHONIOENCODING="utf-8"; python .\test_api_gateway.py
```

Every successful response includes `correlation_id` in the `data` field:

```json
{
  "success": true,
  "data": {
    "correlation_id": "fe35155f-7bd5-4e27-a945-a268aee8fa77"
  }
}
```

## 2) Find Request in Cloud Logging

Open **Google Cloud Console → Logging → Logs Explorer**.

Search by correlation ID (works for all services):

```text
resource.type="cloud_run_revision"
jsonPayload.correlation_id="fe35155f-7bd5-4e27-a945-a268aee8fa77"
```

Filter by specific service:

```text
resource.type="cloud_run_revision"
resource.labels.service_name="project-1"
jsonPayload.correlation_id="fe35155f-7bd5-4e27-a945-a268aee8fa77"
```

Filter by severity:

```text
resource.type="cloud_run_revision"
jsonPayload.severity="ERROR"
jsonPayload.correlation_id="fe35155f-7bd5-4e27-a945-a268aee8fa77"
```

> Note: logs now go to `run.googleapis.com/stderr` as structured JSON.  
> `textPayload` fallback is no longer needed.

## 3) Jump from Logs to Trace

In matching log entries, look for:

- `jsonPayload.trace` → `projects/<project-id>/traces/<trace-id>`

Click the trace link in Cloud Logging log details, or open **Cloud Trace Explorer** and paste the `trace_id`.

## 4) Correlation ID vs Trace ID

- **Correlation ID**
  - App-level identifier generated per request by service middleware
  - Automatically included in all `logger` calls via `ContextVar`
  - Returned in response body and `X-Correlation-ID` response header
  - Use to find all logs for a specific request across services

- **Trace ID**
  - Infrastructure-level identifier from Google Cloud Trace / OpenTelemetry
  - Set by `X-Cloud-Trace-Context` header from API Gateway
  - Use for latency analysis, span visualization, and dependency maps

Use both together:
- Start with `correlation_id` from client response → find logs
- Follow `trace` from logs → open Cloud Trace for timeline

## 5) Send Your Own Correlation ID

When calling a route manually, send a custom ID so you can find the exact request:

```powershell
curl -i "https://lean-hub-gateway-6bbg4rzf.uc.gateway.dev/p4/version" `
  -H "Authorization: Bearer <FIREBASE_ID_TOKEN>" `
  -H "X-Correlation-ID: my-debug-session-001"
```

Then search:

```text
resource.type="cloud_run_revision"
jsonPayload.correlation_id="my-debug-session-001"
```

## 6) Adding Logging to a New Route

Middleware handles `correlation_id` automatically. In a new route, just call the logger:

```python
@app.get("/my-route")
async def my_route():
    logger.info("Processing my-route", extra_field="value")
    # correlation_id is automatically included in the log
```

To include `correlation_id` in the response body (recommended):

```python
from shared_libs.utils import get_correlation_id

@app.get("/my-route")
async def my_route():
    logger.info("Processing my-route")
    return JSONResponse(content=format_response(
        data={
            "result": "...",
            "correlation_id": get_correlation_id()
        }
    ))
```

## 7) Interpreting Common Test Outcomes

- `200` — route exists and backend handled the request; use `correlation_id` to inspect logs
- `422` — route exists but request body is missing required fields (expected for POST routes tested with empty body)
- `404 {"detail":"Not Found"}` — backend route decorator is missing or wrong path; check service `@app.get(...)` decorators
- `401` — Firebase token missing or invalid; check token generation in test script
- `403` on downstream call — service-to-service IAM permission missing on Cloud Run

## 8) Team Best Practices

- Always call `logger.info()` / `logger.error()` inside every route — correlation_id is auto-included
- Never pass `correlation_id` manually to logger — the ContextVar handles it
- Keep `correlation_id` in all response bodies so clients and testers can search logs
- Ensure every new service calls `setup_tracing()` and `instrument_fastapi()` at startup
- Keep `SERVICE_CODE` and `SERVICE_SLUG` constants accurate per service

## Quick Checklist

- [ ] Tests ran through gateway (`test_api_gateway.py`)
- [ ] Copied `correlation_id` from response body
- [ ] Found matching logs in Cloud Logging with `jsonPayload.correlation_id="..."`
- [ ] Followed `trace` link to Cloud Trace timeline
- [ ] Verified all services logged the request with same correlation ID
