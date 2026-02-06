# GitHub Secrets Configuration

Complete guide for setting up GitHub Actions secrets for the Lean Hub.

## Required Secrets

Add these to your GitHub repository: **Settings → Secrets and variables → Actions**

### 1. GCP_PROJECT_ID
Your Google Cloud Project ID

```
Name: GCP_PROJECT_ID
Value: your-actual-project-id
```

### 2. GCP_SA_KEY
Service Account JSON key (entire file content)

```
Name: GCP_SA_KEY
Value: {
  "type": "service_account",
  "project_id": "your-project",
  "private_key_id": "...",
  "private_key": "-----BEGIN PRIVATE KEY-----\n...",
  ...
}
```

### 3. Firebase Secrets

```
Name: FIREBASE_API_KEY
Value: AIzaSyD...

Name: FIREBASE_PROJECT_ID
Value: your-firebase-project

Name: FIREBASE_AUTH_DOMAIN
Value: your-project.firebaseapp.com

Name: FIREBASE_STORAGE_BUCKET
Value: your-project.appspot.com

Name: FIREBASE_MESSAGING_SENDER_ID
Value: 123456789

Name: FIREBASE_APP_ID
Value: 1:123:web:abc
```

#### Creating the Service Account

```bash
# Set your project
export PROJECT_ID="your-project-id"

# Create service account
gcloud iam service-accounts create lean-hub-deployer \
    --display-name="Lean Hub CI/CD Deployer" \
    --project=${PROJECT_ID}

# Grant necessary permissions
gcloud projects add-iam-policy-binding ${PROJECT_ID} \
    --member="serviceAccount:lean-hub-deployer@${PROJECT_ID}.iam.gserviceaccount.com" \
    --role="roles/run.admin"

gcloud projects add-iam-policy-binding ${PROJECT_ID} \
    --member="serviceAccount:lean-hub-deployer@${PROJECT_ID}.iam.gserviceaccount.com" \
    --role="roles/artifactregistry.admin"

gcloud projects add-iam-policy-binding ${PROJECT_ID} \
    --member="serviceAccount:lean-hub-deployer@${PROJECT_ID}.iam.gserviceaccount.com" \
    --role="roles/iam.serviceAccountUser"

# Create and download key
gcloud iam service-accounts keys create lean-hub-key.json \
    --iam-account=lean-hub-deployer@${PROJECT_ID}.iam.gserviceaccount.com

# Copy the contents of lean-hub-key.json
cat lean-hub-key.json
```

#### Adding to GitHub

```
Settings → Secrets and variables → Actions → New repository secret
Name: GCP_SA_KEY
Value: <paste entire JSON content>
```

## Optional Secrets

### FIREBASE_TOKEN (for Firebase CLI operations)
```bash
firebase login:ci
# Copy the generated token
```

Add to GitHub:
```
Name: FIREBASE_TOKEN
Value: <your-firebase-token>
```

## Verification

After adding secrets, they should appear in:
`Settings → Secrets and variables → Actions`

You should see:
- ✓ GCP_PROJECT_ID
- ✓ GCP_SA_KEY
- ✓ FIREBASE_TOKEN (optional)

## Security Notes

1. **Never commit** service account keys to the repository
2. **Rotate keys** periodically (every 90 days recommended)
3. **Use least privilege**: Only grant necessary permissions
4. **Monitor usage**: Check Cloud Logging for suspicious activity
5. **Delete old keys**: Remove unused service account keys

## Testing CI/CD

Once secrets are configured:

```bash
# Make a change to any project
echo "# Test change" >> project_1/README.md

# Commit and push
git add .
git commit -m "Test CI/CD pipeline"
git push origin main

# Watch the workflow
gh run watch
```

## Troubleshooting

### Authentication Errors
- Verify GCP_SA_KEY is valid JSON
- Check service account has required roles
- Ensure project ID matches

### Permission Denied
```bash
# Re-grant permissions
gcloud projects add-iam-policy-binding ${PROJECT_ID} \
    --member="serviceAccount:lean-hub-deployer@${PROJECT_ID}.iam.gserviceaccount.com" \
    --role="roles/run.admin"
```

### Workflow Not Triggering
- Check path filters in workflow files
- Verify branch name is `main`
- Review GitHub Actions logs
