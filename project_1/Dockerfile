# Project 1 Dockerfile
# Pinned to shared_libs v1.0.0 for immutable builds

FROM python:3.11-slim

# Install git for checking out specific versions
RUN apt-get update && apt-get install -y git && rm -rf /var/lib/apt/lists/*

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
COPY project_1/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY project_1/ .

# Environment variables
ENV PORT=8080

# Expose port
EXPOSE 8080

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8080/health')"

# Run the application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]
