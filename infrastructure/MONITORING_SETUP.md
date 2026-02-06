# Cloud Monitoring Setup Guide

Complete guide for setting up centralized Cloud Monitoring dashboard for the Lean Hub.

## Overview

The Lean Hub uses a comprehensive monitoring strategy:

```
┌─────────────────────────────────────────────────────┐
│  Services (Project 1, 2, 3)                         │
│  - JSON structured logs with trace IDs              │
│  - Custom metrics (requests, errors, health)        │
└───────────────┬─────────────────────────────────────┘
                │
                ▼
┌─────────────────────────────────────────────────────┐
│  Google Cloud Logging                               │
│  - Correlation IDs for distributed tracing          │
│  - Cloud Trace integration                          │
└───────────────┬─────────────────────────────────────┘
                │
                ▼
┌─────────────────────────────────────────────────────┐
│  Google Cloud Monitoring                            │
│  - Custom metrics dashboard                         │
│  - Alert policies                                   │
│  - Service health tracking                          │
└───────────────┬─────────────────────────────────────┘
                │
                ▼
┌─────────────────────────────────────────────────────┐
│  Centralized Hub Dashboard                          │
│  - Real-time service health                         │
│  - Request rates and latency                        │
│  - Error tracking                                   │
│  - Resource utilization                             │
│  - Shared library versions                          │
└─────────────────────────────────────────────────────┘
```

## Features

### 1. JSON-Structured Logging
✅ All services use `shared_libs.utils.JSONLogger`
✅ Consistent log format across services
✅ Automatic correlation ID generation
✅ Cloud Trace integration

### 2. Distributed Tracing
✅ Correlation IDs propagated via `X-Correlation-ID` header
✅ Cloud Trace integration via `X-Cloud-Trace-Context`
✅ Request tracing across multiple services
✅ Automatic trace ID extraction

### 3. Custom Metrics
✅ Request count per service
✅ Request duration (ms)
✅ Error count and rate
✅ Service health status
✅ Success/failure rates

### 4. Built-in Metrics (Cloud Run)
✅ CPU utilization
✅ Memory utilization
✅ Instance count
✅ Cold start metrics
✅ Billable container time

## Setup Instructions

### 1. Enable Required APIs

```bash
gcloud services enable \
    monitoring.googleapis.com \
    logging.googleapis.com \
    cloudtrace.googleapis.com \
    --project=$GCP_PROJECT_ID
```

### 2. Install Python Dependencies

```bash
# Add to requirements.txt for services that need monitoring
google-cloud-monitoring>=2.15.0
google-cloud-logging>=3.5.0
google-cloud-trace>=1.11.0
```

### 3. Deploy Monitoring Dashboard

#### Option A: Using Terraform

```bash
cd infrastructure

# Initialize Terraform
terraform init

# Create dashboard
terraform apply -target=google_monitoring_dashboard.lean_hub_dashboard

# Create alert policies
terraform apply -target=google_monitoring_alert_policy.high_error_rate
terraform apply -target=google_monitoring_alert_policy.service_down
terraform apply -target=google_monitoring_alert_policy.high_response_time
```

#### Option B: Using gcloud CLI

```bash
# Create dashboard from JSON
gcloud monitoring dashboards create --config-from-file=infrastructure/dashboard-config.json

# Or use the Cloud Console
# https://console.cloud.google.com/monitoring/dashboards
```

### 4. Configure Notification Channels

```bash
# Create email notification channel
gcloud alpha monitoring channels create \
    --display-name="Lean Hub Alerts" \
    --type=email \
    --channel-labels=email_address=your-email@example.com

# List channels to get ID
gcloud alpha monitoring channels list

# Update Terraform with channel ID
# infrastructure/monitoring-dashboard.tf
# variable "notification_channels" = ["projects/PROJECT_ID/notificationChannels/CHANNEL_ID"]
```

## Dashboard Metrics

### Service Health Overview
- **Green**: All services healthy
- **Yellow**: Degraded performance
- **Red**: Service down or critical errors

### Request Metrics
- **Requests/min**: Total requests across all services
- **Average Response Time**: P50/P95/P99 latencies
- **Success Rate**: Percentage of successful requests (2xx status)
- **Error Rate**: Number of 5xx errors per minute

### Resource Utilization
- **CPU %**: Container CPU usage
- **Memory %**: Container memory usage
- **Instances**: Active container instances

### Service-Specific
- **Project 1**: Standard API metrics
- **Project 2 (RAG)**: GPU metrics, query latency
- **Project 3**: Standard API metrics

### Versioning
- **Shared Library Versions**: Shows which version each service is using
- **Surgical Update Tracking**: Visualize independent version deployments

## Using Monitoring in Code

### Basic Logging with Trace

```python
from shared_libs.utils import JSONLogger

# Initialize logger
logger = JSONLogger("my_service", project_id="my-project")

# Log with correlation ID
logger.info(
    "Processing request",
    correlation_id=correlation_id,
    user_id=user_id,
    request_size=len(data)
)
```

### Recording Custom Metrics

```python
from shared_libs.utils import CloudMonitoringClient

# Initialize monitoring client
monitoring = CloudMonitoringClient("my_service", project_id="my-project")

# Record request
monitoring.record_request(
    endpoint="/api/query",
    method="POST",
    status_code=200,
    duration_ms=125.5
)

# Record error
monitoring.record_error(
    error_type="ValidationError",
    error_message="Invalid input format"
)

# Record health check
monitoring.record_health_check(
    healthy=True,
    details={"db_connected": True, "cache_available": True}
)

# Flush metrics (or done automatically)
monitoring.flush_metrics()
```

### Decorator for Automatic Monitoring

```python
from shared_libs.utils import monitor_request

monitoring = CloudMonitoringClient("my_service")

@app.get("/api/data")
@monitor_request(monitoring)
async def get_data(request: Request):
    # Automatically tracked:
    # - Request duration
    # - Status code
    # - Errors
    return {"data": "response"}
```

## Accessing the Dashboard

### Cloud Console
```
https://console.cloud.google.com/monitoring/dashboards
→ Select "Lean Hub - Centralized Dashboard"
```

### Direct Link
```
https://console.cloud.google.com/monitoring/dashboards/custom/DASHBOARD_ID?project=PROJECT_ID
```

## Correlation ID Flow

```
Client Request
    │
    ├─> X-Correlation-ID: uuid-1234
    │   X-Cloud-Trace-Context: trace-id/span-id
    │
    ▼
API Gateway
    │
    ├─> Validates token
    ├─> Preserves correlation ID
    │
    ▼
Project 1
    │
    ├─> Extracts correlation ID
    ├─> Logs with trace context
    ├─> Records metrics
    │
    └─> Calls Project 2
        │
        ├─> Forwards correlation ID
        ├─> Logs with same trace context
        └─> Records metrics

All logs/metrics linked by correlation_id!
```

## Querying Logs

### Find All Logs for a Request
```
resource.type="cloud_run_revision"
jsonPayload.correlation_id="uuid-1234"
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

## Alert Policies

### High Error Rate (> 5% of requests)
- **Condition**: Error count > 5 per minute
- **Duration**: 5 minutes
- **Action**: Email notification

### Service Down
- **Condition**: Health check fails
- **Duration**: 3 minutes
- **Action**: Email + PagerDuty (if configured)

### High Response Time (> 2 seconds)
- **Condition**: Average latency > 2000ms
- **Duration**: 5 minutes
- **Action**: Email notification

## Cost Optimization

### Logging Costs
- **Free tier**: 50 GB/month
- **Beyond free**: $0.50/GB
- **Retention**: 30 days (configurable in .env)

### Monitoring Costs
- **Free tier**: 150 MB/month metrics
- **Custom metrics**: $0.258/MB
- **Queries**: Free up to API limits

### Optimization Tips
1. Use sampling for high-volume endpoints
2. Aggregate metrics before sending
3. Set appropriate log retention
4. Use log exclusion filters for noise

## Maintenance

### Update Dashboard
```bash
# Edit infrastructure/monitoring-dashboard.tf
# Then apply changes
terraform apply -target=google_monitoring_dashboard.lean_hub_dashboard
```

### Add New Metric
```python
# In shared_libs/utils.py
def record_custom_metric(self, metric_name: str, value: float):
    metric_data = {
        "metric_type": f"custom.googleapis.com/lean_hub/{metric_name}",
        "value": value,
        ...
    }
    self.metrics_buffer.append(metric_data)
```

### Export Data
```bash
# Export logs to BigQuery for analysis
gcloud logging sinks create lean-hub-logs \
    bigquery.googleapis.com/projects/PROJECT_ID/datasets/lean_hub_logs \
    --log-filter='resource.type="cloud_run_revision"'
```

## Troubleshooting

### Metrics Not Appearing
1. Check service account has `monitoring.metricWriter` role
2. Verify metrics are being emitted (check logs)
3. Allow 2-3 minutes for metric propagation

### Correlation IDs Not Linking
1. Verify `X-Correlation-ID` header is forwarded
2. Check trace context middleware is installed
3. Ensure correlation ID is in log output

### Dashboard Empty
1. Generate some traffic to services
2. Wait 5-10 minutes for data to appear
3. Check time range selector in dashboard

## Related Documentation

- [shared_libs/utils.py](../shared_libs/utils.py) - Logging & monitoring utilities
- [SECRETS_MANAGEMENT.md](../SECRETS_MANAGEMENT.md) - GCP credentials setup
- [Cloud Monitoring Docs](https://cloud.google.com/monitoring/docs)
- [Cloud Trace Docs](https://cloud.google.com/trace/docs)

---

**Key Takeaways:**
- ✅ JSON-structured logging with correlation IDs
- ✅ Cloud Trace integration for distributed tracing
- ✅ Centralized dashboard for all services
- ✅ Custom and built-in metrics
- ✅ Automated alerting on critical issues
- ✅ Surgical update tracking via version logs
