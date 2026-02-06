#!/bin/bash
# Deploy Cloud Monitoring Dashboard and Alert Policies
# This creates a centralized Hub dashboard for all services

set -e

echo "🔍 Setting up Cloud Monitoring for Lean Hub..."

# Load environment variables
source ../.env

# Check for required variables
if [ -z "$GCP_PROJECT_ID" ]; then
    echo "Error: GCP_PROJECT_ID not set in .env"
    exit 1
fi

# Enable required APIs
echo "📦 Enabling Cloud Monitoring APIs..."
gcloud services enable \
    monitoring.googleapis.com \
    logging.googleapis.com \
    cloudtrace.googleapis.com \
    --project=$GCP_PROJECT_ID

# Create dashboard using Terraform (if available)
if command -v terraform &> /dev/null; then
    echo "🏗️ Deploying dashboard with Terraform..."
    
    # Initialize Terraform
    terraform init
    
    # Create dashboard
    terraform apply \
        -target=google_monitoring_dashboard.lean_hub_dashboard \
        -var="project_id=$GCP_PROJECT_ID" \
        -auto-approve
    
    # Create alert policies
    terraform apply \
        -target=google_monitoring_alert_policy.high_error_rate \
        -target=google_monitoring_alert_policy.service_down \
        -target=google_monitoring_alert_policy.high_response_time \
        -var="project_id=$GCP_PROJECT_ID" \
        -auto-approve
    
    echo "✅ Dashboard and alerts created via Terraform"
else
    echo "⚠️ Terraform not found - skipping dashboard creation"
    echo "   You can create the dashboard manually in Cloud Console:"
    echo "   https://console.cloud.google.com/monitoring/dashboards/create?project=$GCP_PROJECT_ID"
fi

# Create notification channel (if email provided)
if [ ! -z "$ALERT_EMAIL" ]; then
    echo "📧 Creating notification channel for: $ALERT_EMAIL"
    
    CHANNEL_ID=$(gcloud alpha monitoring channels create \
        --display-name="Lean Hub Alerts" \
        --type=email \
        --channel-labels=email_address=$ALERT_EMAIL \
        --project=$GCP_PROJECT_ID \
        --format="value(name)")
    
    echo "✅ Notification channel created: $CHANNEL_ID"
    echo "   Add this to monitoring-dashboard.tf variable 'notification_channels'"
else
    echo "⚠️ No ALERT_EMAIL set in .env - skipping notification channel"
fi

# Output dashboard link
echo ""
echo "✅ Cloud Monitoring setup complete!"
echo ""
echo "📊 Dashboard URL:"
echo "https://console.cloud.google.com/monitoring/dashboards?project=$GCP_PROJECT_ID"
echo ""
echo "📝 To view logs with correlation IDs:"
echo "https://console.cloud.google.com/logs/query?project=$GCP_PROJECT_ID"
echo ""
echo "🔍 Example log query:"
echo 'resource.type="cloud_run_revision"'
echo 'jsonPayload.correlation_id="YOUR_CORRELATION_ID"'
echo ""
echo "📈 Metrics are available after services receive traffic."
echo "   Allow 5-10 minutes for metrics to populate the dashboard."
