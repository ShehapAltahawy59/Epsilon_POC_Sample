# Project Template Dockerfile
# After copying template -> project_X, replace project_template with project_X in this file.

FROM python:3.11-slim

# Install git for checking out specific shared_libs tags
RUN apt-get update && apt-get install -y git && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Build args passed from reusable workflow
ARG PROJECT_PATH=project_4
ARG SHARED_LIB_VERSION=v1.0.0
ENV PROJECT_PATH=${PROJECT_PATH}
ENV SHARED_LIB_VERSION=${SHARED_LIB_VERSION}

# Pull shared_libs from pinned tag snapshot
COPY .git /tmp/repo/.git
COPY shared_libs/ /tmp/repo/shared_libs/
WORKDIR /tmp/repo
RUN git checkout ${SHARED_LIB_VERSION} -- shared_libs/ 2>/dev/null || echo "Tag not found, using current version"
RUN cp -r shared_libs /app/shared_libs

WORKDIR /app

# Project source is variable-driven; no manual path edits needed
COPY ${PROJECT_PATH}/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY ${PROJECT_PATH}/ .

ENV PORT=8080
EXPOSE 8080

HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8080/health')"

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]
