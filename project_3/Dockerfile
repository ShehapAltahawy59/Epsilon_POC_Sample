# Project 3 Dockerfile
FROM python:3.11-slim

WORKDIR /app

# Copy shared libraries first
COPY shared_libs/ /app/shared_libs/

# Copy project files
COPY project_3/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY project_3/ .

# Environment variables
ENV PORT=8080
ENV PYTHONUNBUFFERED=1

# Expose port
EXPOSE 8080

# Run the application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]
