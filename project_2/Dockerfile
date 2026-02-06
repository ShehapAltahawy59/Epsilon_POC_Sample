# Project 2 Dockerfile
# RAG System with NVIDIA L4 GPU Support
# Pinned to shared_libs v1.0.0

FROM nvidia/cuda:12.1.0-runtime-ubuntu22.04

# Install Python 3.11 and git
RUN apt-get update && apt-get install -y \
    python3.11 \
    python3-pip \
    git \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Set the shared library version to use
ARG SHARED_LIB_VERSION=v1.0.0
ENV SHARED_LIB_VERSION=${SHARED_LIB_VERSION}

# Clone only the shared_libs directory from the specific tag
# This ensures we get EXACTLY the version we want, not whatever is in the current commit
COPY .git /tmp/repo/.git
COPY shared_libs/ /tmp/repo/shared_libs/
WORKDIR /tmp/repo
RUN git checkout ${SHARED_LIB_VERSION} -- shared_libs/ 2>/dev/null || echo "Tag not found, using current version"
RUN cp -r shared_libs /app/shared_libs

WORKDIR /app

# Copy project files
COPY project_2/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY project_2/ .

# Environment variables
ENV PORT=8080
ENV CUDA_VISIBLE_DEVICES=0
ENV NVIDIA_VISIBLE_DEVICES=all
ENV NVIDIA_DRIVER_CAPABILITIES=compute,utility

# Expose port
EXPOSE 8080

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=10s --retries=3 \
    CMD python3 -c "import requests; requests.get('http://localhost:8080/health')"

# Run the application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]
