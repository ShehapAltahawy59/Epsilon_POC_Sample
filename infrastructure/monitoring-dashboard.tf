# Cloud Monitoring Dashboard Configuration
# This configuration creates a centralized Hub dashboard showing all services

resource "google_monitoring_dashboard" "lean_hub_dashboard" {
  dashboard_json = jsonencode({
    displayName = "Lean Hub - Centralized Dashboard"
    
    mosaicLayout = {
      columns = 12
      
      tiles = [
        # Service Health Overview
        {
          width  = 4
          height = 4
          widget = {
            title = "Service Health Status"
            scorecard = {
              timeSeriesQuery = {
                timeSeriesFilter = {
                  filter = "resource.type=\"cloud_run_revision\" AND metric.type=\"custom.googleapis.com/lean_hub/health_status\""
                  aggregation = {
                    alignmentPeriod  = "60s"
                    perSeriesAligner = "ALIGN_MEAN"
                  }
                }
              }
              sparkChartView = {
                sparkChartType = "SPARK_LINE"
              }
            }
          }
        },
        
        # Request Count by Service
        {
          xPos   = 4
          width  = 4
          height = 4
          widget = {
            title = "Requests per Minute (by Service)"
            xyChart = {
              dataSets = [
                {
                  timeSeriesQuery = {
                    timeSeriesFilter = {
                      filter = "resource.type=\"cloud_run_revision\" AND metric.type=\"custom.googleapis.com/lean_hub/request_count\""
                      aggregation = {
                        alignmentPeriod    = "60s"
                        perSeriesAligner   = "ALIGN_RATE"
                        crossSeriesReducer = "REDUCE_SUM"
                        groupByFields      = ["metric.label.service"]
                      }
                    }
                  }
                  plotType = "LINE"
                }
              ]
              yAxis = {
                label = "Requests/min"
                scale = "LINEAR"
              }
            }
          }
        },
        
        # Average Response Time
        {
          xPos   = 8
          width  = 4
          height = 4
          widget = {
            title = "Average Response Time (ms)"
            xyChart = {
              dataSets = [
                {
                  timeSeriesQuery = {
                    timeSeriesFilter = {
                      filter = "resource.type=\"cloud_run_revision\" AND metric.type=\"custom.googleapis.com/lean_hub/request_count\""
                      aggregation = {
                        alignmentPeriod    = "60s"
                        perSeriesAligner   = "ALIGN_MEAN"
                        crossSeriesReducer = "REDUCE_MEAN"
                        groupByFields      = ["metric.label.service"]
                      }
                    }
                  }
                  plotType = "LINE"
                }
              ]
              yAxis = {
                label = "Milliseconds"
                scale = "LINEAR"
              }
            }
          }
        },
        
        # Error Rate
        {
          yPos   = 4
          width  = 6
          height = 4
          widget = {
            title = "Error Rate (%)"
            xyChart = {
              dataSets = [
                {
                  timeSeriesQuery = {
                    timeSeriesFilter = {
                      filter = "resource.type=\"cloud_run_revision\" AND metric.type=\"custom.googleapis.com/lean_hub/error_count\""
                      aggregation = {
                        alignmentPeriod    = "60s"
                        perSeriesAligner   = "ALIGN_RATE"
                        crossSeriesReducer = "REDUCE_SUM"
                        groupByFields      = ["metric.label.service"]
                      }
                    }
                  }
                  plotType = "LINE"
                }
              ]
              yAxis = {
                label = "Errors/min"
                scale = "LINEAR"
              }
              thresholds = [
                {
                  value     = 5
                  color     = "YELLOW"
                  direction = "ABOVE"
                },
                {
                  value     = 10
                  color     = "RED"
                  direction = "ABOVE"
                }
              ]
            }
          }
        },
        
        # Success Rate by Service
        {
          xPos   = 6
          yPos   = 4
          width  = 6
          height = 4
          widget = {
            title = "Success Rate (%) by Service"
            xyChart = {
              dataSets = [
                {
                  timeSeriesQuery = {
                    timeSeriesFilter = {
                      filter = "resource.type=\"cloud_run_revision\" AND metric.type=\"custom.googleapis.com/lean_hub/request_count\" AND metric.label.success=\"true\""
                      aggregation = {
                        alignmentPeriod    = "60s"
                        perSeriesAligner   = "ALIGN_RATE"
                        crossSeriesReducer = "REDUCE_SUM"
                        groupByFields      = ["metric.label.service"]
                      }
                    }
                  }
                  plotType = "LINE"
                }
              ]
              yAxis = {
                label = "Success %"
                scale = "LINEAR"
              }
            }
          }
        },
        
        # Cloud Run CPU Utilization
        {
          yPos   = 8
          width  = 4
          height = 4
          widget = {
            title = "CPU Utilization (%)"
            xyChart = {
              dataSets = [
                {
                  timeSeriesQuery = {
                    timeSeriesFilter = {
                      filter = "resource.type=\"cloud_run_revision\" AND metric.type=\"run.googleapis.com/container/cpu/utilizations\""
                      aggregation = {
                        alignmentPeriod    = "60s"
                        perSeriesAligner   = "ALIGN_MEAN"
                        crossSeriesReducer = "REDUCE_MEAN"
                        groupByFields      = ["resource.label.service_name"]
                      }
                    }
                  }
                  plotType = "LINE"
                }
              ]
            }
          }
        },
        
        # Cloud Run Memory Utilization
        {
          xPos   = 4
          yPos   = 8
          width  = 4
          height = 4
          widget = {
            title = "Memory Utilization (%)"
            xyChart = {
              dataSets = [
                {
                  timeSeriesQuery = {
                    timeSeriesFilter = {
                      filter = "resource.type=\"cloud_run_revision\" AND metric.type=\"run.googleapis.com/container/memory/utilizations\""
                      aggregation = {
                        alignmentPeriod    = "60s"
                        perSeriesAligner   = "ALIGN_MEAN"
                        crossSeriesReducer = "REDUCE_MEAN"
                        groupByFields      = ["resource.label.service_name"]
                      }
                    }
                  }
                  plotType = "LINE"
                }
              ]
            }
          }
        },
        
        # Cloud Run Instance Count
        {
          xPos   = 8
          yPos   = 8
          width  = 4
          height = 4
          widget = {
            title = "Active Instances"
            xyChart = {
              dataSets = [
                {
                  timeSeriesQuery = {
                    timeSeriesFilter = {
                      filter = "resource.type=\"cloud_run_revision\" AND metric.type=\"run.googleapis.com/container/instance_count\""
                      aggregation = {
                        alignmentPeriod    = "60s"
                        perSeriesAligner   = "ALIGN_MEAN"
                        crossSeriesReducer = "REDUCE_SUM"
                        groupByFields      = ["resource.label.service_name"]
                      }
                    }
                  }
                  plotType = "STACKED_AREA"
                }
              ]
            }
          }
        },
        
        # Shared Library Versions
        {
          yPos   = 12
          width  = 12
          height = 2
          widget = {
            title = "Shared Library Versions by Service"
            logsPanel = {
              resourceNames = [
                "projects/${var.project_id}"
              ]
              filter = "resource.type=\"cloud_run_revision\" AND jsonPayload.shared_lib_version!=\"\""
            }
          }
        }
      ]
    }
  })
}

# Alert Policies

resource "google_monitoring_alert_policy" "high_error_rate" {
  display_name = "Lean Hub - High Error Rate"
  combiner     = "OR"
  
  conditions {
    display_name = "Error rate above 5%"
    
    condition_threshold {
      filter          = "resource.type=\"cloud_run_revision\" AND metric.type=\"custom.googleapis.com/lean_hub/error_count\""
      duration        = "300s"
      comparison      = "COMPARISON_GT"
      threshold_value = 5
      
      aggregations {
        alignment_period   = "60s"
        per_series_aligner = "ALIGN_RATE"
      }
    }
  }
  
  notification_channels = var.notification_channels
  
  alert_strategy {
    auto_close = "1800s"
  }
}

resource "google_monitoring_alert_policy" "service_down" {
  display_name = "Lean Hub - Service Down"
  combiner     = "OR"
  
  conditions {
    display_name = "Service health check failed"
    
    condition_threshold {
      filter          = "resource.type=\"cloud_run_revision\" AND metric.type=\"custom.googleapis.com/lean_hub/health_status\""
      duration        = "180s"
      comparison      = "COMPARISON_LT"
      threshold_value = 1
      
      aggregations {
        alignment_period   = "60s"
        per_series_aligner = "ALIGN_MIN"
      }
    }
  }
  
  notification_channels = var.notification_channels
}

resource "google_monitoring_alert_policy" "high_response_time" {
  display_name = "Lean Hub - High Response Time"
  combiner     = "OR"
  
  conditions {
    display_name = "Average response time above 2 seconds"
    
    condition_threshold {
      filter          = "resource.type=\"cloud_run_revision\" AND metric.type=\"custom.googleapis.com/lean_hub/request_count\""
      duration        = "300s"
      comparison      = "COMPARISON_GT"
      threshold_value = 2000
      
      aggregations {
        alignment_period   = "60s"
        per_series_aligner = "ALIGN_MEAN"
      }
    }
  }
  
  notification_channels = var.notification_channels
}

variable "project_id" {
  description = "GCP Project ID"
  type        = string
}

variable "notification_channels" {
  description = "List of notification channel IDs for alerts"
  type        = list(string)
  default     = []
}
