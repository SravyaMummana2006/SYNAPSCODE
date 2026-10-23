# Multi-stage production Dockerfile for SynapsCode
FROM python:3.11-slim

WORKDIR /app

# Install build dependencies for tree-sitter grammars
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend, models, dataset, and pre-built frontend dist
COPY . .

ENV PORT=5000
EXPOSE 5000

# Run with Gunicorn WSGI server
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "2", "app:app"]
