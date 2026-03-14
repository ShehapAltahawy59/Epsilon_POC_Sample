# Lean Hub - Epsilon POC Sample

**⚡ 100% Automated Deployment | 🎯 Surgical Versioning | 💰 Zero Idle Cost**

A production-ready monorepo demonstrating the "Lean Hub" philosophy: **set up GitHub secrets once (15 min), then everything deploys automatically forever!**

## 🚀 How It Works

```
You: git push origin main
                │
                ▼
    GitHub Actions (automatic):
    ✅ Detects what changed (path filtering)
    ✅ Builds only affected services
    ✅ Deploys to GCP Cloud Run
    ✅ Updates monitoring dashboard
    ✅ Tags shared library versions
    ✅ Logs with correlation IDs
                │
                ▼
    Production: Services live in 3-5 minutes!
```

**What's manual?** Only adding secrets to GitHub (one-time, 15 min)  

## Architecture Overview

```
┌─────────────────────────────────────────────────────────┐
│                    Internet Users                        │
└───────────────────────┬─────────────────────────────────┘
                        │
                        ▼
              ┌─────────────────────┐
              │   API Gateway       │
              │   (Firebase Auth)   │
              │   hub.com           │
              └─────────┬───────────┘
                        │
         ┌──────────────┼──────────────┐
         │              │              │
         ▼              ▼              ▼
    ┌────────┐    ┌──────────┐   ┌────────┐
    │Project1│    │Project 2 │   │Project3│
    │  API   │    │   RAG    │   │  API   │
    │        │    │ (GPU L4) │   │        │
    │ v1.0.0 │    │  v1.0.0  │   │ v1.0.0 │
    └───┬────┘    └────┬─────┘   └───┬────┘
        │              │              │
        └──────────────┼──────────────┘
                       │
                ┌──────▼───────┐
                │ shared_libs  │
                │   v1.0.0     │
                │   v2.0.0     │
                └──────────────┘
```

## Key Features

### 🎯 Surgical Versioning
- Each project pins to a specific shared library version
- Update one service without affecting others
- Test new features in isolated environments
- Rollback individual services independently

### 💰 Aggressive Cost Optimization
- **Zero Idle Cost**: Auto-scale to 0 instances
- **Internal-Only Services**: No egress charges
- **Artifact Registry**: Free internal pulls
- **GPU Optimization**: L4 GPUs (2-3x cheaper than A100)
- **Path-Filtered CI/CD**: Only rebuild changed services

### 🔐 Unified Security
- Single public endpoint (API Gateway)
- Firebase Authentication at gateway level
- All Cloud Run services internal-only
- Centralized audit logging

### 🚀 Surgical CI/CD
- Path-based deployment triggers
- Only affected services rebuild
- Automatic shared library version detection
- Git tag-based versioning

### 📊 Complete Observability
- **JSON-structured logging** with correlation IDs
- **Cloud Trace integration** for distributed tracing
- **Centralized monitoring dashboard** for all services
- **Custom metrics** for request tracking and performance
- **Alert policies** for proactive issue detection


## Quick Start

### ⚡ Fully Automated Deployment

After one-time GitHub secrets setup (~15 min), **everything deploys automatically!**

**What's Manual?** Only adding secrets to GitHub 

**What's Automatic?**
- ✅ Service builds & deployments (CI/CD)
- ✅ Monitoring dashboard deployment (CI/CD)
- ✅ API enablement (CI/CD)
- ✅ Version tagging (CI/CD)
- ✅ Correlation IDs & logging (middleware)

### One-Time Setup (15 Minutes)

**Step 1: Configure GitHub Secrets**
```
GitHub Repository → Settings → Secrets and variables → Actions

Required secrets:
- GCP_PROJECT_ID         = "your-gcp-project-id"
- GCP_SA_KEY            = {entire service account JSON}
- FIREBASE_API_KEY      = "AIza..."
- FIREBASE_PROJECT_ID   = "your-firebase-project"
- FIREBASE_AUTH_DOMAIN  = "your-project.firebaseapp.com"


```

**Step 2: Push to GitHub**
```bash
git add .
git commit -m "Initial deployment"
git push origin main

# GitHub Actions automatically:
# ✅ Enables GCP APIs
# ✅ Builds all services
# ✅ Deploys to Cloud Run
# ✅ Creates monitoring dashboard
# ✅ Sets up logging & tracing
```

**That's it!** No manual deployments needed.

### Configuration Files

**All configuration is already in the repo:**

- `.env` (committed) = Non-sensitive config (regions, service names, resource limits)
- GitHub Secrets = Sensitive credentials (never committed)
- Dockerfiles = Version pinning per service

**See [SECRETS_SETUP_GUIDE.md](SECRETS_SETUP_GUIDE.md) for complete setup guide.**


## Project Structure

```
.
├── shared_libs/              # Versioned shared utilities
│   ├── __init__.py
│   └── utils.py             # JSON logging, version tracking
│
├── project_1/               # Simple API service
│   ├── main.py
│   ├── Dockerfile           # Pinned to v1.0.0
│   └── requirements.txt
│
├── project_2/               # RAG with GPU acceleration
│   ├── main.py
│   ├── Dockerfile           # GPU-enabled, pinned to v1.0.0
│   └── requirements.txt
│
├── project_3/               # Another API service
│   ├── main.py
│   ├── Dockerfile           # Pinned to v1.0.0
│   └── requirements.txt
│
├── project_template/        # Reusable starter for project_5+
│   ├── main.py
│   ├── Dockerfile
│   ├── requirements.txt
│   └── shared_lib_version
│
├── .github/workflows/       # 🤖 Automated CI/CD
│   ├── deploy-project-1.yml
│   ├── deploy-project-2.yml
│   ├── deploy-project-3.yml
│   ├── reusable-deploy-project.yml
│   ├── deploy-monitoring.yml    # 📊 Auto-deploys dashboard
│   └── tag-shared-libs.yml
│
├── infrastructure/          # IaC and deployment
│   ├── services-registry.json    # Single source for gateway routes/services
│   ├── generate_api_gateway_config.py
│   ├── deploy-all-services.sh
│   ├── dashboard-config.json
│   ├── monitoring-dashboard.tf
│   └── MONITORING_SETUP.md
│
```

## The Surgical Update Test

Proves that you can update shared libraries for one service without affecting others:

1. Update `shared_libs` to v2.0.0
2. Update **only** Project 1 to use v2.0.0
3. Verify:
   - Project 1 shows v2.0.0 ✅
   - Project 2 shows v1.0.0 ✅
   - Project 3 shows v1.0.0 ✅


## API Endpoints

Once deployed, all services are accessible through the unified gateway:

```bash
# Project 1
GET https://hub.yourdomain.com/p1
GET https://hub.yourdomain.com/p1/health
GET https://hub.yourdomain.com/p1/version

# Project 2 (RAG)
GET  https://hub.yourdomain.com/p2
POST https://hub.yourdomain.com/p2/query
POST https://hub.yourdomain.com/p2/index

# Project 3
GET https://hub.yourdomain.com/p3
GET https://hub.yourdomain.com/p3/status
```

## Cost Analysis

### Traditional Monolith
- Update shared code → redeploy everything
- 3x CI/CD pipelines run
- 3x deployment operations
- All services restart simultaneously
- **Higher risk, higher cost**

### Lean Hub
- Update shared code → redeploy only affected services
- 1x CI/CD pipeline (path-filtered)
- 1x deployment operation
- Other services unaffected
- **Lower risk, 66% cost reduction**

### Estimated Monthly Costs

| Component | Idle Cost | Active Cost |
|-----------|-----------|-------------|
| Project 1 & 3 | $0.50 each | ~$5/month each (low traffic) |
| Project 2 (GPU) | $0 | $0.35/hour when running |
| API Gateway | $0 | $0.50/M requests |
| Artifact Registry | ~$0.10 | Storage only |
| **Total Idle** | **~$1-2/month** | - |

## GitHub Actions Setup

Add these secrets to your GitHub repository:

```bash
GCP_PROJECT_ID      # Your GCP project ID
GCP_SA_KEY          # Service account JSON key
```

The workflows will automatically:
1. Detect changes using path filters
2. Build Docker images
3. Push to Artifact Registry
4. Deploy to Cloud Run
5. Update only affected services


## Monitoring & Observability

All services use JSON-structured logging:

```bash
# View logs with version tracking
gcloud run logs read project-1 --region=us-central1

# Check library versions
curl https://hub.yourdomain.com/p1/version
```

Logs include:
- Service name
- Timestamp (ISO format)
- Log level
- Message
- Shared library version
- Custom metadata

## Add a New Project Fast

Use the standardized onboarding flow:

- Copy `project_template/` -> new folder (for example `project_5/`)
- Add one thin workflow wrapper using `reusable-deploy-project.yml`
- Register service routes in `infrastructure/gateway/services-registry.json`
- Run project deploy, then manual gateway deploy

See `NEW_PROJECT_CHECKLIST.md` for full step-by-step.


## Contributing

This is a POC/sample project demonstrating the Lean Hub architecture. Feel free to:

- Use as a template for your own projects
- Modify for your specific needs
- Extend with additional services
- Add more shared libraries

## Key Takeaways

1. **Versioned Dependencies**: Git tags + Docker ENV vars = immutable builds
2. **Path-Filtered CI/CD**: Only rebuild what changed
3. **Internal-Only Services**: Security + cost savings
4. **Unified Gateway**: One URL for everything
5. **GPU Optimization**: Right-size infrastructure (L4 > A100 for most workloads)
6. **Complete Observability**: JSON logs + correlation IDs + Cloud Trace + centralized dashboard
