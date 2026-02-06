# Run this in Cloud Shell to manually deploy gateway with correct URLs

# Create config with correct URLs
cat > /tmp/gateway-config.yaml << 'EOF'
swagger: '2.0'
info:
  title: Lean Hub API Gateway
  description: Unified access point for all services with Firebase Authentication
  version: 1.0.0

host: hub.yourdomain.com
schemes:
  - https

securityDefinitions:
  firebase:
    authorizationUrl: ""
    flow: "implicit"
    type: "oauth2"
    x-google-issuer: "https://securetoken.google.com/my-lean-hub-project"
    x-google-jwks_uri: "https://www.googleapis.com/service_accounts/v1/metadata/x509/securetoken@system.gserviceaccount.com"
    x-google-audiences: "my-lean-hub-project"

security:
  - firebase: []

paths:
  /p1:
    get:
      summary: Project 1 Root
      operationId: project1Root
      x-google-backend:
        address: https://project-1-494821814955.us-central1.run.app
        path_translation: CONSTANT_ADDRESS
      responses:
        '200':
          description: Successful response
  
  /p1/health:
    get:
      summary: Project 1 Health
      operationId: project1Health
      x-google-backend:
        address: https://project-1-494821814955.us-central1.run.app/health
        path_translation: CONSTANT_ADDRESS
      responses:
        '200':
          description: Healthy
  
  /p1/version:
    get:
      summary: Project 1 Version
      operationId: project1Version
      x-google-backend:
        address: https://project-1-494821814955.us-central1.run.app/version
        path_translation: CONSTANT_ADDRESS
      responses:
        '200':
          description: Version info

  /p2:
    get:
      summary: Project 2 RAG Root
      operationId: project2Root
      x-google-backend:
        address: https://project-2-rag-494821814955.us-central1.run.app
        path_translation: CONSTANT_ADDRESS
      responses:
        '200':
          description: Successful response
  
  /p2/health:
    get:
      summary: Project 2 Health
      operationId: project2Health
      x-google-backend:
        address: https://project-2-rag-494821814955.us-central1.run.app/health
        path_translation: CONSTANT_ADDRESS
      responses:
        '200':
          description: Healthy

  /p3:
    get:
      summary: Project 3 Root
      operationId: project3Root
      x-google-backend:
        address: https://project-3-494821814955.us-central1.run.app
        path_translation: CONSTANT_ADDRESS
      responses:
        '200':
          description: Successful response
  
  /p3/health:
    get:
      summary: Project 3 Health
      operationId: project3Health
      x-google-backend:
        address: https://project-3-494821814955.us-central1.run.app/health
        path_translation: CONSTANT_ADDRESS
      responses:
        '200':
          description: Healthy
  
  /p3/status:
    get:
      summary: Project 3 Status
      operationId: project3Status
      x-google-backend:
        address: https://project-3-494821814955.us-central1.run.app/status
        path_translation: CONSTANT_ADDRESS
      responses:
        '200':
          description: Status info
EOF

# Create new API config
CONFIG_NAME="lean-hub-config-manual-$(date +%Y%m%d-%H%M%S)"
echo "Creating config: $CONFIG_NAME"

gcloud api-gateway api-configs create $CONFIG_NAME \
  --api=lean-hub-api \
  --openapi-spec=/tmp/gateway-config.yaml \
  --project=my-lean-hub-project \
  --backend-auth-service-account=github-actions@my-lean-hub-project.iam.gserviceaccount.com

echo "Waiting for config to be created..."
sleep 10

# Update gateway to use new config
echo "Updating gateway..."
gcloud api-gateway gateways update lean-hub-gateway \
  --api=lean-hub-api \
  --api-config=$CONFIG_NAME \
  --location=us-central1 \
  --project=my-lean-hub-project

echo "Done! Gateway updated with correct URLs."
echo "Wait 2-3 minutes for changes to propagate, then test."
