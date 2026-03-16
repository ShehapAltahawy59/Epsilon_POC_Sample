# Google Cloud Logs, Trace, and Correlation Guide

This guide explains how to use your current gateway tests to debug requests end-to-end in Google Cloud.

It is based on:

- `test_api_gateway.py` for endpoint testing through API Gateway
- `shared_libs/utils.py` for structured logging and trace fields
- service middleware pattern in `project_4/main.py`

## What You Already Have

- API Gateway test calls all registered routes in `infrastructure/gateway/services-registry.json`
- Service responses include a `correlation_id` in many endpoints
- Services emit JSON logs with:
  - `service`
  - `correlation_id`
  - `trace` (formatted as `projects/<project-id>/traces/<trace-id>`) when available
  - `trace_id` and `span_id` when available
- FastAPI auto-instrumentation is enabled via OpenTelemetry (`setup_tracing`, `instrument_fastapi`)

## End-to-End Workflow

1. Run tests through the gateway.
2. Pick one successful request (for example `GET /p4/version`).
3. Copy its `correlation_id` from the response body.
4. Search logs in Cloud Logging using that correlation ID.
5. Open the related trace in Cloud Trace (from `trace` field).
6. Confirm cross-service flow and latency.

## 1) Run Gateway Tests

From repo root (PowerShell):

```powershell
python .\test_api_gateway.py
```

When a route succeeds, the script prints JSON response bodies. For endpoints that include it, copy:

- `data.correlation_id`

Example from your output shape:

```json
{
  "success": true,
  "data": {
    "correlation_id": "bb240454-5eb5-46cb-803e-2ce12ab35e16"
  }
}
```

## 2) Find Request in Cloud Logging

Open **Google Cloud Console -> Logging -> Logs Explorer**.

Use a query like:

```text
resource.type="cloud_run_revision"
jsonPayload.correlation_id="bb240454-5eb5-46cb-803e-2ce12ab35e16"
```

If logs are not parsed into `jsonPayload`, try:

```text
resource.type="cloud_run_revision"
textPayload:"bb240454-5eb5-46cb-803e-2ce12ab35e16"
```

Optional filters:

```text
resource.labels.service_name="project-4"
jsonPayload.severity="INFO"
```

## 3) Jump from Logs to Trace

In matching log entries, inspect:

- `jsonPayload.trace` (or `trace` field in log details)

This points to:

- `projects/<your-project-id>/traces/<trace-id>`

Open the trace link directly from log details, or open **Trace Explorer** and search by trace ID.

## 4) What Correlation ID vs Trace ID Means

- **Correlation ID**
  - App-level request identifier
  - Generated in middleware if `X-Correlation-ID` is missing
  - Returned to clients (`X-Correlation-ID` response header and/or response JSON)
  - Best for support/debug workflows across logs and API responses

- **Trace ID**
  - Infrastructure/distributed tracing identifier (Google Cloud Trace)
  - Comes from `X-Cloud-Trace-Context`
  - Best for latency analysis, spans, and dependency visualization

Use both together:

- Start with `correlation_id` from client response
- Find service logs
- Follow `trace` to distributed trace timeline

## 5) Send Your Own Correlation ID (Recommended)

When calling a route manually, send your own ID:

```powershell
curl -i "https://lean-hub-gateway-6bbg4rzf.uc.gateway.dev/p4/version" `
  -H "Authorization: Bearer <FIREBASE_ID_TOKEN>" `
  -H "X-Correlation-ID: demo-corr-12345"
```

Then search logs:

```text
jsonPayload.correlation_id="demo-corr-12345"
```

This makes troubleshooting much faster for specific user sessions.

## 6) Interpreting Common Test Outcomes

- `200` with response body:
  - Route exists and backend handled request
  - Use `correlation_id` to inspect full request path in logs

- `404 {"detail":"Not Found"}`:
  - Usually backend route is missing/not registered, or gateway path not mapped correctly
  - Verify both `services-registry.json` and service decorators

- `401`:
  - Auth token missing/invalid for protected endpoint
  - Validate Firebase token generation in test script

## 7) Team Best Practices

- Keep `correlation_id` in all service responses for debug endpoints (`/health`, `/version`, `/status`)
- Log `correlation_id` on every important event (startup, request start/end, errors, downstream calls)
- Ensure every service initializes tracing (`setup_tracing`) and instrumentation (`instrument_fastapi`)
- Keep service names stable (`service.name`) so traces are readable across deployments

## Quick Checklist

- [ ] Test ran through gateway (`test_api_gateway.py`)
- [ ] Copied `correlation_id` from response
- [ ] Found matching Cloud Run logs
- [ ] Opened related trace in Cloud Trace
- [ ] Verified service path and latency spans

