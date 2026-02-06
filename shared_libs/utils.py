"""
Unified Observability and Utility Functions
Provides JSON-structured logging with Cloud Trace integration, 
Cloud Monitoring metrics, and versioning for the Lean Hub
"""


import json
import logging
import os
import uuid
from datetime import datetime
from typing import Any, Dict, Optional
from functools import wraps
import time


class JSONLogger:
    """
    JSON-structured logger for unified observability across all services.
    Ensures consistent log formatting with Cloud Trace correlation IDs.
    
    Features:
    - Automatic trace ID extraction from Cloud Run headers
    - Correlation ID generation and propagation
    - Google Cloud Trace integration
    - Structured logging for easy parsing
    """
    
    def __init__(self, service_name: str, project_id: Optional[str] = None):
        self.service_name = service_name
        self.project_id = project_id or os.getenv('GCP_PROJECT_ID', 'unknown')
        self.logger = logging.getLogger(service_name)
        self.logger.setLevel(logging.INFO)
        
        # Create console handler with JSON formatting
        handler = logging.StreamHandler()
        handler.setLevel(logging.INFO)
        self.logger.addHandler(handler)
    
    def _get_trace_context(self) -> Dict[str, str]:
        """
        Extract trace context from Cloud Run environment.
        Cloud Run sets X-Cloud-Trace-Context header which is available as env var.
        Format: TRACE_ID/SPAN_ID;o=TRACE_TRUE
        """
        trace_context = {}
        
        # Try to get trace from environment (set by Cloud Run)
        cloud_trace_context = os.getenv('HTTP_X_CLOUD_TRACE_CONTEXT', '')
        
        if cloud_trace_context:
            # Parse trace context: "TRACE_ID/SPAN_ID;o=TRACE_TRUE"
            trace_parts = cloud_trace_context.split('/')
            if trace_parts:
                trace_id = trace_parts[0]
                # Format for Cloud Logging correlation
                trace_context['trace'] = f"projects/{self.project_id}/traces/{trace_id}"
                trace_context['trace_id'] = trace_id
                
                if len(trace_parts) > 1:
                    span_parts = trace_parts[1].split(';')
                    if span_parts:
                        trace_context['span_id'] = span_parts[0]
        
        return trace_context
    
    def _format_log(self, level: str, message: str, correlation_id: Optional[str] = None, **kwargs) -> str:
        """
        Format log entry as JSON with Cloud Trace correlation.
        
        Log format follows Google Cloud Logging structured log format:
        https://cloud.google.com/logging/docs/structured-logging
        """
        # Get trace context for correlation
        trace_context = self._get_trace_context()
        
        # Generate correlation ID if not provided
        if not correlation_id:
            correlation_id = kwargs.get('correlation_id') or str(uuid.uuid4())
        
        log_entry = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "severity": level,  # Cloud Logging uses 'severity' not 'level'
            "message": message,
            "service": self.service_name,
            "correlation_id": correlation_id,
            **trace_context,  # Add trace/span IDs for Cloud Trace correlation
            **kwargs
        }
        
        # Remove duplicate correlation_id from kwargs if present
        log_entry.pop('correlation_id', None)
        if 'correlation_id' in kwargs:
            log_entry['correlation_id'] = correlation_id
        
        return json.dumps(log_entry)
    
    def info(self, message: str, correlation_id: Optional[str] = None, **kwargs):
        """Log info level message with optional correlation ID"""
        self.logger.info(self._format_log("INFO", message, correlation_id, **kwargs))
    
    def error(self, message: str, correlation_id: Optional[str] = None, **kwargs):
        """Log error level message with optional correlation ID"""
        self.logger.error(self._format_log("ERROR", message, correlation_id, **kwargs))
    
    def warning(self, message: str, correlation_id: Optional[str] = None, **kwargs):
        """Log warning level message with optional correlation ID"""
        self.logger.warning(self._format_log("WARNING", message, correlation_id, **kwargs))
    
    def debug(self, message: str, correlation_id: Optional[str] = None, **kwargs):
        """Log debug level message with optional correlation ID"""
        self.logger.debug(self._format_log("DEBUG", message, correlation_id, **kwargs))


def generate_correlation_id() -> str:
    """
    Generate a unique correlation ID for request tracking.
    Used to trace requests across multiple services.
    """
    return str(uuid.uuid4())


def extract_trace_id_from_header(trace_header: str) -> Optional[str]:
    """
    Extract trace ID from X-Cloud-Trace-Context header.
    Format: TRACE_ID/SPAN_ID;o=TRACE_TRUE
    
    Args:
        trace_header: The X-Cloud-Trace-Context header value
        
    Returns:
        Trace ID or None if invalid format
    """
    if not trace_header:
        return None
    
    parts = trace_header.split('/')
    return parts[0] if parts else None


class CloudMonitoringClient:
    """
    Lightweight Cloud Monitoring client for metrics collection.
    Emits metrics to Google Cloud Monitoring for centralized dashboard.
    
    Metrics emitted:
    - Request count
    - Request duration
    - Error count
    - Service health
    """
    
    def __init__(self, service_name: str, project_id: Optional[str] = None):
        self.service_name = service_name
        self.project_id = project_id or os.getenv('GCP_PROJECT_ID', 'unknown')
        self.metrics_buffer = []
        
        # Try to import Cloud Monitoring (optional dependency)
        try:
            from google.cloud import monitoring_v3
            self.monitoring_client = monitoring_v3.MetricServiceClient()
            self.project_path = f"projects/{self.project_id}"
            self.enabled = True
        except ImportError:
            self.monitoring_client = None
            self.enabled = False
    
    def record_request(self, endpoint: str, method: str, status_code: int, duration_ms: float):
        """
        Record a request metric.
        
        Args:
            endpoint: API endpoint path
            method: HTTP method
            status_code: HTTP response status code
            duration_ms: Request duration in milliseconds
        """
        if not self.enabled:
            return
        
        metric_data = {
            "metric_type": "custom.googleapis.com/lean_hub/request_count",
            "timestamp": datetime.utcnow().isoformat(),
            "service": self.service_name,
            "endpoint": endpoint,
            "method": method,
            "status_code": status_code,
            "duration_ms": duration_ms,
            "success": 200 <= status_code < 300
        }
        
        self.metrics_buffer.append(metric_data)
        
        # Flush buffer if it gets too large (batch writes)
        if len(self.metrics_buffer) >= 10:
            self.flush_metrics()
    
    def record_error(self, error_type: str, error_message: str):
        """
        Record an error metric.
        
        Args:
            error_type: Type/category of error
            error_message: Error message
        """
        if not self.enabled:
            return
        
        metric_data = {
            "metric_type": "custom.googleapis.com/lean_hub/error_count",
            "timestamp": datetime.utcnow().isoformat(),
            "service": self.service_name,
            "error_type": error_type,
            "error_message": error_message
        }
        
        self.metrics_buffer.append(metric_data)
    
    def record_health_check(self, healthy: bool, details: Optional[Dict] = None):
        """
        Record service health status.
        
        Args:
            healthy: Whether service is healthy
            details: Optional health check details
        """
        if not self.enabled:
            return
        
        metric_data = {
            "metric_type": "custom.googleapis.com/lean_hub/health_status",
            "timestamp": datetime.utcnow().isoformat(),
            "service": self.service_name,
            "healthy": healthy,
            "details": details or {}
        }
        
        self.metrics_buffer.append(metric_data)
    
    def flush_metrics(self):
        """
        Flush buffered metrics to Cloud Monitoring.
        Called automatically when buffer is full or can be called manually.
        """
        if not self.enabled or not self.metrics_buffer:
            return
        
        try:
            # In production, this would write to Cloud Monitoring API
            # For now, we log the metrics in structured format
            for metric in self.metrics_buffer:
                print(json.dumps({"monitoring_metric": metric}))
            
            self.metrics_buffer.clear()
        except Exception as e:
            print(f"Error flushing metrics: {e}")


def monitor_request(monitoring_client: Optional[CloudMonitoringClient] = None):
    """
    Decorator to automatically monitor API requests.
    Records request duration, status, and errors.
    
    Usage:
        @monitor_request(monitoring_client)
        async def my_endpoint():
            return {"data": "response"}
    """
    def decorator(func):
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            start_time = time.time()
            status_code = 200
            
            try:
                response = await func(*args, **kwargs)
                
                # Try to extract status code from response
                if hasattr(response, 'status_code'):
                    status_code = response.status_code
                
                return response
            except Exception as e:
                status_code = 500
                if monitoring_client:
                    monitoring_client.record_error(
                        error_type=type(e).__name__,
                        error_message=str(e)
                    )
                raise
            finally:
                duration_ms = (time.time() - start_time) * 1000
                
                if monitoring_client:
                    # Extract endpoint info
                    endpoint = func.__name__
                    method = "GET"  # Default, can be overridden
                    
                    monitoring_client.record_request(
                        endpoint=endpoint,
                        method=method,
                        status_code=status_code,
                        duration_ms=duration_ms
                    )
        
        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            start_time = time.time()
            status_code = 200
            
            try:
                response = func(*args, **kwargs)
                
                if hasattr(response, 'status_code'):
                    status_code = response.status_code
                
                return response
            except Exception as e:
                status_code = 500
                if monitoring_client:
                    monitoring_client.record_error(
                        error_type=type(e).__name__,
                        error_message=str(e)
                    )
                raise
            finally:
                duration_ms = (time.time() - start_time) * 1000
                
                if monitoring_client:
                    endpoint = func.__name__
                    method = "GET"
                    
                    monitoring_client.record_request(
                        endpoint=endpoint,
                        method=method,
                        status_code=status_code,
                        duration_ms=duration_ms
                    )
        
        # Return appropriate wrapper based on function type
        import inspect
        if inspect.iscoroutinefunction(func):
            return async_wrapper
        return sync_wrapper
    
    return decorator


def get_lib_info() -> Dict[str, Any]:
    """
    Returns shared library version information.
    Used for surgical versioning and dependency tracking.
    """
    return {
        "version": "1.0.0",
        "library": "shared_libs",
        "description": "Lean Hub Shared Utilities",
        "timestamp": datetime.utcnow().isoformat()
    }


def format_response(data: Any, success: bool = True, message: str = "") -> Dict[str, Any]:
    """
    Standardized API response format across all services.
    """
    return {
        "success": success,
        "message": message,
        "data": data,
        "timestamp": datetime.utcnow().isoformat()
    }
