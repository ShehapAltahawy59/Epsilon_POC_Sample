#!/bin/bash
# Deploy API Gateway for Lean Hub
# Connects all internal Cloud Run services to a single public endpoint

set -e

PROJECT_ID="${GCP_PROJECT_ID}"
REGION="us-central1"
API_NAME="lean-hub-api"
CONFIG_NAME="lean-hub-config"
GATEWAY_NAME="lean-hub-gateway"

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}API Gateway Deployment${NC}"
echo -e "${BLUE}========================================${NC}"

if [ -z "$PROJECT_ID" ]; then
    echo -e "${YELLOW}Error: GCP_PROJECT_ID environment variable not set${NC}"
    exit 1
fi

# Create API
echo -e "\n${BLUE}Step 1: Creating API...${NC}"
gcloud api-gateway apis create ${API_NAME} \
    --project=${PROJECT_ID} 2>/dev/null || echo "API already exists"

echo -e "${GREEN}✓ API created${NC}"

# Create API Config
echo -e "\n${BLUE}Step 2: Creating API configuration...${NC}"
gcloud api-gateway api-configs create ${CONFIG_NAME} \
    --api=${API_NAME} \
    --openapi-spec=infrastructure/api-gateway-config.yaml \
    --project=${PROJECT_ID} \
    --backend-auth-service-account=${PROJECT_ID}@appspot.gserviceaccount.com

echo -e "${GREEN}✓ API configuration created${NC}"

# Create Gateway
echo -e "\n${BLUE}Step 3: Creating gateway...${NC}"
gcloud api-gateway gateways create ${GATEWAY_NAME} \
    --api=${API_NAME} \
    --api-config=${CONFIG_NAME} \
    --location=${REGION} \
    --project=${PROJECT_ID}

echo -e "${GREEN}✓ Gateway created${NC}"

# Get Gateway URL
echo -e "\n${BLUE}Step 4: Retrieving gateway URL...${NC}"
GATEWAY_URL=$(gcloud api-gateway gateways describe ${GATEWAY_NAME} \
    --location=${REGION} \
    --project=${PROJECT_ID} \
    --format='value(defaultHostname)')

echo -e "\n${BLUE}========================================${NC}"
echo -e "${BLUE}API Gateway Deployed!${NC}"
echo -e "${BLUE}========================================${NC}"

echo -e "\n${GREEN}Gateway URL: https://${GATEWAY_URL}${NC}"

echo -e "\n${YELLOW}Test Endpoints (after Firebase auth):${NC}"
echo -e "Project 1: https://${GATEWAY_URL}/p1"
echo -e "Project 2 RAG: https://${GATEWAY_URL}/p2"
echo -e "Project 3: https://${GATEWAY_URL}/p3"

echo -e "\n${YELLOW}Next Steps:${NC}"
echo -e "1. Set up Firebase Authentication (see infrastructure/firebase-auth-setup.md)"
echo -e "2. Configure custom domain (optional)"
echo -e "3. Test endpoints with Firebase tokens"

echo -e "\n${GREEN}✓ API Gateway is live!${NC}"
