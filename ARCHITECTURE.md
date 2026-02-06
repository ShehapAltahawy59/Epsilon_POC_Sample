# 🏗️ Lean Hub Architecture: Complete Technical Overview

**Last Updated:** February 6, 2026  
**Purpose:** Comprehensive guide to understand the architecture, design decisions, and implementation details

---

## 📋 Table of Contents

1. [Executive Summary](#executive-summary)
2. [Architecture Overview](#architecture-overview)
3. [Core Design Principles](#core-design-principles)
4. [Component Deep Dive](#component-deep-dive)
5. [Automation & CI/CD](#automation--cicd)
6. [Observability Strategy](#observability-strategy)
7. [Security Implementation](#security-implementation)
8. [Cost Optimization](#cost-optimization)
9. [Deployment Flow](#deployment-flow)
10. [Troubleshooting Guide](#troubleshooting-guide)

---

## 🎯 Executive Summary

### What Is Lean Hub?

Lean Hub is a **microservices-based platform** designed to demonstrate enterprise-grade cloud architecture patterns using Google Cloud Platform (GCP). It implements three independent services unified behind a single API Gateway with Firebase Authentication.

### Key Achievements

- ✅ **100% Automated Deployments**: Zero manual intervention after initial 17-minute setup
- ✅ **Centralized Observability**: JSON logging, distributed tracing, and unified monitoring
- ✅ **Security-First**: Internal-only services, Firebase Auth, service account isolation
- ✅ **Cost-Optimized**: Scale-to-zero, surgical deployments, shared libraries
- ✅ **Developer Experience**: Consistent patterns, comprehensive documentation, fail-fast validation

---

## 🏛️ Architecture Overview

### High-Level Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                          Internet                                │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         │ HTTPS + Firebase Auth
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│           API Gateway (lean-hub-gateway)                         │
│  • Firebase Authentication Validation                            │
│  • Request Routing                                               │
│  • Rate Limiting                                                 │
│  • Single Entry Point                                            │
└────────┬──────────────┬──────────────┬─────────────────────────┘
         │              │              │
         │ /p1/*        │ /p2/*        │ /p3/*
         ▼              ▼              ▼
┌─────────────┐  ┌─────────────┐  ┌─────────────┐
│  Project 1  │  │  Project 2  │  │  Project 3  │
│  (FastAPI)  │  │  (RAG+GPU)  │  │  (FastAPI)  │
│             │  │             │  │             │
│ • Internal  │  │ • Internal  │  │ • Internal  │
│   Ingress   │  │   Ingress   │  │   Ingress   │
│ • JSON Log  │  │ • JSON Log  │  │ • JSON Log  │
│ • Traces    │  │ • Traces    │  │ • Traces    │
└─────────────┘  └─────────────┘  └─────────────┘
         │              │              │
         └──────────────┼──────────────┘
                        │
                        ▼
         ┌──────────────────────────────┐
         │   shared_libs (v1.0.0)       │
         │  • JSONLogger                │
         │  • CloudMonitoringClient     │
         │  • Correlation ID helpers    │
         │  • Common utilities          │
         └──────────────────────────────┘
                        │
                        ▼
         ┌──────────────────────────────┐
         │   Cloud Logging & Monitoring │
         │  • Structured JSON logs      │
         │  • Distributed traces        │
         │  • Custom metrics            │
         │  • Centralized dashboard     │
         └──────────────────────────────┘
```

### Why This Architecture?

#### 1. **Microservices Pattern**
**Decision:** Split functionality into independent services  
**Rationale:**
- **Independent Scaling**: Each service scales based on its own load (Project 2 RAG can scale separately)
- **Fault Isolation**: If Project 2 crashes, Projects 1 & 3 continue running
- **Technology Freedom**: Each service can use different frameworks/languages if needed
- **Team Autonomy**: Different teams can own different services
- **Deployment Independence**: Update one service without touching others

**Trade-offs:**
- ❌ More complex than monolith (requires orchestration)
- ✅ But we automated everything with GitHub Actions

#### 2. **API Gateway as Single Entry Point**
**Decision:** Use Google Cloud API Gateway instead of direct service access  
**Rationale:**
- **Security**: Services have `--ingress internal` (not publicly accessible)
- **Authentication**: Centralized Firebase Auth validation (one place to manage)
- **Routing**: Easy to add/remove services without changing client code
- **Observability**: Single point to log/monitor all incoming traffic
- **Rate Limiting**: Protect backend services from abuse
- **Versioning**: Can route `/v1/p1` vs `/v2/p1` to different backends

**Why Not Direct Cloud Run URLs?**
- Direct URLs expose services publicly (security risk)
- Need to manage auth in every service (duplication)
- Hard to change service URLs without breaking clients
- No centralized rate limiting or monitoring

#### 3. **Shared Libraries Approach**
**Decision:** Create `shared_libs/` with common utilities  
**Rationale:**
- **DRY Principle**: Write logging/monitoring code once, use everywhere
- **Consistency**: All services log in same JSON format
- **Versioning**: Lock services to specific lib versions for stability
- **Maintainability**: Fix bugs in one place, all services benefit

**Why Not Package on PyPI?**
- Faster iteration (no publish cycle)
- Private code stays private
- Docker build copies at build time (no external dependencies)

---

## 🔧 Component Deep Dive

### 1. Project 1: Simple API Service

**Purpose:** Demonstrate basic microservice pattern with shared libraries

**Technology Stack:**
- FastAPI (Python web framework)
- Uvicorn (ASGI server)
- Python 3.11

**Endpoints:**
- `GET /` - Root endpoint with version info
- `GET /health` - Health check (for load balancers)
- `GET /version` - Library and service version info

**Why FastAPI?**
- ✅ Automatic OpenAPI docs
- ✅ Type validation with Pydantic
- ✅ Async support (handles concurrent requests)
- ✅ Modern Python best practices

**Configuration:**
- **Memory:** 512MB (lightweight, cost-effective)
- **CPU:** 1 core (sufficient for API)
- **Scale:** 0-10 instances (scale to zero when idle)
- **Ingress:** Internal only (security)

### 2. Project 2: RAG Service with GPU

**Purpose:** Demonstrate GPU workloads for AI/ML (embeddings, inference)

**Technology Stack:**
- FastAPI
- LangChain (RAG framework)
- Sentence Transformers (embeddings)
- FAISS (vector database)
- (Initially) NVIDIA L4 GPU

**Endpoints:**
- `GET /` - Service info
- `GET /health` - Health check
- `POST /query` - RAG query endpoint
- `POST /index` - Index documents

**Why GPU? (Originally)**
- Fast embedding generation (1000x faster than CPU)
- Real-time inference
- Cost-effective for high throughput

**Why CPU Now?**
- GPU quota requires approval from Google
- CPU works for demo/testing (just slower)
- Can upgrade to GPU later without code changes

**Configuration (CPU Mode):**
- **Memory:** 4GB (for embeddings in RAM)
- **CPU:** 2 cores
- **Scale:** 0-2 instances (quota-friendly)
- **Ingress:** Internal only

### 3. Project 3: Another Microservice

**Purpose:** Demonstrate multi-service architecture patterns

**Technology Stack:**
- FastAPI
- Python 3.11

**Endpoints:**
- `GET /` - Service info
- `GET /health` - Health check
- `GET /status` - Status endpoint

**Configuration:**
- Same as Project 1 (512MB, 1 CPU)

### 4. Shared Libraries (`shared_libs/`)

**Purpose:** Centralized utilities for all services

**Components:**

#### `JSONLogger`
**What:** Structured JSON logging with correlation IDs  
**Why:**
- Cloud Logging requires JSON for proper indexing
- Correlation IDs trace requests across services
- Structured data enables powerful queries

**Example:**
```python
logger = JSONLogger("project_1", project_id="my-project")
logger.info("Request received", user_id="123", correlation_id="abc")
# Output: {"message": "Request received", "user_id": "123", "correlation_id": "abc", "timestamp": "..."}
```

#### `CloudMonitoringClient`
**What:** Send custom metrics to Cloud Monitoring  
**Why:**
- Track business metrics (not just system metrics)
- Create custom dashboards
- Set up alerts on important events

**Example:**
```python
monitor = CloudMonitoringClient("project_1")
monitor.record_metric("requests_total", 1, labels={"endpoint": "/health"})
```

#### `@monitor_request` Decorator
**What:** Automatic request timing and error tracking  
**Why:**
- Zero-boilerplate observability
- Consistent metrics across services
- Automatically tracks duration, status codes, errors

**Example:**
```python
@monitor_request("api_endpoint")
async def my_endpoint():
    # Automatically tracked!
    return {"status": "ok"}
```

#### Correlation ID Helpers
**What:** Generate and propagate request IDs  
**Why:**
- Trace requests across service boundaries
- Debug distributed systems
- Link logs from multiple services

**Flow:**
```
Request → Gateway → Project 1 → Project 2
   ID: abc123 → abc123 → abc123
All logs have correlation_id="abc123"
```

### 5. API Gateway Configuration

**File:** `infrastructure/api-gateway-config.yaml`

**What:** OpenAPI 2.0 spec defining routes and authentication

**Key Sections:**

#### Security Definitions
```yaml
securityDefinitions:
  firebase:
    type: "oauth2"
    x-google-issuer: "https://securetoken.google.com/YOUR-PROJECT-ID"
    x-google-audiences: "YOUR-PROJECT-ID"
```

**What This Does:**
- Validates Firebase ID tokens on every request
- Rejects unauthenticated requests with 401
- Extracts user info from JWT token

#### Path Routing
```yaml
paths:
  /p1/health:
    get:
      x-google-backend:
        address: https://project-1-xxx.us-central1.run.app/health
        path_translation: CONSTANT_ADDRESS
```

**What This Does:**
- Maps `/p1/health` → actual Cloud Run URL
- `CONSTANT_ADDRESS` means use the full address as-is
- Backend service never sees the gateway URL

**Why CONSTANT_ADDRESS?**
- Simple and explicit
- No path rewriting complexity
- Easy to debug

---

## 🤖 Automation & CI/CD

### GitHub Actions Workflows

We have **6 automated workflows** that handle everything:

#### 1. `deploy-project-1.yml`
**Triggers:** 
- Push to `main` branch with changes in `project_1/` or `shared_libs/`
- Manual trigger

**What It Does:**
1. Detects which files changed (surgical deployment)
2. Builds Docker image with `shared_libs` embedded
3. Pushes to Artifact Registry
4. Deploys to Cloud Run
5. Triggers API Gateway update (if successful)

**Why Surgical Deployment?**
- Don't rebuild unchanged services (saves time & cost)
- Faster deployments (30 seconds vs 5 minutes)
- Less risk (only touch what changed)

**Key Steps:**
```yaml
- name: Check for changes
  # Only proceed if project_1/ or shared_libs/ changed
  
- name: Build Docker image
  # Build with shared_libs included
  
- name: Deploy to Cloud Run
  # Update only this service
```

#### 2. `deploy-project-2.yml`
**Same pattern as Project 1**, but with:
- GPU configuration (originally)
- Larger memory/CPU allocations
- Now runs in CPU-only mode (no GPU quota)

#### 3. `deploy-project-3.yml`
**Same pattern as Project 1**

#### 4. `tag-shared-libs.yml`
**Triggers:**
- Push to `main` with changes in `shared_libs/`

**What It Does:**
1. Detects version from `shared_libs/utils.py`
2. Creates Git tag (e.g., `v1.0.0`)
3. Pushes tag to GitHub

**Why Tag Shared Libs?**
- Immutable versions (v1.0.0 never changes)
- Services can pin to specific versions
- Rollback capability (revert to v0.9.0)
- Semantic versioning (breaking changes = major version bump)

**Permissions Fix:**
```yaml
permissions:
  contents: write  # REQUIRED to push tags
```

**Without this:** Got `403 Forbidden` errors

#### 5. `deploy-api-gateway.yml`
**Triggers:**
- After any service deployment succeeds
- Manual trigger
- Push to `infrastructure/`

**What It Does:**
1. Gets Cloud Run URLs for all 3 services
2. Replaces placeholders in `api-gateway-config.yaml`
3. Creates new API Gateway config (timestamped)
4. Updates gateway to use new config

**Why Auto-Deploy Gateway?**
- Services get new URLs after deployment
- Gateway must update to route to new URLs
- Fully automated (no manual updates)

**Complex Part: URL Replacement**
```bash
# If service URL is empty, keep placeholder
[ -z "$PROJECT1_URL" ] && PROJECT1_URL="https://project-1-placeholder"

# Replace placeholders with actual URLs
sed "s|https://project-1-placeholder|${PROJECT1_URL}|g"
```

**Why This Matters:**
- Project 2 might not be deployed (no GPU)
- Can't replace with empty string (invalid YAML)
- Keep placeholder = gateway works, just returns error for /p2

#### 6. `deploy-monitoring.yml`
**Triggers:** Manual only

**What It Does:**
1. Deploys Terraform configuration for monitoring
2. Creates Cloud Monitoring dashboard
3. Sets up alerting policies

**Why Manual?**
- Monitoring setup is one-time
- Changes are rare
- Avoid unnecessary Terraform runs (costly)

### Deployment Flow Diagram

```
┌──────────────────────────────────────────────────────────────┐
│  Developer pushes code to main branch                        │
└────────────────┬─────────────────────────────────────────────┘
                 │
                 ▼
┌──────────────────────────────────────────────────────────────┐
│  GitHub Actions: Detect changes                              │
│  • Changed: project_1/ ? → deploy-project-1.yml             │
│  • Changed: project_2/ ? → deploy-project-2.yml             │
│  • Changed: project_3/ ? → deploy-project-3.yml             │
│  • Changed: shared_libs/ ? → tag + deploy all               │
└────────────────┬─────────────────────────────────────────────┘
                 │
                 ▼
┌──────────────────────────────────────────────────────────────┐
│  Service Deployment (parallel)                               │
│  1. Authenticate with GCP (service account)                  │
│  2. Build Docker image                                       │
│  3. Push to Artifact Registry                                │
│  4. Deploy to Cloud Run                                      │
│  5. Wait for deployment success                              │
└────────────────┬─────────────────────────────────────────────┘
                 │
                 ▼
┌──────────────────────────────────────────────────────────────┐
│  API Gateway Update (automatic)                              │
│  1. Get new Cloud Run URLs                                   │
│  2. Update gateway config                                    │
│  3. Create new gateway version                               │
│  4. Route traffic to new version                             │
└────────────────┬─────────────────────────────────────────────┘
                 │
                 ▼
┌──────────────────────────────────────────────────────────────┐
│  Services live and accepting traffic! ✅                     │
│  Total time: 3-5 minutes per service                         │
└──────────────────────────────────────────────────────────────┘
```

---

## 📊 Observability Strategy

### Why Observability Matters

**Problem:** Microservices are distributed - failures can happen anywhere  
**Solution:** Comprehensive logging, tracing, and monitoring

### Three Pillars of Observability

#### 1. Logs (What Happened)

**Implementation:** JSON-structured logs with Cloud Logging

**Why JSON?**
- Cloud Logging indexes JSON fields automatically
- Easy to query: `jsonPayload.user_id="123"`
- Supports nested objects
- Machine-readable

**What We Log:**
```json
{
  "message": "Request processed",
  "level": "INFO",
  "timestamp": "2026-02-06T20:00:00Z",
  "service": "project_1",
  "correlation_id": "abc123",
  "user_id": "user_456",
  "duration_ms": 45,
  "status_code": 200
}
```

**Benefits:**
- Search by correlation ID → see entire request flow
- Filter by user → debug user-specific issues
- Aggregate by status_code → error rates

#### 2. Traces (How It Flowed)

**Implementation:** Cloud Trace with X-Cloud-Trace-Context headers

**What Is Tracing?**
- Follow a single request across multiple services
- See timing of each step
- Identify bottlenecks

**Example Trace:**
```
Request ID: abc123
├─ API Gateway     (5ms)
├─ Project 1       (45ms)
│  ├─ Database     (30ms)  ← Bottleneck!
│  └─ Processing   (10ms)
└─ Total: 50ms
```

**How It Works:**
```python
# Middleware extracts trace ID from header
trace_header = request.headers.get('X-Cloud-Trace-Context')
os.environ['HTTP_X_CLOUD_TRACE_CONTEXT'] = trace_header

# All logs automatically include trace ID
logger.info("Processing")  # Linked to trace!
```

#### 3. Metrics (How Much)

**Implementation:** Cloud Monitoring custom metrics

**What We Track:**
- **Request counts**: How many requests per second?
- **Error rates**: % of requests failing
- **Latency**: p50, p95, p99 response times
- **Resource usage**: CPU, memory, instances

**Custom Metrics:**
```python
@monitor_request("api_request")
async def my_endpoint():
    # Automatically tracks:
    # - request_count (counter)
    # - request_duration (histogram)
    # - request_errors (counter)
    pass
```

**Dashboard:**
We create a centralized dashboard showing:
- Request volume per service
- Error rates
- Response time percentiles
- Service health status

### Correlation IDs: The Secret Sauce

**Problem:** Request touches 3 services - how to link logs?

**Solution:** Correlation ID propagated through headers

**Flow:**
```
1. Gateway generates correlation_id="abc123"
2. Adds X-Correlation-ID: abc123 header
3. Project 1 receives, logs with correlation_id="abc123"
4. Project 1 calls Project 2, forwards header
5. Project 2 logs with same correlation_id="abc123"
6. Query logs: correlation_id="abc123" → see all 3 services!
```

**Benefits:**
- Debug distributed systems
- Trace user journeys
- Calculate true end-to-end latency

---

## 🔒 Security Implementation

### Defense in Depth

We implement **multiple layers** of security:

#### Layer 1: Network Isolation

**Service Configuration:**
```yaml
--ingress internal  # Only accessible from within GCP
```

**What This Means:**
- Services have no public IPs
- Cannot be accessed from internet directly
- Only API Gateway can reach them
- Even with the URL, external requests fail (404)

**Why Important:**
- Reduces attack surface (no direct service exposure)
- Forces all traffic through authenticated gateway
- Prevents accidental public exposure

#### Layer 2: Firebase Authentication

**Gateway Configuration:**
```yaml
security:
  - firebase: []  # All paths require Firebase auth
```

**How It Works:**
1. User authenticates with Firebase (email/password, Google, etc.)
2. Firebase issues JWT token (ID token)
3. Client sends token in `Authorization: Bearer <token>` header
4. Gateway validates token:
   - Signature valid?
   - Not expired?
   - Issued by our Firebase project?
5. If valid → forward to backend
6. If invalid → 401 Unauthorized

**What We Validate:**
- Token signature (cryptographic proof)
- Token expiration (1 hour default)
- Issuer matches our project
- Audience matches our project

**Benefits:**
- No authentication code in services (handled by gateway)
- Standardized auth across all endpoints
- Easy to add OAuth providers (Google, Facebook, etc.)

#### Layer 3: Service Account Permissions

**Principle of Least Privilege:**

**Service Account:** `github-actions@my-project.iam.gserviceaccount.com`

**Permissions (only what's needed):**
- `artifactregistry.admin` - Push Docker images
- `artifactregistry.writer` - Write to specific repository
- `run.admin` - Deploy Cloud Run services
- `iam.serviceAccountUser` - Act as service account
- `apigateway.admin` - Manage API Gateway
- `servicemanagement.admin` - Manage API configs
- `monitoring.admin` - Create dashboards

**What We DON'T Grant:**
- ❌ Owner/Editor (too broad)
- ❌ Storage admin (don't need it)
- ❌ Compute admin (not using VMs)

**Why Important:**
- If GitHub Actions compromised → limited blast radius
- Can't delete production data
- Can't access other GCP services

#### Layer 4: Secrets Management

**GitHub Secrets:**
- Service account key (base64 encoded)
- Firebase credentials
- GCP project ID

**Best Practices:**
- ✅ Never commit secrets to Git
- ✅ Base64 encode JSON keys (avoids special character issues)
- ✅ Rotate keys periodically
- ✅ Use separate service accounts per environment (dev/prod)

**How Secrets Flow:**
```
GitHub Secrets → GitHub Actions → GCP Auth → Services
     (encrypted)    (ephemeral)    (temporary)
```

#### Layer 5: Container Security

**Docker Best Practices:**
- Use official Python base image
- No root user (Cloud Run runs as non-root)
- Minimal dependencies
- No secrets in environment variables at build time

---

## 💰 Cost Optimization

### Scale-to-Zero Architecture

**Configuration:**
```yaml
--min-instances 0   # No instances when idle
--max-instances 10  # Burst capacity
```

**Cost Impact:**
- **Idle services:** $0/hour (no instances running)
- **Active services:** Pay only for request time
- **Burst traffic:** Auto-scale to handle load

**Example Cost Calculation:**
```
Project 1:
- 512MB memory, 1 CPU
- 1000 requests/day, 100ms each
- Total: 100 seconds/day CPU time
- Cost: ~$0.01/day = $0.30/month
```

### Surgical Deployments

**Problem:** Rebuilding all services on every change wastes time & money

**Solution:** Change detection
```yaml
- name: Check for changes
  run: |
    if git diff --name-only HEAD^ HEAD | grep -q "^project_1/"; then
      echo "project_1=true"
    fi
```

**Savings:**
- Changed 1 file → Deploy 1 service (30 seconds)
- Instead of → Deploy 3 services (5 minutes)
- **83% faster deployments**
- **Fewer build minutes** (GitHub Actions cost)

### Shared Libraries = Less Code

**Without Shared Libs:**
- 3 services × 200 lines of logging code = 600 lines
- Bug in logging → fix in 3 places
- Maintenance nightmare

**With Shared Libs:**
- 200 lines in `shared_libs/`
- Bug → fix once, redeploy all
- **DRY = maintainability = cost savings**

### Artifact Registry Optimization

**Strategy:**
- Tag images with Git SHA (immutable)
- Tag with `latest` (mutable, for quick rollback)
- No automatic cleanup (yet)

**Future Optimization:**
- Delete images older than 30 days
- Keep last 10 versions per service
- Could save on storage costs

---

## 🚀 Deployment Flow (Step-by-Step)

### Initial Setup (One-Time, 17 minutes)

1. **Create GCP Project** (2 min)
   ```bash
   gcloud projects create my-lean-hub-project
   gcloud config set project my-lean-hub-project
   ```

2. **Enable APIs** (2 min)
   ```bash
   gcloud services enable run.googleapis.com \
     artifactregistry.googleapis.com \
     apigateway.googleapis.com
   ```

3. **Create Artifact Registry Repository** (2 min)
   ```bash
   gcloud artifacts repositories create lean-hub \
     --repository-format=docker \
     --location=us-central1
   ```

4. **Create Service Account** (3 min)
   ```bash
   gcloud iam service-accounts create github-actions
   gcloud projects add-iam-policy-binding my-project \
     --member="serviceAccount:github-actions@my-project.iam.gserviceaccount.com" \
     --role="roles/artifactregistry.admin"
   # ... add other roles
   ```

5. **Create Service Account Key** (1 min)
   ```bash
   gcloud iam service-accounts keys create key.json \
     --iam-account=github-actions@my-project.iam.gserviceaccount.com
   cat key.json | base64 -w 0  # Copy this
   ```

6. **Setup Firebase** (5 min)
   - Create Firebase project (link to GCP project)
   - Enable Authentication → Email/Password
   - Get Web API key from settings

7. **Add GitHub Secrets** (2 min)
   - Repository → Settings → Secrets → Actions
   - Add all 8 secrets (GCP_PROJECT_ID, GCP_SA_KEY, Firebase keys)

**Total: 17 minutes**  
**After this: Everything is automated! ✨**

### Regular Deployment (Automatic, 3-5 minutes)

1. **Developer makes changes**
   ```bash
   # Edit code
   vim project_1/main.py
   
   # Commit and push
   git add project_1/
   git commit -m "Add new feature"
   git push origin main
   ```

2. **GitHub Actions triggers** (automatic)
   - Detects `project_1/` changed
   - Starts `deploy-project-1.yml`

3. **Build phase** (60 seconds)
   - Checkout code
   - Authenticate with GCP
   - Build Docker image
   - Push to Artifact Registry

4. **Deploy phase** (90 seconds)
   - Deploy to Cloud Run
   - Wait for health check
   - Shift traffic to new revision

5. **Gateway update** (120 seconds)
   - Get new Cloud Run URL
   - Update gateway config
   - Create new gateway version

6. **Done!** (automatic)
   - New code is live
   - Old revision kept for rollback
   - Logs available in Cloud Logging

**Total: 3-5 minutes from push to live**

---

## 🔍 Troubleshooting Guide

### Common Issues & Solutions

#### Issue 1: "Permission Denied" on Docker Push

**Error:**
```
denied: Permission artifactregistry.repositories.uploadArtifacts
```

**Cause:** Service account lacks permission on repository

**Solution:**
```bash
gcloud artifacts repositories add-iam-policy-binding lean-hub \
  --location=us-central1 \
  --member="serviceAccount:github-actions@my-project.iam.gserviceaccount.com" \
  --role="roles/artifactregistry.writer"
```

#### Issue 2: Service Returns 404

**Error:** All endpoints return 404 Not Found

**Possible Causes:**
1. **FastAPI app not starting**
   - Check logs: `gcloud logging read "resource.type=cloud_run_revision"`
   - Look for Python import errors

2. **Service has --ingress internal**
   - This is correct! Should only be accessible via gateway
   - Test from Cloud Shell with auth token

3. **Wrong path in gateway config**
   - Check `api-gateway-config.yaml`
   - Verify URL matches actual Cloud Run URL

#### Issue 3: Gateway Returns 401 Unauthorized

**Error:** API Gateway rejects requests with 401

**Possible Causes:**
1. **No Firebase token provided**
   - Get token: Authenticate with Firebase SDK
   - Add header: `Authorization: Bearer <token>`

2. **Token expired**
   - Firebase tokens expire after 1 hour
   - Get fresh token

3. **Wrong Firebase project in gateway config**
   - Check `YOUR-FIREBASE-PROJECT-ID` replaced correctly
   - Must match actual Firebase project ID

#### Issue 4: Gateway Deployment Fails with "Invalid YAML"

**Error:**
```
Could not read JSON or YAML from config file
```

**Cause:** Sed replacement created invalid YAML (empty URLs)

**Solution:** Workflow now handles this automatically
```bash
# If URL empty, keep placeholder
[ -z "$PROJECT1_URL" ] && PROJECT1_URL="https://project-1-placeholder"
```

#### Issue 5: Service Won't Scale (Stuck at 0 Instances)

**Possible Causes:**
1. **Cold start timeout**
   - Service takes >60 seconds to start
   - Increase startup timeout

2. **Health check failing**
   - Check `/health` endpoint works
   - Verify port 8080 listening

3. **Out of quota**
   - Check quotas: Cloud Console → IAM → Quotas
   - Request increase if needed

---

## 📚 Key Learnings & Best Practices

### What Worked Well ✅

1. **Automation First**
   - 100% automated deployments saved hours of manual work
   - Caught errors early (fail-fast)
   - Consistent deployments (no human error)

2. **Shared Libraries**
   - DRY principle reduced code duplication
   - Consistent logging/monitoring across services
   - Easy to maintain and update

3. **API Gateway Pattern**
   - Single entry point simplified architecture
   - Centralized authentication (one place to manage)
   - Easy to add/remove services

4. **Observability from Day 1**
   - JSON logging made debugging easy
   - Correlation IDs traced requests across services
   - Custom metrics provided business insights

### What We'd Do Differently 🔄

1. **GPU Quota**
   - Should have requested GPU quota earlier
   - CPU-only mode works but is slower
   - Lesson: Plan for quotas before implementation

2. **Environment Separation**
   - Currently only `main` branch (production)
   - Should add `dev` branch → dev environment
   - Allows testing before production

3. **Monitoring Alerts**
   - Have dashboard but no alerts yet
   - Should add: Error rate > 5% → page on-call
   - Proactive vs reactive

4. **Cost Monitoring**
   - Should set up budget alerts
   - Track cost per service
   - Identify optimization opportunities

### Anti-Patterns to Avoid ❌

1. **❌ Don't commit secrets to Git**
   - Use GitHub Secrets / Secret Manager
   - Rotate secrets periodically

2. **❌ Don't grant broad IAM roles**
   - Use least privilege principle
   - Grant only what's needed

3. **❌ Don't skip observability**
   - Add logging from day 1
   - Debugging without logs is painful

4. **❌ Don't deploy all services on every change**
   - Use surgical deployments
   - Save time and money

5. **❌ Don't use public ingress for internal services**
   - Always use API Gateway as entry point
   - Internal ingress = defense in depth

---

## 🎓 Team Training Recommendations

### For New Team Members

**Week 1: Understand the Architecture**
- Read this document
- Review architecture diagram
- Understand microservices pattern
- Learn API Gateway concept

**Week 2: Deploy Your First Service**
- Fork this repo
- Follow SECRETS_SETUP_GUIDE.md
- Deploy all 3 services
- Test with Firebase auth

**Week 3: Make a Change**
- Add new endpoint to Project 1
- Push to main
- Watch GitHub Actions deploy
- Test your endpoint via gateway

**Week 4: Troubleshoot an Issue**
- Introduce a bug
- Use Cloud Logging to find it
- Use Cloud Trace to trace request
- Fix and redeploy

### For Architects

**Study These Patterns:**
- Microservices architecture
- API Gateway pattern
- Shared library versioning
- Distributed tracing
- Infrastructure as Code (IaC)

**Recommended Reading:**
- "Building Microservices" by Sam Newman
- "Site Reliability Engineering" by Google
- "Designing Data-Intensive Applications" by Martin Kleppmann

---

## 📞 Support & Feedback

### Getting Help

1. **Check Documentation**
   - This file (ARCHITECTURE.md)
   - OBSERVABILITY.md
   - SECRETS_SETUP_GUIDE.md
   - QUICK_REFERENCE.md

2. **Check Logs**
   - Cloud Logging: `gcloud logging read`
   - GitHub Actions: Check workflow runs
   - Cloud Console: Logging Explorer

3. **Ask the Team**
   - Create GitHub Issue
   - Tag with `question` label
   - Provide error logs and context

### Providing Feedback

**Found a bug?** → Create GitHub Issue with `bug` label  
**Have an idea?** → Create GitHub Issue with `enhancement` label  
**Want to contribute?** → Fork, make changes, submit Pull Request

---

## 🔄 Future Roadmap

### Phase 1: Production-Ready (Next 3 Months)
- [ ] Add `dev` environment (separate GCP project)
- [ ] Set up monitoring alerts (PagerDuty integration)
- [ ] Add integration tests (test gateway → service flow)
- [ ] Implement graceful degradation (fallbacks for service failures)

### Phase 2: Scale & Performance (Months 4-6)
- [ ] Request GPU quota for Project 2
- [ ] Add Redis caching layer
- [ ] Implement rate limiting per user
- [ ] Add load testing (Locust or k6)

### Phase 3: Enterprise Features (Months 7-12)
- [ ] Multi-region deployment (high availability)
- [ ] Database integration (Cloud SQL)
- [ ] Message queue (Pub/Sub for async processing)
- [ ] Advanced monitoring (custom SLOs/SLIs)

---

## ✅ Conclusion

**What We Built:**
A production-grade microservices platform with:
- ✅ 3 independent services
- ✅ Unified API Gateway with Firebase Auth
- ✅ 100% automated deployments
- ✅ Comprehensive observability
- ✅ Security-first architecture
- ✅ Cost-optimized scaling

**Why This Approach:**
- **Scalability**: Each service scales independently
- **Reliability**: Fault isolation and automated deployments
- **Security**: Multiple layers of defense
- **Maintainability**: Shared libraries and consistent patterns
- **Observability**: See everything happening in real-time
- **Cost-Effective**: Scale-to-zero and efficient resource usage

**Key Takeaway:**
This architecture demonstrates **enterprise best practices** while remaining **simple enough to understand and maintain**. It's not over-engineered, but it's not naive either. It's the sweet spot for modern cloud applications.

**Questions?** Review this document, check the other docs, or reach out to the team!

---

**Document Version:** 1.0  
**Last Updated:** February 6, 2026  
**Maintainer:** DevOps Team  
**Review Cycle:** Monthly
