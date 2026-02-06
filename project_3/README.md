# Project 3

Simple API service demonstrating independent versioning in the Lean Hub.

## Pinned Shared Library Version
- **v1.0.0** (immutable)

## Local Development

```bash
# Install dependencies
pip install -r requirements.txt

# Run the service
python main.py
```

## Docker Build

```bash
# Build from repo root
docker build -f project_3/Dockerfile -t project-3:latest .

# Run container
docker run -p 8080:8080 project-3:latest
```

## Endpoints

- `GET /` - Root endpoint with version info
- `GET /health` - Health check
- `GET /version` - Detailed version information
- `GET /status` - Extended status information

## Surgical Update Process

To update to a new shared_libs version:
1. Update `SHARED_LIB_VERSION` in Dockerfile
2. Update the COPY command to reference the new tag
3. Rebuild and test
4. Deploy only this service (others remain unaffected)
