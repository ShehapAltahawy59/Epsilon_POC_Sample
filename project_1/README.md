# Project 1

Simple API service demonstrating the Lean Hub architecture.

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
docker build -f project_1/Dockerfile -t project-1:latest .

# Run container
docker run -p 8080:8080 project-1:latest
```

## Endpoints

- `GET /` - Root endpoint with version info
- `GET /health` - Health check
- `GET /version` - Detailed version information

## Surgical Update Process

To update to a new shared_libs version:
1. Update `SHARED_LIB_VERSION` in Dockerfile
2. Update the COPY command to reference the new tag
3. Rebuild and test
4. Deploy only this service (others remain unaffected)
