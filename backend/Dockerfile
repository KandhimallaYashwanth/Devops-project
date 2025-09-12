FROM python:3.11-slim

WORKDIR /app

# System deps (optional, keep minimal)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
  && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better layer caching
COPY requirements.txt ./
RUN pip install --no-cache-dir --upgrade pip \
  && pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Ensure .env is not baked into image (use Render env vars)

EXPOSE 5000

# Use gunicorn for production serving
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "app:app"]




