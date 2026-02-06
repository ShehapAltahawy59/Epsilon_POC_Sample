# Project 2 - RAG System

GPU-accelerated Retrieval-Augmented Generation service optimized for NVIDIA L4.

## Pinned Shared Library Version
- **v1.0.0** (immutable)

## GPU Configuration
- **GPU Type**: NVIDIA L4
- **CUDA Version**: 12.1
- **GPU Memory**: Optimized for L4 specifications

## Local Development

```bash
# Install dependencies
pip install -r requirements.txt

# Run the service
python main.py
```

## Docker Build (GPU-enabled)

```bash
# Build from repo root
docker build -f project_2/Dockerfile -t project-2-rag:latest .

# Run container with GPU support
docker run --gpus all -p 8080:8080 project-2-rag:latest
```

## Cloud Run Deployment (GPU)

```bash
# Deploy with L4 GPU on Cloud Run
gcloud run deploy project-2-rag \
  --image gcr.io/YOUR-PROJECT/project-2-rag:latest \
  --platform managed \
  --region us-central1 \
  --gpu 1 \
  --gpu-type nvidia-l4 \
  --memory 16Gi \
  --cpu 4 \
  --max-instances 10 \
  --ingress internal
```

## Endpoints

- `GET /` - Root endpoint with version and GPU info
- `GET /health` - Health check with GPU status
- `GET /version` - Detailed version information
- `POST /index` - Index documents for RAG
- `POST /query` - Query RAG system

## Cost Optimization Notes

- L4 GPUs provide 2-3x better price/performance than A100
- Auto-scaling minimizes idle GPU costs
- Internal-only ingress reduces egress charges
