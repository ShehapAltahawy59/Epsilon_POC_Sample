# New Project Onboarding Checklist

This checklist standardizes adding `project_5+` with low team effort.

## 1) Create the service from template

- Copy `project_template/` to a new folder, for example `project_5/`.
- In `project_5/main.py`, update:
  - `SERVICE_CODE` (example: `project_5`)
  - `SERVICE_SLUG` (example: `project-5`)
  - FastAPI title/description (optional)
- `project_5/Dockerfile` is variable-driven via `PROJECT_PATH`; no manual COPY path edits are needed.
- Set `project_5/shared_lib_version` to desired pinned version (example: `3.1.0`).

## 2) Add deploy workflow wrapper

Create `.github/workflows/deploy-project-5.yml`:

```yaml
name: 'Surgical Deploy: Project 5'

on:
  push:
    branches: [main]
    paths:
      - 'project_5/**'
  workflow_dispatch:

jobs:
  deploy:
    uses: ./.github/workflows/reusable-deploy-project.yml
    secrets: inherit
    with:
      deployment_name: Build and Deploy Project 5
      project_path: project_5
      service_name: project-5
      dockerfile_path: project_5/Dockerfile
      shared_lib_version_file: project_5/shared_lib_version
      max_instances: "10"
      min_instances: "0"
      memory: 512Mi
      cpu: "1"
```

## 3) Register service once for API Gateway automation

In `infrastructure/gateway/services-registry.json`, add a service entry with:

- `id` (example: `p5`)
- `service_name` (example: `project-5`)
- `placeholder_url` (example: `https://project-5-placeholder`)
- `routes` list (`path_suffix`, `method`, `summary`, `operation_id`)

The gateway deploy workflow now auto-generates OpenAPI config from this registry.
No manual gateway OpenAPI file editing is required.

## 5) Optional test coverage

Add `Project 5 (via Gateway)` endpoints to `test_api_gateway.py`.

## 6) Deploy order

1. Push code.
2. Run `Surgical Deploy: Project 5`.
3. Run `Deploy API Gateway` (manual).
4. Run gateway tests and verify logs.

## 7) Verification queries

- Cloud Run service exists:
  - `gcloud run services list --region=us-central1`
- Gateway endpoint works:
  - `GET /p5/health` returns expected status
- Correlation logs:
  - `resource.type="cloud_run_revision" jsonPayload.service="project_5"`
