# Infrastructure Configuration

This directory contains all infrastructure-as-code for the Lean Hub deployment.

## Files

- `api-gateway-config.yaml` - OpenAPI spec for API Gateway with Firebase auth
- `firebase-auth-setup.md` - Firebase Authentication setup guide
- `deploy-all-services.sh` - Deploy all Cloud Run services
- `deploy-gateway.sh` - Deploy API Gateway
- `cost-optimization.md` - Cost optimization strategies
- `terraform/` - Terraform configurations (optional)

## Quick Start

### Prerequisites

1. **GCP Project Setup**
```bash
export GCP_PROJECT_ID="your-project-id"
gcloud config set project $GCP_PROJECT_ID
```

2. **Enable Required APIs**
```bash
gcloud services enable \
    run.googleapis.com \
    artifactregistry.googleapis.com \
    apigateway.googleapis.com \
    servicemanagement.googleapis.com \
    servicecontrol.googleapis.com
```

3. **Authenticate Docker**
```bash
gcloud auth configure-docker us-central1-docker.pkg.dev
```

### Deployment Steps

#### 1. Deploy All Services
```bash
cd infrastructure
chmod +x deploy-all-services.sh
./deploy-all-services.sh
```

This will:
- Create Artifact Registry
- Build Docker images
- Deploy all 3 Cloud Run services (internal-only)
- Output service URLs

#### 2. Update API Gateway Config

After deployment, update `api-gateway-config.yaml`:
- Replace `https://project-*-HASH-uc.a.run.app` with actual URLs
- Update Firebase project ID

#### 3. Deploy API Gateway
```bash
chmod +x deploy-gateway.sh
./deploy-gateway.sh
```

#### 4. Setup Firebase Authentication
Follow instructions in `firebase-auth-setup.md`

## Architecture

```
Internet
    |
    v
[API Gateway] <-- Firebase Auth
    |
    +-- /p1 --> [Cloud Run: Project 1] (Internal)
    |
    +-- /p2 --> [Cloud Run: Project 2 RAG] (Internal, GPU)
    |
    +-- /p3 --> [Cloud Run: Project 3] (Internal)
```

## Security Features

1. **Internal-Only Services**: All Cloud Run services have `--ingress internal`
2. **Single Entry Point**: Only API Gateway is publicly accessible
3. **Firebase Authentication**: All requests require valid Firebase tokens
4. **Zero Trust**: No service is directly accessible from internet

## Cost Optimization

1. **Auto-scaling**: `min-instances=0` for zero cost at idle
2. **Right-sizing**: Services use minimal resources
3. **Internal Routing**: No egress charges between services
4. **Artifact Registry**: Free internal pulls, near-instant deployments
5. **GPU Optimization**: L4 GPUs only for Project 2, 2-3x cheaper than A100

## Monitoring

```bash
# View logs for a service
gcloud run logs read project-1 --region=us-central1

# View API Gateway logs
gcloud logging read "resource.type=api_gateway"
```

## Cost Estimation

- **Project 1 & 3**: ~$0.50/month at low traffic
- **Project 2 (GPU)**: ~$0.35/hour when running (auto-scales to 0)
- **API Gateway**: $0.50/million requests + $2/GB transferred
- **Artifact Registry**: $0.10/GB/month storage

Total idle cost: **~$1-2/month**

## Terraform (Optional)

For declarative infrastructure:
```bash
cd terraform
terraform init
terraform plan
terraform apply
```
