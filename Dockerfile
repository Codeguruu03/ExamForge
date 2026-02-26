# ── Build Frontend ────────────────────────────────────────────────────────────
FROM node:20-alpine AS frontend-builder

WORKDIR /app/frontend
COPY frontend/package*.json ./
RUN npm install
COPY frontend .
RUN npm run build

# ── Build Backend & Serve ─────────────────────────────────────────────────────
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend source
COPY backend /app/backend
COPY --from=frontend-builder /app/frontend/dist /app/frontend/dist

# Mount a volume for uploads
RUN mkdir -p /app/uploads

# Expose port
EXPOSE 8000

# Set environment variables
ENV UPLOAD_DIR=/app/uploads
ENV PYTHONPATH=/app

# Command to run (using Uvicorn)
CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
