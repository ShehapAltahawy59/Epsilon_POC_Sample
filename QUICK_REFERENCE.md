# 🚀 Quick Reference: Manual vs Automatic

**TL;DR**: After 15 minutes of one-time setup, everything else is 100% automatic!

---

## ❌ Manual (One-Time, 15 Minutes Total)

### 1. GitHub Secrets (5 min)
```
Settings → Secrets and variables → Actions

Add these:
✓ GCP_PROJECT_ID
✓ GCP_SA_KEY (entire JSON)
✓ FIREBASE_API_KEY
✓ FIREBASE_PROJECT_ID
✓ FIREBASE_AUTH_DOMAIN
```

### 2. Create GCP Service Account (5 min)
```bash
gcloud iam service-accounts create github-actions
gcloud projects add-iam-policy-binding PROJECT_ID --member="..." --role="roles/run.admin"
gcloud iam service-accounts keys create key.json --iam-account=...
# Copy key.json to GCP_SA_KEY secret
```

### 3. Firebase Setup (3 min)
```
console.firebase.google.com
→ Enable Authentication
→ Copy API key
→ Add to GitHub secrets
```

### 4. Review .env (1 min)
```bash
# Already committed, just review
cat .env
```

---

## ✅ Automatic (After Setup, Forever!)

### On Every Push to GitHub:

```bash
git push origin main
```

**GitHub Actions automatically:**

✅ **Detects what changed** (path filtering)
- Changed `project_1/`? → Deploy Project 1 only
- Changed `project_2/`? → Deploy Project 2 only  
- Changed `project_3/`? → Deploy Project 3 only
- Changed `shared_libs/`? → Create new Git tag (v1.0.1, v2.0.0, etc.)
- Changed `dashboard-config.json`? → Update monitoring dashboard

✅ **Enables GCP APIs** (first time)
- Cloud Run
- Artifact Registry
- API Gateway
- Cloud Logging
- Cloud Monitoring
- Cloud Trace

✅ **Builds Docker images**
- Pins to specific shared_libs version (Git tag)
- Multi-stage builds for optimization
- GPU support for Project 2

✅ **Deploys to Cloud Run**
- Injects all secrets from GitHub
- Sets resource limits from .env
- Internal-only (no public access)
- Auto-scale to 0

✅ **Updates monitoring dashboard**
- Centralized metrics for all services
- Request count, latency, errors
- CPU, memory, instance count
- Correlation ID logs

✅ **Logs everything**
- JSON-structured logs
- Correlation IDs automatically generated
- Cloud Trace integration
- Searchable by correlation_id

---

## 🎯 Result

### Time Investment:
- **One-time setup**: 15 minutes
- **Every deployment after**: 0 minutes (push and forget!)

### What You Get:
- ✅ Surgical deployments (only rebuild what changed)
- ✅ Version pinning (each service chooses its shared_libs version)
- ✅ Full observability (logs, traces, metrics, dashboard)
- ✅ Zero manual deployment work
- ✅ Cost-optimized (scale to 0, internal-only)

---

## 📋 Verification Checklist

After setup, verify automation:

```bash
# 1. Check GitHub Actions
https://github.com/YOUR_REPO/actions
→ Should see workflows running

# 2. Check Cloud Run services deployed
gcloud run services list --project=YOUR_PROJECT
→ Should see project-1, project-2, project-3

# 3. Check monitoring dashboard
https://console.cloud.google.com/monitoring/dashboards?project=YOUR_PROJECT
→ Should see "Lean Hub - Centralized Dashboard"

# 4. Check logs have correlation IDs
https://console.cloud.google.com/logs/query?project=YOUR_PROJECT
# Query: resource.type="cloud_run_revision" jsonPayload.correlation_id!=""
→ Should see JSON logs with correlation_id fields

# 5. Check shared_libs version tags
git tag -l
→ Should see v1.0.0, and new tags on shared_libs changes
```

---

## 🔍 Common Questions

**Q: Do I need to run deploy scripts manually?**  
A: No! GitHub Actions runs them automatically on push.

**Q: Do I need to create the monitoring dashboard manually?**  
A: No! The `deploy-monitoring.yml` workflow creates it automatically.

**Q: Do I need to enable GCP APIs manually?**  
A: No! GitHub Actions enables them automatically on first deployment.

**Q: What if I want to deploy manually anyway?**  
A: You can! Run `./infrastructure/deploy-all-services.sh` locally.

**Q: How do I update a service to use a new shared_libs version?**  
A: Just change the `ARG SHARED_LIB_VERSION` in the Dockerfile and push. CI/CD handles the rest.

**Q: How long does deployment take?**  
A: 3-5 minutes per service (only rebuilds what changed).

---

## 📚 Full Documentation

- [AUTOMATION_CHECKLIST.md](AUTOMATION_CHECKLIST.md) - Complete breakdown
- [SECRETS_MANAGEMENT.md](SECRETS_MANAGEMENT.md) - Secrets setup guide
- [OBSERVABILITY.md](OBSERVABILITY.md) - Monitoring & logging guide

---

**Bottom Line**: Set up GitHub secrets once (15 min), then never worry about deployment again. Just push code! 🚀
