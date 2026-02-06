# Observability and Monitoring

Complete observability setup for the Lean Hub with JSON-structured logging, distributed tracing, and centralized monitoring dashboard.

## Architecture

```
┌─────────────────────────────────────────────┐
│  All Services (Projects 1, 2, 3)           │
│  • JSON-structured logs                     │
│  • Correlation IDs                          │
│  • Cloud Trace integration                  │
│  • Custom metrics (optional)                │
└──────────────┬──────────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────────┐
│  Google Cloud Logging                       │
│  • Centralized log aggregation              │
│  • Searchable by correlation_id             │
│  • Trace linkage                            │
└──────────────┬──────────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────────┐
│  Google Cloud Monitoring                    │
│  • Centralized Hub dashboard                │
│  • Request metrics                          │
│  • Resource utilization                     │
│  • Alert policies                           │
└─────────────────────────────────────────────┘
```

## Features

### ✅ JSON-Structured Logging
All services use `shared_libs.utils.JSONLogger` for consistent log format:

```json
{
  "timestamp": "2026-02-06T10:30:45.123Z",
  "severity": "INFO",
  "service": "project_1",
  "message": "Processing request",
  "correlation_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "trace": "projects/my-project/traces/abc123...",
  "user_id": "user_123",
  "request_size": 1024
}
```

### ✅ Distributed Tracing
Requests are tracked across services using:
- **X-Correlation-ID**: Generated UUID for request tracking
- **X-Cloud-Trace-Context**: Google Cloud Trace format (TRACE_ID/SPAN_ID)

```
Client → API Gateway → Project 1 → Project 2
   ↓         ↓            ↓           ↓
 uuid-1    uuid-1      uuid-1      uuid-1  (same correlation_id)
```

### ✅ Cloud Monitoring Integration
Optional metrics collection for centralized dashboard:
- Request count per service
- Response time (latency)
- Error count and rate
- Service health status
- CPU/Memory utilization
- Instance count

## Quick Start

### 1. Using Basic Logging (No Extra Dependencies)

Already configured! All services emit JSON logs to Cloud Logging automatically.

```python
from shared_libs.utils import JSONLogger

logger = JSONLogger("my_service")
logger.info("Processing request", correlation_id=correlation_id, user_id=user_id)
```

### 2. Adding Cloud Monitoring (Optional)

Install monitoring packages:

```bash
pip install google-cloud-monitoring google-cloud-logging google-cloud-trace
```

Update your service code:

```python
from shared_libs.utils import CloudMonitoringClient, monitor_request

# Initialize monitoring
monitoring = CloudMonitoringClient("my_service", project_id="my-project")

# Option A: Manual recording
monitoring.record_request(
    endpoint="/api/query",
    method="POST",
    status_code=200,
    duration_ms=125.5
)

# Option B: Automatic with decorator
@app.get("/api/data")
@monitor_request(monitoring)
async def get_data(request: Request):
    return {"data": "response"}
```

### 3. Deploy Monitoring Dashboard

```bash
cd infrastructure
chmod +x deploy-monitoring.sh
./deploy-monitoring.sh
```

Or manually via Cloud Console:
```
https://console.cloud.google.com/monitoring/dashboards/create
```

Import [dashboard-config.json](../infrastructure/dashboard-config.json)

## How Correlation IDs Work

### Request Flow
```
1. Client Request
   │
   ├─> X-Correlation-ID: (optional, or generated)
   │   X-Cloud-Trace-Context: TRACE_ID/SPAN_ID
   │
2. API Gateway
   │
   ├─> Validates Firebase token
   ├─> Forwards correlation ID
   │
3. Service (e.g., Project 1)
   │
   ├─> Middleware extracts/generates correlation_id
   ├─> Adds to request.state.correlation_id
   ├─> Logs include correlation_id
   ├─> Response headers include X-Correlation-ID
   │
4. Service calls Service (e.g., Project 1 → Project 2)
   │
   ├─> Forward X-Correlation-ID header
   ├─> Forward X-Cloud-Trace-Context header
   │
5. All logs linked by same correlation_id!
```

### Code Implementation

Every service has this middleware (in [project_1/main.py](../project_1/main.py), etc.):

```python
@app.middleware("http")
async def add_trace_context(request: Request, call_next):
    # Extract or generate correlation ID
    correlation_id = request.headers.get("X-Correlation-ID") or generate_correlation_id()
    
    # Extract Cloud Trace context
    trace_header = request.headers.get("X-Cloud-Trace-Context")
    trace_id = extract_trace_id_from_header(trace_header) if trace_header else None
    
    # Store in request state
    request.state.correlation_id = correlation_id
    request.state.trace_id = trace_id
    
    # Log incoming request
    logger.info(
        f"Incoming request: {request.method} {request.url.path}",
        correlation_id=correlation_id,
        trace_id=trace_id
    )
    
    response = await call_next(request)
    
    # Add to response headers
    response.headers["X-Correlation-ID"] = correlation_id
    
    return response
```

## Querying Logs

### Find All Logs for a Request
```
resource.type="cloud_run_revision"
jsonPayload.correlation_id="a1b2c3d4-e5f6-7890-abcd-ef1234567890"
```

### Find Errors in Last Hour
```
resource.type="cloud_run_revision"
jsonPayload.severity="ERROR"
timestamp>="2026-02-06T10:00:00Z"
```

### Trace Across Services
```
resource.type="cloud_run_revision"
trace="projects/PROJECT_ID/traces/TRACE_ID"
```

### Service-Specific Logs
```
resource.type="cloud_run_revision"
resource.labels.service_name="project-1"
```

## Dashboard Metrics

The centralized Hub dashboard shows:

| Widget | Metric | Description |
|--------|--------|-------------|
| Service Health | health_status | Green/Yellow/Red status per service |
| Requests/min | request_count | Total requests across all services |
| Response Time | request_latencies | P50/P95/P99 latency |
| CPU % | container/cpu/utilizations | CPU usage per service |
| Memory % | container/memory/utilizations | Memory usage per service |
| Active Instances | instance_count | Number of running containers |
| Billable Time | billable_instance_time | Cost tracking |
| Recent Logs | correlation_id logs | Latest requests with trace IDs |

## Alert Policies

Three alert policies are configured:

1. **High Error Rate** (> 5 errors/min for 5 minutes)
2. **Service Down** (health check fails for 3 minutes)
3. **High Response Time** (> 2 seconds avg for 5 minutes)

Alerts are sent via notification channels (email, PagerDuty, etc.)

## Cost Optimization

### Logging Costs
- **Free tier**: 50 GB/month
- **Beyond free**: $0.50/GB
- **Strategy**: 30-day retention, exclude health check logs

### Monitoring Costs
- **Free tier**: 150 MB/month metrics
- **Custom metrics**: $0.258/MB (only if you install google-cloud-monitoring)
- **Strategy**: Use built-in Cloud Run metrics, add custom metrics only if needed

### Optimization Tips
1. **Use JSON logs without Cloud Monitoring packages** for zero extra cost
2. Sample high-volume endpoints (log 1 in 10 requests)
3. Set appropriate log retention (30 days default)
4. Exclude noisy logs with exclusion filters

## Shared Library Versioning Tracking

Each service logs its `shared_lib_version` on startup:

```json
{
  "severity": "INFO",
  "message": "Project 1 API starting up",
  "shared_lib_version": "v1.0.0",
  "service": "project_1"
}
```

Query to see current versions:

```
resource.type="cloud_run_revision"
jsonPayload.shared_lib_version!=""
```

This enables **surgical update verification** - you can confirm that updating shared_libs to v2.0.0 only affects services you rebuilt, while others remain on v1.0.0.

## Examples

### Example 1: Track a Single Request

```bash
# 1. Make a request and capture correlation ID
CORRELATION_ID=$(curl -H "Authorization: Bearer $TOKEN" \
  https://api.example.com/api/data \
  -I | grep X-Correlation-ID | awk '{print $2}')

# 2. Query logs for that request across all services
gcloud logging read \
  "resource.type=\"cloud_run_revision\" AND jsonPayload.correlation_id=\"$CORRELATION_ID\"" \
  --project=$GCP_PROJECT_ID
```

### Example 2: Monitor Error Rate

```python
# services automatically log errors with correlation IDs
try:
    result = process_request(data)
except Exception as e:
    logger.error(
        f"Request processing failed: {str(e)}",
        correlation_id=correlation_id,
        error_type=type(e).__name__
    )
    raise
```

Query errors:
```
resource.type="cloud_run_revision"
jsonPayload.severity="ERROR"
```

### Example 3: Health Checks

```python
from shared_libs.utils import CloudMonitoringClient

monitoring = CloudMonitoringClient("my_service")

@app.get("/health")
async def health():
    try:
        # Check dependencies
        db_healthy = await check_database()
        cache_healthy = await check_cache()
        
        healthy = db_healthy and cache_healthy
        
        monitoring.record_health_check(
            healthy=healthy,
            details={
                "database": db_healthy,
                "cache": cache_healthy
            }
        )
        
        return {"status": "healthy" if healthy else "degraded"}
    except Exception as e:
        monitoring.record_health_check(healthy=False, details={"error": str(e)})
        raise
```

## Troubleshooting

### Logs Not Appearing
✅ Cloud Run automatically sends logs to Cloud Logging  
✅ Check service has proper permissions  
✅ Verify `GCP_PROJECT_ID` environment variable is set

### Correlation IDs Not Linking
✅ Ensure middleware is installed in all services  
✅ Verify `X-Correlation-ID` header is forwarded between services  
✅ Check correlation_id is extracted from request.state

### Dashboard Empty
✅ Generate traffic to services first  
✅ Wait 5-10 minutes for metrics to populate  
✅ Check time range selector in dashboard

### Metrics Not Appearing
✅ Install google-cloud-monitoring package (optional)  
✅ Verify service account has `monitoring.metricWriter` role  
✅ Check metrics are being emitted in logs

## Related Documentation

- [shared_libs/utils.py](../shared_libs/utils.py) - Logging & monitoring utilities
- [infrastructure/MONITORING_SETUP.md](../infrastructure/MONITORING_SETUP.md) - Detailed setup guide
- [SECRETS_MANAGEMENT.md](../SECRETS_MANAGEMENT.md) - GCP credentials
- [Cloud Monitoring Docs](https://cloud.google.com/monitoring/docs)
- [Cloud Trace Docs](https://cloud.google.com/trace/docs)

---

**Key Benefits:**
- ✅ **Zero-config logging**: JSON logs work out of the box
- ✅ **Distributed tracing**: Track requests across services
- ✅ **Cost-efficient**: Use free tier, add paid features only if needed
- ✅ **Surgical updates**: Track which services use which shared_libs version
- ✅ **Centralized**: Single dashboard for all services
- ✅ **Scalable**: Scales with Cloud Run auto-scaling
