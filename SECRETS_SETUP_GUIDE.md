# 🔐 Complete Guide: Getting All Secrets and Adding to GitHub

**Complete step-by-step guide to get every secret and add it to GitHub Actions.**

Time required: **15 minutes**

---

## 📋 Prerequisites

Before starting, you need:
- ✅ A Google Cloud Platform (GCP) account
- ✅ A GitHub repository for this project
- ✅ `gcloud` CLI installed ([Install Guide](https://cloud.google.com/sdk/docs/install))
- ✅ Owner/Editor permissions on a GCP project

---

## 🎯 Secrets You Need to Collect

| Secret Name | Where to Get It | Used For |
|-------------|-----------------|----------|
| `GCP_PROJECT_ID` | GCP Console | Project identifier |
| `GCP_SA_KEY` | Create service account | Authentication |
| `FIREBASE_API_KEY` | Firebase Console | Frontend auth |
| `FIREBASE_PROJECT_ID` | Firebase Console | Firebase project ID |
| `FIREBASE_AUTH_DOMAIN` | Firebase Console | Auth domain |
| `FIREBASE_STORAGE_BUCKET` | Firebase Console | Storage bucket |
| `FIREBASE_MESSAGING_SENDER_ID` | Firebase Console | Messaging ID |
| `FIREBASE_APP_ID` | Firebase Console | App identifier |

---

## 📝 Step-by-Step Instructions

### STEP 1: Create or Select GCP Project (2 minutes)

#### Option A: Use Existing Project

```bash
# List your existing projects
gcloud projects list

# Example output:
# PROJECT_ID              NAME                PROJECT_NUMBER
# my-lean-hub-project     Lean Hub            123456789012

# Copy your PROJECT_ID
```

✅ **Add to GitHub Secrets NOW:**

1. Go to your GitHub repository: `https://github.com/YOUR_USERNAME/YOUR_REPO`
2. Click **Settings** → **Secrets and variables** → **Actions**
3. Click **"New repository secret"**
4. Enter:
   - **Name:** `GCP_PROJECT_ID`
   - **Value:** `my-lean-hub-project` (your actual project ID)
5. Click **"Add secret"**

✅ **Verify:** You should see `GCP_PROJECT_ID` in your secrets list

#### Option B: Create New Project

```bash
# Create a new project (replace with your desired project ID)
gcloud projects create my-lean-hub-project --name="Lean Hub"

# Set as default project
gcloud config set project my-lean-hub-project
```

✅ **Add to GitHub Secrets NOW:**

1. Go to your GitHub repository: `https://github.com/YOUR_USERNAME/YOUR_REPO`
2. Click **Settings** → **Secrets and variables** → **Actions**
3. Click **"New repository secret"**
4. Enter:
   - **Name:** `GCP_PROJECT_ID`
   - **Value:** `my-lean-hub-project` (your actual project ID)
5. Click **"Add secret"**

✅ **Verify:** You should see `GCP_PROJECT_ID` in your secrets list

---

### STEP 2: Enable Required GCP APIs (3 minutes)

**Note:** GitHub Actions will also do this automatically, but enabling now ensures everything works.

```bash
# Set your project ID (replace with yours)
export PROJECT_ID="my-lean-hub-project"

# Enable all required APIs
gcloud services enable \
    run.googleapis.com \
    artifactregistry.googleapis.com \
    apigateway.googleapis.com \
    servicemanagement.googleapis.com \
    servicecontrol.googleapis.com \
    monitoring.googleapis.com \
    logging.googleapis.com \
    cloudtrace.googleapis.com \
    --project=$PROJECT_ID

# This takes 1-2 minutes
# You'll see: "Operation finished successfully"
```

✅ **Verification:**
```bash
gcloud services list --enabled --project=$PROJECT_ID | grep -E "(run|artifact|gateway|monitoring)"
```

---

### STEP 3: Create Service Account for GitHub Actions (5 minutes)

#### 3.1: Create Service Account

```bash
# Create service account
gcloud iam service-accounts create github-actions \
    --display-name="GitHub Actions Deployment" \
    --description="Service account for automated deployments from GitHub Actions" \
    --project=$PROJECT_ID

# You'll see: "Created service account [github-actions]"
```

#### 3.2: Grant Required Permissions

```bash
# Get your project number (needed for some commands)
PROJECT_NUMBER=$(gcloud projects describe $PROJECT_ID --format="value(projectNumber)")

# Grant Cloud Run Admin role (deploy and manage services)
gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:github-actions@${PROJECT_ID}.iam.gserviceaccount.com" \
    --role="roles/run.admin"

# Grant Artifact Registry Admin role (push Docker images)
gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:github-actions@${PROJECT_ID}.iam.gserviceaccount.com" \
    --role="roles/artifactregistry.admin"

# Grant Service Account User role (required for Cloud Run)
gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:github-actions@${PROJECT_ID}.iam.gserviceaccount.com" \
    --role="roles/iam.serviceAccountUser"

# Grant API Gateway Admin role (deploy API Gateway)
gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:github-actions@${PROJECT_ID}.iam.gserviceaccount.com" \
    --role="roles/apigateway.admin"

# Grant Service Management Admin (for API Gateway config)
gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:github-actions@${PROJECT_ID}.iam.gserviceaccount.com" \
    --role="roles/servicemanagement.admin"

# Grant Monitoring Admin (for dashboard deployment)
gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:github-actions@${PROJECT_ID}.iam.gserviceaccount.com" \
    --role="roles/monitoring.admin"

# Each command will show: "Updated IAM policy for project"
```

#### 3.3: Create and Download Service Account Key

```bash
# Create key and save to file
gcloud iam service-accounts keys create github-actions-key.json \
    --iam-account=github-actions@${PROJECT_ID}.iam.gserviceaccount.com \
    --project=$PROJECT_ID

# You'll see: "created key [...] for [github-actions@...]"
```

✅ **Verification:**
```bash
# Check the file was created
ls -lh github-actions-key.json

# Should show a file ~2-3 KB in size
```

✅ **IMPORTANT:** This JSON file contains your `GCP_SA_KEY` secret!

**Open the file and copy its ENTIRE contents:**

#### Method 1: Display and Manually Copy (Works Everywhere)

```bash
# Display the entire JSON file
cat github-actions-key.json

# You'll see output like:
# {
#   "type": "service_account",
#   "project_id": "my-lean-hub-project",
#   "private_key_id": "abc123...",
#   "private_key": "-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----\n",
#   ...
# }

# Select all the text (from { to }) and copy it
# Ctrl+Shift+C (Linux/Cloud Shell) or Cmd+C (macOS) or Ctrl+C (Windows)
```

#### Method 2: Cloud Shell Built-in Editor (If using GCP Cloud Shell)

```bash
# Open in Cloud Shell editor
cloudshell edit github-actions-key.json

# Then:
# 1. Click "Open in Editor" button
# 2. Select all (Ctrl+A)
# 3. Copy (Ctrl+C)
```

#### Method 3: Download File (If using GCP Cloud Shell)

```bash
# Download the file to your local machine
cloudshell download github-actions-key.json

# Then open the downloaded file in your local text editor and copy contents
```

#### Method 4: Auto-Copy Commands (If Available)

```bash
# Windows PowerShell:
Get-Content github-actions-key.json | Set-Clipboard

# macOS:
cat github-actions-key.json | pbcopy

# Linux with xclip (install if needed):
# sudo apt-get install xclip -y
# cat github-actions-key.json | xclip -selection clipboard

# Linux with xsel (alternative):
# sudo apt-get install xsel -y
# cat github-actions-key.json | xsel --clipboard
```

✅ **Add to GitHub Secrets NOW:**

1. **Copy the entire JSON** (use one of the methods above)
2. Go to your GitHub repository: `https://github.com/YOUR_USERNAME/YOUR_REPO`
3. Click **Settings** → **Secrets and variables** → **Actions**
4. Click **"New repository secret"**
5. Enter:
   - **Name:** `GCP_SA_KEY`
   - **Value:** Paste the ENTIRE JSON contents (from `{` to `}`)
6. Click **"Add secret"**

💡 **Tip:** The JSON is usually 2,300-2,500 characters. Make sure you paste ALL of it!

✅ **Verify:** You should see `GCP_SA_KEY` in your secrets list (value will be hidden)

⚠️ **Security Note:** Delete this file now that it's in GitHub:
```bash
# After you've copied it to GitHub secrets:
rm github-actions-key.json
```

---

### STEP 4: Set Up Firebase (5 minutes)

#### 4.1: Create Firebase Project

1. **Go to Firebase Console:**
   ```
   https://console.firebase.google.com
   ```

2. **Click "Add project"**

3. **Select your existing GCP project:**
   - Choose: `my-lean-hub-project` (your GCP project)
   - Click "Continue"

4. **Enable Google Analytics (Optional):**
   - Toggle ON or OFF (your choice)
   - Click "Continue"

5. **Confirm plan:**
   - Review and click "Confirm plan"
   - Wait 30-60 seconds for project creation

✅ **You'll see:** "Your new project is ready"

#### 4.2: Enable Firebase Authentication

1. **In Firebase Console, click "Authentication"** (left sidebar)

2. **Click "Get started"**

3. **Enable Email/Password provider:**
   - Click "Email/Password"
   - Toggle "Enable" to ON
   - Click "Save"

✅ **You'll see:** "Email/Password" listed as Enabled

#### 4.3: Get Firebase Configuration Values

1. **Click the gear icon (⚙️) → "Project settings"** (top left) → Genral

2. **Scroll down to "Your apps"**

3. **Click the Web icon (`</>`)**

4. **Register your app:**
   - App nickname: `Lean Hub Web`
   - Toggle "Firebase Hosting": OFF (not needed)
   - Click "Register app"

5. **Copy the configuration values:**

You'll see code like this:

```javascript
const firebaseConfig = {
  apiKey: "AIzaSyAbc123def456ghi789jkl012mno345pqr",
  authDomain: "my-lean-hub-project.firebaseapp.com",
  projectId: "my-lean-hub-project",
  storageBucket: "my-lean-hub-project.appspot.com",
  messagingSenderId: "123456789012",
  appId: "1:123456789012:web:abc123def456ghi789"
};
```

✅ **Add ALL Firebase values to GitHub Secrets NOW:**

**Go to:** `https://github.com/YOUR_USERNAME/YOUR_REPO` → **Settings** → **Secrets and variables** → **Actions**

Add each secret by clicking **"New repository secret"** for each one:

**Secret 1:**
- Name: `FIREBASE_API_KEY`
- Value: `AIzaSyAbc123def456ghi789jkl012mno345pqr` (your actual key)

**Secret 2:**
- Name: `FIREBASE_AUTH_DOMAIN`
- Value: `my-lean-hub-project.firebaseapp.com` (your actual domain)

**Secret 3:**
- Name: `FIREBASE_PROJECT_ID`
- Value: `my-lean-hub-project` (your actual project ID)

**Secret 4:**
- Name: `FIREBASE_STORAGE_BUCKET`
- Value: `my-lean-hub-project.appspot.com` (your actual bucket)

**Secret 5:**
- Name: `FIREBASE_MESSAGING_SENDER_ID`
- Value: `123456789012` (your actual sender ID)

**Secret 6:**
- Name: `FIREBASE_APP_ID`
- Value: `1:123456789012:web:abc123def456ghi789` (your actual app ID)

6. **Click "Continue to console"**

✅ **Verify:** You should now have 8 total secrets in GitHub:
- ✓ GCP_PROJECT_ID
- ✓ GCP_SA_KEY
- ✓ FIREBASE_API_KEY
- ✓ FIREBASE_AUTH_DOMAIN
- ✓ FIREBASE_PROJECT_ID
- ✓ FIREBASE_STORAGE_BUCKET
- ✓ FIREBASE_MESSAGING_SENDER_ID
- ✓ FIREBASE_APP_ID

✅ **Firebase setup complete!**

---

### STEP 5: Verify All Secrets Collected

**Check you have all 8 secrets:**

```
☐ GCP_PROJECT_ID                = my-lean-hub-project
☐ GCP_SA_KEY                    = {entire JSON contents}
☐ FIREBASE_API_KEY              = AIzaSy...
☐ FIREBASE_AUTH_DOMAIN          = ...firebaseapp.com
☐ FIREBASE_PROJECT_ID           = my-lean-hub-project
☐ FIREBASE_STORAGE_BUCKET       = ...appspot.com
☐ FIREBASE_MESSAGING_SENDER_ID  = 123456789012
☐ FIREBASE_APP_ID               = 1:123456789012:web:...
```

---



## 🚀 STEP 6: Test Automatic Deployment

Now that secrets are configured, test that everything works:

### 7.1: Trigger GitHub Actions

```bash
# Make a small change to trigger deployment
echo "# Test deployment" >> README.md

# Commit and push
git add README.md
git commit -m "Test automatic deployment"
git push origin main
```

### 7.2: Watch GitHub Actions

1. **Go to your GitHub repository**

2. **Click "Actions"** (top navigation)

3. **You'll see workflows running:**
   - ✅ "Surgical Deploy: Project 1" - Running...
   - ✅ "Surgical Deploy: Project 2" - Running...
   - ✅ "Surgical Deploy: Project 3" - Running...
   - ✅ "Tag Shared Libs" - Running...
   - ✅ "Deploy Monitoring Dashboard" - Running...

4. **Click on any workflow to see progress**

5. **Wait 3-5 minutes**

✅ **Success when you see:** All workflows with green checkmarks ✓

### 7.3: Verify Deployment

**Check Cloud Run services deployed:**

```bash
gcloud run services list --project=$PROJECT_ID

# You should see:
# SERVICE     REGION        URL                          LAST DEPLOYED
# project-1   us-central1   https://project-1-...run.app  2026-02-06
# project-2   us-central1   https://project-2-...run.app  2026-02-06
# project-3   us-central1   https://project-3-...run.app  2026-02-06
```

**Check monitoring dashboard:**

1. Go to: https://console.cloud.google.com/monitoring/dashboards?project=YOUR_PROJECT_ID

2. You should see: **"Lean Hub - Centralized Dashboard"**

✅ **Everything is deployed and running!**

---

## 🎉 You're Done!

### What You've Accomplished:

✅ Created GCP service account with proper permissions  
✅ Set up Firebase project with authentication  
✅ Collected all 8 required secrets  
✅ Added secrets to GitHub Actions  
✅ Triggered automatic deployment  
✅ Verified services are running  

### What Happens Now:

From now on, **every time you push code:**

1. GitHub Actions detects what changed
2. Builds and deploys only affected services
3. Updates monitoring dashboard
4. Creates version tags
5. Everything automatic - no manual work!

**Total time for future deployments: 0 minutes** (just push code!)

---

## 🔍 Troubleshooting

### Issue: "Permission denied" errors in GitHub Actions

**Solution:** Check service account permissions:

```bash
# Verify service account has correct roles
gcloud projects get-iam-policy $PROJECT_ID \
    --flatten="bindings[].members" \
    --filter="bindings.members:github-actions@${PROJECT_ID}.iam.gserviceaccount.com"
```

You should see roles:
- `roles/run.admin`
- `roles/artifactregistry.admin`
- `roles/iam.serviceAccountUser`

**If missing, re-run STEP 3.2 commands**

---

### Issue: "Invalid service account key" error

**Solution:** Verify JSON format:

1. Check the `GCP_SA_KEY` secret in GitHub
2. Make sure it starts with `{` and ends with `}`
3. Make sure entire JSON was pasted (including private key)

**Re-create key if needed:**
```bash
gcloud iam service-accounts keys create github-actions-key-new.json \
    --iam-account=github-actions@${PROJECT_ID}.iam.gserviceaccount.com
```

Then re-add to GitHub secrets.

---

### Issue: Firebase configuration not working

**Solution:** Verify Firebase values:

1. Go to Firebase Console → Project Settings
2. Scroll to "Your apps"
3. Click "Config" under your web app
4. Copy values again and update GitHub secrets

---

### Issue: API not enabled errors

**Solution:** Enable APIs manually:

```bash
gcloud services enable \
    run.googleapis.com \
    artifactregistry.googleapis.com \
    --project=$PROJECT_ID
```

Wait 2-3 minutes, then re-run deployment.

---

## 📚 Next Steps

1. **Review Automation:** [AUTOMATION_CHECKLIST.md](AUTOMATION_CHECKLIST.md)
2. **Test Surgical Updates:** [SURGICAL_UPDATE_TEST.md](SURGICAL_UPDATE_TEST.md)
3. **Configure Monitoring:** [OBSERVABILITY.md](OBSERVABILITY.md)
4. **Add Your Services:** Use project templates

---

## 🔐 Security Best Practices

### ✅ DO:
- ✅ Store secrets ONLY in GitHub Actions secrets
- ✅ Delete service account key file after adding to GitHub
- ✅ Rotate service account keys every 90 days
- ✅ Use least-privilege roles (only what's needed)
- ✅ Enable 2FA on GitHub and GCP accounts

### ❌ DON'T:
- ❌ Commit secrets to Git
- ❌ Share service account keys
- ❌ Store secrets in .env files (use .env.local locally only)
- ❌ Grant overly broad permissions

---

## 📞 Need Help?

- **GCP Issues:** Check [GCP Console](https://console.cloud.google.com)
- **Firebase Issues:** Check [Firebase Console](https://console.firebase.google.com)
- **GitHub Actions Issues:** Check Actions tab, view workflow logs
- **General Issues:** See [AUTOMATION_CHECKLIST.md](AUTOMATION_CHECKLIST.md)

---

**🎊 Congratulations! You've completed the setup!**

Your Lean Hub is now fully automated and ready to deploy with every push! 🚀
