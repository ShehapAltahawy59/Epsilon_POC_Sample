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
**What's automatic?** Everything else! See [AUTOMATION_CHECKLIST.md](AUTOMATION_CHECKLIST.md)

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
- See [OBSERVABILITY.md](OBSERVABILITY.md) for details

## Quick Start

### ⚡ Fully Automated Deployment

After one-time GitHub secrets setup (~15 min), **everything deploys automatically!**

**What's Manual?** Only adding secrets to GitHub (see [AUTOMATION_CHECKLIST.md](AUTOMATION_CHECKLIST.md))

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

See: SECRETS_MANAGEMENT.md for step-by-step guide
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

**See [SECRETS_MANAGEMENT.md](SECRETS_MANAGEMENT.md) for complete setup guide.**

### Local Development (Optional)

```bash
# Deploy all services
cd infrastructure
./deploy-all-services.sh

# Deploy API Gateway
./deploy-gateway.sh
```

### Test Locally

```bash
# Test Project 1
cd project_1
pip install -r requirements.txt
python main.py

# Visit http://localhost:8080
```

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
├── .github/workflows/       # 🤖 Automated CI/CD
│   ├── deploy-project-1.yml
│   ├── deploy-project-2.yml
│   ├── deploy-project-3.yml
│   ├── deploy-monitoring.yml    # 📊 Auto-deploys dashboard
│   └── tag-shared-libs.yml
│
├── infrastructure/          # IaC and deployment
│   ├── api-gateway-config.yaml
│   ├── deploy-all-services.sh
│   ├── deploy-gateway.sh
│   ├── deploy-monitoring.sh      # 📊 Monitoring setup
│   ├── dashboard-config.json
│   ├── monitoring-dashboard.tf
│   └── MONITORING_SETUP.md
│
└── SURGICAL_UPDATE_TEST.md  # Proof of concept test
```

## The Surgical Update Test

Proves that you can update shared libraries for one service without affecting others:

1. Update `shared_libs` to v2.0.0
2. Update **only** Project 1 to use v2.0.0
3. Verify:
   - Project 1 shows v2.0.0 ✅
   - Project 2 shows v1.0.0 ✅
   - Project 3 shows v1.0.0 ✅

See [SURGICAL_UPDATE_TEST.md](SURGICAL_UPDATE_TEST.md) for detailed instructions.

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

## Firebase Authentication

Follow the setup guide in [infrastructure/firebase-auth-setup.md](infrastructure/firebase-auth-setup.md) to:

1. Create Firebase project
2. Enable authentication providers
3. Configure API Gateway
4. Integrate with your client apps

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

## Local Development

```bash
# Run any project locally
cd project_1  # or project_2, project_3
pip install -r requirements.txt
python main.py

# Access at http://localhost:8080
```

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

## Documentation

### Getting Started
- **[AUTOMATION_CHECKLIST.md](AUTOMATION_CHECKLIST.md)** - ⭐ What's automatic vs manual (15 min setup!)
- **[SECRETS_MANAGEMENT.md](SECRETS_MANAGEMENT.md)** - GitHub secrets configuration guide

### Core Features
- **[HOW_VERSION_PINNING_WORKS.md](HOW_VERSION_PINNING_WORKS.md)** - Git-based surgical versioning
- **[SURGICAL_UPDATE_TEST.md](SURGICAL_UPDATE_TEST.md)** - Test surgical updates work
- **[OBSERVABILITY.md](OBSERVABILITY.md)** - Logging, tracing, monitoring

### Advanced
- **[infrastructure/MONITORING_SETUP.md](infrastructure/MONITORING_SETUP.md)** - Monitoring deep dive
- **[OBSERVABILITY_IMPLEMENTATION.md](OBSERVABILITY_IMPLEMENTATION.md)** - Implementation details

## Next Steps

1. **Review Automation**: See what's automatic in [AUTOMATION_CHECKLIST.md](AUTOMATION_CHECKLIST.md)
2. **Set Up Secrets** (15 min): Configure GitHub Actions secrets → [SECRETS_MANAGEMENT.md](SECRETS_MANAGEMENT.md)
3. **Push to GitHub**: Automatic deployment happens!
4. **Verify Deployment**: Check GitHub Actions, Cloud Run services, monitoring dashboard
5. **Test Surgical Updates**: Prove independence → [SURGICAL_UPDATE_TEST.md](SURGICAL_UPDATE_TEST.md)
6. **Add Your Services**: Use project templates
7. **Customize Shared Libraries**: Add your common utilities

## Support

For questions or issues:
- Review individual project README files
- Check infrastructure documentation
- See surgical update test case
- Review GitHub Actions workflows

---

**Built with**: Python, FastAPI, Docker, GCP Cloud Run, API Gateway, Firebase, GitHub Actions

**Philosophy**: Minimal maintenance, aggressive cost optimization, surgical versioning

**License**: Use freely for your own projects