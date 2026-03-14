# Project Template

Use this folder to create new services with minimal manual work.

## Quick Use

1. Copy folder:
   - `project_template` -> `project_5` (or any new service folder)
2. Update:
   - `project_5/main.py` (`SERVICE_CODE`, `SERVICE_SLUG`, title)
   - `project_5/Dockerfile` (`project_template` -> `project_5` in COPY lines)
   - `project_5/shared_lib_version` (desired shared lib version)
3. Add workflow wrapper:
   - `.github/workflows/deploy-project-5.yml`
   - Use `reusable-deploy-project.yml`
4. Add gateway routes in `infrastructure/gateway/services-registry.json`:
   - `/p5`, `/p5/health`, `/p5/version`
5. Redeploy:
   - Run deploy-project-5 workflow
   - Run deploy-api-gateway workflow

See `NEW_PROJECT_CHECKLIST.md` for full rollout checklist.
