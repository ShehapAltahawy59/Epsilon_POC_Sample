# Secrets Management Guide

Complete guide for managing secrets in the Lean Hub architecture.

## Architecture

```
┌─────────────────────────────────────────┐
│  .env (COMMITTED to Git)                │
│  - Non-sensitive configuration          │
│  - Service names, regions, resource limits│
│  - Safe to share publicly               │
└─────────────────────────────────────────┘
                    │
                    ▼
┌─────────────────────────────────────────┐
│  GitHub Actions Secrets                 │
│  - API keys, credentials                │
│  - Service account keys                 │
│  - Injected into workflows at runtime   │
└─────────────────────────────────────────┘
                    │
                    ▼
┌─────────────────────────────────────────┐
│  Cloud Run Services                     │
│  - Receive secrets as environment vars  │
│  - No secrets in code or config files   │
└─────────────────────────────────────────┘
```

## What Goes Where

### ✅ .env (Committed to Git)

**Safe to commit - NO SECRETS:**
```bash
# Service configuration
GCP_REGION=us-central1
SERVICE_PROJECT_1=project-1

# Resource limits
STANDARD_MEMORY=512Mi
RAG_GPU_TYPE=nvidia-l4

# Feature flags
DEBUG_MODE=false
LOG_LEVEL=INFO
```

### 🔒 GitHub Actions Secrets

**NEVER in code - Always in GitHub:**
```
GCP_PROJECT_ID          # Your project ID
GCP_SA_KEY              # Service account JSON
FIREBASE_API_KEY        # Firebase API key
FIREBASE_PROJECT_ID     # Firebase project ID
FIREBASE_AUTH_DOMAIN    # Firebase auth domain
FIREBASE_STORAGE_BUCKET # Firebase storage
FIREBASE_MESSAGING_SENDER_ID
FIREBASE_APP_ID
```

### 💻 Local Development

**Environment variables only:**
```powershell
# Set temporarily (PowerShell)
$env:GCP_PROJECT_ID = "my-project"
$env:FIREBASE_API_KEY = "AIza..."

# OR create .env.local (gitignored)
# Then load it: .\load-env.ps1 .env.local
```

## Setup Instructions

### 1. Configure GitHub Secrets

```bash
# Go to your GitHub repository
# Settings → Secrets and variables → Actions → New repository secret

# Add each secret:
Name: GCP_PROJECT_ID
Value: your-actual-project-id

Name: GCP_SA_KEY
Value: <paste entire service account JSON>

Name: FIREBASE_API_KEY
Value: AIzaSy...

# etc.
```

### 2. Create Service Account Key

```bash
# Create service account
gcloud iam service-accounts create lean-hub-ci \
    --display-name="Lean Hub CI/CD"

# Grant permissions
gcloud projects add-iam-policy-binding PROJECT_ID \
    --member="serviceAccount:lean-hub-ci@PROJECT_ID.iam.gserviceaccount.com" \
    --role="roles/run.admin"

gcloud projects add-iam-policy-binding PROJECT_ID \
    --member="serviceAccount:lean-hub-ci@PROJECT_ID.iam.gserviceaccount.com" \
    --role="roles/artifactregistry.admin"

gcloud projects add-iam-policy-binding PROJECT_ID \
    --member="serviceAccount:lean-hub-ci@PROJECT_ID.iam.gserviceaccount.com" \
    --role="roles/iam.serviceAccountUser"

# Create key
gcloud iam service-accounts keys create sa-key.json \
    --iam-account=lean-hub-ci@PROJECT_ID.iam.gserviceaccount.com

# Copy entire JSON content to GitHub secret GCP_SA_KEY
cat sa-key.json

# IMPORTANT: Delete local file after copying
rm sa-key.json
```

### 3. Get Firebase Credentials

```bash
# Go to Firebase Console: https://console.firebase.google.com
# Select your project
# Project Settings → General
# Scroll to "Your apps" → Web app → Config

# Copy each value to GitHub secrets:
FIREBASE_API_KEY=AIza...
FIREBASE_PROJECT_ID=your-project
FIREBASE_AUTH_DOMAIN=your-project.firebaseapp.com
FIREBASE_STORAGE_BUCKET=your-project.appspot.com
FIREBASE_MESSAGING_SENDER_ID=123456789
FIREBASE_APP_ID=1:123:web:abc
```

## How Secrets Are Used

### In GitHub Actions Workflows

```yaml
env:
  # Secrets injected from GitHub
  GCP_PROJECT_ID: ${{ secrets.GCP_PROJECT_ID }}
  FIREBASE_API_KEY: ${{ secrets.FIREBASE_API_KEY }}
  
  # Config from .env (committed)
  GCP_REGION: us-central1
  SERVICE_NAME: project-1

steps:
  - name: Deploy to Cloud Run
    run: |
      gcloud run deploy ${{ env.SERVICE_NAME }} \
        --set-env-vars FIREBASE_API_KEY=${{ env.FIREBASE_API_KEY }}
```

### In Cloud Run Services

```python
# Python app receives secrets as environment variables
import os

firebase_api_key = os.getenv('FIREBASE_API_KEY')
project_id = os.getenv('FIREBASE_PROJECT_ID')

# Use them securely
firebase_admin.initialize_app(credentials, {
    'apiKey': firebase_api_key,
    'projectId': project_id
})
```

## Local Development

### Option 1: Environment Variables (Recommended)

```powershell
# PowerShell - Set for current session
$env:GCP_PROJECT_ID = "your-project"
$env:FIREBASE_API_KEY = "your-key"

# Verify
echo $env:GCP_PROJECT_ID
```

### Option 2: .env.local File (Not Committed)

```bash
# Create .env.local (gitignored)
GCP_PROJECT_ID=your-project
FIREBASE_API_KEY=your-key

# Load it
.\load-env.ps1 .env.local
```

### Option 3: gcloud Application Default Credentials

```bash
# Authenticate with your user account
gcloud auth application-default login

# Use in code
from google.auth import default
credentials, project = default()
```

## Security Best Practices

### ✅ DO:

1. **Store secrets in GitHub Actions secrets**
2. **Use service accounts with minimal permissions**
3. **Rotate secrets every 90 days**
4. **Delete service account keys after copying to GitHub**
5. **Use different projects for dev/staging/prod**
6. **Enable audit logging**
7. **Review secret access regularly**

### ❌ DON'T:

1. **Never commit secrets to Git (even in private repos)**
2. **Never log secrets in CI/CD output**
3. **Never hardcode secrets in source code**
4. **Never share secrets via email/chat**
5. **Never use production secrets in development**
6. **Never reuse secrets across environments**
7. **Never store secrets in .env if it's committed**

## Validation

### Check GitHub Secrets Are Set

```bash
# Use GitHub CLI
gh secret list

# Or check in GitHub UI
# Settings → Secrets and variables → Actions
```

### Verify in Workflow

```yaml
- name: Validate secrets
  run: |
    if [ -z "${{ secrets.GCP_PROJECT_ID }}" ]; then
      echo "Error: GCP_PROJECT_ID not set"
      exit 1
    fi
    echo "✓ All secrets configured"
```

### Test Locally

```powershell
# Validate environment
.\validate-env.ps1 -Verbose

# Should show:
# ✓ GCP_PROJECT_ID is set
# ✓ FIREBASE_API_KEY is set
```

## Rotation Schedule

| Secret | Rotation Period | How to Rotate |
|--------|----------------|---------------|
| Service Account Keys | 90 days | Create new key → Update GitHub → Delete old |
| Firebase API Keys | Annually | Generate new key → Update GitHub → Revoke old |
| Access Tokens | 30 days | Regenerate → Update immediately |

## Troubleshooting

### Secret Not Available in Workflow

```yaml
# Check secret is defined in repository settings
# Settings → Secrets and variables → Actions

# Verify syntax
${{ secrets.SECRET_NAME }}  # ✓ Correct
${{ env.SECRET_NAME }}      # ✗ Wrong (use for env vars)
```

### Permission Denied Errors

```bash
# Verify service account has correct roles
gcloud projects get-iam-policy PROJECT_ID \
  --flatten="bindings[].members" \
  --filter="bindings.members:serviceAccount:lean-hub-ci@*"
```

### Firebase Authentication Fails

```bash
# Verify API key is valid
curl "https://identitytoolkit.googleapis.com/v1/accounts:lookup?key=YOUR_API_KEY"

# Check project ID matches
gcloud config get-value project
```

## Migration from Old Approach

If you had secrets in .env before:

```bash
# 1. Extract all secrets from .env
grep -E "API_KEY|SECRET|PASSWORD|TOKEN" .env > secrets.txt

# 2. Add each to GitHub secrets
# Settings → Secrets and variables → Actions

# 3. Remove secrets from .env
# Keep only non-sensitive config

# 4. Delete secrets.txt
rm secrets.txt

# 5. Commit updated .env
git add .env
git commit -m "Move secrets to GitHub Actions"
git push
```

## Related Documentation

- [.github/SECRETS_SETUP.md](.github/SECRETS_SETUP.md) - GitHub secrets setup
- [ENV_VARIABLES_REFERENCE.md](ENV_VARIABLES_REFERENCE.md) - All variables reference
- [.env](.env) - Non-sensitive configuration (committed)
- [.env.example](.env.example) - Template showing what goes where

---

**Remember:** 
- `.env` = Configuration (committed) ✅
- GitHub Secrets = Credentials (never committed) 🔒
- Local = Environment variables (temporary) 💻
