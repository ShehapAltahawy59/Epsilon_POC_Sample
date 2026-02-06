# 🔧 Complete Guide: How to Get Every Value for .env File

**Step-by-step guide to determine and collect all configuration values for the `.env` file**

Time required: **10 minutes**

---

## 📋 What is the .env File?

The `.env` file in the **root directory** contains **non-sensitive configuration** that is:
- ✅ **Committed to Git** (safe to share publicly)
- ✅ **Used to configure GitHub Actions workflows**
- ✅ **Defines resource settings** (regions, service names, memory, CPU, etc.)

**Location:** `Epsilon_POC_Sample/.env`

**⚠️ Important:** This guide is for the **root .env file** (deployment config), NOT project-specific .env files for local development.

---

## 🎯 Values You Need to Determine

| Variable | Type | How to Get It |
|----------|------|---------------|
| `GCP_REGION` | GCP Region | Choose from GCP regions list |
| `GAR_LOCATION` | GCP Region | Usually same as GCP_REGION |
| `GAR_REPOSITORY` | Name you choose | Your Docker repository name |
| `SERVICE_PROJECT_1/2/3` | Name you choose | Your Cloud Run service names |
| `API_GATEWAY_NAME` | Name you choose | Your API Gateway name |
| `STANDARD_MEMORY/CPU` | Resource limits | Based on workload needs |
| `RAG_MEMORY/CPU/GPU` | Resource limits | Based on AI model needs |

---

## 📝 Step-by-Step: Get Each Value

### STEP 1: Choose GCP Region (2 minutes)

#### What is it?
The Google Cloud region where your Cloud Run services will be deployed.

#### How to choose:

**Option A: List all available regions**
```bash
gcloud compute regions list

# Output shows:
# NAME                CPUS  DISKS_GB  STATUS
# us-central1         0/24  0/10240   UP
# us-east1            0/24  0/10240   UP
# europe-west1        0/24  0/10240   UP
# asia-northeast1     0/24  0/10240   UP
```

**Option B: Check Cloud Run regions**
```bash
gcloud run regions list

# Output:
# us-central1
# us-east1
# us-east4
# us-west1
# europe-west1
# asia-east1
# asia-northeast1
```

**Factors to consider:**
- 🌍 **Proximity to users** - Choose region closest to your users (lower latency)
- 💰 **Cost** - Some regions cost more (check [GCP Pricing](https://cloud.google.com/run/pricing))
- 🎮 **GPU availability** - If using Project 2 RAG, check GPU regions:
  ```bash
  gcloud compute accelerator-types list --filter="zone:us-central1"
  ```

**Recommended regions:**
- **USA:** `us-central1` (Iowa) - Cheapest, good for testing
- **Europe:** `europe-west1` (Belgium) - Low latency for EU users
- **Asia:** `asia-northeast1` (Tokyo) - Low latency for Asian users

**✅ Add to .env:**
```bash
GCP_REGION=us-central1
```

---

### STEP 2: Set Artifact Registry Location (1 minute)

#### What is it?
Where Docker images are stored. Usually the **same as GCP_REGION**.

#### How to determine:

**Best practice:** Use the same region as your Cloud Run services for faster deployments.

```bash
# Same as GCP_REGION
GAR_LOCATION=us-central1
```

**Why same region?**
- ✅ Faster image pulls (images stored near services)
- ✅ Lower network costs (no cross-region transfer)
- ✅ Simpler configuration

**✅ Add to .env:**
```bash
GAR_LOCATION=us-central1
```

---

### STEP 3: Choose Docker Repository Name (1 minute)

#### What is it?
The name of your Artifact Registry repository where Docker images are stored.

#### How to choose:

**Format:** Lowercase letters, numbers, and hyphens only

**Examples:**
- `lean-hub` (recommended - short and descriptive)
- `my-app-images`
- `prod-services`
- `company-microservices`

**Check if name is available:**
```bash
# List existing repositories
gcloud artifacts repositories list --location=us-central1

# If empty or name not listed, it's available
```

**Create the repository:**
```bash
gcloud artifacts repositories create lean-hub \
  --repository-format=docker \
  --location=us-central1 \
  --description="Docker images for Lean Hub services"

# You'll see: "Created repository [lean-hub]"
```

**✅ Add to .env:**
```bash
GAR_REPOSITORY=lean-hub
```

---

### STEP 4: Choose Service Names (2 minutes)

#### What are they?
The names of your Cloud Run services. These appear in GCP Console and URLs.

#### How to choose:

**Format:** Lowercase letters, numbers, and hyphens. Must start with letter.

**Current recommendations:**
```bash
SERVICE_PROJECT_1=project-1          # Main API service
SERVICE_PROJECT_2=project-2-rag      # RAG service with GPU
SERVICE_PROJECT_3=project-3          # Additional service
```

**Naming patterns to consider:**

**Option A: Descriptive names**
```bash
SERVICE_PROJECT_1=api-gateway
SERVICE_PROJECT_2=rag-engine
SERVICE_PROJECT_3=data-processor
```

**Option B: Environment-specific**
```bash
SERVICE_PROJECT_1=prod-api
SERVICE_PROJECT_2=prod-rag
SERVICE_PROJECT_3=prod-core
```

**Option C: Team-based**
```bash
SERVICE_PROJECT_1=team-a-service
SERVICE_PROJECT_2=ml-service
SERVICE_PROJECT_3=team-b-service
```

**Check availability:**
```bash
# List existing Cloud Run services
gcloud run services list --region=us-central1

# If name not listed, it's available
```

**✅ Add to .env:**
```bash
SERVICE_PROJECT_1=project-1
SERVICE_PROJECT_2=project-2-rag
SERVICE_PROJECT_3=project-3
```

---

### STEP 5: Choose API Gateway Names (1 minute)

#### What are they?
The names for your API Gateway resources (gateway, API, config).

#### How to choose:

**Format:** Lowercase letters, numbers, and hyphens

**Current recommendations:**
```bash
API_GATEWAY_NAME=lean-hub-gateway      # The gateway itself
API_GATEWAY_API=lean-hub-api           # The API definition
API_GATEWAY_CONFIG=lean-hub-config     # The configuration
```

**Naming pattern:** Use your app name as prefix

```bash
# For app named "my-app"
API_GATEWAY_NAME=my-app-gateway
API_GATEWAY_API=my-app-api
API_GATEWAY_CONFIG=my-app-config
```

**Check availability:**
```bash
# List existing API Gateways
gcloud api-gateway gateways list

# If name not listed, it's available
```

**✅ Add to .env:**
```bash
API_GATEWAY_NAME=lean-hub-gateway
API_GATEWAY_API=lean-hub-api
API_GATEWAY_CONFIG=lean-hub-config
```

---

### STEP 6: Determine Resource Limits - Standard Services (2 minutes)

#### What are they?
Memory and CPU allocated to Project 1 and Project 3 (standard FastAPI services).

#### How to determine:

**Memory (`STANDARD_MEMORY`):**

**Starting point:** `512Mi` (512 MB) - Good for simple APIs

**Indicators to increase:**
- ❌ Service crashes with OOM (Out of Memory)
- ❌ Cold starts are slow
- ❌ Processing large data in memory

**Options:**
- `256Mi` - Minimal (very light APIs)
- `512Mi` - **Recommended** for FastAPI services
- `1Gi` - APIs with moderate data processing
- `2Gi` - APIs with heavy data processing

**CPU (`STANDARD_CPU`):**

**Starting point:** `1` - One CPU core

**Options:**
- `1` - **Recommended** for most APIs
- `2` - High-throughput APIs
- `4` - CPU-intensive processing

**Max/Min Instances:**

```bash
STANDARD_MAX_INSTANCES=10     # Maximum concurrent instances (prevents runaway costs)
STANDARD_MIN_INSTANCES=0      # Minimum instances (0 = scale to zero when idle)
```

**Cost consideration:**
- `MIN_INSTANCES=0` - Cheapest, but cold starts
- `MIN_INSTANCES=1` - Always ready, but always billed

**✅ Add to .env:**
```bash
STANDARD_MEMORY=512Mi
STANDARD_CPU=1
STANDARD_MAX_INSTANCES=10
STANDARD_MIN_INSTANCES=0
```

---

### STEP 7: Determine Resource Limits - RAG Service (2 minutes)

#### What are they?
Resources for Project 2 (RAG service with GPU for AI model).

#### How to determine:

**Memory (`RAG_MEMORY`):**

**Starting point:** `16Gi` (16 GB) - Required for most AI models

**Why so much?**
- AI models are large (several GB)
- Vector databases need memory
- Embedding generation is memory-intensive

**Options:**
- `8Gi` - Small models
- `16Gi` - **Recommended** for gemini-pro, medium models
- `32Gi` - Large models, extensive vector DB

**CPU (`RAG_CPU`):**

**Starting point:** `4` - Four CPU cores

**Why so many?**
- Preprocessing before GPU
- Vector database queries
- Concurrent request handling

**Options:**
- `2` - Minimal
- `4` - **Recommended**
- `8` - High throughput

**GPU Configuration:**

```bash
RAG_GPU_COUNT=1              # Number of GPUs (usually 1)
RAG_GPU_TYPE=nvidia-l4       # GPU model
```

**Available GPU types:**
```bash
# Check available GPUs in your region
gcloud compute accelerator-types list --filter="zone:us-central1"

# Common options:
# nvidia-l4          - Best value, modern (Recommended)
# nvidia-tesla-t4    - Older, cheaper
# nvidia-tesla-v100  - Faster, more expensive
```

**Max/Min Instances:**

```bash
RAG_MAX_INSTANCES=10     # Limit to prevent GPU cost explosion
RAG_MIN_INSTANCES=0      # Scale to zero (GPUs are expensive!)
```

**⚠️ Cost Warning:**
- GPU instances cost **significantly more** ($0.35-$2.48 per hour)
- Always set `MIN_INSTANCES=0` to avoid idle costs
- Set low `MAX_INSTANCES` (e.g., 3-5 for production)

**✅ Add to .env:**
```bash
RAG_MEMORY=16Gi
RAG_CPU=4
RAG_GPU_COUNT=1
RAG_GPU_TYPE=nvidia-l4
RAG_MAX_INSTANCES=10
RAG_MIN_INSTANCES=0
```

---

### STEP 8: Configure Security Settings (1 minute)

#### What are they?
Security and networking settings for Cloud Run services.

#### Recommended values:

```bash
# Only allow access from API Gateway (not internet)
INGRESS_INTERNAL_ONLY=true

# Allow unauthenticated (API Gateway handles auth)
ALLOW_UNAUTHENTICATED=true

# Request timeout (in seconds)
REQUEST_TIMEOUT=300
```

**Why these values?**

**`INGRESS_INTERNAL_ONLY=true`:**
- ✅ Services only accessible via API Gateway
- ✅ Cannot be accessed directly from internet
- ✅ Enhanced security

**`ALLOW_UNAUTHENTICATED=true`:**
- ✅ API Gateway handles authentication
- ✅ Services trust requests from gateway
- ✅ Simpler service code

**`REQUEST_TIMEOUT=300`:**
- ✅ 5 minutes max for long-running AI operations
- ✅ Prevents hanging requests
- ✅ Adjust based on your needs (max 3600 seconds)

**✅ Add to .env:**
```bash
INGRESS_INTERNAL_ONLY=true
ALLOW_UNAUTHENTICATED=true
REQUEST_TIMEOUT=300
```

---

### STEP 9: Set Development & Monitoring (1 minute)

#### What are they?
Settings for local development and observability.

#### Recommended values:

```bash
# Local Development
LOCAL_PORT=8080
LOG_LEVEL=INFO
DEBUG_MODE=false

# Cloud Monitoring
ENABLE_CLOUD_LOGGING=true
ENABLE_CLOUD_MONITORING=true
LOG_RETENTION_DAYS=30

# Versioning
DEFAULT_SHARED_LIB_VERSION=v1.0.0
```

**Log levels:**
- `DEBUG` - Very verbose, for troubleshooting
- `INFO` - **Recommended** - Normal operations
- `WARNING` - Only warnings and errors
- `ERROR` - Only errors

**Log retention:**
- `7` days - Minimal, cheapest
- `30` days - **Recommended** - Good balance
- `90` days - Compliance requirements
- `365` days - Long-term analysis

**✅ Add to .env:**
```bash
LOCAL_PORT=8080
LOG_LEVEL=INFO
DEBUG_MODE=false
ENABLE_CLOUD_LOGGING=true
ENABLE_CLOUD_MONITORING=true
LOG_RETENTION_DAYS=30
DEFAULT_SHARED_LIB_VERSION=v1.0.0
```

---

## ✅ Complete .env File Template

After following all steps, your `.env` file should look like this:

```bash
# ============================================
# GCP Configuration
# ============================================
GCP_REGION=us-central1
GAR_LOCATION=us-central1
GAR_REPOSITORY=lean-hub

# ============================================
# Service Names
# ============================================
SERVICE_PROJECT_1=project-1
SERVICE_PROJECT_2=project-2-rag
SERVICE_PROJECT_3=project-3

# ============================================
# API Gateway Configuration
# ============================================
API_GATEWAY_NAME=lean-hub-gateway
API_GATEWAY_API=lean-hub-api
API_GATEWAY_CONFIG=lean-hub-config

# ============================================
# Resource Configuration - Standard Services
# ============================================
STANDARD_MEMORY=512Mi
STANDARD_CPU=1
STANDARD_MAX_INSTANCES=10
STANDARD_MIN_INSTANCES=0

# ============================================
# Resource Configuration - RAG Service
# ============================================
RAG_MEMORY=16Gi
RAG_CPU=4
RAG_GPU_COUNT=1
RAG_GPU_TYPE=nvidia-l4
RAG_MAX_INSTANCES=10
RAG_MIN_INSTANCES=0

# ============================================
# Security Settings
# ============================================
INGRESS_INTERNAL_ONLY=true
ALLOW_UNAUTHENTICATED=true
REQUEST_TIMEOUT=300

# ============================================
# Development Settings
# ============================================
LOCAL_PORT=8080
LOG_LEVEL=INFO
DEBUG_MODE=false

# ============================================
# Monitoring
# ============================================
ENABLE_CLOUD_LOGGING=true
ENABLE_CLOUD_MONITORING=true
LOG_RETENTION_DAYS=30

# ============================================
# Versioning
# ============================================
DEFAULT_SHARED_LIB_VERSION=v1.0.0
```

---

## 🔄 After Creating .env: Update Workflows

**⚠️ IMPORTANT:** The `.env` file is a template. You must update workflow files to match!

**Files to update:**
- `.github/workflows/deploy-project-1.yml`
- `.github/workflows/deploy-project-2.yml`
- `.github/workflows/deploy-project-3.yml`

**What to update in each workflow:**

```yaml
env:
  # Update these to match .env
  GCP_REGION: us-central1           # From GCP_REGION
  GAR_LOCATION: us-central1         # From GAR_LOCATION
  GAR_REPOSITORY: lean-hub          # From GAR_REPOSITORY
  SERVICE_NAME: project-1           # From SERVICE_PROJECT_1/2/3
```

**And in the deployment step:**

```yaml
--memory 512Mi              # From STANDARD_MEMORY or RAG_MEMORY
--cpu 1                     # From STANDARD_CPU or RAG_CPU
--max-instances 10          # From STANDARD_MAX_INSTANCES or RAG_MAX_INSTANCES
--min-instances 0           # From STANDARD_MIN_INSTANCES or RAG_MIN_INSTANCES
```

---

## 💰 Cost Estimation Based on Your .env

**Project 1 & 3 (Standard Services):**
- Memory: 512Mi
- CPU: 1
- **Cost:** ~$0.05/hour per instance when running
- **With MIN_INSTANCES=0:** Only pay when handling requests

**Project 2 (RAG Service):**
- Memory: 16Gi
- CPU: 4
- GPU: 1x NVIDIA L4
- **Cost:** ~$0.50-1.00/hour per instance when running
- **With MIN_INSTANCES=0:** Only pay when handling requests

**Monthly estimate (low traffic):**
- 100 requests/day, average 1 second each
- Standard services: **~$0.01/month**
- RAG service: **~$0.05/month**
- **Total: <$1/month**

**Monthly estimate (moderate traffic):**
- 10,000 requests/day
- Standard services: **~$5/month**
- RAG service: **~$20/month**
- **Total: ~$25/month**

---

## 🆘 Troubleshooting

### Issue: "Region does not support GPUs"

**Solution:**
```bash
# Check GPU availability in your region
gcloud compute accelerator-types list --filter="zone:us-central1"

# If no GPUs, change region:
GCP_REGION=us-central1
```

**Regions with L4 GPUs:**
- us-central1, us-west1, us-east1, europe-west1, asia-southeast1

### Issue: "Repository not found" during deployment

**Solution:**
```bash
# Create the Artifact Registry repository
gcloud artifacts repositories create lean-hub \
  --repository-format=docker \
  --location=us-central1
```

### Issue: "Service name already exists"

**Solution:** Choose a different name or delete the existing service:
```bash
# Delete existing service
gcloud run services delete project-1 --region=us-central1

# Or choose new name in .env
SERVICE_PROJECT_1=project-1-v2
```

### Issue: Memory/CPU limits causing errors

**Symptoms:**
- Service crashes
- "exceeded memory limit"
- Slow performance

**Solution:** Increase resources in `.env` and workflow:
```bash
# For standard services
STANDARD_MEMORY=1Gi      # Was 512Mi
STANDARD_CPU=2           # Was 1

# For RAG service
RAG_MEMORY=32Gi          # Was 16Gi
```

---

## 🔗 Next Steps

After completing your `.env` file:

1. ✅ **Update all workflow files** to match .env values
2. ✅ **Create Artifact Registry repository** (Step 3)
3. ✅ **Set up GitHub Secrets** - See [SECRETS_SETUP_GUIDE.md](SECRETS_SETUP_GUIDE.md)
4. ✅ **Commit .env to Git**
   ```bash
   git add .env
   git commit -m "Add deployment configuration"
   git push

Your `.env` file has these sections:

### 1️⃣ **GCP Configuration**
```bash
GCP_REGION=us-central1        # Where to deploy Cloud Run services
GAR_LOCATION=us-central1      # Where Artifact Registry is located
GAR_REPOSITORY=lean-hub       # Docker image repository name
```

**How workflows use it:**
```yaml
# In .github/workflows/deploy-project-1.yml
env:
  GCP_REGION: us-central1           # Hardcoded from .env
  GAR_LOCATION: us-central1         # Hardcoded from .env
  GAR_REPOSITORY: lean-hub          # Hardcoded from .env
```

### 2️⃣ **Service Names**
```bash
SERVICE_PROJECT_1=project-1
SERVICE_PROJECT_2=project-2-rag
SERVICE_PROJECT_3=project-3
```

**How workflows use it:**
```yaml
# In .github/workflows/deploy-project-1.yml
env:
  SERVICE_NAME: project-1           # Hardcoded from .env
```

### 3️⃣ **API Gateway Configuration**
```bash
API_GATEWAY_NAME=lean-hub-gateway
API_GATEWAY_API=lean-hub-api
API_GATEWAY_CONFIG=lean-hub-config
```

**Used when deploying the API Gateway** via `infrastructure/deploy-gateway.sh`

### 4️⃣ **Resource Configuration**
```bash
# Standard Services (Project 1 & 3)
STANDARD_MEMORY=512Mi
STANDARD_CPU=1
STANDARD_MAX_INSTANCES=10
STANDARD_MIN_INSTANCES=0

# RAG Service (Project 2)
RAG_MEMORY=16Gi
RAG_CPU=4
RAG_GPU_COUNT=1
RAG_GPU_TYPE=nvidia-l4
```

**How workflows use it:**
```yaml
# In .github/workflows/deploy-project-1.yml
--memory 512Mi          # From STANDARD_MEMORY
--cpu 1                 # From STANDARD_CPU
--max-instances 10      # From STANDARD_MAX_INSTANCES
```

### 5️⃣ **Security Settings**
```bash
INGRESS_INTERNAL_ONLY=true         # Services only accessible via API Gateway
ALLOW_UNAUTHENTICATED=true         # API Gateway handles auth
REQUEST_TIMEOUT=300                # Request timeout in seconds
```

### 6️⃣ **Development & Monitoring**
```bash
LOCAL_PORT=8080
LOG_LEVEL=INFO
DEBUG_MODE=false
ENABLE_CLOUD_LOGGING=true
ENABLE_CLOUD_MONITORING=true
LOG_RETENTION_DAYS=30
```

---

## 🔄 How Workflows Use the .env File

**Current Implementation:** Values are **hardcoded directly in workflow files**

```yaml
# Example: .github/workflows/deploy-project-1.yml
env:
  # These values come from .env but are hardcoded in the workflow
  GCP_REGION: us-central1
  GAR_LOCATION: us-central1
  GAR_REPOSITORY: lean-hub
  SERVICE_NAME: project-1
```

**Why hardcoded?**
- GitHub Actions doesn't automatically load `.env` files
- Values are stable and rarely change
- Makes workflows self-contained and explicit

---

## ✏️ How to Modify Configuration

### Step 1: Update the .env File

Edit `Epsilon_POC_Sample/.env`:

```bash
# Change deployment region
GCP_REGION=europe-west1           # Was: us-central1
GAR_LOCATION=europe-west1         # Was: us-central1

# Change service name
SERVICE_PROJECT_1=api-gateway     # Was: project-1

# Increase resources for standard services
STANDARD_MEMORY=1Gi               # Was: 512Mi
STANDARD_CPU=2                    # Was: 1
```

### Step 2: Update ALL Workflow Files

You must manually update **each workflow** to match:

**Files to update:**
- `.github/workflows/deploy-project-1.yml`
- `.github/workflows/deploy-project-2.yml`
- `.github/workflows/deploy-project-3.yml`

**Example change in deploy-project-1.yml:**

```yaml
env:
  # Update these to match .env
  GCP_REGION: europe-west1        # Changed
  GAR_LOCATION: europe-west1      # Changed
  GAR_REPOSITORY: lean-hub
  SERVICE_NAME: api-gateway       # Changed
```

**And update the deployment step:**

```yaml
- name: Deploy to Cloud Run
  run: |
    gcloud run deploy api-gateway \    # Changed service name
      --region europe-west1 \           # Changed region
      --memory 1Gi \                    # Changed memory
      --cpu 2 \                         # Changed CPU
```

### Step 3: Commit and Push

```bash
git add .env .github/workflows/
git commit -m "Update deployment configuration"
git push origin main
```

---

## 📋 Common Configuration Changes

### Change Deployment Region

**1. Update .env:**
```bash
GCP_REGION=asia-northeast1
GAR_LOCATION=asia-northeast1
```

**2. Update all 3 workflow files:**
```yaml
GCP_REGION: asia-northeast1
GAR_LOCATION: asia-northeast1
```

**3. Create Artifact Registry in new region:**
```bash
gcloud artifacts repositories create lean-hub \
  --repository-format=docker \
  --location=asia-northeast1
```

### Increase Project 1 Resources

**1. Update .env:**
```bash
STANDARD_MEMORY=1Gi
STANDARD_CPU=2
STANDARD_MAX_INSTANCES=20
```

**2. Update deploy-project-1.yml:**
```yaml
--memory 1Gi
--cpu 2
--max-instances 20
```

### Change Service Names

**1. Update .env:**
```bash
SERVICE_PROJECT_1=gateway-service
SERVICE_PROJECT_2=rag-service
SERVICE_PROJECT_3=core-service
```

**2. Update all 3 workflow files:**
```yaml
# In deploy-project-1.yml
SERVICE_NAME: gateway-service

# In deploy-project-2.yml
SERVICE_NAME: rag-service

# In deploy-project-3.yml
SERVICE_NAME: core-service
```

**3. Update API Gateway config:**
Edit `infrastructure/api-gateway-config.yaml` to point to new service names.

### Adjust GPU Configuration (Project 2)

**1. Update .env:**
```bash
RAG_GPU_COUNT=2
RAG_GPU_TYPE=nvidia-tesla-t4
RAG_MEMORY=32Gi
RAG_CPU=8
```

**2. Update deploy-project-2.yml:**
```yaml
--gpu 2
--gpu-type nvidia-tesla-t4
--memory 32Gi
--cpu 8
```

---

## 🔐 .env vs GitHub Secrets - Quick Reference

### What Goes in .env (Safe to Commit)
- ✅ GCP region names
- ✅ Service names
- ✅ Memory/CPU limits
- ✅ Timeout values
- ✅ Feature flags (DEBUG_MODE, etc.)
- ✅ Docker repository names

### What Goes in GitHub Secrets (NEVER Commit)
- ❌ GCP_PROJECT_ID
- ❌ GCP_SA_KEY (service account key)
- ❌ FIREBASE_API_KEY
- ❌ FIREBASE_PROJECT_ID
- ❌ FIREBASE_AUTH_DOMAIN
- ❌ FIREBASE_STORAGE_BUCKET
- ❌ FIREBASE_MESSAGING_SENDER_ID
- ❌ FIREBASE_APP_ID

---

## 🛠️ Automation Script (Optional Future Enhancement)

If you want workflows to automatically load `.env`, you can add this step:

```yaml
# Add to each workflow after checkout
- name: Load .env configuration
  run: |
    while IFS='=' read -r key value; do
      # Skip comments and empty lines
      [[ $key =~ ^#.*$ ]] && continue
      [[ -z $key ]] && continue
      # Export to GitHub env
      echo "$key=$value" >> $GITHUB_ENV
    done < .env
```

**Current approach (hardcoded) is simpler and more reliable.**

---

## 📊 Configuration Matrix

| Setting | Project 1 | Project 2 (RAG) | Project 3 |
|---------|-----------|-----------------|-----------|
| **Region** | us-central1 | us-central1 | us-central1 |
| **Memory** | 512Mi | 16Gi | 512Mi |
| **CPU** | 1 | 4 | 1 |
| **GPU** | None | 1x L4 | None |
| **Max Instances** | 10 | 10 | 10 |
| **Ingress** | internal | internal | internal |

---

## ✅ Checklist: Modifying Configuration

When changing deployment settings:

- [ ] Update `.env` file with new values
- [ ] Update `deploy-project-1.yml` if Project 1 affected
- [ ] Update `deploy-project-2.yml` if Project 2 affected
- [ ] Update `deploy-project-3.yml` if Project 3 affected
- [ ] If changing regions, create Artifact Registry in new region
- [ ] If changing service names, update `api-gateway-config.yaml`
- [ ] Commit and push changes
- [ ] Verify workflows run successfully

---

## 🆘 Troubleshooting

### Issue: Changes in .env not reflected in deployment

**Cause:** Values are hardcoded in workflow files

**Solution:** Update both `.env` AND the corresponding workflow file(s)

### Issue: Service name mismatch

**Cause:** Service name in workflow doesn't match API Gateway config

**Solution:** 
1. Check service name in workflow: `SERVICE_NAME: project-1`
2. Verify API Gateway routes to: `https://project-1-HASH-uc.a.run.app`
3. Update API Gateway if needed: `./infrastructure/deploy-gateway.sh`

### Issue: Wrong region selected

**Cause:** Hardcoded region in workflow doesn't match .env

**Solution:**
1. Check workflow: `GCP_REGION: us-central1`
2. Check `.env`: `GCP_REGION=us-central1`
3. Ensure they match

---

## 🔗 Related Documentation

- **[SECRETS_SETUP_GUIDE.md](SECRETS_SETUP_GUIDE.md)** - How to set up GitHub Secrets
- **[README.md](README.md)** - Overall project architecture
- **[OBSERVABILITY.md](OBSERVABILITY.md)** - Logging and monitoring configuration

---

**💡 Key Takeaway:** The `.env` file is your **configuration template**. Workflow files are the **actual implementation**. Keep them synchronized!
