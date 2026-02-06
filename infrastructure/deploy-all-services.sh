#!/bin/bash
# Deploy all Cloud Run services with internal-only ingress
# This script sets up the complete Lean Hub infrastructure

set -e

# Load environment variables from .env file
if [ -f ../.env ]; then
    echo "Loading environment variables from .env..."
    export $(cat ../.env | grep -v '^#' | xargs)
elif [ -f .env ]; then
    echo "Loading environment variables from .env..."
    export $(cat .env | grep -v '^#' | xargs)
else
    echo "Warning: .env file not found. Using defaults or environment variables."
fi

# Configuration (loaded from .env or defaults)
PROJECT_ID="${GCP_PROJECT_ID}"
REGION="${GCP_REGION:-us-central1}"
GAR_LOCATION="${GAR_LOCATION:-us-central1}"
REPOSITORY="${GAR_REPOSITORY:-lean-hub}"
SERVICE_P1="${SERVICE_PROJECT_1:-project-1}"
SERVICE_P2="${SERVICE_PROJECT_2:-project-2-rag}"
SERVICE_P3="${SERVICE_PROJECT_3:-project-3}"

# Resource configuration
STANDARD_MEM="${STANDARD_MEMORY:-512Mi}"
STANDARD_CPU_COUNT="${STANDARD_CPU:-1}"
RAG_MEM="${RAG_MEMORY:-16Gi}"
RAG_CPU_COUNT="${RAG_CPU:-4}"
GPU_COUNT="${RAG_GPU_COUNT:-1}"
GPU_TYPE="${RAG_GPU_TYPE:-nvidia-l4}"
MAX_INSTANCES="${STANDARD_MAX_INSTANCES:-10}"
MIN_INSTANCES="${STANDARD_MIN_INSTANCES:-0}"

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}Lean Hub Infrastructure Deployment${NC}"
echo -e "${BLUE}========================================${NC}"

# Check prerequisites
if [ -z "$PROJECT_ID" ]; then
    echo -e "${YELLOW}Error: GCP_PROJECT_ID environment variable not set${NC}"
    exit 1
fi

echo -e "\n${GREEN}✓ Using GCP Project: ${PROJECT_ID}${NC}"
echo -e "${GREEN}✓ Region: ${REGION}${NC}"

# Create Artifact Registry if it doesn't exist
echo -e "\n${BLUE}Step 1: Setting up Artifact Registry...${NC}"
gcloud artifacts repositories create ${REPOSITORY} \
    --repository-format=docker \
    --location=${GAR_LOCATION} \
    --project=${PROJECT_ID} \
    --description="Lean Hub Docker Repository" 2>/dev/null || echo "Repository already exists"

echo -e "${GREEN}✓ Artifact Registry ready${NC}"

# Build and push Project 1
echo -e "\n${BLUE}Step 2: Building and deploying Project 1...${NC}"
docker build -f project_1/Dockerfile -t ${GAR_LOCATION}-docker.pkg.dev/${PROJECT_ID}/${REPOSITORY}/${SERVICE_P1}:latest .
docker push ${GAR_LOCATION}-docker.pkg.dev/${PROJECT_ID}/${REPOSITORY}/${SERVICE_P1}:latest

gcloud run deploy ${SERVICE_P1} \
    --image ${GAR_LOCATION}-docker.pkg.dev/${PROJECT_ID}/${REPOSITORY}/${SERVICE_P1}:latest \
    --platform managed \
    --region ${REGION} \
    --ingress internal \
    --allow-unauthenticated \
    --max-instances ${MAX_INSTANCES} \
    --min-instances ${MIN_INSTANCES} \
    --memory ${STANDARD_MEM} \
    --cpu ${STANDARD_CPU_COUNT} \
    --project ${PROJECT_ID}

echo -e "${GREEN}✓ Project 1 deployed${NC}"

# Build and push Project 2 (RAG with GPU)
echo -e "\n${BLUE}Step 3: Building and deploying Project 2 (RAG)...${NC}"
docker build -f project_2/Dockerfile -t ${GAR_LOCATION}-docker.pkg.dev/${PROJECT_ID}/${REPOSITORY}/${SERVICE_P2}:latest .
docker push ${GAR_LOCATION}-docker.pkg.dev/${PROJECT_ID}/${REPOSITORY}/${SERVICE_P2}:latest

gcloud run deploy ${SERVICE_P2} \
    --image ${GAR_LOCATION}-docker.pkg.dev/${PROJECT_ID}/${REPOSITORY}/${SERVICE_P2}:latest \
    --platform managed \
    --region ${REGION} \
    --ingress internal \
    --allow-unauthenticated \
    --gpu ${GPU_COUNT} \
    --gpu-type ${GPU_TYPE} \
    --max-instances ${MAX_INSTANCES} \
    --min-instances ${MIN_INSTANCES} \
    --memory ${RAG_MEM} \
    --cpu ${RAG_CPU_COUNT} \
    --project ${PROJECT_ID}

echo -e "${GREEN}✓ Project 2 RAG deployed with GPU${NC}"

# Build and push Project 3
echo -e "\n${BLUE}Step 4: Building and deploying Project 3...${NC}"
docker build -f project_3/Dockerfile -t ${GAR_LOCATION}-docker.pkg.dev/${PROJECT_ID}/${REPOSITORY}/${SERVICE_P3}:latest .
docker push ${GAR_LOCATION}-docker.pkg.dev/${PROJECT_ID}/${REPOSITORY}/${SERVICE_P3}:latest

gcloud run deploy ${SERVICE_P3} \
    --image ${GAR_LOCATION}-docker.pkg.dev/${PROJECT_ID}/${REPOSITORY}/${SERVICE_P3}:latest \
    --platform managed \
    --region ${REGION} \
    --ingress internal \
    --allow-unauthenticated \
    --max-instances ${MAX_INSTANCES} \
    --min-instances ${MIN_INSTANCES} \
    --memory ${STANDARD_MEM} \
    --cpu ${STANDARD_CPU_COUNT} \
    --project ${PROJECT_ID}

echo -e "${GREEN}✓ Project 3 deployed${NC}"

# Get Cloud Run URLs
echo -e "\n${BLUE}Step 5: Retrieving service URLs...${NC}"
PROJECT1_URL=$(gcloud run services describe ${SERVICE_P1} --region=${REGION} --format='value(status.url)')
PROJECT2_URL=$(gcloud run services describe ${SERVICE_P2} --region=${REGION} --format='value(status.url)')
PROJECT3_URL=$(gcloud run services describe ${SERVICE_P3} --region=${REGION} --format='value(status.url)')

echo -e "${GREEN}✓ Service URLs retrieved${NC}"

# Display summary
echo -e "\n${BLUE}========================================${NC}"
echo -e "${BLUE}Deployment Complete!${NC}"
echo -e "${BLUE}========================================${NC}"

echo -e "\n${YELLOW}Cloud Run Service URLs (Internal Only):${NC}"
echo -e "Project 1: ${PROJECT1_URL}"
echo -e "Project 2 RAG: ${PROJECT2_URL}"
echo -e "Project 3: ${PROJECT3_URL}"

echo -e "\n${YELLOW}Next Steps:${NC}"
echo -e "1. Update infrastructure/api-gateway-config.yaml with these URLs"
echo -e "2. Deploy API Gateway (see infrastructure/deploy-gateway.sh)"
echo -e "3. Configure Firebase Authentication"
echo -e "4. Set up GitHub secrets for CI/CD"

echo -e "\n${GREEN}All services are internal-only and ready for API Gateway integration!${NC}"
