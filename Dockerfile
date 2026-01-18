FROM python:3.11-slim

WORKDIR /app

# Install system dependencies (optional but recommended)
RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY app.py .

# Set environment
ENV FLASK_ENV=production
ENV PYTHONUNBUFFERED=1

# Expose Railway port (symbolic)
EXPOSE 8080

# Run with gunicorn using Railway PORT
CMD gunicorn app:app \
    --bind 0.0.0.0:${PORT} \
    --workers 2 \
    --timeout 120
